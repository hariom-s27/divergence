# P09 — combined phase report (Parts A–E): statute corpus v1

Agent: Claude Code (Opus, high, ask-before-edits)
Date: 2026-11-21 · Branch `feat/p09-ingest` · HEAD at Part E: `d2018a14a954710e28bae26ea8a7e2d01875375c` (C-C; CI #124 green, owner-reported) · `main` = `8129a49` · PR #9 draft from this branch (owner-reported).
This report holds metadata only: paths, counts, hashes, ids, commit and CI numbers. It contains no law text and no keys.

How numbers are written here. Every corpus count comes from `divergence/statutes/census/d80_facts.json` and is written `value [facts: key]`; the key's definition is stored in that file. A total built from several keys is written `value [sum: key + key]`. A script checks every tagged value and every sum against the facts file (see Phase gate). Other numbers carry their source: `[REPO: <file>]`, `[LOCAL]` (seen only on the owner's machine), `[owner-reported]`, `INFERENCE` or `UNVERIFIED`.

## PLAIN SUMMARY
- **What happened:**
  - P09 built a versioned, point-in-time, frozen corpus of the Income-tax Act, 1961 and the Income-tax Act, 2025: 34 [facts: records.total] section-version records, with the metadata public in git and the law text kept local-only.
  - The corpus is frozen as `statutes-v1`: a hash manifest of 55 [facts: manifest.file_count] files, a golden lookup sweep of 41672 [facts: sweep.queries.total] queries, a code-computed facts file, and decision record D80. CI checks all of it on every push.
  - Part E re-ran the full phase gate (all green) and re-checked the local backup zip's sha256 (matches).
