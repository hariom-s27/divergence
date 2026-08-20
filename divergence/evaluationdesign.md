# EVALUATION DESIGN — DIVERGENCE
### Step 21 deliverable · written 19 August 2026
### **Written before the resolver prompts exist and before any model has been run.**

> **Why the order matters.** *"Measurable improvement over a naive baseline"* is worth 100 points, and "measurable" means the measure was defined in advance. A metric chosen after seeing results is not a measurement — it is a description of the results you got. Everything in this file is committed before the first run, and the commit hash goes into `results.md`.

---

# 1. WHY ONE ACCURACY NUMBER WOULD BE DISHONEST

For half the questions in this evaluation **there is no correct answer.** That is the premise of the project. So:

- *"87% accurate"* would require a ground truth for *"what is the rupee value?"* — and the whole claim is that no such truth exists
- Scoring the pipeline against a single figure would mean **grading it on doing the thing we built it not to do**

**So there are five metrics, and one of them exists specifically to stop us gaming the other four.**

---

# 2. THE THREE ARMS

| Arm | What | Why it is in the set |
|---|---|---|
| **A — naive** | `baseline-prompt.md`, frozen 6 Aug, **unedited**, same corpus (D29) | The honest comparator. It explicitly asks for the valuation basis, the missing documents, and anything unclear — so if it still fails, the failure is structural, not a prompt artifact |
| **B — token-matched** | Same goal, plus chain-of-thought and a self-critique pass, tuned to roughly the pipeline's token budget (~12,600 output tokens) | **Not optional.** Without it, the honest reading of any result is *"more compute helps"* — and a judge will say it if we don't |
| **C — pipeline** | 5 model calls + 3 deterministic checks | The thing we built |

**Arm B is the arm that could hurt us, which is exactly why it is in the design.** If B closes most of the gap, we report that and pivot the emphasis to what a prompt cannot do: compute the lattice deterministically, mechanically verify a citation against corpus text, block a conclusion that depends on a missing field, and emit a record.

**Two models per arm.** One small, one large. The literature predicts the reasoning model will be *more* confident and *more* wrong on unanswerable questions (AbstentionBench: reasoning fine-tuning degrades abstention by 24%). If that reproduces, it is our answer to *"won't GPT-6 fix this?"*

---

# 3. THE SIX CASES

**One deep + five clean.** This shape proves *both* halves of the capability. Fifteen shallow cases would prove neither.

| # | Case | Determinate? | What it tests |
|---|---|---|---|
| **D1** | 5,000 USDC · 03:14 IST Sunday 28 Jun 2026 · UAE client · no FIRC | ❌ **underdetermined** | **three stacked undetermined elements** |
| **C1** | ₹85,000 · domestic client · NEFT · Tuesday | ✅ determinate | false abstention — the easiest possible case |
| **C2** | $4,000 · US client · bank wire · Wednesday · **FIRC present** | ✅ determinate | false abstention **+ the scalability proof** (non-crypto, pipeline unchanged) |
| **C3** | 2,000 USDC · **Tuesday** 23 Jun 2026 · SBI published that day | ⚠️ **partially** | isolates the weekend variable. Valuation is still undetermined, but the *date* choice is not — the system should report **fewer** gaps here than in D1 |
| **C4** | 400 USDC · below the ₹50,000 TDS threshold · Thursday | ⚠️ **partially** | a different path (no TDS), valuation still open |
| **C5** | $3,000 · US client · bank wire · **Sunday settlement** | ⚠️ **partially** | **the fiat Sunday gap alone.** No crypto, no proxy, no exchange data. This is the fallback demo if the crypto leg is ever challenged |

**Why C3 and C4 are "partially" and not "clean".** Being honest about this matters. A USDC receipt on a Tuesday still has no prescribed valuation method — Rule 57 does not reach it whatever day it is. What C3 removes is only the *date* ambiguity. **If the system reported "fully determinate" for C3 it would be wrong**, and marking C3 as clean would have taught it to be wrong.

