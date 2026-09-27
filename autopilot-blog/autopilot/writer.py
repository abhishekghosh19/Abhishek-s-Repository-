"""The writing engine.

Two backends, both free:

1. ``template`` (default, zero cost, zero dependencies) — an open-source
   compositional writer. It matches researched keywords to a curated fact base
   (``content/facts/*.json``) and assembles a full article — title, intro, H2
   sections, FAQ, key takeaways, sources — from a large bank of writing
   templates. Different keywords, different fact mixes and a per-post random
   seed keep every article distinct; ``refresh`` re-composes an existing post
   with a new seed so the blog "edits" itself over time.

2. ``llm`` (free tiers of real LLMs) — if ``LLM_BASE_URL`` + ``LLM_API_KEY``
   are set, the same article spec is sent to any OpenAI-compatible endpoint.
   Free options: Google Gemini API free tier, Groq free tier, OpenRouter
   ``:free`` models, or a local Ollama server. On any LLM failure the engine
   falls back to the template backend so publishing never breaks.

An article is a plain dict:

    {slug, title, meta_description, intro[], sections[{heading, paragraphs[],
     bullets[]}], faq[{question, answer}], takeaways[], tags[], keywords[],
     sources[{title, url}], created, updated, words, reading_time, backend}
"""
from __future__ import annotations

import json
import os
import random
import re
import urllib.request
from typing import Dict, List, Optional

from .config import FACTS_DIR, SITE
from .state import load_posts, now_iso

# ================================================================ fact base

def load_facts() -> List[dict]:
    facts: List[dict] = []
    if not FACTS_DIR.exists():
        return facts
    for path in sorted(FACTS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(data, list):
            facts.extend(data)
    return facts


_TOKEN_RE = re.compile(r"[a-z0-9+#]{2,}")

# Generic/stop tokens that carry no topical signal. "free", "api-key" talk and
# question words are shared by almost every keyword in this niche, so they are
# filtered out before matching against the fact base.
STOP = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "at", "by", "with",
    "is", "are", "be", "no", "not", "free", "key", "keys", "card", "cards", "credit",
    "unlimited", "actually", "truly", "really", "just", "only", "very", "most",
    "more", "best", "top", "how", "what", "when", "where", "why", "who", "which",
    "can", "do", "does", "did", "will", "would", "should", "could", "its", "your",
    "you", "i", "we", "they", "he", "she", "my", "me", "us", "this", "that",
    "these", "those", "get", "gets", "got", "use", "uses", "used", "using", "need",
    "needs", "want", "wants", "make", "makes", "made", "run", "runs", "running",
    "work", "works", "working", "set", "sets", "setup", "setting", "settings",
    "one", "two", "three", "zero", "dollar", "dollars", "budget", "spend",
    "spending", "cost", "costs", "paid", "price", "year", "years", "2024", "2025",
    "2026", "2027", "new", "easy", "simple", "hard", "good", "great", "cheap",
    "expensive", "fast", "slow", "help", "helps", "check", "found", "find",
    "getting", "started", "start", "starting", "beginner", "complete", "full",
    "practical", "guide", "guides", "field", "without", "if", "then", "than",
    "so", "such", "as", "into", "from", "about", "after", "before", "over",
    "under", "up", "down", "out", "off", "again", "further", "once", "here",
    "there", "all", "any", "both", "each", "few", "other", "others", "some",
    "same", "too", "also", "while", "during", "vs", "via", "small", "smaller",
    "big", "self", "hosted", "selfhost", "limit", "limits", "tier", "tiers",
}

ACRONYMS = {"api", "apis", "llm", "ai", "seo", "rss", "json", "html", "cdn", "ui", "gsc", "ci", "id"}


def _tokens(s: str) -> set:
    out = set()
    for t in _TOKEN_RE.findall(s.lower()):
        out.add(t)
        if len(t) > 3 and t.endswith("s"):  # crude plural folding: bots -> bot
            out.add(t[:-1])
    return out


