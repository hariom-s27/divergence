# P10a report — benchmark spec, schema, slots and tooling

Agent: Claude Code (Opus, high, ask-before-edits)
Branch `feat/p10-bench` (from `main` = `16366ce`); Part B committed by the owner as `7bb9dbd`.
Date: 21 Nov 2026. Metadata only: no statute body text, no nugget text, no keys.

## PLAIN SUMMARY

- **What happened:** A benchmark specification, an item schema and four tools (slot sampler, item builder,
  validator, TEST seal) were added with synthetic tests (Part B). In Part C the sampler drew the slots
  twice. Draw 1 was superseded by owner decision (b), a ranking change. Draw 2 (same seed, run once) is
  `SLOTS-v1.csv`: TEST 46 pairs + 8 undated = 100 items, DEV 15 pairs + 2 undated = 32 items, plus reserve
  slots. A CI step re-checks the file on every push.
- **What it means:** Gold answers and abstain labels for every slot come from the frozen statutes-v1
  lookup (D80), not from a model. The owner can now write questions per slot and validate them by code.
- **Problems:** Every quota was filled; TEST abstain share 0.28 (target 0.20–0.30). Draw 2 spreads TEST
  cross_act over 4 mappings (Draw 1: 1). TEST still has no `answer_unknown` items and no 1961 repeal /
  repeal-day abstain pairs. These are accepted as limits. 5 record combinations occur in both DEV and TEST
  (different dates).
- **Decision needed:** none.
- **Next message:** "APPROVED P10b" (item writing / seal plan) after committing.

## Decisions applied (owner, P10a)

| id | decision |
|---|---|
| D1a | strata quotas: version_lookup 0.25, proviso_condition 0.10, cross_act_counterpart 0.20, cross_year_change 0.25, abstain_boundary 0.20 |
| D2 | abstain category = spec class map applied to `reason_class()`: NO_LAW→false_premise, LEGAL→answer_unknown, QUERY→underspecified_intent, CORPUS→stale (horizon window only). Priority false_premise > stale > answer_unknown > underspecified_intent. Excluded from the frame: before_coverage, unknown_enactment_date, unprinted_intermediate |
| D3a | `horizon_window` 2026-11-16 … 2027-03-31, used only for the stale side of abstain_boundary pairs |
| D4a | `undated` is a sixth stratum outside the quotas; gold_status null; category underspecified_intent |
| extras | ~20% reserve slots per stratum (ceil), "unusable → next reserve in order"; DEV/TEST never share (unit, date_a, date_b); scratch in `divergence/bench/_local/scratch/`; `.gitattributes` `divergence/bench/** text eol=lf` |

Spec facts (REPO, `divergence/bench/SPEC-v1.json`): seed 20261121; as_known_on 2026-11-15; window
2022-04-01 … 2026-11-15; max 10 TEST items per unit; tax years 2022-23 … 2026-27; spec sha256 (canonical
JSON) `7ce2c86544fcf2f9370a6e4583b6ef079b268d522d63ed1e25a294268c4348a7`.

## Part A findings (probe, REPO data)

- 18 units, 34 records; 35 (status, records) boundaries inside the window in the golden timeline.
  The 11 units of the 2025 Act have one boundary each (commencement 2026-04-01). The 1961 units have 2–7
  (coverage start, version changes, repeal, repeal day, unprinted intermediates).
- At as_known_on 2026-11-15, 1961:158B v1 and 1961:3 v1 are AMBIGUOUS (`unknown_enactment_date`), whereas the
  golden timeline (as_known_on None) shows them FOUND; the boundary dates are identical.
- `overlap` and `applicability_unclear_row` are class LEGAL (not QUERY); the owner chose strict class mapping.
- `known_text_not_in_corpus` (CORPUS) occurs in the golden sweep's knowledge-grid queries but never in the
  bench frame at 2026-11-15 (tested). The sampler errors if "stale" ever appears inside the window.

## Part B — tools (REPO, commit `7bb9dbd`)

