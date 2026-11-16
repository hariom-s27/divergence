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

## Part B2 (2026-11-16): per-row check rules, check code only

PLAIN SUMMARY
- WHAT HAPPENED: Tightened the edition check. A "label" now has to start a unit (not "... and (3) of"), an
  omission marker "[***]" counts as absent, an insert passes when the label count rises, and editions whose source
  does not print letter-suffixed labels are skipped (owner data LABEL_GAP).
- WHAT IT MEANS: 9 rows move fail -> ok; 3 rows (s.56) still fail and await the owner eye check. Body text,
  extractor and versions are unchanged (guard: sha-equal).
- PROBLEMS: none new. The ita1961_2023 s.2 label gap is a source defect (owner eye check, p.4, p.16); version
  act:1961:2:v1 uses that edition's text.
- DECISION NEEDED: owner eye check of s.56 (ita1961_2023 (XII)/(XIII); ita1961_2024n2 (viib)/(xii)).

Changes (REPO, uncommitted): divergence/statute_build.py (`_bound`, `_count`, `_pick`, `check_effect`,
`_check_labels`, OMITTED_MARK_RE, LABEL_GAP); tests/test_effect_check.py (+5 tests).
- LABEL_GAP: (ita1961_2023, 2) = owner eye check 2026-11-16 p.4, p.16; (ita1961_2024n1, 2) = INFERENCE
  (identical s.2 body, 64,270 chars). A skipped edition adds "skipped:<edition>:source_label_gap" to check_note.

Status changes (final regen B1 040252 -> B2 043254; n=50; deterministic)
- fail -> ok, gap editions skipped (after edition = ita1961_2024n2): fa_2022:s3(a), fa_2022:s3(b), fa_2022:s3(c),
  fa_2023:s3(a), fa_2023:s3(c).
- fail -> ok, rule (a) container no longer cut at "and (3) of": fa_2023:s3(b).
- fail -> ok, rule (b) "[***]" marker: fa2_2024:s3(a)(II) (also skips the gap editions as before-editions),
  fa_2026:s35(b)(A) (with rule (a) for a reference "(e) and (f)").
- fail -> ok, rule (c) count rose 1 -> 2: fa_2025_gz:s3(b)(ii).
- Still fail (s.56; awaiting eye check): fa_2022:s16(b)(i), fa_2023:s32(a)(i), fa_2023:s32(b).
- Note-only changes (same status): 11 rows (skipped notes or "count rose from" wording).
- check_status now: ok 25 | fail 3 | no_edition 22 = no suitable edition 1 + no_label 7 + no_rule 14.

Guard: PASS. Version code columns sha canonical = baseline = regen (b7b8fa369ef0...); body sha baseline = regen
(aebe8deb174f...). Files: regen/AMENDMENT-EFFECTS.20261116-043254.csv; census/partC/C3fix-20261116-043418/.
Phase checks (key unset): pytest 555 passed; flake8 strict 0; corpus_hash OK; gate0 CLEAR; statute_validate 0
errors; statute_tables --check 84 rejections, all empty owner_ok; CI replay facts/missing/attacked equal.
Probe tooling: PyMuPDF / pdfplumber / pdfminer were used only for diagnosis (all four extractors miss the labels on
ita1961_2023); no extractor change.

## Part B3 (2026-11-16): s.56 source label gaps
- LABEL_GAP += (ita1961_2024n2, 56) owner eye check pp.301-305; (ita1961_2023, 56) owner eye check p.466. Source
  defects (labels not printed), like s.2 in ita1961_2023. Check code data only.
- Status changes (regen 043254 -> 044706): fa_2023:s32(a)(i) fail -> ok, fa_2023:s32(b) fail -> ok (ita1961_2024n2
  skipped; checked in ita1961_2025). Note-only: fa_2022:s16(a), s16(b)(i), s16(b)(ii), s16(b)(iii), fa_2023:s32(a)(ii).
- Still fail: fa_2022:s16(b)(i), now checked in ita1961_2024n1 s.56, which also lacks the two labels. INFERENCE: same
  source defect (label census 92/23 vs 92/24); not added without an owner eye check.
- check_status: ok 27 | fail 1 | no_edition 22 (no suitable edition 1, no_label 7, no_rule 14).
- Versions whose body comes from a gap edition (REPO, VERSION-DATES code_note): act:1961:56:v1 2023-04-01..2024-04-01
  (ita1961_2023); act:1961:56:v2 2024-04-01..2025-04-01 (ita1961_2024n2); act:1961:2:v1 2023-04-01..2024-04-01
  (ita1961_2023). Their bodies lack the unprinted labels (source defect); versions themselves unchanged.
- Guard PASS (code-column sha b7b8fa369ef0..., body sha aebe8deb174f...; C3fix-20261116-044921). Final regen:
  regen/AMENDMENT-EFFECTS.20261116-044706.csv. Phase checks: pytest 555; flake8 0; corpus_hash OK; gate0 CLEAR;
  statute_validate 0 errors; statute_tables --check 84 rejections, all empty owner_ok; CI replay equal.

## Part B4 (2026-11-16): ita1961_2024n1 label gaps
- LABEL_GAP: (ita1961_2024n1, 2) evidence now owner eye check p.4-5 (was INFERENCE); added (ita1961_2024n1, 56)
  owner eye check p.336. Probe: s.56 clause text is present on p.336 (pypdf); only the two labels are unprinted.
  Edge search missed that page, so eye checks should scroll to the page, not search.
