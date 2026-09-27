"""Static site renderer — the publisher.

Builds a complete, dependency-free static site into ``site/``:

  index.html            home page (latest posts, "how it works", live stats)
  posts/<slug>.html     article pages (full SEO: meta, JSON-LD, FAQ, sources)
  tags/<tag>.html       tag archives (internal linking for SEO)
  404.html, feed.xml, sitemap.xml, robots.txt
  static/style.css, static/favicon.svg, static/covers/<slug>.svg

All links are relative, so the folder can be deployed from any sub-path of any
free host (GitHub Pages project site, Cloudflare Pages, Netlify, a VPS with
nginx, ...). Absolute URLs only appear in canonical/OG/sitemap tags, which are
taken from SITE['url'] (set SITE_URL once you know the final host).
"""
from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from . import seo
from .config import SITE, SITE_DIR
from .cover import make_cover

esc = html.escape


def _head(title: str, desc: str, extra: str = "", rel: str = "", rss_link: bool = True) -> str:
    favicon = f"{rel}static/favicon.svg"
    css = f"{rel}static/style.css"
    rss = f'<link rel="alternate" type="application/rss+xml" title="{esc(SITE["name"])} RSS" href="{rel}feed.xml"/>' if rss_link else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"/>
{rss}
<link rel="icon" type="image/svg+xml" href="{favicon}"/>
<link rel="stylesheet" href="{css}"/>
{extra}
</head>
"""


def _header(rel: str = "") -> str:
    return f"""<body>
<header class="top">
  <div class="wrap nav">
    <a class="logo" href="{rel}index.html">&#9881; {esc(SITE['name'])}</a>
    <nav>
      <a href="{rel}index.html#latest">Latest</a>
      <a href="{rel}index.html#how">How it works</a>
      <a href="{rel}feed.xml" title="RSS feed">RSS</a>
    </nav>
  </div>
</header>
"""


def _footer(rel: str = "") -> str:
    return f"""<footer class="foot">
  <div class="wrap">
    <p><strong>{esc(SITE['name'])}</strong> — {esc(SITE['tagline'])}</p>
    <p class="fine">
      Written, researched, optimized and published autonomously on free &amp; open tools.
      No cookies, no trackers, no paid plugins. <a href="{SITE['github']}">Read the engine source on GitHub</a>.
      &copy; {esc(SITE['year'])} — content is generated and may improve over time.
    </p>
  </div>
</footer>
</body>
</html>
"""


def _date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return iso[:10]


def _card(slug: str, title: str, desc: str, created: str, tags: List[str], reading_time: int, rel: str = "") -> str:
    tag_html = "".join(f'<a class="chip" href="{rel}tags/{t}.html">{esc(t)}</a>' for t in tags[:3])
    return f"""<a class="card" href="{rel}posts/{slug}.html">
  <img class="card-cover" src="{rel}static/covers/{slug}.svg" alt="" loading="lazy"/>
  <div class="card-body">
    <div class="card-meta">{_date(created)} &middot; {reading_time} min read</div>
    <h3>{esc(title)}</h3>
    <p>{esc(desc)}</p>
    <div class="chips">{tag_html}</div>
  </div>
</a>
"""


def render_home(posts: List[dict], stats: dict) -> str:
    cards = "".join(
        _card(p["slug"], p["title"], p.get("meta_description", ""), p.get("created", ""), p.get("tags", []), p.get("reading_time", 1))
        for p in posts
    ) or '<p class="empty">No posts yet — the engine publishes its first batch on its next run.</p>'
    stats_row = f"""<div class="stats">
      <div><span>{stats['posts']}</span> posts published</div>
      <div><span>{stats['keywords']}</span> keywords tracked</div>
      <div><span>{stats['runs']}</span> autonomous runs</div>
      <div><span>{stats['refreshes']}</span> self-edits</div>
    </div>"""
    head_extra = f"""<link rel="canonical" href="{SITE['url']}/"/>
