"""Build the full section playlist and accessible listening surface."""
import html
import hashlib
import json
import narration
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sample_tracks(lessons):
    recordings=json.loads((ROOT/'audio/catalog.json').read_text())
    result=[]
    for lesson in lessons:
        identity=lesson.stem+'-core'
        transcript=ROOT/'audio/transcripts'/f'{identity}.txt'
        recording=recordings.get(identity)
        if recording:
            asset=(ROOT/recording['src']).resolve()
            if not asset.is_relative_to(ROOT/'audio') or not asset.is_file() or not transcript.exists() or not recording.get('redistribution_basis'):
                raise ValueError('Published recording needs local audio asset, matching transcript and redistribution basis: '+identity)
            if hashlib.sha256(asset.read_bytes()).hexdigest()!=recording.get('sha256') or hashlib.sha256(transcript.read_bytes()).hexdigest()!=recording.get('transcript_sha256'):
                raise ValueError('Recording/transcript fingerprints must match: '+identity)
        result.append(dict(id=identity, chapter=lesson.stem, title=lesson.read_text().splitlines()[0].removeprefix('# '),
                           section='Core concepts sample' if transcript.exists() else 'Chapter narration',
                           src=recording['src'] if recording else None, kind=recording.get('kind','chapter') if recording else None, status=('Sample · voice/pacing review' if recording.get('kind')=='sample' else 'Recording available') if recording else ('Local voice sample ready for review' if transcript.exists() else 'Not generated'),
                           transcript=transcript.read_text() if transcript.exists() else '',
                           lesson='course/'+lesson.stem+'.html'))
    unknown=set(recordings)-{q['id'] for q in result}
    if unknown:raise ValueError('Unknown recording identities: '+', '.join(sorted(unknown)))
    return result


def tracks(lessons):
    if not (ROOT/'audio/sections.json').exists(): return sample_tracks(lessons)
    inventory=json.loads((ROOT/'audio/sections.json').read_text())['sections']
    recordings=json.loads((ROOT/'audio/recordings.json').read_text()) if (ROOT/'audio/recordings.json').exists() else {}
    result=[]
    for entry in inventory:
        recording=recordings.get(entry['id'],{})
        ready=recording.get('qc_pass') is True and recording.get('generation_key')==entry['generation_key']
        result.append(dict(id=entry['id'],chapter=entry['chapter'],title=entry['title'],section=entry['section'],
                           src=entry['src'] if ready else None,revision=entry['generation_key'],kind='section',
                           status='Available' if ready else 'Recording pending',
                           seconds=recording.get('duration_seconds',0) if ready else 0,
                           transcript=(ROOT/entry['transcript']).read_text(),transcript_path=entry['transcript'],
                           lesson='course/'+entry['chapter']+'.html#'+entry['anchor'],
                           aliases=['01-foundations-core'] if entry['id']=='01-foundations--from-rules-to-learned-functions' else []))
    return result


