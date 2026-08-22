# D65 — disagreement gate (Arm D), and a real cross-Act citation bug it caught in already-shipped code

**Date:** 22-23 August 2026
**S1 of the SHOULD list, taken up after all six doable MUST items were green.** Building this found and fixed a real, latent bug in `scope_enforcer.py` (D59) — CI-gated, already shipped — that nothing had caught until this file was tested against real data.

## What was built

**`disagreement_gate.py`** — deterministic, no model call. Takes *k*
independent samples of the same resolver call (same facts, same
`missing[]`, same tax year — different temperature/seed draws) and
reports, per regime, whether `certainty` and `citation` actually agree
across them. This project already has real, measured evidence that
identical-input calls disagree — `results.md` Block E2: node 2's gap
recall read 50%/75%/0% across three seeds of the identical D1 case.
Nothing turned that instability into a structured, per-field signal a
caller could act on; this is that signal.

**Self-tested against real data, not synthetic fixtures**: D1's own three
frozen seed records (`runs/21aug/D1_final_seed1/2/3.json`, already
central to `results.md` Block F) are genuine *k*=3 independent samples of
one input. Real, already-documented disagreement exists between them —
seed 3 diverges from seeds 1/2 on two of three regimes. Verified the gate
correctly flags exactly that shape: `income_tax_on_receipt` and
`valuation_method` both `DISAGREEMENT`, `gst_export` `UNANIMOUS` (all
three seeds independently landed on `insufficient_evidence`, forced there
by `gap_enforcer.py` regardless of what each sample's model said).

## The bug this found, in code that had already shipped and passed CI

Citation comparison needs to recognise that *"Section 115BBH, Income-tax
Act, 2025"* and *"Section 115BBH, Income-tax Act, 1961 — carried into the
Income-tax Act, 2025"* are the same provision — exactly the normalisation
`citation_matcher.py`'s ref-matching already does. The first version of
`_citation_key()` reused `extract_refs()`/`_refs_match()` directly and
returned **`FEMA-2n`** for the citation *"Section 2(6), Integrated Goods
and Services Tax Act, 2017"** — a GST provision resolving to a FEMA
corpus file. Not a corner case: `_refs_match()`'s own rule ("one bracket
chain is a prefix of the other") means a **bracket-less** stored
reference matches *any* more specific citation with the same base
section number, in *any* Act, unless something separately checks which
Act either side is actually in. `citation_matcher.verify()` has always
had that check (`instrument_of()`, compared before ever calling
`_refs_match()`); this new file's copy of the pattern didn't.

**Then found the identical gap in `scope_enforcer.py`'s
`_match_provision_id()` (D59) — already shipped, already a CI gate, three
weeks of real records passed through it.** Same missing check, copied
from the same underlying pattern. `SCOPE_CHECKS` happens to be keyed to
three provisions that are *all* bracket-less stored references (Rule
206, Rule 207, Rule 57) — exactly the precondition that triggers this.
No evidence any real record was actually mismatched this way (the
resolvers' own scoped corpora don't plausibly produce the specific
collision), but the guard was structurally absent, not merely untested.

**Fixed in both files**, same shape as `citation_matcher.verify()`:
compare `instrument_of(cited)` against `instrument_of(stored)` before
trusting a ref match. Verified the fix doesn't change any existing,
already-correct behaviour — re-ran `scope_enforcer.py`'s full self-test
(still 7/7), the real `D1_final_seed2.json` regression (still 3 kept, 0
dropped), and the real historical-bug catch (`D1-a_regimes.json`, still 1
kept, 1 dropped) — before adding a permanent regression test
(`_test_instrument_cross_check`, real corpus data, the actual GST/FEMA
collision) so this specific gap cannot silently reopen.

## What is not built: real k=5 sampling

Producing five real samples needs five real resolver calls at real
temperature. `FEATHERLESS_API_KEY` is not set in this environment — the
same constraint every live-verification item this session has hit (D62,
D63, D64). The self-test uses *k*=3, the real sample count this project
actually has saved on disk, disclosed as three, not presented as five.
The comparison logic itself works for any *k* ≥ 2 and needs no change to
run against five real samples the moment someone with a key produces
them.
