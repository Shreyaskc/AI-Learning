# Coverage ledger and remaining depth

This is a broad first edition with authored explanations, worked calculations and small offline implementations. It is not a completed specialist curriculum at uniform depth. “Authored,” “executed,” “reviewed,” and “learner mastered” are separate states. Learner mastery is unassessed until you complete the gates and projects.

Depth: R=recognize, E=explain with example, I=minimal implementation, V=evaluate a toy mechanism, D=design reasoning/assignment. A design assignment is not evidence of a deployed system. Every numbered lesson has exercises with explained solutions; 19 provides capstone acceptance criteria. All eight lab entry points execute offline. Automated tests validate selected mechanisms, not every paragraph or an ML benchmark.

| Topic | Lesson | Actual depth | Worked evidence / runnable file | Review and limits |
| --- | --- | --- | --- | --- |
| AI vocabulary, tasks, train/inference | [01](01-foundations.md) | E | ticket baseline; foundations.py | Introductory system framing |
| Data arrays, units, dtype, missingness | [02](02-math.md), [13](13-data-platforms.md) | E | shape/storage calculation; train-only scaler | No NumPy/broadcasting implementation |
| Linear algebra and calculus | [02](02-math.md) | I/V for dot/cosine/derivatives; R/E for SVD/PCA | foundations.py; gradient checks | Independently reviewed arithmetic; no full SVD solver |
| Probability/information | [03](03-probability.md) | I/V | Bayes, cross-entropy; foundations.py | Independently reviewed arithmetic |
| Statistics/experimental design | [03](03-probability.md), [17](17-research-experiments.md) | E/I | paired bootstrap; experiments.py | No full causal inference or Bayesian course |
| Optimization | [04](04-optimization.md) | I/V for SGD; E for Adam | one-step update; learning.py | Independently reviewed derivative |
| Linear/logistic models | [05](05-classical-ml.md) | I/V for logistic | full update; learning.py | No framework comparison executed |
| Trees, ensembles, kernels, naive Bayes | [05](05-classical-ml.md) | E | Gini/cost examples and comparison assignment | Tree/forest/SVM fitting remains further lab work |
| Clustering/PCA/anomaly methods | [05](05-classical-ml.md), [18](18-domain-electives.md) | R/E | geometric projection, anomaly failure analysis | No clustering model training |
| Evaluation/leakage/calibration | [06](06-evaluation.md) | I/V | confusion counts, Brier, split tests | Selected checks; no real dataset benchmark |
| Time series/recommenders/bandits | [18](18-domain-electives.md) | E/I baseline | electives.py | Advanced estimators/causal policy evaluation not implemented |
| Neural networks/backprop | [07](07-neural-networks.md) | I for tiny backward trace; E for architecture families | learning.py derivative | No full MLP training/autograd framework lab |
| CNN/RNN/GNN foundations | [07](07-neural-networks.md) | R/E | filter parameter count; architecture discussion | No convolution/RNN/GNN training |
| Tokenization/language modeling | [08](08-transformers.md), [09](09-llm-training.md) | E/I loss | merge example, IDs-to-logits; attention.py | Toy merge; no trained tokenizer/character LM |
| Attention/transformers | [08](08-transformers.md) | I/V minimal block | full projections, normalization/logits; attention.py | Independent review and causal-input regression tests |
| Pretraining/SFT/LoRA | [09](09-llm-training.md) | E/I arithmetic | loss/perplexity/rank counts; attention.py | No actual pretraining/fine-tuning executed |
| RLHF/DPO/alignment | [09](09-llm-training.md) | E | reward/return failure analysis | No PPO/DPO implementation or tuned policy |
| Retrieval/reranking/ANN | [10](10-retrieval-rag.md) | I/V lexical; E dense/ANN | retrieval.py, ranking metrics | No learned dense model/BM25/ANN benchmark |
| Grounded generation/RAG | [10](10-retrieval-rag.md) | E/D; I extractive baseline | extractive citations and abstention tests | No LLM answer generation or judge validation executed |
| Tools/workflows/agents | [11](11-agents-memory.md) | I/V deterministic; E agent loop | platform.py allowlist/idempotency/budget | No model-driven agent or durable backend |
| Context/memory/knowledge graphs | [11](11-agents-memory.md) | E/D | lifecycle and graph traversal worked example | Production memory store/entity resolution not implemented |
| Multimodal/diffusion | [12](12-multimodal.md) | E/I arithmetic | multimodal.py | No image/audio model loading or training |
| Data/feature platforms | [13](13-data-platforms.md) | I/V point-in-time; D migration | platform.py dual-clock join | No live stream/feature store deployment |
| Hardware/distributed training | [14](14-compute-serving.md) | E/I estimates | state/all-reduce arithmetic | No distributed job or GPU benchmark |
| Serving/efficiency | [14](14-compute-serving.md) | I estimates; D planning | KV/weight/capacity calculation | No load test, batching kernel or quantization benchmark |
| MLOps/observability | [15](15-operations.md) | E/D | error budget and incident walkthrough | No deployed monitoring stack |
| Security/privacy/responsibility | [16](16-security-responsibility.md) | I/V selected controls; E broader topics | cross-tenant/tool/cache tests | Not a security audit, DP implementation or legal compliance assessment |
| Research/experiments | [17](17-research-experiments.md) | I/V small bootstrap; D study design | experiments.py, paper-reading protocol | No large-scale replication |
| Projects/interviews/leadership | [19](19-projects-interviews.md) | D assignments | four projects, mock interview, scored rubric | Projects and learner mastery remain unattempted |

## Explicit next-stage gaps

The most valuable next stage is a complete Project B vertical slice with a real generator and validated human evaluation, plus Project A's controlled linear/tree comparison. Then add a trained tiny MLP/character language model, a learned dense-retrieval and BM25 comparison, a durable bounded-agent workflow, and an actual serving load test. These require new implementation and review, not relabeling the current examples.

Advanced elective depth still needed: numerical SVD/PCA and optimization theory; Bayesian graphical models; causal inference and off-policy estimation; full RL/PPO/DPO derivations and experiments; convolution/recurrent/graph training; diffusion derivations; mechanistic interpretability; multi-GPU systems experiments; differential-privacy accounting. These are named as orientations only where present. Specialist research roles require sustained additional work.

## Completion evidence

The repository's validation script checks internal links, generated navigation, code syntax and source/generated consistency. The unit suite checks gradients, probability arithmetic, attention masking through future-input changes, ranking, tenant filtering, deletion, tool validation, idempotency, point-in-time joins, scoped caches and memory arithmetic. A pass supports those stated invariants. It does not imply an unmeasured model is accurate, a service is secure under every attack, or a learner has mastered the material.
