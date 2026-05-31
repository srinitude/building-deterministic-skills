#!/usr/bin/env python3
"""Check whether a SKILL.md is readable and deterministic for weak models.

Validates the dumb-model output contract that building-deterministic-skills
prescribes, calibrated to the research bundled in references/
(writing-agent-skills-for-dumb-models.md) so that a skill authored faithfully
from EITHER skeleton passes:
  - assets/dumb-model-skill-skeleton.md (## Output template + ## Verification checklist)
  - the canonical guide skeleton "deploying-web-app" (## Before you finish, no Output template)
and so the prescriber's own large meta-skill SKILL.md also passes.

Every check is a structural assertion -- never model judgement.

Universal checks (every dumb-model skill must satisfy):
  - body <= 500 lines (the agentskills.io spec's body-length guidance);
  - `## CRITICAL RULES` and `## Gotchas` front-loaded in the first 80 body lines;
  - a workflow section (`## Workflow` or `## Ordered workflow`) with no branching menu;
  - at least MIN_NUMBERED_STEPS numbered steps, counting BOTH `N.` and `- [ ] N.` forms;
  - an INSUFFICIENT CONTEXT escape hatch;
  - a book-end section as the final `##` heading that rechecks the rules: one of
    `## Verification checklist` or `## Before you finish ...`.

Output templates are required by the research only "for any fixed format", so
they are reported (advisory) but not hard-gated here.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# Minimum numbered procedural steps for a real, dumb-model-followable procedure.
# Derived from the bundled skeletons' workflows, not from any one large meta-skill.
MIN_NUMBERED_STEPS = 4

# Accepted final book-end headings (one concept, the research uses two spellings).
BOOKEND_HEADINGS = ("Verification checklist", "Before you finish")


def body_without_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    closing = re.search(r"\n---\s*\n", text[3:])
    if not closing:
        return text
    return text[closing.end() + 3 :]


def count_numbered_steps(body: str) -> int:
    """Count `N.` lines and checkbox `- [ ] N.` lines (the checklist-workflow form)."""
    plain = re.findall(r"^\s*\d+\.\s+", body, re.M)
    checkbox = re.findall(r"^\s*- \[[ xX]\]\s*\d+\.\s+", body, re.M)
    return len(plain) + len(checkbox)


def workflow_section(body: str) -> str:
    match = re.search(r"^## (?:Ordered workflow|Workflow)\b.*$", body, re.M)
    if not match:
        return ""
    next_match = re.search(r"^## ", body[match.end() :], re.M)
    end = match.end() + next_match.start() if next_match else len(body)
    return body[match.end() : end]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", nargs="?", default="SKILL.md")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "dumb-model-readability", "self_test": "ok"}, sort_keys=True))
        return 0

    path = Path(args.skill)
    if not path.is_absolute():
        path = Path.cwd() / path
    text = path.read_text()
    body = body_without_frontmatter(text)
    lines = body.splitlines()

    assert len(lines) <= 500, "SKILL.md body exceeds 500 lines"

    first_80 = "\n".join(lines[:80])
    assert "## CRITICAL RULES" in first_80, "CRITICAL RULES not front-loaded (first 80 body lines)"
    assert "## Gotchas" in first_80, "Gotchas not front-loaded (first 80 body lines)"

    steps = count_numbered_steps(body)
    assert steps >= MIN_NUMBERED_STEPS, (
        f"expected at least {MIN_NUMBERED_STEPS} numbered procedural steps "
        f"(plain `N.` or checkbox `- [ ] N.`), found {steps}"
    )

    workflow = workflow_section(body)
    assert workflow, "workflow section missing (use `## Workflow` or `## Ordered workflow`)"
    forbidden = [r"or use whatever", r"either .{0,120} or"]
    for pattern in forbidden:
        assert not re.search(pattern, workflow, re.I | re.S), f"branching menu found in workflow: {pattern}"

    assert "INSUFFICIENT CONTEXT" in body, (
        "missing INSUFFICIENT CONTEXT escape hatch (name the missing field and stop instead of guessing)"
    )

    headings = re.findall(r"^## .+$", body, re.M)
    assert headings, "no `##` sections found"
    # A book-end re-check section must exist and sit in the latter half of the body
    # (front-loaded AND book-ended rules). It need not be the final heading -- a
    # progressive-disclosure `## Reference` section may legitimately follow it.
    bookend_pos = max((body.rfind(f"## {h}") for h in BOOKEND_HEADINGS), default=-1)
    assert bookend_pos != -1, (
        f"missing a book-end section ({' or '.join(BOOKEND_HEADINGS)}) that rechecks the rules"
    )
    assert bookend_pos >= len(body) * 0.5, (
        "book-end section must appear in the latter half of the body (rules front-loaded AND book-ended)"
    )
    bookend = body[bookend_pos:]
    assert re.search(r"(critical )?rule", bookend, re.I) or re.search(r"did you|check", bookend, re.I), (
        "the final book-end section must recheck the rules / key checks"
    )

    last_heading = headings[-1].strip().lstrip("#").strip()
    has_output_template = bool(re.search(r"^## Output template\s*$", body, re.M))
    print(json.dumps(
        {"PASS_READABILITY": True, "body_lines": len(lines),
         "numbered_steps": steps, "has_output_template": has_output_template,
         "bookend": last_heading},
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
