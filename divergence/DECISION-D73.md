# D73 — real measured cost/timing infrastructure, and what it actually found

**Date:** 23 August 2026

## What was built

1. **`llm_call.py`**: `time.perf_counter()` replaces `time.time()` for
   interval measurement (monotonic, immune to system clock adjustments
   mid-call — the correct tool for "how long did this take", which
   `time.time()` only approximates). Every `_CALLS` entry gained
   `wall_ms` (derived from the same timer as the existing `elapsed_s`,
   never a second independently-tracked number that could drift from
   it). `provenance()`'s `by_node` gained `total_wall_ms`/`p50_wall_ms`/
   `max_wall_ms` per node, via a small hand-rolled `_median()` (standard
   library only, this project's own convention throughout) — trivial
   within one pipeline run (each node normally called once, so
   p50==max==the one sample), meaningful once multiple runs share a
   process without resetting `_CALLS` between them.
2. **`run_all_cases.py`** (new): runs all six real cases through
   `run_pipeline.py`, one subprocess per case — `run_pipeline.py` itself
   untouched; refactoring its already-verified, CI-gated `main()` into
   an importable function was considered and rejected, real risk to
   shipped code for a feature that can't be exercised with real data
   here anyway. Builds the markdown table in `results.md`'s new
   "Measured cost and tokens, per case" section.
3. **`cost_model.py`**: `latency_estimate()` now carries the requested
   disclosure — retained for projecting a hypothetical Claude
   deployment, real measured numbers available two other ways (D64's
   `--measured`, D73's `run_all_cases.py`), neither replacing the other
   since a projection for a deployment nobody has run still needs a
   model.

## What was verified against real, external sources before being used

**Featherless's concurrency model** — not the flat "N requests/second" a
few third-party summaries claimed (checked and rejected: several
disagreed with each other, none matched the primary source). Fetched
directly from Featherless's own docs: concurrent-unit cost scales with
model size — 1 unit under 16B parameters, 2 under 34B, 4 at 70B or
more (`featherless.ai/docs/concurrency`). This project's own three
model slots, checked against that scale: `small` (Qwen2.5-7B) = 1 unit;
`large` (Qwen2.5-72B) and `adversarial` (Mistral-Large-Instruct-2411,
~123B) = 4 units each.

**Featherless's actual per-model pricing** — fetched directly from the
live, public `/v1/models` catalog (a read-only, unauthenticated
endpoint; no API key touched, no inference call made, categorically
different from calling `/v1/chat/completions`). Found real pricing for
`mistralai/Mistral-Large-Instruct-2411`: $0.125 / $1.15 per million
input/output tokens. **Did not find `Qwen/Qwen2.5-7B-Instruct` or
`Qwen/Qwen2.5-72B-Instruct`** — this project's own configured
`small`/`large` slots, which have served every real call this project
has made — in that same live catalog, despite two separate targeted
searches. Reported as unpriced in every table this decision produces,
never guessed at from a third-party aggregator (several of those
disagreed with each other too). A catalog listing and a model's real
serving availability on an existing account are not necessarily the
same thing — `DECISION-D43.md` already documents the identical shape of
gap for `meta-llama/*` licence gating.

## What was actually measured, not modelled

**All six cases' input/output token counts are real**, not estimated —
five (C1–C5) from their own frozen historical records, D1 via a genuine
replay-cache hit against its own historical record (D63/D72), all
verified directly, not assumed. `run_all_cases.py` was run for real, in
this environment, twice: once under `DIVERGENCE_REPLAY=1` (D1 succeeds
via the seeded cache; C1–C5 correctly and cleanly fall back to their
historical token counts, each with an honest one-line reason why the
live/replay attempt failed) and once with no key and no replay mode at
all (every case falls back, cleanly, same honest reasons). Both runs
produced a real, non-crashing table — this is genuine, exercised
behaviour, not a code read.

## What is not claimed

**No case has a real, measured wall-clock time.** Every existing record
in this project — all six frozen historical ones, and the replay-cache
entries seeded from them — predates `llm_call.py`'s own wall-clock
instrumentation (D64). `run_all_cases.py`'s wall-clock column reports
"not measured" for exactly this reason, structurally, not because
something broke: it deliberately never falls back to a historical
number the way tokens do, because no historical number for it exists to
fall back to. The README's "Scalability" section's records/hour formula
is real and ready to use; the two numbers it needs — a real per-record
wall-clock time, and this project's own account's specific
concurrent-unit budget — are both honestly absent, not filled in with a
plausible-looking guess. Running `run_all_cases.py` with a working
`FEATHERLESS_API_KEY` is the one thing that closes the first gap; the
second needs whoever holds the account to say which plan it's on.
