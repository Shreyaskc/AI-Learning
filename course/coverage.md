# Coverage ledger and remaining depth

This is a broad first edition with authored explanations, worked calculations and small offline implementations. It is not a completed specialist curriculum at uniform depth. “Authored,” “executed,” “reviewed,” and “learner mastered” are separate states. Learner mastery is unassessed until you complete the gates and projects.

Depth: R=recognize, E=explain with example, I=minimal implementation, V=evaluate a toy mechanism, D=design reasoning/assignment. A design assignment is not evidence of a deployed system. Every numbered lesson has exercises with explained solutions; 19 provides capstone acceptance criteria. All fourteen lab entry points execute offline. The [29-module crosswalk](module-crosswalk.md) maps every original acceptance module to actual evidence and remaining depth. Automated tests validate selected mechanisms, not every paragraph or an ML benchmark.

| Topic | Lesson | Actual depth | Worked evidence / runnable file | Review and limits |
| --- | --- | --- | --- | --- |
| AI vocabulary, tasks, train/inference | [01](01-foundations.md) | E | ticket baseline; foundations.py | Introductory system framing |
| Data arrays, units, dtype, missingness | [02](02-math.md), [13](13-data-platforms.md) | E | shape/storage calculation; train-only scaler | No NumPy/broadcasting implementation |
| Linear algebra and calculus | [02](02-math.md) | I/V for dot/cosine/derivatives/PCA direction; R/E for SVD | foundations.py; gradient checks | Independent review; tiny power-iteration PCA, no full SVD solver |
| Probability/information | [03](03-probability.md) | I/V | Bayes, cross-entropy; foundations.py | Independently reviewed arithmetic |
| Statistics/experimental design | [03](03-probability.md), [17](17-research-experiments.md) | E/I | paired bootstrap; experiments.py | No full causal inference or Bayesian course |
| Optimization | [04](04-optimization.md) | I/V for SGD; E for Adam | one-step update; learning.py | Independently reviewed derivative |
| Linear/logistic models | [05](05-classical-ml.md) | I/V for logistic | full update; learning.py | Trained vector logistic and frozen comparison; no framework/library comparison |
| Trees, ensembles, kernels, naive Bayes | [05](05-classical-ml.md) | I/V tree; E other families | model_comparison.py, frozen model selection/report | Tree trained; forest/boosting/SVM/kNN/naive Bayes remain further work |
| Clustering/PCA/anomaly methods | [05](05-classical-ml.md), [18](18-domain-electives.md) | I/V k-means/PCA; E anomaly/density | representations.py, geometry/failure analysis | Tiny learned clusters/PCA; density/anomaly experiments remain |
| Evaluation/leakage/calibration | [06](06-evaluation.md) | I/V | confusion counts, Brier, split tests | Selected checks; no real dataset benchmark |
| Time series/recommenders/bandits | [18](18-domain-electives.md) | E/I baseline | electives.py | Advanced estimators/causal policy evaluation not implemented |
| Neural networks/backprop | [07](07-neural-networks.md) | I/V complete tiny MLP; E architecture families | model_comparison.py, every-parameter gradient check | Trained MLP; no framework autograd lab |
| CNN/RNN/GNN foundations | [07](07-neural-networks.md) | R/E | filter count, numerical convolution/recurrence; representations.py | Operations traced; no convolution/RNN/GNN training |
| Tokenization/language modeling | [08](08-transformers.md), [09](09-llm-training.md) | I/V bigram, loss and decoding; E BPE | language_model.py, attention.py | Trained character bigram; no neural LM/subword tokenizer training |
| Attention/transformers | [08](08-transformers.md) | I/V minimal block | full projections, normalization/logits; attention.py | Independent review and causal-input regression tests |
| Pretraining/SFT/LoRA | [09](09-llm-training.md) | E/I arithmetic | trained count-model NLL; SFT mask; LoRA counts | No neural pretraining/SFT/LoRA executed |
| RLHF/DPO/alignment | [09](09-llm-training.md) | E/I scalar DPO | stable preference loss and reward failure analysis | No PPO/DPO policy training |
| Retrieval/reranking/ANN | [10](10-retrieval-rag.md) | I/V lexical/BM25; E dense/ANN | retrieval.py, rag_evaluation.py | BM25 evaluated; no learned dense/ANN/reranker benchmark |
| Grounded generation/RAG | [10](10-retrieval-rag.md) | I/V mock integration; E/D real generator | source-tagged requests, recorded-output adapter, claim support/completeness | No real LLM answer generation or human semantic judge validation executed |
| Tools/workflows/agents | [11](11-agents-memory.md) | I/V durable deterministic; E model agent loop | durable_agent.py, actual child-process crash/recovery | Durable SQLite+provider simulator; no concurrent/real-model agent |
| Context/memory/knowledge graphs | [11](11-agents-memory.md) | I/V memory + typed graph query; D | SQLite TTL/deletion/provenance and scoped traversal tests | No production memory/graph store or entity resolver |
| Multimodal/diffusion | [12](12-multimodal.md) | E/I arithmetic | multimodal.py | No image/audio model loading or training |
| Data/feature platforms | [13](13-data-platforms.md) | I/V point-in-time; D migration | platform.py dual-clock join | No live stream/feature store deployment |
| Hardware/distributed training | [14](14-compute-serving.md) | E/I estimates | state/all-reduce arithmetic | No distributed job or GPU benchmark |
| Serving/efficiency | [14](14-compute-serving.md) | I/V mock serving; I estimates; D real serving | KV/weight/capacity + serving_experiment.py measured queue/load/batching | Real-time mock workload measured; no real-model GPU/quantization benchmark |
| MLOps/observability | [15](15-operations.md) | E/D | saved/reloaded model JSON pipeline; source/split fingerprints; incident | No deployed monitoring/registry/canary stack |
| Security/privacy/responsibility | [16](16-security-responsibility.md) | I/V selected controls; E broader topics | cross-tenant/tool/cache tests | Not a security audit, DP implementation or legal compliance assessment |
| Research/experiments | [17](17-research-experiments.md) | I/V small bootstrap; D study design | experiments.py, paper-reading protocol | No large-scale replication |
| Projects/interviews/leadership | [19](19-projects-interviews.md) | D assignments | four projects, mock interview, scored rubric | Projects and learner mastery remain unattempted |

