# Model × skill matrix evaluations

Use this reference when a user asks to generate skills across many models, run a model/use-case benchmark, compare skill determinism across providers, or invoke generated skills repeatedly to measure determinism.

## Core lesson

Do not launch the exhaustive nested loop first. Enumerate the matrix, compute call count and time/cost exposure, then run a small pilot that proves the harness and determinism metric.

A typical request shape can explode quickly:

```text
models × use_cases × (1 generation + N invocation runs)
```

In the May 2026 pilot, `/model` enumeration produced 584 models and research produced 21 use cases:

```text
584 × 21 = 12,264 combinations
with 2 invocation runs: 36,792 model calls
```

The measured pilot took 432.25 seconds for one combination, implying roughly 61 serial days. Treat this as a budget/scope gate, not a task to silently start.

## Default workflow

1. Enumerate models using the same source path your agent runtime's model picker uses, rather than OCR-only extraction of a UI list. Most runtimes expose a model-inventory builder (a function that returns per-provider model rows for the authenticated providers); call it directly from the runtime's own Python environment. Pass a large `max_models` (pickers often default to ~50) to get the full count. This source path is authoritative and OCR-independent — it still works when a vision tool is unavailable (e.g. balance/429). Pickers also surface non-chat rows (e.g. `text-embedding-3-large`); filter those out for chat-completion benchmarks. Sketch:

   ```python
   # call your runtime's model-inventory builder from its own venv/site-packages.
   # Function/argument names below are illustrative — use your runtime's real API.
   payload = build_models_payload(load_picker_context(),
       include_unconfigured=True, picker_hints=True, canonical_order=True, max_models=10_000)
   # payload["providers"][*]["models"] -> the per-provider model rows
   ```
2. Save the enumeration as JSON and CSV with provider, model id, model count, current provider, and source.
3. Build a use-case list with source-backed evidence and a synthetic invocation for each use case.
4. Compute matrix size before any generation:
   - combinations = model_count × use_case_count
   - generation_calls = combinations
   - invocation_calls = combinations × invocation_runs
   - total_calls = generation_calls + invocation_calls
5. If total_calls is high, run a pilot first and report the estimate before the full matrix.
6. Pilot at least one model/use-case pair end-to-end:
   - generate SKILL.md
   - validate the generated skill mechanically
   - invoke the generated skill twice with the same synthetic input
   - compare exact hashes and a canonicalized semantic/template score
7. Only run the full matrix after explicit user confirmation on scope/budget.

## Harness gotchas

- Quiet agent-CLI output may still include ANSI color, worktree creation/cleanup lines, warnings, and a `session_id:` line. Strip ANSI and wrapper lines before validating generated `SKILL.md` byte-0 frontmatter.
- Worktree-isolated invocations (a `--worktree`-style flag) need a git repository as `cwd`; running from `/tmp` can fail before the model is called. Use a harmless repo cwd for harness calls.
- `--max-turns 1` is usually too low when preloading skills because the child agent may spend its only turn loading/inspecting skill references. Use enough turns for the model to actually produce the artifact, or prompt with already-inlined constraints if tool use is disabled.
- Exact byte determinism is stricter than useful task determinism. Record both: raw byte hash equality and canonicalized output/schema equality.
- Free-form prose headings are not deterministic. For invocation benchmarks, require JSON-only output with fixed keys and sorted-key canonicalization before hashing.
- A generated skill can be structurally good yet miss a benchmark-specific output template. Keep validation rules explicit and separate from agentskills.io validity.
- **Determinism is governed by OUTPUT FIELD TYPE, not model strength.** Measured finding (4-model × 3-case pilot, May 2026): generated skills were structurally near-perfect (11/11 dumb-model-contract checks) and produced valid JSON on 100% of invocations, yet value-level canonical determinism was only ~20%. Breakdown: enumerated fields (e.g. `priority` ∈ {low,medium,high}) are deterministic; extractive fields (regex, SQL, copied action-items) are mostly deterministic; free-text/summary/creative fields are NOT deterministic. Example: identical input twice → `priority` and `action_items` byte-identical, but a free-text `task` field reworded ("...with deadline" vs "...with conference preparation") → different canonical hash. So when you WANT determinism, design the skill's output template with enumerated/extractive fields and avoid free-text summary fields. By category, `code` benchmarked ~67% value-deterministic while `everyday`/`creative` were ~0%.
- **Model strength hits GENERATION reliability more than invocation determinism.** The weakest pilot model (a `flash-lite` tier) failed to emit a parseable `{"skill_md": ...}` on 2/3 cases, while stronger models generated 3/3. So `generation_ok` is itself a model-strength signal; record it separately from determinism.
- Invocation path that works headlessly: a oneshot CLI call (`<agent> -z PROMPT -m MODEL --provider PROVIDER -t ""`-style) that prints ONLY the final response to stdout (no banner/spinner/session line). Disabling tools (`-t ""`) makes the model answer directly. Oneshot typically has no `--max-turns` flag; it runs to completion. Measured ~18s for a fast model's single JSON call, ~41s/combo (3 calls) including a reasoning model. Use `subprocess.run(..., timeout=...)` per call and stream results to JSONL with `flush()` so a long run is resumable/inspectable mid-flight.

