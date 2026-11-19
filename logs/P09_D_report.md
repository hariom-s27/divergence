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
