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

## Still open before this table is the final one

- Node 5, the adversarial checker (Step 5) — has never run at all
- Three seeds on D1, all arms (Step 4) — only possible now that temperature is `default`, not `0`
- M1's field-naming fix (Step 2) — necessary but, per D48, no longer sufficient on its own
- Producing real input documents for C1, C2, C3, C4, C5 and re-freezing those cases (D48) — a scope decision, not yet scheduled against Steps 6-9's dates
- `node3_valuation.py` generalized beyond the single canonical case (D47) — needs per-case SBI/FBIL sheet data that was never collected
- M5's contract gap — see `README.md`'s Honest Limitations