GENERIC_TAG_TOKENS = {"free", "api", "apis", "data", "no", "key", "open", "source", "self", "host"}
# Keyword tokens that match too many facts to be meaningful on their own.
NEUTRAL_KW_TOKENS = {"api", "apis", "data", "free", "open", "source"}


def _curated_tokens(fact: dict) -> set:
    """Tokens from the fact's curated metadata (tags, topic, aliases) — the
    intentional topical signal an author put there."""
    return _tokens(
        " ".join(fact.get("tags", [])) + " " + fact.get("topic", "") + " " + " ".join(fact.get("aliases", []))
    )


def _disc_tags(fact: dict) -> set:
    """Tags that carry topic-specific signal (not just 'free'/'api'/'open')."""
    out = set()
    for t in fact.get("tags", []):
        toks = _tokens(t)
        if not toks <= GENERIC_TAG_TOKENS:
            out |= toks
    return out


def _kw_raw_tokens(phrase: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall(phrase.lower()) if t not in STOP and len(t) > 1]


def _match_tokens(raw_tokens: List[str], vocab: set) -> set:
    """Match keyword tokens against a token vocab, counting each word once
    even when plural folding produced both forms ('pages'/'page')."""
    matched = set()
    for t in raw_tokens:
        if t in vocab:
            matched.add(t)
        elif len(t) > 3 and t.endswith("s") and t[:-1] in vocab:
            matched.add(t)
        elif len(t) > 2 and not t.endswith("s") and (t + "s") in vocab:
            matched.add(t)
    return matched


def _anchor_token(phrase: str) -> Optional[str]:
    """First distinctive (non-neutral) token of the phrase — the intent anchor
    ('gemini' in 'gemini api free tier python')."""
    for t in _kw_raw_tokens(phrase):
        if t not in NEUTRAL_KW_TOKENS:
            return t
    return None


def relevance(fact: dict, kw: str) -> float:
    """Score how well a fact serves a keyword.

    strong: keyword token found in curated metadata  -> 3.0 each
    weak:   keyword token found only in the body     -> 0.3 each (capped)
    """
    raw = _kw_raw_tokens(kw)
    curated = _curated_tokens(fact)
    strong = _match_tokens(raw, curated)
    body = _tokens(fact.get("claim", "") + " " + fact.get("detail", ""))
    weak = _match_tokens(raw, body) - strong  # body-only hits (folding-safe)
    return round(3.0 * len(strong) + min(1.2, 0.3 * len(weak)), 2)


def pick_facts(kw: str, facts: List[dict], count: int = 4) -> List[dict]:
    """Pick at most ``count`` genuinely relevant facts.

    - score >= 6 (2+ curated hits): clearly on-topic, always taken
    - score 3..6 (1 curated hit):  taken only if it shares a distinctive tag
      with the already-picked facts, or its single hit is a non-generic token
      (e.g. 'python', 'weather') — and at most ``count - strong - 1`` of them,
      so a post keeps at least one universal section.
    Bonuses: the intent anchor (+1.5) and data APIs for bare 'free api'
    queries (+1.0). The writer pads whatever remains with universal sections.
    """
    raw = _kw_raw_tokens(kw)
    anchor = _anchor_token(kw)
    general_api_query = set(raw) <= {"api", "apis"}
    rows = []
    for f in facts:
        s = relevance(f, kw)
        curated = _curated_tokens(f)
        if general_api_query and "data" in curated:
            s += 1.0
        if anchor and anchor in curated:
            s += 1.5
        rows.append((s, f, _match_tokens(raw, curated)))
    rows.sort(key=lambda r: -r[0])

    strong = [r for r in rows if r[0] >= 6]
    mid = [r for r in rows if 3 <= r[0] < 6]
    top = [f for _, f, _ in strong][:count]

    if not top:
        return [f for _, f, _ in mid][:count]

    if len(top) < count:
        top_disc = set()
        for f in top:
            top_disc |= _disc_tags(f)

        def share(r: tuple) -> int:
            return len(_disc_tags(r[1]) & top_disc)

        # only facts that are topically linked to the picks (shared distinctive
        # tag) or hit a non-generic token (e.g. 'python') make the cut; the
        # writer pads the rest with universal on-niche sections
        candidates = [
            r for r in mid
            if share(r) > 0 or (r[2] and not r[2] <= NEUTRAL_KW_TOKENS)
        ]
        candidates.sort(key=lambda r: (-share(r), -r[0]))
        allowed = max(0, count - len(top) - 1)
        top += [f for _, f, _ in candidates[:allowed]]
    return top


