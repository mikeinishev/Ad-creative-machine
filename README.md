# Ad Creative Machine

A **7-agent pipeline** that takes a **quiz/sales-funnel URL** and produces **Meta Ads creatives**
end to end — both **static images** and **short-form video** for TikTok / YouTube Shorts / Meta
Reels. It crawls the funnel, extracts marketing intelligence, researches competitor ads, writes
creative briefs, generates the images, storyboards the videos, and renders them.

> Verified on `100plus.boomerangme.com` (Richie AI restaurant funnel). Operating guide for agents:
> [`CLAUDE.md`](CLAUDE.md).

## 🧠 The agents

| # | Agent | Dir | Input | Output | Engine |
|---|-------|-----|-------|--------|--------|
| 1 | **Design Analyzer** | `agents/design_analyzer` | funnel URL | screenshots + `design_<slug>.json` | Playwright + OpenAI vision |
| 2 | **Marketing Analyst** | `agents/marketing_analyst` | crawl | `marketing_<slug>.json` | **session model (Opus 4.8), no API** |
| 3 | **Competitor Intel** | `agents/competitor_intel` | marketing JSON | `data_<slug>.json` + creatives | Apify Meta Ad Library (US) + OpenAI vision |
| 4 | **Creative Strategist** | `agents/creative_strategist` | 1+2+3 | `creative_briefs_<slug>.json` | **session model (Opus 4.8), no API** |
| 5 | **Designer** | `agents/designer` | briefs | `<placement>_<variant>.png` | OpenAI **gpt-image-2** (Responses background mode) |
| 6 | **Video Storyboard** | `agents/video_storyboard` | briefs (Agent 4) | `storyboards_<slug>.json` | **session model (Opus 4.8), no API** |
| 7 | **Video Producer** | `agents/video_producer` | storyboards (Agent 6) | `<platform>.mp4` | **Google Veo 3** (submit→poll→download) + ffmpeg |

**Flow** is linear. Agent 4 is the fan-in (merges design + marketing + competitor). Agents **5**
(static images) and **6** (video storyboards) both branch off Agent 4's briefs, and Agent **7**
renders Agent 6's storyboards into video.

Agents **2, 4 and 6 do NOT call any external LLM API** — a thin `analyze.py`/`synthesize.py`
builds a complete context bundle, and the **Claude Code session model itself (always the strongest
available — currently Opus 4.8, 1M context)** performs the analysis and writes the JSON.

## 🚀 Run the pipeline

Everything runs from the repo root with the project venv (`.venv/bin/python`). Slug = the URL
host+path (e.g. `100plus.boomerangme.com`). Intermediate data → `outputs/`, screenshots →
`URLs/<slug>/` (both gitignored).

```bash
# 1 — Design Analyzer: crawl the funnel (screenshots every screen, submits a TEST lead, walks to
#     the Stripe paywall) → vision-analyze the screenshots.
.venv/bin/python agents/design_analyzer/crawl.py "https://<funnel-url>"
.venv/bin/python agents/design_analyzer/analyze.py URLs/<slug>

# 2 — Marketing Analyst (no API): builds the context bundle → session model writes the JSON.
.venv/bin/python agents/marketing_analyst/analyze.py URLs/<slug>

# 3 — Competitor Intel: Apify Meta Ad Library (US) + OpenAI vision classification.
.venv/bin/python agents/competitor_intel/run.py outputs/analysis/marketing_<slug>_<ts>.json

# 4 — Creative Strategist (no API): builds the strategy bundle → session model writes the briefs.
.venv/bin/python agents/creative_strategist/synthesize.py <slug>

# 5 — Designer (gpt-image-2). Approval flow: concepts (low) → resize (high).
.venv/bin/python agents/designer/generate.py --briefs <slug> --phase concept
.venv/bin/python agents/designer/generate.py --briefs <slug> --phase resize --skip-existing

# 6 — Video Storyboard (no API): builds the bundle → session model writes the storyboards.
.venv/bin/python agents/video_storyboard/synthesize_video.py <slug>

# 7 — Video Producer: Veo 3 render → ffmpeg stitch → per-platform export.
.venv/bin/python agents/video_producer/produce.py <slug>        # add --dry-run to preview
```

## ✨ Key design choices

- **Agent 5 — one cohesive image, text designed in.** gpt-image-2 designs the whole ad (audience
  badge → headline hook → short money-focused line → CTA button with shadow + cursor), via the
  **Responses API `background` mode** (submit all → render server-side in parallel → poll), which
  sidesteps the ~60s synchronous-connection wall. Sizes are ÷16 then resized to exact Meta targets
  (`agents/designer/meta_placements.py`). A/B/C hook variants; quality is phase-aware (concept→low,
  resize→high).
- **Agent 7 — all video text rendered IN-SCENE by Veo.** No post overlays: each storyboard shot
  carries a `veo_text_treatment` (cinematic typography look) and the exact words, which the producer
  bakes into the Veo prompt so the text is generated in-camera (Hollywood-grade). Veo 3 = 8s/clip,
  9:16, native audio; one render per clip, stitched + exported per platform.
- **Market = US only** for now.

## 🔑 Env / deps

Secrets in `.env` (gitignored): `OPENAI_API_KEY`, `APIFY_TOKEN`/`APIFY_API_TOKEN`, `FIGMA_TOKEN`,
`GEMINI_API_KEY`/`GOOGLE_API_KEY` (Veo 3). Python venv at `.venv`:
`playwright` (+ `playwright install chromium`), `openai`, `Pillow`, `certifi`, `google-genai`.
System dependency: **ffmpeg** (Agent 7). See each agent's `requirements.txt`.

## 📁 Layout

```
agents/
  design_analyzer/    crawl.py, analyze.py
  marketing_analyst/  analyze.py            (context builder; session model writes JSON)
  competitor_intel/   run.py
  creative_strategist/ synthesize.py        (context builder; session model writes JSON)
  designer/           generate.py, compositor.py, meta_placements.py
  video_storyboard/   synthesize_video.py, video_specs.py   (context builder; session model writes JSON)
  video_producer/     produce.py, veo_client.py
shared/   schemas/, META_ADS_SPEC.md, VIDEO_ADS_SPEC.md, video_ad_playbook.json
outputs/  analysis/ competitor_intel/ briefs/ creatives/ storyboards/ videos/   (gitignored)
URLs/<slug>/   per-funnel screenshots + manifest + page_text                    (gitignored)
```
