"""
Video-ad platform specs + Veo 3 constraints — single source of truth for Agent 6.

Derived from the verified research playbook (shared/video_ad_playbook.json):
exact 2026 specs for Meta (Reels/Stories/Feed/In-stream), YouTube (Shorts/VAC),
TikTok (In-Feed/Spark), plus Google Veo 3 generation constraints. Storyboards must
respect these so the rendered clips fit each platform and shoot cleanly on Veo 3.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Cross-platform safe zone (keep faces / text / CTA inside this central box)
# ---------------------------------------------------------------------------
SAFE_ZONE = {
    "canvas": "1080x1920 (9:16)",
    "central_box": "≈900x1400 centred (≈ inset top 14%, bottom ~20-35%, sides ~6%)",
    "rule": "All faces, burned-in text, logos and CTA must sit inside the central box, "
            "clear of the bottom 35% (caption/CTA/handle UI) and the right-rail icons.",
}


# ---------------------------------------------------------------------------
# Veo 3 (Google) — the renderer used in the next series. Storyboards target it.
# ---------------------------------------------------------------------------
VEO3 = {
    "model": "Google Veo 3 (Gemini)",
    "max_clip_s": 8,                       # selectable 4/6/8; 8s unlocks 1080p/4K + extension
    "fps": 24,
    "resolutions": ["720p (default)", "1080p (needs 8s clip)", "4K (needs 8s clip, since Jan 2026)"],
    "aspect_ratios": ["9:16 (vertical)", "16:9 (landscape)"],  # no native 1:1 → centre-crop a master
    "audio": "Native single-pass audio (48kHz stereo): synced DIALOGUE (lip-sync), SFX, ambient bed, "
             "music — all prompt-driven, PER CLIP. Dialogue in quotes, label 'SFX:', describe ambience, "
             "request a music cue.",
    "rules": [
        "Every ad is built on an 8-SECOND beat grid: 15s ≈ 2 clips (8s+~7s), 30s ≈ 4 clips of ~8s.",
        "Each shot's Veo prompt is SELF-CONTAINED — the model has no memory of prior shots; restate "
        "character, setting, style, lighting, and audio every time.",
        "Lock character/product/scene with up to 3 reference images ('Ingredients to Video') reused "
        "across all shots for consistency.",
        "NEVER ask Veo to render brand text/headline/subhead/CTA/logos — text rendering is unreliable. "
        "All typography is a POST overlay (Agent 5's layer).",
        "Continue action across cuts with Scene Extension (drops to 720p) or first/last-frame "
        "interpolation; carry a voice across a cut only if it's present in the final ~1s of the prior clip.",
        "Render the 9:16 master at 1080p/4K; centre-crop for 1:1/4:5 (Meta feed) or 16:9 (YouTube "
        "in-stream) keeping subjects within crop-safe margins.",
    ],
}


# ---------------------------------------------------------------------------
# Delivery targets (what Agent 6 storyboards aim to satisfy)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class VideoTarget:
    key: str
    platform: str
    placement: str
    aspect_ratio: str
    resolution: str           # recommended upload resolution
    ideal_duration: str       # best-converting window
    max_duration_s: int       # practical surface cap
    max_file_size: str
    container: str
    video_codec: str
    fps: str
    is_master: bool           # 9:16 master vs a crop-derived derivative
    notes: str


TARGETS: Dict[str, VideoTarget] = {
    # --- 9:16 vertical masters (the primary deliverables) ---
    "tiktok_infeed": VideoTarget(
        "tiktok_infeed", "TikTok", "In-Feed / Spark", "9:16", "1080x1920",
        "9–15s (in-feed conversion); 24–38s completion lane", 600, "≤ 500 MB", "MP4/MOV",
        "H.264 (de-facto)", "30 (de-facto)", True,
        "Most retention-demanding. Cut every 2–3s, native/UGC look, trending audio swapped in post, "
        "engineer a seamless loop (rewatch is king). Official min 540x960; bitrate ≥516kbps.",
    ),
    "youtube_shorts": VideoTarget(
        "youtube_shorts", "YouTube", "Shorts ad", "9:16", "1080x1920",
        "10–30s (action ads); <60s", 180, "≤ 256 GB (≈250 MB advisory)", "MP4 (Fast Start)",
        "H.264 High (HEVC accepted)", "24/25/30/48/50/60", True,
        "Only the first 60s plays in the Shorts feed. Rewards completion to the LAST frame + staying "
        "in feed → end on a satisfying/looping final frame. CTA chip auto-appears ~3s in.",
    ),
    "meta_reels": VideoTarget(
        "meta_reels", "Meta (FB+IG)", "Reels", "9:16", "1080x1920 (1440x2560 rec)",
        "15–30s (conversion); 7–15s reach lane", 90, "≤ 4 GB", "MP4/MOV",
        "H.264", "30 (convention)", True,
        "Hook in first ~1.5s. Cut every 3–5s. Reels weights standalone retention LEAST — add a "
        "save-worthy payoff + 'save this' prompt (saves/DM-sends per reach matter most).",
    ),
    "meta_stories": VideoTarget(
        "meta_stories", "Meta (FB+IG)", "Stories", "9:16", "1080x1920 (1440x2560 rec)",
        "6–15s per card", 120, "≤ 4 GB", "MP4/MOV", "H.264", "30 (convention)", True,
        "Ads 15s+ may split into separate Story cards — design within one short card.",
    ),
    # --- derivatives (centre-crop the 9:16 master) ---
    "meta_feed": VideoTarget(
        "meta_feed", "Meta (FB+IG)", "Feed (4:5)", "4:5", "1080x1350 (1440x1800 rec)",
        "15–30s (hook in first ~3s)", 3600, "≤ 4 GB", "MP4/MOV", "H.264", "30 (convention)", False,
        "Derivative: centre-crop the 9:16 master to 4:5 (or 1:1 fallback 1080x1080).",
    ),
    "youtube_instream": VideoTarget(
        "youtube_instream", "YouTube", "Skippable in-stream / VAC", "16:9", "1920x1080",
        "15–30s (≥10s to serve; brand in first ~5s)", 180, "≤ 256 GB", "MP4 (H.264)",
        "H.264 High (HEVC accepted)", "24/25/30/48/50/60", False,
        "Derivative/companion: render a 16:9 master from Veo (16:9 is native) or crop. Sound ON by "
        "default; skippable after 5s → front-load brand.",
    ),
    "meta_instream": VideoTarget(
        "meta_instream", "Meta (FB+IG)", "In-stream", "16:9", "1920x1080 (min 1080x1080)",
        "5–15s (message in first ~3s)", 600, "≤ 4 GB", "MP4/MOV", "H.264", "30 (convention)", False,
        "Derivative: 16:9 or 1:1. Sound ON by default.",
    ),
}

# Default set of platforms Agent 6 storyboards target (the vertical masters).
DEFAULT_TARGET_KEYS: List[str] = ["tiktok_infeed", "youtube_shorts", "meta_reels"]


def master_targets() -> List[VideoTarget]:
    return [t for t in TARGETS.values() if t.is_master]


def derivative_targets() -> List[VideoTarget]:
    return [t for t in TARGETS.values() if not t.is_master]


def ideal_master_duration() -> Tuple[int, int]:
    """A 15–30s vertical master serves TikTok/Shorts/Reels; trim to each platform's lane."""
    return (15, 30)


if __name__ == "__main__":
    print(f"Veo 3: max {VEO3['max_clip_s']}s/clip @ {VEO3['fps']}fps · {', '.join(VEO3['aspect_ratios'])}\n")
    print(f"{'target':<18}{'aspect':<7}{'resolution':<22}{'ideal':<34}{'max file'}")
    print("-" * 95)
    for t in TARGETS.values():
        tag = "" if t.is_master else "  (derivative)"
        print(f"{t.key:<18}{t.aspect_ratio:<7}{t.resolution:<22}{t.ideal_duration:<34}{t.max_file_size}{tag}")
