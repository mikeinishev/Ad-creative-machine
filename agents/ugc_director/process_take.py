"""Probe, decode, transcribe and align a downloaded, already authorized video take."""
import argparse
import json
import re
import subprocess
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('video',type=Path)
p.add_argument('--language',required=True,choices=['en','es','tr','pt'])
p.add_argument('--seconds',required=True,type=float)
p.add_argument('--clip',required=True,type=int)
p.add_argument('--verify-model',type=Path,help='Optional second local Whisper model for independent transcript review')
a=p.parse_args()
video=a.video.resolve(); assets=video.parent
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
(assets/f'c{a.clip:02}_probe.json').write_text(json.dumps(probe,indent=2))
if not any(s['codec_type']=='audio' for s in probe['streams']):raise SystemExit('REJECT: missing native audio')
duration=float(probe['format']['duration'])
if abs(duration-a.seconds)>.25:raise SystemExit(f'REVIEW: expected {a.seconds}s, got {duration}')
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
levels_run=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True)
levels={k:float(v) for k,v in re.findall(r'(mean_volume|max_volume):\s*([-\d.]+)',levels_run.stderr)}
(assets/f'c{a.clip:02}_audio_levels.json').write_text(json.dumps(levels,indent=2))
print('AUDIO LEVELS:',levels)
wav=assets/f'c{a.clip:02}.wav'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-ar','16000','-ac','1',str(wav)],check=True)
prefix=assets/f'c{a.clip:02}_align'
with (assets/f'c{a.clip:02}_align.log').open('w') as log:
 subprocess.run(['whisper-cli','-m',str(Path.home()/'.cache/hyperframes/whisper/models/ggml-small.bin'),'-f',str(wav),'-l',a.language,'-ojf','-dtw','small','-nfa','-ng','-of',str(prefix)],stdout=log,stderr=log,check=True)
trans=json.loads(prefix.with_suffix('.json').read_text())
print('TRANSCRIPT:', ' '.join(s['text'] for s in trans['transcription']))
verification=a.verify_model
if verification is None and a.language=='tr':
 candidate=Path.home()/'.cache/hyperframes/whisper/models/ggml-large-v3-turbo.bin'
 if candidate.exists():verification=candidate
if verification:
 if not verification.is_file():raise SystemExit(f'Missing verification model: {verification}')
 verify_prefix=assets/f'c{a.clip:02}_verify'
 with (assets/f'c{a.clip:02}_verify.log').open('w') as log:
  subprocess.run(['whisper-cli','-m',str(verification),'-f',str(wav),'-l',a.language,'-ojf','-ng','-of',str(verify_prefix)],stdout=log,stderr=log,check=True)
 verified=json.loads(verify_prefix.with_suffix('.json').read_text())
 print('SECOND TRANSCRIPT:', ' '.join(s['text'] for s in verified['transcription']))
print('Probe/decode/ASR complete. Compare disagreements before subtitle edits. ASR is not human listening or a native-language quality guarantee.')
