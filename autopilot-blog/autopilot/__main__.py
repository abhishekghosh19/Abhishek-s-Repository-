"""Command-line interface for The Free Stack autopilot.

Examples
--------
    python -m autopilot research                 # keyword research only
    python -m autopilot write --keyword "free api for developers"
    python -m autopilot run --posts 2            # one full autopilot cycle
    python -m autopilot run --posts 2 --refresh 1 --loop --interval 3600
    python -m autopilot publish                  # rebuild the static site
    python -m autopilot social                   # flush the social queue
    python -m autopilot audit                    # SEO audit of the library
    python -m autopilot stats                    # library statistics
"""
from __future__ import annotations

import argparse
import json
import sys


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="autopilot", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("research", help="run keyword research (free endpoints, offline fallback)")
    sp.add_argument("--top", type=int, default=30)

    sp = sub.add_parser("write", help="write one article (for a keyword, or the best fresh one)")
    sp.add_argument("--keyword", help="specific keyword to write about")
    sp.add_argument("--backend", choices=["auto", "template", "llm"], default="auto")
    sp.add_argument("--no-publish", action="store_true")

    sp = sub.add_parser("run", help="one full autopilot cycle: research->write->seo->publish->social")
    sp.add_argument("--posts", type=int, default=2)
    sp.add_argument("--refresh", type=int, default=0, help="also self-edit N oldest posts")
    sp.add_argument("--backend", choices=["auto", "template", "llm"], default="auto")
    sp.add_argument("--keyword", help="force one specific keyword into this run")
    sp.add_argument("--loop", action="store_true", help="keep running instead of exiting")
    sp.add_argument("--interval", type=int, default=86400, help="seconds between runs in --loop mode")
    sp.add_argument("--max-runs", type=int, default=0)
    sp.add_argument("--json", action="store_true", help="print machine-readable report")

    sub.add_parser("publish", help="rebuild the static site from saved articles")
    sp = sub.add_parser("social", help="flush the social queue now")
    sp.add_argument("--dry-run", action="store_true")
    sub.add_parser("audit", help="SEO audit of every post")
    sub.add_parser("stats", help="library statistics")

    args = p.parse_args(argv)

    if not args.cmd:
        p.print_help()
        return 0

    from . import blog, keywords as kw, seo, site, social
    from .state import load_posts, load_state, save_state

    if args.cmd == "research":
        res = kw.research()
        print(f"mode={res['mode']} keywords={len(res['keywords'])} (queried {res['queries']} suggest requests)")
        for k in res["keywords"][: args.top]:
            print(f"  {k['score']:>5.2f}  L{k['level']}  {k['phrase']}   ({', '.join(k['sources'])})")
        return 0

    if args.cmd == "write":
        state = load_state()
        existing = set(load_posts().keys())
        if args.keyword:
            k = {"phrase": args.keyword, "parents": [], "score": 0, "level": 0, "sources": ["manual"], "positions": {}}
        else:
            res = kw.research()
            fresh = kw.new_keywords(res, state, limit=1)
            if not fresh:
                print("no fresh keywords found (all already used). Use --keyword to force one.")
                return 1
            k = fresh[0]
            state["last_run_at"] = blog.now_iso()
            state["runs_total"] = state.get("runs_total", 0) + 1
        article = blog.write_article(k, existing, backend=args.backend)
        blog.save_post(article)
        state["posts"][article["slug"]] = {
            "title": article["title"], "created": article["created"], "updated": article["updated"],
            "tags": article["tags"], "words": article["words"], "backend": article["backend"],
        }
        state["processed_keywords"].append(k["phrase"])
        state["social_queue"].append(social.queue_item(article, "published"))
        if not args.no_publish:
            site.build_site(load_posts().values(), state)
        save_state(state)
        print(f"wrote posts/{article['slug']}.html  ({article['words']} words, {article['reading_time']} min, backend={article['backend']})")
        return 0

    if args.cmd == "run":
        if args.loop:
            blog.run_loop(posts=args.posts, refresh=args.refresh, backend=args.backend,
                          interval=args.interval, max_runs=args.max_runs)
            return 0
        rep = blog.run_once(posts=args.posts, refresh=args.refresh, backend=args.backend,
                            force_keyword=args.keyword)
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            blog._print_report(rep)
        return 0 if not rep["errors"] else 2

    if args.cmd == "publish":
        state = load_state()
        summary = site.build_site(load_posts().values(), state)
        print(f"built {summary['pages']} pages ({summary['posts']} posts) in {summary['site_dir']}")
        return 0

    if args.cmd == "social":
        state = load_state()
        if args.dry_run:
            for item in state.get("social_queue", []):
                print(f"would post [{item['kind']}] {item['title']}")
        else:
            results = social.flush_queue(state)
            save_state(state)
            for r in results:
                chs = ", ".join(f"{k}: {v}" for k, v in r.get("channels", {}).items()) or "only rss (built in)"
                print(f"  {r['id']}  ->  {chs}")
        return 0

    if args.cmd == "audit":
        posts = load_posts()
        if not posts:
            print("no posts yet")
            return 1
        total = 0
        for slug, article in sorted(posts.items()):
            a = seo.audit(article)
            total += a["score"]
            mark = "ok " if a["score"] >= 80 else "LOW"
            fails = [c["check"] for c in a["checks"] if not c["ok"]]
            print(f"  [{mark}] {a['score']:>3}  {slug}  {('missing: ' + ', '.join(fails)) if fails else ''}")
        print(f"average score: {round(total / len(posts))}%")
        return 0

    if args.cmd == "stats":
        state = load_state()
        posts = load_posts()
        print(f"posts published : {len(posts)}")
        print(f"keywords tracked: {len(state.get('keywords_seen', {}))}")
        print(f"keywords used   : {len(state.get('processed_keywords', []))}")
        print(f"autonomous runs : {state.get('runs_total', 0)}")
        print(f"self-edits      : {state.get('counters', {}).get('posts_refreshed', 0)}")
        print(f"social queue    : {len(state.get('social_queue', []))} pending item(s)")
        if posts:
            words = sum(a.get("words", 0) for a in posts.values())
            print(f"total words     : {words}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
