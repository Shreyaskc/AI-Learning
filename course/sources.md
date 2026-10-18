# Primary sources and evidence boundaries

Reference check: 2026-10-18. Paper identity, abstract and stated contribution were checked on the primary arXiv pages; this course does not claim to have reproduced their experiments. Foundational explanations and tiny examples are original educational treatments. Links to living documentation can change. No current model ranking, vendor price, API compatibility or hardware throughput is asserted.

## Foundations and implementation

[scikit-learn: Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) supports the distinction between fitting preprocessing on training data and transforming held-out data. Used in 01 and 06. The course itself has no scikit-learn dependency and does not claim an executed library comparison.

For deeper stable foundations, the authors provide [An Introduction to Statistical Learning](https://www.statlearning.com/) and [Mathematics for Machine Learning](https://mml-book.github.io/). These are optional references, not copied content or prerequisites for the offline labs. Their complete contents were not inspected in this rebuild.

## Architectures and training

[Attention Is All You Need — Vaswani et al., 2017](https://arxiv.org/abs/1706.03762): original Transformer architecture and scaled dot-product attention; 08. Separate architecture definitions from reported translation benchmark results. Decoder-only variants discussed in the course are not all the original encoder-decoder design.

[Training Compute-Optimal Large Language Models — Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556): empirical model/data allocation at a compute budget; 09. Findings depend on tested training regimes, data and objective; no universal current optimal ratio is asserted.

[Training language models to follow instructions with human feedback — Ouyang et al., 2022](https://arxiv.org/abs/2203.02155): one demonstration/ranking/reinforcement-learning pipeline; 09. Its findings do not make RLHF a mandatory stage or establish perfect alignment.

[LoRA — Hu et al., 2021](https://arxiv.org/abs/2106.09685): low-rank adaptation parameterization; 09. Reduced trainable parameter count is not the same as eliminating base-model memory.

[Direct Preference Optimization — Rafailov et al., 2023](https://arxiv.org/abs/2305.18290): preference objective with policy/reference ratios; 09. Preference optimization does not independently prove factual correctness or broad safety.

[On Calibration of Modern Neural Networks — Guo et al., 2017](https://arxiv.org/abs/1706.04599): empirical calibration analysis; deeper follow-up for 06. Calibration in a target population must be evaluated; the course does not reproduce the paper's experiments.

## Retrieval and agents

[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks — Lewis et al., 2020](https://arxiv.org/abs/2005.11401): combines parametric generation with non-parametric retrieval; 10. The lexical extractive lab is an intentionally simpler baseline, not a replication of this trained model.

[Lost in the Middle — Liu et al., 2023](https://arxiv.org/abs/2307.03172): context-position sensitivity in evaluated language-model tasks; 10. Test your own models and distributions instead of assuming a permanent universal effect.

[ReAct — Yao et al., 2022](https://arxiv.org/abs/2210.03629): interleaved reasoning/action method and task evaluations; 11. Production durability, authorization and retry controls are separate engineering requirements.

## Multimodal

[Learning Transferable Visual Models From Natural Language Supervision — Radford et al., 2021](https://arxiv.org/abs/2103.00020): image/text contrastive representation learning; 12. Alignment performance is not proof of complete scene understanding.

[Denoising Diffusion Probabilistic Models — Ho et al., 2020](https://arxiv.org/abs/2006.11239): a probabilistic diffusion approach; 12. The scalar lab illustrates noise arithmetic only and does not train a generative model.

## Hardware and serving

[ZeRO — Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054): partitioning training states for memory efficiency; 14. Actual memory includes activation, buffer and framework effects beyond parameter accounting.

[FlashAttention — Dao et al., 2022](https://arxiv.org/abs/2205.14135): IO-aware exact-attention computation; 14. Hardware speedups are empirical and workload-dependent, not measured here.

[Efficient Memory Management for LLM Serving with PagedAttention — Kwon et al., 2023](https://arxiv.org/abs/2309.06180): KV-cache memory management and serving evaluation; 14. The course reproduces memory arithmetic only, not throughput benchmarks.

## Keeping claims current

For each new integration, record exact model/runtime/tokenizer versions, source date, license, workload, metric and reproduction instructions. Recheck claims when those change. Separate “a paper reported this,” “our experiment observed this,” and “we hypothesize this will help.” Speculation about future intelligence, universal agent reliability or guaranteed interviews is not used as evidence in this course.
