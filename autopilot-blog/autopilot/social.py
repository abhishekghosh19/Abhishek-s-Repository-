"""Social media management on free channels only.

Every channel below is free and needs no paid API plan:

  channel     what it needs                                   cost
  ----------  --------------------------------------------    -------
  rss         nothing — feed.xml is part of the site          $0
  discord     a webhook URL from any server (webhook creation
              is free)                                        $0
  telegram    a bot token from @BotFather + a chat id         $0
  mastodon    any instance + an app access token              $0
  bluesky     an account + app password (AT Protocol)         $0

Channels are configured purely through environment variables (see .env.example).
Anything unconfigured is skipped with a clear status instead of failing the run,
so the engine works out of the box and grows as credentials are added.

The queue (``state["social_queue"]``) is persistent: a post that failed on a
channel is retried on the next run; an item counts as delivered once every
*configured* channel has accepted it.
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Tuple

from .config import SITE

USER_AGENT = "FreeStackBlog/1.0 (social poster)"
REQUEST_TIMEOUT = 15
RATE_LIMIT_SECONDS = 4  # be polite between outbound posts


def _post_json(url: str, payload: dict, headers: Dict[str, str] = None, method: str = "POST") -> Tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")[:300]
    except urllib.error.HTTPError as e:  # noqa: BLE001 - we want the status
        return e.code, (e.reason or "")[:300]


def _get_json(url: str, headers: Dict[str, str] = None) -> Tuple[int, str]:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")[:300]
    except urllib.error.HTTPError as e:
        return e.code, (e.reason or "")[:300]


# ------------------------------------------------------------------ channels

def ch_rss(item: dict) -> Tuple[bool, str]:
    return True, "listed in feed.xml (built into the site)"


def ch_discord(item: dict) -> Tuple[bool, str]:
    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        return False, "DISCORD_WEBHOOK_URL not set"
    text = item["social_text"][:2000]
    status, _ = _post_json(url, {"content": text})
    return status == 204, f"discord http {status}"


def ch_telegram(item: dict) -> Tuple[bool, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        return False, "TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not set"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    status, body = _post_json(
        url,
        {
            "chat_id": chat,
            "text": item["social_text"][:4000],
            "disable_web_page_preview": False,
        },
    )
    ok = status == 200 and '"ok":true' in body
    return ok, f"telegram http {status}"


def ch_mastodon(item: dict) -> Tuple[bool, str]:
    instance = os.environ.get("MASTODON_INSTANCE", "").strip().rstrip("/")
    token = os.environ.get("MASTODON_ACCESS_TOKEN", "").strip()
    if not instance or not token:
        return False, "MASTODON_INSTANCE/MASTODON_ACCESS_TOKEN not set"
    status, body = _post_json(
        f"{instance}/api/v1/statuses",
        {"status": item["social_text"][:500]},
        headers={"Authorization": f"Bearer {token}"},
    )
    ok = 200 <= status < 300
    return ok, f"mastodon http {status}"


def ch_bluesky(item: dict) -> Tuple[bool, str]:
    handle = os.environ.get("BSKY_HANDLE", "").strip()
    password = os.environ.get("BSKY_APP_PASSWORD", "").strip()
    if not handle or not password:
        return False, "BSKY_HANDLE/BSKY_APP_PASSWORD not set"
    status, body = _post_json(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        {"identifier": handle, "password": password},
    )
    if not (200 <= status < 300):
        return False, f"bluesky auth http {status}"
    try:
        jwt = json.loads(body)["accessJwt"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return False, "bluesky auth: bad response"
    status, body = _post_json(
        "https://bsky.social/xrpc/app.bsky.feed.post",
        {"record": {"$type": "app.bsky.feed.post", "text": item["social_text"][:300]}},
        headers={"Authorization": f"Bearer {jwt}"},
    )
    ok = 200 <= status < 300
    return ok, f"bluesky http {status}"


CHANNELS: Dict[str, object] = {
    "rss": ch_rss,
    "discord": ch_discord,
    "telegram": ch_telegram,
    "mastodon": ch_mastodon,
    "bluesky": ch_bluesky,
}

# Channels that actually need outbound network (rss is local).
NETWORK_CHANNELS = ["discord", "telegram", "mastodon", "bluesky"]


def configured_channels() -> List[str]:
    out = []
    for name in CHANNELS:
        if name == "rss":
            out.append(name)
            continue
        try:
            ok, _ = CHANNELS[name]({"social_text": ""})
        except Exception:
            ok = False
        if ok:
            out.append(name)
    return out


# ------------------------------------------------------------------ queueing

def queue_item(article: dict, kind: str = "published") -> dict:
    """Build a social queue item for an article (idempotent by post+kind)."""
    excerpt = (article.get("intro") or [""])[0]
    if len(excerpt) > 220:
        excerpt = excerpt[:217].rsplit(" ", 1)[0] + "..."
    hashtags = " ".join(f"#{t.replace('-', '')}" for t in article.get("tags", [])[:3])
    suffix = " (updated)" if kind == "updated" else ""
    text = f"{article['title']}\n\n{excerpt}\n\n{article.get('meta_description', '')}\n\n{hashtags}\n{SITE['url']}/posts/{article['slug']}.html{suffix}"
    return {
        "id": f"{article['slug']}:{kind}-{article.get('updated', '')}",
        "post_slug": article["slug"],
        "kind": kind,
        "title": article["title"],
        "social_text": text,
        "created": _now(),
        "status": {name: {"state": "queued"} for name in CHANNELS},
    }


def _now() -> str:
    from .state import now_iso

    return now_iso()


def flush_queue(state: dict) -> List[dict]:
    """Attempt to deliver every queued item on every channel. Returns per-item summaries."""
    results = []
    for item in state.get("social_queue", []):
        item_result = {"id": item["id"], "channels": {}}
        for name in CHANNELS:
            st = item["status"].setdefault(name, {})
            if st.get("state") == "posted":
                continue
            try:
                ok, msg = CHANNELS[name](item)
            except Exception as e:  # noqa: BLE001 - never let one channel kill the run
                ok, msg = False, f"error: {e}"
            st["state"] = "posted" if ok else "skipped" if "not set" in msg or "not configured" in msg else "failed"
            st["attempts"] = st.get("attempts", 0) + (1 if "not set" not in msg else 0)
            st["message"] = msg
            st["at"] = _now()
            if "not set" not in msg:
                item_result["channels"][name] = f"{'ok' if ok else 'fail'} ({msg})"
        if any(v.get("state") == "posted" for v in item["status"].values()):
            state["counters"]["social_delivered"] = state["counters"].get("social_delivered", 0) + 1
        if any(v.get("state") == "failed" for v in item["status"].values()):
            time.sleep(RATE_LIMIT_SECONDS)
        results.append(item_result)
        time.sleep(RATE_LIMIT_SECONDS)
    return results
