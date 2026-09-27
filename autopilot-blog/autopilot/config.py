"""Central configuration for The Free Stack — an autonomous blog engine.

Everything in this project runs on free & open resources:

  * keyword research : free, keyless autocomplete endpoints (Google / DuckDuckGo / Bing)
  * content writing  : open-source template writer (stdlib only), or any OpenAI-compatible
                       LLM endpoint that has a free tier (Gemini, Groq, OpenRouter, Ollama...)
  * seo              : generated meta tags, JSON-LD, sitemap.xml, robots.txt, RSS
  * hosting          : static output in ``site/`` -> GitHub Pages / Cloudflare Pages / Netlify
  * social media     : free channels: RSS, Discord webhook, Telegram bot, Mastodon, Bluesky
  * self-updating    : GitHub Actions cron (free for this public repo) re-runs the engine
                       daily and commits new posts, which deploys the site automatically.

No pip dependencies. Python >= 3.9 standard library only.
"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content"
FACTS_DIR = CONTENT_DIR / "facts"
DATA_DIR = BASE_DIR / "data"
POSTS_DATA_DIR = DATA_DIR / "posts"
SITE_DIR = BASE_DIR / "site"


def _site_url() -> str:
    """Absolute base URL of the published site (used for canonical/sitemap/OG tags).

    Default assumes this repo is published to GitHub Pages from the ``/autopilot-blog/site``
    subdirectory. Override with the SITE_URL env var once the site is live somewhere.
    """
    url = os.environ.get("SITE_URL", "").strip()
    if not url:
        user = os.environ.get("GITHUB_PAGES_USER", "abhishekghosh19")
        repo = os.environ.get("GITHUB_PAGES_REPO", "Abhishek-s-Repository-")
        url = f"https://{user}.github.io/{repo}/autopilot-blog/site"
    return url.rstrip("/")


SITE = {
    "name": "The Free Stack",
    "tagline": (
        "An autonomous blog about building things on free & open tools. "
        "It researches its own keywords, writes the posts, handles the SEO, "
        "and posts to social media by itself."
    ),
    "short": "free & open tools, zero budget",
    "author": "Scribe (an autonomous writing agent)",
    "description": (
        "Practical guides on free APIs, open-source alternatives, free hosting, "
        "domains and no-cost automation — researched, written, optimized and "
        "published by a self-running blog engine."
    ),
    "url": _site_url(),
    "github": (
        "https://github.com/abhishekghosh19/Abhishek-s-Repository-/tree/main/autopilot-blog"
    ),
    "year": "2026",
    # Tokens used to judge whether a researched keyword fits this blog's niche.
    "niche_tokens": [
        "free", "open", "source", "opensource", "self-host", "selfhost", "self",
        "host", "hosting", "api", "apis", "blog", "static", "domain", "domains",
        "automation", "cron", "seo", "rss", "github", "python", "llm", "ai",
        "telegram", "bot", "b", "scraping", "data", "alternative", "alternatives",
        "website", "websites", "freeapi", "tier", "limit", "limits", "no-cost",
    ],
}
