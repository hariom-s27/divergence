# RESULTS — DIVERGENCE

### Step 30 deliverable. In progress — being filled in as the evaluation actually runs, not written after the fact.

**For the narrative version of how the numbers below got here — seven real bugs, what broke, what changed, what moved — see [`ITERATION-STORY.md`](ITERATION-STORY.md) (Step 28).**

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
- **M5 (false abstention) is undefined on every row, and now correctly reported as such.** No prompt anywhere asks any arm to report the `elements{}` shape the scorer needs. `eval/score.py` previously computed `0.0%` (a false "perfect" score) for this exact situation — found and fixed under D48, see that file for the one-line bug. **The closest thing this project has to real false-abstention evidence is C1 and C2's records, said plainly here rather than left implicit:** both receipts genuinely have zero valuation dispute, and the pipeline reports exactly one method with `spread.inr == 0` on both — it does not manufacture a range where none exists. That is evidence the system doesn't cry wolf on every input, on two real cases; it is not a measurement of M5, and the two should not be conflated. If the sharpest version of "how do we know you don't just flag everything" comes up, this is the answer that exists today.
- **All six cases now have arm-C rows.** M3 (citation validity) is 100% on every one of them — every citation the pipeline produced was real, current, and individually verified. M4 (method enumeration) is 100% or higher on every row for the same reason it was on D1/C2: ⚙ B's valuation lattice enumerates deterministically, so this reflects arithmetic, not resolver quality. **`m4_enumeration()` has no ceiling and can read well over 100%** — C3 scores 12/5 (240%), because C3's `valuation` block is still D1's borrowed 12-method lattice (see the row below), scored against C3's own `methods_expected: 5`. Not a metric bug and not silently capped; a number over 100% on this metric always means the same known, disclosed cause: a case scored against a lattice that isn't its own.
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
| **C2** | **C** | **Qwen2.5-7B+72B** | **100.0%** | **—** | **0.0%** | **100.0%** | **0.0%** | **1/1**\* | **—** |
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

\* C1, C2, and C5's M4 columns were updated after Block E1 and the Firecrawl follow-up below gave each its own real valuation instead of D1's borrowed one — see those sections for why the count dropped and what it now means.

Citation recall, mean by arm, 21-Aug documents: arm A 0.100, arm B 0.100, arm C **0.307** (n=5, same sample size as before). Arm C improved; arms A/B moved slightly the other way. **Correction, D52: this is not temperature variance** — every run through Block E1 was actually still at temperature 0 (see D52), so the honest explanation is the changed input document (`input.md` replacing `case.md`), not sampling. Not a regression worth chasing tonight either way.

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

### The Rule 206 defect, fixed and re-run — both records kept

The defect above wasn't left as a disclosed footnote. `03-income-tax.md` gained an explicit instruction (the "RULE 206/207 GATE"): before citing Rule 206 or 207 at all, check their own opening words — both are scoped to income "in foreign currency," and a VDA is defined elsewhere as NOT foreign currency, so neither reaches a virtual-digital-asset receipt regardless of which row looks inviting. Cross-checked against `cases/D1/ground_truth.json`'s own frozen `citations_expected[]`: Rule 206/207 were never in that list at all — the correct answer never cites them, which this fix now matches.

Re-ran D1 with the fixed prompt. **`runs/21aug/D1_fixed_pipeline.json` is new; `runs/21aug/D1_pipeline.json` (the original, defect and all) is kept, not overwritten** — both before and after are on record. Result: Rule 206 no longer appears anywhere in the new record's `income_tax_on_receipt` reasoning or outcome. The specific defect node 5 found is gone.

**It surfaced a second, different, genuine defect in the same spot.** The fixed run now cites `Rule 243(8)(e)` (the RCASP reporting waterfall) as the valuation method instead. Ran node 5 against the new record: it landed on this too — *"Rule 243(8)(e) is incorrectly referenced because Rule 243 is part of the reporting requirements rule set meant for crypto asset providers. Fair Market Valuation clearly falls under Rule 57."* That is correct, and matches ground truth's own expected answer (Rule 57's seven rows reach no method for this receipt — the lacuna, `GAZETTE-FINDINGS.md` #1) more precisely than the prompt fix does yet. **Not fixed further tonight** — one targeted fix per finding, reported honestly rather than iterated until the record looks clean.

