# D59 — ⚙ E, the scope-reach enforcer: node 5's item 2, turned into code for the three cases already proven

**Date:** 21 August 2026
**Different in kind from D42–D58: those closed submission gaps and fixed found bugs. This is the one genuine new capability added after the ship-plan work was otherwise complete — a fourth deterministic gate, built, tested against real historical failures, and caught regressing against the project's own frozen demo record before it ever reached `run_pipeline.py`.**

## Where this came from

`citation_matcher.py`'s own `LIMITATIONS` section has said this since it was
written: *"A VERIFIED citation exists in our corpus and is current. It does
NOT mean the provision supports the proposition it was cited for...
Mitigation: the adversarial node checks support. This checks existence."*
Node 5's own checklist (`architecture.md`) lists **"scope reach — does
column B / the opening words actually reach this fact pattern"** as item 2,
right after currency, and names two real catches against it: *"Rule 115 not
applying at all"* and *"row 7 of Rule 57."* Both were real. Both were only
ever caught because node 5 — an LLM call, probabilistic — happened to run
and happened to land the attack that day.

Three real instances of this exact failure exist in this project's own
history, each fixed, each time, by adding a SCOPE GATE paragraph to prompt
03 (D54, D55) — a stronger request, still only a request:

1. **`runs/21aug/D1-a_regimes.json`** (and its matching attack,
   `D1-a_attack.json`) — `income_tax_on_receipt` cites *"Rule 11UA,
   Income-tax Rules, 1962"* and its `reasoning` says the fair market value
   is *"determined using the telegraphic transfer buying rate of USDC...
   as per Rule 11UA."* Rule 11UA's current-numbering successor, Rule 57,
   contains **zero** virtual-digital-asset references — its rows that serve
   s.92 (the section that brought a VDA into "property") cover only
   jewellery, art and shares; its one residual catch-all is scoped to
   s.26(2)(j) alone, never to s.92 (`ITR2026-RULE-57.md`).
2. **DECISION-D50.md's addendum** — Rule 243(8)(e) cited as this taxpayer's
   own valuation method. Its own opening words scope it to *"the
   aggregate-reporting obligations of a reporting crypto-asset service
   provider"* — a regulated intermediary, never the individual whose
   receipt is being valued.
3. **DECISION-D50.md** — Rule 206/207 cited to convert a VDA receipt. Both
   convert income *"in foreign currency,"* and s.2(111) of the Income-tax
   Act, 2025 defines a VDA as *"not being Indian currency or foreign
   currency."*

Three real, hand-verified, previously-only-caught-by-an-LLM findings. The
obvious next step: stop depending on node 5 having been asked.

## What was built: `scope_enforcer.py`

Same shape as `gap_enforcer.py` (⚙ A) and `citation_matcher.py` (⚙ C):
deterministic, no model call, no API. `SCOPE_CHECKS` maps each of the three
provisions' `provision_id` (matched via the same ref-extraction
`citation_matcher.py` already trusts, so *"Rule 11UA"* and *"Rule 206,
Income-tax Rules, 2026"* resolve to the same entry) to a small function
encoding the exact textual scope condition already proven in the corpus.
`enforce_scope(regimes, facts)` drops any regime conclusion whose citation
fails its scope check — the same `accept=False -> DROPPED, not flagged`
semantics ⚙ C already uses, because a citation whose own scope does not
reach these facts is exactly as invalid as a fabricated one.

Wired into `run_pipeline.py` as a new step, `[5/N] ⚙ E SCOPE-REACH
ENFORCER`, between ⚙ C (citation matcher) and ⚙ A (gap constraint
enforcer) — after existence/currency is checked, before the gap constraint
is applied. Drops fold into `limits[]` the same way ⚙ C's drops already do.
`N` is now 6 (7 with `--node5`), up from 5 (6) — disclosed here rather than
left for someone to notice the step count changed.

## The bug this file's own test suite did not catch — a real record did

