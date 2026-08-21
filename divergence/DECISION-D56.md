# D56 — two ground_truth.json trees existed; the real one was never the one being checked against in prose

**Date:** 21 August 2026
**Found doing a GitHub organization pass — checking for confusingly duplicate filenames across the repo, the same class of thing D44's cleanup addressed. This one was hiding in plain sight.**

## The fact, stated plainly

Two complete sets of `ground_truth.json` exist for all six cases:
`divergence/cases/<CASE>/ground_truth.json` and
`divergence/step21drop/cases/<CASE>/ground_truth.json`. Checked directly,
not assumed: `git log --follow` on each path shows the real, quoted
freeze commit (`225ed20b6e697012d25d6063560907d96424a0de`) updated all six
files under `divergence/cases/` — and touched **nothing** under
`step21drop/`. `step21drop/cases/*/ground_truth.json` was last written at
the earlier, rejected pre-freeze commit (`a267f19`, the one D44 explicitly
decided *not* to treat as the freeze because the ground truth in it was
incomplete) and simply never updated again.

**`eval/score.py` has always read from the correct location.**
`CASES = os.path.join(ROOT, "cases")` resolves to `divergence/cases/`, not
`step21drop/cases/`. Confirmed by reading the constant directly, not
inferred. Every M1–M5 score in `results.md`, for every case, every arm,
every run tonight, was scored against the real, frozen ground truth. This
is not a scoring bug.

**What actually diverged between the two trees, checked field by field,
all six cases:** only `citations_expected[]` (and its accompanying
`_citations_note`/`_citations_status`/`_citations_reasoning` comment
fields). `facts`, `missing[]`, `elements`, and `methods_expected` are
byte-identical in every case, confirmed with `diff` field-name-by-field-name,
not eyeballed. Nothing that any of the five metrics reads was ever
affected.

## What this actually cost — a claim written into results.md was wrong

Block F of `results.md` (written earlier tonight, during the D1 fix cycle)
says: *"Checked directly against `step21drop/cases/D1/ground_truth.json`
before writing any claim about it into this file: `citations_expected` is
`[]` — empty, never filled in."* That check used the wrong path. The real,
frozen file — `divergence/cases/D1/ground_truth.json` — has a filled
`citations_expected[]`: Section 2(47A), Section 115BBH, Rule 56, Rule 57,
Section 393(1) Table Sl. No. 8(vi), Section 439(8), Section 2(6) IGST,
FEMA section 3.

**The instruction that originally prompted that Block F claim — the one I
called out as making a false claim about the project — was actually
right.** It said D1's ground truth "lists Rule 56 and Rule 57," "does not
list Rule 243," and "expects s.393(1) Table Sl. No. 8(vi) cited." All
three are true of the real file. I corrected a claim that didn't need
correcting, using a file that looked plausible (same case, same
filename, a real and complete-looking `ground_truth.json`) but was the
wrong one. Fixed in place in `results.md`, not silently — this is exactly
the class of error this project's own discipline exists to catch, applied
to this project's own documentation this time, not its resolver output.

## Why `citations_expected` being filled still doesn't move any metric

`_citations_status`'s own text, sitting in the file the whole time,
already said so: *"NOT currently consumed by `eval/score.py`'s
`m3_citations()` — that function validates whatever the run cited, it
does not compare against this list yet."* M3 as actually computed checks
only that a cited provision is real, current, and correctly quoted — never
whether it matches this pre-registered list. So while the *prose claim*
in `results.md` needed correcting, no *score* anywhere in this project
needed correcting. Worth being precise about which of the two actually
happened.

## What was fixed

- Copied the real, current `input.md` for all six cases from
  `step21drop/cases/<CASE>/` into `divergence/cases/<CASE>/` — verified
  byte-identical after copying, not just assumed. `divergence/cases/` is
  now a complete, self-contained, canonical location: the real frozen
  ground truth and the real input document, both in the one place the
  freeze commit and `eval/score.py` both already treat as authoritative.
- Added `step21drop/cases/README.md` stating plainly which file in that
  tree is real (`input.md`) and which is stale and unused
  (`ground_truth.json`), so the next person who diffs the two trees — or
  the next session of this same assistant — doesn't have to rediscover
  this from scratch.
- Corrected the specific wrong claim in `results.md`'s Block F.
- Existing commands elsewhere in this project's docs that point at
  `step21drop/cases/<CASE>/input.md` are unaffected and still correct —
  only `ground_truth.json` was ever the problem, and nothing has ever
  read it from that path.

## What to say about it

> "Cleaning up the repo's organization, we found two different copies of
> our own ground truth sitting in two different folders, one of them
> stale since before our real freeze commit. We checked which one
> `eval/score.py` actually reads — the real one, always — so no score in
> this project needed correcting. What did need correcting was a claim in
> our own results file, checked against the stale copy earlier tonight,
> that said a field was empty when the real, frozen version has always had
> it filled in. We're disclosing the mix-up and the correction together,
> because finding this kind of thing in our own work, not just our
> resolver's, is the same discipline applied consistently rather than only
> when it's convenient."
