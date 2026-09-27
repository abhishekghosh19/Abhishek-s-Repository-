"""Keyword research using free, keyless public endpoints.

Primary sources (all free, no API key, no account):

  * Google Autocomplete     https://suggestqueries.google.com/complete/search
  * DuckDuckGo Autocomplete https://duckduckgo.com/ac/
  * Bing Autocomplete       https://www.bing.com/osjson.aspx

These are the same suggestion feeds that power the search boxes everyone uses.
They are unofficial and can be rate-limited, so the engine is polite (one
request per seed/query, short timeout) and degrades gracefully.

If none of the endpoints is reachable (offline machine, restricted CI, etc.)
the engine falls back to a bundled suggestion tree in
``content/offline_suggestions.json`` so the pipeline never dead-ends.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Tuple

from .config import CONTENT_DIR, SITE

USER_AGENT = "Mozilla/5.0 (compatible; FreeStackBlog/1.0; autonomous research)"
TIMEOUT = 8

ENDPOINTS: List[Tuple[str, str]] = [
    ("google", "https://suggestqueries.google.com/complete/search?client=firefox&q={q}"),
    ("duckduckgo", "https://duckduckgo.com/ac/?q={q}&kl=us-en"),
    ("bing", "https://www.bing.com/osjson.aspx?query={q}"),
]

OFFLINE_FILE = CONTENT_DIR / "offline_suggestions.json"


# ---------------------------------------------------------------- http layer

def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def _parse(text: str, name: str) -> List[str]:
    """Parse one endpoint's raw JSON into a list of suggestion strings."""
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return []
    out: List[str] = []
    try:
        if name == "google":
            items = data[1] if isinstance(data, list) and len(data) > 1 else []
            for item in items:
                s = item[0] if isinstance(item, (list, tuple)) else item
                if isinstance(s, str):
                    out.append(s.strip())
        elif name == "duckduckgo":
            for item in data if isinstance(data, list) else []:
                if isinstance(item, dict):
                    s = item.get("phrase")
                elif isinstance(item, (list, tuple)):
                    s = item[0]
                else:
                    s = item
                if isinstance(s, str):
                    out.append(s.strip())
        elif name == "bing":
            for item in data if isinstance(data, list) else []:
                s = item[0] if isinstance(item, (list, tuple)) else item
                if isinstance(s, str):
                    out.append(s.strip())
    except Exception:
        return []
    return [s for s in out if s and 3 <= len(s) <= 90][:15]


def suggest(query: str) -> Tuple[Dict[str, dict], int]:
    """Query every free autocomplete endpoint for ``query``.

    Returns ({phrase: {"sources": set, "positions": {endpoint: rank}}}, online_count).
    """
    found: Dict[str, dict] = {}
    online = 0
    for name, tpl in ENDPOINTS:
        try:
            text = _fetch(tpl.format(q=urllib.parse.quote(query)))
            online += 1
            for rank, phrase in enumerate(_parse(text, name), start=1):
                p = phrase.lower().strip()
                info = found.setdefault(p, {"sources": set(), "positions": {}})
                info["sources"].add(name)
                info["positions"][name] = min(info["positions"].get(name, 99), rank)
        except Exception:
            continue
    return found, online


# ----------------------------------------------------------- offline fallback

