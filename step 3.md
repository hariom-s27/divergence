# PROBLEM STATEMENT — DIVERGENCE
### Step 3 deliverable · Final · 4 August 2026

---

# PART 1 — THE DELIBERATION

*Five perspectives stress-testing the draft. Read this before the final statements — the reasoning matters more than the wording.*

---

### The draft we started from

> *"When you ask an AI about tax or law, it gives an answer. It sounds confident. But sometimes the law itself has no answer — the rule was never written, two official methods disagree, or the required document does not exist. In those cases a confident answer is worse than no answer, because you cannot tell it apart from a real one. We built a workflow that finds those situations and says so."*

---

### 🧓 VOICE 1 — The Grandmother (no technical background)

*"I followed you until 'the law itself has no answer.' What does that mean? Laws are written down. How can there not be an answer?"*

**This is the most important objection in the whole document.** The idea of *legal undecidability* is not intuitive to anyone outside law or tax. Most people assume the rule exists somewhere and the difficulty is finding it.

The fix is not a better definition — it is a concrete example, immediately. *"There is no official rule for what a dollar was worth in rupees at 3 a.m. on a Sunday, because the government only publishes one rate a day, on weekdays."* Now she understands, because she can picture it.

**Verdict: the abstraction must never travel alone. It needs its example attached.**

---

### 🔪 VOICE 2 — The Hostile Judge

*"Isn't this just a tax calculator with extra steps? And isn't 'AI is sometimes wrong' the most obvious observation in the world?"*

Both land. The second is worse than the first.

"AI hallucinates" is not a novel problem statement in 2026 — every judge has heard it a hundred times. If your pitch reduces to that, you score middling on Innovation and you deserve to.

**So the statement must draw a distinction sharp enough that it is clearly not the tired hallucination point.** Here is that distinction, and it turned out to be the best thing to come out of this exercise:

> **An AI can say "I don't know." It cannot say "nobody knows."**

Those are different failures. The first is uncertainty about the model's own knowledge — models can sometimes express it, and a lot of research targets it. The second is uncertainty *in the world*: the answer does not exist, for anyone, because the rule was never written. A model has no way to represent that, so it reaches for the nearest plausible answer and delivers it in the same confident register as a settled fact.

That is not hallucination. Hallucination is getting a knowable thing wrong. **This is fabricating an answer to a question that has none — and it is undetectable precisely because there is no correct answer to check against.**

**Verdict: lead with the "I don't know / nobody knows" distinction. It is the intellectual core.**

---

### 👩‍💼 VOICE 3 — The Chartered Accountant

*"Fine, but I already know the law is unclear here. That is my job. What do you give me that I don't have?"*

Fair, and it exposes something the draft got wrong. The CA is not surprised by ambiguity. What she lacks is **coverage** — she cannot check every transaction, and she does not know which of her client's forty receipts contain a silently chosen number until an assessing officer picks one out.

So the value is not "we reveal that the law is unclear." It is: **we find every place it is unclear, mark it, and show what the alternatives cost — before someone else finds it for you.**

*"Also — if your tool says 'unclear' on everything, it is useless. How often does it abstain?"*

That question needs an answer from the evaluation data, not from a pitch. Add it to Step 21: **report the abstention rate.** A system that abstains on 90% of cases is noise.

**Verdict: reframe the value from revelation to coverage. And measure the abstention rate.**

---

### 🛠 VOICE 4 — The Engineer

*"'A workflow that finds those situations and says so' — that is a description of an outcome, not a system. What actually does the finding?"*

Correct. The closing sentence is passive and vague, and an engineer-judge will notice. It should name the mechanism at least at the level of a shape: the system resolves the question more than one way, and where the answers diverge it reports the divergence rather than picking.

*"Second thing. Is this problem AI-specific? A human accountant also silently picks one method."*

Genuinely good question and worth answering honestly: **yes, humans do this too — but a human writes their assumption in a working paper, and a client can question a person.** The AI's version arrives with no working paper and in a register that discourages questioning. Scale and unauditability are what make it different, not novelty of the error.

**Verdict: name the mechanism in the closing line. Prepare the human-comparison answer for Q&A.**

---

### 🎤 VOICE 5 — The Storyteller

