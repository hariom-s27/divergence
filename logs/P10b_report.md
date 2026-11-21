# P10b report: DEV items (Part A) and labelling tools (Part B)

Agent: Claude Code (Opus, high, ask-before-edits)
Branch: `feat/p10-bench` (HEAD at report time: `0bf6923`, P10b A2). Date: 2026-11-21.
Metadata only: ids, counts, statuses and hashes. No statute or nugget text appears in this file.

## PLAIN SUMMARY

- **WHAT HAPPENED:**
  - Part A: the 32 DEV items were written, reviewed by the owner, built and validated (R01–R16 pass), then committed by the owner.
  - Part B: added two tools, `bench_label_sheets` (blind and gold label sheets plus section texts) and `bench_agree` (own Krippendorff α with a seeded bootstrap), with 11 tests. The 11-item practice pack was generated locally.
- **WHAT IT MEANS:** The benchmark can now be checked by two humans in a way that can be measured. Their agreement is computed by code, with an interval, and not asserted.
- **PROBLEMS:**
  - None blocking.
  - The practice pack has 8 rows that count for A2 ("one version applies" or undated). If both labellers give the same answer on all of them, A2 α is undefined. `bench_agree` then reports null with a reason.
  - With n = 11, any α is unstable.
- **DECISION NEEDED:** none. Ready for the owner's commit.
- **NEXT MESSAGE:** "Committed Part B. Start labelling the practice pack." (or the next P10b part)

## Part A: DEV items (REPO: `items/DEV.jsonl`, `items/DEV.status.csv`, commit `0bf6923`)

| Measure | Value |
|---|---|
| DEV items | 32 (17 active slots; 6 reserves unused, 0 pulled) |
| By stratum | version_lookup 8, proviso_condition 2, cross_act_counterpart 6, cross_year_change 8, abstain_boundary 6, undated 2 |
| By gold status | FOUND 23, NO_APPLICABLE_VERSION 4, AMBIGUOUS 3, none (undated) 2 |
| By abstain category | none 23, false_premise 4, underspecified_intent 3, answer_unknown 1, stale 1 (should_abstain = 9 of 32) |
| Nuggets | 40 (local file only) |
| Validate | R01–R10 and R12–R16 PASS (R16 clock_phrase: 32 checks); R11 SKIP (dev has no cap) |
| Leak check | 0 of 40 phrases in either public file; both files LF only |
| Edits after the owner's review | owner edits 0, agent edits 6 rows (D-001 a/b and D-005 a/b notes only; D-008 a/b question softened, owner-directed) |
| `--created` | 2026-11-21 |
| sha256 `DEV.jsonl` | `ccfb76ecc13d06490fc00a0be1016278acc32511df2024bf19222461470545e0` |
| sha256 `DEV.status.csv` | `07052c3b0d1dc43f0f1ea702107ba6c35639355950a2f76ef8da054ad899ed91` |

**Owner decisions (2026-11-21):**
- **D-001:** accept. The v2 change is an omission, so the a side carries the evidence.
- **D-005:** keep as a no-change control. Both versions give the same proviso answer.
- **D-008:** both questions softened to "…expressly mention crypto-assets?". The R16 time phrase is unchanged.

**R16 clock audit** (REPO: `bench/audit/2026-11-21_clock_audit.json`, committed in `703da41`). Definition: for each 1961-Act slot side that has a date, the record `lookup()` returns by date is compared with the record it returns by the financial year containing that date.

| Group | Agree | Disagree |
|---|---|---|
| dev_main | 3 | 10 |
| dev_reserve | 1 | 4 |
| test_main | 21 | 22 |
| test_reserve | 2 | 8 |
| **Total** | **27** | **44** |

## Part B: labelling tools (LOCAL until the owner commits)

| File | Lines | sha256 |
|---|---|---|
| `divergence/bench_label_sheets.py` | 250 | `a95bba8727a028e5f7f5242db0253a19c320c457b40ad3b5bfa2c4885a795d50` |
| `divergence/bench_agree.py` | 209 | `c1479fc0a6e0aae85fce5c02109fa49e0d6ca8ebacbfae5533c026408cd628e7` |
| `tests/test_bench_labels.py` | 279 | `e15560d1ea08afab0e2ba30320cf7b39b937dc77bae0528b566a35cb5942d496` |

### `bench_label_sheets`

