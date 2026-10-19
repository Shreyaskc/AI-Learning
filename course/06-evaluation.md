# 06 · Evaluation, leakage and decision quality

Prerequisites: 01, 03 and 05. Outcomes: select metrics from actions, quantify uncertainty, detect contamination, and define abstention.

Imagine an urgency detector flags 170 tickets: 80 are genuinely urgent and 90 are not. It also misses 20 urgent tickets. Is that useful for a team with limited review time? We will calculate several views of the same outcomes before choosing a metric.

## Count outcomes before naming scores

With 100 truly urgent tickets, a system catches 80 and misses 20. Among 900 non-urgent tickets it flags 90. True positives TP=80, false negatives FN=20, false positives FP=90, true negatives TN=810. Precision is TP/(TP+FP)=80/170≈.471. Recall is TP/(TP+FN)=.8. Accuracy is (TP+TN)/1000=.89. F1 is the harmonic mean of precision and recall, about .593. It ignores true negatives and assumes a particular balance; it is not the objective for every workflow.

Sweeping thresholds traces precision-recall and receiver-operating-characteristic curves. ROC uses true-positive versus false-positive rates; a low false-positive rate may still create many false positives in a very large negative population. PR behavior depends on prevalence. Area under a curve measures ranking across thresholds, while your deployment uses an operating point with an action budget. For top-k review queues use precision@k, recall@k and urgent cases caught within the service window.

For numeric targets, mean absolute error is easy to interpret in target units; root mean square error emphasizes large misses. Percentage errors can explode near zero. For probabilistic prediction use proper scoring rules such as log loss or Brier score `mean((p-y)²)`. A model is calibrated if events assigned probability p occur about fraction p over the relevant population. Good ranking, good calibration and good action utility are distinct properties.

## Splits are hypotheses about deployment

An untouched test set estimates only the distribution and measurement process it represents. Hold out future time for forecasting; separate people or entities for cold-start questions; preserve groups during cross-validation. Deduplicate near-duplicate documents and template-derived answers across training and testing. For LLMs, public benchmark inclusion in pretraining is often unknown, so treat possible contamination as a limitation rather than claiming clean causal comparison.

Leakage can occur through preprocessing, future labels, target encoding, retrieval indexes containing test answers, prompts tuned on test cases, and human adjudicators who know the candidate model. Delayed targets require waiting for label maturity. A model evaluated one day after checkout cannot have complete 30-day lateness labels.

Distribution shift includes changes in input frequency, label frequency and the relationship between inputs and targets. These are often called covariate, prior/label and concept shift; terminology varies, so define the actual change. Drift alerts identify symptoms, not necessarily business damage. Validate against new labels when possible.

## Quantify what the sample can support

Suppose 80/100 independent positives are caught. A rough normal standard error is sqrt(.8×.2/100)=.04, so an approximate 95% interval is .8±.078. Small counts or extreme rates call for better intervals such as Wilson or exact methods. Repeated observations from the same customer invalidate naive independence; resample by customer or use a suitable clustered model. Report counts and intervals per important slice, not only the aggregate.

Model A and B should usually be compared on the same cases. A paired bootstrap resamples case indices and recomputes their score difference, preserving pairing. It measures sampling variability under the chosen resampling assumptions; it does not fix biased labels or deployment mismatch.

## LLM systems need layered evaluation

Evaluate retrieval recall against known relevant documents, ranking quality such as reciprocal rank, answer correctness against an explicit rubric, citation support at claim level, refusal/abstention behavior, tool success, and end-to-end user outcomes separately. A judge model is a noisy measurement instrument: calibrate against blinded human samples, check order and style bias, pin its version, and report disagreement. String overlap can miss paraphrases; fluent prose can conceal incorrect claims.

Abstention sends uncertain or unsupported cases to another path. Plot coverage (fraction automatically handled) against error among handled cases. A model's self-reported confidence is not automatically calibrated. Use validation evidence and an explicit fallback. Human review itself has latency, cost and error rates.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

Run [learning.py](../labs/learning.py) for threshold metrics and Brier score.

1. You improve retrieval recall but answer correctness falls. Explain. Solution: extra distractors may overwhelm evidence; reranking, context ordering and generator behavior matter. Diagnose with component ablations.
2. A subgroup has 3/3 correct outputs. Can you call it solved? Solution: no; interval uncertainty and sampling selection remain large.
3. Give a release gate for a support assistant. Example solution: no unauthorized cross-tenant retrieval on adversarial tests, lower confidence bound on supported-answer correctness above an agreed target, p95 latency within budget, escalation path exercised, and staged online rollout. Targets must come from product risk and capacity, not this example.

## Interview rehearsal and vocabulary

Interview: compute metrics; explain calibration versus discrimination; design a test strategy including leakage audit, slices, uncertainty, failure severity and rollback. Vocabulary: precision, recall, ROC, PR, calibration, Brier, contamination, drift, coverage, abstention.

## What to carry forward

A score is meaningful only with its population, split, uncertainty and action threshold. Keep ranking quality, probability accuracy and decision value separate. Next, [learn how a neural network builds its own features](07-neural-networks.md), while retaining this evaluation contract.