def duration(seconds):
    value=int(seconds)
    return str(value//60)+':'+str(value%60).zfill(2)


def safe_json(value):
    return json.dumps(value,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')


def page(items):
    chapters=list(dict.fromkeys(q['chapter'] for q in items))
    options=[];chapter_options=[];fallback=[]
    for chapter in chapters:
        group=[q for q in items if q['chapter']==chapter]
        chapter_options.append('<option value="'+chapter+'">'+html.escape(group[0]['title'])+'</option>')
        options.append('<optgroup label="'+html.escape(group[0]['title'],quote=True)+'">')
        for q in group:
            options.append('<option value="'+q['id']+'">'+html.escape(q['section']+' · '+(duration(q['seconds']) if q.get('seconds') else q['status']))+'</option>')
        options.append('</optgroup>')
        fallback.append('<details><summary>'+html.escape(group[0]['title'])+'</summary>')
        for q in group:
            link='<a href="'+html.escape(q['src'],quote=True)+'" download>Download audio</a> · ' if q['src'] else ''
            fallback.append('<p><strong>'+html.escape(q['section'])+'</strong> · '+link+'<a href="'+html.escape(q.get('transcript_path',q['lesson']),quote=True)+'">Read transcript</a> · <a href="'+q['lesson']+'">Lesson</a></p>')
        fallback.append('</details>')
    available=sum(bool(q['src']) for q in items)
    complete=sum(all(q['src'] for q in items if q['chapter']==chapter) for chapter in chapters)
    seconds=sum(q.get('seconds',0) for q in items)
    hours=int(seconds//3600);minutes=int(seconds%3600//60)
    summary=f'{available} of {len(items)} sections available across {complete} of {len(chapters)} complete chapters · {hours}h {minutes}m of narration'
    return '''<h1>Listen to AI Fluency</h1><p class="lead">Section-by-section explanations, worked examples and practice, in course order.</p><p id="audio-coverage">'''+summary+'''. <a href="audio/coverage.html">View section coverage</a>.</p>
<p>Choose a chapter or section, then Play or Resume. Opt into continuous playback to follow the course like a podcast. Reopening stays silent. Pause or Stop cancels the current run; choosing a section loads it paused. The player stops at any unavailable recording instead of silently skipping it.</p>
<p class="small">Practice recordings include worked answers. Pause at the spoken cue to try the question first. Narration explains the written material and notation; keep the lesson open for code, exact commands and visual arrays.</p>
<div id="listen-interactive" hidden><label for="audio-chapter">Jump to chapter</label><select id="audio-chapter">'''+''.join(chapter_options)+'''</select><label for="audio-track">Section</label><select id="audio-track">'''+''.join(options)+'''</select>
<h2 id="audio-title"></h2><p id="audio-status" role="status" aria-live="polite"></p><p id="audio-storage" class="small"></p>
<audio id="course-audio" controls preload="none" aria-label="Course narration"></audio>
<div class="audio-actions"><button id="audio-play" type="button">Play</button><button id="audio-resume" type="button">Resume</button><button id="audio-pause" type="button">Pause</button><button id="audio-stop" type="button">Stop</button><button id="audio-previous" type="button">Previous section (paused)</button><button id="audio-next" type="button">Next section (paused)</button></div>
<div class="audio-settings"><label for="audio-speed">Speed</label><select id="audio-speed"><option id="audio-custom-speed" hidden value="">Current speed</option><option value="0.5">0.5×</option><option value="0.75">0.75×</option><option value="1">1×</option><option value="1.25">1.25×</option><option value="1.5">1.5×</option><option value="1.75">1.75×</option><option value="2">2×</option><option value="2.5">2.5×</option><option value="3">3×</option></select><label><input id="audio-continue" type="checkbox"> Continue through sections and chapters</label></div>
<p id="audio-position"></p><p><a id="audio-lesson" target="_blank" rel="noopener">Read this section (new tab) →</a> <a id="audio-download" hidden download>Download recording</a></p>
<details><summary>Matching transcript</summary><div id="audio-transcript"></div></details>
<details><summary>Use your own local recording</summary><p>Attach a personal recording to the selected section for this tab only. It is not uploaded. After reopening, choose the file again to resume its saved position.</p><label for="audio-file">Local audio file</label><input id="audio-file" type="file" accept="audio/*"></details></div>
<noscript><p>Continuous playback and resume require JavaScript. Download each section and read its matching transcript below.</p>'''+''.join(fallback)+'''</noscript>
<p class="small">Synthetic narration: Kokoro-82M v1.0, af_heart. Original AI Fluency course material. <a href="audio/ATTRIBUTION.md">Narration credit</a>.</p><p class="small">Selected section, per-section position, speed and continuous-play preference are saved in this browser when storage is available. Chapter jumps return to that chapter's last selected section. No cross-device sync. Reopening never starts sound. Changed recordings restart at zero to avoid resuming at the wrong point. Study checkboxes and practice ratings remain separate. Background and lock-screen playback depend on your browser and operating system.</p>
<script id="audio-data" type="application/json">'''+safe_json(items)+'''</script><script src="podcast.js" defer></script>'''


def coverage_page(items):
    ready=sum(bool(q['src']) for q in items)
    rows=[]
    for q in items:
        rows.append('<tr><td>'+html.escape(q['title'])+'</td><td><a href="../listen.html?track='+q['id']+'">'+html.escape(q['section'])+'</a></td><td>'+('Validated' if q['src'] else 'Missing')+'</td><td>'+duration(q.get('seconds',0))+'</td><td><a href="../'+q['transcript_path']+'">Transcript</a> · <a href="../'+q['lesson']+'">Source section</a></td></tr>')
    return '<h1>Audio coverage</h1><p>'+str(ready)+' of '+str(len(items))+' numbered-course sections have current, validated recordings. Every chapter introduction and every heading section is inventoried. Glossary and other reference pages are written references, outside this episode sequence.</p><p>Validation checks source/transcript/recording hashes, pronunciation text coverage, nonempty phonemes, signal duration, long silence and full audio decoding. These checks do not establish flawless pronunciation or device playback; listen and report an issue using the section name.</p><div class="table-wrap" role="region" tabindex="0" aria-label="Section audio coverage"><table><tr><th scope="col">Chapter</th><th scope="col">Section</th><th scope="col">Status</th><th scope="col">Duration</th><th scope="col">Evidence</th></tr>'+''.join(rows)+'</table></div>'
