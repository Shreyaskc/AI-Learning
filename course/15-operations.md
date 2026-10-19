# 15 · MLOps, observability and release discipline

Prerequisites: 06, 10–14. Outcomes: version a complete AI behavior, define actionable monitors, and plan rollout and recovery.

A model is reloaded in a service but its saved scaler is missing. The weights are identical and the predictions change. Start with this concrete compatibility failure; it explains why a release must version the whole behavior, not just one model file.

## Practical extension: save the whole fitted prediction path

The model-comparison report now contains each selected model's fitted JSON artifact: family/schema version, feature order, training-fitted scaler, and learned coefficients, tree nodes or MLP weights. It also records implementation SHA-256 and fingerprints for the frozen train/validation/test rows. Unlike an executable pickle, this format stores data and uses an explicit supported-family loader. It is still an educational schema, not a signed or hardened deployment format.

`artifact_predict` takes raw feature values, applies the saved scaler and runs the saved model without retraining. The tests serialize/reload all four families and compare predictions with the original in-memory fitted pipeline. This catches an important train/serve skew: saving weights while forgetting the scaler would change the score despite an identical model family name. A second check replays the committed report's test metrics from its saved artifacts.

A fingerprint helps detect a changed input or implementation; it does not establish that the data is representative, lawful or correctly labeled. For production, add dependency/runtime versions, artifact signing/integrity checks, access controls, deployment compatibility and rollback drills. Treat a changed feature order or scaler schema as a model compatibility change, not a harmless metadata edit.

## Version the behavior, not just the model

A prediction depends on data definitions, preprocessing, feature versions, model weights, prompt templates, tokenizer, retriever/reranker, index snapshot, runtime settings and policy. An experiment record ties these to source revision, random seeds, dataset identifiers, training/evaluation configuration and results. A registry records candidate versions and approval/status metadata; it cannot compensate for an untraceable dataset.

For reproducibility, distinguish bitwise identical output from statistically similar results and functionally equivalent behavior. Hardware kernels, parallel order and stochastic generation can introduce differences. Pin integration versions and run regression checks; do not promise exact reproducibility on every device from a seed alone. These core labs intentionally avoid external dependencies to keep their checks reproducible and cheap.

## An operational contract

Suppose we measure the fraction of eligible requests that return a useful response within the latency budget. That measured fraction is a service-level indicator (SLI). Its target over a defined window is a service-level objective (SLO). A service agreement may add contractual consequences. For an internal assistant, define successful request carefully: valid response, within latency budget, with required evidence and no authorization violation. Availability without useful answers can hide product failure.

Worked arithmetic: a hypothetical 99.9% request-success SLO over one million eligible requests allows 1,000 failures. If 800 failures have occurred halfway through the window, 80% of the error budget is consumed. That suggests investigating burn rate and potentially pausing risky releases. It does not mean authorization violations are an acceptable 0.1% budget; high-severity controls may have independent zero-tolerance release gates and incident handling.

Observability should connect traces across ingestion, retrieval, generation, tools and post-processing. Capture stage timing, version IDs, token counts, cache status, tool outcomes and evidence IDs. Avoid indiscriminate logging of private prompts or documents. Sampling, redaction, access controls and retention rules are part of observability design.

## Monitor symptoms and outcomes

Data checks detect missing fields, schema changes, unexpected category rates and freshness violations. Model checks detect score-distribution changes, slice-specific errors, calibration loss and uncertainty. Application checks measure unsupported answers, citation coverage, abstention, duplicate tool effects and task completion. Infrastructure checks measure saturation, queue age, memory and latency tails.

Drift is a change in a monitored distribution; performance degradation is a change in task quality. Drift can occur without harm, and quality can drop without visible input drift if labels or policies change. Delayed ground truth requires leading indicators plus later outcome reconciliation. Every alert should name an owner, expected response and decision; a dashboard without an action is not operational readiness.

## Release and rollback

Offline gates use frozen evaluation and safety tests. Shadow traffic runs a candidate without controlling user actions; it can compare outputs and timings but cannot measure all effects of changed actions. Canary rollout exposes a bounded population, watches quality/cost/latency and preserves a fast rollback. An A/B experiment tests an effect under controlled assignment; it is not synonymous with canary risk containment.

Rollback requires compatible model, feature, prompt and index versions. If a migration destroyed old data or changed tool side effects, flipping a model pointer may be insufficient. Use reversible data migrations, dual reads/writes where justified, and practice a rollback drill. Define kill switches for tools separately from ordinary model release switches.

Worked incident: urgency recall drops after a feature service migration. Immediate steps: limit harm through a fallback queue, identify affected versions and time window, compare online values with replay, verify labels and logging, then restore a compatible path. Retraining immediately on suspect features may preserve the defect. The postmortem should identify causal evidence, failed safeguards, ownership and preventive tests rather than blame an individual.

Run [platform.py](../labs/platform.py) for version-sensitive cache and idempotency examples. This is not a production deployment or live load test. Use its invariants when implementing a real service.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

1. A new prompt passes every unit test but doubles output length. Is release safe? Solution: evaluate cost, latency, truncation, user usefulness and quality under realistic workload; unit tests cover only stated invariants.
2. A drift alarm fires while labeled performance is stable. Retrain automatically? Solution: investigate cause and sample coverage first; retraining has risk and cost, and drift alone is not sufficient evidence.
3. What belongs in a runbook? Solution: symptom, severity, owner/on-call, diagnostic queries, safe mitigation, rollback/kill-switch instructions, escalation and recovery verification.

## Interview rehearsal and vocabulary

Interview: define SLI/SLO/error budget; explain shadow versus canary versus experiment; handle an offline-to-online regression with explicit ownership and recovery. Vocabulary: registry, lineage, reproducibility, SLI, SLO, error budget, shadow, canary, drift, rollback, runbook.

## What to carry forward

Reproducibility, monitoring and rollback are useful when they lead to a safe operating decision. Keep the whole compatible prediction path and a named owner for its failures. Next, [challenge its security and responsibility boundaries](16-security-responsibility.md).
