#!/usr/bin/env python3
"""check-content-preserved.py

Stronger-than-coverage preservation gate. Where a trigger/heading coverage check
only confirms quoted trigger phrases and H2 headings survive an edit, THIS check
asserts that no atomic content unit — command lines, list items, inline code
tokens (paths, flags, function names) — from the ORIGINAL SKILL.md was silently
dropped when a skill is rewritten or conformed.

Use it whenever you re-author or bulk-conform an existing skill so that no
context, content, meaning, or intent is lost relative to the original. A unit
counts as preserved if its normalized text appears anywhere in the new SKILL.md
OR in any file under the skill's references/ directory (relocation is allowed).

Platform-agnostic: standard library only, no hardcoded paths.

Usage:
  check-content-preserved.py --self-test
  # single skill: compare a new skill dir against an original/backup dir
  check-content-preserved.py --skill PATH/TO/skill --backup PATH/TO/original/skill
  # batch: a targets file of SKILL.md paths + a backup root that mirrors a skills root
  check-content-preserved.py --targets FILE --skills-root DIR --backup-root DIR
  # strict mode: exit nonzero if any unit is missing (default is report-only, exit 0)
  check-content-preserved.py --skill ... --backup ... --strict

A missing unit is a CANDIDATE loss: either it was reworded (acceptable — confirm
the meaning survives) or it must be restored. In --strict mode any missing unit
fails the gate, which is the right setting for mechanical/bulk conformance where
no rewording is intended.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

MIN_INLINE_LEN = 4  # ignore trivially short inline-code tokens


def split_body(text: str) -> str:
    if not text.startswith("---"):
        return text
    m = re.search(r"\n---\s*\n", text[3:])
    return text[m.end() + 3:] if m else text


def normalize(s: str) -> str:
    # <wbr> is an invisible word-break hint used to neutralize scanner false
    # positives; it carries no meaning, so strip it before comparing.
    s = s.replace("<wbr>", "")
    return re.sub(r"\s+", " ", s).strip().lower()


def extract_units(body: str):
    """Yield (kind, text) atomic content units from a SKILL.md body."""
    units = []
    in_fence = False
    for ln in body.splitlines():
        stripped = ln.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            if stripped:
                units.append(("code", stripped))
            continue
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*\S)\s*$", ln)
        if m:
            units.append(("list", m.group(1)))
        for tok in re.findall(r"`([^`]+)`", ln):
            if len(tok) >= MIN_INLINE_LEN:
                units.append(("inline", tok))
    return units


def haystack_for(new_md: Path) -> str:
    parts = []
    if new_md.exists():
        parts.append(new_md.read_text(encoding="utf-8", errors="replace"))
    refs = new_md.parent / "references"
    if refs.is_dir():
        for f in sorted(refs.rglob("*")):
            if f.is_file():
                try:
                    parts.append(f.read_text(encoding="utf-8", errors="replace"))
                except Exception:  # noqa: BLE001
                    pass
    return normalize("\n".join(parts))


def audit_one(backup_md: Path, new_md: Path):
    """Return (units_checked, missing[list of (kind, text)])."""
    if not backup_md.exists():
        return 0, []
    hay = haystack_for(new_md)
    seen = set()
    missing = []
    original_body = split_body(backup_md.read_text(encoding="utf-8", errors="replace"))
    for kind, unit in extract_units(original_body):
        n = normalize(unit)
        if not n or n in seen:
            continue
        seen.add(n)
        if n not in hay:
            missing.append((kind, unit))
    return len(seen), missing


def report(rel: str, checked: int, missing) -> None:
    print(f"content-preserved: {rel}  units={checked}  missing={len(missing)}")
    for kind, unit in missing:
        print(f"  MISSING[{kind}] {unit}")


def run_single(skill: Path, backup: Path, strict: bool) -> int:
    new_md = skill / "SKILL.md" if skill.is_dir() else skill
    backup_md = backup / "SKILL.md" if backup.is_dir() else backup
    checked, missing = audit_one(backup_md, new_md)
    report(str(new_md), checked, missing)
    return 1 if (strict and missing) else 0


def run_batch(targets: Path, skills_root: Path, backup_root: Path, strict: bool) -> int:
    paths = [ln.strip() for ln in targets.read_text().splitlines() if ln.strip()]
    any_missing = False
    for t in paths:
        new_md = Path(t)
        try:
            rel = new_md.relative_to(skills_root)
        except ValueError:
            rel = Path(new_md.name)
        backup_md = backup_root / rel
        checked, missing = audit_one(backup_md, new_md)
        report(str(rel), checked, missing)
        if missing:
            any_missing = True
    if any_missing and strict:
        print("FAIL: at least one skill dropped original content (strict mode)", file=sys.stderr)
        return 1
    return 0


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bak = root / "bak" / "demo"
        new = root / "new" / "demo"
        (bak).mkdir(parents=True)
        (new / "references").mkdir(parents=True)
        original = (
            "---\nname: demo\n---\n\n# Demo\n\n"
            "## Steps\n\n```bash\nfoo --run alpha\n```\n\n"
            "- Use `bar-flag` for safety\n- Avoid the beta path\n"
        )
        (bak / "SKILL.md").write_text(original)
        # new keeps foo command + bar-flag, relocates the beta bullet into a ref
        (new / "SKILL.md").write_text(
            "---\nname: demo\n---\n# Demo\n```bash\nfoo --run alpha\n```\n"
            "Use `bar-flag` for safety\n"
        )
        (new / "references" / "more.md").write_text("Avoid the beta path entirely.")
        checked, missing = audit_one(bak / "SKILL.md", new / "SKILL.md")
        assert not missing, f"all content preserved/relocated, should be empty: {missing}"

        # now drop the foo command entirely
        (new / "SKILL.md").write_text("---\nname: demo\n---\n# Demo\nUse `bar-flag` for safety\n")
        (new / "references" / "more.md").write_text("Avoid the beta path entirely.")
        checked2, missing2 = audit_one(bak / "SKILL.md", new / "SKILL.md")
        assert any(u == "foo --run alpha" for _, u in missing2), missing2
    print(json.dumps({"check": "content-preserved", "self_test": "ok"}, sort_keys=True))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--skill", help="new skill dir or SKILL.md")
    ap.add_argument("--backup", help="original/backup skill dir or SKILL.md")
    ap.add_argument("--targets", help="batch: file of SKILL.md paths")
    ap.add_argument("--skills-root", help="batch: root the targets are under")
    ap.add_argument("--backup-root", help="batch: backup root mirroring skills-root")
    ap.add_argument("--strict", action="store_true",
                    help="exit nonzero if any original content unit is missing")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.skill and args.backup:
        return run_single(Path(args.skill), Path(args.backup), args.strict)
    if args.targets and args.skills_root and args.backup_root:
        return run_batch(
            Path(args.targets), Path(args.skills_root), Path(args.backup_root), args.strict
        )
    ap.error("provide --self-test, or --skill+--backup, or --targets+--skills-root+--backup-root")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