<meta property="og:title" content="{esc(SITE['name'])}"/>
<meta property="og:description" content="{esc(SITE['description'])}"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="{SITE['url']}/"/>
<meta name="twitter:card" content="summary"/>"""
    body = f"""<main class="wrap">
  <section class="hero">
    <p class="kicker">autonomous blog &middot; free stack edition</p>
    <h1>{esc(SITE['name'])}</h1>
    <p class="lede">{esc(SITE['tagline'])}</p>
    <div class="chips">
      <span class="chip solid">keyword research</span>
      <span class="chip solid">self-writing</span>
      <span class="chip solid">self SEO</span>
      <span class="chip solid">social posting</span>
      <span class="chip solid">$0.00 / month</span>
    </div>
    {stats_row}
  </section>

  <section id="latest">
    <h2>Latest from the engine</h2>
    <div class="grid">{cards}</div>
  </section>

  <section id="how" class="how">
    <h2>How this blog runs itself</h2>
    <p class="how-intro">Every day, on a free GitHub Actions schedule, the same loop wakes up and does this:</p>
    <ol class="steps">
      <li><h3>1 &middot; Research</h3><p>Expands seed topics through free, keyless autocomplete endpoints (Google, DuckDuckGo, Bing) and scores the candidates for fit.</p></li>
      <li><h3>2 &middot; Write</h3><p>Matches the winning keyword to a curated fact base and composes a full article — intro, sections, FAQ, takeaways, sources — with an open-source template writer (or a free-tier LLM when one is configured).</p></li>
      <li><h3>3 &middot; Optimize</h3><p>Generates meta tags, JSON-LD structured data, a cover image, sitemaps, robots.txt and an RSS feed, then audits every post against an SEO checklist.</p></li>
      <li><h3>4 &middot; Publish &amp; post</h3><p>Commits the rebuilt site to the repo — GitHub Pages deploys it automatically — and queues the post to free social channels (RSS, Discord, Telegram, Mastodon, Bluesky). Older posts get periodically re-composed, so the blog edits itself over time.</p></li>
    </ol>
    <p class="fine">Everything above is open source and lives in this repo: <a href="{SITE['github']}">autopilot-blog/</a>. Fork it and you get a working clone of the whole engine.</p>
  </section>
</main>
"""
    return _head(f"{SITE['name']} — {esc(SITE['short'])}", SITE["description"], head_extra) + _header() + body + _footer()


def render_post(article: dict, related: List[dict], prev: dict, nxt: dict) -> str:
    m = seo.meta_tags(article)
    extra = f"""<link rel="canonical" href="{m['canonical']}"/>
<meta property="og:title" content="{esc(m['og_title'])}"/>
<meta property="og:description" content="{esc(m['og_description'])}"/>
<meta property="og:type" content="{m['og_type']}"/>
<meta property="og:url" content="{esc(m['og_url'])}"/>
<meta property="og:image" content="{esc(m['og_image'])}"/>
<meta name="twitter:card" content="{m['twitter_card']}"/>
<meta name="twitter:title" content="{esc(m['og_title'])}"/>
<meta name="twitter:description" content="{esc(m['og_description'])}"/>
<meta name="twitter:image" content="{esc(m['og_image'])}"/>
<meta name="robots" content="index, follow, max-image-preview:large"/>
{seo.json_ld_script(article)}"""

    intro = "".join(f"<p>{esc(p)}</p>" for p in article.get("intro", []))
    sections = []
    for sec in article.get("sections", []):
        ps = "".join(f"<p>{esc(p)}</p>" for p in sec.get("paragraphs", []))
        if sec.get("bullets"):
            ps += '<ul>' + "".join(f"<li>{esc(b)}</li>" for b in sec["bullets"]) + "</ul>"
        sections.append(f"<section><h2>{esc(sec['heading'])}</h2>{ps}</section>")
    faq = "".join(
        f'<details><summary>{esc(q["question"])}</summary><p>{esc(q["answer"])}</p></details>'
        for q in article.get("faq", [])
    )
    takeaways = "<ul>" + "".join(f"<li>{esc(t)}</li>" for t in article.get("takeaways", [])) + "</ul>"
    sources = "<ol>" + "".join(f'<li><a href="{esc(s["url"])}" rel="noopener" target="_blank">{esc(s["title"] or s["url"])}</a></li>' for s in article.get("sources", []) if s.get("url")) + "</ol>"
    tags = "".join(f'<a class="chip" href="../tags/{t}.html">{esc(t)}</a>' for t in article.get("tags", []))
    rel_cards = "".join(_card(r["slug"], r["title"], r.get("meta_description", ""), r.get("created", ""), r.get("tags", []), r.get("reading_time", 1), rel="../") for r in related)
    updated_badge = ""
    if article.get("updated_count"):
        updated_badge = f' <span class="badge">updated &times;{article["updated_count"]}</span>'
    prev_html = f'<a href="../posts/{esc(prev["slug"])}.html">&larr; {esc(prev["title"][:60])}</a>' if prev else ""
    next_html = f'<a href="../posts/{esc(nxt["slug"])}.html">{esc(nxt["title"][:60])} &rarr;</a>' if nxt else ""

    body = f"""<main class="wrap post">
  <article>
    <a class="back" href="../index.html">&larr; all posts</a>
    <h1>{esc(article['title'])}</h1>
    <p class="meta-line">{_date(article.get('created',''))} &middot; {article.get('reading_time',1)} min read &middot; by {esc(SITE['author'])} &middot; last updated {_date(article.get('updated', article.get('created','')))}{updated_badge}</p>
    <img class="cover" src="../static/covers/{esc(article['slug'])}.svg" alt="{esc(article['title'])}"/>
    <div class="prose">
      {intro}
      {''.join(sections)}
      <aside class="aside"><h2>Key takeaways</h2>{takeaways}</aside>
      <section id="faq"><h2>Frequently asked questions</h2>{faq}</section>
      <section id="sources"><h2>Sources</h2>{sources}</section>
    </div>
    <div class="tagrow">{tags}</div>
  </article>
  {f'<section class="related"><h2>Related from the engine</h2><div class="grid">{rel_cards}</div></section>' if rel_cards else ''}
  <nav class="pager">{prev_html}<span></span>{next_html}</nav>
