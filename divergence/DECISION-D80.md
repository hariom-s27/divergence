# D80 — Statute corpus v1 freeze

Date: 21 November 2026 (freeze commit `9b5aa8d`)

Status: Accepted — soft freeze (hard at the TEST seal).

Owner decisions, informed by model proposals; code by OpenAI Codex (P09 Part D, C-A) and Claude Code (C-B, C-C) under plan gates.

How numbers are written here. Every corpus count comes from `divergence/statutes/census/d80_facts.json` and is written `value [facts: <key>]`; the key's definition is stored in that file. A total built from several keys is written `value [sum: key + key]`. A script checks every tagged value and every sum against the facts file (P09 C-C report). Numbers that are not in the facts file carry their source: `[REPO: <file>]` (a committed file) or `[owner-reported]`. Labels such as `(P09C-26)` name entries in the owner's private project log; each rule is stated in full here, so the log is not needed to read this file.

## Decision

Statute corpus v1 is exactly the files listed in `divergence/statutes/STATUTE-HASHES.json`. It is identified by these anchors:

| Anchor | Value |
|---|---|
| Manifest sha256 | `5b163396f1d98e0c5e4b08c4cf2cdc89adf879603a6edb60922f906db7fe6033` [facts: manifest.sha256] |
| Manifest file count | 55 [facts: manifest.file_count] |
| Freeze commit | `9b5aa8dfc5e40ac3bebe206b99909f3a498802a1` (21 November 2026) |
| Golden sweep `census/sweep.json` sha256 | `e503aecec0efcc28fb2e37ae91e5c2444e97e5de57ee6f471c3400ec472fb051` [facts: sweep.sha256] |
| Facts file `census/d80_facts.json` sha256 | `07b07b47f3f369a526d6bce116cd8e4c882d6a5faf59d66524ce803d88968da3` (computed in P09 C-C; a file cannot hold its own hash, so this is not a facts key) |
| Git tag | `statutes-v1`, created by the owner on the commit that adds this file |

## What is frozen and what is not

Frozen (in the manifest): the record metadata files (`records/`), `VERSION-DATES`, `AMENDMENT-EFFECTS`, `SOURCES`, `MAPPING`, `SECTION-LIST`, the record schema, the owner CSVs, `CORRIGENDUM-DISPOSITION.csv`, `census/sweep.json`, `census/ITD-GAZETTE-DIFFS.csv`, `census/LABEL-GAPS.csv` and `census/BODY-CAVEATS.csv`.

Not in the manifest, and why:

- `README` files: prose that explains the corpus; editing it does not change any record.
- Timelines (`C4_TIMELINE.md`, `D80_TIMELINE.md`): generated views. `D80_TIMELINE.md` is still checked by the golden sweep check below.
- `census/d80_facts.json`: computed from the frozen files; it has its own CI check and its hash is recorded above.
- The manifest itself: it cannot list its own hash.

Bodies (the law text) are `local_only`: 26 [facts: bodies.nonempty] bodies with text and 5 [facts: bodies.empty_placeholders] empty placeholders. They live in a git-ignored folder. Whether a public reproduction is allowed by the Copyright Act, 1957, s.52(1)(q)(ii) is untested (risk R02, see D78). So bodies are not published. Each record stores the body's hash (`body_sha256`), and the bodies are backed up privately: 3 copies [REPO: logs/P09_C-B_report.md] (laptop; Google Drive account A, hash matches; Google Drive account B, web upload, owner-reported, no hash). A restore test from the backup passed: 65/65 files matched their sha256 and the body guard rebuilt the same 26 bodies [REPO: logs/P09_C-B_report.md].

## How it is checked

CI (`.github/workflows/python-package-conda.yml`), on every push:

- corpus hash check of the frozen hackathon corpus (`corpus_hash.py --verify`);
- `python -m divergence.statute_validate` (record rules V01–V16, see D78);
- `python -m divergence.statute_census --check` (golden sweep: recomputes every lookup and compares with `sweep.json` and `D80_TIMELINE.md`);
- `python -m divergence.statute_validate --verify` (every manifest file still has its recorded sha256);
- `python -m divergence.statute_facts --check divergence/statutes/census/d80_facts.json` (the facts file equals a fresh computation).

Local only: `python -m divergence.statute_guard --body` (rebuilds the bodies from the raw PDFs and compares their hashes) and `python -m divergence.statute_caveats --check` (checks caveat spans against the stored bodies). Both need the git-ignored bodies and raw PDFs, which are not in the public repo, so they cannot run in CI.

