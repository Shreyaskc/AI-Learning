# Synthetic narration credit

The Foundations section sample is synthetic speech generated locally using
**Kokoro-82M v1.0, voice af_heart**, with the official `kokoro` Python package 0.9.4.
The script is original AI Fluency course material; it is not a book excerpt or a
recording of a person. No custom voice cloning, paid service or remote inference
was used. This is one voice/pacing review sample, not complete chapter narration.

- Official model: https://huggingface.co/hexgrad/Kokoro-82M
- Official engine: https://github.com/hexgrad/kokoro
- Official voice list: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
- Engine license copy: [Apache-2.0](licenses/Kokoro-Apache-2.0.txt)

The model card declares Apache-2.0 and welcomes deployment. The supplied voice is
listed in that model repository; no output-publication restriction was found in
those upstream materials. This records the basis for using the sample, not a
blanket warranty concerning every upstream right or use case. No model weights or
voice tensors are distributed in this repository.

Model revision: `f3ff3571791e39611d31c381e3a41a3af07b4987`.
The downloaded model SHA-256 was verified against the author-published value:
`496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4`.

The 208-word matching transcript is
[01-foundations-core.txt](transcripts/01-foundations-core.txt).
Generation used paragraph chunks, speed 1.0, two CPU threads and 24 kHz mono audio.
The M4A is about 90 seconds and 800 KB, AAC with fast-start metadata; ffmpeg loudness
processing targeted -19 LUFS and -1.5 dBTP. Decoded checks measured -19.13 LUFS and
-1.48 dBTP. Human listening, pronunciation and device playback review remain needed.

The earlier Samantha/System Voice test recording remains outside the repository
and is not included, published or uploaded to Library.