- **What it means:** P10 (the benchmark) and the retriever can cite any lookup as `statutes-v1` + manifest sha + `record_id` + `as_of` + `as_known_on`, and anyone can check that the corpus has not drifted. For the resume: a reproducible, hash-anchored legal corpus with point-in-time lookup, an ITD-vs-Gazette audit, and every number tied to code.
- **Problems:** No check failed. Open items: the old CI lint baseline "740" cannot be reproduced (see Phase gate); Python 3.10 in CI is past end of life; `LICENSE` is effectively empty; the scratch folder holds about 3.1 GB of working files [LOCAL]; 11 scratch folders cannot be opened by this account [LOCAL]. Two owner checks remain (O1, O2 below).
- **Decision needed:** none for P09. P10 start: decide P09C-27 (Python / action versions), E-13 (main-branch ruleset), `LICENSE`, and scratch cleanup (with an exact list and the owner's yes).
- **Next message:** the owner reviews this file and runs the commit lines at the end.

## Owner steps referenced in this report
- **O1.** The v1.0-reverie release notes first said "built by me"; the owner corrected them to "within a 3-person team" [owner-reported]. Status here: corrected — see owner step O1.
- **O2.** Fixity of backup copy 2 (Google Drive account A, the `G:` drive copy). The agent did not read `G:`. Status here: owner check — see owner step O2.

## 1. Timeline

Dates are commit dates from `git log` (Asia/Calcutta). "Not recorded" means no committed report or log names it.

| Part | Dates (2026) | Commits | CI runs | Tool | Report |
|---|---|---|---|---|---|
| A — fetcher, sources, section list, mapping | 13 Nov | `05dd3e1` | not recorded | not recorded | none; commit message only |
| B — extractor v1 → v11 | 13–14 Nov | `18cf28e`, `cc23478`, `81c9673`, `a2f41a5`, `235b486`, `c225e26`, `c5a0f19`, `557c52e`, `d79bbfe`, `8b63577`, `14fd0f8` | not recorded | not recorded | none; commit messages only |
| C0–C3 — title pages, act_parse ledger, version proposals, canonical CSVs | 15–16 Nov | `68da1aa`, `d942617`, `d1dd159`, `89f8cec`, `f1d967c` | not recorded | not recorded | none; commit messages only |
| C3-fix — effects parser, per-row checks, owner batches | 16 Nov | `aa4da25` … `eb09682` (15 commits) | not recorded | not recorded | [`logs/P09_C3fix_report.md`](P09_C3fix_report.md) |
| C4 — D78 amendment, lookup v2, 34 records, spot checks | 16–17 Nov | `80bafc6`, `7b7d357`, `8631d0a`, `c70ce8f`, `8dfaacc` | not recorded | not recorded | [`logs/P09_C4_report.md`](P09_C4_report.md) |
| D — audit, corrigenda, caveats, records refresh | 19–21 Nov | `ad87775`, `9886d6d`, fixes `424047e`, `98789f6` | #119 failed, #120 failed; both fixed | OpenAI Codex | [`logs/P09_D_report.md`](P09_D_report.md) |
| C-A — manifest scope, golden sweep, facts tool, CI steps | 21 Nov | `554adc2`, `f0e8967` | #122 green [REPO: logs/P09_C-B_report.md] | OpenAI Codex | [`logs/P09_C-A_report.md`](P09_C-A_report.md) |
| C-B — backup, restore test, freeze, facts, CI | 21 Nov | `9b5aa8d` | #123 green [owner-reported] | Claude Code | [`logs/P09_C-B_report.md`](P09_C-B_report.md) |
| C-C — DECISION-D80, decision-doc counts | 21 Nov | `d2018a1` | #124 green [owner-reported] | Claude Code | [`logs/P09_C-C_report.md`](P09_C-C_report.md) |
| E — this report, phase gate, backup fixity | 21 Nov | (this file; owner commits) | — | Claude Code | this file |

P09 has 44 commits on this branch whose subject starts with "P09" [LOCAL: `git log`]. D80 itself names the tools: "code by OpenAI Codex (P09 Part D, C-A) and Claude Code (C-B, C-C)" [REPO: divergence/DECISION-D80.md].

## 2. What was built

One line each; paths are in the repo unless marked local-only.

- **Fetcher + manual sources:** `divergence/statute_fetch.py` (GET-only, allowlisted host, rate gap, request cap, stop on 403/429), `divergence/statute_sources.py`, `divergence/statutes/SOURCES.json` (URLs plus manual items), `SECTION-LIST.json`, `MAPPING.csv`; gate0 skips `_local_text` (Part A, C0).
- **Extractor:** `divergence/statute_extract.py` v1 → v11.1 (page furniture, footnotes, tables, editor notes, amendment apparatus, Act-key aliases) (Part B, C0).
- **Amendment ledger and versions:** `divergence/act_parse.py`, `divergence/statute_build.py`, `divergence/statute_tables.py`; canonical `divergence/statutes/AMENDMENT-EFFECTS.csv` and `VERSION-DATES.csv` (C1–C3-fix).
- **Records (schema D78 + amendment):** `divergence/statute_schema.py`, `divergence/statute_records.py`, `divergence/statute_ingest.py`, records under `divergence/statutes/records/1961/` and `records/2025/`; amendment `divergence/DECISION-D78-AMENDMENT-2026-11-16.md` (C4).
- **Lookup v2:** `divergence/statute_lookup.py` — half-open date ranges, a reason for every non-FOUND result, "as known on" (amendments enacted later are hidden), and a corpus horizon (`CORPUS_CHECKED_THROUGH`) (C4-B).
- **Corrigendum disposition:** `divergence/statutes/CORRIGENDUM-DISPOSITION.csv` (Part D).
- **ITD-vs-Gazette audit (R1–R6):** rules in `V3_RULES` in `divergence/statute_build.py`, results in `divergence/statutes/census/ITD-GAZETTE-DIFFS.csv` (Part D).
- **Body caveats:** `divergence/statute_caveats.py`, `divergence/statutes/census/BODY-CAVEATS.csv` (Part D).
- **Label gaps:** `divergence/statutes/census/LABEL-GAPS.csv` (C3-fix evidence, Part D census).
- **Body guard:** `divergence/statute_guard.py` (`--code`, `--body`, `--raw`) rebuilds bodies and compares hashes; bodies themselves are local-only under `divergence/statutes/_local_text/` (git-ignored).
- **Manifest v1 freeze:** `divergence/statutes/STATUTE-HASHES.json`, written by `python -m divergence.statute_validate --freeze` in C-B (scope and preview built in C-A).
- **Golden sweep:** `divergence/statute_census.py` (`--check`, `--update`), golden files `divergence/statutes/census/sweep.json` and `D80_TIMELINE.md` (C-A).
- **Facts file:** `divergence/statute_facts.py`, `divergence/statutes/census/d80_facts.json` (C-A tool, C-B file).
- **D80:** `divergence/DECISION-D80.md` (C-C); decision-doc counts set to 39 (D41–D78 and D80; D79 reserved).
- **CI steps added** to `.github/workflows/python-package-conda.yml`: "Statute records validation (D78)" and "Golden lookup sweep check (D80)" (C-A); "Statute manifest verify (D80)" and "D80 facts check" (C-B).

## 3. Key numbers

All from `divergence/statutes/census/d80_facts.json` (facts_version 1, 53 keys). Definitions are in that file.

**Records**
- Records: 34 [facts: records.total] = 17 [facts: records.act.1961] (1961 Act) + 17 [facts: records.act.2025] (2025 Act). Check: 34 [sum: records.act.1961 + records.act.2025].
- By status: 20 [facts: records.status.in_force] in force, 6 [facts: records.status.repealed_saved] repealed but saved, 5 [facts: records.status.never_operative] never operative, 3 [facts: records.status.unprinted] unprinted. Check: 34 [sum: records.status.in_force + records.status.repealed_saved + records.status.never_operative + records.status.unprinted].
- Records flagged `repeal_day_unsettled`: 2 [facts: records.repeal_day_unsettled].
- `amended_by` items: 127 [facts: amended_by.items]; items with an empty URL: 0 [facts: amended_by.empty_url].

**Bodies (local-only)**
- 26 [facts: bodies.nonempty] bodies with text and 5 [facts: bodies.empty_placeholders] empty placeholders: 31 [sum: bodies.nonempty + bodies.empty_placeholders] records with a non-null `body_chars`.

**Manifest and horizon**
- Manifest: 55 [facts: manifest.file_count] files, sha256 `5b163396f1d98e0c5e4b08c4cf2cdc89adf879603a6edb60922f906db7fe6033` [facts: manifest.sha256].
- Corpus horizon: `2026-11-15` [facts: corpus_checked_through] (inclusive).

**ITD-vs-Gazette audit**
- Diff rows: 17 [facts: diffs.total] = 12 [sum: diffs.kept.itd.accidental + diffs.kept.itd.substantive + diffs.kept.instrument.substantive] kept + 5 [sum: diffs.removed.instrument.substantive + diffs.removed.pipeline.substantive] removed. Check: 17 [sum: diffs.kept.itd.accidental + diffs.kept.itd.substantive + diffs.kept.instrument.substantive + diffs.removed.instrument.substantive + diffs.removed.pipeline.substantive].
- Kept: 8 [facts: diffs.kept.itd.accidental] accidental ITD, 1 [facts: diffs.kept.itd.substantive] substantive ITD, 3 [facts: diffs.kept.instrument.substantive] amended-span leftovers.
- Removed: 3 [facts: diffs.removed.instrument.substantive] explained by an amending instrument, 2 [facts: diffs.removed.pipeline.substantive] caused by our own pipeline.

**Corrigenda, caveats, label gaps**
- Corrigenda: 7 [sum: corrigenda.class.typo + corrigenda.class.substantive] = 6 [facts: corrigenda.class.typo] typos + 1 [facts: corrigenda.class.substantive] substantive.
- Body caveats: 27 [facts: caveats.total] = 3 [facts: caveats.amended_span.substantive] amended span + 8 [facts: caveats.itd_diff.accidental] ITD accidental + 1 [facts: caveats.itd_diff.substantive] ITD substantive + 15 [facts: caveats.label_gap.unspecified] label gap. Check: 27 [sum: caveats.amended_span.substantive + caveats.itd_diff.accidental + caveats.itd_diff.substantive + caveats.label_gap.unspecified].
- Label-gap rows: 15 [facts: label_gaps.rows]. These rows fall in 3 [REPO: divergence/statutes/census/LABEL-GAPS.csv] versions (1961 Act s.2 v1, s.56 v1, s.56 v2), as stated in D80.

**Golden sweep (`census/sweep.json`, sha256 `e503aecec0efcc28fb2e37ae91e5c2444e97e5de57ee6f471c3400ec472fb051` [facts: sweep.sha256])**
- Queries: 41672 [facts: sweep.queries.total] = 39456 [facts: sweep.queries.daily] daily + 126 [facts: sweep.queries.tax_year] tax-year + 2090 [facts: sweep.queries.boundary] boundary. Check: 41672 [sum: sweep.queries.daily + sweep.queries.tax_year + sweep.queries.boundary].
- Statuses: 9792 [facts: sweep.statuses.found] FOUND, 6632 [facts: sweep.statuses.ambiguous] AMBIGUOUS, 25248 [facts: sweep.statuses.no_applicable_version] NO_APPLICABLE_VERSION. Check: 41672 [sum: sweep.statuses.found + sweep.statuses.ambiguous + sweep.statuses.no_applicable_version].
- Classes: 10123 [facts: sweep.classes.corpus] CORPUS, 26 [facts: sweep.classes.legal] LEGAL, 21730 [facts: sweep.classes.no_law] NO_LAW, 3 [facts: sweep.classes.query] QUERY.
- Reasons:

| Reason | Count |
|---|---|
| `before_commencement` | 16335 [facts: sweep.reasons.before_commencement] |
| `beyond_corpus_horizon` | 5590 [facts: sweep.reasons.beyond_corpus_horizon] |
| `after_repeal` | 5395 [facts: sweep.reasons.after_repeal] |
| `before_coverage` | 3518 [facts: sweep.reasons.before_coverage] |
| `known_text_not_in_corpus` | 597 [facts: sweep.reasons.known_text_not_in_corpus] |
| `unprinted_intermediate` | 310 [facts: sweep.reasons.unprinted_intermediate] |
| `unknown_enactment_date` | 108 [facts: sweep.reasons.unknown_enactment_date] |
| `repeal_day_unsettled` | 21 [facts: sweep.reasons.repeal_day_unsettled] |
| `applicability_unclear_row` | 3 [facts: sweep.reasons.applicability_unclear_row] |
| `midyear_effect` | 3 [facts: sweep.reasons.midyear_effect] |
| `overlap` | 2 [facts: sweep.reasons.overlap] |

Not cited here: `manifest.present` (its value is a boolean; the manifest exists).

## 4. Freeze anchors

| Anchor | Value | Source |
|---|---|---|
| Annotated tag | `statutes-v1` → `d2018a1` | owner screenshot [owner-reported] |
| Immutable release "Statute corpus v1 (D80)" | assets: `STATUTE-HASHES.json` `5b163396…6033`; `sweep.json` `e503aece…b051`; `d80_facts.json` `07b07b47…8da3`; plus a release attestation | owner screenshot [owner-reported]; the manifest and sweep shas equal the facts keys above; the facts-file sha is `07b07b47f3f369a526d6bce116cd8e4c882d6a5faf59d66524ce803d88968da3` [REPO: logs/P09_C-B_report.md] |
| Immutable release "Reverie Hacks 2026 submission (v1.0-reverie)" | → `92c6eda`; release notes corrected — see owner step O1 | [owner-reported] |
| Tag ruleset "frozen tags" | targets `statutes-v*`, `v1.0-reverie`; restricts updates and deletions; blocks force pushes; bypass list empty | [owner-reported] |
| GitHub Archive Program | on | [owner-reported] |
| Software Heritage | save request accepted 21 Nov 2026; SWHID pending | [owner-reported] |
| Freeze commit (manifest) | `9b5aa8dfc5e40ac3bebe206b99909f3a498802a1` | [REPO: divergence/DECISION-D80.md] |

**Backup of the local-only bodies and raw sources (3 copies)** [REPO: logs/P09_C-B_report.md]:

| # | Copy | Fixity at Part E |
|---|---|---|
| 1 | Laptop: `divergence\statutes\_local_text\scratch\backup-20261121.zip` (git-ignored) | `Get-FileHash … -Algorithm SHA256` = `D40E94743EC71C68DCA5F72C26E73CA01F6128A5932164588889BA2BE25B359F` — **equal to the C-B value; PASS** [LOCAL] |
| 2 | Google Drive account A (`G:` synced copy) | owner check — see owner step O2 |
| 3 | Google Drive account B (web upload) | owner-reported; no hash recorded |

The C-B restore test passed: 65/65 files matched their sha256 and the body guard rebuilt the same 26 bodies [REPO: logs/P09_C-B_report.md].

## 5. Phase gate (Part E, 2026-11-21, read-only, key unset, real outputs)

| # | Command | Real output | Result |
|---|---|---|---|
| 1 | `git status --short` | (empty) | PASS |
| 2 | `python -m pytest -q -p no:cacheprovider` | `898 passed, 1 skipped in 85.00s (0:01:25)` | PASS |
| 3 | `python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` (CI selection) | `0`, exit 0 | PASS |
| 4 | `python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics` (full, local) | `968` | info |
| 5 | same, with `--exclude divergence/statutes/_local_text` | `369` | info |
| 6 | `python -m divergence.gate0_check` | `0 problem(s) that block Gate 0`, `7 warning(s)`, `GATE 0 CLEAR on everything this script can see.`, exit 0 | PASS |
| 7 | `python corpus_hash.py --verify` (from `divergence/`) | `17 frozen hash(es), 17 current file(s)`; `[OK]  Every Tier A file's content matches its frozen hash. No drift.`, exit 0 | PASS |
| 8 | `python -m divergence.statute_validate` | `statute_validate: 34 records, 0 errors, 0 warnings`, exit 0 | PASS |
| 9 | `python -m divergence.statute_validate --verify` | `statute_validate: 34 records, 0 errors, 0 warnings`, exit 0 | PASS |
| 10 | `python -m divergence.statute_census --check` | `golden sweep: OK sweep.json e503aecec0efcc28fb2e37ae91e5c2444e97e5de57ee6f471c3400ec472fb051 D80_TIMELINE.md 9695d8ec9e32b433359dd0b1e3ba4f95feeda41e87e216ca1440554ae7a287d4`, exit 0 | PASS |
| 11 | `python -m divergence.statute_facts --check divergence/statutes/census/d80_facts.json` | `statute facts: OK`, exit 0 | PASS |
| 12 | `python -m divergence.statute_guard --code` | `statute_guard --code: 34 rows sha256 b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7 PASS`, exit 0 | PASS |
| 13 | `python -m divergence.statute_guard --body` (local only) | `statute_guard --body: 26 bodies sha256 aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d PASS`, exit 0 | PASS [LOCAL] |
| 14 | `python -m divergence.statute_caveats --check` (local only) | JSON summary: `"rows": 27`, `"counts": {"amended_span": 3, "itd_diff": 9, "label_gap": 15}`, `"span_hash_checks": 12`, `"fallback_rows": 12`, `"explicit_evidence_rows": 0`, 12 of 12 coverage entries `true`, 3 absence (zero-width) caveats, `"sha256": "d875053bc5993e0ce3c030c75f282ad94171b7ff983559da47cd7de9e03be7dc"`, exit 0 | PASS [LOCAL] |
| 15 | Backup zip `Get-FileHash` | `D40E94743EC71C68DCA5F72C26E73CA01F6128A5932164588889BA2BE25B359F` | PASS (equal) |

The caveats counts match the facts file: 3 amended span, 9 = 8 + 1 ITD, 15 label gap, 27 rows.

**flake8 counts, explained**
- (i) CI selection (the only lint that can fail CI): 0.
- (ii) Local full count: 968, of which 599 come from the git-ignored `divergence/statutes/_local_text/` (968 − 369, computed from rows 4 and 5) [LOCAL].
- (iii) Local, excluding `_local_text`: 369 [LOCAL]. Caveat: `--exclude` replaces flake8's default exclude list. There is no `.flake8`, `setup.cfg` or `tox.ini`, and no `.venv` folder, so this probably does not change the count (INFERENCE).
- (iv) CI-equivalent full count on a fresh clone of `d2018a1` (Python 3.10, flake8 7.5.0): 351 [owner-reported: fresh-clone run].
- The 369 vs 351 gap is likely untracked local files outside `_local_text` (INFERENCE; not checked file by file).
- Earlier baselines: "740" (CI scope, quoted in C4 and Part D reports) — historic, UNVERIFIED; it does not reproduce on a fresh clone. Local 958 (Part D) → 968 (C-A, +10 from new tests; two E128 fixed) [REPO: logs/P09_C-A_report.md].

**The 7 gate0 warnings, by file** (all in the frozen hackathon corpus; none blocks Gate 0)

| File | Warnings |
|---|---|
| `GST-CGST-50.md` | 1 — known_limitation still open |
| `IT-115BBH.md` | 1 — known_limitation still open (2025 Act section number) |
| `IT-2-47A.md` | 1 — known_limitation still open (2025 Act section number) |
| `IT-439-8.md` | 2 — known_limitation still open; `source_type = unofficial_full_text` |
| `ITR2026-RULE-247.md` | 1 — known_limitation still open |
| `SBI-TTBR-DATA.md` | 1 — known_limitation still open |

## 6. Problems and slips (metadata only)

| # | What | Status | Source |
|---|---|---|---|
| S1 | CI #119 failed: an f-string form that only Python 3.12 accepts, in `divergence/statute_sources.py` | fixed in `424047e` | [REPO: git log; DECISION-D80.md] |
| S2 | CI #120 failed: `test_r6` needed a git-ignored local folder | fixed in `98789f6` | [REPO: git log; DECISION-D80.md] |
| S3 | OpenAI Codex sandbox stops: git config access, pytest cache writes, CRLF line-ending warnings; each stop was resumed only after the owner's disposition | closed | [REPO: logs/P09_D_report.md, logs/P09_C-A_report.md]; [owner-reported] |
| S4 | 11 scratch pytest temp folders (`C-A-step*-pytest`, `C4-*-pytest`) return "Access denied" to this account; likely created by a sandboxed run (INFERENCE) | open; see Scratch | [LOCAL] |
| S5 | Auto-mode notices in Claude Code sessions: at C-C step C1, and again at Part E step E1. CLAUDE.md forbids auto mode; no write was made before APPROVED in either part | recorded | [REPO: logs/P09_C-C_report.md D4]; this report |
| S6 | C-B: a read-only helper probe script was written to the user's Temp folder, outside the workspace, before approval | recorded, not deleted | [REPO: logs/P09_C-B_report.md D1] |
| S7 | An agent suggested a lightweight tag for `statutes-v1`; not used — the owner created an annotated tag | closed | [owner-reported] |
| S8 | v1.0-reverie release notes first said "built by me" | corrected — see owner step O1 | [owner-reported] |
| S9 | D80 wording slip: D80 cites "risk R02" for the copyright question | left unchanged (D80 is a frozen decision file; edits need a new decision); recorded here | [REPO: divergence/DECISION-D80.md]; [owner-reported] |
| S10 | The D78 amendment still says "53 empty URLs"; the facts file gives 0 [facts: amended_by.empty_url]. D80 records the correction; the amendment file stays unchanged by rule | recorded | [REPO: logs/P09_C-C_report.md] |
| S11 | Parts A, B and C0–C3 have no part report in `logs/`; only commit messages | recorded | [LOCAL: `Get-ChildItem logs`] |

## 7. Known limits carried to P10

From D80 "Where it fails / what broke" [REPO: divergence/DECISION-D80.md]:
- Bodies come from the ITD consolidated PDFs, which differ from the Gazette in places; the Gazette is the authority (see the audit numbers above).
- Label gaps: 3 [REPO: divergence/statutes/census/LABEL-GAPS.csv] versions have bodies without clause labels; the labels are not printed in those PDFs.
- R1 cannot remove an ITD margin heading that falls mid-sentence.
- The 1 [facts: diffs.kept.itd.substantive] substantive ITD diff (a formula row) was not checked against the Gazette image.
- The corpus-horizon check (eGazette) was a title search, not full text [owner-reported].
- Bodies are not public: the copyright question is untested, so they stay local-only.
- P10 rule (P09D-39): no gold answer span may cross a body-caveat span, unless the question quotes the Gazette wording itself.
- Repeal day 1 April 2026: lookups are AMBIGUOUS (`repeal_day_unsettled`) because which Act governs that day is not settled.
- 4 [REPO: logs/P09_C-A_report.md] C901 complexity warnings remain in `divergence/statute_validate.py`.

Open repo-hygiene items for the start of P10:
- **P09C-27:** CI runs Python 3.10 (end of life 1 October 2026, as stated in D80) and older action versions (`actions/setup-python@v3`). Kept through P09; decide at P10 start.
- **E-13:** no ruleset on the `main` branch yet [owner-reported].
- **`LICENSE`:** the file is 2 bytes, effectively empty [LOCAL]. The owner should choose a licence (code vs metadata) before wider sharing.
- **Scratch cleanup:** see the next section; nothing is deleted without an exact list and the owner's yes for each item.
- The CLAUDE.md field-level replay check (DIVERGENCE_REPLAY=1) was not run in Part E (not in the Part E check list; nothing it reads changed in P09 C-A to E).

## 8. Scratch inventory (`divergence\statutes\_local_text\scratch\`, git-ignored, LOCAL)

Sizes from `Get-ChildItem -Recurse` on 2026-11-21. Nothing was deleted.

| Folder | Files | Bytes | Note |
|---|---|---|---|
| `backup-20261121` | 67 | 1,555,934,224 | backup staging (copy-1 source) |
| `restore-20261121` | 67 | 1,555,934,224 | C-B restore test |
| `ci_d1dd159` | 740 | 12,596,436 | earlier CI-like checkout |
| `pages` | 12 | 10,617,887 | page dumps |
| `c1_text` | 12 | 2,306,334 | C1 working text |
| `C3fix` | 16 | 319,624 | C3-fix working files |
| `refreeze-20261121` | 56 | 180,626 | C-B determinism re-freeze |
| `C-C-tools` | 2 | 19,298 | facts-key checker + negative-test copy |
| `__pycache__` | 2 | 16,253 | bytecode |
| `C-B-tools` | 3 | 8,894 | C-B helper scripts |
| 11 `*-pytest` folders | ? | ? | Access denied (S4) |

Loose files: the backup zip (1,541,535,636 bytes; keep — it is copy 1) and about 80 small probe scripts, run outputs and handoff notes (`c0_*`, `c3_*`, `C4_*`, `p09_*`). Cleanup is later, with an exact list and the owner's yes per item. The two largest candidates are `restore-20261121` and `backup-20261121` (about 3.1 GB together), but only after O2 confirms copy 2.

## 9. Post-write checks

See SELF-AUDIT item 4.

## Deviations
- **E-D1.** The task header said "Claude Code (Sonnet, high, ask-before-edits)". The model actually running is Opus, so the header and the commit line say Opus (owner decision at APPROVED).
- **E-D2.** `statute_caveats --check` ran in the background and finished after the E1 outline; its result was reported before APPROVED and is in row 14.
- **E-D3.** The flake8 count (iv) and the "historic, UNVERIFIED" tag on 740 come from the owner's answer at APPROVED, not from an agent run.

## SELF-AUDIT
1. **Steps asked vs done:** E1 steps 1–7 done and reported. E2: this file written; post-write checks in item 4. No other file created or edited.
2. **Decisions made or changed, and why:** header model per owner (E-D1); `manifest.present` not tagged because the checker compares the text "True" with lowercase prose; bodies sum written as "records with a non-null `body_chars`" to follow the key definitions; label gaps given both as 15 rows (facts) and 3 versions (REPO), as D80 does.
3. **Implementation:** one new file, `logs/P09_report.md`. Commands are listed in the Phase gate table and in item 4.
4. **Checks (after writing this file, real outputs):**
   - Facts-key checker `python -B divergence\statutes\_local_text\scratch\C-C-tools\c3_factkeys.py logs\P09_report.md divergence\statutes\census\d80_facts.json`: first run 1 mismatch (my wording "55-file" glued to a tag; fixed by rewording, value unchanged); second run `facts tags: 57; sum tags: 10; skipped examples: 2; distinct keys used: 52 of 53; unused keys: ['manifest.present']; mismatches: 0`, exit 0. PASS.
   - Safety scan (`Select-String` with the five patterns from the Part E task: user-profile path, app-data folder, e-mail address, upper-case secret word, credential word): 0 hits. PASS. Statute body text: none; the file was written by the agent from metadata only (section numbers, rule names, counts, hashes).
   - `python -m pytest -q -p no:cacheprovider`: `898 passed, 1 skipped in 43.15s`. PASS.
   - `python -m divergence.statute_validate --verify`: `statute_validate: 34 records, 0 errors, 0 warnings`, exit 0. PASS.
   - `python -m divergence.gate0_check`: `0 problem(s) that block Gate 0`, `7 warning(s)`, `GATE 0 CLEAR on everything this script can see.`, exit 0. PASS.
5. **Frozen items:** corpus hash OK (row 7); statute manifest verify OK (row 9); facts OK (row 11); golden sweep OK (row 10). No file under `divergence/corpus/`, `replay_cache/`, `runs/` or `divergence/statutes/` was edited; no DECISION file was edited; the sealed test set was not touched. Replay check not run (see section 7).
6. **Assumed or not checked:** every [owner-reported] item (tag, releases, ruleset, Archive Program, Software Heritage, CI #123/#124, copy 2 and copy 3, flake8 351, S7–S9); CI run numbers before #119; the tools used in Parts A–C4 (not recorded); the cause of the 369 vs 351 gap.
7. **Errors and retries:** the scratch inventory hit "Access denied" on 11 folders (recorded, not retried with other rights). Several long checks were moved to the background by the owner; all finished with exit 0.
8. **Safety:** no commit, push, tag, merge, reset, clean, stash or delete; no `--freeze` or `--update`; no network or model calls; no environment variables or keys read or printed; no body files or PDFs opened by the agent (the guard and caveats tools read them internally).
9. **git status / git diff --stat:** `git status --short` = `?? logs/P09_report.md` (only this file). `git diff --stat` is empty (no tracked file changed).
10. **Risks for the next steps:** scratch cleanup must wait for O2; P10 must decide P09C-27 before CI runner images drop Python 3.10; any corpus change needs a new decision, `STATUTE-HASHES-v2` and tag `statutes-v2`.