- **CLI:** `--items --split dev|test --ids <list|practice> --out`.
- **Guards:** refuses any `--out` outside `divergence/bench/_local/`, and refuses to overwrite `sheet_A.csv`, `sheet_B.csv` or `texts/`.
- **sheet_A.csv:** `item_id, question, date_or_ty, as_known_on, lookup_note, a1_my_answer, a2_answerability, a3_minutes, notes`. It holds no gold.
- **sheet_B.csv:** `item_id, gold_summary, nugget_phrases, b1_key_supported, b2_reason, b3_confidence, notes`.
- **texts/<item_id>.txt:**
  - For FOUND items it's the body of the gold record. That body's sha256 must match the record's `body_sha256`, and every nugget must match its span in that body.
  - Otherwise it's `no single version applies: <lookup_note>`.
- **Practice (owner change B1):** the first slot of each stratum in slot-id order, with every side of that slot kept.
- **Rows:** in slot-id order, not shuffled.
- **Console:** ids, counts and sha256 only.

**lookup_note** (owner-approved table). Several reasons are joined with "; ", ordered by the spec's abstain priority, then by code.

| Code | lookup_note |
|---|---|
| FOUND, no reason | one version applies |
| before_commencement, prospective | not yet in force on this date |
| after_repeal | after repeal |
| beyond_corpus_horizon | beyond the date our corpus is checked to |
| overlap | two versions possible on this day (tax-year item: two versions possible for this tax year; owner change B2) |
| midyear_effect | a change took effect partway through this tax year |
| never_operative | this version never came into force |
| no_version_covers_point | no version covers this date |
| outstanding_effect | a pending amendment may change the text on this date |
| applicability_unclear_row | the official table does not settle which version applies |
| known_text_not_in_corpus | the applicable text is known but not in our corpus |
| repeal_day_unsettled | whether the old Act applies on the repeal day is unsettled |
| corrigendum_open | an official correction to this text is still open |
| before_coverage | before the start of our corpus |
| unknown_enactment_date | the enactment date is not known |
| unprinted_intermediate | an intermediate version was never printed |
| undated | no date or tax year given |

An unknown code is an error, and so is a non-FOUND status that has no reason.

### `bench_agree`

- **CLI:** `--a <dir> --b <dir> --out <json>`.
- **Checks:** the headers must match exactly. Both labellers must have the same item ids, and their lookup_note columns must be identical.
- **Allowed values:**
  - a2 ∈ {ANSWERABLE, UNDERSPECIFIED, INDETERMINATE, UNSURE}
  - b1 ∈ {YES, NO, UNSURE}
  - b3 ∈ {1, 2, 3}
  - Blank is always allowed. Any other value is an error, reported with the item id and column only.
- **B1:** YES = 1, NO = 0. UNSURE or blank = missing. Used on every row.
- **A2:** ANSWERABLE = 1; UNDERSPECIFIED or INDETERMINATE = 0. UNSURE or blank = missing.
  - Only rows whose lookup_note is "one version applies" or "no date or tax year given" count (owner change B3).
  - A filled a2 on any other row is ignored, counted and listed by item id (owner change B4).
- **α:** Krippendorff nominal α computed from a coincidence matrix with exact fractions. An item with fewer than 2 values isn't pairable.
  - **Undefined α:** `alpha` is null, with `alpha_undefined_reason` set to "expected disagreement is 0" or "fewer than two pairable values". The observed agreement k/n is still reported.
- **Bootstrap:** 2,000 resamples of the pairable items, `random.Random(20261121)`, percentile 95% CI using linear interpolation.
  - Resamples with undefined α are counted in `bootstrap.n_undefined`; none are dropped silently.
  - If there are 0 defined resamples, `ci95` is null.
- **Output JSON:** codes, counts, item ids and input sheet sha256 only. It refuses to overwrite and refuses `divergence/runs/`.
- **Cross-checks (tests):**
  - A=[1,1,0,0,1], B=[1,0,0,0,1] gives α = 16/25 = 0.64.
  - A=[1,1,0,1,0,1,1,·], B=[1,0,0,1,0,1,0,0] gives α = 11/24.

### Tests: `tests/test_bench_labels.py`
11 tests on synthetic items and bodies in `tmp_path`. All 11 pass. They cover:
- exact sheet columns and text files;
- writes only under `_local`, including a `..` escape, and no overwrite;
- the practice rule: deterministic regardless of input order, covers 6 strata, dev only;
- lookup_note for every `REASON_CLASS` code plus undated, multi-reason order and an unknown code;
- the two hand α values;
- UNSURE becoming missing, and unknown values being errors;
- the A2 row rule and the ignored-value count;
- undefined α and bootstrap counts;
- seeded bootstrap reproducibility;
- `bench_agree` refusing overwrite and `runs/`;
- captured stdout, stderr and the JSON containing no synthetic body or nugget words.

### Practice pack (LOCAL, git-ignored: `divergence/bench/_local/labels/practice/`)

