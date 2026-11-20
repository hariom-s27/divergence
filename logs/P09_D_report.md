# P09 D - Part A compact report

Agent: Codex, GPT-6 based.
Owner-reported UI: GPT-6.1 Sol; effort High; approval Ask for approval.
Runtime model id / effort are not independently exposed; sandbox workspace-write; reviewer auto_review.
Compacted 2026-11-20 (Asia/Calcutta); measurements retained from 2026-11-19; A1 additions measured in this run.

Historical stop notes

Runpy: the earlier invocation failed before completion; the corrected invocation was approved.
The complete history is retained byte-for-byte in the local archive below.

Gazette cache: the earlier cache interpretation caused a stop; the owner corrected it.
265620 and registered instruments may use pdf_pages in memory; edition cache misses still STOP.

A3 audit: the first draft had 80 unexplained hunks; the initial six-row editorial claim was withdrawn.
Restoring existing C3 preparation and classifier produced 15 content rows; all 17 C3 rows were reconciled.

## Part A

PLAIN SUMMARY

- What happened: the full report was moved unchanged; this compact report and a 15-row v2 were created.
- A1: act:1961:56:v2; Specified=0; Specifed=0; case-insensitive whole tokens specified=0; specifed=0.
- A1: requested Explanation present=yes; zero-based character offset=19452.
- A2: 265935:36 items/2 spine; 269669:53/4; 245119:7/1; CORRIGENDUM-ITEMS.csv has 7 spine rows.
- A3: original 80 unexplained rows retained; corrected v2 has 15 unexplained content rows.
- A4: TLA 2025 apparatus count=0 each for 1961 sections 2,3,56,115BBH,158B,194S,285BAA.
- A5: LABEL-GAPS: act:1961:2:v1=7; act:1961:56:v1=2; act:1961:56:v2=6; total=15; no records beyond the known three.
- A6: 7 edition hashes computed and byte identities rechecked; historical full-hash matches=0; conflicts=0.
- A7: manifest dry run: 50 existing + 4 future = 54 files.
- A8: owner should add this exact bibliographic line; the saved date remains 2026-11-19:
265935.pdf · Corrigenda, Income-tax Act, 2025 (30 of 2025), 3 Sep 2025 · https://egazette.gov.in/WriteReadData/2025/265935.pdf · date saved 2026-11-19
- What it means: v2 replaces no file and remains an owner-review draft; all owner columns are empty.
- Problems: source label gaps and owner classifications remain; the stored FA2023 unit is (xi), not (xii).
- Decision needed: classify the 7 corrigendum rows and 15 v2 differences; add the A8 source line.
- Next message: owner-filled table paths and decisions; Part B has not started.

Archive integrity

Archive: divergence/statutes/_local_text/census/partD/20261119-172809/P09_D_report_FULL_A.md
Original size: 68,476,794 bytes; LF line count: 447,232.
SHA256 before move: 7a74022c5332d5fea87172f4a3e250194fe754e20b09e2c7bcaeebcb66836e70
SHA256 after move:  7a74022c5332d5fea87172f4a3e250194fe754e20b09e2c7bcaeebcb66836e70
Result: equal; archive was moved without editing, deleting or overwriting.

A1 additional read-only checks

Record: act:1961:56:v2; body path resolved with statute_validate.body_path (divergence/statute_validate.py:208).
Case-sensitive substring counts: Specified=0; Specifed=0.
Case-insensitive token rule: regex word boundaries with re.IGNORECASE on the original decoded body.
Token counts: specified=0; specifed=0; both offset lists are empty.
Explanation to s.56(2)(xii), including the requested formula: yes.
Original-body zero-based Explanation offset: 19452; formula offset: 19597.
Explanation block SHA16: f4ba1c67b4da3a36.
Presence check: exact corrigendum phrase SHA16 identity, NFKC/case/whitespace normalization, and three-variable formula signature.
The following (xiii) heading bounds the block; the printed (xii) heading is absent in this body.
Normalization is used only for this presence check; raw token counts and the A3 comparison are unchanged.
245119 spine row, reproduced as metadata:
item_key: corr_fa2023:p29l1
section: 56; unit: sub-section (2) > clause (xi)
record_ids: act:1961:56:v1;act:1961:56:v2;act:1961:56:v3
old_in_body: {"act:1961:56:v1":0,"act:1961:56:v2":0,"act:1961:56:v3":0}
new_in_body: {"act:1961:56:v1":0,"act:1961:56:v2":0,"act:1961:56:v3":1}
Stored unit (xi) is preserved exactly; it was not corrected or used to relabel the requested (xii) check.

A2 - item counts

| PDF | Items | Spine | Outside spine |
|---|---:|---:|---:|
| 265935 | 36 | 2 | 34 |
| 269669 | 53 | 4 | 49 |
| 245119 | 7 | 1 | 6 |

A3 - original versus corrected draft

All original 80 proposed classes: unexplained=80; corrigendum=0; amendment=0; itd_editorial=0; itd_error=0.
All corrected 15 proposed classes: unexplained=15; the other four classes=0.

| Section | Original v1 | Corrected v2 |
|---|---:|---:|
| 1 | 0 | 0 |
| 2 | 7 | 4 |
| 3 | 0 | 0 |
| 92 | 0 | 0 |
| 194 | 6 | 0 |
| 301 | 0 | 0 |
| 393 | 60 | 7 |
| 400 | 0 | 0 |
| 446 | 0 | 1 |
| 509 | 0 | 0 |
| 536 | 7 | 3 |
| Total | 80 | 15 |

| Stage | Content hunks | Net change |
|---|---:|---:|
| C3 Gazette versus ITD 2025 | 17 | - |
| Switch to ITD 2026 | 84 | +67 |
| Helper Gazette canonicalization | 84 | 0 |
| Apply September spine items | 81 | -3 |
| Apply January spine items | 77 | -4 |
| Apply 16 FA2026 effects with C3 ITD preparation | 15 | -62 |
| Original helper ITD canonicalization | 80 | +65 |

Counts are net hunks, including splits/merges; they are not independent legal-change counts. TOLA2026 effects=0.
Method: exact C3 ITD preparation at divergence/statute_build.py:905-908.
Unchanged word_hunks:182; marks_only:214; _alnum:223; gazette_class:864 in that same module.
Six original s194 hunks returned content:884; their resegmented counterparts return itd_addition at table-furniture branch:877-878.
No new filter or threshold; the helper and classifier remain unchanged.
v2 materializes the archived corrected_preview_rows produced by that audited method; extraction was not rerun for A3.

C3 reconciliation - 17 original rows; IDs and classes only

