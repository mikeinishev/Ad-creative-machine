#!/usr/bin/env python3
"""Visual + speech inspection of one downloaded take, producing everything the edit needs.

  python3 agents/ugc_director/inspect_take.py OUT/c01.mp4 --lang es

Writes next to the take (prefix = file stem):
  _contact.jpg  one frame per second          → casting continuity, product fidelity, no invented text
  _hook.jpg     first 2 s at 4 fps            → action underway in frame one, payoff by ~1.5 s
  _layout.jpg   one frame per second with guide lines at y=500 (yellow) / 700 (cyan) / 900 (red)
                → where face and product sit, to place captions/CTA per shot (720×1280 coordinates)
  _cuts.json    hard cuts inside the take (scene score > 0.25) → caption layout may change at a cut
  _words.json   word-level timestamps (whisper.cpp) → caption in/out points from ACTUAL speech
  _asr.txt      sentence transcript → compare against the scripted lines
  _inspect.json probe, full-decode result, audio levels, the above paths
Look at the images yourself before accepting the take. ASR agreement is not human listening.
"""
import argparse, json, math, re, subprocess
from pathlib import Path

MODELS = [
    Path.home() / 'Library/Application Support/github.com.thewh1teagle.vibe/ggml-medium.bin',
    Path.home() / '.cache/hyperframes/whisper/models/ggml-small.bin',
]  # the vibe ggml-large-v3-turbo.bin on this Mac is truncated (whisper aborts "not all tensors loaded")


def sh(*cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('video', type=Path)
    p.add_argument('--lang', required=True, help='whisper language code: es, pt, tr, en ...')
    p.add_argument('--model', type=Path)
    a = p.parse_args()
    v = a.video.resolve()
    base = v.with_suffix('')
    report = {'video': str(v)}

    probe = json.loads(sh('ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(v), check=True).stdout)
    dur = float(probe['format']['duration'])
    vs = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    report.update(duration=dur, size=f"{vs['width']}x{vs['height']}",
                  audio_stream=any(s['codec_type'] == 'audio' for s in probe['streams']))
    report['decode_ok'] = sh('ffmpeg', '-v', 'error', '-i', str(v), '-f', 'null', '-').returncode == 0
    lv = sh('ffmpeg', '-hide_banner', '-i', str(v), '-vn', '-af', 'volumedetect', '-f', 'null', '-').stderr
    report['audio_levels'] = {k: float(x) for k, x in re.findall(r'(mean_volume|max_volume):\s*([-\d.]+)', lv)}

    cols = math.ceil(dur / 2)
    sh('ffmpeg', '-v', 'error', '-y', '-i', str(v), '-vf', f'fps=1,scale=240:-1,tile={cols}x2', '-frames:v', '1', f'{base}_contact.jpg')
    sh('ffmpeg', '-v', 'error', '-y', '-t', '2', '-i', str(v), '-vf', 'fps=4,scale=240:-1,tile=8x1', '-frames:v', '1', f'{base}_hook.jpg')
    guides = ','.join(f'drawbox=y={y}:w=iw:h=3:color={c}:t=fill' for y, c in ((500, 'yellow'), (700, 'cyan'), (900, 'red')))
    sh('ffmpeg', '-v', 'error', '-y', '-i', str(v), '-vf', f'fps=1,{guides},scale=240:-1,tile={cols}x2', '-frames:v', '1', f'{base}_layout.jpg')
    cut_log = sh('ffmpeg', '-i', str(v), '-vf', "select='gt(scene,0.25)',showinfo", '-f', 'null', '-').stderr
    cuts = [round(float(t), 3) for t in re.findall(r'pts_time:([0-9.]+)', cut_log)]
    Path(f'{base}_cuts.json').write_text(json.dumps(cuts))
    report['cuts'] = cuts

    if report['audio_stream']:
        model = a.model or next((m for m in MODELS if m.exists()), None)
        if not model:
            raise SystemExit('No whisper model found; pass --model')
        wav = Path(f'{base}_asr.wav')
        sh('ffmpeg', '-v', 'error', '-y', '-i', str(v), '-ar', '16000', '-ac', '1', str(wav), check=True)
        txt = sh('whisper-cli', '-m', str(model), '-l', a.lang, '-np', '-f', str(wav)).stdout
        Path(f'{base}_asr.txt').write_text(txt)
        sh('whisper-cli', '-m', str(model), '-l', a.lang, '-np', '-ml', '1', '-sow', '-oj', '-of', f'{base}_words', '-f', str(wav))
        wj = Path(f'{base}_words.json')
        if wj.exists():
            seg = json.loads(wj.read_text()).get('transcription', [])
            words = [dict(t0=s['offsets']['from'] / 1000, t1=s['offsets']['to'] / 1000, w=s['text'].strip()) for s in seg if s['text'].strip()]
            wj.write_text(json.dumps(words, ensure_ascii=False, indent=1))
        report['transcript'] = ' '.join(l.split(']', 1)[-1].strip() for l in txt.splitlines() if l.strip())
        report['asr_model'] = model.name
    Path(f'{base}_inspect.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report['audio_stream']:
        raise SystemExit('REJECT: no audio stream (speaker switch was off)')


if __name__ == '__main__':
    main()
