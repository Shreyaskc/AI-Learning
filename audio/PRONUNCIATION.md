# Listening adaptations

`pronunciations.json` expands field acronyms or supplies tested initialisms.
`speech-math.json` contains precise, original spoken forms for symbolic expressions.
`code-narration.json` explains each fenced code block without dictating punctuation.
`editorial.json` contains carefully adapted attention-matrix and backpropagation walkthroughs bound to
the exact original paragraph hash. These files feed deterministic generated transcripts.

The local English G2P audit showed that separated `A I` and `A P I` can start with
an article sound rather than the letter A. Tested forms `A.I.` and `A.P.I.` produce
letter pronunciations. Plural APIs, CPUs and GPUs are expanded to unambiguous words.
Conditional probability, division, negative values, plus-or-minus intervals and units
such as nats per token are expanded explicitly. Automated tests protect these distinctions.

When adding a formula, specify which quantity is divided by which and explain symbols
in the lesson; do not rely on the speech model guessing raw notation. A changed code
fence or adapted passage requires a fresh authored explanation. Review transcripts
before generation and listen to changed episodes where a playback device is available.
Nonempty phonemes and a valid waveform are necessary checks, not proof that every
word is pronounced as a human teacher would choose.

The full token audit also exposed punctuation-only output for leading decimals such
as `.5`. Transcripts now say “zero point five” and spell each digit in longer leading
decimals. The audit requires alphabetic pronunciation output, not just punctuation.
An omitted zero in “position 0” is prevented by spelling “position zero” explicitly.
The backpropagation adaptation names each weight, bias and derivative without
ambiguous compact notation. These repairs change recording hashes and trigger
incremental regeneration.
