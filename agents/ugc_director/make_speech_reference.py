"""Create timed speech references; explicit voice, scene timing, and duration checks."""
import argparse, asyncio, json, subprocess
from pathlib import Path


def probe(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))
async def main():
    p=argparse.ArgumentParser();p.add_argument('spec',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    d=json.loads(a.spec.read_text());a.out.mkdir(parents=True,exist_ok=True)
    for clip in d['clips']:
        folder=a.out/clip['id'];folder.mkdir(exist_ok=True);segments=[]
        for n,s in enumerate(clip['scenes'],1):
            provider=d.get('provider','edge')
            file=folder/f's{n:02}.{"aiff" if provider=="macos" else "mp3"}'
            if not file.exists() or file.stat().st_size==0:
                if provider=='macos':
                    textfile=folder/f's{n:02}.txt';textfile.write_text(s['text'])
                    subprocess.run(['say','-v',d['voice'],'-r',str(d.get('words_per_minute',170)),'-f',str(textfile),'-o',str(file)],check=True)
                else:
                    import edge_tts
                    await edge_tts.Communicate(s['text'],d['voice'],rate=d.get('rate','+0%'),pitch=d.get('pitch','+0Hz')).save(str(file))
            duration=probe(file);available=s['end']-s['start']-.15
            if duration>available:raise ValueError(f'{clip["id"]} scene{n}: {duration:.2f}s exceeds {available:.2f}s; shorten copy')
            segments.append(dict(file=str(file),duration=duration,**s))
        cmd=['ffmpeg','-y','-v','error']
        for s in segments:cmd+=['-i',s['file']]
        filters=[f'[{n}:a]adelay={round((s["start"]+.08)*1000)}:all=1[a{n}]' for n,s in enumerate(segments)]
        filters.append(''.join(f'[a{n}]' for n in range(len(segments)))+f'amix=inputs={len(segments)}:normalize=0,apad,atrim=0:{clip["duration"]}[out]')
        out=folder/f'{clip["id"]}_speech.wav'
        cmd+=['-filter_complex',';'.join(filters),'-map','[out]','-ar','24000','-ac','1','-c:a','pcm_s16le',str(out)]
        subprocess.run(cmd,check=True)
        (folder/'source.json').write_text(json.dumps(dict(voice=d['voice'],provider=provider,clip=clip['id'],segments=segments,output_duration=probe(out)),ensure_ascii=False,indent=2))
        print(out,flush=True)
asyncio.run(main())
