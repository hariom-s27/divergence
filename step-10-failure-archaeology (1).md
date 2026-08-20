# STEP 10 — FAILURE ARCHAEOLOGY
### Deliverable · 6 August 2026
*The reframe that matters · borrowed from engineering safety · the protocol · pre-registered predictions*

---

# AN HONESTY NOTE FIRST

**I cannot run these experiments.** I have no live model access here, and inventing "observed failures" would poison the most important evidence in your submission — the same line we drew on interviews.

So this document contains the **protocol, the taxonomy, the scoring method, and pre-registered predictions.** The `failure-catalogue.md` gets filled by you, with raw outputs pasted in as proof.

That division is actually the right one. **The design of the experiment is where the thinking lives; running it is mechanical.** And a protocol written before you see any results is far more credible than a catalogue assembled after the fact to justify a diagram you already drew.

---

# PART 1 — FIRST PRINCIPLES: WHAT IS A "FAILURE" HERE?

The obvious answer is "the model got it wrong." That answer will produce a weak catalogue.

**Wrong compared to what?** For half our questions there is no correct answer — that is the entire premise. So "wrong" cannot be the organising idea.

## The better definition

> **A failure is any output that would lead a competent user to a worse decision than they would have made without it.**

This is a decision-theoretic definition, not an accuracy one, and it changes what you look for:

- A confidently wrong rupee number is a failure ✅
- A *correct* rupee number presented as settled when it is contestable is **also a failure**, because the user now believes something they should not
- Garbled JSON is barely a failure at all — the user notices instantly and loses nothing

That last point is the seed of the whole step.

---

# PART 2 — THE REFRAME: SORT BY DETECTABILITY, NOT BY TYPE ⭐

The roadmap's failure list — *numeric confusion, date errors, entity confusion, fabricated citations, silent rate selection* — sorts failures by **what went wrong.** That is the natural way and it is the wrong way for us.

**Sort by whether the user can tell.**

| Class | Definition | Example | Real cost |
|---|---|---|---|
| **Class 1 — Loud** | User notices immediately | Malformed output, obvious nonsense, currency shown as dollars when it should be rupees | ⚪ Near zero. Annoying, harmless |
| **Class 2 — Checkable** | Wrong, but verifiable with effort | Fabricated section number, wrong date, misread invoice figure | 🟡 Real, but a careful CA catches it |
| **Class 3 — Silent** | **Cannot be detected by checking, because there is nothing to check against** | A confident rupee figure where no method is prescribed; no mention that a choice was made; no mention that a required document does not exist | 🔴 **The whole reason this project exists** |

## Why this reframe is the most valuable thing in Step 10

Three reasons, and each one is worth points.

**1. It defines your product's territory precisely.** Everyone builds tools for Class 2 — fact-checkers, citation verifiers, hallucination detectors. **Almost nobody builds for Class 3, because Class 3 has no ground truth to check against.** That is exactly why it is unaddressed, and exactly why you can address it.

**2. It gives you a metric no other team will have.** Not "accuracy" but:

> **Silent Failure Rate — the fraction of failures a competent CA would *not* have caught.**

A team that reports "our system is 87% accurate" is one of many. A team that reports *"the single prompt produced 11 silent failures in 30 cases; ours produced 1, and disclosed the other 10 as open questions"* is saying something nobody else is saying.

**3. It rescues you if the baseline performs well.** This was a real risk — a good single prompt might match you on extraction. But it **cannot** win on Class 3, because Class 3 failures are structural, not accuracy-related. A single prompt has no mechanism to say "a choice was made here." **So the comparison holds even if the baseline is excellent.**

That is a genuinely important robustness property of your evaluation design, and it came from asking "what is a failure?" instead of assuming.

---

# PART 3 — BORROWED PATTERN: FMEA

Engineering has done this for seventy years. **Failure Mode and Effects Analysis** — used in aerospace, automotive and medical devices — scores every failure mode on three dimensions:

**Risk Priority Number = Severity × Occurrence × Detection**

And crucially: **"Detection" is scored so that a *harder-to-detect* failure scores *higher* risk.** A failure that is severe, frequent and invisible is the top priority — above one that is catastrophic but obvious.

**FMEA independently arrived at our reframe.** That is strong validation, and it gives us a standard framework rather than an invented one — the fifth borrowed professional ancestor after IFRS 13, metrology, auditing, and FIN 48.

## Our scoring

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| **Severity** | Cosmetic | Wrong figure, correctable | Loses a statutory defence under s.439(8) |
| **Occurrence** | <10% of runs | 10–40% | >40% |
| **Detection** | User sees it instantly | Catchable with effort | **No way to know** |

RPN ranges 1–125. Anything scoring **Detection = 5** goes to the top regardless of the rest.

**This table is your architecture.** The highest-RPN failures determine which nodes exist. Not a diagram — a risk register.

---

# PART 4 — PRE-REGISTERED PREDICTIONS

Written before running anything, so the *surprise* is the finding. Fill the last two columns with real numbers.