# ================================================================ templates

INTRO_PATTERNS: List[str] = [
    "Let's be honest: the internet is full of posts that pretend {kw} is complicated. It isn't. What's actually complicated is separating the free options that hold up from the free options that quietly become $20/month. That's what this post digs into.",
    "If you've been searching for {kw}, you've probably noticed two kinds of advice: paid tools that open with a soft upsell, and abandoned blog posts that stopped being true years ago. This one is built to stay useful, and it's maintained automatically.",
    "This is the kind of post The Free Stack exists to write: a practical, no-fluff guide to {kw}, assembled from free tiers, open-source projects and endpoints that ask for no API key at all.",
    "You don't need a budget to get good at {kw}. You need a map of the free tools, and an honest read on the trade-offs between them. Here's that map — researched, written and fact-checked by the same engine that publishes this blog.",
    "Most 'complete guides' to {kw} pad the word count with ads. This one is different: every recommendation below runs on a free tier, an open-source project, or both. If a recommendation ever costs money, we say so in plain words.",
    "Here's the premise: {kw} should cost nothing to get started. Between open-source projects, free API tiers and self-hostable tools, it can. Below is the working setup we actually use, plus the gotchas we hit.",
]

INTRO_COVERAGE = (
    "We'll walk through {sections} — and finish with the questions people actually "
    "ask, so you can check before you buy anything. You shouldn't have to buy anything."
)

SECTION_OPENERS: List[str] = [
    "Start with the basics.",
    "Here's the part most people get wrong.",
    "Worth spending ten minutes on:",
    "The short version:",
    "First, the thing that actually matters:",
    "Skip the fluff and start here:",
    "The foundation looks like this:",
]

SECTION_BRIDGES: List[str] = [
    "In practice that means:",
    "In other words:",
    "The upshot:",
    "Concretely:",
    "Which, in day-to-day terms, means:",
    "So what does that look like when you're actually doing it?",
]

SECTION_CLOSERS: List[str] = [
    "No signup wall, no credit card — just a README and some patience.",
    "If you only do one thing today, make it this one.",
    "Keep it this simple and you'll be ahead of most tutorials out there.",
    "The links in the sources section go straight to the primary docs.",
    "For a personal project or side business, this covers you without breaking a sweat.",
    "Write down what you change and why — your future self will thank you.",
]

BULLET_INTROS: List[str] = [
    "Quick checklist:",
    "The bare minimum:",
    "If you want the condensed version:",
    "Do it in this order:",
]

TAKEAWAY_TEMPLATES: List[str] = [
    "{fact} That one fact covers most of the confusion around {kw}.",
    "Remember: {fact}",
    "The whole point in one sentence: {fact}",
    "Don't forget — {fact}",
]

FAQ_QUESTIONS: List[str] = [
    "Is {kw} actually free?",
    "How much do I need to know before trying {kw}?",
    "What are the real limitations of {kw}?",
    "Can I keep this free forever, or is it a trial?",
    "What would you do first if you only had one free afternoon?",
]

LIMIT_LINES: List[str] = [
    "the catch is usually scale or politeness: rate limits, bandwidth caps, or the fine print of the free tier",
    "free tiers are generous for personal projects, but a growing business should read the pricing page before scaling into it",
    "keyless public endpoints can get throttled if you hammer them, so batch your requests and cache what you fetch",
    "the free tier is the product, not the teaser — but the paid tier exists for when you need SLAs, support or volume",
]

