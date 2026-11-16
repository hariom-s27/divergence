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
- divergence/statute_schema.py:19 (STATUSES + unprinted), :36 (REPEAL_LAST_DAY -> REPEAL_DAY 2026-04-01);
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