| C3 SHA16 | C3 class | With new corrigenda | Aligned preview SHA16:class |
|---|---|---|---|
| 90a1d83cadaac911 | content | content | 90a1d83cadaac911:content |
| 769b157db1b2ea8c | content | content | 769b157db1b2ea8c:content |
| 1d058f3a49580ed1 | content | content | 1d058f3a49580ed1:content |
| 542cdc6ecbfa4f27 | content | corrigendum | none |
| 43313fec4a8ed8ac | content | content | none |
| 8505ef3946377e8b | content | content | none |
| 5dbda163005b089a | content | content | 33410c69bc459cd8:format |
| 7d4478c559067e47 | content | content | 7d4478c559067e47:content |
| 032d932e5803abf6 | content | content | fb5f97c86c27aa13:content |
| 04ca6540edc66d66 | content | content | 04ca6540edc66d66:content |
| a19d5fbf04b8fc9c | content | content | a19d5fbf04b8fc9c:content |
| a19361d3b4c96e74 | content | content | b446c47785bc30fa:itd_addition |
| d176bb3cd60c9109 | content | content | 765d4b46174e3c7a:format |
| d7571a8288e71e36 | content | content | 2122687890e529d1:format |
| 2e96ecaf32ecadff | content | corrigendum | none |
| d9a830ffacce67c8 | content | corrigendum | none |
| 3bc1d541e6b2c29c | content | content | 3bc1d541e6b2c29c:content |

Original C3 classifier: content=17. With new corrigenda: corrigendum=3, content=14.
Eight original rows retain content overlaps; nine do not. New/resegmented rows explain why v2 totals 15.
Legacy helper proposals were heuristic labels, not C3 classifier outputs, and are not used for v2.

A4-A5

A4 apparatus counts: 2=0; 3=0; 56=0; 115BBH=0; 158B=0; 194S=0; 285BAA=0.
A5 ledger/continuity gaps: act:1961:2:v1=7; act:1961:56:v1=2; act:1961:56:v2=6.
LABEL-GAPS.csv rows=15; records=3; new records beyond the known three=0.

A6 - edition SHA256

| Edition | SHA256 | Historical matches | Conflicts |
|---|---|---:|---:|
| ita1961_2023 | 90860f3cb806137512aeaccc294e6d01edbf349430635b0e9d7050f8c7b3c68d | 0 | 0 |
| ita1961_2024n1 | b4d9453d34248d28288f76140e6a1ff89739deea73a3124ad77e8aeca84ccc88 | 0 | 0 |
| ita1961_2024n2 | e55d9d0c847f87a6dc1298ee975e893915f86d198f56395d0fa4f9be67144d19 | 0 | 0 |
| ita1961_2025 | 77e10fc161a3c04928c2dee387fbcec0b5dc4fd1cf2d72fa90cf64d9f1a8e853 | 0 | 0 |
| ita1961_2026 | 73d264fd05bc3b19ee003f399aeb50faf7ea36a42f345fa94ebb9b3a2ad0cb93 | 0 | 0 |
| ita2025_2025 | 548111b39d1e7d907ba7b117fd52b8b9db2afa3213dbaecdbd97f9dd4e459190 | 0 | 0 |
| ita2025_2026 | ee2a32197b8935636c97efbbbf6fc198b3d30a5694bc9ce2c28c6764fa65ab7f | 0 | 0 |

All seven current PDF hashes equal the hashes measured in the archived Part A probe.
The archived historical search found no matching full hashes and no conflicting explicit source-PDF hashes.

A7-A8

Manifest: records=34; public text=0; fixed existing tables=5; schema=1; owner CSVs=10.
Existing=50; future=4; proposed total=54. This run writes no manifest.
MANUAL-SOURCES format has four fields separated by a middle dot; exact owner line appears in PLAIN SUMMARY.
MANUAL-SOURCES.txt itself remains unchanged.

Local draft files

All paths below are relative to the partD folder named in the archive path.
CORRIGENDUM-ITEMS.csv: 7 rows; unchanged.
SHA256: 50832d720ea107f9a1deb072d13f76390dec7d0d2204d6ce8e2d19b937ecdfe9
ITD-GAZETTE-DIFFS.csv: original v1; 80 rows; unchanged.
SHA256: 29aa636015893fc18e4742a179182bfa63616ce525a721c49a4bf5f27368bbfe
ITD-GAZETTE-DIFFS.v2.csv: 15 content rows; same columns; owner_class/owner_ok/owner_note empty.
SHA256: f448c2242b29c10e33a77b5304ecc211ab57ad4a442eaf28fe7bc87ef746aaab
LABEL-GAPS.csv: 15 rows; unchanged.
SHA256: de598779773f9562ed526365d937d90706395a3bb57c2f421935f17212c784bc
Helper unchanged SHA256: dc4f3d62d3c038f91f1a599df47dd958b7ea2f7a84e84a781023dce2a833cc72
Classifier module unchanged SHA256: 022830d2d024f81b3c9478436645ad11cfa16893a097dd6d4c16d8a58273a50c

Protected snapshot and bodies

Scope: every file under divergence/statutes/_local_text except the entire census/partD subtree.
Before/after result: unchanged; 7,525 files; added=0; removed=0; changed=0.
Evidence: divergence/statutes/_local_text/census/partD/20261119-172809/PART-A-SNAPSHOT.json
Snapshot-file SHA256: 8037702a22ef89daa2463b878fc708eb2ed6ddcc7070887406bb60681bec990c
The evidence file contains archived before/after hashes and this run before/after hashes; all four maps agree.
31/31 bodies verified (26 guard + 5 direct).
This run rechecked all 31 local body file SHA256/character counts against their records using the code-resolved paths.
The five never-operative IDs: act:2025:2:v1; act:2025:393:v1; act:2025:400:v1; act:2025:446:v1; act:2025:536:v1.
All five direct bodies match; character counts=0. Part C must retain the same 26+5 restore-test split.
Code guard: 34 rows; equal; recomputed in this run.
SHA256: b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7
Body guard: 26 edition-built bodies; equal in the archived completed guard run; no build/extraction rerun in this compaction.
SHA256: aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d
The full protected snapshot matches the archived guard/audit inputs byte-for-byte.

Commands and controls

Read-only preparation: Test-Path; rg; Get-Content; python -B metadata/source reads.
Execution: one inline Python process via python -B -c; program fragments supplied in memory; no on-disk runner.
In-process operations: guarded open/read; SHA256 snapshots; body_path; regex token checks; existing in-memory pdf_pages for 245119.
A1 source phrases were hash-identified with existing corrigendum_items; only counts, offsets and SHA16 were emitted.
PowerShell Test-Path checked all runtime input/output paths; path lists stay outside this compact report.
Move-Item -LiteralPath logs/P09_D_report.md -Destination
  divergence/statutes/_local_text/census/partD/20261119-172809/P09_D_report_FULL_A.md
