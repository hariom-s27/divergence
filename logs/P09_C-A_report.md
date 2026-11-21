Agent: OpenAI Codex (GPT-6.1 Sol, High, ask for approval).

## PLAIN SUMMARY

- What happened: Step 2 was committed by the owner as `554adc2`. Step 3 generated two golden files, inserted exactly two CI steps, and records metadata-only evidence here.
- What it means: the sweep SHA matches the approved value; D80 differs from C4 by exactly the approved s.56 v2 table row; the root preview now contains 55 files with no missing scope files.
- Problems: Gate0 reports seven existing corpus-limitation warnings and no blocking problem; all 17 frozen corpus files match. Four C901 findings remain by owner instruction. No required count, hash, fact or timeline check failed.
- Decision needed: owner reviews this report and runs the plain local checks before deciding whether to commit and push.
- Next message: final check results and prepared owner commit commands; Codex will STOP without committing.

## SELF-AUDIT

| Hard rule / amendment | Status | Evidence |
|---|---|---|
| 1. Plan gate before writes | Kept | Owner approved Step 2, its amendments, lint cleanup, and the printed Step 3 plan before their writes. |
| 2. Forbidden Git mutations | Kept | Codex ran no commit, push, tag, reset, checkout, clean or stash. The Step 2 commit was made by the owner. |
| 3. Offline, no paid/model calls, no secrets | Kept | Only local tools and standard-library calculations were used; no keys or environment values were read or printed. Bytecode suppression was set explicitly. P09 spend remains INR 0; external model/API calls: 0. |
| 4. No real-root freeze or forbidden generated JSON | Kept | No real-root freeze ran; `divergence/statutes/STATUTE-HASHES.json` and `divergence/statutes/census/d80_facts.json` remain absent. Test manifests are confined to pytest temporary fixtures. |
| 5. Protected data and files | Kept | Step 3 changes only the two authorized golden files, the workflow insertion, and this report. No records, existing CSV/JSON inputs, owner data, C4, frozen corpus, replay cache, runs, decisions, README or START-HERE were edited. |
| 6. No body text opened, printed, quoted or copied by Codex | Kept | Existing validator/tests may hash body bytes internally under the owner's amendment. Facts read only allowed metadata. Scope tests prune the real local-text folder before traversal and copy only metadata. Outputs and this report contain metadata only. |
| 7. Check unseen paths | Kept | Explicit Step 3 paths were checked with Test-Path before use; results matched the plan. |
| 8. Path and shell formatting | Kept | Report paths use backticks; prepared PowerShell commands use separate lines. |
| 9. Stop on unexpected values/output | Kept | Sweep SHA, the timeline diff, preview count and all supplied context comparisons match. No expected values were adjusted. Earlier warning stops were resumed only after owner disposition. |
| 10. Sandbox-only test failures | Kept | Both Step 3 full runs passed with no sandbox-only failures; owner local pytest remains the release check. |
| 11. Required agent header | Kept | This report begins with the required header. |
| Existing body hashing allowed; new facts/scope code must avoid real local text | Kept | No Python source was edited during Step 3; facts use their explicit metadata allowlist. |
| Pytest cache disabled and fresh basetemp folders used | Kept | Every sandbox pytest run used `-p no:cacheprovider`; each approved basetemp was absent before its first run. |
| Never delete a folder | Kept | No folder deletion command ran; test folders are retained. |
| Allowed warnings only | Kept | The two approved Git permission warnings are ignored. LF-to-CRLF warnings are allowed only for Python/Markdown/YAML files outside the statutes folder; none occurred under statutes. |
| Approved scope and CI sequencing | Kept | Only approved rows 01-08 A-part, 10, 13, 14 preview, 19, 20 and 25 are used. No other Part B/C/owner work was added. CI adds validation and golden sweep check only; manifest verification and facts CI steps remain deferred. |
| Report bounds | Kept | The final handoff checks line count and byte size against at most 600 lines and less than 100 KB. |

## Files changed

Step 3 starts at owner commit `554adc27a971a45056beacff1a250b1204cfc88b`, branch `feat/p09-ingest`, with a clean tree.

