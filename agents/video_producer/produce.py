#!/usr/bin/env python3
"""
Agent 7 — Video Producer.

Renders Agent 6 storyboards into platform-ready VIDEO ads. Mirror of Agent 5 (static)
for video: for each concept it renders the Veo 3 clips (submit → poll → download, like
Agent 5's background mode), stitches them, burns the typography/captions overlay on top
(Veo can't render text), and exports per-platform cuts (TikTok / Shorts / Reels + 4:5/16:9
derivatives) to each platform's spec. Veo 3 is the next-series renderer; this is the
production/assembly engine that drives it.

Pipeline per concept:
  storyboards_<slug>.json → [render clips on Veo 3] → trim to clip spans → concat master
  → burn timed text overlays → export per-platform cuts → outputs/videos/<brief_id>/

Async queue flow (recommended — submit, leave, come back; Veo keeps clips ~2 days):
  python agents/video_producer/produce.py <slug> --submit            # queue clips, save op-ids, EXIT
  python agents/video_producer/produce.py <slug> --collect           # download ready + assemble (re-run)

Other:
  python agents/video_producer/produce.py <slug> --dry-run           # full plan, no render
  python agents/video_producer/produce.py <slug> --synthetic         # placeholder assemble (no key)
  python agents/video_producer/produce.py <slug>                     # blocking one-shot (submit+wait)
  python agents/video_producer/produce.py <slug> --brief brief_001 --model veo-3.0-fast-generate-001

Env: GOOGLE_API_KEY (or GEMINI_API_KEY) for Veo. Needs ffmpeg on PATH.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
STORY_DIR = REPO_ROOT / "outputs" / "storyboards"
VIDEO_DIR = REPO_ROOT / "outputs" / "videos"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import veo_client  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "agents" / "video_storyboard"))
from video_specs import TARGETS, VEO3  # noqa: E402


# ---------------------------------------------------------------------------
def load_env() -> None:
    envp = REPO_ROOT / ".env"
    if envp.exists():
        for line in envp.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _latest_storyboard(slug: str) -> Optional[Path]:
    files = sorted(STORY_DIR.glob(f"storyboards_{slug}_*.json"))
    return files[-1] if files else None


def _ff(args: List[str]) -> None:
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()[:400]}")


def ensure_ffmpeg() -> None:
    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
        sys.exit("ERROR: ffmpeg not found on PATH (brew install ffmpeg).")


# ---------------------------------------------------------------------------
# Clip planning: group shots by clip_id → one Veo render per clip (8s grid).
# ALL text is rendered IN-SCENE by Veo (cinematic typography) — no post overlays.
# ---------------------------------------------------------------------------
import re as _re

# Treatments are STABLE + simple (NOT morphing/assembling — mid-animation frames look garbled).
_DEFAULT_TREATMENT = {
    "hook": "a clean bold steady title in the upper-middle, fully formed",
    "solution/proof": "a big bold hero title in brand green with subtle depth, centred and steady",
    "proof": "a clean bold title, centred and steady",
    "cta": "set inside a clean rounded brand-green button, centred in the lower-middle, fully formed",
}


def _text_directive(shot: Dict[str, Any], palette: str) -> str:
    txt = _re.sub(r"\[[^\]]*\]", "", (shot.get("on_screen_text") or "")).strip()
    txt = _re.sub(r"\s{2,}", " ", txt).strip(" ·|/")
    if not txt:
        return ""
    treat = (shot.get("veo_text_treatment") or "").strip() or \
        _DEFAULT_TREATMENT.get((shot.get("beat_role") or "").lower(), "a clean bold centred title")
    return (f" TITLE TEXT — overlay ONE LARGE bold title-card across the OPEN area of the frame, like a "
            f"film title (big, spanning roughly a third to half the frame width, in clear empty space, "
            f"NOT placed on the phone, a screen, a wall, a sign, clothing or any object — it floats over "
            f"the scene). It must read EXACTLY \"{txt}\" — spell it precisely, ONLY these words, every "
            f"letter fully formed and STEADY (no morphing/assembling/letters mid-flight), clean bold "
            f"sans-serif, high-contrast and clearly legible, {treat}; brand palette {palette}. Render it "
            f"EXACTLY ONCE — do NOT duplicate or echo it, and render NO other words, numbers, captions, "
            f"menus, labels or signage anywhere in the frame (no text on phone screens, props or walls).")


def compose_clip_prompt(clip: Dict[str, Any], colors: List[str]) -> str:
    """Build one Veo prompt for a clip — scene + ONE short, steady, exactly-spelled in-scene title per beat."""
    cs = clip["shots"]
    start = min(float(s["start_s"]) for s in cs)
    palette = ", ".join(colors) if colors else "the brand palette"
    head = (f"Vertical 9:16, Hollywood-grade cinematic commercial, {VEO3['max_clip_s']}s. Photoreal, "
            f"premium lighting, shallow depth of field, filmic color. Native audio per beat; restate "
            f"subject/setting/style each beat. PLAIN, uncluttered backgrounds — NO incidental signage, "
            f"posters, menus, screens-of-text or any writing in the environment. The ONLY text in the "
            f"whole clip is the short title(s) specified below, rendered cleanly and spelled exactly.")
    lines = [head]
    for s in cs:
        a = round(float(s["start_s"]) - start, 1)
        b = round(float(s["end_s"]) - start, 1)
        lines.append(f"[{a:.1f}s-{b:.1f}s] {s['veo_prompt'].strip()}{_text_directive(s, palette)}")
    return "\n".join(lines)


def plan_clips(master: Dict[str, Any], colors: List[str]) -> List[Dict[str, Any]]:
    shots = master.get("shots", [])
    order: List[str] = []
    by_clip: Dict[str, List[Dict[str, Any]]] = {}
    for s in shots:
        cid = s.get("clip_id", f"clip_{s.get('shot_no')}")
        by_clip.setdefault(cid, []).append(s)
        if cid not in order:
            order.append(cid)
    clips = []
    for cid in order:
        cs = by_clip[cid]
        start = min(float(s["start_s"]) for s in cs)
        end = max(float(s["end_s"]) for s in cs)
        span = round(min(end - start, VEO3["max_clip_s"]), 2)
        clip = {"clip_id": cid, "shots": cs, "span_s": span}
        clip["prompt"] = compose_clip_prompt(clip, colors)
        clips.append(clip)
    return clips


# ---------------------------------------------------------------------------
# ffmpeg assembly
# ---------------------------------------------------------------------------
_SYNTH_COLORS = ["0x16314A", "0x1F4D3A", "0x4A2A2A", "0x2A2A4A", "0x3A2A4A"]


def synthetic_clip(out: Path, seconds: float, idx: int = 0) -> None:
    """Placeholder render (no Veo): a colored gradient 9:16 clip + silent audio.
    (Only for testing the stitch/overlay/export pipeline without a Veo key.)"""
    out.parent.mkdir(parents=True, exist_ok=True)
    c = _SYNTH_COLORS[idx % len(_SYNTH_COLORS)]
    _ff(["-f", "lavfi", "-i", f"gradients=s=1080x1920:c0={c}:c1=0x0A0A0A:d={seconds}:r=24",
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
         "-t", f"{seconds}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-shortest", str(out)])


def trim_norm(inp: Path, seconds: float, out: Path) -> None:
    """Trim to `seconds` and normalize to 1080x1920/24fps/aac for clean concat."""
    _ff(["-i", str(inp), "-t", f"{seconds}",
         "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24",
         "-c:a", "aac", "-ar", "48000", "-ac", "2", str(out)])


def concat(parts: List[Path], out: Path) -> None:
    inputs: List[str] = []
    for p in parts:
        inputs += ["-i", str(p)]
    n = len(parts)
    streams = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    fc = f"{streams}concat=n={n}:v=1:a=1[v][a]"
    _ff([*inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out)])


def export_cut(master: Path, out: Path, duration_s: float, aspect: str) -> None:
    """Trim to platform duration + crop/scale to the target aspect + faststart."""
    if aspect == "9:16":
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    elif aspect == "4:5":
        vf = "crop=in_w:in_w*5/4,scale=1080:1350"
    elif aspect == "1:1":
        vf = "crop=in_w:in_w,scale=1080:1080"
    elif aspect == "16:9":
        vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
    else:
        vf = "scale=1080:1920"
    _ff(["-i", str(master), "-t", f"{duration_s}", "-vf", f"{vf},fps=24",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-r", "24",
         "-c:a", "aac", "-ar", "48000", "-movflags", "+faststart", str(out)])


# ---------------------------------------------------------------------------
# Vision QA gate: check that each clip's title text rendered correctly; if not,
# re-render that clip (new Veo seed) until it passes or attempts run out.
# ---------------------------------------------------------------------------
def _openai():
    from openai import OpenAI

    k = os.environ.get("OPENAI_API_KEY")
    return OpenAI(api_key=k, timeout=90, max_retries=2) if k else None


def _frame_bytes(video: Path, t: float) -> bytes:
    out = video.parent / f"_qa_{int(t*10)}.png"
    _ff(["-ss", f"{t}", "-i", str(video), "-frames:v", "1", str(out)])
    b = out.read_bytes()
    out.unlink(missing_ok=True)
    return b


def qa_clip(oai, clip: Dict[str, Any], raw: Path) -> Dict[str, Any]:
    """Check every text beat in a clip. Returns {'ok': bool, 'fails': [...]}. Veo clips are 8s;
    sample each shot at its mid-point relative to the clip start."""
    cs = clip["shots"]
    start = min(float(s["start_s"]) for s in cs)
    fails = []
    for s in cs:
        txt = _re.sub(r"\[[^\]]*\]", "", (s.get("on_screen_text") or "")).strip(" ·|/")
        if not txt:
            continue
        mid = (float(s["start_s"]) + float(s["end_s"])) / 2 - start
        mid = max(0.3, min(mid, VEO3["max_clip_s"] - 0.3))
        try:
            b64 = base64.b64encode(_frame_bytes(raw, mid)).decode()
            r = oai.chat.completions.create(
                model="gpt-4o-mini", temperature=0, max_tokens=160,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": [
                    {"type": "text", "text":
                        f"This is a frame from a video ad. It should display the title text EXACTLY: "
                        f"\"{txt}\". Reply JSON {{\"correct\":bool,\"found\":\"<text you see>\","
                        f"\"other_gibberish_text\":bool}}. Set correct=true ONLY if that exact text is "
                        f"present, clearly legible, spelled exactly right, and not duplicated."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}},
                ]}])
            v = json.loads(r.choices[0].message.content)
            if not v.get("correct") or v.get("other_gibberish_text"):
                fails.append({"shot": s["shot_no"], "expected": txt, "saw": v.get("found"),
                              "gibberish": v.get("other_gibberish_text")})
        except Exception as e:  # noqa: BLE001
            print(f"   (qa skip shot {s['shot_no']}: {e})", file=sys.stderr)
    return {"ok": not fails, "fails": fails}


def render_clip(client, clip: Dict[str, Any], raw: Path, args: argparse.Namespace) -> Path:
    """Submit one clip, poll, download → raw (with transient-retry)."""
    op = {clip["clip_id"]: veo_client.submit_clip(client, clip["prompt"], model=args.model,
                                                  aspect_ratio="9:16", resolution=args.resolution,
                                                  duration_seconds=str(VEO3["max_clip_s"]))}
    got = veo_client.poll_and_download(client, op, {clip["clip_id"]: raw})
    v = got[clip["clip_id"]]
    if isinstance(v, Exception):
        raise RuntimeError(str(v))
    return v


def qa_gate(client, oai, clips, clip_files: Dict[str, Path], args: argparse.Namespace) -> None:
    """Re-render any clip whose title text fails QA, up to args.qa_retries."""
    if not oai:
        print("  (QA requested but OPENAI_API_KEY missing — skipping)", file=sys.stderr)
        return
    by_id = {c["clip_id"]: c for c in clips}
    for cid, raw in list(clip_files.items()):
        for attempt in range(args.qa_retries + 1):
            rep = qa_clip(oai, by_id[cid], Path(raw))
            if rep["ok"]:
                if attempt:
                    print(f"  ✓ QA {cid}: text correct (after {attempt} re-render(s))")
                break
            print(f"  ⚠ QA {cid} failed: {rep['fails']}", file=sys.stderr)
            if attempt >= args.qa_retries:
                print(f"  ✗ QA {cid}: giving up after {args.qa_retries} re-renders", file=sys.stderr)
                break
            print(f"  ↻ re-rendering {cid} (QA attempt {attempt + 1}/{args.qa_retries})…")
            Path(raw).unlink(missing_ok=True)
            clip_files[cid] = render_clip(client, by_id[cid], Path(raw), args)


def _jobs_path(slug: str) -> Path:
    return VIDEO_DIR / f"_jobs_{slug}.json"


def _clip_raw(bid: str, cid: str) -> Path:
    return VIDEO_DIR / bid / "_work" / f"{cid}_raw.mp4"


def assemble_concept(sb: Dict[str, Any], clip_files: Dict[str, Path], args: argparse.Namespace) -> Dict[str, Any]:
    """Steps 2–4: trim clips to span → concat master → per-platform exports. Text is already
    in-frame from Veo (no overlay)."""
    bid = sb["brief_id"]
    master = sb["master"]
    out_dir = VIDEO_DIR / bid
    work = out_dir / "_work"
    clips = plan_clips(master, (sb.get("brand", {}) or {}).get("colors", []))
    res = {"brief_id": bid, "concept_name": sb.get("concept_name"), "exports": []}

    trimmed = []
    for c in clips:
        t = work / f"{c['clip_id']}_trim.mp4"
        trim_norm(clip_files[c["clip_id"]], c["span_s"], t)
        trimmed.append(t)
    master_mp4 = out_dir / "master_9x16.mp4"
    if len(trimmed) == 1:
        trim_norm(trimmed[0], master["target_duration_s"], master_mp4)
    else:
        concat(trimmed, master_mp4)
    print(f"  ✅ {bid} · master_9x16 ({master['target_duration_s']}s) → {master_mp4.relative_to(REPO_ROOT)}")

    if getattr(args, "master_only", False):
        res["master"] = str(master_mp4.relative_to(REPO_ROOT))
        return res
    for cut in sb.get("platform_cuts", []):
        tkey = cut.get("platform_target")
        spec = TARGETS.get(tkey)
        aspect = cut.get("aspect_ratio") or (spec.aspect_ratio if spec else "9:16")
        dur = min(float(cut.get("duration_s") or master["target_duration_s"]), master["target_duration_s"])
        out = out_dir / f"{tkey}.mp4"
        export_cut(master_mp4, out, dur, aspect)
        size_mb = round(out.stat().st_size / 1_000_000, 1)
        res["exports"].append({"platform": tkey, "aspect": aspect, "duration_s": dur,
                               "file": str(out.relative_to(REPO_ROOT)), "size_mb": size_mb})
        print(f"  ✅ {bid} · {tkey} ({aspect}, {dur}s, {size_mb}MB) → {out.relative_to(REPO_ROOT)}")
    return res


def submit_concept(sb: Dict[str, Any], args: argparse.Namespace, client) -> Dict[str, Any]:
    """Queue every (not-yet-rendered) clip on Veo; return {clip_id: {operation, raw, span_s, status}}."""
    bid = sb["brief_id"]
    clips = plan_clips(sb["master"], (sb.get("brand", {}) or {}).get("colors", []))
    (VIDEO_DIR / bid / "_work").mkdir(parents=True, exist_ok=True)
    jobs: Dict[str, Any] = {}
    for c in clips:
        cid = c["clip_id"]
        raw = _clip_raw(bid, cid)
        rec = {"raw": str(raw.relative_to(REPO_ROOT)), "span_s": c["span_s"]}
        if raw.exists() and raw.stat().st_size > 10000:
            rec["status"] = "downloaded"
        else:
            op = veo_client.submit_clip(client, c["prompt"], model=args.model,
                                        aspect_ratio="9:16", resolution=args.resolution,
                                        duration_seconds=str(VEO3["max_clip_s"]))
            rec["operation"] = veo_client.op_name(op)
            rec["status"] = "submitted"
        jobs[cid] = rec
    return jobs


def produce_one(sb: Dict[str, Any], slug: str, args: argparse.Namespace, client) -> Dict[str, Any]:
    """Blocking one-shot: render (or placeholder) all clips, then assemble."""
    bid = sb["brief_id"]
    clips = plan_clips(sb["master"], (sb.get("brand", {}) or {}).get("colors", []))
    work = VIDEO_DIR / bid / "_work"
    work.mkdir(parents=True, exist_ok=True)
    clip_files: Dict[str, Path] = {}

    if args.synthetic:
        for i, c in enumerate(clips):
            p = work / f"{c['clip_id']}_raw.mp4"
            synthetic_clip(p, VEO3["max_clip_s"], i)
            clip_files[c["clip_id"]] = p
    else:
        by_id = {c["clip_id"]: c for c in clips}
        out_paths = {cid: _clip_raw(bid, cid) for cid in by_id}

        def _sub(cids):
            return {cid: veo_client.submit_clip(client, by_id[cid]["prompt"], model=args.model,
                                                aspect_ratio="9:16", resolution=args.resolution,
                                                duration_seconds=str(VEO3["max_clip_s"])) for cid in cids}

        got: Dict[str, Any] = {cid: p for cid, p in out_paths.items()
                               if p.exists() and p.stat().st_size > 10000}
        todo = [cid for cid in by_id if cid not in got]
        if got:
            print(f"  reusing {len(got)} existing clip(s): {list(got)}")
        print(f"  submitting {len(todo)} Veo clip(s) for {bid} → polling…")
        if todo:
            got.update(veo_client.poll_and_download(client, _sub(todo), {c: out_paths[c] for c in todo}))
        for attempt in range(args.retries):
            failed = [cid for cid, v in got.items() if isinstance(v, Exception)]
            if not failed:
                break
            print(f"  ↻ retry {len(failed)} failed clip(s): {failed} (attempt {attempt + 1}/{args.retries})", file=sys.stderr)
            time.sleep(8)
            got.update(veo_client.poll_and_download(client, _sub(failed), {c: out_paths[c] for c in failed}))
        for cid, v in got.items():
            if isinstance(v, Exception):
                raise RuntimeError(f"clip {cid} failed after retries: {v}")
            clip_files[cid] = v

    if args.qa and not args.synthetic:
        qa_gate(client, _openai(), clips, clip_files, args)

    return assemble_concept(sb, clip_files, args)


def _select_boards(args: argparse.Namespace):
    path = Path(args.storyboard) if args.storyboard else _latest_storyboard(args.slug)
    if not path or not path.exists():
        sys.exit(f"ERROR: no storyboards for '{args.slug}'. Run Agent 6 first.")
    boards = json.loads(path.read_text()).get("storyboards", [])
    if args.brief:
        wanted = {b.strip() for b in args.brief.split(",")}
        boards = [b for b in boards if b["brief_id"] in wanted]
    if not boards:
        sys.exit("ERROR: no storyboards matched.")
    return path, boards


def cmd_submit(args: argparse.Namespace) -> int:
    """Queue all Veo clips, persist operation ids to a jobs file, and EXIT (no waiting)."""
    path, boards = _select_boards(args)
    client = veo_client.make_client()
    manifest = {"slug": args.slug, "storyboard": str(path.relative_to(REPO_ROOT)),
                "submitted_at": datetime.now().isoformat(), "model": args.model,
                "resolution": args.resolution, "briefs": {}}
    n_sub = n_have = 0
    for sb in boards:
        jobs = submit_concept(sb, args, client)
        manifest["briefs"][sb["brief_id"]] = {"concept_name": sb.get("concept_name"), "clips": jobs}
        for r in jobs.values():
            n_have += r["status"] == "downloaded"
            n_sub += r["status"] == "submitted"
        print(f"  ↑ {sb['brief_id']}: {sum(1 for r in jobs.values() if r['status']=='submitted')} queued, "
              f"{sum(1 for r in jobs.values() if r['status']=='downloaded')} already done")
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    _jobs_path(args.slug).write_text(json.dumps(manifest, indent=2))
    print(f"\nQueued {n_sub} Veo clip(s) ({n_have} already rendered). Operation ids saved → "
          f"{_jobs_path(args.slug).relative_to(REPO_ROOT)}\n"
          f"Come back later (Veo keeps clips ~2 days) and run:\n"
          f"  python agents/video_producer/produce.py {args.slug} --collect")
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    """Read the jobs file, download ready clips, assemble concepts whose clips are all done."""
    jp = _jobs_path(args.slug)
    if not jp.exists():
        sys.exit(f"ERROR: no jobs file {jp} — run --submit first.")
    manifest = json.loads(jp.read_text())
    sb_path = REPO_ROOT / manifest["storyboard"]
    boards = {b["brief_id"]: b for b in json.loads(sb_path.read_text()).get("storyboards", [])}
    client = veo_client.make_client()
    ensure_ffmpeg()

    pending = downloaded = errored = assembled = 0
    for bid, bdata in manifest["briefs"].items():
        for cid, rec in bdata["clips"].items():
            raw = REPO_ROOT / rec["raw"]
            if raw.exists() and raw.stat().st_size > 10000:
                rec["status"] = "downloaded"; continue
            if rec.get("status") == "downloaded" and not raw.exists():
                rec["status"] = "submitted"  # file vanished → re-collect
            op = rec.get("operation")
            if not op:
                rec["status"] = "error"; errored += 1; continue
            state, payload = veo_client.check(client, op)
            if state == "pending":
                rec["status"] = "pending"; pending += 1
                print(f"  … {bid}/{cid}: rendering")
            elif state == "error":
                rec["status"] = "error"; rec["error"] = payload; errored += 1
                print(f"  ❌ {bid}/{cid}: {payload}", file=sys.stderr)
            else:
                veo_client.download(client, payload, raw)
                rec["status"] = "downloaded"; downloaded += 1
                print(f"  ⬇ {bid}/{cid}: downloaded")

    # assemble concepts whose every clip is downloaded
    for bid, bdata in manifest["briefs"].items():
        recs = bdata["clips"]
        if recs and all(r.get("status") == "downloaded" for r in recs.values()):
            sb = boards.get(bid)
            if not sb:
                continue
            clip_files = {cid: REPO_ROOT / r["raw"] for cid, r in recs.items()}
            try:
                assemble_concept(sb, clip_files, args)
                bdata["assembled"] = True
                assembled += 1
            except Exception as e:  # noqa: BLE001
                print(f"  ❌ assemble {bid}: {e}", file=sys.stderr)

    jp.write_text(json.dumps(manifest, indent=2))
    print(f"\nCollect: {downloaded} downloaded, {pending} still rendering, {errored} errored, "
          f"{assembled} concept(s) assembled → outputs/videos/")
    if pending:
        print(f"  ↻ {pending} clip(s) not ready — re-run --collect in a few minutes.")
    return 0


def run(args: argparse.Namespace) -> int:
    if args.collect:
        return cmd_collect(args)
    path, boards = _select_boards(args)

    if args.dry_run:
        print(f"▶ Agent 7 · {path.name} · {len(boards)} concept(s) · DRY-RUN")
        for sb in boards:
            colors = (sb.get("brand", {}) or {}).get("colors", [])
            clips = plan_clips(sb["master"], colors)
            print(f"\n■ {sb['brief_id']} — {sb.get('concept_name')} "
                  f"({sb['master']['target_duration_s']}s, {len(clips)} Veo clips · text rendered IN-SCENE by Veo)")
            for c in clips:
                roles = " → ".join(s.get("beat_role", "?") for s in c["shots"])
                texts = " | ".join(f'"{s.get("on_screen_text","")[:30]}"' for s in c["shots"] if s.get("on_screen_text"))
                print(f"  • {c['clip_id']} ({c['span_s']}s): {roles}")
                if texts:
                    print(f"      in-frame text: {texts}")
            for cut in sb.get("platform_cuts", []):
                t = TARGETS.get(cut.get("platform_target"))
                print(f"    export {cut.get('platform_target')} → {cut.get('aspect_ratio')} "
                      f"{cut.get('duration_s')}s (≤{t.max_file_size if t else '?'})")
        print("\nDry run — no render.")
        return 0

    if args.submit:
        print(f"▶ Agent 7 · {path.name} · {len(boards)} concept(s) · SUBMIT (queue → exit)")
        return cmd_submit(args)

    # default: blocking one-shot (submit + poll + assemble)
    print(f"▶ Agent 7 · {path.name} · {len(boards)} concept(s) · "
          f"{'SYNTHETIC' if args.synthetic else f'Veo {args.model}'}")
    ensure_ffmpeg()
    client = None if args.synthetic else veo_client.make_client()
    results = []
    for sb in boards:
        try:
            results.append(produce_one(sb, args.slug, args, client))
        except Exception as e:  # noqa: BLE001
            print(f"  ❌ {sb['brief_id']} failed: {e}", file=sys.stderr)
            results.append({"brief_id": sb["brief_id"], "error": str(e)})
    ok = sum(len(r.get("exports", [])) for r in results)
    print(f"\nDone: {ok} platform videos across {len(results)} concept(s) → outputs/videos/")
    return 0 if ok else 1


def main() -> None:
    load_env()
    ap = argparse.ArgumentParser(description="Agent 7 — Video Producer (Veo 3 + ffmpeg)")
    ap.add_argument("slug", help="funnel slug, e.g. 100plus.boomerangme.com")
    ap.add_argument("--storyboard", default="", help="override path to storyboards_<slug>.json")
    ap.add_argument("--brief", help="comma-separated brief ids (default: all)")
    ap.add_argument("--model", default=veo_client.DEFAULT_MODEL, help="Veo model id")
    ap.add_argument("--resolution", default="1080p", choices=["720p", "1080p"])
    ap.add_argument("--retries", type=int, default=2, help="resubmit clips that hit transient Veo errors")
    ap.add_argument("--master-only", action="store_true", help="build only the 9:16 master (skip platform exports)")
    ap.add_argument("--qa", action="store_true", help="vision-check each clip's title text; re-render until correct")
    ap.add_argument("--qa-retries", type=int, default=3, help="max re-renders per clip to pass text QA")
    ap.add_argument("--synthetic", action="store_true", help="assemble with placeholder clips (no Veo key)")
    ap.add_argument("--submit", action="store_true",
                    help="QUEUE all Veo clips, save operation ids to outputs/videos/_jobs_<slug>.json, and exit")
    ap.add_argument("--collect", action="store_true",
                    help="download ready clips from the jobs file and assemble finished concepts (re-runnable)")
    ap.add_argument("--dry-run", action="store_true", help="print the production plan only")
    args = ap.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