</main>
"""
    return _head(f"{m['title']}", m["description"], extra, rel="../") + _header(rel="../") + body + _footer(rel="../")


def render_tag(tag: str, posts: List[dict]) -> str:
    cards = "".join(_card(p["slug"], p["title"], p.get("meta_description", ""), p.get("created", ""), p.get("tags", []), p.get("reading_time", 1), rel="../") for p in posts)
    extra = f'<meta name="robots" content="index, follow"/>'
    body = f"""<main class="wrap">
  <a class="back" href="../index.html">&larr; all posts</a>
  <h1>Tag: {esc(tag)}</h1>
  <p class="lede">Everything the engine has published under <code>{esc(tag)}</code> ({len(posts)} post{'s' if len(posts) != 1 else ''}).</p>
  <div class="grid">{cards}</div>
</main>
"""
    return _head(f"{esc(tag)} | {SITE['name']} — {esc(SITE['short'])}", f"All {SITE['name']} posts tagged {tag}.", extra, rel="../") + _header(rel="../") + body + _footer(rel="../")


def render_404() -> str:
    body = """<main class="wrap">
  <h1>404</h1>
  <p class="lede">This page doesn't exist — but the blog that would have written it is running fine.</p>
  <p><a class="button" href="index.html">Back to the front page</a></p>