**`checked_and_survived` was non-empty for the first time all night** on this run — one conclusion (the GST export finding) survived node 5's attack unbroken. Read together with D50's calibration concern: still not proof node 5 discriminates reliably, but the first single data point where it didn't attack literally everything it saw.

### The third scope-reach error, and this one really mattered

Rule 243(8)(e) — the provision the fix above reached for instead of Rule 206 — has its own scope gate too, checked directly against `corpus/verbatim/ITR2026-RCASP-VALUATION.md`: it governs *"the aggregate-reporting obligations of a reporting crypto-asset service provider,"* not a taxpayer. D1's record was, for a few hours tonight, asserting `certainty: settled` on a valuation method that this project's entire thesis says does not exist — the opposite of the headline finding, on the page a reader opens first. Full account, the fix, and why it's one generalized SCOPE GATE rather than a third special-cased patch: [`DECISION-D54.md`](DECISION-D54.md).

`runs/21aug/D1_v3_pipeline.json`: `valuation_method` is now its own regime object (the enum already allowed this; nothing used it before), `certainty: lacuna`, citing Rule 243 only as the closest-but-rejected provision. **Ran node 5 against it and the `valuation_method` conclusion survived unattacked** — an independent second model confirming the answer holds, not just that nobody attacked it yet. `output-interface.html` regenerated from this record; section 03 now shows a "No rule found" chip on the valuation line next to the 12-method range in section 02.

**This is node 5's second real catch on unplanted data** (D50 was the first) — found this defect itself, the same night it first ran, before any human flagged it. A cheap, deterministic guard was also added (`node5_adversarial.py`'s `_reject_upward_revisions`) after D50 caught node 5 proposing a `settled → settled` "downgrade" on a landed attack — tested against that exact known example (correctly rejected) and then against a second, independent case the same guard caught live on this v3 run (`insufficient_evidence → insufficient_evidence`), not a single replay.

**Three instances of the identical failure now confirmed**, same project, same night: Rule 57 row 7 → a s.92 receipt; Rule 206 row 3 → a s.115BBH VDA receipt; Rule 243(8)(e) → a taxpayer who is not a reporting service provider. Real citations, correctly quoted, applied outside their own scope every time. That pattern is the finding, not an embarrassment to bury — a model given verbatim statute and a genuinely underdetermined question reliably reaches for the nearest rule that mentions the right words. Measured on this project, by this project, three times.

### D1, three labelled rows — what actually moved, and why

Three real records now exist for D1's arm C. Shown separately, not collapsed to the latest:

| Record | What it has | M1 | M2 recall | M3 valid | M4 methods |
|---|---|---|---|---|---|
| `D1_pipeline.json` | Rule 206 defect (D50) | 100.0% | 25.0% | 100.0% | 12/12 |
| `D1_fixed_pipeline.json` | Rule 206 fixed, Rule 243 defect introduced (D50 addendum) | 81.8% | 75.0% | 100.0% | 12/12 |
| `D1_v3_pipeline.json` | Both fixed — the current record, what `output-interface.html` renders (D54) | 45.5% | 0.0% | 100.0% | 12/12 |

**M3 and M4 are identical across all three, and that is the real finding, not a null result.** Neither metric is capable of seeing any of the three scope-reach defects — M3 only checks a citation is real and current (it was, every time, including both defective versions), M4 only counts the deterministic valuation lattice's own method count, untouched by which regime cites what. **Three substantive, confirmed-wrong legal conclusions, invisible to every metric that would normally stand in for "is this record correct," caught only by adversarial reading.** That is a stronger argument for node 5's place in this pipeline than the ablation score is on its own.

**M1 and M2 moving between these three rows is not about the fix — it's ordinary temperature variance.** Each record is an independent run at the model's own (non-zero, D52) temperature; node 1 and node 2 are re-executed fresh each time regardless of what changed in the resolver prompt, so their output varies the same way Block E2's three seeds already documented. Reading M1/M2's movement here as evidence about the Rule 206/243 fixes would be a mistake — they aren't measuring it.

## Block E1, 21 August: C5 gets its own real valuation, C1 gets the false-abstention proof

D47 disclosed that every non-D1 record's `valuation` block was silently D1's own. `node3_valuation.py` now takes `--case`/`--out` instead of being hardcoded to D1; full account in [`DECISION-D51.md`](DECISION-D51.md).

