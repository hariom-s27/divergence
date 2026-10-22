# D77 — the live node-5 mutation sweep (R=3): pre-registered, amended twice, human-audited

**Date:** 22 October 2026

## What ran

`mutate.py`'s sweep against a live node 5, the run D69 scaffolded and
`results.md` carried as "has not been run" from 23 Aug until now. Every
number below is read from `runs/2026-10-21_mutants/full/summary.json`
(field path in brackets) or `full/human_audit.json`. None is retyped from
a log. The generated results block in `results.md` ("Results — node-5
mutation sweep") comes from the same two files via
`runs/2026-10-21_mutants/render_results_section.py`.

- **When:** first call started 2026-10-21T18:51:06Z
  [`metadata.first_start_utc`], last call finished 2026-10-22T04:30:42Z
  [`metadata.last_finish_utc`].
- **Model:** `mistralai/Mistral-Large-Instruct-2411` on Featherless. That is
  both the requested model [`metadata.requested_models`] and the `model`
  field the provider returned on every response [`metadata.response_models`].
- **Temperature:** none sent [`metadata.temperature_sent` = None], i.e.
  the model's own default, per D45/D52.
- **Seed:** none sent [`metadata.seed_sent` = None]. Featherless documents
  its seed as "Not reliable, as we use multiple servers"
  [`metadata.seed_note`]. Mutant construction is seeded and deterministic
  [`metadata.mutation_seed` = 1337]; node 5's sampling is not.
- **Size:** 42 mutants (7 operators x 6 cases, of which 2 are no-ops
  [`noop_mutants`]) + 6 nulls = 48 requests per repetition, x 3
  [`reps`] = 144 per-call files [`counts.files`].
- **Calls and tokens:** 212 API calls including retries
  [`metadata.api_calls_incl_retries`]: 144 first attempts + 68 schema
  retries [`error_rates.schema_retried_calls`]. 2,545,704 input tokens
  [`metadata.total_in_tokens`], 172,823 output tokens
  [`metadata.total_out_tokens`], 32,536.3 s of summed call latency
  [`metadata.total_latency_s`].
- **Harness:** HEAD `3e2949e` plus the uncommitted edits below
  [`metadata.harness_head`, `metadata.harness_uncommitted`]. They are
  committed together with this record.

## Harness changes the run needed

- **Cache redirect** (`replay_cache.py`): `CACHE_DIR` honours
  `DIVERGENCE_REPLAY_CACHE_DIR`, so a live run records into
  `runs/2026-10-21_mutants/_live_cache/` and never into the frozen
  `replay_cache/`.
- **Response-model capture** (`llm_call.py`): every live call's provenance
  row carries `response_model`, the `model` field of the provider's own
  response. This makes "which model answered" an observation, not an
  assumption.
- **Nulls** (`mutate.py --nulls`, `op_null`): one identity "mutant" per
  case per repetition, sent live like the rest. It is the control that
  ANY-ATTACK was never compared against before.
- **SPECIFIC matcher** (`build_spec`, `match_specific`): the primary kill
  rule. The spec comes from original-vs-mutated data only, never from node
  5's answer. 11 offline tests are in `tests/test_mutate_specific.py`.
- **Schema retry** (`_attempt`, `_is_shape_error`): one more identical call
  when node 5's own output-contract check rejects the answer. Both attempts
  are kept (`attempts[]`, `first_attempt_error`, `schema_retried`).
- **Resume by skip** (`run_live`): an existing per-call file is skipped and
  never overwritten.
- **`--max-error-rate`**: stops once after-retry ERRORs make the final rate
  certain to exceed the line.
- **`--per-rep-cache`**: repetition *n* records into `_live_cache/r<n>/`.
  Live mode never reads the cache, so no repetition can replay another.

`tests/test_mutate_runner.py` covers the runner offline.

## Pre-registration (written before the calls they govern)

| File | Written | SHA-256 |
|---|---|---|
| `expectations.md` | 2026-10-21, before any live node-5 call (file time 17:43:23Z) | `b1084abfb944ee95e8735f349abaac798f20574ce0ebb065700c6f2a64d61737` |
| `expectations_amendment.md` | 2026-10-21 18:49 UTC (in-file), after the 8-call pilot, before the full sweep | `edfdae807ff5e6b01754e326b351edf020c3cb35c7f2391de08a487a925718c7` |
| `expectations_amendment_2.md` | 2026-10-21 21:16:14 UTC (in-file), during the sweep, before the stop; working-directory line added 2026-10-22T00:43:17Z | `96f33bba7dabdb78c54f0e8efa695ee8e2f5a669bb1e97dadd6f2e8072d44a3f` |

- **Amendment 1:** the schema-retry rule, the stop line moved from 10% to a
  15% after-retry ERROR rate, the per-rep cache, the mixed base-record
  temperature limitation, and a human audit of every SPECIFIC hit. It does
  not change the matcher, operators, model, prompt or temperature.
- **Amendment 2:** if the stop line triggers on node-5 output-shape failures
  only (not harness, cache or transport), resume to completion as a
  documented deviation. More than 3 transport-final ERRORs means stop for
  good.

## The stop and the resume

- **Pre-approval of the resume:** given by the owner at
  **2026-10-22T00:36:15Z**, at 84/144 calls and 21 ERRORs. Source: the sweep
  agent's record, `P03_report.md` §C0, the owner's local audit file (not in
  this repo).
- **On disk, separately:**
  - **Stop:** the runner stopped after call 87/144 (C5_OVERCLAIM_r2), whose
    file finished at **2026-10-22T00:42:53Z**, with 22 after-retry ERRORs
    (22 > 15% of 144).
  - **Amendment line:** the working-directory line was added to amendment 2
    at **2026-10-22T00:43:17Z**.
  - **Resume:** the first resumed call (C5_NULL_r2) started at
    **2026-10-22T00:43:29Z**. The 87 existing files were skipped and none
    was overwritten.
- **ERRORs by final cause** [`errors[].first_line`]: 33 shape failures on
  both attempts, 1 transport (C2_NULL_r1), 1 unparseable JSON
  (C1_OVERCLAIM_r3). Transport-final total = 1, within amendment 2's limit
  of 3.
- **Error rates:** first-attempt 68/144 [`error_rates.first_attempt`];
  after retry 35/144 [`error_rates.after_retry`]. ERRORs are excluded from
  every denominator.

## Result

| Measure | Result | Field |
|---|---|---|
| SPECIFIC, matcher (primary) | 13/89 = 14.6% [8.0–23.7%] | `primary_specific_matcher` |
| SPECIFIC, human-confirmed | 1/89 = 1.1% [0.0–6.1%] | `primary_specific_human_confirmed` |
| Human partial (not headline) | 8/89 = 9.0% [4.0–16.9%] | `human_partial_NOT_HEADLINE` |
| SPECIFIC, term-clean subset | 0/53 = 0.0% [0.0–6.7%] | `specific_term_clean_subset` |
| SPECIFIC placebo on nulls | 3/101 = 3.0% [0.6–8.4%] | `specific_placebo` |
| ANY-ATTACK, mutants | 85/89 = 95.5% [88.9–98.8%] | `secondary_any_attack` |
| ANY-ATTACK, nulls (false flag) | 15/15 = 100.0% [78.2–100.0%] | `null_false_flag_any_attack` |

Clopper-Pearson exact 95% intervals, as computed by `summarize.py` via
`binom_ci.py`.

## The human audit

- **Rater:** 1 independent human rater, R1, a friend of the owner
  [`rater.id`, `rater.relation`]. Wording was AI-assisted, "ChatGPT for
  wording only (self-attested)" [`rater.ai_assistance`]. The rater did not
  see the agent's suggestions [`rater.saw_suggestions` = false].
- **The header:** the answer file's header literally reads "RATER: ChatGPT"
  [`provenance.answer_file_header_verbatim`]. The rater self-attested: "I
  read the items and decided each verdict myself; ChatGPT only reworded my
  reasons" [`provenance.self_attestation`].
- **The owner** did not audit.
- **Rules:** fixed "before verdicts (per owner)" [`rules_fixed`]. Confirmed
  = points at the planted change AND is not seen in null runs.
- **Verdicts:** confirmed 1 (C4_OVERCLAIM_r2), partial 8, not_confirmed 4,
  and placebo chance matches 3 of 3.
- **The rater's own caveat:** "Errors in null runs are unavailable
  observations, not evidence that the critic stayed quiet."
- **The guide** the rater used (`AUDIT_GUIDE_second_rater.md`, neutral facts
  only) is not on disk; it is cited by name in `human_audit.json` [`guide`].
  `full/human_audit_sheet.md` is the owner's sheet, with the agent's
  suggestions marked "not a verdict".

## What this result supports

**The node-5 critic, at default temperature on Featherless, rarely
identifies planted defects (human-confirmed 1/89) and flags untouched
controls as often as mutants; its value as a specific-defect detector is
not supported.**

## What it does not support

- Any claim about real-world faults: mutants are not real faults; see
  `results.md`'s "Mutation testing" for Just et al. (FSE 2014) and
  Papadakis et al. (ICSE 2018).
- Any claim about other models, other temperatures or other providers.
- Any claim that node 5 is useless as a disclosure step. This measured
  specific-defect detection only.

Limitations, in full, are in the generated `results.md` block. In short:
- OVERCLAIM's downgrade route cannot fire on a null, so its low placebo is
  partly by construction.
- The base-record temperature is mixed (C1–C5 at 0, D1 at the default).
- The retry selects well-formed outputs.
- The matcher is lenient on OVERCLAIM (9 of the 13 matcher hits).
- 8/40 mutants have fewer than 2 valid repetitions.
- n is small.

## Resume-safe wording

"Pre-registered a mutation test of an LLM critic (144 planned calls, 212
API calls incl. 68 schema retries, 3 repetitions, null controls); a human
audit confirmed the critic identified only 1 of 89 planted defects, while
it flagged every untouched control that returned a valid answer (15/15) —
reported as the result."
