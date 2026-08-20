# STEP 21 DROP — what's in here and what to do

Unzip into `divergence\`. It adds four things and overwrites one.

```
evaluation-design.md      <- Step 21 deliverable. Read it first.
eval/score.py             <- the five metrics, runnable
cases/                    <- 6 case folders + 4 ablation variants, scaffolded
runs/                     <- empty, where normalised run files go
gate0_check.py            <- OVERWRITES yours: utf-8 stdout + a stale-ok marker
```

## The two remaining Gate 0 flags

They are false positives — `canonical_case.py` quotes its own history in the
docstring, which is exactly right. The new checker honours an explicit marker
so you don't have to delete a true sentence. Change that line to:

```python
    Three different percentages (8.5%, 9.27%, 9.394%) and three different rupee   # stale-ok
```

Then `gate0_check.py` reports **0 problems**. Same idea as `~~strikethrough~~`
in markdown: retired figures are allowed where they are being *reported* as
retired, and the exemption is explicit rather than a silent suppression.

**And delete `canonical_case.DAMAGED_BACKUP.py`** — the refactor is verified
end to end, so it's a second copy of the old single-point calculator with no
job left. Move it to `_old_corpus_backup\` if you want the history.

---

## What P1 does tomorrow morning — ~4 hours

`cases/` is scaffolded. Each folder has `case.md` (the scenario, already written)
and `ground_truth.json` (a filled skeleton you correct and extend).

1. Produce the actual input document for each case — `invoice.pdf`,
   `payment.png`, or `payment.txt`. **Typed input is fine for at least two;
   say so openly rather than hiding it.**
2. Correct `ground_truth.json` in each folder. The `facts`, `missing` and
   `elements` blocks are pre-filled from the scenario — check every value.
3. Fill `citations_expected[]` from the scoping table in `architecture.md`.

> ### `git add cases/ && git commit -m "ground truth, pre-registered"`
> ### Then put that hash in `results.md`.
>
> **Do this before any model runs.** If ground truth is written after seeing a
> pipeline output you will grade toward what the pipeline produced, every
> number becomes circular, and the damage is invisible from the outside.

## What P3 does — arms A and B

`baseline-prompt.md` has been frozen since 6 August and has **never been run.**
That is 100 points resting on an unexecuted comparison.

Protocol is in `evaluation-design.md` §5. The short version: fresh session every
run, five runs per case, temperature default not zero, save every raw output
including the good ones, change nothing between runs.

For arms A and B you hand-code the prose output into the run-file shape at the
top of `eval/score.py`. That hand-coding is why the protocol says two scorers
independently on the first five.

```
python eval/score.py --run runs/D1_armA_large_seed1.json   # one run, detail
python eval/score.py --all                                  # everything
python eval/score.py --table                                # markdown for results.md
```

---

## Two things in the design worth knowing about

**C3 and C4 are marked "partially determinate", not "clean".** A USDC receipt on
a Tuesday still has no prescribed valuation method — Rule 57 doesn't reach it
whatever day it is. Only the *date* ambiguity closes. If we'd marked C3 clean we
would have been training the system to give a wrong answer, so **metric 5 is
scored per element, not per case.**

**The scorer credits keyword overlap, not just string similarity.** Arm A answers
in prose: "no FIRC" and "bank certificate of foreign inward remittance (FIRC)"
are the same gap, and a pure ratio scores them 0.28. Under-crediting the baseline
is the straw-man failure this whole evaluation exists to avoid.

An earlier version over-corrected and matched "purpose code" to "no FIRC". Both
directions of error are bad; **that one is worse, because inflating arm A hides
the failure we are trying to measure.** Fixed to require a shared distinctive
token. Worth an `iteration-log.md` entry — it is a real v1→v2 on a scoring rule,
and "documented iteration" is a scored sub-criterion.

---

## §7 of evaluation-design.md — read it out loud as a team

It states, in advance, what would falsify the claim:

- arm A names ≥6 of 12 methods unprompted → the lacuna is visible to a good
  single prompt, and our contribution is the enforcement, not the detection
- arm B ≈ arm C → it's a chain-of-thought result, not an architecture result,
  **and we say that in the video**
- node 5 catches 0 of 4 planted defects → the adversarial checker is theatre
  and we cut the novelty claim resting on it

**Agreeing to these now, before any data exists, is what makes the results
believable later.** It is also the cheapest Bonus-criterion signal available:
four independent judges each see a team that wrote down how it could be wrong.