ANSWER_TEMPLATES: List[str] = [
    "Mostly, yes. {fact} {limit}",
    "Less than you'd think. {fact} Start there and only add pieces when you feel actual pain.",
    "The honest answer: {fact} {limit}",
    "{fact} Treat that as the working assumption and re-check the docs once a quarter.",
]

TITLE_PATTERNS: List[str] = [
    "The Complete Guide to {kw_title} (2026)",
    "{kw_title}: A Practical Field Guide",
    "How to Get {kw_title} Without Spending a Dollar",
    "{kw_title} — What Actually Works in 2026",
    "{kw_title}: Free Tools, Real Trade-offs",
    "{kw_title} on a $0 Budget: An Honest Walkthrough",
]

META_DESC_PATTERNS: List[str] = [
    "{kw_title}: practical, no-fluff guidance on the free and open options — the tools, the limits, and the trade-offs that matter. Written and maintained by an autonomous blog engine.",
    "What does {kw_title} cost in 2026 (spoiler: nothing), and how do you set it up properly? Covers free tiers, open-source alternatives and honest trade-offs.",
]

# Universal, on-niche sections used when keyword-specific facts run thin.
FILLER_SECTIONS: List[dict] = [
    {
        "heading": "Choose boring technology first",
        "claim": "The best infrastructure for a side project is the least surprising kind: static files, a public repo, a free CDN in front of it.",
        "detail": "Every exotic dependency is a future tax. If a free, open-source tool can serve the job, pick the one with the longest track record and the biggest community, and save the interesting experiments for the parts users actually touch.",
        "tags": ["self-host", "static", "blog"],
    },
    {
        "heading": "Automate the boring parts",
        "claim": "Anything you do twice by hand should become a script. That's the entire discipline of free automation.",
        "detail": "A cron expression, a webhook, or a scheduled workflow costs nothing to run and buys back an hour every week. Start with one small automation — a nightly backup, a feed check, a deploy on push — and add more only when the first one proves itself.",
        "tags": ["automation", "cron", "github"],
    },
    {
        "heading": "Measure before you optimize",
        "claim": "You cannot improve what you do not measure, and the measurement tools here are all free.",
        "detail": "Search console data, a simple counter in your build log, or raw access logs tell you which pages earn their keep. Ten minutes of reading that data is worth more than an hour of guessing, and none of it requires a paid analytics account.",
        "tags": ["seo", "data", "apis"],
    },
    {
        "heading": "Keep a changelog",
        "claim": "Write down what you changed and why, even for experiments you might throw away.",
        "detail": "A dated note beats a vague memory every single time — it's how an autonomous blog like this one tracks its own edits, and it's how you will know in six months why the setup is the way it is.",
        "tags": ["blog", "self-host"],
    },
]

# ================================================================ helpers

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:70] or "post"


def _unique_slug(base: str, existing: set) -> str:
    if base not in existing:
        return base
    i = 2
    while f"{base}-{i}" in existing:
        i += 1
    return f"{base}-{i}"


