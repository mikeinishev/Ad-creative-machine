#!/usr/bin/env python3
"""Stamp client attribution onto the finished table-tent mockups.

The mockups are already rendered (same framing, same 12-degree angle, white seamless) — this
only composites a header band on top of them, so nothing is re-generated and the product shot
stays byte-identical underneath:

    ORDERED BY                                   [ approved logo ]
    <Venue name>
    (pin) <Street address>

The logo is cropped straight out of the print-ready artwork the client approved, so it is the
exact lockup that went to press.

Usage:
  python agents/designer/label_mockups.py                 # all clients
  python agents/designer/label_mockups.py --only 01,07    # a subset
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = Path("/Users/mikeinishev/Projects/Demo project/output/imagegen/table-tent-mockups")
MOCKUPS = SRC_DIR / "final"
DESIGNS = SRC_DIR / "source"
OUT_DIR = REPO_ROOT / "outputs" / "creatives" / "2026.07.28_boomerang_client_tent_labeled"

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

INK = (17, 17, 17)
MUTED = (122, 122, 122)
ADDR = (100, 100, 100)
PIN = (232, 121, 43)

MARGIN = 62
SS = 4  # supersample factor for the pin glyph

# slug -> (mockup file, venue, address, print design, logo crop box in the 2081x1481 artwork)
CLIENTS = {
    "01": ("01-taj-mockup.png", "Taj Indian Cuisine & Bar",
           "444 S Park St, Madison, WI 53715",
           "01-taj-print.png", (1148, 42, 1828, 168)),
    "02": ("02-bone-burger-mockup.png", "Bronx Burger Co.",
           "610 Exterior St 4th FLOOR, Bronx, NY 10451",
           "02-design.png", (1528, 0, 2081, 258)),
    "03": ("03-johns-barber-mockup.png", "John's Barber Shop — TLH Barbers",
           "3850 Killearn Ct, Tallahassee, FL 32309",
           "03-design.png", (1448, 25, 2020, 368)),
    "06": ("06-philly-mockup.png", "Philly Philly Cheesesteaks",
           "24 S York Rd, Hatboro, PA 19040",
           "06-design.png", (1500, 28, 1900, 296)),
    "07": ("07-jets-pizza-mockup.png", "Jet's Pizza",
           "9853 Tamiami Trl N, Naples, FL 34108",
           "07-design.png", (1636, 0, 2081, 338)),
    "08": ("08-fiesta-mockup.png", "Fiesta Mexicana Grill",
           "836 Florence St NW, Concord, NC 28025",
           "08-design.png", (1518, 0, 2035, 405)),
    "09": ("09-bigfoot-coffee-mockup.png", "Bigfoot Brew Coffee",
           "220 S Main St, Cascade, ID 83611",
           "09-design.png", (1425, 55, 1865, 336)),
}


def tracked(draw: ImageDraw.ImageDraw, xy: Tuple[int, int], text: str,
            font: ImageFont.FreeTypeFont, fill, spacing: float) -> None:
    """Draw text with manual letter-spacing (Pillow has no tracking)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing


def pin_glyph(h: int) -> Image.Image:
    """A classic map pin: teardrop body with a punched-out hole, drawn 4x then downscaled."""
    w = int(h * 0.72)
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    W, H = w * SS, h * SS
    r = W / 2
    d.ellipse([0, 0, W, W], fill=PIN)                       # head
    d.polygon([(r * 0.22, W * 0.72), (r * 1.78, W * 0.72), (r, H)], fill=PIN)  # tail
    hole = r * 0.40
    d.ellipse([r - hole, r - hole, r + hole, r + hole], fill=(0, 0, 0, 0))     # hole
    return img.resize((w, h), Image.LANCZOS)


def fit(draw: ImageDraw.ImageDraw, text: str, max_w: int,
        start: int, floor: int) -> ImageFont.FreeTypeFont:
    """Largest bold size at which `text` still fits `max_w` on one line."""
    for size in range(start, floor - 1, -1):
        f = ImageFont.truetype(BOLD, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
    return ImageFont.truetype(BOLD, floor)


def label(slug: str, spec) -> Path:
    mock, venue, address, design, box = spec
    base = Image.open(MOCKUPS / mock).convert("RGB")
    W, _ = base.size
    draw = ImageDraw.Draw(base)

    # --- approved logo, cropped from the print artwork, as a rounded chip top-right ---
    logo_w = 0
    if design and box:
        lg = Image.open(DESIGNS / design).convert("RGB").crop(box)
        cap_h, cap_w = 116, 300
        scale = min(cap_h / lg.height, cap_w / lg.width)
        lg = lg.resize((int(lg.width * scale), int(lg.height * scale)), Image.LANCZOS)
        mask = Image.new("L", (lg.width * SS, lg.height * SS), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, lg.width * SS - 1, lg.height * SS - 1], radius=14 * SS, fill=255)
        lg.putalpha(mask.resize(lg.size, Image.LANCZOS))
        lx, ly = W - MARGIN - lg.width, 74
        base.paste(lg, (lx, ly), lg)
        logo_w = lg.width + 46

    # --- attribution block, left ---
    text_w = W - MARGIN * 2 - logo_w
    y = 78
    tracked(draw, (MARGIN, y), "ORDERED BY", ImageFont.truetype(BOLD, 18), MUTED, 2.6)

    y += 34
    f_name = fit(draw, venue, text_w, 40, 25)
    draw.text((MARGIN, y), venue, font=f_name, fill=INK)

    y += f_name.size + 18
    pin = pin_glyph(27)
    base.paste(pin, (MARGIN + 1, y + 1), pin)
    draw.text((MARGIN + pin.width + 11, y + 2), address,
              font=ImageFont.truetype(REG, 22), fill=ADDR)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{slug}-{Path(mock).stem.split('-', 1)[1].replace('-mockup', '')}-ordered.png"
    base.save(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated client keys, e.g. 01,07")
    a = ap.parse_args()
    keys = [k.strip() for k in a.only.split(",")] if a.only else list(CLIENTS)
    for k in keys:
        if k not in CLIENTS:
            raise SystemExit(f"unknown client key {k}; valid: {', '.join(CLIENTS)}")
        print("  ", label(k, CLIENTS[k]).relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
