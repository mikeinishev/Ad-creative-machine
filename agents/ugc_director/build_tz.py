#!/usr/bin/env python3
"""Render a Russian production brief (TZ.md) with storyboard frames from an authored scripts.json.

  python3 agents/ugc_director/build_tz.py PACK/scripts.json --frames storyboard --title "ТЗ: видео по образцу 220 — getreviews"

Frames are looked up as PACK/<frames>/<pattern>; missing frames render as a placeholder,
so the brief can be built before the images are ready and rebuilt afterwards.
Pattern fields: {source_id} {scene} {country_lc} {casting}. Default matches image_frames.py.

Per creative the brief shows: casting + product references, a scene table (frame, timing, purpose,
action, line, translation, on-screen text), on-screen text, the A/B/C hooks, and the exact
Higgsfield clip prompts with their reference files. Common requirements come from the pack's
`requirements` list ([[param, value], ...]) or the defaults below.
"""
import argparse, json
from pathlib import Path

DEFAULT_REQUIREMENTS = [
    ('Формат', '9:16, вертикальное «снято коллегой на телефон» UGC'),
    ('Генерация', 'Higgsfield → Seedance 2.0, 720p, Audio ON, бесплатный Unlimited в веб-интерфейсе. '
                  'Платный Seedance 2.5 (CLI) — только по явному разрешению Mike на конкретный ролик'),
    ('Референсы в каждый клип', 'персонаж (кастинг) + полная локальная подставка; роли референсов назвать в промпте'),
    ('Голос', 'живой носитель, один и тот же голос во всём ролике; губы синхронно; без женского TTS-гайда для мужчины'),
    ('Музыка', 'нет. Только речь и звук зала'),
    ('Плашки «демо», лейблы', 'нет'),
    ('Предложение', 'ищем ОДИН ресторан. Никаких цен, цифр и результатов клиентов'),
    ('Монтаж', 'жёсткие склейки на завершённом действии; не растягивать до ровной длины'),
    ('Субтитры', 'точная услышанная речь после ASR; белый текст на тёмной подложке; не на лице и не на подставке'),
    ('Текст на экране', 'хук-заголовок 0–1.8 с и CTA в последней сцене над подставкой'),
    ('Запрещено', 'бьюти-фильтр, кино-грейд, слоумо, искусственное боке, выдуманный читаемый UI телефона, '
                  'туристический реквизит, упрощённая подставка без QR'),
]
ACCEPTANCE = ('**Приёмка каждого ролика:** хук ловится в первые 1.5 с · подставка совпадает с референсом '
              '(колесо слева, QR справа) · звук целиком без обрывов · один голос · губы в синхроне · '
              'концовка с CTA не обрезана · текст проверил носитель языка.')
WORK_ORDER = [
    'Носитель проверяет реплики.',
    'Голосовая проба 4 с первой реплики на стартовом кадре каждого персонажа → Mike слушает.',
    'Генерация клипов в Higgsfield, проверка дублей (`inspect_take.py`), монтаж (`compose_edit.py`).',
    'Приёмка по чек-листу → упаковка с номером .seq → загрузка в Meta только по команде Mike.',
]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('scripts', type=Path)
    p.add_argument('--frames', default='storyboard')
    p.add_argument('--pattern', default='{source_id}_{scene}.png')
    p.add_argument('--title', default='ТЗ: видео-креативы')
    p.add_argument('--intro', default='', help='markdown paragraph(s) under the title: funnel, sample ad, why')
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    root = a.scripts.resolve().parent
    pack = json.loads(a.scripts.read_text())

    def img(rel, alt):
        return f'![{alt}](<{rel}>)' if (root / rel).exists() else f'_(кадр {alt} ещё рисуется)_'

    def rel(path):
        path = Path(path)
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return str(path)

    L = [f'# {a.title}', '']
    if a.intro:
        L += [a.intro, '']
    L += ['## Общие требования', '', '| Параметр | Значение |', '|---|---|']
    L += [f'| {k} | {v} |' for k, v in (pack.get('requirements') or DEFAULT_REQUIREMENTS)]
    L += ['', ACCEPTANCE, '']
    for c in pack['creatives']:
        fields = dict(source_id=c['source_id'], country_lc=str(c.get('country', '')).lower(), casting=c.get('casting', ''))
        L += ['---', '', f"## {c['source_id']} · {c.get('venue', '')} · {c.get('duration', '?')} с · {c.get('language', '')}", '']
        refs = c.get('frame_references') or c['clips'][0]['references']
        L += [' '.join(img(rel(r), Path(r).stem) for r in refs), '']
        if c.get('casting_prompt'):
            L += [f"**Персонаж:** {c['casting_prompt']}", '']
        if c.get('venue_prompt'):
            L += [f"**Место:** {c['venue_prompt']}", '']
        L += ['### Раскадровка', '', '| # | Время | Кадр | Зачем сцена | Действие (для генерации) | Реплика | Перевод | Текст на экране |',
              '|---|---|---|---|---|---|---|---|']
        for s in c['scenes']:
            frame = img(f"{a.frames}/{a.pattern.format(scene=s['id'], **fields)}", s['id'])
            cell = lambda t: str(t or '—').replace('|', '/').replace('\n', ' ')
            L.append(f"| {s['id']} | {s['start']}–{s['end']} с | {frame} | {cell(s.get('purpose_ru'))} | {cell(s.get('visual'))} | "
                     f"{cell(s.get('dialogue'))} | {cell(s.get('dialogue_ru'))} | {cell(s.get('overlay'))} |")
        ep = c.get('edit_plan', {})
        if ep:
            L += ['', '### Текст на экране', ''] + [f'- {ep[k]}' for k in ('hook_headline', 'cta_overlay') if ep.get(k)]
        if c.get('hooks'):
            L += ['', '### Запасные хуки (A/B первой сцены)', '']
            L += [f"- **{h['variant']}{' (основной)' if h.get('selected') else ''}:** «{h['spoken']}» — {h['visual']}" for h in c['hooks']]
        L += ['', f"<details><summary>Промпты для Higgsfield — {c['source_id']}</summary>", '']
        for cl in c['clips']:
            r = ', '.join(f'`{rel(x)}`' for x in cl['references'])
            L += [f"**Клип {cl['id']} · {cl['duration']} с** · референсы: {r}", '', '```', cl['prompt'], '```', '']
        L += ['</details>', '']
    L += ['---', '', '## Порядок работы', ''] + [f'{i}. {t}' for i, t in enumerate(WORK_ORDER, 1)] + ['']
    out = a.out or root / 'TZ.md'
    out.write_text('\n'.join(L))
    print(out, len(L), 'lines')


if __name__ == '__main__':
    main()
