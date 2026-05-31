# building-deterministic-skills

A meta [Agent Skill](https://agentskills.io) that teaches an AI agent how to
**author other Agent Skills deterministically** — structured so small,
quantized, distilled, or hallucination-prone models can execute them without
guessing, and validated against the canonical [agentskills.io](https://agentskills.io)
specification and its reference validator.

It encodes the "dumb-model output contract": front-loaded-and-book-ended
critical rules, defaults-not-menus workflows, procedures-over-declarations,
offloading math/counting/exact-string checks to scripts, an INSUFFICIENT
CONTEXT escape hatch, and conditional progressive disclosure.

It is **platform-agnostic**: it works with any agent runtime that loads Agent
Skills. It does not depend on, import, or reference any single host.

## Why

Skills that rely on model creativity or bury load-bearing rules in the middle
fail on weak models. This skill is the methodology (and the validators) for
producing skills that pass the agentskills.io frontmatter, size, layout, and
description gates AND remain executable by low-reasoning models.

## What's in the box

| Path | Purpose |
|------|---------|
| `SKILL.md` | The methodology: critical rules, mandatory layout, frontmatter rules (incl. the closed agentskills.io field set), the dumb-model output contract, ordered workflow, validation pipeline, output template, and verification checklist. |
| `references/dumb-model-authoring.md` | The full authoring guide for weak-model-friendly skills (load before changing the output contract). |
| `references/llm-smart-vs-dumb-factors.md` | Bundled research: the cognitive factors that make an LLM dumb vs. smart, by stage. |
| `references/writing-agent-skills-for-dumb-models.md` | Bundled research: spec-compliant authoring guide mapping each dumbness factor to a countermeasure. |
| `references/dumb-vs-smart-factor-research.md` | Multi-source synthesis (Firecrawl/Exa/Perplexity/Tavily/arXiv/OpenSrc) — the factor→countermeasure spine behind the output contract. |
| `references/third-party-skill-adoption.md` | Adopting external skill repos safely. |
| `references/productized-agent-skill-release.md` | Releasing a skill as a standalone versioned repo. |
| `assets/dumb-model-skill-skeleton.md` | Starting template for a new generated skill. |
| `scripts/` | Deterministic validators (frontmatter, readability, coverage, source/report grounding, preserved invariants, dead links, determinism). Pure Python stdlib; each supports `--self-test`. |
| `evals/evals.json` | Trigger, anti-trigger, and functional eval cases (incl. agentskills.io frontmatter compliance). |
| `reports/source-grounding/` | Firecrawl map + scrape ledger that ground the agentskills.io claims (consumed by `check-source-grounding.py`). |
| `reports/research/` | Multi-tool research artifacts (Firecrawl map/scrape of agentskills.io, Exa deep research, Perplexity, Tavily, arXiv, OpenSrc). |

## Install

This is a standard Agent Skill directory. Install it with your agent runtime's
skill installer pointed at this repository, or copy the skill directory into
your runtime's skills library. The skill name must equal its directory name
(`building-deterministic-skills`).

## Validate locally

The validators are pure Python (standard library only) and run on any Python 3.9+
with no external setup:

```bash
python3 scripts/check-skill-frontmatter.py
python3 scripts/check-dumb-model-readability.py SKILL.md
python3 scripts/check-dumb-model-coverage.py
python3 scripts/check-preserved-invariants.py
python3 scripts/check-no-dead-links.py
python3 scripts/check-source-grounding.py
python3 scripts/check-report-grounding.py
python3 scripts/check-determinism.py
```

For full agentskills.io compliance, also run the canonical reference validator:

```bash
# from github.com/agentskills/agentskills
skills-ref validate .
```

`check-dumb-model-coverage.py` reads the research bundled under `references/`, so
it needs no external files.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md). All checks in
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) must pass.

## License

[Apache License 2.0](LICENSE). See [NOTICE](NOTICE).