*"Nobody remembers a definition. They remember a person and a number."*

The draft is all concept and no human being. The pitch needs a face in the first ten seconds and a figure that stings.

**The figure exists, and it is very good.** On 28–29 June 2026, USDT on Indian exchanges traded at ₹102.88 while the interbank USD/INR rate sat at ₹94.65. On a single $5,000 invoice:

| Valuation method | Declared income |
|---|---|
| Indian exchange price | ₹5,14,400 |
| USD × interbank rate | ₹4,73,250 |
| **Difference** | **₹41,150** |

**Both are defensible. No rule says which one is right. One invoice, ₹41,000 apart.**

That is the single strongest fact in the entire project. It is concrete, computed, checkable, and it makes an abstract idea physical in about four seconds.

**Verdict: open with a person, land the ₹41,000 within thirty seconds.**

---

## What changed as a result

| # | Change | Driven by |
|---|---|---|
| 1 | Lead with **"I don't know" vs "nobody knows"** | Voice 2 — separates us from the tired hallucination point |
| 2 | Attach a concrete example to the abstraction, always | Voice 1 — undecidability isn't intuitive |
| 3 | Value is **coverage**, not revelation | Voice 3 — CAs already know the law is unclear |
| 4 | Name the mechanism, not just the outcome | Voice 4 |
| 5 | Open with a person; land ₹41,150 fast | Voice 5 |
| 6 | **New action:** measure and report the abstention rate | Voice 3 |
| 7 | **New Q&A answer needed:** humans do this too — why is AI different? | Voice 4 |

---

# PART 2 — THE FINAL STATEMENTS

---

## THE ONE-LINER

> ### An AI can say "I don't know." It cannot say "nobody knows." We built the workflow that can.

**Six-word version:** *AI invents answers the law lacks.*

**Alternates, if the room is wrong for the main one:**
- *"When the law has no answer, AI makes one up — and you can't tell."*
- *"We built an AI workflow whose job is to prove a question has no settled answer."*

---

## THE 30-SECOND VERSION

> An Indian freelancer gets paid $5,000 by a US client. To file her taxes she needs one number: what that was worth in rupees at the moment it arrived.
>
> There is no official rule for that number. India publishes one exchange rate a day, on weekdays only. Her payment landed on a Sunday.
>
> Ask any AI and it will give her a figure — confidently, with no mention that it chose one method over another. On 28–29 June, the two defensible methods were ₹41,000 apart on an invoice that size.
>
> **An AI can say "I don't know." It cannot say "nobody knows."** We built a workflow that resolves the question several ways, and where the answers diverge, reports the divergence instead of picking one.

*(~120 words · roughly 35 seconds spoken · trim the last sentence if you need exactly 30)*

---

## THE 3-MINUTE VERSION

**[0:00–0:25] The person**

An Indian freelancer invoices a US client for $5,000 and is paid in a digital dollar. It arrives in seconds. Eleven months later her chartered accountant asks a simple question: what was that worth in rupees at the moment it landed?

She does not know. And it turns out neither does the law.

**[0:25–0:55] The gap**

There is no prescribed method in Indian tax law for valuing a digital asset in rupees at a point in time. The rule that covers property, jewellery and shares was never extended to cover this. The one official exchange rate is published once a day, on weekdays, from a random five-minute window late in the morning. Her payment settled at three in the morning on a Sunday, when no official rate exists at all.

So there are two defensible answers. Use the Indian market price, or use the dollar rate. On 28–29 June 2026 those two were 8.5% apart — ₹41,150 on an invoice this size. Both defensible. No rule says which.

**[0:55–1:25] What AI does with that**

Ask ChatGPT or Gemini and you get a number. Confident. Fluent. No mention that a choice was made, no mention that the law is silent, no mention that the document proving the payment came from abroad does not exist for this route.

This is not the familiar hallucination problem. Hallucination is getting a knowable thing wrong. This is different and worse: **fabricating an answer to a question that has none.** You cannot detect it by checking, because there is nothing to check against.

An AI can say "I don't know." It has no way to say "nobody knows."

**[1:25–2:10] What we built**

A seven-step workflow that refuses to collapse an open question into a single answer.

