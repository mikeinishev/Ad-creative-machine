# Ad Creative Machine

A **7-agent pipeline** that takes a **quiz/sales-funnel URL** and produces **Meta Ads
creatives** end to end — both **static images** and **short-form video**: it crawls the
funnel, extracts marketing intelligence, researches competitor ads, writes creative
briefs, generates the images (Agent 5), and storyboards + renders the videos (Agents 6→7).

**Status:** the full pipeline (Agents 1→7) is built and runnable. Verified on
`100plus.boomerangme.com` (Richie AI restaurant funnel). Static creatives (Agent 5) are
production-grade. **Video text via Veo (Agent 7) is a proven model ceiling — see Gotchas;
that step is currently paused.**

---

## How to initiate ("run the Ad Creative Machine")

Give a funnel URL and run the agents **in order**. Everything runs from the repo
root with the project venv: `.venv/bin/python …`. Slug = the URL host+path (e.g.
`100plus.boomerangme.com`). Intermediate data lands in `outputs/`, screenshots in
`URLs/<slug>/`. Both are gitignored.

```bash
# 1. Agent 1 — crawl the funnel (screenshots every screen, submits a TEST lead,
#    walks to the Stripe paywall). Then vision-analyze the screenshots.
.venv/bin/python agents/design_analyzer/crawl.py "https://<funnel-url>"
.venv/bin/python agents/design_analyzer/analyze.py URLs/<slug>
#    → outputs/analysis/design_<slug>_<ts>.json

# 2. Agent 2 — Marketing Analyst. NO external API: the script only builds the
#    context bundle; the CODING AGENT (this session, max model — Opus 4.8 1M)
#    reads it and WRITES outputs/analysis/marketing_<slug>_<ts>.json.
.venv/bin/python agents/marketing_analyst/analyze.py URLs/<slug>
#    → bundle: outputs/analysis/_marketing_context_<slug>.md → agent writes marketing JSON

# 3. Agent 3 — Competitor Intel (Apify Meta Ad Library, US) + OpenAI vision.
.venv/bin/python agents/competitor_intel/run.py outputs/analysis/marketing_<slug>_<ts>.json
#    → outputs/competitor_intel/data_<slug>_<ts>.json (+ creatives/)

# 4. Agent 4 — Creative Strategist. NO external API: builds the strategy bundle;
#    the CODING AGENT writes outputs/briefs/creative_briefs_<slug>_<ts>.json.
.venv/bin/python agents/creative_strategist/synthesize.py <slug>
#    → bundle: outputs/briefs/_strategy_context_<slug>.md → agent writes briefs JSON

# 5. Agent 5 — Designer (gpt-image-2). APPROVAL FLOW:
#    a) concepts in LOW quality (base format only, all A/B/C hooks) → review/approve
.venv/bin/python agents/designer/generate.py --briefs <slug> --phase concept
#    b) AFTER approval → resizes in HIGH quality (all other placements)
.venv/bin/python agents/designer/generate.py --briefs <slug> --phase resize --skip-existing
#    → outputs/creatives/<brief_id>/<placement>_<A|B|C>.png
```

---

## The agents

| # | Agent | Dir | Input | Output | Engine |
|---|-------|-----|-------|--------|--------|
| 1 | **Design Analyzer** | `agents/design_analyzer` | funnel URL | screenshots + `design_<slug>.json` | Playwright + OpenAI vision |
| 2 | **Marketing Analyst** | `agents/marketing_analyst` | crawl | `marketing_<slug>.json` | **session model (Opus 4.8), no API** |
| 3 | **Competitor Intel** | `agents/competitor_intel` | marketing JSON | `data_<slug>.json` + creatives | Apify Meta Ad Library (US) + OpenAI vision |
| 4 | **Creative Strategist** | `agents/creative_strategist` | 1+2+3 outputs | `creative_briefs_<slug>.json` | **session model (Opus 4.8), no API** |
| 5 | **Designer** | `agents/designer` | briefs | `<placement>_<variant>.png` | OpenAI **gpt-image-2** (Responses background mode) |
| 6 | **Video Storyboard** | `agents/video_storyboard` | briefs (Agent 4) | `storyboards_<slug>.json` | **session model (Opus 4.8), no API** |
| 7 | **Video Producer** | `agents/video_producer` | storyboards (Agent 6) | `<platform>.mp4` | **Google Veo 3** (submit→poll→download) + ffmpeg |

