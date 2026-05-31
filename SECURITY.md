# Security Policy

## Reporting a vulnerability

If you discover a security issue in this skill — for example a validator that
could be bypassed, a generated-skill contract that could lead an agent to leak
secrets or run unsafe commands, or grounding artifacts that could be poisoned —
please **do not open a public issue**.

Instead, use GitHub's private vulnerability reporting:
**Security → Report a vulnerability** on this repository, or open a
[private security advisory](https://github.com/srinitude/building-deterministic-skills/security/advisories/new).

Please include a description, steps to reproduce (a minimal `SKILL.md`/script
snippet is ideal), and any suggested remediation. We aim to acknowledge reports
within 7 days.

## Scope

This is a documentation-and-validators meta-skill. The highest-impact concerns:

1. A validator that passes a skill a reasonable security scanner would reject.
2. A generated-skill output contract that encourages exfiltration, destructive
   commands, or editing of a deployed agent package.
3. Tampered source-grounding artifacts under `reports/` that would let false
   claims pass `check-source-grounding.py`.

All shipped scripts are stdlib-only and perform no network access or writes
outside the skill directory.