Before/after move SHA256 was checked in-process; only three new outputs use exclusive creation.
Git commands: git log --format=%h -1; git status --short; git diff --stat; git diff --check.
Frozen check: git diff --stat -- divergence/corpus divergence/replay_cache divergence/runs; empty.
Tracked diff --stat is empty; HEAD remains 8dfaacc. Owner checks/tests listed in chat were not run by this compaction.
Git global-ignore and .pytest_cache permission warnings came from the sandbox; the owner reruns git status locally.
Network calls=0; model/API calls=0. No commits, tags, pushes, deletions or record edits.
File writes outside the three new approved outputs and network operations were blocked in-process.

Deviations and validation

Current original report line count is 447,232 LF lines, versus the owner-estimated 445,968; its byte count agrees.
Early attempts stopped before file changes: the guard blocked a subprocess pipe; a diagnostic misread a parser string field.
The pipe distinction and parser field handling were corrected in-memory; no helper or CSV was edited.
Historical attachment path-check exception remains in the full archive; all current runtime paths were checked.
A8 retains the explicitly requested bibliographic source title; no extracted instrument wording is included.
Report scan: no fenced extraction blocks, quote blocks, raw body/old-word/new-word payload fields or long lines.
Report is constructed from allowlisted metadata; body-overlap scan passed with A8 bibliographic metadata excluded.
Final size: 14357 bytes; lines: 238; maximum line length: 150 characters.

SELF-AUDIT

1. Plan gate respected before every write? Yes; explicit APPROVED covers the move and three new files, plus A1 reads.
2. Zero network and zero model calls? Yes; network audit blocking; no API/LLM invocation.
3. Frozen paths untouched? Yes; tracked and frozen git diff --stat are empty; protected snapshots agree.
4. No law text in chat/report/committed files? Yes; counts/hashes/IDs only, plus explicitly requested A8 bibliographic metadata.
5. Both guards equal? Yes; code recomputed; archived body guard equal, with identical protected inputs and 31 direct file checks.
6. No commit/push/tag/merge by agent? Yes; only read-only Git commands.
7. No deletion; no hand-edited records? Yes; archive moved unchanged; no record writes.
8. Every path seen or Test-Path checked? Yes for this run; historical attachment exception is retained above.
9. Every number came from a command shown? Yes; archived probe metadata and this inline verification; no invented counts.
10. Deviations listed? Yes; line-count difference, early no-write stops and historical exception disclosed.

STOP: compact Part A ready for owner review; original CSVs preserved; Part B not started.

## Part B - amended preview count STOP

PLAIN SUMMARY

- What happened: approved implementation began; the amended metadata preview expects 30 changed records, versus 29 supplied by the owner.
- What it means: implementation is incomplete. No tests, v3 comparison or official --update dry run were executed.
- Problems: excluding the FA2023 disposition note from 56:v1 does not exclude its four URL changes or counterpart note.
- Decision needed: confirm 30 changed records, or specify which otherwise-approved metadata changes to exclude.
- Next message: confirm the corrected expected count and continuation. Record writes still require APPROVED WRITE.

Agent header

- Codex, GPT-6 based; owner-reported UI GPT-6.1 Sol / High / Ask for approval.
- Sandbox workspace-write; reviewer auto_review; exact runtime identifiers not independently exposed.

Amended preview (not an official --update dry run)

| Measurement | Expected/observed |
|---|---:|
| Owner expected changed record files | 29 |
| Computed changed record files | 30 |
| Record notes changed | 13 |
| Counterpart notes changed | 17 |
| URL cells changed | 53 |
| Lookup flag changes | 1 |

- FA2023 item touches act:1961:56:v2 and v3 only. No disposition note is added to v1.
- act:1961:56:v1 still needs URLs for fa_2022:s16(a), s16(b)(i), s16(b)(ii), s16(b)(iii), plus counterpart.notes.
- Full metadata preview: divergence/statutes/_local_text/census/partD/20261119-172809/B-v3/record-diff.json.
- Partial source edits: statute_sources.py registration/parser; statute_records.py projection/disposition helpers; statute_ingest.py note preservation.
- R2/plural implementation, v3 rules freeze, tests and production provenance generation remain pending.
- SOURCES.json, disposition/census CSVs and all 34 record files were not written. No body or placeholder file was written.

Protected snapshot

- Scope: all _local_text files except census/partD; 7,525 before and after; unchanged.
- Evidence: B-v3/protected-before.json and B-v3/protected-after.json; SHA256 values below.
- protected-before.json: 3f203c6eb75b2662cb1d41b5c8bc9090e5439190e9167728a43029e4786ba57a
- protected-after.json: b369cf571b092bd4ee8487dd0f2928b4e5d7f492662c4b91fa296c7810447db6
- record-diff.json: 26d7dba01f954bbb8a9aa225df63a416d4578523c63295ce386b804be6285375

Commands/controls

- Read-only Test-Path/Get-Content/source inspection and python -B metadata previews; source edits only within the approved Part B files.
- Before/after protected snapshot programs and the amended metadata preview were run with python -B.
- No network, model/API calls, tests, git state changes, installs, deletes, commits or pushes.
- Full Part B run guards were not rerun: this STOP occurred before the probe. No new body-verification claim is made.
- Required future wording: 26/26 bodies verified by guard; 5/5 never_operative placeholders empty as designed.

SELF-AUDIT

1. Plan gate respected? Yes; owner APPROVED with four amendments before implementation.
2. Zero network and model calls? Yes; local metadata/source work only.
3. Frozen inputs untouched? No frozen-file writes; protected snapshot unchanged. Git diff verification pending.
4. No extracted wording in chat/report? Yes; metadata/counts/IDs/hashes only.
5. Both guards equal? Not rerun in this attempt; prior values are unchanged historical evidence, not a new run.
6. No commit/push/tag/merge? Yes.
7. No deletion or hand-edited records? Yes; no record files written.
8. Paths verified? Yes; source/output paths were previously seen or Test-Path checked.
9. Numbers generated by shown commands? Yes; amended pure metadata preview and complete snapshots.
10. Deviations listed? Yes; owner expectation 29 differs from computed 30; remaining implementation stopped.

Post-report read-only Git verification: frozen-path diff empty; changed paths are the three listed source files and this report.
Sandbox warnings: global ignore and .pytest_cache permission warnings; owner reruns git status locally. Git also reported its existing LF/CRLF checkout policy.