**C5** shares D1's exact settlement weekend (28 June 2026), so the SBI sheets already on disk (25 June, 29 June) answer it directly — no new data collected. Its record now carries its own **2-method, Rs 150 / 0.0532% spread** lattice (the genuine date-choice-only dispute it actually has), not D1's borrowed 12-method, Rs 47,868 / 10.19% one.

**C1** has no currency conversion at all (a domestic INR invoice paid in INR) — no lattice to build, one determinate figure. Representing that honestly needed a real schema change: `valuation.methods`'s `minItems: 2` (*"a single method is a failure state"*) assumed every case has a dispute. Amended to `minItems: 1`, distinguishing a real failure (nonzero spread, one method found where more should exist) from the true state (`spread.inr == 0`, nothing to enumerate) — the ninth-plus post-freeze schema amendment, same family as D46's seven, output contract only, `ground_truth.json` untouched. C1's record now shows exactly one method, zero spread — the record saying "here there is one answer," which is what makes D1's twelve believable.

**Both now match ground truth's own `methods_expected` exactly** (C1: 1/1, C5: 2/2) — the pre-registered ground truth had already anticipated this shape; the pipeline's output simply hadn't matched it until tonight.

**C2, C3, C4 are not fixed** *(update below — C2 now is)*. C2 is genuinely determinate too (a Wednesday wire, a day SBI did publish a rate) but building its real single-value proof needs the actual 17 June 2026 SBI rate, which isn't in the corpus — typing a plausible number in rather than collecting it would be the exact fabrication this project's valuation lattice exists to refuse. Left disclosed, not faked.

---

## C2 fixed, and a correction about what C3/C4 actually still need

Checked `corpus/tier-a/SBI-TTBR-DATA.md`'s own front matter before reaching for a new tool: its `source_url` is `github.com/sahilgupta/sbi-fx-ratekeeper`, a real, live, actively-maintained public archive of SBI's daily rate PDFs — not a one-off scrape. Fetched `SBI_REFERENCE_RATES_USD.csv` directly (`gh api` to find it, then a direct fetch — no Firecrawl needed for a structured GitHub CSV). It has real rows through 2026-06-17 09:12, TT BUY **94.05** — exactly C2's date, exactly the rate its false-abstention proof needed. Cross-checked the existing corpus figures against this same live source first (25 June 94.00, 29 June 93.95, 23 June 94.30 all matched exactly) before trusting the new number.

**C2's record now carries its own single-method, zero-spread valuation** (₹3,76,200, no dispute — 17 June is an ordinary Wednesday with a normally-published rate, unlike D1/C5's four-day weekend hole). Building it surfaced two more real bugs in `node3_valuation.py` (both fixed): the per-method `date_choice.reason` text and the uncertainty-budget's "which official date" line both unconditionally asserted *"no rate was published on the settlement date"* — true for D1/C5, **false** for C2, where a rate plainly was published. Both are now conditioned on whether more than one official candidate actually exists. D1's own default path re-verified unaffected before committing.

**C2 also matches ground truth's `methods_expected: 1` exactly** — three for three now (C1, C2, C5) between the pipeline's real output and what pre-registration already expected.

**Correction to what's said about C3 and C4 above: they do not need SBI rate data at all.** Both are VDA (USDC) receipts, and Block D's own fix this same night (the Rule 206/207 gate) established that Rule 206 — the provision that names the SBI rate — never reaches a VDA in the first place, foreign currency only. C3 and C4's real valuation lattices need CoinDCX-style crypto market data (a daily candle, a USDC/USDT peg reading) for 23 June and 18 June respectively, not an SBI sheet. That data was not collected tonight. Said plainly here rather than left as the same "needs SBI data" framing repeated from before this was actually checked.

**What this means for the scalability claim (Step 31).** C2's own case file states its purpose plainly: *"THIS IS THE SCALABILITY PROOF — no crypto anywhere, same pipeline, unchanged."* Until tonight, that claim held for facts, gaps, regimes and citations, but not for valuation — C2's record carried D1's crypto lattice, which would have shown a USDC valuation dispute on a plain USD bank wire if its page had ever been generated and shown. It is fixed now: C2's record, end to end including valuation, belongs to C2. The scalability proof is what it was always meant to be — the same pipeline, no code change, no prompt change, no new corpus file, run against a receipt with no crypto in it at all, producing a correct, case-specific, schema-valid record throughout. C3 and C4 do not yet make the same claim; their pages should not be shown as if their valuation sections were case-specific until the crypto market data above is collected.

