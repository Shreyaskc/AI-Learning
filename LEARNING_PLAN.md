# The AI Fluency Roadmap

**Goal:** Be able to hold your own in any conversation about AI, LLMs, and agents — understand the terminology, explain how things work at a functional level, and know what matters in the ecosystem. Part 2 goes further: the actual math and engineering underneath.

**How to use this:** Open `index.html` in this folder (just double-click it). It's an interactive course that mirrors this plan — every phase below is a module in the app, with hands-on demos, quizzes, and flashcards. Work through it in order; each module builds on the last.

---

## Part 1: The 6 Fluency Phases

### Phase 1 — The Big Picture (Module 1)
*Time: ~1 hour*

Untangle the buzzwords so you never confuse AI, ML, deep learning, and generative AI again.

**You're done when you can explain:**
- The difference between AI, machine learning, and deep learning (they're nested, not synonyms)
- What "training" vs "inference" means
- Why LLMs exploded around 2020–2023 and not before (data + compute + the transformer architecture)

### Phase 2 — Inside an LLM (Module 2)
*Time: ~2 hours. This is the most technical phase — take it slow.*

Understand what's actually happening when an LLM generates text. This is the foundation everything else rests on.

**You're done when you can explain:**
- What a **token** is and why models see tokens, not words
- What an **embedding** is (meaning as coordinates in space)
- What **attention** does, in one sentence ("every word looks at every other word to figure out what matters")
- That LLMs are **next-token predictors** — and why that simple objective produces intelligence-like behavior
- The three training stages: **pretraining → fine-tuning → RLHF**

### Phase 3 — Talking to LLMs (Module 3)
*Time: ~1.5 hours*

Practical fluency: prompts, parameters, and limitations.

**You're done when you can explain:**
- System prompt vs user message, and why roles exist
- What a **context window** is and what happens when it fills up
- What **temperature** and **top-p** actually change
- Few-shot prompting and chain-of-thought, and when to use them
- What a **hallucination** is and *why* it happens (not a bug — a consequence of next-token prediction)

### Phase 4 — Beyond the Model: RAG & Knowledge (Module 4)
*Time: ~1.5 hours*

How real products give LLMs knowledge they weren't trained on.

**You're done when you can explain:**
- Semantic search vs keyword search
- The **RAG** pipeline end-to-end: chunk → embed → store → retrieve → augment → generate
- When to use RAG vs fine-tuning vs long context (the #1 architecture conversation in applied AI)

### Phase 5 — Agents & Tools (Module 5)
*Time: ~2 hours. This is where the industry is right now.*

From chatbots that talk to agents that *do*.

**You're done when you can explain:**
- **Tool use / function calling** — how a text-only model "acts" on the world
- The **agent loop**: think → act → observe → repeat
- What **MCP** (Model Context Protocol) is and the problem it solves
- Agent memory, planning, multi-agent systems, and guardrails

### Phase 6 — The Ecosystem & Fluency (Module 6)
*Time: ~1 hour, then ongoing*

The map of the territory: who builds what, how models are compared, and the safety vocabulary.

**You're done when you can explain:**
- The major labs and model families; open-weights vs closed
- How to think about model choice: capability vs cost vs latency
- What benchmarks are (and their limits)
- Core safety terms: alignment, jailbreak, prompt injection, red-teaming

---

## Part 2: Under the Hood (Modules 7–9)

Once the fluency foundations are locked in, Part 2 goes deeper — the actual math and engineering, not just the vocabulary.

### Phase 7 — The Transformer, Precisely (Module 7)
*Time: ~2 hours*

The real attention formula (Q, K, V, softmax, scaling), multi-head attention, positional encoding, the feedforward block, residual connections, layer norm, and where a model's parameters actually live.

### Phase 8 — Training at Scale (Module 8)
*Time: ~1.5 hours*

Loss functions, gradient descent, backpropagation, optimizers and learning rate schedules, Chinchilla scaling laws, and how training gets split across thousands of GPUs (data/tensor/pipeline parallelism, mixed precision).

### Phase 9 — Inference Engineering (Module 9)
*Time: ~1.5 hours*

The KV cache, quantization (INT8/INT4, GGUF), speculative decoding, and constrained decoding — the serving-side tricks that make a trained model fast and cheap to actually run.

**You're done with Part 2 when you can explain:** the attention formula end to end; why residual connections matter for deep networks; the Chinchilla tradeoff between model size and data; and at least two of the three inference tricks (KV cache, quantization, speculative decoding) well enough to explain why each one is a free lunch, not a shortcut.

---

## Retention System (built into the app)

- **Interactive demos** — you learn tokenization by tokenizing, agents by stepping through an agent loop. Doing > reading.
- **Quizzes** — end of every module, with explanations for every answer. Retake until 80%+.
- **Flashcards** — the glossary doubles as a spaced-repetition deck. Do 10 cards a day; 5 minutes.
- **The Feynman test** — after each module, explain the topic out loud to an imaginary friend in plain English. If you stumble, reread that lesson.

## Suggested Schedule

| Week | Focus |
|------|-------|
| 1 | Modules 1–2 (foundations + how LLMs work) |
| 2 | Modules 3–4 (prompting + RAG), daily flashcards |
| 3 | Module 5 (agents), daily flashcards |
| 4 | Module 6, retake all quizzes, flashcards to "mastered" |

## Going Deeper (optional, after the app)

- **3Blue1Brown — "Neural Networks" series (YouTube):** the best visual intuition for how neural nets and transformers work
- **Andrej Karpathy — "Intro to Large Language Models" (YouTube, ~1 hr):** the single best LLM overview talk
- **Anthropic's docs & prompt engineering guide (docs.anthropic.com):** practical, current, well-written
- **"What Is ChatGPT Doing… and Why Does It Work?" — Stephen Wolfram (essay):** deep but readable
- Hands-on: get an API key (Anthropic or others) and make your first API call; then build a tiny RAG script. The app's final module points you there.

---

*Everything in the app runs locally in your browser. Your progress is saved automatically (localStorage). No account, no internet needed after opening.*
