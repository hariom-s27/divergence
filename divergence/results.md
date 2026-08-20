# RESULTS — DIVERGENCE

### Step 30 deliverable. In progress — being filled in as the evaluation actually runs, not written after the fact.

---

## Pre-registration

**Ground truth frozen at commit `225ed20b6e697012d25d6063560907d96424a0de`**, 20 August 2026, `15:38:14+05:30`. `citations_expected[]`, `missing[]`, `elements`, and `methods_expected` for all 6 cases were complete at that commit and have not been edited since.

**Disclosure: `schema.json` was amended seven times after that commit**, across two commits the same day — three widening a field to allow a value the pipeline had always documented producing but the schema never actually permitted, two more of the same shape, and two additions for fields the resolver prompts have always asked for that `additionalProperties: false` was silently forbidding. None of the seven touch `cases/*/ground_truth.json` — the schema defines the output contract every arm is checked against equally, not what counts as a correct answer. Full account of all seven: [`DECISION-D46.md`](DECISION-D46.md).

---

## Step 1 complete: nodes 3/4 automated, arm C has real regimes now

As of tonight, `regimes[]` is no longer structurally empty. `node_resolver.py` automates the income-tax and GST resolvers (prompts 03/04), wired into `run_pipeline.py` by default. Five real bugs found and fixed getting from "it runs" to "it produces a correct record" — full account in [`DECISION-D45.md`](DECISION-D45.md), [`DECISION-D46.md`](DECISION-D46.md) and [`iteration-log.md`](step22drop/iteration-log.md).

D1 and C2 now have complete, schema-valid, full-pipeline (arm C) records with real, individually-verified citations. Node 5 (adversarial) is still not automated — that's Step 5 of the plan, not this one — and only 2 of 6 cases have a complete arm-C record so far.

### Real numbers, all metrics, everything that currently has a scoreable run

| Case | Arm | Model | M1 extract | M2 recall | M2 prec | M3 valid | M3 stale | M4 methods | M5 false abst |
|---|---|---|---|---|---|---|---|---|---|
| C1 | A | Qwen2.5-72B | 0.0% | — | 0.0% | 25.0% | 0.0% | 2/1 | — |
| C1 | B | Qwen2.5-72B | 0.0% | — | 0.0% | 25.0% | 0.0% | 2/1 | — |
| C2 | A | Qwen2.5-72B | 9.1% | — | 0.0% | 50.0% | 0.0% | 2/1 | — |
| C2 | B | Qwen2.5-72B | 9.1% | — | 0.0% | 50.0% | 0.0% | 2/1 | — |
| **C2** | **C** | **Qwen2.5-7B+72B** | **9.1%** | **— (see note)** | **0.0%** | **100.0%** | **0.0%** | **12/1** | **—** |
| C3 | A | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 25.0% | 0.0% | 2/5 | — |
| C3 | B | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 20.0% | 0.0% | 2/5 | — |
| C4 | A | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 50.0% | 0.0% | 2/10 | — |
| C4 | B | Qwen2.5-72B | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% | 2/10 | — |
| C5 | A | Qwen2.5-72B | 0.0% | 100.0% | 100.0% | 50.0% | 0.0% | 2/2 | — |
| C5 | B | Qwen2.5-72B | 0.0% | 100.0% | 33.3% | 50.0% | 0.0% | 2/2 | — |
| D1 | A | Qwen2.5-72B | 0.0% | 75.0% | 100.0% | 60.0% | 0.0% | 2/12 | — |
| D1 | B | Qwen2.5-72B | 9.1% | 25.0% | 33.3% | 50.0% | 0.0% | 2/12 | — |
| **D1** | **C** | **Qwen2.5-7B+72B** | **18.2%** | **25.0%** | **100.0%** | **100.0%** | **0.0%** | **12/12** | **—** |

**Citation recall, mean by arm (`eval/m3b_citation_coverage.py`, the metric measuring completeness rather than mere validity): arm A 0.150, arm B 0.150, arm C 0.250 (n=2 for arm C, n=5 for A/B — small sample, real result, not padded).** Arm C's small sample is the honest current state, not hidden.

### What each number actually means, read this before quoting one

- **M1 (extraction accuracy) is still not fairly scoreable, for any arm.** Ground truth uses field names (`asset`, `settlement_datetime_ist`, `counterparty_declared`) that no extractor — pipeline or baseline — has ever been told to match. A correct extraction under a different field name scores as a miss. Not fixed yet; see D45's discussion of the two live options (fix the prompt vs. fuzzy-match the scorer) and why neither was chosen under time pressure.
- **M5 (false abstention) is still undefined on every row.** No prompt anywhere asks any arm to report the `elements{}` shape the scorer needs.
- **D1 and C2's arm C rows are the first genuinely complete pipeline runs that exist.** M3 (citation validity) is 100% on both — every citation the pipeline produced was real, current, and individually verified (not a false positive from a concatenated multi-citation string; see D45 finding #5 for the bug that would have hidden this). M4 (method enumeration) is 100% on both, because ⚙ B's valuation lattice enumerates deterministically — no model involved, so this number reflects arithmetic, not resolver quality.
- **C2's M2 recall reads "—" for a real reason worth investigating, not ignoring.** C2's ground truth expects zero gaps (a clean, determinate case) — node 2 reported one gap anyway, so precision scores 0.0 rather than the undefined-recall case being neutral. Whether that's a genuine false positive from node 2 or a legitimate finding ground truth under-specified has not been checked yet.
- **This is 2 of 6 cases with a complete arm-C record.** The other four (C1, C3, C4, C5) still need `node_resolver.py` run for them before arm C's numbers are anything but partial.

---

## Still open before this table is the final one

- Nodes 3/4 for C1, C3, C4, C5 (Step 1 continues)
- Node 5, the adversarial checker (Step 5) — has never run at all
- Three seeds on D1, all arms (Step 4) — only possible now that temperature is `default`, not `0`
- M1's field-naming fix, M5's contract gap — see `README.md`'s Honest Limitations
