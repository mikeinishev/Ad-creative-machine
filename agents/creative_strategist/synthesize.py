#!/usr/bin/env python3
"""
Agent 4 — Creative Strategist (context builder).

IMPORTANT: Agent 4 does NOT call any external LLM API. The synthesis — the
opportunity matrix AND the creative briefs (real copywriting, not templates) — is
performed by the Claude Code coding agent itself, using the MAXIMUM model available
in the session (currently Opus 4.8 @ 1M context; always use the strongest model).

This script does only the deterministic part: find the latest design (Agent 1),
marketing (Agent 2) and competitor (Agent 3) outputs for a slug and assemble them
into one complete strategy bundle. The coding agent then reads that bundle, builds
an intelligent opportunity matrix and writes ONE briefs JSON per funnel:
  outputs/briefs/creative_briefs_<slug>_<ts>.json   (all briefs for this funnel)

(Old briefs from other funnels in outputs/briefs/ are left untouched — each funnel
gets its own creative_briefs_<slug>_*.json.)

Flow:
  1. python agents/creative_strategist/synthesize.py <slug>      # build the bundle
  2. (coding agent reads the bundle, builds matrix + writes the briefs JSON)

Brief JSON is Agent-5-ready. Each brief in creative_briefs[]:
  {
    "brief_id", "concept_name", "priority",
    "opportunity": {"audience","value_proposition","hook_type","score","reasoning"},
    "target_audience", "value_proposition",
    "hook_variations": {"hook_a","hook_b","hook_c"},   # real A/B/C copy: proven / alt / experimental
    "body_copy", "cta": {"primary","secondary"},
    "creative_direction": {
       "visual_concept": "<rich, cinematic 15-40 line scene for gpt-image-2>",
       "color_scheme": ["#.."], "typography_style": "..", "imagery": [".."],
       "layout": "<short layout note>",
       "formats": [{"name","dimensions","aspect_ratio"}]   # 1:1, 4:5, 9:16
    },
    "reference_creatives": [{"ad_id","page_name","what_to_learn"}],
    "reasoning": ".."
  }
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = REPO_ROOT / "outputs" / "analysis"
COMPET_DIR = REPO_ROOT / "outputs" / "competitor_intel"
BRIEFS_DIR = REPO_ROOT / "outputs" / "briefs"


def _latest(globdir: Path, pattern: str) -> Optional[Path]:
    files = sorted(globdir.glob(pattern))
    return files[-1] if files else None


def resolve_inputs(slug: str, args: argparse.Namespace) -> Dict[str, Path]:
    design = Path(args.design) if args.design else _latest(ANALYSIS_DIR, f"design_{slug}_*.json")
    marketing = Path(args.marketing) if args.marketing else _latest(ANALYSIS_DIR, f"marketing_{slug}_*.json")
    competitor = Path(args.competitor) if args.competitor else _latest(COMPET_DIR, f"data_{slug}_*.json")
    missing = [n for n, p in [("design", design), ("marketing", marketing), ("competitor", competitor)] if not p or not p.exists()]
    if missing:
        sys.exit(f"ERROR: missing inputs for slug '{slug}': {missing}. Run agents 1–3 first.")
    return {"design": design, "marketing": marketing, "competitor": competitor}


def _distill_competitor(comp: Dict[str, Any]) -> str:
    pats = comp.get("patterns", {})
    lines = [
        f"- Patterns (winners): hooks={pats.get('hook_distribution')}, "
        f"visuals={pats.get('visual_styles')}, formats={pats.get('format_distribution')}, "
        f"niche_relevant={pats.get('niche_relevant_count')}/{pats.get('total_analyzed')}",
        "- Niche-relevant winning creatives (reference pool):",
    ]
    for w in comp.get("winning_creatives", []):
        c = w.get("classification") or {}
        if not c.get("niche_relevant"):
            continue
        lines.append(
            f"    · ad_id={w['ad_id']} | {w['page_name']} | {w['days_active']}d | {w['media_type']} | "
            f"hook={c.get('hook_type')} visual={c.get('visual_style')} cta={c.get('cta_type')} | "
            f"\"{str(c.get('primary_message',''))[:70]}\" | {w.get('local_path','')}"
        )
    return "\n".join(lines)


def build_bundle(inputs: Dict[str, Path]) -> Dict[str, Any]:
    design = json.loads(inputs["design"].read_text())
    marketing = json.loads(inputs["marketing"].read_text())
    competitor = json.loads(inputs["competitor"].read_text())
    slug = marketing.get("source", {}).get("slug") or design.get("source", {}).get("slug") or "funnel"

    mt = marketing.get("market_targeting", {})
    brand = design.get("funnel_structure", {}).get("brand_assets", {})

    md = f"""# Creative strategy context — {slug}

## MARKET TARGETING (Agent 2)
- Vertical: {mt.get('vertical')} · Niche: {mt.get('niche')} · Sub-niche: {mt.get('sub_niche')}
- Geo: {mt.get('geo')} · Language: {mt.get('language')} · Confidence: {mt.get('confidence')}
- Business model: {mt.get('business_model')}
- Product: {mt.get('product_category')}
- Price point: {mt.get('price_point')}

## BRAND (Agent 1 design)
- Color palette: {brand.get('color_palette')}
- (typography per screen is in the design JSON below; funnel is bold sans-serif, clean/minimal)

## COMPETITOR INTEL (Agent 3, vision-classified)
{_distill_competitor(competitor)}

---

## RAW INPUTS (full)

### marketing_{slug}.json (Agent 2)
```json
{json.dumps(marketing, ensure_ascii=False, indent=2)}
```

### competitor data_{slug}.json (Agent 3)
```json
{json.dumps(competitor, ensure_ascii=False, indent=2)}
```

### design_{slug}.json (Agent 1)
```json
{json.dumps(design, ensure_ascii=False, indent=2)}
```
"""
    return {"slug": slug, "markdown": md}


def run(args: argparse.Namespace) -> int:
    slug = args.slug
    inputs = resolve_inputs(slug, args)
    bundle = build_bundle(inputs)
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BRIEFS_DIR / f"_strategy_context_{bundle['slug']}.md"
    out_path.write_text(bundle["markdown"])

    print(f"✔ strategy context ready → {out_path.relative_to(REPO_ROOT)}")
    print("  inputs:")
    for k, p in inputs.items():
        print(f"    {k:<11} {p.relative_to(REPO_ROOT)}")
    print(
        f"\nNEXT: the Claude Code agent (max model, Opus 4.8 1M) should read this bundle,\n"
        f"build an intelligent opportunity matrix (audience × value_prop × proven-hook,\n"
        f"scored with real reasoning grounded in the competitor patterns), select the top\n"
        f"{args.top} concepts, write REAL A/B/C hook copy + cinematic visual concepts, and\n"
        f"save ONE briefs JSON:\n  outputs/briefs/creative_briefs_{bundle['slug']}_<ts>.json\n"
        f"(Agent-5-ready shape — see this script's module docstring.)"
    )
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Agent 4 — creative strategy context builder (no external API)")
    ap.add_argument("slug", help="funnel slug, e.g. 100plus.boomerangme.com")
    ap.add_argument("--design", default="", help="override path to design_<slug>.json")
    ap.add_argument("--marketing", default="", help="override path to marketing_<slug>.json")
    ap.add_argument("--competitor", default="", help="override path to competitor data_<slug>.json")
    ap.add_argument("--top", type=int, default=5, help="number of briefs to generate (default 5)")
    args = ap.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
