# THE BASELINE PROMPT — FROZEN
### Step 16 · 6 August 2026
**Written before any pipeline exists. Frozen on creation. Published in full.**

---

# WHY THIS IS FROZEN

Your Technical Execution score — 100 points across four judges — rests on *"measurable improvement over a naive baseline."* That measurement is worth nothing if the baseline is weak.

**And it will be weak if you write it later.** Not through dishonesty — through ordinary human bias. After a week of building a seven-stage pipeline, nobody writes a genuinely strong single prompt. You unconsciously leave out the instruction that would have helped it. A sharp judge senses this, asks to see the baseline, and your whole comparison evaporates.

**So it is written today, on 6 August, before a single line of pipeline code exists.** It cannot be weakened in hindsight because there is nothing yet to weaken it in favour of.

## The rules, from here to submission

1. **Do not edit this prompt.** Not one word, not to "make it fairer," not to fix a typo
2. **Publish it in full** in the documentation
3. **Report every case where it beats the pipeline**, prominently
4. If you must change it, **keep the old version and report both**

---

# THE PROMPT

```
You are an expert Indian chartered accountant specialising in cross-border
taxation and virtual digital assets. You have twenty years of practice and
your clients rely on you to be both accurate and candid.

Attached is an invoice, and a record of a payment received in USDC by an
Indian freelancer from a foreign client for professional services.

Provide a complete analysis covering:

1. The INR value of the receipt at the time it was received, and the basis
   on which you arrived at that figure.
2. Income tax treatment, citing the specific provisions you rely on.
3. GST treatment, citing the specific provisions you rely on.
4. Any FEMA implications, citing the specific provisions you rely on.
5. Any documents that would be required, and any that appear to be missing.
6. Anything else the taxpayer should be aware of, including anything you
   are uncertain about or where the law is unclear.

Be thorough and accurate. Where you cite a provision, give the exact
section or rule number. Where you make an assumption, state it.
```

---

# WHY THIS IS A GOOD PROMPT, NOT A STRAW MAN

Every line is there to make it harder to beat. Read them individually:

| Line | Why it's there |
|---|---|
| *"expert Indian chartered accountant… twenty years"* | Full expert role priming |
| *"accurate and candid"* | Explicitly invites honesty, not just correctness |
| **"and the basis on which you arrived at that figure"** | **Directly asks it to disclose its valuation method.** The exact thing we say it won't do |
| *"citing the specific provisions"* × 3 | Demands citations in all three regimes |
| **"and any that appear to be missing"** | **Directly asks for absence detection.** Our Node 2's whole job |
| **"including anything you are uncertain about or where the law is unclear"** | **Directly invites it to flag the lacuna** |
| *"Where you make an assumption, state it"* | Asks for exactly the disclosure we build a pipeline to produce |

## This is the fairness argument, and it is strong

We are not asking a naive question and then declaring victory. **We are explicitly asking the model to do the four things our pipeline exists to do** — disclose its method, find what's missing, flag where the law is unclear, and state its assumptions.

**If it still doesn't, the failure is structural, not a prompt-quality artifact.** That is the entire point, and this prompt is what proves it.

## Say this in Q&A, word for word

> *"We wrote the baseline on day three, before the pipeline existed, and we've published it in full. It asks the model, in plain terms, to state the basis for its valuation, to identify missing documents, and to flag anything where the law is unclear. It's a good prompt. If it still gives one confident number without mentioning it chose, that's not because we asked badly."*

---

# WHAT WE PREDICT — REGISTERED IN ADVANCE

Written before running it, so the surprise is the finding.

| # | Prediction | Confidence |
|---|---|---|
| P1 | Gives **one** INR figure, not a range | High |
| P2 | Names a rate source vaguely — *"the market rate on the date"* — without naming a venue | High |
| P3 | **Does not mention that no method is prescribed**, despite line 6 asking | **Medium-high — this is the key test** |
| P4 | Cites 115BBH and 194S under the **1961** numbering, without noting the tax-year question | High |
| P5 | Invents or implies a rate for 28 June, a day when SBI published nothing | High |
| P6 | Mentions the missing FIRC — line 5 asks directly | Medium |
| P7 | States FEMA as settled rather than as an inference | Medium-high |
| P8 | Treats it as one 30% event, missing the two-stage structure | Medium |
| P9 | Says something hedging like *"consult a professional"* while still giving a definite number | High |

**P3 is the experiment.** Everything else is supporting detail.

**If P3 is wrong** — if the model, when asked plainly, does say *"there is no prescribed method and I have chosen one"* — then a large part of our argument is a prompt-engineering result. **We report that honestly and pivot the emphasis to the things a prompt cannot do**: computing both figures, decomposing the gap, mechanically verifying citations against corpus text, and producing a record.

Published work already tells us roughly what to expect — a carefully crafted prompt *boosts* abstention but does not resolve the underlying inability. **So expect partial success, and say so before anyone asks.**

---

# HOW TO RUN IT

- **Five runs per input.** One run is an anecdote; five is a rate
- **Both models**, ChatGPT and Gemini
- **Temperature default**, not zero — that is how a real user would use it
- **Save every raw output**, including the good ones
- **Change nothing between runs**

Then score against the same ground truth as the pipeline, on the same fields.

---

# THE ONE THING THAT WOULD RUIN THIS

**Editing it after seeing the results.**

If you run it and it does better than expected, the pull to "fix" the prompt will be strong and will feel like fairness. It isn't. **A baseline you adjusted after seeing its score is not a baseline — it's a target you moved.**

Freeze it. Publish it. Let it win where it wins.
