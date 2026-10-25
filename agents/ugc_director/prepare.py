#!/usr/bin/env python3
"""Build a session-model brief or validate/render its authored UGC storyboard."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def validate(pack, *, legacy=False):
    errors = []
    ids = set()
    forbidden = re.compile(r'\b(?:five|5)\s+restaurants?\b|\b(?:cinco|5)\s+restaurantes?\b|\b(?:beş|5)\s+restoran\w*|\b(?:пять|5)\s+ресторан\w*', re.I)
    for ad in pack['creatives']:
        aid = ad['source_id']
        if aid in ids:
            errors.append(f'{aid}: duplicate ID')
        ids.add(aid)
        if len(ad['hooks']) != 3:
            errors.append(f'{aid}: expected three hooks')
        if not legacy:
            errors.extend(validate_contract(ad))
        end = 0
        for scene in ad['scenes']:
            if scene['start'] != end or scene['end'] <= scene['start']:
                errors.append(f'{aid}/{scene["id"]}: invalid timeline')
            end = scene['end']
            words = len(scene['dialogue'].split())
            if words / (scene['end'] - scene['start']) > 3:
                errors.append(f'{aid}/{scene["id"]}: rushed speech')
            for key in ('visual', 'prompt', 'dialogue', 'purpose_ru', 'frame_prompt'):
                if not scene.get(key):
                    errors.append(f'{aid}/{scene["id"]}: missing {key}')
            if forbidden.search(scene['dialogue']):
                errors.append(f'{aid}: recruitment quantity must be one')
        if end != ad['duration']:
            errors.append(f'{aid}: duration mismatch')
        if sum(c['duration'] for c in ad['clips']) != end:
            errors.append(f'{aid}: clip duration mismatch')
        for clip in ad['clips']:
            if not 1 <= clip['duration'] <= 15:
                errors.append(f'{aid}: Seedance 2.0 clip exceeds limit')
        if not ad.get('disclosure') or not ad.get('claim_ledger'):
            errors.append(f'{aid}: missing disclosure/evidence ledger')
    return errors


def validate_contract(ad):
    """Check objective planning commitments; never certify perceived quality."""
    aid = ad['source_id']
    c = ad.get('production_contract')
    if not isinstance(c, dict):
        return [f'{aid}: missing production_contract (see UGC_PRODUCTION_LEARNINGS.md)']
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(f'{aid}: {message}')
    h = c.get('hook', {})
    chosen = next((x for x in ad.get('hooks', []) if x.get('variant') == h.get('variant')), None)
    require(chosen is not None, 'select an existing hook variant')
    require(h.get('starts_at') == 0, 'visual hook must start in frame one')
    payoff = h.get('payoff_by')
    require(isinstance(payoff, (int, float)) and not isinstance(payoff, bool) and 0 < payoff <= 2,
            'visual hook payoff must occur within 2 seconds')
    for key in ('mechanism', 'bridge', 'evidence'):
        require(bool(h.get(key)), f'hook missing {key}')
    if chosen:
        require(bool(chosen.get('visual')) and bool(chosen.get('bridge')), 'selected hook needs action and bridge')
    v = c.get('voice', {})
    for key in ('speaker_id', 'actor_voice', 'reference_kind', 'reference', 'acceptance'):
        require(bool(v.get(key)), f'voice missing {key}')
    require(v.get('dialogue_mode') == 'on_camera_lip_sync', 'talking owner requires visible lip sync')
    require(v.get('reference_kind') in ('native_probe', 'approved_native'), 'use native voice test or accepted native reference; no synthetic guide')
    if v.get('reference_kind') == 'approved_native':
        require(v.get('reference_voice') == v.get('actor_voice'), 'voice reference must match actor voice')
        require(v.get('acceptance') in ('user_accepted', 'listening_accepted'), 'native reference needs listening acceptance')
    require(c.get('music') is False, 'music must be off')
    require(c.get('on_screen_demo_label') is False, 'no on-screen demo/recreation label')
    require(type(c.get('recruitment_count')) is int and c['recruitment_count'] == 1, 'recruitment quantity must be one')
    require(bool(c.get('product_reference')), 'complete actual product reference required')
    required = {'hook_playback', 'product_fidelity', 'full_audio', 'speaker_continuity', 'lip_sync', 'ending'}
    require(required.issubset(set(c.get('review_required', []))), 'missing mandatory playback/audio/ending review gates')
    return errors


def render(pack, folder):
    e = html.escape
    parts = ['<!doctype html><meta charset="utf-8"><title>UGC production boards</title>',
             '<style>body{background:#141414;color:#eee;font:17px/1.55 system-ui;max-width:1250px;margin:auto;padding:32px}article{border-top:2px solid #555;margin:60px 0}section{background:#222;padding:24px;margin:16px 0;border-radius:12px}pre{white-space:pre-wrap;font:14px/1.5 monospace}img{max-width:100%;max-height:650px}summary{cursor:pointer;color:#c7ed76}small{color:#bbb}</style>',
             '<h1>UGC — сценарии и раскадровки</h1><p>Конверсия требует проверки рекламным тестом.</p>']
    for ad in pack['creatives']:
        aid = ad['source_id']
        parts.append(f'<article><h2>{aid} · {e(ad["language"])} · {ad["duration"]}s</h2><p>{e(ad["hypothesis_ru"])}</p>')
        board = folder / 'boards' / f'{aid}.png'
        if board.exists():
            parts.append(f'<a href="boards/{aid}.png"><img src="boards/{aid}.png"></a>')
        parts.append('<h3>Три входа в историю</h3>')
        for h in ad['hooks']:
            parts.append(f'<p><b>{e(h["variant"])}: {e(h["spoken"])}</b><br>{e(h["visual"])}<br><small>{e(h["bridge"])}</small></p>')
        for s in ad['scenes']:
            parts.append(f'<section><h3>{s["id"]} · {s["start"]}–{s["end"]}s</h3><b>{e(s["dialogue"])}</b><p>{e(s["purpose_ru"])}</p><p>{e(s["visual"])}</p><p>Overlay: {e(s["overlay"])}</p><details><summary>Scene / frame prompts</summary><pre>{e(s["prompt"])}\n\nFRAME:\n{e(s["frame_prompt"])}</pre></details></section>')
        for c in ad['clips']:
            parts.append(f'<details><summary>{e(c["id"])} · {c["duration"]}s · Seedance prompt</summary><pre>{e(c["prompt"])}</pre></details>')
        parts.append(f'<details><summary>Evidence and editing</summary><pre>{e(json.dumps({k:ad[k] for k in ("claim_ledger","edit_plan","qa")}, ensure_ascii=False, indent=2))}</pre></details></article>')
    (folder / 'review.html').write_text('\n'.join(parts))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--validate', action='store_true')
    p.add_argument('--legacy', action='store_true', help='Historical packs only: skip the current production contract, never certify release')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.validate:
        pack = json.loads(args.source.read_text())
        errors = validate(pack, legacy=args.legacy)
        if errors:
            raise SystemExit('\n'.join(errors))
        render(pack, args.out)
        print(f'Validated {len(pack["creatives"])} creatives; {sum(len(a["scenes"]) for a in pack["creatives"])} scenes. Visual/audio/claim QA is still separate.')
    else:
        bundle = '\n\n'.join([(ROOT/'agents/ugc_director/AGENT_PROMPT.md').read_text(),
                              (ROOT/'shared/UGC_VIDEO_PLAYBOOK.md').read_text(),
                              (ROOT/'shared/UGC_PRODUCTION_LEARNINGS.md').read_text(),
                              '# Source data\n'+args.source.read_text()])
        (args.out/'_ugc_context.md').write_text(bundle)
        print('Context ready. Session model must author scripts.json; no external model API called.')


if __name__ == '__main__':
    main()