| # | Failure mode | Class | S | O | D | RPN | Predicted rate | **Observed** | **Node that catches it** |
|---|---|---|---|---|---|---|---|---|---|
| **F1** | **Silent rate selection** — gives one rupee figure, never says a choice was made | 🔴 3 | 5 | 5 | 5 | **125** | ~100% | | **Node 4** — dual valuation |
| **F2** | **Silent completeness** — answers with no mention that FIRC/counterparty is absent | 🔴 3 | 5 | 5 | 5 | **125** | ~90% | | **Node 3** — gap detector |
| **F3** | **Stale citation** — cites Rule 11UA / s.270A(6), retired 1 April 2026 | 🔴 3 | 4 | 5 | 5 | **100** | ~95% | **Corpus versioning** |
| **F4** | **False settledness** — states the FEMA position as settled law rather than inference | 🔴 3 | 5 | 3 | 5 | **75** | ~70% | **Node 5c** — certainty label |
| **F5** | **Fabricated citation** — a plausible section number that does not exist | 🟡 2 | 5 | 3 | 3 | 45 | ~20% | **Citation matcher** |
| **F6** | **Regime collapse** — answers income tax only, ignores GST and FEMA | 🔴 3 | 4 | 3 | 5 | **60** | ~60% | **Nodes 5a/b/c** — parallel |
| **F7** | **Single-event tax** — treats it as one 30% event, missing the two-stage structure | 🟡 2 | 5 | 3 | 3 | 45 | ~50% | **Node 5a** |
| **F8** | Numeric / decimal / currency confusion | 🟡 2 | 3 | 3 | 3 | 27 | ~25% | **Node 2** — schema |
| **F9** | Date normalisation error | 🟡 2 | 3 | 3 | 3 | 27 | ~20% | **Node 2** |
| **F10** | Entity confusion — trade name vs legal name vs handle | 🟡 2 | 3 | 3 | 3 | 27 | ~40% | **Node 2** entity resolution |
| **F11** | **Weekend invention** — invents a rate for a day when none was published | 🔴 3 | 4 | 3 | 5 | **60** | ~80% | **Node 4** `no_rate_published` |
| **F12** | Extraction failure on a bad photo | ⚪ 1 | 2 | 3 | 1 | 6 | ~30% | Node 1, and it is *visible* |
| **F13** | Malformed / unparseable output | ⚪ 1 | 1 | 1 | 1 | 1 | ~5% | Schema enforcement |

## What the table already tells you, before a single run

**The top five failures by RPN are all Class 3.** F1, F2, F3, F4, F6, F11 — six of the top seven are invisible to the user.

**And look at what F12 and F13 score.** A blurry photo and broken JSON — the failures people naturally worry about — are near the bottom, because **the user can see them.**

> **Your architecture is not designed against the failures that are most common. It is designed against the failures that are most invisible.**

That single sentence is worth putting in the documentation and saying out loud in Q&A. It explains, in one line, why seven nodes and not three.

---

# PART 5 — THE PROTOCOL

## Inputs — 6 cases, deliberately mixed

**Label each one, and report rates separately.** Otherwise you are constructing failures, not observing them.

| # | Input | Type |
|---|---|---|
| A1 | Clean invoice PDF + clean transaction record | 🟢 Natural |
| A2 | Phone photo at an angle, slightly blurred | 🟢 Natural |
| A3 | WhatsApp screenshot with the counterparty as a handle only | 🟢 Natural |
| B1 | Payment settling 3 a.m. Sunday | 🟡 Selected |
| B2 | Payment dated 28–29 June 2026 | 🟡 Selected |
| B3 | Question whose correct answer changed on 1 April 2026 | 🔴 Constructed |

**This matters for integrity.** If all six were constructed traps you would be demonstrating that you can break a model, which nobody doubts. Reporting natural-input failure rates separately is what makes the number believable.

## Runs — five per input, not one

**LLMs are stochastic. One run is an anecdote; five is a rate.** 6 inputs × 5 runs = 30 observations, per model. Run on both ChatGPT and Gemini.

Record every run, including successes. **A failure catalogue that contains no successes is not a catalogue, it is a highlight reel** — and a judge will assume that.

## Scoring — two people, independently

Each output scored against pre-written ground truth by two people separately, then compared. Where you disagree, that disagreement is itself a finding worth recording: it usually means your failure definition is fuzzy.

## The killer question, asked per failure

> **"Would a competent CA, reading only this output and not the source documents, have any reason to doubt it?"**

- **No** → Class 3, and this is your product's territory
- Yes, with effort → Class 2
- Yes, immediately → Class 1

---

# PART 6 — THE BASELINE PROMPT

Write this **now**, use it for archaeology, and **freeze it**. This is the same prompt that becomes your Step 16 baseline — so writing it before you have built anything means it cannot be unconsciously weakened later.

```
You are an expert Indian chartered accountant specialising in cross-border
taxation and virtual digital assets.

Attached is an invoice and a record of a payment received in USDC by an
Indian freelancer from a foreign client.

Provide a complete analysis covering:
1. The INR value of the receipt at the time it was received
2. Income tax treatment, with the relevant sections
3. GST treatment, with the relevant provisions
4. Any FEMA implications
5. Any documents that would be required
6. Anything the taxpayer should be aware of

Be thorough, accurate and cite the specific provisions you rely on.
```

