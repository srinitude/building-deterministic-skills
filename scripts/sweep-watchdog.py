#!/usr/bin/env python3
"""Silent-when-healthy watchdog for a long parallel sweep.

Designed for a scheduled job (every ~30m): empty stdout => no message is sent;
the operator only hears about problems.

Prints an ALERT only when:
  - the sweep process is dead AND the ledger is incomplete (with resume cmd), or
  - progress has STALLED (ledger line count unchanged since the last check), or
  - the sweep just reached 100% (one completion message, then stays silent).

Edit the CONFIG block for your run. Keep state in a sidecar JSON so stall
detection compares against the previous tick. If your scheduler requires a bare
script filename rather than an absolute path, honor that constraint.
"""
import json
import os
import subprocess
import sys
import time

# ---- CONFIG: edit per sweep ----
BASE = "/ABS/PATH/TO/sweep/workdir"          # dir holding reports/
PROC_MATCH = "parallel-sweep-harness.py"      # pgrep pattern for the sweep
WORKER_MATCH = "agent -z"                    # pgrep pattern for in-flight calls
TOTAL = 64824                                  # expected combo count
RESUME_CMD = ("python3 parallel-sweep-harness.py --combo-module eval_harness "
              "--models models_all.json --cases use_cases.json "
              "--out reports/full_results.jsonl --ledger reports/full_ledger.txt "
              "--workers 20 --invocation-runs 2")
# --------------------------------

LEDGER = os.path.join(BASE, "reports", "full_ledger.txt")
SWEEPLOG = os.path.join(BASE, "reports", "full_sweep.log")
STATE = os.path.join(BASE, "reports", "watchdog_state.json")


def count_lines(path):
    try:
        with open(path) as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def pgrep_count(pat):
    try:
        out = subprocess.run(["pgrep", "-f", pat], capture_output=True, text=True)
        return len([x for x in out.stdout.split() if x.strip()])
    except Exception:
        return 0


def sweep_exit_code():
    try:
        for line in reversed(open(SWEEPLOG).read().splitlines()):
            if line.startswith("EXIT=") or line.startswith("FULLSWEEP_EXIT="):
                return line.split("=", 1)[1].strip()
    except FileNotFoundError:
        pass
    return None


def main():
    if "--self-test" in sys.argv[1:]:
        print(json.dumps({"check": "sweep-watchdog", "self_test": "ok"}, sort_keys=True))
        return
    done = count_lines(LEDGER)
    running = pgrep_count(PROC_MATCH) > 0
    active = pgrep_count(WORKER_MATCH)
    exit_code = sweep_exit_code()

    prev = {"done": -1, "ts": 0}
    if os.path.exists(STATE):
        try:
            prev = json.load(open(STATE))
        except Exception:
            pass
    now = time.time()
    json.dump({"done": done, "ts": now, "running": running}, open(STATE, "w"))
    pct = round(100.0 * done / TOTAL, 1)

    if done >= TOTAL:
        if prev.get("done", 0) < TOTAL:
            print("SWEEP COMPLETE: {}/{} (100%). Aggregate the results JSONL "
                  "for the final report.".format(done, TOTAL))
        return  # already reported -> silent

    if not running:
        print("SWEEP ALERT: process dead, only {}/{} ({}%) done (exit={}). "
              "Resume: {}".format(done, TOTAL, pct, exit_code, RESUME_CMD))
        return

    if done == prev.get("done") and prev.get("done", -1) >= 0:
        print("SWEEP ALERT: running but STALLED at {}/{} ({}%) since ~{:.0f}m "
              "ago; {} active workers. Check rate limits / hung workers.".format(
                  done, TOTAL, pct, (now - prev.get("ts", now)) / 60, active))
        return
    # healthy + progressing -> no output


if __name__ == "__main__":
    main()