Determinism: the 55 scope files were copied to a fresh folder and frozen again; the second manifest was byte-identical to the first [REPO: logs/P09_C-B_report.md].

Golden sweep size: 41672 [facts: sweep.queries.total] lookups = 39456 [facts: sweep.queries.daily] daily + 126 [facts: sweep.queries.tax_year] tax-year + 2090 [facts: sweep.queries.boundary] boundary queries. Check: 41672 [sum: sweep.queries.daily + sweep.queries.tax_year + sweep.queries.boundary]. Statuses: 9792 [facts: sweep.statuses.found] FOUND, 6632 [facts: sweep.statuses.ambiguous] AMBIGUOUS, 25248 [facts: sweep.statuses.no_applicable_version] NO_APPLICABLE_VERSION.

Backup fixity (the backup copies still match their sha256) is re-checked at Part E and again at the TEST seal.

## Numbers

| Group | Item | Value |
|---|---|---|
| Records | total | 34 [facts: records.total] |
| | Income-tax Act, 1961 | 17 [facts: records.act.1961] |
| | Income-tax Act, 2025 | 17 [facts: records.act.2025] |
| | status `in_force` | 20 [facts: records.status.in_force] |
| | status `repealed_saved` | 6 [facts: records.status.repealed_saved] |
| | status `never_operative` | 5 [facts: records.status.never_operative] |
| | status `unprinted` | 3 [facts: records.status.unprinted] |
| Bodies | with text | 26 [facts: bodies.nonempty] |
| | empty placeholders | 5 [facts: bodies.empty_placeholders] |
| Corrigenda | typo | 6 [facts: corrigenda.class.typo] |
| | substantive | 1 [facts: corrigenda.class.substantive] |
| | total | 7 [sum: corrigenda.class.typo + corrigenda.class.substantive] |
| ITD vs Gazette diffs | kept, origin ITD, accidental | 8 [facts: diffs.kept.itd.accidental] |
| | kept, origin ITD, substantive | 1 [facts: diffs.kept.itd.substantive] |
| | kept, origin instrument, substantive | 3 [facts: diffs.kept.instrument.substantive] |
| | removed, origin instrument, substantive | 3 [facts: diffs.removed.instrument.substantive] |
| | removed, origin pipeline, substantive | 2 [facts: diffs.removed.pipeline.substantive] |
| | total | 17 [facts: diffs.total] |
| Body caveats | itd_diff, accidental | 8 [facts: caveats.itd_diff.accidental] |
| | itd_diff, substantive | 1 [facts: caveats.itd_diff.substantive] |
| | amended_span, substantive | 3 [facts: caveats.amended_span.substantive] |
| | label_gap, unspecified | 15 [facts: caveats.label_gap.unspecified] |
| | total | 27 [facts: caveats.total] |
| Label gaps | rows | 15 [facts: label_gaps.rows] |
| Repeal-day flags | records with `repeal_day_unsettled` | 2 [facts: records.repeal_day_unsettled] |
| amended_by | items | 127 [facts: amended_by.items] |
| | items with empty URL | 0 [facts: amended_by.empty_url] |
| Sweep queries | daily / tax_year / boundary / total | 39456 [facts: sweep.queries.daily] / 126 [facts: sweep.queries.tax_year] / 2090 [facts: sweep.queries.boundary] / 41672 [facts: sweep.queries.total] |
| Sweep statuses | FOUND / AMBIGUOUS / NO_APPLICABLE_VERSION | 9792 [facts: sweep.statuses.found] / 6632 [facts: sweep.statuses.ambiguous] / 25248 [facts: sweep.statuses.no_applicable_version] |
| Sweep reasons | before_commencement | 16335 [facts: sweep.reasons.before_commencement] |
| | beyond_corpus_horizon | 5590 [facts: sweep.reasons.beyond_corpus_horizon] |
| | after_repeal | 5395 [facts: sweep.reasons.after_repeal] |
| | before_coverage | 3518 [facts: sweep.reasons.before_coverage] |
| | known_text_not_in_corpus | 597 [facts: sweep.reasons.known_text_not_in_corpus] |
| | unprinted_intermediate | 310 [facts: sweep.reasons.unprinted_intermediate] |
| | unknown_enactment_date | 108 [facts: sweep.reasons.unknown_enactment_date] |
| | repeal_day_unsettled | 21 [facts: sweep.reasons.repeal_day_unsettled] |
| | applicability_unclear_row | 3 [facts: sweep.reasons.applicability_unclear_row] |
| | midyear_effect | 3 [facts: sweep.reasons.midyear_effect] |
| | overlap | 2 [facts: sweep.reasons.overlap] |
| Sweep reason classes | NO_LAW / CORPUS / LEGAL / QUERY | 21730 [facts: sweep.classes.no_law] / 10123 [facts: sweep.classes.corpus] / 26 [facts: sweep.classes.legal] / 3 [facts: sweep.classes.query] |
| Corpus horizon | `CORPUS_CHECKED_THROUGH` | 2026-11-15 [facts: corpus_checked_through] |