**This is a genuinely good prompt.** It names the expertise, gives full context, asks for all three regimes, requests citations, and even invites the model to flag concerns in point 6.

**That last point is deliberate, and it is the fair test.** We explicitly invited the model to raise anything the taxpayer should know. If it *still* does not say "the law prescribes no method here and I chose one," the failure is structural rather than a prompt-quality artifact.

**Publish this prompt in full in the documentation.** It is the strongest possible answer to *"was your baseline a straw man?"*

---

# PART 7 — OUR OWN FAILURES ARE DATA ⭐

Include them. Twice now, this project has made an error that is precisely the failure type we are cataloguing.

| Our failure | Class | Why it happened |
|---|---|---|
| Cited Rule 11UA after it became Rule 57 | 🔴 3 | Every source agreed, because they were reading each other |
| Cited s.270A(6) after it became s.439(8) | 🔴 3 | Same cause, three days later |

**Both are F3 — stale citation. Both were invisible. Both survived four adversarial research passes.**

**Put these in the catalogue with the raw evidence.** Three things follow:

1. It **proves F3 is real** without needing to construct a test — you have naturally occurring instances
2. It shows the failure affects **careful, motivated humans**, not just models — which makes the case broader and more sympathetic
3. It is honest in a way judges notice. *"Here is our own failure log"* is unusual

**And it makes B3 — the staleness test — the most defensible case in the set**, because you are not constructing a trap. You are asking the model the exact question you got wrong yourselves.

---

# PART 8 — TRAPS IN THIS STEP

| Trap | Why it bites | Avoid by |
|---|---|---|
| **Running once and calling it evidence** | Stochastic output; you would report noise | 5 runs minimum |
| **Only recording failures** | A highlight reel, and judges assume it | Record every run, successes included |
| **All inputs constructed to break it** | Proves nothing except that you can break a model | Label natural vs selected vs constructed; report separately |
| **Sorting by failure type** | Hides the Class 3 insight, which is the whole point | Sort by detectability |
| **Weakening the baseline** | Destroys the entire comparison's value | Write and freeze it now; publish it |
| **Assuming the model always fails** | It won't, and pretending otherwise is worse than losing | Report where it wins, prominently |
| **Deriving nodes from the diagram** | Backwards. The diagram should come from the evidence | Fill the "node that catches it" column *after* observing |

---

# PART 9 — WHAT CHANGES

| # | Change | Why |
|---|---|---|
| **C36** | **Sort the failure catalogue by detectability, not type** | Class 3 is the product's territory; type-sorting hides it |
| **C37** | **Adopt FMEA scoring (S × O × D)** with Detection weighted so invisible = higher risk | A seventy-year-old engineering standard that independently reached our conclusion |
| **C38** | **Add Silent Failure Rate as a headline metric** | Nobody else will report this. It is more meaningful than accuracy |
| **C39** | 5 runs per input minimum; record successes too | Rates, not anecdotes |
| **C40** | Label inputs natural / selected / constructed; report rates separately | Integrity — otherwise we constructed the finding |
| **C41** | **Write and freeze the baseline prompt today**, publish it in full | Prevents unconscious weakening; answers the straw-man charge |
| **C42** | **Include our own two stale-citation errors in the catalogue** | Naturally occurring proof of F3, and honest |
| **C43** | Node justification comes from RPN, not from the diagram | *"Our architecture is designed against the most invisible failures, not the most common"* |

---

# PART 10 — NEW QUESTIONS

| # | Question | Why it matters |
|---|---|---|
| N1 | Does a stronger reasoning model produce *fewer* Class 3 failures, or the same number more convincingly? | **If more convincing, our case gets stronger as models improve.** Test both a fast and a reasoning model |
| N2 | Does explicitly asking "what are you uncertain about?" fix F1? | If yes, the fix is a prompt not a pipeline — and we must say so honestly |
| N3 | Do the two models fail the *same* way or differently? | If differently, cross-model disagreement is itself a cheap uncertainty signal |
| N4 | What is a CA's actual detection rate on Class 2 failures? | Turns "catchable with effort" from assumption into measurement — one interview question |

**N1 and N2 are the two that could hurt us, which is exactly why they must be run first.**

If a single prompt with one extra sentence — *"tell me what you were uncertain about"* — closes most of F1, then a large part of our argument is a prompt-engineering result rather than an architecture result. **We need to know that before a judge asks it.**

And if it does happen: the honest answer is still good. *"One extra sentence closes 40% of it. Our pipeline closes 90%, quantifies the gap in rupees, and produces a record. But we'll tell you the cheap fix works partly, because pretending otherwise would be exactly the behaviour we built this to prevent."*

**That answer would score better than a suspicious silence.**

---

# THE ONE-LINE SUMMARY

**Do not catalogue failures by what went wrong. Catalogue them by whether the user could tell — because the failures nobody can see are the only ones worth building a system against.**
