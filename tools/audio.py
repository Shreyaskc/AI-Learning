"""Incremental source -> transcript -> Kokoro -> validated AAC workflow.

sync/check use the standard library. generate requires the pinned optional environment.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unicodedata
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor,as_completed
import narration

ROOT=narration.ROOT


def atomic_json(path,value):
    temporary=path.with_suffix('.tmp.json');temporary.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n');temporary.replace(path)


def comparable(text):return ''.join(c for c in unicodedata.normalize('NFKC',text).casefold() if c.isalnum())


def generate(args):
    # Never initialize an ML runtime for sync/check or the static reader build.
    import importlib.metadata
    import numpy as np
    import soundfile as sf
    import torch
    from kokoro import KModel,KPipeline
    snapshot=Path(args.snapshot).expanduser().resolve()
    for name in ['config.json','kokoro-v1_0.pth','voices/af_heart.pt']:
        if not (snapshot/name).is_file():raise SystemExit('Missing official local model file: '+name)
    if narration.sha((snapshot/'kokoro-v1_0.pth').read_bytes())!=narration.MODEL_SHA:raise SystemExit('Model checksum mismatch')
    expected_voice=narration.SETTINGS.get('voice_sha256')
    if expected_voice and narration.sha((snapshot/'voices/af_heart.pt').read_bytes())!=expected_voice:raise SystemExit('Voice checksum mismatch')
    if narration.sha((snapshot/'config.json').read_bytes())!='5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f':raise SystemExit('Config checksum mismatch')
    torch.set_num_threads(args.threads);torch.set_num_interop_threads(1)
    entries=narration.desired()
    if args.chapter:entries=[e for e in entries if e['chapter'].startswith(args.chapter)]
    if args.limit:entries=entries[:args.limit]
    records_path=ROOT/'audio/recordings.json'
    records=json.loads(records_path.read_text()) if records_path.exists() else {}
    pending=[]
    for entry in entries:
        previous=records.get(entry['id'],{});asset=ROOT/entry['src']
        if previous.get('generation_key')==entry['generation_key'] and previous.get('qc_pass') and asset.is_file() and narration.sha(asset.read_bytes())==previous.get('sha256'):
            continue
        pending.append(entry)
    if not pending:print('No missing or stale recordings; no model initialized.');return
    print(f'Initializing official local Kokoro for {len(pending)} pending sections; CPU threads={args.threads}',flush=True)
    model=KModel(repo_id='hexgrad/Kokoro-82M',config=str(snapshot/'config.json'),model=str(snapshot/'kokoro-v1_0.pth')).to('cpu').eval()
    pipeline=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',model=model,device='cpu')
    voice=torch.load(snapshot/'voices/af_heart.pt',weights_only=True,map_location='cpu')
    versions={name:importlib.metadata.version(name) for name in ['kokoro','misaki','torch','transformers','soundfile','en-core-web-sm']}
    if versions['kokoro']!='0.9.4' or versions['misaki']!='0.9.4':raise SystemExit('Use kokoro==0.9.4 and misaki==0.9.4 for this voice recipe')
    run_start=time.monotonic();completed=0
    for entry in pending:
        start=time.monotonic();torch.manual_seed(int(entry['generation_key'][:8],16))
        pieces=[];segments=[]
        paragraphs=[p.strip() for p in entry['text'].strip().split('\n\n') if p.strip()]
        for index,paragraph in enumerate(paragraphs):
            samples=[];graphemes=[];phoneme_count=0
            with torch.inference_mode():
                for gs,ps,audio in pipeline(paragraph,voice=voice,speed=1.0):
                    if audio is None or not len(audio):raise ValueError('Empty TTS output: '+entry['id'])
                    chunk=audio.detach().cpu().numpy()
                    if not np.isfinite(chunk).all() or np.max(np.abs(chunk))<0.001:raise ValueError('Nonfinite/silent TTS output: '+entry['id'])
                    samples.append(chunk);graphemes.append(gs);phoneme_count+=len(ps or '')
            if not samples or not phoneme_count:raise ValueError('No pronunciation output: '+entry['id'])
            if comparable(' '.join(graphemes))!=comparable(paragraph):
                raise ValueError('Grapheme coverage differs; possible truncation: '+entry['id']+' paragraph '+str(index+1)+'\nINPUT '+paragraph+'\nOUTPUT '+' '.join(graphemes))
            audio=np.concatenate(samples).astype(np.float32)
            # Avoid accidental PCM clipping while preserving each section's dynamics.
            peak=float(np.max(np.abs(audio)))
            if peak>0.98:audio*=0.98/peak
            pieces.append(audio)
            segments.append({'paragraph':index+1,'characters':len(paragraph),'phonemes':phoneme_count,'seconds':round(len(audio)/24000,3),'graphemes_complete':True})
            if index+1<len(paragraphs):pieces.append(np.zeros(6000,dtype=np.float32))
        raw=np.concatenate(pieces)
        seconds=len(raw)/24000
        words=entry['words']
        if not (max(1,words/8)<=seconds<=words*1.25+25):raise ValueError('Implausible duration: '+entry['id']+' '+str(seconds))
        frame=480
        padded=np.pad(raw,(0,(-len(raw))%frame))
        rms=np.sqrt(np.mean(padded.reshape(-1,frame)**2,axis=1))
        longest=run=0
        for silent in rms<0.001:
            run=run+1 if silent else 0;longest=max(longest,run)
        longest_silence=longest*frame/24000
        if longest_silence>4.0:raise ValueError('Unexpected long silence: '+entry['id']+' '+str(longest_silence))
        with tempfile.TemporaryDirectory(prefix='ai-fluency-audio-') as tmp:
            wav=Path(tmp)/'section.wav';encoded=Path(tmp)/'section.m4a'
            sf.write(wav,raw,24000,subtype='PCM_16')
            command=['ffmpeg','-v','error','-nostdin','-y','-i',str(wav),'-af','loudnorm=I=-19:TP=-1.5:LRA=7','-ar','24000','-ac','1','-c:a','aac','-b:a','64k','-movflags','+faststart','-metadata','title='+entry['title']+' — '+entry['section'],'-metadata','artist=Synthetic narration: Kokoro-82M v1.0, af_heart',str(encoded)]
            subprocess.run(command,check=True)
            info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,sample_rate,channels','-of','json',str(encoded)],text=True))
            duration=float(info['format']['duration'])
            if abs(duration-seconds)>0.25 or info['streams'][0]['codec_name']!='aac':raise ValueError('Encoded media duration/codec mismatch: '+entry['id'])
            subprocess.run(['ffmpeg','-v','error','-nostdin','-i',str(encoded),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
            asset=ROOT/entry['src'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(encoded,asset)
        record={'generation_key':entry['generation_key'],'sha256':narration.sha(asset.read_bytes()),'bytes':asset.stat().st_size,'duration_seconds':duration,'source_sha256':entry['source_sha256'],'transcript_sha256':entry['transcript_sha256'],'paragraph_count':len(paragraphs),'segments':segments,'longest_silence_seconds':round(longest_silence,3),'qc_pass':True,'graphemes_complete':True,'phonemes_nonempty':True,'decoded':True,'versions':versions,'cpu_threads':args.threads,'generation_seconds':round(time.monotonic()-start,3)}
        records[entry['id']]=record;atomic_json(records_path,records)
        completed+=1
        print(f'VALIDATED {entry["chapter"]} {entry["section"]}: {duration:.1f}s, {record["bytes"]} bytes; {completed}/{len(pending)} this run; elapsed {time.monotonic()-run_start:.0f}s',flush=True)
    print('Generation checkpoint complete.',flush=True)


def audit_pronunciation(args):
    import re
    from kokoro import KPipeline
    pipeline=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',model=False)
    known={}
    for term in ['A.I.','A.P.I.','PCA','GPU','CPU']:
        phones,_=pipeline.g2p(term)
        if not phones:raise SystemExit('Empty acronym pronunciation: '+term)
        known[term]=phones
    if 'ɐ' in known['A.I.'] or 'ɐ' in known['A.P.I.']:raise SystemExit('Initial A is being treated as an article')
    failures=[];tokens_count=0;paragraphs=0
    for entry in narration.desired():
        for paragraph in entry['text'].strip().split('\n\n'):
            phones,tokens=pipeline.g2p(paragraph);paragraphs+=1
            if not phones:failures.append({'section':entry['id'],'reason':'empty paragraph phonemes'})
            for token in tokens:
                if any(character.isalnum() for character in token.text):
                    tokens_count+=1
                    if not any(c.isalpha() for c in (token.phonemes or '')):failures.append({'section':entry['id'],'token':token.text,'reason':'token has no spoken phonemes'})
    evidence={'sections':len(narration.sections()),'paragraphs':paragraphs,'alphanumeric_tokens':tokens_count,'acronym_probes':known,'missing':failures,'human_listening_review':False}
    if args.report:atomic_json(Path(args.report),evidence)
    if failures:raise SystemExit('Pronunciation audit requires review: '+json.dumps(failures[:20],ensure_ascii=False))
    print('PASS: phoneme output for',tokens_count,'alphanumeric tokens in',paragraphs,'paragraphs; acronym probes pass. This is not human listening review.')


def report():
    entries=narration.desired();records=narration.read_json('audio/recordings.json') if (ROOT/'audio/recordings.json').exists() else {}
    ready={e['id'] for e in entries if records.get(e['id'],{}).get('generation_key')==e['generation_key'] and records.get(e['id'],{}).get('qc_pass') is True and (ROOT/e['src']).exists()}
    seconds=sum(records[e['id']]['duration_seconds'] for e in entries if e['id'] in ready)
    total_bytes=sum(records[e['id']]['bytes'] for e in entries if e['id'] in ready)
    lines=['# Narration coverage and validation','',f'{len(ready)} of {len(entries)} sections currently have validated recordings matching the current transcript/voice recipe. Total available duration: {seconds/3600:.2f} hours; media: {total_bytes/1e6:.2f} MB.','',
           'The inventory includes every introduction and heading section in the 20 numbered chapters. All normalized source text is partitioned once; narration retains explanations, worked examples, exercises and solutions. Written reference pages such as the glossary are outside this ordered episode sequence.','',
           '| Chapter | Ready / sections | Duration (minutes) |','| --- | --- | --- |']
    for chapter in dict.fromkeys(e['chapter'] for e in entries):
        group=[e for e in entries if e['chapter']==chapter];done=[e for e in group if e['id'] in ready]
        lines.append('| '+chapter+' | '+str(len(done))+' / '+str(len(group))+' | '+f'{sum(records[e["id"]]["duration_seconds"] for e in done)/60:.1f}'+' |')
    lines += ['', '## Reproducible checks','',
              '`python3 tools/audio.py sync` updates section/transcript inventory. `check` fails on new, missing, changed or corrupt material; `generate` reuses validated unchanged clips and checkpoints each new one. Model/config/voice downloads are pinned and verified, and synthesis can run entirely offline. See the README for exact dependencies and commands.','',
              'Each recording has complete input-grapheme coverage, nonempty phonemes, finite non-silent waveform, plausible duration, maximum-silence checks and a successful encoded-media decode. Numeric equations and acronyms are explicitly adapted for listening; the two fenced code blocks have authored explanations. Metadata and per-paragraph checks are retained in `audio/recordings.json`. Each file and transcript is SHA-256 bound to its generation recipe.','',
              'The generator uses Kokoro-82M v1.0, af_heart, 24 kHz mono AAC, requested 64 kbit/s, fast-start metadata and loudness processing targeting -19 LUFS and -1.5 dBTP. Source text and inference remain local. No paid service, credentials or cloned voice are used.','',
              '## Limits and deployment gate','',
              'Automated text/phoneme/signal checks do not establish flawless pronunciation. Rendered browser smoke checks are reported separately from these automated checks. Mobile, screen-reader and background playback and full human listening review are not established by waveform or DOM-double tests.','',
              'The existing Pages workflow remains unchanged because the connected credential lacks workflow-write permission. Remote enforcement for future direct pushes requires the owner to install `review/proposed-course-validation-workflow.yml` or add the documented pre-upload check steps. The local audio gate and contributor commands are delivered without changing scopes.','']
    (ROOT/'review/AUDIO-COVERAGE.md').write_text('\n'.join(lines))
    evidence={'sections':len(entries),'ready':len(ready),'duration_seconds':seconds,'bytes':total_bytes,'words':sum(e['words'] for e in entries),'settings':narration.SETTINGS,'source_files':{name:narration.sha((ROOT/name).read_bytes()) for name in ['tools/audio.py','tools/narration.py','audio/speech-math.json','audio/pronunciations.json','audio/code-narration.json','audio/editorial.json']}}
    atomic_json(ROOT/'review/evidence/full-audio-coverage.json',evidence)
    print('Wrote coverage report:',len(ready),'/',len(entries))


def verify_live(args):
    base=args.base.rstrip('/')+'/'
    if not base.startswith('https://'):raise SystemExit('Use the verified HTTPS site URL.')
    errors=narration.coverage()
    if errors:raise SystemExit('Local coverage must pass first: '+errors[0])
    entries=narration.desired();records=narration.read_json('audio/recordings.json')
    expected={e['src']:records[e['id']]['sha256'] for e in entries}
    expected.update({e['transcript']:e['transcript_sha256'] for e in entries})
    import build
    for path in list(build.outputs())+[ROOT/name for name in ['app.js','practice.js','podcast.js','terms.js','style.css','README.md']]:
        expected[str(path.relative_to(ROOT))]=narration.sha(path.read_bytes())
    query='?verify='+args.revision
    def request(path):
        for attempt in range(4):
            try:
                req=urllib.request.Request(base+path+query,headers={'Cache-Control':'no-cache'})
                result=hashlib.sha256()
                with urllib.request.urlopen(req,timeout=45) as response:
                    status=response.status
                    for chunk in iter(lambda:response.read(1024*1024),b''):result.update(chunk)
                if status!=200 or result.hexdigest()!=expected[path]:raise ValueError('HTTP/content mismatch: '+path)
                return {'path':path,'status':status,'sha256':result.hexdigest()}
            except (urllib.error.URLError,ValueError) as error:
                if attempt==3:raise
                time.sleep(2*(attempt+1))
    results=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(request,path):path for path in expected}
        for future in as_completed(futures):
            results.append(future.result())
            if len(results)%40==0:print('Live bytes verified:',len(results),'/',len(expected),flush=True)
    ranges=[]
    for chapter in dict.fromkeys(e['chapter'] for e in entries):
        entry=next(e for e in entries if e['chapter']==chapter)
        req=urllib.request.Request(base+entry['src']+query,headers={'Range':'bytes=0-1023','Cache-Control':'no-cache'})
        with urllib.request.urlopen(req,timeout=30) as response:
            data=response.read();status=response.status;header=response.headers.get('Content-Range','')
        if status!=206 or data!=(ROOT/entry['src']).read_bytes()[:1024]:raise SystemExit('Range request did not match: '+entry['src'])
        ranges.append({'chapter':chapter,'status':status,'content_range':header})
    related=[]
    for url in [url for _,url in build.COURSES]+['https://github.com/Shreyaskc/'+url.rstrip('/').rsplit('/',1)[1] for _,url in build.COURSES]:
        with urllib.request.urlopen(url,timeout=30) as response:
            if response.status!=200:raise SystemExit('Related course link unavailable: '+url)
            related.append({'url':url,'status':response.status})
    report={'related_courses':related,'base':base,'revision':args.revision,'files_verified':len(results),'sections':len(entries),'range_checks':ranges,'files':sorted(results,key=lambda r:r['path'])}
    if args.report:atomic_json(Path(args.report),report)
    print('PASS: exact live bytes for',len(results),'pages/scripts/transcripts/media; HTTP 206 audio delivery in',len(ranges),'chapters.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='operation',required=True)
    sub.add_parser('sync',help='reconcile all source sections and matching speech transcripts')
    checker=sub.add_parser('check',help='fail for new, changed, missing, corrupt or unvalidated narration')
    checker.add_argument('--transcripts-only',action='store_true')
    generator=sub.add_parser('generate',help='incrementally synthesize only missing/stale sections from local official model files')
    generator.add_argument('--snapshot',required=True)
    generator.add_argument('--threads',type=int,choices=[1,2],default=1)
    generator.add_argument('--chapter',help='chapter prefix, e.g. 08 or 08-transformers')
    generator.add_argument('--limit',type=int)
    live=sub.add_parser('verify-live',help='compare every deployed section and transcript against local hashes')
    live.add_argument('--base',default='https://shreyaskc.github.io/AI-Learning/')
    live.add_argument('--revision',required=True)
    live.add_argument('--report',type=Path)
    pronunciation=sub.add_parser('audit-pronunciation',help='check every transcript token with the installed local English G2P pipeline')
    pronunciation.add_argument('--report',type=Path)
    sub.add_parser('report',help='write the current coverage table and compact QC evidence')
    sub.add_parser('status')
    args=parser.parse_args()
    if args.operation=='sync':
        entries=narration.sync();print(f'Synced {len(entries)} sections in {len({e["chapter"] for e in entries})} chapters; {sum(e["words"] for e in entries)} spoken words.')
    elif args.operation=='check':
        errors=narration.coverage(not args.transcripts_only)
        if errors:raise SystemExit('\n'.join(errors))
        print('PASS: complete, current, hash-verified narration for every course section.' if not args.transcripts_only else 'PASS: complete current transcripts for every section.')
    elif args.operation=='generate':generate(args)
    elif args.operation=='verify-live':verify_live(args)
    elif args.operation=='report':report()
    elif args.operation=='audit-pronunciation':audit_pronunciation(args)
    else:
        entries=narration.desired();records=json.loads((ROOT/'audio/recordings.json').read_text()) if (ROOT/'audio/recordings.json').exists() else {}
        for chapter in dict.fromkeys(e['chapter'] for e in entries):
            group=[e for e in entries if e['chapter']==chapter];ready=sum(records.get(e['id'],{}).get('generation_key')==e['generation_key'] and records.get(e['id'],{}).get('qc_pass') is True for e in group)
            print(f'{chapter}: {ready}/{len(group)} sections validated')
        print('Errors:',len(narration.coverage()))


if __name__=='__main__':main()
