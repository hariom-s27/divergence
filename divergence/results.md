# RESULTS — DIVERGENCE

### Step 30 deliverable. In progress — being filled in as the evaluation actually runs, not written after the fact.

---

## Pre-registration

**Ground truth frozen at commit `225ed20b6e697012d25d6063560907d96424a0de`**, 20 August 2026, `15:38:14+05:30`. `citations_expected[]`, `missing[]`, `elements`, and `methods_expected` for all 6 cases were complete at that commit and have not been edited since.

**Disclosure: `schema.json` was amended seven times after that commit**, across two commits the same day — three widening a field to allow a value the pipeline had always documented producing but the schema never actually permitted, two more of the same shape, and two additions for fields the resolver prompts have always asked for that `additionalProperties: false` was silently forbidding. None of the seven touch `cases/*/ground_truth.json` — the schema defines the output contract every arm is checked against equally, not what counts as a correct answer. Full account of all seven: [`DECISION-D46.md`](DECISION-D46.md).

---

## Step 1 complete: nodes 3/4 automated, arm C has real regimes now, for all 6 cases

`regimes[]` is no longer structurally empty. `node_resolver.py` automates the income-tax and GST resolvers (prompts 03/04), wired into `run_pipeline.py` by default. Ten real bugs found and fixed getting from "it runs" to "it produces a correct record" across two passes tonight — full account in [`DECISION-D45.md`](DECISION-D45.md), [`DECISION-D46.md`](DECISION-D46.md), [`DECISION-D47.md`](DECISION-D47.md), [`DECISION-D48.md`](DECISION-D48.md) and [`iteration-log.md`](step22drop/iteration-log.md).

All six cases now have complete, schema-valid, full-pipeline (arm C) records. Node 5 (adversarial) is still not automated — that's Step 5 of the plan, not this one.

**Read D48 before quoting C3's row below.** Finishing Step 1 also found that C3's input document never states its own core facts (amount, asset — only its title does), so C3 extracted zero fields and its gap/recall numbers reflect an almost-empty input, not the pipeline's judgment. The same finding shows C1, C2, C4, C5's ground truth expects a counterparty name and invoice number that were never written into any of those cases' input text either, capping their M1 ceiling below 100% regardless of extractor quality. D48 also documents a real bug in `eval/score.py` (M5 was silently scoring "0.0%, perfect" instead of "not measured" whenever a run had no `elements{}` data — fixed; every row below reflects the fix).

### Real numbers, all metrics, all 18 arm x case combinations that now exist

| Case | Arm | Model | M1 extract | M2 recall | M2 prec | M3 valid | M3 stale | M4 methods | M5 false abst |
|---|---|---|---|---|---|---|---|---|---|
| C1 | A | Qwen2.5-72B | 0.0% | — | 0.0% | 25.0% | 0.0% | 2/1 | — |
| C1 | B | Qwen2.5-72B | 0.0% | — | 0.0% | 25.0% | 0.0% | 2/1 | — |
| **C1** | **C** | **Qwen2.5-7B+72B** | **11.1%** | **—** | **0.0%** | **100.0%** | **0.0%** | **12/1** | **—** |
| C2 | A | Qwen2.5-72B | 9.1% | — | 0.0% | 50.0% | 0.0% | 2/1 | — |
| C2 | B | Qwen2.5-72B | 9.1% | — | 0.0% | 50.0% | 0.0% | 2/1 | — |
| **C2** | **C** | **Qwen2.5-7B+72B** | **9.1%** | **— (see note)** | **0.0%** | **100.0%** | **0.0%** | **12/1** | **—** |
| C3 | A | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 25.0% | 0.0% | 2/5 | — |
| C3 | B | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 20.0% | 0.0% | 2/5 | — |
| **C3** | **C** | **Qwen2.5-7B+72B** | **0.0%** | **50.0% (see D48)** | **14.3%** | **100.0%** | **0.0%** | **12/5** | **—** |
| C4 | A | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 50.0% | 0.0% | 2/10 | — |
| C4 | B | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% | 2/10 | — |
| **C4** | **C** | **Qwen2.5-7B+72B** | **22.2%** | **0.0%** | **0.0%** | **100.0%** | **0.0%** | **12/10** | **—** |
| C5 | A | Qwen2.5-72B | 0.0% | 100.0% | 100.0% | 50.0% | 0.0% | 2/2 | — |
| C5 | B | Qwen2.5-72B | 0.0% | 100.0% | 33.3% | 50.0% | 0.0% | 2/2 | — |
| **C5** | **C** | **Qwen2.5-7B+72B** | **10.0%** | **0.0%** | **0.0%** | **100.0%** | **0.0%** | **12/2** | **—** |
| D1 | A | Qwen2.5-72B | 0.0% | 75.0% | 100.0% | 60.0% | 0.0% | 2/12 | — |
| D1 | B | Qwen2.5-72B | 9.1% | 25.0% | 33.3% | 50.0% | 0.0% | 2/12 | — |
| **D1** | **C** | **Qwen2.5-7B+72B** | **18.2%** | **25.0%** | **100.0%** | **100.0%** | **0.0%** | **12/12** | **—** |

