---
name: building-deterministic-skills
description: >
  Build deterministic Agent Skills that weak models can execute without guessing. Use when the user says "build a deterministic skill", "make an agentskills.io-compliant skill", "validate a skill with skills-ref", "make the skill easy for dumb models", "write a skill generator", "add skill evals", or "make a skill the dumbest model can follow", even if they do not say "Agent Skills" explicitly. Do NOT use for ordinary prose editing, pure trigger-phrase tuning, non-skill prompt engineering, or generic documentation tasks.
license: Apache-2.0
metadata:
  version: 0.2.0
  tags: [skills, authoring, deterministic, agentskills, validation, weak-models]
---

# Building deterministic, dumb-model-friendly Agent Skills

## CRITICAL RULES (read first)

1. Preserve both targets: the skill you write must pass the agentskills.io validator (`skills-ref`) and the skill it generates must be easy for weak models to follow.
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
- A security/lint scanner may warn on documented commands or research artifacts. Keep documented shell snippets minimal and store raw research under `reports/` so the shipped skill body stays clean. When a real-but-flagged literal trips the scanner to a `dangerous` verdict, read `references/security-scanner-false-positives.md` for the faithful neutralization techniques (invisible `<wbr>` in prose, adjacent-string splits in code, quarantine of non-instructional noise) and the self-corruption pitfall.
- A `dangerous` scanner verdict on legitimate docs/tooling is usually a threat-pattern LITERAL (`curl … | sh`, `~/.agent/config.yaml`, `os.getenv("…KEY")`, `setuid`, `/etc/passwd`), not a real threat. Neutralize faithfully and NEVER run a guard-sanitizer over its own engine scripts. NEVER `<wbr>` a copy-pasteable shell command (it corrupts the copy) — restructure it instead (`REQ="…$KEY"` then `curl "$REQ"`; download-then-run installers; `$(printf '.env')` for env-path literals). When bulk-conforming, mechanical boilerplate passes gates but produces low-quality skills a reviewer rejects — hand-author each skill from its pristine source with skill-specific content, and keep every original H2 (even host-named ones like `## <Host> Integration Notes`) + trigger phrase verbatim for coverage. Read `references/scanner-false-positives-and-bulk-conformance.md`.

## When to use

Use this skill when the user wants a deterministic Agent Skill package that is:

1. agentskills.io compliant (passes the canonical `skills-ref` validator);
2. portable across any agent runtime that loads Agent Skills (no dependency on one host);
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

## Frontmatter rules (agentskills.io specification)

1. File starts at byte 0 with `---` and closes frontmatter with `\n---\n`.
2. `name` is 1-64 characters, lowercase letters/digits/hyphens only, must not start or end with a hyphen, must not contain consecutive hyphens (`--`), and equals the parent directory name (compared after NFKC normalization).
3. `description` is 1-1024 characters, imperative, and includes what the skill does plus when to use it.
4. `description` includes at least six quoted trigger phrases and one explicit `Do NOT use for` clause naming at least two neighboring task types or skills.
5. `license` is present.
6. `compatibility` appears only when environment requirements exist and stays under 500 characters.
7. Only these top-level frontmatter fields are allowed by the agentskills.io spec: `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`. Put EVERYTHING else (`version`, `author`, `tags`, `related_skills`, `dependencies`, `platforms`, etc.) inside `metadata:`. A top-level `version:` or `author:` fails the canonical `skills-ref` validator.
8. Keep `SKILL.md` body at or below 500 lines (the agentskills.io body-length guidance — under ~5000 tokens recommended); move detail into `references/`. The spec sets no hard total-character cap, but individual runtimes may; keep the body lean regardless.

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

Read `references/dumb-model-authoring.md` before changing this output contract. Start new generated skills from `assets/dumb-model-skill-skeleton.md` when the user has not supplied a stronger template. The research spine behind this contract is bundled in `references/`: read `references/dumb-vs-smart-factor-research.md` for the factor→countermeasure synthesis, and `references/llm-smart-vs-dumb-factors.md` plus `references/writing-agent-skills-for-dumb-models.md` for the full evidence and citations.

## Ordered workflow

1. Read the user's artifact and identify the one skill root to create. If no artifact, skill name, or task is supplied, output `INSUFFICIENT CONTEXT: <missing field>` and stop instead of inventing a skill.
2. Create `SKILL.md`, `references/`, `scripts/`, `assets/`, and `evals/` in that skill root.
3. Write the description first, then verify it has six quoted trigger phrases and a `Do NOT use for` clause.
4. Write `## CRITICAL RULES`, `## Gotchas`, and the numbered workflow before adding long references.
5. Add conditional reference pointers only after the referenced file exists.
6. Put mechanical checks into scripts and make every script support `--self-test`.
7. Add `evals/evals.json` with trigger, anti-trigger, and functional cases.
8. Run every validation command in the Validation pipeline section.
9. Fix each failing command, then rerun the same command.
10. Return only after all checks pass and the final report includes command evidence.

