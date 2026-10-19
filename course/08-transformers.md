# 08 · Tokens, embeddings and transformers

Prerequisites: 02–03 and 07. Outcomes: trace text into next-token logits, calculate masked attention, and distinguish architecture from training objective.

Follow a short text through one prediction: text → token IDs → vectors → attention and other transformations → next-token scores. At every stage we will ask what changed and which positions were allowed to contribute. You need dot products, matrix shapes and softmax from [02](02-math.md), plus the layer and residual ideas from [07](07-neural-networks.md).

## Text becomes IDs, then vectors

A tokenizer maps text to discrete IDs from a vocabulary. Word, subword, byte-level and character tokenizers make different tradeoffs in vocabulary size, length, rare strings and multilingual coverage. Byte-pair encoding repeatedly merges frequent symbol pairs in its training corpus; production variants differ in preprocessing and special-token rules. A token is not necessarily a word, character or fixed number of bytes. Token counts require the actual tokenizer and message formatting.

Start with a toy corpus containing `low` and `lower`, represented as characters plus an end marker. If a learned merge joins `l`+`o`, `low` becomes `[lo,w,_]`; if another joins `lo`+`w`, it becomes `[low,_]`, while `lower` becomes `[low,e,r,_]`. This shows the merge mechanism; production BPE requires corpus-wide pair counts, deterministic tie-breaking, normalization and special-token handling. It is not legitimate to infer exact provider token IDs from this toy.

An embedding table E with V_vocab rows (one per vocabulary ID) and d columns looks up a d-dimensional vector for each ID. These coordinates are learned to serve an objective; they are not literal containers of meaning. Similarity depends on model, layer, pooling, normalization and training. A document embedding often pools many contextual token representations; it is not automatically the same artifact as a vocabulary embedding table.

Define three toy token IDs 0, 1 and 2, with embedding rows E0=(1,0), E1=(0,1), E2=(1,1). Use the input sequence [0,1], so X is [[1,0],[0,1]], shape 2×2.

Position information matters because pure attention without a position mechanism does not encode sequence order by itself. Original transformers used position encodings; modern architectures may use learned positions or rotations such as RoPE. Position mechanisms and length extrapolation require empirical evaluation rather than assuming unlimited context.

## One attention head, with shapes

At each position, a query vector is compared with key vectors at permitted positions. After scaling and masking, softmax converts comparison scores to weights; those weights combine value vectors. Queries and keys control the weighting; values supply the content being mixed. These are learned calculations, not conscious searches.

The two-position example below will make that operation concrete. For its general notation, T counts positions and d_model counts coordinates in each input vector. Let X be T×d_model. Compute Q=XW_Q, K=XW_K and V=XW_V. Q and K are T×d_k; V is T×d_v. Scores S=QKᵀ/sqrt(d_k) have shape T×T. Add a mask M with zero for allowed positions and negative infinity for prohibited ones. Row-wise softmax produces A; output is AV with shape T×d_v.

