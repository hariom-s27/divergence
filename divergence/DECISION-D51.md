# D51 — node3_valuation.py made per-case; C1 and C5 get their own real valuation; C2/C3/C4 still don't

**Date:** 21 August 2026
**Closes part of D47's gap. Read D47 first.**

## What changed

`node3_valuation.py` was hardcoded to `canonical_case.json` (D1) only.
`--case <path>` now reads any case file of the same shape; `--out <path>`
writes anywhere instead of always overwriting `valuation.json`. D1's default
invocation (`python node3_valuation.py`) is byte-for-byte unchanged —
checked directly: re-ran it and diffed against the committed
`valuation.json`, only `generated_at` and uncertainty-budget line order
differed, both cosmetic, reverted before committing.

**`candle`/`peg` (the market/crypto leg) are now optional, present or
absent together.** A case with no crypto leg has neither key at all;
`load()` and `build()` treat that as "this case has no market leg," not an
error. This is the real code change — the old code assumed every case
crosses a date choice AND a market/proxy choice, which was only ever true
for D1.

## C5 — fixed, no new data collected

C5 (USD 3,000, value-dated Sunday 28 June 2026) shares D1's exact weekend,
so the same SBI sheets (25 June, 29 June) that were already on disk answer
it. `c5_case.json` carries those, with no `candle`/`peg` — C5 is a plain
fiat wire, there is no crypto leg to represent. Result: **2 methods**
(not D1's 12), spread Rs 150 / 0.0532% — the genuinely narrow dispute C5
actually has (which date's rate, nothing else), not D1's stacked
crypto-proxy uncertainty. Patched directly into `runs/21aug/C5_pipeline.json`
(facts/regimes/citations untouched, `valuation` only), re-validated against
`schema.json`. Matches ground truth's own `methods_expected: 2` for C5
exactly — the pre-registered expectation already anticipated this shape.

## C1 — fixed, and it needed a schema amendment

C1 (₹85,000 domestic NEFT) has no currency conversion at all — an INR
invoice paid in INR. There is no lattice to build; representing it through
`node3_valuation.py`'s date/market-crossing machinery would manufacture a
dispute that does not exist. `schema.json`'s `valuation.methods` required
`minItems: 2` with the comment *"a single method is a failure state."*
That was true when a single method could only mean an incomplete lattice.
It stops being true the moment a case has no dispute to enumerate.

**Amended `methods` to `minItems: 1`**, with the description now
distinguishing the two ways a single method can arise: a real failure
(`spread.inr` nonzero, lattice incomplete) versus the honest true state
(`spread.inr == 0`, nothing to enumerate). C1's valuation is now one method,
`rate: 1.0`, `spread: {inr: 0, percent: 0}`, `uncertainty_budget: []` —
patched into `runs/21aug/C1_pipeline.json` the same way as C5, re-validated.
Also matches ground truth's `methods_expected: 1` exactly.

**This is the eighth-plus schema amendment after the freeze commit, same
family as D46's seven.** Same standard applies: it touches the output
contract only, `cases/*/ground_truth.json` is untouched, and it was found
by trying to represent a real case honestly, not by looking for a rule that
would make a number look better.

**Why this matters for the project's own thesis, not just plumbing.** A
system that only ever reports "twelve defensible answers" is not
credible when a case genuinely has one. C1 saying "here there is exactly
one figure, no dispute" next to D1 saying "here there are twelve" is what
makes the twelve believable. `run_pipeline.py`'s no-jsonschema fallback
check (`validate_schema()`) also had the old `< 2` threshold hardcoded;
updated to `< 1` for consistency, though the installed-`jsonschema` path
(used throughout tonight) never exercised the stale branch.

## C2, C3, C4 — not fixed tonight, and why

C2 (USD, Wednesday 17 June 2026, a day SBI *did* publish a rate) is the
other genuinely-determinate case per the plan — but building its real
single-value proof honestly needs the actual SBI TT buying rate published
for 17 June 2026, which is not in the corpus. Only 25/29 June sheets (D1's
weekend) exist on disk. Typing a plausible-looking rate from memory to fill
this in would be exactly the fabrication this project's own valuation
lattice exists to refuse — "no number typed from memory" is stated in
`node3_valuation.py`'s own long-standing comments, not a new rule invented
to excuse skipping this. C2 still carries D1's borrowed valuation block,
same as D47 originally disclosed, now narrower in scope: two of five
non-D1 cases (C1, C5) are fixed; C2, C3, C4 are not.

## What to say about it

> "Two of our five non-headline cases needed a valuation lattice at all —
> C5 shared D1's exact weekend, so real SBI data we'd already captured
> answered it directly. C1 needed something different: it has no currency
> conversion at all, so we had to change our own schema to let a record say
> 'there is exactly one right answer here' instead of forcing every case
> through the same multi-method shape. The other three still carry a
> placeholder we flagged the night we found it, because building their real
> answer honestly needs rate data for dates we haven't captured, and we're
> not going to type a number in to make the table look more finished."
