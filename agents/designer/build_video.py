#!/usr/bin/env python3
"""Assemble a short vertical ad video from still frames rendered by Agent 5.

Variant-A motion build: gpt-image-2 produces perfectly-spelled still beats, ffmpeg adds the
movement (slow push-in per beat + crossfades). This exists because Veo 3 cannot render exact
burned-in text reliably (documented project ceiling), while stills can.

The beat list and timing come from the brief's `meta.assembly` block, so the video follows the
same source of truth as the frames.

Usage:
  python agents/designer/build_video.py --briefs outputs/briefs/<frames>.json \
      --out outputs/videos/097_mi_reviews_mech3_video_9x16.mp4
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CREATIVES_DIR = REPO_ROOT / "outputs" / "creatives"

FPS = 30
XFADE = 0.25   # seconds of crossfade between beats
ZOOM = 0.04    # total push-in over a beat (4%)


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{' '.join(cmd)}\n\n{proc.stderr[-2000:]}")


def beat_clip(src: Path, dst: Path, dur: float, w: int, h: int) -> None:
    """One still → a clip with a slow, centred push-in."""
    frames = max(1, int(round(dur * FPS)))
    # Render the zoom on a 2x supersampled frame so the push-in stays smooth, then scale back.
    vf = (
        f"scale={w*2}:{h*2},"
        f"zoompan=z='1+{ZOOM}*on/{frames}':d={frames}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={FPS},"
        f"format=yuv420p"
    )
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(src), "-vf", vf,
         "-t", f"{dur}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", str(dst)])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--briefs", required=True, help="frames brief JSON (needs meta.assembly)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--placement", default="stories_reels")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    a = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ERROR: ffmpeg not on PATH (brew install ffmpeg).")

    data = json.loads(Path(a.briefs).read_text())
    assembly = (data.get("meta") or {}).get("assembly")
    if not assembly:
        sys.exit("ERROR: brief has no meta.assembly block.")
    beats = assembly["beats"]

    srcs: list[tuple[Path, float]] = []
    for b in beats:
        p = CREATIVES_DIR / b["frame"] / f"{a.placement}_A.png"
        if not p.exists():
            sys.exit(f"ERROR: missing frame {p} — render the frames first.")
        srcs.append((p, float(b["out"]) - float(b["in"])))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        clips = []
        for i, (src, dur) in enumerate(srcs):
            # Pad each beat by the crossfade so the visible time per beat stays as briefed.
            c = tmp / f"beat{i}.mp4"
            beat_clip(src, c, dur + (XFADE if i < len(srcs) - 1 else 0), a.width, a.height)
            clips.append((c, dur))
            print(f"  beat {i+1}/{len(srcs)}: {src.parent.name} · {dur}s")

        # Chain crossfades: each xfade starts XFADE before the running length ends.
        inputs, filters, prev, offset = [], [], "0:v", 0.0
        for i, (c, dur) in enumerate(clips):
            inputs += ["-i", str(c)]
        for i in range(1, len(clips)):
            offset += clips[i - 1][1]
            label = f"x{i}"
            filters.append(
                f"[{prev}][{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}[{label}]"
            )
            prev = label
        fc = ";".join(filters) if filters else None

        cmd = ["ffmpeg", "-y", *inputs]
        if fc:
            cmd += ["-filter_complex", fc, "-map", f"[{prev}]"]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-r", str(FPS), str(out)]
        run(cmd)

    total = sum(d for _, d in clips)
    try:
        shown = out.resolve().relative_to(REPO_ROOT)
    except ValueError:
        shown = out
    print(f"\n✔ {shown} · {total:.1f}s · {a.width}x{a.height} · silent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
