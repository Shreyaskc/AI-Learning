"""Validate generated pages, local links/fragments, syntax and lesson contracts."""
import hashlib
import json
import ast
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs
import build
import listen
import narration

ROOT = build.ROOT
errors = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.targets=[]; self.ids=set(); self.current=0; self.has_main=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:errors.append('duplicate ID: '+attrs['id'])
            self.ids.add(attrs['id'])
        if tag=='main':self.has_main=True
        if attrs.get('aria-current')=='page':self.current+=1
        for name in ('href','src'):
            if name in attrs:self.targets.append(attrs[name])


expected=build.outputs()
for path,content in expected.items():
    if not path.exists() or path.read_text()!=content:errors.append(f'stale generated output: {path.relative_to(ROOT)}')
audio_items=listen.tracks(build.LESSONS)
audio_ids={q['id'] for q in audio_items}|{alias for q in audio_items for alias in q.get('aliases',[])}
audio_chapters={q['chapter'] for q in audio_items}
parsers={}
for path in ROOT.rglob('*.html'):
    if '.git' in path.parts:continue
    parser=Page();parser.feed(path.read_text());parsers[path]=parser
    if not parser.has_main:errors.append(f'main landmark absent: {path}')
    if path.parent==ROOT/'course' and parser.current!=1:errors.append(f'current lesson absent: {path}')
for path,parser in parsers.items():
    for target in parser.targets:
        url=urlsplit(target)
        if url.scheme or url.netloc:continue
        resolved=(path.parent/unquote(url.path)).resolve() if url.path else path
        if not resolved.is_relative_to(ROOT):errors.append(f'link escapes repo: {path}: {target}');continue
        if not resolved.exists():errors.append(f'broken link: {path.relative_to(ROOT)}: {target}');continue
        if resolved == ROOT/'listen.html' and url.query:
            params=parse_qs(url.query)
            if params.get('track',[None])[0] is not None and params['track'][0] not in audio_ids:errors.append('unknown audio section: '+target)
            if params.get('chapter',[None])[0] is not None and params['chapter'][0] not in audio_chapters:errors.append('unknown audio chapter: '+target)
        if url.fragment and resolved == ROOT/'practice.html' and '=' in url.fragment:
            import practice
            bank=practice.questions(build.LESSONS); by_id={q['id']:q for q in bank}
            params=parse_qs(url.fragment)
            topic=params.get('topic',['all'])[0]; question=params.get('q',[None])[0]
            if topic!='all' and topic not in {q['topic'] for q in bank}:errors.append('unknown practice topic: '+target)
            if question and (question not in by_id or (topic!='all' and by_id[question]['topic']!=topic)):errors.append('unknown/mismatched practice question: '+target)
            continue
        if url.fragment and resolved in parsers and unquote(url.fragment) not in parsers[resolved].ids:
            errors.append(f'broken anchor: {path.relative_to(ROOT)}: {target}')
for path in (ROOT/'course').glob('*.md'):
    text=path.read_text()
    if text.count('```')%2:errors.append(f'unbalanced fences: {path.name}')
    if re.search(r'\b(TODO|TBD|PLACEHOLDER)\b',text):errors.append(f'placeholder: {path.name}')
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
        url=urlsplit(target)
        if not url.scheme and not url.netloc and not (path.parent/unquote(url.path)).exists():
            errors.append(f'broken Markdown link: {path.name}: {target}')
for path in list((ROOT/'labs').glob('*.py'))+list((ROOT/'tools').glob('*.py')):
    try:ast.parse(path.read_text(),filename=str(path))
    except SyntaxError as exc:errors.append(str(exc))
if [int(path.stem[:2]) for path in build.LESSONS]!=list(range(len(build.LESSONS))):errors.append('numbered chapters must be contiguous from 00')
errors.extend(narration.coverage())
for path in build.LESSONS[1:]:
    text=path.read_text().lower()
    for required in ['prerequisite','outcomes:','solution','interview']:
        if required not in text:errors.append(f'missing lesson element {required}: {path.name}')
evidence=ROOT/'review/evidence/model-comparison.json'
if evidence.exists():
    report=json.loads(evidence.read_text())
    actual=hashlib.sha256((ROOT/'labs/model_comparison.py').read_bytes()).hexdigest()
    if report.get('implementation_sha256')!=actual:errors.append('model evidence source fingerprint is stale')
if errors:
    print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(parsers)} HTML pages; local links/anchors, generated consistency, lesson elements, Python syntax')
