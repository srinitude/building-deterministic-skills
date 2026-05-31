# Writing Powerful Agent Skills the Dumbest Model Can Follow

A practical, spec-compliant authoring guide for building [Agent Skills](https://agentskills.io) that execute reliably **even on small, quantized, distilled, or otherwise weak models.**

This guide combines two sources:

1. **The cognitive theory** — [the factors that make an LLM dumb vs. smart](./llm-smart-vs-dumb-factors.md). A skill can't raise a model's intrinsic ceiling, but **bad skill design wastes capability the model already has**, and **good design recovers it.** Your job is to remove every avoidable source of dumbness from the one stage you control: *inference*.
2. **The official format and methodology** — the [Agent Skills specification and skill-creation guides](https://agentskills.io) (spec, best practices, description optimization, eval-driven iteration, and script design). These tell you *how* to package and validate the skill.

This document fuses them: every official best practice is annotated with *which dumbness mechanism it defeats*, so you understand not just the rule but why it works.

> **Mental model:** Treat the target model as a brilliant but extremely literal new hire who has *no working memory beyond the page in front of them, gets distracted by clutter, can't ask follow-up questions, and is rewarded for sounding confident even when wrong.* Write for that person.

---

## What an Agent Skill Is

A skill is a folder containing a `SKILL.md` file plus optional supporting resources ([What are skills?](https://agentskills.io/what-are-skills.md)):

```
my-skill/
├── SKILL.md        # Required: YAML frontmatter (metadata) + Markdown instructions
├── scripts/        # Optional: executable code the agent can run
├── references/     # Optional: docs loaded on demand
├── assets/         # Optional: templates, schemas, lookup tables
└── evals/          # Recommended: test cases for eval-driven iteration
```

Agents load skills via **progressive disclosure** in three stages ([Overview](https://agentskills.io/home.md)) — and each stage maps directly to a dumbness defense:

| Stage | What loads | Dumbness it defeats |
|---|---|---|
| **1. Discovery** | Only `name` + `description` (~100 tokens) of every skill, at startup | **Context rot / prompt bloat** — keeps the always-on footprint tiny |
| **2. Activation** | Full `SKILL.md` body, only when a task matches the description | **Curse of instructions** — the model only sees rules relevant *now* |
| **3. Execution** | `scripts/`, `references/`, `assets/` pulled in only at the step that needs them | **Lost in the middle** — detail arrives exactly when attention is on it |

This is why progressive disclosure isn't just an organizing convenience — it is the single most important architectural defense against weak-model failure.

---

## The Translation Table: Dumbness Factor → Countermeasure

Each row maps a finding from the [factors doc](./llm-smart-vs-dumb-factors.md) to a concrete authoring rule, cross-referenced to the official guidance that implements it.

| Dumbness factor | What it means for a weak model | Countermeasure | Official basis |
|---|---|---|---|
| **Emergent-ability threshold** — reasoning doesn't exist below a scale threshold | Small models can't reliably do multi-step reasoning unaided | Give the *procedure*, not the reasoning. Decision tables + numbered steps. | "Favor procedures over declarations" |
| **Tokenization** — BPE number splits → systematic arithmetic errors | Bad at math, counting, exact string ops | Offload to a tool or bundled script. Never compute in-head. | "Bundling reusable scripts" |
| **Quantization / distillation loss** — fine-grained reasoning degrades first | Nuance and implicit inference erode | State edge cases explicitly via a **Gotchas** section. | "Gotchas sections" |
| **Sycophancy** — trained to agree, not to be correct | Rubber-stamps wrong premises | Validation loops + plan-validate-execute + explicit stop conditions. | "Validation loops", "Plan-validate-execute" |
| **Hallucination from guessing-rewarded training** | Fabricates confidently | Authorize uncertainty: an `INSUFFICIENT CONTEXT` escape hatch. | "Calibrating control" |
| **No / low test-time reasoning** — weak models blurt | Single-pass, no self-correction | Checklists + validation loops that force think→act→verify. | "Checklists for multi-step workflows" |
| **Lost in the middle** — U-shaped attention | Buried rules get skipped | Front-load + book-end constraints; keep gotchas in `SKILL.md`. | "Keep gotchas in SKILL.md" |
| **Context rot** — accuracy falls as input grows | Long skills degrade the model pre-task | `SKILL.md` < 500 lines / 5000 tokens; progressive disclosure. | Spec: "Progressive disclosure" |
| **Prompt bloat** — irrelevant context degrades accuracy | Every extra sentence is a distraction | "Add what the agent lacks, omit what it knows." | "Spending context wisely" |
| **Curse of instructions** — all-rules success ≈ (per-rule rate)^N | Each added rule multiplies failure odds | Aim for moderate detail; sequence don't stack; provide defaults not menus. | "Aim for moderate detail", "Provide defaults, not menus" |
| **Instruction sensitivity** — wording swings behavior | Inconsistent terms confuse the model | One term per concept; unambiguous param names. | (cross-spec convention) |
| **Sampling variability** | Same prompt, different output | Provide an output **template**, not prose. | "Templates for output format" |
| **Weak skill triggering** — skill never loads | Capability sits unused | Optimize the `description`; test trigger rate. | "Optimizing skill descriptions" |

---

## Part 1 — The Spec (the container)

Get these mechanics right or nothing else matters. Source: [Specification](https://agentskills.io/specification.md).

### Frontmatter fields

```yaml
---
name: skill-name                    # REQUIRED
description: What it does + when to use it.   # REQUIRED
license: Apache-2.0                 # optional
compatibility: Requires git, jq, internet access   # optional, <500 chars
metadata:                           # optional
  author: example-org
  version: "1.0"
allowed-tools: Bash(git:*) Bash(jq:*) Read   # optional, experimental
---
```

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | 1–64 chars; lowercase `a-z`, digits, hyphens only; no leading/trailing/consecutive hyphens; **must match the parent directory name** |
| `description` | Yes | 1–1024 chars; non-empty; says *what* it does and *when* to use it; include trigger keywords |
| `license` | No | License name or bundled file reference |
| `compatibility` | No | ≤500 chars; environment requirements only (most skills omit it) |
| `metadata` | No | Arbitrary string→string map |
| `allowed-tools` | No | Space-delimited pre-approved tools (experimental) |

Valid: `pdf-processing`, `data-analysis`. Invalid: `PDF-Processing` (uppercase), `-pdf` (leading hyphen), `pdf--processing` (consecutive hyphens).

### Optional directories

- **`scripts/`** — executable code; self-contained or clearly documenting dependencies, with helpful errors and graceful edge-case handling.
- **`references/`** — docs the agent reads on demand (`REFERENCE.md`, `FORMS.md`, domain files). Keep each focused — smaller files = less context burned.
- **`assets/`** — static resources: templates, images, data files, schemas.

### Progressive disclosure budget (the hard ceiling against context rot)

1. **Metadata** ~100 tokens — always loaded.
2. **Instructions** — `SKILL.md` body, **< 5000 tokens recommended, under 500 lines.** Loaded on activation.
3. **Resources** — loaded only when required.

Keep file references **one level deep** from `SKILL.md`; avoid deeply nested reference chains.

### Validate before shipping

```bash
skills-ref validate ./my-skill
```

Checks frontmatter validity and naming conventions ([skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref)).

---

## Part 2 — Start From Real Expertise (don't let the model write generic mush)

The most common failure is asking an LLM to generate a skill from its general training knowledge — producing vague filler like "handle errors appropriately" or "follow best practices." That's exactly the kind of low-signal content that triggers the model to wander down unproductive paths ([Best practices](https://agentskills.io/skill-creation/best-practices.md)).

Two reliable ways to ground a skill in real expertise:

- **Extract from a hands-on task.** Complete the real task with an agent, then capture: the steps that *worked*, the **corrections you had to make**, the actual input/output formats, and the project-specific context the agent didn't already know.
- **Synthesize from existing artifacts.** Feed in your real runbooks, incident reports, API specs, schemas, code-review comments, and version-control history (patches reveal patterns through what actually changed). Project-specific material beats generic references every time.

> **Dumb-model link:** Generic advice is pure prompt bloat — it consumes context (causing context rot) while telling a weak model nothing it didn't already know. Specific gotchas are the highest-value tokens in the whole skill.

---

## Part 3 — Spend Context Wisely (defeat context rot + prompt bloat)

Once activated, the full `SKILL.md` competes for attention with conversation history, system context, and other skills. Every token is a liability for a weak model.

### Add what the agent lacks, omit what it knows

```markdown
<!-- Too verbose — the agent already knows what PDFs are -->
## Extract PDF text
PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text, you'll need a library.
pdfplumber is recommended because it handles most cases well.

<!-- Better — jumps straight to what the agent wouldn't know -->
## Extract PDF text
Use pdfplumber for text extraction. For scanned documents, fall back to
pdf2image with pytesseract.
```

The test for every line: **"Would the agent get this wrong without this instruction?"** If no, cut it. If unsure, test it (Part 6).

### Design coherent units

Scope a skill like you'd scope a function — one coherent unit that composes well. Too narrow forces multiple skills to co-load (overhead + conflicting instructions). Too broad won't trigger precisely. "Query a database and format results" is one unit; adding "database administration" is overreach.

### Aim for moderate detail — this directly beats the curse of instructions

Overly comprehensive skills *hurt*: the model struggles to find what's relevant and chases instructions that don't apply to the current task. Concise, stepwise guidance with one working example beats exhaustive documentation. **When you find yourself covering every edge case, ask whether most are better left to the agent's own judgment** — every rule you remove raises the odds the rest are followed (the (per-rule rate)^N math from the factors doc).

### Structure large skills with progressive disclosure

When a skill legitimately needs more, move detail to `references/`. The critical part: **tell the agent *when* to load each file.**

```markdown
Read references/api-errors.md ONLY if the API returns a non-200 status code.
```

…is far better than a generic "see references/ for details" — because a weak model won't infer the trigger on its own.

---

## Part 4 — Calibrate Control (match specificity to fragility)

Not every part of a skill needs the same prescriptiveness ([Best practices](https://agentskills.io/skill-creation/best-practices.md)). Most skills mix both; calibrate each part independently. **For weak models, bias toward the prescriptive end** — treat more of the skill like a narrow bridge.

### Give freedom on open fields; be prescriptive on narrow bridges

```markdown
<!-- High freedom — many valid paths (e.g., a code review). Explain WHY. -->
## Code review process
1. Check all database queries for SQL injection (use parameterized queries)
2. Verify authentication checks on every endpoint
3. Look for race conditions in concurrent code paths
4. Confirm error messages don't leak internal details

<!-- Low freedom — fragile, exact sequence required (e.g., a migration) -->
## Database migration
Run exactly this sequence:
    python scripts/migrate.py --verify --backup
Do not modify the command or add additional flags.
```

### Provide defaults, not menus (anti-bloat, anti-curse-of-instructions)

```markdown
<!-- Too many options — forces the weak model to reason about a choice -->
You can use pypdf, pdfplumber, PyMuPDF, or pdf2image...

<!-- Clear default with one escape hatch -->
Use pdfplumber for text extraction.
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

### Favor procedures over declarations (the core anti-dumbness move)

Teach *how to approach a class of problems*, not *what to produce for one instance* — weak models can't reason from a one-off answer to a new case.

```markdown
<!-- Specific answer — only useful for this exact task -->
Join orders to customers on customer_id, filter region = 'EMEA', sum amount.

<!-- Reusable method — works for any analytical query -->
1. Read the schema from references/schema.yaml to find relevant tables
2. Join tables using the _id foreign key convention
3. Apply filters from the user's request as WHERE clauses
4. Aggregate numeric columns and format as a markdown table
```

Specific details (output templates, "never output PII," tool-specific commands) are still valuable — just make the *approach* generalize.

### Explain the "why" for flexible instructions

For high-freedom parts, "Do X because Y tends to cause Z" outperforms a rigid "ALWAYS do X." A model that understands purpose makes better context-dependent decisions — and, notably, follows the instruction *more* reliably.

---

## Part 5 — Patterns for Effective Instructions

Reusable structures; use the ones that fit. Each is annotated with the dumbness it defeats.

### Gotchas sections — *defeats quantization/distillation loss + lost-in-the-middle*

The highest-value content in many skills: concrete corrections to mistakes the model *will* make, not general advice. Keep them in `SKILL.md` (front, not buried) so the model reads them before hitting the situation.

```markdown
## Gotchas
- The users table uses soft deletes. Queries MUST include
  `WHERE deleted_at IS NULL` or results include deactivated accounts.
- The user ID is `user_id` in the DB, `uid` in auth, `accountId` in billing.
  All three are the same value.
- /health returns 200 if the web server is up, even if the DB is down.
  Use /ready to check full service health.
```

> **Iteration tip:** Every time you correct the agent, add that correction here. This is the most direct way to improve a skill.

### Templates for output format — *defeats sampling variability*

Models pattern-match against concrete structures far better than they parse prose descriptions. Inline short templates; store long ones in `assets/` and reference on demand.

```markdown
## Report structure
# [Analysis Title]
## Executive summary
[One-paragraph overview]
## Key findings
- Finding with supporting data
## Recommendations
1. Specific actionable recommendation
```

### Checklists for multi-step workflows — *defeats blurting + skipped steps*

```markdown
## Form processing workflow
Progress:
- [ ] Step 1: Analyze the form (run scripts/analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run scripts/validate_fields.py)
- [ ] Step 4: Fill the form (run scripts/fill_form.py)
- [ ] Step 5: Verify output (run scripts/verify_output.py)
```

### Validation loops — *defeats sycophancy + hallucination + blurting*

Do the work → run a validator → fix → repeat until it passes. The validator can be a script, a reference checklist, or a self-check.

```markdown
## Editing workflow
1. Make your edits
2. Run validation: python scripts/validate.py output/
3. If validation fails: review the error, fix it, run validation again
4. Only proceed when validation passes
```

### Plan-validate-execute — *the strongest defense for destructive/batch ops*

Have the agent build an intermediate plan in a structured format, **validate it against a source of truth**, and only then execute. The validation step is the key ingredient — it catches a confidently-wrong plan before it does damage.

```markdown
## PDF form filling
1. Extract fields: python scripts/analyze_form.py input.pdf → form_fields.json
2. Create field_values.json mapping each field name to its value
3. Validate: python scripts/validate_fields.py form_fields.json field_values.json
4. If validation fails, revise field_values.json and re-validate
5. Fill: python scripts/fill_form.py input.pdf field_values.json output.pdf
```

A good validator error — `Field 'signature_date' not found — available: customer_name, order_total, signature_date_signed` — gives a weak model exactly enough to self-correct.

### Bundling reusable scripts — *defeats tokenization weakness + reinvention*

If execution traces show the agent reinventing the same logic each run (building a chart, parsing a format, validating output), write a tested script once and bundle it in `scripts/`. See Part 8.

---

## Part 6 — Optimize the Description So the Skill Actually Triggers

A skill only helps if it activates, and the `description` carries the *entire* triggering burden — it's all the agent sees at discovery time ([Optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions.md)).

### Writing principles

- **Imperative phrasing:** "Use this skill when…" not "This skill does…"
- **User intent, not implementation:** describe what the user is trying to achieve.
- **Be pushy:** list contexts explicitly, including ones where the user *doesn't* name the domain — "…even if they don't explicitly mention 'CSV' or 'analysis.'"
- **Concise:** a few sentences; hard cap 1024 characters.

```yaml
# Before
description: Process CSV files.

# After
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

> **Nuance:** Agents only consult skills for tasks that need capability beyond their basics. A trivial "read this PDF" may not trigger a PDF skill even on a perfect description — that's expected.

### Test triggering with eval queries

Build ~20 labeled queries (8–10 should-trigger, 8–10 should-not):

```json
[
  { "query": "I've got a spreadsheet in ~/data/q4_results.xlsx with revenue in col C and expenses in col D — can you add a profit margin column and highlight anything under 10%?", "should_trigger": true },
  { "query": "whats the quickest way to convert this json file to yaml", "should_trigger": false }
]
```

- **Strong should-trigger queries** are ones where the skill helps but the connection isn't obvious — vary phrasing, explicitness, detail, and number of steps.
- **Strong should-not-trigger queries** are **near-misses** that share keywords but need something else (e.g., "write a python script that reads a csv and uploads each row to postgres" — that's ETL, not analysis). Weak negatives ("what's the weather?") test nothing.
- **Add realism:** file paths, personal context ("my manager asked me to…"), specific column/company names, casual language, typos.

### Run multiple times and use a train/validation split

Behavior is nondeterministic — run each query ~3× and compute a **trigger rate**; should-trigger passes if rate > 0.5, should-not passes if < 0.5. To avoid overfitting the description to specific phrasings, split queries **~60% train / ~40% validation** (proportional mix in each, fixed across iterations). Optimize against train only; **select the iteration with the best *validation* pass rate** — which may not be the last one.

The loop: evaluate → identify train-set failures → revise (broaden if should-triggers miss, add boundaries if should-nots false-fire; avoid pasting in keywords from failed queries — generalize the concept) → repeat (~5 iterations) → select by validation. The [`skill-creator` skill](https://github.com/anthropics/skills/tree/main/skills/skill-creator) automates this end-to-end.

---

## Part 7 — Eval-Driven Iteration (prove the skill makes the model smarter)

A skill seeming to work once means nothing. Structured evals prove it works reliably, across edge cases, and **better than no skill at all** ([Evaluating skills](https://agentskills.io/skill-creation/evaluating-skills.md)). This is the empirical answer to the factors doc's measurement section — you're running your own clean, uncontaminated benchmark.

### Test cases

Store in `evals/evals.json`. Each has a realistic **prompt**, a human-readable **expected output**, and optional **input files**:

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales in data/sales_2025.csv. Find the top 3 months by revenue and make a bar chart.",
      "expected_output": "A bar chart showing top 3 months by revenue, labeled axes and values.",
      "files": ["evals/files/sales_2025.csv"],
      "assertions": [
        "The output includes a bar chart image file",
        "The chart shows exactly 3 months",
        "Both axes are labeled",
        "The chart title or caption mentions revenue"
      ]
    }
  ]
}
```

Start with **2–3 cases**, vary phrasing/detail/formality, cover at least one edge case, use realistic context. Add **assertions** *after* the first run, once you've seen what "good" looks like.

### The with/without baseline — the whole point

Run each case **twice: once with the skill, once without** (or vs. the previous version). Spawn each run in a **clean context** (subagent or fresh session) so the agent follows only the `SKILL.md`. Capture timing:

```json
{ "total_tokens": 84852, "duration_ms": 23332 }
```

### Assertions: specific, observable, not brittle

- Good: "The output file is valid JSON" · "The chart has labeled axes" · "Includes ≥3 recommendations."
- Weak: "The output is good" (too vague) · "uses exactly the phrase 'Total Revenue: $X'" (too brittle).
- Reserve assertions for objectively checkable things; leave style/feel to human review. Use **scripts** for mechanical checks (valid JSON, row counts, file dimensions) — more reliable than LLM judgment.

### Grade, aggregate, analyze

Record PASS/FAIL with **concrete evidence** (quote the output; don't give benefit of the doubt). Aggregate into `benchmark.json` and read the **delta** — what the skill *costs* (time, tokens) vs. what it *buys* (pass rate):

```json
{
  "run_summary": {
    "with_skill":    { "pass_rate": { "mean": 0.83 }, "tokens": { "mean": 3800 } },
    "without_skill": { "pass_rate": { "mean": 0.33 }, "tokens": { "mean": 2100 } },
    "delta": { "pass_rate": 0.50, "tokens": 1700 }
  }
}
```

A skill that adds 13s but lifts pass rate 50 points is worth it; one that doubles tokens for +2 points isn't. Then mine the patterns:

- **Drop assertions that pass in both configs** — they don't measure skill value and inflate the score.
- **Investigate assertions that fail in both** — broken assertion, too-hard case, or wrong check.
- **Study assertions that pass *with* but fail *without*** — that's where the skill earns its keep; learn *why*.
- **High `stddev` (inconsistent across runs)** → ambiguous instructions; add examples / tighten guidance.
- **Time/token outliers** → read the execution transcript to find the bottleneck.

### Human review + the improvement loop

Assertions only check what you thought of. A human catches "technically correct but misses the point." Record actionable feedback per case (`"chart missing axis labels and months are alphabetical not chronological"`, not `"looks bad"`).

Then give all three signals — **failed assertions + human feedback + execution transcripts** — plus the current `SKILL.md` to an LLM and ask for changes, instructing it to: **generalize** (not patch specific cases), **keep it lean** (remove instructions if pass rates plateau — over-constraint is real), **explain the why**, and **bundle repeated work** into scripts. Rerun in `iteration-<N+1>/`, regrade, repeat until feedback is consistently empty.

> **Critical for weak models:** Run the entire eval suite **against the weakest model you intend to support.** A skill that passes on a frontier model can collapse on a small one — and the small one is where good skill design matters most.

---

## Part 8 — Scripts: Offload What the Architecture Is Bad At

Tokenization makes models bad at math, counting, and exact string ops ([factors doc §2](./llm-smart-vs-dumb-factors.md)). Routing those to scripts converts a probabilistic guess into a deterministic computation — the single biggest reliability win for weak models ([Using scripts](https://agentskills.io/skill-creation/using-scripts.md)).

### One-off commands vs. bundled scripts

When a package already does the job, reference it inline with a runtime that auto-resolves deps — `uvx`/`pipx` (Python), `npx`/`bunx` (JS), `deno run`, `go run`. **Pin versions** (`npx eslint@9.0.0`), **state prerequisites** in `SKILL.md` (or the `compatibility` field), and **move complex commands into `scripts/`** once they're hard to get right in one shot.

### Reference scripts with relative paths

```markdown
## Available scripts
- `scripts/validate.sh` — Validates configuration files
- `scripts/process.py` — Processes input data

## Workflow
1. Run validation:  bash scripts/validate.sh "$INPUT_FILE"
2. Process results: python3 scripts/process.py --input results.json
```

Paths are relative to the **skill directory root** (where the agent runs commands). Self-contained scripts can declare deps inline — Python [PEP 723](https://peps.python.org/pep-0723/) (`uv run`), Deno `npm:` specifiers, Bun auto-install, Ruby `bundler/inline`.

### Design scripts for agentic use — every rule here is a dumbness defense

| Rule | Why it matters for a weak model |
|---|---|
| **No interactive prompts** (hard requirement) | Agents run in non-interactive shells; a TTY prompt hangs forever. Take input via flags/env/stdin. |
| **`--help` documents the interface** | It's how the agent *learns* the script. Brief description + flags + examples. Keep it concise (enters context). |
| **Helpful error messages** | The message shapes the agent's next attempt. "Error: --format must be one of: json, csv, table. Received: xml" beats "invalid input." |
| **Structured output (JSON/CSV/TSV)** | Parseable by agent *and* tools (`jq`, `cut`). Send data to stdout, diagnostics to stderr. |
| **Idempotency** | Agents retry; "create if not exists" beats "fail on duplicate." |
| **Closed-set inputs / enums** | Reject ambiguity with a clear error instead of guessing. |
| **`--dry-run` for destructive ops** | Lets the agent preview before committing — pairs with plan-validate-execute. |
| **Meaningful, documented exit codes** | Distinct codes per failure type tell the agent what went wrong. |
| **Predictable output size** | Harnesses truncate at ~10–30K chars, silently losing info. Default to a summary; support `--offset`/`--output`. |

---

## SKILL.md Skeleton (copy-paste starting point)

```markdown
---
name: deploying-web-app
description: >
  Deploys the web app to staging or production. Use when the user asks to
  deploy, ship, release, roll out, or push the app live — even if they
  don't say "deploy" explicitly.
compatibility: Requires Node.js 18+ and the project's deploy CLI.
---

# Deploying the Web App

## CRITICAL RULES (read first)
- NEVER deploy to production without running tests first.
- If any test fails, STOP and report the failure. Do not deploy.
- If you cannot find the config file, output INSUFFICIENT CONTEXT and stop.

## Gotchas
- "prod"/"live"/"production" all mean the production target.
- The deploy CLI exits 0 on success; any non-zero code is a failure.

## Available scripts
- `scripts/run_tests.sh` — runs the full test suite, exits non-zero on failure
- `scripts/deploy.sh` — deploys to a target; supports --dry-run

## Workflow
Progress:
- [ ] 1. Run tests: `bash scripts/run_tests.sh`
       - All pass → continue. Any fail → STOP, report which test failed.
- [ ] 2. Determine target: user said prod/live/production → production; else → staging.
- [ ] 3. Dry run: `bash scripts/deploy.sh --target <target> --dry-run`, review the plan.
- [ ] 4. Deploy: `bash scripts/deploy.sh --target <target>`.
- [ ] 5. Verify exit code is 0. If not 0 → STOP, report the error output verbatim.
- [ ] 6. Report: "Deployed to <target> successfully."

## Before you finish (read again)
- Did the tests pass before you deployed?
- Did you verify the exit code?

## Reference (load only when needed)
- Rollback: read references/rollback.md ONLY if a deploy fails.
- Env vars: read references/env-vars.md ONLY if step 1 reports a missing variable.
```

It embodies the whole guide: spec-valid frontmatter with a pushy imperative description; critical rules front-loaded **and** book-ended; a gotchas section; a checklist workflow with explicit branches and stop conditions; an `INSUFFICIENT CONTEXT` escape hatch; plan-validate-execute via `--dry-run`; tool offloading; verification gates; consistent terminology; and conditional (when-to-load) progressive disclosure.

---

## Weak-Model Failure Signatures → Fix

Read execution transcripts, not just final outputs. Match the symptom to the fix:

| Symptom in transcript | Likely cause | Fix |
|---|---|---|
| Skips a rule | Rule buried mid-doc, or too many rules | Front-load/book-end (Part 5); cut rules (Part 3) |
| Tries several approaches before one works | Instructions too vague | Be more prescriptive (Part 4); add a default |
| Follows an irrelevant instruction | Instruction didn't apply to this task | Scope tighter; aim for moderate detail (Part 3) |
| Wrong arithmetic / counts | Model is doing math itself | Offload to a script (Part 8) |
| Confidently wrong / fabricated | Hallucination + sycophancy | Escape hatch + validation loop (Part 5) |
| Inconsistent output shape | Free-form prose, no template | Output template (Part 5) |
| Degrades on long inputs | Context rot / bloat | Trim + progressive disclosure (Parts 3, 6) |
| Passes sometimes, fails others (high stddev) | Ambiguous instructions | Add examples; tighten (Part 7) |
| Skill never loads | Weak description | Optimize + test triggering (Part 6) |

---

## One-Glance Shipping Checklist

**Spec & structure**
- [ ] `SKILL.md` frontmatter valid; `name` matches directory; `description` ≤ 1024 chars.
- [ ] Body under ~500 lines / 5000 tokens; references one level deep.
- [ ] `skills-ref validate ./my-skill` passes.

**Content (anti-dumbness)**
- [ ] Grounded in real expertise, not generic LLM filler.
- [ ] "Would the agent get this wrong without this line?" — every line earns its tokens.
- [ ] Procedures over declarations; defaults not menus; moderate detail.
- [ ] Hard constraints front-loaded **and** book-ended; gotchas in `SKILL.md`.
- [ ] Output templates for any fixed format.
- [ ] Validation loop / plan-validate-execute on fragile or destructive steps.
- [ ] `INSUFFICIENT CONTEXT` escape hatch + verification gates.
- [ ] One term per concept; unambiguous parameter names.
- [ ] Conditional ("load X *when* Y") progressive disclosure for references.

**Scripts**
- [ ] Math/counting/exact-formatting offloaded to scripts.
- [ ] Non-interactive; `--help`; structured stdout + stderr diagnostics; meaningful exit codes; `--dry-run` for destructive ops; pinned deps; predictable output size.

**Description & evals**
- [ ] Description tested with ~20 queries (incl. near-miss negatives), train/val split, selected by validation pass rate.
- [ ] Output evals run **with vs. without** the skill; positive delta in pass rate justifies the token cost.
- [ ] Assertions specific/observable; graded with evidence; patterns analyzed.
- [ ] Iterated via failed assertions + human feedback + transcripts.
- [ ] **Tested against the weakest target model.**

---

*Combines [llm-smart-vs-dumb-factors.md](./llm-smart-vs-dumb-factors.md) with the full [Agent Skills documentation](https://agentskills.io): [What are skills?](https://agentskills.io/what-are-skills.md), [Overview](https://agentskills.io/home.md), [Specification](https://agentskills.io/specification.md), [Best practices](https://agentskills.io/skill-creation/best-practices.md), [Optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions.md), [Evaluating skills](https://agentskills.io/skill-creation/evaluating-skills.md), and [Using scripts](https://agentskills.io/skill-creation/using-scripts.md). Cognitive findings sourced in the factors doc (Wei et al., Stanford "Lost in the Middle," Chroma & Redis "Context Rot," OpenAI, Anthropic, ManyIFEval "Curse of Instructions," and others).*
