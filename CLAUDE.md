# Ad Creative Machine

A 5-agent pipeline that takes a **quiz/sales-funnel URL** and produces **Meta Ads
creatives** end to end: it crawls the funnel, extracts marketing intelligence,
researches competitor ads, writes creative briefs, and generates the images.

**Status:** the URL flow (Agents 1→5) is built and runnable. Verified on
`100plus.boomerangme.com` (Richie AI restaurant funnel).

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

Flow is linear (each agent consumes the previous). Agent 4 is the fan-in (merges
design + marketing + competitor). Each agent dir has an `AGENT_PROMPT.md` with the
authoritative spec.

---

## Key principles (do it this way)

- **Agents 2 & 4 do NOT call any external LLM API.** Their `analyze.py`/`synthesize.py`
  only assemble a complete context bundle; the **Claude Code session model itself
  (always the strongest available — currently Opus 4.8, 1M context)** performs the
  analysis and writes the JSON. No char/token caps. If a stronger model is available,
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

---

## Env / deps

- Secrets in `.env` (gitignored): `OPENAI_API_KEY`, `APIFY_TOKEN`/`APIFY_API_TOKEN`,
  `FIGMA_TOKEN`.
- Python venv at `.venv`. Deps: `playwright` (+ `playwright install chromium`),
  `openai`, `Pillow`, `certifi`. See `agents/designer/requirements.txt`.
- Generated artifacts (`outputs/`, `URLs/`), `inputs/`, `.venv`, `__pycache__` are
  gitignored.

## File map

```
agents/
  design_analyzer/   crawl.py, analyze.py
  marketing_analyst/ analyze.py            (context builder; session model writes JSON)
  competitor_intel/  run.py
  creative_strategist/ synthesize.py       (context builder; session model writes JSON)
  designer/          generate.py, compositor.py, meta_placements.py
shared/              schemas/, META_ADS_SPEC.md
outputs/             analysis/ competitor_intel/ briefs/ creatives/   (gitignored)
URLs/<slug>/         per-funnel screenshots + manifest + page_text    (gitignored)
```
