# P09 Part C-B — backup, restore test, freeze, facts, CI

Agent: Claude Code (Opus, high, ask-before-edits)
Date: 2026-11-21 · Branch `feat/p09-ingest` · Start HEAD `f0e896790b9fe5043ae861bd975a1f9173be0de6` (= origin; CI #122 green)
Items: P09C-07, P09C-08, P09C-09 (local check), P09C-11, P09C-12, P09C-13, P09C-14.
This report holds metadata only: paths, sizes, sha256 values, counts, ids and statuses. It contains no law text and no keys.

## PLAIN SUMMARY
- **What happened:**
  - The local statute bodies and raw sources (65 files, 1.56 GB) were backed up to a zip.
  - The zip was restored with a different tool and checked: 65/65 files match their sha, and the body guard rebuilt the same 26 bodies.
  - The statute corpus was frozen into `divergence/statutes/STATUTE-HASHES.json` (55 files). A second freeze of a fresh copy gave a byte-identical manifest.
  - `census/d80_facts.json` was written, and two CI steps were added: manifest verify and facts check.
- **What it means:** The statute corpus v1 is now locked by hashes that CI can check. Every reported count comes from code, in a checked facts file. The git-ignored law text has a backup that has been restored and verified.
- **Problems:**
  - No check failed.
  - The third backup copy was reported by the owner with no hash pasted to the agent.
  - The agent wrote one helper script to Temp before approval (deviation D1).
- **Decision needed:** None. Ready for the owner's commit.
- **Next message:** The owner reviews the diff and runs the prepared commit lines (end of report).

## Backup (B2) — P09C-11
Folder: `divergence/statutes/_local_text/scratch/backup-20261121/`. This folder is git-ignored.

Copy rule: files were copied as bytes with `shutil.copyfile`. Every source sha was checked before copying, and every copy was re-hashed after.

| Item | Value |
|---|---|
| `bodies/` | 31 files: 26 with body_chars > 0, 5 with body_chars == 0 |
| Records with no body file | 3, all `unprinted`, as expected |
| Body sha vs record `body_sha256` | 31/31 match |
| `raw/2026-11-13/` | 34 files: 30 registered in SOURCES.json by sha, 4 not registered |
| Unregistered raw files | `FETCH-LOG.json`, `manual/c13_2022.pdf`, `manual/c14_2022.pdf`, `manual/MANUAL-SOURCES.txt` |
| SOURCES.json sha entries found in raw | 26/26 |
| Raw files with identical bytes under two names | 4 pairs; both copies kept |
| `raw/spikes/` | 0 files (see spikes check) |
| Data files / bytes | 65 / 1,555,927,071 |
| Re-hash mismatches after copy | 0 |
| `SHA256SUMS.txt` | 65 lines, `<sha256>  <relative path>`, sorted, UTF-8, LF; data files only |
| `BACKUP-NOTE.txt` | date, HEAD, counts, total bytes, body guard sha; no text |

**Spikes check** (owner change 2). The small json and html spike files were not included.

| File | Bytes | sha256 | Same bytes as | Outcome |
|---|---|---|---|---|
| `_raw/spikes/ita1961_fa2026.pdf` | 179141656 | `73d264fd05bc3b19ee003f399aeb50faf7ea36a42f345fa94ebb9b3a2ad0cb93` | `ita1961_2026.pdf` | skipped |
| `_raw/spikes/pdf_test.pdf` | 114083035 | `548111b39d1e7d907ba7b117fd52b8b9db2afa3213dbaecdbd97f9dd4e459190` | `ita2025_2025.pdf` | skipped |

**Zip** (owner change 3): stdlib `zipfile`, ZIP_DEFLATED, allowZip64, UTF-8 names.

| Item | Value |
|---|---|
| Path | `divergence/statutes/_local_text/scratch/backup-20261121.zip` |
| Size | 1,541,535,636 bytes |
| Entries | 67 = 65 data files + 2 metadata files |
| Names equal folder relative paths | yes; 0 duplicates |
| `testzip` CRC check | OK |
| Non-ASCII names | 2, UTF-8 flag set on both |
| sha256 (`Get-FileHash`) | `D40E94743EC71C68DCA5F72C26E73CA01F6128A5932164588889BA2BE25B359F` |

**Copies (P09C-12).** The task asked for a USB third copy. A second, separate cloud account was used instead.

| # | Copy | Hash | Source of the hash |
|---|---|---|---|
| 1 | Laptop (local zip above) | `D40E9474…B359F` | agent |
| 2 | Google Drive account A, synced: `G:\My Drive\divergence-backup\backup-20261121.zip` | `D40E94743EC71C68DCA5F72C26E73CA01F6128A5932164588889BA2BE25B359F` (matches) | owner-pasted |
| 3 | Google Drive account B, a different account, web upload | not pasted to the agent | owner-reported |

The owner first described copy 3 as an "unsynced cold cloud drive" and then named it as Google Drive account B (web upload). It was used as the third copy in place of USB.

## Restore test (B3) — P09C-11
- The folder `divergence/statutes/_local_text/scratch/restore-20261121/` was checked absent, then filled with `Expand-Archive`, on purpose a different tool from `zipfile`. Exit `$?` True.
- Check against `SHA256SUMS.txt`: 65 listed, 65 checked, **0 mismatches, 0 missing, 0 extra**. Both metadata files are present. 1,555,927,071 bytes checked. The two em-dash names survived.
- `python -m divergence.statute_guard --body --raw divergence\statutes\_local_text\scratch\restore-20261121\raw\2026-11-13` returned 26 bodies, sha256 `aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d`, **PASS**.

## Freeze dry run (B4)
- `python -m divergence.statute_validate`: 34 records, 0 errors, 0 warnings.
- `python -m divergence.statute_validate --preview`: 55 files, 0 missing scope files. The list is identical to the B1 preview.
- Scope breakdown: 6 root metadata files, 4 census files, 10 owner files, 34 records, 1 schema = 55.
- `git status --short`: empty. `STATUTE-HASHES.json` was absent.

## Freeze (B5.1–3) — P09C-07, P09C-13
- The owner typed `yes freeze`. `python -m divergence.statute_validate --freeze` printed `froze 55 files -> STATUTE-HASHES.json`, exit 0. Freeze was run once on the default root.
- Manifest `divergence/statutes/STATUTE-HASHES.json`:

  | Field | Value |
  |---|---|
  | Keys | `corpus_checked_through`, `file_count`, `hashes`, `manifest_version` |
  | manifest_version | 1 |
  | file_count | **55** |
  | corpus_checked_through | 2026-11-15 |
  | hashes | 55 entries |
  | sha256 | `5b163396f1d98e0c5e4b08c4cf2cdc89adf879603a6edb60922f906db7fe6033` |

- **Determinism:** the 55 scope files were copied, by their relative paths only, to `divergence/statutes/_local_text/scratch/refreeze-20261121/`. That root sees 55 scope paths, identical to the real ones. `freeze(root, strict=False)` was run there through the Python API.

  | Manifest | sha256 |
  |---|---|
  | Real | `5b163396f1d98e0c5e4b08c4cf2cdc89adf879603a6edb60922f906db7fe6033` |
  | Re-freeze | `5b163396f1d98e0c5e4b08c4cf2cdc89adf879603a6edb60922f906db7fe6033` |

  The two files are **byte-identical**.

## Verify and census (B5.2, B5.4)
- `python -m divergence.statute_validate --verify`: 34 records, 0 errors, 0 warnings, exit 0. The tool prints no separate OK line; 0 errors with exit 0 means OK.
- `python -m divergence.statute_census --check`: `golden sweep: OK`, sweep.json `e503aecec0efcc28fb2e37ae91e5c2444e97e5de57ee6f471c3400ec472fb051`, D80_TIMELINE.md `9695d8ec9e32b433359dd0b1e3ba4f95feeda41e87e216ca1440554ae7a287d4`.

## Facts (B5.5) — P09C-08, P09C-14
- `python -m divergence.statute_facts --out divergence/statutes/census/d80_facts.json`: exit 0.
- `python -m divergence.statute_facts --check divergence/statutes/census/d80_facts.json`: `statute facts: OK`.
- facts_version 1, 53 facts. File sha256: `07b07b47f3f369a526d6bce116cd8e4c882d6a5faf59d66524ce803d88968da3`.
- Compared with the B1 baseline (`--print` before the freeze), only the 3 `manifest.*` facts changed:
  - present false → true
  - file_count null → 55
  - sha256 null → the manifest sha
- The other 50 values are unchanged.

| key | value |
|---|---|
| amended_by.empty_url | 0 |
| amended_by.items | 127 |
| bodies.empty_placeholders | 5 |
| bodies.nonempty | 26 |
| caveats.amended_span.substantive | 3 |
| caveats.itd_diff.accidental | 8 |
| caveats.itd_diff.substantive | 1 |
| caveats.label_gap.unspecified | 15 |
| caveats.total | 27 |
| corpus_checked_through | 2026-11-15 |
| corrigenda.class.substantive | 1 |
| corrigenda.class.typo | 6 |
| diffs.kept.instrument.substantive | 3 |
| diffs.kept.itd.accidental | 8 |
| diffs.kept.itd.substantive | 1 |
| diffs.removed.instrument.substantive | 3 |
| diffs.removed.pipeline.substantive | 2 |
| diffs.total | 17 |
| label_gaps.rows | 15 |
| manifest.file_count | 55 |
| manifest.present | true |
| manifest.sha256 | 5b163396f1d98e0c5e4b08c4cf2cdc89adf879603a6edb60922f906db7fe6033 |
| records.act.1961 | 17 |
| records.act.2025 | 17 |
| records.repeal_day_unsettled | 2 |
| records.status.in_force | 20 |
| records.status.never_operative | 5 |
| records.status.repealed_saved | 6 |
| records.status.unprinted | 3 |
| records.total | 34 |
| sweep.classes.corpus | 10123 |
| sweep.classes.legal | 26 |
| sweep.classes.no_law | 21730 |
| sweep.classes.query | 3 |
| sweep.queries.boundary | 2090 |
| sweep.queries.daily | 39456 |
| sweep.queries.tax_year | 126 |
| sweep.queries.total | 41672 |
| sweep.reasons.after_repeal | 5395 |
| sweep.reasons.applicability_unclear_row | 3 |
| sweep.reasons.before_commencement | 16335 |
| sweep.reasons.before_coverage | 3518 |
| sweep.reasons.beyond_corpus_horizon | 5590 |
| sweep.reasons.known_text_not_in_corpus | 597 |
| sweep.reasons.midyear_effect | 3 |
| sweep.reasons.overlap | 2 |
| sweep.reasons.repeal_day_unsettled | 21 |
| sweep.reasons.unknown_enactment_date | 108 |
| sweep.reasons.unprinted_intermediate | 310 |
| sweep.sha256 | e503aecec0efcc28fb2e37ae91e5c2444e97e5de57ee6f471c3400ec472fb051 |
| sweep.statuses.ambiguous | 6632 |
| sweep.statuses.found | 9792 |
| sweep.statuses.no_applicable_version | 25248 |

Each fact's definition and source are stored in `d80_facts.json`.

## Local-only checks (B5.6)
These checks need git-ignored files, so they cannot run in CI.

| Command | Result |
|---|---|
| `python -m divergence.statute_caveats --check` (P09C-09) | exit 0; rows 27; counts amended_span 3, itd_diff 9, label_gap 15; span_hash_checks 12; coverage 12/12 true; sha256 `d875053bc5993e0ce3c030c75f282ad94171b7ff983559da47cd7de9e03be7dc` (= BODY-CAVEATS.csv in manifest) |
| `python -m divergence.statute_guard --code` | 34 rows `b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7` PASS |
| `python -m divergence.statute_guard --body` | 26 bodies `aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d` PASS |
| `python -m divergence.gate0_check` | exit 0; `GATE 0 CLEAR on everything this script can see.`; 7 existing advisory notes (open known_limitation / unofficial source); 0 FAIL |
| `python corpus_hash.py --verify` (from `divergence/`) | exit 0; 17 frozen hashes, 17 files; `[OK] … No drift.` |

## CI diff (B5.7) — `.github/workflows/python-package-conda.yml`
Two steps were inserted right after "Golden lookup sweep check (D80)". Nothing else in the file changed.
```diff
@@ -49,6 +49,12 @@ jobs:
     - name: Golden lookup sweep check (D80)
       run: |
         python -m divergence.statute_census --check
+    - name: Statute manifest verify (D80)
+      run: |
+        python -m divergence.statute_validate --verify
+    - name: D80 facts check
+      run: |
+        python -m divergence.statute_facts --check divergence/statutes/census/d80_facts.json
     - name: Prompt-injection scanner self-test
```
Both commands were run from the repo root: verify exit 0 (0 errors), facts exit 0 (`statute facts: OK`).

## Tests and lint (B5.8)
- `python -m pytest -q -p no:cacheprovider`: **898 passed, 1 skipped** in 40.42 s, exit 0.
- `python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`: **0**, exit 0.
- Line endings: `git check-attr` gives `text set, eol lf` for both new files under `divergence/statutes/`. Neither file contains CRLF, so no CRLF warning is expected for them.

## Scratch folders created (all git-ignored under `divergence/statutes/_local_text/scratch/`; none deleted)
- `C-B-tools/`: `b2_backup.py`, `b3_check.py`, `b5_refreeze.py`
- `backup-20261121/` and `backup-20261121.zip`
- `restore-20261121/`
- `refreeze-20261121/`: 55 scope copies plus its own `STATUTE-HASHES.json`

## Deviations
- **D1.** In B1, before approval, the agent wrote a read-only probe script outside the repo: `%TEMP%\claude\…\scratchpad\b1_probe.py` (user profile path omitted). It only listed and hashed files. The owner told the agent to leave it untouched, and it was not deleted. Later helpers were moved into `scratch/C-B-tools/` (owner change 1).
- **D2.** The zip was built with stdlib `zipfile`, not `Compress-Archive` (owner change 3). The restore used `Expand-Archive`.
- **D3.** The third backup copy is a second Google Drive account, not USB, and has no agent-visible hash (owner decision; see P09C-12).
- **D4.** The B2 script added checks nobody asked for: a `testzip` CRC test and a check that the UTF-8 name flag is set.

## What was not done
- No commit, push or tag. No network or model calls. No `--update`. No second `--freeze` on the default root.
- No data, golden, frozen, CSV, records, SOURCES or DECISION files were edited.
- No body or PDF text was opened, printed or diffed.
- Nothing was deleted, including the scratch folders and the Temp `b1_probe.py`.
- The replay check from CLAUDE.md (DIVERGENCE_REPLAY=1, field-level) was not run. It is not part of the C-B task, and nothing it reads was changed.

## SELF-AUDIT
1. **Steps asked vs done:** B1–B5 were all done, in order, each after its own approval. The freeze ran only after `yes freeze`.
2. **Decisions:**
   - SHA256SUMS lists data files only, and the metadata files are known extras in B3.
   - The determinism check used the Python API `freeze(root, strict=False)` with `manifest_paths` to confirm the scope.
   - The facts comparison with the B1 baseline was done by eye across all 53 keys.
3. **Implementation:**
   - Tracked changes: a new `divergence/statutes/STATUTE-HASHES.json` (written by the tool), a new `divergence/statutes/census/d80_facts.json` (written by the tool), the workflow edit, and this report.
   - Git-ignored helpers: `b2_backup.py`, `b3_check.py`, `b5_refreeze.py`.
4. **Checks:** All passed. Real outputs are quoted in the sections above.
5. **Frozen items:** corpus_hash verify OK (17/17); census golden OK; the statute manifest verifies; records, CSVs and SOURCES were not touched. Replay check not run (see "What was not done").
6. **Assumed / not checked:**
   - The copy 2 hash and the existence of copy 3 are owner-reported. The agent did not read `G:` or account B.
   - The spikes json/html files were not hashed.
7. **Errors and retries:** None. Three long runs were moved to the background and all finished with exit 0.
8. **Safety:** No commit or push, no keys or environment variables read, no law text printed, no deletes.
9. **git status** before writing this report: ` M .github/workflows/python-package-conda.yml`, `?? divergence/statutes/STATUTE-HASHES.json`, `?? divergence/statutes/census/d80_facts.json`. With this report added, `?? logs/P09_C-B_report.md` joins them.
10. **Risks for next steps:**
    - Any later edit to one of the 55 scope files will fail CI verify until there is a new decision and a re-freeze.
    - The local scratch folders hold about 3.1 GB, which the owner can delete when they choose.
    - Copy 3 has no recorded hash.