</main>
"""
    return _head(f"404 | {SITE['name']}", "Page not found.", "", rel="") + _header() + body + _footer()


# ------------------------------------------------------------------ css

CSS = """
:root{
  --bg:#0b0f14; --panel:#111823; --panel2:#0e141d; --line:#1e2a3a;
  --text:#e6edf3; --muted:#8b98a9; --accent:#56d364; --accent2:#58a6ff;
  --radius:14px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
a{color:var(--accent2);text-decoration:none}
a:hover{text-decoration:underline}
code{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-size:.9em}
.top{position:sticky;top:0;z-index:10;background:rgba(11,15,20,.85);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.nav{display:flex;align-items:center;justify-content:space-between;height:58px}
.logo{font-weight:800;font-size:1.05rem;color:var(--text);letter-spacing:.2px}
.logo:hover{text-decoration:none;color:var(--accent)}
.top nav a{margin-left:18px;color:var(--muted);font-size:.92rem}
.top nav a:hover{color:var(--text);text-decoration:none}
.hero{padding:64px 0 30px}
.kicker{color:var(--accent);text-transform:uppercase;letter-spacing:.18em;font-size:.72rem;font-weight:700;margin:0 0 10px}
h1{font-size:2.6rem;line-height:1.12;margin:.2rem 0 .8rem;letter-spacing:-.02em}
.lede{color:var(--muted);font-size:1.12rem;max-width:640px;margin:0 0 18px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
.chip{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:3px 12px;font-size:.78rem;color:var(--muted);background:var(--panel2)}
a.chip{color:var(--accent2)}
a.chip:hover{border-color:var(--accent2);text-decoration:none}
.chip.solid{background:rgba(86,211,100,.12);border-color:rgba(86,211,100,.35);color:var(--accent)}
.stats{display:flex;flex-wrap:wrap;gap:26px;margin-top:22px;color:var(--muted);font-size:.92rem}
.stats span{color:var(--text);font-weight:700;font-size:1.15rem;margin-right:6px}
section{margin:44px 0}
h2{font-size:1.45rem;letter-spacing:-.01em;margin:0 0 16px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
@media(max-width:860px){.grid{grid-template-columns:repeat(2,1fr)}h1{font-size:2rem}}
@media(max-width:560px){.grid{grid-template-columns:1fr}}
.card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;color:var(--text);transition:transform .12s ease,border-color .12s ease}
.card:hover{transform:translateY(-3px);border-color:var(--accent);text-decoration:none}
.card-cover{width:100%;display:block;aspect-ratio:1200/630;object-fit:cover}
.card-body{padding:16px 18px 18px}
.card-meta{color:var(--muted);font-size:.78rem;margin-bottom:6px}
.card h3{font-size:1.05rem;line-height:1.35;margin:0 0 8px}
.card p{color:var(--muted);font-size:.9rem;margin:0 0 10px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.post{padding-bottom:20px}
.back{display:inline-block;margin:26px 0 8px;color:var(--muted);font-size:.9rem}
h1.post-title,.post h1{margin-top:0}
.meta-line{color:var(--muted);font-size:.88rem;margin-bottom:18px}
.badge{background:rgba(88,166,255,.15);border:1px solid rgba(88,166,255,.4);color:var(--accent2);border-radius:999px;padding:1px 9px;font-size:.75rem}
.cover{width:100%;border-radius:var(--radius);border:1px solid var(--line);display:block;margin-bottom:26px}
.prose{max-width:74ch}
.prose p{margin:0 0 1.15em}
.prose h2{margin:1.7em 0 .6em}
.prose section{margin:0}
.prose ul,.prose ol{padding-left:1.3em;margin:0 0 1.2em}
.prose li{margin-bottom:.45em}
details{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin-bottom:10px}
details summary{cursor:pointer;font-weight:600}
details p{margin:.7em 0 0;color:var(--muted)}
.aside{background:rgba(86,211,100,.07);border:1px solid rgba(86,211,100,.3);border-radius:var(--radius);padding:18px 22px;margin:30px 0}
.aside h2{margin-top:0;font-size:1.1rem;color:var(--accent)}
.aside ul{margin:0;padding-left:1.2em}
.tagrow{margin-top:26px}
.related{margin-top:44px}
.pager{display:flex;justify-content:space-between;gap:16px;margin:34px 0 10px;color:var(--muted);font-size:.92rem;flex-wrap:wrap}
.how{background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius);padding:30px 28px}
.how-intro{color:var(--muted)}
.steps{list-style:none;padding:0;margin:18px 0 8px;display:grid;gap:16px}
.steps li{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.steps h3{margin:0 0 6px;font-size:1rem}
.steps p{margin:0;color:var(--muted);font-size:.94rem}
.foot{border-top:1px solid var(--line);margin-top:60px;padding:30px 0 40px;color:var(--muted)}
.fine{font-size:.85rem;color:var(--muted)}
.button{display:inline-block;background:var(--accent);color:#06130a;font-weight:700;padding:10px 18px;border-radius:10px}
.empty{color:var(--muted)}
"""


def favicon_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0b0f14"/>
<path d="M14 44 L30 22 L38 34 L50 16" stroke="#56d364" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="50" cy="16" r="5" fill="#58a6ff"/>
</svg>
"""


# ------------------------------------------------------------------ build

def build_site(posts: List[dict], state: dict) -> dict:
    """Render every page into SITE_DIR. Returns a build summary."""
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "static").mkdir(exist_ok=True)
    (SITE_DIR / "static" / "covers").mkdir(exist_ok=True)
    (SITE_DIR / "posts").mkdir(exist_ok=True)
    (SITE_DIR / "tags").mkdir(exist_ok=True)

    posts = sorted(posts, key=lambda p: p.get("created", ""), reverse=True)
    written = 0

    def w(path: Path, content: str) -> None:
        nonlocal written
        path.write_text(content, encoding="utf-8")
        written += 1

    # static assets
    w(SITE_DIR / "static" / "style.css", CSS)
    w(SITE_DIR / "static" / "favicon.svg", favicon_svg())

    stats = {
        "posts": len(posts),
        "keywords": len(state.get("keywords_seen", {})),
        "runs": state.get("runs_total", 0),
        "refreshes": state.get("counters", {}).get("posts_refreshed", 0),
    }

    for i, p in enumerate(posts):
        # cover image
        w(SITE_DIR / "static" / "covers" / f"{p['slug']}.svg",
          make_cover(p["slug"], p["title"], SITE["name"], SITE["short"]))
        older = posts[i + 1] if i + 1 < len(posts) else None
        newer = posts[i - 1] if i > 0 else None
        related = []
        for q in posts:
            if q["slug"] == p["slug"]:
                continue
            shared = set(q.get("tags", [])) & set(p.get("tags", []))
            if shared and len(related) < 3:
                related.append(q)
        w(SITE_DIR / "posts" / f"{p['slug']}.html", render_post(p, related, older, newer))

    w(SITE_DIR / "index.html", render_home(posts, stats))
    for tag in sorted({t for p in posts for t in p.get("tags", [])}):
        tag_posts = [p for p in posts if tag in p.get("tags", [])]
        w(SITE_DIR / "tags" / f"{tag}.html", render_tag(tag, tag_posts))

    w(SITE_DIR / "404.html", render_404())
    w(SITE_DIR / "feed.xml", seo.rss(posts))
    w(SITE_DIR / "sitemap.xml", seo.sitemap(posts))
    w(SITE_DIR / "robots.txt", seo.robots())

    return {"pages": written, "posts": len(posts), "site_dir": str(SITE_DIR)}
