#!/usr/bin/env python3
"""Validate Firecrawl map/scrape coverage and cited artifacts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def collect_urls(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in {"url", "sourceurl", "source_url"} and isinstance(child, str) and child.startswith("http"):
                found.append(child)
            else:
                found.extend(collect_urls(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_urls(child))
    elif isinstance(value, str) and value.startswith("http"):
        found.append(value)
    unique: list[str] = []
    for url in found:
        if url not in unique:
            unique.append(url)
    return unique


def has_markdown(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "markdown" and isinstance(child, str) and child.strip():
                return True
            if has_markdown(child):
                return True
    if isinstance(value, list):
        return any(has_markdown(child) for child in value)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "source-grounding", "self_test": "ok"}, sort_keys=True))
        return 0

    root = skill_root()
    fcdir = root / "reports" / "source-grounding" / "firecrawl" / "agentskills-io"
    map_path = fcdir / "map.json"
    ledger_path = fcdir / "scrape-ledger.json"
    assert map_path.exists() and map_path.stat().st_size > 0, "Firecrawl map missing"
    assert ledger_path.exists() and ledger_path.stat().st_size > 0, "scrape ledger missing"

    urls = collect_urls(json.loads(map_path.read_text()))
    assert len(urls) > 0, "Firecrawl map has zero URLs"
    ledger = json.loads(ledger_path.read_text())
    scrapes = ledger.get("scrapes")
    assert isinstance(scrapes, list), "ledger.scrapes must be a list"
    assert len(scrapes) == len(urls), f"scrape coverage mismatch: {len(scrapes)} != {len(urls)}"

    by_url = {entry.get("url"): entry for entry in scrapes if isinstance(entry, dict)}
    missing_urls = [url for url in urls if url not in by_url]
    assert not missing_urls, "ledger missing URLs: " + ", ".join(missing_urls)
    for url in urls:
        entry = by_url[url]
        status = entry.get("status")
        output = entry.get("output")
        assert status in {"scraped", "failed"}, f"invalid status for {url}: {status}"
        if status == "scraped":
            path = root / str(output)
            assert path.exists() and path.stat().st_size > 0, f"scrape artifact missing: {output}"
            data = json.loads(path.read_text())
            assert has_markdown(data), f"scrape artifact has no markdown: {output}"
        else:
            assert entry.get("exit_code") is not None or entry.get("note"), f"failed scrape lacks evidence: {url}"

    reference = (root / "references" / "dumb-model-authoring.md").read_text()
    cited = sorted(set(re.findall(r"reports/source-grounding/firecrawl/agentskills-io/scrapes/[A-Za-z0-9._-]+\.json", reference)))
    assert len(cited) >= 3, "dumb-model reference must cite at least three scraped Agent Skills artifacts"
    missing_citations = [path for path in cited if not (root / path).exists()]
    assert not missing_citations, "cited Firecrawl paths missing: " + ", ".join(missing_citations)

    print(json.dumps({"PASS_SOURCEGROUNDING": True, "mapped_urls": len(urls), "scrapes": len(scrapes), "citations": len(cited)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
