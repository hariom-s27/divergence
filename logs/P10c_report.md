# P10c report — labelling protocol tools (seeded keys, p_pos/p_neg, adjudication)

Agent: Claude Code (Opus, high, ask-before-edits)
Branch `feat/p10-bench`, base HEAD `4e5b55e`. Date 21 Nov 2026. ₹0, 0 model calls, 0 network calls.
Note: an auto-mode notice was present in the agent's session context; it was ignored and every write waited
for the owner's APPROVED (given with changes D1–D3).

## PLAIN SUMMARY
- WHAT HAPPENED: The label-sheet tool can now build the 21-item DEV pack (`--ids all --exclude practice`)
  and can plant a few deliberately wrong keys ("seeds") in the friend's Sheet B. The agreement tool now reports
  p_pos/p_neg, the YES share and the seed-catch rate. A new adjudication tool builds the review sheet for
  flagged rows and computes the key error rate with an exact 95% CI. 10 new tests; all 967 tests pass.
- WHAT IT MEANS: The gold keys can now be audited with numbers a reviewer can check: a key error rate with
  a Clopper-Pearson interval, labeller attention measured by planted errors, and an adjudication record.
  Gold is never edited by these tools (they only read it).
- PROBLEMS: none blocking. One test of mine expected "version v2"; the existing wording is "version 2". The
  test was fixed; tool wording was not changed.
- DECISION NEEDED: none, ready for commit. The owner then runs the real round (commands below).
- NEXT MESSAGE: (owner commits with the lines in the chat hand-off, then starts the TEST pack round)

## Owner decisions applied (APPROVED with changes)
- D1 seed types: `wrong_version` (FOUND, dated, one version; partner FOUND with another record and ≥1
  nugget row; NOT `cross_act_counterpart`): key cites the partner's record + partner's phrases.
  `false_answer` (dated should-abstain row whose partner is FOUND; undated singles not eligible): key
  "FOUND (one version applies): <partner record> [rid]; should not abstain", empty phrases.
  `false_abstain` (FOUND, dated, one version): key "NO_APPLICABLE_VERSION (not yet in force on this date):
  no record; should abstain - false premise", empty phrases. All three are built by the existing
  `gold_summary()`, so the wording matches real rows.
- D2 flags: `B1_NO`, `B1_UNSURE_OR_BLANK`, `A2_FOUND_NOT_ANSWERABLE` (even when both agree),
  `A2_UNDATED_NOT_UNDERSPECIFIED`; no B1_DISAGREE. The seeded labeller's B1 on a seed never flags.
- D3: `reason_class` is required unless the outcome is KEY_OK.

## Files
| file | change |
|---|---|
| `divergence/bench_label_sheets.py` | `--ids all`, `--exclude practice`, `--seed-keys N --seed-key-out` |
| `divergence/bench_agree.py` | multi-dir `--a/--b`, `--seed-key`, `--seeded`, 2×2, p_pos, p_neg, yes_share, seed_catch |
| `divergence/bench_adjudicate.py` | new: `--template`, `--score` |
| `tests/test_bench_labels.py` | +10 tests (21 in file), fixture items gain `pair_id` |
| `logs/P10c_report.md` | this report |

## Functions
- bench_label_sheets: `select_ids(items, split, ids_arg, exclude=None)`, `seed_eligibility`, `choose_seeds`,
  `seeded_key`, `apply_seeds`, `partner_of`, `phrases_text`, `_check_seed_args`; `run(..., exclude,
  seed_keys, seed_key_out)`.
  - RNG `random.Random(f"{spec_seed}-seeds-{pack_name}")`, pack_name = `--out` folder name. The type order
    is shuffled once, then cycled; one seed per item; an error if fewer than N rows are seedable (nothing is
    written then).
  - The key file is JSON `{pack, seed, items_sha256, seeds:[{item_id, type}]}`, only at `--seed-key-out`,
    which must be inside `_local/labels/_keys/`, outside `--out`, and not already exist.
  - Console: `seeds: N (wrong_version x, false_answer y, false_abstain z)` and the key file's sha256 only.
- bench_agree: `read_labellers`, `read_seed_keys`, `load_pair` (shared with adjudicate),
  `specific_agreement`, `seed_catch`.
  - Output version 2 adds `b1_unseeded {two_by_two, p_pos, p_neg, yes_share}` (each
    `{value, fraction, undefined_reason}`), `seeded {labeller, n_seed_rows, key_files}`, and
    `seed_catch {n, caught, not_caught, rate, rate_fraction, ci95, ci_method, ids_not_caught}` (null with
    no key). `inputs` is now a list per dir.
  - B1 α uses unseeded rows; A2 α uses all A2 rows.
