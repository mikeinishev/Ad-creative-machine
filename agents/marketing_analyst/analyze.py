#!/usr/bin/env python3
"""
Agent 2 — Marketing Analyst (context builder).

IMPORTANT: Agent 2 does NOT call any external LLM API. The analysis is performed
by the Claude Code coding agent itself, using the MAXIMUM model available in the
session (currently Opus 4.8 @ 1M context; always use the strongest model available
so the output is as relevant and useful as possible).

This script's only job is the deterministic part: assemble the COMPLETE, UNABRIDGED
funnel context that Agent 1 captured (every screen's text + the design analysis +
manifest signals) into one bundle. No character caps, no token limits. The coding
agent then reads that bundle and writes the enriched marketing analysis JSON.

Flow:
  1. python agents/marketing_analyst/analyze.py URLs/<slug>            # build the bundle
  2. (coding agent reads the bundle, performs the analysis with the max model)
  3. coding agent writes outputs/analysis/marketing_<slug>_<ts>.json   # enriched schema below

Enriched output schema (TOP-LEVEL keys — downstream agents read them here):
  market_targeting:   {vertical, niche, sub_niche, geo{countries,primary}, language,
                       business_model, product_category, price_point, confidence, evidence[]}
  landing_analysis:   {headline, subheadline, pain_points[], benefits[], social_proof[], cta_structure[]}
  audiences[]:        {segment, demographics, psychographics, pain_points[], triggers[]}
  value_propositions[]:{id, headline, unique_mechanism, supporting_points[], target_audience}
  offers[]:           {type, description, value_stack[], pricing, urgency_elements[]}
  competitor_research:{search_queries[], seed_keywords[], known_competitors[],
                       ad_angles_to_watch[], exclude_brand_terms[], platforms[], geo[]}
  source:             {type, url, slug, screens, analyst_model, analyzed_at}

The market_targeting + competitor_research blocks are what Agent 3 consumes to know
WHAT and WHERE to search the Meta Ad Library.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
URLS_DIR = REPO_ROOT / "URLs"
OUT_DIR = REPO_ROOT / "outputs" / "analysis"


def _resolve_crawl(arg: str) -> Path:
    p = Path(arg)
    if not p.is_absolute():
        cand = (Path.cwd() / p).resolve()
        p = cand if cand.exists() else (URLS_DIR / arg).resolve()
    if not p.exists():
        p = (URLS_DIR / Path(arg).name).resolve()
    return p


def _latest_design_analysis(slug: str) -> Optional[Path]:
    files = sorted(OUT_DIR.glob(f"design_{slug}_*.json"))
    return files[-1] if files else None


def build_bundle(crawl_dir: Path) -> Dict[str, Any]:
    manifest = json.loads((crawl_dir / "manifest.json").read_text())
    slug = manifest.get("slug", crawl_dir.name)

    # full, unabridged per-screen text
    screens: List[str] = []
    for step in manifest.get("steps", []):
        idx = step["step"]
        tf = crawl_dir / "page_text" / f"{idx:02d}.txt"
        if not tf.exists():
            continue
        text = tf.read_text(errors="ignore").strip()
        if text:
            screens.append(
                f"### SCREEN {idx:02d} — type={step.get('type','screen')} "
                f"· action={step.get('action','')}\n{text}"
            )

    design_block = ""
    dpath = _latest_design_analysis(slug)
    if dpath:
        design_block = (
            f"\n\n## DESIGN ANALYSIS (Agent 1)\n```json\n{dpath.read_text()}\n```"
        )

    bundle_md = (
        f"# Funnel context for Agent 2 — {slug}\n\n"
        f"- Source URL: {manifest.get('url')}\n"
        f"- Crawl status: {manifest.get('status')} · screens: {len(screens)}\n"
        f"- Note: this is the COMPLETE funnel copy, every screen, unabridged.\n\n"
        f"## FUNNEL COPY (in order)\n\n" + "\n\n".join(screens) + design_block
    )
    return {"slug": slug, "url": manifest.get("url"), "screens": len(screens), "markdown": bundle_md}


def run(args: argparse.Namespace) -> int:
    crawl_dir = _resolve_crawl(args.crawl)
    if not (crawl_dir / "manifest.json").exists():
        sys.exit(f"ERROR: no manifest.json in {crawl_dir} (run crawl.py first).")

    bundle = build_bundle(crawl_dir)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"_marketing_context_{bundle['slug']}.md"
    out_path.write_text(bundle["markdown"])

    print(f"✔ context bundle ready · {bundle['screens']} screens → {out_path.relative_to(REPO_ROOT)}")
    print(
        "\nNEXT: the Claude Code agent (max available model, e.g. Opus 4.8 1M) should now\n"
        "read this bundle and WRITE the enriched marketing analysis to:\n"
        f"  outputs/analysis/marketing_{bundle['slug']}_<ts>.json\n"
        "following the schema in this file's module docstring (market_targeting,\n"
        "landing_analysis, audiences, value_propositions, offers, competitor_research)."
    )
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Agent 2 — marketing context builder (no external API)")
    ap.add_argument("crawl", help="path to URLs/<slug> dir, or just the <slug>")
    args = ap.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
