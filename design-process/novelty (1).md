# STEP 8 — NOVELTY VERIFICATION
### Deliverable · 4 August 2026
*Honest prior art · what is not novel · what is · the reframe that survives*

---

# THE VERDICT UP FRONT

**Two of our three "novel" mechanisms are not novel. One is arguable. And someone published our core diagnosis three months ago.**

| Claim | Verdict |
|---|---|
| AI should abstain when uncertain | ❌ **Mature research field.** Not novel |
| A node that critiques the earlier nodes | ❌ **Very mature.** Self-Refine, Reflexion, CoVe, DeCRIM, DISC. Not novel |
| LLMs mishandle legal indeterminacy | ❌ **Published May 2026** in a law review. Not our insight |
| Detecting missing inputs *before* reasoning, as a hard constraint | ⚠️ Arguable |
| Resolving a live case under a lacuna and **pricing the disagreement** | ✅ **Not found anywhere** |
| Linking the output to a **statutory penalty exclusion** | ✅ Not found anywhere |
| **The objective itself — hand uncertainty to the user as a priced, recorded choice** | ✅ **This is the real novelty** |

**This is good news, not bad.** Finding this now means we position correctly. Finding it in Q&A from a judge would have been much worse.

---

# PART 1 — WHAT ALREADY EXISTS

## 1. Abstention is a mature field

Not a gap. A subfield.

<cite index="69-1">Work on uncertainty-based abstention shows that by sacrificing a few highly uncertain samples you can improve correctness by 2–8%, avoid 50% of hallucinations by correctly identifying unanswerable questions, and increase safety substantially with almost no computational overhead.</cite>

<cite index="64-1">Research on whether LLMs can express the limits of their knowledge has advanced through confidence calibration and abstention. Kadavath et al. (2022) showed self-assessed confidence correlates with accuracy but overconfidence emerges on hard tasks. Abstention research positions withholding an answer on questions that "should not be answered" as a general safety capability.</cite>

There is a 2026 paper (I-CALM) on incentivising confidence-aware abstention, a full survey on uncertainty quantification and calibration in LLMs, and AbstentionBench measuring exactly this.

**If we say "we made an AI that can abstain," we look like we have not read anything.**

## 2. Self-critique nodes are very well-trodden

Our Node 6 — the adversarial checker — is a known pattern with many names.

<cite index="71-1">Chain-of-Verification generates verification questions to refine a response in a single pass; Self-Refine has a single LLM iteratively critique and revise its own output until a stopping criterion.</cite> Plus Reflexion, CRITIC, DeCRIM, DISC, Double-Checker, ALIGNRAG, and multi-agent debate.

**But the search also gave us a real design lesson we would otherwise have got wrong:**

<cite index="72-1">A growing body of evidence indicates that *intrinsic* self-correction without external signals remains fundamentally unreliable — which motivates using an independent critic rather than self-evaluation.</cite>

And more bluntly: <cite index="78-1">the refinement loop is only as good as the feedback channel. Wherever a checker exists — a SQL executor, a hallucination detector, a factuality probe — refinement is rebuilt around it.</cite>

**So a Node 6 that just asks the model to argue with itself would be a known-weak design.** Our version must be grounded against the corpus and the gap list — external, mechanical signals. That happens to be what we already planned with the citation matcher, but now we know *why*, and we can say so.

## 3. Someone published our diagnosis three months ago ⚠️

This is the one that stings, and we must cite it.

**Shira Gur-Arieh, *"LLMs and the Collapse of Legal Indeterminacy,"* SSRN, May 2026.**

<cite index="66-1">The paper argues that legal texts are open-textured so that statutes written today can absorb tomorrow's technologies and moral disputes without constant revision; that ambiguity underwrites adversarial practice by allowing litigants to contest meaning; and that although LLMs output text — the medium through which law expresses meaning — and so appear better suited to preserve nuance and acknowledge uncertainty, they fail to realise this promise, clashing with legal indeterminacy in ways more subtle and potentially more insidious than rule-based systems. Indeterminate legal language imposes an irreducible burden of judgment, and that burden has to be discharged somewhere.</cite>

**That is our problem statement, written by a legal academic, published in May.**

### Why this is actually a gift

1. **Independent validation of the problem.** A law scholar found it important enough to publish. That is third-party evidence for the Impact category, far stronger than our own assertion.
2. **It is a diagnosis, not a system.** The paper argues the burden of judgment "has to be discharged somewhere." **It does not say where, or build anything.**
3. **We can answer it directly.** Our position: *the burden must be discharged by the human, visibly, with the alternatives priced and the choice recorded.* That is a concrete answer to an open question posed by a law review three months ago.

**Citing this paper and answering it makes us look like we know the field. Not citing it and being asked about it would be fatal.**

## 4. ⭐ THE CLOSEST PRIOR ART OF ALL — and we found it late

