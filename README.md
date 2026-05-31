# building-deterministic-skills

A meta [Agent Skill](https://agentskills.io) that teaches an AI agent how to
**author other Agent Skills deterministically** — structured so small,
quantized, distilled, or hallucination-prone models can execute them without
guessing, and validated against the agentskills.io reference validator
(`skills-ref`) so it stays portable across any agent runtime that loads Agent
Skills.

It encodes the "dumb-model output contract": front-loaded-and-book-ended
critical rules, defaults-not-menus workflows, procedures-over-declarations,
offloading math/counting/exact-string checks to scripts, an INSUFFICIENT
CONTEXT escape hatch, and conditional progressive disclosure.

## Why

Skills that rely on model creativity or bury load-bearing rules in the middle
fail on weak models. This skill is the methodology (and the validators) for
producing skills that pass agentskills.io frontmatter, size, discovery, and
security gates AND remain executable by low-reasoning models.

## What's in the box

| Path | Purpose |
|------|---------|
| `SKILL.md` | The methodology: critical rules, mandatory layout, frontmatter rules, the dumb-model output contract, ordered workflow, validation pipeline, and verification checklist. |
| `references/dumb-model-authoring.md` | The full authoring guide for weak-model-friendly skills (load before changing the output contract). |
| `references/third-party-skill-adoption.md` | Adopting external skill repos safely. |
| `references/productized-agent-skill-release.md` | Releasing a skill as a standalone versioned repo. |
| `assets/dumb-model-skill-skeleton.md` | Starting template for a new generated skill. |
| `scripts/` | Deterministic validators (frontmatter, readability, coverage, source/report grounding, preserved invariants, dead links, determinism). Each supports `--self-test`. |
| `evals/evals.json` | Trigger, anti-trigger, and functional eval cases. |
| `reports/source-grounding/` | Web map + scrape ledger that ground the agentskills.io claims (consumed by `check-source-grounding.py`). |

## Install

Agent Skills are folders. Install by copying this package into the directory
your agent loads skills from (commonly `<skills-root>/building-deterministic-skills/`),
then refresh your agent's skill index. Consult your runtime's documentation for
the exact skills directory and refresh command.

## Validate locally

The validators are pure Python (stdlib only). Most run on any Python 3.9+ with
no external setup:

```bash
python3 scripts/check-skill-frontmatter.py
python3 scripts/check-dumb-model-readability.py SKILL.md
python3 scripts/check-no-dead-links.py
python3 scripts/check-preserved-invariants.py
python3 scripts/check-source-grounding.py
python3 scripts/check-report-grounding.py
python3 scripts/check-determinism.py
```

For agentskills.io compliance, also run the canonical reference validator
(`skills-ref validate ./`) from `github.com/agentskills/agentskills`.
`check-dumb-model-coverage.py` requires the bundled factor/guide references; in
CI it runs only its deterministic `--self-test`.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md). All checks in
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) must pass.

## License

[Apache License 2.0](LICENSE). See [NOTICE](NOTICE).