| file | role |
|---|---|
| `divergence/bench/SPEC-v1.json` | spec (sorted keys, LF) |
| `divergence/bench/schema/bench_item.schema.json` | item schema, JSON Schema draft 2020-12 |
| `divergence/bench_slots.py` | frame from exact lookups (every boundary checked against the golden timeline), seeded draw, CSV + summary, `--check` |
| `divergence/bench_build.py` | owner draft CSV → items; gold re-checked by lookup; nugget offsets by exact search in the local body; nugget phrases only in `_local/` |
| `divergence/bench_validate.py` | rules R01–R15 (schema, slot match, lookup gold, abstain consistency, date expressions, nugget bounds/sha16/caveats, quotas, per-unit cap, pairs, duplicates, active slots, split disjointness); prints ids only |
| `divergence/bench_seal.py` | `--seal` / `--check` of TEST items + nuggets (P10b) |
| `tests/test_bench_{slots,build,validate,seal}.py` | 41 tests on a synthetic 5-record corpus (placeholder words) |

## Draw 1 (superseded)

Superseded by owner decision (b), 21 Nov 2026: the sampler ranked combos by unit load first, which
concentrated cross_act and abstain_boundary. The files were never committed and were deleted with the
owner's yes before Draw 2. The numbers are kept here for the record (LOCAL; computed by code).

Command: `python -m divergence.bench_slots --spec divergence/bench/SPEC-v1.json --out divergence/bench/slots/SLOTS-v1.csv`
→ `wrote SLOTS-v1.csv (167 rows) and SLOTS-v1.summary.json`; then `--check` →
`OK SLOTS-v1.csv sha256 1312c5500f7818390d82e0f819384dd4011354641d74abcd869dd022ab1e2d65`.

### Pairs per stratum and split (n = slots; one draw, seed 20261121)

| stratum | TEST main | TEST reserve | DEV main | DEV reserve | frame combos |
|---|---|---|---|---|---|
| version_lookup | 12 | 3 | 4 | 1 | 8 |
| proviso_condition | 5 | 1 | 1 | 1 | 8 (same as version) |
| cross_act_counterpart | 9 | 2 | 3 | 1 | 16 |
| cross_year_change | 11 | 3 | 4 | 1 | 20 |
| abstain_boundary | 9 | 2 | 3 | 1 | 27 |
| undated (singles) | 8 | 2 | 2 | 1 | 18 units |
| **items (main)** | **100** | | **32** | | |

Unfilled slots: **none** (main and reserve). Reserves used: 0 (no slot has been marked unusable yet).

### Abstain share and categories (main items)

| split | items | abstain items | share | in [0.20, 0.30] | false_premise | stale | answer_unknown | underspecified_intent |
|---|---|---|---|---|---|---|---|---|
| TEST | 100 | 28 | 0.28 | yes | 14 | 6 | 0 | 8 |
| DEV | 32 | 8 | 0.25 | yes | 4 | 1 | 1 | 2 |

Definition: share = items with `should_abstain` true / main items of the split. All TEST
underspecified_intent items are the 8 undated singles.

### TEST items per unit (cap 10; observed max 10)

| unit | items | unit | items | unit | items |
|---|---|---|---|---|---|
| 1961:115BBH | 10 | 1961:56 | 10 | 2025:301 | 3 |
| 1961:158B | 9 | 2025:1 | 4 | 2025:393 | 4 |
| 1961:194S | 8 | 2025:194 | 8 | 2025:400 | 4 |
| 1961:2 | 8 | 2025:2 | 4 | 2025:446 | 4 |
| 1961:285BAA | 4 | 2025:3 | 4 | 2025:509 | 4 |
| 1961:3 | 4 | 2025:536 | 4 | 2025:92 | 4 |

All 18 units appear in TEST. 1961:285BAA and 1961:3 hold undated items only: neither has a FOUND interval in the
frame at 2026-11-15, so no contrast pair is possible for them.

### TEST coverage per stratum (units · boundary kinds)

