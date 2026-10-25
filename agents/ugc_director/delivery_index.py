#!/usr/bin/env python3
"""Create a local review page from the actual delivered video manifest."""
import html,json,re
from pathlib import Path
DEST=Path('/Users/mikeinishev/Projects/Ad creatives machine=]/outputs/videos/2026.10.25_boomerang_ugc_hooks')
def render():
 pack=json.loads((DEST/'_pack.json').read_text());parts=['''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>UGC · готовые ролики</title><style>body{margin:32px auto;padding:0 20px;max-width:1100px;background:#171818;color:#eee;font:17px/1.5 system-ui}h1{font-size:30px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}article{padding:20px;background:#242626;border-radius:16px}video{display:block;width:100%;max-height:620px;background:#000;border-radius:10px}a{color:#b9e78f}small{color:#aaa}h2{font-size:20px}</style><h1>UGC · готовые ролики</h1>''',f'<p>{len(pack["videos"])} файлов из 10. Статусы исправлений указаны на карточках. 9:16 · речь и звук помещения.</p><main>']
 for v in pack['videos']:
  if not (DEST/v['file']).is_file():raise FileNotFoundError(v['file'])
  e=html.escape;name=e(v['file']);note=f'<p style="color:#ffb890">{e(v.get("review_note",""))}</p>' if v.get('review_note') else '';
  captions=DEST/'editable'/str(v['id'])/'compositions/captions.html'
  if captions.exists():
   spoken=' '.join(html.unescape(x) for x in re.findall(r'<span>(.*?)</span>',captions.read_text()))
   (DEST/f'{v["id"]}_script.md').write_text(f'# {v["id"]} · {v["language"]} · {v["duration"]} s\n\n{spoken}\n\nИсточник: субтитры финального монтажа. Отдельные экранные CTA не входят в расшифровку речи.\n')
  parts.append(f'<article><h2>{v["id"]} · {e(v["language"])} · исходный {e(v["source_id"])}</h2>{note}<p><small>{v["duration"]} секунд</small></p><video controls preload="metadata" playsinline src="{name}"></video><p><a href="{name}" download>Скачать MP4</a></p><p><a href="{v["id"]}_script.md">Текст финального ролика</a></p><p><a href="editable/{v["id"]}/">Монтажный проект</a></p></article>')
 parts.append('</main><p><small>Проверены экспорт, субтитры и выбранные кадры. Проверка речи носителем языка и рекламный тест конверсии не проводились.</small></p></html>');(DEST/'index.html').write_text('\n'.join(parts));print(DEST/'index.html')
if __name__=='__main__':render()
