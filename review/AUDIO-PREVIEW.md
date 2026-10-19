# Audio preview and continuous listening — draft review

## Delivered and not yet delivered

One real narration sample was generated locally from the public Foundations course:
Samantha (installed en_US System Voice), 165 words/minute, 94.61 seconds. The original
transcript is audio/transcripts/01-foundations-core.txt. ffmpeg converted the on-device
AIFF to AAC in M4A at requested 64 kbit/s with fast-start metadata. The file is 812 KiB;
decoding/volume checks found 2,086,231 samples, mean -15.8 dB and peak -1.7 dB. This
verifies a decodable non-silent recording, not a human listening-quality review.

The private sample and standalone local player are in the sibling audio-preview
folder, outside this public Git repository. No audio bytes were uploaded. No paid
API, account setup, cloned voice or cloud speech service was used. The sandboxed say
attempt returned only an empty audio header; the explicitly scoped local speech-service
execution succeeded. No expensive model was loaded.

Apple's macOS Tahoe 26 license section 2F permits original System Voice projects for
personal, noncommercial use and restricts publishing/public sharing, including nonprofit
contexts: https://www.apple.com/legal/sla/docs/macOSTahoe.pdf. Therefore the public
recording catalog is empty. The local recording can be reviewed privately; it must
not be committed to Pages or uploaded to a shared Library. A voice with verified
redistribution rights is needed before public recordings are added. No cloud Library
capability is currently available, and no Library upload was attempted.

The draft includes an honest Listen preview with 20 chapter slots and one authored
sample transcript, not 20 recorded chapters. The Foundations section has a direct
Listen link. A local-file picker can attach a personal recording without upload; its
blob URL remains in memory, requiring file reselection after reopening. The private
standalone preview directly attaches the sample for convenient voice/pacing review.

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
is ready for the user's private voice/pacing review. This is a draft PR only; no merge
or deployment is authorized.

Recreate the local preview after obtaining the private sample:

```
python3 tools/make_audio_preview.py --sample ../audio-preview/foundations-samantha.m4a
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
