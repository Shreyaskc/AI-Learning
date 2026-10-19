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

First consider three of the lab documents: A covers password reset, B covers office hours, C covers a restricted tenant's reset procedure. The lab adds a fourth red-tenant document D containing instruction-like malicious text. A user in tenant blue asks “reset account password.” A lexical overlap scorer finds A with three matching terms and C with two; C is unauthorized and must never become context. For a separate generic ranking task whose relevant authorized IDs are {Y,Z}, retrieving [X,Y] has recall@2=1/2 and reciprocal rank=1/2. Precision@2 is also 1/2 here. If an answer states “support is open 24 hours” while A only explains reset steps, the citation does not support that statement even if A was relevant to the query.

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

## Practical extension: BM25 plus an evaluated generation boundary

Run `python3 labs/rag_evaluation.py --report /tmp/rag-report.json`. The retriever now implements term-frequency saturation, inverse document frequency and length normalization. The generation boundary accepts structured answer claims and evaluates their support and task correctness separately. Default answers are deliberately mixed-quality **authored mock fixtures**; no model is invoked and their scores are not a model benchmark.

For query term t in document d, the implemented contribution is `idf(t)*tf*(k1+1)/(tf+k1*(1-b+b*length(d)/average_length))`, where `idf(t)=log(1+(N-df(t)+.5)/(df(t)+.5))`. N counts authorized documents, df counts authorized documents containing t, and tf counts its occurrences in d. k1=1.2 controls saturation; b=.75 controls length normalization. Each distinct query term contributes once. Empty queries, unseen terms and empty authorized corpora return no candidates. [Lucene's BM25 documentation](https://lucene.apache.org/core/9_12_1/core/org/apache/lucene/search/similarities/BM25Similarity.html) documents the IDF convention; actual production implementations also include indexing and normalization details absent here.

Worked two-document example: texts `term term extra` and `term other` have lengths 3 and 2, average 2.5, and df(term)=N=2. Thus idf=log(1.2)≈.182322. First-document frequency factor is 4.4/(2+1.2*(.25+.75*1.2))=4.4/3.38≈1.301775, contribution≈.237342. Second-document factor is 2.2/(1+1.2*(.25+.75*.8))=2.2/2.02≈1.089109, contribution≈.198568. Repetition helps but saturates; length affects normalization. Scores are not probabilities.

The request builder first filters tenant access, then computes corpus statistics and candidates within that authorized subset. It emits query, tenant, instruction and source-tagged context, plus a SHA-256 hash of the exact request. Corpus statistics can themselves reveal information, so this tiny design avoids computing them across unauthorized documents. Large systems may choose other authorized-index strategies and must analyze their leakage/performance tradeoffs.

The response schema contains `abstain` and a list of `{text,sources}` claims. The evaluator checks: is relevant evidence in the context; is the answer withheld appropriately given that context; does every claim cite a supplied source that explicitly supports it; and does the response cover the required answer facts? Grounded-but-irrelevant text is not automatically a correct answer. The exact-match fact checklist is intentionally small and curated. It will misgrade valid paraphrases and does not replace human semantic evaluation.

The seven-case fixture suite includes one successful reset answer, an answer containing one supported and one fabricated claim, two correct abstentions, a paraphrase retrieval miss, a wrong citation, and an instruction-like malicious-source case. Recorded results show one retrieval miss, 2/5 supported claims and 3/7 end-to-end successes. These counts were injected to verify evaluation failure paths. They are evidence that the harness distinguishes these conditions, not evidence that a language model resists injection or answers at that accuracy.

## Integrating separately recorded real-model outputs

Export exact requests with `python3 labs/rag_evaluation.py --export-requests /tmp/rag-requests.json`. Supply those synthetic contexts to a separately configured model only when you have an appropriate lightweight runtime and budget. Save responses with metadata `kind: recorded-real-model`, model ID, runtime version and recording date; key each response by case ID with its `request_sha256`. `--responses /path/to/outputs.json` evaluates the same schema and rejects a mismatched request/context hash. Read the `RecordedGenerator` class for the file contract. No provider endpoint, credential or implicit download is embedded.

No real generator was run here. A real generator requires an explicit runtime, resource budget and provenance record; host-specific execution decisions belong in the validation report. The trained bigram in 09 demonstrates real generation but is not substituted for a semantic RAG model. A future real-model report must use a separate provenance label and must never overwrite the mock report as if it were a measured model result.

Exercises: (1) Return the correct office-hours text with the reset source ID. Solution: the support check fails despite correct-looking words because the cited source does not support that claim. (2) Retrieve no evidence for an answerable paraphrase and abstain. Solution: abstention is appropriate for the supplied context, yet end-to-end retrieval/answer coverage fails. (3) Return only a true but irrelevant fact. Solution: groundedness and required-answer completeness must be separate gates. (4) Rewrite facts into paraphrases. Solution: the exact-match evaluator will reject some legitimate answers; add blinded human labels or a validated semantic judge before drawing conclusions about model quality.

Mastery gate: reproduce the failure taxonomy, hand-compute the BM25 example, identify the authorization boundary and explain which reported scores come from mock fixtures versus actual inference. Dense retrieval, ANN tradeoffs and real generator evaluation remain explicit deeper work.
