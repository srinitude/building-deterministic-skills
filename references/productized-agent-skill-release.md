# Productized deterministic agent-skill release pattern

Use this reference when the user asks for a deterministic agentskills.io-compliant skill as a standalone package/repository, not just a local `~/.hermes/skills/<name>` entry.

## TDD chronology that satisfies strict reviews

1. **BOOTSTRAP before tests**: create the repo, package manager config, typecheck/test scripts, and CI workflow first. Commit this as the bootstrap commit before writing RED tests.
2. **RED before implementation**: write contract/API/interface tests only. Capture a failing test log under `reports/` before adding implementation.
3. **GREEN**: implement the smallest production code that makes the user-facing contracts pass.
4. **REFACTOR/EVIDENCE**: write a `reports/tdd-ledger.md` with commit SHAs for BOOTSTRAP/RED/GREEN/REFACTOR and a `reports/build-report.md` with final command evidence.
5. **README contract**: include a comprehensive `README.md` for humans and agents, with quick start, agent invocation contract, runtime architecture, deployment-target memory segmentation, verification loop, research refresh, gates/CI, and troubleshooting. Add a contract test that fails before the README exists or omits required sections.
6. **Release**: push to the requested private/public repo, tag the final verified commit, wait for remote CI, then verify local status, tag target, and repo visibility.

## Useful gates for deterministic skill packages

Add package scripts and tests for these gates early so failures are actionable:

- `check:loc`: max lines per file and max lines per construct.
- `check:nesting`: AST-based nesting depth; for tests, measure nesting relative to the test declaration.
- `check:portable`: no hardcoded user paths or machine-specific source paths in committed source.
- `check:agentskills`: frontmatter, required directories, one-level references, and package layout. Enforce agentskills.io `name`, `description`, `license`, `compatibility`, and flat string-valued `metadata` fields.
- `check:skills-ref`: run the official `skills-ref validate .` reference validator from a pinned devDependency so CI catches upstream-format drift.
- `check:no-deprecated`: compare used primitives against a generated/source-grounded deprecation inventory.
- `check:words`: scan source and tests for development residue. If a requirement names a legacy script such as `check:placeholders`, keep the package script name for compatibility while the implementation can emit a neutral gate name.

## Real-service tests without leaking credentials

For external APIs, prefer a two-branch contract test:

- If the required environment variable is absent, assert the client fails closed and does not silently use a fake service.
- If the environment variable is present, call the real service and assert a stable contract field rather than broad implementation details.

Never print the secret value. Report only presence/absence and stable response fields.

## Grounding external platforms

When a skill depends on upstream projects, capture source-grounding artifacts in `reports/research/`:

- exact upstream repo commit or source-cache reference;
- API/docs notes in `references/`;
- generated inventories for primitives and deprecated APIs;
- map/search artifacts for deployment-target or platform research.

Use the inventories in gates instead of relying on memory about upstream APIs.

## Final release verification checklist

- `bun install && bun run ci` exits 0 locally.
- Individual gates pass independently.
- The live-service branch has been exercised when credentials are available.
- The build report and TDD ledger name the final evidence and commit SHAs.
- `git status --short --branch` is clean and tracking the remote branch.
- The remote tag peels to the intended final commit.
- Remote CI for the final commit completed successfully.
- Repo visibility matches the user's request.
