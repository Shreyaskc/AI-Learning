# Crosswalk to the 29-module acceptance matrix

The original acceptance design used 29 modules. This course groups them into 20 numbered chapters so related explanations share context; grouping does not imply omitted topics are finished. This ledger identifies actual implementation evidence and remaining depth for every original module. “Implemented” means a minimal educational mechanism, not production readiness. Learner mastery remains unassessed.

| Matrix ID and module | Course mapping | Evidence now present | Significant remaining depth |
| --- | --- | --- | --- |
| 00 What AI systems do | [01](01-foundations.md) | prediction contract, learned versus deterministic paths, leakage baseline | broader real-user task observation |
| 01 Numeric/data foundations | [02](02-math.md), [13](13-data-platforms.md) | shapes/units/dtype/broadcasting explanation, train-only scaling and parity tests | NumPy broadcasting/indexing integration lab |
| 02 Linear algebra | [02](02-math.md) | dot/cosine/matmul, projection, trained tiny PCA direction | robust SVD/eigensolver and numerical conditioning course |
| 03 Calculus/optimization | [02](02-math.md), [04](04-optimization.md) | derivation, updates, every MLP weight/bias checked | deeper convex/nonconvex theory and optimizer implementation comparison |
| 04 Probability/uncertainty | [03](03-probability.md) | Bayes, distributions, moments, entropy/loss, numeric checks | broader simulation and Bayesian estimation |
| 05 Statistics/experiments | [03](03-probability.md), [17](17-research-experiments.md) | bootstrap, power/multiple-testing calculation, design critique | cluster/sequential experiments and full causal estimation |
| 06 Data/evaluation | [01](01-foundations.md), [06](06-evaluation.md) | split before fitting, time/group contracts, metrics, frozen comparison | real-data leakage repair benchmark and subgroup uncertainty |
| 07 Linear/generalized models | [05](05-classical-ml.md) | trained vector logistic model, analytic gradients, JSON pipeline artifact | linear solver/library comparison and inferential diagnostics |
| 08 Classical supervised learning | [05](05-classical-ml.md) | trained greedy tree versus logistic/constant/MLP, finite-data failure | actual forest/boosting/SVM/kNN/naive-Bayes model comparisons |
| 09 Unsupervised/representation | [02](02-math.md), [05](05-classical-ml.md) | trained k-means/PCA, density/visualization caveats | DBSCAN, nonlinear projection and anomaly detector experiments |
| 10 Time/ranking/recommendations | [18](18-domain-electives.md) | rolling last-value baseline, ranking calculations, feedback/causal discussion | trained recommender/forecast models and policy evaluation |
| 11 Neural fundamentals | [07](07-neural-networks.md) | trained full MLP, all-parameter gradient checks, nonlinear failure task | framework autograd equivalent and larger data |
| 12 Deep training reliability | [04](04-optimization.md), [07](07-neural-networks.md), [15](15-operations.md) | loss decrease, scaling, seeded initialization, saved/reloaded predictions | full learning curves, dropout/Adam/schedule/checkpoint ablations |
| 13 Vision/sequence foundations | [07](07-neural-networks.md) | numerical convolution and order-sensitive recurrence | trained CNN/RNN/LSTM, transfer-learning classifier |
| 14 Tokenization/language modeling | [08](08-transformers.md), [09](09-llm-training.md) | BPE worked example, trained bigram, unknown policy, held-out NLL and generation | trained subword tokenizer/neural character LM |
| 15 Attention/transformers | [08](08-transformers.md) | full Q/K/V/block/logit trace, causal input perturbation tests | trained transformer and optimization comparison |
| 16 LLM inference/limits | [08](08-transformers.md), [09](09-llm-training.md), [10](10-retrieval-rag.md) | temperature/top-k/top-p code, stop budget, output schema/support checks | measured real-model generation and capability/error study |
| 17 Training/adaptation | [09](09-llm-training.md) | likelihood training mechanism, SFT-mask arithmetic, LoRA counts | executed neural continued pretraining, SFT/LoRA comparison and forgetting |
| 18 Preferences/alignment | [09](09-llm-training.md), [16](16-security-responsibility.md) | RL foundations, reward hacking, DPO scalar objective | learned reward/policy and PPO/DPO training/evaluation |
| 19 Retrieval | [10](10-retrieval-rag.md) | authorized BM25 and lexical baselines, ranking/case evaluation | learned dense retrieval, ANN and reranker benchmark |
| 20 RAG | [10](10-retrieval-rag.md) | context assembly, generation adapter, mock claim-level evaluation and real-output hash binding | actual generator inference, human semantic rubric validation and freshness/conflict cases |
| 21 Tools/workflows/agents | [11](11-agents-memory.md) | bounded durable workflow, separate-process crash/recovery, provider idempotency | real model-selected agent, concurrent leases/fencing and external provider integration |
| 22 Context/memory/graphs | [11](11-agents-memory.md) | persistent memory TTL/provenance/deletion, permission-scoped typed two-hop traversal | entity resolution and graph-versus-vector task comparison |
| 23 Multimodal/generative | [12](12-multimodal.md) | contrastive/noise/WER arithmetic and failure analyses | actual image/audio models, diffusion training/derivation |
| 24 Data/features | [13](13-data-platforms.md) | dual-clock feature join, train/serve artifact parity, index migration design | deployed batch/stream store and backfill/version migration drill |
| 25 Inference/distributed systems | [14](14-compute-serving.md) | memory/collective estimates and measured bounded mock batching/latency | real-model load test, KV/quantization kernels, multi-GPU run |
| 26 MLOps/LLMOps | [15](15-operations.md) | source/data fingerprints, saved JSON pipelines, runbook/rollout design | deployed registry, live drift/quality monitors and canary rollback drill |
| 27 Security/privacy/responsibility | [16](16-security-responsibility.md) | tenant/tool/cache/memory/graph boundary tests, privacy/fairness tradeoffs | broad adversarial audit, DP accounting and empirical fairness mitigation |
| 28 Senior design/capstones | [19](19-projects-interviews.md) | worked capacity/cost defense, changing constraints, project rubrics | completed learner capstones, external feedback and sustained research practice |

## What to do next

Choose an unimplemented cell that matters to your role and turn it into a controlled experiment with prerequisites, assumptions, baseline, costs, tests and failure analysis. For LLM application roles the largest current gap is actual model generation with validated semantic evaluation. For ML engineering it is real-data/library comparisons and training/deployment debugging. For platform roles it is real inference workloads, concurrent recovery and rollout drills. Research roles require substantially deeper elective mathematics and experimental work.

The practical labs close several earlier implementation gaps but do not make every cell complete. Use [coverage](coverage.md), the [source notes](sources.md) and the [project gates](19-projects-interviews.md) together.
