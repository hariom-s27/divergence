#!/usr/bin/env python3
"""
REPLAY CACHE — DIVERGENCE
A pipeline that can only be reproduced by whoever holds a paid API key is
not actually reproducible — it's a demo. This makes `run_pipeline.py`
replayable with DIVERGENCE_REPLAY=1 and no API key at all, from real,
already-verified request/response pairs, not synthetic stand-ins.

    $env:DIVERGENCE_REPLAY = "1"          # PowerShell
    export DIVERGENCE_REPLAY=1            # bash
    python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" \\
        --text step21drop/cases/D1/input.md --node5 --out runs/replay_test.json

Cache key: sha256(node_name + system + user_content), where user_content
is JSON-serialised the same way every time. Same node, same inputs, same
key -- deterministic, not fuzzy-matched. `llm_call.call_json()` checks
this cache first when replay mode is active; a MISS raises a clear error
naming exactly what's missing, never silently falls through to a real
API call (which would defeat the point) and never fabricates a plausible-
looking response (which would be worse).

Recording is automatic and cheap: every real, successful call, in normal
(non-replay) operation, is saved here too -- so the cache grows from
genuine runs over time. `build_replay_cache.py` seeds it once, up front,
by reconstructing the exact requests today's corpus/prompts produce and
pairing them with D1's real, already-verified, frozen output --
disclosed as exactly that, not hidden as if it were a fresh live call.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "replay_cache")


def is_replay_mode():
    return os.environ.get("DIVERGENCE_REPLAY", "").strip() == "1"


def _key(node_name, system, user_content):
    payload = json.dumps(
        {"node": node_name, "system": system, "user": user_content},
        sort_keys=True, default=str, ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _path(key):
    return os.path.join(CACHE_DIR, f"{key}.json")


def load(node_name, system, user_content):
    """Returns the cached response object, or None if this exact
    (node, system, user_content) triple has never been cached."""
    key = _key(node_name, system, user_content)
    p = _path(key)
    if not os.path.exists(p):
        return None
    entry = json.load(open(p, encoding="utf-8"))
    return entry["response"]


def save(node_name, system, user_content, response_obj, source="live"):
    """source is 'live' for a real call recorded in normal operation, or
    'seeded' for one built by build_replay_cache.py from an already-
    verified saved run -- kept in the entry so the cache is honest about
    its own provenance, not indistinguishable from a fresh call."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = _key(node_name, system, user_content)
    entry = {
        "node": node_name,
        "source": source,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "response": response_obj,
    }
    with open(_path(key), "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)
    return key


def stats():
    if not os.path.isdir(CACHE_DIR):
        return {"entries": 0, "by_node": {}}
    by_node = {}
    for fn in os.listdir(CACHE_DIR):
        if not fn.endswith(".json"):
            continue
        entry = json.load(open(os.path.join(CACHE_DIR, fn), encoding="utf-8"))
        by_node[entry["node"]] = by_node.get(entry["node"], 0) + 1
    return {"entries": sum(by_node.values()), "by_node": by_node}


if __name__ == "__main__":
    s = stats()
    print(f"\n  replay_cache/: {s['entries']} entr(y/ies)\n")
    for node, n in sorted(s["by_node"].items()):
        print(f"    {node:<20} {n}")
    print()
    sys.exit(0)
