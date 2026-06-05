# Agent 5 — OpenAI `gpt-image-2` Setup (ACTIVE engine)

This is the active image engine for the Designer agent. It supersedes the legacy
DALL·E 3 / Imagen / Midjourney setup docs in this folder.

## 1. Install

```bash
python3 -m venv .venv
.venv/bin/pip install openai Pillow
# or:  .venv/bin/pip install -r agents/designer/requirements.txt
```

## 2. Auth

`OPENAI_API_KEY` is read from `.env` at the repo root (or the environment):

```
OPENAI_API_KEY=sk-proj-...
```

## 3. Run

```bash
# all briefs (formats taken from each brief)
.venv/bin/python agents/designer/generate.py

# one brief, explicit placements
.venv/bin/python agents/designer/generate.py --brief brief_001 --placements feed_vertical,stories_reels

# dry-run: print the plan, no API calls / no cost
.venv/bin/python agents/designer/generate.py --limit 2 --dry-run

# print the placement spec table
.venv/bin/python agents/designer/meta_placements.py
```

## 4. Model facts (verified against the live API)

| Param | Value |
|---|---|
| `model` | `gpt-image-2` |
| `quality` | `low` \| `medium` \| `high` \| `auto` — **project default `medium` ("mid")** |
| `size` | width & height **÷16**, longest edge ≤ 3840, above a min pixel budget |
| return | base64 in `data[0].b64_json` |

Because Meta's 1080-based sizes aren't ÷16, we generate at a clean ÷16 `gen` size and
downscale (LANCZOS) to the exact Meta `target`. See `meta_placements.py`.

```python
from openai import OpenAI
import base64, io
from PIL import Image

client = OpenAI()  # reads OPENAI_API_KEY
resp = client.images.generate(
    model="gpt-image-2",
    prompt=prompt,
    size="1152x2048",   # placement.gen (9:16)
    quality="medium",   # "mid"
    n=1,
)
raw = base64.b64decode(resp.data[0].b64_json)
img = Image.open(io.BytesIO(raw)).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)
img.save("stories_reels.png", format="PNG", optimize=True)
```

## 5. Performance & cost notes

- `medium` quality renders are noticeably slower than `low`; allow a generous per-image
  timeout. The generator sets a client-side timeout and logs per-image seconds.
- One creative per API call (`n=1`) keeps failures isolated and the log clean.
- Use `--dry-run` to validate the plan (briefs × placements) before spending anything.

## 6. Troubleshooting — `APIConnectionError: Connection error` at ~60s

Observed and diagnosed during integration:

- A **clean** prompt at any placement size renders fine (`low` ≈16s, `medium` ≈48–127s).
- Some brief prompts fail **reproducibly** with `[Errno 54] Connection reset by peer` at
  **~60–61s**, even with `stream=True` (zero partial images arrive first).
- This is **OpenAI image-safety handling**, not a network/size bug: the server stalls on a
  flagged prompt and resets the socket instead of returning a clean moderation error.
- In this project the trigger is **income / "business-opportunity" claims** (e.g.
  "$10,000 recurring monthly income", "earn recurring revenue", partner-program / MLM-style
  framing). The 9:16 variant of the same brief sometimes slips through — moderation is
  probabilistic.

**What the generator does:** `_call_with_retry()` retries transient resets with a fresh
client + backoff, logs the failure, and continues with the other placements. Failed
creatives are recorded in `generation_log_<ts>.json` and the brief `metadata.json`.

**How to get a flagged creative to render:** soften the visual prompt in Agent 4's
`image_generation_prompts.json` — describe the *scene/mood* rather than literal earnings
("growth chart trending up" instead of "$0 → $10,000"), drop hard income figures from the
on-image text overlay, and avoid get-rich / guaranteed-income phrasing.

## 7. Placements → sizes

See [`shared/META_ADS_SPEC.md`](../../shared/META_ADS_SPEC.md) for the full Meta 2026 table
and Stories/Reels safe zones.