Part B - implementation and pre-write STOP (2026-11-20)
PLAIN SUMMARY
- What happened: implemented approved metadata projection and frozen R1-R6; v3 and the --update dry run completed.
- What it means: preview matches records 30, record notes 13, counterpart notes 17, URL cells 53, lookup flags 1.
- Problems: v3 has 109 rows but 108 unique row IDs; duplicate v3:aa3e0d898febabab is at data rows 70 and 89.
- Decision needed: approve an identifier/reconciliation audit and uniqueness fix, with comparison rules and codebook unchanged.
- Next message: resolve this STOP first; owner nature confirmations and literal APPROVED WRITE remain pending.
Agent: Codex; owner UI reports GPT-6.1 Sol / High / Ask for approval; workspace-write; auto_review.
Results (original arithmetic stop above remains history)
- Sources: 19 registered instruments; check_sources 0 differences; seven edition identities retained.
- Dispositions: 7 approved; 6 typo, 1 substantive; all pre_commencement; owner_ok=yes for all 7.
- Commencement: act_s1=2026-04-01; effect:fa_2023:s32(b)=2024-04-01; dates computed from primary inputs.
- FA2023 touches 56:v2 and v3 only; 56:v1 retains four FA2022 URL fills and its counterpart note.
- Preview: only approved metadata fields change; bodies, status, dates, identifiers and amendment membership do not change.
- Canonical records: all 34 unchanged; no backups or record rewrites performed.
- 26/26 bodies verified by guard; 5/5 never_operative placeholders empty as designed.
- Code guard EQUAL: b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 (34 rows).
- Body guard EQUAL: aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d (26).
- V3: 15 baseline plus 94 new rows; 104 kept; removed R2=2, R5=3; R1/R3/R4=0; R6 removes none.
- Kept origins: itd 99, instrument 5. Removed origins: pipeline 2, instrument 3. All owner columns remain blank.
- Kept itd proposals: substantive 85 (no certificate), accidental 14 (plural 2, markup/Act reference 12).
- Identifier STOP: 99 kept itd rows have 98 unique IDs; the two duplicate-ID entries are both proposed accidental.
- Cause: historical hunk_key hashes words/context without absolute position; new IDs reuse that key. C3 remains unchanged.
- Full word-free table, each proposal/reason and 30-record field-count summary: B-v3/STOP-preview.md.
- Full twelve-column table: divergence/statutes/census/ITD-GAZETTE-DIFFS.csv. Preserved unchanged after this STOP.
- R2 uses assent<=2026-03-30 AND wef<=2026-04-01. Headings 11; eligible effects 14; applied 10.
- Deferred: fa_2026:s84(c)/renumber and fa_2026:s84(c)/insert, both wef=2027-04-01; both editor_note=yes.
- Deferred cross-check: 2 agreements, 0 disagreements; no rule adjustment.
- Unanchored target_not_unique: fa_2026:s35(c), s84(a), s84(b)(i), s84(b)(ii); not applied.
- Frozen rule functions 13/13 unchanged; source files statute_build.py and statute_sources.py remain byte-identical to run start.
- One blank-line-only test lint fix after freeze is AST-identical; evidence B-v3/test-style-proof.json.
- Reusing the old CLI capsule now refuses that raw test-file hash difference; the original capsule and outputs are preserved.
Checks and commands (all from repo root; no network or model/API calls)
- python -B B-v3/run_part_b.py prepare / freeze / v3 / dry-run (full path is the local Part D directory above).
- Actual CLI main(["--update"]) under in-process write/network blocking: exit 0, write=False; identical 30-record diff.
- python -B -m pytest: sources/records/ingest/v3 modules; not test_real_spec_case and not test_local_v3_regression.
- Result: 116 passed, 33 deselected; cache disabled; basetemp B-v3/pytest-unit-final; 32 existing-record cases await writes.
- P09D_REAL_V3_REGRESSION=1; pytest tests/test_statute_build_v3.py -k test_local_v3_regression: 1 passed, 49 deselected.
- Strict flake8 changed files: 0. Full tree: 958 = standing 740 + existing Part A local helper 218; Part B adds 0.
- Read-only: Test-Path; Get-Content; rg; Python snapshots/hash/AST/CSV checks; git status/diff/show; frozen-path diff --stat empty.
- Historical sandbox warnings: global ignore and .pytest_cache permissions; owner reruns git status locally. LF/CRLF policy warnings noted.
Protected snapshot and hashes (full maps local only)
- Entire _local_text except census/partD: 7,525 files before/after, unchanged. Both snapshot maps match exactly.
- B-v3/protected-before.json SHA256: 3f203c6eb75b2662cb1d41b5c8bc9090e5439190e9167728a43029e4786ba57a
- B-v3/protected-after-prewrite.json SHA256: 66346d46bd2d6a936e271116003a5278248a537589d35ebc7f05cbfb5ec388f6
- Canonical 34-record byte-map SHA256: 602e26da219664dd5a38c5fced29ae87073e763d7bfd91772f18315e997d6116
- B-v3/v3-summary.json SHA256: 47d0dff3d3f6eaefc0c5b003e3d21c1834150d7a8b96acbe704bf89fe8291a5d
- B-v3/update-dry-run.json SHA256: 4c5bf6ab360753b6e8b7f72c8dc7340bc621627a376b5476c5f7d5243149cc16
- B-v3/rules.json file SHA256: 5832bf405419ebe82604fbe889f3ddab535dfe59bc779eafe00134cf57449115
- V3 canonical rules-object SHA256: 13c52e9e7686208e39229a4df03b87c0cd3bacc8c4573017ca259a609fc5b7b7
- Disposition SHA256: d701fd5bcb972e97ffe3303fa32e7e0aae0cae8f12f7812f010147c11ae768e4
Deviations/limits
- Duplicate IDs prevent unambiguous confirmation; no corrective comparison or identifier edit after seeing results.
- The exact-hash real-input regression passed but does not establish row-ID uniqueness; a uniqueness assertion is needed.
- Full-tree lint exceeds the original 740 because of the preserved Part A helper; no new Part B lint findings.
- Path precheck omission: flake8-final.json was created inside the approved B-v3 directory before a separate Test-Path.
- No commit now. Owner checks and deferred separate git add commands are in STOP-preview.md; run after completed Part B only.
SELF-AUDIT
1. Plan gate respected? Yes; owner approvals and 30-record correction cover implementation/runs; this identifier issue stops further changes.
2. Zero network/model calls? Yes; local-only runs; in-process write/network audit guards on production runs.
3. Frozen paths untouched? Yes; protected map unchanged; limited git diff --stat empty; ledger/date files unchanged.
4. No law text in chat/report/public outputs? Yes; IDs/counts/hashes and metadata only; no extracted blocks.
5. Both guards equal? Yes; prepare() in v3 and dry run; code 34 rows, body 26; 5 empty placeholders independently verified.
6. No commit/push/tag/merge? Yes; read-only git only.
7. No deletion/hand-edited records? Yes; all 34 record bytes unchanged and protected map unchanged.
8. All paths seen or Test-Path checked? No; one local lint artifact omission is listed above; approved directory scope respected.
9. Every number command-generated? Yes; v3-summary, dry-run/CLI evidence, pytest/flake8 outputs, snapshots and CSV identifier scan.
10. Deviations listed? Yes; duplicate ID, style-only capsule hash limitation, historical lint delta and path precheck omission.

