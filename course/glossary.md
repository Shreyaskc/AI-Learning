# Glossary and concept index

Use this index to return to the first explanation. A definition is a retrieval cue, not a replacement for the worked lesson. Symbols are defined locally; a parameter named T in one source need not have the same meaning in another.

| Term | Meaning | First explanation | Short example | Aliases |
| --- | --- | --- | --- | --- |
| AI | Broad field of search, planning, learning and related intelligent behavior | [01](01-foundations.md) |  |  |
| Machine learning | Improving a behavior from data under an objective | [01](01-foundations.md) |  |  |
| Deep learning | Learning with multiple neural transformations | [01](01-foundations.md) |  |  |
| Generative model | Model of a data distribution used to describe or sample data | [01](01-foundations.md) |  |  |
| Parameter | A number fitted from training data that controls a model’s output. | [01](01-foundations.md) | A learned coefficient multiplies package weight when estimating delivery cost. | parameters; model parameter; model parameters |
| Hyperparameter | A setting chosen outside the parameter-fitting process to control a model or its training. It may be selected using validation data. | [01](01-foundations.md) | Maximum tree depth is chosen before fitting a delivery-time decision tree. | hyperparameters |
| Feature | An input measurement available to a model when it makes a prediction. | [01](01-foundations.md) | Package weight can be an input to a delivery-cost model. | features |
| Target | The outcome a supervised model is trained to predict. | [01](01-foundations.md) | Observed delivery duration is the target for a delivery-time model. | targets |
| Example | One case in a dataset. In supervised learning, a labeled example contains inputs and the corresponding target. | [01](01-foundations.md) | One parcel’s measurements together with its observed delivery duration form a labeled example. | examples; training example; training examples |
| Training | The process of fitting model parameters using data and a learning objective. | [01](01-foundations.md) | Training adjusts model coefficients using historical parcel deliveries. |  |
| Inference | Applying a fitted model to inputs to produce outputs. | [01](01-foundations.md) | Inference estimates the delivery duration for a new parcel using the fitted model. |  |
| Self-supervised learning | Deriving training targets from data itself | [01](01-foundations.md) |  |  |
| Leakage | Using information unavailable under the intended evaluation/deployment contract | [01](01-foundations.md) |  |  |
| Baseline / ablation | Reference behavior / controlled removal of a component | [01](01-foundations.md) |  |  |
| Tensor / shape / dtype | Multi-axis array / dimensions / numeric representation | [02](02-math.md) |  |  |
| Dot product | Sum of coordinate-wise products | [02](02-math.md) |  |  |
| Norm / cosine | Vector magnitude / normalized directional similarity | [02](02-math.md) |  |  |
| Rank / SVD / PCA | Independent-direction count / matrix factorization / variance-preserving projection | [02](02-math.md) |  |  |
| Logit | Unnormalized score; binary log odds in logistic regression | [02](02-math.md), [05](05-classical-ml.md) |  |  |
| Softmax | Exponentiate and normalize scores into positive weights | [02](02-math.md) |  |  |
| Gradient / chain rule | Vector of partial derivatives / derivative rule for composition | [02](02-math.md) |  |  |
| Conditional probability | Probability given an observed event | [03](03-probability.md) |  |  |
| Prior / likelihood / posterior | Before-evidence distribution / probability of evidence under a hypothesis / updated distribution | [03](03-probability.md) |  |  |
| Expectation / variance | Weighted average / average squared centered deviation | [03](03-probability.md) |  |  |
| Standard error | Sampling spread of an estimator, rather than spread of individual outcomes | [03](03-probability.md) |  |  |
| Confidence / credible interval | Frequentist procedure coverage / Bayesian posterior interval | [03](03-probability.md) |  |  |
| Entropy / cross-entropy | Expected self-surprise / expected surprise under predicted distribution | [03](03-probability.md) |  |  |
| KL divergence | Asymmetric expected log probability ratio between distributions | [03](03-probability.md) |  |  |
| Confounding | A common influence that can make association misleading about intervention effects | [03](03-probability.md) |  |  |
| Aleatoric / epistemic | Outcome variability under information / uncertainty about model knowledge | [03](03-probability.md) |  |  |
| Empirical risk | Average sample loss | [04](04-optimization.md) |  |  |
| SGD / batch / epoch | Stochastic gradient updates / update's examples / pass through training data | [04](04-optimization.md) |  |  |
| Regularization | Constraints or penalties favoring selected solution properties | [04](04-optimization.md) |  |  |
| Momentum / Adam | Gradient-history smoothing / adaptive moment-based optimizer | [04](04-optimization.md) |  |  |
| Underfitting / overfitting | Insufficient relevant fit / sample fit failing to generalize | [04](04-optimization.md) |  |  |
| Logistic regression | Sigmoid of an affine score for a binary target | [05](05-classical-ml.md) |  |  |
| Margin / kernel | Separation from a boundary / implicit feature-space similarity construction | [05](05-classical-ml.md) |  |  |
| Bagging / boosting | Averaging resampled learners / sequential objective-improving learners | [05](05-classical-ml.md) |  |  |
| Precision / recall | Fraction of flagged cases truly positive / fraction of positives caught | [06](06-evaluation.md) |  |  |
| Calibration | Predicted event probabilities matching observed rates in a population | [06](06-evaluation.md) |  |  |
| Brier score | Mean squared probability error for a binary outcome | [06](06-evaluation.md) |  |  |
| Contamination | Evaluation content or information entering training/development in a compromising way | [06](06-evaluation.md) |  |  |
| Drift / abstention | Distribution change / choosing not to automate an unsupported case | [06](06-evaluation.md) |  |  |
| Activation / residual | Nonlinear transformation / added identity pathway | [07](07-neural-networks.md) |  |  |
| Backprop / autograd | Reverse chain-rule propagation / software differentiation of a computation graph | [07](07-neural-networks.md) |  |  |
| Convolution / recurrence | Shared local filters / repeated state update over a sequence | [07](07-neural-networks.md) |  |  |
| Tokenizer / BPE | Text-to-ID conversion / learned symbol-pair merge procedure | [08](08-transformers.md) |  |  |
| Embedding | Learned vector representation under an objective | [08](08-transformers.md) |  |  |
| Query / key / value | Projections controlling attention matching / matching / content mixture | [08](08-transformers.md) |  |  |
| Causal mask | Prohibits dependence on future sequence positions | [08](08-transformers.md) |  |  |
| Autoregressive / teacher forcing | Conditional next-step generation / training with known target prefixes | [08](08-transformers.md) |  |  |
| Temperature / top-p | Score scaling / probability-mass-prefix sampling filter | [08](08-transformers.md) |  |  |
| Perplexity | Exponentiated mean token negative log likelihood | [09](09-llm-training.md) |  |  |
| SFT / PEFT / LoRA | Supervised adaptation / limited-parameter adaptation / low-rank update parameterization | [09](09-llm-training.md) |  |  |
| Policy / reward / return | Action distribution / scored feedback / aggregate future reward | [09](09-llm-training.md) |  |  |
| RLHF / DPO | Human-feedback reinforcement-learning family / direct preference objective | [09](09-llm-training.md) |  |  |
| Reward hacking | Improving a proxy without improving intended benefit | [09](09-llm-training.md) |  |  |
| BM25 / ANN | Lexical ranking family / approximate nearest-neighbor search | [10](10-retrieval-rag.md) |  |  |
| Bi-encoder / cross-encoder | Independent query/document representations / joint pair processing | [10](10-retrieval-rag.md) |  |  |
| Reranker / hybrid retrieval | Reordering candidates with more work / combining retrieval signals | [10](10-retrieval-rag.md) |  |  |
| RAG / grounding / provenance | Retrieval-conditioned generation / evidence support / traceable source origin | [10](10-retrieval-rag.md) |  |  |
| Tool / workflow / agent | Callable operation / fixed control flow / model-selected action loop | [11](11-agents-memory.md) |  |  |
| Idempotency | Repeating a logical operation key does not duplicate intended effects | [11](11-agents-memory.md) |  |  |
| Context / memory | Invocation working set / persistent information across interactions | [11](11-agents-memory.md) |  |  |
| Knowledge graph / entity resolution | Typed entity relations / deciding identity across references | [11](11-agents-memory.md) |  |  |
| OCR / WER / diarization | Extracting text from pixels / transcription error rate / who spoke when | [12](12-multimodal.md) |  |  |
| VAE / GAN / diffusion | Probabilistic latent model / adversarial generator training / noise-and-denoise model family | [12](12-multimodal.md) |  |  |
| Event / availability time | When an event happened / when it was known to the system | [13](13-data-platforms.md) |  |  |
| Feature store / backfill / skew | Managed feature definitions/storage / historical materialization / inconsistent train/serve behavior | [13](13-data-platforms.md) |  |  |
| FLOP / bandwidth | Floating-point operation / bytes transferred per unit time | [14](14-compute-serving.md) |  |  |
| Data / tensor / pipeline parallelism | Split examples / split operations / split layer groups | [14](14-compute-serving.md) |  |  |
| Collective / sharding | Coordinated multi-worker communication / partitioned state | [14](14-compute-serving.md) |  |  |
| Prefill / decode / KV cache | Prompt processing / next-token steps / stored prior keys and values | [14](14-compute-serving.md) |  |  |
| Quantization | Reduced-precision representation with numerical and runtime tradeoffs | [14](14-compute-serving.md) |  |  |
| Speculative decoding | Draft proposals plus target verification under an acceptance procedure | [14](14-compute-serving.md) |  |  |
| SLI / SLO / error budget | Measured indicator / target / allowed misses under the target | [15](15-operations.md) |  |  |
| Shadow / canary / rollback | Noncontrolling evaluation / bounded exposure / restore compatible prior behavior | [15](15-operations.md) |  |  |
| Injection / poisoning / exfiltration | Untrusted content redirects control / corrupts learned evidence / unauthorized data transfer | [16](16-security-responsibility.md) |  |  |
| Differential privacy | Formal bounded output-distribution change under neighboring datasets | [16](16-security-responsibility.md) |  |  |
| Equalized odds / calibration | Matched group error rates / probability validity within a population | [16](16-security-responsibility.md) |  |  |
| Power / p-value / effect size | Detection probability under an alternative / null-model incompatibility measure / magnitude of difference | [17](17-research-experiments.md) |  |  |
| Horizon / rolling origin | Forecast distance / sequential historical forecast evaluation | [18](18-domain-electives.md) |  |  |
| Implicit feedback / bandit | Behavioral signal confounded with exposure / action learning with partial feedback | [18](18-domain-electives.md) |  |  |

## Symbols and units

n is usually example count, d feature width, w model coefficients, b bias, y target, p predicted probability, eta learning rate, lambda regularization strength. In attention, T is sequence length and d_k key/query head width; tau is sampling/contrastive temperature. Context specifies any different convention. GB means 10^9 bytes; GiB means 2^30 bytes. A probability has no physical unit; latency, throughput and money do.
