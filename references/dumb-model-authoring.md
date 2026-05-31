# Dumb-model authoring reference

Use this reference when a generated skill must remain understandable to small, quantized, distilled, low-reasoning, context-rot-prone, sycophantic, hallucination-prone, or otherwise weak models.

## Source grounding

Local validation sources:

1. `/Users/kiren/Downloads/llm-smart-vs-dumb-factors.md`
2. `/Users/kiren/Downloads/writing-agent-skills-for-dumb-models.md`

Firecrawl source artifacts used for the official Agent Skills format and writing practices:

1. `reports/source-grounding/firecrawl/agentskills-io/scrapes/agentskills.io-specification.json`
2. `reports/source-grounding/firecrawl/agentskills-io/scrapes/agentskills.io-skill-creation-best-practices.json`
3. `reports/source-grounding/firecrawl/agentskills-io/scrapes/agentskills.io-skill-creation-optimizing-descriptions.json`
4. `reports/source-grounding/firecrawl/agentskills-io/scrapes/agentskills.io-skill-creation-using-scripts.json`
5. `reports/source-grounding/firecrawl/agentskills-io/scrapes/agentskills.io-skill-creation-evaluating-skills.json`

## Dumbness factor to countermeasure mapping

| Dumbness factor | Failure mode in skills | Required countermeasure in generated skills |
|---|---|---|
| emergent-threshold | Multi-step reasoning may not exist in the target model. | Use procedures-over-declarations: numbered steps, decision tables, exact commands, and no hidden reasoning jumps. |
| tokenization | Numbers, counts, hashes, and exact strings are error-prone. | Offload math/counting to scripts; make exact checks executable. |
| quantization/distillation | Fine nuance and edge cases are lost first. | Keep a Gotchas section in `SKILL.md` with concrete failure corrections. |
| sycophancy | The model may agree with a false premise. | Add validation loops, plan-validate-execute gates, and explicit pass/fail checks. |
| hallucination | The model may fabricate missing facts. | Add an INSUFFICIENT CONTEXT escape hatch that names the missing field. |
| low-test-time-reasoning | The model blurts without self-correction. | Use checklists plus validate-fix-rerun loops. |
| lost-in-the-middle | Buried rules are skipped. | Use front-loaded-AND-book-ended critical rules and keep Gotchas in `SKILL.md`. |
| context-rot | Long activated context reduces reliability. | Keep `SKILL.md` under 500 lines and use conditional progressive disclosure. |
| prompt-bloat | Irrelevant prose distracts the model. | Add only what the agent lacks; omit generic filler. |
| curse-of-instructions | Each extra rule multiplies failure risk. | Use defaults-not-menus, moderate detail, and sequence rules instead of stacking them. |
| instruction-sensitivity | Wording changes alter behavior. | Use one-term-per-concept and unambiguous parameter names. |
| sampling-variability | Free-form prose changes between runs. | Provide output templates for fixed formats. |
| weak-triggering | The skill never loads. | Optimize the description with realistic trigger phrases and near-miss anti-triggers. |

## Required generated-skill shape

````markdown
# Skill Title

## CRITICAL RULES
1. State non-negotiable rules here.
2. Point to scripts for exact checks.
3. Use INSUFFICIENT CONTEXT when required facts are missing.

## Gotchas
- Concrete failure the model is likely to make.
- Correct action for that failure.

## Workflow
Progress:
- [ ] 1. Exact command or tool call.
- [ ] 2. Validate output with a script.
- [ ] 3. Fix the named failure and rerun the same validator.

## Output template
```text
Result:
Evidence:
Assumptions:
```

## Verification checklist
- [ ] Critical rules were read before starting.
- [ ] Scripts validated every exact count or path.
- [ ] Critical rules are rechecked before finishing.
````

## Authoring steps for weak models

1. Write the `description` first. Include what, when, six quoted trigger phrases, and a `Do NOT use for` clause.
2. Write `## CRITICAL RULES` before any long explanation.
3. Write `## Gotchas` next. Convert every known correction into a concrete rule.
4. Write the workflow as numbered steps. Each step has one action and one expected result.
5. Choose defaults-not-menus. Put rare exceptions in Gotchas.
6. Add scripts for math, counting, exact string validation, link checks, JSON checks, table checks, and report grounding.
7. Add output templates for any fixed response shape.
8. Move long background material into `references/` and state the exact condition for loading it.
9. Add evals that run against the weakest model the skill must support.
10. End with a verification checklist that book-ends the critical rules.

## Validation commands for this skill package

- Run `scripts/check-dumb-model-coverage.py` to confirm every dumbness factor above appears with a matching countermeasure.
- Run `scripts/check-dumb-model-readability.py SKILL.md` to confirm the skill itself follows the same weak-model rules.
- Run `scripts/check-source-grounding.py` to confirm the Firecrawl map, scrape ledger, and cited Agent Skills artifacts exist.
