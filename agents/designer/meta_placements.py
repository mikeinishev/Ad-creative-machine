"""
Meta Ads placement specifications — single source of truth for Agent 5 (Designer).

Maps every Meta (Facebook + Instagram) ad placement to:
  - its delivery aspect ratio
  - the EXACT pixel size Meta wants on upload (`target`)
  - the gpt-image-2 generation size (`gen`) — divisible by 16, same aspect ratio,
    chosen slightly ABOVE target so we DOWNSCALE (LANCZOS) for crisp output.

Why a separate `gen` size?
  gpt-image-2 only accepts sizes where width & height are both divisible by 16
  (longest edge <= 3840). Meta's canonical 1080-based sizes are NOT divisible by
  16 (1080 / 16 = 67.5), so we generate at the nearest clean multiple and resize
  down to the exact Meta target.

Spec sources (2026):
  - theoptimizer.io/blog/every-meta-ad-size-you-need-in-2026
  - tryvizup.com/blog/meta-ad-specs-2026-every-dimension-size-you-need
  - Meta Ads Guide (facebook.com/business/ads-guide)
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Placement:
    key: str                 # stable id, e.g. "feed_vertical"
    label: str               # human label, e.g. "Feed (FB/IG)"
    aspect_ratio: str        # "4:5"
    target: Tuple[int, int]  # exact Meta upload size, e.g. (1080, 1350)
    gen: Tuple[int, int]     # gpt-image-2 size (÷16, same ratio, >= target)
    surfaces: Tuple[str, ...]  # where it serves
    safe_zone: str           # text/UI safe-zone guidance


# ---------------------------------------------------------------------------
# Placement catalogue
# ---------------------------------------------------------------------------
PLACEMENTS: Dict[str, Placement] = {
    "feed_vertical": Placement(
        key="feed_vertical",
        label="Feed — 4:5 (recommended)",
        aspect_ratio="4:5",
        target=(1080, 1350),
        gen=(1088, 1360),          # 1088/16=68, 1360/16=85, ratio 0.800 == 4:5
        surfaces=("Facebook Feed", "Instagram Feed", "Explore"),
        safe_zone="No UI overlay. 4:5 takes more mobile screen than 1:1 → higher CTR.",
    ),
    "feed_square": Placement(
        key="feed_square",
        label="Square — 1:1",
        aspect_ratio="1:1",
        target=(1080, 1080),
        gen=(1088, 1088),          # 1088/16=68
        surfaces=(
            "Feed", "Carousel cards", "Marketplace", "Search results",
            "Messenger inbox", "Right column (desktop)",
        ),
        safe_zone="Universal fallback. Carousel cards MUST be 1:1 (Meta crops 4:5 to 1:1).",
    ),
    "stories_reels": Placement(
        key="stories_reels",
        label="Stories / Reels — 9:16",
        aspect_ratio="9:16",
        target=(1080, 1920),
        gen=(1152, 2048),          # 1152/16=72, 2048/16=128, ratio 0.5625 == 9:16
        surfaces=("FB Stories", "IG Stories", "FB Reels", "IG Reels"),
        safe_zone=(
            "Keep headline/logo/CTA inside the centre 1080x1420 area. "
            "Top ~14% (~250px): profile + 'Sponsored'. "
            "Bottom ~20-35% (~340-670px): caption + CTA + engagement icons."
        ),
    ),
    "instream_landscape": Placement(
        key="instream_landscape",
        label="In-Stream / Landscape — 16:9",
        aspect_ratio="16:9",
        target=(1920, 1080),
        gen=(2048, 1152),          # 2048/16=128, 1152/16=72, ratio 1.777 == 16:9
        surfaces=("In-stream video", "Desktop/TV placements"),
        safe_zone="Horizontal format; used for longer/desktop content.",
    ),
    "audience_network": Placement(
        key="audience_network",
        label="Audience Network — 1.91:1",
        aspect_ratio="1.91:1",
        target=(1200, 628),
        gen=(1216, 640),           # 1216/16=76, 640/16=40, ratio 1.90 ≈ 1.91:1
        surfaces=("Audience Network native/banner", "Link ads"),
        safe_zone="Standard banner/native layout; minimal critical content.",
    ),
}


# Aspect-ratio → placement key (lets the generator resolve a brief format that
# only specifies an aspect ratio or a "1080x1080"-style dimension string).
ASPECT_TO_PLACEMENT: Dict[str, str] = {
    "4:5": "feed_vertical",
    "1:1": "feed_square",
    "9:16": "stories_reels",
    "16:9": "instream_landscape",
    "1.91:1": "audience_network",
    "1.9:1": "audience_network",
}

# Common brief dimension strings → placement key (exact + near matches).
DIMENSION_TO_PLACEMENT: Dict[str, str] = {
    "1080x1350": "feed_vertical",
    "1080x1080": "feed_square",
    "1080x1920": "stories_reels",
    "1920x1080": "instream_landscape",
    "1200x628": "audience_network",
}

# Sensible default placement set when a brief doesn't pin specific formats.
DEFAULT_PLACEMENT_KEYS: List[str] = ["feed_vertical", "feed_square", "stories_reels"]


def resolve_placement(
    *, aspect_ratio: str = "", dimensions: str = "", name: str = ""
) -> Placement:
    """Resolve a brief format spec to a Placement.

    Tries, in order: exact dimensions → aspect ratio → name keyword → 1:1 fallback.
    """
    dims = (dimensions or "").lower().replace(" ", "").replace("px", "")
    if dims in DIMENSION_TO_PLACEMENT:
        return PLACEMENTS[DIMENSION_TO_PLACEMENT[dims]]

    ar = (aspect_ratio or "").strip()
    if ar in ASPECT_TO_PLACEMENT:
        return PLACEMENTS[ASPECT_TO_PLACEMENT[ar]]

    n = (name or "").lower()
    if "stor" in n or "reel" in n:
        return PLACEMENTS["stories_reels"]
    if "feed" in n and ("4:5" in n or "vertical" in n):
        return PLACEMENTS["feed_vertical"]
    if "in-stream" in n or "instream" in n or "landscape" in n:
        return PLACEMENTS["instream_landscape"]
    if "audience" in n or "banner" in n:
        return PLACEMENTS["audience_network"]

    return PLACEMENTS["feed_square"]


def gen_size_str(p: Placement) -> str:
    """gpt-image-2 `size` argument, e.g. '1152x2048'."""
    return f"{p.gen[0]}x{p.gen[1]}"


def target_size_str(p: Placement) -> str:
    return f"{p.target[0]}x{p.target[1]}"


if __name__ == "__main__":
    print(f"{'placement':<26}{'ratio':<9}{'meta target':<14}{'gpt-image-2 gen'}")
    print("-" * 70)
    for p in PLACEMENTS.values():
        print(
            f"{p.key:<26}{p.aspect_ratio:<9}"
            f"{target_size_str(p):<14}{gen_size_str(p)}"
        )
