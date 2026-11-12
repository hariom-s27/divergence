# P08 report — D78 versioned statute records (schema, validator, exact lookup)

Branch: `feat/d78-corpus-schema`. Commits: Part A `0bf94e8`, Part B `b188be6`, Part C (this report + D78 evidence) pending owner commit.
Date: 13 November 2026. Public file: no keys, no personal data.

## PLAIN SUMMARY

- **WHAT HAPPENED:** We fixed the shape of a "versioned statute record" before any law text is ingested (DECISION-D78). Code now validates such records against 16 rules (V01–V16) and answers "which version applied?" with FOUND, NO_APPLICABLE_VERSION or AMBIGUOUS — never the nearest version. 10 invented FAKE records test every rule and every expected lookup. Tests: 100 before, 87 new, 187 total, all passing.
- **WHAT IT MEANS:** Version accuracy (1961 Act vs 2025 Act, retrospective amendments, mid-year changes) can now be measured by deterministic code, and the code refuses instead of guessing. The frozen hackathon corpus and its replay are untouched and still reproduce field by field.
- **PROBLEMS:** (1) No Python 3.10 on this machine (local: Python 3.14.3); CI on push is the 3.10 check. (2) In the Part B chat, a hand-trimmed fixture-hash table had typos; the fixture files themselves were correct (validator-checked). The table below is printed by a command reading the record files. (3) One command error in Part A (a missing parent folder), fixed by creating the folder and re-running the same approved step.
- **DECISION NEEDED:** none for P08. P09 (ingest of real pages) should first answer the open items in section 10.
- **NEXT MESSAGE:** `Committed Part C. Start P09 planning.`

## SELF-AUDIT

### 1. Steps done (evidence)

| Part | Step | Status | Evidence |
|---|---|---|---|
| A | branch `feat/d78-corpus-schema` | done | `git switch -c feat/d78-corpus-schema` → `Switched to a new branch` |
| A | `.gitattributes` +2, `.gitignore` +2 | done | `git check-attr eol` → `eol: lf` for `divergence/statutes/README.md` and `tests/fixtures/statutes/x.json`; `git check-ignore -v` → `.gitignore:19:divergence/statutes/_local_text/` |
| A | `statutes/README.md`, `records/.gitkeep`, `text/.gitkeep`, `schema/statute_record.schema.json` | done | commit `0bf94e8`; `Draft202012Validator.check_schema` → `schema ok 4.26.0` |
| A | `DECISION-D78.md` | done | commit `0bf94e8`; `{{…}}` filled in Part C |
| A | CLAUDE.md report line (PD-03) + counts 37→38 / D77→D78 | done | Select-String for the old count strings → no hits; gate0 → `GATE 0 CLEAR` |
| B | `statute_schema.py`, `statute_lookup.py`, `statute_validate.py` | done | commit `b188be6` |
| B | 10 FAKE fixtures + 9 bodies | done | `python -m divergence.statute_validate --root tests/fixtures/statutes --allow-fixtures` → `statute_validate: 10 records, 0 errors, 1 warnings`, exit 0 |
| B | tests | done | `187 passed`; new files `87 passed` (schema 24, lookup 30, validate 33) |
| B | default root | done | `python -m divergence.statute_validate` → `statute_validate: 0 records, 0 errors, 0 warnings`, exit 0 |
| B | flake8 on new files (`--max-line-length=127`) | done | no output, exit 0 |
| C | phase gate | done | section 6 |
| C | D78 `{{…}}` filled | done | date, commit `b188be6`, 87 / 187, 10 fixtures |
| C | this report | done | this file |

### 2. Decisions

**Owner-approved changes, by plan:**

- Part A plan:
  - Q1 (a): add a 2-line D78 entry in `START-HERE.md` after the D77 entry, so "D75–D78 linked by title" stays true.
  - Q2: keep every word of D78; restore title, Date and Status lines, `##` headings and `-` bullets; three clocks as a numbered list 1–3; the s.52(1)(q) (i)/(ii) quotes as `>` blockquotes, word for word.
  - Q3: `record_id` regex `^(act|rule|notification|circular):(1961|2025):[A-Za-z0-9.\-]+:v[1-9][0-9]*$`.
  - Q4: range-end-only changes on the extra count lines (README.md:513/516, divergence/README.md:12/73, DOCUMENTATION.md:454/469, START-HERE.md:145).
