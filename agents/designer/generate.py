#!/usr/bin/env python3
"""
Agent 5 — Designer: creative image generator (OpenAI gpt-image-2, medium quality).

Turns Agent 4 briefs into Meta-ready creatives.

Default mode = ONE COHESIVE IMAGE (text designed in):
  gpt-image-2 designs the whole creative — scene + integrated headline/CTA typography — as
  a single unified ad (text is PART of the composition, not pasted on top). Each hook variant
  is its own render. Use --text-mode composite to instead paint a text-free scene and overlay
  the text with Pillow (reliable text, but less integrated).

APPROVAL FLOW (standard 2-step — do NOT generate all sizes up front):
  1. CONCEPTS in LOW quality: `--phase concept` → base placement only (default feed_square),
     all hook variants, quality auto = LOW (fast + reliable under the ~60s API limit). Refine
     the concepts/copy with the user, then APPROVE the concept + hook. No resizes.
  2. After approval → RESIZES in HIGH quality: `--phase resize` (+ `--skip-existing`) → all the
     OTHER placements (feed_vertical, stories_reels, …) for the approved briefs/variants;
     quality auto = HIGH.
  (`--phase all` (auto = medium) does everything at once; only use when explicitly asked.)
  Copy on creatives is intentionally minimal: ONE bold headline (the hook) + ONE short
  money-focused supporting line (≤~12 words, from the brief's `subhead`) + a CTA button.

Features:
  - A/B/C hook variations (one image per variant; visual identical) → <placement>_<A|B|C>.png
  - parallel generation (--concurrency), transient-retry + moderation auto-soften
  - --skip-existing (resume), optional --qa vision check, prompts saved in metadata

Inputs (resolution order; or pass --briefs <path|slug>):
  outputs/briefs/image_generation_prompts.json     (legacy; text baked → model mode)
  latest outputs/briefs/creative_briefs_<slug>_*.json  (Agent 4 → composite mode)
  outputs/briefs/creative_briefs.json

Output:
  outputs/creatives/<brief_id>/<placement>_<variant>.png
  outputs/creatives/<brief_id>/metadata.json
  outputs/creatives/generation_log_<ts>.json

Env: OPENAI_API_KEY (from .env or environment)

Examples:
  python agents/designer/generate.py --briefs 100plus.boomerangme.com
  python agents/designer/generate.py --briefs <slug> --variants A --placements feed_square
  python agents/designer/generate.py --briefs <slug> --dry-run
  python agents/designer/generate.py --briefs <slug> --skip-existing --concurrency 4 --qa
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from meta_placements import (  # noqa: E402
    DEFAULT_PLACEMENT_KEYS,
    PLACEMENTS,
    Placement,
    gen_size_str,
    resolve_placement,
)
import compositor  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIEFS_DIR = REPO_ROOT / "outputs" / "briefs"
CREATIVES_DIR = REPO_ROOT / "outputs" / "creatives"

MODEL = "gpt-image-2"
DEFAULT_QUALITY = "medium"
ALL_VARIANTS = ["A", "B", "C"]


# ---------------------------------------------------------------------------
# Env / client
# ---------------------------------------------------------------------------
def load_env() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
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
    return OpenAI(api_key=key, timeout=300, max_retries=0)


# ---------------------------------------------------------------------------
# Brief loading → normalized jobs
# ---------------------------------------------------------------------------
def load_jobs(briefs_path: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
    """Return (jobs, source_kind). source_kind: 'briefs' (composite-capable) or 'prompts'."""
    if briefs_path:
        p = Path(briefs_path)
        if not p.exists():
            cands = sorted(BRIEFS_DIR.glob(f"creative_briefs_{briefs_path}_*.json"))
            if not cands:
                sys.exit(f"ERROR: no briefs found for '{briefs_path}'")
            p = cands[-1]
        data = json.loads(p.read_text())
        return (_jobs_from_prompts(data), "prompts") if "image_prompts" in data \
            else (_jobs_from_briefs(data), "briefs")

    prompts_file = BRIEFS_DIR / "image_generation_prompts.json"
    if prompts_file.exists():
        return _jobs_from_prompts(json.loads(prompts_file.read_text())), "prompts"
    per_funnel = sorted(BRIEFS_DIR.glob("creative_briefs_*.json"))
    if per_funnel:
        return _jobs_from_briefs(json.loads(per_funnel[-1].read_text())), "briefs"
    briefs_file = BRIEFS_DIR / "creative_briefs.json"
    if briefs_file.exists():
        return _jobs_from_briefs(json.loads(briefs_file.read_text())), "briefs"
    sys.exit(f"ERROR: no briefs found in {BRIEFS_DIR}")


def _scene_prompt(concept_name: str, visual_concept: str, colors: List[str], p: Placement) -> str:
    return (
        f"Professional Meta Ads background SCENE for '{concept_name}' "
        f"({p.aspect_ratio}, {p.target[0]}x{p.target[1]}).\n"
        f"SCENE:\n{visual_concept}\n\n"
        f"COLOR PALETTE: {', '.join(colors) if colors else 'clean, brand-appropriate'}.\n"
        "STYLE: professional commercial photography, photorealistic, high production value, "
        "natural lighting, clear focal point, premium and appetizing.\n"
        "CRITICAL: Render the SCENE ONLY. Do NOT draw any text, words, letters, numbers, "
        "logos, watermarks, buttons or UI — produce a clean photographic background. Leave "
        "calm negative space in the upper area and an uncluttered lower band so a headline and "
        "a call-to-action button can be added in post-production. Keep key subjects centered."
    )


def _baked_prompt(concept_name: str, visual_concept: str, hook: str, subhead: str,
                  cta: str, colors: List[str], p: Placement, audience: str = "") -> str:
    """One cohesive, finished ad — text DESIGNED INTO the image. Minimal copy: an audience
    BADGE + ONE headline + ONE short money-focused line + a CTA button. No paragraphs."""
    try:
        accent = "#%02X%02X%02X" % compositor.pick_accent(colors)
    except Exception:
        accent = "a vivid accent color"
    palette = ", ".join(colors) if colors else "a clean, premium brand palette"
    sub = (subhead or "").strip()
    badge = (audience or "").strip()
    n = 1
    lines = []
    if badge:
        lines.append(f"  {n}) AUDIENCE BADGE — a small, distinct rounded pill/tag at the very TOP "
                     f"(eyebrow above the headline), in the accent color {accent} or a contrasting "
                     f"chip, that names who the ad is for: \"{badge}\". It must read as a tag/label, "
                     f"clearly smaller than the headline.\n")
        n += 1
    lines.append(f"  {n}) HEADLINE — the single dominant element, big and bold: \"{hook}\"\n")
    n += 1
    if sub:
        lines.append(f"  {n}) ONE short supporting line — large enough to read easily on a phone, "
                     f"high contrast: \"{sub}\"\n")
        n += 1
    lines.append(
        f"  {n}) CTA BUTTON — a clearly drawn rounded button filled with {accent} with the label "
        f"\"{cta}\". Give the button a soft DROP SHADOW so it visibly lifts off the background and "
        f"stands out. Place a realistic white MOUSE CURSOR (an arrow pointer with a thin dark "
        f"outline, or a hand/pointer cursor) hovering over the button's lower-right area as if about "
        f"to click it — a deliberate click-prompt to boost CTR.\n")
    return (
        f"Design ONE single, cohesive, finished professional Meta Ads creative — a complete "
        f"advertisement where the typography is DESIGNED INTO the composition together with the "
        f"imagery (a unified graphic-design layout, NOT text pasted on top of a photo). "
        f"Exact canvas {p.aspect_ratio}, {p.target[0]}x{p.target[1]}px.\n\n"
        f"CONCEPT: {concept_name}\nSCENE / IMAGERY:\n{visual_concept}\n\n"
        f"PUT EXACTLY THESE TEXT ELEMENTS AND NOTHING ELSE (modern bold sans-serif, perfectly "
        f"spelled, fully visible, never cropped, no extra/duplicate/gibberish words):\n"
        + "".join(lines)
        + f"\nThe audience badge SEGMENTS the viewer — it should grab the right person ('that's me') "
        f"before they read the headline.\n"
        f"STRICT: do NOT add any paragraph, body copy, fine print, or any other text beyond the "
        f"above. Every word must be large and clearly legible on mobile — no small unreadable text.\n"
        f"ART DIRECTION: integrated, premium, high-converting layout; clear hierarchy "
        f"(audience badge → headline → imagery → CTA). Text sits over clean areas / negative space / "
        f"a subtle scrim for strong contrast. Brand palette: {palette}. Commercial photography "
        f"blended with crisp graphic-design typography. Keep all text inside safe margins "
        f"({p.safe_zone}). Sharp, high-resolution, balanced. No watermark."
    )


def _jobs_from_briefs(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    for b in data.get("creative_briefs", []):
        cd = b.get("creative_direction", {})
        concept = b.get("concept_name", "")
        vc = cd.get("visual_concept") or cd.get("layout", "clean modern marketing scene")
        colors = cd.get("color_scheme") or cd.get("colors") or []
        hv = b.get("hook_variations", {}) or {}
        hooks = {"A": hv.get("hook_a"), "B": hv.get("hook_b"), "C": hv.get("hook_c")}
        if not any(hooks.values()):
            hooks = {"A": b.get("value_proposition", "")}
        cta = (b.get("cta", {}) or {}).get("primary", "Learn More")
        # short, money-focused supporting line (≤~12 words) — NOT the long body paragraph
        subhead = (b.get("subhead") or "").strip()
        if not subhead:
            words = (b.get("body_copy", "") or "").split()
            subhead = " ".join(words[:12]) + ("…" if len(words) > 12 else "")
        # audience call-out badge (segments the viewer); fall back to target_audience
        audience = (b.get("audience_callout") or "").strip()
        formats = []
        for fmt in cd.get("formats", []):
            p = resolve_placement(aspect_ratio=fmt.get("aspect_ratio", ""),
                                  dimensions=fmt.get("dimensions", ""), name=fmt.get("name", ""))
            formats.append({
                "placement": p,
                "has_scene": True,
                "scene_prompt": _scene_prompt(concept, vc, colors, p),
                "baked": {v: _baked_prompt(concept, vc, h, subhead, cta, colors, p, audience)
                          for v, h in hooks.items() if h},
            })
        jobs.append({
            "brief_id": b.get("brief_id", "brief"), "concept_name": concept,
            "hooks": {v: h for v, h in hooks.items() if h},
            "body": subhead, "cta": cta, "colors": colors,
            "logo_path": cd.get("logo_path"), "formats": formats,
        })
    return jobs


def _jobs_from_prompts(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    for item in data.get("image_prompts", []):
        hook = item.get("hook", "")
        formats = []
        for fmt in item.get("formats", []):
            p = resolve_placement(aspect_ratio=fmt.get("aspect_ratio", ""),
                                  dimensions=fmt.get("dimensions", ""), name=fmt.get("format_name", ""))
            formats.append({"placement": p, "has_scene": False, "scene_prompt": None,
                            "baked": {"A": fmt.get("detailed_prompt", "")}})
        jobs.append({"brief_id": item.get("brief_id", "brief"),
                     "concept_name": item.get("concept_name", ""),
                     "hooks": {"A": hook}, "body": "", "cta": "", "colors": [],
                     "logo_path": None, "formats": formats})
    return jobs


# ---------------------------------------------------------------------------
# gpt-image-2 via the Responses API BACKGROUND mode (submit → poll → fetch).
# This avoids holding a long synchronous connection (which hit a ~60s reset wall):
# we submit all jobs (each returns an id in ~3s), they render server-side in parallel,
# and we poll for results. Wall-clock ≈ slowest job, not the sum.
# ---------------------------------------------------------------------------
ORCHESTRATOR_MODEL = "gpt-4.1-mini"  # cheap mainline model; only invokes the image tool
_MONEY_RE = re.compile(r"\$\s?\d[\d,. ]*(k|m|mo|month|/mo|/month|year)?", re.I)
_CLAIM_RE = re.compile(r"\b(guarantee[d]?|income|revenue|earn|profit|MRR|ROI|\d+%)\b", re.I)


def soften(prompt: str) -> str:
    return _CLAIM_RE.sub("great outcomes", _MONEY_RE.sub("strong results", prompt))


def submit_image(client, prompt: str, p: Placement, quality: str) -> str:
    """Queue one gpt-image-2 render in background; return the response id (fast, ~3s)."""
    r = client.responses.create(
        model=ORCHESTRATOR_MODEL,
        input="Use the image_generation tool to render EXACTLY this, do not change the wording:\n\n" + prompt,
        tools=[{"type": "image_generation", "model": MODEL, "size": gen_size_str(p), "quality": quality}],
        background=True, store=True,
    )
    return r.id


def _extract_image(resp) -> Optional[bytes]:
    for o in (resp.output or []):
        if getattr(o, "type", "") == "image_generation_call" and getattr(o, "result", None):
            return base64.b64decode(o.result)
    return None


def collect_images(client, id_map: Dict[Any, str], timeout: int = 1200, poll: int = 6) -> Dict[Any, Any]:
    """Poll background response ids until done. Returns {key: bytes | Exception}."""
    pending = dict(id_map)
    out: Dict[Any, Any] = {}
    deadline = time.time() + timeout
    while pending and time.time() < deadline:
        time.sleep(poll)
        for key, rid in list(pending.items()):
            try:
                r = client.responses.retrieve(rid)
            except Exception:  # transient poll error — retry next round
                continue
            if r.status == "completed":
                img = _extract_image(r)
                out[key] = img if img else RuntimeError("completed but no image in response")
                del pending[key]
            elif r.status in ("failed", "cancelled", "incomplete"):
                out[key] = RuntimeError(f"{r.status}: {getattr(r, 'error', None) or r.status}")
                del pending[key]
        print(f"   …{len(out)}/{len(id_map)} ready", end="\r", file=sys.stderr)
    for key in pending:
        out[key] = RuntimeError("timeout")
    print(f"   {len(out)}/{len(id_map)} done", file=sys.stderr)
    return out


def _to_target_png(raw: bytes, p: Placement) -> bytes:
    """Resize a baked render to the exact Meta target, return PNG bytes."""
    from PIL import Image, ImageOps

    img = ImageOps.fit(Image.open(io.BytesIO(raw)).convert("RGB"), p.target, Image.Resampling.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


# ---------------------------------------------------------------------------
# Vision QA (optional)
# ---------------------------------------------------------------------------
def qa_check(client, png: bytes, headline: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    try:
        b64 = base64.b64encode(png).decode()
        resp = client.chat.completions.create(
            model=model, temperature=0, max_tokens=200,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": [
                {"type": "text", "text": (
                    f"This is an ad creative. Expected headline: \"{headline}\". Return JSON "
                    "{\"headline_readable\":bool,\"headline_correct\":bool,\"text_cropped\":bool,"
                    "\"looks_broken\":bool,\"issues\":\"...\"}.")},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "low"}},
            ]}],
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run(args: argparse.Namespace) -> int:
    # Phase-aware quality default: concepts in LOW (fast, reliable under the 60s limit) →
    # refine → resizes in HIGH. Explicit --quality overrides.
    if args.quality is None:
        args.quality = {"concept": "low", "resize": "high", "all": "medium"}[args.phase]
    jobs, kind = load_jobs(args.briefs)
    if args.brief:
        wanted = {b.strip() for b in args.brief.split(",")}
        jobs = [j for j in jobs if j["brief_id"] in wanted]
    if args.limit:
        jobs = jobs[: args.limit]
    if not jobs:
        sys.exit("ERROR: no briefs matched the filter.")

    pfilter: Optional[set] = None
    if args.placements:
        pfilter = {k.strip() for k in args.placements.split(",")}
        if pfilter - set(PLACEMENTS):
            sys.exit(f"ERROR: unknown placements {pfilter - set(PLACEMENTS)}. Valid: {list(PLACEMENTS)}")

    variants = [v for v in (args.variants.upper().split(",") if args.variants else ALL_VARIANTS) if v in ALL_VARIANTS]
    # DEFAULT = one cohesive image with text designed in (model). Opt into overlay with --text-mode composite.
    composite = args.text_mode == "composite"

    # build output units: (job, fmt, variant) → out_path
    units: List[Dict[str, Any]] = []
    for job in jobs:
        formats = [f for f in job["formats"] if pfilter is None or f["placement"].key in pfilter]
        if not formats and pfilter:
            continue
        # APPROVAL FLOW: concept = base placement only (no resizes); resize = everything else.
        if args.phase == "concept":
            base = [f for f in formats if f["placement"].key == args.base]
            formats = base or (formats[:1] if formats else [])
        elif args.phase == "resize":
            formats = [f for f in formats if f["placement"].key != args.base]
        for f in formats:
            avail = [v for v in variants if v in job["hooks"]] or [next(iter(job["hooks"]))]
            for v in avail:
                p = f["placement"]
                out = CREATIVES_DIR / job["brief_id"] / f"{p.key}_{v}.png"
                units.append({"job": job, "fmt": f, "variant": v, "out": out,
                              "composite": composite and f["has_scene"]})

    if args.skip_existing:
        units = [u for u in units if not u["out"].exists()]
    if not units:
        print("Nothing to do (all outputs exist?)."); return 0

    mode_lbl = "composite(scene+overlay)" if composite else "model(text baked)"
    phase_lbl = {"concept": f"CONCEPT (base={args.base}, no resizes — for approval)",
                 "resize": f"RESIZE (all but {args.base} — post-approval)", "all": "ALL"}[args.phase]
    print(f"▶ Agent 5 · phase={phase_lbl} · {len(jobs)} briefs · {len(units)} creatives · "
          f"variants={variants} · mode={mode_lbl} · quality={args.quality} · concurrency={args.concurrency}")
    if args.dry_run:
        for u in units:
            print(f"[dry-run] {u['job']['brief_id']} · {u['fmt']['placement'].key}_{u['variant']} "
                  f"({'composite' if u['composite'] else 'model'})")
        print(f"\nDry run: {len(units)} creatives planned.")
        return 0

    client = make_client()

    def _submit_all(spec):  # spec: list of (key, prompt, placement) → {key: id|Exception}
        res: Dict[Any, Any] = {}
        with ThreadPoolExecutor(max_workers=max(4, args.concurrency)) as ex:
            futs = {ex.submit(submit_image, client, pr, pl, args.quality): k for k, pr, pl in spec}
            for f in as_completed(futs):
                k = futs[f]
                try:
                    res[k] = f.result()
                except Exception as e:  # noqa: BLE001
                    res[k] = e
        return res

    def _retry_failed(results, spec_of):
        retry = [(k, soften(pr), pl) for k, (pr, pl) in
                 ((k, spec_of(k)) for k, v in results.items() if isinstance(v, Exception))]
        if not retry:
            return
        print(f"  ↻ {len(retry)} failed → resubmitting softened…", file=sys.stderr)
        ids = _submit_all(retry)
        live = {k: v for k, v in ids.items() if not isinstance(v, Exception)}
        for k, v in collect_images(client, live).items():
            results[k] = v

    # SUBMIT — composite → scenes (one per brief×placement, pre-softened); model → baked per unit.
    scene_keys = {(u["job"]["brief_id"], u["fmt"]["placement"].key): u for u in units if u["composite"]}
    model_units = [u for u in units if not u["composite"]]
    uid_to_unit = {id(u): u for u in model_units}

    scene_spec = [(k, soften(u["fmt"]["scene_prompt"]), u["fmt"]["placement"]) for k, u in scene_keys.items()]
    baked_spec = [(id(u), u["fmt"]["baked"][u["variant"]], u["fmt"]["placement"]) for u in model_units]
    print(f"  submitting {len(scene_spec) + len(baked_spec)} background render jobs (gpt-image-2 {args.quality})…")
    scene_ids = _submit_all(scene_spec)
    baked_ids = _submit_all(baked_spec)

    # POLL — all render server-side in parallel; collect (wall-clock ≈ slowest job)
    scenes = collect_images(client, {k: v for k, v in scene_ids.items() if not isinstance(v, Exception)})
    scenes.update({k: v for k, v in scene_ids.items() if isinstance(v, Exception)})
    model_raw = collect_images(client, {k: v for k, v in baked_ids.items() if not isinstance(v, Exception)})
    model_raw.update({k: v for k, v in baked_ids.items() if isinstance(v, Exception)})

    # moderation retry (one softened resubmit for anything that failed)
    _retry_failed(scenes, lambda k: (scene_keys[k]["fmt"]["scene_prompt"], scene_keys[k]["fmt"]["placement"]))
    _retry_failed(model_raw, lambda k: (uid_to_unit[k]["fmt"]["baked"][uid_to_unit[k]["variant"]],
                                        uid_to_unit[k]["fmt"]["placement"]))

    # resize baked renders → exact Meta target
    model_out: Dict[int, Any] = {}
    for uid, raw in model_raw.items():
        if isinstance(raw, Exception):
            model_out[uid] = raw
        else:
            try:
                model_out[uid] = _to_target_png(raw, uid_to_unit[uid]["fmt"]["placement"])
            except Exception as e:  # noqa: BLE001
                model_out[uid] = e

    # assemble outputs
    log: Dict[str, Any] = {"timestamp": datetime.now(timezone.utc).isoformat(), "model": MODEL,
                           "quality": args.quality, "mode": mode_lbl, "results": []}
    ok = fail = 0
    qa_client = client if args.qa else None
    per_brief: Dict[str, List[Dict[str, Any]]] = {}

    for u in units:
        job, f, v = u["job"], u["fmt"], u["variant"]
        p: Placement = f["placement"]
        u["out"].parent.mkdir(parents=True, exist_ok=True)
        entry = {"brief_id": job["brief_id"], "placement": p.key, "variant": v,
                 "aspect_ratio": p.aspect_ratio, "target_size": f"{p.target[0]}x{p.target[1]}",
                 "file": str(u["out"].relative_to(REPO_ROOT)),
                 "headline": job["hooks"].get(v, "")}
        try:
            if u["composite"]:
                scene = scenes.get((job["brief_id"], p.key))
                if isinstance(scene, Exception) or scene is None:
                    raise RuntimeError(f"scene failed: {scene}")
                png = compositor.compose(scene, p.target, p.key, job["hooks"][v],
                                         job["body"], job["cta"], job["colors"], job.get("logo_path"))
                entry["prompt"] = f["scene_prompt"]
            else:
                res = model_out.get(id(u))
                if isinstance(res, Exception) or res is None:
                    raise RuntimeError(f"generation failed: {res}")
                png = res
                entry["prompt"] = f["baked"][v]
            u["out"].write_bytes(png)
            entry["status"] = "success"
            if qa_client:
                entry["qa"] = qa_check(qa_client, png, job["hooks"].get(v, ""))
            ok += 1
            qa_flag = ""
            if entry.get("qa") and (entry["qa"].get("text_cropped") or entry["qa"].get("looks_broken")):
                qa_flag = "  ⚠ QA"
            print(f"✅ {job['brief_id']} · {p.key}_{v}{qa_flag} → {entry['file']}")
        except Exception as e:  # noqa: BLE001
            entry["status"] = "error"
            entry["error"] = str(e)
            fail += 1
            print(f"❌ {job['brief_id']} · {p.key}_{v} FAILED: {e}", file=sys.stderr)
        log["results"].append(entry)
        per_brief.setdefault(job["brief_id"], []).append(entry)

    # per-brief metadata (merge across runs, keyed by placement_variant)
    for bid, entries in per_brief.items():
        mpath = CREATIVES_DIR / bid / "metadata.json"
        by_key: Dict[str, Any] = {}
        if mpath.exists():
            try:
                for c in json.loads(mpath.read_text()).get("creatives", []):
                    by_key[f"{c.get('placement')}_{c.get('variant')}"] = c
            except (json.JSONDecodeError, OSError):
                pass
        for c in entries:
            by_key[f"{c['placement']}_{c['variant']}"] = c
        mpath.write_text(json.dumps({"brief_id": bid, "model": MODEL, "quality": args.quality,
                                     "generated_at": log["timestamp"],
                                     "creatives": list(by_key.values())}, indent=2))

    log["successful"], log["failed"] = ok, fail
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (CREATIVES_DIR / f"generation_log_{ts}.json").write_text(json.dumps(log, indent=2))
    print(f"\nDone: {ok} ok, {fail} failed → outputs/creatives/generation_log_{ts}.json")
    return 1 if fail else 0


def main() -> None:
    load_env()
    ap = argparse.ArgumentParser(description="Agent 5 Designer — gpt-image-2 generator (hybrid compositing)")
    ap.add_argument("--briefs", help="creative_briefs_<slug>_<ts>.json path or bare <slug> (latest); else auto-detect")
    ap.add_argument("--brief", help="comma-separated brief ids (default: all)")
    ap.add_argument("--placements", help=f"comma-separated placement keys. Valid: {','.join(PLACEMENTS)}")
    ap.add_argument("--phase", choices=["concept", "resize", "all"], default="all",
                    help="APPROVAL FLOW: 'concept' = base placement only (for approval, no resizes); "
                         "'resize' = all OTHER placements (run after approval); 'all' = everything")
    ap.add_argument("--base", default="feed_square",
                    help="base/master placement for the concept phase (default feed_square)")
    ap.add_argument("--variants", help="comma-separated A,B,C (default: all available)")
    ap.add_argument("--text-mode", choices=["model", "composite"], default="model",
                    help="model (default) = one cohesive image with text designed in by gpt-image-2; "
                         "composite = scene + Pillow text overlay")
    ap.add_argument("--quality", default=None, choices=["low", "medium", "high", "auto"],
                    help="default is phase-aware: concept→low (fast iteration), resize→high, all→medium")
    ap.add_argument("--concurrency", type=int, default=3, help="parallel gpt-image-2 calls")
    ap.add_argument("--skip-existing", action="store_true", help="skip placements/variants already on disk")
    ap.add_argument("--qa", action="store_true", help="run a vision QA check on each creative")
    ap.add_argument("--limit", type=int, help="only first N briefs")
    ap.add_argument("--dry-run", action="store_true", help="plan only, no API calls")
    args = ap.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
