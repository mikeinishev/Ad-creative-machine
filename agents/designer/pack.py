#!/usr/bin/env python3
"""Pack approved creatives into dated pack folders with canonical names.

Naming convention (user's canon, examples: 033_mi_restaurant_owners_revenue20_money_on_table):

  outputs/creatives/<YYYY.MM.DD>_<brand>_<pack_slug>/
      <seq3>_mi_<audience>_<offer>_<accent>[_<variant>]_<ratio>.png

  - seq3     : GLOBAL zero-padded creative number (001…), persisted in outputs/creatives/.seq
               (one seq per concept+variant; all ratios of the same creative share it)
  - mi       : author mark — Mike Inishev (distinguishes our creatives from colleagues')
  - audience : who the ad calls out: restaurant_owners, restaurant_gms, …
  - offer    : the offer being sold: customers100 (100 customers/radius), revenue20 (+20%), …
  - accent   : what the creative shows / its emphasis: money_on_table, lift_chart,
               toast_kitchen_pass, aero_city, …
  - variant  : a/b/c — only when the source has multiple hook variants
  - ratio    : 4x5 | 1x1 | 9x16  (from feed_vertical / feed_square / stories_reels)

  status (ok|draft) is NOT in the filename — it lives in the pack's _pack.json.

Usage:
  pack.py --pack 2026.06.10_richie_pos --brief toast_aero_night \
          --audience restaurant_owners --offer customers100 --accent toast_aero_radius [--copy]

Moves (default) or copies all PNGs from outputs/creatives/<brief_id>/ into the pack.
metadata.json from the source dir is merged into the pack's _pack.json index.
"""
import argparse, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CRE = ROOT / "outputs" / "creatives"
SEQ_FILE = CRE / ".seq"

RATIO = {"feed_vertical": "4x5", "feed_square": "1x1", "stories_reels": "9x16",
         "feed_horizontal": "16x9", "right_column": "1x1rc"}


def next_seq() -> int:
    """Monotonic, never-reused. Take max(.seq counter, highest seq already on disk) + 1 so a
    lost/reset .seq can never recycle an existing creative number. Numbers only ever go up."""
    counter = int(SEQ_FILE.read_text().strip()) if SEQ_FILE.exists() else 0
    on_disk = 0  # only OUR creatives (mi author mark) — colleagues' packs have their own numbering
    for p in CRE.glob("*/*.png"):
        m = re.match(r"(\d+)_mi_", p.name)
        if m:
            on_disk = max(on_disk, int(m.group(1)))
    return max(counter, on_disk) + 1


def save_seq(n: int):
    SEQ_FILE.write_text(str(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True, help="pack folder name: YYYY.MM.DD_<brand>_<slug>")
    ap.add_argument("--brief", required=True, help="source brief_id dir under outputs/creatives/")
    ap.add_argument("--audience", required=True)
    ap.add_argument("--offer", required=True)
    ap.add_argument("--accent", required=True)
    ap.add_argument("--author", default="mi")
    ap.add_argument("--status", default="ok", choices=["ok", "draft"],
                    help="recorded in _pack.json only (not in the filename)")
    ap.add_argument("--copy", action="store_true", help="copy instead of move")
    a = ap.parse_args()

    src = CRE / a.brief
    if not src.is_dir():
        raise SystemExit(f"no such source dir: {src}")
    dst = CRE / a.pack
    dst.mkdir(exist_ok=True)

    pngs = sorted(src.glob("*.png"))
    if not pngs:
        raise SystemExit(f"no PNGs in {src}")

    # group by variant letter so each creative (concept+variant) gets ONE seq across ratios
    groups = {}
    for p in pngs:
        m = re.match(r"(feed_vertical|feed_square|stories_reels|feed_horizontal|right_column)_([A-C])\.png", p.name)
        if not m:
            print(f"  ?? skipping unrecognized name: {p.name}")
            continue
        groups.setdefault(m.group(2), []).append((m.group(1), p))

    multi = len(groups) > 1
    index_entries = []
    seq = next_seq() - 1
    for variant in sorted(groups):
        seq += 1
        for placement, p in sorted(groups[variant]):
            vpart = f"_{variant.lower()}" if multi else ""
            new = f"{seq:03d}_{a.author}_{a.audience}_{a.offer}_{a.accent}{vpart}_{RATIO[placement]}.png"
            (shutil.copy2 if a.copy else shutil.move)(str(p), str(dst / new))
            index_entries.append({"file": new, "seq": seq, "variant": variant,
                                  "placement": placement, "source": f"{a.brief}/{p.name}"})
            print(f"  {p.name} -> {a.pack}/{new}")
    save_seq(seq)

    # merge source metadata + entries into the pack index
    idx_path = dst / "_pack.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else {"pack": a.pack, "items": []}
    meta_src = src / "metadata.json"
    entry = {"brief_id": a.brief, "audience": a.audience, "offer": a.offer,
             "accent": a.accent, "status": a.status, "files": index_entries}
    if meta_src.exists():
        try:
            entry["source_metadata"] = json.loads(meta_src.read_text())
        except Exception:
            pass
    idx["items"].append(entry)
    idx_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False))

    # clean up the source dir if everything moved
    if not a.copy:
        leftovers = [p for p in src.iterdir() if p.name not in ("metadata.json", ".DS_Store")]
        if not leftovers:
            (src / "metadata.json").unlink(missing_ok=True)
            (src / ".DS_Store").unlink(missing_ok=True)
            src.rmdir()
            print(f"  removed empty source dir {a.brief}/")


if __name__ == "__main__":
    main()