- Part B plan:
  - D5 step-2 clarification: records with `enacted_on` > `as_known_on` dropped; null `enacted_on` kept and marked.
  - Q1 (b): `unknown_enactment_date` is added only if a marked record is still a candidate after supersession.
  - Q2: a null start date never covers the query point (no −∞).
  - Q3: `--freeze` refuses on any ERROR (WARNs do not block); manifest findings use check-id `FREEZE`.
  - Four added tests: `test_f3_never_operative_with_as_known_on`, `test_unknown_enactment_on_superseded_version_does_not_block`, `test_outstanding_effect_without_date_is_ambiguous`, and the "Z" rejection test (`test_v01_retrieved_at_z_rejected`; also `test_retrieved_at_z_suffix_rejected` at schema level).
  - `retrieved_at` needs a numeric offset (`+HH:MM` / `-HH:MM`); the schema regex rejects `Z` (one-line edit to the Part A schema file).
  - Fixture F8 `text_current_as_of` = 2026-09-01; no validator rule for its order against `outstanding_effects` (see section 10).
  - Subprocess tests use `sys.executable` with cwd = repo root; writing inside pytest's `tmp_path` allowed for tests only.
- Part C plan:
  - Q1 (a): keep the git-ignored replay output `divergence/cache/p08_replay_check.json`.
  - Fixture hash table printed by a command reading the record files; D78 `{{commit}}` = `b188be6`.

**Decisions I made that the prompt did not specify:**

- Schema: dates and `retrieved_at` carry a regex `pattern` as well as `format`, because jsonschema 4.26.0 here has a `date` format checker but no `date-time` checker. Alternative: `format` only (would not be enforced).
- Schema: `heading`, `source_acknowledgement`, `original_note` require a non-space character (`\S`).
- F2 (local_only, body deliberately absent): the required `body_sha256` / `body_chars` are of a notional body text, stated in its `notes`. Alternative: make them optional for local_only (would change D3).
- Fake `enacted_on` dates D7 left open: F1, F5 v1, F8 2025-08-01; F2 2010-03-01; F5 v2 2026-08-01; F6 2026-02-01; F7 2026-05-15; F3 null (to exercise the step-2 clarification).
- Validator: cross-field checks read fields defensively, so V12/V13/V15 still report when V01 also fails; an unexpected exception inside a check is reported as `ERROR … could not evaluate`, never skipped.
- V14 runs git only when a local_only record exists; a non-git root or missing git gives `WARN (root): V14 not_a_git_repo`.
- Extra test `test_freeze_refused_on_error` (covers Part B Q3).
- Replay `--out` inside the repo but outside `runs/`, in the existing git-ignored `divergence/cache/` (the standing rule forbids writing outside the repo).

### 3. Deviations from the prompt

- The approved D78 text was pasted without line breaks; structure restored as approved (Part A Q2). Wording unchanged.
- The Part A schema file was edited once in Part B (`Z` removed from the `retrieved_at` pattern), on the owner's instruction.
- `git ls-files --eol` for new files could only run after the owner's commits; in Parts A/B a byte scan for CR/BOM was used instead (section 8).
- The fixture-table command was run as a Bash heredoc on stdin (`python - <<'EOF' … EOF`) instead of the planned `python -c "…"`, because Windows PowerShell 5.1 breaks embedded double quotes passed to native programs. Same logic; the full code is shown in section 4.

### 4. Numbers (each with its source)

| Number | Value | Source |
|---|---|---|
| tests before | 100 | `python -m pytest -q -p no:cacheprovider` at `0bf94e8` → `100 passed in 15.95s` |
| tests new | 87 | pytest on the 3 new files → `87 passed in 4.06s` |
| tests total | 187 | phase gate pytest → `187 passed in 20.01s` |
| fixtures | 10 records, 9 bodies | validator → `10 records`; freeze test asserts `file_count == 19` |
| validator checks | 16 (V01–V16) | `divergence/statute_validate.py` |
| replay facts / missing / attacked | 13 / 3 / 4 items, all equal | replay compare (section 6) |
| local Python | `Python 3.14.3` | `python --version` |
| jsonschema | 4.26.0 | `divergence/requirements.txt`; `check_schema` output |