Definitions. Reason and class counts count reasons, not lookups: one AMBIGUOUS lookup can carry several reasons, so they do not add up to the status counts. `label_gap.unspecified` means label-gap caveat rows; label-gap caveats carry no substantive/accidental nature, so the nature cell is empty and the facts key uses the word `unspecified`. The amendment to D78 (16 November 2026, item D7) reported 53 empty `amended_by` URLs; those URLs were filled in P09 Part D, so the frozen value is 0 [facts: amended_by.empty_url] [REPO: logs/P09_D_report.md]. The amendment file is not edited.

## Corpus horizon

`CORPUS_CHECKED_THROUGH` is 2026-11-15 [facts: corpus_checked_through]. A lookup for a date after it returns AMBIGUOUS with `beyond_corpus_horizon`; the code does not claim to know law made after the last check.

- Owner eGazette check, 17 November 2026 [owner-reported]: Ministry of Law search for 18 August to 17 November 2026, 21 [owner-reported] results read; Acts search, latest Act 17 August 2026. No new Income-tax, Finance or Taxation Act or Ordinance was found. Limit: this was a search by title, not a full-text search.
- Tool-assisted search, 19 November 2026 [owner-reported]: recorded with evidence class `tool_assisted` (weaker than an owner read of the official site).

## Sources and their limits

The consolidated Acts used for the bodies are the Income Tax Department (ITD) PDFs. They are a reproduction, not the Gazette. ITD's own disclaimer (https://www.incometaxindia.gov.in/disclaimer, fetched 2026-11-21, LEGAL-PRIMARY) says its contents "do not purport to be legal documents", that the Department "does not warrant the accuracy or completeness of the information", and that in case of variance with the Act or Rules "the latter shall prevail". Commercial use needs the Department's written permission. Wherever ITD and the Gazette differ, the Gazette is the authority.

ITD-vs-Gazette audit (`census/ITD-GAZETTE-DIFFS.csv`):