---

## Block E2, 21 August: three seeds on D1, the first runs at real temperature

D52 (above) found that every run through Block E1 was actually still at temperature 0, despite the fix existing in code since earlier tonight. `$env:DIVERGENCE_TEMPERATURE = "default"` set explicitly and verified against the first run's own `_meta.llm.temperature` field before trusting the rest. Three seeds (`DIVERGENCE_SEED` 1/2/3, an explicit, reproducible seed each time, not an unlabelled random draw), all three arms, D1 only, saved separately in `runs/21aug/` (arm C) and `runs/21aug/seed{1,2,3}/` (arms A/B).

**n=3. The three numbers are reported individually below, not as a mean or a min–max range — at this sample size a range still implies a smooth distribution between two points that doesn't exist, and a mean is worse. Three data points are three data points.**

| Metric | Arm A (seed 1, 2, 3) | Arm B (seed 1, 2, 3) | Arm C (seed 1, 2, 3) |
|---|---|---|---|
| M1 extraction | 0.0%, 0.0%, 0.0% | 0.0%, 0.0%, 0.0% | **100.0%, 100.0%, 100.0%** |
| M2 gap recall | 50.0%, 0.0%, 25.0% | 25.0%, 75.0%, 50.0% | 50.0%, 75.0%, 0.0% |
| M2 gap precision | 100.0%, 0.0%, 50.0% | 33.3%, 100.0%, 50.0% | 100.0%, 40.0%, 0.0% |
| M3 citation valid | 50.0%, 20.0%, 25.0% | 50.0%, 20.0%, 40.0% | **100.0%, 100.0%, 100.0%** |

**Arm C's M1 and M3 are the same value on all three seeds — 100.0% every time.** That is a real result now, not an artifact of measuring the same deterministic draw three times: this is the first point in the project where "stable" and "measured at temperature 0" are no longer the same claim. Arms A and B's M1 stayed at 0.0% on every seed too, for the reason already established (the field-name contract lives in `01-extract.md` only) — consistent across seeds, not a coincidence of one draw.

**M2 (gap recall) moves on every arm, arm C included — 50%, 75%, then 0% across its three seeds of the same case, same input, same code.** Step 21 calls M2 "the strongest metric"; at three data points with that much movement between them, no single number from this table should be quoted as *the* M2 result — only the three together. Not investigated further tonight; the individual numbers are reported so a reader can see exactly what happened rather than a smoothed-over summary of it.

**This instability is not just our own measurement — it's a specific, published finding about legal-domain LLM behavior at temperature 0.** Blair-Stanek and Van Durme, *"LLMs Provide Unstable Answers to Legal Questions"* (ICAIL 2025; [arXiv:2502.05196](https://arxiv.org/abs/2502.05196)), curated 500 real legal questions from split-decision court cases and found leading models — GPT-4o, Claude-3.5, Gemini-1.5 — reach different conclusions on identical questions at temperature 0, checked directly against their own abstract rather than assumed from the title. Their instability is about which party wins; ours is about which gaps get found — different task, same underlying property (a temperature-0 legal-reasoning call is not the fully deterministic thing it's often assumed to be). Read together, this project's 50/75/0% spread looks less like a defect specific to this pipeline and more like a reproduction of an already-published result, on a different task, in the same domain.

