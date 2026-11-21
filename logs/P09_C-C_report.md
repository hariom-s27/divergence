# P09 Part C-C — DECISION-D80 + decision-doc counts

Agent: Claude Code (Opus, high, ask-before-edits)
Date: 2026-11-21 · Branch `feat/p09-ingest` · Start HEAD `9b5aa8dfc5e40ac3bebe206b99909f3a498802a1` (C-B commit; CI #123 green, owner-reported)
Items: P09C-15, P09C-16, P09C-26.
This report holds metadata only: paths, counts, hashes, ids and the short quotes the task allowed. It contains no law text beyond those quotes, and no keys.

## PLAIN SUMMARY
- **What happened:**
  - Wrote `divergence/DECISION-D80.md`, the decision record for the statute corpus v1 freeze (123 lines, 15 sections).
  - Every corpus number in D80 is tagged with its `d80_facts.json` key. A checker script found 0 mismatches across 72 value tags and 5 sum tags.
  - Changed the decision-doc counts to 39 (D41–D78 and D80; D79 reserved) in `README.md`, `divergence/README.md`, `divergence/START-HERE.md` and `CLAUDE.md`, and added a D80 entry to START-HERE.
- **What it means:** The freeze now has a public record that a reader can check: the anchors (manifest sha, commit, sweep sha, facts sha, tag), what is frozen, how it is checked, and where it fails. Every number in it is tied to code output.
- **Problems:**
  - None failed.
  - The checker skips the two format examples on D80 line 9. It prints each skipped line.
  - One facts key, `manifest.present`, is not cited in D80. That is not needed.
  - The CLAUDE.md replay check was not run (see SELF-AUDIT 5).
- **Decision needed:** none. Ready for the owner's commit, then the tag `statutes-v1` on that commit.
- **Next message:** the owner reviews the diff, runs the commit lines at the end, and creates the tag.

## Files
| File | Change |
|---|---|
| `divergence/DECISION-D80.md` | new; 123 lines; sha256 `03bdf4767e844ca48d70522d2f5fff706e1538899334ddd1c4e0f905141d0e71` (before commit; CRLF/LF may change it on checkout) |
| `README.md` | 4 edits (7 lines): count/range words only |
| `divergence/README.md` | 2 edits (3 lines): count/range words only |
| `divergence/START-HERE.md` | 4 count edits + a new D80 entry (3 lines) |
| `CLAUDE.md` | 1 line: count/range words only (owner addition 4) |
| `logs/P09_C-C_report.md` | this report |
| `divergence/statutes/_local_text/scratch/C-C-tools/c3_factkeys.py` | git-ignored checker (owner addition 1); not committed |
| `divergence/statutes/_local_text/scratch/C-C-tools/D80-corrupted-selftest.md` | git-ignored copy of D80 with 2 deliberate errors, used for the negative test; not committed |

## D80 content map
| § | Section | Main sources |
|---|---|---|
| 1 | Header: date, status, authorship | C-B commit date |
| 2 | Decision and anchors | `manifest.sha256`, `manifest.file_count`, `sweep.sha256`, facts sha computed in C1 (`07b07b47…8da3`) |
| 3 | Frozen / not frozen; bodies `local_only`; backup | `bodies.*`; [REPO: P09_C-B_report.md] |
| 4 | How it is checked | workflow file; `sweep.queries.*`, `sweep.statuses.*` |
| 5 | Numbers table and definitions | 52 of 53 keys; F1 note (`amended_by.empty_url` 0 vs the amendment's 53) |
| 6 | Corpus horizon | `corpus_checked_through`; eGazette checks [owner-reported] |
| 7 | Sources and limits | ITD disclaimer (fetched 2026-11-21, owner's chat, quotes exactly as in the task); `diffs.*`; R1–R6 restated from `V3_RULES` in `statute_build.py` |
| 8 | Corrigenda rule; how D6 is amended | `corrigenda.class.*`; [REPO: P09_D_report.md L492/L494] |
| 9 | Body caveats, P10 rule, label gaps | [REPO: LABEL-GAPS.csv] (3 records, counted by code in C1) |
| 10 | Lookup notes | `records.repeal_day_unsettled`, `sweep.reasons.repeal_day_unsettled`; [REPO: P09_C-A_report.md] |
| 11 | Citation convention | rule stated in full |
| 12 | Changing the corpus | rule stated in full |
| 13 | Where it fails | CI #119/#120 [REPO: git log]; P09C-27; 4 C901 [REPO: P09_C-A_report.md] |
| 14–15 | Not tax advice; Related | — |

Owner addition 3: each private-log ID (P09D-35, P09D-39, P09C-25, P09C-26, P09C-27) appears only as a label in brackets, next to the full rule in plain words.

**How D6 is amended (D80 §8):** D6 keeps exactly two lookup flags, `repeal_day_unsettled` and `corrigendum_open`. D80 keeps both flags. It narrows only when `corrigendum_open` is set: for a corrigendum that takes effect on or after the provision's commencement. The amendment file is not edited.

## Facts-key check
Command (run from the repo root):
```
python -B divergence\statutes\_local_text\scratch\C-C-tools\c3_factkeys.py divergence\DECISION-D80.md divergence\statutes\census\d80_facts.json
```
Real output, exit 0:
```
SKIPPED format example line 9: `value [facts: <key>]
SKIPPED format example line 9: `value [sum: key + key]
facts tags: 72; sum tags: 5; skipped examples: 2; distinct keys used: 52 of 53; unused keys: ['manifest.present']; mismatches: 0
```
What the checker does:
- For each `[facts: key]` tag, it compares the token just before the tag with the facts value. Backticks and commas are stripped before comparing.
- For each `[sum: k1 + k2 …]` tag, it checks that every key exists and that the shown total equals the sum of the facts values.
- Its first run gave 2 hits. Both were the format example on line 9 (`value [facts: <key>]`). The checker now skips a token that is literally `value` and prints the skipped line.

Negative test, on a copy with `records.total` changed to 35 and the kept-diffs sum changed to 13. Exit 1, as expected:
```
MISMATCH line 59: records.total shown=35 facts=34
SUM MISMATCH line 117: shown=13 sum=12 keys=['diffs.kept.itd.accidental', 'diffs.kept.itd.substantive', 'diffs.kept.instrument.substantive']
facts tags: 72; sum tags: 5; skipped examples: 2; distinct keys used: 52 of 53; unused keys: ['manifest.present']; mismatches: 2
```

## README / START-HERE / CLAUDE.md: old → new
Only count/range words changed. Each item shows the old text, then the new text.

**README.md**
- L7–9
  - Old: "…and all 24 / dated design decisions merged into a single chronological read instead of / 24 separate files."
  - New: "…and all 39 / dated design decisions (D41–D78 and D80; D79 is reserved for the evaluation / protocol) merged into a single chronological read instead of 39 separate files."
- L512–513
  - Old: "Full list: 38 decision documents, `divergence/DECISION-D41.md` to / `DECISION-D78.md` (D41 predates the sequence)."
  - New: "Full list: 39 decision documents, `divergence/DECISION-D41.md` to / `DECISION-D78.md` and `DECISION-D80.md` (D41 predates the sequence; D79 is reserved for the evaluation protocol)."
- L516
  - Old: "…and D75–D78 are linked there by title:**"
  - New: "…and D75–D78 and D80 are linked there by title:**"
- L566
  - Old: "**38 dated decision documents (D41–D78)**"
  - New: "**39 dated decision documents (D41–D78 and D80; D79 is reserved for the evaluation protocol)**"

**divergence/README.md**
- L11–12
  - Old: "all 38 dated design decisions (D41–D78) … (D41–D74 summarised, D75–D78 linked by title)"
  - New: "all 39 dated design decisions (D41–D78 and D80; D79 is reserved for the evaluation protocol) … (D41–D74 summarised, D75–D78 and D80 linked by title)"
- L73
  - Old: "`DECISION-D41.md` … `DECISION-D78.md` | Thirty-eight dated documents, … (D41–D74 summarised, D75–D78 linked by title)"
  - New: "`DECISION-D41.md` … `DECISION-D80.md` | Thirty-nine dated documents (D41–D78 and D80; D79 is reserved for the evaluation protocol), … (D41–D74 summarised, D75–D78 and D80 linked by title)"

**divergence/START-HERE.md**
- L2
  - Old: "all 38 decision documents (D41–D78) … D75–D78 linked by title … thirty-eight separate files"
  - New: "all 39 decision documents (D41–D78 and D80; D79 is reserved for the evaluation protocol) … D75–D78 and D80 linked by title … thirty-nine separate files"
- L141
  - Old: "Thirty-eight dated documents (D41–D78)."
  - New: "Thirty-nine dated documents (D41–D78 and D80; D79 is reserved for the evaluation protocol)."
- L145
  - Old: "D75–D78 are listed by title"
  - New: "D75–D78 and D80 are listed by title"
- L769 (now L772)
  - Old: "there are now 38, D41–D78)"
  - New: "there are now 39, D41–D78 and D80; D79 is reserved for the evaluation protocol)"
- New entry after D78:
  ```
  ## [D80](DECISION-D80.md) — statute corpus v1 freeze: manifest, golden sweep, facts
  21 November 2026. Not summarised here yet; full record: [`DECISION-D80.md`](DECISION-D80.md).
  ```

**CLAUDE.md**
- L11
  - Old: "divergence/DECISION-D41.md … DECISION-D78.md (38 files)."
  - New: "divergence/DECISION-D41.md … DECISION-D80.md (39 files: D41–D78 and D80; D79 reserved)."

The count of 39 does not include `DECISION-D78-AMENDMENT-2026-11-16.md`. That matches how the old count of 38 was made.

## Checks (key unset: `[bool]$env:FEATHERLESS_API_KEY` = False)
| Command | Real output | Result |
|---|---|---|
| `python -m pytest -q -p no:cacheprovider` | `898 passed, 1 skipped in 62.51s` | PASS |
| `python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` | `0` | PASS |
| `python -m divergence.gate0_check` | `GATE 0 CLEAR on everything this script can see.`; 7 existing advisory notes; exit 0 | PASS |
| `python -m divergence.statute_validate --verify` | `statute_validate: 34 records, 0 errors, 0 warnings`; exit 0 | PASS |
| `python -m divergence.statute_facts --check divergence/statutes/census/d80_facts.json` | `statute facts: OK` | PASS |
| `python corpus_hash.py --verify` (from `divergence/`) | `[OK] Every Tier A file's content matches its frozen hash. No drift.` | PASS |
| Facts-key check | 0 mismatches (above) | PASS |
| `git status --short` | ` M CLAUDE.md`, ` M README.md`, ` M divergence/README.md`, ` M divergence/START-HERE.md`, `?? divergence/DECISION-D80.md` (this report adds `?? logs/P09_C-C_report.md`) | PASS: only the 6 approved files |

## Deviations
- **D1.** The checker skips the format example on D80 line 9. This is printed on every run, so a reader can see it.
- **D2.** `corpus_hash.py --verify` was not in the task's check list. I ran it because CLAUDE.md lists it for hand-off.
- **D3.** I wrote a negative-test copy of D80 into the approved C-C-tools folder. This was not in the plan. It is git-ignored and was not deleted.
- **D4.** At C1, a system notice said auto mode was active. CLAUDE.md forbids auto mode. No write was made before APPROVED.

## SELF-AUDIT
1. **Steps asked vs done:**
   - C1 and C2 are done.
   - All four owner additions are done: the checker is in the workspace; "fetched 2026-11-21" and the exact quotes; rules stated in full with IDs as labels; the CLAUDE.md line.
   - F1 is stated as instructed.
2. **Decisions made or changed, and why:**
   - Sum format `value [sum: k1 + k2]`, so the checker can verify totals.
   - The facts-file sha is not tagged, because a file cannot hold its own hash.
   - Two sentences in my draft could not be backed by a file, so I removed them: "the corpus keeps the Gazette reading and records these as caveats", and "filled from registered sources".
   - §10: the way the lookup applies the first-day-of-assessment-year doctrine to the 2025 Act is tagged INFERENCE.
3. **Implementation:** the files are in the table above.
   - The checker uses the regex `(\S+) \[(facts|sum): ([^\]]+)\]`.
   - Commands are listed under Checks.
4. **Checks:** all passed. Real outputs are quoted above.
5. **Frozen items:**
   - corpus_hash: OK.
   - The statute manifest verifies.
   - Facts check: OK.
   - No file under `divergence/statutes/` (in scope), `corpus/`, `replay_cache/` or `runs/`, and no DECISION file other than the new D80, was edited.
   - The CLAUDE.md field-level replay check (DIVERGENCE_REPLAY=1) was not run: it is not in this task's check list, and nothing it reads was changed.
   - The sealed test set was not touched.
6. **Assumed or not checked:**
   - The ITD disclaimer quotes: these come from the owner's chat fetch, and I did not fetch them.
   - The eGazette checks of 17 and 19 Nov, and the 21 results: owner-reported.
   - The copy-3 backup.
   - CI #123 green: owner-reported.
   - "Python 3.10 end of life 1 Oct 2026": taken from the task text.
   - The RDA recommendation: taken from the task text, with no network check.
7. **Errors and retries:** the checker's first run flagged the format example (2 hits). Fixed by printing a skip line. Second run: 0 mismatches.
8. **Safety:**
   - No commit, push or tag.
   - No network or model calls. No keys read or printed; only the bool check.
   - No deletes. No law text in outputs beyond the quotes the task allowed.
9. **git status / git diff --stat** (before this report):
   ```
    M CLAUDE.md
    M README.md
    M divergence/README.md
    M divergence/START-HERE.md
   ?? divergence/DECISION-D80.md

    CLAUDE.md                |  2 +-
    README.md                | 14 +++++++-------
    divergence/README.md     |  6 +++---
    divergence/START-HERE.md | 11 +++++++----
    4 files changed, 18 insertions(+), 15 deletions(-)
   ```
10. **Risks for the next steps:**
    - The tag `statutes-v1` must go on the commit that adds D80 (D80 §2 says so).
    - The facts sha in D80 is only correct while `d80_facts.json` is unchanged. CI's facts check enforces that.
    - The D78 amendment still says "53 empty URLs". D80 records the correction, but the old file stays as it is by rule.

## Prepared commit lines (owner runs them; the agent does not)
```
git add divergence/DECISION-D80.md
git add README.md
git add divergence/README.md
git add divergence/START-HERE.md
git add CLAUDE.md
git add logs/P09_C-C_report.md
git commit -m "P09 C-C: DECISION-D80 statute corpus v1 freeze; decision-doc counts 39 (D41-D78, D80)" -m "P09C-15/16/26. Every D80 number keyed to d80_facts.json (0 mismatches). D79 reserved for the eval protocol. Agent: Claude Code (Opus, high)."
```
