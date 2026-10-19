"""Deterministic full-section transcripts and coverage; no ML dependencies on import."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ADAPTER_VERSION='section-narration-1'
MODEL_SHA='496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4'
MODEL_REVISION='f3ff3571791e39611d31c381e3a41a3af07b4987'
VOICE_SHA=''
SETTINGS={'model':'Kokoro-82M v1.0','model_revision':MODEL_REVISION,'model_sha256':MODEL_SHA,'voice':'af_heart','speed':1.0,'sample_rate':24000,'codec':'aac','bitrate':'64k','loudness_target_lufs':-19,'true_peak_target_dbtp':-1.5,'paragraph_pause_ms':250,'voice_sha256':'0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff','engine':'kokoro==0.9.4','pronunciation_engine':'misaki==0.9.4'}


def sha(value):return hashlib.sha256(value.encode() if isinstance(value,str) else value).hexdigest()
def read_json(name):return json.loads((ROOT/name).read_text())
def slug(text):return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')


def sections(paths=None):
    """Partition all normalized source text, including each chapter introduction, exactly once."""
    result=[]
    for path in paths or sorted((ROOT/'course').glob('[0-9][0-9]-*.md')):
        lines=path.read_text().splitlines(keepends=True)
        title=lines[0].strip().removeprefix('# ')
        boundaries=[0]+[i for i,line in enumerate(lines) if re.match(r'^#{2,6} ',line)]+[len(lines)]
        seen=set()
        for begin,end in zip(boundaries,boundaries[1:]):
            heading='Introduction and prerequisites' if begin==0 else re.sub(r'^#{2,6} ','',lines[begin].strip())
            anchor=slug(title) if begin==0 else slug(heading)
            identity=path.stem+'--'+('introduction' if begin==0 else anchor)
            if identity in seen:raise ValueError('Duplicate section ID: '+identity)
            seen.add(identity)
            raw=''.join(lines[begin:end])
            result.append(dict(id=identity,chapter=path.stem,title=title,section=heading,anchor=anchor,source='course/'+path.name,source_sha256=sha(raw),start_line=begin+1,end_line=end,raw=raw))
    return result


def inline_code(value,math):
    if value in math:return math[value].rstrip('.')
    if value.startswith('python3 '):
        if '-m http.server' in value:return 'Run the Python three local web server on port eight thousand.'
        filename=value.split()[1].split('/')[-1].removesuffix('.py').replace('_',' ')
        return 'Run the Python three '+filename+' lab command shown in the written section.'
    if value.startswith('--responses '):return 'the responses argument pointing to your recorded outputs J son file'
    if value in ['[low,_]','[lo,w,_]','[low,e,r,_]']:return math[value]
    if any(char in value for char in '=+*^|<>·'):
        raise ValueError('Author a precise speech-math entry for: '+value)
    return value.replace('_',' ').replace('.py',' dot py').replace('.html',' dot H T M L').replace('/',' slash ')


def plain(text,math,pronunciations):
    text=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',text)
    text=re.sub(r'`([^`\n]+)`',lambda m:inline_code(m[1],math),text)
    text=text.replace('**','')
    # Also expand the same full equations when the author writes them outside code spans.
    for expression,spoken in sorted(math.items(),key=lambda pair:len(pair[0]),reverse=True):
        if len(expression)>6 and any(c in expression for c in '=|^·'):
            text=text.replace(expression,spoken.rstrip('.'))
    # Speak operators and identifiers instead of asking the voice to guess raw notation.
    for original,spoken in [('dL/dW1_jk','the loss derivative for first-layer weight j k'),('dL/db1_j','the loss derivative for hidden bias j'),('dL/db2','the loss derivative for the output bias'),('dL/dv_j','the loss derivative for output weight j'),('dL/dw','the derivative of loss with respect to w'),('dL/dz','the derivative of loss with respect to z'),('dL/db','the derivative of loss with respect to bias b'),('dz/dw','the derivative of z with respect to w'),('QKᵀ','Q times K transposed'),('UΣVᵀ','U times sigma times V transposed'),('XW_Q','X times W sub Q'),('XW_K','X times W sub K'),('XW_V','X times W sub V')]:
        text=text.replace(original,spoken)
    text=re.sub(r'\b(AV|AB|BA)\b',lambda m:' times '.join(m[0]),text)
    text=re.sub(r'\bwx\b','w times x',text)
    text=re.sub(r'\b(\d+)([a-z])\b',r'\1 times \2',text)
    text=re.sub(r'\b([a-z])-(?=[a-z]\b)',r'\1 minus ',text)
    text=re.sub(r'(?<=[\d)])-(?=\w)',' minus ',text)
    text=text.replace('requests/s','requests per second').replace('tokens/s','tokens per second').replace('tokens/request','tokens per request')
    text=text.replace('train/test','training and test').replace('train/serve','training and serving').replace('input/output','input and output').replace('query/document','query and document').replace('prompt/response','prompt and response')
    text=re.sub(r'\b(log|exp|sqrt|sigmoid|tanh)\(([^()]+)\)',lambda m:{'log':'natural logarithm of ','exp':'exponential of ','sqrt':'square root of ','sigmoid':'sigmoid of ','tanh':'hyperbolic tangent of '}[m[1]]+m[2],text)
    text=re.sub(r'P\(([^()|]+)\|([^()]+)\)',r'the probability of \1 given \2',text)
    for unit,spoken in [('nats/token','nats per token'),('bits/token','bits per token'),('GB/s','gigabytes per second'),('GiB/s','gibibytes per second'),('MB/s','megabytes per second'),('cost/request','cost per request'),('seconds/request','seconds per request'),('ms/request','milliseconds per request')]:text=text.replace(unit,spoken)
    text=re.sub(r'\$([\d.]+)(/million)?',lambda m:('0'+m[1] if m[1].startswith('.') else m[1])+(' dollar' if m[1]=='1' else ' dollars')+(' per million' if m[2] else ''),text)
    text=text.replace('_',' sub ')
    text=text.replace('+',' plus ').replace('*',' times ').replace('^',' raised to the power ')
    text=text.replace('A/B test','A B test').replace('A/B experiment','A B experiment')
    text=re.sub(r'\b([A-Za-z]+)/(?=[A-Za-z])',lambda m:m[1]+(' divided by ' if len(m[1])==1 or m[1]=='transposed' else ' and '),text)
    text=text.replace('/',' divided by ')
    text=text.replace('-infinity','negative infinity')
    text=text.replace('The score for row i is The score for row i is','The score for row i is')
    text=text.replace('the Euclidean norm The Euclidean norm of x is','the Euclidean norm:')
    for token,replacement in sorted(pronunciations.items(),key=lambda pair:len(pair[0]),reverse=True):
        text=re.sub(r'(?<![\w])'+re.escape(token)+r'(?![\w])',replacement,text)
    text=re.sub(r'\b(\d+(?:\.\d+)?)e([+-]?\d+)\b',lambda m:m[1]+' times ten to the power '+m[2].replace('-','negative '),text,flags=re.I)
    text=re.sub(r'(?<!\w)-(?!\s)(?=\d|\.)','negative ',text)
    for source,target in [('±',' plus or minus '),('≈',' approximately '),('≥',' greater than or equal to '),('≤',' less than or equal to '),('≠',' not equal to '),('→',' leads to '),('²',' squared'),('ᵀ',' transposed'),('Σ',' sigma '),('×',' by '),('·',' dot '),('=',' equals '),('>',' greater than '),('<',' less than '),('∝',' proportional to '),('∑',' sum '),('√','square root of '),(' / ',' or '),('–',' to '),('—',', '),('…',', '),('||',' norm '),('∥',' relative to ')]:text=text.replace(source,target)
    text=re.sub(r'\bexp\(([^()]+)\)',r'exponential of \1',text)
    text=re.sub(r'\blog\(([^()]+)\)',r'natural logarithm of \1',text)
    text=re.sub(r'\bsqrt\(([^()]+)\)',r'square root of \1',text)
    text=text.replace('2dr','two times d times r')
    # Misaki can emit punctuation alone for leading decimals: make every digit audible.
    digit_words=['zero','one','two','three','four','five','six','seven','eight','nine']
    text=re.sub(r'(?<![\w.])\.(\d+)',lambda m:'zero point '+' '.join(digit_words[int(d)] for d in m[1]),text)
    text=re.sub(r'\bposition 0\b','position zero',text)
    text=re.sub(r'\.{2,}', '.', text)
    text=re.sub(r'\ban (large language model)',r'a \1',text)
    text=re.sub(r'\b[Rr]un Run\b','Run',text)
    return re.sub(r'\s+',' ',text).strip()


def transcript(section,math=None,pronunciations=None,blocks=None,editorial=None):
    math=math if math is not None else read_json('audio/speech-math.json')
    pronunciations=pronunciations if pronunciations is not None else read_json('audio/pronunciations.json')
    blocks=blocks if blocks is not None else read_json('audio/code-narration.json')
    editorial=editorial if editorial is not None else read_json('audio/editorial.json')
    overrides=[e for e in editorial if e['section']==section['id']]
    raw=section['raw']
    for override in overrides:
        if sha(override['source'])!=override['source_sha256'] or override['source'] not in raw:
            raise ValueError('Editorial adaptation is stale: '+section['id'])
        raw=raw.replace(override['source'],override['spoken'])
    chapter_number=int(section['chapter'][:2])
    title=section['title'].split(' · ',1)[-1]
    output=[plain(f'Chapter {chapter_number}: {title}. {section["section"]}.',math,pronunciations)]
    if 'practice' in section['section'].lower() or 'diagnostic' in section['section'].lower():
        output.append('This section includes questions and worked answers. Pause when prompted to try each question before listening to its solution.')
    paragraph=[];code=[];in_code=False;table_header=None
    def flush():
        if paragraph:
            output.append(plain(' '.join(paragraph),math,pronunciations));paragraph.clear()
    for line in raw.splitlines():
        if line.startswith('```'):
            flush()
            if in_code:
                key=sha('\n'.join(code))
                if key not in blocks:raise ValueError('New code block requires an authored explanation: '+section['id']+' '+key)
                output.append(plain(blocks[key]['spoken'],math,pronunciations));code=[]
            in_code=not in_code;continue
        if in_code:code.append(line);continue
        if re.match(r'^#{1,6} ',line):flush();continue
        if not line.strip():flush();table_header=None;continue
        if line.startswith('|'):
            flush();cells=[c.strip() for c in re.split(r'\|(?![^`]*`(?:(?:[^`]*`){2})*[^`]*$)',line.strip().strip('|'))]
            # This course's tables contain no unescaped pipe in a code cell.
            if all(re.fullmatch(r':?-+:?',c) for c in cells):continue
            if table_header is None:table_header=cells;continue
            output.append(plain('Table row. '+'. '.join(f'{label}: {value}' for label,value in zip(table_header,cells))+'.',math,pronunciations));continue
        if line.startswith('- '):
            flush();output.append(plain(line[2:],math,pronunciations));continue
        if re.match(r'^\d+\.\s',line):
            flush();line=re.sub(r'^(\d+)\.\s',r'Question \1. ',line)
            line=re.sub(r'\b(?:Example solution|Solution|Answer):', 'Pause now and try your answer. When you are ready, continue. Solution:',line)
            output.append(plain(line,math,pronunciations));continue
        if line.startswith('Exercises:'):
            flush();line=line.replace('Solution:','Pause to try this exercise. Then continue for the solution:')
            output.append(plain(line,math,pronunciations));continue
        paragraph.append(line)
    flush()
    if in_code:raise ValueError('Unclosed code block: '+section['id'])
    text='\n\n'.join(part for part in output if part)+'\n'
    if re.search(r'`|```|https?://',text):raise ValueError('Unspoken markup/URL remains: '+section['id'])
    return text


def desired():
    math=read_json('audio/speech-math.json');pronunciations=read_json('audio/pronunciations.json');blocks=read_json('audio/code-narration.json');editorial=read_json('audio/editorial.json')
    result=[]
    for section in sections():
        text=transcript(section,math,pronunciations,blocks,editorial)
        entry={k:v for k,v in section.items() if k!='raw'}
        entry.update(transcript='audio/narration/'+section['id']+'.txt',transcript_sha256=sha(text),words=len(text.split()),adapter=ADAPTER_VERSION)
        entry['generation_key']=sha(json.dumps({'transcript_sha256':entry['transcript_sha256'],'settings':SETTINGS},sort_keys=True))
        entry['src']='audio/sections/'+section['id']+'-'+entry['generation_key'][:12]+'.m4a'
        entry['text']=text
        result.append(entry)
    return result


def sync():
    entries=desired()
    for entry in entries:
        path=ROOT/entry['transcript'];path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists() or path.read_text()!=entry['text']:path.write_text(entry['text'])
    public=[{k:v for k,v in entry.items() if k!='text'} for entry in entries]
    (ROOT/'audio/sections.json').write_text(json.dumps({'version':1,'settings':SETTINGS,'sections':public},indent=2,ensure_ascii=False)+'\n')
    return public


def coverage(require_audio=True):
    errors=[];expected=desired();path=ROOT/'audio/sections.json'
    if not path.exists():return ['Missing audio section inventory; run audio.py sync']
    actual=json.loads(path.read_text())
    public=[{k:v for k,v in entry.items() if k!='text'} for entry in expected]
    if actual.get('sections')!=public or actual.get('settings')!=SETTINGS:errors.append('Section inventory is stale; run audio.py sync')
    recordings=read_json('audio/recordings.json') if (ROOT/'audio/recordings.json').exists() else {}
    for entry in expected:
        transcript_path=ROOT/entry['transcript']
        if not transcript_path.exists() or sha(transcript_path.read_bytes())!=entry['transcript_sha256']:errors.append('Missing/stale transcript: '+entry['id'])
        if not require_audio:continue
        recording=recordings.get(entry['id'])
        if not recording or recording.get('generation_key')!=entry['generation_key']:errors.append('Missing/stale recording: '+entry['id']);continue
        audio_path=ROOT/entry['src']
        if not audio_path.exists() or sha(audio_path.read_bytes())!=recording.get('sha256'):errors.append('Missing/corrupt recording: '+entry['id'])
        if recording.get('qc_pass') is not True:errors.append('Unvalidated recording: '+entry['id'])
    extras=set(recordings)-{e['id'] for e in expected}
    if extras:errors.append('Orphaned recording entries: '+', '.join(sorted(extras)))
    return errors
