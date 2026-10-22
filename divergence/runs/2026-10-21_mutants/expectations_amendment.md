# Amendment to expectations.md (P03)

Written **2026-10-21 18:49 UTC (2026-10-22 00:19 IST)**: after the 8-call D1 pilot and **before** the full sweep (`full/`, R=3). `expectations.md` is left unchanged. Nothing here changes the SPECIFIC matcher, the operators, the model, the prompt or the temperature.

## 1. Schema-retry rule (new)
- When node 5's own output-contract check (`node5_adversarial._validate_attack_shape`) rejects an answer, `check()` raises an `LLMError` beginning `node5_adversarial:`. `mutate.py` then makes **one** more call with the identical request.
- Transport/HTTP/unparseable-JSON failures (`[node5_adversarial] …`) are **not** retried here; `llm_call`'s own retries already cover them.
- Both attempts are saved in the per-call file (`attempts[]`, `first_attempt_error`, `schema_retried`). The verdict comes from the final attempt.
- If the retry also fails, the call is **ERROR**: excluded from every denominator and counted separately.
- The summary reports the **first-attempt error rate** and the **after-retry ERROR rate** separately.
- Known bias: the retry keeps the model's well-formed outputs and drops the malformed ones, which mildly favours more coherent samples. It does nothing about garbled text inside otherwise well-formed outputs.

## 2. Stop line (replaces the 10% rule)
**STOP if the after-retry ERROR rate exceeds 15%.** The runner (`--max-error-rate 0.15`) stops as soon as after-retry ERRORs exceed 15% of **all 144 planned calls** (i.e. at the 22nd ERROR), which is the point where the final rate is certain to exceed 15%. The run can be resumed: files already on disk are skipped, never overwritten.

## 3. Per-rep live cache
Rep *n* records its live responses into `_live_cache/r<n>/`, which is empty or absent before the sweep. Live mode never reads the cache (`llm_call.py`, replay branch only when `DIVERGENCE_REPLAY=1`), so no repetition can replay another. Identical requests within one rep (a schema retry; the C2/D1 null and its no-op DATE_SHIFT) share a cache key, and the later response replaces the earlier one *in that cache only*. The per-call JSON files are the record.

## 4. Erratum to expectations.md
The last note in `expectations.md` reads "escapes `—` as `—`". It should read "escapes `—` as `—`" (the JSON escape `json.dumps` writes by default). It is a wording slip in an explanatory note and affects no rule, term or prediction.

## 5. Limitation: mixed temperature in the base records
The mutants are built from frozen records produced under different protocols:
- `runs/21aug/C1_pipeline.json` … `C5_pipeline.json`: `_meta.llm.temperature = "0 (dev default)"` (20 Aug, before D52's fix).
- `runs/21aug/D1_final_seed2.json`: `"default (model's own)"`.

Node 5 itself runs at the model's default temperature (none sent, per D45/D52) for every call in this sweep. Differences between C1–C5 and D1 may partly reflect how their base conclusions were produced, not only node 5.

## 6. Human audit of every SPECIFIC hit
Every mutant the matcher credits (`caught_specific = true`) will be read by a human, judging whether node 5 actually pointed at the planted change. The summary reports **both**:
- the **matcher count** (the pre-registered primary score), and
- the **human-confirmed count**, with each hit's verdict and a one-line reason (in `full/human_audit.json`).

The matcher count is not revised by the audit. Placebo hits on null critiques are audited the same way.
