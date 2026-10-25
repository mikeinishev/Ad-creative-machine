#!/usr/bin/env python3
"""Pack an inspected finished UGC master, allocating one never-reused creative ID."""
import argparse, fcntl, hashlib, json, shutil, subprocess
from pathlib import Path

PRIMARY=Path('/Users/mikeinishev/Projects/Ad creatives machine=]')
DEST=PRIMARY/'outputs/videos/2026.10.25_boomerang_ugc_hooks'

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('project',type=Path);p.add_argument('--source',required=True)
 p.add_argument('--product',required=True,choices=['getreviews','customers100'])
 p.add_argument('--accent',required=True);p.add_argument('--language',required=True)
 p.add_argument('--expected-duration',type=float,default=30,help='Reviewed edit duration in seconds; defaults to 30')
 p.add_argument('--visual-reviewed',action='store_true',required=True)
 p.add_argument('--transcript-reviewed',action='store_true',required=True)
 a=p.parse_args();project=a.project.resolve();video=project/f'{a.source}_hook_master.mp4'
 if not video.exists():raise SystemExit(f'Missing final video {video}')
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
 streams=data['streams'];v=next(s for s in streams if s['codec_type']=='video')
 if (v['width'],v['height'])!=(720,1280) or not any(s['codec_type']=='audio' for s in streams):raise SystemExit('Invalid video dimensions or missing audio')
 duration=float(data['format']['duration'])
 if not 15 <= a.expected_duration <= 60:raise SystemExit('Expected duration must be between 15 and 60 seconds')
 if abs(duration-a.expected_duration)>.1:raise SystemExit(f'Expected {a.expected_duration}-second final, got {duration}')
 subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
 digest=hashlib.sha256(video.read_bytes()).hexdigest();DEST.mkdir(parents=True,exist_ok=True)
 with (PRIMARY/'outputs/creatives/.seq').open('r+') as seq:
  fcntl.flock(seq,fcntl.LOCK_EX)
  manifest=DEST/'_pack.json';pack=json.loads(manifest.read_text()) if manifest.exists() else {'date':'2026-10-25','videos':[],'status':'in_progress'}
  existing=next((x for x in pack['videos'] if x.get('sha256')==digest),None)
  if existing:print(DEST/existing['file']);return
  number=int(seq.read().strip())+1;seq.seek(0);seq.write(str(number));seq.truncate();seq.flush()
  name=f'{number:03}_mi_restaurant_owners_{a.product}_{a.accent}_9x16.mp4'
  shutil.copy2(video,DEST/name)
  shutil.copytree(project,DEST/'editable'/str(number),ignore=shutil.ignore_patterns('node_modules','.hyperframes','*_hook_master.mp4','*_raw_rejected_body.mp4'),dirs_exist_ok=False)
  pack['videos'].append(dict(id=number,source_id=a.source,file=name,language=a.language,duration=round(duration,3),status='rendered_reviewable',sha256=digest,limitations=['native-speaker listening not performed','conversion untested']))
  temp=manifest.with_suffix('.tmp');temp.write_text(json.dumps(pack,ensure_ascii=False,indent=2));temp.replace(manifest)
 progress=PRIMARY/'outputs/storyboards/2026.10.25_ugc_hooks_v3/production.json'
 if progress.exists():
  status=json.loads(progress.read_text())
  for entry in status['videos']:
   if entry['source_id']==a.source:
    entry.update(status='final_verified',final_creative_id=str(number),final_path=str(DEST/name),qa='Full decode and reviewed transcript/visuals; native-speaker listening not performed.')
  progress.write_text(json.dumps(status,ensure_ascii=False,indent=2))
 from delivery_index import render
 render()
 print(DEST/name)

if __name__=='__main__':main()
