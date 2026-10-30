#!/usr/bin/env python3
"""Casting stills and storyboard frames through the local ChatGPT subscription (codex exec + built-in image tool).

No OpenAI API key, no API billing: every image is one `codex exec` run that calls Codex's
built-in image tool; the PNG is picked up from ~/.codex/generated_images/<thread_id>/.

  # storyboard: one frame per scene of every creative in an authored pack
  python3 agents/ugc_director/image_frames.py --from-scripts PACK/scripts.json --kind storyboard --out PACK/storyboard
  # casting: one portrait per creative that has casting_prompt (local look-alike, no actor reference)
  python3 agents/ugc_director/image_frames.py --from-scripts PACK/scripts.json --kind casting --out PACK/casting
  # arbitrary jobs: [{"out": "x.png", "refs": ["a.png"], "prompt": "..."}]
  python3 agents/ugc_director/image_frames.py --jobs jobs.json

Existing files are skipped, so an interrupted run is resumed by running the same command again.
Long runs get killed when backgrounded by some harnesses: run in the foreground with
`timeout 580 python3 ...` in a loop until every job reports exists/ok.
"""
import argparse, concurrent.futures as cf, json, shutil, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
IMAGES = Path.home() / '.codex' / 'generated_images'
STYLE = ('Ordinary phone photo, available light, natural skin texture, ordinary deep focus. No beauty filter, '
         'no cinematic grade, no artificial bokeh, no added text, captions, labels or logos that are not on the product. '
         'Highest quality and detail.')


def frame_name(creative, scene_id):
    return f"{creative['source_id']}_{scene_id}.png"


def casting_and_venue(c):
    """casting_prompt/venue_prompt fields, else the CASTING/VENUE lines of the first clip prompt."""
    if c.get('casting_prompt'):
        return c['casting_prompt'], c.get('venue_prompt', '')
    lines = c['clips'][0]['prompt'].splitlines()
    casting = next((l for l in lines if l.startswith('CASTING')), '')
    venue = next((l for l in lines if l.startswith('VENUE')), '')
    if 'EXACT SAME' in casting.upper():
        return '', venue
    return casting, venue


def jobs_from_scripts(pack_path, kind, out_dir, scenes_filter):
    pack = json.loads(Path(pack_path).read_text())
    jobs = []
    for c in pack['creatives']:
        refs = [str(Path(r)) for r in c.get('frame_references') or c['clips'][0]['references']]
        product = c.get('references', {}).get('product')
        casting_still = c.get('references', {}).get('casting')
        if casting_still and casting_still not in refs:
            refs = [casting_still] + refs  # person first, product last
        if kind == 'casting':
            casting, venue = casting_and_venue(c)
            if not casting:
                continue  # same-actor creatives use the winner's frames, no new casting still
            jobs.append(dict(out=str(out_dir / f"{c['source_id']}_casting.png"), refs=[product] if product else [],
                             prompt=('A vertical 9:16 casting still for a UGC ad. The reference is the exact product: '
                                     'reproduce it faithfully, upright in its acrylic holder on the counter in front of the person. '
                                     'Do not copy any other face. Hands rest on the counter behind the product, sly half-smile at the camera. '
                                     f'{casting} {venue}')))
            continue
        for s in c['scenes']:
            if scenes_filter and s['id'] not in scenes_filter:
                continue
            roles = c.get('reference_roles') or ('The first reference(s) show the on-camera person: keep exactly this person '
                                                 '(face, build, hair, facial hair, clothes). The LAST reference is the exact product: '
                                                 'whenever it is in frame reproduce it faithfully.')
            jobs.append(dict(out=str(out_dir / frame_name(c, s['id'])), refs=refs,
                             prompt=(f"ONE vertical 9:16 storyboard frame for a UGC video ad. {roles}\n"
                                     f"Scene {s['id']} ({s['start']}–{s['end']} s). {s.get('frame_prompt') or s['visual']}")))
    return jobs


def run(job, retries, timeout):
    out = Path(job['out'])
    if out.exists():
        return out.name, 'exists'
    out.parent.mkdir(parents=True, exist_ok=True)
    logs = out.parent / '_logs'
    logs.mkdir(exist_ok=True)
    refs = [str(Path(r).resolve()) for r in job.get('refs', [])]
    prompt = (f"Create the image with the built-in image tool using referenced_image_paths = {json.dumps(refs)}.\n"
              f"{job['prompt']}\n{STYLE}\nDo not write files or use any API. When the image is generated, reply DONE.")
    cmd = ['codex', 'exec', '-m', 'gpt-6-astra', '-c', 'model_reasoning_effort="xhigh"', '-s', 'read-only',
           '--skip-git-repo-check', '--json', prompt]
    for attempt in range(1, retries + 1):
        try:
            cp = subprocess.run(cmd, cwd=REPO, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            continue
        (logs / f'{out.stem}_{attempt}.log').write_text(cp.stdout[-20000:] + '\n---\n' + cp.stderr[-5000:])
        tid = next((json.loads(l).get('thread_id') for l in cp.stdout.splitlines() if '"thread.started"' in l), None)
        pngs = sorted((IMAGES / str(tid)).glob('*.png'), key=lambda f: f.stat().st_mtime) if tid else []
        if pngs:
            shutil.copyfile(pngs[-1], out)
            return out.name, 'ok'
    return out.name, 'FAILED'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument('--from-scripts', type=Path)
    src.add_argument('--jobs', type=Path)
    p.add_argument('--kind', choices=['storyboard', 'casting'], default='storyboard')
    p.add_argument('--out', type=Path, help='output directory for --from-scripts')
    p.add_argument('--scenes', nargs='*', help='only these scene ids, e.g. s01 s06 (key frames)')
    p.add_argument('--concurrency', type=int, default=4)
    p.add_argument('--retries', type=int, default=2)
    p.add_argument('--timeout', type=int, default=1500)
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    if a.from_scripts:
        if not a.out:
            p.error('--out is required with --from-scripts')
        jobs = jobs_from_scripts(a.from_scripts, a.kind, a.out, set(a.scenes or []))
    else:
        jobs = json.loads(a.jobs.read_text())
    print(len(jobs), 'images', flush=True)
    if a.dry_run:
        for j in jobs:
            print(j['out'], '<-', [Path(r).name for r in j.get('refs', [])])
        return
    with cf.ThreadPoolExecutor(a.concurrency) as ex:
        for name, status in ex.map(lambda j: run(j, a.retries, a.timeout), jobs):
            print(name, status, flush=True)


if __name__ == '__main__':
    main()