| stratum | units | boundary kinds (pairs) |
|---|---|---|
| version_lookup | 158B, 194S, 2, 56 (6 items each) | version-change 9, version-span 3 |
| proviso_condition | 158B 2, 194S 2, 2 2, 56 4 | version-change 4, version-span 1 |
| cross_act_counterpart | 115BBH↔194 ×8, 158B↔301 ×1 | act-transition 9 |
| cross_year_change | 115BBH + 10 units of the 2025 Act | tax-year 11 (all false_premise sides) |
| abstain_boundary | 9 units of the 2025 Act | horizon 6, commencement 3 |
| undated | 285BAA 4, 3 4 | — |

Draw 1 DEV: cross_act 115BBH↔194 ×2, 194S↔400 ×1; abstain_boundary commencement 2, horizon 1;
cross_year units 158B, 194S, 56, 2025:194.

### Excluded corpus-gap intervals (not answerable, not abstain items)

- as_of intervals: **11**. before_coverage 7 (the opening interval of each 1961 unit; 285BAA up to 2026-04-01),
  unknown_enactment_date 2 (158B to 2024-09-01, s.3 to 2026-04-01), unprinted_intermediate 2 (s.2, 2024-04-01 to
  2024-10-01).
- tax-year entries: **8**. s.2 TY 2023-24 (unprinted), 285BAA TY 2022-23 to 2024-25 (before_coverage), s.3 TY 2022-23 to
  2025-26 (unknown_enactment_date).

### DEV / TEST overlap (Draw 1)

- Shared (unit, date_a, date_b) keys: **0**. Shared record combinations: **8**.

## Owner decision (b) — ranking change

Options offered after Draw 1: (a) accept; (b) rank combos by prior use first; (c) per-category floors
(not recommended: it targets a count). The owner chose **(b)**: rank candidate combos by
(prior uses of the combo, unit load), lower first, with the seeded `rng.choice` breaking ties
(`divergence/bench_slots.py: combo_score`, test `test_rank_prefers_unused_combo_over_lower_unit_load`).
Draw 1 files were deleted with the owner's explicit yes. The sampler was then run **once** with the same
seed (20261121), and the result is accepted as drawn, with no further redraws.

## Draw 2 (accepted) — `SLOTS-v1.csv`

`wrote SLOTS-v1.csv (167 rows) and SLOTS-v1.summary.json`; `--check` →
`OK SLOTS-v1.csv sha256 aa2b98eef17931d62e2fe43c244eecbb4ded10fda43b6a357360c02386e7ac0f`.

### Pairs per stratum and split (n = slots)

The counts follow from the quotas, so they are identical to Draw 1: TEST 12 / 5 / 9 / 11 / 9 pairs (version,
proviso, cross_act, cross_year, abstain) + 8 undated = 100 items, with reserves 3 / 1 / 2 / 3 / 2 + 2 undated.
DEV 4 / 1 / 3 / 4 / 3 + 2 undated = 32 items, with reserves 1 / 1 / 1 / 1 / 1 + 1 undated. Unfilled: **none**.
Reserves used: 0.

### Abstain share and categories (main items)

| split | items | abstain | share | in [0.20, 0.30] | false_premise | stale | answer_unknown | underspecified_intent |
|---|---|---|---|---|---|---|---|---|
| TEST | 100 | 28 | 0.28 | yes | 16 | 4 | 0 | 8 |
| DEV | 32 | 9 | 0.2812 | yes | 4 | 1 | 1 | 3 |

All TEST underspecified_intent items are the 8 undated singles; DEV has 2 undated + 1 midyear_effect side.

### cross_act mapping spread (pairs)

| split | 115BBH↔194 | 158B↔301 | 194S↔393 | 194S↔400 | 2↔2 | 56↔2 | 56↔92 |
|---|---|---|---|---|---|---|---|
| Draw 1 TEST | 8 | 1 | 0 | 0 | 0 | 0 | 0 |
| **Draw 2 TEST** | 3 | 4 | 1 | 1 | 0 | 0 | 0 |
| Draw 2 DEV | 0 | 0 | 1 | 1 | 1 | 0 | 0 |