**FIN 48 / ASC 740-10-50, and Thomson Reuters ONESOURCE Uncertain Tax Positions.**

<cite index="93-1">ONESOURCE Uncertain Tax Positions (formerly TaxStream FIN 48) helps analyse and report the tax treatment of open positions under ASC 740-10-50 and IAS 37 — keeping an organised inventory of all positions, calculating tax and interest for each one, and reporting on them with a full audit trail, while giving the information needed to decide what to disclose.</cite>

Inventory of uncertain positions · tax calculated per position · full audit trail · decide what to disclose. **That is structurally our product, shipped for corporations since roughly 2007, under a formal accounting standard.**

**The concept of a managed, quantified, disclosed uncertain tax position is not new. It is an accounting standard.**

### Why this strengthens us

| | FIN 48 / ONESOURCE | Us |
|---|---|---|
| Who | Corporations with tax directors | Individuals and their CAs |
| Reports to | Investors, in financial statements | The assessing officer, in the return |
| Detection | **A human decides a position is uncertain** | **The system finds it** |
| Granularity | Position level, annual cycle | **Transaction level, at the moment** |
| India, individuals | **No equivalent exists** | — |

**The framing:** *Large corporations have had a formal framework for uncertain tax positions since 2006. A freelancer in Pune has a CoinGecko screenshot. We are bringing an established professional discipline down to the transaction level, for the people who never got it.*

That is far more credible than claiming to invent a category — and it disarms *"isn't this just FIN 48?"* before it is asked. Yes, conceptually. That is the point.

**Also worth naming:** **Blue J** does AI tax outcome prediction for controversy work — assessing position risk before you commit. **BayesJudge** (2024) applies Bayesian uncertainty to legal judgment prediction. Both *predict an outcome with confidence*; we report that **no determinate outcome exists**. Different objective.

## 5. Other near prior art

| Work | What it does | Gap |
|---|---|---|
| Open-texture annotation in regulation (AI & Law, 2025) | Labels vague terms in statutory *text* | Never resolves a case or prices the gap |
| AbstentionBench (2025) | Measures whether models abstain on unanswerable questions | Measurement, not a system |
| Formal-reasoning legal AI (2026) | Combines LLM agents with formal logic | **Names our problem as its own unsolved limitation** — our best citation |
| Legal hallucination profiling (Dahl, Magesh, Suzgun, Ho, 2024) | Measures legal hallucination rates | Wrong-answer detection, not no-answer detection |

---

# PART 2 — THE HONEST NODE-BY-NODE AUDIT

| Node | Novel? | Honest position |
|---|---|---|
| 1 Intake / OCR | ❌ No | Standard |
| 2 Structured extraction | ❌ No | Standard schema-constrained extraction |
| **3 Gap detector before reasoning** | ⚠️ **Arguable** | See below — this is subtly different from abstention |
| 4 Dual valuation with divergence | ⚠️ Partly | Multi-method computation is ordinary; *reporting the spread as the output* is not |
| 5 Regime resolvers with citation | ❌ No | Grounded generation with citation is standard |
| 6 Adversarial checker | ❌ **No** | Self-Refine family. Must be repositioned |
| 7 Composer with recorded election | ✅ **Yes** | No prior art found for forcing and recording a user election over a legal range |

## Why Node 3 is arguable rather than clearly novel

Abstention asks: *"am I confident enough to answer?"* — a decision about **the answer**, made at the end.

Node 3 asks: *"which inputs required by the law are absent?"* — a check on **the inputs**, made at the start, whose result propagates as a hard constraint that downstream nodes cannot override.

Those are different in kind. Abstention is a confidence threshold on an output. Ours is a **type constraint on an input**. A conclusion depending on a field marked missing is *structurally* impossible, not merely discouraged.

**That is the Option-type argument from Step 4, and it is a defensible distinction.** But do not oversell it — say "we think this framing is different, here is why," not "nobody has done this."

## How to reposition Node 6 honestly

Do not claim the mechanism. Claim the **grounding and the consequence.**

> Self-critique is a well-established pattern, and the literature is clear that *intrinsic* self-critique is unreliable. Ours is grounded externally — the checker verifies citations mechanically against the corpus and checks whether any conclusion depends on a field the gap detector marked missing. What is unusual is not that we critique, but what the critique is allowed to do: a conclusion it breaks is **downgraded and the attack is published in the output**, rather than being silently revised away.

**That last part may be the genuinely uncommon bit.** Every system in the literature uses critique to *improve* the answer before showing it. We use it to *degrade* the answer and show the user the attack. The critique is an output, not a hidden step.

---

# PART 3 — THE REFRAME THAT SURVIVES

Here is the pattern across the entire literature, and it is the opening.

**Every approach treats uncertainty as a property of the model, to be reduced or hidden.**

- Calibration: *make the model's confidence match its accuracy*
- Abstention: *withhold the answer when confidence is low*
- Self-critique: *catch and fix the model's mistakes*
- Uncertainty quantification: *measure how unsure the model is*

