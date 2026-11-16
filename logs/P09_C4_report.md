# P09 Part C4 report

## C4-A: read-only findings (16 Nov 2026)

### PLAIN SUMMARY
- What happened: all nine C4-A steps ran in memory (scripts piped to `python -B -`; no files written, no network,
  no model/API calls). Record projection per D2-D7, Act 30 of 2025 assent, corpus horizon proposal, a dry run of the
  current lookup on 32 cases, the owner-years formula check, a storage_mode search, and a list of lines C4-B must change.
- What it means: the design gives exactly the expected records from the real tables (20 / 6 / 5 / 3, retro 2).
  Today's lookup already matches the target on 13 of 32 cases; the other 19 are the C4-B work.
- Problems: none blocking. Two harness retries (see Self-audit). Five open questions, all decided by the owner below.
- Decision needed: none; owner decisions recorded below. Next: PART C4-B plan gate.
- Next message: the owner's PART C4-B instructions.

### Owner decisions (16 Nov 2026)
- CORPUS_CHECKED_THROUGH = 2026-11-15 (basis: registry + owner web check; an eGazette check is pending before D80).
- Q1 amended_by.kind = instrument type (`finance_act` for the five Finance Acts), plus a new optional `operation`
  field (substitute / insert / omit / renumber).
- Q2 counterpart.source_url = "" (MAPPING.csv carries no URL).
- Q3 edition knowledge dates are computed in C4-C (in process) and cross-checked against the C2 sheet.
- Q4 amended_by is cumulative: every effect in the version's state (127 items over 34 records).

### Step 1: repo state (LOCAL)
| Check | Result |
|---|---|
| Branch / HEAD | feat/p09-ingest / eb09682 |
| git status | clean before and after |
| `python -B -m pytest --collect-only -q -p no:cacheprovider` | 613 tests collected |
| VERSION-DATES.csv sha256 | 572ea9315a05ffd16cec9b592821177e2dbfd2e95712759faf21adeede52bca4 |
| AMENDMENT-EFFECTS.csv sha256 | b3ecb5dd1fb2c2587e01f27dab90494772474d3c3ed7456cc8ad12dc741baf5c |
| SOURCES.json sha256 | 45c3fcd4fa2279da006d40f46b7d306cde76f173b6d288733286acb234d43073 |
| Version code-column guard (in memory) | 34 rows, b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 (unchanged) |
| Body guard aebe8deb... | not run in C4-A (owner decision G1 = c); first run in C4-C |

Code-column guard definition: sha256 of `act_parse.csv_text(rows sorted by record_key, code columns)`, where code
columns = VERSION_COLUMNS minus VERSION_OWNER (same as the C3-fix guard).

### Step 2: record projection per D2-D7 (LOCAL, in memory)
Inputs: VERSION-DATES.csv, AMENDMENT-EFFECTS.csv, SOURCES.json (items + manual), FETCH-LOG.json, MAPPING.csv,
statute_build.LABEL_GAP, and edition knowledge dates read from the local C2 sheet
`census/partC/C2-20261116-071401/PENDING-23.md` (sha256 5e0c17599b4ab5c6c051a2bacbba3ecab9241be288ca0634aa5bd9b9dd2b001d).
Ends are half-open; repeal-day rows get to = from + 1 day; retro (D5) moves the predecessor's end to enacted_on.

| record_id | status | from | to | retro_from | enacted_on | applies | basis | flags | body source | text_current_as_of | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| act:1961:2:v1 | in_force | 2023-04-01 | 2024-04-01 | | 2023-03-31 | 2022-23..2022-23 | charging_ay_rule | | ita1961_2023 | 2023-03-31 | source_label_gap |
| act:1961:2:v2 | unprinted | 2024-04-01 | 2024-08-16 | | 2023-03-31 | - | unclear | | none (src ita1961_2026) | 2026-03-30 | |
| act:1961:2:v3 | unprinted | 2024-08-16 | 2024-10-01 | 2024-07-23 | 2024-08-16 | - | unclear | | none (src ita1961_2026) | 2026-03-30 | |
| act:1961:2:v4 | in_force | 2024-10-01 | 2025-04-01 | | 2024-08-16 | 2024-25..2024-25 | transaction_date | | ita1961_2024n2 | 2024-08-16 | |
| act:1961:2:v5 | repealed_saved | 2025-04-01 | 2026-04-01 | | 2025-03-29 | 2024-25..2024-25 | charging_ay_rule | | ita1961_2025 | 2025-03-29 | |
| act:1961:2:v6 | in_force | 2026-04-01 | 2026-04-02 | | 2025-03-29 | 2025-26..2025-26 | charging_ay_rule | repeal_day_unsettled | ita1961_2026 | 2026-03-30 | |
| act:1961:3:v1 | repealed_saved | 2023-03-31 | 2026-04-01 | | null | 2022-23..2025-26 | charging_ay_rule | | ita1961_2023 | 2023-03-31 | |
| act:1961:56:v1 | in_force | 2023-04-01 | 2024-04-01 | | 2023-03-31 | 2022-23..2022-23 | charging_ay_rule | | ita1961_2023 | 2023-03-31 | source_label_gap |
| act:1961:56:v2 | in_force | 2024-04-01 | 2025-04-01 | | 2023-03-31 | 2023-24..2023-24 | charging_ay_rule | corrigendum_open | ita1961_2024n2 | 2024-08-16 | source_label_gap |
| act:1961:56:v3 | repealed_saved | 2025-04-01 | 2026-04-01 | | 2024-08-16 | 2024-25..2025-26 | charging_ay_rule | | ita1961_2025 | 2025-03-29 | |
| act:1961:115BBH:v1 | repealed_saved | 2023-04-01 | 2026-04-01 | | 2022-03-30 | 2022-23..2025-26 | charging_ay_rule | | ita1961_2023 | 2023-03-31 | |
| act:1961:158B:v1 | in_force | 2023-03-31 | 2024-09-01 | | null | - | unclear | | ita1961_2023 | 2023-03-31 | |
| act:1961:158B:v2 | in_force | 2024-09-01 | 2025-03-29 | | 2024-08-16 | 2024-25..2024-25 | transaction_date | | ita1961_2024n2 | 2024-08-16 | |
| act:1961:158B:v3 | repealed_saved | 2025-03-29 | 2026-04-01 | 2025-02-01 | 2025-03-29 | 2024-25..2025-26 | transaction_date | | ita1961_2025 | 2025-03-29 | |
| act:1961:194S:v1 | in_force | 2022-07-01 | 2025-04-01 | | 2022-03-30 | 2022-23..2024-25 | transaction_date | | ita1961_2023 | 2023-03-31 | |
| act:1961:194S:v2 | repealed_saved | 2025-04-01 | 2026-04-01 | | 2025-03-29 | 2025-26..2025-26 | transaction_date | | ita1961_2025 | 2025-03-29 | |
| act:1961:285BAA:v1 | in_force | 2026-04-01 | 2026-04-02 | | 2025-03-29 | - | unclear | repeal_day_unsettled | ita1961_2025 | 2025-03-29 | |
| act:2025:1:v1 | in_force | 2026-04-01 | open | | 2025-08-21 | 2026-27.. | ita2025_tax_year | | ita2025_2026 | 2026-03-30 | |
| act:2025:2:v1 | never_operative | null | null | | 2025-08-21 | - | unclear | | none (empty body) | 2026-03-30 | |
| act:2025:2:v2 | in_force | 2026-04-01 | open | | 2026-03-30 | 2026-27.. | ita2025_tax_year | | ita2025_2026 | 2026-03-30 | |
| act:2025:3:v1 | in_force | 2026-04-01 | open | | 2025-08-21 | 2026-27.. | ita2025_tax_year | | ita2025_2026 | 2026-03-30 | |
| act:2025:92:v1 | in_force | 2026-04-01 | open | | 2025-08-21 | 2026-27.. | ita2025_tax_year | | ita2025_2026 | 2026-03-30 | |
| act:2025:194:v1 | in_force | 2026-04-01 | open | | 2025-08-21 | 2026-27.. | ita2025_tax_year | | ita2025_2026 | 2026-03-30 | |
| act:2025:301:v1 | in_force | 2026-04-01 | open | | 2025-08-21 | 2026-27.. | transaction_date | | ita2025_2026 | 2026-03-30 | |
| act:2025:393:v1 | never_operative | null | null | | 2025-08-21 | - | unclear | | none (empty body) | 2026-03-30 | |
| act:2025:393:v2 | in_force | 2026-04-01 | 2027-04-01 | | 2026-03-30 | 2026-27..2026-27 | transaction_date | | ita2025_2026 | 2026-03-30 | |
| act:2025:393:v3 | unprinted | 2027-04-01 | open | | 2026-03-30 | - | unclear | | none (src ita2025_2026) | 2026-03-30 | |
| act:2025:400:v1 | never_operative | null | null | | 2025-08-21 | - | unclear | | none (empty body) | 2026-03-30 | |
| act:2025:400:v2 | in_force | 2026-04-01 | open | | 2026-03-30 | 2026-27.. | procedural | | ita2025_2026 | 2026-03-30 | |
| act:2025:446:v1 | never_operative | null | null | | 2025-08-21 | - | unclear | | none (empty body) | 2026-03-30 | |
| act:2025:446:v2 | in_force | 2026-04-01 | open | | 2026-03-30 | 2026-27.. | penalty_default_date | | ita2025_2026 | 2026-03-30 | |
| act:2025:509:v1 | in_force | 2026-04-01 | open | | 2025-08-21 | 2026-27.. | procedural | | ita2025_2026 | 2026-03-30 | |
| act:2025:536:v1 | never_operative | null | null | | 2025-08-21 | - | unclear | | none (empty body) | 2026-03-30 | |
| act:2025:536:v2 | in_force | 2026-04-01 | open | | 2026-03-30 | 2026-27.. | procedural | | ita2025_2026 | 2026-03-30 | |

