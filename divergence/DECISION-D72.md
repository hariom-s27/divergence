# D72 — the replay cache's own real gaps closed: key completeness, provenance restoration, seed honesty

**Date:** 23 August 2026

## What this actually is, disclosed before the rest

A request asked for "a response cache and replay mode" for
`llm_call.py`. Reading the file first (as asked) found that mechanism
already shipped as D63 — `replay_cache.py`, `DIVERGENCE_REPLAY=1`, a
loud raise on a cache miss, a CI gate that runs it on every push. Not
rebuilt from scratch. What follows is the part of the request that
named real, specific, verifiable gaps in that existing mechanism, found
by checking the request's own claims against the actual code rather than
assuming either "already done" or "build everything as literally
specified":

1. **The cache key was incomplete.** `_key(node_name, system,
   user_content)` — no model, no temperature, no max_tokens. A live
   model or temperature change between a real run and a later replay
   attempt would have gone undetected, silently serving a response
   generated under different settings. Real, confirmed by reading
   `_key()`'s own source, not assumed from its docstring.
2. **The seed value was never recorded.** `_raw_call()` already sent
   `DIVERGENCE_SEED` to the API when set (line 403, pre-D72) but nothing
   downstream ever surfaced it. Confirmed by grepping `provenance()`'s
   own return dict for `seed` — absent.
3. **Featherless's own documented caveat about `seed` was never quoted
   anywhere in this codebase.** Verified directly against the primary
   source before writing anything down (`featherless.ai/docs/completions`,
   fetched and read, not taken on the request's own word): *"Random seed
   for generation. (Not reliable, as we use multiple servers)."* — exact
   wording, `/v1/chat/completions`, the endpoint this project's own
   `_raw_call()` actually calls.

## Two deliberate deviations from the literal request, both disclosed

**Cache key uses `model_key` (the slot name), not the fully-resolved
`provider`/`model` the request specified.** Resolving those needs
`provider_name()`/`model_id()`, which need an API key to even pick a
provider — and replay mode's entire reason for existing is running with
none. Including them in the *lookup* key would make replay mode unable
to compute its own lookup key in the zero-key environment it's built
for, which would defeat the point more thoroughly than the gap it was
meant to close. `model_key` is the most specific thing genuinely
computable in both modes. The *resolved* provider/model id is still
recorded, as metadata, in every entry a real live call or a real
historical seed produces — available to a reader, just not part of what
gets hashed.

**Storage stays at `replay_cache/<key>.json`, not
`runs/<record_id>/calls/<key>.json`.** The existing scheme is global
(content-keyed, not record-id-scoped) — which is exactly why
`--record-id D1-replay` has worked all session regardless of what label
a given run used, and why the CI gate can pass without knowing a
specific record_id in advance. A per-record_id scheme would break that
property and fragment the project into two parallel cache stores for no
correctness gain the key-completeness fix doesn't already provide.

## What was verified, and how

- `replay_cache.py`'s `_key()`/`save()`/`load()` extended; `load()` now
  returns the full entry (provider, model, tokens, retries, elapsed_s,
  seed), not just the response, so a replay hit can restore the
  *original* call's real provenance.
- `llm_call.py`'s replay branch now restores that real historical data
  into `_CALLS`, with an explicit `"replayed": True` on every entry —
  live calls get `"replayed": False` for the same reason, so the field
  is never just silently absent. `provenance()` gained a top-level
  `"replayed"` (true if *any* call in the run was served from cache) and
  `"seed"`/`"seed_note"` (the verified Featherless quote, plus an
  explicit pointer to what this project's reproducibility actually rests
  on instead).
- `build_replay_cache.py` re-seeds all five node entries using D1's own
  *real* historical `_meta` (provider, model, in/out tokens, retries —
  actually measured, not fabricated) for every field that record
  genuinely has, and an honestly-empty `elapsed_s=0.0`/`seed=None` for
  the two fields that record predates (D64, this commit) rather than
  guessing at them.
- **Ran the full pipeline end to end in replay mode after reseeding**:
  `facts`/`missing`/`attacked` still byte-identical to the frozen D1
  originals (no regression), and `_meta.llm.by_node` now shows real,
  non-zero historical token counts on every node instead of the zeroed
  stand-in every prior replay run this session has shown — a visible,
  immediate confirmation the fix works, not just a code read.

## What is not claimed

**The exact two-command sequence this decision documents in
`divergence/README.md` — run live once, then replay that same run —
was not executed end to end here.** The first command needs a real
`FEATHERLESS_API_KEY` this environment does not have, the same
constraint every S/M/D item touching live model behaviour has hit since
D62. What *was* verified is the identical code path under a different
name: `build_replay_cache.py`'s `source="seeded"` calls `replay_cache.save()`
with the same signature, same key computation, same stored fields a real
`source="live"` call would use — and replaying that seeded data
reproduced the frozen record exactly. The "live" and "seeded" paths are
structurally the same function call from two different call sites, not
two different mechanisms — but a literal fresh live response was never
generated and replayed here, and this file does not claim it was.
