# D50 — node 5 ran for the first time: a real defect caught, an ablation, and a calibration finding

**Date:** 21 August 2026
**05-adversarial.md's own header said "THIS NODE HAS NEVER RUN" and named the
ablation as "what decides whether it earns its place." This is that run.**

## Built per D46's Step 5, same pattern as node_resolver.py

`node5_adversarial.py`: scoped to the full verbatim corpus (not per-regime
like nodes 3/4 — 05-adversarial.md's own header says its scope is "the full
verbatim corpus + the gap list + the valuation lattice"), the `adversarial`
model slot (`mistralai/Mistral-Large-Instruct-2411`, D41 — a different model
family from the Qwen resolvers on purpose), validates its own output shape
before returning, records provenance to `_meta`. Wired into `run_pipeline.py`
behind `--node5`, off by default, so every existing record stays reproducible
without it. `schema.json`'s top-level `attacked[]` property already existed
(present since before tonight) — no schema amendment needed for this one.

**Design choice, stated plainly:** node 5's `downgraded_to` recommendations
are NOT automatically written back into `regimes[].certainty`. `target` is
free text ("the exact conclusion you are attacking"), not a structured
pointer, and fuzzy-matching it back to one specific `regimes[]` entry was
judged more likely to silently corrupt the wrong entry than to help. A run
with `--node5` gets a `limits[]` entry saying so. `attacked[]` sits next to
`regimes[]` in the same record for a reader to cross-reference by eye.

## Finding 1 — node 5's first real-data run caught a genuine, previously undisclosed defect in D1's own published record

Ran node 5 against D1's actual, already-committed `runs/21aug/D1_pipeline.json`
— not a planted variant, the real thing already cited in `results.md` as a
100%-M3-valid record. Its `income_tax_on_receipt` conclusion reads: *"The
fair market value is determined using the telegraphic transfer buying rate
of USDC on the last day of the tax year (2026-03-31)."*

**That date is wrong, and checking the corpus directly shows why.**
`ITR2026-RULE-206.md` is a table; row 3 — *"Income from house property,
profits and gains of business or profession..., income from other
sources"* — is the one row whose specified date is *"last day of the tax
year of the assessee."* Every other row uses a different date rule. D1's
resolver output pulled row 3's date onto a s.115BBH virtual-digital-asset
receipt, which Rule 56 (elsewhere in the same conclusion, correctly) already
fixes to the date of receipt — 28 June, not 31 March. Two different
valuation dates asserted in the same paragraph, and the second one is the
wrong row of a multi-row table applied to facts it doesn't serve. This is
the identical failure shape as the project's own named historical catch
("Rule 57 row 7... serves s.26(2)(j) alone, not s.92") — a citation that is
real and current (which is why `citation_matcher.py` correctly marked it
`verified: true`) attached to reasoning that misapplies it.

**This was not caught by any existing metric.** M3 (citation validity) only
checks that a cited provision exists and is current — it has no concept of
"the right row of this provision." M1, M2, M4 don't touch resolver
reasoning at all. Node 5 caught it because judging scope reach against the
verbatim text is literally checklist item 2. `05-adversarial.md`'s own
framing — "everything credited to adversarial review so far was found by a
human" — is no longer accurate as of this run.

## Finding 2 — the ablation, D1-a through D1-d

`make_ablation_variants.py` plants each of the four named defects into a
**copy** of D1's real `regimes[]` (never the original — `runs/21aug/D1_pipeline.json`
is untouched), one at a time, by hand, not by a model — matching the
D1-a/b/c/d case files' own instruction ("one of our own four real errors,
planted deliberately"). Each variant run through `node5_adversarial.py`
against the same real `missing[]`/`valuation` D1 already has.

| Variant | Planted defect | Checklist item | Result |
|---|---|---|---|
| D1-a | cites Rule 11UA for FY 2026-27 | 1, operative status | **CAUGHT** — "Rule 11UA, which is not current for FY 2026-27. The correct rule... is Rule 56" |
| D1-b | applies Rule 57 row 7 to a s.92 receipt | 2, scope reach | **NOT CAUGHT** — none of 5 attacks mention Rule 57 or row 7 at all, though the planted sentence is verbatim in the input node 5 received (checked directly, not assumed) |
| D1-c | asserts GST despite FIRC/verification missing | 3, missing document | **CAUGHT** — "depends on the independent verification... the conclusion is not valid until this information is obtained" |
| D1-d | values USDC at the USDT print, proxy unstated | 4, correct instrument | **CAUGHT** — "the rate source used... is the USDT/INR print... not the rate source named by the law" |

**3 of 4 caught.** D1-b's miss is reported here at the same weight as the
three catches, per 05-adversarial.md's own instruction written before this
run: *"Report the result whichever way it comes out."* No retry, no prompt
tweak attempted to fix the miss before reporting it — that would be
optimizing the ablation's outcome after seeing it, the same discipline this
project applies to its ground truth.

## Finding 3 — a calibration concern, found by reading all five runs together, not any single one

**`checked_and_survived` was empty in every one of the five node-5 runs
tonight** — the real D1 record and all four variants. Every conclusion node
5 was given, it attacked; every attack, it recorded as landed
(`survived: false`). `05-adversarial.md` names this exact pattern as a
warning sign, written before any run existed: *"`checked_and_survived` must
not be empty either. A checker that breaks everything is as useless as one
that breaks nothing."*

Read plainly: node 5 currently cannot distinguish a conclusion with a real
defect (D1-a, D1-c, D1-d — genuinely wrong) from one that is merely
uncertain by design (every D1-family conclusion here is already
`insufficient_evidence`, forced there correctly by `gap_enforcer.py` because
of the counterparty-verification gap). The SYSTEM prompt's own instruction
to "default to attacking" and treat "this appears correct" as a sign of not
looking hard enough may be tuned too far toward the first failure mode this
project catalogued (silent overconfidence) and not calibrated against the
second (attacking a conclusion that is already correctly hedged). This
reads as one plausible explanation for D1-b's miss too — five generic,
recycled attacks were available and easy to re-issue; finding the one
sentence with the actually-planted defect required reading the *reasoning*
field specifically for its stated scope, which the checker did for D1-a,
D1-c, and D1-d's variants but not D1-b's.

**Not fixed tonight.** Re-tuning the prompt to fix D1-b's miss immediately
after seeing it would be adjusting the test to fit the answer, the exact
harm 05-adversarial.md's pre-registered framing exists to prevent. This is
reported as three findings — a real catch on unplanted data, a 3/4 ablation
score, and a genuine calibration gap — not smoothed into a single "node 5
works" headline.

## What to say about it

> "We built the adversarial checker the same night we ran it for the first
> time, so we have no track record to lean on — only this run. It caught a
> real, previously undisclosed error in our own headline case: a resolver
> conclusion that cited the right rule and the wrong row of it. On the
> planted-defect ablation we designed before running anything, it caught
> three of four. And reading all five runs together, not one of them, shows
> it currently attacks everything it's given rather than discriminating —
> which is very likely why it missed the fourth. We're reporting all three
> of those findings at the same weight, because the node's whole premise is
> publishing the attack instead of hiding it, and that has to apply to
> attacks on the node itself."
