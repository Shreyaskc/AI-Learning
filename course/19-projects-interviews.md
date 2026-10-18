# 19 · Projects, mastery gates and interview practice

Prerequisites: the relevant core chapters; 06 and 16 are mandatory for every project. Outcomes: produce inspectable evidence, defend a design, and communicate uncertainty. Reading completion is not demonstrated mastery.

## Four projects with concrete deliverables

**Project A — A trustworthy tabular predictor.** Use synthetic support tickets or a documented public dataset. Define decision time, target maturity and costs. Implement a constant/rule baseline, logistic model and a tree-family comparison using an optional pinned library environment. Split by time or entity as justified; fit preprocessing inside training only. Deliver data contract, model comparison, uncertainty, slices, threshold selection on validation, a frozen final test report, and a script that reruns it. This extends the standard-library lab; the repository does not claim to include a trained tree benchmark.

Acceptance: no future fields, no final-test tuning, reproducible artifacts, error analysis that leads to a next experiment, and a clear explanation of where the data is unrealistic. Counter-test: inject a post-outcome feature and demonstrate why an apparently excellent score is invalid.

**Project B — A cited knowledge assistant.** Build ingestion, lexical baseline, optional dense retrieval/reranking, ACL enforcement, provenance and deletion. Add a generator only after retrieval evaluation. Include answerable, unanswerable, conflicting, stale and adversarial documents. Report retrieval recall/ranking separately from citation support, answer correctness, abstention, latency and cost. Use synthetic data by default; optional provider calls require separate configuration and budget.

Acceptance: an unauthorized document never enters model context; generated claims carry supporting evidence or are withheld; deletion invalidates derived records; human-rubric evaluation includes disagreements. Counter-test: a highly relevant unauthorized page and an authorized page containing malicious instructions.

**Project C — A bounded operations assistant.** Start with read-only diagnosis and a fixed state machine. Compare a model-selected next-step variant only if task variability justifies it. Enforce schemas, allowlists, budgets, durable operation IDs and audit logging. Simulate timeouts, duplicate requests, unknown tools and stale state. Deliver transition diagram, retry policy, recovery trace, threat model and incident report.

Acceptance: the assistant stops at its budget, repeated operation IDs do not duplicate effects, ambiguous timeouts trigger status checks, and sensitive changes follow explicit authorization policy. Counter-test: crash after effect but before acknowledgement; demonstrate recovery without repeating the effect.

**Project D — A serving/platform design with measurements.** Begin with a small local mock service and load generator, then optionally a real CPU/GPU model. Measure queueing, throughput and tail latency for different prompt/output lengths. Estimate weight/KV memory, choose admission/batching policy, record versions, define SLOs and practice rollback. Declare whether measurements come from a mock or real model; never label mock tokens/s as GPU throughput.

Acceptance: capacity arithmetic is dimensionally correct, overload degrades predictably, tenant quotas work, cost per successful task is defined, and rollback returns to a compatible data/model/index set. Counter-test: one tenant sends long contexts that would exhaust shared memory.

Each project needs a README, clean run instructions, provenance, tests, evaluation report, architecture/dataflow, assumptions, limitations, resource estimate and five-minute defense. These are assignments; the tiny course labs are starting mechanisms, not completed production capstones.

## Evidence-based phase gates

After 01–06: repair a leaky split, calculate Bayes and one gradient, and justify a cost-aware metric. Pass only when calculations and availability logic are correct without referring to a solution.

After 07–09: trace a two-layer backward pass and masked attention, explain autoregressive loss and contrast SFT/LoRA/preferences. Pass when gradient checks and future-input invariance tests work and you can explain their limits.

After 10–13: deliver the Project B vertical slice with explicit provenance, permissions and memory lifecycle. Pass when missing evidence and unsupported output are diagnosed separately and adversarial tests exercise boundaries.

After 14–18: defend capacity, rollout, threat and experiment plans under a changed requirement. Pass when assumptions are revised coherently, not by adding vocabulary. Keep status as unattempted / attempted / passed / needs review and attach evidence; the reader's completion checkbox records study progress only.

## A scored mock interview

Use 75 minutes: 10 minutes foundations, 15 implementation/debugging, 35 design, 10 failure injection and 5 reflection. Have a reviewer choose one unseen variation.

Foundation prompts: explain training versus inference using a concrete predictor; compute precision from TP=30,FP=70; derive the sigmoid/log-loss gradient; explain why cosine is not calibrated relevance. Answer anchors: parameter changes versus fixed application; precision=.3; dL/dz=p-y then multiply by input; geometric score does not establish event frequency.

Implementation prompt: a model has superb test performance but collapses online. Model answer: reconstruct decision time and data lineage, inspect target/post-outcome fields and entity/time overlap, audit train-only preprocessing, compare feature parity and label maturity, then evaluate shift and selection. “Use a bigger model” is premature because the evaluation may be invalid.

Design prompt: build a multi-tenant documentation assistant for 10,000 employees. Clarify active traffic, document count/size/update rate, permission complexity, residency, latency/quality targets, escalation and budget. A strong design includes versioned ingestion, permission-aware retrieval, ranking, evidence assembly, generation contract, abstention, caches scoped by identity/policy/version, evaluation and human ownership.

Worked capacity assumptions: 2% of employees simultaneously active is 200; if each active user sends one request every 20 seconds, average arrival rate is 10 requests/s. At hypothetical mean response time 4 s, Little's law gives mean concurrency 40. At 2,000 prompt and 300 generated tokens per request, token traffic averages 20,000 input and 3,000 output tokens/s. Those arithmetic loads do not prove a serving cluster can handle them. Benchmark actual context distributions and headroom. If assumed prices were $1/million input tokens and $4/million output tokens, cost/request would be .002+.0012=$.0032 before retrieval/infrastructure. These invented prices are for arithmetic only, not current vendor pricing.

Failure injection: permissions change while answers are cached; a source contains injection; one tenant floods long prompts; embedding migration changes dimension; a tool times out after executing. Model answer: invalidate/version authorization caches, enforce trusted boundaries, admit by resource budget with quotas, dual-index and validate migration, query operation status/idempotency before retry. Explain remaining consistency windows rather than claiming perfect instant behavior.

## Rubric and leadership evidence

Score each from 0 (absent/wrong) to 3 (clear, tested and defended): problem framing, mechanism/math, evaluation, implementation/debugging, capacity/cost, security/privacy, operations, tradeoffs/communication. A useful rehearsal target is at least 2 in every category, then strengthen weak areas; this is a study rubric, not an employer's hiring bar. A serious leakage or authorization error requires correction regardless of total score.

For leadership questions use only actual experience. Explain context, your specific decision, alternatives, evidence, outcome and what you would change. Do not invent achievements to match a role. Practice disagreement about quality targets, build-versus-buy, migration ownership and incident response. The senior signal is clear judgment under constraints, including knowing what evidence is missing.

## Interview tracks and boundaries

Solutions architects emphasize requirements, integration, permissions and build/buy. ML engineers deepen modeling, data and reproducible evaluation. LLM application engineers deepen retrieval, tools and error analysis. Platform engineers deepen scheduling, hardware, distributed failure and observability. Applied scientists deepen statistics, controlled experiments and causal assumptions. Research scientists require sustained mathematics, paper replication and novel research beyond this course.

Choose two projects, record a mock defense, review mistakes a week later, and solve a changed scenario. Vocabulary becomes useful when it lets you derive an answer and revise a decision, not when it replaces either.
