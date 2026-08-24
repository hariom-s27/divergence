# D76 — true factored verification in node 5 (S6), and passive JSON-mode/repair telemetry in provenance() (S8)

**Date:** 23 August 2026

## S6 — the other half of factored verification, D67 didn't close it

`DECISION-D67.md` (S6's first pass) made node 5 **draft-blind**: an
opt-in flag strips each conclusion's own `reasoning` field before node 5
ever reads it, so the checker can't be anchored by the producer's own
persuasive case for itself. That closed one real exposure (Panickssery et
al., NeurIPS 2024 — an LLM evaluator favours reasoning that reads like
its own) but left a second, larger one standing, found reading
`node5_adversarial.check()`'s own prompt construction: **every call —
draft-blind or not — still bundles every conclusion in `regimes[]` into
one shared context.** An attack on conclusion 2 is still formed
immediately after the same call has just read conclusions 1 and 3. That
is joint verification of multiple targets, not factored verification of
one — regardless of whether `reasoning` was stripped from what gets
jointly verified.

**Dhuliawala et al., *Chain-of-Verification Reduces Hallucination in
Large Language Models*** (Findings of ACL 2024) name the general shape of
the fix: draft a response, plan verification questions, then **"answers
those questions independently"**, generated *"so the answers are not
biased by other responses."* Quoted directly from the paper's own
abstract — no precision/F1 numbers appear there, so none is claimed here;
the design lesson is taken, the technique's own reported numbers are not.

**What was built:** `node5_adversarial.check_factored(regimes, missing,
valuation, tax_year, model="adversarial", draft_blind=False)` — a plain
Python loop calling the existing `check()` once per conclusion, each call
seeing exactly one target and nothing about the others' outcome,
citation, or certainty, still checked against the identical gap list,
valuation lattice, and full corpus every call already used. Composes
freely with `draft_blind` (D67) — both, either, or neither. Wired as
`node5_adversarial.py --factored` and `run_pipeline.py --node5
--factored`, alongside the existing `--draft-blind` flag, same
reproducibility discipline: off by default, so every existing `--node5`
run stays reproducible without it.

**Reused, not reinvented — same pattern as `resolve_k()` (D75).** Rather
than a new call shape, `check_factored()` is a loop over the existing
per-target primitive. This gets provenance for free: `run_pipeline.py`'s
own `_meta.llm` is built from `llm_call.provenance()`, which reads the
global `_CALLS` list every real `call_json()` invocation already appends
to — so N factored calls show up automatically as `calls: N` on
`node5_adversarial`'s row, with no separate wiring needed. The one place
this isn't free: `run_pipeline.py`'s own progress-line printer expected a
single `meta` dict, not a list of N; fixed to sum `in_tokens`/
`out_tokens`/`retries` across the list when `--factored` is set.

**Cost, disclosed, not hidden:** N calls instead of 1 (N = `len(regimes)`,
typically 3 on this project's own cases) — roughly triples node 5's own
token cost and call count whenever `--factored` is used. Never on by
default for exactly this reason.

### Verified two ways, no live key available

1. **Real replay-cache behaviour, not a mock.** `check()` (joint) in
   replay mode against D1's real seeded cache still **hits** — 4 attacks,
   2 survived, byte-identical to `runs/21aug/D1_final_seed2_attack.json`
   — proving nothing regressed. `check_factored()` against the identical
   real data correctly **misses** — raises `LLMError` naming a cache key
   that was never seeded — because a single-conclusion request hashes to
   a genuinely different key than the joint one. That miss is the proof
   the new code path constructs a real, different, independent request
   rather than silently collapsing to the joint call under the hood.
2. **Mechanical isolation and merge correctness**, `check()` mocked (no
   key needed for this half): fed three real-shaped conclusions through
   `check_factored()`, asserted each underlying call received exactly one
   conclusion (`len(regimes) == 1` inside the mock, checked, not assumed),
   that `attacked`/`limits` concatenate in the original order, and that
   `per_target_meta` carries one row per conclusion with the right
   `target_index`/`regime` labels. All three checks passed.

**What is not claimed:** whether factored verification actually changes
what node 5 catches — same disclosure D67 already made for draft-blind,
now made again for its sibling flag. That is a live question this
environment has no `FEATHERLESS_API_KEY` to ask. What this decision
closes is the part that was answerable without one: the flag exists,
defaults to off, is proven to construct genuinely independent requests
(not just claimed to), and composes with `--draft-blind` — one comparison
away the moment someone can run it.

---

## S8 — `response_format` survival and JSON-repair events, into `provenance()`

`llm_call.py` sends `response_format={"type": "json_object"}` on every
JSON-mode call, with a silent fallback (pop the kwarg, retry) if the
provider errors on it. Featherless's own documented
`/v1/chat/completions` parameter list — checked directly, not assumed —
does not name `response_format`, `json_schema`, `n`, or `logprobs` at
all. `capability_probe.py` (D68, S8's first pass) already built the
**controlled** experiment for this: a flag-vs-no-flag A/B call pair,
self-tested, classified into REJECTED / ENFORCED / APPARENT NO-OP /
INCONCLUSIVE / ERROR. What it does not do is tell a reader what actually
happened across the *real* pipeline calls this project has made — this
closes that other half.

**What was built, in `llm_call.py`, `replay_cache.py`:**

1. **`_extract_json_verbose(text)`** — the same relaxed JSON parser
   (strict `json.loads`, then fence-stripped, then brace-matched) now
   returns `(obj, method)` instead of just `obj`. `method` is `"direct"`
   (no repair needed), `"fenced"`, or `"brace_matched"`. `_extract_json()`
   is kept as a thin wrapper for `try_parse_json()`'s existing callers
   (`capability_probe.py`), unaffected by this.
2. **`_raw_call()`** now returns a fifth value, `response_format_sent`:
   `True` if the request that produced the response still carried
   `response_format`, `False` if it was attempted and popped after the
   provider rejected it outright, `None` if this call never attempts it
   at all (the Anthropic path — a different API shape, not a rejection;
   this project's real evaluation runs on Featherless exclusively, D44,
   so this branch is a completeness note more than a live path).
3. **`call_json()`**'s retry loop records both signals per call into
   `_CALLS`: `response_format_sent`, `json_repair_method`, and
   `json_repaired` (`method != "direct"`). **A call can be
   `response_format_sent=True` AND `json_repaired=True` at once** — the
   provider didn't error on the kwarg, yet the response still needed
   fence-stripping or brace-matching to parse — which is itself passive
   evidence toward "silent no-op," the exact question `capability_probe.py`
   already asks directly. This field doesn't replace that probe; it's the
   every-real-call signal alongside the controlled one.
4. **`provenance()`** aggregates both, per node and project-wide:
   `by_node[node].json_repairs`, `.response_format_popped`,
   `.response_format_not_applicable`; top-level `json_repair_events`,
   `response_format_popped_events`, `response_format_not_recorded_events`.
5. **`replay_cache.save()`/`load()`** extended to carry
   `response_format_sent`/`json_repair_method` as stored metadata (not
   part of the lookup key, same treatment D72 already gives
   provider/model/token counts) — a replayed call restores the ORIGINAL
   call's real signal, not a fabricated default. Cache entries saved
   before this decision don't have these keys; `entry.get(...)` correctly
   reads them back as `None` ("not recorded"), never silently presented
   as `"direct"`/`True`.

### Verified against the real replay cache, not just compiled

Ran the exact CI replay-reproducibility check
(`DIVERGENCE_REPLAY=1 run_pipeline.py --node5`, same command
`.github/workflows/python-package-conda.yml` runs) against the modified
code. **All existing assertions still pass** — `facts`, `missing`, and
`attacked` byte-identical to the frozen `D1_final_seed2.json`/
`_attack.json`, `replayed: True` throughout. On this replayed run (every
cache entry predates D76): `json_repair_events: 0`,
`response_format_popped_events: 0`,
`response_format_not_recorded_events: 5` — exactly the five nodes, each
correctly reading `response_format_not_applicable` for a pre-D76 cache
entry rather than a fabricated value. This is the honest state of the
signal today: **it has never yet been measured against a live call in
this project's history**, because none of the cached entries predate a
live key being available; the first real number appears the moment a
future live run (`run_all_cases.py`, D73's own still-open item) produces
one.

### What is not built

- **A live-measured `json_repair_events` count.** Same constraint named
  throughout this file and every S/M item since D62: no
  `FEATHERLESS_API_KEY` in this environment. The counters are real, wired,
  verified not to break the replay contract, and read `0`/`not_applicable`
  on 100% pre-D76 data — which is the correct, honest value for data that
  predates the instrumentation, not a claim that repair events don't
  happen in practice.
- **A merge of this passive signal into `capability_probe.py`'s own
  report.** The probe's controlled A/B and this file's passive per-call
  counters answer related but distinct questions (does the flag do
  anything under controlled conditions, vs. how often did production
  calls need repair regardless) — left as two separate, clearly-labelled
  signals rather than combined into one number that would blur which
  question it answers.