| File | Change |
|---|---|
| `divergence/statutes/census/sweep.json` | New deterministic golden sweep; 14,406 bytes. |
| `divergence/statutes/census/D80_TIMELINE.md` | New golden metadata timeline; 8,018 bytes. |
| `.github/workflows/python-package-conda.yml` | Exactly six inserted lines: the two requested root-level command steps. |
| `logs/P09_C-A_report.md` | This metadata-only report. |

`git diff --stat` before report creation (tracked files only; the new golden files and report are untracked until the owner stages them):

```text
 .github/workflows/python-package-conda.yml | 6 ++++++
 1 file changed, 6 insertions(+)
```

Step 2's nine Python files are already in the owner's `554adc2` commit; no Python source edits are planned or made in Step 3.

The workflow inserts "Statute records validation (D78)" and "Golden lookup sweep check (D80)" immediately after "Corpus integrity hash check" and before "Prompt-injection scanner self-test". Each runs from the repository root without a directory change. Its diff contains no other changes.

## Test counts

| Run | Passed | Failed | Skipped | Notes |
|---|---:|---:|---:|---|
| Step 2 focused, sandbox | 93 | 0 | 2 | Includes the then-absent committed-golden skip. |
| Step 2 full, sandbox | 896 | 0 | 3 | No PD-15 failures. |
| Step 2 owner local, owner-reported | 897 | 0 | 2 | Also owner-reported fatal lint 0, validation 0 errors, code guard PASS. |
| Step 3 first full, sandbox | 897 | 0 | 2 | 43.45 seconds; committed-golden test runs and passes. |
| Step 3 final full, sandbox | 897 | 0 | 2 | 58.79 seconds; committed-golden test runs and passes; no PD-15 failures. |

Retained pytest folders (each was absent before its first run; none deleted):

- `divergence/statutes/_local_text/scratch/C-A-step2-focused-pytest`
- `divergence/statutes/_local_text/scratch/C-A-step2-full-pytest`
- `divergence/statutes/_local_text/scratch/C-A-step3-golden-pytest`
- `divergence/statutes/_local_text/scratch/C-A-step3-final-pytest`

The committed-golden test previously skipped because the golden files did not exist. Both now exist, the real-records golden check passes, and that test no longer skips.

## Flake8 and Python 3.10

- Supplied local whole-repository baseline: 958. The historical 740 count was CI scope.
- Step 2 broad count: initially 970, then 968 after fixing two E128 continuation-indentation findings in the new tests.
- Step 2 fatal lint: 0.
- Step 3 final fatal lint: 0, exit 0. Final broad count: 968, exit 0; unchanged from Step 2 and 10 above the local baseline of 958.
- No complexity refactor was made, as instructed.
- Step 2 and final Step 3 Python 3.10 grammar checks passed for all nine Python files; the newer-syntax pattern scan found no matches (rg exit 1 means no matches). Changed f-string expressions use no newer syntax. This is not a substitute for an owner Python 3.10 runtime run.

The nine-file scan retained exactly these findings; the two E128 findings were fixed:

| File and line at Step 2 | Finding |
|---|---|
| `divergence/statute_validate.py:146` | C901 `check_v07_status`, complexity 18 |
| `divergence/statute_validate.py:329` | C901 `validate`, complexity 12 |
| `divergence/statute_validate.py:424` | C901 `verify`, complexity 11 |
| `divergence/statute_validate.py:462` | C901 `main`, complexity 14 |

## Validation, preview, census and guard

| Check | Initial Step 3 result | Exit |
|---|---|---:|
| Golden update | Exactly two golden outputs; both previously absent. | 0 |
| Golden check | OK for both files; hashes below. | 0 |
| Default-root preview | 34 records, 0 errors, 0 warnings; 55 files, 0 missing scope files. | 0 |
| Default-root validation after CI edit | 34 records, 0 errors, 0 warnings. | 0 |
| Root census check after CI edit | OK for both golden files. | 0 |
| Facts stdout | 53 facts; all 41 direct/aggregate context checks matched. | 0 |
| Final code guard | 34 rows; PASS; SHA-256 `b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7`. | 0 |
| Final default-root validation | 34 records, 0 errors, 0 warnings. | 0 |
| Final default-root preview | 55 files, 0 missing scope files; 0 validation errors. | 0 |
| Final golden check | OK; both SHA-256 values match the table below. | 0 |
| Gate0 | 0 blocking problems, 7 existing corpus-limitation warnings; GATE 0 CLEAR. | 0 |
| Corpus hash verification, run from `divergence/` | 17 frozen hashes, 17 current files; every Tier A content hash matches; no drift. | 0 |

