# 13 · Data and feature platforms

Prerequisites: 01, 06 and 10–11. Outcomes: construct historical features without future knowledge, design feature/index lifecycles, and reason about training-serving consistency.

A historical event says it happened before a prediction, but the system received it afterward. Could the original model have used it? Work through that timing question before designing a feature store or migration; it determines whether offline evaluation represents the real service.

## Two clocks matter

Event time records when something happened. Availability/ingestion time records when the system knew it. Historical prediction at decision time t must use only events both eligible by event time and available by t. Labels also need an observation horizon and maturity delay.

Worked example: predict a machine's fault at t=10. Event A occurred at 8 and arrived at 9 with value 5. Event B occurred at 7 but arrived at 12 with value 100. Event C occurs at 11 and arrives at 11 with value 20. A correct “prior observed total” at t=10 is 5: B arrived too late, C is in the future. A query checking only event_time≤10 incorrectly gives 105. A backfill may later include B in a corrected event history, but must not pretend B was available for the original online decision.

Run [platform.py](../labs/platform.py) for this exact point-in-time filter. Extend it to a per-entity time-window aggregate and test boundary inclusion. Document whether events at the exact decision timestamp are available before or after the decision; real ordering may require sequence numbers.

## A model is downstream of data contracts

An ingestion contract defines schema, units, entity keys, timestamp semantics, ownership and quality expectations. Batch ingestion favors reproducible snapshots; streaming favors low-latency updates but must handle duplicates, out-of-order events and partial failures. Track source offsets, transformation version and lineage so a training dataset can be reconstructed. A model hash without a data snapshot is insufficient reproducibility.

Missingness has meaning. A missing sensor value may indicate an outage, not a typical reading. Impute using training data and often include a missingness indicator. Do not assume zero means absent in every schema. Category dictionaries and vocabularies are fitted artifacts; define behavior for unseen categories rather than silently dropping rows. A schema change from milliseconds to seconds can produce valid numbers with invalid meaning.

## Offline and online paths

An offline store supports large historical scans for training and backfills. An online store supports low-latency feature lookup at inference. Time to live (TTL) describes how long a stored value is eligible before expiry. A feature store coordinates definitions and materialization; it does not automatically guarantee point-in-time correctness. Shared transformation logic reduces skew, but parity tests must compare sampled online values against historical reconstruction under matching timestamps and versions.

Training-serving skew arises from different preprocessing, stale online values, entity-key bugs, incompatible feature versions or different availability assumptions. A model version should declare required feature schema and transformation version. A rolling update may need dual writes, backfill, parity checks, shadow reads and rollback to avoid mixing incompatible data.

For embeddings, the model/version, tokenizer, normalization and dimension are part of the contract. Vectors from different embedding spaces should not silently share one index. Re-embedding requires cost estimates, incremental backfill, dual indexes, evaluation and an atomic read-path switch. Indexing, metadata and permissions can lag each other; define consistency and fail-closed behavior when access state is uncertain.

## Reusable embeddings and knowledge products

A shared representation can reduce duplicate modeling effort across recommendation, search and anomaly tasks. But a representation trained for one objective may fail another, leak sensitive attributes or become stale. Define downstream evaluation tasks, cold-start behavior, ownership, allowed uses and drift/refresh triggers. A broad “universal embedding” claim needs broad evidence; reuse alone does not prove semantic sufficiency.

Synthetic transaction-like events can illustrate entity histories without exposing proprietary systems. Keep identifiers, labels and target definitions invented. Evaluate label delay and selection bias before generalizing to risk decisions. A reusable data product includes documentation, lineage, version policy and support ownership, not merely a vector column.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

1. A late event corrects last month's historical aggregate. Should a reproduced old score change? Solution: distinguish “replay what was known then” from “recompute with corrected truth.” Store versions/availability to support both explicitly.
2. A feature TTL expires before its materialized replacement. What should serving do? Solution: apply a documented fallback/missingness path compatible with training or refuse/escalate; never silently use a semantically different default.
3. A deleted document persists in a vector cache. Is deleting the source sufficient? Solution: no; trace derived chunks, embeddings, summaries and caches and verify propagation within the promised deletion window.

## Interview rehearsal and vocabulary

Interview: explain event versus availability time; design a point-in-time join; defend a migration plan with schema compatibility, cost, ownership and rollback. Vocabulary: data contract, event time, availability time, watermark, backfill, feature store, materialization, lineage, skew, replay.

## What to carry forward

A reproducible feature needs both meaning and availability history. Shared transformations and versioned artifacts help only when the serving path obeys the same contract. Next, [budget memory, latency and throughput](14-compute-serving.md) for that path.
