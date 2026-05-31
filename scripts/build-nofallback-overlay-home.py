#!/usr/bin/env python3
"""Build a no-fallback overlay runtime-home for honest per-model benchmarking.

WHY: A model x use-case determinism benchmark is only valid if each result is
attributable to the NAMED model. Many agent runtimes wrap a oneshot call in a
fallback chain: when the requested model errors, the runtime silently retries a
DIFFERENT model and returns that output as if it were the requested model's.
That makes dead / unauthorized / non-chat (embedding) models and broken-OAuth
providers all report success under the wrong model id — corrupting the data.

FIX (this script): create a sibling runtime-home dir that symlinks every entry
of the real home EXCEPT the config file, which is a real copy with the fallback
chain key(s) emptied. Harness subprocesses point at this overlay via the home
env var your runtime honors; the user's real config is never mutated. The
writable runtime dirs are REAL dirs in the overlay so session writes do not
write through symlinks into the user's real home.

PLATFORM-AGNOSTIC: this script is runtime-neutral. Set the constants below (or
the matching environment variables) to your agent runtime's values:
  - AGENT_REAL_HOME  -> your runtime's home dir (default: ~/.agent)
  - AGENT_OVERLAY_HOME -> where to build the overlay (default: ~/.agent-harness)
  - AGENT_HOME_ENV   -> the env var name your runtime reads to override its home
  - AGENT_CONFIG_NAME -> the config file name inside the home (default: config.yaml)
  - FALLBACK_KEYS    -> the config keys that enable provider/model fallback
Different runtimes name these differently; there is no built-in default that
matches every runtime, so confirm them against your runtime's docs.

Idempotent: safe to re-run. Requires PyYAML only if your config is YAML.

AFTER BUILDING, VERIFY (do not skip):
  1. A known-good chat model still answers under <HOME_ENV>=<overlay>.
  2. A model that should fail (an embedding model, or a known-unauthorized id)
     now fails HONESTLY instead of being rescued by fallback.
Caveat: the overlay strips fallback but NOT credentials. OAuth providers that
only "worked" via fallback will now honestly fail — that failure is correct
data, not a regression.
"""
import json
import os
import sys

# --- Adapt these to your agent runtime (or set the matching env vars). ---
REAL = os.path.expanduser(os.environ.get("AGENT_REAL_HOME", "~/.agent"))
OVERLAY = os.path.expanduser(os.environ.get("AGENT_OVERLAY_HOME", "~/.agent-harness"))
# The env var name your runtime reads to override its home dir.
HOME_ENV = os.environ.get("AGENT_HOME_ENV", "AGENT_HOME")
CONFIG_NAME = os.environ.get("AGENT_CONFIG_NAME", "config.yaml")
# Fallback keys to neutralize. [] for list-shaped keys, None for scalar.
FALLBACK_KEYS = {"fallback_providers": [], "fallback_model": None}
# Dirs that must be REAL (writable) in the overlay, not symlinks.
WRITABLE_DIRS = {"sessions", "logs", "checkpoints", "tmp", "audio_cache"}


def main():
    if "--self-test" in sys.argv[1:]:
        print(json.dumps({"check": "build-nofallback-overlay-home", "self_test": "ok"}, sort_keys=True))
        return
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML required for YAML configs: pip install pyyaml")
    if not os.path.isdir(REAL):
        sys.exit("Real home not found: " + REAL)
    os.makedirs(OVERLAY, exist_ok=True)

    # Clear stale links / old config in the overlay (keep real writable dirs).
    for name in os.listdir(OVERLAY):
        p = os.path.join(OVERLAY, name)
        if os.path.islink(p):
            os.unlink(p)
        elif name == CONFIG_NAME and os.path.isfile(p):
            os.remove(p)

    linked = real_dirs = 0
    for name in os.listdir(REAL):
        if name == CONFIG_NAME:
            continue  # handled separately below
        src = os.path.join(REAL, name)
        dst = os.path.join(OVERLAY, name)
        if name in WRITABLE_DIRS and os.path.isdir(src):
            os.makedirs(dst, exist_ok=True)
            real_dirs += 1
            continue
        if os.path.lexists(dst):
            continue
        os.symlink(src, dst)
        linked += 1

    with open(os.path.join(REAL, CONFIG_NAME)) as f:
        cfg = yaml.safe_load(f) or {}
    removed = []
    for key, empty_val in FALLBACK_KEYS.items():
        if key in cfg:
            cfg[key] = empty_val
            removed.append(key)
    with open(os.path.join(OVERLAY, CONFIG_NAME), "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print("Overlay home:", OVERLAY)
    print("Symlinked entries:", linked, "| real writable dirs:", real_dirs)
    print("Fallback keys neutralized:", removed)
    print("Point harness subprocesses at " + HOME_ENV + "=" + OVERLAY)


if __name__ == "__main__":
    main()