Both newly inserted CI commands have already passed locally from the repository root.

## Golden hashes and timeline diff

| File | SHA-256 |
|---|---|
| `divergence/statutes/census/sweep.json` | `e503aecec0efcc28fb2e37ae91e5c2444e97e5de57ee6f471c3400ec472fb051` |
| `divergence/statutes/census/D80_TIMELINE.md` | `9695d8ec9e32b433359dd0b1e3ba4f95feeda41e87e216ca1440554ae7a287d4` |

The sweep SHA equals the owner's required SHA exactly. The comparison against `divergence/statutes/census/C4_TIMELINE.md` contains exactly one changed table row and no header/title or other differences:

```diff
-| 2024-04-01 | 2025-04-01 | AMBIGUOUS | act:1961:56:v2 | corrigendum_open | LEGAL |
+| 2024-04-01 | 2025-04-01 | FOUND | act:1961:56:v2 | [] | [] |
```

Unit: `act:1961:56`. The metadata-only comparison used `git diff --no-index`; exit 1 was expected because this one row differs.

## Facts and CONTEXT cross-check

The table contains every emitted fact, sorted by key, with its emitted definition and source. A blank caveat nature is represented by the key component `unspecified`; its source CSV cell is empty. Reasons/classes have no independent numeric target in the prompt; their values are read from the sweep whose exact bytes match the required SHA.