Part B - read-only diagnosis and repair PLAN (STOP)
PLAIN SUMMARY
What happened: unchanged in-memory replay exactly reproduced v3. What it means: the extra rows include implementation artifacts, not 89 established legal differences.
Problems: R3 discards unique scope witnesses; R4/R5 reintroduce furniture; IDs repeat. Decision needed: approve bug-fix PLAN. Next message: APPROVED plan; no owner classifications or record writes.
Counts v2/kept-v3: s1=0/0; s2=4/11; s3=0/0; s92=0/0; s194=0/6; s301=0/0; s393=7/80; s400=0/0; s446=1/0; s509=0/0; s536=3/7; total=15/104.
Stages v2/R1/R2/R3/R4/R5: 15/15/15/27/27/104; net changes 0/0/+12/0/+77. R5 introduces 88 and replaces/removes 11 exact signatures. These are hunk counts.
C3 ITD preparation: yes, statute_build.py:2266-2270 and 1931-1935 match current C3:910-912. Order: Gazette R4, R1, corrigenda, R2-filtered/R3-guarded effects, C3 ITD preparation, R5, diff/classifier.
s194: 5 exact old keys; 0ec8 is old 3ca1 resegmented (ITD-only payload 4 to 9 tokens, 5 extra column-header tokens). Before R5: content=0, table-furniture=6. R4 removes headers only on the Gazette side.
Unanchored: fa_2026:s35(c), target (E)>(II): 2 heading/2 literal hits; unique prior override [26590,26740). fa_2026:s84(a), target (1)>Table>serial3>Note3: 3/27 hits; override [3614,3764).
Unanchored: fa_2026:s84(b)(i), target (4)>Table>serial7>column>(a)>(i): 7/8 hits at (a); override [27267,27292). s84(b)(ii), target (4)>Table>serial7>column>(b)>long-line>(c)>(iv): 7/9 at (b); override [29445,29675).
PLAN files: statute_build.py, tests/test_statute_build_v3.py; fresh local B-v3-repair1 evidence/controller; report. Preserve all current CSVs, fixtures and capsules. R1-R6, codebook and historical C3 functions unchanged.
PLAN fixes/tests: retain C3 furniture classification through R4/R5; validate unique scoped R3 witnesses; occurrence keys include section plus absolute Gazette/ITD positions. Invented integration/ambiguity/repetition tests, then fresh guarded run/dry run and STOP; no target final count.
Commands/evidence: read-only Get-Content/rg/Test-Path; python -B stdin replay and s194 payload/hash checks; frozen-path git diff --stat empty. All 47 hashed code/data/report files unchanged before this append.
SELF-AUDIT
1. Plan gate respected? Yes; owner authorized read-only diagnosis and this short report append; repair awaits approval.
2. Zero network/model calls? Yes; replay and diagnostics blocked network and filesystem writes in process.
3. Frozen paths untouched? Yes; frozen-path diff empty; no writes outside this append.
4. No law text in chat/report/public outputs? Yes; structural units, counts, positions and hashes only.
5. Both guards equal? Yes; unchanged replay executes both; actual saved v3 metadata reproduced exactly.
6. No commit/push/tag/merge? Yes; only read-only git diff.
7. No deletion/hand-edited records? Yes; all 34 record-file hashes unchanged.
8. Paths verified? Yes for this diagnosis; earlier path-precheck omission remains recorded above.
9. Numbers command-generated? Yes; exact replay, stage counters, original CSV keys and s194 payload comparisons.
10. Deviations listed? Yes; integration/identifier bugs above; one JSON metadata-printer error was corrected read-only with string keys.

Part B - repaired v3 pre-write STOP (2026-11-20)
PLAIN SUMMARY
- What happened: approved implementation repairs passed tests; frozen repaired v3 and the metadata-only --update dry run completed.
- What it means: 17 audit rows = 15 baseline + 2 new; 12 kept, 5 removed; all 17 row IDs unique; all 12 final occurrences covered.
- Problems: no check failure remains; 9 kept itd nature proposals await owner confirmation. No effects remain unanchored.
- Decision needed: owner yes/no for each kept itd proposal. All owner columns remain blank.
- Next message: owner confirmations; literal APPROVED WRITE remains a later gate. No canonical record writes or backups were performed.
Agent: Codex, GPT-6 based; owner UI GPT-6.1 Sol / High / Ask for approval; workspace-write; auto_review. Runtime model id/effort not independently exposed.
Implementation and frozen rules
- statute_build.py: R3 validated scoped witnesses with conflicting bounds rejected; R4 physical furniture on both sides; C3 certificates retained through R5 by source-span mapping.
- Occurrence keys include section plus absolute Gazette/original-ITD word spans; reconciliation uses occurrences and coordinates, preserving v2 trace IDs.
- R1-R6, plural rule, codebook and historical C3 functions unchanged. 43 function hashes and 6 raw code files frozen; no source/test/controller changes after freeze.
- Tests use invented strings for furniture, adjacent word changes, scope conflicts, repeated contexts and deterministic position-based IDs.
Results
- Final status/rule: kept none=12; removed R2=2, R5=3; removed R1/R3/R4/R6=0. R6 remains evidence-only.
- Kept origins: itd=9, instrument=3. Removed origins: pipeline=2, instrument=3.
- Kept itd proposals: substantive=7, reason no_accidental_certificate; accidental=2, reason regular_or_irregular_plural.
- Kept by section: s2=3, s393=7, s536=2; all other spine sections=0. s194 furniture content rows=0.
- Unanchored effects=0; the four formerly rejected effects now use validated scoped witnesses. Eligible effects=14; headings=11.
- R2 knowledge=2026-03-30; assent<=knowledge AND wef<=2026-04-01. The comparison rule was not adjusted to the results.
- Deferred: fa_2026:s84(c)/renumber and fa_2026:s84(c)/insert, both wef=2027-04-01; editor_note=yes for both.
- Deferred note cross-check: 2 agreements, 0 disagreements; no rule change on that basis.
- Actual CLI --update dry run: exit 0, write=False; changed records=30, record notes=13, counterpart notes=17, URL cells=53, lookup flags=1.
- Projected only: corrigendum_open=0; empty amended_by URL cells=0. All 34 stored record files remain byte-identical.
- 56:v1 retains its 4 FA2022 URL fills and counterpart note; FA2023 disposition continues to touch only 56:v2 and v3.
- 26/26 bodies verified by guard; 5/5 never_operative placeholders empty as designed. Stored body SHA256 and character counts checked independently.
- Code guard EQUAL: b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 (34 rows).
- Body guard EQUAL: aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d (26).
- Current public CSV, original v1/v2 drafts, old v3 capsule, public historical fixture, SOURCES, disposition and ledger/date tables preserved.
Checks and local evidence (B-v3-repair1 under the existing Part D directory)
- python -B divergence/statutes/_local_text/census/partD/20261119-172809/B-v3-repair1/run_repair.py unit: 130 passed, 33 deselected.
- Same controller phases freeze, v3, regression, dry-run and verify completed. Independent real regression: 1 passed, 63 deselected.
- Strict full-tree flake8=0; full-tree count=958, unchanged (standing 740 plus historical Part A helper 218); no new findings.
- Read-only commands: Test-Path/Get-Content/rg; Python AST/hash/CSV checks; git show for C3 AST verification; frozen-path git diff --stat empty.
- Initial pytest harness was blocked before collection at its default log destination; retry used a fresh capsule-local log/temp directory. Failed attempt retained.
- Initial slow snapshot was interrupted before creating a file; excluded partD was then pruned before traversal. Both completed snapshots cover the same 7,525 protected files.
- Optional local process inspection returned sandbox AccessDenied; the owned snapshot session was interrupted through session control. No process was stopped through the denied query.
- Tool-session reset lost unfinished setup/lint handles; those metadata-only phases were restarted with exclusive creation after confirming their outputs absent.
- Historical sandbox git global-ignore/.pytest_cache warnings remain history; owner reruns git status locally. No git state changes.
- Production phases enforce in-process write/network blocking; edition cache misses STOP. Registered instrument PDF reads remain in memory; no extraction fallback or paid/model calls.
- Complete table and every nature reason: B-v3-repair1/ITD-GAZETTE-DIFFS.csv and STOP-preview.md; all owner columns blank.
- Full before/after maps, frozen code/input hashes, dry-run diff and verification are local; no full map or extracted text is embedded here.
- Protected result: 7,525 files before/after, unchanged; additional history and all 34 record-byte maps unchanged.
- protected-before.json and protected-after.json SHA256 (equal): 95f30dab8357cb0d178746da1b271af9cc50516f3e710e8dc8805114351fb27e
- Repaired CSV SHA256: 5def82ad530d9ed7d15182f334eb5c2df957787d0e868a40d2d3b201aa3d1843
- v3-summary.json and fresh golden fixture SHA256 (equal): f85db57e004d73417c79425b1b610809f21bcb19eb9f7112c0a904fc5ce8910d
- rules.json file SHA256: 08955c3463cd926f6d0ebbe838be92f00522658c4e3ff22e2c4f7cce241bbcc2
- Canonical capsule rules-object SHA256: da63871e1f5e330a49479e4d10b3a9a1a9d610aef782d0c09afb7e1f77cb836c
- update-dry-run.json SHA256: cea6b38fb84a3b7f2f64f44c6766231d83104ddda2384c07b6b076ad710df657
SELF-AUDIT
1. Plan gate respected? Yes; owner approved these repairs, unchanged rules/codebook, fresh local outputs and the relaxed 600-line report cap.
2. Zero network/model calls? Yes; local parsing/tests only; production network audit remains active.
3. Frozen paths untouched? Yes; 7,525-file maps equal, historical data/record maps equal, frozen-path diff --stat empty.
4. No law text in chat/report/public outputs? Yes; counts, structural IDs, hash/position evidence and reason codes only.
5. Both guards equal? Yes; v3, regression and dry-run prepare paths; 26 real bodies plus 5 empty placeholders independently checked.
6. No commit/push/tag/merge? Yes; git reads only. The owner is not committing the report now.
7. No deletion/hand-edited records? Yes; existing protected/history files preserved; 34 canonical record-byte hashes unchanged.
8. Paths verified? Yes; approved files/directories checked; new outputs use exclusive creation inside the verified capsule.
9. Every number command-generated? Yes; test/lint JSON, frozen v3 result, actual CLI dry run and verified snapshots.
10. Deviations listed? Yes; operational harness/traversal/session retries above. No rule/codebook change, target count, or post-run source edit.
Report after append: 35838 bytes; 459 lines; longest line 286 characters; no extracted text blocks.

