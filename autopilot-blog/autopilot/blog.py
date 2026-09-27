"""The autopilot: research -> write -> seo -> publish -> social -> repeat.

``run_once`` is what a human (or the GitHub Actions cron) invokes. It is
idempotent-friendly: it only acts on keywords that have not been used yet, so
running it any number of times never duplicates content.
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from . import keywords as kw
from . import seo, site, social
from .config import SITE
from .state import load_posts, load_state, now_iso, save_last_run, save_post, save_state
from .writer import refresh_article, write_article


def _report_base() -> dict:
    return {
        "at": now_iso(),
        "site": SITE["name"],
        "research_mode": None,
        "researched": 0,
        "new_keywords": [],
        "published": [],
        "refreshed": [],
        "audits": {},
        "social": [],
        "build": None,
        "errors": [],
    }


def _audit_all(posts: Dict[str, dict]) -> Dict[str, dict]:
    return {slug: seo.audit(a) for slug, a in posts.items()}


def run_once(posts: int = 2, refresh: int = 0, backend: str = "auto", force_keyword: Optional[str] = None) -> dict:
    state = load_state()
    rep = _report_base()

    # 1 -- keyword research (free endpoints, offline fallback)
    research = kw.research()
    rep["research_mode"] = research["mode"]
    rep["researched"] = len(research["keywords"])
    state["runs_total"] = state.get("runs_total", 0) + 1
    state["last_run_at"] = now_iso()

    fresh = kw.new_keywords(research, state, limit=max(posts, refresh))
    rep["new_keywords"] = [k["phrase"] for k in fresh]

    existing_slugs = set(load_posts().keys())

    # 2 -- write new articles
    written = 0
    for k in fresh[:posts]:
        try:
            article = write_article(k, existing_slugs, backend=backend)
        except Exception as e:  # noqa: BLE001
            rep["errors"].append(f"write failed for {k['phrase']}: {e}")
            continue
        existing_slugs.add(article["slug"])
        save_post(article)
        state["posts"][article["slug"]] = {
            "title": article["title"],
            "created": article["created"],
            "updated": article["updated"],
            "tags": article["tags"],
            "words": article["words"],
            "backend": article["backend"],
        }
        state["processed_keywords"].append(k["phrase"])
        state["counters"]["posts_published"] = state["counters"].get("posts_published", 0) + 1
        state["social_queue"].append(social.queue_item(article, "published"))
        rep["published"].append(article["slug"])
        written += 1

    # 2b -- optional one-off keyword from the CLI
    if force_keyword:
        k = {"phrase": force_keyword, "parents": [], "score": 0, "level": 0, "sources": ["manual"], "positions": {}}
        article = write_article(k, existing_slugs, backend=backend)
        existing_slugs.add(article["slug"])
        save_post(article)
        state["posts"][article["slug"]] = {
            "title": article["title"],
            "created": article["created"],
            "updated": article["updated"],
            "tags": article["tags"],
            "words": article["words"],
            "backend": article["backend"],
        }
        state["processed_keywords"].append(k["phrase"])
        state["counters"]["posts_published"] = state["counters"].get("posts_published", 0) + 1
        state["social_queue"].append(social.queue_item(article, "published"))
        rep["published"].append(article["slug"])
        written += 1

    # 3 -- self-editing: re-compose the oldest posts (the blog updates itself)
    if refresh > 0:
        posts_all = load_posts()
        oldest = sorted(posts_all.values(), key=lambda a: a.get("created", ""))[:refresh]
        for old in oldest:
            if random.random() < 0.25 and len(posts_all) > 4:
                # occasionally refresh a random mid-blog post instead, for variety
                old = random.choice(list(posts_all.values()))
            try:
                updated = refresh_article(old)
                save_post(updated)
                state["posts"][updated["slug"]]["updated"] = updated["updated"]
                state["posts"][updated["slug"]]["updated_count"] = updated.get("updated_count", 0)
                state["counters"]["posts_refreshed"] = state["counters"].get("posts_refreshed", 0) + 1
                state["social_queue"].append(social.queue_item(updated, "updated"))
                rep["refreshed"].append(updated["slug"])
            except Exception as e:  # noqa: BLE001
                rep["errors"].append(f"refresh failed for {old['slug']}: {e}")

    # 4 -- seo audit of the whole library
    rep["audits"] = {s: a["score"] for s, a in _audit_all(load_posts()).items()}

    # 5 -- publish: rebuild the static site
    try:
        rep["build"] = site.build_site(load_posts().values(), state)
    except Exception as e:  # noqa: BLE001
        rep["errors"].append(f"build failed: {e}")

    # 6 -- social media management
    try:
        rep["social"] = social.flush_queue(state)
    except Exception as e:  # noqa: BLE001
        rep["errors"].append(f"social flush failed: {e}")

    # prune the queue: keep only the 5 most recent items per slug
    state["social_queue"] = _prune_queue(state["social_queue"])

    save_state(state)
    save_last_run(rep)
    rep["posts_total"] = len(state["posts"])
    rep["keywords_pool"] = len(state.get("keywords_seen", {}))
    return rep


def _prune_queue(queue: List[dict], keep: int = 5) -> List[dict]:
    by_slug: Dict[str, List[dict]] = {}
    for item in queue:
        by_slug.setdefault(item["post_slug"], []).append(item)
    keep_ids = set()
    for slug, items in by_slug.items():
        items.sort(key=lambda i: i.get("created", ""), reverse=True)
        for i in items[:keep]:
            keep_ids.add(i["id"])
    return [i for i in queue if i["id"] in keep_ids]


def run_loop(posts: int = 2, refresh: int = 0, backend: str = "auto", interval: int = 86400, max_runs: int = 0) -> None:
    """Run the autopilot forever (or ``max_runs`` times), sleeping between runs."""
    import time

    n = 0
    while True:
        rep = run_once(posts=posts, refresh=refresh, backend=backend)
        _print_report(rep)
        n += 1
        if max_runs and n >= max_runs:
            break
        time.sleep(interval)


# ------------------------------------------------------------------ reporting

def _print_report(rep: dict) -> None:
    line = "=" * 62
    print(f"\n{line}\n  THE FREE STACK — autonomous run @ {rep['at']}\n{line}")
    print(f"  research   : {rep['researched']} keywords ({rep['research_mode']} mode)")
    if rep["new_keywords"]:
        print(f"  new topics : {', '.join(rep['new_keywords'][:6])}")
    if rep["published"]:
        print(f"  published  : {len(rep['published'])} new post(s)")
        for s in rep["published"]:
            print(f"               - posts/{s}.html")
    else:
        print("  published  : none (no fresh keywords this run)")
    if rep["refreshed"]:
        print(f"  self-edits : {', '.join(rep['refreshed'])}")
    if rep.get("build"):
        print(f"  site build : {rep['build']['pages']} pages, {rep['build']['posts']} posts in {rep['build']['site_dir']}")
    scores = rep.get("audits", {})
    if scores:
        avg = round(sum(scores.values()) / len(scores))
        print(f"  seo audit  : {avg}% average across {len(scores)} post(s)")
    channels_ok = set()
    for item in rep.get("social", []):
        for ch, msg in item.get("channels", {}).items():
            if msg.startswith("ok"):
                channels_ok.add(ch)
    if channels_ok:
        print(f"  social     : delivered on {', '.join(sorted(channels_ok))}")
    else:
        print("  social     : no outbound channels configured (RSS feed always on)")
    if rep["errors"]:
        print("  errors     :")
        for e in rep["errors"]:
            print(f"               ! {e}")
    print(f"  totals     : {rep.get('posts_total', 0)} posts, {rep.get('keywords_pool', 0)} keywords tracked\n{line}\n")