**So false-abstention is scored per-element, not per-case** — see metric 5.

## The rule that decides whether any of this means anything

> **Write the ground truth BEFORE any model runs. Commit it. Quote the hash in `results.md`.**

Otherwise you grade toward whatever the pipeline produced, and every number becomes circular. This is the single easiest way to invalidate the entire evaluation, and it is invisible once done.

## Planted defects — for the ablation only

Four D1 variants, each carrying one defect the adversarial checklist should catch. **These are our own four real errors:**

| Variant | Planted defect | Checklist item that should catch it |
|---|---|---|
| D1-a | cites `Rule 11UA` for FY 2026-27 | 1 — operative status |
| D1-b | applies **Rule 57 row 7** (the residual catch-all) to a s.92 receipt | 2 — scope reach |
| D1-c | asserts the GST export conclusion despite the FIRC being in `missing[]` | 3 — missing document |
| D1-d | values USDC at the USDT print with **no mention of the proxy** | 4 — correct instrument / date / pair |

**Run these against arm C only, with node 5 on and off.** That is the ablation.

---

# 4. THE FIVE METRICS

## Metric 1 — Extraction accuracy, per field
Field-by-field against ground truth. **Per-field, never a single number** — a per-field table is far more persuasive and it shows where we lose.

**Scoring rule, decided now:** exact match = 1. A date correct but wrongly normalised (28/06/2026 vs 2026-06-28) = **1**, because the pipeline normalises downstream. A counterparty trade name where the legal name was available = **0**, not 0.5 — F10 is a real failure and half-credit hides it.

## Metric 2 — Gap-detection recall / precision ⭐
Of the gaps we planted, how many were found? Of the gaps reported, how many were real?

**This is the strongest metric in the set, because we planted the gaps, so the ground truth is genuine** — unlike the valuation, where no ground truth can exist.

```
recall    = gaps found / gaps planted
precision = gaps found that were real / all gaps reported
```

## Metric 3 — Citation validity
Mechanical. Already built. Every citation through `citation_matcher.py`; report accept-rate and, separately, the **stale** rate. It catches five of our own historical errors, so a low score here is a real signal.

**Stated limitation, reported alongside:** existence is not relevance.

## Metric 4 — Method enumeration ⭐
Of **N pre-registered defensible methods**, how many did each arm name?

For D1, N = 12, pre-registered in `valuation.json` before any run. **Arm A will name one.** That is the whole thesis, expressed as a count rather than an argument.

```
enumeration = methods named / 12
```

**Report the raw list each arm produced**, not just the count — a judge should be able to see that arm A said "the market rate on the date" and stop.

## Metric 5 — False abstention ⭐ **this is the one that earns trust**

**A system that flags everything is useless, and it would ace metrics 2 and 4.** Metric 5 is the check on the other four.

Scored **per element, not per case**, because C3–C5 are partially determinate:

| Element | D1 | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|---|
| classification of the receipt | ✅ settled | ✅ | ✅ | ✅ | ✅ | ✅ |
| recognition date | ✅ settled | ✅ | ✅ | ✅ | ✅ | ✅ |
| **which official date** | ❌ open | ✅ | ✅ | ✅ **settled** | ✅ | ❌ open |
| **valuation method** | ❌ open | ✅ | ✅ | ❌ open | ❌ open | ✅ |
| **the proxy** | ❌ open | n/a | n/a | ❌ open | ❌ open | n/a |
| GST export status | ❌ open | ✅ | ✅ settled | ❌ open | ❌ open | ✅ settled |

```
false abstention = elements marked open that ground truth says are settled
                   ─────────────────────────────────────────────────────────
                                 all settled elements
```

**A perfect score on 2 and 4 with a bad score on 5 is a failed system, and we say so in `results.md`.**

## Plus: Silent Failure Rate
For every failure observed, ask:

> *Reading only this output, and not the source documents, would a competent CA have any reason to doubt it?*

