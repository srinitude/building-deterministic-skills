#!/usr/bin/env python3
"""Validate dumbness-factor coverage against the research bundled IN this skill.

building-deterministic-skills is grounded in two research docs that are bundled
into references/ so the skill is fully self-contained (no dependency on any
local filesystem path):

  - references/llm-smart-vs-dumb-factors.md       (the cognitive theory)
  - references/writing-agent-skills-for-dumb-models.md (the authoring guide)

For every dumbness factor this checker asserts (a) the factor is present in the
bundled research and (b) the matching countermeasure terms are present in the
authored skill material (SKILL.md + dumb-model-authoring.md + the skeleton).
Every check is a structural assertion -- never model judgement.

--factors / --guide override the source docs (default: the bundled copies).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


# Factor -> {source_aliases: how the bundled research names it,
#            required_terms: countermeasure phrasing required in authored material}
FACTOR_RULES = {
    "emergent-threshold": {
        "source_aliases": ["Emergent-ability threshold", "Emergent ability", "emergent abilities"],
        "required_terms": ["procedures-over-declarations", "numbered steps"],
    },
    "tokenization": {
        "source_aliases": ["Tokenization"],
        "required_terms": ["Offload math/counting to scripts", "exact string"],
    },
    "quantization/distillation": {
        "source_aliases": ["Quantization / distillation", "Quantization", "Distillation"],
        "required_terms": ["Gotchas section"],
    },
    "sycophancy": {
        "source_aliases": ["Sycophancy"],
        "required_terms": ["validation loops", "plan-validate-execute"],
    },
    "hallucination": {
        "source_aliases": ["Hallucination", "hallucinate"],
        "required_terms": ["INSUFFICIENT CONTEXT"],
    },
    "low-test-time-reasoning": {
        "source_aliases": ["No / low test-time reasoning", "test-time reasoning", "test-time compute"],
        "required_terms": ["checklists", "validate-fix-rerun"],
    },
    "lost-in-the-middle": {
        "source_aliases": ["Lost in the middle"],
        "required_terms": ["front-loaded-AND-book-ended critical rules", "Gotchas in `SKILL.md`"],
    },
    "context-rot": {
        "source_aliases": ["Context rot"],
        "required_terms": ["under 500 lines", "conditional progressive disclosure"],
    },
    "prompt-bloat": {
        "source_aliases": ["Prompt bloat"],
        "required_terms": ["Add only what the agent lacks", "omit generic filler"],
    },
    "curse-of-instructions": {
        "source_aliases": ["Curse of instructions"],
        "required_terms": ["defaults-not-menus", "moderate detail"],
    },
    "instruction-sensitivity": {
        "source_aliases": ["Instruction sensitivity"],
        "required_terms": ["one-term-per-concept"],
    },
    "sampling-variability": {
        "source_aliases": ["Sampling variability"],
        "required_terms": ["output templates"],
    },
    "weak-triggering": {
        "source_aliases": ["Weak skill triggering", "Optimizing descriptions", "Optimizing skill descriptions"],
        "required_terms": ["description", "trigger phrases"],
    },
}


def contains_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def main() -> int:
    root = skill_root()
    default_factors = root / "references" / "llm-smart-vs-dumb-factors.md"
    default_guide = root / "references" / "writing-agent-skills-for-dumb-models.md"

    parser = argparse.ArgumentParser()
    parser.add_argument("--factors", type=Path, default=default_factors,
                        help="cognitive-factors doc (default: bundled references/ copy)")
    parser.add_argument("--guide", type=Path, default=default_guide,
                        help="authoring-guide doc (default: bundled references/ copy)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "dumb-model-coverage", "factors": len(FACTOR_RULES), "self_test": "ok"}, sort_keys=True))
        return 0

    assert args.factors.exists(), f"factors doc missing: {args.factors} (expected bundled in references/)"
    assert args.guide.exists(), f"guide doc missing: {args.guide} (expected bundled in references/)"

    factors_text = args.factors.read_text()
    guide_text = args.guide.read_text()
    authored = "\n".join(
        [
            (root / "SKILL.md").read_text(),
            (root / "references" / "dumb-model-authoring.md").read_text(),
            (root / "assets" / "dumb-model-skill-skeleton.md").read_text(),
        ]
    )
    source_text = factors_text + "\n" + guide_text

    failures = []
    for factor, rule in FACTOR_RULES.items():
        if not contains_any(source_text, rule["source_aliases"]):
            failures.append(f"source missing {factor} (aliases: {rule['source_aliases']})")
        missing_terms = [term for term in rule["required_terms"] if term.lower() not in authored.lower()]
        if missing_terms:
            failures.append(f"{factor} missing countermeasure terms: {', '.join(missing_terms)}")
    assert not failures, "\n".join(failures)
    print(json.dumps({"PASS_COVERAGE": True, "factors_checked": sorted(FACTOR_RULES)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
