# Third-party skill adoption when the installer scan blocks a large repo

Use this when the user asks to install or adopt a community skill from a GitHub repo and `hermes skills install ...` blocks because the repository contains optional runtime code, tests, reports, evals, lockfiles, or training scripts that are not needed for normal prompt-skill use.

## Pattern

1. Try the official installer first with the most specific identifier:
   `hermes skills inspect owner/repo/path/to/skill`
   `hermes skills install owner/repo/path/to/skill --yes`

2. If the installer blocks on a dangerous scan, classify the findings before acting:
   - Findings in `SKILL.md` or platform references are load-bearing and must be handled as skill content risk.
   - Findings in optional app code, tests, generated reports, lockfiles, training scripts, or eval fixtures often mean the package is too broad for the installer, not that the prompt/reference payload is unusable.

3. Fetch the repo through a source-grounded path (`git clone` or `opensrc path owner/repo`) and locate the skill root. Do not rely only on raw GitHub URLs: private/authenticated repositories can work through git credentials while raw/API endpoints return 404.

4. Install only the minimal prompt-skill payload when normal use does not require executable extras:
   - `SKILL.md`
   - `references/` files referenced by the skill
   - optionally `templates/` or `assets/` only if the SKILL.md says normal use requires them
   - do not copy `src/`, `tests/`, `reports/`, `evals/`, `scripts/`, lockfiles, or deployment config unless the user explicitly wants those workflows and accepts the scan implications

5. Use `skill_manage`/file writes for the curated local install, then verify:
   - `skill_view(<name>)` loads the skill
   - `hermes skills list --source local` shows the skill enabled for curated local installs; for hub installs, use `hermes skills list --source hub` or `--source all`
   - linked reference files appear in `skill_view` output

6. Skills.sh detail URLs (`https://www.skills.sh/owner/repo/skill`) are not direct `SKILL.md` URLs. Prefer the canonical Hermes identifier `skills-sh/owner/repo/skill`, then run `hermes skills inspect ...` before install. If the installer blocks with a community caution and the user explicitly asked to install that skill, review the findings, remove or adapt stale platform-specific files, and only use `--force --yes` when the remaining payload is understood.

7. Do not leave dependency folders such as `node_modules/` inside a native Hermes skill package just to make a harness runnable. They bloat scans and produce false dangerous findings. Do not use a `node_modules` symlink inside the skill as a workaround: Hermes security scans can still treat it as part of the package. Keep `package.json`/lockfiles if needed, document or implement a runtime dependency directory outside the skill (for example under `~/.hermes/runtime/<skill>/`), and verify scripts with syntax/help checks against that runtime before removing transient dependency folders.

8. Tell the user exactly what was installed and why the full repo install was avoided or forced.

## Do not persist

Do not save the transient scan output as a permanent statement that a tool or repository is unsafe. Save the adoption pattern: official install first, inspect findings, curate the minimal payload only when appropriate, then verify discovery.