<!-- Thanks for contributing! Please confirm the checklist below. -->

## What does this change?

<!-- Describe the change and the why, not just the what. -->

## Source grounding

<!-- If you changed claims about agentskills.io or Hermes, cite the source. -->

## Checklist

- [ ] I ran the validator pipeline locally and it passed:
  - [ ] `python3 scripts/check-skill-frontmatter.py`
  - [ ] `python3 scripts/check-dumb-model-readability.py SKILL.md`
  - [ ] `python3 scripts/check-no-dead-links.py`
  - [ ] `python3 scripts/check-preserved-invariants.py`
  - [ ] `python3 scripts/check-source-grounding.py`
  - [ ] `python3 scripts/check-report-grounding.py`
  - [ ] `python3 scripts/check-determinism.py`
- [ ] Critical rules stayed front-loaded and book-ended in `SKILL.md`.
- [ ] New referenced files live under `references/`, `scripts/`, `assets/`, `evals/`, or `reports/`.
- [ ] New scripts support `--self-test` and are deterministic.
- [ ] I read [CONTRIBUTING.md](../CONTRIBUTING.md).
