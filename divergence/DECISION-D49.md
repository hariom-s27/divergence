# D49 — generated real input documents for all six cases, mechanically, from frozen ground truth

**Date:** 21 August 2026 (started night of 20 Aug)
**Directly closes the gap D48 found. Read that first.**

## What was done, and the order it was done in

`ground_truth.json` for all six cases was frozen at commit `225ed20b`, before
any scored run, and has not been edited since — not tonight, not in this
change. What changed instead: `make_case_docs.py`, a new mechanical script,
reads each case's already-frozen `facts` block and renders a realistic input
document (`step21drop/cases/<CASE>/input.md`) containing every fact in that
block, phrased the way an actual invoice-plus-payment-confirmation packet
would phrase it — not a JSON dump, not a bullet list.

**The order matters and is the whole justification.** The answer key
(`ground_truth.json`) came first, at the freeze commit, weeks before any of
this was written. The exam paper (`input.md`) is being typed up now, to match
an answer key that already existed and cannot be edited to make this easier.
That is the correct order. The order that would corrupt pre-registration is
the reverse — writing or editing an answer key after seeing how a document
performs. This script cannot do that: it only reads `ground_truth.json` and
`case.md`; it never writes to either.

## Why a script, not a person, wrote the documents

The instruction that produced this file was explicit: *"a script generates
them, not you. If you hand-write the documents, you'll unconsciously make
them easy to read, and that's the bias the freeze exists to prevent."*
`make_case_docs.py` has no per-case branches written by hand — template
selection is a pure function of two already-frozen fields
(`bank_involved`, `asset`), applied identically to all six cases. It cannot
choose to make C3 easier than C1 because it does not know which one is being
graded harder.

## What the script guarantees, and how that was checked, not assumed

- **100% fact coverage, verified mechanically, not eyeballed.** The script
  tracks which `facts` keys it actually interpolated into the rendered text
  and prints a coverage line per case; it exits non-zero if any case is
  incomplete. Run output: all six cases, 100%, zero missing keys.
- **No invented facts.** The renderer only ever emits values pulled directly
  from `gt["facts"]` — there is no free-text field, no filler description,
  no invented company detail beyond what `ground_truth.json` already states.
- **`ground_truth.json` and `case.md` are both untouched.** Checked with
  `git status` after running the script: only six new `input.md` files and
  the generator script itself appear. Nothing under `cases/` changed.

## What this fixes and does not fix

C3 previously extracted zero fields against `case.md`, which never restated
its own amount or asset in the body text. `step21drop/cases/C3/input.md` now
states 2,000 USDC and the settlement time directly in its payment
confirmation paragraph. C1, C2, C4, C5 previously had ground truth expecting
a counterparty name and invoice number that appeared nowhere in `case.md`;
`input.md` now states both, mechanically pulled from the same frozen ground
truth that will grade them.

This does not touch M1's other named problem (D45): ground truth's own field
*names* (`asset`, `settlement_datetime_ist`, `counterparty_declared`) still
don't match what `01-extract.md` tells the model to call these fields. That
is a separate, still-open fix (Block B / Step 2) — this change makes the
facts reachable in the input; it does not yet make the extractor call them
by the right name.

## What happens to tonight's (20 Aug) runs against the old `case.md`

Not deleted, not silently replaced. `runs/{C1,C2,C3,C4,C5,D1}_pipeline.json`
and their arm A/B counterparts remain exactly as run, against `case.md`.
Once arm A/B/C are re-run against `input.md`, `results.md` will report both:
the 20-Aug numbers (run against under-specified input, most useful as the
diagnostic that led to this fix) and the new numbers (run against complete
input), not one quietly overwriting the other.

## What to say about it

> "Five of our six case files never got the standalone input document their
> own checklist required — ground truth for those cases named facts, like a
> counterparty, that existed in no document. We didn't edit the frozen
> ground truth, and we didn't hand-write the missing documents either,
> because either one risks the same bias: writing toward a result you've
> already seen. Instead a mechanical script reads the already-frozen answer
> key and generates the input document from it, with no per-case human
> discretion, verified for complete coverage automatically rather than by
> eye. The exam paper was typed up to match an answer key that came first
> and cannot move."
