# 17 · Experiments and reading research

Prerequisites: 03 and 06; use 09 or 14 for domain-specific studies. Outcomes: turn a claim into a falsifiable experiment and distinguish results, explanation and speculation.

You add a reranker and the assistant score rises. Did the reranker help, or did the examples, labels or tuning budget change too? Begin with a comparison that could disprove your claim, then use statistics to describe the remaining uncertainty.

## Ask a question that can lose

“Reranking improves our assistant” is underspecified. A testable claim is: on a frozen set of support queries, adding reranker R to the same candidate generator improves relevant-document reciprocal rank, without exceeding a declared latency budget. Keep corpus, query labels, candidate count and evaluation protocol fixed. If changes include better chunking and a different embedding model, the result does not isolate reranking.

State hypothesis, primary metric, sampling unit, minimum effect worth acting on, sample-size rationale, stopping rule and failure criteria before observing the final test. Exploratory analysis is valuable, but identify it as exploratory and validate promising findings on new evidence. Reusing a final test after many iterations makes it a development set.

## A paired evaluation lab

Run [experiments.py](../labs/experiments.py). It compares two systems' correctness on the same tiny cases and bootstraps paired differences. The same sampled indices feed both systems. Resampling each system independently would discard useful pairing and estimate a different variability structure. With very small, hand-constructed data the result is an illustration, not a meaningful product confidence interval.

For an online test, choose randomization unit based on interference: user/session/team may be better than request. Check sample-ratio mismatch, missing outcomes, novelty effects, exposure logging and guardrails. An intent-to-treat estimate compares assigned groups; filtering to “users who adopted the feature” can introduce selection bias.

## Statistical comparisons

A hypothesis test asks how incompatible a statistic is with a specified null model. A p-value is not the probability the null is true, the probability of replication, or the size of the effect. Statistical significance can coexist with negligible practical value. Report effect size, interval, sample size and assumptions.

Power is the probability of rejecting a specified false null under a chosen effect and design. For an illustrative independent two-arm proportion comparison near p=.5, normal-approximation planning with 5% two-sided significance and 80% power uses delta for the absolute difference worth detecting and n for examples per arm. The values 1.96 and .84 are standard-normal quantiles for those significance/power choices; .25 is the binary-outcome variance at p=.5. Under these assumptions, the rough planning formula is `n≈2*(1.96+.84)²*.25/delta²` per arm. For delta=.05, n≈1568 per arm. This simplification assumes independent units, equal sample sizes and a stable binary endpoint; cluster effects, rare events and multiple metrics can require different methods.

Multiple testing increases opportunities for false discoveries. If 20 independent true nulls are each tested at .05, chance of at least one false positive is `1-.95^20≈.642`. Real tests may be dependent; the example illustrates why cherry-picking is dangerous. Methods controlling family-wise error or false discovery rate address different objectives. Sequential monitoring needs a valid sequential design; repeatedly checking ordinary fixed-sample p-values and stopping when favorable is not the same experiment.

## Read a paper in four passes

First identify the question, setting and claimed contribution. Second trace the method's inputs, outputs, objective, assumptions and resource needs. Third audit evidence: datasets, baselines, tuning budgets, compute, uncertainty, ablations and negative results. Fourth try a small reproduction or changed-condition test. Ask what would falsify your interpretation.

For [Attention Is All You Need](https://arxiv.org/abs/1706.03762), distinguish the architecture definition from translation benchmark results. The equation can be implemented directly; the reported benchmark result depends on training/evaluation setup. For [FlashAttention](https://arxiv.org/abs/2205.14135), separate exact-attention semantics from hardware-dependent speed claims. For a scaling study, ask which data, compute range and loss were fit before extrapolating to a different deployment objective.

Maintain a claim ledger with source version/date, exact claim, evidence type, limits and next verification date. A preprint is not invalid because it is a preprint, but peer review is also not proof of correctness. Replication, transparent artifacts and independent evaluations add evidence.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

1. A paper improves a score after using 10× more compute. Does it establish a better algorithm? Solution: it establishes a result under that resource allocation; compare controlled compute and data budgets to isolate efficiency.
2. Why include a negative ablation? Solution: it shows where an added mechanism fails or adds no value, preventing a universal story from one favorable case.
3. Design a replication with limited compute. Solution: reproduce a core mechanism on a small public/synthetic setup, declare deviations, compare to a baseline and avoid claiming full original-scale replication.

## Interview rehearsal and vocabulary

Interview: interpret an interval and p-value; critique a benchmark comparison; propose a low-cost experiment whose result would change an architecture decision. Vocabulary: hypothesis, effect size, power, null, p-value, multiple testing, ablation, replication, intent-to-treat, selection bias.

## What to carry forward

An experiment is valuable when its result can change a decision. Separate what was observed, why you think it happened and what remains a hypothesis. Next, [apply the reasoning to tasks with different feedback and time structure](18-domain-electives.md).
