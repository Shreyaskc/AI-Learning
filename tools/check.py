"""Validate generated pages, local links/fragments, syntax and lesson contracts."""
import ast
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import build

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
if len(build.LESSONS)!=20:errors.append('expected 20 numbered lessons')
for path in build.LESSONS[1:]:
    text=path.read_text().lower()
    for required in ['prerequisite','outcomes:','solution','interview']:
        if required not in text:errors.append(f'missing lesson element {required}: {path.name}')
if errors:
    print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(parsers)} HTML pages; local links/anchors, generated consistency, lesson elements, Python syntax')
