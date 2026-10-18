# 00 · Start here: learn, build, explain

AI Fluency is a self-study course for a software engineer learning AI from first principles. Its destination is the ability to reason about models, build and evaluate small systems, and defend production architecture choices. Interview readiness requires practice and feedback; no course guarantees every interview.

## How to use the course

Read in order on your first pass. Each chapter states prerequisites and outcomes, develops a mechanism, works an example, then asks you to retrieve the idea without looking. Write your answer before opening a solution. Run the linked lab, change an assumption, and explain why the output changed. An explanation that merely repeats a formula is not yet understanding.

The examples use invented support tickets, libraries and equipment. They contain no employer data or claimed personal achievements. Python labs require only the standard library and make no network calls. They demonstrate mechanisms on tiny data; they are not trained production models or evidence of real-world accuracy.

From the repository root:

```sh
python3 labs/foundations.py
python3 labs/learning.py
python3 labs/attention.py
python3 labs/retrieval.py
python3 labs/platform.py
python3 -m unittest discover -s labs -p 'test_*.py'
python3 tools/build.py
python3 tools/check.py
```

Open `index.html` for the generated reader. Markdown in `course/` is the source of truth. No GPU, paid API, external library or account is needed. A web server is optional: `python3 -m http.server 8000` and visit localhost port 8000. Browser progress is local to that browser and is not an assessment credential.

## Three learning paths

**First principles:** work through 00–19, roughly 100–150 hours including exercises and projects. This is a planning estimate, not a measured completion time. Allocate more time if probability or calculus is new.

**Practicing engineer:** take the diagnostic below; still read 01 and 06. Review 02–05 where you cannot derive the answers, then complete 07–19 and two projects. Existing Python ability is useful but does not replace evaluation skills.

**Architect interview rehearsal:** after the first pass, use 06, 10, 11 and 13–19. Spend 45 minutes on a design, 15 on a capacity estimate, and 15 on a failure analysis. Ask another person to challenge assumptions. Keep a log of errors rather than memorizing polished scripts.

## Diagnostic with answers

Score one point only if you can explain the reasoning, not just name the term.

1. Why can fitting a scaler before the train/test split contaminate evaluation? Answer: test distribution statistics influence the fitted pipeline; fitting belongs within each training fold.
2. Compute the dot product of (1,2) and (3,4). Answer: 11, a weighted sum, not a distance.
3. A rare fault has prevalence 1%; a detector has 90% sensitivity and 10% false-positive rate. Is a positive result usually correct? Answer: no; 90/(90+990), about 8.3% precision in 10,000 cases.
4. Differentiate `(wx-y)^2/2` with respect to w. Answer: `(wx-y)x`; the x comes from the chain rule.
5. Why is 99% accuracy weak evidence on a 1% positive problem? Answer: predicting every case negative achieves it.
6. What does a causal attention mask prohibit? Answer: using later positions while predicting the next token.
7. Why does adding retrieval not guarantee truth? Answer: retrieval may miss evidence; evidence may be false or outdated; the generator may not follow it.
8. What must a retried payment-like tool call carry? Answer: an enforced idempotency key and authorization context; a prompt instruction is insufficient.
9. Why is event time alone insufficient for historical feature construction? Answer: an event may have arrived after the historical decision.
10. What differs between a latency average and a p99 latency? Answer: mean measures overall average, p99 marks the slow-tail boundary for 99% of observed requests.

0–4: full path. 5–7: target weak prerequisites. 8–10: prove the answers with a lab or design before skipping. This tiny diagnostic does not measure all competence.

## Dependencies and review rhythm

01 defines the problem and splitting contract. 02 → 03 → 04 supplies math. Those plus 01 feed 05 → 06 → 07 → 08 → 09. Then 06+08+09 → 10 → 11; 07+08+09 → 12. 06+10+11 → 13 → 14 → 15. Chapter 16 deepens security. Chapter 17 uses 03+06 for experiments; 03+05+06+13 → 18 covers electives and 19 integrates projects/interviews. Chapter 16's threat modeling should also be revisited while building 10 and 11.

After every chapter, close the page and explain its mechanism in 90 seconds. Review the next day, one week later and one month later. On each review: define three terms, redo one calculation, solve one changed example, and name one failure mode. If you fail, reread the relevant section and schedule another next-day attempt. Spacing dates are a practical study convention, not a universal optimal schedule.

## Evidence labels

**Foundation** means a mathematical identity or well-established mechanism under stated assumptions. **Empirical** means a finding on a particular dataset, model or experimental setup; it may not transfer. **Design judgment** means a recommendation whose merit depends on requirements. **Open question** means unsettled evidence. Primary-source references are collected in [Sources](sources.md); they are learning evidence, not a live model leaderboard.

See [coverage and remaining depth](coverage.md) before treating the course as an exhaustive specialization. Begin with [01 · What AI systems learn](01-foundations.md).