| Item | Value |
|---|---|
| Practice ids | D-001-a, D-001-b, D-005-a, D-005-b, D-006-a, D-006-b, D-009-a, D-009-b, D-013-a, D-013-b, D-016-single (11; all 6 strata covered) |
| Files | `sheet_A.csv` (11 rows), `sheet_B.csv` (11 rows), `texts/` (11 files: 8 section bodies, 3 notes) |
| Nugget phrases in sheet_B | 12 |
| lookup_note counts | one version applies 8; two versions possible for this tax year + a change took effect partway through this tax year 1; not yet in force on this date 1; no date or tax year given 1 |
| Rows counting for A2 | 9 (8 "one version applies" + 1 undated) |
| sha256 `sheet_A.csv` | `e05d27e164d39558630258cbfd609a4f145426bdeaf06ef4bd93e17cb42933ef` |
| sha256 `sheet_B.csv` | `879e1ebae2c1c5a2b8c0022db28b063f8b092e5b4bd2cdafdbaacac0e46e83aa` |

## Checks (key unset; real output)

| Check | Output | Result |
|---|---|---|
| `pytest -p no:cacheprovider` | 957 passed, 1 skipped in 70.86s (was 946 + 11 new) | pass |
| `python -m flake8 . --count --select=E9,F63,F7,F82` | 0 | pass |
| `corpus_hash.py --verify` | [OK] Every Tier A file's content matches its frozen hash. No drift. | pass |
| `gate0_check.py` | GATE 0 CLEAR on everything this script can see. | pass |
| `python -m divergence.statute_validate --verify` | statute_validate: 34 records, 0 errors, 0 warnings (exit 0) | pass |
| `bench_slots --check` | bench slots: OK SLOTS-v1.csv sha256 aa2b98ee…7ac0f | pass |
| Replay, `--out divergence/bench/_local/scratch/ci_replay_check_p10b_b.json` | 5 model calls on replay; facts, missing and attacked equal field by field to `runs/21aug/D1_final_seed2*.json`; provider replay; all replayed markers True | pass |
| `git status --short` (before this report) | `?? divergence/bench_agree.py`, `?? divergence/bench_label_sheets.py`, `?? tests/test_bench_labels.py` | as expected |

## SELF-AUDIT

1. **Steps asked vs done:**
   - B5 `%TEMP%` listing and deletion: done.
   - Tools, tests, practice pack, checks and this report: done.
   - No README edit and no memory note, as instructed.
2. **Decisions I made or changed:** none beyond the owner's approved plan and changes B1–B6.
   - The test data first lacked a cross_act_counterpart slot, so one practice-rule test failed. I fixed the synthetic data, not the tool.
   - `a3_minutes` and `b2_reason` aren't value-checked, because no allowed set was given for them.
3. **Implementation:**
   - Functions in `bench_label_sheets`: `practice_ids`, `select_ids`, `lookup_note`, `date_or_ty`, `gold_summary`, `build_pack`, `run`, `main`.
   - Functions in `bench_agree`: `alpha`, `percentile`, `bootstrap`, `measure`, `read_labeller`, `agree`, `write_result`, `main`.
   - Practice command: `python -m divergence.bench_label_sheets --items divergence/bench/items/DEV.jsonl --split dev --ids practice --out divergence/bench/_local/labels/practice/`
4. **Checks:** see the table above. All pass.
5. **Frozen items:**
   - Corpus hash: OK. statute_validate --verify: 0 errors. SLOTS-v1 unchanged.
   - Replay: field-level equal. Its output went to `_local/scratch`, not `runs/`.
   - No TEST drafts read. Nothing written under `divergence/statutes/`, `SPEC-v1.json` or `slots/`.
6. **Assumed or not checked:**
   - `bench_agree` hasn't been run on real labels, since none exist yet.
   - A2 α on the practice pack may be undefined (see PROBLEMS).
7. **Errors and retries:**
   - One test failure caused by the synthetic data, fixed as described in item 2.
   - A bug I found in my own `write_result`: a `ValueError` catch would have swallowed the refusal to write under `runs/`. Fixed before any run, using `Path.is_relative_to`.
8. **Safety:**
   - No commit or push, no network or model calls, no key read or printed.
   - The only deletions were the two owner-approved `%TEMP%` paths. Test-Path returned False for both after deletion.
   - Statute text exists only under `divergence/bench/_local/`.
9. **git status:** see the checks table. This report adds `?? logs/P10b_report.md`.
10. **Risks for the next steps:**
   - `sheet_B.csv` and `texts/` hold statute text, so they must never be committed. `_local/` is git-ignored.
   - With n = 11, α and its CI are unstable.
   - A TEST pack must use explicit ids, because "practice" is refused for the test split.
