# P09 C3-fix report

## Part B (2026-11-16, branch feat/p09-ingest @ f1d967c; code + regen only, canonical tables unchanged)

PLAIN SUMMARY
- WHAT HAPPENED: The effects parser now records where a change happens (position) separately from what it creates
  (new_units) and whether it touches words or a whole unit (scope). A code-only per-row check compares each row with
  the extracted editions. The ledger was regenerated outside the canonical files.
- WHAT IT MEANS: "after clause (47)" no longer reads as a change to clause (47), and word-level edits are no longer
  recorded as unit edits. Version texts, ids and dates are unchanged (guard: sha-equal).
- PROBLEMS: 12 rows fail the check. Most come from editions whose extracted s.2 text lacks the lettered clauses, or
  from small labels that repeat inside a container. These are not parser errors; the owner decides with owner_target.
- DECISION NEEDED: Part C (merge + owner review); see HANDOFF_B.

Changes (REPO, uncommitted)
- divergence/act_parse.py: `locate`, `block_new_units`, `successors`, `_verb_segments`, `_inner_headings`, `_instr`,
  `_unit_label` replace `_units`. New columns: position, new_units, scope, check_status, check_note, owner_target.
  owner_target is in OWNER_COLUMNS (merge carries it). apply_owner_splits gives each split row its own verb clause.
- divergence/statute_build.py: `effect_checks`, `check_effect`, `container_segment`, `_count`, `_bound`. build()
  keeps the per-section edition list and a body sha per version. New flag `--check-effects` (writes regen only).
  `_inserts_section` is unchanged.
- tests/test_act_parse_position.py, tests/test_effect_check.py (invented text; real-id tests skip without local PDFs).

Definitions (owner-approved rules 1-5)
- Edition after the effect: the first FOUND edition with knowledge date >= assent_date that does not mark the effect
  pending. Before: the last FOUND edition with knowledge date < assent_date.
- A label counts only where it starts a unit, searched inside the top digit-led container (else the whole section).
  proviso/Explanation new units are compared by count. An anchor without a label gives no_label.

Numbers (code: guard_b.py over the final regen file; n = 50 rows, no seeds; deterministic)
- Rows per pattern: insert-after-unit 13, insert-after-words 6, insert-after-section 3, substitute-for-unit 11,
  substitute-for-words 7, substitute-for-section 2, omit-in-unit 3, omit-in-words 4, renumber 1, unparsed 0.
- Rows changed per column (vs canonical): target_unit 22, new_units 16, position 50, scope 50, check_status 50,
  check_note 50 (the last four are new columns). wef/deemed_from/commencement/quote_sha256/operation/ids: 0.
- check_status: ok 16 | fail 12 | no_edition 22 = no suitable edition 1 + no_label 7 + no_rule 14
  (substitute/renumber have no check rule).
- Fail ids: fa_2022:s3(a) s3(b) s3(c) s16(b)(i); fa_2023:s3(a) s3(b) s3(c) s32(a)(i) s32(b); fa2_2024:s3(a)(II);
  fa_2025_gz:s3(b)(ii); fa_2026:s35(b)(A).
- Fail causes (LOCAL, observed): the ita1961_2023 and ita1961_2024n1 s.2 bodies contain no lettered clause labels
  ((12A), (42C), (47A), (28CA) ... absent) -> 6 s.2 fails. Labels such as (iv), (f), (c), (d) repeat inside the
  container -> 3 fails. 3 more are not yet traced (fa_2023:s3(b), s32(a)(i), s32(b): label missing in ita1961_2024n2).

Differences from the owner's expected values (the text was trusted)
- fa_2022:s16(b)(i): new_units = (XII);(XIII). The inserted text has an Explanation after (XIII), but the flat text
  does not show whether it sits inside (XIII) or beside it, so under the leading-labels rule it is not listed
  (owner_target can add it).
- fa_2022:s28: new_units = 115BBH;115BBI (the inserted text has two sections).
- fa_2026:s35(c): target_unit = long line[2] > sub-clause (E) > item (II); the instruction names no clause.

Guard (statute_build --propose twice with the same code; canonical effects vs final regen)
- Version code columns sha: canonical = baseline = regen (b7b8fa369ef0...); body sha baseline = regen
  (aebe8deb174f...); 0 differences. RESULT: PASS.

Phase checks (key unset)
- pytest: 550 passed (502 before). flake8 strict: 0. corpus_hash --verify: OK. gate0: CLEAR.
- statute_validate: 0 records, 0 errors. statute_tables --check: 84 rejections, all "owner_ok '' not in yes/fix"
  (expected: owner columns are empty). CI replay: facts/missing/attacked equal to runs/21aug (field-level).

Safety: no network, no model/API calls, no commit/push, no keys, no deletes; canonical CSVs and frozen items
unchanged (git diff vs HEAD / 3fbc388 empty for them).