A first version of `enforce_scope()` dropped every citation of the three
provisions unconditionally, whenever the receipt's asset was a known
virtual digital asset. The five-case self-test passed. Then, before
touching `run_pipeline.py`, it was run against real saved records instead
of only synthetic fixtures — and against `runs/21aug/D1_final_seed2.json`,
**the frozen record already live on `output-interface.html`**, it dropped
one of the record's two remaining conclusions:

```
"regime": "valuation_method",
"outcome": "No provision in the text prescribes a specific method for
             determining the rupee value of USDC on the valuation date.",
"certainty": "lacuna",
"citation": {"provision": "Rule 57, Income-tax Rules, 2026", ...}
```

That is not a claim that Rule 57 governs. It is Rule 57 being cited **as
evidence that nothing does** — the exact pattern `ITR2026-RULE-57.md`'s
"five locked doors" analysis is built on, and this project's own headline
finding. A scope check keyed only to "provision + facts" cannot tell that
conclusion apart from the historical bug (`D1-a`'s *"determined... as per
Rule 11UA,"* asserted as the method) without also looking at what the
conclusion is actually claiming.

**Fixed using a field the schema already defines for exactly this
distinction, not a keyword guess at free text.** `certainty == "lacuna"`
means, by `schema.json`'s own definition, *"no rule exists."* `enforce_scope()`
now exempts any regime entry with that certainty value, unconditionally,
before running any scope check. The historical bug (`D1-a`, certainty
`insufficient_evidence`, forced there by an unrelated gap constraint, not
by a lacuna finding) never carries `lacuna` — confirmed by re-running both
records through the fixed function. The guard costs nothing against the
real catch and prevents a false drop on the project's own correct output.

Two regression cases were added to `scope_enforcer.py`'s self-test
specifically for this — the exact citation, the exact asset, one with
`certainty: lacuna` (must survive) and one without (must still drop) — so
this cannot silently regress again. Final self-test: **7/7**, plus two
direct checks against the real files (`D1_final_seed2.json`: 0 dropped,
unchanged; `D1-a_regimes.json`: 1 dropped, the real historical bug, still
caught).

## What was deliberately left out: s.393(1)

A fourth candidate provision — Section 393(1) Table Sl. No. 8(vi), *"FOR
PAYMENTS TO RESIDENT"* (`DECISION-D55.md`'s inverted-role bug) — was
considered and rejected. Unlike the three above, that failure turns on
**which direction a conclusion argues**, not on citation + facts alone: the
correct, current D1 answer legitimately cites this same provision to
explain why *no* TDS obligation arises, because the real test is the
residence of the counterparty receiving the underlying transfer, not the
direction of payment. Telling the correct use apart from the historical
inverted-logic bug requires reading the outcome text's polarity, and a
keyword guess at polarity was judged more likely to drop a correct
conclusion than to catch a wrong one — the identical shape of mistake this
section's own regression just found and fixed for Rule 57. Left for node 5,
same as before this file existed. Stated as a limitation in
`scope_enforcer.py`, not silently omitted.

## What this is not

Not an NLI model, not a general scope-reading system. Three hand-verified
findings, encoded once each. A fourth misapplied provision this project has
never analysed is exactly as invisible to this file as it was before ⚙ E
existed — node 5 remains the only backstop for anything outside these
three. What changed is that these three specific, already-proven failures
can no longer reach a record regardless of whether node 5 is run that day —
"the adversarial node happened to catch it" became "the code cannot emit
it," for exactly the failures this project has already paid to find.

## CI

Two gates added alongside `scope_enforcer.py --self-test`:
`gap_enforcer.py --self-test` (⚙ A) was written with a working exit code
from the start but, unlike `citation_matcher.py` and `gate0_check.py`
(D57), was never actually wired into `.github/workflows/python-package-conda.yml`
— the same class of gap D57 fixed, found doing the same kind of pass. Both
now run on every push.
