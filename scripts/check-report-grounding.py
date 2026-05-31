#!/usr/bin/env python3
"""Verify the change report's changed/created paths exist."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def changed_section(text: str) -> str:
    match = re.search(r"^## Changed/created paths\s*$", text, re.M)
    if not match:
        raise AssertionError("report missing Changed/created paths section")
    next_match = re.search(r"^## ", text[match.end() :], re.M)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.end() : end]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "report-grounding", "self_test": "ok"}, sort_keys=True))
        return 0

    root = skill_root()
    report = root / "reports" / "building-deterministic-skills-dumbening-changes.md"
    assert report.exists() and report.stat().st_size > 0, "change report missing"
    section = changed_section(report.read_text())
    paths = re.findall(r"^- `([^`]+)`", section, re.M)
    assert paths, "no changed/created paths listed"
    missing = [path for path in paths if not (root / path).exists()]
    assert not missing, "report claims missing paths: " + ", ".join(missing)
    print(json.dumps({"PASS_REPORTGROUNDING": True, "paths_checked": paths}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
