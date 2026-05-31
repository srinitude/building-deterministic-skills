# Third-party skill adoption when the installer scan blocks a large repo

Use this when the user asks to install or adopt a community skill from a GitHub repo and the
installer blocks because the repository contains optional runtime code, tests, reports, evals,
lockfiles, or training scripts that are not needed for normal prompt-skill use.

## Pattern

1. Try the official installer first with the most specific identifier (inspect, then install the
   single skill path, not the whole repo).

2. If the installer blocks on a dangerous scan, classify the findings before acting:
   - Findings in `SKILL.md` or its referenced docs are load-bearing and must be handled as skill content risk.
   - Findings in optional app code, tests, generated reports, lockfiles, training scripts, or eval
     fixtures often mean the package is too broad for the installer, not that the prompt/reference
     payload is unusable.

3. Fetch the repo through a source-grounded path (`git clone`, or a source-fetch tool such as
   `opensrc path owner/repo`) and locate the skill root. Do not rely only on raw GitHub URLs:
   private/authenticated repositories can work through git credentials while raw/API endpoints
   return 404.

4. Install only the minimal prompt-skill payload when normal use does not require executable extras:
   - `SKILL.md`
   - `references/` files referenced by the skill
   - optionally `assets/` only if the SKILL.md says normal use requires them
   - do not copy `src/`, `tests/`, `reports/`, lockfiles, or deployment config unless the user
     explicitly wants those workflows and accepts the scan implications

5. Perform the curated install (copy the minimal payload into the local skill library), then verify:
   - the skill loads in the host's skill viewer/loader
   - the host's skill list shows the skill enabled
   - linked reference files resolve from the installed copy

6. Repository detail pages on skill directories are not direct `SKILL.md` URLs. Resolve the canonical
   skill path first, inspect it, and only override an installer's community caution after you have
   reviewed the findings, removed or adapted stale platform-specific files, and understand the
   remaining payload.

7. Do not leave dependency folders such as `node_modules/` inside a skill package just to make a
   harness runnable. They bloat scans and produce false dangerous findings. Do not use a
   `node_modules` symlink inside the skill as a workaround: security scans can still treat it as part
   of the package. Keep `package.json`/lockfiles if needed, place any runtime dependency directory
   OUTSIDE the skill, and verify scripts with syntax/help checks against that runtime before removing
   transient dependency folders.

8. Tell the user exactly what was installed and why the full repo install was avoided or forced.

## Do not persist

Do not save the transient scan output as a permanent statement that a tool or repository is unsafe.
Save the adoption pattern: official install first, inspect findings, curate the minimal payload only
when appropriate, then verify discovery.
