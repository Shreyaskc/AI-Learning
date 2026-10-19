"""Build the honest, preview-stage audio playlist and accessible listening surface."""
import html
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracks(lessons):
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


def safe_json(value):
    return json.dumps(value,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')


def page(items):
    options=''.join('<option value="'+q['id']+'">'+html.escape(q['title']+' — '+q['status'])+'</option>' for q in items)
    transcripts=''.join(('<p><a href="'+html.escape(q['src'],quote=True)+'" download>Download section recording</a></p>' if q['src'] else '')+'<details><summary>'+html.escape(q['title']+' — sample transcript')+'</summary><p>'+html.escape(q['transcript']).replace('\n\n','</p><p>')+'</p></details>' for q in items if q['transcript'])
    published=sum(bool(q['src']) and q.get('kind')=='sample' for q in items)
    full=sum(bool(q['src']) and q.get('kind')=='chapter' for q in items)
    return ('''<h1>Listen to AI Fluency</h1><p class="lead">Audio preview: review one Foundations section before we expand narration. Section samples available: AUDIO_COUNT. Full chapter recordings: FULL_COUNT of 20. Full course narration is not ready yet.</p>
<p>Choose a chapter, then Play or Resume. “Continue to next chapter” applies after you start playback; reopening this page never starts sound. Pause or Stop cancels the current continuous run. A chapter change loads it paused. The playlist stops at missing recordings so it does not silently skip course content.</p>
<div id="listen-interactive" hidden><label for="audio-track">Chapter / section</label><select id="audio-track">'''+options+'''</select>
<h2 id="audio-title"></h2><p id="audio-status" role="status" aria-live="polite"></p><p id="audio-storage" class="small"></p>
<audio id="course-audio" controls preload="none" aria-label="Course narration"></audio>
<div class="audio-actions"><button id="audio-play" type="button">Play</button><button id="audio-resume" type="button">Resume</button><button id="audio-pause" type="button">Pause</button><button id="audio-stop" type="button">Stop</button><button id="audio-next" type="button">Next chapter (paused)</button></div>
<div class="audio-settings"><label for="audio-speed">Speed</label><select id="audio-speed"><option value="0.75">0.75×</option><option value="1">1×</option><option value="1.25">1.25×</option><option value="1.5">1.5×</option><option value="1.75">1.75×</option><option value="2">2×</option></select><label><input id="audio-continue" type="checkbox"> Continue to next chapter</label></div>
<p id="audio-position"></p><p><a id="audio-lesson" target="_blank" rel="noopener">Read this lesson (new tab) →</a> <a id="audio-download" hidden download>Download recording</a></p>
<details><summary>Matching transcript</summary><div id="audio-transcript"></div></details>
<details><summary>Use a local recording for private preview</summary><p>For the selected section, choose a recording from your device. It stays in this browser tab and is not uploaded. After reopening, choose the file again to resume its saved position. The earlier restricted System Voice preview stays private; the Kokoro sample is provided for review.</p><label for="audio-file">Local audio file</label><input id="audio-file" type="file" accept="audio/*"></details></div>
<noscript><p>Playlist and resume behavior require JavaScript. Download the available section sample and read its matching transcript below.</p>'''+transcripts+'''</noscript>
<p class="small">Synthetic narration sample: Kokoro-82M v1.0, af_heart. Original AI Fluency course script. <a href="audio/ATTRIBUTION.md">Narration credit and sources</a>.</p><p class="small">Position, selected section, speed and continuous-play preference are stored on this browser only when storage is available. No cross-device sync. Clearing site data removes them. Existing study checkboxes and practice ratings use separate storage. Background and lock-screen playback depend on your browser and operating system.</p>
<script id="audio-data" type="application/json">'''+safe_json(items)+'''</script><script src="podcast.js" defer></script>''').replace('AUDIO_COUNT',str(published)).replace('FULL_COUNT',str(full))
