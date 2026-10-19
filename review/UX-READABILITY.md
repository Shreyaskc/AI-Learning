# Q&A and reading-flow review

Date: 2026-10-19. Branch `ux/question-practice`, based on verified merged main `975c9c861df67d648d1bbd21b307d9339af7211e`. Existing course URLs and teaching calculations remain; this change is prepared for a new draft PR and does not inherit the earlier merge approval.

## Observed before

Direct HTTP inspection of the live home and evaluation lesson confirmed that the only interactive button was “Lessons.” The home had no practice entry, and questions/solutions appeared together as ordinary paragraph text near lesson ends. The diagnostic link opened the orientation chapter rather than a question flow. `app.js` handled study checkboxes, title search and the menu only. This is source/markup evidence, not a rendered iPhone observation.

Independent beginner-readability review scanned all 20 lessons. It found abstract notation ahead of concrete examples, compressed first-use vocabulary and important teaching appended after apparent practice/interview endings, especially in 02, 05, 07–11, 14 and 15.

## Changed learner flow

- Home starts newcomers at lesson 01; diagnostic is optional and opens its ten questions directly. “Practice Q&A” is a persistent learning-mode entry, and each lesson links to its topic.
- The practice page derives 69 complete prompt/solution pairs from the existing lesson source, including Foundations' three items and both Transformer groups (three plus four). A fixture from merged main verifies prompt/solution integrity. Further worked exercises remain in lessons with closed native answer disclosures.
- One question is shown at a time: think or optionally write → reveal answer/reasoning → choose Got it / Partly / Need practice → explicit Next. Self-ratings are never inferred from free text or answer reveal. The lesson explanation is linked before and after reveal.
- Topics/search, previous/next, exact question deep links, browser back/forward, per-topic resume, empty-result recovery and a cancelable reset keep navigation predictable.
- Notes are retained only in memory for that page session. Persisted data contains self-ratings and resume IDs under a Q&A-specific key; course study checkboxes remain separate. Storage denial, malformed data and quota failures retain usable session behavior with a visible warning.
- Answer containers use `hidden` until reveal; native closed details support no-JavaScript practice/reading. Labels, normal keyboard controls, focus movement, status text and pressed/expanded states are explicit. CSS specifies 44–48px targets, constrained flexible columns and a narrow-screen layout.

## Reading changes

Every numbered lesson now starts from a concrete problem, connects required prior skills, and ends with a short takeaway/bridge. Teaching extensions are integrated before final practice rather than restarting after an interview ending. These are prose and sequencing edits, not only added headings:

- 00 removes the quiz/terminal as a beginner gate and explains the phone-complete reading path before optional setup.
- 01 teaches one ticket predictor before model-family taxonomy and makes prediction-versus-action concrete.
- 02 starts with two tickets and a weighted matrix calculation; defines indices and units locally; moves data shapes earlier and compression into an optional deeper pass.
- 03 starts with 10,000-machine counts; builds probability notation from denominators, sampling from repeated outcomes, and information formulas from binary loss.
- 04 explains the knobs/objective/step-size before notation and shows repeated updates; optimizer taxonomy is a deeper orientation.
- 07 explains a hidden layer with actual numbers before its compact formula.
- 08 puts token lookup beside tokenization, Q/K/V definitions before the complete attention calculation, and the block trace before questions. Identity matrices and dimensions are explained locally.
- 09 places the trained tiny language model beside its objective, supervision masks beside response training, and a locally defined preference calculation after preference concepts.
- 11 follows one permitted incident action through uncertainty, crash and recovery before context/memory/graph taxonomy; product states and tool-operation states are distinguished.
- 14 follows one request and a memory/queue budget before optional hardware/distributed training; measured mock results keep their exact limitations.
- 12–19 receive task-first transitions and clearer first-use terms, including modalities, TTL, service indicators, statistical symbols and forecast horizons. Derivations, failure caveats, source links and synthetic/mock-versus-real boundaries remain.

## Verification and limits

Final local checks pass: all 60 existing course tests, 10 new Python content/structure tests, 13 JavaScript Q&A behavioral groups, existing reader smoke tests, all 14 labs and 26-page validation.

Run `python3 tools/build.py --check`, `python3 tools/check.py`, both Python test suites, `node tools/test_reader.js`, `node tools/test_practice.js` and `python3 tools/run_labs.py`.

Independent review scanned all 20 chapters and rechecked the targeted rewritten mechanisms and Q&A state/UI code. It reported no remaining source/readability/behavioral blocker after the first-use terminology fixes, while retaining the rendered-QA limitation.

The practice tests cover all 69 original pairs, diagnostic/Foundations/Transformer counts, lossless answer/reasoning splitting, closed initial answers/no-JS fallback, topic deep links, lesson explanation anchors, and source sequencing guards. JavaScript tests exercise repeated reveal/rating, notes, navigation boundaries, topic resume/reload, history, reset/cancel, invalid URL state and storage failure using the same state/UI code with DOM doubles. Existing numerical labs remain unchanged.

Authorized browser inventory was rechecked and returned no connected surfaces. The prior native-browser attempt had reported a locked Mac; no new app launch, unlock bypass or workaround was attempted. Consequently no new rendered desktop/320px screenshots or real screen-reader/touch audit is claimed. Narrow-screen and accessibility checks here are structural/CSS contracts and DOM behavior, not visual proof. These remain a required manual review before merge.

The actual Pages workflow and OAuth permissions are unchanged. Only its separately stored proposal includes the extra checks. No deployment is configured or triggered by this branch.
