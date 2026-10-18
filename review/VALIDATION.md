# Validation and review record

Date: 2026-10-18. This record describes evidence from this rebuild, not learner mastery or production certification.

## Repository identity and preservation

- Verified repository: https://github.com/Shreyaskc/AI-Learning (GitHub viewer permission ADMIN).
- Identity evidence: existing `index.html` title “AI Fluency — from tokens to agents”; `LEARNING_PLAN.md` title “The AI Fluency Roadmap.”
- Local checkout: `/Users/shreyas/Documents/Codex/2026-10-18/task-2/ai-fluency`.
- Original clean commit: `5b8767d61ce875f57c33e8f962d9a550fbb30296`.
- Preserved branch: `archive/pre-rebuild-2026-10-18`.
- Complete-history bundle: `../ai-fluency-original-2026-10-18.bundle`; `git bundle verify` passed before replacing files. No uncommitted content existed in this fresh checkout.
- Rebuild: `course/zero-to-ai-platform`. No default-branch changes, force push, history deletion or visibility change.
- No repository-local AGENTS.md, .agents skills or .codex instructions were found. Other work repositories were not modified.

## Authoring and review

Twenty numbered chapters plus glossary, coverage and references were authored. Mathematical explanations, code and synthetic examples are original; old course/assets are preserved in Git rather than silently re-used. Topic depth is recorded in `course/coverage.md`.

An independent reviewer checked the proposed sequence, then chapters 02–08 for arithmetic and terminology, then the expanded representative attention chapter and lab, plus sampled retrieval, data-platform, serving and security material. Corrections incorporated: conditional token probabilities, a finite zero-correlation counterexample, least-squares intercept handling, separate temperature symbol, input-level causal-mask tests, a third embedding row matching output vocabulary, and the retrieval example's document count.

The reviewer independently ran all 26 Python tests successfully and checked the attention/LN/logits, dual-clock example, memory/all-reduce/Little's law arithmetic and security caveats. This was a sample review; every paragraph has not received an independent specialist audit. No 28/36 rubric score is claimed, and no learner assessment has been completed.

## Executed checks

Environment: Python 3.14.6 on this Mac; Node 26.0.0; the proposed CI uses Node 20. Python code requires 3.10+; the proposed CI uses Python 3.12. Only the local Python environment has executed at the time of initial commit; No CI validation run has been claimed.

- Eight standard-library lab entry points run successfully: foundations, learning, attention, retrieval, platform, multimodal, experiments, electives.
- `python3 -m unittest discover -s labs -p 'test_*.py'`: 26 tests pass.
- `python3 tools/build.py --check`: 24 generated pages match Markdown sources.
- `python3 tools/check.py`: all local HTML/Markdown links, anchors, current navigation markers, code fences, lesson elements and Python syntax pass.
- `node --check app.js` and `node --check sw.js`: pass.
- `node tools/test_reader.js`: reader progress/search/menu and legacy-worker retirement behavior pass using DOM/storage/service-worker doubles.
- `git diff --check`: pass.

Selected expected values: rare-event precision .083333; analytic/numeric logistic gradient -.626694; causal second-row weights (.669762,.330238); first-position token probabilities (.786985,.106507,.106507); point-in-time total 5 versus leaky total 105; KV size .5 GiB/sequence under the declared assumptions.

## Remaining verification limitations

Rendered desktop/mobile visual inspection was attempted but not completed: no browser automation surface was connected, and the native Safari action returned that the Mac was locked and automatic unlock failed. No unlock workaround was attempted. Accessibility is supported structurally (landmarks, labels, skip link, focus styles, table scrolling, responsive CSS), but a real browser/screen-reader audit remains needed. JavaScript DOM-double tests are not a substitute for rendered verification.

No expensive training, provider calls, real generative RAG, dense/ANN retrieval benchmark, distributed GPU run, production load test or security audit was executed. The labs label their toy/mock scope. Four capstones remain learner assignments. These limitations and advanced topic gaps are explicit in the coverage ledger.

The original main-only Pages workflow is unchanged. A proposed replacement with validation gates is preserved in `review/proposed-course-validation-workflow.yml`, because the existing GitHub OAuth credential rejected workflow-file updates (missing workflow scope). That rejected push did not create the remote course branch. The archive branch push succeeded. The initial local implementation commit, including its workflow proposal, remains recoverable in local branch `review/with-ci-local`. The publishable course commit excludes changes to `.github/workflows/pages.yml`. A draft PR does not deploy the live site. Merge and any production release remain separate decisions.
