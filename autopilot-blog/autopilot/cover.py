"""Deterministic, dependency-free cover images (SVG, 1200x630 — OG size).

Each post gets a gradient derived from a hash of its slug, so the same post
always renders the same cover (important for OG caches and sitemap integrity).
"""
from __future__ import annotations

import hashlib
import html
import re
from typing import List


def _hue(slug: str) -> int:
    return int(hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8], 16) % 360


def _wrap(text: str, max_chars: int, lines: int = 2) -> List[str]:
    words = text.split()
    lines_out: List[str] = []
    current = ""
    for w in words:
        candidate = f"{current} {w}".strip()
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines_out.append(current)
            current = w
        if len(lines_out) == lines:
            break
    if current and len(lines_out) < lines:
        lines_out.append(current)
    if len(lines_out) > lines:
        lines_out = lines_out[:lines]
        lines_out[-1] = lines_out[-1][: max_chars - 1].rstrip() + "…"
    return lines_out


def make_cover(slug: str, title: str, site_name: str, tagline: str) -> str:
    h1 = _hue(slug)
    h2 = (h1 + 45) % 360
    c1 = f"hsl({h1} 70% 46%)"
    c2 = f"hsl({h2} 75% 30%)"
    wrapped = _wrap(title, 26)
    title_y = 300 if len(wrapped) > 1 else 330
    t1 = f'<text x="72" y="{title_y}" font-family="Verdana, Geneva, sans-serif" font-size="58" font-weight="bold" fill="#ffffff">{html.escape(wrapped[0])}</text>'
    t2 = (
        f'<text x="72" y="{title_y + 70}" font-family="Verdana, Geneva, sans-serif" font-size="58" font-weight="bold" fill="#ffffff">{html.escape(wrapped[1])}</text>'
        if len(wrapped) > 1
        else ""
    )
    slug_safe = re.sub(r"[^a-z0-9\-]", "", slug.lower())
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="{html.escape(title)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M 48 0 L 0 0 0 48" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#grid)"/>
  <circle cx="1080" cy="110" r="170" fill="#ffffff" opacity="0.06"/>
  <circle cx="980" cy="540" r="230" fill="#ffffff" opacity="0.05"/>
  <text x="72" y="120" font-family="Verdana, Geneva, sans-serif" font-size="26" font-weight="bold" fill="#ffffff" opacity="0.92">{html.escape(site_name).upper()}</text>
  <rect x="72" y="150" width="120" height="6" rx="3" fill="#ffffff" opacity="0.85"/>
  {t1}
  {t2}
  <text x="72" y="565" font-family="Verdana, Geneva, sans-serif" font-size="22" fill="#ffffff" opacity="0.75">{html.escape(tagline)}  ·  #{html.escape(slug_safe)}</text>
</svg>
"""
