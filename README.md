# AI Fluency — from first principles to AI systems

A rebuilt self-study course for software engineers learning AI from zero, with a path toward ML, LLM application and senior AI-platform interviews. Twenty authored chapters combine explanations, derivations, worked numbers, exercises with solutions, eight small offline labs, and four capstone assignments. It does not guarantee interview results or claim uniform specialist depth.

**Start:** [Learning contract and diagnostic](course/00-start.md). **Read in a browser:** open [index.html](index.html), or serve the directory locally. **Inspect actual scope:** [coverage ledger and remaining gaps](course/coverage.md). **Look up terms:** [glossary](course/glossary.md).

## Run locally

Python 3.10+ is required; validated in this workspace with the Python version recorded in [review/VALIDATION.md](review/VALIDATION.md). No packages, API keys, downloads or GPUs are required. Examples use synthetic data, make no network calls, and are educational implementations rather than production services.

```sh
python3 tools/build.py
python3 tools/check.py
python3 -m unittest discover -s labs -p 'test_*.py'
python3 labs/foundations.py
python3 labs/learning.py
python3 labs/attention.py
python3 labs/retrieval.py
python3 labs/platform.py
python3 labs/multimodal.py
python3 labs/experiments.py
python3 labs/electives.py
python3 -m http.server 8000
```

Visit `http://localhost:8000`. Opening `index.html` directly also works. The reader has lesson search, previous/next navigation and local study checkboxes. Progress belongs to your browser; it does not score mastery. No analytics or external scripts are loaded. Print a lesson for a clean paper copy.

## Course map

- 00–04: orientation, prediction tasks, mathematical/data bridge, probability and optimization.
- 05–09: classical ML, trustworthy evaluation, neural networks, a complete tiny attention block, LLM training/adaptation.
- 10–13: retrieval/RAG, tools/workflows/context/memory/graphs, multimodal orientation, data/feature platforms.
- 14–16: compute and serving, operational discipline, security/privacy/responsible AI.
- 17–19: experiments/research, domain electives, projects and interview defenses.

[Primary sources](course/sources.md) distinguish mathematical mechanisms, empirical findings and design judgments. Current vendor rankings/prices and untested API integrations are deliberately outside the evidence claimed here. Optional future GPU/provider projects require their own setup and cost controls.

## Preservation and migration

Original repository commit: `5b8767d61ce875f57c33e8f962d9a550fbb30296`. The original clean tree and complete history were preserved in local branch `archive/pre-rebuild-2026-10-18` and verified bundle `../ai-fluency-original-2026-10-18.bundle` before replacement. Rebuild branch: `course/zero-to-ai-platform`. No history was deleted or rewritten.

To inspect the original without overwriting this course, clone the bundle into a separate directory:

```sh
git clone ../ai-fluency-original-2026-10-18.bundle ../ai-fluency-original
```

The old JavaScript course and visual assets were replaced with original Markdown lessons and generated HTML. `LEARNING_PLAN.md` points to the new map. The service worker at the original URL retires only the old course caches/registration so returning readers receive the rebuilt files. This release does not promise installed-PWA offline caching; a local copy works without network.

## Editing and validation

Edit `course/*.md`, `style.css`, `app.js`, or lab sources. Run `python3 tools/build.py`; generated lesson HTML and the index are committed so GitHub Pages needs no dependency install. `tools/check.py` catches stale generated output and broken local links. The proposed workflow in `review/proposed-course-validation-workflow.yml` runs the same checks and all eight labs before a main-branch deploy. Installing it requires an owner credential with workflow permission; the existing live Pages workflow is unchanged. Draft PRs do not deploy the live site.

The custom renderer supports the intentionally small Markdown subset used in this repository, including code blocks and tables. It escapes source HTML. Derivations use readable inline formulas and code blocks, avoiding external mathematics-rendering dependencies.

No license grant is added to the pre-existing repository or its history. Before broader redistribution, the owner should choose an appropriate license and confirm third-party terms for any later added data/models.
