# D64 — real wall-clock latency instrumentation, and why it isn't populated yet

**Date:** 22-23 August 2026
**M6 of a same-day priority list. Built the measurement infrastructure and the report; the actual live numbers are explicitly not asserted, because producing them needs a real API key this environment doesn't have — the same honest gap as D62's live verification and D63's original build.**

## What was missing

`cost_model.py::latency_estimate()` has always been a *model* — a formula
over token counts and an assumed tokens/second rate, explicitly for a
hypothetical Anthropic Claude deployment (`README.md`'s Cost section:
"an estimate of what this architecture would cost if deployed on a
metered provider... not a number from an actually-measured run"). Nothing
anywhere recorded real, measured wall-clock time for the pipeline's
actual runs, on its actual provider (Featherless, Qwen/Mistral).

## What was built

**`llm_call.py`**: `call_json()` now records `elapsed_s` — real
`time.time()` around the full call (including any internal retries) —
into every `_CALLS` entry, folded by `provenance()` into
`_meta.llm.by_node[node].elapsed_s` on every future record, live or
replayed (replay is `0.0` by construction — no network call happens).
This is additive to `_meta.llm`, which has never had a strict schema
(`schema.json`'s `_meta.llm` is `{"type": "object"}` with no
`additionalProperties: false`), so no schema change was needed.

**`cost_model.py --measured <record.json>`**: reads a record's own
`_meta.llm.by_node` and reports the real per-node elapsed time and a
sequential total — clearly separated from Section 5's modelled figures
above it, with an explicit note on *why* they are never put in one ratio:
Section 5 prices a Claude deployment; a real run is Featherless
Qwen/Mistral. Different providers, different models — an "error" number
between them would falsely imply the model predicts this deployment's
speed.

**Found and fixed while testing this, not designed for and skipped**:
the first version silently showed `0.00` for any record written before
this instrumentation existed (`by_node` entries present, but no
`elapsed_s` key, defaulted through `.get(..., 0.0)`) — indistinguishable
from a genuinely-measured near-instant call. Tested against
`runs/21aug/D1_final_seed2.json` specifically because it's real, pre-D64
data, not just a happy-path fixture — caught the false zero immediately.
Fixed to check `"elapsed_s" in row` explicitly and print "no data" rather
than a number that looks measured but isn't. Also found and fixed, same
pass: `cost_model.py` never guarded stdout's encoding, unlike every other
executable script in this project — `python cost_model.py` crashes with
`UnicodeEncodeError` on the ₹ sign on a default Windows console. A
pre-existing gap this file happened to be the one to surface; fixed with
the same one-line guard `citation_matcher.py` etc. already carry.

Verified against three cases, not assumed: a real pre-D64 record (correctly
shows "no data, predates D64"), a replay-mode record (correctly shows
"0.0 by construction, not evidence of latency"), and a synthetic
same-shaped fixture with fake `elapsed_s` values (correctly renders the
real table) — the synthetic fixture was written to disk for this one test
and deleted immediately after, never committed, never presented as real
data anywhere.

## What is explicitly NOT claimed

**No real measured latency number is published anywhere in this
project as a result of this work.** `FEATHERLESS_API_KEY` was not set in
the environment this was built in (the same constraint D62's live
verification and D63's cache-seeding both hit) — every existing saved
record predates this instrumentation, so there is no real `elapsed_s`
data to report yet. The infrastructure is real and tested; a genuine
measured number requires someone with a live key to run
`run_pipeline.py` once, after which `cost_model.py --measured` on that
new record produces a real, honest, first data point. Stated as pending
here, exactly like D62's live check, rather than fabricated or silently
left unmentioned.
