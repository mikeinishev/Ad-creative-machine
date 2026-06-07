#!/usr/bin/env python3
"""
Agent 6 — Video Storyboard / Script (context builder).

IMPORTANT: Agent 6 does NOT call any external LLM API. Like Agents 2 & 4, this script
only assembles a complete context bundle; the Claude Code coding agent itself (max model,
Opus 4.8 1M) writes the storyboards JSON. Storyboarding is creative work for the session model.

It converts Agent 4's static ad concepts (creative_briefs_<slug>.json) into shot-by-shot
short-form VIDEO storyboards + scripts for TikTok, YouTube Shorts and Meta Reels — built on
Google Veo 3's 8-second beat grid, following the verified video-ad playbook
(shared/video_ad_playbook.json) and platform specs (agents/video_storyboard/video_specs.py).

Flow:
  1. python agents/video_storyboard/synthesize_video.py <slug>      # build the bundle
  2. (coding agent reads the bundle + writes outputs/storyboards/storyboards_<slug>_<ts>.json)

Each storyboard (one per Agent-4 concept) carries a 9:16 MASTER shot list + per-platform cuts.
Each SHOT carries: shot_no, clip_id, beat_role, start_s/end_s/duration_s, visual, veo_prompt
(self-contained, audio inline), camera, on_screen_text (EXACT words), veo_text_treatment
(cinematic typography look), text_position, voiceover, sfx_music, transition, reference_images,
pattern_interrupt, safe_zone_check. Map: audience_callout→self-ID hook · headline hook→hook line ·
subhead→solution/proof payoff · offer+cta→CTA beat. ALL text is rendered IN-SCENE by Veo 3 as
cinematic typography (no post overlays); Agent 7 injects on_screen_text + veo_text_treatment.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIEFS_DIR = REPO_ROOT / "outputs" / "briefs"
OUT_DIR = REPO_ROOT / "outputs" / "storyboards"
PLAYBOOK = REPO_ROOT / "shared" / "video_ad_playbook.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from video_specs import TARGETS, VEO3, SAFE_ZONE, DEFAULT_TARGET_KEYS  # noqa: E402


def _latest_briefs(slug: str) -> Optional[Path]:
    files = sorted(BRIEFS_DIR.glob(f"creative_briefs_{slug}_*.json"))
    return files[-1] if files else None


def _distill_playbook() -> str:
    if not PLAYBOOK.exists():
        return "(playbook missing — see shared/VIDEO_ADS_SPEC.md)"
    pb = json.loads(PLAYBOOK.read_text()).get("playbook", {})
    bp = pb.get("best_practices", {})

    def bullets(items, n=12):
        return "\n".join(f"- {x}" for x in (items or [])[:n])

    structures = "\n".join(
        f"- **{s.get('name')}** — {s.get('arc')}  _(best for: {s.get('best_for')})_"
        for s in (bp.get("structures") or [])
    )
    platform_notes = "\n".join(
        f"- **{n.get('platform')}** — ideal {n.get('ideal_duration')}: {n.get('notes')}"
        for n in (bp.get("per_platform_notes") or [])
    )
    return f"""## HOOKS (first 1–3s)
{bullets(bp.get('hooks'))}

## SCRIPT STRUCTURES / ARCS
{structures}

## PACING
{bullets(bp.get('pacing'))}

## CAPTIONS & SOUND
{bullets(bp.get('captions_sound'))}

## CTA
{bullets(bp.get('cta'))}

## DOs
{bullets(bp.get('dos'))}

## DON'Ts
{bullets(bp.get('donts'))}

## PER-PLATFORM NOTES
{platform_notes}

## STORYBOARD ARC RECOMMENDATION (how to map an Agent-4 concept → a video)
{pb.get('storyboard_arc_recommendation','')}