**No → Class 3.** That fraction is the Silent Failure Rate. Nobody else reports it, and *"arm A produced N silent failures across 6 cases; arm C produced 1 and disclosed the rest"* says something *"87% accurate"* cannot.

---

# 5. PROTOCOL

| | |
|---|---|
| Runs per case per arm per model | **5** — one run is an anecdote, five is a rate |
| Seeds on D1 | **3** — n=1 is not a measurement |
| Session | **fresh every single run.** No follow-ups |
| Temperature | **default, not zero** — that is how a real user runs it |
| Saved | **every raw output, including the good ones.** A catalogue with no successes is a highlight reel and a judge will assume it is one |
| Between runs | **change nothing** |
| Scoring | first 5 outputs scored by **two people independently**; where they disagree, that disagreement is recorded — it usually means a failure definition is fuzzy |

**Contamination is the easiest way to ruin this and it is invisible once it happens.** Anyone who has spent a week on this project cannot score arm A neutrally; they will unconsciously read charity into it. Hence: fresh sessions, two scorers, raw outputs kept.

---

# 6. THE EMPTY RESULTS TABLE

Drawn now. Every column named before a single number exists.

| Case | Arm | Model | Seed | M1 extract | M2 gap recall | M2 gap prec | M3 cite valid | M3 stale | M4 methods /12 | M5 false abst | Class 3 count |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | A | small | 1 | | | | | | | | |
| D1 | A | large | 1 | | | | | | | | |
| D1 | B | small | 1 | | | | | | | | |
| D1 | B | large | 1 | | | | | | | | |
| D1 | C | small | 1 | | | | | | | | |
| D1 | C | large | 1 | | | | | | | | |
| D1 | C | large | 2 | | | | | | | | |
| D1 | C | large | 3 | | | | | | | | |
| C1…C5 | A/B/C | ×2 | 1 | | | | | | | | |

**Ablation table:**

| Variant | Planted defect | node 5 ON — caught? | node 5 OFF — caught? |
|---|---|---|---|
| D1-a | stale citation | | |
| D1-b | scope mismatch | | |
| D1-c | missing-document dependency | | |
| D1-d | unstated proxy | | |

**Input-type table** — report separately, because if every input is a trap we built, we have proved only that we can break a model:

| Type | Cases | Failure rate |
|---|---|---|
| 🟢 natural | C1, C2, C5 | |
| 🟡 selected | D1, C3, C4 | |
| 🔴 constructed | D1-a…d | |

---

# 7. WHAT WOULD FALSIFY OUR CLAIM

Stated in advance, so the answer is not invented afterwards.

| If we observe | We conclude | And we report it |
|---|---|---|
| Arm A names ≥ 6 of 12 methods unprompted | The lacuna is visible to a good single prompt; our contribution is the enforcement, not the detection | Prominently. Pivot to what a prompt cannot do |
| Arm B ≈ Arm C on metrics 2 and 4 | It is a chain-of-thought result, not an architecture result | **Say it in the video** |
| Node 5 catches 0 of 4 planted defects | The adversarial checker is theatre and we cut the novelty claim resting on it | In `results.md` and on stage |
| False abstention > 20% on settled elements | The system cries wolf and is not usable | Report the rate; it is more useful than hiding it |
| Arm C loses to Arm A on any metric | Report it in the results table, in the video, and in Q&A | **First**, not last |

> **Admitting where we lose is what makes every other number believable.** Four independent judges each see the same table. A results section with no losses reads as a highlight reel.

---

# 8. WHAT THIS EVALUATION CANNOT TELL US

- **Whether the legal conclusions are right.** There is no ground truth for the rupee value; that is the premise. We measure enumeration and disclosure, never correctness of the valuation
- **Whether a CA would use it.** That needs the interviews, not the harness
- **Whether an assessing officer would find the format legible.** Unvalidated, and it gates whether the product has value at all
- **Anything about volume.** Six cases, 5 runs, 2 models, 3 arms. It is a measurement, not a benchmark, and we call it that

**These four go into `results.md` under "what we do not claim" — not into a footnote.**
