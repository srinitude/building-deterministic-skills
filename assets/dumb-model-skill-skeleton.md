---
name: example-skill-name
description: >
  Do one concrete task with deterministic steps. Use when the user says "trigger phrase one", "trigger phrase two", "trigger phrase three", "trigger phrase four", "trigger phrase five", or "trigger phrase six", even if they do not name the tool explicitly. Do NOT use for neighboring-skill-one or neighboring-skill-two tasks.
license: MIT
---

# Example Skill Name

## CRITICAL RULES

1. State the non-negotiable rule.
2. Use scripts for exact counts, hashes, and string checks.
3. If a required field is missing, output `INSUFFICIENT CONTEXT: <field>` and stop.

## Gotchas

- Concrete mistake the model is likely to make: exact correction.
- Ambiguous term: canonical term to use.

## Workflow

Progress:
- [ ] 1. Run the exact command: `python3 scripts/validate_input.py --input INPUT`
- [ ] 2. If the command exits nonzero, report the stderr line verbatim.
- [ ] 3. Produce the output using the template below.
- [ ] 4. Run the verification command: `python3 scripts/verify_output.py --input OUTPUT`

## Output template

```text
Result:
Evidence:
Assumptions:
```

## References

- Read `references/details.md` ONLY when step 1 reports missing domain details.

## Verification checklist

- [ ] Critical rules were read before starting.
- [ ] Gotchas were checked before acting.
- [ ] Exact checks ran through scripts.
- [ ] Output matches the template.
- [ ] Critical rules were rechecked before finishing.
