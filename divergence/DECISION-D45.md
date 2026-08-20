# D45 — Steps 27/29/31: the first real runs, and five bugs only running anything ever found

**Date:** 20 August 2026
**Builds on D42–D44 (provider, model selection, repo/pre-registration hygiene).**
D45 is what happened the first time any of it was actually run end to end.

## Why this is one decision, not five bug-fix notes

Every fix below was found the same way: **run the real thing, don't reason
about whether it would work.** Nodes 1–5, `run_arms.py`, and `eval/score.py`
had each been built and unit-tested in isolation. Not one of them had been
run as a full chain, against a real model, before Step 27. Five real,
distinct bugs surfaced in the first two hours of actually doing that — none
of them visible from reading the code, all of them visible in ten seconds
of watching it run. That is the argument for Steps 27–31 existing at all,
and it is worth stating as a decision, not just a log entry.

## The five, in one table

| # | Where | What broke | Root cause | Fix |
|---|---|---|---|---|
| 1 | `llm_call.py` | Protocol violation | `temperature=0` on every call, contradicting `evaluation-design.md`'s own "default, not zero" (D39) | `DIVERGENCE_TEMPERATURE` env var, explicit per run, recorded in `provenance()` |
| 2 | `schema.json` | D1's first real run: `INVALID` | `date_choice.chosen` required a string; `node3_valuation.py` sets it `null` **on purpose** (R99 — an unresolved date choice) | `"chosen": ["string", "null"]` |
| 3 | `node1_extract.py` | C2's first real run: `INVALID`, 3 steps downstream of the actual cause | The 7B model nested `extraction_notes` inside `facts{}} — valid JSON, wrong shape, invisible to `call_json()`'s retry logic | Node validates its own output shape immediately; a contract violation now fails loud, at the node that caused it |
| 4 | `run_arms.py` | Arm A's first run: 0/6 schema-valid | The model was handed the raw Draft-2020-12 `schema.json` and echoed the schema *definition* back instead of a data instance | Replaced with `SCHEMA_EXAMPLE` — a filled example, the same style prompts 01–05 already use successfully |
| 5 | `run_arms.py` | Arm B's first run: D1/C2 produced zero output tokens | `token_budget()` capped a single completion at the *sum* of two much smaller separate node calls | Floor the match at `DEFAULT_MAX_TOKENS`, never below it |

Two more were found running the actual scorers, not the pipeline, and they
don't fit the table above because nothing in them was "broken" so much as
"never checked against a real record":

- `schema.json`'s `extracted_field.value` never allowed `boolean`, though
  every case's `ground_truth.json` already uses boolean facts
  (`"bank_involved": {"value": false}`). Fixed the same way as #2.
- `citation_matcher.py` verifies a bare `"Section 2(111)"` (no Act name)
  against the wrong corpus file (`FEMA-2n.md`) — weak instrument
  disambiguation on an unqualified citation. Not fixed in the matcher;
  worked around by citing the fully-qualified form in ground truth. Live
  hazard for any future resolver output using the short form.

## What running it also proved, that reading it couldn't

**Arm C's citation recall reads 0.000, and that is not a finding about the
pipeline.** `regimes[]` is empty on every arm-C record — nodes 3/4/5 are
still hand-run and no `--regimes` file has been passed yet. Arm C has not
been given the chance to cite anything. Reporting that number without this
sentence would be exactly the misleading-baseline-comparison failure
`evaluation-design.md` §2 exists to prevent — aimed at ourselves this time,
not at arm A.

**M1 (extraction accuracy) cannot be scored yet, for any arm.**
`ground_truth.json`'s field names (`asset`, `settlement_datetime_ist`,
`counterparty_declared`...) don't match what any extractor — pipeline,
arm A, or arm B — actually produces (`asset_currency`,
`settlement_datetime`, `counterparty_name`...). `01-extract.md` never pins
down exact field names. Two live fixes, deliberately not chosen here
because it's a real design decision: rewrite the prompt to match the
pre-registered ground truth (same move as fix #4 above), or add fuzzy field
matching to the scorer — the second option is the same shape of mistake
`eval/score.py`'s own v1.5 already made once on gap-matching.

**M5 (false abstention) — "the metric that earns trust" — is undefined on
every single row scored so far.** `elements{}` is a ground-truth-only
concept; no prompt anywhere asks any arm to report it in a scoreable shape.

## What this changes about how the remaining steps should run

**Never trust an untested integration point, however carefully each side
was built.** Nodes 1–5 were each individually correct against their own
unit tests. Two of the five bugs above (`date_choice.chosen`,
`extracted_field.value`) were schema gaps that had existed since 6 August
and simply never been exercised by a real record. The other three
(temperature, raw-schema confound, token-match floor) only exist at the
seam between two components that had never actually talked to each other.
**Steps 27–31 exist specifically to find seam bugs unit tests cannot see —
and did, five times, in one session.**

`eval/normalize_runs.py` — the adapter connecting `run_pipeline.py` and
`run_arms.py`'s real output to `score.py`'s expected input — is the same
kind of seam, built the same way: additive, `score.py` itself untouched,
run against real files before being trusted.
