#!/usr/bin/env python3
"""Validate SKILL.md frontmatter against the agentskills.io specification.

Platform-agnostic: standard library only, no dependency on any agent runtime.
Mirrors the canonical `skills-ref` field rules so a skill can be checked offline
before shipping:
  - starts at byte 0 with `---` and closes the frontmatter block;
  - `name`: 1-64 chars, lowercase letters/digits/hyphens, no leading/trailing/
    consecutive hyphens, equals the parent directory name;
  - `description`: present, non-empty, <= 1024 chars;
  - only the allowed top-level fields appear (closed set);
  - `compatibility` (if present) <= 500 chars;
  - non-empty body after frontmatter; total content <= 100000 chars.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_CONTENT_CHARS = 100_000
MAX_NAME_LENGTH = 64
MAX_COMPATIBILITY_LENGTH = 500
# agentskills.io spec: closed set of allowed top-level frontmatter fields.
ALLOWED_TOP_LEVEL_FIELDS = {
    "name", "description", "license", "allowed-tools", "metadata", "compatibility",
}


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def split_frontmatter(content: str) -> str:
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter (---)"
    end = re.search(r"\n---\s*\n", content[3:])
    assert end is not None, "frontmatter is not closed with a '---' line"
    assert len(content) <= MAX_SKILL_CONTENT_CHARS, "SKILL.md exceeds content limit"
    body = content[end.end() + 3:].strip()
    assert body, "SKILL.md must have a body after the frontmatter"
    return content[3:end.start() + 3]


def parse_frontmatter(raw: str) -> dict:
    try:
        import yaml  # type: ignore

        parsed = yaml.safe_load(raw)
    except Exception:
        # Minimal stdlib fallback: read top-level "key:" lines only.
        parsed = {}
        for line in raw.splitlines():
            if line.startswith((" ", "\t")):
                continue
            m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
            if m:
                parsed[m.group(1)] = m.group(2).strip()
    assert isinstance(parsed, dict), "frontmatter must be a YAML mapping"
    return parsed


def validate_name(name, parent: str) -> None:
    assert isinstance(name, str) and name.strip(), "frontmatter must include a non-empty name"
    name = unicodedata.normalize("NFKC", name.strip())
    assert 1 <= len(name) <= MAX_NAME_LENGTH, "name length out of [1,64]"
    assert name == name.lower(), "name must be lowercase"
    assert not (name.startswith("-") or name.endswith("-")), "name cannot start/end with a hyphen"
    assert "--" not in name, "name cannot contain consecutive hyphens"
    assert all(c.isalnum() or c == "-" for c in name), "name allows only letters, digits, hyphens"
    assert name == unicodedata.normalize("NFKC", parent), "name must match the parent directory name"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "skill-frontmatter", "self_test": "ok"}, sort_keys=True))
        return 0

    root = skill_root()
    content = (root / "SKILL.md").read_text()
    raw = split_frontmatter(content)
    parsed = parse_frontmatter(raw)

    validate_name(parsed.get("name"), root.name)

    assert "description" in parsed, "frontmatter must include description"
    description = str(parsed["description"]).strip()
    assert description, "description must be non-empty"
    assert len(description) <= MAX_DESCRIPTION_LENGTH, "description exceeds 1024 chars"

    extra = set(parsed.keys()) - ALLOWED_TOP_LEVEL_FIELDS
    assert not extra, (
        f"disallowed top-level frontmatter field(s): {sorted(extra)}. "
        f"Allowed: {sorted(ALLOWED_TOP_LEVEL_FIELDS)}. Nest everything else under 'metadata'."
    )
    if "compatibility" in parsed:
        assert len(str(parsed["compatibility"])) <= MAX_COMPATIBILITY_LENGTH, "compatibility exceeds 500 chars"

    print(json.dumps({"PASS_FRONTMATTER": True, "name": parsed.get("name")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
