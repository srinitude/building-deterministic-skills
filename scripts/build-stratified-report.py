#!/usr/bin/env python3
"""Build a STRATIFIED determinism report from a model x use-case sweep JSONL.

Why stratified (not a flat average): a single overall determinism/gen-ok number
mixes three populations with very different expected behavior:
  (a) text/chat models      -> the meaningful denominator
  (b) non-text models       -> embeddings/audio/image; expected ~0% generation
  (c) unroutable/fallback-only providers -> also ~0%
Flat-averaging buries the real text-model signal. This script reports text-model
determinism as the HEADLINE, breaks out non-text + per-provider generation, and
reports determinism three ways (valid-JSON / raw-byte / canonical-value).

Tolerates a partial trailing JSONL line, so it is safe to run mid-sweep on a
snapshot of the live results file.

Each result record is expected to carry at least:
  model (str "provider:model_id"), provider, model_id, case_id, category,
  generation_ok (bool), skill_checks_passed/skill_checks_total (int),
  invocation_runs (list), raw_exact_match (bool|None),
  canonical_exact_match (bool|None), all_schema_pass (bool|None).
A sibling models list (JSON array of {provider, model_id, modality}) supplies
modality; absent that, everything is treated as chat.

Usage:
  build-stratified-report.py <results.jsonl> [models.json]

Adapt the record/field names to your harness's schema if they differ.
"""
import json
import os
import sys
from collections import defaultdict


def load_jsonl(path):
    recs = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except Exception:
            pass  # tolerate a partial trailing line (mid-write snapshot)
    return recs


def pct(a, b):
    return round(100.0 * a / b, 1) if b else 0.0


def det_stats(recs):
    elig = [r for r in recs if r.get("generation_ok") and r.get("invocation_runs")]
    canon = sum(1 for r in elig if r.get("canonical_exact_match"))
    raw = sum(1 for r in elig if r.get("raw_exact_match"))
    schema = sum(1 for r in elig if r.get("all_schema_pass"))
    return {
        "eligible": len(elig),
        "canonical_det": canon, "canonical_det_pct": pct(canon, len(elig)),
        "raw_det": raw, "raw_det_pct": pct(raw, len(elig)),
        "schema_valid": schema, "schema_valid_pct": pct(schema, len(elig)),
    }


def main():
    if "--self-test" in sys.argv[1:]:
        print(json.dumps({"check": "build-stratified-report", "self_test": "ok"}, sort_keys=True))
        return
    if len(sys.argv) < 2:
        print("usage: build-stratified-report.py <results.jsonl> [models.json]")
        sys.exit(2)
    path = sys.argv[1]
    models_path = sys.argv[2] if len(sys.argv) > 2 else ""
    recs = load_jsonl(path)

    modality = {}
    if models_path and os.path.exists(models_path):
        for m in json.load(open(models_path)):
            modality[m["provider"] + ":" + m["model_id"]] = m.get("modality", "chat")
    for r in recs:
        r["_modality"] = modality.get(r.get("model"), "chat")

    text = [r for r in recs if r["_modality"] == "chat"]
    nontext = [r for r in recs if r["_modality"] != "chat"]

    print("=" * 74)
    print("STRATIFIED DETERMINISM REPORT  -  {} combinations analyzed".format(len(recs)))
    print("=" * 74)

    t_gen = sum(1 for r in text if r.get("generation_ok"))
    n_gen = sum(1 for r in nontext if r.get("generation_ok"))
    print("\nGENERATION (skill authoring) success:")
    print("  text/chat models : {}/{} ({}%)".format(t_gen, len(text), pct(t_gen, len(text))))
    print("  non-text models  : {}/{} ({}%)  [embeddings/audio/image - expected low]".format(
        n_gen, len(nontext), pct(n_gen, len(nontext))))

    ds = det_stats(text)
    print("\nDETERMINISM (text/chat models, generation_ok + invoked twice):")
    print("  eligible combos       : {}".format(ds["eligible"]))
    print("  valid-JSON both runs  : {}/{} ({}%)".format(ds["schema_valid"], ds["eligible"], ds["schema_valid_pct"]))
    print("  RAW byte match        : {}/{} ({}%)".format(ds["raw_det"], ds["eligible"], ds["raw_det_pct"]))
    print("  CANONICAL value match : {}/{} ({}%)   <-- headline determinism".format(
        ds["canonical_det"], ds["eligible"], ds["canonical_det_pct"]))

    cs = [(r.get("skill_checks_passed", 0), r.get("skill_checks_total", 0))
          for r in text if r.get("generation_ok") and r.get("skill_checks_total")]
    if cs:
        perfect = sum(1 for a, b in cs if a == b)
        print("\nGENERATED-SKILL CONTRACT QUALITY (text models):")
        print("  avg checks passed : {:.2f} / {}".format(sum(a for a, _ in cs) / len(cs), cs[0][1]))
        print("  perfect           : {}/{} ({}%)".format(perfect, len(cs), pct(perfect, len(cs))))

    print("\nDETERMINISM BY USE-CASE CATEGORY (text models):")
    bycat = defaultdict(list)
    for r in text:
        bycat[r.get("category")].append(r)
    for cat in sorted(bycat):
        d = det_stats(bycat[cat])
        if d["eligible"]:
            print("  {:<14} canon-det {}/{} ({}%)".format(cat, d["canonical_det"], d["eligible"], d["canonical_det_pct"]))

    print("\nMODEL DETERMINISM RANKING (text models, >=3 eligible combos):")
    bymodel = defaultdict(list)
    for r in text:
        bymodel[r.get("model")].append(r)
    ranked = []
    for model, rs in bymodel.items():
        d = det_stats(rs)
        if d["eligible"] >= 3:
            ranked.append((d["canonical_det_pct"], model, d))
    ranked.sort(reverse=True)
    for p, model, d in ranked[:60]:
        print("  {:>5}%  {:<46} ({}/{} canon)".format(p, model, d["canonical_det"], d["eligible"]))

    print("\nGENERATION SUCCESS BY PROVIDER (all modalities; exposes fallback-only/unroutable):")
    byprov = defaultdict(list)
    for r in recs:
        byprov[r.get("provider")].append(r)
    for prov in sorted(byprov):
        rs = byprov[prov]
        g = sum(1 for r in rs if r.get("generation_ok"))
        print("  {:<16} {}/{} ({}%)".format(prov, g, len(rs), pct(g, len(rs))))

    out = {
        "combinations_analyzed": len(recs),
        "text_models": {"combos": len(text), "gen_ok": t_gen, "determinism": ds},
        "nontext_models": {"combos": len(nontext), "gen_ok": n_gen},
        "by_category": {c: det_stats(rs) for c, rs in bycat.items()},
        "model_ranking": [{"model": m, "canonical_det_pct": p, **d} for p, m, d in ranked],
    }
    outp = path.replace(".jsonl", "_stratified_report.json")
    json.dump(out, open(outp, "w"), indent=2)
    print("\nWrote", outp)


if __name__ == "__main__":
    main()