- Kept: 12 [sum: diffs.kept.itd.accidental + diffs.kept.itd.substantive + diffs.kept.instrument.substantive]. Of these, 8 [facts: diffs.kept.itd.accidental] are accidental ITD differences; 1 [facts: diffs.kept.itd.substantive] is a substantive ITD difference (a formula row; the Gazette's image of that formula was not checked); 3 [facts: diffs.kept.instrument.substantive] are amended-span leftovers, where the text was changed by an amending instrument.
- Removed: 5 [sum: diffs.removed.instrument.substantive + diffs.removed.pipeline.substantive] = 3 [facts: diffs.removed.instrument.substantive] explained by an amending instrument + 2 [facts: diffs.removed.pipeline.substantive] caused by our own extraction pipeline.

The comparison rules R1–R6 were fixed in code before the comparison ran (`V3_RULES` in `divergence/statute_build.py`). In plain words: R1 removes headings that ITD adds in the margin, but only when they form a complete sentence; R2 applies an amendment only if it was enacted by the knowledge date and takes effect by the next 1 April; R3 applies an amendment only if its target and anchor word are unique; R4 removes table column-header rows and page-break furniture; R5 ignores ITD's square brackets, omission markers and inline "(N of YYYY)" references; R6 records image evidence for text missing from the Gazette text layer and never removes a row. Known limit: R1 cannot remove a margin heading that falls in the middle of a sentence.

Defects on the Gazette side that ITD fixed silently were also found: the IFSCA Act title spelled "Centers", and a missing list label "(a)" in s.393. They are listed here so a reader knows the Gazette text has defects of its own.

## Corrigenda rule

Rule (P09D-35): a corrigendum that takes effect before the provision commences raises no `corrigendum_open` flag, because the provision never applied in its uncorrected form. All 7 [sum: corrigenda.class.typo + corrigenda.class.substantive] corrigenda in `CORRIGENDUM-DISPOSITION.csv` are of this kind: 6 [facts: corrigenda.class.typo] typos and 1 [facts: corrigenda.class.substantive] substantive item. The substantive item is `corr_ita2025:p491l33`: s.536(2)(c) of the 2025 Act, "on after" corrected to "on or after", Gazette corrigenda of 30 January 2026.

How this amends the D78 amendment (16 November 2026), item D6. D6 keeps exactly two lookup flags, `repeal_day_unsettled` and `corrigendum_open`. D80 keeps both flags but narrows when `corrigendum_open` is set: only for a corrigendum that takes effect on or after the provision's commencement. With the frozen disposition, no record carries `corrigendum_open`; in the Part D sweep the flag's count went from 411 to 0 [REPO: logs/P09_D_report.md]. The D78 amendment file is not edited.

## Body caveats and the P10 rule

`census/BODY-CAVEATS.csv` marks spans of the stored bodies that are not reliable Gazette wording: ITD differences, amended spans and label gaps (counts in the table above).

Rule for P10 (P09D-39): no gold answer span may cross a caveat span, unless the question quotes the Gazette wording itself. Where text is absent rather than different, the caveat is a point (zero-width) caveat at that position.

Label gaps: 3 [REPO: divergence/statutes/census/LABEL-GAPS.csv] versions have bodies without clause labels: 1961 Act s.2 version 1, s.56 version 1 and s.56 version 2. The labels are not printed in those PDFs and cannot be recovered from them.

## Lookup notes

- Repeal day: 2 [facts: records.repeal_day_unsettled] records carry `repeal_day_unsettled` for 1 April 2026, the day the 1961 Act was repealed and the 2025 Act commenced. Lookups on that day are AMBIGUOUS (21 [facts: sweep.reasons.repeal_day_unsettled] sweep reasons), because which Act governs that single day is not settled.
- Charging rules: rows with `basis_category` = `charging_ay_rule` follow the doctrine that the law in force on the first day of the assessment year governs the charge, so a change inside the year does not add `midyear_effect` for them. For the 2025 Act the tax year takes the place of the assessment year (applicability starts with tax year 2026-27, D78). INFERENCE: this is how the lookup applies the doctrine, not a court ruling on the 2025 Act.
- "As known on": a lookup can ask for the law as it was known on a date; amendments enacted after that date are hidden (D78 and its amendment, step 4 of the lookup order).
- One timeline row changed between the C4 timeline and the D80 timeline [REPO: logs/P09_C-A_report.md]: 1961 Act s.56 version 2, 2024-04-01 to 2025-04-01, from AMBIGUOUS / `corrigendum_open` to FOUND. The cause is the Part D corrigendum disposition above (that corrigendum took effect before commencement).

## Citation convention

Rule (P09C-26): a lookup result is cited as `statutes-v1` + manifest sha256 + `record_id` + `as_of` + `as_known_on` (+ status and reason when not FOUND). This follows the RDA Data Citation recommendation: cite a timestamped query over versioned data, plus a checksum. P10 gold answers use this form; P10 may amend it by a new decision.

## Changing the corpus

Soft freeze now; hard freeze at the TEST seal. Any change after this file needs a dated amendment file, a new manifest (`STATUTE-HASHES-v2`) and a new tag `statutes-v2`. Rule (P09C-25): the golden files (`sweep.json`, `D80_TIMELINE.md`) change only through `python -m divergence.statute_census --update`, run under a named decision. Old tags are never moved.

## Where it fails / what broke

- ITD text differs from the Gazette in places (see Sources); bodies come from ITD.
- Label gaps: 3 [REPO: divergence/statutes/census/LABEL-GAPS.csv] versions have no clause labels.
- R1 cannot remove margin headings that fall mid-sentence.
- The substantive formula row was not checked against the Gazette image.
- The horizon check is title-only, not full text.
- Bodies are not public, because the copyright question (R02) is untested.
- During Part D, CI run #119 failed on an f-string that only Python 3.12 accepts, and CI run #120 failed because a test depended on a git-ignored folder; both were fixed [REPO: git log `424047e`, `98789f6`].
- CI runs Python 3.10, which reached end of life on 1 October 2026, and older GitHub Action versions (`actions/setup-python@v3`). Rule (P09C-27): kept through P09 and decided at the start of P10.
- 4 [REPO: logs/P09_C-A_report.md] C901 complexity warnings remain in `divergence/statute_validate.py`.

## Not tax advice

This corpus and its lookups are research data for a benchmark, not tax advice.

## Related

- D78 — versioned statute records: schema, validator and exact version lookup.
- D78 amendment, 16 November 2026 — dates, projection and exact lookup v2 (item D6 narrowed above).
- D79 — reserved for the evaluation protocol, to be written in P10. That is why D80 exists before D79.
