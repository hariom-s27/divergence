# D47 — valuation.json is scoped to one case, and every other record silently inherits it

**Date:** 20 August 2026
**Found while continuing Step 1 (running nodes 3/4 for C1, C3, C4, C5). Read next to D45/D46, same class of finding — not a metric bug, a disclosure record accuracy bug.**

## The fact, stated plainly

`node3_valuation.py` reads exactly one file, `canonical_case.json`, and writes
exactly one file, `valuation.json`. Both are singular by construction — there
is no `--case` argument, no per-record input. `canonical_case.json` holds the
fact pattern for D1 alone: 5,000 USDC, receipt 03:14 IST Sunday 28 June 2026,
SBI TTBR candidates from the sheets either side of that weekend.

`run_pipeline.py --valuation` defaults to that same single `valuation.json`
for every `--record-id`. Nothing about the flag or the default is case-aware.

**C2's already-committed record (`runs/C2_pipeline.json`, cited in
`results.md`'s table) carries D1's valuation block verbatim** — a
5,000-USDC/28-June/SBI-94.00 lattice attached to a case that is $4,000 fiat,
Wednesday 17 June, settled by SWIFT wire with an e-FIRA already in hand and
*"no crypto anywhere"* by the case file's own description (`step21drop/cases/C2/case.md`).
There is no valuation dispute in C2 at all — the block is not just
case-mismatched, it asserts an ambiguity C2 does not have.

Running C1, C3, C4, C5 the same way would repeat this for four more records
before it was noticed and said out loud once, in one place, for one case.

## Why this does not retroactively touch the results.md table

Checked directly, not assumed: `grep -n valuation node_resolver.py
gap_enforcer.py` returns nothing except an unrelated string match
(`VALID_REGIME` containing the substring `valuation_method`). Neither
resolver prompt nor the gap enforcer reads the `valuation` block at all —
`regimes[]`, `missing[]`, `limits`, and every citation are produced
independently of it. **M1 through M5 as scored in `results.md` are unaffected
by this bug.** What is affected is narrower and still real: the `valuation`
field inside each disclosure record is not evidence about that case, it is a
copy of D1's evidence with a different `record_id` stapled on. A reader who
opened `C2_pipeline.json` expecting to see why C2 has no valuation dispute
would instead see someone else's dispute.

C3 makes the same point sharper. C3 exists specifically to test whether the
date-choice gap *closes* when SBI published a rate the same day (`case.md`:
*"the date choice is closed, the valuation method is still open... If it
reports the same [gap count as D1], it is not reading the facts"*). Attaching
D1's still-open-date-choice valuation block to C3's record would visually
contradict the exact thing that test case is built to demonstrate, in the one
field a reader would check first.

## What is being done about it tonight, and what is not

**Not fixing `node3_valuation.py` tonight.** Generalizing it to be
case-parametric needs per-case SBI/FBIL sheet snapshots for five more dates
(17 Jun, 23 Jun x2, 28 Jun fiat, plus C4's date) that were never fetched,
because the valuation lattice was built and scoped for the one canonical case
before the eval set existed. That is a real, multi-hour data-collection task,
not a code fix, and taking it on unilaterally tonight under the Step 1/4/5/6
deadline would be the same mistake D45 already named once — redesigning a
system under time pressure instead of disclosing its actual scope.

**Proceeding to run C1, C3, C4, C5 through `run_pipeline.py` anyway**, because
the field it corrupts is not one any of M1–M5 reads, and each record will
carry this same disclosure inline (see below) rather than silently reusing a
mismatched block with no explanation attached.

**Considered and rejected:** stamping a `case_scope_note` key directly into
each record's `valuation` block. Tried it on `C2_pipeline.json` first —
`schema.json`'s `valuation` object is `additionalProperties: false`, so the
note itself would have made the record schema-INVALID. Adding an eighth
post-freeze schema amendment just to create room for a disclosure string felt
like a different kind of change from the seven in D46 (those fixed the
schema's fit to output the pipeline already, documented, produced; this one
would exist solely to carry a footnote) — inviting exactly the kind of
under-pressure contract patch this project should be suspicious of in itself.
Reverted the JSON edit; the disclosure lives here and in `results.md` instead,
where a reader of the record is pointed to it without the record's own
validated shape being touched.

## What to say about it

> "Our valuation lattice was built for one case before the eval set existed.
> Wiring nodes 3 and 4 into the other five records surfaced that
> `valuation.json` never became case-aware — every non-D1 record was
> silently inheriting D1's own valuation dispute. It does not touch anything
> the five metrics score, because neither resolver reads it. It does touch
> the honesty of the record itself, which is exactly the class of thing this
> project exists to catch, so it is disclosed here, in every affected record,
> and in results.md, rather than fixed by quietly redesigning the lattice
> under deadline pressure tonight."
