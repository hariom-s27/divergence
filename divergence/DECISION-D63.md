# D63 — replay cache: DIVERGENCE_REPLAY=1 reproduces D1 with no API key

**Date:** 22 August 2026
**M5 of a same-day priority list. Two real bugs found and fixed while building this, both before anything shipped — the second one caught by tracing the actual data flow, not by trusting the first fix.**

## What "reproducible" actually requires

A pipeline that only runs for whoever holds a paid Featherless key is a
demo, not something a judge (or this project's own CI) can independently
re-run. `replay_cache.py` + `DIVERGENCE_REPLAY=1` makes
`run_pipeline.py` reproduce a real, already-verified run — D1, the
frozen demo record — from cached request/response pairs, with **zero**
API calls, on a machine that has never talked to Featherless.

```
$env:DIVERGENCE_REPLAY = "1"
python run_pipeline.py --record-id D1-replay --tax-year "FY 2026-27" `
    --text cases/D1/input.md --node5 --out runs/replay_test.json
```

`llm_call.call_json()` (the single place every node talks to a model)
checks replay mode first. A cache hit returns the real cached response
with no network call. A miss raises `LLMError` naming exactly what
request has no cached replay — never silently falls through to a real
call (defeats the point) and never fabricates a plausible response
(worse than either).

## Two real bugs, found before this shipped, not after

**Bug 1 — `provenance()` and every node's own CLI print statement call
`provider_name()`/`model_id()` unconditionally**, and both of those
functions are deliberately built (D44) to raise an error if
`FEATHERLESS_API_KEY` is missing — which it always is, on purpose, in
replay mode. The very first thing `run_pipeline.py --node5` does is print
the provider; every node's `extract()`/`detect_gaps()`/`resolve()`/
`check()` calls `provenance()` immediately after its own `call_json()`
returns. Both would have crashed replay mode one line after the first
cache hit. Fixed with `provider_display()`/`model_display()` — the same
functions, made replay-safe — and `provenance()` itself branching on
`replay_cache.is_replay_mode()` before touching either.

**Bug 2 — nonce spotlighting (D62) is fundamentally incompatible with a
naive request-hash cache key, and the first version of this file shipped
that incompatibility unnoticed.** Every real node1 call generates a
fresh, cryptographically random nonce on purpose — a predictable one is
forgeable, which defeats spotlighting's entire point — and that nonce
appears in BOTH the system prompt (the instruction names it) and the
user content (the document is wrapped in it). Hashing either directly
means the identical document never produces the identical cache key
twice: replay would silently miss on its own single most important node,
every time, even immediately after seeding it. Caught before shipping by
actually testing key stability across two different real random nonces
(not assumed from reading the code) — confirmed the keys differed.
**Fixed** with `call_json(..., cache_key_system=, cache_key_content=)`:
node1 rebuilds the identical request with a fixed placeholder nonce
purely for cache-key purposes, while the request actually sent to the
model keeps the real random one throughout. Re-tested after the fix:
stable keys now match across different real nonces for the same
document, confirmed directly, not assumed.

## Verified end to end, not just unit-tested in isolation

`build_replay_cache.py` seeds all five node entries — extract, gap
detector, both resolvers, adversarial checker — by reconstructing each
one's exact request (the same functions `run_pipeline.py` itself calls,
against today's live corpus and prompts) and pairing it with D1's real,
already-schema-validated output
(`runs/21aug/D1_final_seed2.json` and its matching
`D1_final_seed2_attack.json`), disclosed as seeded
(`source: "seeded"` in each cache entry), never indistinguishable from a
live call.

Ran the full pipeline, `--node5` included, with `DIVERGENCE_REPLAY=1` and
**no `FEATHERLESS_API_KEY` set in the environment at all**:
- `provider=replay`, `0 in / 0 out tokens` on every one of 5 calls.
- Output `facts{}` — **byte-for-byte identical** to the frozen record.
- Output `missing[]` — **byte-for-byte identical**.
- Output `attacked[]` — **byte-for-byte identical** to the separately-saved
  `D1_final_seed2_attack.json` (the record it belongs to never carried
  `attacked` itself, since node 5 was originally run as a separate pass —
  confirmed this precisely rather than assuming the two files should
  match each other).
- `schema.json: VALID` on the replayed record, same as the original.

## What this is and is not

**Is**: a genuine reproducibility guarantee for D1, checked continuously
— wired into CI (`Replay reproducibility check (no API key)`, this
project's actual GitHub Actions runner, which has no Featherless secret
configured, so this is a real test of the claim, not a simulated one).

**Is not**: a cache for every possible input. Only D1 is seeded today.
Any other case, or any prompt/corpus change, needs `build_replay_cache.py`
re-run (or, for a genuinely new input, a real `--node5` run with a key,
which the normal `source="live"` recording path then adds to the cache
automatically, growing it over time without any extra step).