**Fixture bodies** — printed by this command, which reads the record files (not typed by hand):

```
python - <<'EOF'
import json, pathlib
rows = sorted((json.loads(p.read_bytes().decode('utf-8'))
               for p in pathlib.Path('tests/fixtures/statutes/records').rglob('*.json')),
              key=lambda r: r['record_id'])
t = '| record_id | body_sha256 | body_chars |\n|---|---|---|\n' + ''.join(
    f"| {r['record_id']} | {r['body_sha256']} | {r['body_chars']} |\n" for r in rows)
MARK = '<!--' + 'FIXTURE_TABLE-->'
p = pathlib.Path('logs/P08_report.md')
s = p.read_bytes().decode('utf-8')
assert s.count(MARK) == 1
p.write_bytes(s.replace(MARK, t.rstrip('\n')).encode('utf-8'))
EOF
```

| record_id | body_sha256 | body_chars |
|---|---|---|
| act:1961:sFAKE2:v1 | bd77c906b38dd0381369aac39c9bb2a9c54fa678341d0e699b29c7c0074fedd1 | 82 |
| act:1961:sFAKE3:v1 | 99edf388deb1cdb732e427bdbe3ac7ed4e255f4bdcc1bb3db96e62686e0ac6e6 | 100 |
| act:1961:sFAKE4:v1 | ed70d5c674f534feb7e0de9044fede20664a416ed98ad788ef85ae2166b54434 | 82 |
| act:1961:sFAKE4:v2 | 30dcd51ed29d13cf61eef3abf29499fe1ab7ff88c48dd8ca6094cac08eac0b6e | 118 |
| act:2025:sFAKE1:v1 | 9dec37d9320caf226e370bb72ee4a4408d243d19539b2dea293e8d6223120328 | 93 |
| act:2025:sFAKE5:v1 | cf8aedb683e4a831bf3791ec75092fa91c441e6b33e11e0c5f0ae7e090fef4d1 | 82 |
| act:2025:sFAKE5:v2 | 1aedecdf1df3d85f2e94cda42867f119ab25d4274883275aed4f92d8ac7c1f24 | 98 |
| act:2025:sFAKE6:v1 | 3e03af3007b060859aef5cd764c6cdc8a82feb2de0c0fc0ec5506e420dc77039 | 100 |
| act:2025:sFAKE8:v1 | b69175826469f3f192d9ef65a2d194c08ba1337137fe61502396f0f9b0b36972 | 97 |
| circular:2025:FAKE-CIRC-1:v1 | 14cc75b6e32cafb3cd840464553a0d5dd7068e2873613a8a773accc5cee84e59 | 93 |

`body_sha256` = SHA-256 of the body's UTF-8 bytes; `body_chars` = Unicode code points. `act:2025:sFAKE5:v2` has 98 code points in 100 bytes (it contains "—"). `act:1961:sFAKE2:v1` is local_only and its body is deliberately absent (WARN `body_absent_local`).

### 5. Tests

Before 100, new 87, total 187, failures 0, skipped 0. New files: `tests/test_statute_schema.py` (24), `tests/test_statute_lookup.py` (30, one per D7 expectation plus edge cases), `tests/test_statute_validate.py` (33, one or more per V01–V16, plus freeze/verify and usage errors). No D7 expectation contradicted D5; no expectation or rule was changed to make a test pass.

### 6. Frozen items and phase gate (API keys unset)

| Check | Output | Result |
|---|---|---|
| `git diff --stat 4231691 -- divergence/corpus divergence/replay_cache divergence/runs` | (empty) | pass |
| `cd divergence; python corpus_hash.py --verify` | `[OK]  Every Tier A file's content matches its frozen hash. No drift.` | pass |
| `cd divergence; python gate0_check.py` | `GATE 0 CLEAR on everything this script can see.` | pass |
| `python -m pytest -q -p no:cacheprovider` | `187 passed in 20.01s` | pass |
| `python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` | `0` | pass |
| replay: `DIVERGENCE_REPLAY=1`, keys unset (`False False False`), CI command with `--out cache/p08_replay_check.json`, compared to `runs/21aug/D1_final_seed2.json` and `D1_final_seed2_attack.json` | `facts equal: True 13` · `missing equal: True 3` · `attacked equal: True 4` · `provider: replay replayed: True all by_node replayed: True` | pass (field-level) |
| `git status --short -- divergence/replay_cache divergence/runs divergence/corpus` after replay | (empty) | pass |