| Key | Value | Definition | Source | Context |
|---|---|---|---|---|
| `amended_by.empty_url` | `0` | amended_by items with missing, null, empty or whitespace-only url; checks amended_by[*].url only. | `divergence/statutes/records/**/*.json` | MATCH |
| `amended_by.items` | `127` | Total amended_by array items across records. | `divergence/statutes/records/**/*.json` | MATCH |
| `bodies.empty_placeholders` | `5` | Records with body_chars == 0; null body_chars are excluded. | `divergence/statutes/records/**/*.json` | MATCH |
| `bodies.nonempty` | `26` | Records with body_chars > 0; no body files are read. | `divergence/statutes/records/**/*.json` | MATCH |
| `caveats.amended_span.substantive` | `3` | Caveat rows by source / nature: amended_span / substantive. | `divergence/statutes/census/BODY-CAVEATS.csv` | Matches context breakdown |
| `caveats.itd_diff.accidental` | `8` | Caveat rows by source / nature: itd_diff / accidental. | `divergence/statutes/census/BODY-CAVEATS.csv` | MATCH |
| `caveats.itd_diff.substantive` | `1` | Caveat rows by source / nature: itd_diff / substantive. | `divergence/statutes/census/BODY-CAVEATS.csv` | MATCH |
| `caveats.label_gap.unspecified` | `15` | Caveat rows by source / nature: label_gap / . | `divergence/statutes/census/BODY-CAVEATS.csv` | Matches context breakdown |
| `caveats.total` | `27` | Number of body caveat metadata rows. | `divergence/statutes/census/BODY-CAVEATS.csv` | MATCH |
| `corpus_checked_through` | `"2026-11-15"` | Inclusive corpus knowledge horizon from CORPUS_CHECKED_THROUGH. | `divergence/statute_schema.py:CORPUS_CHECKED_THROUGH` | MATCH |
| `corrigenda.class.substantive` | `1` | Corrigenda by class: substantive. | `divergence/statutes/CORRIGENDUM-DISPOSITION.csv` | MATCH |
| `corrigenda.class.typo` | `6` | Corrigenda by class: typo. | `divergence/statutes/CORRIGENDUM-DISPOSITION.csv` | MATCH |
| `diffs.kept.instrument.substantive` | `3` | Diff rows by status / origin / nature: kept / instrument / substantive. | `divergence/statutes/census/ITD-GAZETTE-DIFFS.csv` | MATCH |
| `diffs.kept.itd.accidental` | `8` | Diff rows by status / origin / nature: kept / itd / accidental. | `divergence/statutes/census/ITD-GAZETTE-DIFFS.csv` | MATCH |
| `diffs.kept.itd.substantive` | `1` | Diff rows by status / origin / nature: kept / itd / substantive. | `divergence/statutes/census/ITD-GAZETTE-DIFFS.csv` | MATCH |
| `diffs.removed.instrument.substantive` | `3` | Diff rows by status / origin / nature: removed / instrument / substantive. | `divergence/statutes/census/ITD-GAZETTE-DIFFS.csv` | MATCH |
| `diffs.removed.pipeline.substantive` | `2` | Diff rows by status / origin / nature: removed / pipeline / substantive. | `divergence/statutes/census/ITD-GAZETTE-DIFFS.csv` | MATCH |
| `diffs.total` | `17` | Number of ITD/Gazette diff rows. | `divergence/statutes/census/ITD-GAZETTE-DIFFS.csv` | MATCH |
| `label_gaps.rows` | `15` | Number of label-gap rows. | `divergence/statutes/census/LABEL-GAPS.csv` | MATCH |
| `manifest.file_count` | `null` | Manifest-declared file_count; null when the manifest is absent. | `divergence/statutes/STATUTE-HASHES.json` | MATCH |
| `manifest.present` | `false` | Whether `STATUTE-HASHES.json` exists. | `divergence/statutes/STATUTE-HASHES.json` | MATCH |
| `manifest.sha256` | `null` | SHA-256 of manifest bytes; null when absent. | `divergence/statutes/STATUTE-HASHES.json` | MATCH |
| `records.act.1961` | `17` | Records by Act: 1961. | `divergence/statutes/records/**/*.json` | MATCH |
| `records.act.2025` | `17` | Records by Act: 2025. | `divergence/statutes/records/**/*.json` | MATCH |
| `records.repeal_day_unsettled` | `2` | Records whose lookup_flags include repeal_day_unsettled. | `divergence/statutes/records/**/*.json` | MATCH |
| `records.status.in_force` | `20` | Records by status: in_force. | `divergence/statutes/records/**/*.json` | MATCH |
| `records.status.never_operative` | `5` | Records by status: never_operative. | `divergence/statutes/records/**/*.json` | MATCH |
| `records.status.repealed_saved` | `6` | Records by status: repealed_saved. | `divergence/statutes/records/**/*.json` | MATCH |
| `records.status.unprinted` | `3` | Records by status: unprinted. | `divergence/statutes/records/**/*.json` | MATCH |
| `records.total` | `34` | Number of record JSON files. | `divergence/statutes/records/**/*.json` | MATCH |
| `sweep.classes.corpus` | `10123` | Sweep classes count for CORPUS; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.classes.legal` | `26` | Sweep classes count for LEGAL; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.classes.no_law` | `21730` | Sweep classes count for NO_LAW; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.classes.query` | `3` | Sweep classes count for QUERY; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.queries.boundary` | `2090` | Sweep queries count for boundary; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | MATCH |
| `sweep.queries.daily` | `39456` | Sweep queries count for daily; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | MATCH |
| `sweep.queries.tax_year` | `126` | Sweep queries count for tax_year; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | MATCH |
| `sweep.queries.total` | `41672` | Sum of sweep query counts across kinds; null when `sweep.json` is absent. | `divergence/statutes/census/sweep.json` | MATCH |
| `sweep.reasons.after_repeal` | `5395` | Sweep reasons count for after_repeal; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.applicability_unclear_row` | `3` | Sweep reasons count for applicability_unclear_row; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.before_commencement` | `16335` | Sweep reasons count for before_commencement; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.before_coverage` | `3518` | Sweep reasons count for before_coverage; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.beyond_corpus_horizon` | `5590` | Sweep reasons count for beyond_corpus_horizon; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.known_text_not_in_corpus` | `597` | Sweep reasons count for known_text_not_in_corpus; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.midyear_effect` | `3` | Sweep reasons count for midyear_effect; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.overlap` | `2` | Sweep reasons count for overlap; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.repeal_day_unsettled` | `21` | Sweep reasons count for repeal_day_unsettled; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.unknown_enactment_date` | `108` | Sweep reasons count for unknown_enactment_date; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.reasons.unprinted_intermediate` | `310` | Sweep reasons count for unprinted_intermediate; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | Read from SHA-verified sweep |
| `sweep.sha256` | `"e503aecec0efcc28fb2e37ae91e5c2444e97e5de57ee6f471c3400ec472fb051"` | SHA-256 of committed `sweep.json` bytes; null when absent. | `divergence/statutes/census/sweep.json` | MATCH |
| `sweep.statuses.ambiguous` | `6632` | Sweep statuses count for AMBIGUOUS; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | MATCH |
| `sweep.statuses.found` | `9792` | Sweep statuses count for FOUND; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | MATCH |
| `sweep.statuses.no_applicable_version` | `25248` | Sweep statuses count for NO_APPLICABLE_VERSION; read from `sweep.json` without recomputation. | `divergence/statutes/census/sweep.json` | MATCH |