Queries and keys determine weights; values supply mixed content. The sqrt(d_k) scale controls typical score magnitude under a simplifying independent-unit-variance argument; it is not a probability correction. Multi-head attention computes multiple such projections and combines their outputs, allowing different learned interactions. See [the original Transformer paper](https://arxiv.org/abs/1706.03762) for the architecture and scaled attention definition.

Worked example: let the last query be (1,0), keys (1,0) and (0,1), values (2,0) and (0,4). d_k=2, so scores are (.707,0), softmax weights about (.670,.330), and output about (1.340,1.321). These are weighted coordinates, not a retrieved sentence or proof of reasoning. At the first position in a causal decoder the second key must be masked; its weight becomes zero and output is exactly (2,0).

Choose W_Q=[[1,0],[1,0]], W_K=I (the 2×2 identity matrix [[1,0],[0,1]], which leaves coordinates unchanged) and W_V=[[2,0],[0,4]]. Then Q=[[1,0],[1,0]], K=[[1,0],[0,1]], V=[[2,0],[0,4]]. Multiplying gives QKᵀ=[[1,0],[1,0]]. Scaling by sqrt(2) and applying a causal mask gives rows [.707,-infinity] and [.707,0]. Softmax produces [[1,0],[.669762,.330238]]. AV is [[2,0],[1.339523,1.320954]], shape 2×2.

Run [attention.py](../labs/attention.py), which computes every query position and verifies the causal mask. Change a future token's value and check that earlier outputs stay unchanged.

## A block and the language-model head

A typical decoder block uses normalization, attention, residual addition, then a position-wise feedforward network with another residual path. Exact order and activation vary. The feedforward network transforms each position separately; attention mixes across positions. Repeating blocks produces contextual representations. A final projection produces vocabulary logits: one unnormalized score per possible next token. Softmax turns those scores into next-token probabilities.

Decoder-only models use causal masks for autoregressive generation. Encoder models can attend bidirectionally to input positions and are useful for representation tasks. Encoder-decoder models let a decoder attend to an encoded source as well as earlier outputs. The original Transformer was encoder-decoder; “transformer” does not mean every model is a decoder-only chat model.

During teacher-forced training, a shifted input/target sequence supplies many next-token losses in parallel, with masks preventing future-target leakage. During ordinary autoregressive generation, sample or select one next token, append it, and repeat. The sampling distribution may use temperature: softmax(z/tau). Smaller positive temperature tau sharpens it; this does not guarantee correctness. Top-p retains a probability-mass prefix and renormalizes; decoding changes output statistics and may affect evaluation.

## Representative implementation: IDs to a complete tiny block

Continue the two-token calculation through residuals, normalization and vocabulary scores. The fixed small matrices expose operations; they were not trained to understand language.

For a transparent post-normalization block, use identity output projection, add residual X, then layer-normalize each row: `LN(r)=(r-mean(r))/sqrt(mean((r-mean(r))²)+epsilon)`. On the first row r=(3,0), mean=1.5, variance=2.25 and epsilon=1e-5, giving approximately (.999998,-.999998). Set the feedforward map to `FF(h)=ReLU(h I) I` with zero biases. It yields approximately (.999998,0) on that row. Add its residual and normalize again: the row remains approximately (1,-1). These identity choices are educational constants; learned feedforward maps are generally wider and different.

Choose vocabulary projection U=[[1,0,-1],[0,1,0]], shape 2×3. A final representation near (1,-1) yields vocabulary logits near (1,-1,-1), whose softmax is approximately (.787,.107,.107). Selecting or sampling a token from this distribution gives the next ID; a decoder converts IDs back to text. The full trace is implemented in [attention.py](../labs/attention.py), including the block and logits. It does not train these matrices, so the output has no linguistic capability claim.

## Costs and misconceptions

Dense self-attention forms T² pairwise scores per head, with compute proportional to T²d for the attention mixing part. Other projections and feedforward layers also cost compute; do not describe the whole model using only T². Padding and masks waste work unless implementations avoid it. Attention weights are not reliable standalone causal explanations of predictions.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

1. With T=10,d_k=4,d_v=6, what are shapes of S and AV? Solution: 10×10 and 10×6.
2. Why can teacher forcing train positions together while decoding is sequential? Solution: training already knows target prefixes; inference must obtain each newly generated prefix.
3. Does lower temperature solve hallucinations? Solution: no; it can make a wrong high-probability answer more repeatable.
1. Change X at position 1 from (0,1) to (4,-3), recompute Q,K,V and the entire block. Which previous outputs may change? Solution: position 0 cannot change under the causal mask because all permitted dependencies originate at position 0; position 1 can change. Test all output coordinates, not just row-weight sums. Without the mask, earlier outputs can change; the lab tests that counterexample too.
2. An all-masked row produces NaNs. Diagnose it. Solution: softmax of all negative infinity is undefined because no allowed value exists. Ensure a valid attention pattern (for example each valid decoder position can see itself), and handle padded query rows explicitly. Do not turn NaNs into arbitrary probabilities and call it fixed.
3. You need a document classifier, not generation. Is a causal decoder mandatory? Solution: no. A bidirectional encoder can represent complete input context efficiently for classification; compare quality/latency with simpler baselines. For translation or conditional generation, encoder-decoder can be appropriate; for next-token generation, causal decoder is natural. Architecture follows task and evidence.
4. A colleague reads attention weights as “the causal reason.” What would test that interpretation? Solution: intervene on inputs or components under a controlled analysis, compare alternative paths and evaluate output changes. Even interventions have assumptions; the weight matrix alone is insufficient.

Mastery gate: reconstruct shapes and the first row by hand; run the projection/block tests; explain future-input invariance; then solve the changed-input exercise before reading output. Completing these tasks demonstrates a minimal attention implementation, not mastery of training a full transformer or interpreting a large model.

## Interview rehearsal and vocabulary

Interview: describe the text-to-logits pipeline; calculate masked attention; discuss context scaling and architecture choices under latency constraints. Vocabulary: tokenizer, BPE, embedding, contextual representation, query, key, value, mask, head, logit, autoregressive, teacher forcing.

## What to carry forward

Attention chooses a weighted mixture of permitted value vectors; the rest of the block transforms that mixture into next-token scores. A causal mask is a dependency rule, not a factuality guarantee. Next, [learn how the model acquires its parameters and behavior](09-llm-training.md).
