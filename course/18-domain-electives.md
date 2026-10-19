# 18 · Domain electives: time, recommendations and anomalies

Prerequisites: 03, 05–06 and 13. Outcomes: avoid common domain-specific leakage, compute a baseline ranking/forecast, and define when a task needs deeper specialization. These are worked orientations, not complete courses in causal inference, forecasting or reinforcement learning.

Forecasting tomorrow’s load and ranking a recommendation list are both prediction tasks, but they expose different information and feedback. Use familiar baselines to see why the split and success measure must change. The later bandit and causal terms are an orientation, not assumed expertise.

## Forecasting respects the clock

Imagine making a forecast on Monday for Tuesday’s load. Monday is the forecast origin; the one-day distance to Tuesday is the horizon. Forecasting predicts a value at that horizon using only information available at the origin. Seasonality repeats patterns; trend is a systematic direction; residuals are what remains under a chosen model. A strong baseline can be “last observed value” or “same seasonal position last week.” Compare using rolling-origin evaluation: train up to t, predict t+h, advance origin, and refit only as declared. Do not let future normalization statistics or revised external indicators enter historical forecasts.

Worked example: daily equipment loads are [10,12,11,13]. A one-step last-value forecast for the fourth day is 11, absolute error 2. Over eligible origins forecasting values [12,11,13] from [10,12,11], absolute errors are [2,1,2], MAE=5/3≈1.667. A model must beat this baseline under the same origins and data availability. With uncertainty intervals, report coverage by horizon, not only pooled error.

Time series often have dependence, nonstationarity and overlapping targets. Randomly splitting overlapping windows can leak almost identical histories across train and test. A gap between splits may be needed where labels/windows overlap. Exogenous predictors are valid only if actually known at forecast time. A revised annual statistic is not the same feature as the initially published value.

## Recommendations are a two-stage decision system

Candidate generation chooses a manageable set; ranking orders it for a user/context. Popularity is a meaningful baseline. Collaborative filtering exploits patterns of user-item interaction; content models use item/user attributes. Matrix factorization approximates a user-item score with `u·v`, a learned low-dimensional representation. Implicit feedback such as clicks mixes preference with exposure: an unclicked item may never have been shown.

Worked ranking: a user has two held-out relevant items A and C. Top three recommendations [B,A,C] have precision@3=2/3, recall@3=1, reciprocal rank=1/2. NDCG gives earlier relevant results more weight and divides by the best possible ordering. For binary relevance, a common discounted gain is 1/log2(rank+1) at a relevant position, with rank starting at 1. Comparing the sum with its ideal-order value produces the normalized score; graded labels can give different gains. This is another ranking objective, not a direct user-satisfaction measurement. Offline ranking improvements may reflect popularity or position bias rather than better user outcomes. Evaluate cold-start users/items, diversity, novelty and long-term behavior under a clear product objective.

The next ideas are an optional deeper pass on feedback. A contextual bandit chooses an action with a reward and learns from partial feedback. It trades exploration and exploitation; unlike a full reinforcement-learning formulation, the basic model does not optimize a long sequence of state transitions. Logged-policy evaluation requires support/overlap: you cannot reliably estimate actions that had essentially no chance of being taken without additional assumptions. Propensity weighting can have high variance when propensities are tiny.

## Anomaly and risk-like decisions

An anomaly score measures departure from a reference distribution or learned pattern. A synthetic transaction stream can illustrate rare-event detection, but a rare merchant or unusual spending pattern is not proof of fraud. Labels may be delayed, selected by prior review policy or incomplete. Decisions can change observed labels, creating feedback loops.

Use temporal evaluation, calibrated probabilities where appropriate, precision/recall under a review budget, and explicit false-positive costs. If only investigated cases get labels, observed accuracy may not represent the whole population. Introduce a carefully governed sampling/audit plan to estimate missed cases, rather than silently treating unreviewed negatives as true negatives.

Reusable transaction embeddings can support multiple tasks, but require separate downstream tests and entity/time leakage audits. Changes in representation version can break score calibration and historical comparisons. Keep the example nonproprietary; no employer-specific dataset, architecture or result is implied.

## Graphs, causality and deeper boundaries

Probabilistic graphical models represent factorization and dependencies; a knowledge graph records explicit relations. They are not interchangeable. Bayesian modeling puts distributions over uncertain quantities; it is more than applying Bayes' rule to one detector. Causal inference needs assumptions about interventions, confounding and selection. Mechanistic interpretability investigates internal computations, while ordinary feature attribution often explains behavior relative to a baseline. These topics merit dedicated derivations and experiments beyond this orientation.

Run [electives.py](../labs/electives.py) for the forecasting baseline, ranking metrics and a matrix-factorization score. Change history and ranking order, then reason about the new result before running.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

1. Why is random splitting bad for overlapping forecast windows? Solution: shared history/targets can make test data near-copies and violate the future-prediction question.
2. Why not assign zero relevance to every unclicked item? Solution: lack of exposure is not evidence of dislike; account for the logging policy and missing feedback.
3. A risk model has better recall but overloads reviewers. Is it an improvement? Solution: evaluate at a fixed action budget and include queue delay, precision and costs.

## Interview rehearsal and vocabulary

Interview: defend a temporal split; calculate a ranking measure; design a feedback-aware platform that separates prediction quality from causal outcome claims. Vocabulary: horizon, origin, seasonality, rolling evaluation, candidate generation, collaborative filtering, implicit feedback, NDCG, bandit, propensity, selection bias.

## What to carry forward

Time, exposure and selection determine which comparisons are valid. Reuse the evaluation principles while changing the contract to match the task. Finally, [turn the learning into projects and interview defenses](19-projects-interviews.md).
