# 10 · Retrieval, ranking and grounded generation

Prerequisites: 02, 06, 08–09. Outcomes: implement lexical retrieval, separate ranking from generation quality, and design authorized evidence assembly.

## Find evidence before writing an answer

A search system maps a query to candidate documents. An inverted index maps terms to postings containing document IDs and possibly positions. BM25 scores query-term matches using term rarity, saturation and document-length normalization. Dense retrieval encodes queries and documents into vectors and scores their relationships. A learned embedding can connect paraphrases absent exact overlap, but may miss exact identifiers, negation or domain distinctions. Lexical and dense approaches often complement each other; evaluate on labeled queries rather than assuming one always wins.

Exact vector search compares every candidate. Approximate nearest-neighbor (ANN) structures reduce search work by accepting some missed neighbors. Graph-based indexes such as HNSW navigate neighbor links; quantization can compress vectors. Index settings trade memory, build/update cost, latency and recall. ANN recall relative to exact neighbors is distinct from relevance recall against human labels. A perfect approximation to a poor embedding still retrieves poorly.

Candidate generation favors recall; a reranker spends more work on a smaller set. A bi-encoder embeds query and document independently, enabling stored vectors. A cross-encoder jointly processes both and can inspect detailed interactions, usually at higher per-pair cost. Hybrid retrieval can combine lexical and dense candidate lists with reciprocal rank fusion: score(d)=sum_lists 1/(k+rank_list(d)). Here k is a smoothing constant, not the number of results; rank starts at 1. Scores are ranking tools, not relevance probabilities.

## Chunking and access are part of correctness

Chunking divides sources into units that fit retrieval and context budgets. Preserve headings, tables and identifiers; arbitrary character cuts may separate a claim from its qualification. Overlap can recover boundaries but increases duplicate tokens and index size. Store source ID, version, offsets, timestamp, ownership, tenant and access policy alongside each chunk.

Enforce authorization in trusted application/database logic before content enters a prompt. Post-filtering a small candidate list can reduce authorized recall; measure this under realistic permission distributions. Never rely on an LLM to decide which private documents a user may see. Cache keys must include authorization scope and source/model versions. A deleted source should disappear from indexes, caches, summaries and derived memory according to a documented lifecycle.

## A worked retrieval evaluation

First consider three of the lab documents: A covers password reset, B covers office hours, C covers a restricted tenant's reset procedure. The lab adds a fourth red-tenant document D containing instruction-like malicious text. A user in tenant blue asks “reset account password.” A lexical overlap scorer finds A with three matching terms and C with two; C is unauthorized and must never become context. For a query with relevant set {A,D}, retrieving [B,A] has recall@2=1/2 and reciprocal rank=1/2. Precision@2 is also 1/2 here. If an answer states “support is open 24 hours” while A only explains reset steps, the citation does not support that statement even if A was relevant to the query.

Run [retrieval.py](../labs/retrieval.py). It tokenizes tiny synthetic documents, filters tenant access, ranks lexical overlap, computes recall and reciprocal rank, and returns an extractive answer with source ID. This is a transparent retrieval-and-evidence baseline, not an LLM and not BM25 or learned dense search. Its deliberate limitation helps isolate whether evidence exists before adding generation.

## Add generation with measured boundaries

A RAG pipeline ingests/version-controls sources, retrieves candidates, reranks, assembles context and generates an answer with provenance. [The original RAG paper](https://arxiv.org/abs/2005.11401) studied combining a pretrained generator with non-parametric retrieval. Modern retrieve-then-prompt systems may use different training and inference mechanisms; avoid treating every design as the identical original model.

A useful answer contract says: answer only what the evidence supports, attach source identifiers to factual claims, express conflicts and abstain when the evidence is missing. Enforce structured fields in code, then evaluate their semantics. A schema-valid citation can still point at the wrong paragraph. Query rewriting may improve recall but can drift from user intent or inject unauthorized terms; preserve the original query and compare both paths.

RAG, long context and fine-tuning solve overlapping problems. Retrieval offers source freshness and permission-aware selection. Long context can avoid some retrieval misses but consumes tokens and does not guarantee uniform evidence use. Fine-tuning changes behavior and representations but has update and validation costs. [Lost in the Middle](https://arxiv.org/abs/2307.03172) reports context-position sensitivity in tested models/tasks; this is evidence to test ordering in your system, not a timeless claim that every model fails identically.

## Failure analysis and practice

Track ingestion omissions, stale versions, retrieval misses, reranker mistakes, truncated qualifiers, unsupported generation and wrong citation attachment separately. A single “answer quality” score obscures repair choices.

1. If relevant A ranks third and k=2, is the generator at fault for not using it? Solution: first fix or measure candidate recall; the generator never received A.
2. Design a conflicting-policy response. Solution: compare timestamps and authority metadata; state the conflict and route to the policy owner if authority cannot be resolved. Never silently blend inconsistent instructions.
3. When is graph retrieval useful? Solution: when queries require typed relationships and traversal, such as ownership chains; compare against metadata joins and ordinary search before adding graph complexity.

Interview: explain retrieval versus generation; compute recall and reciprocal rank; design tenant-safe indexing, freshness, deletion and evaluation under a p95 latency budget. Vocabulary: inverted index, BM25, bi-encoder, cross-encoder, ANN, HNSW, reranker, chunk, hybrid retrieval, grounding, provenance.
