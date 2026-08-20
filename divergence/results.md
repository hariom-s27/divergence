# RESULTS — DIVERGENCE

### Step 30 deliverable. In progress — being filled in as the evaluation actually runs, not written after the fact.

---

## Pre-registration

**Ground truth frozen at commit `225ed20b6e697012d25d6063560907d96424a0de`**, 20 August 2026, `15:38:14+05:30`. `citations_expected[]`, `missing[]`, `elements`, and `methods_expected` for all 6 cases were complete at that commit and have not been edited since.

**Disclosure: `schema.json` was amended three times after that commit**, in commit `1b1e9d3` the same day. `date_choice.chosen` was widened to allow `null` (matching output `node3_valuation.py` had documented producing since before the freeze, just never exercised against the schema until a real run happened). `extracted_field.value` was widened to allow `boolean` (every case's `ground_truth.json` already used one; the schema had simply never allowed it). The `_meta` object was added, to carry model provenance that did not exist as a concept at freeze time. None of the three touch `cases/*/ground_truth.json` — the schema defines the output contract every arm is checked against equally, not what counts as a correct answer. Full account: [`DECISION-D46.md`](DECISION-D46.md).

---

## What's actually measured so far

The first real numbers, from Steps 27, 29 and 31, are in [`README.md`](../README.md#first-real-numbers-from-steps-27-29-and-31-20-aug) and the full detail with every bug found getting there is in [`DECISION-D45.md`](DECISION-D45.md) and [`iteration-log.md`](step22drop/iteration-log.md).

**This file is not the final results table.** Arm C's `regimes[]` is still empty on every record — nodes 3/4/5 have not been wired into an automated run yet, so arm C has not had the chance to produce a citation, and its current numbers in the interim table are not a comparison, they are an incomplete run. M1 (extraction accuracy) and M5 (false abstention) are not scoreable yet either — see the limitations in `README.md`. This file gets its real content once those are addressed.