## Running the gated full matrix (after explicit budget/scope confirmation)

Once the user approves the exhaustive run, do NOT just loop serially — a 584×111×3 matrix (~64.8k combos / ~194k calls) is ~31 serial days at the measured ~41s/combo. Run it parallel, resumable, and watched. Pattern that worked (May 2026):

1. **Parallel workers via `ThreadPoolExecutor`.** Each combo is subprocess-I/O-bound (a oneshot CLI call), so threads release the GIL during `subprocess.run`. Each oneshot child peaks ~195 MB RSS — size workers by RAM (20 workers ≈ 4 GB; safe on a 128 GB / 16-core box). The real ceiling is per-provider rate limits, not CPU/RAM.
2. **Provider-spread ordering.** Round-robin the combo queue across providers so concurrent in-flight calls hit DIFFERENT providers. Naive `for model: for case:` ordering slams one provider with all 20 workers and triggers 429s.
3. **fsync checkpoint/resume ledger.** Append each completed combo key (`provider:model_id::case_id`) to a ledger file AND the result to a results JSONL, both under a single `threading.Lock`, with `f.flush(); os.fsync(f.fileno())`. On startup, load the ledger into a set and skip done combos. A kill at any point loses only the in-flight combos; re-running the exact command resumes. ALWAYS smoke-test resume on a 4-combo subset before the real launch: run once, confirm ledger has 4 lines, run again, confirm it reports "already done: 4, remaining: 0".
4. **Launch durably + notify.** Start the sweep as a background process (`nohup ... >log 2>&1; echo EXIT=$status >>log`) with completion notification, not in the foreground.
5. **Silent-when-healthy watchdog.** Register a scheduled job (every ~30m) that runs a small monitor script. The script prints NOTHING when the sweep is progressing (empty stdout ⇒ no alert sent), and prints an ALERT only when: process dead + ledger incomplete, ledger count unchanged since last check (stall), or 100% complete. Keep last-count+timestamp in a sidecar JSON. A copy-paste resume command belongs INSIDE the alert text so recovery is one step. (If your scheduler requires a bare script filename rather than an absolute path, honor that.)

A reusable harness + watchdog live in `scripts/parallel-sweep-harness.py` and `scripts/sweep-watchdog.py` — adapt paths/totals, don't rewrite from scratch.

## Per-model attribution traps (the biggest correctness risk in a model benchmark)

A model benchmark is only valid if each result is attributable to the NAMED model. Three traps silently corrupt per-model data — fix them BEFORE the gated full run, not after. All were caught mid-flight in May 2026 by sampling early records and seeing impossible "successes."

1. **Silent fallback-rescue (the worst confound).** Many agent runtimes wrap a oneshot call in a fallback chain: when the requested model errors, the runtime silently retries on a DIFFERENT model and returns that output as if it were the requested model's. Net effect: dead/unauthorized/non-chat models (embeddings) and broken-OAuth providers all report `ok`, and you record the fallback model's behavior under the wrong model id. Detection: under the real config, an embedding model or a known-unauthorized model returns a clean chat answer — impossible if attribution were honest. Confirm by toggling: it answers WITH fallback, fails WITHOUT.
   - **Fix — no-fallback overlay home.** Build a sibling runtime-home dir that symlinks every entry of the real home EXCEPT the config file, which is a real copy with the fallback chain key(s) emptied (empty list for list-shaped keys, null for scalar keys — your runtime names these differently). Point harness subprocesses at it via whatever home-override env var your runtime honors. This disables fallback for the harness only, never mutating the user's real config. Make the writable runtime dirs (sessions/logs/checkpoints/tmp) REAL dirs in the overlay so session writes don't write through symlinks. Idempotent rebuild script. After building, VERIFY: a known-good model still answers, AND a model that should fail now fails honestly instead of being rescued.
   - Caveat: the overlay strips fallback but NOT credentials — OAuth providers that only "worked" via fallback will now honestly fail. That failure is correct data, not a regression.
   - A reusable, idempotent builder lives in `scripts/build-nofallback-overlay-home.py` (adapt the REAL/OVERLAY/HOME_ENV/CONFIG_NAME/FALLBACK_KEYS constants — or their matching env vars — to your runtime); don't rewrite it from scratch.