Replay mode only reads the cache (`replay_cache.load`; a miss raises), so nothing was written to the frozen cache.

### 7. Errors and retries; TEST seal

**Errors and retries:**

- Part A: `New-Item` on `divergence/statutes/records/.gitkeep` failed (`Could not find a part of the path`) because the `records` folder did not exist yet. Fixed by creating the folder and re-running the same approved step once.
- Part B: none. One check command was moved to the background mid-run; it finished with exit 0 and its output was read.
- Part B chat (not a file): a hand-trimmed fixture-hash table had typos. The fixture files were correct (validator-checked); section 4's table is printed by a command.
- Part C: the first fixture-table insert stopped on its own check (`AssertionError` at the `assert s.count(<marker>) == 1` line, exit 1; the marker is the HTML comment `FIXTURE_TABLE`). Cause: the report shows the insert code, and that code contained the marker literal, so the marker appeared 3 times instead of once. Nothing was written. Reported to the owner; fixed (owner-approved) by splitting the literal (`MARK = '<!--' + 'FIXTURE_TABLE-->'`), so only the real placeholder matches. Re-run once.

**TEST seal:** no sealed test set exists yet. None was created, opened or inspected in P08.

### 8. Safety

- No commit, push, merge or rebase by the agent; the owner committed Parts A and B.
- No API key read, printed or written. Keys were checked only as booleans; for the replay they were cleared inside that one child shell.
- No personal data in the new files. No absolute paths outside the repo in this report.
- `git add` commands given to the owner list explicit paths only; never `git add -A` / `git add .`; `divergence/submission/thesis-4pager.html`, `.pdf` and `final_sub/` never staged.
- No `divergence/statutes/STATUTE-HASHES.json` and no `divergence/statutes/_local_text/` created; `--freeze` ran only inside pytest `tmp_path`.
- `git init` ran only inside pytest `tmp_path` (V14 test).
- LF verified: `git ls-files --eol divergence/statutes tests/fixtures/statutes` → every file `i/lf w/lf attr/text eol=lf` (the two empty `.gitkeep` files show `i/none w/none`).
- Python 3.10: local `python --version` → `Python 3.14.3`; no Python 3.10 run happened locally. CI on push (Python 3.10) is the 3.10 check. Code avoids 3.11+ syntax and APIs (`from __future__ import annotations`; no `match`, `datetime.UTC`, `except*`).

### 9. Paid / external calls

0 network, 0 model calls, ₹0 this phase. Running total: unchanged from Week A (₹ not recorded, PR-15).

### 10. Risks and open items for P09 (ingest)

- `text_current_as_of` vs `outstanding_effects`: an effect dated before `text_current_as_of` probably means the stored text is stale or the effect is already applied. No validator rule yet (owner decision); decide when real pages show how often it happens.
- `omitted` records with a null `in_force_from` never cover an `as_of` point (Part B Q2). Real omitted sections may lack a known start date; ingest must record one or accept NO_APPLICABLE_VERSION.
- `as_known_on` is only as good as the `enacted_on` dates recorded at ingest; null dates make lookups AMBIGUOUS (`unknown_enactment_date`) unless superseded.
- Mid-year changes make tax-year lookups AMBIGUOUS by design. If many real sections change mid-year, tax-year questions in the benchmark will mostly abstain; measure this on the first ingest.
- Consolidated "as amended" pages give one text per date of consolidation, not one per amendment. Mapping them to versions with `amended_by` and `supersedes` needs a rule per page; `source_amended_up_to` is stored verbatim for that.
- `counterpart` (1961 ↔ 2025) marked SECONDARY is a lead, not a fact, until the official CBDT table is ingested.
- The `unit` regex `[A-Za-z0-9.\-]+` may not fit every real token (e.g. sub-sections with brackets); check on real section labels before ingest.
- The public form of verbatim Act text waits for the legal check in D78 (s.52(1)(q)(ii), ITD Copyright Policy and Disclaimer).
- No local Python 3.10 run: a 3.10-only failure would first show in CI.
