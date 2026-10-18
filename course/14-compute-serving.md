# 14 · Training compute, hardware and inference serving

Prerequisites: 07–09 and 13. Outcomes: estimate memory and capacity with explicit assumptions, separate prefill from decode, and reason about parallelism and efficiency. Numeric estimates here are hypothetical arithmetic, not hardware benchmarks.

## What a GPU accelerates

A CPU excels at flexible control and diverse workloads; a GPU provides many parallel arithmetic units with high-bandwidth device memory. Model execution uses matrix operations, kernels, memory movement, synchronization and communication. Floating-point formats trade range, precision and storage. FP32 typically uses four bytes, BF16/FP16 two bytes, and nominal INT8 one byte per stored value; scales, metadata and packing alter actual memory. BF16 and FP16 have different exponent/mantissa allocations, so equal byte size does not mean identical numerical behavior.

A kernel can be compute-bound when arithmetic throughput limits it, bandwidth-bound when moving bytes limits it, or overhead/communication-bound. Arithmetic intensity is operations per byte moved. A roofline argument bounds performance by the smaller of compute capacity and memory bandwidth times arithmetic intensity. Peak advertised FLOP/s is not sustained application throughput.

## Training memory and parallelism

A model with P parameters may need weights, gradients, optimizer states, activations and temporary buffers during training. A rough mixed-precision Adam accounting sometimes uses 2 bytes for weights, 2 for gradients, 4 for master weights and 8 for two FP32 moments: 16P bytes before activations. Actual frameworks and configurations differ; state assumptions rather than quoting 16 as universal. At P=1 billion this subtotal is 16 GB in decimal units, plus potentially substantial activations.

Data parallelism replicates a model over workers, each processing different examples, then combines gradients. Tensor parallelism splits operations or tensors across workers and requires layer-level communication. Pipeline parallelism places groups of layers on different workers and passes activations, with scheduling bubbles. Sharded data parallelism partitions states across workers; [ZeRO](https://arxiv.org/abs/1910.02054) describes staged partitioning of optimizer state, gradients and parameters. Adding GPUs can become limited by collectives, network bandwidth, synchronization, imbalance or input pipelines.

An all-reduce combines tensors across workers and returns the result to each. A ring all-reduce of S bytes per worker over N workers moves roughly `2(N-1)S/N` bytes per worker in the idealized bandwidth accounting; latency and topology add cost. For N=4,S=1 GB, that is 1.5 GB per worker, not zero overhead. Gradient accumulation can raise effective batch without storing all examples at once, but changes update frequency and may affect optimization.

Checkpointing saves recoverable model/optimizer/data-progress state. Activation checkpointing instead recomputes some intermediates during backprop to save activation memory. They solve different problems. Reproducibility also needs RNG and sampler state; distributed failure recovery must avoid skipped or duplicated data beyond the declared policy.

## Prefill and decode

Prefill processes the prompt and builds attention state. Decode generates new tokens step by step. KV caching stores prior keys and values so ordinary autoregressive decode avoids recomputing them every step; it consumes memory that grows with active sequences and context length. It does not make all attention work disappear.

For L layers, T cached positions, H_kv key/value heads, head width d and b bytes/value, an idealized single-sequence KV size is `2 L T H_kv d b`. The 2 accounts for keys and values. With L=32,T=4096,H_kv=8,d=128,b=2, size is 536,870,912 bytes, .5 GiB. Sixteen such sequences need 8 GiB before weights, allocator overhead, temporary buffers and other state. Grouped-query attention uses fewer KV heads than query heads, changing this estimate.

A 7-billion-parameter model at two bytes/parameter has a 14 GB weight payload, about 13.04 GiB; that is not total VRAM required. Quantization can lower weight memory and alter bandwidth/compute demands, but introduces accuracy, kernel availability and scale/zero-point overhead. Quantize, evaluate and benchmark the actual workload rather than treating compression as a free lunch.

Run [platform.py](../labs/platform.py) to reproduce these estimates and modify batch/context assumptions. It does not load or benchmark a GPU model.

## Serving techniques and their limits

Batching amortizes model execution across requests but can add waiting and mix lengths. Continuous batching lets requests enter/leave generation batches over time. Admission control and per-tenant quotas protect the queue from overload. Prefix caching reuses compatible prompt work; cache correctness depends on model, exact prefix, tokenization and access scope. [PagedAttention](https://arxiv.org/abs/2309.06180) studies block-based KV memory management. [FlashAttention](https://arxiv.org/abs/2205.14135) reduces memory traffic for exact attention through IO-aware tiling; it does not abolish the dense attention arithmetic dependency on sequence length.

Speculative decoding proposes tokens using a cheaper draft and verifies them with a target. Correct acceptance procedures can preserve the target sampling distribution under their assumptions. Benefit depends on acceptance rate, draft overhead, batch shape and hardware; verification is not proof that proposed statements are factually true.

Measure time to first token, inter-token latency, end-to-end latency, throughput, errors and quality for realistic length distributions. Little's law `N=lambda*W` relates average in-system concurrency N, arrival rate lambda and average response time W in a stable system. At 20 requests/s and mean 2 s, average in-flight requests is 40. This does not prove 40 slots can satisfy tail SLOs under bursts.

## Practice and solutions

1. Doubling context doubles the idealized KV size. Does it double total runtime? Solution: not necessarily; prefill/decode composition, attention work, batch efficiency and other operations differ.
2. Why does tensor parallelism across a slow network disappoint? Solution: frequent layer communication can dominate saved compute. Measure topology and collectives.
3. Would you buy more GPUs for slow p99? Solution: first inspect queueing, prompt/output distributions, tenant skew, memory saturation and downstream tools; capacity only helps the actual bottleneck.

Interview: compute weight/KV memory; compare data/tensor/pipeline parallelism; defend a capacity plan with assumptions, benchmarks, headroom, isolation, failure handling and cost per successful task. Vocabulary: FLOP, bandwidth, arithmetic intensity, BF16, collective, sharding, prefill, decode, KV cache, quantization, batching, speculative decoding.
