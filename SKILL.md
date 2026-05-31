---
name: building-deterministic-skills
description: >
  Build deterministic Agent Skills that weak models can execute without guessing. Use when the user says "build a deterministic skill", "make an agentskills.io-compliant skill", "validate a skill against hermes-agent", "make the skill easy for dumb models", "write a skill generator", "add skill evals", or "ensure skills_guard passes", even if they do not say "Agent Skills" explicitly. Do NOT use for ordinary editing, pure trigger tuning, non-Hermes prompt engineering, hermes-agent-skill-authoring, or skill-description-optimizer tasks.
license: Apache-2.0
version: 0.1.0
metadata:
  hermes:
    tags: [skills, authoring, deterministic, agentskills, validation, weak-models]
    related_skills: [hermes-agent-skill-authoring, skill-description-optimizer]
---

# Building deterministic, dumb-model-friendly Agent Skills

## CRITICAL RULES (read first)

1. Preserve both targets: the skill you write must pass Hermes validators and the skill it generates must be easy for weak models to follow.
2. Front-load and book-end every generated skill's critical rules. Put the rules near the top, then repeat the final self-check at the bottom.
3. Use defaults-not-menus. Choose one default path for the workflow; put exceptions in Gotchas.
4. Use procedures-over-declarations. Write numbered steps and exact commands, not broad advice.
5. Offload math/counting/exact string checks to scripts. Do not rely on model arithmetic.
6. Add an INSUFFICIENT CONTEXT escape hatch when missing facts would otherwise cause hallucination.
7. Use conditional progressive disclosure: say exactly when to load each reference, asset, script, and eval.
8. Validate every claim with a command before returning to the user.

## Gotchas

- Dumb models lose rules buried in the middle. Keep load-bearing rules in `SKILL.md`, not only in references.
- Too many choices create failure. A single safe default beats a menu of options.
- Ambiguous terms drift. Use one-term-per-concept and repeat that term exactly.
- Free-form output varies. Provide output templates for fixed formats.
- Long skills rot context. Move details to `references/dumb-model-authoring.md` with explicit load triggers.
- The Hermes scanner may warn on research artifacts; `tools.skills_guard.scan_skill(source='agent-created')` may still be allowed.

## When to use

Use this skill when the user wants a deterministic Agent Skill package that is:

1. agentskills.io compliant;
2. validated against the live hermes-agent codebase;
3. structured so small, quantized, distilled, low-reasoning, sycophantic, hallucination-prone, context-rot-prone models can still execute it;
4. packaged with `references/`, `scripts/`, `assets/`, and `evals/` when those resources are required.

Do not use this skill for ordinary prose editing, standalone documentation, pure description optimization, or skills that intentionally rely on model creativity.

## Mandatory directory layout

```text
skill-name/
├── SKILL.md
├── references/   # load only when a named condition says to load it
├── scripts/      # deterministic validators and helpers
├── assets/       # templates, schemas, fixtures, skeletons
└── evals/        # trigger, anti-trigger, and functional cases
```

Any file referenced from `SKILL.md` must live in one of those four directories. Keep file references one level deep when possible.

## Frontmatter rules (Hermes + agentskills.io)

1. File starts at byte 0 with `---` and closes frontmatter with `\n---\n`.
2. `name` has 1-64 lowercase letters, digits, and hyphens; it equals the parent directory name.
3. `description` is 1-1024 characters, imperative, and includes what the skill does plus when to use it.
4. `description` includes at least six quoted trigger phrases and one explicit `Do NOT use for` clause naming at least two neighboring skills.
5. `license` is present.
6. `compatibility` appears only when environment requirements exist and stays under 500 characters.
7. Portable agentskills.io repositories use flat string metadata. Local Hermes skills may keep `metadata.hermes` when needed.
8. Total `SKILL.md` length stays at or below 100000 characters; body stays at or below 500 lines.

## Dumb-model output contract for generated skills

Every skill produced with this skill must include all items below.