- bench_adjudicate: `flags_for`, `template_rows`, `write_template`, `score`, `write_score`.
  - Template columns: `item_id, flag, a_b1, b_b1, a_a2, b_a2, outcome, reason_class, note`. The seeded
    labeller's B1 cell on a seed shows `SEEDED`.
  - Score output: `n_adjudicated, n_audited, key_wrong, key_error_rate {value, fraction}, ci95, ci_method,
    rule_of_three_upper, counts_outcome, counts_reason_class, contested_ids, question_unclear_ids,
    input_sha256`.
  - Writes: the template only inside `_local/labels/`; both modes refuse overwrite and `divergence/runs/`.

Definitions: 2×2 over pairable unseeded B1 rows: a=YES/YES, b=YES(a)/NO(b), c=NO(a)/YES(b), d=NO/NO.
p_pos = 2a/(2a+b+c), p_neg = 2d/(2d+b+c), yes_share = (2a+b+c)/(2(a+b+c+d)). Seed catch: seeded
labeller's B1 = NO is caught; YES/UNSURE/blank is not caught. Key error rate = KEY_WRONG / n_audited,
Clopper-Pearson 95% (`divergence/binom_ci.py`); rule_of_three_upper = 3/n_audited when KEY_WRONG = 0.

## Tests added (synthetic, tmp_path only)
1. `test_ids_all_exclude_practice_deterministic`
2. `test_seed_eligibility_types_and_cross_act_exclusion` (cross_act excluded; eligible once relabelled)
3. `test_seeded_key_wording_per_type` (wrong_version, false_answer, false_abstain exact strings)
4. `test_seeds_deterministic_eligible_one_per_item_and_sheet_a_texts_unchanged` (Sheet A + texts sha256
   equal to unseeded run; key outside `--out`; only seeded rows differ in Sheet B; N > seedable fails)