## Explicit next-stage gaps

The model comparison, trained MLP and bigram, BM25 evaluation, durable serial workflow, persistent memory and measured mock-serving experiment are now implemented and tested. Their limits remain substantive: no real generative LLM or validated semantic judge, no learned dense/ANN/reranker comparison, no neural fine-tuning, no concurrent durable agent or real external provider, and no actual model-serving/GPU load measurement. Public-data/library comparisons, framework training debugging and real deployment drills remain next-stage work.

Advanced elective depth still needed: robust SVD and optimization theory; Bayesian graphical models; causal inference and off-policy estimation; full RL/PPO/DPO derivations and experiments; convolution/recurrent/graph training; diffusion derivations; mechanistic interpretability; multi-GPU systems experiments; differential-privacy accounting. These are named as orientations only where present. Specialist research roles require sustained additional work.

## Completion evidence

The repository's validation script checks internal links, generated navigation, code syntax and source/generated consistency. The unit suite checks all MLP weight/bias gradients, learned model serialization/preprocessing parity, language distributions/masks/preference numerics, BM25 and claim-evaluation paths, real child-process crash recovery, persistent budgets, memory/graph isolation, bounded serving accounting, probability arithmetic, attention masking through future-input changes, ranking, tenant filtering, deletion, tool validation, idempotency, point-in-time joins, scoped caches and memory arithmetic. A pass supports those stated invariants. It does not imply an unmeasured model is accurate, a service is secure under every attack, or a learner has mastered the material.