Additional aggregate comparisons against the supplied CONTEXT:

| Aggregate | Actual | Expected | Result |
|---|---:|---:|---|
| `aggregate.caveats.amended_span` | 3 | 3 | MATCH |
| `aggregate.caveats.itd_diff` | 9 | 9 | MATCH |
| `aggregate.caveats.label_gap` | 15 | 15 | MATCH |
| `aggregate.diffs.kept` | 12 | 12 | MATCH |
| `aggregate.diffs.removed` | 5 | 5 | MATCH |

All 41 direct and aggregate comparisons matched; no expected value or source data was changed. `amended_by.empty_url` checks `amended_by[*].url` only. The facts module reads `census/sweep.json` rather than recomputing it. No standalone facts JSON was written.

## Gate0 warnings

Gate0 exits 0 and is clear on blocking checks. Its seven warnings describe existing limitations in the unchanged frozen corpus; no remedy or corpus edit was attempted:

| File named by Gate0 | Warning metadata |
|---|---|
| `GST-CGST-50.md` | Known limitation: s.74A text not yet obtained. |
| `IT-115BBH.md` | Known limitation: 2025 Act section number unconfirmed. |
| `IT-2-47A.md` | Known limitation: 2025 Act section number unconfirmed. |
| `IT-439-8.md` | Known limitation: unofficial full-text source requires verification. |
| `IT-439-8.md` | Source type is unofficial_full_text. |
| `ITR2026-RULE-247.md` | Known limitation: referenced section 514 not held. |
| `SBI-TTBR-DATA.md` | Known limitation: rate-sheet data comes through a community archive. |

## Sandbox-only failures

None in the completed Step 2 runs or either Step 3 full run. PD-15 was anticipated but did not reproduce. Final sandbox counts are 897 passed, 0 failed and 2 skipped.

## Deviations and owner dispositions

- The initial read-only inspection stopped for Git sandbox permission warnings. The owner accepted exactly the ignore-file and pytest-cache permission warnings and supplied a clean local status.
- The owner explicitly allowed existing tools/tests to read body bytes internally for hashing/validation, while keeping body text output/copying and new facts/scope access forbidden.
- The owner moved pytest basetemps from the proposed repository-root paths to fresh folders under the local scratch tree. The Step 3 scratch names were separately printed in the plan and approved.
- Step 2 stopped for LF-to-CRLF warnings outside statutes. The owner accepted such warnings for Python/Markdown/YAML files outside statutes only; any occurrence under statutes remains a STOP.
- The owner corrected the local lint baseline from historical CI-scope 740 to local 958, authorized only trivial lint fixes, and required retaining C901 findings.
- The Step 3 first full suite had 897 passed and 2 skipped versus Step 2 sandbox 896 passed and 3 skipped because the committed-golden test now runs. This is the expected golden-file transition.
- No unapproved implementation or data changes were made.

## What was NOT done

- No real-root statute freeze and no creation of `divergence/statutes/STATUTE-HASHES.json`.
- No creation of `divergence/statutes/census/d80_facts.json`; facts were printed and incorporated in this report only.
- No edit to `divergence/statutes/census/C4_TIMELINE.md`, records, existing CSV/JSON inputs, owner data, frozen corpus, replay cache, runs, pre-registration, scorer or TEST seal.
- No manifest-verify or facts CI step; those remain Part B work.
- No body text opened, printed, quoted or copied by Codex.
- No network access, secret/environment-value disclosure or external model/API call.
- No folder deletion, staging, commit, push or tag by Codex.