**Citation recall, mean by arm (`eval/m3b_citation_coverage.py`, the metric measuring completeness rather than mere validity): arm A 0.150, arm B 0.150, arm C 0.257 (n=5 for every arm now).** Arm C's sample is now the same size as A/B, for the first time.

### What each number actually means, read this before quoting one

- **M1 (extraction accuracy) is capped below 100% by construction for five of six cases, not just unfairly field-named.** D45 already flagged the field-name mismatch. D48 found something larger and upstream: C1, C2, C4, C5's ground truth expects a counterparty name and invoice number that were never written into that case's `case.md` at all — no extractor could ever reach them. C3 is missing even its primary facts (amount, asset) from the body text. D1 is the one case built with a full input paragraph, which is why it's also the only case where M1 numbers reflect a real attempt. Fixing field names (still-needed, still Step 2) will not close this gap on its own.
- **M5 (false abstention) is undefined on every row, and now correctly reported as such.** No prompt anywhere asks any arm to report the `elements{}` shape the scorer needs. `eval/score.py` previously computed `0.0%` (a false "perfect" score) for this exact situation — found and fixed under D48, see that file for the one-line bug.
- **All six cases now have arm-C rows.** M3 (citation validity) is 100% on every one of them — every citation the pipeline produced was real, current, and individually verified. M4 (method enumeration) is 100% or higher on every row for the same reason it was on D1/C2: ⚙ B's valuation lattice enumerates deterministically, so this reflects arithmetic, not resolver quality.
- **C2's M2 recall reads "—" for a real reason still not investigated.** C2's ground truth expects zero gaps — node 2 reported one anyway, so precision scores 0.0 rather than the undefined-recall case being neutral. Whether that is a real false positive or a legitimate finding ground truth under-specified is still open.
- **C3's M2 recall (50.0%) should not be read as "the gap detector did well on C3."** Read D48. C3's own case file explicitly predicts it should show *fewer* gaps than D1, as the test of whether the system reads facts rather than pattern-matches case shape. It showed more, because its input text does not restate its own facts, not because of a gap-detector defect.
- **Node 3's `valuation` block inside every non-D1 record is the canonical D1 case's valuation, not that case's own.** `node3_valuation.py` was built for one case and never parametrized (D47). It does not affect any of the five metrics above — neither resolver reads it — but the `valuation` field itself, if opened directly in any `runs/*.json` file other than D1's, should not be read as describing that case.

---

## Block A/B, 21 August: real input documents + the field-name fix, re-run on all 18

D48 found the root cause of M1's near-zero numbers: five case files never had a real input document, and ground truth's field names never matched what `01-extract.md` told the extractor to call them. Both are now fixed — see [`DECISION-D49.md`](DECISION-D49.md) for the document generator, and [`01-extract.md`](step22drop/prompts/01-extract.md) for the explicit 13-field contract added to the prompt. All 18 arm x case combinations were re-run against `step21drop/cases/<CASE>/input.md` instead of the old `case.md`. Saved to `runs/21aug/`, kept separate from the 20 Aug runs above rather than overwriting them.