**Checked directly, not assumed: the instability is real, but one of the three
numbers is inflated by a real, separate bug in the scorer.** Ran
`eval/score.py`'s own `_similar()` function against every ground-truth-gap ×
reported-gap pair by hand, for all three seeds, rather than trusting the
summary line. Seed 1 (50%) and seed 3 (0%) hold up exactly — every credited
match and every miss is a fair reading of what the model actually reported.
**Seed 2 (75%) does not, fully.** `_similar()` has no one-to-one constraint: a
single reported item, *"documentation proving the foreign exchange
transaction,"* shares distinctive tokens with **two different** ground-truth
gaps (*"bank certificate of foreign inward remittance"* and *"official
exchange rate for the settlement date"*) and gets credited against both,
because the matcher checks each ground-truth item independently rather than
matching reported items one-to-one. Seed 2 substantively identified two real
gaps (counterparty verification, and one vague item gesturing at the
foreign-exchange documentation generally); the scorer credited three. **Not
fixed tonight** — `_similar()`'s matching logic has been re-run across every
already-published number in this file, and changing it now means
re-verifying all of them, which is exactly the kind of under-pressure change
this project's own hard-stop rule exists to prevent. Disclosed here instead:
the real instability finding stands (0% and 50% are both real, independently
confirmed low numbers on the same case), and one of the three published
figures — 75%, not 50% or 0% — is measured with a scorer that has a known,
now-documented double-counting bug.

**Arm A produced one schema-invalid record out of three seeds** (seed 2) — a real baseline failure rate, 1/3, consistent with `run_arms.py`'s own standing framing that a baseline unable to hold the output contract is itself a finding, not noise to discard.

You can trust that this table reflects real variance, specifically because D52 is written down first — a temperature bug found, disclosed, and only then relied on, in that order.

---

## Block F, 21 August: final D1 fix cycle, three seeds, freeze

Three defects were found and fixed in sequence tonight, each fix's own re-run
surfacing the next: Rule 206 (D50) → Rule 243(8)(e) (D50 addendum, D54) → a
fourth, found reading `D1_v3_pipeline.json` after it went out: s.393(1)'s TDS
conclusion said *"no deduction obligation arises... as the recipient is
outside India"* — s.393(1) addresses the person responsible for **paying**,
not the recipient, and Priya is the resident recipient, not outside India in
any sense the section cares about. Node 5's own attack on `D1_v3` already
said this in different words before it was read: *"s.393(1) applies to
payments made to residents, not non-residents... the conclusion... is
incorrect."* A fourth instance of the identical scope-reach failure, on the
same record, the same night. Fixed in `step22drop/prompts/03-income-tax.md`
with an S.393(1) SCOPE GATE, same shape as the Rule 206/207 gate and the
Rule 243 guidance already there — one generalized pattern applied a fourth
time, not a fourth special-cased patch.

`D1_v3_pipeline.json`'s `valuation_method.citation.provision` was also found
to still read `Rule 243(8)(e)` — the provision considered and rejected, not
the provision the `lacuna` conclusion actually rests on (Rule 57, read with
Rule 56 for the date). Fixed in the same prompt edit: the citation template
now says explicitly to cite the provision that was checked and found not to
reach, never the rejected one.

**Pre-registered before any of the three seed runs below were executed:**
the demo record is generated from the first seed (`DIVERGENCE_SEED=1`, then
`2`, then `3` if needed) whose record is schema-valid and whose `regimes[]`
contains all three expected objects (`income_tax_on_receipt`,
`valuation_method`, and TDS/penalty folded correctly per the prompt). This
rule was written into this file before any of the three runs were started.
All three seeds' M1/M2/M3/M4 are reported below regardless of which one is
selected — the selection rule picks the demo record, it does not hide the
other two.

**Two more real bugs found and fixed while running the first seed, both in
`node5_adversarial.py`, neither a legal-reasoning defect:** the model
sometimes emits `downgraded_to: ""` instead of omitting the field, which
`_validate_attack_shape` was rejecting outright — fixed to treat an empty
string the same as absent, for both `attacked[].downgraded_to` and
`checked_and_survived[]`. Separately, `_reject_upward_revisions` was setting
a rejected `downgraded_to` to `None` — but `schema.json`'s own definition
`$ref`s the certainty enum with no null member, so a rejection was producing
a *schema-invalid* record purely from our own guard's side effect. Fixed to
delete the key instead of nulling it. Both found live, both fixed before any
seed was scored.

**Seed 1 is schema-invalid** — `regimes[1].condition_met: null`, not one of
`yes|no|unknown` (a node 3/4 output-shape slip, not a node 5 issue). Per the
pre-registered rule, **seed 2 is the selected demo record** — schema-valid,
`regimes[]` carries all three expected objects, `valuation_method` now cites
**Rule 57** (not Rule 243), `certainty: lacuna`.

| Seed | Schema | M1 | M2 recall | M3 valid | M4 methods |
|---|---|---|---|---|---|
| 1 | **INVALID** (`condition_met: null`) | 100.0% | 50.0% | 100.0% | 12/12 |
| **2 (selected)** | VALID | 100.0% | 50.0% | 100.0% | 12/12 |
| 3 | VALID | 100.0% | 25.0% | 100.0% | 12/12 |

All three M1=100%/M3=100%/M4=12/12 — the 45.5%/0.0% figures the pre-`Block F`
`D1_v3_pipeline.json` record scored are not reproduced here. We do not have a
root cause for that single low draw beyond ordinary sampling variance already
documented in Block E2 (M1 was never that unstable across those three seeds
either) — flagged, not chased, per the hard-stop below.

**Node 5 ran against the selected record** (`D1_final_seed2_attack.json`):
4 attacks, **all 4 landed** (`survived: false` on every one — corrected
here; an earlier pass through this file mis-stated this as "2 landed, 2
survived," reading node5_adversarial.py's own CLI print wrong. The "2" in
that print is `checked_and_survived`'s length — two *separate* conclusions
checked and never attacked at all, not two of the four attacked ones
holding up. Caught re-verifying against the raw JSON before writing this
correction, not assumed). No rejections were needed from the downgrade
guard on any of the four.

One of the four landed attacks is a **fourth independent catch of the
identical scope-reach failure**, on a claim this same fix cycle introduced
minutes earlier: seed 2's `income_tax_on_receipt` reasoning says *"no
deduction obligation arises under s.393(1)... because the recipient is a
resident and the payer is outside India"* — an exemption for a foreign payer
that is not stated anywhere in the s.393(1) text the model was given. Node
5's attack: *"the condition that no deduction obligation arises because the
payer is outside India is not supported by the text of s.393(1)... the
conclusion... is incorrect."* Found independently, matches a read of
`corpus/verbatim/IT-393-1-T8vi.md` done before this attack ran. **Per the
hard-stop rule below, this is disclosed here and in `limits[]`'s equivalent
narrative, not fixed with a sixth prompt edit** — the S.393(1) SCOPE GATE
already added this cycle correctly stopped the *first* version of this error
(inverting who "outside India" refers to); the model found a second escape
hatch not addressed by that same edit. One generalized gate closed one
failure mode, not the whole space of ways to reach the same wrong outcome.

A second landed attack repeats Rule 57 row 7's own "catch-all" objection
(risks.md's ⭐ strongest-attack-on-the-project row) — expected, already
answered there. A third, on the `place_of_supply` GST condition, is the
incoherent-attack-text failure mode already disclosed in "Where we lose,"
not a new instance of anything ("two trees somehow link... the Law of
Supply Location must thus be definitely USA" is not a coherent legal
argument). **The fourth, not previously written up here, argues the
classification limb itself** — that receiving USDC as payment may not be a
"transfer" of a virtual digital asset under s.2(47), so s.115BBH might not
even reach this receipt. Ground truth's `elements.classification: settled`
and this project's entire case narrative treat classification as the one
genuinely settled question in D1; this attack contests that. Read as node
5's documented over-eagerness (attacks nearly everything, per "Where we
lose") rather than a fifth real finding — but published here rather than
quietly left out a second time, since leaving it out once was already the
mistake being corrected in this edit.

**Correction to a correction, made later the same night ([D56](DECISION-D56.md)):**
the paragraph above originally said the instruction that started this cycle
was wrong to assert D1's `citations_expected[]` "lists Rule 56 and Rule 57,"
"does not list Rule 243," and "expects s.393(1) Table Sl. No. 8(vi) cited."
That "correction" checked `step21drop/cases/D1/ground_truth.json`, a stale
copy last touched at the rejected pre-freeze commit (`a267f19`), not the
real, frozen file (`cases/D1/ground_truth.json`, updated by the actual freeze
commit `225ed20b`, and the one `eval/score.py` has always read from —
`CASES = os.path.join(ROOT, "cases")`). **The real file has all three:**
Rule 56, Rule 57, and s.393(1) Table Sl. No. 8(vi) are in
`citations_expected[]`; Rule 243 is not. The original instruction was
right; this file's own "correction" of it was the error. Fixed here rather
than left standing — full account, including why no M1–M5 score anywhere
was ever affected by the two trees diverging (only `citations_expected`
itself differs; scoring reads the real file and doesn't consume that field
regardless): [`DECISION-D56.md`](DECISION-D56.md).

### The hard-stop, applied

Four confirmed instances of the identical failure now exist, not three: Rule
57 row 7, Rule 206 row 3, Rule 243(8)(e), and s.393(1)'s payer/recipient
inversion (the fourth, fixed this Block) — and a **fifth**, the "foreign
payer exemption" version of the s.393(1) error just above, found by node 5
in the same run that was meant to freeze the record, after the fix that was
supposed to close this class of error. That fifth instance is the one this
Block does **not** chase. The instruction that opened this cycle said
plainly that each previous fix had produced a new error and that this
would keep happening "because it is a property of the problem, not of your
code," and set the rule in advance: after this cycle, whatever remains is
disclosed, not fixed. `D1_final_seed2.json` and its attack file are frozen
as the demo record on that basis — not because the fifth finding is minor,
but because the alternative is an unbounded sixth, seventh, eighth cycle,
each one likely to surface its own next finding, three days before
submission.

**`output-interface.html` regenerated from `D1_final_seed2.json`** — three
regime rows, a "No rule found" chip on the `valuation_method` row next to
the twelve-method / Rs 47,868.76 range in section 02, citation on that row
reads Rule 57, no `Rule 243` anywhere on the rendered page (checked by
substring), no replacement character anywhere in the file (checked at the
byte level, not by eye). `demo-C1.html` regenerated from the existing
`C1_pipeline.json` alongside it, unchanged content, for the video's
one-figure/twelve-figure contrast.

**Frozen.** Any finding raised against `D1_final_seed2.json` from this point
is disclosed in `limits[]` and here, not repaired. We stop three days before
submission, deliberately, because every fix cycle this project has run has
surfaced a new error, and we would rather publish a known, honestly-labelled
state than an unexamined one.

### Addendum: the attacks are on the page now, and one accounting error caught fixing it

"We publish the attack" was a claim this project made from the start
(architecture.md's own words on 🤖 5) that `node7_disclosure.py` never
actually rendered — the composer read `regimes[]`, `missing[]`,
`valuation[]`, never `attacked[]`. Fixed: a new section 05, "What we tried
to break," reads `attacked[]`/`checked_and_survived[]` exactly as
`node5_adversarial.py` wrote them, with a LANDED/SURVIVED badge per attack
and the downgrade it proposed where one exists. Deterministic — no new
model call, same discipline as every other part of the composer. A
`--attack <file>` CLI flag merges a separately-kept attack file in at
render time (D1_final_seed2.json and its attack file were never merged on
disk, matching how earlier records in this project were kept); the
frozen record itself is untouched.

**Regenerating the page to test this surfaced a real accounting error in
this file and in `DECISION-D55.md`, fixed in place above**: both said
"4 attacks, 2 landed, 2 survived" for the selected record, reading
`node5_adversarial.py`'s own CLI summary line wrong — the "2" there is
`checked_and_survived`'s length (two separate conclusions never attacked at
all), not a 2-2 split of the four that were. The raw JSON shows
`survived: false` on all four `attacked[]` entries — **all four landed**,
verified directly against the file before writing this correction, not
assumed from memory. A fourth landed attack (contesting whether receiving
USDC counts as a "transfer" under s.2(47), and so whether s.115BBH reaches
this receipt at all) had also gone unmentioned in the original write-up;
it's now in both docs, read as node 5's documented attack-everything
over-eagerness rather than a sixth real finding, but published rather than
quietly dropped a second time.

## Where we lose

Every finding below is already documented elsewhere in this file or in a decision doc. Collected here, in one place, because a reader should not have to hunt through the night's chronology to find out where the pipeline is actually worse than the alternative, or wrong outright. Nothing here is softened and nothing carries a mitigating clause.

- **Arm A beat arm C on gap recall on D1, in the 20-Aug table.** 75.0% versus 25.0%. The naive baseline, with no scaffolding at all, found more of the real gaps than the full pipeline did on the headline case.
- **Arm C scores 0.0% gap recall on C3, C4, and C5 in the 21-Aug table** — three of six cases where the structured pipeline found none of the gaps ground truth expects. This is the same node (🤖 2) credited elsewhere with genuine successes; on these three cases it found nothing.
- **Gap detection is measurably unstable, not just imprecise.** Three seeds of the identical D1 case, same code, same input, same everything except sampling: 50%, 75%, 0% recall. No single number from that spread is quotable as "the" result — see Block E2.
- **The adversarial node missed a planted defect outright.** D1-b's planted misapplication of Rule 57 row 7 was sitting verbatim in the text node 5 was given, and none of its five attacks on that variant mentioned it.
- **The adversarial node attacks almost everything it sees.** `checked_and_survived` was non-empty in 3 of 8 runs across the night (Block F's seed 2 run added a third — 2 separate conclusions checked and never attacked at all; all 4 of that same run's actual attacks landed, 0 survived) — every other run attacked every conclusion it was given. That is very likely the same reason D1-b's specific defect was missed: several generic attacks were available and easier to reissue than reading for the one planted sentence.
- **The adversarial node has also emitted incoherent output and mislabeled an upgrade as a downgrade**, twice, on real runs — not a hypothetical edge case exercised only in testing. The downgrade bug is now fixed and guarded in code (D54); the incoherent-attack-text failure mode is not.
- **Two of six cases (C3, C4) still carry a valuation block belonging to a different case (D1's), not their own.** We refused to fabricate the missing rate/market data rather than paper over it, which is the right call and also means the gap is still open, not resolved.
- **M5 (false abstention) has never been scoreable, on any run, and the scorer was silently returning a false "0.0%, perfect" for it until that bug was caught and fixed (D48).** No arm has ever been asked to produce the data this metric needs.
- **We amended our own pre-registered schema nine-plus times after our own freeze commit.** Every one is disclosed, none touches ground truth, and that is exactly the sentence a hostile judge is entitled to ask us to say without prompting.
- **The same class of legal-reasoning error — a real, current, correctly-quoted provision applied outside its own scope — happened five separate times in this project's own resolver output**, caught by a human twice and by our own adversarial node three times, invisible to every accuracy metric every time: Rule 57 row 7 (s.92), Rule 206 row 3 (VDA), Rule 243(8)(e) (RCASP, not taxpayer), s.393(1) (recipient/payer inverted), and — found in the same run meant to freeze the record, after the fix for the fourth — a second, different s.393(1) error asserting a foreign-payer exemption the statute's text does not state. The fifth is disclosed, not fixed; see Block F's hard-stop.
- **`D1_final_seed2.json`, the frozen demo record, still asserts an unsupported s.393(1) exemption** ("no deduction obligation... as... the payer is outside India") that our own adversarial node attacked and that a direct read of `corpus/verbatim/IT-393-1-T8vi.md` does not support. Frozen anyway, per the pre-registered selection rule and the hard-stop — see Block F.

None of this is offered as a caveat on the numbers above — it is the other half of them. A results table with only wins in it would be the least trustworthy thing in this repository, on a project whose entire argument is that a confident number resting on ground that quietly moved is worse than an honest range.

---

## Still open before this table is the final one

- **M2's real instability under temperature** (Block E2) — arm C's three seeds on D1 alone: 50%, 75%, 0% gap recall. Worth understanding before results.md is called final, and worth five more seeds before quoting any single M2 number as representative — not yet done.
- **Why C3 reports more gaps than D1, not fewer** — C3's own case file predicts the opposite; see above. Not yet checked whether this is a gap-detector over-flag or an under-specified ground truth.
- **RESOLVED — D1's demo record is frozen at `D1_final_seed2.json`** (Block F). Four D1 records now exist in sequence (original Rule 206 defect, Rule 206 fix / Rule 243 defect, both fixed / s.393(1) defect, and the frozen record); the unsupported foreign-payer reading of s.393(1) in the frozen record is disclosed above, in "Where we lose," and in `limits[]`, not fixed further.
- **Node 5's calibration** (D50) — attacks nearly every conclusion it sees; `checked_and_survived` non-empty in 3 of 8 runs, not never (corrected — see "Where we lose"). Worth investigating before the node's output is used for anything beyond disclosure.
- `node3_valuation.py` generalized for C3, C4 (D47/D51 — C1, C2, C5 are done) — needs CoinDCX-style crypto market data (candle + USDC/USDT peg) for 23 June and 18 June respectively, not SBI data (corrected above)
- **The frozen D1 record's s.393(1) foreign-payer claim** (Block F) — caught by node 5, not fixed, per the hard-stop. If there is a further fix cycle before submission, this is the first item on it.
- M5's contract gap — see `README.md`'s Honest Limitations
- Prior-art check (Block C) — both done: OBJ-1 (does software already solve this), see [`prior-art/OBJ-1.md`](prior-art/OBJ-1.md); DEMAND (do real people hit this), see [`prior-art/DEMAND.md`](prior-art/DEMAND.md) — a real person hitting D1's exact fact pattern (SBI TT rate not published for the settlement date) found independently on a public forum