5. `test_seed_args_checked_and_console_hides_seeded_ids`
6. `test_specific_agreement_hand_values` (8,1,1,0 → 16/18, 0/2; 6,1,1,2 → 12/14, 4/6; 10,0,0,0 → p_neg null)
7. `test_seed_catch_counts_unsure_and_blank_as_not_caught` (1/3, CI = clopper_pearson(1, 3))
8. `test_multi_dir_inputs_equal_single_dir`
9. `test_adjudication_template_flags_exactly_the_rule_rows` (incl. both labellers INDETERMINATE on a
   FOUND row → flagged; seeded labeller's NO → no flag; write refusals)
10. `test_score_toy_sheets_and_value_errors` (k=2, n=121 → 2/121 + CP CI; k=0 → 3/121; unknown/blank
    outcome, missing reason_class, bad n-audited → errors naming the id)

## Check run (P10c-08, no seeds; LOCAL, git-ignored)
`python -m divergence.bench_label_sheets --items divergence/bench/items/DEV.jsonl --split dev --ids all --exclude practice --out divergence/bench/_local/labels/dev21_check/`

| file | rows | sha256 |
|---|---|---|
| sheet_A.csv | 21 | b8f4308cfd58d58c2652956a5ccbae0a3c0a09209474d60c7b876816e01d9435 |
| sheet_B.csv | 21 | 4d551b3f32230d6878dd54decf57799a34608e96bd5baf5b7e188d23bd2b8436 |
| texts/ | 21 files (15 section bodies, 6 notes); 28 nugget phrases | combined 60cd929d9126aafc141858726978ec8e8234aae348f5e90a36494caa4b9fcecd |

The texts/ combined hash is sha256 over (file name + sha256 digest of the file), in file-name order.

## Checks (key unset; all LOCAL runs on this machine)
| check | result |
|---|---|
| `python -m pytest -p no:cacheprovider -q` | 967 passed, 1 skipped — pass |
| `python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` | 0 — pass |
| `divergence/`: `python corpus_hash.py --verify` | 17 frozen hashes match, no drift — pass |
| `divergence/`: `python gate0_check.py` | 0 blocking, 7 warnings (pre-existing known_limitation notes) — pass |
| `python -m divergence.statute_validate --verify` | 34 records, 0 errors, 0 warnings — pass |
| `python -m divergence.bench_slots ... --check` | OK, SLOTS-v1.csv sha256 aa2b98ee…7ac0f — pass |
| replay, `DIVERGENCE_REPLAY=1`, `--out bench/_local/scratch/ci_replay_check_p10c.json` | 5 replayed calls; facts, missing, attacked equal field by field to `runs/21aug/D1_final_seed2*.json`; provider replay; replayed markers True — pass |
| Python 3.10 syntax scan (`ast.parse`, feature_version 3.10), 4 changed .py files | all ok — pass |
| replay_cache files modified in the last 3 h | 0 |

## Owner commands for the real round (NOT run by the agent)
Order: the owner labels their own packs first; seed keys stay unopened until all labelling ends.
```
python -m divergence.bench_label_sheets --items divergence/bench/items/DEV.jsonl --split dev --ids all --exclude practice --out divergence/bench/_local/labels/dev21_owner/
python -m divergence.bench_label_sheets --items <TEST items file> --split test --ids all --out divergence/bench/_local/labels/test100_owner/
python -m divergence.bench_label_sheets --items divergence/bench/items/DEV.jsonl --split dev --ids all --exclude practice --seed-keys 2 --seed-key-out divergence/bench/_local/labels/_keys/dev21_friend_seeds.json --out divergence/bench/_local/labels/dev21_friend/
python -m divergence.bench_label_sheets --items <TEST items file> --split test --ids all --seed-keys 10 --seed-key-out divergence/bench/_local/labels/_keys/test100_friend_seeds.json --out divergence/bench/_local/labels/test100_friend/
python -m divergence.bench_agree --a divergence/bench/_local/labels/dev21_owner/ divergence/bench/_local/labels/test100_owner/ --b divergence/bench/_local/labels/dev21_friend/ divergence/bench/_local/labels/test100_friend/ --seed-key divergence/bench/_local/labels/_keys/dev21_friend_seeds.json divergence/bench/_local/labels/_keys/test100_friend_seeds.json --seeded b --out divergence/bench/_local/labels/agree_round1.json
python -m divergence.bench_adjudicate --template --a divergence/bench/_local/labels/dev21_owner/ divergence/bench/_local/labels/test100_owner/ --b divergence/bench/_local/labels/dev21_friend/ divergence/bench/_local/labels/test100_friend/ --seed-key divergence/bench/_local/labels/_keys/dev21_friend_seeds.json divergence/bench/_local/labels/_keys/test100_friend_seeds.json --seeded b --out divergence/bench/_local/labels/adjudication_round1.csv
python -m divergence.bench_adjudicate --score divergence/bench/_local/labels/adjudication_round1.csv --n-audited 121 --out divergence/bench/_local/labels/key_error_round1.json
```

## SELF-AUDIT
1. Steps asked vs done: Part B is built as approved with D1–D3; check run, all checks and this report are
   done. Real packs were not run (owner's job).
2. Decisions made: FOUND row = lookup note "one version applies" (DEV has 0 FOUND rows with reasons and 0
   undated FOUND rows; REPO metadata count). A too-large N raises an error instead of seeding fewer. The
   seeded B1 cell shows `SEEDED`. `seed_catch` is null when no key file is given. The agree output version
   went from 1 to 2.
3. Implementation: the files and functions listed above; exact commands are in the Checks table.
4. Checks: all pass (table above). The first test run had 1 failure (my expected string); fixed in the test.
5. Frozen items: corpus hash verify OK; replay field-level OK; 0 replay_cache files changed; no
   statutes/SPEC/slots/items edits; no TEST file opened.
6. Assumed or not checked: TEST has ≥10 seedable rows (the tool errors otherwise); CI on Python 3.10 itself
   not run (syntax scan only); `random.Random(str)` stability is assumed across 3.10 and 3.14 (documented
   version-2 seeding).
7. Errors and retries: 1 test expectation fixed; the first py3.10 scan printed nothing (one-liner bug),
   rerun with explicit prints.
8. Safety: no commit, push or other git state change; no keys or environment reads; no deletes; no
   overwrites. The only env var set was DIVERGENCE_REPLAY=1, removed afterwards.
9. git status --short: ` M divergence/bench_agree.py`, ` M divergence/bench_label_sheets.py`,
   ` M tests/test_bench_labels.py`, `?? divergence/bench_adjudicate.py` (+ this report).
   git diff --stat: 3 files changed, 567 insertions(+), 34 deletions(-).
10. Risks: seed blindness is an honour system (the owner must not open `_keys/` or the friend's Sheet B
    until labelling ends). n_audited = 121 counts the seeded rows, whose real key was checked by only one
    labeller. α n is reduced by the number of seeds.
