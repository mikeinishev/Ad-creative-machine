#!/usr/bin/env python3
"""Pack approved creatives into dated pack folders with canonical names.

Naming convention (mirrors the colleague's reference pack 2026.06.06_richie_100plus):

  outputs/creatives/<YYYY.MM.DD>_<brand>_<pack_slug>/
      <seq>_<status>_<brand>_<audience>_<concept>[_<variant>]_<ratio>.png

  - seq      : GLOBAL incrementing creative number, persisted in outputs/creatives/.seq
               (one seq per concept+variant; all ratios of the same creative share it)
  - status   : ok (approved/final) | draft (concept, not approved)
  - brand    : product brand, e.g. richie
  - audience : who the ad calls out, e.g. restaurant_owner, toast_owner, square_owner
  - concept  : short concept slug, e.g. radius_superreal_aero, big_offer_contract
  - variant  : a/b/c — only when the source has multiple hook variants
  - ratio    : 4x5 | 1x1 | 9x16  (from feed_vertical / feed_square / stories_reels)

Usage:
  pack.py --pack 2026.06.10_richie_pos --brief toast_aero_night \
          --audience toast_owner --concept aero_night_radius [--status ok] [--copy]

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
    n = int(SEQ_FILE.read_text().strip()) if SEQ_FILE.exists() else 200
    return n + 1


def save_seq(n: int):
    SEQ_FILE.write_text(str(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True, help="pack folder name: YYYY.MM.DD_<brand>_<slug>")
    ap.add_argument("--brief", required=True, help="source brief_id dir under outputs/creatives/")
    ap.add_argument("--audience", required=True)
    ap.add_argument("--concept", required=True)
    ap.add_argument("--brand", default="richie")
    ap.add_argument("--status", default="ok", choices=["ok", "draft"])
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
            new = f"{seq}_{a.status}_{a.brand}_{a.audience}_{a.concept}{vpart}_{RATIO[placement]}.png"
            (shutil.copy2 if a.copy else shutil.move)(str(p), str(dst / new))
            index_entries.append({"file": new, "seq": seq, "variant": variant,
                                  "placement": placement, "source": f"{a.brief}/{p.name}"})
            print(f"  {p.name} -> {a.pack}/{new}")
    save_seq(seq)

    # merge source metadata + entries into the pack index
    idx_path = dst / "_pack.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else {"pack": a.pack, "items": []}
    meta_src = src / "metadata.json"
    entry = {"brief_id": a.brief, "audience": a.audience, "concept": a.concept,
             "status": a.status, "files": index_entries}
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
