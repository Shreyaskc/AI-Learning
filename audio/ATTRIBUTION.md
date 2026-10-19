# Synthetic narration credit

Course section recordings use **Kokoro-82M v1.0, voice af_heart**, generated locally
with the official `kokoro` Python package 0.9.4. Scripts adapt the original AI Fluency
lessons into listening-friendly explanations, including equations, worked examples
and practice. They are not book excerpts or recordings of a person. No custom voice
cloning, paid speech service or remote inference is used.

- Official model: https://huggingface.co/hexgrad/Kokoro-82M
- Official engine: https://github.com/hexgrad/kokoro
- Official voice list: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
- Engine license copy: [Apache-2.0](licenses/Kokoro-Apache-2.0.txt)

The official model and engine declare Apache-2.0, and the supplied voice is listed
in the model repository. No output-publication restriction was found in those
upstream materials. This records the basis for using these recordings, not a blanket
warranty about every upstream right or use case. No model weights, voice tensors or
optional synthesis dependencies are distributed in this repository.

## Provenance and validation

Model revision: `f3ff3571791e39611d31c381e3a41a3af07b4987`.
The downloaded model SHA-256 matches the author-published value:
`496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4`.
The configuration and voice checksums are also pinned in `tools/audio_model.py`.

The [section inventory](sections.json) binds source sections to
[matching transcripts](narration/). The [recording manifest](recordings.json) records
per-paragraph grapheme/phoneme checks, duration, silence bounds, media hashes,
decoding validation and the actual dependency versions. The
[coverage report](../review/AUDIO-COVERAGE.md) summarizes readiness by chapter.

Synthesis runs in paragraph chunks on CPU, speed 1.0, with 24 kHz mono output.
Encoding uses AAC/M4A with fast-start metadata and requested 64 kbit/s; loudness
processing targets -19 LUFS and -1.5 dBTP. These automated checks do not establish
flawless pronunciation, human listening approval or uninterrupted device playback.
Pronunciation rules spell out notation and acronyms, and the written section remains
the reference for code, exact commands and visual arrays.

The earlier [89.8-second Foundations review sample](samples/foundations-kokoro-af-heart-v1.m4a)
and its [original sample transcript](transcripts/01-foundations-core.txt) are retained
as provenance; they are not an extra episode in the ordered full-course playlist.
The Apple Samantha/System Voice test remains outside Git, Pages and Library.
