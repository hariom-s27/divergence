# divergence/bench — dated-statute benchmark (P10)

Contrast-pair questions about which version of an Income-tax Act provision applies on a
date or tax year, and when a model should abstain. Gold comes from deterministic code
(`divergence.statute_lookup.lookup` at `as_known_on` 2026-11-15), never from a model.

## Files

| path | public? | what |
|---|---|---|
| `SPEC-v1.json` | yes | seed, window, split sizes, strata quotas, per-unit cap, abstain class map |
| `schema/bench_item.schema.json` | yes | JSON Schema (draft 2020-12) for one item |
| `slots/SLOTS-v1.csv` | yes | sampled slots: one row per side (`a`/`b`/`single`), metadata and gold only |
| `slots/SLOTS-v1.summary.json` | yes | counts per split/stratum/unit, abstain share, reserves, excluded gaps |
| `items/DEV.jsonl`, `items/DEV.status.csv` | yes | DEV items (no nugget text) and slot status |
| `_local/drafts/` | **no** (git-ignored) | your draft CSVs |
| `_local/items/TEST.jsonl`, `TEST.status.csv` | **no** | TEST items until the seal (P10-07) |
| `_local/nuggets/<split>.jsonl` | **no** | nugget phrases (copied law text) |
| `_local/scratch/` | **no** | helper scripts and scratch output |
| `TEST-SEAL.json` | yes (P10b) | sha256 of the TEST items and nuggets files |

Never put statute text into a public file. Nugget phrases live only under `_local/`.

## Strata

- `version_lookup`: the same section on two dates that fall under different versions (both answerable).
- `proviso_condition`: the same frame as version_lookup, but the question must turn on a proviso or
  condition. A person checks this; if the record has none, mark the slot `unusable` (see below).
- `cross_act_counterpart`: a 1961 section before 1 April 2026 and its 2025 counterpart (MAPPING.csv) after.
- `cross_year_change`: the same section in two adjacent tax years with different gold.
- `abstain_boundary`: two dates on either side of a boundary where exactly one side must abstain
  (commencement, repeal, repeal day, horizon).
- `undated`: a single question with no date or tax year (always `underspecified_intent`).

Abstain category = the spec's class map applied to `reason_class()` of each gold reason. The priority is
false_premise > stale > answer_unknown > underspecified_intent. Intervals with before_coverage,
unknown_enactment_date or unprinted_intermediate are excluded from the frame.

## Writing items

1. Copy the slot ids you are working on into a draft CSV in `_local/drafts/`, with columns:
   `slot_id, side, status, unusable_reason, question, author, notes,`
   `nugget_phrase_1..3, nugget_occurrence_1..3, nugget_match_1..3, quotes_gazette_1..3`.
   - `side`: `a`, `b` or `single`, exactly as in SLOTS-v1.csv. Write both sides of a pair.
   - `question`: dated sides must name the date (e.g. "1 May 2025") or the tax year ("tax year 2024-25");
     undated questions must name neither. Bare years such as "Income-tax Act, 1961" are fine.
   - Nuggets: an exact phrase from the body of the slot's `gold_record_id` (abstain sides have none).
     If the phrase occurs more than once, set `nugget_occurrence_n` (1-based). `nugget_match_n` is
     exact, regex or numeric. Set `quotes_gazette_n` true only if the phrase deliberately quotes a span
     listed in BODY-CAVEATS.csv.
   - `author`: owner (default) or claude-draft.
2. Build (local bodies required):
   `python -m divergence.bench_build --draft divergence/bench/_local/drafts/dev.csv --created 2026-11-22`
   The command refuses to overwrite existing outputs unless you add `--force`. Errors name slot ids only.
3. Validate:
   `python -m divergence.bench_validate --items divergence/bench/items/DEV.jsonl --partial`
   Drop `--partial` once every slot of the split has been written. Exit 1 means at least one rule failed.

### Unusable slots and reserves

If a slot cannot be written honestly (e.g. no proviso exists), set `status` = `unusable` and
give an `unusable_reason` on that slot's row. The build then activates the next reserve slot
(`T-R..`/`D-R..`) of the same stratum and split in order, skipping any reserve that would break
the TEST per-unit cap. Then write the activated reserve's rows. Never pick reserves by hand.

## Checks

- `python -m divergence.bench_slots --spec divergence/bench/SPEC-v1.json --out divergence/bench/slots/SLOTS-v1.csv --check`
  recomputes the slots and compares them with the committed file (CI runs this step).
- Bench files are LF on every platform (`.gitattributes`: `divergence/bench/** text eol=lf`).

## Seal (P10b, overview)

When all TEST items are written and validated, the owner runs:
`python -m divergence.bench_seal --seal divergence/bench/_local/items/TEST.jsonl divergence/bench/_local/nuggets/test.jsonl`
This records the sha256 of both files, the item count and the spec hash in `TEST-SEAL.json` (committed).
`--check` with the same paths verifies the files later. The TEST items stay local until the
seal decision (P10-07) says otherwise.
