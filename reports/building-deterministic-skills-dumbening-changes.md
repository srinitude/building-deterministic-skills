# building-deterministic-skills — platform-agnostic refactor report

Generated: 2026-05-31.

This release makes the skill fully platform-agnostic: it no longer depends on, imports, or
references any single agent runtime. Validation now anchors on the agentskills.io specification and
its canonical `skills-ref` reference validator, plus pure-stdlib checks bundled in `scripts/`.

## sha256 ledger

- After SKILL.md sha256: `1fb691bb7269b11ce3897b088d277340a77a003b81ae977f1bed8ec87f07b6dc`
- The before/after sha for each prior release is preserved in git history (`git log -p SKILL.md`).

## Preserved invariants

- Frontmatter validation is enforced offline by `scripts/check-skill-frontmatter.py`, mirroring the
  canonical `skills-ref` field rules (closed top-level field set, name format, length caps).
- agentskills.io compliance is verified by the official `skills-ref validate` reference validator.
- The dumb-model output contract terms and at least eight numbered Common pitfalls survive, enforced
  by `scripts/check-preserved-invariants.py`.
- Existing references are still present and linked: `references/third-party-skill-adoption.md`,
  `references/productized-agent-skill-release.md`, and `references/dumb-model-authoring.md`.
- The research spine is bundled and linked: `references/llm-smart-vs-dumb-factors.md`,
  `references/writing-agent-skills-for-dumb-models.md`, and `references/dumb-vs-smart-factor-research.md`.

## Changed/created paths

- `SKILL.md`
- `references/dumb-model-authoring.md`
- `references/llm-smart-vs-dumb-factors.md`
- `references/writing-agent-skills-for-dumb-models.md`
- `references/dumb-vs-smart-factor-research.md`
- `references/third-party-skill-adoption.md`
- `references/productized-agent-skill-release.md`
- `assets/dumb-model-skill-skeleton.md`
- `evals/evals.json`
- `scripts/check-skill-frontmatter.py`
- `scripts/check-preserved-invariants.py`
- `scripts/check-dumb-model-coverage.py`
- `scripts/check-dumb-model-readability.py`
- `scripts/check-source-grounding.py`
- `scripts/check-determinism.py`
- `scripts/check-no-dead-links.py`
- `scripts/check-report-grounding.py`
- `reports/source-grounding/firecrawl/agentskills-io/map.json`
- `reports/source-grounding/firecrawl/agentskills-io/scrape-ledger.json`
- `reports/research`
- `reports/building-deterministic-skills-dumbening-changes.md`

## Source-grounding evidence

- agentskills.io spec captured under `reports/source-grounding/firecrawl/agentskills-io/`.
- Multi-tool research captured under `reports/research/` (Firecrawl map+scrape of agentskills.io,
  Exa answer + deep research, Perplexity, Tavily, arXiv, and the canonical `agentskills/agentskills`
  + `anthropics/skills` source via OpenSrc).
- `references/dumb-model-authoring.md` cites scraped Agent Skills artifacts that resolve on disk.

## Rejected tradeoffs

- Rejected keeping any runtime-specific validation (importing one host's internal validators), because
  the skill must be portable across every agent runtime that loads Agent Skills. Replaced with the
  canonical `skills-ref` validator plus pure-stdlib offline checks.
- Rejected deleting the original references to shorten the skill, because that would lower workflow coverage.
- Rejected hiding Gotchas in a reference-only doc, because weak models skip buried rules.
- Rejected offering multiple workflow choices, because defaults-not-menus is required for dumb-model readability.
- Rejected fabricating any research artifact; every tool call's real output is saved under `reports/research/`.

## Verification status

See the final response / CI for command evidence. The local verifier scripts fail closed on missing
files, missing factors, dead links, nondeterministic script output, disallowed frontmatter fields, and
ungrounded report paths.