Part B - owner adjudication, promotion and APPROVED WRITE; C-check STOP (2026-11-20)
PLAIN SUMMARY
- What happened: owner decisions applied; repaired public CSV/fixture promoted; code-generated metadata updates written after a verified 34-record backup.
- What it means: 30 records changed as approved; lookup flags/URLs now match the intended state; both guards, spot checks, design cases and sweep passed.
- Problems: full pytest is not green: 803 passed, 8 failed, 2 skipped. Six failures are write-guard/harness conflicts; two are manual-provenance-URL loader incompatibilities.
- Decision needed: approve the bounded C-recovery plan below, or retain this applied state and defer further work.
- Next message: approval for C recovery. P09D-39 module code and plan remain unstarted at this first requested STOP; D follows the C-results boundary.
Agent: Codex, GPT-6 based; owner UI GPT-6.1 Sol / High / Ask for approval; workspace-write; auto_review. Runtime model id/effort not independently exposed.
Owner decisions and promotion
- Nine kept itd rows have owner_ok=yes and exact owner notes; final itd natures: 8 accidental, 1 substantive.
- Three kept instrument rows and five removed rows retain computed natures; owner_ok empty; owner_note exactly not owner-confirmed by protocol P09D-38.
- Promoted CSV and fixture rows match. The computed nature_reasons remain original proposal provenance; final row natures carry owner adjudication. No R1-R6/codebook change.
- Frozen B-v3-repair1 raw outputs remain unchanged. Owner-adjudicated promotion copies and evidence are in B-write/.
- First-run CSV and fixture were copied byte-for-byte to B-v3/ITD-GAZETTE-DIFFS.csv and B-v3/gazette_v3_expected.json before replacement.
- CSV before SHA256: f7e521af28c7f5ced22172f9b69cb29d63b176f4b6101ec1ea75c00117ff5dad
- CSV after SHA256: 37b1faa1f3c1b4eee76076ca49b972370305d8977de0a5bfc896559b99ee7c73
- Fixture before SHA256: 47d0dff3d3f6eaefc0c5b003e3d21c1834150d7a8b96acbe704bf89fe8291a5d
- Fixture after SHA256: ac52ec6914f9595f691467cf8027e37550303543fc49a90332ba12b4fbf56333
- Both B-v3 archive hashes equal their before hashes. No first-run or repaired computed artifact was overwritten.
Approved write and passing checks
- statute_ingest main([--update, --write, --backup-dir, <planned backup>]): exit 0; only the existing guarded writer serialized records.
- Backup: divergence/statutes/_local_text/census/partD/20261119-172809/D-B-records-backup-20261120; 34/34 files match before-write SHA256 values.
- Actual changes: records=30; record notes=13; counterpart notes=17; URL cells=53; lookup flags=1. Backup-to-current metadata diff is entirely allowlisted.
- act:1961:56:v1 retains four FA2022 URL fills and counterpart note; FA2023 corrigendum disposition touches only v2/v3.
- statute_validate: 34 records, 0 errors, 0 warnings.
- Code guard EQUAL: b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 (34 rows).
- Body guard EQUAL: aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d (26).
- 26/26 bodies verified by guard; 5/5 never_operative placeholders empty as designed. Stored SHA256 and character counts independently checked.
- statute_tables --check: AMENDMENT-EFFECTS accepted 50/rejected 0; VERSION-DATES accepted 34/rejected 0.
- Owner spot checks: 9/9, S7 PASS. Reused C4 input validation and exact status/candidate checks; replaced only the historical S7 non-pass reporting tail in the new local runner.
- Existing tests/test_statute_records.py real design cases: 32/32 passed; no expected-case edit in this run.
- Local sweep uses the same C4 assent grid: daily=39,456; tax_year=126; boundary=2,090; total=41,672. corrigendum_open 411 -> 0.
- Sweep stored in local sweep-B/ with COPY.md; committed census/C4_TIMELINE.md unchanged.
- Stored metadata: amended_by items=127; empty URL cells=0; corrigendum_open flags=0; repeal_day_unsettled remains on 2 records.
- Strict flake8=0. Full flake8=958, unchanged (standing 740 plus historical Part A helper 218); local write helper adds zero findings.
Full pytest STOP diagnosis (read-only; no loader/test/source fix or retry after failure)
- Passed=803; failed=8; skipped=2. Full raw output remains local in B-write/full-pytest-output.txt; no extracted blocks copied here.
- Harness group: three tests/test_gate0_check.py tests attempt fixed real-repository probe writes, including a protected _local_text probe directory; the required write guard correctly blocked them.
- Gate0 failures: test_gate0_allows_ci_bound_for_retired_percentage; test_gate0_stale_figures_need_a_left_boundary; test_gate0_skips_local_text_folders.
- Harness group: three tests/test_qa_scorer.py tests use tempfile.mkstemp in the system temp directory outside the approved evidence root; writes were blocked.
- QA failures: test_sealed_test_split_refused; test_cli_end_to_end; test_cli_missing_response_exits_nonzero.
- Loader group: statute_fetch.py:116-118 rejects a url field on every manual entry. Approved B2 adds manual provenance URLs to fa_2022 and fa_2026.
- Exact loader error: SOURCES.json: manual item fa_2022 must not carry a slug or url. This also prevents the unknown-key CLI test reaching its intended check.
- Loader failures: tests/test_statute_fetch.py::test_real_sources_json_loads_and_is_on_the_allowlist; ::test_cli_rejects_unknown_only_key.
Bounded C-recovery PLAN (await approval; no D code)
- Modify divergence/statute_fetch.py and tests/test_statute_fetch.py: permit only registry-matching manual provenance URLs as metadata; continue rejecting manual slugs and mismatched/unregistered URLs.
- Preserve download selection as items only, check_url and its ITD host restriction, request cap, redirect/refusal and pacing rules. No manual download or network call.
- Add invented-input tests for metadata URL acceptance/refusal and proof that manual keys never enter the downloader; retain real SOURCES and unknown-key CLI regressions.
- Fresh local runner/evidence: B-write-recovery/. Run the unchanged full suite against a byte-verified isolated worktree copy; redirect system temp into that local root.
- Put the test copy under B-write-recovery/.tox/worktree, already excluded by installed default artifact rules; change no lint configuration or excludes. Lint the real repository.
- Copy current tracked/unignored files and required local body files; verify bytes. Do not edit frozen scorer/corpus files or weaken the production write guard to admit real-repository probes.
- Then focused fetch tests, isolated full pytest, strict/full lint, original-tree validator/guards/tables/spot checks/cases/sweep and protected verification; STOP. No record rewrite or new owner adjudication.
Preservation and commands
- Production write/check phases used in-process write/network guards and mandatory existing edition caches; no cache fallback, network/model call, commit/push/tag/merge.
- Completed controller phases: setup, promote, write, checks, spots, cases, sweep, tests (failed), lint, verify. Independent provenance proof completed after the test STOP.
- Read-only diagnosis: rg/Get-Content/Test-Path; Python error classification/AST/hash checks; inspected installed flake8 defaults. No source alteration to bypass failing tests.
- Helper-only preflight style corrections removed an unused import/indentation issues before promotion/write. Child bytecode writes disabled. Existing artifacts retained.
- Read-path omissions: one optional read used absent tests/conftest.py before Test-Path; rg then located the actual root conftest.py. One rg wildcard invocation was corrected. No protected write.
- Protected before/after: 7,525 files, unchanged; snapshot files have identical SHA256: 66346d46bd2d6a936e271116003a5278248a537589d35ebc7f05cbfb5ec388f6
- Current record backup/field proof: B-write/record-provenance-proof.json; SHA256 c57013dec3a23644fc0c729eda024716197bde2c906ac3dcab2180754fa184a6
- Full test metadata SHA256: e2bb49ef481db1da529d3400ab50c78da40979c44e0f3d24526b41077b11d4c4
- Promotion evidence SHA256: 63e7d9102eba4a0e0cdb8896c0f8a9ffccd0aba8e1b785dec3b9f1185d2808d9
- D module/table do not exist; no P09D-39 implementation was started.
SELF-AUDIT
1. Plan/approval respected? Yes for adjudication/promotion/record write; explicit APPROVED WRITE supplied. New loader/harness repair awaits approval under the STOP rule.
2. Zero network/model calls? Yes; in-process network audit active; all tests local; no provider calls.
3. Frozen paths untouched? Protected 7,525-file map unchanged; no scorer/corpus/ledger/date-table edits. Only approved metadata records/public promotion paths changed.
4. No law text in public/chat? Yes; owner metadata notes, IDs, counts and hashes only; detailed test output remains local.
5. Both guards equal? Yes; actual code/body guard commands passed; 26 real bodies and 5 empty placeholders independently verified.
6. No commit/push/tag/merge? Yes; none performed.
7. No deletion/hand-edited records? Yes for existing data; guarded code writer only, 34 originals preserved and SHA-verified.
8. Paths prechecked? No: optional absent tests/conftest.py read omission noted above; all actual output roots were verified.
9. Every number command-generated? Yes; promotion/write/check/test/lint JSON, identical snapshots and provenance verification.
10. Deviations listed? Yes; 8 full-suite failures, operational discovery/style issues and the bounded recovery plan. C is not all-green; D remains pending.
Report after append: 45394 bytes; 535 lines; longest line 286 characters; metadata only, no extracted text blocks.