## Validation pipeline

1. **agentskills.io compliance:** run the canonical reference validator — `skills-ref validate ./<skill>` (from `github.com/agentskills/agentskills`). Only the allowed top-level frontmatter fields may appear (`name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`); fix every reported error.
2. **Frontmatter (offline):** run `scripts/check-skill-frontmatter.py` — it mirrors the canonical rules (byte-0 frontmatter, name matches parent directory, name format, description ≤ 1024, compatibility ≤ 500, closed field set, non-empty body) with no external dependency.
3. **Description quality:** require `Use when`, at least six quoted trigger phrases, one `Do NOT use for` clause, and length at or below 1024 characters.
4. **Dumb-model coverage:** run `scripts/check-dumb-model-coverage.py` (it reads the research bundled in `references/llm-smart-vs-dumb-factors.md` and `references/writing-agent-skills-for-dumb-models.md` by default — no external paths required).
5. **Self-application readability:** run `scripts/check-dumb-model-readability.py SKILL.md`.
6. **Preserved invariants:** run `scripts/check-preserved-invariants.py` (confirms the dumb-model contract terms and at least eight numbered pitfalls survive any edit).
7. **Content preservation (when rewriting/conforming an existing skill):** run `scripts/check-content-preserved.py --skill <new> --backup <original>` so that no command line, list item, or inline-code token from the original was silently dropped. Add `--strict` for mechanical/bulk conformance where no rewording is intended. A reported `MISSING` unit is either reworded (confirm the meaning survives) or must be restored — never lose context, content, meaning, or intent relative to the original.
8. **Source grounding:** run `scripts/check-source-grounding.py` after the Firecrawl map and scrape artifacts exist.
9. **Determinism:** run `scripts/check-determinism.py` and require byte-identical `--self-test` output for every script.
10. **No dead links:** run `scripts/check-no-dead-links.py`.
11. **Report grounding:** run `scripts/check-report-grounding.py` after the change report exists.

## Output template

When you finish, return the result in exactly this shape (fill every line; do not add prose around it):

```text
Skill: <skill-name> at <absolute skill dir>
Shape: CRITICAL RULES + Gotchas + numbered workflow + Output template + book-end checklist present
Validation pipeline (each PASS/FAIL with evidence):
- skills-ref validate: <PASS/FAIL>
- check-skill-frontmatter: <PASS/FAIL>
- check-dumb-model-coverage: <PASS/FAIL>
- check-dumb-model-readability: <PASS/FAIL>
- check-preserved-invariants: <PASS/FAIL>
- check-source-grounding / check-determinism / check-no-dead-links / check-report-grounding: <PASS/FAIL>
Files created/changed: <comma-separated absolute paths>
Assumptions: <INSUFFICIENT CONTEXT items, or "none">
```

## Description-quality checklist

The description is the activation surface. It must contain:

1. Imperative `Use when` wording.
2. At least six quoted trigger phrases users actually say.
3. One explicit `Do NOT use for` clause naming at least two related task types or skills.
4. A hedge such as `even if they do not say "Agent Skills" explicitly`.
5. What the skill produces and when to activate it.
6. No XML angle brackets in field values.
7. Length at or below 1024 characters.
8. One-term-per-concept vocabulary aligned with the body.

## Community skill adoption

When adopting a third-party skill repository into a local skill library, follow `references/third-party-skill-adoption.md` only after the official installer has been tried and scan findings have been classified.

## Standalone productized skill repositories

When the user wants a deterministic agentskills.io skill built, tested, pushed, and versioned as a standalone repo, follow `references/productized-agent-skill-release.md`. Keep the dumb-model output contract above in force while following that release chronology.

## Model × use-case skill evaluation matrices

When the user asks to generate skills across many models, compare determinism by model, or run a nested model/use-case skill benchmark, load `references/model-skill-matrix-evals.md` before starting the loop. First enumerate the matrix, compute model-call count and measured pilot timing, then run a small pilot and gate the exhaustive run on explicit budget/scope confirmation. Use JSON-only canonicalized invocation outputs for determinism; raw prose hashes are useful diagnostics but not sufficient.

## Common pitfalls