def _offline_tree() -> dict:
    if OFFLINE_FILE.exists():
        try:
            return json.loads(OFFLINE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def offline_suggest(query: str, tree: dict) -> Dict[str, dict]:
    info: Dict[str, dict] = {}
    for rank, phrase in enumerate(tree.get(query, []), start=1):
        p = phrase.lower().strip()
        info[p] = {"sources": {"offline"}, "positions": {"offline": rank}}
    return info


# ------------------------------------------------------------------- scoring

_TOKEN_RE = re.compile(r"[a-z0-9+#.\-]{2,}")


def _tokens(s: str) -> set:
    return set(_TOKEN_RE.findall(s.lower()))


def _score(phrase: str, level: int, sources: set, positions: dict, niche: set) -> float:
    s = 3.0 if level <= 1 else 1.2
    s += 0.8 * max(0, len(sources) - 1)  # cross-source agreement
    if positions:
        best = min(positions.values())
        s += max(0.0, 1.0 - best / 12.0)  # higher in the suggestions = better
    overlap = _tokens(phrase) & niche
    s += min(1.5, 0.5 * len(overlap))
    if len(phrase) > 55:
        s -= 0.6
    if phrase.endswith("?"):
        s += 0.2  # question keywords make great FAQ/SEO material
    return round(s, 2)


# ------------------------------------------------------------------ research

def load_seeds() -> List[dict]:
    return json.loads((CONTENT_DIR / "seeds.json").read_text(encoding="utf-8"))


def research(depth: int = 2, top: int = 60) -> dict:
    """Expand seed phrases through the free suggest endpoints (or the offline tree).

    Returns {"mode": "online"|"offline", "keywords": [ {phrase, level, score,
    parents, sources, positions} ... ]} sorted best-first.
    """
    seeds = load_seeds()
    niche = set(SITE["niche_tokens"])
    tree = _offline_tree()
    pool: Dict[str, dict] = {}
    online_hits = 0
    total_queries = 0

    def consider(phrase: str, parent: str, level: int, info: dict) -> None:
        p = phrase.lower().strip()
        if not p or p == parent:
            return
        if len(p) < 4 or len(p) > 90 or not re.search(r"[a-z0-9]", p):
            return
        entry = pool.get(p)
        if entry is None:
            entry = pool[p] = {
                "phrase": p,
                "level": level,
                "parents": set(),
                "sources": set(),
                "positions": {},
            }
        else:
            entry["level"] = min(entry["level"], level)
        if parent:
            entry["parents"].add(parent)
        entry["sources"] |= set(info["sources"])
        for src, pos in info["positions"].items():
            entry["positions"][src] = min(entry["positions"].get(src, 99), pos)

    for seed in seeds:
        q = seed["query"].lower().strip()
        seed_niche = niche | _tokens(q)
        total_queries += 1
        found, online = suggest(q)
        online_hits += online
        if not found:
            found = offline_suggest(q, tree)
        level1 = [p for p in found.keys()]
        for p in level1:
            consider(p, q, 1, found[p])

        if depth >= 2:
            # expand only the strongest level-1 suggestions, keeping requests low
            ranked = sorted(level1, key=lambda p: min(found[p]["positions"].values()))
            for p in ranked[:4]:
                total_queries += 1
                found2, online2 = suggest(p)
                online_hits += online2
                if not found2:
                    found2 = offline_suggest(p, tree)
                for c in found2.keys():
                    consider(c, p, 2, found2[c])

    keywords = []
    for entry in pool.values():
        keywords.append(
            {
                "phrase": entry["phrase"],
                "level": entry["level"],
                "score": _score(
                    entry["phrase"],
                    entry["level"],
                    entry["sources"],
                    entry["positions"],
                    seed_niche if len(pool) < 4 else niche,
                ),
                "parents": sorted(entry["parents"]),
                "sources": sorted(entry["sources"]),
                "positions": {k: v for k, v in entry["positions"].items()},
            }
        )
    keywords.sort(key=lambda k: (-k["score"], len(k["phrase"])))
    mode = "online" if online_hits > 0 else "offline"
    return {"mode": mode, "queries": total_queries, "keywords": keywords[:top]}


def new_keywords(research_result: dict, state: dict, limit: int) -> List[dict]:
    """Keywords from research that have not been used for a post yet."""
    done = set(state.get("processed_keywords", []))
    seen = state.setdefault("keywords_seen", {})
    for k in research_result["keywords"]:
        seen[k["phrase"]] = max(seen.get(k["phrase"], 0), k["score"])
    fresh = [k for k in research_result["keywords"] if k["phrase"] not in done]
    return fresh[:limit]
