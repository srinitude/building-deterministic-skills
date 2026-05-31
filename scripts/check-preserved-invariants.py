#!/usr/bin/env python3
"""Check preserved coverage and the dumb-model output contract strings.

Platform-agnostic: depends only on the Python standard library and the skill's
own files. It guards against edits that silently weaken the skill by asserting
the dumb-model contract terms, the agentskills.io validation anchors, the wired
reference files, and a minimum number of numbered pitfalls all survive.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.M)
    match = pattern.search(text)
    if not match:
        return ""
    next_match = re.search(r"^## ", text[match.end():], re.M)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.end():end]


def pitfall_count(text: str) -> int:
    return len(re.findall(r"^\d+\.\s+", section(text, "Common pitfalls"), re.M))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "preserved-invariants", "self_test": "ok"}, sort_keys=True))
        return 0

    root = skill_root()
    text = (root / "SKILL.md").read_text()
    backup = root.parent / (root.name + ".bak") / "SKILL.md"
    original = backup.read_text() if backup.exists() else ""

    # agentskills.io validation anchors that must stay wired into the methodology.
    required_anchors = [
        "skills-ref",
        "agentskills.io",
        "check-skill-frontmatter.py",
        "check-dumb-model-readability.py",
        "check-dumb-model-coverage.py",
        "check-determinism.py",
        "check-no-dead-links.py",
        "check-source-grounding.py",
        "check-report-grounding.py",
        "check-preserved-invariants.py",
    ]
    missing = [item for item in required_anchors if item not in text]
    assert not missing, "missing validation anchors: " + ", ".join(missing)

    original_pitfalls = pitfall_count(original) if original else 8
    current_pitfalls = pitfall_count(text)
    assert current_pitfalls >= original_pitfalls, f"pitfall count dropped: {current_pitfalls} < {original_pitfalls}"
    assert current_pitfalls >= 8, "expected at least 8 numbered common pitfalls"

    required_refs = [
        "references/productized-agent-skill-release.md",
        "references/third-party-skill-adoption.md",
        "references/dumb-model-authoring.md",
    ]
    for ref in required_refs:
        assert ref in text, f"SKILL.md does not reference {ref}"
        assert (root / ref).exists(), f"referenced file is missing: {ref}"

    required_contract_terms = [
        "front-loaded-AND-book-ended critical rules",
        "Gotchas section",
        "defaults-not-menus",
        "INSUFFICIENT CONTEXT",
        "output templates",
        "offloading math/counting to scripts",
        "conditional progressive disclosure",
        "procedures-over-declarations",
        "one-term-per-concept",
    ]
    missing_terms = [term for term in required_contract_terms if term not in text]
    assert not missing_terms, "missing dumb-model contract terms: " + ", ".join(missing_terms)

    print(json.dumps({"PASS_PRESERVED": True, "pitfalls": current_pitfalls}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