supersedes = v(n-1) of the same unit for every n > 1 (none for v1).

Counts: 34 records; in_force 20, repealed_saved 6, never_operative 5, unprinted 3 (expected 20 / 6 / 5 / 3: match).
Retro: act:1961:2:v3, act:1961:158B:v3 (expected: match). Problems raised by the projection: none.

Other fields:
- basis_exceptions: only act:1961:2:v1 (fa_2023:s3(a)=procedural; fa_2023:s3(c)=procedural; fa_2023:s3(d)=transaction_date).
- owner_target: 2 rows (fa_2022:s16(b)(ii) on 1961 s.56; fa_2026:s35(c) on 2025 s.2). Both change only the clause
  path inside the same section, so target_section is kept for enacted_on and amended_by.
- amended_by: 46 items if only each row's own effect_ids; 127 items as the D5 state (same unit, wef <= VERSION-DATES
  start; owner decision Q4). url = registered URL or "": registered for fa_2023, fa2_2024, fa_2025_gz; "" for
  fa_2022 and fa_2026 (53 of 127 items empty).
- Schema amendment_kind enum: finance_act, amendment_act, ordinance, notification, other.
  AMENDMENT-EFFECTS operation values: substitute 20, insert 22, omit 7, renumber 1 (owner decision Q1).
- counterpart (1961 records only; 2025 records null, 17): 2->2, 3->3, 56->92, 158B->301, 285BAA->509 SECONDARY;
  115BBH->194 SECONDARY "unverified"; 194S->393 CBDT_official "official Act PDF, owner eye check".
- Source fields: source_url and retrieved_at from FETCH-LOG for the body edition; unprinted records use the latest
  edition checked for the act (ita1961_2026 / ita2025_2026); never_operative records have none.
- text_current_as_of: knowledge date of the body edition; unprinted = latest edition checked; never_operative =
  the successor record's enacted_on.

### Step 3: Act 30 of 2025 assent (REPO + LOCAL)
SOURCES.json, list `manual`, key `ita2025_gz`, field `assent_date` = 2025-08-21. Registered file sha256 =
local file sha256 = 7acfb16fd7f3db8b4f85fc532b6d6924478ef86fa2e5b7683d282f8825f8017c. One hit for act_no 30 / 2025.

### Step 4: corpus horizon and spine effects per instrument
Counting rule: each AMENDMENT-EFFECTS row is counted once under its instrument = the effect_id prefix (the `act_key`
column holds labels such as "Act No. 8 of 2023"). Spine = target_section in act_parse.SPINE[target_act].

| Instrument | Assent / gazette | Spine effects |
|---|---|---|
| fa_2022 | 2022-03-30 | 9 |
| fa_2023 | 2023-03-31 | 8 |
| fa_2024 | 2024-02-15 | 0 |
| fa2_2024 | 2024-08-16 | 9 |
| fa_2025_gz | 2025-03-29 | 8 |
| fa_2026 | 2026-03-30 | 16 |
| tola_2026 / tola_2026_gz | 2026-08-17 | 0 (expected 0) |
| ord_2_2026 | gazette 2026-06-05 | 0 (expected 0) |
| all other registered keys (editions, fa_2025 ITD copy, ita2025_gz, corrigenda, notifications, circulars) | - | 0 |

Total 50 effects, all spine; no effect instrument is unregistered.
Evidence: FETCH-LOG 2026-11-13 06:36-06:53 (+05:30); MANUAL-SOURCES save dates 2026-11-13, 2026-11-15; latest
registered instrument 2026-08-17. Proposal (rule: latest date the instrument list was checked) = 2026-11-15;
alternative = 2026-08-17. Owner decision: 2026-11-15 (eGazette check pending before D80).

### Step 5: dry run of TODAY's lookup (code unchanged; records converted to inclusive ends)
| # | Query | Today | Expected after C4-B |
|---|---|---|---|
| 1 | 1961 s.2 as_of 2023-03-31 | NO {no_version_covers_point} | NO {before_coverage} |
| 2 | 1961 s.2 as_of 2023-04-01 | FOUND v1 | FOUND v1 |
| 3 | 1961 s.2 as_of 2024-03-31 | FOUND v1 | FOUND v1 |
| 4 | 1961 s.2 as_of 2024-04-01 | FOUND v2 | AMB v2 {unprinted_intermediate} |
| 5 | 1961 s.2 as_of 2024-07-23 | FOUND v3 | AMB v3 {unprinted_intermediate} |
| 6 | 1961 s.2 as_of 2024-10-01 | FOUND v4 | FOUND v4 |
| 7 | 1961 s.2 as_of 2026-03-31 | FOUND v5 | FOUND v5 |
| 8 | 1961 s.2 as_of 2026-04-01 | FOUND v6 | AMB v6 {repeal_day_unsettled} |
| 9 | 1961 s.2 as_of 2026-04-02 | NO {no_version_covers_point} | NO {after_repeal} |
| 10 | 1961 s.56 as_of 2024-04-01 | FOUND v2 | AMB v2 {corrigendum_open} |
| 11 | 1961 s.56 as_of 2026-04-01 | NO {no_version_covers_point} | NO {after_repeal} |
| 12 | 1961 s.158B as_of 2025-02-01 | FOUND v3 | FOUND v3 |
| 13 | 1961 s.158B as_of 2025-02-15 K=2025-03-01 | FOUND v2 | FOUND v2 |
| 14 | 1961 s.158B as_of 2025-02-15 K=2025-04-01 | FOUND v3 | FOUND v3 |
| 15 | 1961 s.194S as_of 2022-06-30 | NO {no_version_covers_point} | NO {before_coverage} |
| 16 | 1961 s.285BAA as_of 2026-04-01 | FOUND v1 | AMB v1 {repeal_day_unsettled} |
| 17 | 2025 s.393 as_of 2026-03-31 | NO {no_version_covers_point} | NO {before_commencement} |
| 18 | 2025 s.393 as_of 2026-04-01 | FOUND v2 | FOUND v2 |
| 19 | 2025 s.393 as_of 2026-06-01 K=2026-03-01 | NO {never_operative} | AMB {known_text_not_in_corpus} |
| 20 | 1961 s.2 as_of 2023-05-01 K=2023-03-30 | NO {no_version_covers_point} | AMB {known_text_not_in_corpus} |
| 21 | 1961 s.3 as_of 2024-05-01 K=2024-01-01 | AMB v1 {unknown_enactment_date} | AMB v1 {unknown_enactment_date} |
| 22 | 1961 s.3 TY 2022-23 | AMB v1 {midyear_effect} | FOUND v1 |
| 23 | 1961 s.194S TY 2022-23 | AMB v1 {midyear_effect} | AMB v1 {midyear_effect} |
| 24 | 1961 s.2 TY 2023-24 | NO {no_version_covers_point} | AMB v2 {unprinted_intermediate} |
| 25 | 1961 s.2 TY 2024-25 | AMB v4,v5 {midyear_effect, overlap} | AMB v4,v5 {midyear_effect, overlap} |
| 26 | 1961 s.56 TY 2025-26 | FOUND v3 | FOUND v3 |
| 27 | 1961 s.158B TY 2021-22 | NO {no_version_covers_point} | NO {before_coverage} |
| 28 | 1961 s.158B TY 2022-23 | NO {no_version_covers_point} | AMB v1 {applicability_unclear_row} |
| 29 | 1961 s.285BAA TY 2026-27 | NO {no_version_covers_point} | NO {after_repeal} |
| 30 | 2025 s.1 TY 2025-26 | NO {no_version_covers_point} | NO {before_commencement} |
| 31 | 2025 s.393 TY 2026-27 | FOUND v2 | FOUND v2 |
| 32 | 2025 s.1 as_of 2026-11-16 (CCT + 1 day) | FOUND v1 | AMB {beyond_corpus_horizon} |

