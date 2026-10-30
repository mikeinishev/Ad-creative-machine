#!/usr/bin/env python3
"""PAID route: render clips with the Higgsfield CLI (spends team-workspace credits). Default route is the free web Unlimited.

Use ONLY after Mike explicitly approved credits for these specific clips. The script refuses to submit
unless --approved-credits covers the server-side cost estimate.

  # estimate only (free)
  python3 agents/ugc_director/higgsfield_render.py --out OUT --clip c01=OUT/c01_prompt.txt --clip c02=OUT/c02_prompt.txt \\
      --image casting.png --image product.png --estimate
  # render after approval
  python3 agents/ugc_director/higgsfield_render.py ... --approved-credits 168

Observed 2026-10-29 (seedance_2_5, omni_reference, 9:16, audio, 12 s): 84 credits at 720p, 192 at 1080p;
seedance_2_0 via CLI 54 at 720p. Two clips rendered in parallel in ~5 min. Images are attached in
the given order; name their roles in the prompt ("attached image 1 = the owner ...; image 2 = the product").
Login: `higgsfield auth login`; billing workspace: `higgsfield workspace list|set` (team "Boomerang").
The Higgsfield MCP is not configured in Claude Code; the CLI is the same account and the same credits.
"""
import argparse, json, re, subprocess
from pathlib import Path


def hf(*args, timeout=180):
    cp = subprocess.run(['higgsfield', *args, '--json'], capture_output=True, text=True, timeout=timeout)
    if cp.returncode:
        raise SystemExit(f'higgsfield {args[0]} {args[1]} failed: {cp.stderr[-800:] or cp.stdout[-800:]}')
    return json.loads(cp.stdout)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--clip', action='append', required=True, help='ID=prompt_file')
    p.add_argument('--image', action='append', default=[], help='reference image, repeat in role order')
    p.add_argument('--model', default='seedance_2_5')
    p.add_argument('--duration', type=int, default=12)
    p.add_argument('--resolution', default='720p', choices=['480p', '720p', '1080p'])
    p.add_argument('--aspect', default='9:16')
    p.add_argument('--estimate', action='store_true')
    p.add_argument('--approved-credits', type=float)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    clips = [c.split('=', 1) for c in a.clip]
    common = ['--mode', 'omni_reference' if a.image else 't2v', '--duration', str(a.duration), '--resolution', a.resolution,
              '--aspect_ratio', a.aspect, '--generate_audio', 'true', '--bitrate_mode', 'high']
    for img in a.image:
        common += ['--image', str(Path(img).resolve())]
    ws = subprocess.run(['higgsfield', 'workspace', 'list'], capture_output=True, text=True).stdout
    print('workspace:', next((l for l in ws.splitlines() if '✓' in l), 'unknown').strip())
    costs = {cid: hf('generate', 'cost', a.model, '--prompt', Path(pf).read_text(), *common)['credits'] for cid, pf in clips}
    total = sum(costs.values())
    print('cost:', costs, 'total', total)
    if a.estimate:
        return
    if a.approved_credits is None or total > a.approved_credits:
        raise SystemExit(f'REFUSED: estimate {total} credits exceeds --approved-credits {a.approved_credits}')
    jobs = {}
    for cid, pf in clips:
        res = hf('generate', 'create', a.model, '--prompt', Path(pf).read_text(), *common)
        jobs[cid] = res[0] if isinstance(res, list) else res.get('id')
        (a.out / f'{cid}_job.json').write_text(json.dumps({'job_id': jobs[cid], 'model': a.model, 'credits': costs[cid],
                                                           'images': a.image, 'prompt_file': pf}, indent=2))
        print(cid, 'submitted', jobs[cid])
    for cid, jid in jobs.items():
        done = hf('generate', 'wait', jid, '--timeout', '25m', '--interval', '15s', '--quiet', timeout=1600)
        url = next(iter(re.findall(r'https://[^"\s]+\.mp4', json.dumps(done))), None)
        if not url:
            raise SystemExit(f'{cid}: no result url: {json.dumps(done)[:500]}')
        dst = a.out / f'{cid}.mp4'
        subprocess.run(['curl', '-sS', '-o', str(dst), url], check=True)  # curl: python TLS fails on this Mac
        print(cid, '→', dst)
    print(subprocess.run(['higgsfield', 'account', 'status'], capture_output=True, text=True).stdout.strip())


if __name__ == '__main__':
    main()
