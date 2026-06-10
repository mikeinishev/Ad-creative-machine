#!/usr/bin/env python3
"""
Agent 1 — vision analysis of crawled funnel screenshots.

Turns a crawl (URLs/<slug>/ produced by crawl.py) into the structured funnel
design analysis Agent 1 is meant to output (shared/schemas/design_analysis.json).

For each screen it sends the screenshot PLUS the text crawl.py already extracted
(page_text/NN.txt) to an OpenAI vision model, which classifies the screen
(welcome / question / result / offer) and pulls headline, subheadline, CTA,
visual elements, colour palette and typography. Per-screen results are merged
into one funnel_structure JSON + a human summary.

Usage:
  python agents/design_analyzer/analyze.py URLs/100plus.boomerangme.com
  python agents/design_analyzer/analyze.py 100plus.boomerangme.com --model gpt-4o
  python agents/design_analyzer/analyze.py URLs/<slug> --max-screens 8

Output:
  outputs/analysis/design_<slug>_<ts>.json
  outputs/analysis/design_<slug>_<ts>_summary.md
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
URLS_DIR = REPO_ROOT / "URLs"
OUT_DIR = REPO_ROOT / "outputs" / "analysis"
DEFAULT_MODEL = "gpt-4o-mini"

SCREEN_SCHEMA_HINT = """Return ONLY a JSON object with this exact shape:
{
  "type": "welcome|question|result|offer",
  "headline": "main heading text (verbatim, '' if none)",
  "subheadline": "secondary line ('' if none)",
  "cta_text": "primary button label ('' if none)",
  "question": "the quiz question asked, if this is a question screen ('' otherwise)",
  "answer_options": ["option labels if present"],
  "visual_elements": ["short tags: logo, hero_image, progress_bar, icon, chart, testimonial, stars, card_form, badge, illustration, photo"],
  "color_scheme": ["up to 5 dominant colors as #RRGGBB hex, estimated from the image"],
  "typography": {"heading": "e.g. 'bold sans-serif'", "body": "e.g. 'regular sans-serif'"},
  "is_paywall": true|false
}
Classification guide:
- welcome: intro / first screen / "start" framing
- question: asks something with options or an input field
- result: shows a personalized outcome/plan/number
- offer: pricing, plan selection, or a checkout/payment (card fields) → is_paywall true on a payment screen
Use the provided extracted text as the source of truth for wording; use the image for layout, colors, and visual elements."""


def load_env() -> None:
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def make_client():
    from openai import OpenAI

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("ERROR: OPENAI_API_KEY not set (looked in environment and .env).")
    return OpenAI(api_key=key, timeout=120, max_retries=2)


def _data_url(img_path: Path, max_w: int = 820) -> str:
    """Downscale (width-capped) and base64-encode as a data URL to bound token cost."""
    from PIL import Image

    img = Image.open(img_path).convert("RGB")
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.Resampling.LANCZOS)
    # cap very tall full-page shots so a single screen isn't enormous
    if img.height > 2200:
        img = img.crop((0, 0, img.width, 2200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def analyze_screen(
    client, model: str, img_path: Path, page_text: str, crawler_type: str, idx: int
) -> Dict[str, Any]:
    text_excerpt = (page_text or "").strip()[:1500]
    messages = [
        {
            "role": "system",
            "content": "You are a funnel design analyst. Extract structured data from one funnel screen. Be precise and terse.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Funnel screen #{idx}. Crawler tag: '{crawler_type}'.\n\n"
                        f"EXTRACTED TEXT:\n```\n{text_excerpt}\n```\n\n{SCREEN_SCHEMA_HINT}"
                    ),
                },
                {"type": "image_url", "image_url": {"url": _data_url(img_path), "detail": "low"}},
            ],
        },
    ]
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=700,
        )
        data = json.loads(resp.choices[0].message.content)
    except Exception as e:  # noqa: BLE001
        return {"type": "question", "headline": "", "error": str(e)}
    return data


def run(args: argparse.Namespace) -> int:
    # resolve crawl dir (accept absolute path, relative path, or bare slug)
    p = Path(args.crawl)
    if not p.is_absolute():
        cand = (Path.cwd() / p).resolve()
        p = cand if cand.exists() else (URLS_DIR / args.crawl).resolve()
    if not p.exists():
        p = (URLS_DIR / Path(args.crawl).name).resolve()
    if not (p / "manifest.json").exists():
        sys.exit(f"ERROR: no manifest.json in {p} (run crawl.py first).")

    manifest = json.loads((p / "manifest.json").read_text())
    slug = manifest.get("slug", p.name)
    steps = manifest.get("steps", [])
    if args.max_screens:
        steps = steps[: args.max_screens]

    client = make_client()
    print(f"▶ analyzing {len(steps)} screens from {p.relative_to(REPO_ROOT)} with {args.model}")

    screens: List[Dict[str, Any]] = []
    flow: List[str] = []
    palette: Counter = Counter()

    for step in steps:
        idx = step["step"]
        img = p / step["screenshot"]
        txt = ""
        tf = p / "page_text" / f"{idx:02d}.txt"
        if tf.exists():
            txt = tf.read_text(errors="ignore")
        if not img.exists():
            continue

        s = analyze_screen(client, args.model, img, txt, step.get("type", ""), idx)
        sid = f"screen_{idx}"
        screen = {
            "id": sid,
            "type": s.get("type", "question") if s.get("type") in ("welcome", "question", "result", "offer") else "question",
            "headline": s.get("headline", ""),
            "subheadline": s.get("subheadline", ""),
            "cta_text": s.get("cta_text", ""),
            "visual_elements": s.get("visual_elements", []) or [],
            "color_scheme": s.get("color_scheme", []) or [],
            "typography": s.get("typography", {}) or {},
            "source_screenshot": f"URLs/{slug}/{step['screenshot']}",
        }
        # carry quiz extras when present
        if s.get("question"):
            screen["question"] = s["question"]
        if s.get("answer_options"):
            screen["answer_options"] = s["answer_options"]
        if s.get("is_paywall") or step.get("type") == "paywall":
            screen["is_paywall"] = True
            screen["type"] = "offer"
        for c in screen["color_scheme"]:
            if isinstance(c, str) and c.startswith("#"):
                palette[c.upper()] += 1
        screens.append(screen)
        flow.append(sid)
        print(f"  [{idx:02d}] {screen['type']:<8} {screen['headline'][:50]!r}")

    funnel = {
        "funnel_structure": {
            "screens": screens,
            "flow": flow,
            "brand_assets": {
                "logo_url": "",
                "color_palette": [c for c, _ in palette.most_common(6)],
            },
        },
        "source": {
            "type": "url_crawl",
            "url": manifest.get("url"),
            "slug": slug,
            "crawl_status": manifest.get("status"),
            "screens_analyzed": len(screens),
            "model": args.model,
            "analyzed_at": datetime.now().isoformat(),
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUT_DIR / f"design_{slug}_{ts}.json"
    json_path.write_text(json.dumps(funnel, indent=2, ensure_ascii=False))

    md = [
        f"# Funnel design analysis — {slug}",
        "",
        f"- Source URL: {manifest.get('url')}",
        f"- Crawl status: {manifest.get('status')} · screens analyzed: {len(screens)}",
        f"- Brand palette: {', '.join(funnel['funnel_structure']['brand_assets']['color_palette'])}",
        f"- Flow: {' → '.join(flow)}",
        "",
        "| # | Type | Headline | CTA |",
        "|---|------|----------|-----|",
    ]
    for s in screens:
        md.append(
            f"| {s['id'].split('_')[1]} | {s['type']} | {s['headline'][:48]} | {s['cta_text'][:24]} |"
        )
    (OUT_DIR / f"design_{slug}_{ts}_summary.md").write_text("\n".join(md))

    print(f"\n✔ {len(screens)} screens → {json_path.relative_to(REPO_ROOT)}")
    return 0


def main() -> None:
    load_env()
    ap = argparse.ArgumentParser(description="Agent 1 — vision analysis of crawled funnel")
    ap.add_argument("crawl", help="path to URLs/<slug> dir, or just the <slug>")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"vision model (default {DEFAULT_MODEL})")
    ap.add_argument("--max-screens", type=int, help="limit screens analyzed")
    args = ap.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