**M1, before and after, arm C only:**

| Case | M1, 20 Aug (old `case.md`) | M1, 21 Aug (new `input.md` + field contract) |
|---|---|---|
| C1 | 11.1% | **100.0%** |
| C2 | 9.1% | **100.0%** |
| C3 | 0.0% | **100.0%** |
| C4 | 22.2% | **77.8%** |
| C5 | 10.0% | **90.0%** |
| D1 | 18.2% | **100.0%** |

Mean across the six cases moved from **11.8% to 94.6%**. That is the real effect of D48/D49's fix, not a scoring change — nothing about `eval/score.py`'s `m1_extraction()` changed between the two tables.

**Arms A and B's M1 did not move (still 0.0-9.1%), on the same new documents.** This is expected, not a bug: the field-name contract was added to `01-extract.md`, the pipeline's own node-1 prompt — not to `baseline-prompt.md` or `arm-b-cot.md`, which represent naive and token-matched-but-unengineered prompting on purpose. The honest reading is that giving a model complete input closes most of the gap by itself (C1/C2/D1 all reach 100% once the document is complete), but the field-name contract is doing real, separate work too — arms A/B had the same complete documents and stayed near zero, because nothing ever told them what to call each field.

**Full 21-Aug table, all 18 rows:**

| Case | Arm | Model | M1 extract | M2 recall | M2 prec | M3 valid | M3 stale | M4 methods | M5 false abst |
|---|---|---|---|---|---|---|---|---|---|
| C1 | A | Qwen2.5-72B | 0.0% | — | 0.0% | 50.0% | 0.0% | 2/1 | — |
| C1 | B | Qwen2.5-72B | 0.0% | — | 0.0% | 25.0% | 0.0% | 2/1 | — |
| **C1** | **C** | **Qwen2.5-7B+72B** | **100.0%** | **—** | **0.0%** | **100.0%** | **0.0%** | **1/1**\* | **—** |
| C2 | A | Qwen2.5-72B | 9.1% | — | 0.0% | 50.0% | 0.0% | 2/1 | — |
| C2 | B | Qwen2.5-72B | 9.1% | — | 0.0% | 50.0% | 0.0% | 2/1 | — |
| **C2** | **C** | **Qwen2.5-7B+72B** | **100.0%** | **—** | **0.0%** | **100.0%** | **0.0%** | **12/1** | **—** |
| C3 | A | Qwen2.5-72B | 0.0% | 100.0% | 66.7% | 50.0% | 0.0% | 2/5 | — |
| C3 | B | Qwen2.5-72B | 0.0% | 100.0% | 50.0% | 40.0% | 0.0% | 2/5 | — |
| **C3** | **C** | **Qwen2.5-7B+72B** | **100.0%** | **0.0%** | **0.0%** | **100.0%** | **0.0%** | **12/5** | **—** |
| C4 | A | Qwen2.5-72B | 0.0% | 100.0% | 66.7% | 50.0% | 0.0% | 2/10 | — |
| C4 | B | Qwen2.5-72B | 0.0% | 100.0% | 40.0% | 40.0% | 0.0% | 2/10 | — |
| **C4** | **C** | **Qwen2.5-7B+72B** | **77.8%** | **0.0%** | **0.0%** | **100.0%** | **0.0%** | **12/10** | **—** |
| C5 | A | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 50.0% | 0.0% | 2/2 | — |
| C5 | B | Qwen2.5-72B | 0.0% | 100.0% | 33.3% | 50.0% | 0.0% | 2/2 | — |
| **C5** | **C** | **Qwen2.5-7B+72B** | **90.0%** | **0.0%** | **0.0%** | **100.0%** | **0.0%** | **2/2**\* | **—** |
| D1 | A | Qwen2.5-72B | 0.0% | 25.0% | 66.7% | 50.0% | 0.0% | 2/12 | — |
| D1 | B | Qwen2.5-72B | 0.0% | 75.0% | 50.0% | 40.0% | 0.0% | 2/12 | — |
| **D1** | **C** | **Qwen2.5-7B+72B** | **100.0%** | **25.0%** | **50.0%** | **100.0%** | **0.0%** | **12/12** | **—** |

