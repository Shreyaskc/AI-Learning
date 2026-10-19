# 09 · LLM pretraining, adaptation and alignment

Prerequisites: 04, 06 and 08. Outcomes: separate training stages, compute language-model loss, and reason about adaptation and reward limitations.

## Pretraining learns a predictive distribution

An autoregressive model factors a sequence probability as `P(t1,...,tT)=product_i P(t_i|t_<i)`. Maximizing likelihood is minimizing mean negative log probability of observed tokens. For three targets assigned probabilities .5,.25,.8, mean loss is `-(log(.5)+log(.25)+log(.8))/3≈.768` nats/token. Perplexity is exp(loss)≈2.154. Compare perplexities only under compatible tokenization, datasets and scoring conventions; a lower number on one corpus is not a universal capability ranking.

Data pipelines select, deduplicate, filter, license, tokenize and mix documents. They define what the model can learn and what sensitive material it may memorize. Contamination control and dataset documentation belong before a final benchmark. More raw data is not automatically more useful data. Synthetic data can provide targeted examples but can also amplify teacher errors, reduce diversity or leak evaluation content.

Empirical scaling studies fit relationships between loss, parameters, tokens and compute within tested regimes. [Chinchilla](https://arxiv.org/abs/2203.15556) studied compute allocation between model size and training tokens. Treat the observed tradeoff as a study result under its setup, not a permanent universal tokens-per-parameter law or a direct deployment-cost optimum.

## Supervised adaptation

Supervised fine-tuning (SFT) trains on desired input/output demonstrations. It teaches formats and behaviors, but can also add knowledge and alter existing behavior. Mask prompt tokens as appropriate when optimizing assistant responses; avoid accidentally teaching the model to reproduce hidden or irrelevant fields. Full fine-tuning updates all selected model weights; parameter-efficient methods update a smaller subset or added components.

LoRA represents a weight update as `DeltaW=BA` with rank at most r. For a 1024×1024 matrix, full tuning has 1,048,576 coefficients; r=8 adapters have 2×1024×8=16,384, excluding other trainable components. Lower trainable parameter count reduces optimizer/gradient storage for the update, but the base model still occupies memory. [LoRA's primary paper](https://arxiv.org/abs/2106.09685) motivates and evaluates this parameterization. Quantized adapter training adds numerical and implementation choices; evaluate quality and memory in your workload.

## Preferences and reinforcement learning

A common preference pipeline starts with demonstrations, collects comparisons between candidate answers, trains a reward model, then optimizes the policy with a penalty for departing too far from a reference. [InstructGPT](https://arxiv.org/abs/2203.02155) is one concrete human-feedback recipe; it is not a mandatory universal sequence for all language models.

Reinforcement learning vocabulary: state is information available to choose; action changes the interaction; policy maps state to action distribution; reward scores a transition or outcome; return aggregates future rewards, often with discount gamma. A value function estimates expected return. Policy gradients adjust action probabilities according to estimated advantage (better or worse than a baseline). Credit assignment asks which earlier decisions contributed to later outcomes. Exploration can discover successful strategies but may be costly or unsafe in a real system.

Preference optimization can also use paired chosen/rejected responses without an explicit online reward-learning loop. [DPO](https://arxiv.org/abs/2305.18290) derives a specific objective involving policy/reference log-probability ratios. It still depends on preference data, reference and optimization assumptions. Preferences are measurements from particular raters and tasks, not a guarantee of truth or a universal social objective.

Reward hacking occurs when an optimized proxy improves without the intended benefit. If a judge prefers longer answers, a policy may inflate length. Separate reward training data from evaluation, audit failure slices, and use external task checks where possible. Outcome-verifiable domains can support rewards such as passing independent code tests; passing tests still does not prove all desired behavior.

## Capabilities, reasoning and limits

Posttraining may improve instruction following, tool use and task performance. Reasoning-oriented training and test-time search spend compute to improve certain tasks; transfer, cost and reliability must be measured. Do not treat a displayed reasoning narrative as a faithful trace of internal causation. Unsupported generation has multiple causes: missing knowledge, ambiguous prompts, misleading context, optimization incentives and decoding behavior. Next-token prediction describes a common objective, not a complete explanation of every failure.

Run the loss and low-rank parameter calculations in [attention.py](../labs/attention.py). No large neural-model pretraining or GPU fine-tuning is executed in this course. Such experiments require separate data, licensing, hardware and evaluation plans.

1. Why might a fine-tuned model still need retrieval? Solution: current, authorized and attributable facts may change faster than retraining; adaptation and external knowledge serve different purposes.
2. Does high reward establish safety? Solution: only for what reward and evaluation actually measure, subject to gaming and generalization gaps.
3. Why can lower pretraining loss coexist with worse user behavior? Solution: objectives, task distributions and output preferences differ.

Interview: derive sequence loss; contrast SFT, LoRA, RLHF and DPO; then design an adaptation experiment with a reference baseline, privacy review, clean test set and rollback. Vocabulary: pretraining, SFT, PEFT, LoRA, policy, reward, return, advantage, RLHF, DPO, reward hacking, perplexity.

## Practical extension: actually train a tiny language model

Run `python3 labs/language_model.py`. It fits a character bigram model, selects smoothing on validation data, evaluates held-out negative log likelihood and samples a sequence. It is a genuine learned probabilistic model, but not a neural network, pretrained LLM or question-answering system.

For each previous character a, training counts how often character b follows it. Add begin/end symbols and an unknown symbol. Estimate `P(b|a)=(count(a,b)+alpha)/(count(a)+alpha*V)`, where V is the number of predicted symbols and alpha>0 adds smoothing. With observed transitions a→b twice and a→c once, V=4,alpha=.5, P(b|a)=(2+.5)/(3+2)=.5, P(c|a)=1.5/5=.3, and each of two unseen continuations gets .1. The row sums to one. Without smoothing, an unseen test transition would have zero probability and infinite negative log likelihood.

The vocabulary and counts come only from training strings. An unseen held-out character maps to `<UNK>`; it does not silently expand the trained vocabulary. This trades detail for a well-defined distribution. Evaluation includes the end symbol and reports unknown count. Different unknown policies and tokenization change perplexity, so document them before comparing models.

The corpus consists of three short invented cat/dog sentences repeated eight times. Alpha is selected from {.1,.5,1} on two validation sentences. The final two sentences include unseen characters. Recorded alpha=.1 gives held-out NLL≈1.3990 nats/token and perplexity≈4.0513 over 37 tokens including end markers, versus unigram NLL≈2.8748. These tiny, highly related strings do not establish general language capability. The seeded sample `cat og og a ma cathemat cand on og can og san.` shows local character associations without coherent semantics. Lower perplexity can coexist with nonsense.

## Supervision masks and a preference calculation

SFT often optimizes only desired response positions. If prompt/response target probabilities are [.01,.8,.7] and mask is [0,1,1], mean supervised loss is `-(log(.8)+log(.7))/2≈.289909`. Including the .01 prompt probability instead changes both the objective and normalization. `masked_mean_nll` rejects an all-zero mask rather than dividing by zero. In a real causal model, response tokens still attend to the prompt; masking the prompt's loss does not remove prompt conditioning.

For a toy DPO pair, define margin `m=beta*(log(pi(chosen)/pi_ref(chosen))-log(pi(rejected)/pi_ref(rejected)))` and loss `-log(sigmoid(m))`. A policy equal to its reference has margin zero and loss log(2)≈.693147. With reference probabilities .5/.5, policy .8/.2 and beta=.1, margin=.1*log(4)≈.138629 and loss≈.626233. The lab calculates this stably. The objective rewards relative preference under the pair; it does not prove the chosen answer is true. This is a scalar objective demonstration, not trained DPO or PPO.

Exercises: (1) Compute P(b|a) after adding one more a→b transition to the worked example. Solution: (3+.5)/(4+2)=7/12≈.583333. (2) Add a held-out-only character and verify that vocabulary remains unchanged and unknown count increases. (3) Why not pick alpha using test perplexity? Solution: that would make test data choose the fitted procedure. (4) Increase chosen-answer probability for a false but rater-preferred answer. Solution: DPO's loss may improve while factual utility worsens; evaluation must measure correctness independently.

Mastery gate: explain counts→conditional distribution→loss→sampling, trace one held-out transition, and distinguish a trained bigram, an SFT mask and a preference objective from executed LLM fine-tuning. Actual transformer adaptation and its forgetting/privacy tradeoffs remain unexecuted.

## Inspect decoding distributions

`decoding_distribution` in the language-model lab implements positive temperature, then top-k selection, then top-p selection within the top-k-renormalized distribution. The order is explicit because library conventions can differ. For logits [2,1,0] at tau=1, probabilities are approximately [.6652,.2447,.0900]. Top-k=2 removes the last token and renormalizes to [.7311,.2689,0]. Top-p=.8 then retains both remaining tokens because the first alone has mass below .8. Lower temperature sharpens scores; it does not add evidence or guarantee truth.

The helper rejects temperature zero instead of dividing by zero; greedy argmax is a separate limiting decision rule. Real runtimes can still vary under nominally deterministic settings through kernels, scheduling or provider changes. The bigram's seeded sampling is reproducible in this specified local implementation, not a universal reproducibility claim for every LLM API.