Part B - owner-selected URL representation recovery (2026-11-20) - STOP
PLAIN SUMMARY
- What happened: removed url from manual fa_2022/fa_2026; appended the same literal URLs to where with the requested middle-dot separator; byte_verified unchanged.
- What it means: registered_url resolves the same URLs; actual statute_ingest --update reports 0 changes; the unchanged fetch loader accepts all 15 items.
- Problems: requested fetch/statute suite has no failures. Full plain pytest remains owner-run; its six Gate0/QA write-guard conflicts were not rerun here.
- Decision needed: none for this recovery. Prior fetch-code/isolated-worktree proposal superseded by owner option b.
- Next message: STOP as requested; do not begin D. No isolated worktree, D module or BODY-CAVEATS.csv created.
Agent: Codex, GPT-6 based; owner UI GPT-6.1 Sol / High / Ask for approval; workspace-write; auto_review.
- SOURCES before SHA256: 0bf4e03dac155837619740e2318b7b5bd9f4574c061f524990ffccec3f7c22c8
- SOURCES after SHA256: f2305ef3bfc0dbfcd9766f067b36053cf3e3e7a5a45b8d2991512db6644d9e39
- Only the two approved manual entries differ: url removed and where appended; every other JSON value is identical, including both byte_verified values.
- statute_fetch.py unchanged SHA256: ce83404233790e9a2dabd0ecd9c4b0714595d211ad2d796fc3f37df6f6e89003
- Dry run: exit 0; write=False; changed_records=0; diff=[]; all 34 record-file hashes unchanged.
- 26/26 bodies verified by guard; 5/5 never_operative placeholders empty as designed.
- tests/test_statute_fetch.py plus all other test_statute*.py files: 13 files, 634 passed, 2 skipped, 0 failed; former two loader-related failures now pass.
- Commands: python -B divergence/statutes/_local_text/census/partD/20261119-172809/B-url-recovery/run_url_recovery.py prepare / dry-run / tests / verify.
- Pytest cache disabled; fresh capsule-local pytest/log/system-temp paths; bytecode writes disabled. Network and out-of-scope writes blocked in process; edition cache misses STOP.
- Protected before/after: 7,525 files, unchanged; identical snapshot SHA256: 66346d46bd2d6a936e271116003a5278248a537589d35ebc7f05cbfb5ec388f6
- Evidence: B-url-recovery/{representation,dry-run,statute-tests,verification}.json and immutable SOURCES.before.json/SOURCES.after.json.
SELF-AUDIT
1. Approval respected? Yes; exact owner metadata-only recovery, required zero-diff gate, selected tests, report append and STOP.
2. Zero network/model calls? Yes; local metadata, guarded parsing and fake/offline tests only.
3. Frozen paths untouched? Yes; protected maps equal; limited frozen-path git diff --stat empty.
4. No law text in public/chat? Yes; metadata/counts/hashes only; test details remain local.
5. Guards/body verification preserved? Yes; guarded prepare in actual zero-change dry run; approved 26-real/5-empty split.
6. No commit/push/tag/merge? Yes; git read-only diff only.
7. No deletion/record edits? Yes for existing data; all 34 record bytes unchanged; original metadata/evidence preserved.
8. Paths verified? Yes; exact approved file, verified new evidence root and exclusive-create outputs.
9. Numbers command-generated? Yes; dry-run/test JSON and before/after hash verification.
10. Deviations listed? None for this recovery; full plain pytest intentionally delegated to owner; no fetch-code edit or isolated-worktree retry.
Report after append: 48841 bytes; 567 lines; longest line 286 characters; no extracted text blocks.