\* C1 and C5's M4 columns were updated after Block E1 (below) gave each its own real valuation instead of D1's borrowed one — see that section for why the count dropped and what it now means.

Citation recall, mean by arm, 21-Aug documents: arm A 0.100, arm B 0.100, arm C **0.307** (n=5, same sample size as before). Arm C improved; arms A/B moved slightly the other way, which reads as ordinary run-to-run variance now that temperature is not pinned to 0, not a regression worth chasing tonight.

### C3's own prediction, checked honestly, and it did not hold

C3's case file states plainly: *"the date choice is closed, the valuation method is still open. The system should report FEWER gaps here than in D1. If it reports the same number, it is not reading the facts."* With real documents, D1 reports 2 gaps (declaration of payment for services; independent verification of the counterparty's identity) and **C3 reports 3** (declaration of service payment; income tax deduction; valuation date) — more, not fewer. This is reported as a finding, not adjusted or explained away. Two honest possibilities, neither checked yet: gap detector is over-flagging a TDS/deduction question C3 does not actually have open, or C3's ground truth under-specifies what should already be closed. Worth investigating before the next results.md revision, not before this one goes out with the number as measured.

### Arm B failed to hold the schema on C3, on the first attempt

First run of arm B on C3 returned `'gst_export' is not one of ['income_tax', 'gst', 'fema', 'valuation']` — a real baseline failure, not repaired, recorded as `schema_valid: false` before being re-run for the table above. Kept here rather than only in the retried record: an unscaffolded baseline inventing its own regime label instead of the schema's enum is exactly the kind of failure the schema-conformance metric exists to catch.

### An infrastructure finding, not a methodology one

Four of six arm-B calls failed on the first attempt tonight with `Concurrency limit exceeded... Total needed: 8 units... plan limit: 4 units` — a genuine Featherless-side collision, not a code bug (confirmed by reading the recorded `error` field directly rather than guessing). Root cause: a background pipeline run was stopped mid-flight shortly before, and the server-side concurrency slot did not appear to release as fast as the local process did. Retried individually a few minutes later and all four succeeded cleanly. No code changed for this — the fix is procedural: don't stop a background run and immediately start another 72B call against the same key.

---

## Block D, 21 August: node 5 ran for the first time

`05-adversarial.md`'s own header said this node had never run — everything credited to adversarial review before tonight was found by a human reading adversarially. `node5_adversarial.py` now exists (built the same way `node_resolver.py` was — scoped prompt loading, its own output-shape validation, provenance recorded to `_meta`), wired into `run_pipeline.py` behind `--node5`, off by default so every prior record stays reproducible. Full account: [`DECISION-D50.md`](DECISION-D50.md).

**First run, on D1's real, already-published record, caught a genuine defect no existing metric catches.** D1's `income_tax_on_receipt` conclusion asserts the valuation date is the date of receipt (28 June) in one sentence and then, two sentences later, says the rate is taken from "the last day of the tax year (2026-03-31)" — checked directly against `ITR2026-RULE-206.md`: that date rule belongs to row 3 of the table, scoped to house-property/business/other-source income, not to a s.115BBH virtual-digital-asset receipt. A real citation (`Rule 206` is current and correctly cited, which is why M3 scored it valid) attached to the wrong row of a multi-row table. Node 5 caught it because that is literally checklist item 2, scope reach.

### The ablation — 4 planted defects, D1's real conclusions as the base

`make_ablation_variants.py` plants each defect (by hand, not by model) into a **copy** of D1's real `regimes[]`; `runs/21aug/D1_pipeline.json` itself is untouched.

| Variant | Planted defect | Checklist item | Result |
|---|---|---|---|
| D1-a | cites Rule 11UA for FY 2026-27 | 1, operative status | **CAUGHT** |
| D1-b | applies Rule 57 row 7 to a s.92 receipt | 2, scope reach | **NOT CAUGHT** |
| D1-c | asserts GST despite FIRC/verification missing | 3, missing document | **CAUGHT** |
| D1-d | values USDC at the USDT print, proxy unstated | 4, correct instrument | **CAUGHT** |