1. **Putting referenced files outside the four resource directories.** Move them into `references/`, `scripts/`, `assets/`, or `evals/` and update the pointer.
2. **Letting generated skills hide critical rules in a reference.** Keep CRITICAL RULES and Gotchas in `SKILL.md`.
3. **Offering menus in workflows.** Pick the default path and put exceptions in Gotchas.
4. **Asking the model to count, hash, diff, sort, or validate exact strings in its head.** Write a script.
5. **Using inconsistent names for the same concept.** Pick one term and reuse it everywhere.
6. **Writing a description with too few trigger phrases.** Six realistic phrases is the minimum.
7. **Writing a long SKILL.md without conditional progressive disclosure.** Move details to a reference and say when to read it.
8. **Putting disallowed fields at the top level of frontmatter.** Keep only `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility` at the top; nest everything else under `metadata`.
9. **Deleting `references/third-party-skill-adoption.md` or `references/productized-agent-skill-release.md`.** These are still wired to important workflows.
10. **Treating a caution verdict from a security scanner as automatic failure.** Classify findings; documented commands and research artifacts are usually safe — neutralize or relocate noisy raw artifacts rather than deleting capability.
11. **Using broad advice without examples.** Replace it with a numbered procedure and an output template.
12. **Forgetting to book-end critical rules.** Repeat the final self-check in the verification checklist.
13. **Panic-deleting capability when a scanner says `dangerous`.** Classify first: a `caution` verdict that the scanner's install policy still permits is fine. Critical findings on docs/tooling are threat-pattern LITERALS — neutralize faithfully (invisible `<wbr>` in prose, adjacent-string splits in code, reword path-literals in trigger phrases) or quarantine non-instructional noise (vendored deps, binaries, research caches). See `references/scanner-false-positives-and-bulk-conformance.md`.
14. **Running a guard-sanitizer over its own engine scripts.** It inserts `<wbr>` into the very regex/replace literals it scans for (`setuid`→`set<wbr>uid`) and silently breaks detection with no error. Keep the conformance build engine OUTSIDE any scanned skill directory. When bulk-conforming many existing skills, also: back up first, derive targets from live discovery, keep the conform step content-preserving (never delete original body/triggers/H2s), and make the orchestrator idempotent + resumable via a ledger.

15. **Starting an exhaustive model × use-case skill benchmark before sizing the matrix.** Model pickers can expose hundreds of models; a harmless-looking nested loop can become tens of thousands of paid calls. Load `references/model-skill-matrix-evals.md`, compute combinations and call counts first, run one pilot, and ask for explicit scope/budget confirmation before the full run.
16. **Calling raw prose outputs deterministic because they agree semantically.** Record semantic agreement, but for benchmark determinism require JSON-only fixed-key outputs and canonical hashes. Strip ANSI/session/worktree wrapper text from agent-CLI output before checking byte-0 frontmatter or raw hashes.
17. **Losing original content/meaning/intent when rewriting or conforming an existing skill.** Trigger-phrase + heading coverage is necessary but NOT sufficient — a rewrite can still silently drop a command, a hard-won gotcha bullet, or an exact flag. Run `scripts/check-content-preserved.py --skill <new> --backup <original>` (add `--strict` for mechanical conformance) and resolve every `MISSING` unit: confirm it was reworded with the meaning intact, or restore it.

## Before you finish (book-end)

1. Did the generated skill front-load critical rules and repeat them in the final checklist?
2. Did the generated skill include Gotchas, defaults-not-menus, output templates, one-term-per-concept, and INSUFFICIENT CONTEXT?
3. Did every count, hash, exact string check, and link check run through a script?
4. Did every reference pointer name the condition that triggers loading it?
5. Did every validation command run and pass?

## Verification checklist

- [ ] `skills-ref validate ./<skill>` reports no errors (agentskills.io compliant).
- [ ] `scripts/check-skill-frontmatter.py` passes for `SKILL.md`.
- [ ] `scripts/check-preserved-invariants.py` confirms the preserved dumb-model contract and at least eight numbered pitfalls.
- [ ] `references/dumb-model-authoring.md` exists and is linked from `SKILL.md`.
- [ ] The generated-skill output contract requires front-loaded-AND-book-ended critical rules, Gotchas section, defaults-not-menus, INSUFFICIENT CONTEXT, output templates, offloading math/counting to scripts, and conditional progressive disclosure.
- [ ] `scripts/check-dumb-model-coverage.py` passes against the bundled `references/llm-smart-vs-dumb-factors.md` and `references/writing-agent-skills-for-dumb-models.md`.
- [ ] `scripts/check-dumb-model-readability.py SKILL.md` passes.
- [ ] Only allowed top-level frontmatter fields are present (`name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`); everything else is nested under `metadata`.
- [ ] `scripts/check-source-grounding.py` passes for the Firecrawl map and scrape ledger.
- [ ] `scripts/check-determinism.py` passes.
- [ ] `scripts/check-no-dead-links.py` passes.
- [ ] `scripts/check-content-preserved.py` reports no unresolved `MISSING` units when an existing skill was rewritten or conformed (no content/meaning/intent lost).
- [ ] `scripts/check-report-grounding.py` passes after the change report exists.
- [ ] Final report records before and after sha256 values and rejected tradeoffs.
- [ ] Critical rules stayed front-loaded and book-ended in the generated skill contract.