n = 32 cases; today = expected on 13, differs on 19. No expected case looks wrong under the design
(INFERENCE: hand trace of D9 on the projected records; the real check is C4-B's parametrized test).

### Step 6: owner-years formula check (report only)
Formula as specified; "end" = the projected half-open in_force_to (result basis). n = 24 dated non-unclear rows:
OK 21, OK via VD-4 3 (act:1961:3:v1, act:1961:56:v3, act:1961:115BBH:v1), DIFF 0 (expected: match).
Information only: on the raw VERSION-DATES end, act:1961:2:v6 (from = to = 2026-04-01) would be a fourth VD-4 case.

### Step 7: storage_mode / body location
No conflict with local_only: DECISION-D78.md line 37 (bodies stay local while building; public form decided at
release), divergence/statutes/README.md line 4, .gitignore line 18. statutes/records/ and statutes/text/ hold only
.gitkeep.

### Step 8: lines C4-B must change (half-open dates and D9-D11)
- divergence/statute_lookup.py:132 (`as_of <= end`), :161 and :163 (mid-year tests); steps 3-11 (lines 101-180)
  replaced per D9.
- divergence/statute_schema.py:19 (STATUSES + unprinted), :36 (replace former repeal-last-day constant with REPEAL_DAY 2026-04-01);
  new CORPUS_CHECKED_THROUGH, REASON_CLASS, reason_class().
- divergence/statute_validate.py:27 (import), :103 (V05 strict from < to), :135-153 (V07 REPEAL_DAY; unprinted rule),
  :207-226 (V10: null body only for unprinted).
- divergence/statutes/schema/statute_record.schema.json: :38-39 and :92-93 (body fields nullable only for unprinted),
  :56 (status enum), :143-155 (amended_by item: optional operation, Q1), :172 (counterpart source_url, Q2);
  new optional lookup_flags, basis_category, basis_exceptions.
- Fixtures (inclusive -> half-open): act__2025__sFAKE5__v1.json:14 (2026-08-16 -> 2026-08-17);
  act__1961__sFAKE4__v1.json:14, act__1961__sFAKE4__v2.json:14, act__1961__sFAKE2__v1.json:14 (2026-03-31 -> 2026-04-01).
- Tests expected to change: tests/test_statute_lookup.py:45-47 (F1 as_of 2026-03-31 -> before_commencement),
  :55-58 (F2 TY 2026-27 -> after_repeal); validator V07 fixture expectations. tests/test_statute_build.py:72-74
  stays (VERSION-DATES keeps exclusive ends and is not converted).

### Step 9: plan for C4-B and C4-C (detail in the C4-B plan gate)
C4-B (code + tests; no real records):
- New divergence/statute_records.py: pure projection (this C4-A prototype as a function) and basis_exceptions parser.
- New divergence/statute_guard.py: `--code` (VERSION-DATES only) and `--body` (statute_build with a no-write path);
  tests; the body guard first runs in C4-C.
- Lookup per D9/D10; schema, validator and fixtures per Step 8; Q1/Q2 schema changes.
- New tests (estimate about 70; total about 680): test_spec_case[1..32] on records projected from the committed
  tables; test_reason_class_covers_every_emitted_reason; edge-rule tests (after_repeal, before_commencement,
  beyond_corpus_horizon, hindsight drop, unprinted / unclear windows, before_coverage, charging rule skips mid-year,
  half-open end); validator tests (V05 equal dates, V07 repeal day, unprinted body rules); projection tests
  (counts 20/6/5/3, retro end move, Act 30 fallback, cumulative amended_by, empty url, counterpart 1961 only,
  never_operative / unprinted text dates, label-gap note); guard tests (code sha b7b8fa36..., stubbed body guard).
C4-C: write the 34 real records (metadata in statutes/records/<act>/, bodies local_only); compute knowledge dates in
process and cross-check the C2 sheet (Q3); body guard (expected aebe8deb...) and per-record body sha cross-check;
statute_validate on the real root (no --freeze); the 32 cases on the real records.

### SELF-AUDIT (C4-A)
1. Plan gate: kept (runs only after the owner's APPROVED; one extra in-memory print inside step 2's scope).
2. No commit / push: kept.
3. Protected files (tables, owner/, bodies, FREEZE-HASHES, replay cache, runs/, pre-registration, QA scorer, TEST set,
   no --freeze): kept; table shas unchanged.
4. No network, model/API calls, new dependencies or environment-variable reads: kept.
5. Writes: only this report section and the scratch handoff, after owner approval. Runs wrote nothing
   (git status clean before and after; census/partC file count 290 before and after; python -B, no bytecode).
6. Deterministic; STOP on unclear: kept; open questions went to the owner (decided above).
7. Errors and retries: (a) PowerShell here-strings drop the last newline, so the first step-2 run joined two lines
   (SyntaxError); re-run with an explicit newline, code unchanged. (b) one Grep with a brace glob over a subpath
   matched nothing; re-run per file. (c) Step 4 counts by effect_id prefix instead of act_key (labels).
8. No law text, keys or personal data in this report.
9. Auto mode: off during the runs.

## C4-B: baseline and STOP before implementation (16 Nov 2026)

### PLAIN SUMMARY
- What happened: owner approved the implementation plan and all 20 per-file edit requests. Baseline collection and
  both lint commands completed. A subsequent source read used an unverified path and failed; implementation stopped.
- What it means: no code, schema, test, fixture, protected input, or real record was changed. C4-B remains incomplete.
- Problems: `Get-Content divergence/statutes/FETCH-LOG.json` reported that the path does not exist. PowerShell treated
  this as a non-terminating error, so the already-submitted command finished its remaining read-only statements.
  No retry, alternate path, or further implementation was attempted after receiving the result.
- Decision needed: owner instruction to resume with read-only discovery of the actual FETCH-LOG location.
- Next message: owner authorizes that discovery and continuation; existing per-file approvals remain recorded.

### Baseline and requested STOP evidence
- Branch: feat/p09-ingest; HEAD: 80bafc62612c30a86694d14e31bd260c152b1120; initial git status clean.
- Collected tests: before 613; after not run. Full pytest: not run.
- CI-selected flake8: before 0, exit 0; after not run.
- Full CI flake8: before 740 findings, exit 0 under the pre-existing --exit-zero warning policy; after not run.
- Commands used: `python -B -m pytest --collect-only -q -p no:cacheprovider`;
  `python -B -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`;
  `python -B -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`.
- statute_guard --code: not run; module not created. Real body guard: not run (reserved for C4-C).
- gate0 / corpus_hash --verify / statute_validate / statute_tables --check: not run because of STOP.
- Former repeal-last-day constant occurrences printed before any edits: statute_schema.py:36; statute_validate.py:27,145,146;
  logs/P09_C4_report.md:179 (historical C4-A reference). No replacements made yet.
- Added owner requirements retained: all 34 supersedes links tested; existing C2 repeal-day assertions unchanged;
  report per-file diff totals, collection/lint before and after, guards, protected hashes, and all gate results.
- Expected future projection: 34 records (20/6/5/3), retro 2, cumulative amendments 127, empty URLs 53;
  expected future test total approximately 681 including the added supersedes invariant. None asserted yet.

Protected input SHA-256 values (before; after re-read at this STOP):

| Input | Before | After |
|---|---|---|
| VERSION-DATES.csv | 572ea9315a05ffd16cec9b592821177e2dbfd2e95712759faf21adeede52bca4 | same SHA, independently verified |
| AMENDMENT-EFFECTS.csv | b3ecb5dd1fb2c2587e01f27dab90494772474d3c3ed7456cc8ad12dc741baf5c | same SHA, independently verified |
| SOURCES.json | 45c3fcd4fa2279da006d40f46b7d306cde76f173b6d288733286acb234d43073 | same SHA, independently verified |

Only this appended report section and the ignored scratch handoff are written for STOP reporting. Exact per-file
diff totals and file hashes are supplied in the handoff and owner-facing STOP message after this append.

### SELF-AUDIT (C4-B baseline STOP)
1. Plan gate: kept yes; explicit APPROVED received before runs/writes, then each file edit separately approved.
2. No commit/push: kept yes; only read-only git inspection; owner-only commit commands prepared in the STOP message.
3. Protected inputs: kept yes; no code/test/fixture/body/table edits, no freeze, no real records, no body guard.
4. Offline/no dependencies/secrets: kept yes; no network, model/API calls, dependency installation, key or environment reads.
5. Write locations: kept yes; only approved committed report and scratch/C4_handoff_B.md for reporting.
6. Determinism and STOP: kept yes; failed source read disclosed, no retry or improvised recovery; only STOP reporting follows.
7. Report format/public content: kept yes; PLAIN SUMMARY first, details, SELF-AUDIT; no keys, personal data or law text.
8. Handoff: kept yes; scratch/C4_handoff_B.md records files, hashes, counts and open questions.

Automatic approval review is configured as auto_review; explicit owner approval was still obtained and respected.

### C4-B resumed implementation and final STOP (16 Nov 2026)

#### PLAIN SUMMARY
- What happened: resumed on explicit owner approval, read C4-A first, verified the supplied FETCH-LOG SHA, implemented
  the approved files and 68 additional tests, then ran the required checks sequentially. The final tables check failed.
- What it means: code and tests are reviewable but C4-B is incomplete; no commit, push, real records or body-guard run.
- Problems: statute_tables.check_versions delegates raw VERSION-DATES dates to the newly strict V05. The two preserved
  equal-date repeal-day rows are rejected, while D3 requires their projected records to end on the following day.
  Full lint also has three additional advisory findings. No code or test expectations were changed after this failure.
- Decision needed: owner approval of a follow-up compatibility plan for the table checker, outside the original edit list.
  Preserve strict record V05, protected tables and C2 assertions; do not suppress these rejections or change expectations.
- Next message: owner directs/approves the table-checker follow-up. Existing working changes remain uncommitted.

#### Implementation and evidence
- D78 amendment written separately; original DECISION-D78.md unchanged. Horizon 2026-11-15 and evidence recorded.
- Half-open helpers, REPEAL_DAY, complete reason classes, D9 lookup order, schema and D11 validator implemented.
- Pure project(vd, effects, sources, mapping, knowledge, fetch_log=None): no implicit local reads. CI uses committed
  tables/SOURCES only, synthetic or None knowledge, and no real FETCH-LOG. Printed bodies are not manufactured.
- Registered assent fallback verified as 2025-08-21. Real-table tests pass: 34 records, statuses 20/6/5/3, retro 2,
  amended_by 127, empty URLs 53, and all 34 immediate-predecessor supersedes links (None for v1).
- All 32 fixed C4-A spec cases pass. URL preflight counts were 53 empty both without and with FETCH-LOG; expectations
  were not changed. Projection tests include cumulative provenance, clause-only owner targets, exceptions and sources.
- FETCH-LOG verified at the owner-supplied _local_text/_raw/2026-11-13/FETCH-LOG.json path:
  43476df6fd7b9f72f453a48bdb83f831b1cd30be140b39f2f399dade2ca1423e, before and after.
- All four code users of the former repeal-last-day constant were printed before editing and replaced; historical
  report references updated. Existing C2 repeal-day test function is AST-identical to HEAD (all assertions retained).
- build(write=False) creates nothing; synthetic default/write=True outputs match the existing serializer's four files
  and hashes. Guard body tests stub build and do not read the corpus; historical body-hash serialization retained.

#### Required check results

| Check | Before | After / result |
|---|---|---|
| pytest collection | 613 | 681 (+68) |
| Full pytest | not run as a baseline (collection baseline only) | 680 passed, 1 skipped, 62.53 s, exit 0 |
| CI flake8 selection | 0, exit 0 | 0, exit 0 |
| Full CI flake8 | 740 findings, configured exit 0 | 743 findings, configured exit 0 |
| gate0 | not rerun as baseline | 0 blockers, 7 warnings, exit 0 |
| corpus_hash --verify | not rerun as baseline | 17 frozen / 17 current, no drift, exit 0 |
| statute_validate | not rerun as baseline | 0 records, 0 errors, 0 warnings, exit 0 |
| statute_tables --check | not rerun as baseline | effects accepted 50/rejected 0; versions accepted 32/rejected 2, exit 1 |

The skipped existing test is test_v14_not_a_git_repo_warn: the mandated scratch tmp_path is inside the repository's
Git work tree. Full lint remains advisory exactly as the checked-in CI command; the increase is one C901, one E305,
and one E501 finding. No lint selection/threshold was weakened and no skip was added.

Code guard output (exit 0):

    statute_guard --code: 34 rows sha256 b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 PASS

Failing check output (exit 1):

    AMENDMENT-EFFECTS.csv: accepted 50, rejected 0
    VERSION-DATES.csv: accepted 32, rejected 2
      REJECTED act:1961:2:v6: V05: in_force_from 2026-04-01 must be < in_force_to 2026-04-01
      REJECTED act:1961:285BAA:v1: V05: in_force_from 2026-04-01 must be < in_force_to 2026-04-01

Protected SHA-256 values before AND after (identical, independently re-read):

- VERSION-DATES.csv: 572ea9315a05ffd16cec9b592821177e2dbfd2e95712759faf21adeede52bca4
- AMENDMENT-EFFECTS.csv: b3ecb5dd1fb2c2587e01f27dab90494772474d3c3ed7456cc8ad12dc741baf5c
- SOURCES.json: 45c3fcd4fa2279da006d40f46b7d306cde76f173b6d288733286acb234d43073
- Expected body guard remains aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d; NOT RUN.

#### Per-file implementation diff (+ / - relative to HEAD; new files counted in full)

| File | + | - |
|---|---:|---:|
| divergence/DECISION-D78-AMENDMENT-2026-11-16.md | 89 | 0 |
| divergence/statute_schema.py | 33 | 4 |
| divergence/statutes/schema/statute_record.schema.json | 24 | 4 |
| divergence/statute_validate.py | 15 | 5 |
| divergence/statute_lookup.py | 100 | 42 |
| divergence/statute_records.py | 170 | 0 |
| divergence/statute_guard.py | 44 | 0 |
| divergence/statute_build.py | 5 | 4 |
| tests/test_statute_schema.py | 45 | 1 |
| tests/test_statute_lookup.py | 123 | 3 |
| tests/test_statute_validate.py | 52 | 0 |
| tests/test_statute_build.py | 61 | 0 |
| tests/test_statute_records.py | 198 | 0 |
| tests/test_statute_guard.py | 38 | 0 |
| tests/fixtures/statutes/records/2025/act__2025__sFAKE5__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE2__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE4__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE4__v2.json | 1 | 1 |

logs/P09_C4_report.md is also modified (this section); its final diff count and SHA, all implementation file SHAs,
and the scratch handoff state are recorded in C4_handoff_B.md after this append. No other committed paths edited.

#### SELF-AUDIT (C4-B resumed STOP)
1. Plan gate: kept yes; resume explicitly approved and all 20 per-file confirmations retained; no new edit scope added.
2. No commit/push: kept yes; changes remain uncommitted; only owner-prepared commit commands supplied at STOP.
3. Protected files: kept yes; table/source/FETCH hashes identical; original D78, real bodies, owner files, frozen corpus,
   replay cache, runs, pre-registration, QA scorer and TEST files not edited; no real freeze or real records written.
4. Offline/no new dependencies/secrets: kept yes; no network/model/API calls, installs or environment/key reads.
   PYTHONDONTWRITEBYTECODE was set, not read, to prevent subprocess bytecode writes.
5. Write scope: kept yes; only the 19 approved committed paths and scratch artifacts; pytest basetemp under scratch.
6. Deterministic STOP: kept yes; statute_tables failure stopped implementation immediately; no fix, retry, expected-result
   edit or weakened check followed; only mandatory STOP evidence and report/handoff writes followed.
7. Report/public content: kept yes; summaries/details/audits present; no keys, personal data or substantive law text.
8. Handoff: kept yes; C4_handoff_B.md extended with latest files, SHAs, counts and blocking question at STOP.

### C4-B option (a) fix and default-temp STOP (16 Nov 2026)

#### PLAIN SUMMARY
- What happened: owner approved the shared date-conversion fix, all six file edits and a narrow exception for the
  requested default-temp pytest run. Applied the fix and five regression cases. Scratch pytest passed; default-temp
  pytest failed during fixture setup with WinError 5 (Access is denied) while enumerating its temporary directory.
- What it means: the shared-helper changes are tested under scratch, but C4-B is still incomplete. The requested
  zero-skip default-temp run and the remaining verification sequence have not completed. Nothing committed or pushed.
- Problems: runtime filesystem access to pytest's default temporary directory. No test assertion caused this error.
  No retry, permission changes, new basetemp workaround, or remaining check was run after receiving the failure.
- Decision needed: owner instruction for a permission-reviewed default-temp retry, then the remaining approved checks.
- Next message: owner authorizes the recovery path and continuation; no further implementation changes proposed.

#### Changes (option a)
- statute_records.project_dates(vd, effects, sources) now holds the single repeal-day/retro date conversion, including
  predecessor ends. project() and statute_tables.check_versions/_record both use it. Canonical tables are not changed.
- Removed the table checker's separate retro conversion. Malformed raw date rejection and strict record V05 remain.
- New regression cases: both real repeal-day rows accepted (two cases); ordinary equal-date row still rejected;
  all 34 shared temporal projections match project(); retro predecessor end moves preserved (five cases total).
- The existing synthetic retro test now supplies its raw deemed-date start as required by D5; its expected values
  are unchanged. Synthetic effects carry target_act/target_section. No expected result was edited or skip added.
- Original C2 repeal-day test function remains AST-identical to HEAD; all existing C2 assertions are retained.
- E305 blank line and E501 wrapping edits applied. The former new C901 was project, complexity 18; date, row and
  knowledge-link helpers were mechanically extracted. Final flake8 count and complexity verification are pending.

#### Check results and pending work

| Check | Original / previous result | This attempt |
|---|---|---|
| Collection | 613 original; 681 before fix | 686 (+5 fix cases; +73 overall) |
| Scratch full pytest | 680 passed, 1 skipped | 685 passed, 1 skipped, 32.45 s, exit 0 |
| Pytest without basetemp | not run | 20 passed, 1 setup error, 1.31 s, exit 1; stopped at first error |
| CI-selected flake8 | 0 before / 0 last run | not rerun: STOP occurred first |
| Full CI flake8 | 740 original / 743 last run | not rerun; target 740 is not yet verified |
| statute_guard --code | 34 rows, approved SHA, PASS | not rerun after fix |
| gate0 | 0 blockers, 7 warnings, exit 0 | not rerun after fix |
| corpus_hash --verify | 17/17 match, exit 0 | not rerun after fix |
| statute_validate | 0 records/errors/warnings, exit 0 | not rerun after fix |
| statute_tables --check | effects 50/0, versions 32/2, exit 1 before fix | not rerun after fix; target 50/0 and 34/0 remains required |

The scratch skip is the unchanged test_v14_not_a_git_repo_warn because its tmp_path lies inside the repository.
The default-temp error occurred at setup of test_csv_never_overwritten_and_owner_columns_kept. Temporary directory
enumeration was denied before its test body ran. No personal temporary path is included in this public report.

Commands actually run:

    python -B -m pytest --collect-only -q -p no:cacheprovider
    python -B -m pytest -q -x -p no:cacheprovider --basetemp=divergence/statutes/_local_text/scratch/C4-B-fix-pytest
    python -B -m pytest -q -x -p no:cacheprovider

PYTHONDONTWRITEBYTECODE was set (not read) for both test processes. The default-temp exception was explicitly
approved by the owner; no source edits occurred outside the workspace and no permission changes were attempted.

Last measured code guard output (before this fix; not presented as a rerun):

    statute_guard --code: 34 rows sha256 b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 PASS

Protected hashes before AND after this fix (identical, independently re-read for STOP evidence):

- VERSION-DATES.csv: 572ea9315a05ffd16cec9b592821177e2dbfd2e95712759faf21adeede52bca4
- AMENDMENT-EFFECTS.csv: b3ecb5dd1fb2c2587e01f27dab90494772474d3c3ed7456cc8ad12dc741baf5c
- SOURCES.json: 45c3fcd4fa2279da006d40f46b7d306cde76f173b6d288733286acb234d43073
- FETCH-LOG: 43476df6fd7b9f72f453a48bdb83f831b1cd30be140b39f2f399dade2ca1423e
- Real body guard not run; first real run remains C4-C. No real records or law bodies written.

#### Updated per-file implementation totals (+ / - relative to HEAD)

| File | + | - |
|---|---:|---:|
| divergence/DECISION-D78-AMENDMENT-2026-11-16.md | 89 | 0 |
| divergence/statute_schema.py | 34 | 4 |
| divergence/statutes/schema/statute_record.schema.json | 24 | 4 |
| divergence/statute_validate.py | 15 | 5 |
| divergence/statute_lookup.py | 100 | 42 |
| divergence/statute_records.py | 211 | 0 |
| divergence/statute_guard.py | 44 | 0 |
| divergence/statute_build.py | 5 | 4 |
| tests/test_statute_schema.py | 45 | 1 |
| tests/test_statute_lookup.py | 123 | 3 |
| tests/test_statute_validate.py | 52 | 0 |
| tests/test_statute_build.py | 61 | 0 |
| tests/test_statute_records.py | 198 | 0 |
| tests/test_statute_guard.py | 38 | 0 |
| tests/fixtures/statutes/records/2025/act__2025__sFAKE5__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE2__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE4__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE4__v2.json | 1 | 1 |
| divergence/statute_tables.py | 16 | 10 |
| tests/test_statute_tables.py | 54 | 2 |

The report is also modified; its final SHA and diff totals, all 21 changed-file SHAs, and this STOP's pending work
are recorded in scratch/C4_handoff_B.md after this append. The report and all implementation changes stay uncommitted.

#### SELF-AUDIT (option a STOP)
1. Plan gate: kept yes; follow-up plan, all six file approvals and the default-temp exception received before changes.
2. No commit/push: kept yes; owner-only commands prepared, never executed.
3. Protected files: kept yes; hashes identical; no protected input, body, owner, freeze, cache, runs, preregistration,
   QA scorer or TEST-set file edited; strict V05 unchanged and C2 assertions retained.
4. Offline/dependencies/secrets: kept yes; no network/model/API calls, installs or environment/key reads.
5. Write scope: kept yes; approved workspace files/scratch, plus only the explicitly approved pytest default-temp exception.
6. STOP/determinism: kept yes; default-temp PermissionError stopped execution; no retries, weakened checks, new skips,
   expected-result edits or code fixes followed. Only mandatory STOP reporting/evidence was produced afterwards.
7. Report/public content: kept yes; summary, details and audit; no keys, personal data or substantive law text.
8. Handoff: kept yes; updated at STOP with final files, hashes, counts and pending verification.

### C4-B remaining checks and whitespace STOP (16 Nov 2026)

#### PLAIN SUMMARY
- What happened: owner prohibited any default-temp retry and assigned plain pytest to himself. Ran only the
  authorized remaining checks sequentially. Scratch pytest and every runtime/lint/hash check passed. git diff --check
  then failed because this report had a new blank line at EOF (line 482), introduced in the previous report append.
- What it means: shared projection/table-check behavior is verified, including real effects 50/0 and versions 34/0.
  C4-B remains at STOP because the final diff check failed; git status --short was not run after that failure.
- Problems: report-only EOF whitespace. This mandatory STOP append consumes the former trailing blank as a section
  separator and ends with a single newline; that is not presented as a successful recheck. No implementation changed.
- Decision needed: owner instruction to run the final git diff --check and git status --short after this report update.
- Next message: owner authorizes those two checks. Plain pytest remains owner-run; no temp retry or permission change.

#### Final runtime/check table

| Check | Before C4-B | Latest result |
|---|---|---|
| Collected tests | 613 | 686 (+73; measured before this unchanged-code run) |
| Scratch pytest | collection baseline only | 685 passed, 1 skipped, 31.85 s, exit 0 |
| CI-selected flake8 | 0 | 0, exit 0 |
| Full CI flake8 | 740 | 740, configured warning exit 0; all three new findings removed |
| statute_guard --code | approved reference SHA | 34 rows, identical approved SHA, PASS, exit 0 |
| gate0 | not rerun as baseline | 0 blockers, 7 warnings, exit 0 |
| corpus_hash --verify | frozen manifest unchanged | 17 frozen / 17 current, no drift, exit 0 |
| statute_validate | no real records | 0 records, 0 errors, 0 warnings, exit 0 |
| statute_tables --check | 50 effects / 34 version rows | effects accepted 50/rejected 0; versions accepted 34/rejected 0; exit 0 |
| Protected hashes | approved reference values below | all four match, exit 0 |
| git diff --check | previously passed before last report append | exit 1: logs/P09_C4_report.md:482: new blank line at EOF |
| git status --short | previously recorded 21 changed paths | not run after failure |

The existing scratch skip is test_v14_not_a_git_repo_warn, because scratch tmp_path is in the Git work tree.
No test or skip was changed. Plain pytest was not retried, no default temporary folder accessed by this run,
and no permissions were changed. The owner will run plain pytest himself.

Current code guard output:

    statute_guard --code: 34 rows sha256 b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 PASS

Current real-table integration output:

    AMENDMENT-EFFECTS.csv: accepted 50, rejected 0
    VERSION-DATES.csv: accepted 34, rejected 0

Protected SHA-256 values before AND after (identical; all four checked against approved references):

- VERSION-DATES.csv: 572ea9315a05ffd16cec9b592821177e2dbfd2e95712759faf21adeede52bca4
- AMENDMENT-EFFECTS.csv: b3ecb5dd1fb2c2587e01f27dab90494772474d3c3ed7456cc8ad12dc741baf5c
- SOURCES.json: 45c3fcd4fa2279da006d40f46b7d306cde76f173b6d288733286acb234d43073
- FETCH-LOG: 43476df6fd7b9f72f453a48bdb83f831b1cd30be140b39f2f399dade2ca1423e

Shared-helper regression/spec tests pass: repeal-day rows accepted; non-repeal equality rejected by strict V05;
retro/predecessor conversion shared; 32 spec cases; all 34 supersedes links; statuses 20/6/5/3, retro 2,
amended_by 127, empty URLs 53. Real body guard remains NOT RUN (C4-C). No real records written.

#### Updated implementation per-file totals (+ / - relative to HEAD)

| File | + | - |
|---|---:|---:|
| divergence/DECISION-D78-AMENDMENT-2026-11-16.md | 89 | 0 |
| divergence/statute_schema.py | 34 | 4 |
| divergence/statutes/schema/statute_record.schema.json | 24 | 4 |
| divergence/statute_validate.py | 15 | 5 |
| divergence/statute_lookup.py | 100 | 42 |
| divergence/statute_records.py | 211 | 0 |
| divergence/statute_guard.py | 44 | 0 |
| divergence/statute_build.py | 5 | 4 |
| tests/test_statute_schema.py | 45 | 1 |
| tests/test_statute_lookup.py | 123 | 3 |
| tests/test_statute_validate.py | 52 | 0 |
| tests/test_statute_build.py | 61 | 0 |
| tests/test_statute_records.py | 198 | 0 |
| tests/test_statute_guard.py | 38 | 0 |
| tests/fixtures/statutes/records/2025/act__2025__sFAKE5__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE2__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE4__v1.json | 1 | 1 |
| tests/fixtures/statutes/records/1961/act__1961__sFAKE4__v2.json | 1 | 1 |
| divergence/statute_tables.py | 16 | 10 |
| tests/test_statute_tables.py | 54 | 2 |

The report is also modified. Its final diff totals and SHA, all changed-file hashes, and this STOP's state
are recorded in scratch/C4_handoff_B.md after this append. All changes remain uncommitted.

#### SELF-AUDIT (remaining-checks STOP)
1. Plan gate: kept yes; owner explicitly approved remaining checks; prior report/handoff edit approvals retained.
2. No commit/push: kept yes; no state-changing git command executed, owner-only commit lines prepared.
3. Protected files: kept yes; four protected hashes match; no real bodies, records, owner/freeze/cache/run/
   preregistration/QA scorer/TEST-file edits; strict V05 and C2 assertions unchanged.
4. Offline/dependencies/secrets: kept yes; no network/model/API calls, installs or environment/key reads.
5. Write scope: kept yes; only scratch pytest output and the approved report/handoff; no default-temp retry.
6. STOP/determinism: kept yes; whitespace check failure stopped the sequence immediately, no subsequent checks,
   source changes, retries or permission changes. Only mandatory STOP reporting/evidence followed.
7. Report/public content: kept yes; summary/details/audit; no keys, personal data or substantive law text.
8. Handoff: kept yes; updated with latest runtime results, file hashes, counts and the two pending git checks.

## C4-C: deterministic canonical records built and verified

### PLAIN SUMMARY
- What happened: built 34 real records and 31 local bodies twice with identical bytes. Validator and 32 real-record spec cases pass. After the owner-approved empty-root test fix, full pytest passes 729 tests with 1 existing skip; all remaining lint, gate, corpus, replay, table and hash checks pass.
- What it means: C4-C is complete and ready for owner review/commit; bodies remain local and protected inputs are unchanged.
- Problems: no C4-C blockers. Gate0 retains 7 existing warnings; full flake8 retains its 740-finding baseline with 0 C4-C findings. Five Gazette headings remain an explicit Part D eye-check item before D80.
- Decision needed: none for C4-C; owner decides review/commit and Part D sequencing. No commit/push or freeze was performed.
- Next message: owner review/commit result or Part D instructions.

### Implementation and source decisions
- New command: python -B -m divergence.statute_records --build. It reuses project(), project_dates(), build(write=False), extraction owner choices and the validator body-path resolver. It preflights metadata and all destination conflicts, writes UTF-8/LF deterministic JSON and local bodies, and reuses identical outputs without overwriting.
- Existing projection/date logic, canonical tables, schema, lookup, validator, extracted bodies and protected corpus/cache/run files are unchanged. New JSON omits printed body text; unprinted body metadata is null, and never-operative bodies are empty and hashed.
- First real body guard: 26 bodies, aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d PASS. Guard now uses latest_raw_dir() and prints the folder; seven PDF probes passed in _raw/2026-11-13.
- The five never-operative originals use registered ita2025_2025/FETCH-LOG source fields and headings, retain successor-based text_current_as_of=2026-03-30, and carry the registered full Gazette SHA note plus heading_not_gazette_checked. Their source_amended_up_to is null, matching the C2 unknown edition date.
- C3-20261115-211035 contains one GAZETTE-CHECK.md with 11 bounds and comparison hunks, no independent heading fields or complete body blocks. Applied the owner's explicit fallback; no new Gazette extraction.
- OPEN FOR PART D, BEFORE D80 FREEZE: owner eye check of 5 Gazette headings (2025 s.2, 393, 400, 446, 536).
- Real-record spec fixture reads only committed record JSON; no local-body access, skip or xfail. All 32 expected cases are unchanged. Owner-approved option (c) preserves the exact 0/0/0 assertion on an explicit empty temporary root and adds a real-default-root test for 34 records, 0 errors and exit 0 without asserting warnings (CI has no local bodies).

### Counts on REAL saved records

| Measurement | Expected | Actual |
|---|---|---|
| Records | 34 | 34 |
| in_force / repealed_saved / never_operative / unprinted | 20 / 6 / 5 / 3 | 20 / 6 / 5 / 3 |
| Retro | 2 | 2 |
| repeal_day_unsettled / corrigendum_open | 2 / 1 | 2 / 1 |
| source_label_gap notes | 3 | 3 |
| amended_by items / empty URLs | 127 / 53 | 127 / 53 |
| Counterpart filled, 1961 only | 17 | 17 |
| Printed / empty / absent body files | 26 / 5 / 3 | 26 / 5 / 3 |
| heading_not_gazette_checked notes | 5 | 5 |

### Check results

| Check | Actual result |
|---|---|
| Knowledge dates computed in process vs C2 sheet | all 7 entries equal; no sheet/body text printed |
| First real body guard | 26 bodies, approved SHA, PASS |
| Synthetic ingest and guard tests | 15 passed in 0.84 s |
| First build / second build | 65 files created / 0 files created |
| Byte identity | 34 JSON + 31 body files identical |
| Real-record validator | 34 records, 0 errors, 0 warnings; warning list: none |
| Real-record spec cases | 32 passed, 41 deselected, 0.24 s |
| Round-trip code columns | b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 PASS |
| Full VERSION-DATES rejoin | 572ea9315a05ffd16cec9b592821177e2dbfd2e95712759faf21adeede52bca4 PASS |
| Saved printed-body hashes vs guard map | 26/26 equal |
| Canonical tables | effects 50 accepted/0 rejected; versions 34 accepted/0 rejected |
| Full scratch pytest | 729 passed, 1 existing skip, 102.96 s, exit 0; total 730 |
| Strict / full flake8 counts | 0 / 740, both exit 0; 0 findings in C4-C source/test/verifier paths |
| gate0 | 0 blockers, 7 existing warnings, exit 0 |
| corpus_hash --verify | 17 frozen / 17 current, no drift, exit 0 |
| Guarded replay | facts/missing/attacked equal; all replay markers true; 0 live calls; all 5 cache hashes identical, exit 0 |
| Requested table/guard reruns | tables 50/0 and 34/0; code guard 34 rows, approved b7b8fa36 SHA; body guard 26 bodies, approved aebe8deb SHA; all exit 0 |

Round-trip recovers record dates/status (including retro predecessor ends and repeal-day equality), rejoins unchanged table-only fields by key, and verifies code/full CSV hashes. Shared projection fields are compared to the saved JSON. No owner columns or expected hashes were edited.

### Commands actually completed in the build/check phase

```powershell
python -B divergence/statutes/_local_text/scratch/C4_C_verify.py preflight --out divergence/statutes/_local_text/census/partC/C4-20261116-225408
python -B -m pytest tests/test_statute_ingest.py tests/test_statute_guard.py -q -x -p no:cacheprovider --basetemp=divergence/statutes/_local_text/scratch/C4-C-ingest-pytest
python -B -m divergence.statute_records --build
python -B divergence/statutes/_local_text/scratch/C4_C_verify.py snapshot --out divergence/statutes/_local_text/census/partC/C4-20261116-225408
python -B -m divergence.statute_records --build
python -B divergence/statutes/_local_text/scratch/C4_C_verify.py identical --out divergence/statutes/_local_text/census/partC/C4-20261116-225408
python -B -m divergence.statute_validate
python -B -m pytest tests/test_statute_records.py -k test_real_spec_case -q -x -p no:cacheprovider --basetemp=divergence/statutes/_local_text/scratch/C4-C-spec-pytest
python -B divergence/statutes/_local_text/scratch/C4_C_verify.py roundtrip --out divergence/statutes/_local_text/census/partC/C4-20261116-225408
python -B -m divergence.statute_guard --code
python -B divergence/statutes/_local_text/scratch/C4_C_verify.py protected --out divergence/statutes/_local_text/census/partC/C4-20261116-225408
python -B -m divergence.statute_tables --check
python -B -m pytest -q -x -p no:cacheprovider --basetemp=divergence/statutes/_local_text/scratch/C4-C-pytest-r2
python -B -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
python -B -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
python -B divergence/gate0_check.py
python -B divergence/corpus_hash.py --verify
python -B divergence/statutes/_local_text/scratch/C4_C_verify.py replay --out divergence/statutes/_local_text/census/partC/C4-20261116-225408
python -B -m divergence.statute_tables --check
python -B -m divergence.statute_guard --code
python -B -m divergence.statute_guard --body
```

Python bytecode writes were disabled, pytest cache disabled, and all pytest basetemps were dedicated scratch paths. Plain/default-temp pytest was not run. Guarded replay executed with network/provider/key/cache-write paths set to abort immediately; no such attempt occurred. The sole existing skip is test_v14_not_a_git_repo_warn because its temporary path is inside this Git work tree. No skip/xfail was added.

### Per-record metadata (34 real records; no body text)

Intervals are half-open; null dates never cover. SHA column is the first 12 hex characters of body_sha256; full hashes are in record JSON. Notes: label_gap=source_label_gap, heading_pending=heading_not_gazette_checked.

| Record ID | Status | From | To | Retro from | Applies TY | Basis | Knowledge | Edition | Flags | Amendments | Body chars | Body SHA prefix | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| act:1961:115BBH:v1 | repealed_saved | 2023-04-01 | 2026-04-01 | ? | 2022-23..2025-26 | charging_ay_rule | 2023-03-31 | ita1961_2023 | ? | 1 | 1342 | 10f8d8055627 | ? |
| act:1961:158B:v1 | in_force | 2023-03-31 | 2024-09-01 | ? | ? | unclear | 2023-03-31 | ita1961_2023 | ? | 0 | 1266 | bf01191553bb | ? |
| act:1961:158B:v2 | in_force | 2024-09-01 | 2025-03-29 | ? | 2024-25..2024-25 | transaction_date | 2024-08-16 | ita1961_2024n2 | ? | 1 | 1588 | 7a931bde29de | ? |
| act:1961:158B:v3 | repealed_saved | 2025-03-29 | 2026-04-01 | 2025-02-01 | 2024-25..2025-26 | transaction_date | 2025-03-29 | ita1961_2025 | ? | 2 | 1642 | 55234ff1d2b5 | ? |
| act:1961:194S:v1 | in_force | 2022-07-01 | 2025-04-01 | ? | 2022-23..2024-25 | transaction_date | 2023-03-31 | ita1961_2023 | ? | 1 | 3134 | f3d03f14889c | ? |
| act:1961:194S:v2 | repealed_saved | 2025-04-01 | 2026-04-01 | ? | 2025-26..2025-26 | transaction_date | 2025-03-29 | ita1961_2025 | ? | 2 | 3142 | c26f2379d6fe | ? |
| act:1961:285BAA:v1 | in_force | 2026-04-01 | 2026-04-02 | ? | ? | unclear | 2025-03-29 | ita1961_2025 | repeal_day_unsettled | 1 | 2159 | 4c28b245a127 | ? |
| act:1961:2:v1 | in_force | 2023-04-01 | 2024-04-01 | ? | 2022-23..2022-23 | charging_ay_rule | 2023-03-31 | ita1961_2023 | ? | 6 | 64271 | 3a304eadfea8 | label_gap |
| act:1961:2:v2 | unprinted | 2024-04-01 | 2024-08-16 | ? | ? | unclear | 2026-03-30 | ita1961_2026 | ? | 8 | null | null | ? |
| act:1961:2:v3 | unprinted | 2024-08-16 | 2024-10-01 | 2024-07-23 | ? | unclear | 2026-03-30 | ita1961_2026 | ? | 13 | null | null | ? |
| act:1961:2:v4 | in_force | 2024-10-01 | 2025-04-01 | ? | 2024-25..2024-25 | transaction_date | 2024-08-16 | ita1961_2024n2 | ? | 15 | 65253 | d0097d8fe9be | ? |
| act:1961:2:v5 | repealed_saved | 2025-04-01 | 2026-04-01 | ? | 2024-25..2024-25 | charging_ay_rule | 2025-03-29 | ita1961_2025 | ? | 17 | 66552 | 3e34f6c01908 | ? |
| act:1961:2:v6 | in_force | 2026-04-01 | 2026-04-02 | ? | 2025-26..2025-26 | charging_ay_rule | 2026-03-30 | ita1961_2026 | repeal_day_unsettled | 20 | 67100 | eba9234847f3 | ? |
| act:1961:3:v1 | repealed_saved | 2023-03-31 | 2026-04-01 | ? | 2022-23..2025-26 | charging_ay_rule | 2023-03-31 | ita1961_2023 | ? | 0 | 500 | eb1bf6ea93e2 | ? |
| act:1961:56:v1 | in_force | 2023-04-01 | 2024-04-01 | ? | 2022-23..2022-23 | charging_ay_rule | 2023-03-31 | ita1961_2023 | ? | 5 | 19309 | 309999cb8b8d | label_gap |
| act:1961:56:v2 | in_force | 2024-04-01 | 2025-04-01 | ? | 2023-24..2023-24 | charging_ay_rule | 2024-08-16 | ita1961_2024n2 | corrigendum_open | 7 | 21124 | 18a6eee0f418 | label_gap |
| act:1961:56:v3 | repealed_saved | 2025-04-01 | 2026-04-01 | ? | 2024-25..2025-26 | charging_ay_rule | 2025-03-29 | ita1961_2025 | ? | 8 | 21344 | 1ddea0ea86f4 | ? |
| act:2025:194:v1 | in_force | 2026-04-01 | open | ? | 2026-27..open | ita2025_tax_year | 2026-03-30 | ita2025_2026 | ? | 0 | 6124 | 33cdfdaee294 | ? |
| act:2025:1:v1 | in_force | 2026-04-01 | open | ? | 2026-27..open | ita2025_tax_year | 2026-03-30 | ita2025_2026 | ? | 0 | 187 | c1c5f4532885 | ? |
| act:2025:2:v1 | never_operative | null | null | ? | ? | unclear | 2026-03-30 | ita2025_2025 | ? | 0 | 0 | e3b0c44298fc | heading_pending |
| act:2025:2:v2 | in_force | 2026-04-01 | open | ? | 2026-27..open | ita2025_tax_year | 2026-03-30 | ita2025_2026 | ? | 4 | 59370 | 4399ccd118fe | ? |
| act:2025:301:v1 | in_force | 2026-04-01 | open | ? | 2026-27..open | transaction_date | 2026-03-30 | ita2025_2026 | ? | 0 | 1713 | 9787f22bc599 | ? |
| act:2025:393:v1 | never_operative | null | null | ? | ? | unclear | 2026-03-30 | ita2025_2025 | ? | 0 | 0 | e3b0c44298fc | heading_pending |
| act:2025:393:v2 | in_force | 2026-04-01 | 2027-04-01 | ? | 2026-27..2026-27 | transaction_date | 2026-03-30 | ita2025_2026 | ? | 4 | 40384 | b448b2d07355 | ? |
| act:2025:393:v3 | unprinted | 2027-04-01 | open | ? | ? | unclear | 2026-03-30 | ita2025_2026 | ? | 6 | null | null | ? |
| act:2025:3:v1 | in_force | 2026-04-01 | open | ? | 2026-27..open | ita2025_tax_year | 2026-03-30 | ita2025_2026 | ? | 0 | 485 | e106d9a73f72 | ? |
| act:2025:400:v1 | never_operative | null | null | ? | ? | unclear | 2026-03-30 | ita2025_2025 | ? | 0 | 0 | e3b0c44298fc | heading_pending |
| act:2025:400:v2 | in_force | 2026-04-01 | open | ? | 2026-27..open | procedural | 2026-03-30 | ita2025_2026 | ? | 1 | 1477 | d9a47c256829 | ? |
| act:2025:446:v1 | never_operative | null | null | ? | ? | unclear | 2026-03-30 | ita2025_2025 | ? | 0 | 0 | e3b0c44298fc | heading_pending |
| act:2025:446:v2 | in_force | 2026-04-01 | open | ? | 2026-27..open | penalty_default_date | 2026-03-30 | ita2025_2026 | ? | 1 | 681 | d0663e95f202 | ? |
| act:2025:509:v1 | in_force | 2026-04-01 | open | ? | 2026-27..open | procedural | 2026-03-30 | ita2025_2026 | ? | 0 | 2188 | 473187baa637 | ? |
| act:2025:536:v1 | never_operative | null | null | ? | ? | unclear | 2026-03-30 | ita2025_2025 | ? | 0 | 0 | e3b0c44298fc | heading_pending |
| act:2025:536:v2 | in_force | 2026-04-01 | open | ? | 2026-27..open | procedural | 2026-03-30 | ita2025_2026 | ? | 4 | 11906 | 451d3e66ed80 | ? |
| act:2025:92:v1 | in_force | 2026-04-01 | open | ? | 2026-27..open | ita2025_tax_year | 2026-03-30 | ita2025_2026 | ? | 0 | 8152 | ff4d35394113 | ? |

### Protected-file hashes before/after

- Equality: PASS; all protected hashes and the frozen cache file set are unchanged. Replay-specific before/after maps also match all 5 current frozen cache files.

| File | Before SHA-256 | After SHA-256 |
|---|---|---|
| divergence/corpus/FREEZE-HASHES.json | 4a839ee99b74b14c86f1f5ef6a3cc18324c2a4aa6919f3baf495f33f9e767538 | 4a839ee99b74b14c86f1f5ef6a3cc18324c2a4aa6919f3baf495f33f9e767538 |
| divergence/replay_cache/01096fd4bb6f1f5ea12355d99d850bd11508c54bd698bddf3e2939c96e4e3148.json | f407b26bec1b99df18d5b9af4d41b387d64f50dc159d48317da948e5949b3098 | f407b26bec1b99df18d5b9af4d41b387d64f50dc159d48317da948e5949b3098 |
| divergence/replay_cache/477b65700f77a23e8128fd99166ebcc72441940b013d1534c6394656e2281e37.json | 45c18d1cfe88bdba37d4b82f4fd4ad4df4dccfbe0a8e9003c23fdb42a27cfa72 | 45c18d1cfe88bdba37d4b82f4fd4ad4df4dccfbe0a8e9003c23fdb42a27cfa72 |
| divergence/replay_cache/7e51ef4f4e8cb1ed7a71ab7e87291af8a47c87763662f95e1e36d5de57a963d6.json | a0cdd7fc301467470489b7426d882421764b8e055a063e6690c99b4f233ad16d | a0cdd7fc301467470489b7426d882421764b8e055a063e6690c99b4f233ad16d |
| divergence/replay_cache/892dca8aa3f772263f11e6264b2ee5b85ea9de67db22807576f4e3746fbca1df.json | c061239da762cd3620a4ee9637ab34075a3225e159fa080b8d6d6faabfb34268 | c061239da762cd3620a4ee9637ab34075a3225e159fa080b8d6d6faabfb34268 |
| divergence/replay_cache/f66dbeb4d9c554397f728f5830a97a44e55d1d9ba456918a5c9377b5e2dfb3cd.json | d1a89686b33fcdd62682ca9231bef3ec7a79a44696f61aa521ca2aa3520a5793 | d1a89686b33fcdd62682ca9231bef3ec7a79a44696f61aa521ca2aa3520a5793 |
| divergence/statutes/AMENDMENT-EFFECTS.csv | b3ecb5dd1fb2c2587e01f27dab90494772474d3c3ed7456cc8ad12dc741baf5c | b3ecb5dd1fb2c2587e01f27dab90494772474d3c3ed7456cc8ad12dc741baf5c |
| divergence/statutes/MAPPING.csv | 192eba4d125dd181e3056e332806abffe189de905a8ff6e943868b1385603902 | 192eba4d125dd181e3056e332806abffe189de905a8ff6e943868b1385603902 |
| divergence/statutes/SOURCES.json | 45c3fcd4fa2279da006d40f46b7d306cde76f173b6d288733286acb234d43073 | 45c3fcd4fa2279da006d40f46b7d306cde76f173b6d288733286acb234d43073 |
| divergence/statutes/VERSION-DATES.csv | 572ea9315a05ffd16cec9b592821177e2dbfd2e95712759faf21adeede52bca4 | 572ea9315a05ffd16cec9b592821177e2dbfd2e95712759faf21adeede52bca4 |
| divergence/statutes/_local_text/_raw/2026-11-13/FETCH-LOG.json | 43476df6fd7b9f72f453a48bdb83f831b1cd30be140b39f2f399dade2ca1423e | 43476df6fd7b9f72f453a48bdb83f831b1cd30be140b39f2f399dade2ca1423e |
| divergence/statutes/_local_text/census/partC/C2-20261116-071401/PENDING-23.md | 5e0c17599b4ab5c6c051a2bacbba3ecab9241be288ca0634aa5bd9b9dd2b001d | 5e0c17599b4ab5c6c051a2bacbba3ecab9241be288ca0634aa5bd9b9dd2b001d |

### Test scans and change scope

- Literal _local_text scan of tests/test_statute_ingest.py: 0 matches.
- Literal _local_text scan of tests/test_statute_records.py: 0 matches.
- Literal _local_text scan of tests/test_statute_guard.py: 0 matches.
- Added/updated root-test functions have 0 literal _local_text matches; the pre-existing synthetic fixture constant in that file is unchanged. The only validator-test changes are the owner-approved empty-root fixture and added real-root test.
- Final completion scope: 42 paths (8 code/test/report paths and 34 JSON records), exactly matching expanded git status; 0 missing and 0 unexpected. No bodies or ignored local data. Exact SHA ledger, expanded status, 31 local body paths/hashes, and prepared commit commands are in the ignored handoff. No commit or push.

### Short incident history
- Earlier inspection search/path/filter errors were stopped and recorded; no retries or weakened checks followed without approval.
- Guard raw-root issue was corrected with explicit approval and a regression test; first real guard passed.
- Verifier relative-path display was normalized with explicit approval; existing census folder reused.
- Never-operative provenance and missing independent Gazette headings were resolved by the owner's explicit source/fallback rules.
- Prior STOP: the empty-default-root assumption failed; owner-approved option (c) now preserves the empty-root assertion and independently verifies the populated default root.


### Warning detail and final Git evidence

Validator warnings: none locally. Gate0's 7 existing warnings are: GST-CGST-50 missing s.74A text; IT-115BBH and IT-2-47A counterpart-number limitations; IT-439-8 unofficial-source limitation and unofficial source_type; ITR2026-RULE-247 missing s.514; SBI-TTBR-DATA community-archive limitation. Frozen files were not edited to close them.

Both flake8 commands match the approved baseline (0 / 740). Full output is in the existing local census folder; no new C4-C findings. Protected table, SOURCES, FETCH-LOG, MAPPING, FREEZE-HASHES and replay-cache hashes are identical before/after. The replay compared facts, missing and attacked field by field and required all replay markers.

Final git diff --stat (tracked diffs; 36 new untracked paths are additional):

```text
 divergence/statute_guard.py    |   4 +-
 divergence/statute_records.py  |  16 ++++
 logs/P09_C4_report.md          | 190 +++++++++++++++++++++++++++++++++++++++++
 tests/test_statute_guard.py    |  20 +++++
 tests/test_statute_records.py  |  14 ++-
 tests/test_statute_validate.py |   8 +-
 6 files changed, 249 insertions(+), 3 deletions(-)
```

Final git diff --check: PASS. Expanded git status exactly matches the 42-path list (6 modified + 36 new); no bodies are in the list. Prepared commands are printed at STOP and in the ignored handoff. Owner eye check of 5 Gazette headings remains open for Part D before D80; no freeze is claimed.

### SELF-AUDIT
1. Plan gate kept yes: implementation/source/fallback/guard changes approved by exact path; remaining check failures stop work.
2. No commit/push kept yes: read-only git evidence only; prepared 42-path completion commands never executed.
3. Protected items kept yes: before/after hashes identical; no owner/table/extracted-body/corpus/cache/runs/preregistration/scorer/TEST-set edit; no freeze or cache builder.
4. Offline/no secrets kept yes: no network/model/API calls, dependencies, environment/key inspection; only nonsecret bytecode controls set.
5. Paths kept yes: Test-Path before unconfirmed reads; no scratch recursion/locked-folder access/deletion/permission changes; same census folder and dedicated pytest folders.
6. Determinism/STOP kept yes: two builds and the final snapshot are byte-identical; prior failures stopped until explicit owner authorization. Full tests and every required final check now pass; no checks weakened or expected hashes edited.
7. Public reporting kept yes in this phase: metadata/hash labels only, no law body text, secrets, personal data or 31-path body ledger; prior output incident disclosed above.
8. Handoff kept yes: C4_handoff_C.md updated with all 42 changed-file SHAs, counts, final checks, the 31-body ledger, staging scope and Part D open item.
