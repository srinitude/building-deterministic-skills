# building-deterministic-skills dumb-model update report

Generated: 2026-05-29T07:18:44Z

## sha256 ledger

- Before SKILL.md sha256: `77e48b01dacae6977fb490792d0fea1d5f0e574b1353db51de2017da50823cc0`
- After SKILL.md sha256: `7b96fd2b61882820af4f9271f197a31de34a09c5ba097491e5d5b0797a2bcd65`
- Before references aggregate sha256: `1701bbc93c0af2a8a33c7471b8f26c47ea525d0cace8e7bb8d3bee5b89ea029e`
- After references aggregate sha256: `686b5dd4c6dc5d640a0ea48f5561531f5bb23cdbd42dcaf29c4d86980bc99ed9`

## Preserved invariants

- Frontmatter validation remains wired through `_validate_frontmatter` and `_validate_content_size`.
- Discovery validation remains wired through `iter_skill_index_files`.
- Security validation remains wired through `tools.skills_guard.scan_skill` and `should_allow_install`.
- Hermes pytest gate remains wired to `tests/tools/test_skill_manager_tool.py tests/tools/test_skill_size_limits.py tests/agent/test_skill_utils.py tests/tools/test_skills_guard.py`.
- Common pitfalls count increased from 8 to 12, preserving the original >=8 invariant.
- Existing references are still present and linked: `references/third-party-skill-adoption.md` and `references/productized-agent-skill-release.md`.
- New dumb-model authoring reference is present and linked: `references/dumb-model-authoring.md`.

## Changed/created paths

- `SKILL.md`
- `references/dumb-model-authoring.md`
- `assets/dumb-model-skill-skeleton.md`
- `evals/evals.json`
- `scripts/check-skill-frontmatter.py`
- `scripts/check-preserved-invariants.py`
- `scripts/check-dumb-model-coverage.py`
- `scripts/check-dumb-model-readability.py`
- `scripts/check-source-grounding.py`
- `scripts/check-determinism.py`
- `scripts/check-no-dead-links.py`
- `scripts/check-report-grounding.py`
- `reports/source-grounding/firecrawl/agentskills-io/map.json`
- `reports/source-grounding/firecrawl/agentskills-io/scrape-ledger.json`
- `reports/source-grounding/firecrawl/agentskills-io/search.json`
- `reports/source-grounding/firecrawl/agentskills-io/scrapes`
- `reports/building-deterministic-skills-dumbening-changes.md`

## Firecrawl/source-grounding evidence

- Firecrawl map: `reports/source-grounding/firecrawl/agentskills-io/map.json` with 18 mapped URLs.
- Firecrawl scrape ledger: `reports/source-grounding/firecrawl/agentskills-io/scrape-ledger.json` with 18 scraped URLs and 0 scrape failures.
- Firecrawl search: `reports/source-grounding/firecrawl/agentskills-io/search.json` exists.
- Firecrawl crawl was attempted and timed out after 600 seconds; the timeout is recorded in the scrape ledger. No crawl success was fabricated.
- `references/dumb-model-authoring.md` cites 5 scraped Agent Skills artifacts that resolve on disk.

## Rejected tradeoffs

- Rejected deleting the original references to shorten the skill, because that would lower workflow coverage.
- Rejected removing Hermes validation primitives, because the skill must still validate against live hermes-agent behavior.
- Rejected hiding Gotchas in a reference-only doc, because weak models skip buried rules.
- Rejected offering multiple workflow choices, because defaults-not-menus is required for dumb-model readability.
- Rejected fabricating a successful Firecrawl crawl artifact after the crawl command timed out.

## Verification status

See the final response for command evidence. The local verifier scripts were added so these claims fail closed on missing files, missing factors, dead links, nondeterministic script output, and ungrounded report paths.
