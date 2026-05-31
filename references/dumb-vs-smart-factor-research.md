# LLM dumb-vs-smart factors → deterministic agent-skill countermeasures (multi-source research)

This reference is the consolidated, source-grounded enumeration of every factor that
makes a large language model behave **dumb vs. smart**, paired with the concrete
**authoring countermeasure** that makes an Agent Skill execute *deterministically and
identically on the weakest models*. It is the research spine behind
`SKILL.md`'s dumb-model output contract.

It was assembled from independent research run with multiple tools (artifacts under
`reports/research/`):

- **Firecrawl** — `map` of the full https://agentskills.io site (19 URLs) + scrapes of
  every page (`reports/research/firecrawl/agentskills-scrape-ledger.json`), plus topic
  searches per capability stage (`reports/research/firecrawl/s*.json`).
- **Exa** — `answer` for factors + authoring, and a completed `research-create` deep
  research report (`reports/research/exa/deep-research-report.md`).
- **Perplexity** — `sonar-pro` grounded synthesis (`reports/research/perplexity/`).
- **Tavily** — advanced `search` on both themes (`reports/research/tavily/`).
- **arXiv** — seminal papers (`reports/research/arxiv/`): Chinchilla scaling,
  Lost-in-the-Middle, Why Language Models Hallucinate, Curse of Instructions,
  Emergent Abilities.
- **OpenSrc** — the canonical `agentskills/agentskills` reference (incl. the `skills-ref`
  validator) and `anthropics/skills` (`reports/research/opensrc/`).

The two foundational documents are bundled verbatim alongside this file:
`references/llm-smart-vs-dumb-factors.md` and
`references/writing-agent-skills-for-dumb-models.md`. Read those for the full evidence
and citations; this file is the actionable cross-tool synthesis.

## The throughline

Pretraining sets the capability ceiling; architecture and post-training shape what is
accessible; **inference-time choices (reasoning budget, context hygiene, prompting)
decide how much of that latent intelligence actually shows up.** A skill cannot raise a
model's intrinsic ceiling, but **bad skill design wastes capability the model already
has, and good design recovers it.** The author's job is to remove every avoidable source
of dumbness from the one stage they control: *inference*.

## Factor → countermeasure table (the contract spine)

| Stage | Dumbness factor | What it does to a weak model | Deterministic authoring countermeasure |
|---|---|---|---|
| Pretraining | Emergent-ability threshold | multi-step reasoning may not exist below scale | give the **procedure**, not the reasoning — numbered steps + decision tables |
| Pretraining | Data gaps / narrow corpus | systemic blind spots, hallucination | prefix a small fixed canonical-fact block; answer only from it; verify by exact-string match |
| Architecture | Tokenization | systematic arithmetic / counting / exact-string errors | offload math/counting/hashing/exact checks to bundled `scripts/` |
| Architecture | Quantization / distillation loss | nuance and edge cases erode first | state edge cases explicitly in a `## Gotchas` section in `SKILL.md` |
| Architecture | Position extrapolation | reliability collapses past trained length | keep `SKILL.md` short; progressive disclosure of references |
| Post-training | Sycophancy / reward hacking | rubber-stamps wrong premises | validation loops + plan-validate-execute + explicit stop conditions |
| Post-training | Hallucination (guessing-rewarded) | fabricates confidently | `INSUFFICIENT CONTEXT: <field>` escape hatch that names the missing field and stops |
| Inference | No / low test-time reasoning | blurts a single pass, no self-correction | checklists + validate-fix-rerun loops that force think→act→verify |
| Context | Lost in the middle (U-shaped attention) | buried rules get skipped | **front-load AND book-end** critical rules; keep Gotchas in `SKILL.md` |
| Context | Context rot | accuracy falls as input grows | `SKILL.md` ≤ 500 lines / ~5000 tokens; conditional progressive disclosure |
| Context | Prompt bloat | every extra sentence distracts | add only what the agent lacks; omit generic filler |
| Instructions | Curse of instructions: P(all)≈(per-rule rate)^N | each added rule multiplies failure odds | defaults-not-menus; moderate detail; sequence don't stack |
| Instructions | Instruction sensitivity | wording swings behavior | one-term-per-concept; unambiguous parameter names |
| Sampling | Sampling variability | same prompt, different output shape | provide an **output template**, not prose |
| Activation | Weak skill triggering | the skill never loads | optimize the `description`; test trigger rate with eval queries |
| Measurement | Benchmark contamination / memorization | "smart" is partly an illusion | run your own clean evals **with vs. without** the skill on the **weakest** target model |

## Progressive disclosure = the architectural defense (from agentskills.io)

The agentskills.io three-stage load maps directly onto dumbness defenses:

1. **Discovery** — only `name` + `description` (~100 tokens), always on → defeats context rot / prompt bloat.
2. **Activation** — full `SKILL.md` body, only when the description matches → defeats the curse of instructions (the model only sees rules relevant now).
3. **Execution** — `scripts/`, `references/`, `assets/` pulled in only at the step that needs them → defeats lost-in-the-middle (detail arrives when attention is on it).

Keep references **one level deep**; always state the **exact condition** that triggers loading each one ("Read `references/<file>` ONLY when …", naming the real file), because a weak model won't infer the trigger.

## Spec compliance (agentskills.io, confirmed against the canonical `skills-ref` validator)

- Allowed top-level frontmatter fields are a **closed set**: `name`, `description`,
  `license`, `allowed-tools`, `metadata`, `compatibility`. Put everything else
  (`version`, `author`, `tags`, …) under `metadata`. A top-level `version:`/`author:`
  fails `skills-ref validate`.
- `name`: 1–64 chars, lowercase letters/digits/hyphens, no leading/trailing/consecutive
  hyphens, equals the parent directory (NFKC-normalized).
- `description`: 1–1024 chars; says what + when; pushy imperative triggers.
- `compatibility`: ≤ 500 chars, only when environment requirements exist.

## Failure-signature → fix (read transcripts, not just outputs)

| Symptom | Cause | Fix |
|---|---|---|
| skips a rule | rule buried / too many rules | front-load + book-end; cut rules |
| tries several approaches first | instructions too vague | be prescriptive; add a default |
| follows an irrelevant instruction | didn't apply to this task | scope tighter; moderate detail |
| wrong arithmetic / counts | model doing math itself | offload to a script |
| confidently wrong / fabricated | hallucination + sycophancy | escape hatch + validation loop |
| inconsistent output shape | free-form prose | output template |
| degrades on long inputs | context rot / bloat | trim + progressive disclosure |
| passes sometimes, fails others (high stddev) | ambiguous instructions | add examples; tighten |
| skill never loads | weak description | optimize + test triggering |