1. A `## CRITICAL RULES` section within the first 80 body lines.
2. A `## Gotchas` section in `SKILL.md` with concrete failure corrections.
3. A numbered workflow with exact commands and no branching menus.
4. Front-loaded-AND-book-ended critical rules.
5. Defaults-not-menus for every ambiguous choice.
6. Procedures-over-declarations for every reusable task pattern.
7. An INSUFFICIENT CONTEXT escape hatch that names the missing field and stops instead of guessing.
8. Output templates for fixed-format deliverables.
9. Offloading math/counting to scripts for all counts, hashes, line totals, schema checks, and exact string validation.
10. Conditional progressive disclosure instructions that name the exact in-skill reference file only after that file exists.
11. One-term-per-concept naming across the description, workflow, scripts, and reports.
12. A final verification checklist that repeats the critical safety and validation checks.

Read `references/dumb-model-authoring.md` before changing this output contract. Start new generated skills from `assets/dumb-model-skill-skeleton.md` when the user has not supplied a stronger template.

## Ordered workflow

1. Run source validation command:
   `cd /Users/kiren/.hermes/hermes-agent && ./venv/bin/python -m pytest tests/tools/test_skill_manager_tool.py tests/tools/test_skill_size_limits.py tests/agent/test_skill_utils.py tests/tools/test_skills_guard.py -q`
2. Read the user's artifact and identify the one skill root to create.
3. Create `SKILL.md`, `references/`, `scripts/`, `assets/`, and `evals/` in that skill root.
4. Write the description first, then verify it has six quoted trigger phrases and a `Do NOT use for` clause.
5. Write `## CRITICAL RULES`, `## Gotchas`, and the numbered workflow before adding long references.
6. Add conditional reference pointers only after the referenced file exists.
7. Put mechanical checks into scripts and make every script support `--self-test`.
8. Add `evals/evals.json` with trigger, anti-trigger, and functional cases.
9. Run every validation command in the Validation pipeline section.
10. Fix each failing command, then rerun the same command.
11. Return only after all checks pass and the final report includes command evidence.

## Validation pipeline

1. **Hermes frontmatter:** run `scripts/check-skill-frontmatter.py` for this skill, and for generated skills import `tools.skill_manager_tool._validate_frontmatter` plus `tools.skill_manager_tool._validate_content_size`.
2. **Hermes discovery:** import `agent.skill_utils.get_all_skills_dirs` and `agent.skill_utils.iter_skill_index_files`, then confirm the skill path is found.
3. **Hermes security scan:** import `tools.skills_guard.scan_skill` and `tools.skills_guard.should_allow_install`; scan with `source='agent-created'` and require `allowed is True`.
4. **Description quality:** require `Use when`, at least six quoted trigger phrases, one `Do NOT use for` clause, and length at or below 1024 characters.
5. **Dumb-model coverage:** run `scripts/check-dumb-model-coverage.py --factors /Users/kiren/Downloads/llm-smart-vs-dumb-factors.md --guide /Users/kiren/Downloads/writing-agent-skills-for-dumb-models.md`.
6. **Self-application readability:** run `scripts/check-dumb-model-readability.py SKILL.md`.
7. **Source grounding:** run `scripts/check-source-grounding.py` after Firecrawl map and scrape artifacts exist.
8. **Determinism:** run `scripts/check-determinism.py` and require byte-identical `--self-test` output for every script.
9. **No dead links:** run `scripts/check-no-dead-links.py`.
10. **Hermes pytest:** run `cd /Users/kiren/.hermes/hermes-agent && ./venv/bin/python -m pytest tests/tools/test_skill_manager_tool.py tests/tools/test_skill_size_limits.py tests/agent/test_skill_utils.py tests/tools/test_skills_guard.py -q`.

## Description-quality checklist

The description is the activation surface. It must contain:

1. Imperative `Use when` wording.
2. At least six quoted trigger phrases users actually say.
3. One explicit `Do NOT use for` clause naming at least two related skills.
4. A hedge such as `even if they do not say "Agent Skills" explicitly`.
5. What the skill produces and when to activate it.
6. No XML angle brackets in field values.
7. Length at or below 1024 characters.
8. One-term-per-concept vocabulary aligned with the body.

