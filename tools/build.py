"""Build the dependency-free static reader from the repository's Markdown subset."""
import argparse
import html
import re
import practice
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / 'course'
LESSONS = sorted(COURSE.glob('[0-9][0-9]-*.md'))
EXTRAS = [COURSE / name for name in ['glossary.md', 'coverage.md', 'module-crosswalk.md', 'sources.md']]


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def inline(raw):
    pieces = []
    # Preserve inline code from other formatting substitutions.
    for i, piece in enumerate(re.split(r'(`[^`]+`)', raw)):
        if piece.startswith('`') and piece.endswith('`'):
            pieces.append('<code>'+html.escape(piece[1:-1])+'</code>')
            continue
        text = html.escape(piece)
        def link(match):
            label, target = match.groups()
            # Repository-authored links only; do not enable executable URL schemes.
            if re.match(r'(?i)(javascript|data|vbscript):', target):
                raise ValueError('unsupported link target')
            if target.endswith('.md') and not target.startswith(('http:', 'https:')):
                target = target[:-3]+'.html'
            return '<a href="'+target+'">'+label+'</a>'
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        pieces.append(text)
    return ''.join(pieces)


def render(markdown, lesson=None):
    lines = markdown.splitlines()
    out, paragraph, code = [], [], []
    in_code = False
    def flush():
        if paragraph:
            out.append('<p>'+inline(' '.join(paragraph))+'</p>')
            paragraph.clear()
    i=0
    while i < len(lines):
        line=lines[i]
        if line.startswith('```'):
            flush()
            if in_code:
                out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>')
                code=[]
            in_code=not in_code
            i+=1; continue
        if in_code:
            code.append(line); i+=1; continue
        if not line.strip():
            flush(); i+=1; continue
        heading=re.match(r'^(#{1,6}) (.+)$',line)
        if heading:
            flush(); level=len(heading[1]); title=heading[2]
            out.append(f'<h{level} id="{slug(title)}">{inline(title)}</h{level}>')
            i+=1; continue
        if line.startswith('|'):
            flush(); rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                row=[cell.strip() for cell in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', cell) for cell in row):
                    rows.append(row)
                i+=1
            out.append('<div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable reference table"><table>')
            for index,row in enumerate(rows):
                tag='th' if index==0 else 'td'
                scope=' scope="col"' if index==0 else ''
                out.append('<tr>'+''.join(f'<{tag}{scope}>{inline(cell)}</{tag}>' for cell in row)+'</tr>')
            out.append('</table></div>'); continue
        bullet=re.match(r'^- (.+)',line)
        if bullet:
            flush(); out.append('<ul>')
            while i<len(lines) and lines[i].startswith('- '):
                out.append('<li>'+inline(lines[i][2:])+'</li>'); i+=1
            out.append('</ul>'); continue
        if lesson and line.startswith('Exercises:'):
            flush()
            pieces=re.split(r'(?:^|\s+)\((\d+)\)\s+',line.removeprefix('Exercises:').strip())
            out.append('<div class="worked-exercises"><h3>More worked practice</h3>')
            for number,exercise in zip(pieces[1::2],pieces[2::2]):
                pair=re.split(r'\s+Solution:\s*',exercise,maxsplit=1)
                if len(pair)==2:
                    out.append('<details class="worked-exercise inline-question"><summary>'+inline(pair[0])+'</summary><div class="inline-solution"><p><strong>Answer and reasoning</strong></p><p>'+inline(pair[1])+'</p></div></details>')
                else:out.append('<p>'+inline(number+'. '+exercise)+'</p>')
            out.append('</div>');i+=1;continue
        question = practice.QUESTION.match(line) if lesson else None
        if question:
            flush()
            prompt, solution = question.groups()
            identity = practice.questions([lesson])
            item = next(q for q in identity if q['question'] == prompt)
            out.append('<details class="inline-question"><summary>'+inline(prompt)+'</summary><div class="inline-solution"><p><strong>Answer and reasoning</strong></p><p>'+inline(solution)+'</p><a href="../practice.html#topic='+lesson.stem+'&amp;q='+item['id']+'">Practice this question →</a></div></details>')
            i+=1; continue
        paragraph.append(line); i+=1
    flush()
    if in_code: raise ValueError('unclosed code fence')
    return '\n'.join(out)


def title(path):
    return path.read_text().splitlines()[0].removeprefix('# ')


def layout(current, body, root=False, title_override=None):
    prefix='' if root else '../'
    nav=''.join(f'<a data-lesson="{p.stem}" href="{prefix}course/{p.stem}.html"'+
                (' aria-current="page"' if p==current else '')+'>'+html.escape(title(p))+'</a>'
                for p in LESSONS+EXTRAS)
    page_title=title_override or (title(current) if current else 'AI Fluency · From first principles to AI systems')
    learn_current=' aria-current="true"' if not title_override else ''
    practice_current=' aria-current="true"' if title_override else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A self-study AI course with worked mathematics, offline Python labs and practical system design.">
<title>{html.escape(page_title)} · AI Fluency</title><link rel="stylesheet" href="{prefix}style.css">
<script src="{prefix}app.js" defer></script></head>
<body data-chapter="{current.stem if current else ''}"><a class="skip" href="#main">Skip to lesson</a>
<header><a class="brand" href="{prefix}index.html">AI / FLUENCY</a><nav class="mode-nav" aria-label="Learning mode"><a href="{prefix}index.html"{learn_current}>Learn</a><a href="{prefix}practice.html"{practice_current}>Practice Q&amp;A</a></nav><button id="menu" aria-expanded="false" aria-controls="sidebar">Lessons</button></header>
<div class="layout"><aside id="sidebar"><label for="search">Find a lesson or reference</label><input id="search" type="search" placeholder="Try transformers or security">
<p id="progress" aria-live="polite">Study progress is stored in this browser.</p><nav aria-label="Course lessons">{nav}</nav><p class="small">Checkboxes track study, not assessed mastery.</p></aside>
<main id="main" tabindex="-1">{body}<footer>Original explanations · Synthetic examples · <a href="{prefix}course/coverage.html">Evidence and remaining depth</a> · <a href="{prefix}README.md">Repository guide</a></footer></main></div></body></html>'''


def outputs():
    generated={}
    for p in LESSONS+EXTRAS:
        before=''
        if p in LESSONS:
            before=f'<div class="lesson-meta">SELF-STUDY / CORE COURSE <label><input id="completed" type="checkbox" data-id="{p.stem}"> Studied this lesson</label></div>'
        if p in LESSONS:
            items=practice.questions([p])
            if items:
                before+=f'<a class="topic-practice" href="../practice.html#topic={p.stem}">Practice this topic · {len(items)} questions →</a>'
        body=before+render(p.read_text(), lesson=p if p in LESSONS else None)
        if p in LESSONS:
            i=LESSONS.index(p)
            prev=f'<a rel="prev" href="{LESSONS[i-1].stem}.html">← {html.escape(title(LESSONS[i-1]))}</a>' if i else '<a href="../index.html">← Course home</a>'
            nxt=f'<a rel="next" href="{LESSONS[i+1].stem}.html">{html.escape(title(LESSONS[i+1]))} →</a>' if i+1<len(LESSONS) else '<a href="coverage.html">Coverage and next stage →</a>'
            body+=f'<nav class="paging" aria-label="Lesson navigation">{prev}{nxt}</nav>'
        generated[p.with_suffix('.html')]=layout(p,body)
    cards=''.join(f'<a class="card" href="course/{p.stem}.html"><span>{p.stem[:2]}</span><h2>{html.escape(title(p).split(" · ",1)[-1])}</h2><p>{html.escape(next((line for line in p.read_text().splitlines()[1:] if line.strip()),""))}</p></a>' for p in LESSONS)
    home=f'''<div class="eyebrow">A COURSE FOR SOFTWARE ENGINEERS</div><h1>Build your understanding<br>from the ground up.</h1><p class="lead">Learn what models learn, how they fail, and how to build AI systems you can explain and defend.</p><div class="home-actions"><a class="start" href="course/01-foundations.html">Start learning →</a><a class="start secondary" href="practice.html">Practice Q&amp;A →</a></div><p class="home-diagnostic">Already familiar with the basics? <a href="practice.html#topic=00-start">Try the 10-question diagnostic</a>. New here? Start with the first lesson; the diagnostic is optional.</p><div class="stats"><span><strong>20</strong> authored chapters</span><span><strong>14</strong> offline Python labs</span><span><strong>4</strong> capstone assignments</span></div><p>Start with no AI background. Follow the mathematics and worked examples, run tiny inspectable implementations, then practice evaluation, production design and interview defenses. Read the <a href="course/coverage.html">coverage ledger</a>: specialist topics have different depths and production projects remain assignments.</p><section class="cards" aria-label="Ordered curriculum">{cards}</section>'''
    generated[ROOT/'index.html']=layout(None,home,root=True)
    generated[ROOT/'practice.html']=layout(None,practice.page(practice.questions(LESSONS),inline),root=True,title_override="Practice Q&A")
    return generated


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    stale=[]
    for path,content in outputs().items():
        if args.check:
            if not path.exists() or path.read_text()!=content: stale.append(str(path.relative_to(ROOT)))
        else:path.write_text(content)
    if stale: raise SystemExit('Stale generated pages: '+', '.join(stale))
    print(f'{"Checked" if args.check else "Built"} {len(LESSONS)+len(EXTRAS)+2} static pages')


if __name__=='__main__':main()
