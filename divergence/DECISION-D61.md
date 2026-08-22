# D61 — mutation corpus: manufacturing labelled defects at zero annotation cost

**Date:** 22 August 2026
**A deliberate reprioritization, not a stale-plan collision: an earlier planning document (`IDEAS-AND-PLAN.md`, Idea 9) marked mutation testing "no, but cheap enough to be the first post-submission experiment." A newer, more time-pressured plan overrode that to a same-day MUST. Built the way everything else this session has been: additive, tested both directions, nothing frozen touched.**

## The problem this answers

This project has exactly three confirmed real-world scope-reach failures
(⚙ E, `DECISION-D59.md`) and a handful of other found bugs. Six is not a
rate. Mutation testing manufactures many more labelled instances *by
construction* — take a real, already-verified conclusion from one of the
six cases, apply a small, well-defined perturbation that a correctly
functioning check should catch, and see whether it actually does.

## What was built: `mutation_corpus.py`

Seven operators, applied to the six cases' own real saved regime
conclusions (`runs/21aug/*_pipeline.json`, `D1_final_seed2.json` for D1 —
read-only, the frozen record is never written to). No model call, no API,
zero marginal cost, fully reproducible. Each operator is skipped
explicitly on a case it doesn't fit — never forced onto a fact pattern
that would make the test meaningless (documented in the code, and in the
report's own `applicable: False` rows).

| Operator | What it does | Applicable | Caught |
|---|---|---|---|
| `YEAR_FLIP` | cites the current-numbering form under the wrong-side tax year | 3/6 | 3/3 |
| `NUMBERING_SYSTEM_SWAP` | cites the former-numbering form under the current tax year | 3/6 | 3/3 |
| `FABRICATED_CITATION` | a plausible section number this corpus doesn't hold | 6/6 | 6/6 |
| `SCOPE_VIOLATION` | cites one of ⚙ E's 3 known-bad provisions on a VDA case | 9 (3 cases × 3) | 9/9 |
| `REGIME_CROSS_CITE` | swaps one regime's real citation onto a different regime | 6/6 | 1/6 |
| `OVERCONFIDENT_CERTAINTY` | relabels a hedged conclusion as `settled` | 8/8 | 8/8 |
| `DEPENDENCY_DROP` | clears a real `depends_on_missing`, claims `settled` | 6/6 | 0/6 |

**30/41 applicable mutations caught overall — reported here for
completeness, and immediately set aside, per the source idea's own
instruction: "report per-dimension recall, never a single aggregate."**
The blended number hides that four of the seven rows are at or near 100%
and two are near 0% for structurally different reasons. Averaging them
produces a number that describes nothing real.

## Two genuine, newly-measured gaps — not previously disclosed anywhere

1. **`DEPENDENCY_DROP`, 0/6.** `gap_enforcer.py` forces certainty to
   `insufficient_evidence` whenever `depends_on_missing` is non-empty —
   correctly, unconditionally, exactly as designed (⚙ A). But it has no
   way to notice that a real dependency was silently *removed* before it
   ever saw the record. If node 2 (or a compromised/buggy resolver) drops
   a gap it should have declared, nothing downstream currently re-derives
   that the dependency should have been there. This is a real limitation
   of ⚙ A's actual guarantee, not previously stated this precisely
   anywhere in this project's docs.
2. **`REGIME_CROSS_CITE`, 1/6, and the 1 needs an honest correction.**
   Citing a real, current, correctly-quoted provision on the *wrong
   regime* (e.g. a GST citation attached to an income-tax conclusion) is
   invisible to `citation_matcher.py` (the citation exists and is
   current) and to `scope_enforcer.py` in general (it checks reach
   against facts, not regime membership). The one case that DID get
   caught (D1) is not evidence against this: D1's swap happened to move
   *Rule 57* — one of ⚙ E's three known-bad citations — onto a different
   regime, and it was dropped for the *original* scope-reach reason, not
   because anything checks regime-appropriateness. Verified by reading
   the actual `caught_by` field, not assumed from the count. Reported
   honestly as 1/6 by mechanism, not overstated as evidence of a
   regime-check that does not exist.

**One catch that*is* real and worth naming precisely.** Within
`OVERCONFIDENT_CERTAINTY`, D1's `valuation_method` (real citation: Rule
57, real certainty: `lacuna`) relabelled to `settled` **was** caught — by
`scope_enforcer.py`, not by coincidence this time. `enforce_scope()`
exempts `certainty == "lacuna"` specifically because a lacuna citation is
evidence of absence, not a claim of authority (D59). Strip the `lacuna`
label back to `settled` and that exemption no longer applies — the
underlying scope violation Rule 57 always had is exposed again. This is
the mutation corpus validating ⚙ E's own design decision from the
inside: the exemption is precise enough that defeating it honestly (by
actually changing what's being claimed) puts the record back in the
danger zone the check was built for.

## What this is not

Not a claim that this project now has 7 new named failure classes with
measured base rates — `n` for four of the seven operators is 3–9,
manufactured from 6 cases, not independently sampled. It is what mutation
testing actually buys: real, cheap, honestly-labelled evidence of *which*
of this project's existing gates cover *which* kind of defect, and two
newly-precise statements of where they don't, found by construction
rather than by waiting for a seventh real bug to show up.

## Not wired into CI

Deliberately a report script, run on demand, same category as
`cost_model.py` — not a pass/fail gate. There is nothing to fail: every
row's result is already known and expected (or is itself the finding).
