"""Persistent state for the autopilot.

State lives in ``data/`` and is committed to the repo, which is what makes the
engine resumable across free GitHub Actions runs: each scheduled run picks up
exactly where the previous one left off (which keywords were used, which posts
exist, what is still in the social queue).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .config import DATA_DIR, POSTS_DATA_DIR

STATE_PATH = DATA_DIR / "state.json"
LAST_RUN_PATH = DATA_DIR / "last_run.json"

DEFAULT_STATE: Dict[str, Any] = {
    "version": 1,
    "runs_total": 0,
    "last_run_at": None,
    # Keywords the engine has already published a post about.
    "processed_keywords": [],
    # Every keyword ever seen during research (for stats / dedupe of display).
    "keywords_seen": {},
    # slug -> post metadata (the full article is in data/posts/<slug>.json)
    "posts": {},
    # Pending social-media posts: one item per published/refreshed article.
    "social_queue": [],
    "counters": {
        "posts_published": 0,
        "posts_refreshed": 0,
        "social_delivered": 0,
        "social_skipped": 0,
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _blank_state() -> Dict[str, Any]:
    return json.loads(json.dumps(DEFAULT_STATE))


def load_state() -> Dict[str, Any]:
    if STATE_PATH.exists():
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        merged = _blank_state()
        merged.update(data)
        return merged
    return _blank_state()


def save_state(state: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    POSTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_name("state.json.tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, STATE_PATH)


def save_post(article: Dict[str, Any]) -> None:
    POSTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = POSTS_DATA_DIR / f"{article['slug']}.json"
    path.write_text(json.dumps(article, indent=2) + "\n", encoding="utf-8")


def load_posts() -> Dict[str, Dict[str, Any]]:
    """Return {slug: article} for every saved article, newest first by created."""
    if not POSTS_DATA_DIR.exists():
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for p in sorted(POSTS_DATA_DIR.glob("*.json")):
        try:
            out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def save_last_run(report: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LAST_RUN_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
