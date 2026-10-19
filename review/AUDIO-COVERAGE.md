# Narration coverage and validation

179 of 179 sections currently have validated recordings matching the current transcript/voice recipe. Total available duration: 4.14 hours; media: 132.06 MB.

The inventory includes every introduction and heading section in the 20 numbered chapters. All normalized source text is partitioned once; narration retains explanations, worked examples, exercises and solutions. Written reference pages such as the glossary are outside this ordered episode sequence.

| Chapter | Ready / sections | Duration (minutes) |
| --- | --- | --- |
| 00-start | 8 / 8 | 10.4 |
| 01-foundations | 7 / 7 | 9.3 |
| 02-math | 10 / 10 | 16.4 |
| 03-probability | 8 / 8 | 12.3 |
| 04-optimization | 8 / 8 | 9.4 |
| 05-classical-ml | 11 / 11 | 17.6 |
| 06-evaluation | 8 / 8 | 8.8 |
| 07-neural-networks | 10 / 10 | 15.1 |
| 08-transformers | 9 / 9 | 15.3 |
| 09-llm-training | 13 / 13 | 17.7 |
| 10-retrieval-rag | 10 / 10 | 16.7 |
| 11-agents-memory | 12 / 12 | 16.9 |
| 12-multimodal | 7 / 7 | 8.5 |
| 13-data-platforms | 8 / 8 | 7.8 |
| 14-compute-serving | 10 / 10 | 17.1 |
| 15-operations | 9 / 9 | 9.9 |
| 16-security-responsibility | 8 / 8 | 9.1 |
| 17-research-experiments | 8 / 8 | 8.2 |
| 18-domain-electives | 8 / 8 | 9.3 |
| 19-projects-interviews | 7 / 7 | 12.3 |

## Reproducible checks

`python3 tools/audio.py sync` updates section/transcript inventory. `check` fails on new, missing, changed or corrupt material; `generate` reuses validated unchanged clips and checkpoints each new one. Model/config/voice downloads are pinned and verified, and synthesis can run entirely offline. See the README for exact dependencies and commands.

Each recording has complete input-grapheme coverage, nonempty phonemes, finite non-silent waveform, plausible duration, maximum-silence checks and a successful encoded-media decode. Numeric equations and acronyms are explicitly adapted for listening; the two fenced code blocks have authored explanations. Metadata and per-paragraph checks are retained in `audio/recordings.json`. Each file and transcript is SHA-256 bound to its generation recipe.

The generator uses Kokoro-82M v1.0, af_heart, 24 kHz mono AAC, requested 64 kbit/s, fast-start metadata and loudness processing targeting -19 LUFS and -1.5 dBTP. Source text and inference remain local. No paid service, credentials or cloned voice are used.

## Limits and deployment gate

Automated text/phoneme/signal checks do not establish flawless pronunciation. Rendered browser smoke checks are reported separately from these automated checks. Mobile, screen-reader and background playback and full human listening review are not established by waveform or DOM-double tests.

The existing Pages workflow remains unchanged because the connected credential lacks workflow-write permission. Remote enforcement for future direct pushes requires the owner to install `review/proposed-course-validation-workflow.yml` or add the documented pre-upload check steps. The local audio gate and contributor commands are delivered without changing scopes.