**3 of 4.** D1-b's miss is reported at the same weight as the three catches — no retry, no prompt change attempted before writing this down, per `05-adversarial.md`'s own pre-registered instruction to report the ablation "whichever way it comes out."

### A calibration finding, visible only across all five runs together

`checked_and_survived` was empty in every one of the five node-5 runs tonight (the real D1 record plus all four variants) — every conclusion it was given, it attacked, every attack landed. `05-adversarial.md` names this exact pattern as a warning sign in its own text, written before any run existed: *"a checker that breaks everything is as useless as one that breaks nothing."* Read plainly: node 5 cannot yet tell a conclusion with a real defect apart from one that is merely, correctly, hedged (every D1-family conclusion here was already `insufficient_evidence` before node 5 ever saw it, forced there by `gap_enforcer.py`). This is the most likely explanation for D1-b's miss too — several generic attacks were available and easy to reissue instead. Not re-tuned tonight; doing so after seeing the miss would be adjusting the test to fit the result. Full reasoning in D50.

---

## Block E1, 21 August: C5 gets its own real valuation, C1 gets the false-abstention proof

D47 disclosed that every non-D1 record's `valuation` block was silently D1's own. `node3_valuation.py` now takes `--case`/`--out` instead of being hardcoded to D1; full account in [`DECISION-D51.md`](DECISION-D51.md).

**C5** shares D1's exact settlement weekend (28 June 2026), so the SBI sheets already on disk (25 June, 29 June) answer it directly — no new data collected. Its record now carries its own **2-method, Rs 150 / 0.0532% spread** lattice (the genuine date-choice-only dispute it actually has), not D1's borrowed 12-method, Rs 47,868 / 10.19% one.

**C1** has no currency conversion at all (a domestic INR invoice paid in INR) — no lattice to build, one determinate figure. Representing that honestly needed a real schema change: `valuation.methods`'s `minItems: 2` (*"a single method is a failure state"*) assumed every case has a dispute. Amended to `minItems: 1`, distinguishing a real failure (nonzero spread, one method found where more should exist) from the true state (`spread.inr == 0`, nothing to enumerate) — the ninth-plus post-freeze schema amendment, same family as D46's seven, output contract only, `ground_truth.json` untouched. C1's record now shows exactly one method, zero spread — the record saying "here there is one answer," which is what makes D1's twelve believable.

**Both now match ground truth's own `methods_expected` exactly** (C1: 1/1, C5: 2/2) — the pre-registered ground truth had already anticipated this shape; the pipeline's output simply hadn't matched it until tonight.

**C2, C3, C4 are not fixed.** C2 is genuinely determinate too (a Wednesday wire, a day SBI did publish a rate) but building its real single-value proof needs the actual 17 June 2026 SBI rate, which isn't in the corpus — typing a plausible number in rather than collecting it would be the exact fabrication this project's valuation lattice exists to refuse. Left disclosed, not faked.

---

## Still open before this table is the final one

- Three seeds on D1, all arms (Step 4) — only possible now that temperature is `default`, not `0`
- **Why C3 reports more gaps than D1, not fewer** — C3's own case file predicts the opposite; see above. Not yet checked whether this is a gap-detector over-flag or an under-specified ground truth.
- **The real defect node 5 found in D1's own record (D50)** — Rule 206's "last day of the tax year" row misapplied to a receipt-date valuation. Not yet fixed in `node_resolver.py`'s prompt; D1's published record still carries it, disclosed rather than quietly patched.
- **Node 5's calibration** (D50) — currently attacks every conclusion it sees; `checked_and_survived` has never been non-empty. Worth investigating before the node's output is used for anything beyond disclosure.
- `node3_valuation.py` generalized for C2, C3, C4 (D47/D51 — C1 and C5 are done) — needs SBI/FBIL sheet data for their specific dates that was never collected
- M5's contract gap — see `README.md`'s Honest Limitations
- Prior-art check (Block C) — OBJ-1 (does software already solve this) done, see [`prior-art/OBJ-1.md`](prior-art/OBJ-1.md); DEMAND evidence (do real people hit this) not yet done
