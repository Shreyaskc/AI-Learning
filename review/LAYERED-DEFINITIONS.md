# Layered definitions — draft review

## Coverage and design

All 83 previous glossary entries have been reviewed and rewritten with four layers:
original textbook-style technical definition, plain-language explanation, analogy
with an explicit limit, and concrete example. Two new entries bring the total to
85: Representation distinguishes the general encoding concept from an embedding;
Attention distinguishes model-internal weighted mixing from external retrieval.
Grouped entries explain each constituent separately; slashes do not create aliases.

The seven existing bold technical marks retain popovers. Ordinary bold emphasis is
unchanged. Technical definition, intuition and example are visible; the analogy is
a native expandable disclosure, reset closed when opening or switching a term.
The full reference renders as readable sections instead of an eight-column table.
All four layers and source links remain readable without JavaScript. Only definitions
used by a page are embedded into its runtime JSON, avoiding an 85-entry payload on
every lesson. Source of truth remains course/glossary.md.

## Before / after

Parameter previously: “A number fitted from training data that controls a model’s
output.” Now: a quantity estimated in a model's parameterization, with f(x)=wx+b
and each symbol explained. Plain language contrasts a fitted parameter with a
hyperparameter. Analogy: knobs adjusted by fitting, limited because individual
neural weights rarely correspond to single interpretable facts. Example: a fitted
delivery-cost coefficient and intercept, with units.

Embedding previously: “Learned vector representation under an objective.” Now:
a mapping of objects into a vector space, learned or otherwise, with geometric
relationships shaped by an objective; table and contextual forms are distinguished.
The map analogy explicitly warns that proximity is not universal meaning or truth.
The example uses query/passage vectors in retrieval.

Training/inference, feature/target, calibration/equalized odds, precision/recall,
confidence/credible intervals, and SFT/PEFT/LoRA now explicitly contrast adjacent
concepts. Formulas state their assumptions and explain symbols locally.

## Sources and limits

Each entry links primary research, authors' teaching material, standards or official
implementation documentation. Terminology was checked against those sources;
analogies and parcel examples are original. No passages were copied from textbooks.
Definitions concern stable foundations or explicitly scoped conventions. Operational
terms such as agent and memory are framed as course/application conventions rather
than universal formal definitions. No performance superiority is claimed.

Generated links/anchors, schema completeness and analogy limits are checked, along
with all 83 original reference names, scoped payloads, alias separation, disclosure
reset and existing modal lifecycle behavior. Existing Q&A source-pair tests preserve
all 69 questions and answers. Browser/native QA remains blocked: the Mac is locked
and no browser surface is connected. DOM-double and CSS checks are not screen-reader,
mobile or real keyboard verification. No merge or deployment in this draft.
