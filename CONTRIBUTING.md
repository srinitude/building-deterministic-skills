# Contributing to building-deterministic-skills

Thanks for helping improve this meta-skill. This project IS the methodology it
teaches: every change must keep both targets intact — the skill must stay valid
against the agentskills.io spec, and the skills it tells you to generate must
stay easy for weak models to execute.

## Ground rules

1. **Preserve both targets.** Keep the skill valid against the agentskills.io
   spec AND keep the generated-skill output contract weak-model-friendly.
2. **Front-load and book-end critical rules.** `## CRITICAL RULES` stays near
   the top of `SKILL.md`; the final self-check repeats the load-bearing ones.
3. **Defaults, not menus.** The workflow has one default path. Exceptions go in
   `## Common pitfalls` / `## Gotchas`.
4. **Offload exact checks to scripts.** Counting, hashing, frontmatter,
   coverage, and grounding checks live in `scripts/`, each with `--self-test`.
5. **Keep source grounding honest.** Claims about agentskills.io must be backed
   by `reports/source-grounding/` artifacts or the cited public source. Do not
   delete the grounding artifacts; `check-source-grounding.py` depends on them.
6. **No secrets, no network in scripts.** Validators are stdlib-only and
   offline so they run in clean CI and pass a security scan.

## Local validation

```bash
python3 scripts/check-skill-frontmatter.py
python3 scripts/check-dumb-model-readability.py SKILL.md
python3 scripts/check-no-dead-links.py
python3 scripts/check-preserved-invariants.py
python3 scripts/check-source-grounding.py
python3 scripts/check-report-grounding.py
python3 scripts/check-determinism.py
python3 scripts/check-dumb-model-coverage.py --self-test
```

For agentskills.io compliance, also run the canonical reference validator from
`github.com/agentskills/agentskills`:

```bash
skills-ref validate ./
```

## Pull request checklist

- [ ] CI (`.github/workflows/ci.yml`) is green.
- [ ] `SKILL.md` stays compact (move detail into `references/` rather than
      growing the body; many runtimes cap total SKILL.md size).
- [ ] New referenced files live under `references/`, `scripts/`, `assets/`,
      `evals/`, or `reports/` and are linked with an explicit load condition.
- [ ] New scripts support `--self-test` and are deterministic.
- [ ] The preserved-invariants and grounding checks still pass.

## Reporting issues

Use the issue templates. For security-sensitive issues, see
[SECURITY.md](SECURITY.md) instead of filing a public issue.

## License of contributions

By contributing, you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).
