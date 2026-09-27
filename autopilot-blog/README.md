# The Free Stack — a blog that runs itself

> An **autonomous blog** that researches its own keywords, writes its own posts,
> does its own SEO, posts to social media by itself, and re-publishes on a
> schedule — built **entirely from free, public or open-source resources**.
> No paid APIs. No paid hosting. No paid plugins. Python standard library only.

The engine lives in this folder (`autopilot-blog/`). Every day, a free
GitHub Actions cron wakes it up, it writes new posts about the free & open
tools it covers, commits the rebuilt static site, and GitHub Pages deploys it —
the public blog updates itself.

**Try it now (no setup needed):**

```bash
cd autopilot-blog
python3 -m autopilot run --posts 2     # one full cycle: research -> write -> seo -> publish -> social
python3 -m autopilot publish           # (re)build the static site in site/
# then point any static host (or: python3 -m http.server) at site/
```

---

## What it does, end to end

```
 ┌────────────┐   ┌───────────┐   ┌──────────┐   ┌───────────┐   ┌──────────────┐
 │  1. KEY-   │   │ 2. WRITE  │   │ 3. SEO   │   │ 4. PUBLISH│   │ 5. SOCIAL    │
 │  WORD      │──▶│           │──▶│          │──▶│           │──▶│              │
 │  RESEARCH  │   │           │   │          │   │           │   │              │
 └────────────┘   └───────────┘   └──────────┘   └───────────┘   └──────────────┘
 free, keyless    template writer  meta tags     static HTML     RSS + free
 suggest APIs     or free-tier     JSON-LD       in site/        channels:
 (Google/DDG/     LLM, fallback    sitemaps      -> GitHub       Discord,
 Bing)            to template      robots, RSS   Pages (free)    Telegram,
                  from a curated               -> committed     Mastodon,
                  fact base                          -> deployed  Bluesky
```

1. **Keyword research** — expands ~14 seed topics through the *free, keyless
   autocomplete endpoints* behind Google, DuckDuckGo and Bing search boxes
   (the same feeds a human sees while typing), two levels deep, then scores
   candidates by cross-source agreement, suggestion position and niche fit.
   If the endpoints are unreachable it falls back to a bundled suggestion
   tree, so the pipeline never dead-ends.
2. **Writing** — the winning keyword is matched to a curated, source-cited
   fact base (`content/facts/*.json`, 42 facts) and an article is composed:
   title, intro, 4 H2 sections, 3-question FAQ, key takeaways, source list.
   Two backends: an open-source **template writer** (default, zero cost,
   deterministic per seed) or any **OpenAI-compatible LLM** — Google Gemini's
   free tier, Groq's free tier, OpenRouter `:free` models, or a local Ollama
   server. If the LLM fails, it silently falls back to the template writer.
3. **Self-editing** — on each run it can re-compose the oldest posts with a
   fresh seed (`--refresh`), so the blog *updates* itself over time
   ("updated ×N" badge, `dateModified` bumped, re-queued to social).
4. **SEO** — per post: title/meta/canonical, Open Graph + Twitter cards,
   `Article` + `FAQPage` + `BreadcrumbList` JSON-LD, deterministic SVG cover
   image; per site: `sitemap.xml`, `robots.txt`, RSS feed, tag archives with
   internal linking. Every post is scored by a built-in audit (title length,
   description length, depth, FAQ, sources…) — see `python -m autopilot audit`.
5. **Publishing** — everything renders to a dependency-free static site in
   `site/` (relative links, works from any sub-path). Committed to the repo,
   it deploys automatically to **GitHub Pages** (free) — or Cloudflare Pages,
   Netlify, any nginx box.
6. **Social media management** — each published/refreshed post is queued and
   flushed to the channels you've configured, all free:

   | channel  | what you need (all free)                          |
   |----------|---------------------------------------------------|
   | RSS      | nothing — `feed.xml` is part of the site          |
   | Discord  | a webhook URL (server settings → integrations)    |
   | Telegram | a bot token from @BotFather + a chat id           |
   | Mastodon | any instance + an app access token                |
   | Bluesky  | your account + an app password (AT Protocol)      |

   Unconfigured channels are skipped, never fatal. Failures are retried on the
   next run (the queue persists in `data/`).

### Self-updating for real (the $0 cron)

`.github/workflows/autopilot.yml` (at the repo root) runs the engine **daily at
06:17 UTC** — GitHub Actions is free for public repos (unlimited minutes) —
then commits `autopilot-blog/data` and `autopilot-blog/site`. If the repo has
GitHub Pages pointed at `autopilot-blog/site/`, the public blog redeploy
automatically. You can also trigger it manually from the Actions tab
(`workflow_dispatch`, with inputs for how many posts to write).

```
Actions cron ──▶ research ──▶ write ──▶ audit ──▶ build site/
      ▲                                 └─▶ commit ──▶ GitHub Pages ──▶ public blog
      └──────────── next day ◀─────────────────┘
```

---

## Free resources used (and why they're free)

| capability          | resource                                              | cost |
|---------------------|-------------------------------------------------------|------|
| keyword research    | Google / DuckDuckGo / Bing autocomplete endpoints (keyless, unofficial) | $0 |
| writing             | stdlib Python template engine; optional Gemini/Groq/OpenRouter/Ollama free tiers | $0 |
| hosting             | GitHub Pages (or Cloudflare Pages / Netlify free tiers) | $0 |
| CI / cron           | GitHub Actions (free, unlimited minutes, public repo) | $0 |
| domain (optional)   | `is-a.dev` free custom domain, or `eu.org` free subdomain, or the Pages URL | $0 |
| social posting      | RSS (built-in), Discord webhooks, Telegram Bot API, Mastodon API, Bluesky AT Protocol | $0 |
| search visibility   | Google Search Console + Bing Webmaster Tools (free)   | $0 |
| structured data     | Schema.org / JSON-LD (open standard)                  | $0 |
| fonts / images      | system font stack; deterministic generated SVG covers | $0 |

