# Audio preview and continuous listening — draft review

## Current sample

One shareable candidate was generated locally from original Foundations text:
Kokoro-82M v1.0, af_heart, official kokoro package 0.9.4. It has 208 words and lasts
89.8 seconds, with a matching transcript at audio/transcripts/01-foundations-core.txt.
The draft includes the 800160-byte M4A as a single section sample, not a complete
chapter. The other 19 chapter slots have no recording; full chapter narrations are
0/20. Voice and pacing still need user review before expansion.

Generation used an isolated Python 3.12 environment, official PyPI wheels, the
vendor's official spaCy English model and official Hugging Face model files. There
was no paid API, account setup, credential use, cloud inference or custom voice
cloning. The source text stayed on-device during synthesis. Model weights matched
the author-published SHA-256. Paragraph-sized chunks ran with two CPU threads; the
six paragraphs took about 8.7 seconds of synthesis after model initialization.

The encoded sample is 24 kHz mono AAC with fast-start metadata. Decoding, finite
waveform and duration checks passed; raw PCM had no near-clipped samples. ffmpeg
loudness processing targeted -19 LUFS and -1.5 dBTP; encoded analysis measured
-19.13 LUFS and -1.48 dBTP. These are signal checks, not a human listening review.
Metadata/provenance is in review/evidence/kokoro-sample.json; visible synthetic
narration credit and upstream references are in audio/ATTRIBUTION.md.

The official model and engine declare Apache-2.0; af_heart is listed in the supplied
voice repository. No output-publication restriction was found in those upstream
materials. That is the documented basis for this review candidate, not a blanket
warranty about all upstream rights. An engine license copy is retained. No model
weights or voice tensors are distributed in Git.

The earlier 94.61-second Samantha/System Voice test stays private in the sibling
workspace folder, outside Git, Pages and Library, because Apple's macOS Tahoe 26
license section 2F restricts public sharing: https://www.apple.com/legal/sla/docs/macOSTahoe.pdf.
Its original separate transcript is preserved there. The new Kokoro sample was
successfully saved to the user's Library for native review, with its Library identity
retained locally; the restricted sample was never uploaded.

## Playback and resume contract

A dedicated Listen page owns one audio element throughout the playlist. Press Play
or Resume to start. Continue-to-next-chapter is opt-in and saved as a preference;
reopening never plays automatically. Pause/Stop cancels the current run; Stop also
resets that section's position. Manually changing chapters pauses and clears the old
source. End-of-track continues only while explicitly armed and opted in. A missing
next recording stops at that chapter, and the final chapter never loops. Play promise
rejections show a tap-to-continue instruction; unavailable/undecodable media stops
continuation. Native seeking and speed controls remain available. Browser/OS pauses
are treated as interruptions requiring Resume rather than automatic retries.

The new ai-fluency-audio-v1 storage record contains version, current chapter/section
ID, per-section seconds, speed and continuous-play preference. It never stores an
active-play flag or local blob URLs. Time updates write at most every five seconds;
pause, seek, preference changes and page lifecycle changes flush. Invalid values and
unknown IDs are sanitized, restored positions are clamped to decoded duration, and
storage errors leave in-tab playback usable. This is same-browser/origin storage,
not cross-device sync or guaranteed retention. file:// preview storage is browser-
dependent. Closing the browser abruptly can lose up to the latest five seconds.

Before this change, the reader already saved study checkboxes and Q&A ratings and
per-topic question resume. It did not save text scroll position or audio position.
The audio record is separate and leaves those prior records and session notes alone.

Optional Media Session metadata, play/pause/stop, seek and chapter selection are
registered where supported. Chapter controls intentionally select paused. No claim
is made of uninterrupted iOS, background or locked-screen playback.

## Asset strategy and publication path

Public recordings must be local audio/ assets with an authored matching transcript,
asset SHA-256, transcript SHA-256 and a documented redistribution basis in
 audio/catalog.json. The build rejects missing or changed assets/transcripts and
unknown recording IDs. Suggested production format: mono AAC/M4A or MP3 at 48–64
kbit/s after listening tests; 10 minutes at 64 kbit/s is about 4.8 MB before overhead.
Use content-versioned filenames when replacing recordings. Native preload=none avoids
fetching whole playlists before Play; there is no service-worker audio cache or
whole-course prefetch. GitHub Pages/browser HTTP caching applies; native range and
seeking behavior needs live-device verification when publishable assets exist.

After private sample feedback: choose a redistribution-cleared voice/backend, approve
voice and pacing, generate one section at a time with matching transcript and QA, then
fill the catalog. Full narration has deliberately not been generated before that review.

## Validation and limitations

14 media/DOM-double groups cover explicit start, continuation, missing/final chapter,
repeatable resume, throttle/flush, stop and pause cancellation, pending-play races,
corrupt/denied storage, speed/seek bounds, interruptions/errors, private file handling,
Media Session and DOM lifecycle wiring. Python checks cover catalog honesty, transcript,
single media element, no autoplay, labels, separate state and exclusion of private
voice binaries. Existing glossary/Q&A/reader checks and offline labs also pass.

Actual browser interactions remain blocked: no browser is connected, and the Mac is
locked with automatic unlock unavailable. No rendered/mobile, audible listening,
screen-reader, real media-policy or background playback pass is claimed. The sample
is ready for voice/pacing review. This remains a draft PR only; merge and deployment are pending user approval.

Recreate the local preview with the local Kokoro review sample:

```
python3 tools/make_audio_preview.py --sample ../audio-preview/foundations-kokoro-af-heart.m4a
node tools/test_podcast.js
```

## Integration with layered definitions

PR #5 now includes the definitions draft branch as an ancestor and targets that
branch for review. The shared CSS conflict was resolved by keeping both features,
and all 27 generated pages were rebuilt from combined source. An integration test
asserts Listen navigation plus layered dialogs on every page, seven Foundations
term links plus its section audio link, 85 glossary sections and the listening player.
Combined checks passed: 80 Python tests, 14 offline labs, 14 audio behavior groups,
13 Q&A groups, term lifecycle/disclosure behavior, reader smoke tests, generated
links and JavaScript syntax. This integrates draft branches only; main and the
recovery archive are unchanged. Both PRs remain drafts pending approval.
