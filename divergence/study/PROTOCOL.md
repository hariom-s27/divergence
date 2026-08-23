# STUDY PROTOCOL — disclosure format and decision quality

**Written and published before any trial is run.** Nothing in this
document may be edited after data collection begins except to append a
dated erratum — the same discipline this project applies to its own
ground truth (`results.md`'s "Pre-registration" section, `DECISION-D46.md`).

**What this is, and what it is not.** This is the preparatory
instrument for M7 (the four-person decision-quality study) — the
control-condition interface, the payoff function, the trial design, the
screener, and an empty results table. It is not the study itself.
Running it — recruiting four real people, sitting them through eight
real trials each, recording their real responses — is the
investigator's own task, outside what this repository can do for
itself. `results.md`'s own "STATISTICAL LIMITS" section already applies
here with even more force than it does to the six evaluation cases: n=4
is four independent units, not a sample large enough to support any
population-level claim.

---

## 1. The payoff function

Published here, before any trial, exactly as it will be applied —
changing it after seeing results would be exactly the kind of
undisclosed post-hoc adjustment this project's own pre-registration
discipline exists to prevent.

**Task.** On each trial, the participant is shown one disclosure page
(either `output-interface.html`'s full lattice, or
`baseline-interface.html`'s single figure — see §2) for one real case,
and states the INR figure they would file.

**Inputs**, read directly from that case's own real, frozen valuation
record (`runs/21aug/*.json`, never invented for the study):
- `lo`, `hi` — the minimum and maximum `inr_value` across that record's
  own `valuation.methods[]`. For a case with no real dispute (a single
  method, zero spread — C1, C2 in this design), `lo = hi` = that one
  real figure.
- `W = hi - lo` (range width). For a no-dispute case, `W` is defined as
  `max(1, 0.01 × lo)` so the formula below never divides by zero, while
  still making any deviation at all from the one real figure count as a
  large, immediate penalty — appropriate, since there genuinely is no
  second defensible figure to be lenient toward.
- `x` — the participant's own filed figure for that trial.

**Formula:**

```
if lo <= x <= hi:
    payoff = 100                                            # inside the defensible range
elif x > hi:
    d = min((x - hi) / W, 2.0)
    payoff = max(0, 100 - 50 * d)                            # overpayment
else:  # x < lo
    d = min((lo - x) / W, 2.0)
    payoff = max(0, 100 - 125 * d)                           # understatement
```

**Why asymmetric, and why these exact constants.** Any figure inside
`[lo, hi]` scores the same full 100 — consistent with this project's own
thesis, already argued in `results.md`'s "External precedent" section
(the OECD's own transfer-pricing guidance: "any point in the range
satisfies" a defensible-range test) — the lattice's own midpoint is not
treated as more correct than its edges. Overpayment (filing *above* the
defensible range) is real but bounded: unnecessary tax paid, a genuine
cost, penalized at rate 50 per range-width. Understatement (filing
*below* the defensible range) is penalized at rate 125 — two and a half
times as steep — reflecting the asymmetric real-world stakes this
project's own corpus documents: an unsupported low figure risks a real
under-reporting exposure, not merely an inefficiency. Both penalty
terms are capped at 2 range-widths of deviation (`d` clamped to 2.0) and
the payoff is floored at 0, so one wild trial cannot produce an
unbounded or negative score.

**Worked example**, D1's own real range (`lo = 469,750.00`,
`hi = 517,618.76`, `W = 47,868.76` — the same real figures already
published in `results.md` and `SAMPLES.md`), computed and verified, not
hand-rounded:

| Filed figure (INR) | Position | Payoff |
|---|---|---|
| 490,000.00 | inside `[lo, hi]` | 100.00 |
| 469,750.00 | at `lo` | 100.00 |
| 517,618.76 | at `hi` | 100.00 |
| 550,000.00 | above `hi` by 0.68 range-widths | 66.18 |
| 600,000.00 | above `hi`, capped | 13.95 |
| 440,000.00 | below `lo` by 0.62 range-widths | 22.31 |
| 400,000.00 | below `lo`, capped | 0.00 |

**Decision quality** for a trial is defined as `payoff / 100` — a
fraction, adapting the decision-quality-as-fraction-of-optimal-payoff
measure from Fernandes, Walls, Munson, Hullman, and Kay, *"Uncertainty
Displays Using Quantile Dotplots or CDFs Improve Transit Decision-
Making,"* CHI 2018 (DOI 10.1145/3173574.3173718) — see §5 for exactly
how that paper's own metric is adapted here, and why "optimal" collapses
to a constant (100) in this task rather than needing an expectation over
a probability distribution the way it does in theirs.

---

## 2. Design: 8 trials, within-subject, counterbalanced, alternating

**Two conditions.** Baseline (`baseline-interface.html`, D74 — one
figure, no lattice, no uncertainty budget, no election control) and
Lattice (`output-interface.html`, the real disclosure page). Same CSS,
same header, same underlying record for a given case — the single
manipulated variable is whether uncertainty is disclosed at all.

**Four real cases**, chosen deliberately, not arbitrarily:

| Case | Real dispute? | Range | Why chosen |
|---|---|---|---|
| D1 | Yes | ₹469,750.00 – ₹517,618.76 (10.19%) | The flagship case — among the largest real spreads in this project's corpus (C3/C4 nominally match this figure, but only because their own `valuation` block is D1's own borrowed lattice, not case-specific data — see below) |
| C5 | Yes | a real, much smaller spread (₹150, 0.053%) | Tests whether a *small* real range is treated differently from a large one |
| C1 | No | single figure, zero spread | A domestic invoice — genuinely no valuation uncertainty exists |
| C2 | No | single figure, zero spread | A cross-border wire settled same-day — no gap, no uncertainty |

**C3 and C4 are deliberately excluded.** Their `valuation` block is D1's
own borrowed 12-method lattice, not case-specific data —
`node7_disclosure.py`'s own header already says so ("DO NOT RENDER OR
SHOW C3/C4's PAGE AS A DEMO"), and real crypto market data for their
actual dates was never collected. Presenting a borrowed lattice to a
study participant as if it were that case's own real dispute would be
building the study on a fabricated stimulus — excluded on the same
disclosure discipline as everywhere else in this project, not an
oversight.

**Sequence.** Condition alternates strictly every trial. Each of the
four cases appears exactly twice per participant — once under each
condition — separated by four trials, never back-to-back (reducing the
chance a participant simply recalls their own prior answer rather than
re-deciding). Counterbalanced 2×2 across the four participants: starting
condition (Baseline-first vs. Lattice-first) crossed with case-order
rotation, so pooled across all four, no case and no condition is
systematically advantaged by serial position.

| Trial | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| 1 | D1 · Baseline | D1 · Lattice | C5 · Baseline | C5 · Lattice |
| 2 | C5 · Lattice | C5 · Baseline | C1 · Lattice | C1 · Baseline |
| 3 | C1 · Baseline | C1 · Lattice | C2 · Baseline | C2 · Lattice |
| 4 | C2 · Lattice | C2 · Baseline | D1 · Lattice | D1 · Baseline |
| 5 | D1 · Lattice | D1 · Baseline | C5 · Lattice | C5 · Baseline |
| 6 | C5 · Baseline | C5 · Lattice | C1 · Baseline | C1 · Lattice |
| 7 | C1 · Lattice | C1 · Baseline | C2 · Lattice | C2 · Baseline |
| 8 | C2 · Baseline | C2 · Lattice | D1 · Baseline | D1 · Lattice |

Before each trial: the administrator opens the specified file
(`output-interface.html` or `baseline-interface.html`, regenerated for
that trial's case via `python node7_disclosure.py --record
runs/21aug/<case>.json` or `python baseline_interface.py --record
runs/21aug/<case>.json`) and records the participant's filed figure.
**Do not tell the participant which condition they are viewing, and do
not use the words "baseline," "lattice," "condition," or "control" in
front of them** — both interfaces are designed to read as ordinary
product pages (§`baseline_interface.py`'s own docstring), and naming the
manipulation defeats it.

---

## 3. The SURE screener — verbatim, administered after every trial

Verified directly against the primary source, not relayed from memory —
including the full author byline, checked in its own second pass after
an initial draft of this document got it wrong (see `DECISION-D74.md`
for the disclosed correction): **Légaré F, Kearing S, Clay K, Gagnon S,
D'Amours D, Rousseau M, O'Connor A. "Are you SURE? Assessing patient
decisional conflict with a 4-item screening test." *Canadian Family
Physician.* 2010;56(8):e308–e314. PMID 20705870, PMCID PMC2920798.**

Read exactly as published — the acronym is load-bearing (each item's
first letter spells SURE) and the items are deliberately, positively
framed; do not paraphrase, reorder, or adapt the wording, including for
this study's own tax-filing context. Administer immediately after the
participant states their filed figure for a trial, before moving to the
next trial:

1. **(S)** Do you feel SURE about the best choice for you?
2. **(U)** Do you know the benefits and risks of each option?
3. **(R)** Are you clear about which benefits and risks matter most to
   you?
4. **(E)** Do you have enough support and advice to make a choice?

Each answered **yes** or **no** only.

**Scoring**, exactly as published: yes = 1, no = 0. Sum the four items
(range 0–4). **A score of ≤ 3 is a positive result for decisional
conflict.** (Equivalently stated in the original: a score of < 4. Both
describe the identical rule on an integer 0–4 scale — confirmed against
the primary source, not two different rules.)

---

## 4. Two open questions

Asked once, after all 8 trials are complete — not per-trial, to avoid
cueing the participant to the manipulation before they have finished it:

1. **When you decided which figure to file, what made you choose that
   specific number?**
2. **Did seeing — or not seeing — a range of possible figures change
   how confident you felt in the number you chose? Why or why not?**

Record responses verbatim. These are qualitative and exploratory — no
scoring rule is defined for them, and none should be invented after the
fact.

---

## 5. Results template

**Read this before the table below.** n = 4. Four participants are four
independent units of observation, not a sample large enough to estimate
a population effect from. **No inferential claim is made from this
data, and no p-value will be reported anywhere against it** — the same
discipline `results.md`'s own "STATISTICAL LIMITS" section already
applies to this project's six evaluation cases, applied here with more
force, since four is fewer than six. What this table can honestly
support: four real, individually-inspectable case studies of how one
person's filed figure and decisional-conflict score differed, or didn't,
between conditions — reported as exactly that, not aggregated into a
mean that implies a claim about people in general.

**Decision quality**, adapted from Fernandes, Walls, Munson, Hullman,
and Kay, CHI 2018 (§1) — cited precisely: the paper's first author is
Fernandes, with Kay as senior/last author; "Kay et al." is the common
informal short-form for this line of work (the paper's own related-work
section uses the identical shorthand for Kay's separate, earlier 2016
CHI paper), used here with the correct full citation given rather than
silently crediting the wrong author order. Their own metric is
*expected payoff / optimal payoff*, an expectation because their task
(when to arrive for a bus) has a stochastic outcome. This study's task
has no stochastic outcome — a filed figure deterministically produces
one payoff via §1's formula — so *decision quality* here is simply
`payoff / 100`, "optimal" collapsing to the constant 100 achievable by
any figure inside `[lo, hi]`, not an expectation over a distribution.
This simplification is disclosed here, not left for a reader to
discover the metric was changed without saying so.

**The table below is intentionally empty.** Filled in by hand after the
study is actually run — never populated with a plausible-looking number
in its place.

### Per-trial results

| Participant | Trial | Case | Condition | Filed figure (INR) | `[lo, hi]` | Payoff | Decision quality |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

*(32 rows: 4 participants × 8 trials. Delete unused rows only if a
participant is genuinely unable to complete all 8 — note why, do not
silently shorten the table.)*

### SURE screener results

One row per trial per participant, same 32 rows as "Per-trial results"
above — administered immediately after that trial's filed figure (§3).

| Participant | Trial | Case | Condition | S | U | R | E | Score (0–4) | Decisional conflict (≤3)? |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |

### Open questions

| Participant | Q1 response | Q2 response |
|---|---|---|
| | | |
| | | |
| | | |
| | | |

### What may honestly be said once this table is filled in

- Per-participant, per-case comparisons (`this person's decision
  quality under Baseline vs. under Lattice, for the same underlying
  case`) — four such genuine within-subject pairs per case, individually
  reportable.
- Whether SURE scores indicating decisional conflict (≤3) occurred more
  often under one condition than the other, described as counts, not
  rates with confidence intervals — n=4 does not support an interval.
- Direct quotation from the two open questions, which needs no
  statistical justification to report honestly.

### What may not be said

- Any statement of the form "condition X produces better decisions" as
  a general claim.
- Any p-value, confidence interval, or effect size computed across
  participants.
- Any claim that this generalizes beyond these four people and these
  four cases.