Part D - P09D-39 completed (2026-11-20) - STOP
Agent: Codex, GPT-6 based; runtime id/effort not exposed; owner UI GPT-6.1 Sol / High / Ask for approval; workspace-write; auto_review.
PLAIN SUMMARY
- What happened: generated BODY-CAVEATS.csv and independent --check PASS; 27 rows: itd_diff=9, amended_span=3, label_gap=15; 12/12 kept refs covered.
- What it means: 12/12 spans inside stored bodies; UTF-8 sha16 matches; moved_pair:6-7 shared marker PASS; bodyless offset rows=0.
- Problems: evidence_key contains occurrence hashes, no coordinates; explicit rows=0; approved scoped observer fallback=12; state restoration tested.
- Decision needed: none for generation; no classifications or R1-R6 changed. Git ignore/.pytest_cache permission warnings are sandbox-origin; owner checks status locally.
- Next message: STOP after D generation/check; no staging or commit.
Covered: v2:04ca6540edc66d66=yes; v2:1198795e7740ed71=yes; v2:1d058f3a49580ed1=yes; v2:3bc1d541e6b2c29c=yes
Covered: v2:4ba98c8a53b744f6=yes; v2:7d4478c559067e47=yes; v2:8708535b92f6500b=yes; v2:90a1d83cadaac911=yes
Covered: v2:a19d5fbf04b8fc9c=yes; v2:fb5f97c86c27aa13=yes; v3:9255c33aa23d7927=yes; v3:d6e0e4b1fb1042ac=yes
Absence units (end exclusive): v2:fb5f97c86c27aa13 s.393 [0,40384); v2:8708535b92f6500b s.536(2) [67,11488); v3:d6e0e4b1fb1042ac s.393(8) [39114,39390)
TABLE SHA256: 6d42a02255bc56c79ac6df03d46c21a57629530c230de72625d9fe24c67a50ae
Protected before/after: 7525 files, unchanged; both snapshot maps in D-caveats/.
Snapshot SHA256: 66346d46bd2d6a936e271116003a5278248a537589d35ebc7f05cbfb5ec388f6
Records: 34/34 hashes unchanged; prior inputs unchanged. 26/26 bodies verified by guard; 5/5 never_operative placeholders empty as designed.
Tests: 14 statute files; 664 passed, 2 skipped, 0 failed; 30 new caveat tests included. Strict/full flake8 new module/tests/runner=0. Evidence: D-caveats/.
Owner-reported pre-D checks: plain pytest 812 passed/1 skipped; strict flake8=0; validator=34/0/0; tables=0 rejected; both guards PASS; GATE 0 CLEAR; corpus=17/17.
SELF-AUDIT
1. Approval respected? Yes; exact D scope and evidence-first amendment.
2. Network/model calls? Zero; in-process network/write boundary active.
3. Existing inputs unchanged? Yes; protected, record and input hashes equal.
4. Public law wording? None; offsets, identifiers, labels and hashes only.
5. All kept refs covered? Yes; 9 itd plus 3 instrument, removed rows excluded.
6. Missing text fabricated? No; three gaps use containing-unit spans.
7. Span/hash/pair checks? PASS; all LABEL-GAPS offsets/hash empty.
8. Observer restored? Yes; finally restores functions/state; success/failure tested; explicit-coordinate path bypass tested.
9. Unexpected writes? None; only new module/tests/table, local D evidence and this append; no record writes or staging.
10. Deviations? Evidence stores digests rather than coordinates; approved fallback used. STOP after independent --check.
Report after append: 51878 bytes; 598 lines; longest line 286 characters; no extracted text blocks.
P09D-39 point amendment: v3:d6e0e4b1fb1042ac=39114; v2:8708535b92f6500b=3285; v2:fb5f97c86c27aa13=7689; counts itd_diff=9/amended_span=3/label_gap=15. TABLE SHA256: d875053bc5993e0ce3c030c75f282ad94171b7ff983559da47cd7de9e03be7dc
--write/--check PASS; 50 caveat tests; statute 684 passed/2 skipped; point bounds/window:40 hashes PASS; 7525 protected/34 records/inputs unchanged; strict/full flake8=0; evidence D-point-caveats/. Report: 52364 bytes; 600 lines; no extracted text blocks.
