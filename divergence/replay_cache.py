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

D72: the key now also covers model_key/temperature/max_tokens, not just
node/system/user -- closing a real gap the original key left open (a
model or temperature change between a live run and a later replay
attempt would previously have gone undetected, silently serving a
response generated under different settings). Deliberately NOT the
fully-RESOLVED provider/model id, though -- resolving those needs
provider_name()/model_id(), which need an API key to pick a provider at
all, and replay mode's entire reason for existing is running with none.
model_key (the slot name, e.g. "small") is the most specific thing
computable in both modes without ever touching a key. The resolved
provider/model id IS still recorded, as metadata, in every entry saved
from a real live call (source="live") or a real historical one
(build_replay_cache.py, source="seeded") -- available to a human or to
cost_model.py reading the file, just not part of the lookup key itself.
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


def _key(node_name, system, user_content, model_key=None, temperature=None, max_tokens=None):
    payload = json.dumps(
        {"node": node_name, "system": system, "user": user_content,
         "model_key": model_key, "temperature": temperature, "max_tokens": max_tokens},
        sort_keys=True, default=str, ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _path(key):
    return os.path.join(CACHE_DIR, f"{key}.json")


def load(node_name, system, user_content, model_key=None, temperature=None, max_tokens=None):
    """Returns the full cached entry dict (node, source, cached_at,
    provider, model, in_tokens, out_tokens, retries, elapsed_s, seed,
    response), or None if this exact request has never been cached.
    D72: used to return only entry["response"] -- now returns the whole
    entry so a replay hit can restore the ORIGINAL call's real
    provenance (what model, how many tokens, how long it took) instead
    of the zeroed stand-in llm_call.py used to fabricate for every
    replayed call."""
    key = _key(node_name, system, user_content, model_key, temperature, max_tokens)
    p = _path(key)
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def save(node_name, system, user_content, response_obj, source="live",
         model_key=None, temperature=None, max_tokens=None,
         provider=None, model=None, in_tokens=0, out_tokens=0,
         retries=0, elapsed_s=0.0, seed=None,
         response_format_sent=None, json_repair_method=None):
    """source is 'live' for a real call recorded in normal operation, or
    'seeded' for one built by build_replay_cache.py from an already-
    verified saved run -- kept in the entry so the cache is honest about
    its own provenance, not indistinguishable from a fresh call.

    provider/model/in_tokens/out_tokens/retries/elapsed_s/seed (D72):
    the real, resolved values from the call that produced response_obj,
    stored as metadata alongside it -- NOT part of the lookup key
    (see _key()'s own docstring for why), but available to restore on a
    later replay hit and to a human reading the file directly.

    response_format_sent/json_repair_method (S8/D76): same treatment,
    same reason -- neither is part of the lookup key, both are metadata
    about the ORIGINAL live call, restored verbatim on a later replay hit
    rather than silently reset to a default. Cache entries saved before
    D76 don't have these keys at all; a replay hit against one of those
    correctly reads them back as None via entry.get(), not a fabricated
    "direct"/True that never happened."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = _key(node_name, system, user_content, model_key, temperature, max_tokens)
    entry = {
        "node": node_name,
        "source": source,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "model_key": model_key,
        "provider": provider,
        "model": model,
        "in_tokens": in_tokens,
        "out_tokens": out_tokens,
        "retries": retries,
        "elapsed_s": elapsed_s,
        "seed": seed,
        "response_format_sent": response_format_sent,
        "json_repair_method": json_repair_method,
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