Flow is linear (each agent consumes the previous). Agent 4 is the fan-in (merges
design + marketing + competitor); Agents 5 (static images) and 6 (video storyboards)
both branch off Agent 4's briefs, and Agent 7 renders Agent 6's storyboards into video.
Each agent dir has an `AGENT_PROMPT.md` with the authoritative spec.

**Agent 6** converts the static concepts into shot-by-shot short-form VIDEO storyboards
+ scripts for TikTok / YouTube Shorts / Meta Reels, built on Google Veo 3's 8-second beat
grid. Each shot carries a `veo_prompt`, the exact `on_screen_text`, and a `veo_text_treatment`
(cinematic typography look) so **Agent 7 renders ALL text IN-SCENE via Veo — no post overlays**.
```bash
.venv/bin/python agents/video_storyboard/synthesize_video.py <slug>   # → session model writes storyboards JSON
#    → bundle: outputs/storyboards/_storyboard_context_<slug>.md
#    → agent writes outputs/storyboards/storyboards_<slug>_<ts>.json (9:16 master + per-platform cuts)
```
Specs: `agents/video_storyboard/video_specs.py` + `shared/VIDEO_ADS_SPEC.md` (+ full research
in `shared/video_ad_playbook.json`).

**Agent 7** renders the storyboards into platform MP4s with **Google Veo 3** (submit→poll→
download, like Agent 5's background mode) + ffmpeg. One Veo render per `clip_id` (8s grid),
trim → concat → per-platform export. **All text is generated in-camera by Veo** (cinematic
typography from `veo_text_treatment` + `on_screen_text`) — no overlays. Needs `GEMINI_API_KEY`/
`GOOGLE_API_KEY` + `ffmpeg`.
```bash
.venv/bin/python agents/video_producer/produce.py <slug> --dry-run    # production plan, no render
.venv/bin/python agents/video_producer/produce.py <slug>              # live Veo render → outputs/videos/<brief_id>/
```

---

## Key principles (do it this way)

- **Agents 2, 4 & 6 do NOT call any external LLM API.** Their `analyze.py`/`synthesize.py`/
  `synthesize_video.py` only assemble a complete context bundle; the **Claude Code session
  model itself (always the strongest available — currently Opus 4.8, 1M context)** performs
  the analysis and writes the JSON. No char/token caps. If a stronger model is available,
  use it.
- **Agent 5 uses gpt-image-2 via the Responses API `background` mode** (submit → poll
  → fetch), NOT synchronous `images.generate`. Submit all jobs up front → they render
  server-side in parallel → poll. This avoids the ~60s synchronous-connection reset
  wall (15 creatives, 0 fails, ~76s).
- **Approval flow for creatives:** concepts first in **low** quality (fast/cheap,
  `--phase concept`) → refine copy/design with the user → **resizes in high** quality
  after approval (`--phase resize`). `--quality` default is phase-aware
  (concept→low, resize→high, all→medium).
- **Cohesive single image** is the default — gpt-image-2 designs the whole ad with the
  text built in (`--text-mode model`). `--text-mode composite` is a Pillow-overlay
  fallback. **Minimal copy:** one bold headline (the hook) + one short money-focused
  line (≤~12 words, the brief's `subhead`) + a CTA button. No paragraphs.
- **A/B/C hook variations** per concept → `<placement>_<A|B|C>.png`.
- **Market = US only** for now (Canada intentionally excluded).
- Agent 2 is the source of truth for **what/where Agent 3 searches**
  (`market_targeting.niche/geo` + `competitor_research.search_queries` +
  `exclude_brand_terms`).
- **Proven winner = the "radius magnet" angle** (`brief_002`): *"100 customers are around
  you. We bring them all. In 14 days. Guaranteed — or you pay $0."* — geo-proximity demand +
  14-day deadline + $0 risk-reversal, badge "Restaurant Owner?", CTA "Check if my area is
  open". This real ad drove 2 sales from minimal traffic; lean on it.
- **Style-variant briefs** (`outputs/briefs/radius_variations.json`) carry ONE angle across
  visually distinct treatments (RV1 superrealism aerial, RV2 clean SaaS minimal, RV3 tech
  radar/HUD, RV4 lifestyle owner, RV5 editorial red). When the user wants "more variety,"
  vary `visual_concept` + `color_scheme`, not the offer. RV1/RV2/RV3 shipped in HIGH across
  4:5 / 1:1 / 9:16.

---

## Gotchas (learned the hard way)

- **gpt-image-2 sizes must be divisible by 16** (longest edge ≤ 3840). Meta's 1080
  sizes aren't, so we generate at a ÷16 size then resize to the exact Meta target.
  See `agents/designer/meta_placements.py` (Meta 2026 spec, single source of truth).
- **gpt-image-2 moderation** resets the connection (~60s, reproducible) on income/$
  claims or brand/UI-label phrasing ("Meta ad card", labeled nodes). Mitigations are
  built in: scene prompts pre-softened, failed jobs auto-resubmit softened; for a
  reproducible block, rephrase the brief's `visual_concept`/copy.
- **Apify actor `curious_coder/facebook-ads-library-scraper` is pay-per-result,
  minimum 10.** It takes multiple `urls` in one run with a shared `count` (cheaper).
  Niche-anchor the queries or results go off-topic.
- **macOS framework Python + urllib has no usable CAs** → use `certifi` for the SSL
  context (done in `competitor_intel/run.py`).
- **Each crawl submits a real TEST lead** to the connected CRM (authorized). Default
  identity: `test.sobaka@gmail.com`, `+13234442211`, "Test Tester" (override with
  `--email/--phone/--name`). It stops AT the paywall — never pays.
- **Veo 3 text rendering is a proven model ceiling (Agent 7).** Across 5+ prompt iterations
  + an automated `--qa` re-render loop, Veo reliably renders SHORT (≤3-word) titles but with
  per-take stochastic spelling glitches ("Owner"→"Ower", "Guests"→"Guestess") and
  hallucinated prop/background text. All-Veo perfect text is irreducible; the only
  zero-variance path is an animated motion-graphics overlay (rejected aesthetically — looks
  "ублюдски"). Mitigations baked into `produce.py` (≤3-word steady titles, one large
  title-card in open frame, heavy bokeh, strip prop text, strong negative_prompt) raise the
  hit rate but don't guarantee it. **Video is paused; static (Agent 5) is the reliable path.**
- **Veo video-gen quota is tight/separate** — 429 RESOURCE_EXHAUSTED after ~10+ renders in a
  session (separate from text quota). Re-run `produce.py <slug> --master-only --qa` after reset.

---

## Env / deps

- Secrets in `.env` (gitignored): `OPENAI_API_KEY`, `APIFY_TOKEN`/`APIFY_API_TOKEN`,
  `FIGMA_TOKEN`, and `GEMINI_API_KEY`/`GOOGLE_API_KEY` (Veo 3, Agent 7 —
  `AIzaSyCiTEPTz6ZjxLfqQAyXw0d6SSz_ev0udC0`; also in the macOS keychain as `GEMINI_API_KEY`).
- Python venv at `.venv`. Deps: `playwright` (+ `playwright install chromium`),
  `openai`, `Pillow`, `certifi` (Agents 1–5); `google-genai` (Veo 3, Agent 7). See
  `agents/designer/requirements.txt` + `agents/video_producer/requirements.txt`.
- **System dep (not pip): `ffmpeg` on PATH** (`brew install ffmpeg`) for Agent 7
  trim/concat/export. The installed ffmpeg 8.1 has no `drawtext` filter — not relied on
  (all video text is rendered in-scene by Veo).
- Generated artifacts (`outputs/`, `URLs/`), `inputs/`, `.venv`, `__pycache__` are
  gitignored.

## File map

```
agents/
  design_analyzer/   crawl.py, analyze.py
  marketing_analyst/ analyze.py            (context builder; session model writes JSON)
  competitor_intel/  run.py
  creative_strategist/ synthesize.py       (context builder; session model writes JSON)
  designer/          generate.py, compositor.py, meta_placements.py, requirements.txt
  video_storyboard/  synthesize_video.py, video_specs.py   (context builder; session model writes JSON)
  video_producer/    produce.py, veo_client.py, requirements.txt   (Veo 3 + ffmpeg)
shared/              schemas/, META_ADS_SPEC.md, VIDEO_ADS_SPEC.md, video_ad_playbook.json
outputs/   analysis/ competitor_intel/ briefs/ creatives/ storyboards/ videos/   (gitignored)
URLs/<slug>/         per-funnel screenshots + manifest + page_text    (gitignored)
```
