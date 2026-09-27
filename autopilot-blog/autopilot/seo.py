"""SEO machinery — all free, standards-based.

  * on-page meta: title, meta description, canonical, Open Graph, Twitter card
  * structured data: JSON-LD (Article, FAQPage, BreadcrumbList) per Schema.org
  * sitemap.xml + robots.txt generation
  * RSS 2.0 feed
  * an audit that scores every post (title length, description length, depth, FAQ...)

Search engines themselves (Google Search Console, Bing Webmaster Tools) are free
services the owner can wire up once the site is live — see README.
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from email.utils import format_datetime
from typing import Dict, List

from .config import SITE


def _post_url(slug: str) -> str:
    return f"{SITE['url']}/posts/{slug}.html"


def meta_tags(article: dict) -> Dict[str, str]:
    title = f"{article['title']} | {SITE['name']}"
    desc = article.get("meta_description") or article.get("meta_description_fallback", SITE["description"])
    url = _post_url(article["slug"])
    cover = f"{SITE['url']}/static/covers/{article['slug']}.svg"
    return {
        "title": title,
        "description": desc,
        "canonical": url,
        "og_title": article["title"],
        "og_description": desc,
        "og_url": url,
        "og_image": cover,
        "og_type": "article",
        "twitter_card": "summary_large_image",
    }


def json_ld(article: dict) -> List[dict]:
    url = _post_url(article["slug"])
    pub = article.get("created")
    mod = article.get("updated") or pub
    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["title"],
        "description": article.get("meta_description", ""),
        "datePublished": pub,
        "dateModified": mod,
        "author": {"@type": "Organization", "name": SITE["author"], "url": SITE["github"]},
        "publisher": {
            "@type": "Organization",
            "name": SITE["name"],
            "logo": {"@type": "ImageObject", "url": f"{SITE['url']}/static/favicon.svg"},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "image": f"{SITE['url']}/static/covers/{article['slug']}.svg",
        "keywords": ", ".join(article.get("keywords", [])),
        "articleSection": ", ".join(article.get("tags", [])),
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q["question"],
                "acceptedAnswer": {"@type": "Answer", "text": q["answer"]},
            }
            for q in article.get("faq", [])
        ],
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["url"] + "/"},
            {"@type": "ListItem", "position": 2, "name": article["title"], "item": url},
        ],
    }
    out = [article_ld]
    if faq_ld["mainEntity"]:
        out.append(faq_ld)
    out.append(breadcrumb_ld)
    return out


# ------------------------------------------------------------------ audit

def audit(article: dict) -> dict:
    checks = []

    def add(name: str, ok: bool, note: str = ""):
        checks.append({"check": name, "ok": bool(ok), "note": note})

    title = article.get("title", "")
    desc = article.get("meta_description", "")
    add("title-length", 30 <= len(title) <= 65, f"{len(title)} chars")
    add("meta-description", 120 <= len(desc) <= 160, f"{len(desc)} chars")
    add("word-count", article.get("words", 0) >= 550, f"{article.get('words', 0)} words")
    add("h2-sections", len(article.get("sections", [])) >= 3, f"{len(article.get('sections', []))} sections")
    add("faq", len(article.get("faq", [])) >= 3, f"{len(article.get('faq', []))} questions")
    add("takeaways", len(article.get("takeaways", [])) >= 3)
    add("sources", len(article.get("sources", [])) >= 1, f"{len(article.get('sources', []))} linked")
    add("tags", 1 <= len(article.get("tags", [])) <= 6, f"{len(article.get('tags', []))} tags")
    add("slug", 3 <= len(article.get("slug", "")) <= 70)
    passed = sum(1 for c in checks if c["ok"])
    score = round(100 * passed / len(checks))
    return {"score": score, "passed": passed, "total": len(checks), "checks": checks}


# ------------------------------------------------------------------ sitemaps

def _fmt(dt_iso: str) -> str:
    try:
        return datetime.fromisoformat(dt_iso).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return SITE["year"]


def sitemap(posts: List[dict]) -> str:
    base = SITE["url"].rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [
        {"loc": base + "/", "lastmod": now, "priority": "1.0"},
    ]
    for p in posts:
        urls.append(
            {
                "loc": f"{base}/posts/{p['slug']}.html",
                "lastmod": _fmt(p.get("updated") or p.get("created") or now),
                "priority": "0.8",
            }
        )
    for tag in sorted({t for p in posts for t in p.get("tags", [])}):
        urls.append(
            {
                "loc": f"{base}/tags/{tag}.html",
                "lastmod": now,
                "priority": "0.5",
            }
        )
    urls.append({"loc": f"{base}/feed.xml", "lastmod": now, "priority": "0.5"})
    body = "".join(
        f"  <url><loc>{html.escape(u['loc'])}</loc><lastmod>{u['lastmod']}</lastmod><priority>{u['priority']}</priority></url>\n"
        for u in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n"
    )


def robots() -> str:
    return (
        "# The Free Stack — an autonomous blog. All content is generated for public consumption.\n"
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url'].rstrip('/')}/sitemap.xml\n"
    )


def rss(posts: List[dict], limit: int = 20) -> str:
    base = SITE["url"].rstrip("/")
    newest = max((p.get("created", "") for p in posts), default=datetime.now(timezone.utc).isoformat())
    try:
        last_build = format_datetime(datetime.fromisoformat(newest))
    except (ValueError, TypeError):
        last_build = format_datetime(datetime.now(timezone.utc))

    def rfc(dt_iso: str) -> str:
        try:
            return format_datetime(datetime.fromisoformat(dt_iso))
        except (ValueError, TypeError):
            return last_build

    items = []
    for p in posts[:limit]:
        excerpt = (p["intro"][0] if p.get("intro") else p.get("meta_description", ""))[:400]
        cats = "".join(f"<category>{html.escape(t)}</category>" for t in p.get("tags", []))
        link = f"{base}/posts/{p['slug']}.html"
        items.append(
            f"""    <item>
      <title>{html.escape(p['title'])}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{rfc(p.get('created', newest))}</pubDate>
      <description>{html.escape(excerpt)}</description>
      {cats}
    </item>
"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html.escape(SITE['name'])}</title>
    <link>{base}</link>
    <description>{html.escape(SITE['description'])}</description>
    <language>en</language>
    <lastBuildDate>{last_build}</lastBuildDate>
    <atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml"/>
{items}  </channel>
</rss>
"""


def json_ld_script(article: dict) -> str:
    safe_close = "<\\/"
    blocks = []
    for ld in json_ld(article):
        payload = json.dumps(ld, ensure_ascii=False).replace("</", safe_close)
        blocks.append(f'<script type="application/ld+json">{payload}</script>')
    return "".join(blocks)
