# Executed practical evidence

These files distinguish actual training, simulated boundaries and measured mock workloads. They are not production or employer-data results. All data and effects are synthetic. No provider API, GPU workload or heavy local language model was invoked.

| File | What actually ran | What it does not establish |
| --- | --- | --- |
| model-comparison.json | Constant/logistic/tree/MLP fitted on 160 rows; candidate selection on 80 validation rows; final 80-row evaluation; fitted JSON pipeline artifacts | Real-data performance, equal compute tuning or a universal family ranking |
| language-model.json | Smoothed character-bigram training, validation smoothing choice, held-out NLL/seeded sampling; SFT mask and scalar DPO calculation | A trained neural LLM, semantic fluency, executed SFT/LoRA/DPO policy training |
| rag-mock.json | Authorized BM25 retrieval and evaluation of seven authored answer fixtures | Real model quality, semantic-judge validity or demonstrated model injection resistance |
| rag-requests.json | Exact source-tagged synthetic requests and hashes for the recorded-output adapter | Any real model inference; no real-model output file is included |
| durable-agent.json | Separate SQLite stores and child processes; abrupt exit after committed simulated provider effect; recovery/reconciliation and memory lifecycle | Distributed exactly-once guarantee, concurrent lease safety or a real external provider |
| serving-local.json | Actual monotonic timings of bounded threaded mock service with overload/batching | GPU/token throughput or a real inference-service capacity estimate |
| representations.json | Fitted tiny PCA/k-means plus convolution/recurrent numeric traces | Trained CNN/RNN/GNN or robust numerical solver behavior |

To reproduce deterministic reports from the repository root:

```sh
python3 labs/model_comparison.py --report /tmp/model-comparison.json
python3 labs/language_model.py --report /tmp/language-model.json
python3 labs/rag_evaluation.py --report /tmp/rag-mock.json --export-requests /tmp/rag-requests.json
python3 labs/durable_agent.py --report /tmp/durable-agent.json
python3 labs/representations.py > /tmp/representations.json
python3 labs/serving_experiment.py --report /tmp/serving-local.json
```

Serving measurements will vary with scheduling and host conditions. Do not replace historical results merely because a rerun looks better. `python3 tools/run_labs.py` smoke-tests all fourteen lab entry points without overwriting these records. Model artifacts retain preprocessing and are replay-tested; the source fingerprint check rejects a stale model-comparison implementation report.

## Recorded real-generation adapter contract

The default RAG output is always `mock-fixture`. A separately produced real-model response file must have this structure (illustrative only, not an executed response):

```json
{
  "metadata": {
    "kind": "recorded-real-model",
    "model_id": "actual-model-id-required",
    "runtime_version": "actual-runtime-required",
    "recorded_at": "actual-recording-date-required"
  },
  "outputs": {
    "reset": {
      "request_sha256": "copy-the-exact-exported-request-hash",
      "response": {
        "abstain": false,
        "claims": [
          {"text": "Reset account password using the settings page.", "sources": ["A"]}
        ]
      }
    }
  }
}
```

Supply an entry for every exported case. The adapter rejects mismatched hashes, so results cannot silently be attached to different contexts. Run `python3 labs/rag_evaluation.py --responses /path/to/real-responses.json --report /tmp/rag-real.json` only with actual provenance. Schema acceptance does not verify that a claimed model really produced the file; honest recording and independent audit remain necessary. The exact-claim evaluator is a fixture checklist, not an adequate semantic quality judge for arbitrary paraphrased outputs. Add validated human labels before using its score to compare real models.