The 2↔2, 56↔2 and 56↔92 mappings are absent from TEST. 1961:2 and 1961:56 reach the cap of 10 through
version/proviso pairs, which are drawn first in strata order (INFERENCE from the per-unit counts below).

### abstain_boundary kinds (pairs)

| split | commencement | horizon | repeal | repeal-day |
|---|---|---|---|---|
| Draw 1 TEST | 3 | 6 | 0 | 0 |
| **Draw 2 TEST** | 5 | 4 | 0 | 0 |
| Draw 2 DEV | 2 | 1 | 0 | 0 |

TEST abstain_boundary pairs come from 9 different 2025 units (one pair each). No 1961 repeal or
repeal-day pair was drawn: by then the 1961 units with FOUND intervals are at the cap or carry a higher
unit load (INFERENCE).

### Other strata (Draw 2 TEST)

| stratum | units (pairs) | kinds |
|---|---|---|
| version_lookup | 158B 2, 194S 2, 2 4, 56 4 | version-change 8, version-span 4 |
| proviso_condition | 158B 1, 194S 2, 2 1, 56 1 | version-change 3, version-span 2 |
| cross_year_change | 115BBH + 10 units of the 2025 Act, 1 each | tax-year 11 (all false_premise sides) |
| undated | 285BAA 4, 3 4 | — |

DEV: version 2 ×2, 56 ×2; proviso 56; cross_year 158B ×2, 194S, 2025:301; abstain_boundary 2025:194, 509, 536;
undated 285BAA, 3.

### TEST items per unit (cap 10; observed max 10)

| unit | items | unit | items | unit | items |
|---|---|---|---|---|---|
| 1961:115BBH | 5 | 1961:56 | 10 | 2025:301 | 4 |
| 1961:158B | 10 | 2025:1 | 4 | 2025:393 | 5 |
| 1961:194S | 10 | 2025:194 | 5 | 2025:400 | 5 |
| 1961:2 | 10 | 2025:2 | 4 | 2025:446 | 4 |
| 1961:285BAA | 4 | 2025:3 | 4 | 2025:509 | 4 |
| 1961:3 | 4 | 2025:536 | 4 | 2025:92 | 4 |

### DEV / TEST overlap (Draw 2)

- Shared (unit, date_a, date_b) keys: **0** (guaranteed by the sampler; validator rule R15).
- Shared record combinations (same units, same gold on both sides, different dates): **5** (Draw 1: 8).

### Remaining coverage limits (accepted, not redrawn)

TEST has 0 answer_unknown items and no 1961 repeal / repeal-day abstain pairs. The cap leaves no room for
mappings that involve s.2 or s.56. Report these as limits of the benchmark; do not redraw to change them.

## Checks (real output; key unset; Draw 2 state)

| check | output | result |
|---|---|---|
| `python -m pytest -p no:cacheprovider -q` | `940 passed, 1 skipped in 43.86s` | PASS |
| `python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` | `0` | PASS |
| `python -m divergence.statute_validate --verify` | `statute_validate: 34 records, 0 errors, 0 warnings` | PASS |
| `python -m divergence.statute_census --check` | `golden sweep: OK sweep.json e503aece… D80_TIMELINE.md 9695d8ec…` | PASS |
| `python -m divergence.bench_slots … --check` | `bench slots: OK SLOTS-v1.csv sha256 aa2b98ee…` | PASS |
| `divergence/: python corpus_hash.py --verify` | `Every Tier A file's content matches its frozen hash. No drift.` | PASS |
| `divergence/: python gate0_check.py` | `GATE 0 CLEAR on everything this script can see.` | PASS |
| replay check (`DIVERGENCE_REPLAY=1`, `--out divergence/bench/_local/scratch/ci_replay_check_d2.json`) | facts, missing, attacked, provider=replay, replayed markers: all PASS | PASS |
| Py3.10 syntax scan of new `.py` files (`ast`, feature_version 3.10) | all OK | PASS |
| `SLOTS-v1.csv` contains CRLF | `False` | PASS |

Nothing under `divergence/statutes/` was created or changed (verify + census OK). No TEST items were written.
