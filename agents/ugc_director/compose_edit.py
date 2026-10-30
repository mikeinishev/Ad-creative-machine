#!/usr/bin/env python3
"""Assemble a UGC master: concat clips, burn hook title / captions / CTA as PNG overlays, write SRT.

  .venv/bin/python agents/ugc_director/compose_edit.py OUT/edit.json        # needs Pillow + ffmpeg
  .venv/bin/python agents/ugc_director/compose_edit.py OUT/edit.json --offsets   # print clip start times

edit.json (paths relative to the file):
{
  "clips": ["c01.mp4", "c02.mp4"],
  "out": "220_mx_local_getreviews_9x16.mp4",
  "srt": "subtitles_es-MX.srt",
  "items": [
    {"text": "¿Y la reseña?", "start": 0, "end": 1.8, "role": "title", "y": 420},
    {"text": "El plato, lo salvé.\\nLa reseña se me olvidó.", "start": 0, "end": 4.26, "role": "caption", "y": 930},
    {"text": "Mira si tu restaurante puede\\nparticipar  →", "start": 20.5, "end": 24.128, "role": "cta", "y": 430}
  ]
}
Times are on the concatenated timeline (clip N starts at the sum of previous clip durations;
see --offsets). Caption in/out points come from inspect_take.py _words.json, never from the script.
`y` is the top of the box in 720×1280 coordinates. Choose it per shot from _layout.jpg so the box
covers neither face nor product; at a hard cut where the layout changes, split the caption into
two items with the same text and different y (the SRT merges them back into one cue).
Placement that worked: hook title on the chest under the chin; captions in the band under the
product (≈930) or on the apron (≈520–600) when the product sits low; CTA on the chest above the
product; keep box bottoms above ≈1030 (Reels bottom UI).
"""
import argparse, json, subprocess
from pathlib import Path

FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
FONT_BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
SIZES = {'title': 44, 'caption': 34, 'cta': 32}


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)]))


def overlay_png(path, text, role, size, y, W, H):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT if role == 'caption' else FONT_BOLD, size)
    lines = text.split('\n')
    boxes = [d.textbbox((0, 0), l, font=font) for l in lines]
    tw = max(b[2] - b[0] for b in boxes)
    th = sum(b[3] - b[1] for b in boxes) + 7 * (len(lines) - 1)
    px, py = 18, 13 if role == 'caption' else 12
    x = (W - tw - 2 * px) // 2
    d.rounded_rectangle((x, y, x + tw + 2 * px, y + th + 2 * py), radius=12, fill=(12, 12, 12, 188))
    ty = y + py
    for l, b in zip(lines, boxes):
        d.text((x + px, ty - b[1]), l, font=font, fill=(255, 255, 255, 255))
        ty += b[3] - b[1] + 7
    im.save(path)
    return y + th + 2 * py


def ts(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('spec', type=Path)
    p.add_argument('--offsets', action='store_true')
    a = p.parse_args()
    root = a.spec.resolve().parent
    spec = json.loads(a.spec.read_text())
    clips = [root / c for c in spec['clips']]
    durs = [duration(c) for c in clips]
    total = sum(durs)
    if a.offsets:
        t = 0
        for c, d in zip(clips, durs):
            print(f'{c.name}: start {t:.3f}  duration {d:.3f}')
            t += d
        print(f'total {total:.3f}')
        return
    W, H = spec.get('width', 720), spec.get('height', 1280)
    ov_dir = root / 'overlays'
    ov_dir.mkdir(exist_ok=True)
    items = spec['items']
    n = len(clips)
    args = ['ffmpeg', '-v', 'error', '-y'] + sum((['-i', str(c)] for c in clips), [])
    graph = [''.join(f'[{i}:v]' for i in range(n)) + f'concat=n={n}:v=1:a=0[v0]',
             ''.join(f'[{i}:a]' for i in range(n)) + f'concat=n={n}:v=0:a=1[aout]']
    for i, it in enumerate(items):
        png = ov_dir / f'{i:02d}_{it["role"]}.png'
        bottom = overlay_png(png, it['text'], it['role'], it.get('size', SIZES[it['role']]), it['y'], W, H)
        if bottom > H * 0.81:
            print(f'WARNING: item {i} box bottom {bottom}px is inside the Reels bottom UI zone')
        args += ['-loop', '1', '-t', f'{total:.3f}', '-i', str(png)]
        graph.append(f"[{n + i}:v]format=rgba[o{i}]")
        graph.append(f"[v{i}][o{i}]overlay=0:0:enable='between(t,{it['start']:.3f},{it['end']:.3f})'[v{i + 1}]")
    out = root / spec['out']
    script = root / 'compose.filter'
    script.write_text(';\n'.join(graph))
    args += ['-filter_complex_script', str(script), '-map', f'[v{len(items)}]', '-map', '[aout]',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '24',
             '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', f'{total:.3f}', str(out)]
    subprocess.run(args, check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(out), '-f', 'null', '-'], check=True)

    cues = []
    for it in sorted((i for i in items if i['role'] == 'caption'), key=lambda i: i['start']):
        if cues and cues[-1][2] == it['text'] and abs(cues[-1][1] - it['start']) < 0.05:
            cues[-1][1] = it['end']
        else:
            cues.append([it['start'], it['end'], it['text']])
    if spec.get('srt'):
        (root / spec['srt']).write_text('\n\n'.join(f'{k}\n{ts(s)} --> {ts(e)}\n{t}' for k, (s, e, t) in enumerate(cues, 1)) + '\n')
    times = spec.get('contact_times') or [round(x * total / 10 + total / 20, 2) for x in range(10)]
    sel = '+'.join(f"eq(n\\,{int(t * 24)})" for t in times)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-vf', f"select='{sel}',scale=240:-1,tile={len(times)}x1",
                    '-frames:v', '1', '-vsync', 'vfr', str(out.with_name(out.stem + '_contact.jpg'))], check=True)
    print(json.dumps({'out': str(out), 'duration': round(duration(out), 3), 'items': len(items), 'cues': len(cues),
                      'contact': str(out.with_name(out.stem + '_contact.jpg'))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