**All of it is about the model's relationship to a knowable truth.** The goal is always to get closer to the right answer, or to decline gracefully.

**Nobody treats uncertainty as a property of the world that must be handed to the user as a decision.**

When the law has not decided, there is no right answer to get closer to, and declining is not available — the freelancer still has to file a number by 31 August. So both standard moves fail:

- *Reduce the uncertainty* → impossible; the missing thing is a legislative decision, not information
- *Abstain* → useless; she cannot file "it's ambiguous"

**The third move, which we could not find anywhere: resolve it every defensible way, price the difference, and require the user to elect one — recording that they knew about the other.**

## Name it: from abstention to election

| | Abstention | **Election** |
|---|---|---|
| Trigger | Model is unsure | **World has not decided** |
| Output | "I don't know" | Both answers + the cost of the difference |
| Who decides | Nobody | **The user, on the record** |
| Value | Avoids a wrong answer | **Creates a defensible position** |

**This is the novelty claim, and it holds after everything above.**

---

# PART 4 — THE CLAIM, IN ONE SENTENCE

> **Existing work on uncertainty in AI tries to reduce it or withhold an answer. When the law itself has not decided, neither is possible — the user must still file a number. We resolve the question every defensible way, quantify what the disagreement costs in rupees, and require the user to elect one on the record — producing exactly the contemporaneous disclosure that Section 270A(6) rewards.**

Every clause is defensible. Nothing in it claims a mechanism we did not invent.

---

# PART 5 — Q&A DEFENCES

**"Isn't this just abstention? That's a solved research area."**
> Abstention decides whether to answer. Our user cannot not-answer — she has a filing deadline. We're not withholding, we're resolving multiple ways and pricing the difference so she can choose defensibly. Different problem, different output.

**"Self-critique nodes are everywhere — Self-Refine, Reflexion, CoVe."**
> Correct, and we cite them. We're not claiming the mechanism. Two differences: ours is grounded externally against a corpus, because the literature is clear that intrinsic self-critique is unreliable. And ours *publishes* the attack rather than silently revising it away. Everyone else uses critique to improve the answer before you see it; we use it to degrade the answer and show you why.

**"Hasn't someone written about LLMs and legal indeterminacy?"**
> Yes — Gur-Arieh, SSRN, May 2026, and it's a good paper. It argues the burden of judgment "has to be discharged somewhere." It doesn't say where. Our answer: by the human, visibly, with the alternatives priced and the choice recorded. We're building an answer to a question a law review posed three months ago.

**"So what's actually new?"**
> The objective. Every approach we found treats uncertainty as the model's problem — reduce it, or decline. We treat it as the world's problem and hand it to the user as a priced, recorded decision. We call it election rather than abstention, and we couldn't find prior art for it.

**"Isn't a high school team claiming a research contribution a bit much?"**
> We're not claiming a new algorithm. Every mechanism we use is off the shelf and cited. What we're claiming is that nobody has pointed them at this problem in this configuration, and we checked before saying so.

---

# PART 6 — WHAT WE COULD NOT VERIFY

| # | Unresolved | Effect |
|---|---|---|
| U16 | Is "election over a legal range" claimed in legal-tech commercially rather than academically? | Search Thomson Reuters, LexisNexis, Harvey, Luminance product docs |
| U17 | Does any tax-tech product quantify the cost of a disputed method? | Search Big 4 tax technology |
| U18 | Is 270A(6) evidence generation done by any Indian product? | Interview question for the tax litigation CA |
| U19 | Is "normative indeterminacy" claimed as a formal third uncertainty category? | Not found. Present as *our framing*, not as established terminology |

**On U19 — soften the claim.** We did not find it named, but absence of evidence is weak here. Say *"we think this is a third category the standard dichotomy doesn't cover"*, never *"we discovered a third category."*

---

# PART 7 — WHAT CHANGED

| # | Change |
|---|---|
| **C14** | Cite Gur-Arieh (SSRN, May 2026) in the documentation and answer it directly |
| **C15** | Reposition Node 6: claim the external grounding and the published attack, not the mechanism |
| **C16** | Adopt **"from abstention to election"** as the headline novelty framing |
| **C17** | Node 6 must be externally grounded — intrinsic self-critique is documented as unreliable |
| **C18** | Soften the third-category claim to "our framing" |
| **C19** | Add a prior-art section to the documentation. **Citing what exists is a strength, not an admission** |

---

# THE LESSON

We went in expecting to confirm novelty and instead found that most of our mechanisms are standard. **That is the correct outcome of a novelty search done honestly.**

A team that claims everything is new has not looked. A team that can say *"these six things exist, we use four of them, here is precisely the one thing that doesn't exist yet"* is far more credible — and that is what the Innovation criterion is actually asking: *meaningfully different from existing solutions the judges know of.*

**You cannot answer that question without knowing what exists.**