2. **Provider-slug duplication / unroutability.** A model picker may list the same model set under two provider slugs where only one is routable by the oneshot path (May 2026: `openai` ≡ `openai-api`, 124 identical models, but `--provider openai` → "Unknown provider"; `fireworks` appears in the picker but its slug is unknown to the oneshot resolver). Picker-listed ≠ oneshot-routable. Before the full run, probe each provider with one trivial oneshot call; dedup identical-set slugs (keep the routable one) and drop slugs that return "Unknown provider" for EVERY model (they can never succeed and only add identical-failure noise). Do NOT drop a provider on a single bad model — probe a few, because per-model availability varies (next point).

3. **Per-model invokability varies WITHIN a provider — treat it as data, not an exclusion filter.** Under one authenticated provider, some model ids answer and others return "no final response" / empty (deprecated ids, ids the key lacks access to, non-chat models). A non-responding model is itself a valid determinism outcome (non-deterministic-by-failure); record it, don't silently exclude it. Keep ALL models (including embeddings/image/audio if the user said "every model") and let each model's real outcome — works / no-response / unroutable — be the recorded result. Only wholesale-drop a provider when EVERY model under it is unroutable (trap 2).

   - **Over-correction pitfall (caught May 2026).** A "probe one (or three) models per provider, drop the provider if they fail" classifier is too aggressive and silently deletes good data. It dropped `openai-api` (124 models) because its first inventory rows were a deprecated embedding/old-chat id (`text-embedding-ada-002`, `gpt-3.5-turbo`, `gpt-4-0613`) that returned empty — even though `gpt-5.4-mini` under the same provider answered fine. It also dropped OAuth providers whose probe model only ever "worked" via fallback. Two rules that prevent the over-correction: (a) NEVER drop a provider because individual models fail to respond — only drop on the slug-level "Unknown provider" routing error (trap 2), which means NO model can ever route; (b) distinguish "no final response / empty" (a per-MODEL outcome → keep, record as failure) from "Unknown provider" (a per-PROVIDER routing failure → the only wholesale-drop reason). When in doubt, keep the model and let the sweep record its honest outcome; an extra 0%-determinism row is cheap, a wrongly-excluded working model is lost signal.

## JSON-extraction robustness (harness parser)

Models often wrap a `{"skill_md": "..."}` (or invocation) JSON in prose preamble and a ```` ```json ```` fence, AND the string VALUE contains nested ```` ``` ```` fences and `{}`. A naive brace-counter miscounts braces inside string literals and fails to parse a perfectly valid response. Use `json.JSONDecoder().raw_decode(text[idx:])` scanned from each `{` (it respects string literals), after stripping one outer fence. Add a fallback that accepts raw markdown when the cleaned output starts with `---` and contains `name:` (some models ignore the JSON-wrapper instruction and emit the SKILL.md directly). A bare-prose "the skill already exists" non-answer is real generation non-determinism — count it as a generation failure, but first harden the gen prompt ("you are authoring NEW text from scratch, you have no filesystem and no existing skills to look up") to reduce it.

## Recommended determinism metrics

For each generated skill and invocation output, record:

```json
{
  "model": "provider:model-id",
  "case_id": "use-case-id",
  "generation_ok": true,
  "skill_checks": {
    "frontmatter_at_byte_0": true,
    "name_matches": true,
    "critical_rules": true,
    "gotchas": true,
    "workflow": true,
    "output_template": true,
    "insufficient_context": true,
    "scripted_checks": true
  },
  "invocation_runs": [
    {"raw_sha256": "...", "canonical_sha256": "...", "schema_pass": true}
  ],
  "raw_exact_match": false,
  "canonical_exact_match": true
}
```

Use raw exact match to detect formatting variance. Use canonical exact match to judge whether the skill can drive repeatable task behavior.

## Report shape

The final report should include:

- Source path used for model enumeration.
- Model count, use-case count, combinations, total calls, and measured pilot timing.
- Research sources used to create use cases.
- The use-case list with sources and synthetic invocations.
- Pilot artifacts and validation results.
- Explicit statement whether the exhaustive run was completed or gated on budget/scope.

**Stratify, don't flat-average.** A single overall `generation_ok_pct` or determinism number is misleading because it mixes three populations with very different expected behavior: (a) text/chat models (the meaningful denominator), (b) non-text models (embeddings/audio/image — expected ~0% generation), and (c) providers that are unroutable or only "succeeded" via fallback (also ~0%). Report text-model determinism as the HEADLINE metric, and break out non-text and per-provider generation-success separately. Also report determinism three ways — valid-JSON-both-runs (≈100% expected), raw-byte match, and canonical-value match (the headline) — and break it down by use-case category and per model (rank models, requiring ≥3 eligible combos to avoid small-sample noise). The reusable stratified report builder lives in `scripts/build-stratified-report.py` (adapt to your JSONL schema); it tolerates a partial trailing line so it can run mid-sweep on a snapshot.
