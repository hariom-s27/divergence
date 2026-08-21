# D55 — the fourth (and fifth) scope-reach error, two node-5 code bugs, and the freeze

**Date:** 21 August 2026
**Directly continues D54. Read that first — this is the cycle that was meant to close the class of error D54 fixed.**

## What triggered this cycle

D54's own record (`D1_v3_pipeline.json`) was re-read before shipping it as
the demo page, not just re-scored. Its `income_tax_on_receipt` conclusion
said: *"No deduction obligation arises under s.393(1) as the recipient is
outside India."* Priya — the taxpayer this record is about — is the
**resident recipient**. s.393(1) addresses the person **responsible for
paying**, not the recipient. Node 5's own attack on that exact record, read
after the fact, had already said so in different words: *"s.393(1) applies
to payments made to residents, not non-residents... the conclusion... is
incorrect."* A fourth instance of the identical scope-reach failure D54
named — found on the record that was about to become the thing a judge
opens first.

## The fix — S.393(1) SCOPE GATE, same shape as the other two

`03-income-tax.md` gained an S.393(1) SCOPE GATE under (d): state explicitly
which party occupies which role (payer vs. recipient) before writing any
TDS conclusion; a resident recipient is not "outside India" for this
section's purposes just because the payer is abroad.

**A second scope question was found reading the actual corpus text before
trusting this fix was complete**, not after: `corpus/verbatim/IT-393-1-T8vi.md`
scopes Table Sl. No. 8(vi) to *"any sum by way of consideration for
TRANSFER OF a virtual digital asset"* — acquiring a VDA from someone, not
any payment that happens to be settled in one. A payment for freelance
services, where the VDA is only the settlement currency, is arguably a
different transaction. Added to the same SCOPE GATE section: check which of
the two this receipt actually is before citing 8(vi) either way, and say so
in `reasoning` if the text does not itself settle it.

**Also fixed, same commit:** the lacuna citation template in the JSON
output example was allowing `Rule 243(8)(e)` (the rejected provision) into
`citation.provision` instead of Rule 57 (what a `lacuna` valuation
conclusion actually rests on). Tightened to name explicitly what the
conclusion rests on, never the last rule checked and discarded.

## Two node5_adversarial.py bugs, found running the fix, neither legal

1. The model sometimes emits `downgraded_to: ""` where the contract wants
   the field absent. `_validate_attack_shape` was hard-failing on this —
   fixed to treat an empty/whitespace string the same as absent, for both
   `attacked[].downgraded_to` and `checked_and_survived[]`.
2. `_reject_upward_revisions` (D54) was setting a rejected `downgraded_to`
   to `None` — but `schema.json`'s `downgraded_to` `$ref`s the certainty
   enum, which has no null member. Our own guard was producing
   schema-invalid output as a side effect of rejecting a bad value. Fixed
   to delete the key instead of nulling it.

Both found live, on seed 1 of the three-seed run below, before any seed was
scored — the same "catch it before it reaches the scoreboard" discipline
this project applies everywhere else.

## The three-seed run and selection

Pre-registered in `results.md` *before* any seed ran: pick the first of
seeds 1/2/3 that is schema-valid and whose `regimes[]` carries all three
expected objects. **Seed 1 is schema-invalid** (`condition_met: null`, a
node 3/4 shape slip unrelated to node 5). **Seed 2 is selected** —
schema-valid, all three regime objects present, `valuation_method` cites
**Rule 57**, `certainty: lacuna`. All three seeds score M1=100%/M3=100%/
M4=12/12; M2 (gap recall) varies 50%/50%/25% — full table in `results.md`.

## Node 5, run against the selected record — a fifth instance, disclosed not fixed

`D1_final_seed2_attack.json`: 4 attacks, **all 4 landed** — corrected here;
this doc originally said "2 landed, 2 survived," which mis-read the CLI's
own summary line. `checked_and_survived` (length 2) is a separate list of
conclusions never attacked at all, not a split of the four that were. No
rejections were needed from the downgrade guard on any of the four (one
target's before-certainty was ambiguous under the word-overlap matcher and
correctly skipped, not guessed). One landed attack is a **fifth instance of
the scope-reach pattern**: seed 2's own `income_tax_on_receipt` reasoning
invented a new escape hatch this fix cycle didn't anticipate — *"no
deduction obligation arises under s.393(1)... because... the payer is
outside India"* — an exemption not stated anywhere in the text. Node 5
caught it, unprompted, matching a direct read of the corpus text done
independently before this attack ran. A second landed attack repeats Rule
57 row 7's own catch-all objection (expected); a third is the incoherent
place-of-supply argument already named as a known failure mode; a fourth
contests the classification limb itself (whether receiving USDC is a
"transfer" under s.2(47)) — most likely the node's documented
attack-everything over-eagerness rather than a sixth real finding, noted
rather than omitted.

**This is not fixed with a sixth prompt edit.** The instruction that opened
this cycle said explicitly that each previous fix had produced a new error
and that this would keep happening, and set the rule before any of this
ran: after one final cycle, whatever remains is disclosed, not chased.
`D1_final_seed2.json` is frozen on that basis. Full account, including the
"Where we lose" and "Still open" updates, in `results.md`'s Block F.

## One claim in the instruction that started this cycle turned out to be wrong

It asserted D1's `citations_expected[]` "lists Rule 56 and Rule 57" and
that ground truth "expects s.393(1) Table Sl. No. 8(vi) cited." Checked
directly against `step21drop/cases/D1/ground_truth.json` before writing
anything about it: **`citations_expected` is `[]`**, never filled in, with
its own note saying so. No citation-matches-ground-truth claim is made
anywhere for D1 as a result — corrected here rather than repeated.

## What to say about it

> "We ran one more fix cycle on D1 before freezing it. It fixed a fourth
> instance of the same scope-reach failure and, in the same run, our own
> adversarial checker found a fifth — a different escape hatch to the same
> wrong conclusion, on a claim this very fix cycle introduced. We are
> disclosing that fifth instance, not fixing it, because the alternative is
> an unbounded chain of cycles three days before submission, and because a
> disclosed, verified-current limitation is worth more to a judge than
> another few hours spent chasing whatever the next one turns out to be."