A note on the autocomplete endpoints: they are public feeds with no key, used
here politely (one request per query, short timeout, offline fallback). They're
unofficial and can change — the engine treats any of the three failing as
normal and only needs at least one to answer.

## Quick start

Requires **Python ≥ 3.9**. No pip installs — standard library only.

```bash
cd autopilot-blog

python3 -m autopilot research              # see what the keyword research finds
python3 -m autopilot run --posts 2         # full cycle: writes 2 posts, builds site, flushes social
python3 -m autopilot run --posts 2 --refresh 1    # + self-edit one oldest post
python3 -m autopilot write --keyword "free weather api"   # force one topic
python3 -m autopilot publish               # rebuild site/ from saved articles
python3 -m autopilot audit                 # SEO score for every post
python3 -m autopilot social                # flush the social queue now
python3 -m autopilot stats                 # library statistics
python3 -m autopilot run --posts 1 --loop --interval 3600 # run forever, hourly
```

Then serve `site/` — `python3 -m http.server 8123` inside `site/` is enough to
look around; for the real thing, deploy `site/` to GitHub Pages:

1. Repo **Settings → Pages → Build and deployment → Source: Deploy from a branch**
2. Branch `main`, folder `/autopilot-blog/site` → Save
3. The blog is live at `https://<you>.github.io/<repo>/autopilot-blog/site/`
   (for a cleaner URL, put the project in a dedicated repo named after the
   site, or map a free domain — below)

### Free domain options

* **is-a.dev** — `you.is-a.dev`, free, instant, points at GitHub Pages
  (add the CNAME in Pages settings). Best option.
* **eu.org** — genuinely free subdomain, manual approval (days–weeks).
* **The Pages URL itself** — free forever, no setup.

### Making it truly hands-off (5 minutes of setup)

1. Keep the workflow (already in `.github/workflows/autopilot.yml`) — it runs
   daily and pushes content. Nothing else to configure.
2. *(Optional)* add repo **secrets** to upgrade the engine:

   | secret | unlocks |
   |---|---|
   | `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` | real LLM prose (free tiers: Gemini `https://generativelanguage.googleapis.com/v1beta/openai`, Groq `https://api.groq.com/openai/v1`, OpenRouter `https://openrouter.ai/api/v1` + a `:free` model, or local Ollama) |
   | `DISCORD_WEBHOOK_URL` | posts to your Discord server |
   | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | posts to your Telegram channel/chat |
   | `MASTODON_INSTANCE`, `MASTODON_ACCESS_TOKEN` | posts to your Mastodon instance |
   | `BSKY_HANDLE`, `BSKY_APP_PASSWORD` | posts to your Bluesky account |
   | `SITE_URL` | final absolute URL for canonical/sitemap/OG tags |

   Local development uses the same variables (see `.env.example`).

3. *(Optional)* verify the site in **Google Search Console** (free) and
   submit `sitemap.xml` — that's the whole "SEO setup".

### The state model (why it's resumable)

`data/state.json` (committed) holds everything the loop needs to continue:
keywords already published, posts metadata, the social queue, run counters.
Each run only acts on *new* keywords, so runs are idempotent — daily cron,
manual triggers and local experiments can all mix without duplicating content.

## Project layout

```
autopilot-blog/
├── autopilot/            # the engine (stdlib only)
│   ├── keywords.py       # free suggest-endpoint research + scoring + offline fallback
│   ├── writer.py         # template writer + OpenAI-compatible LLM backend + self-refresh
│   ├── seo.py            # meta, JSON-LD, sitemap, robots, RSS, audit
│   ├── site.py           # static site renderer (dark theme, cards, FAQ, tags)
│   ├── social.py         # RSS/Discord/Telegram/Mastodon/Bluesky channels + queue
│   ├── blog.py           # the autopilot orchestrator (run_once / run_loop)
│   ├── cover.py          # deterministic SVG cover images (OG 1200×630)
│   ├── config.py         # site identity, niche tokens, URL
│   ├── state.py          # persistent, committed state
│   └── __main__.py       # CLI (python -m autopilot ...)
├── content/
│   ├── seeds.json        # seed topics the research expands
│   ├── offline_suggestions.json  # fallback suggestion tree (no-network mode)
│   └── facts/            # 42 source-cited fact cards the writer draws from
├── data/                 # committed state + one JSON per article (generated)
├── site/                 # the published static site (generated, deployed)
├── .env.example
└── README.md
.github/workflows/autopilot.yml   # the daily free cron (repo root)
```

## Extending it

* **New topic family** — add a fact card to `content/facts/` (claim, detail,
  steps, tags, `aliases`, source URL) and optionally a seed to `seeds.json`.
  The research, matching, writing, SEO and social loop all pick it up.
* **New social channel** — add one function to `autopilot/social.py`
  (`def ch_name(item) -> (ok, msg)`) and register it in `CHANNELS`.
* **Different LLM** — set the three `LLM_*` env vars to any
  OpenAI-compatible endpoint; no code changes.
* **Clone the whole blog** — fork this repo. You get a working autonomous
  blog that replicates itself: same engine, same free stack, your identity in
  `autopilot/config.py` (name, tagline, URL).

## Fair-use & ethics

* Suggest endpoints are hit politely and cached per query; the engine works
  fully offline without them.
* LLM-written content is clearly machine-assisted: the byline says so, and the
  footer links the engine source. Keep factual claims tied to the cited sources
  in `content/facts/` — that's what the fact base is for.
* Respect each social platform's posting limits; the engine rate-limits
  outbound posts by default.
