# D58 — four real bugs, found doing a deliberate bug-hunting pass, not a review

**Date:** 21 August 2026
**Different in kind from D42–D57: those were mostly found reviewing docs and organization. These four were found by deliberately looking for bugs in the running code, on request, after the submission-facing work was otherwise done.**

## 1. `schema.json`: `condition_met` couldn't be null, even though it always should be when `qualifying_condition` is null

Same shape as two amendments D45/D46 already made (`qualifying_condition`
and `consequence_if_failed`, both widened to `["string", "null"]`) —
`condition_met` was simply missed at the time. Confirmed on a real record
(`D1_final_seed1.json`): every time the resolver correctly returned
`qualifying_condition: null` (no qualifying condition applies to this
regime), it also, correctly and consistently, returned `condition_met:
null` — there is no sensible non-null answer to "was the condition met"
when there was no condition. The schema was rejecting a schema-valid,
semantically correct response.

**Fixed:** `condition_met`'s enum now includes `null`. Verified the
previously-failing record validates now; verified the frozen
`D1_final_seed2.json` demo record is unaffected (still valid, unchanged).
Purely additive — can only turn a previously-invalid record valid, never
the reverse, so nothing that validated before can stop validating now.

**One consequence, handled directly, not glossed over:** this schema fix
retroactively means seed 1 of Block F's three-seed run would validate
today, and the pre-registered selection rule (first schema-valid seed)
would pick it instead of seed 2 if run fresh. **The frozen demo record does
not change.** Seed 1's content was already read and quoted in this
project's own documentation before this fix existed — re-running the
selection now would be exactly the cherry-picking the rule exists to
prevent, even though the rule was applied honestly at the time it mattered.
Full reasoning: `results.md`'s Block F.

## 2. `run_pipeline.py`'s `manifest.provisions_checked[].verified` was hardcoded `true`

Built the night before (also 21 Aug, an earlier pass) to finally populate
`schema.json`'s long-defined-but-never-written `manifest` object. Every
entry's `verified` field was set to `True` unconditionally — correct in
the narrow sense that these are real files read directly off disk, not an
unverified model claim, but skipping a real, meaningful check that was
available: whether each provision's own citation is actually **current for
the record's stated tax year**, the same check every other citation in
this pipeline goes through.

**Fixed:** `build_manifest()` now calls `citation_matcher.verify()` (the
same function that gates every resolver-produced citation) for each
provision against the record's `tax_year`, and uses the real verdict.
Verified this is a real, working check and not decorative: run against
`FY 2026-27` (correct for this project's cases), all entries return `True`;
run against the wrong year, `FY 2025-26`, five of ten income-tax provisions
correctly return `False` — the check catches a real mismatch when one
exists, not just when convenient.

## 3. The disclosure page's election radio buttons didn't record anything

`render_election()` — "if you have already decided, record it here" — had
no code behind that sentence. Ticking a box did nothing; a page reload lost
it. **Fixed:** the choice now persists in the reader's own browser
(`localStorage`, keyed to the specific record so two different receipts
opened in the same browser never collide), with a visible status line
(`aria-live="polite"`, so it's announced to a screen reader too) and an
explicit clear control — no hidden gestures. No server, no network call:
consistent with this project's own "no API for the demo" discipline (D33),
this is storage in the reader's own browser, nothing sent anywhere. Applies
automatically to every future record with a real valuation dispute; C1/C2
(single-method, no dispute) correctly render no election UI at all, since
there's nothing to elect between.

## 4. `eval/score.py`'s gap matcher was not one-to-one — a real, measured scoring bug

Found checking whether the M2 gap-recall instability documented in
`results.md` (Block E2, 50%/75%/0% across three seeds) was fully real or
partly a scoring artifact, per the same discipline this project has applied
to every other self-caught bug. Hand-verified every ground-truth-to-reported
pairing the scorer actually decided, for all three seeds, against the raw
JSON. Two of three held up exactly. The third didn't: `_similar()` checked
each ground-truth item independently, with no constraint against two
different ground-truth items claiming the *same* reported item — confirmed
on `D1-seed2_pipeline.json`, where the single reported item *"documentation
proving the foreign exchange transaction"* matched both the FIRC gap and
the official-exchange-rate gap, crediting one real finding as two and
inflating that seed's recall from a fair 50% to a credited 75%.

**Disclosed without fixing, for one night**, because changing the scorer
meant re-verifying every M2 number already published, under deadline
pressure, which is exactly what this project's hard-stop rule exists to
prevent. Fixed properly once there was room to do it right:

- `_max_bipartite_match()` — standard augmenting-path (Kuhn's algorithm)
  maximum bipartite matching between planted and reported items, using
  `_similar()` as the edge predicate. Small N (a handful of gaps per side),
  so no need for anything faster.
- `m2_gaps()` rewritten to use it — a reported item can satisfy at most one
  planted gap, and vice versa.
- **Every M2 number in `results.md` that this could have affected was
  re-scored, not assumed.** Re-ran `eval/normalize_runs.py --report`
  against both `runs/` and `runs/21aug/`, plus every individual seed and
  labelled-record file quoted anywhere in `results.md`, and diffed against
  the previously-published numbers cell by cell.

**What actually changed, and nothing else:**

| Location | Was | Now |
|---|---|---|
| Block E2 table, Arm C M2 recall, seed 2 | 75.0% | 50.0% |
| Block E2 table, Arm B M2 precision, seed 2 | 100.0% | 75.0% |
| D1 three-labelled-records table, `D1_fixed_pipeline.json` M2 recall | 75.0% | 50.0% |
| 21-Aug 18-row table, D1 arm A M2 precision | 66.7% | 33.3% |

Every other M2 cell in every table in `results.md` — the 20-Aug table, the
21-Aug table's other rows, the Block F seed-selection table, the D1-arm
headline "75.0% vs 25.0%" loss quoted in "Where we lose" — was re-checked
against the fixed scorer and confirmed **unchanged**. The instability
finding itself is not weakened by any of this; it's now measured with a
scorer that doesn't have a known bug in it, which is a stronger position
than disclosing around one.

## What to say about all four

> "Asked to specifically hunt for bugs rather than review docs, we found
> four: a schema field rejecting its own resolver's correct output, a
> manifest field that looked checked but wasn't, a UI control that recorded
> nothing despite saying it would, and a real double-counting bug in our
> own scorer that had inflated one of our own published numbers. We fixed
> all four, and for the scoring bug specifically, re-scored everything it
> could have touched rather than assuming the blast radius — one number in
> four different places in our results file, all corrected in place, all
> marked with what they used to say."
