# Exa deep research — LLM dumb-vs-smart factors and agent-skill countermeasures

Source: Exa research-create (model exa-research), researchId r_01kszmd2tqa1vc7hvrx41kg6fn.

Stage 1 — Pretraining: scale, data composition, quality, diversity
Factors that make a model "dumb":
- Insufficient pretraining scale (too few tokens) limits exposure to language patterns and knowledge, yielding poor generalization and fragile reasoning [Deciphering the Impact of Pretraining Data on Large Language Models through Machine Unlearning](https://arxiv.org/html/2402.11537v3).  
- Low data quality (noisy, duplicated, corrupted pages, or bad HTML) reduces effective signal and increases hallucination risk [Scaling Laws Revisited: Modeling the Role of Data Quality in Language Model Pretraining](https://openreview.net/forum?id=x54wwB6QvL).  
- Narrow or biased corpora (lack of domain or language diversity) produce brittle models with systemic blind spots [Deciphering the Impact of Pretraining Data on Large Language Models through Machine Unlearning](https://arxiv.org/html/2402.11537v3).  
- Missing high-impact sources (e.g., books for multi-step reasoning, code corpora for programming skills) reduces certain capabilities even if token counts are large [Deciphering the Impact of Pretraining Data on Large Language Models through Machine Unlearning](https://arxiv.org/html/2402.11537v3).  

Factors that make a model "smart":
- Large, high-quality, and diverse token budgets tuned for data quality produce richer representations and robustness [Scaling Laws Revisited: Modeling the Role of Data Quality in Language Model Pretraining](https://openreview.net/forum?id=x54wwB6QvL).  
- Including targeted, high-signal datasets (books, curated code, domain collections) improves specific capabilities without requiring orders-of-magnitude more tokens [Deciphering the Impact of Pretraining Data on Large Language Models through Machine Unlearning](https://arxiv.org/html/2402.11537v3).  

Deterministic countermeasures agent-skill authors can apply (so weakest models execute identically every time):
- Constrain the runtime input space to curated micro-corpora: when a skill requires domain knowledge, prefix skill prompts with a small, fixed, curated knowledge snippet (canonical facts) stored as deterministic context rather than relying on model knowledge learned at pretraining scale [Programming Every Example: Lifting Pre-training Data Quality Like Experts at Scale](https://icml.cc/virtual/2025/poster/44780).  
  - Implementation: embed a 200–1000 token canonical fact block (same for every call) and require the model to answer only from that block; verify by exact-string match tests.  
- Use deterministic data-refinement pipelines (example-level cleaning) for any in-skill example or micro-corpus — preprocess with a deterministic program (ProX-style example-level cleaners) so the same cleaned tokens are passed every time [Programming Every Example: Lifting Pre-training Data Quality Like Experts at Scale](https://icml.cc/virtual/2025/poster/44780).  
- Replace probabilistic reliance on broad knowledge with deterministic lookup: for factual checks, call an external deterministic knowledge store (database / vector store with exact-match fallback) and only accept model output that matches entries under exact-match or deterministic verification logic [Deciphering the Impact of Pretraining Data on Large Language Models through Machine Unlearning](https://arxiv.org/html/2402.11537v3).  
- Use minimal, high-signal few-shot exemplars embedded in prompt (fixed examples, same order) rather than exposing a long or variable context — fewer, deterministic examples reduce variance caused by pretraining gaps [Scaling Laws Revisited: Modeling the Role of Data Quality in Language Model Pretraining](https://openreview.net/forum?id=x54wwB6QvL).  
- Provide explicit failure modes and guardrails in the skill (if evidence absent, return a fixed refusal token), and validate outputs via deterministic validators that reject anything not matching the expected format or that contradicts the canonical block.

Stage 2 — Architecture, tokenization, quantization, distillation
Factors that make a model "dumb":
- Inefficient or mismatched architecture (poor depth/width tradeoffs, absent optimized attention patterns) causes wasted capacity and slower or incorrect inference behavior [Survey of different Large Language Model Architectures: Trends, Benchmarks, and Challenges](https://arxiv.org/html/2412.03220v1).  
- Fragile or domain-mismatched tokenization produces broken semantic units (fragmented domain terms), degrading comprehension and adding nondeterminism if different tokenizers/preprocessing are applied [How Different Tokenization Algorithms Impact LLMs and Transformer Models](https://arxiv.org/abs/2511.03825).  
- Aggressive low-bit quantization without calibration can change numerical behavior and produce inconsistent outputs, especially for complex tasks [Evaluating Quantized Large Language Models](https://arxiv.org/abs/2402.18158).  
- Naive distillation (label-only, no rationale supervision) strips intermediate reasoning and leads to brittle student behavior [Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes](https://arxiv.org/abs/2305.02301).  

Factors that make a model "smart":
- Architectures optimized for compute and memory (sparse attention, efficient transformer variants, balanced scaling) preserve capability at lower cost [Survey of different Large Language Model Architectures: Trends, Benchmarks, and Challenges](https://arxiv.org/html/2412.03220v1).  
- Deterministic, consistent tokenization (single tokenizer version, fixed preprocessing) preserves identical input encodings and reduces variability [How Different Tokenization Algorithms Impact LLMs and Transformer Models](https://arxiv.org/abs/2511.03825).  
- Calibrated 8-bit quantization or quantization-aware training preserves performance while reducing non-deterministic artifacts [Evaluating Quantized Large Language Models](https://arxiv.org/abs/2402.18158).  
- Rationale-enhanced distillation transfers stepwise reasoning to smaller models, improving consistent behavior on multi-step tasks [Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes](https://arxiv.org/abs/2305.02301).  

Deterministic countermeasures agent-skill authors can apply:
- Lock tokenizer and preprocessing end-to-end: bundle the tokenizer binary/version, normalization rules, and a deterministic pipeline with your skill. Always run the same deterministic preprocessing on inputs before invoking the model; include a tokenization test harness in CI to ensure identical token sequences across environments [How Different Tokenization Algorithms Impact LLMs and Transformer Models](https://arxiv.org/abs/2511.03825).  
- Use deterministic inference configurations: prefer greedy decoding or beam search with fixed beams and fixed RNG seeds when exact repeatability is required; record and freeze decoding hyperparameters in the skill manifest. Test the chosen decoding mode on canonical inputs to verify identical outputs [Evaluating Quantized Large Language Models](https://arxiv.org/abs/2402.18158).  
- Favor calibrated quantized models (8-bit PTQ with calibration set) and validate output determinism across runs; if using low-bit (4-bit) models, add deterministic post-processing validators that reject or canonicalize outputs shown to be unstable [Evaluating Quantized Large Language Models](https://arxiv.org/abs/2402.18158).  
- When using distilled small models, prefer rationale-enhanced distillation and multi-task distillation (answer + explanation) so the student reproduces teacher stepwise behavior; embed an enforced final-answer extraction step (e.g., output JSON with an "answer" field) and validate exact-match postconditions to guarantee identical execution [Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes](https://arxiv.org/abs/2305.02301).  
- If model architecture constraints hamper determinism, wrap the model with deterministic logic: transform or canonicalize model outputs using deterministic parsers, and reject nonconforming responses before returning them to callers.

Stage 3 — Post-training: RLHF, sycophancy, hallucination
Factors that make a model "dumb":
- Poorly specified RLHF objectives that prioritize user-pleasing agreement over factual accuracy amplify sycophancy (agreeing even when false) and hallucination [How RLHF Amplifies Sycophancy](https://arxiv.org/abs/2602.01002).  
- Labeler bias and skewed preference data cause the reward model to prefer flattering or speculative answers rather than conservative factual responses [Sycophancy in Large Language Models: Causes and Mitigations](https://arxiv.org/abs/2411.15287).  
- Reward optimization with too-large policy updates causes behavioral drift away from the base policy and can increase confident hallucination [Reinforcement Learning from Human Feedback - RLHF Book](https://rlhfbook.com/book.pdf).  

Factors that make a model "smart":
- Rewarding factuality and calibrated humility (preference for uncertainty/refusal when unsupported) reduces hallucinations and discourages sycophancy [Sycophancy in Large Language Models: Causes and Mitigations](https://arxiv.org/abs/2411.15287).  
- Constraining RLHF with small KL penalties (limiting drift from the base policy) preserves base-model factual priors while improving instruction-following [Reinforcement Learning from Human Feedback - RLHF Book](https://rlhfbook.com/book.pdf).  

Deterministic countermeasures agent-skill authors can apply:
- Force determinism at skill boundaries: require the model to output a structured, validated schema (tight JSON or fixed tokens) and run deterministic validators that only accept schema-conforming outputs; on failure, return a fixed fallback response. This prevents sycophantic freeform answers from leaking into the skill result [Reinforcement Learning from Human Feedback - RLHF Book](https://rlhfbook.com/book.pdf).  
- Use disagreement/contradiction prompts and negative examples baked into the skill manifest: include deterministic prompt templates that force the model to consider counter-evidence and to explicitly state confidence on every call (e.g., "Answer only if evidence present in canonical block; otherwise output: 'INSUFFICIENT_EVIDENCE'"), reducing sycophancy [How RLHF Amplifies Sycophancy](https://arxiv.org/abs/2602.01002).  
- Calibrate post-hoc: attach a deterministic truth-checker (external retriever + exact-match verification) before accepting an answer; require passes of the checker for any factual claim and otherwise return a deterministic refusal token [Sycophancy in Large Language Models: Causes and Mitigations](https://arxiv.org/abs/2411.15287).  
- Fix sampling to deterministic modes (greedy or fixed-seed sampling) inside the skill; combine with ensemble reranking (deterministic ranking of N outputs) and select the top-ranked canonical output according to exact-match rules to ensure identical run-to-run behavior [Reinforcement Learning from Human Feedback - RLHF Book](https://rlhfbook.com/book.pdf).  

Stage 4 — Inference-time compute and reasoning
Factors that make a model "dumb":
- Limited inference compute (no multiple samples, no reasoning traces) prevents exploration of reasoning paths, causing simple incorrect or unsupported outputs [Inference-Time Computations for LLM Reasoning and Planning: A Benchmark and Insights](https://arxiv.org/abs/2502.12521).  
- Using stochastic decoding without control introduces non-deterministic final answers across runs [Enhancing Reasoning Accuracy in Large Language Models During Inference Time](https://arxiv.org/abs/2603.21301).  
- Poor intermediate thought processes (unverified chain-of-thought) yield logically inconsistent or incorrect final answers [Inference-Time Computations for LLM Reasoning and Planning: A Benchmark and Insights](https://arxiv.org/abs/2502.12521).  

Factors that make a model "smart":
- Controlled inference strategies (self-consistency, dual-model agreement, deterministic ensemble voting, or planner/executor separation) improve reasoning quality and robustness [Enhancing Reasoning Accuracy in Large Language Models During Inference Time](https://arxiv.org/abs/2603.21301).  
- Orchestrating small executors under a deterministic planner (DisCIPL-style) lets weaker models reliably perform subtasks under fixed instructions [Enabling Small Language Models to Solve Complex Reasoning Tasks (MIT News on DisCIPL)](https://news.mit.edu/2025/enabling-small-language-models-solve-complex-reasoning-tasks-1212).  

Deterministic countermeasures agent-skill authors can apply:
- Use deterministic decoding as a default for skills requiring identical output (greedy or beam with fixed seed). Where improved accuracy is needed, use controlled self-consistency: sample multiple traces with fixed seeds and deterministically choose the majority final answer or a deterministic aggregation function [Enhancing Reasoning Accuracy in Large Language Models During Inference Time](https://arxiv.org/abs/2603.21301).  
- Decompose tasks into atomic subtasks with deterministic I/O: require each subtask to return a strict schema and validate before running the next subtask. This isolates stochasticity and forces deterministic chaining [Inference-Time Computations for LLM Reasoning and Planning: A Benchmark and Insights](https://arxiv.org/abs/2502.12521).  
- Implement planner/executor split: use a stable (possibly larger) planner to emit a fixed plan and have smaller deterministic executors follow the plan with locked prompts and deterministic decoding, rejecting deviations [Enabling Small Language Models to Solve Complex Reasoning Tasks (MIT News on DisCIPL)](https://news.mit.edu/2025/enabling-small-language-models-solve-complex-reasoning-tasks-1212).  
- Add deterministic step-checks and proofs: for reasoning skills, require the model to enumerate numbered steps and include exact-check assertions that the runtime verifier enforces before accepting the answer [Enhancing Reasoning Accuracy in Large Language Models During Inference Time](https://arxiv.org/abs/2603.21301).  

Stage 5 — Context handling: lost-in-the-middle, context rot, context window limits
Factors that make a model "dumb":
- Lost-in-the-middle positional bias (information in the middle of long contexts is recalled poorly) causes brittle behavior when important facts aren’t at the start/end of the context [Lost in the Middle: How Language Models Use Long Contexts](https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.tacl2023.pdf).  
- Context rot (attention dilution across long windows) degrades constraint enforcement and factual recall as context grows [Context rot explained (& how to prevent it) - Redis Blog](https://redis.io/blog/context-rot).  
- Catastrophic forgetting when adapting to long contexts can reduce short-text performance if models are naively extended [LongReD: Mitigating Short-Text Degradation of Long-Context Large Language Models via Restoration Distillation](https://arxiv.org/html/2502.07365v1).  

Factors that make a model "smart":
- Models with robust long-context training and restoration-distillation techniques preserve short-context behavior and recall across long inputs [LongReD: Mitigating Short-Text Degradation of Long-Context Large Language Models via Restoration Distillation](https://arxiv.org/html/2502.07365v1).  

Deterministic countermeasures agent-skill authors can apply:
- Position engineering: always place critical facts at the start or the end of the context window (deterministically sandwiching important content) so primacy/recency biases favor retrieval [Lost in the Middle: How Language Models Use Long Contexts](https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.tacl2023.pdf).  
- Deterministic external memory / semantic cache: store canonical facts in an external deterministic store (key-value or vector store with deterministic exact-match fallback) and prefetch or inject only the required canonical blocks into prompts; never rely on raw long context to carry essential state [Context rot explained (& how to prevent it) - Redis Blog](https://redis.io/blog/context-rot).  
- Restoration distillation for long-context enabled models: where you control the model family, use short-to-long distillation to preserve deterministic short-context behavior while adding long-window capability [LongReD: Mitigating Short-Text Degradation of Long-Context Large Language Models via Restoration Distillation](https://arxiv.org/html/2502.07365v1).  
- Chunking with deterministic retrieval order: split long documents into canonical chunks and retrieve/inject them in a fixed, deterministic order (by timestamp or canonical index) rather than by variable relevance scoring. Validate required facts via exact-match checks against the canonical chunks.

Stage 6 — Prompting, elicitation, few-shot selection and prompt engineering
Factors that make a model "dumb":
- High sensitivity to prompt phrasing and underspecified instructions leads to large behavioral variance from tiny phrasing differences [Revisiting Prompt Sensitivity in Large Language Models for Text Classification: The Role of Prompt Underspecification](https://arxiv.org/html/2602.04297v1).  
- Over-prompting (too many or noisy few-shot examples) can degrade performance for smaller models (the "few-shot dilemma") [The Few-shot Dilemma: Over-prompting Large Language Models](https://arxiv.org/html/2509.13196v1).  
- Ad-hoc prompt development (no testing, no versioning) yields irreproducible skills [Promptware Engineering: Software Engineering for LLM Prompt Development](https://wssun.github.io/papers/2025-FSE-20230SEWorkshop-Promptware-Engineering.pdf).  

Factors that make a model "smart":
- Well-specified, instruction-rich, templated prompts reduce variance and improve adherence to expected output formats [Revisiting Prompt Sensitivity in Large Language Models for Text Classification: The Role of Prompt Underspecification](https://arxiv.org/html/2602.04297v1).  
- Careful selection of a small number of semantically relevant few-shot exemplars (embedding or TF-IDF retrieval) improves performance without overloading context [The Few-shot Dilemma: Over-prompting Large Language Models](https://arxiv.org/html/2509.13196v1).  

Deterministic countermeasures agent-skill authors can apply:
- Treat prompts as versioned software artifacts (promptware): store prompt templates, exact examples, and normalization rules in source control; run automated prompt unit tests against canonical inputs to assert exact outputs before deployment [Promptware Engineering: Software Engineering for LLM Prompt Development](https://wssun.github.io/papers/2025-FSE-20230SEWorkshop-Promptware-Engineering.pdf).  
- Use strict prompt templates with explicit output constraints and canonical labels (e.g., "Return exactly one of: YES, NO, MAYBE"), and enforce via deterministic validators (regex/JSON schema) so outputs are identical across runs [Revisiting Prompt Sensitivity in Large Language Models for Text Classification: The Role of Prompt Underspecification](https://arxiv.org/html/2602.04297v1).  
- Limit few-shot examples to an empirically-determined small number (e.g., 3–5) selected deterministically via embedding/TF-IDF nearest neighbors; fix the ordering of examples to avoid run-to-run variation [The Few-shot Dilemma: Over-prompting Large Language Models](https://arxiv.org/html/2509.13196v1).  
- Adopt prompt ensembling deterministically: precompute N prompt variants, run them with fixed seeds, and deterministically aggregate outputs (majority vote or canonical tie-breaking rule) to obtain a single identical answer [Promptware Engineering: Software Engineering for LLM Prompt Development](https://wssun.github.io/papers/2025-FSE-20230SEWorkshop-Promptware-Engineering.pdf).  

Stage 7 — Measurement and benchmark contamination
Factors that make a model appear artificially "smart" (but be "dumb" in generalization):
- Benchmark data contamination (training data including test examples) inflates scores and hides true generalization gaps [Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/html/2406.04244v1).  
- Label leakage and dataset duplicates cause overfitting to benchmark idiosyncrasies [Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/html/2406.04244v1).  
- Overreliance on a narrow set of benchmarks can fail to detect brittleness to out-of-distribution cases [Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/html/2406.04244v1).  

Deterministic countermeasures agent-skill authors can apply:
- Evaluate skills only on uncontaminated or regenerated test sets; use regenerated test data or procedural generation to avoid overlap with pretraining data [Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/html/2406.04244v1).  
- Use held-out deterministic scenario tests (fixed seed synthetic cases or canonical real-world cases) as part of CI that must pass exactly before deployment; record exact inputs and outputs to detect drift [Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/html/2406.04244v1).  
- For behavioral validation, prefer ground-truth deterministic checks (exact-match facts, schema validation) over soft-scoring metrics that can be gamed by contamination. Maintain a contamination-detection pipeline (overlap-matching / fingerprinting) between evaluation sets and available training sources [Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/html/2406.04244v1).  
- Use ensemble and cross-model checks deterministically: require multiple independent models (or frozen skill versions) to agree exactly on outputs for critical skills; otherwise mark the case for human review [Large Language Models Miss the Multi-Agent Mark](https://arxiv.org/html/2505.21298v1).  

Practical deterministic implementation checklist for agent-skill authors (apply these to every skill to make the weakest models behave identically each run):
1. Freeze and bundle the tokenizer and preprocessing code/version; run a tokenization CI test on canonical inputs [How Different Tokenization Algorithms Impact LLMs and Transformer Models](https://arxiv.org/abs/2511.03825).  
2. Use rigid prompt templates stored in source control; include exact few-shot exemplars in fixed order and run prompt unit tests with expected exact outputs [Promptware Engineering: Software Engineering for LLM Prompt Development](https://wssun.github.io/papers/2025-FSE-20230SEWorkshop-Promptware-Engineering.pdf).  
3. Prefer deterministic decoding (greedy or fixed-seed beam search) for identical outputs; if sampling is used for quality, sample with fixed seeds and perform deterministic aggregation (majority voting with fixed tie-breaker) [Enhancing Reasoning Accuracy in Large Language Models During Inference Time](https://arxiv.org/abs/2603.21301).  
4. Always inject a small canonical knowledge block or query deterministic external store for any factual claims; require exact-match verification or return a canonical refusal token [Programming Every Example: Lifting Pre-training Data Quality Like Experts at Scale](https://icml.cc/virtual/2025/poster/44780).  
5. Validate model outputs with deterministic validators (JSON schema, regex, exact-string checks); reject and retry deterministically or return a fixed fallback if validation fails [Reinforcement Learning from Human Feedback - RLHF Book](https://rlhfbook.com/book.pdf).  
6. Use calibrated quantized/distilled models tested across identical inputs and include calibration datasets in CI to detect nondeterministic behavior introduced by compression [Evaluating Quantized Large Language Models](https://arxiv.org/abs/2402.18158).  
7. Use restoration-distillation, planner/executor patterns, or external deterministic control flows to avoid large-model-only reasoning dependencies and enable small-model determinism where possible [LongReD: Mitigating Short-Text Degradation of Long-Context Large Language Models via Restoration Distillation](https://arxiv.org/html/2502.07365v1); [Enabling Small Language Models to Solve Complex Reasoning Tasks (MIT News on DisCIPL)](https://news.mit.edu/2025/enabling-small-language-models-solve-complex-reasoning-tasks-1212).  
8. Continuously test skills on uncontaminated, deterministic evaluation sets and require exact pass/fail criteria in CI before release [Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/html/2406.04244v1).  

Adopt these prescriptive, deterministic engineering patterns as the baseline for every skill: fixed preprocessing/tokenization, templated prompts, deterministic decoding/aggregation, canonical knowledge injection with exact verification, schema validation and fixed-fallbacks, and uncontaminated test suites. These practices convert probabilistic LLM behavior into controlled, repeatable skill executions even when the deployed model is small or otherwise weak.
