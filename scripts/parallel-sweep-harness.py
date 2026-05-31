#!/usr/bin/env python3
"""Parallel, resumable model x use-case determinism sweep.

Reusable harness for the GATED full matrix run (see
references/model-skill-matrix-evals.md "Running the gated full matrix").
Provide your own single-combo function via --combo-module: a Python module
exposing `run_combination(model_id, provider, case, invocation_runs,
gen_timeout, inv_timeout) -> dict`. That function must do generate ->
validate -> invoke xN -> canonical hash and return a JSON-serializable record
with at least keys: generation_ok (bool), canonical_exact_match (bool|None).

Key properties:
  * ThreadPoolExecutor parallelism (subprocess I/O bound; GIL released in
    subprocess.run). Workers sized by RAM (~195 MB per oneshot child call).
  * Provider-spread (round-robin) ordering so concurrent in-flight calls hit
    different providers -> fewer per-provider 429s.
  * fsync checkpoint/resume ledger keyed "provider:model_id::case_id". Re-run
    the same command to resume; only remaining combos are executed.

Example:
  python3 parallel-sweep-harness.py --combo-module eval_harness \
      --models models_all.json --cases use_cases.json \
      --out reports/full_results.jsonl --ledger reports/full_ledger.txt \
      --workers 20 --invocation-runs 2
"""
import argparse
import importlib
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def combo_key(provider, model_id, case_id):
    return "{}:{}::{}".format(provider, model_id, case_id)


def load_ledger(path):
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(line)
    return done


def provider_spread_order(models, cases):
    """Round-robin combos across providers so concurrent workers spread load."""
    by_provider = {}
    for m in models:
        by_provider.setdefault(m["provider"], []).append(m)
    queues = {}
    for prov, ms in by_provider.items():
        q = []
        for m in ms:
            for c in cases:
                q.append((m, c))
        queues[prov] = q
    order = []
    provs = list(queues.keys())
    idx = {p: 0 for p in provs}
    remaining = sum(len(q) for q in queues.values())
    while remaining > 0:
        for p in provs:
            i = idx[p]
            if i < len(queues[p]):
                order.append(queues[p][i])
                idx[p] = i + 1
                remaining -= 1
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--combo-module", required=False,
                    help="importable module exposing run_combination(...)")
    ap.add_argument("--models", required=False, help="JSON: [{provider, model_id}]")
    ap.add_argument("--cases", required=False, help='JSON: {"cases": [{"id", ...}]}')
    ap.add_argument("--out", required=False)
    ap.add_argument("--ledger", required=False)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--invocation-runs", type=int, default=2)
    ap.add_argument("--gen-timeout", type=int, default=200)
    ap.add_argument("--inv-timeout", type=int, default=150)
    ap.add_argument("--progress-every", type=int, default=50)
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps({"check": "parallel-sweep-harness", "self_test": "ok"}, sort_keys=True))
        return
    missing = [f for f in ("combo_module", "models", "cases", "out", "ledger") if not getattr(args, f)]
    if missing:
        ap.error("the following arguments are required: " + ", ".join("--" + m.replace("_", "-") for m in missing))

    sys.path.insert(0, os.path.dirname(os.path.abspath(args.combo_module))
                    if os.path.sep in args.combo_module else ".")
    mod = importlib.import_module(args.combo_module.replace(".py", ""))
    run_combination = mod.run_combination

    with open(args.models) as f:
        models = json.load(f)
    with open(args.cases) as f:
        cases = json.load(f)["cases"]

    order = provider_spread_order(models, cases)
    done = load_ledger(args.ledger)
    todo = [(m, c) for (m, c) in order
            if combo_key(m["provider"], m["model_id"], c["id"]) not in done]

    total = len(order)
    print("Total combos: {} | done: {} | remaining: {} | workers: {}".format(
        total, len(done), len(todo), args.workers), file=sys.stderr)
    if not todo:
        print("Nothing to do -- sweep already complete.", file=sys.stderr)
        return

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    lock = threading.Lock()
    out_f = open(args.out, "a")
    led_f = open(args.ledger, "a")
    ctr = {"n": 0, "gen_ok": 0, "det": 0, "start": time.time()}

    def work(mc):
        m, c = mc
        try:
            rec = run_combination(m["model_id"], m["provider"], c,
                                  args.invocation_runs, args.gen_timeout,
                                  args.inv_timeout)
        except Exception as e:
            rec = {"model": m["provider"] + ":" + m["model_id"],
                   "provider": m["provider"], "model_id": m["model_id"],
                   "case_id": c["id"], "generation_ok": False,
                   "gen_error": "harness_exc: " + str(e)[:300],
                   "canonical_exact_match": None}
        key = combo_key(m["provider"], m["model_id"], c["id"])
        with lock:
            out_f.write(json.dumps(rec) + "\n")
            out_f.flush()
            os.fsync(out_f.fileno())
            led_f.write(key + "\n")
            led_f.flush()
            os.fsync(led_f.fileno())
            ctr["n"] += 1
            if rec.get("generation_ok"):
                ctr["gen_ok"] += 1
            if rec.get("canonical_exact_match"):
                ctr["det"] += 1
            n = ctr["n"]
            if n % args.progress_every == 0 or n == len(todo):
                el = time.time() - ctr["start"]
                rate = n / el if el else 0
                eta = (len(todo) - n) / rate if rate else 0
                print("[{}/{}] gen_ok={} det={} | {:.2f} combo/s | {:.0f}m | "
                      "ETA {:.1f}h".format(n, len(todo), ctr["gen_ok"], ctr["det"],
                                           rate, el / 60, eta / 3600), file=sys.stderr)
        return rec

    try:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            for _ in as_completed([ex.submit(work, mc) for mc in todo]):
                pass
    finally:
        out_f.close()
        led_f.close()
    print("DONE. {} combos in {:.1f}m. gen_ok={} det={}".format(
        ctr["n"], (time.time() - ctr["start"]) / 60, ctr["gen_ok"], ctr["det"]),
        file=sys.stderr)


if __name__ == "__main__":
    main()
