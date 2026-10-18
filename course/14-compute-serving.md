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

## Practical extension: measure a bounded local service

Run `python3 labs/serving_experiment.py`. This performs a small real-time load experiment with worker threads and a bounded queue, not a mathematical event simulation. It makes no network calls and performs no model inference. The synthetic service hashes a small payload and sleeps for an assumed cost of .004 seconds per batch plus .002 seconds per item. Sleeping approximates an I/O/wait component and preserves CPU for concurrent work; it is not a neural-network kernel model.

The open-loop producer schedules arrivals independently of completions. Queue insertion is nonblocking; when capacity eight is full, the request is counted as rejected. Two workers process batches of at most one or four items. Use a monotonic clock for arrival, start and finish. Queue latency is start-arrival; service latency is finish-start; end-to-end is finish-arrival. Percentiles use nearest rank: sort n values and select index ceil(p*n)-1. Report accepted request counts and rejected fraction alongside latency, because rejecting hard requests can make the remaining latency look attractive.

The committed [local result](../review/evidence/serving-local.json) records Python 3.14.6, Darwin arm64, 12 logical CPUs, workload assumptions, actual observed arrival window and queue depth. No hostname or user prompts are logged. A single short run produced:

| Scenario | Offered / completed / rejected | End-to-end p95 | Mean queue time | Completed requests/s including drain |
| --- | --- | --- | --- | --- |
| Underload, batch 1 | 60 / 60 / 0 | 9.13 ms | .032 ms | 100.14 |
| Overload, batch 1 | 120 / 24 / 96 | 41.98 ms | 24.10 ms | 244.19 |
| Overload, batch up to 4 | 120 / 34 / 86 | 35.22 ms | 12.33 ms | 443.01 |

These are measured mock-request rates, never tokens/s or GPU throughput. The producer offered roughly 2,010 requests/s in the overload cases, far exceeding the mock workers' capacity. Batching improved accepted throughput in this workload because its assumed fixed cost is amortized. Per-request service time inside a batch increased, and most offered requests were still rejected. This does not establish that batching always reduces latency or that these settings meet a real SLO.

The observed service time can exceed the requested sleep duration because operating-system scheduling and timer resolution add delay. A p99 over 24 completed requests is the largest observation under this convention; it cannot establish a stable production tail. Repeat runs under documented conditions and use larger representative samples for serious capacity claims. The test suite checks accounting, nonnegative decomposition and queue bounds, without brittle assertions that one timing must be faster on every host.

Exercises: (1) Why is 244 completed requests/s not the same as 2,010 offered requests/s? Solution: the queue rejects excess arrivals, and completed throughput includes drain time; both numerator and observation window differ. (2) Can you call batch 4 “safe” from the p95 alone? Solution: no; rejection rate is about 71.7% and accepted-only latency omits those failed requests. (3) Increase the fixed cost while keeping per-item cost unchanged. Solution: larger batches may amortize more work, but filling/waiting and queue fairness can alter end-to-end results. Measure rather than assuming. (4) Replace the mock with a real inference callable. Solution: separately label model/runtime/hardware, prompt and output distributions, cache state, first-token/inter-token metrics and quality; preserve admission and failure accounting.

Mastery gate: reproduce a new report without overwriting the historical evidence, calculate completed+rejected=offered, explain the latency components, and identify the mock cost assumptions. Real-model load tests, token-aware continuous batching, quantization and distributed serving remain beyond the measured evidence here.