- Status change (regen 044706 -> 050804): fa_2022:s16(b)(i) fail -> ok (three gap editions skipped; checked in
  ita1961_2025). Note-only: fa_2022:s16(a), s16(b)(ii), s16(b)(iii), fa_2023:s32(a)(ii), fa2_2024:s23.
- check_status: ok 28 | fail 0 | no_edition 22 (no suitable edition 1, no_label 7, no_rule 14).
- Guard PASS (code-column sha b7b8fa369ef0..., body sha aebe8deb174f...; C3fix-20261116-050941). Phase checks:
  pytest 555; flake8 0; corpus_hash OK; gate0 CLEAR; statute_validate 0 errors; tables --check 84 rejections, all
  empty owner_ok; CI replay equal. Final regen for Part C: regen/AMENDMENT-EFFECTS.20261116-050804.csv.

## Part C (2026-11-16): owner-decision tool and approved effects merge

PLAIN SUMMARY
- WHAT HAPPENED: Added --apply-owner for both tables, with validation and a per-row non-owner hash guard.
  After APPROVED MERGE, merged only AMENDMENT-EFFECTS.20261116-050804.csv; 50 rows before and after.
- WHAT IT MEANS: Owner decisions produce a reviewable regen CSV; code cells cannot change through this tool.
  The existing --merge behavior and canonical-sha protection are unchanged.
- PROBLEMS: No new blockers. Gate0 has 7 existing warnings; 84 owner rejections remain expected.
- DECISION NEEDED: None for Part C; owner approvals still need filling. NEXT MESSAGE: none required.

Implementation (REPO, uncommitted)
- divergence/statute_tables.py: --apply-owner; strict headers/keys, owner_ok/fix notes, consecutive YYYY-YY,
  closed basis categories, unclear/never_operative/empty-state applicability validation; failures write nothing.
- Output is exclusively a new regen CSV; canonical columns are preserved and only existing owner columns change.
  Non-owner row hashes are checked before/after updates and CSV serialization, before any output write.
- VERSION-DATES key is record_key (not version_id); owner_note already exists, so fix requires a note there too.
- tests/test_statute_tables.py: 40 invented-data cases added (8 -> 48): valid/invalid batches, no partial writes,
  hash-guard trips, existing/missing version note column, regeneration owner carry and unchanged merge SHA guard.

Owner-approved pre-merge correction (LOCAL)
- The two owner_note cells on fa_2026:s84(c)/renumber and /insert were already present and identical in both files:
  "owner reading: coupled operations; ITD footnote agrees (secondary)". All other owner cells are empty.
- Replaced the erroneous all-empty rule with cell-by-cell owner equality and owner_target empty everywhere.
- Precheck PASS: 50 identical effect_ids in identical order; target_unit changed 22 cells; new_units populated 16.
  Every other original canonical column unchanged. New position/scope/check_status/check_note populated 50 each;
  owner_target populated 0. Candidate checks: ok 28 / fail 0 / no_edition 22. b01 application skipped per addendum.

Merge counts and hashes (LOCAL; exact approved candidate byte match, no line-ending difference)
- Effects rows: 50 -> 50; VERSION-DATES remains 34 rows. Merge preview: 50 changed, 0 added, 0 removed.
- Canonical file before: 215704d51101722f42018a2e803513cc5cc05edc88e4e8192e1f008ff02f4686
- Canonical file after:  ebcf9fa45ecf721982b73505627130dc5b658bd2794f4d46abac726711ec853c
- Code columns before: cea378c5bde68200c510ef31cff75d17c15d617c016984eee4357527d721a947
- Code columns after:  dabf38f9e8a3f99283052221a1f75404063b54ac0ce0bab2a26434ebf12ac8c6
  Code hash = SHA256 of compact UTF-8 JSON of ordered rows of (column name, value), excluding owner columns.

Phase checks (LOCAL; FEATHERLESS_API_KEY unset; no network/model/API calls)
- python -m pytest -p no:cacheprovider -q --tb=line: 595 passed in 43.43s; full suite run once after merge.
- python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics: 0.
- divergence/: python gate0_check.py: GATE 0 CLEAR (0 blockers, 7 existing warnings).
- divergence/: python corpus_hash.py --verify: all 17 frozen Tier A hashes match.
- python -m divergence.statute_validate: 0 records, 0 errors, 0 warnings; no manifest, so --verify not applicable.
- python -m divergence.statute_tables --check: effects rejected 50, versions rejected 34; exit 1 expected.
  All 84 reasons are "owner_ok '' not in yes/fix"; --counts confirms all owner_ok empty.
- guard_b.py: PASS, 0 differences; versions 34/34, bodies 26/26; output C3fix-20261116-053057/GUARD.md.
  Version code SHA b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7;
  body SHA aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d (baseline = regen).
- Offline CI replay: facts/missing/attacked equal frozen records field by field; provider and all node markers replay.
  Output: _local_text/scratch/C3fix/PartC-ci-replay-0d67b150fd.json (outside frozen runs/).

SELF-AUDIT
- Changed: statute_tables.py, tests/test_statute_tables.py, AMENDMENT-EFFECTS.csv, this report; no code cells hand-edited.
- Frozen corpus/replay_cache/runs, named preregistration docs and existing DECISION-D*.md unchanged vs 3fbc388.
- TEST seal not edited; no holdout contents inspected. _local_text tracked files: 0; outputs remain ignored/untracked.
- Earlier targeted tests: sandbox temp denial, then escalated retry 48 passed. Initial owner-emptiness failure stopped
  work until owner-authorized diagnosis corrected the rule. No further failures; git diff --check clean.
- No network, live model/API calls, keys printed, deletion, reset, Auto mode, commit or push; owner runs commit commands.