## Community skill adoption

When adopting a third-party skill repository into the local skill library, follow `references/third-party-skill-adoption.md` only after the official installer has been tried and scan findings have been classified.

## Standalone productized skill repositories

When the user wants a deterministic agentskills.io skill built, tested, pushed, and versioned as a standalone repo, follow `references/productized-agent-skill-release.md`. Keep the dumb-model output contract above in force while following that release chronology.

## Common pitfalls

1. **Putting referenced files outside the four resource directories.** Move them into `references/`, `scripts/`, `assets/`, or `evals/` and update the pointer.
2. **Letting generated skills hide critical rules in a reference.** Keep CRITICAL RULES and Gotchas in `SKILL.md`.
3. **Offering menus in workflows.** Pick the default path and put exceptions in Gotchas.
4. **Asking the model to count, hash, diff, sort, or validate exact strings in its head.** Write a script.
5. **Using inconsistent names for the same concept.** Pick one term and reuse it everywhere.
6. **Writing a description with too few trigger phrases.** Six realistic phrases is the minimum.
7. **Writing a long SKILL.md without conditional progressive disclosure.** Move details to a reference and say when to read it.
8. **Removing `_validate_frontmatter`, `_validate_content_size`, `iter_skill_index_files`, `skills_guard`, `scan_skill`, or the pytest gate while simplifying.** That lowers coverage.
9. **Deleting `references/third-party-skill-adoption.md` or `references/productized-agent-skill-release.md`.** These are still wired to important workflows.
10. **Treating a caution verdict from `tools.skills_guard.scan_skill(source='agent-created')` as failure.** Require `should_allow_install` to return `True`.
11. **Using broad advice without examples.** Replace it with a numbered procedure and an output template.
12. **Forgetting to book-end critical rules.** Repeat the final self-check in the verification checklist.

## Before you finish (book-end)

1. Did the generated skill front-load critical rules and repeat them in the final checklist?
2. Did the generated skill include Gotchas, defaults-not-menus, output templates, one-term-per-concept, and INSUFFICIENT CONTEXT?
3. Did every count, hash, exact string check, and link check run through a script?
4. Did every reference pointer name the condition that triggers loading it?
5. Did every validation command run and pass?

## Verification checklist

- [ ] `scripts/check-skill-frontmatter.py` passes for `SKILL.md`.
- [ ] `scripts/check-preserved-invariants.py` confirms preserved Hermes validation coverage and at least eight numbered pitfalls.
- [ ] `references/dumb-model-authoring.md` exists and is linked from `SKILL.md`.
- [ ] The generated-skill output contract requires front-loaded-AND-book-ended critical rules, Gotchas section, defaults-not-menus, INSUFFICIENT CONTEXT, output templates, offloading math/counting to scripts, and conditional progressive disclosure.
- [ ] `scripts/check-dumb-model-coverage.py --factors /Users/kiren/Downloads/llm-smart-vs-dumb-factors.md --guide /Users/kiren/Downloads/writing-agent-skills-for-dumb-models.md` passes.
- [ ] `scripts/check-dumb-model-readability.py SKILL.md` passes.
- [ ] `scripts/check-source-grounding.py` passes for `reports/source-grounding/firecrawl/agentskills-io/map.json` and the scrape ledger.
- [ ] `scripts/check-determinism.py` passes.
- [ ] `scripts/check-no-dead-links.py` passes.
- [ ] `scripts/check-report-grounding.py` passes after the change report exists.
- [ ] The Hermes pytest gate passes: `pytest tests/tools/test_skill_manager_tool.py tests/tools/test_skill_size_limits.py tests/agent/test_skill_utils.py tests/tools/test_skills_guard.py`.
- [ ] `tools.skills_guard.scan_skill(source='agent-created')` returns `allowed=True` through `should_allow_install`.
- [ ] Final report records before and after sha256 values and rejected tradeoffs.
- [ ] Critical rules stayed front-loaded and book-ended in the generated skill contract.
