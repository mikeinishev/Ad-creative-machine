"""
Text/CTA/logo compositor for Agent 5.

AI image models (incl. gpt-image-2) render text unreliably — headlines get
truncated or misspelled. So the reliable path is HYBRID: gpt-image-2 paints the
photographic SCENE only (no text), and this module composites the headline, body
and CTA button with Pillow — pixel-perfect, correctly spelled, inside the Meta
safe zones. Works for any placement size.
"""
from __future__ import annotations

import colorsys
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

RGB = Tuple[int, int, int]

# Candidate bold/regular sans-serif fonts (macOS first, then common Linux).
_BOLD_CANDIDATES = [
    ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
    ("/System/Library/Fonts/Supplemental/Helvetica.ttc", 1),
    ("/System/Library/Fonts/HelveticaNeue.ttc", 0),
    ("/Library/Fonts/Arial Bold.ttf", 0),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0),
]
_REG_CANDIDATES = [
    ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
    ("/System/Library/Fonts/Helvetica.ttc", 0),
    ("/Library/Fonts/Arial.ttf", 0),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
]


def _font(size: int, bold: bool) -> ImageFont.FreeTypeFont:
    for path, idx in (_BOLD_CANDIDATES if bold else _REG_CANDIDATES):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size, index=idx)
            except Exception:
                continue
    return ImageFont.load_default(size=size)


def _to_rgb(c: str, default: RGB = (17, 17, 17)) -> RGB:
    try:
        return ImageColor.getrgb(c)
    except Exception:
        return default


def pick_accent(colors: List[str]) -> RGB:
    """Most saturated, reasonably-bright non-grey color → the CTA button color."""
    best: Optional[RGB] = None
    best_sat = -1.0
    for c in colors or []:
        rgb = _to_rgb(c, (0, 0, 0))
        h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in rgb])
        if s > best_sat and 0.18 < l < 0.85 and s > 0.25:
            best_sat, best = s, rgb
    return best or (13, 177, 75)  # default confident green


def _insets(placement_key: str, w: int, h: int) -> Tuple[int, int, int]:
    """(top_inset, bottom_inset, side_pad) honoring Meta safe zones."""
    if placement_key == "stories_reels":            # 1080x1920 — keep centre 1080x1420
        return int(h * 0.14) + 24, int(h * 0.22) + 24, 72
    if placement_key == "instream_landscape":
        return 56, 64, 96
    if placement_key == "audience_network":
        return 40, 44, 56
    side = max(48, int(w * 0.06))
    return int(h * 0.05), int(h * 0.06), side


def _wrap(draw, text: str, font, max_w: int) -> List[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _fit_headline(draw, text: str, max_w: int, max_h: int, start_px: int, min_px: int):
    """Largest bold font where the wrapped headline fits the allotted band."""
    size = start_px
    while size >= min_px:
        font = _font(size, bold=True)
        lines = _wrap(draw, text, font, max_w)
        lh = int(size * 1.16)
        if len(lines) * lh <= max_h and all(draw.textlength(l, font=font) <= max_w for l in lines):
            return font, lines, lh
        size -= 4
    font = _font(min_px, bold=True)
    return font, _wrap(draw, text, font, max_w), int(min_px * 1.16)


def _gradient(size: Tuple[int, int], top: bool, max_alpha: int, frac: float) -> Image.Image:
    """Vertical alpha scrim (black) for legibility — strong at the edge, fading inward."""
    w, h = size
    band = int(h * frac)
    grad = Image.new("L", (1, band))
    for y in range(band):
        a = int(max_alpha * (1 - y / band)) if top else int(max_alpha * (y / band))
        grad.putpixel((0, y), a)
    grad = grad.resize((w, band))
    full = Image.new("L", (w, h), 0)
    full.paste(grad, (0, 0 if top else h - band))
    black = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    black.putalpha(full)
    return black


def _rounded_button(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def compose(
    scene_png: bytes,
    target: Tuple[int, int],
    placement_key: str,
    headline: str,
    body: str,
    cta: str,
    colors: List[str],
    logo_path: Optional[str] = None,
) -> bytes:
    """Composite headline + body + CTA (+ optional logo) onto the scene. Returns PNG bytes."""
    import io

    w, h = target
    scene = Image.open(io.BytesIO(scene_png)).convert("RGB")
    img = ImageOps.fit(scene, (w, h), Image.Resampling.LANCZOS).convert("RGBA")

    # legibility scrims (top for headline, bottom for CTA)
    img.alpha_composite(_gradient((w, h), top=True, max_alpha=170, frac=0.42))
    img.alpha_composite(_gradient((w, h), top=False, max_alpha=205, frac=0.34))

    draw = ImageDraw.Draw(img)
    top_inset, bottom_inset, side = _insets(placement_key, w, h)
    max_w = w - 2 * side
    white, accent = (255, 255, 255), pick_accent(colors)

    # logo (optional, top-left inside safe zone)
    y = top_inset
    if logo_path and Path(logo_path).exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            lw = int(w * 0.26)
            logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.Resampling.LANCZOS)
            img.alpha_composite(logo, (side, y))
            y += logo.height + 24
        except Exception:
            pass

    # headline
    start_px = int(w / (10.5 if placement_key == "stories_reels" else 12.5))
    band_h = int(h * 0.30)
    font, lines, lh = _fit_headline(draw, headline, max_w, band_h, start_px, int(w / 24))
    for line in lines:
        draw.text((side, y), line, font=font, fill=white,
                  stroke_width=max(1, font.size // 28), stroke_fill=(0, 0, 0, 160))
        y += lh

    # body (optional, smaller)
    if body:
        bfont = _font(max(20, int(w / 30)), bold=False)
        y += int(lh * 0.25)
        for line in _wrap(draw, body, bfont, max_w)[:4]:
            draw.text((side, y), line, font=bfont, fill=(238, 238, 238))
            y += int(bfont.size * 1.3)

    # CTA button (bottom, above bottom safe zone)
    if cta:
        cfont = _font(max(26, int(w / 22)), bold=True)
        tw = draw.textlength(cta, font=cfont)
        pad_x, pad_y = int(w * 0.05), int(w * 0.028)
        bw, bh = int(tw + 2 * pad_x), int(cfont.size + 2 * pad_y)
        bx = (w - bw) // 2
        by = h - bottom_inset - bh
        _rounded_button(draw, (bx, by, bx + bw, by + bh), radius=bh // 2, fill=accent + (255,))
        # contrasting text color
        lum = 0.299 * accent[0] + 0.587 * accent[1] + 0.114 * accent[2]
        tcol = (255, 255, 255) if lum < 150 else (17, 17, 17)
        # vertical centering via textbbox
        tb = draw.textbbox((0, 0), cta, font=cfont)
        draw.text((bx + (bw - tw) / 2, by + (bh - (tb[3] - tb[1])) / 2 - tb[1]),
                  cta, font=cfont, fill=tcol)

    out = io.BytesIO()
    img.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()
