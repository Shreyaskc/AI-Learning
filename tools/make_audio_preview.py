"""Assemble a local review player; keep restricted personal recordings outside Git."""
import argparse
import copy
import html
from pathlib import Path
from urllib.parse import quote
import build
import listen


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--sample',type=Path,required=True)
    args=parser.parse_args()
    sample=args.sample.resolve()
    if sample.is_relative_to(build.ROOT): raise SystemExit('Keep the private System Voice sample outside the public repository.')
    if not sample.is_file() or sample.stat().st_size<10000: raise SystemExit('A nonempty generated recording is required.')
    items=copy.deepcopy(listen.tracks(build.LESSONS))
    for item in items:
        item['lesson']='https://shreyaskc.github.io/AI-Learning/'+item['lesson']
        if item['id']=='01-foundations-core':
            item['src']=quote(sample.name)
            item['status']='Private local voice preview; not a public recording'
    body=listen.page(items)
    body=body.replace('href="audio/ATTRIBUTION.md"','href="https://github.com/Shreyaskc/AI-Learning/blob/audio/podcast-player/audio/ATTRIBUTION.md"')
    body=body.replace('<script src="podcast.js" defer></script>','<script>'+ (build.ROOT/'podcast.js').read_text()+'</script>')
    output=sample.parent/'listen-preview.html'
    content='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local Foundations audio preview</title><style>'+(build.ROOT/'style.css').read_text()+'</style></head><body><main id="main">'+body+'<p>Local review preview. <a download href="'+html.escape(quote(sample.name),quote=True)+'">Download local sample</a></p></main></body></html>'
    output.write_text(content)
    print(output)


if __name__=='__main__':main()