## SHOT FIELDS (each shot must carry these)
{bullets(pb.get('storyboard_fields'), 30)}
"""


def _specs_block() -> str:
    lines = ["## VEO 3 (renderer — next series)"]
    lines.append(f"- {VEO3['model']} · max {VEO3['max_clip_s']}s/clip @ {VEO3['fps']}fps · "
                 f"{', '.join(VEO3['aspect_ratios'])} · {VEO3['audio']}")
    for r in VEO3["rules"]:
        lines.append(f"- {r}")
    lines.append("\n## PLATFORM TARGETS (fit the export to these)")
    for t in TARGETS.values():
        tag = "MASTER 9:16" if t.is_master else "derivative (centre-crop)"
        lines.append(f"- **{t.key}** [{tag}] {t.platform}/{t.placement}: {t.aspect_ratio} {t.resolution} · "
                     f"ideal {t.ideal_duration} · ≤{t.max_duration_s}s · {t.max_file_size} · "
                     f"{t.container}/{t.video_codec} {t.fps}fps")
    lines.append(f"\n## SAFE ZONE\n- {SAFE_ZONE['rule']} ({SAFE_ZONE['central_box']})")
    return "\n".join(lines)


def build_bundle(slug: str, briefs_path: Path) -> str:
    briefs = json.loads(briefs_path.read_text())
    market = briefs.get("meta", {}).get("market", {})
    concise = []
    for b in briefs.get("creative_briefs", []):
        cd = b.get("creative_direction", {})
        concise.append({
            "brief_id": b.get("brief_id"),
            "concept_name": b.get("concept_name"),
            "priority": b.get("priority"),
            "target_audience": b.get("target_audience"),
            "audience_callout": b.get("audience_callout"),
            "value_proposition": b.get("value_proposition"),
            "hook_variations": b.get("hook_variations"),
            "subhead": b.get("subhead"),
            "body_copy": b.get("body_copy"),
            "cta": b.get("cta"),
            "color_scheme": cd.get("color_scheme"),
            "visual_concept": cd.get("visual_concept"),
            "reference_creatives": b.get("reference_creatives"),
        })

    return f"""# Video storyboard context — {slug}

Market: {market} · Source briefs: {briefs_path.name}

You (the coding agent, max model) will write shot-by-shot VIDEO storyboards from the static
concepts below, following the playbook + specs, and save:
`outputs/storyboards/storyboards_{slug}_<ts>.json`.

For EACH concept produce a storyboard with: a 9:16 MASTER shot list (built on Veo 3's 8s beat
grid, ~15s default arc / optional 30s), and per-platform CUTS (tiktok_infeed, youtube_shorts,
meta_reels — trim/tune duration + notes per platform). Map the Agent-4 fields onto the arc:
audience_callout → self-identifying HOOK text; headline hook (hook_a) → the spoken + in-scene hook
line (A/B with hook_b/hook_c); subhead → the money payoff in SOLUTION/PROOF; offer+cta → the CTA
beat. ALL text is rendered IN-SCENE by Veo as cinematic typography (no post overlays) — each shot
gives the EXACT `on_screen_text` + a `veo_text_treatment` (the look), and Agent 7 bakes them into
the Veo prompt. Each `veo_prompt` is a self-contained Veo 3 prompt (subject/setting/action/style/
camera/lighting/AUDIO).

---

# AGENT-4 CONCEPTS (static)
```json
{json.dumps(concise, ensure_ascii=False, indent=2)}
```

---

# VIDEO-AD PLAYBOOK (best practices)
{_distill_playbook()}

---

# SPECS
{_specs_block()}
"""


def run(args: argparse.Namespace) -> int:
    slug = args.slug
    briefs_path = Path(args.briefs) if args.briefs else _latest_briefs(slug)
    if not briefs_path or not briefs_path.exists():
        sys.exit(f"ERROR: no creative_briefs found for slug '{slug}'. Run Agent 4 first.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bundle = build_bundle(slug, briefs_path)
    out_path = OUT_DIR / f"_storyboard_context_{slug}.md"
    out_path.write_text(bundle)

    print(f"✔ storyboard context ready → {out_path.relative_to(REPO_ROOT)}")
    print(f"  briefs: {briefs_path.relative_to(REPO_ROOT)}")
    print(
        f"\nNEXT: the coding agent (max model, Opus 4.8 1M) reads this bundle and WRITES\n"
        f"  outputs/storyboards/storyboards_{slug}_<ts>.json\n"
        f"with a 9:16 master shot list + per-platform cuts per concept "
        f"(targets: {', '.join(DEFAULT_TARGET_KEYS)})."
    )
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Agent 6 — video storyboard context builder (no external API)")
    ap.add_argument("slug", help="funnel slug, e.g. 100plus.boomerangme.com")
    ap.add_argument("--briefs", default="", help="override path to creative_briefs_<slug>.json")
    args = ap.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