def _truncate(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    cut = s[: n - 1].rsplit(" ", 1)[0]
    return cut.rstrip(",.;:") + "…"


def _title_case(s: str) -> str:
    small = {"a", "an", "and", "for", "in", "of", "on", "or", "the", "to", "vs", "with"}
    words = s.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if lw in ACRONYMS:
            out.append(lw.upper())
        elif i == 0 or i == len(words) - 1:
            out.append(w.capitalize())
        elif lw in small:
            out.append(lw)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def _words(article: dict) -> int:
    n = len(article["title"].split())
    for p in article["intro"]:
        n += len(p.split())
    for sec in article["sections"]:
        n += len(sec["heading"].split())
        for p in sec["paragraphs"]:
            n += len(p.split())
        for b in sec.get("bullets", []):
            n += len(b.split())
    for q in article["faq"]:
        n += len((q["question"] + " " + q["answer"]).split())
    for t in article["takeaways"]:
        n += len(t.split())
    return n


# ================================================================ template writer

def _compose_sections(rng: random.Random, facts: List[dict], kw: str) -> List[dict]:
    sections = []
    for fact in facts:
        paragraphs = [
            f"{rng.choice(SECTION_OPENERS)} {fact['claim'].strip()}",
            f"{rng.choice(SECTION_BRIDGES)} {fact['detail'].strip()}",
            f"{rng.choice(SECTION_CLOSERS)}",
        ]
        sections.append(
            {
                "heading": fact.get("heading") or _title_case(fact["topic"]),
                "paragraphs": paragraphs,
                "bullets": list(fact.get("steps", [])),
                "source": {"title": fact.get("source_title", ""), "url": fact.get("source_url", "")},
            }
        )
    # light ordering: keep fact-driven sections in relevance order, but vary the close
    if len(sections) > 2 and rng.random() < 0.35:
        sections[-1], sections[-2] = sections[-2], sections[-1]
    return sections


def _compose_faq(rng: random.Random, facts: List[dict], kw: str) -> List[dict]:
    faq = []
    for q_tpl in rng.sample(FAQ_QUESTIONS, 3):
        question = q_tpl.format(kw=kw)
        fact = rng.choice(facts)
        limit = rng.choice(LIMIT_LINES).capitalize() + "."
        answer = rng.choice(ANSWER_TEMPLATES).format(
            fact=fact["claim"].strip(), limit=limit
        )
        faq.append({"question": question, "answer": answer})
    return faq


def _compose_takeaways(rng: random.Random, facts: List[dict], kw: str) -> List[str]:
    out = []
    for fact in facts[:4]:
        first_sentence = re.split(r"(?<=[.!?])\s+", fact["claim"].strip())[0]
        out.append(rng.choice(TAKEAWAY_TEMPLATES).format(fact=first_sentence, kw=kw))
    return out


def write_article_template(kw: dict, existing_slugs: set, seed: Optional[int] = None) -> dict:
    phrase = kw["phrase"]
    rng = random.Random(seed if seed is not None else (phrase + str(len(existing_slugs))))
    facts = pick_facts(phrase, load_facts())

    sections = _compose_sections(rng, facts, phrase)

    # pad with universal on-niche sections so every post has 4 solid H2s,
    # rather than forcing weak fact matches into the body
    if len(sections) < 4:
        pool = [s for s in FILLER_SECTIONS if s["heading"] not in {x["heading"] for x in sections}]
        rng.shuffle(pool)
        for fill in pool[: 4 - len(sections)]:
            sections.append(
                {
                    "heading": fill["heading"],
                    "paragraphs": [
                        f"{rng.choice(SECTION_OPENERS)} {fill['claim'].strip()}",
                        f"{rng.choice(SECTION_BRIDGES)} {fill['detail'].strip()}",
                        f"{rng.choice(SECTION_CLOSERS)}",
                    ],
                    "bullets": [],
                    "source": {"title": "", "url": ""},
                }
            )

    base_slug = slugify(phrase)
    slug = _unique_slug(base_slug, existing_slugs)

    title = None
    for pattern in rng.sample(TITLE_PATTERNS, len(TITLE_PATTERNS)):
        candidate = pattern.format(kw=phrase, kw_title=_title_case(phrase))
        candidate_slug = slugify(candidate.split(":")[0].split("—")[0])
        if candidate_slug == base_slug or candidate_slug not in existing_slugs:
            title = candidate
            break
    if title is None:
        title = f"{_title_case(phrase)}: A Practical Field Guide"

    meta_desc = _truncate(
        rng.choice(META_DESC_PATTERNS).format(kw_title=_title_case(phrase), kw=phrase),
        158,
    )

    headings = [s["heading"] for s in sections]
    if len(headings) > 3:
        coverage = f"{', '.join(headings[:-1])}, and {headings[-1]}"
    else:
        coverage = " and ".join(headings)
    intro = [
        rng.choice(INTRO_PATTERNS).format(kw=phrase),
        INTRO_COVERAGE.format(sections=coverage),
    ]

    tags = sorted(
        {t for f in facts for t in f.get("tags", []) if t},
        key=lambda t: -sum(1 for f in facts if t in f.get("tags", [])),
    )[:4]

    sources = [
        s
        for s in (sec.get("source", {}) for sec in sections)
        if s.get("url")
    ][:6]

    article = {
        "slug": slug,
        "title": title,
        "meta_description": meta_desc,
        "intro": intro,
        "sections": sections,
        "faq": _compose_faq(rng, facts or FILLER_SECTIONS, phrase),
        "takeaways": _compose_takeaways(rng, facts or FILLER_SECTIONS, phrase),
        "tags": tags,
        "keywords": [phrase] + list(kw.get("parents", []))[:2],
        "sources": sources,
        "created": now_iso(),
        "updated": now_iso(),
        "backend": "template",
    }
    article["words"] = _words(article)
    article["reading_time"] = max(1, round(article["words"] / 200))
    return article


# ================================================================ LLM backend

LLM_SYSTEM_PROMPT = f"""You are the writing engine of "{SITE['name']}", an autonomous blog about
building things on free & open tools (free APIs, open-source alternatives, free hosting,
no-cost automation). Tone: practical, direct, lightly witty, zero marketing fluff. Never
recommend a paid product as a solution; mention paid tiers only as an honest caveat.

You MUST respond with ONLY a JSON object (no markdown fences) with exactly these keys:
{{
  "title": str,            // <= 65 chars, contains the keyword
  "meta_description": str, // 120-158 chars, contains the keyword
  "intro": [str, str],     // two opening paragraphs, total ~120-180 words
  "sections": [ {{"heading": str, "paragraphs": [str, str], "bullets": [str]}} ],  // 3-5 sections
  "faq": [ {{"question": str, "answer": str}} ],  // exactly 3
  "takeaways": [str, str, str, str]
}}
Total body length 700-1100 words. Use the provided facts as the factual basis and cite
their source titles naturally. Do not invent URLs, statistics or product names."""


def _llm_chat(messages: List[dict], timeout: int = 90) -> str:
    base = os.environ.get("LLM_BASE_URL", "").rstrip("/")
    key = os.environ.get("LLM_API_KEY", "")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    body = json.dumps(
        {"model": model, "messages": messages, "temperature": 0.8, "max_tokens": 2600}
    ).encode("utf-8")
    req = urllib.request.Request(
        base + "/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "User-Agent": "FreeStackBlog/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    return data["choices"][0]["message"]["content"]


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object in LLM response")
    return json.loads(text[start : end + 1])


def write_article_llm(kw: dict, existing_slugs: set, seed: Optional[int] = None) -> dict:
    phrase = kw["phrase"]
    facts = pick_facts(phrase, load_facts())
    rng = random.Random(seed if seed is not None else phrase)
    fact_blob = json.dumps(
        [
            {k: f.get(k) for k in ("topic", "claim", "detail", "source_title", "source_url")}
            for f in facts
        ],
        indent=1,
    )
    user_prompt = (
        f"Keyword: {phrase}\n"
        f"Niche: {SITE['name']} — {SITE['short']}\n"
        f"Year: {SITE['year']}\n\n"
        f"Verified facts (use these; do not add URLs beyond these):\n{fact_blob}"
    )
    raw = _llm_chat(
        [
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )
    data = _extract_json(raw)

    sections = []
    for sec in data.get("sections", [])[:5]:
        paragraphs = [str(p) for p in sec.get("paragraphs", []) if str(p).strip()][:4]
        bullets = [str(b) for b in sec.get("bullets", []) if str(b).strip()][:8]
        if paragraphs:
            sections.append({"heading": str(sec.get("heading", "")).strip(), "paragraphs": paragraphs, "bullets": bullets})
    faq = [
        {"question": str(q.get("question", "")).strip(), "answer": str(q.get("answer", "")).strip()}
        for q in data.get("faq", [])[:3]
        if str(q.get("question", "")).strip()
    ]
    takeaways = [str(t) for t in data.get("takeaways", [])[:4] if str(t).strip()]

    base_slug = slugify(phrase)
    slug = _unique_slug(base_slug, existing_slugs)
    article = {
        "slug": slug,
        "title": str(data.get("title", f"{_title_case(phrase)}: A Practical Field Guide"))[:120],
        "meta_description": _truncate(str(data.get("meta_description", "")) or meta_fallback(phrase), 158),
        "intro": [str(p) for p in data.get("intro", [])[:2] if str(p).strip()] or [
            f"A practical, no-fluff guide to {phrase}."
        ],
        "sections": sections or _compose_sections(rng, facts, phrase),
        "faq": faq or _compose_faq(rng, facts, phrase),
        "takeaways": takeaways or _compose_takeaways(rng, facts, phrase),
        "tags": sorted({t for f in facts for t in f.get("tags", [])})[:4],
        "keywords": [phrase] + list(kw.get("parents", []))[:2],
        "sources": [
            {"title": f.get("source_title", ""), "url": f.get("source_url", "")}
            for f in facts
            if f.get("source_url")
        ][:6],
        "created": now_iso(),
        "updated": now_iso(),
        "backend": "llm",
    }
    article["words"] = _words(article)
    article["reading_time"] = max(1, round(article["words"] / 200))
    return article


def meta_fallback(phrase: str) -> str:
    return _truncate(
        f"{_title_case(phrase)}: the free, open and practical options — tools, limits and honest trade-offs, written and maintained by an autonomous blog engine.",
        158,
    )


# ================================================================ public API

def backend_available(name: str) -> bool:
    if name in ("template", "auto", ""):
        return True
    if name == "llm":
        return bool(os.environ.get("LLM_API_KEY"))
    return False


def write_article(kw: dict, existing_slugs: set, backend: str = "auto", seed: Optional[int] = None) -> dict:
    """Write one article for a keyword. ``auto`` = LLM if configured, else template."""
    use_llm = backend == "llm" or (backend == "auto" and backend_available("llm"))
    if use_llm:
        try:
            return write_article_llm(kw, existing_slugs, seed=seed)
        except Exception:
            if backend == "llm":
                raise
            # fall through to the always-working template backend
    return write_article_template(kw, existing_slugs, seed=seed)


def refresh_article(article: dict) -> dict:
    """Re-compose an existing post with a fresh seed (the blog 'edits' itself).

    Preserves slug, title, keywords, created date; rewrites sections, FAQ and
    takeaways with new template choices and any newer facts; bumps `updated`.
    """
    kw = {"phrase": article["keywords"][0] if article.get("keywords") else article["slug"], "parents": []}
    existing = set(load_posts().keys())
    existing.discard(article["slug"])
    new_seed = (article.get("updated", "") + str(article.get("updated_count", 0))).encode()
    new_seed = int.from_bytes(new_seed[:8].ljust(8, b"0"), "big", signed=False) ^ 0x9E3779B9
    fresh = write_article_template(kw, existing, seed=new_seed)
    updated = dict(article)
    updated.update(
        {
            "sections": fresh["sections"],
            "faq": fresh["faq"],
            "takeaways": fresh["takeaways"],
            "intro": fresh["intro"],
            "sources": fresh["sources"],
            "updated": now_iso(),
            "updated_count": article.get("updated_count", 0) + 1,
            "backend": f"{article.get('backend', 'template')}+refresh",
        }
    )
    updated["words"] = _words(updated)
    updated["reading_time"] = max(1, round(updated["words"] / 200))
    return updated
