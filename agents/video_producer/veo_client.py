"""
Veo 3 client for Agent 7 — submit → poll → download (google-genai).

Mirrors Agent 5's background pattern: `generate_videos` returns a long-running
operation immediately (no held connection), so we submit ALL clips up front, let
them render server-side in parallel, poll the operations, then download the mp4s.

Veo 3 facts (Gemini API):
  - models: 'veo-3.0-generate-001' (quality), 'veo-3.0-fast-generate-001' (fast)
  - aspect_ratio: '16:9' | '9:16'   · resolution: '720p' | '1080p'
  - duration_seconds: '4' | '6' | '8'  (1080p / reference-images / extension require '8')
  - native audio (always on, 48kHz) · 24fps · clips stored ~2 days
  - person_generation: 'allow_all' (text→video) | 'allow_adult' (image→video)
Needs GOOGLE_API_KEY (or GEMINI_API_KEY) in the environment / .env.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_MODEL = "veo-3.0-generate-001"


def make_client():
    from google import genai

    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GOOGLE_API_KEY (or GEMINI_API_KEY) not set — required for Veo 3 rendering. "
            "Add it to .env. (Dry-run works without a key.)"
        )
    return genai.Client(api_key=key)


def submit_clip(
    client,
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = "9:16",
    resolution: str = "1080p",
    duration_seconds: str = "8",
    negative_prompt: str = ("misspelled words, distorted text, warped letters, gibberish text, "
                            "duplicated text, extra text, background signage, posters with text, "
                            "menus, captions, subtitles, small unreadable text, letters mid-animation, "
                            "unreadable typography, blurry, low quality, watermark"),
    reference_images: Optional[List[str]] = None,
):
    """Queue one Veo 3 render; returns the long-running operation (fast)."""
    from google.genai import types

    cfg: Dict[str, Any] = {
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "duration_seconds": str(duration_seconds),
        "negative_prompt": negative_prompt,
    }
    kwargs: Dict[str, Any] = {"model": model, "prompt": prompt}
    # optional image-to-video / reference frame (consistency); else text-to-video
    if reference_images:
        first = Path(reference_images[0])
        if first.exists():
            kwargs["image"] = types.Image.from_file(location=str(first))
            cfg["person_generation"] = "allow_adult"
        else:
            cfg["person_generation"] = "allow_all"
    else:
        cfg["person_generation"] = "allow_all"
    kwargs["config"] = types.GenerateVideosConfig(**cfg)
    return client.models.generate_videos(**kwargs)


def op_name(op) -> str:
    """The persistable operation id (e.g. 'models/veo-3.0-generate-001/operations/abc')."""
    return op.name


def check(client, name: str):
    """Refresh an operation by its saved NAME (survives process restarts).
    Returns ('pending', None) | ('error', msg) | ('done', op)."""
    from google.genai import types

    op = client.operations.get(types.GenerateVideosOperation(name=name))
    if not getattr(op, "done", False):
        return ("pending", None)
    if getattr(op, "error", None):
        return ("error", str(op.error))
    return ("done", op)


def download(client, op, out_path: Path) -> Path:
    """Download the finished video of a done operation to out_path."""
    gv = op.response.generated_videos[0]
    client.files.download(file=gv.video)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gv.video.save(str(out_path))
    return out_path


def poll_and_download(
    client, ops: Dict[Any, Any], out_paths: Dict[Any, Path],
    timeout: int = 1800, poll: int = 12,
) -> Dict[Any, Any]:
    """Poll all operations until done, download each clip. Returns {key: Path | Exception}."""
    pending = dict(ops)
    out: Dict[Any, Any] = {}
    deadline = time.time() + timeout
    while pending and time.time() < deadline:
        time.sleep(poll)
        for key, op in list(pending.items()):
            try:
                op = client.operations.get(op)
            except Exception:  # transient — retry next round
                continue
            pending[key] = op
            if not getattr(op, "done", False):
                continue
            try:
                if getattr(op, "error", None):
                    raise RuntimeError(str(op.error))
                gv = op.response.generated_videos[0]
                client.files.download(file=gv.video)
                out_paths[key].parent.mkdir(parents=True, exist_ok=True)
                gv.video.save(str(out_paths[key]))
                out[key] = out_paths[key]
            except Exception as e:  # noqa: BLE001
                out[key] = e
            del pending[key]
        print(f"   …{len(out)}/{len(ops)} clips ready", end="\r")
    for key in pending:
        out[key] = RuntimeError("timeout")
    print(f"   {len(out)}/{len(ops)} clips done")
    return out