It reads the messy inputs — a photographed invoice, a payment record. Before it reasons about anything, it establishes what is **missing**, and passes that forward as a hard constraint, so no conclusion can rest on a document that does not exist. It values the payment under both methods and reports the gap. It resolves the payment under three separate regimes, and each conclusion must carry the exact provision it rests on — mechanically checked against the statutory text, so a fabricated citation is rejected rather than believed. Then a final step exists only to attack everything the earlier steps concluded. Anything it successfully attacks is downgraded and carries the attack into the output.

The report opens with what is missing. Then the range. A single confident number, never.

**[2:10–2:40] Why it matters and how we know it works**

A chartered accountant already knows the law is unclear here. What she cannot do is check every one of her client's transactions. We find every place the ambiguity is hiding, mark it, and show what the alternatives cost — before an assessing officer finds it first.

We tested this against a single well-written prompt across 30 cases, scored field by field. We published that prompt in full, and we report the cases where it beat us.

**[2:40–3:00] What we do not claim**

This is not tax advice. It does not make anything compliant. It is not a legal certificate. Where the law prescribes no method, we do not invent one — that is the entire point.

The rupee case is our proof, not our scope. The same workflow runs unchanged on an ordinary cross-border payment, and the underlying problem — AI inventing answers the law does not have — exists in medicine, insurance, immigration and building regulation.

---

# PART 3 — DEFENCES

## "Isn't this just a tax calculator?"
> A calculator gives you a number. We tell you when the law doesn't have one — and show you the two different numbers you could each defend.

## "Isn't 'AI is sometimes wrong' obvious?"
> Hallucination is getting a knowable thing wrong. This is fabricating an answer to a question that has none. You can fact-check the first. There is nothing to check the second against.

## "Humans do this too."
> They do. But a human writes their assumption in a working paper, and you can question a person. The AI's version arrives with no working paper, in a register that discourages questioning, at a scale no one audits.

## "How many people actually have this problem?"
> The crypto segment isn't measurable from public data and we won't pretend otherwise. But it's our case study, not our scope — the underlying failure appears anywhere AI meets a regulated domain. And the enforcement is real: CBDT issued 44,057 communications for under-reporting in this exact area.

## "Does saying 'it's unclear' actually help?"
> Only if it's rare and specific. That's why we report our abstention rate — a system that says "unclear" about everything is noise. We flag the specific places, with the specific provision, and the specific rupee cost of the disagreement.

## "Why not just pick the conservative number?"
> Because the conservative choice differs by regime. The higher valuation raises this year's income tax but also raises your cost basis, lowering tax later. There is no single safe direction — which is exactly why the choice has to be visible rather than silent.

---

# PART 4 — WORDS WE NEVER USE

| ❌ Never | ✅ Instead |
|---|---|
| "Makes your payments compliant" | "An evidence and disclosure layer. It does not make any flow compliant." |
| "You owe ₹X" | "Under method A it is ₹X, under method B ₹Y. The law does not choose." |
| "Receiving crypto is illegal in India" | "Very likely non-compliant **by inference** from FEMA s.2(n) read with ss.7–8 — not by explicit prohibition." |
| "Our system is accurate" | "Our system is accurate on these fields, in these conditions, and here is where it loses." |
| Opening any pitch with "crypto" | Open with the person and the ₹41,150 |

---

# PART 5 — THE 30-SECOND TEST

**Protocol.** Each person, separately, no notes, explains the problem in 30 seconds to the other two. Not the solution — the *problem*.

**Passing requires all four:**
- [ ] Names a specific person and what they need
- [ ] Explains that the law has no answer, with a concrete example attached
- [ ] Distinguishes this from ordinary AI error
- [ ] Uses no jargon

**Record it.** Play it back. People are consistently worse than they think and consistently better on the third try.

| Person | Attempt 1 | Attempt 2 | Attempt 3 | Passed |
|---|---|---|---|---|
| P1 | ☐ | ☐ | ☐ | ☐ |
| P2 | ☐ | ☐ | ☐ | ☐ |
| P3 | ☐ | ☐ | ☐ | ☐ |

**This is not a formality.** Q&A is scored on whether *the team* understands its own work, and judges direct questions at whoever has been quiet. Thirty seconds each, three times, is the cheapest points in the entire competition.
