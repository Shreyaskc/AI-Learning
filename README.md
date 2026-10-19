# AI Fluency — learn, build, explain

**Live course: [shreyaskc.github.io/AI-Learning](https://shreyaskc.github.io/AI-Learning/)**

A self-study course for software engineers starting AI from zero, with a path toward ML, LLM application and senior AI-platform interviews. Twenty chapters combine original explanations, worked mathematics, 69 practice questions, fourteen offline Python labs and four capstone assignments. Specialist depth varies; the [coverage ledger](https://shreyaskc.github.io/AI-Learning/course/coverage.html) explains the boundaries. No course guarantees interview results.

## Start and navigate

1. **New to AI:** [start with chapter 01](https://shreyaskc.github.io/AI-Learning/course/01-foundations.html). No diagnostic, account or installation is required. Follow the Previous/Next links in order.
2. **Choose a path:** [chapter 00](https://shreyaskc.github.io/AI-Learning/course/00-start.html) explains prerequisites, the optional diagnostic, three learning paths and spaced review. On mobile, use **Lessons** to open the chapter menu; search filters chapter/reference titles.
3. **Learn vocabulary:** bold technical terms open layered definitions: technical meaning, plain explanation, an analogy with its limits and an example. The [glossary](https://shreyaskc.github.io/AI-Learning/course/glossary.html) has all 85 entries and links back to lessons.
4. **Practice:** [Practice Q&A](https://shreyaskc.github.io/AI-Learning/practice.html) presents one question at a time. Try it, reveal the answer, then choose Got it / Partly / Need practice. Optional notes stay in the current session. Lesson answer disclosures start closed.
5. **Listen:** [Listen](https://shreyaskc.github.io/AI-Learning/listen.html) contains narration for every introduction and section in the 20 numbered chapters. Use each lesson's **Listen to this section** link to start at that point. Chapter/section selectors, transcripts, downloads, speed and previous/next controls are available. The [audio coverage table](https://shreyaskc.github.io/AI-Learning/audio/coverage.html) lists every section and its recording.
6. **Build and defend:** run the linked labs when you have a computer, change an assumption and explain the result. Finish with [projects and mock interviews](https://shreyaskc.github.io/AI-Learning/course/19-projects-interviews.html). A checked box is study progress, not assessed mastery.

### Course sequence

- **00–04:** orientation, prediction tasks, mathematical/data bridge, probability and optimization.
- **05–09:** classical ML, evaluation, neural networks, transformers and LLM training/adaptation.
- **10–13:** retrieval/RAG, agents/tools/context/memory/graphs, multimodal concepts and data/feature platforms.
- **14–16:** compute and serving, operations, security/privacy/responsible AI.
- **17–19:** experiments/research, domain electives, projects and interview defenses.

The [29-module crosswalk](course/module-crosswalk.md) audits the previous course's topic coverage. [Primary sources](course/sources.md) separate mathematical mechanisms, empirical findings and design judgments. The examples use invented data, not employer material or claimed personal achievements.

## Audio and resume

Narration uses **Kokoro-82M v1.0, af_heart** with original course scripts. It explains the full section material, including worked numbers, rather than giving chapter summaries. Formulas are expanded into spoken notation; code blocks have authored explanations. Keep the written section open for exact commands and visual arrays. Practice episodes include solutions and give a pause-to-try cue.

Press **Play** or **Resume** to begin. Turn on **Continue through sections and chapters** to follow the whole course like a podcast. One media element stays in use across transitions. Pause/Stop cancels the current run; Stop also resets the current position. Manually choosing a section loads it paused. The final section stops; a missing recording stops rather than silently skipping content. Browser playback restrictions produce a tap-to-continue message.

The same browser saves the selected section, per-section position, speed, continuous-play preference and last selected section in each chapter. Reopening stays silent and offers Resume; a changed recording restarts at zero. Progress is flushed on pause/seek and page lifecycle changes, and otherwise about every five seconds. Abrupt closure can lose the latest few seconds. Storage denial, clearing site data, private browsing and browser eviction can prevent persistence. There is **no cross-device sync**, and file:// storage behavior varies: use the live site or local HTTP server for a stable origin.

Lesson checkboxes, practice ratings/question resume and audio position use separate browser records. Text scroll position and free-text notes are not durable progress. Native/Media Session controls work where supported. Uninterrupted iOS/background/locked-screen playback is **not guaranteed or claimed as tested**. No account, analytics or cloud speech generation is required to listen; media downloads are ordinary static files from the course site, with no whole-course prefetch.

[Narration credit and licensing basis](audio/ATTRIBUTION.md) · [Generation/QC evidence](review/AUDIO-COVERAGE.md). The earlier restricted Apple System Voice test recording is excluded from Git, Pages and Library.

## Courses

- [AI Fluency — live app](https://shreyaskc.github.io/AI-Learning/) · [repository](https://github.com/Shreyaskc/AI-Learning)
- [System Design Fluency — live app](https://shreyaskc.github.io/system-design-fluency/) · [repository](https://github.com/Shreyaskc/system-design-fluency)
- [DSA Fluency — live app](https://shreyaskc.github.io/dsa-fluency/) · [repository](https://github.com/Shreyaskc/dsa-fluency)

- [Principal Leadership Fluency — live app](https://shreyaskc.github.io/principal-leadership-fluency/) · [repository](https://github.com/Shreyaskc/principal-leadership-fluency)
- [Production Platforms Fluency — live app](https://shreyaskc.github.io/production-platforms-fluency/) · [repository](https://github.com/Shreyaskc/production-platforms-fluency)
- [Practical Engineering Fluency — live app](https://shreyaskc.github.io/practical-engineering-fluency/) · [repository](https://github.com/Shreyaskc/practical-engineering-fluency)

The app's **Courses** area uses the same links. All six course URLs are verified. The small course list can accommodate later courses once they exist and have verified URLs.

## Run locally

Reading, building the static reader and running the educational labs need Python 3.10+; JavaScript checks also need Node. They need no API keys, external Python packages, GPU or model downloads. Optional **audio generation** has its own dependency setup below; prerecorded listening does not.

```sh
python3 tools/build.py
python3 tools/check.py
python3 -m unittest discover -s tools -p 'test_*.py'
python3 -m unittest discover -s labs -p 'test_*.py'
node tools/test_practice.js
node tools/test_terms.js
node tools/test_podcast.js
node tools/test_reader.js
python3 tools/run_labs.py
python3 -m http.server 8000
```

Visit `http://localhost:8000`. Opening `index.html` directly also supports reading, but HTTP gives a predictable storage origin and media behavior. The tiny synthetic-data labs make no network calls and demonstrate mechanisms rather than production model quality. Print a lesson for a clean paper copy. JavaScript-free lesson/Q&A fallbacks remain available; the listening fallback provides per-section audio downloads and transcripts.

## Contributor workflow: keep new content narrated

The source of truth is `course/[0-9][0-9]-*.md`. `tools/narration.py` inventories the chapter introduction and **every heading section**, partitions all normalized source text exactly once and produces a matching listening transcript for each. Generated files are committed for static hosting.

1. Edit/add a numbered chapter or section. Keep chapter numbers contiguous from 00 and heading IDs unique.
2. Run `python3 tools/audio.py sync`. This detects new/changed sections and updates `audio/sections.json` plus `audio/narration/*.txt`. Review the transcripts; do not hand-edit generated copies.
3. For new notation, add a precise expansion to `audio/speech-math.json`; update `audio/pronunciations.json` for acronyms. New code fences require an authored explanation in `audio/code-narration.json`, keyed to the exact code hash. Carefully adapted mathematical passages in `audio/editorial.json` are bound to their original source; source edits invalidate them until reviewed. Sync again after changing these rules.
4. Incrementally generate missing/stale clips with the optional local runtime below. A validated clip with an unchanged transcript and voice recipe is reused. Each successful section checkpoints independently, so interruption does not discard earlier work.
5. Run `python3 tools/audio.py check`, `python3 tools/build.py`, `python3 tools/check.py` and the tests above. Check fails for new/missing/stale source inventories, transcripts, recordings, mismatched file hashes or missing QC. `tools/check.py` includes this audio gate and validates section links. Review the generated coverage table and listen to changed narration before publishing.
6. Commit source, adaptation rules, transcripts, inventory, recording manifest, referenced media and rebuilt HTML. Open/review a PR. Changed audio uses a new content-versioned filename; previous committed versions remain recoverable in Git. Do not commit model weights, environments or temporary WAV files.

`python3 tools/audio.py status` reports chapter coverage. `python3 tools/audio.py check --transcripts-only` validates text while generation is in progress. Full validation is fast and uses only the standard library; it never loads a speech model.

### Optional local generation setup

The tested generation environment is Python 3.12 on macOS arm64, using official PyPI packages and the official spaCy English model. `audio/requirements.txt` pins the main dependencies; `audio/requirements-macos-arm64.lock` records the exact tested environment. Generation needs local disk for roughly 330 MB of model weights plus optional dependencies and output, and uses CPU; no paid speech API or credentials are needed. Other platforms may need an appropriate official PyTorch build.

```sh
uv venv --python 3.12 .venv-audio
uv pip install --python .venv-audio/bin/python --only-binary :all: -r audio/requirements.txt
python3 tools/audio_model.py --destination .audio-model
python3 tools/audio.py sync
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1 \
  .venv-audio/bin/python tools/audio.py generate --snapshot .audio-model --threads 1
python3 tools/audio.py check
```

`audio_model.py` downloads only the pinned official model/config/voice files over HTTPS and verifies all three checksums. It does not request tokens or send course text to an inference service. The generator uses paragraph chunks, checks complete grapheme coverage and nonempty pronunciation output, rejects silent/truncated/implausible results, normalizes loudness, encodes AAC/M4A and decodes each file before marking it validated. These checks are not a guarantee of flawless pronunciation or a substitute for listening review. `--chapter 08` limits generation to a chapter; rerunning resumes only missing/stale work. `audit-pronunciation` runs a local token/phoneme audit with the same optional runtime. After deployment, `python3 tools/audio.py verify-live --revision <main-sha> --report review/evidence/live-audio.json` compares every deployed episode/transcript/page with local hashes and checks audio range delivery in every chapter.

### CI / deployment boundary

The existing Pages workflow deploys committed files after a push to `main`; it was left unchanged because the connected credential lacks workflow-write permission. Therefore local checks do **not** become a remote enforcement guarantee for arbitrary direct pushes. The owner can install the reviewed [proposed validation workflow](review/proposed-course-validation-workflow.yml), which runs the standard-library audio gate, reader checks and tests before deployment. No model download or generation belongs in that CI check. Minimal manual change: add `python3 tools/audio.py check` and the existing course checks before upload/deploy, or adopt the proposed workflow. No token scope expansion was requested or performed.

## Preservation

Original repository commit `5b8767d61ce875f57c33e8f962d9a550fbb30296` remains on `archive/pre-rebuild-2026-10-18`. Complete original history was also preserved in the verified sibling bundle `../ai-fluency-original-2026-10-18.bundle` before replacement. No history was rewritten. To inspect it separately:

```sh
git clone ../ai-fluency-original-2026-10-18.bundle ../ai-fluency-original
```

The legacy service worker retires only the old course caches/registration. There is no promise of installed-PWA offline caching; a downloaded local copy works without the site. No new license grant is added to the pre-existing course repository/history. Narration's model/engine attribution is recorded separately.
