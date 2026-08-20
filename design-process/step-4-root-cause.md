# STEP 4 — ROOT CAUSE EXCAVATION
### Deliverable · 4 August 2026
*First-principles analysis · prior art · cross-domain transfer · ten domains · what this changes*

---

# PART 1 — THE FIVE WHYS, RUN PROPERLY

The version in the roadmap stopped at five. It should not have. Here is the full chain.

| # | Question | Answer |
|---|---|---|
| 1 | A freelancer can't work out her tax. Why? | The rupee value of her payment at receipt is disputed |
| 2 | Why is it disputed? | Two defensible methods give figures ₹41,150 apart on one $5,000 invoice |
| 3 | Why does no one settle it? | **No prescribed method exists.** Rule 11UA covers property, jewellery and shares — it was never extended to digital assets |
| 4 | Why doesn't the AI say so? | It has no representation for "the law does not say" |
| 5 | Why not? | Models are trained on text where questions have answers. Fluency and the admission of undecidability are in tension |
| 6 | Why is that dangerous rather than merely imperfect? | **Because the failure is undetectable by checking.** With hallucination you can verify against a truth. Here there is no truth to verify against |
| 7 | Why has nobody built the fix? | Because "correct" is not defined, so the standard ML loop — measure accuracy, improve accuracy — has nothing to optimise against |

**Why 6 and 7 matter more than 5.** Step 5 is where the roadmap stopped and it is a decent insight but a common one. Step 6 explains why this class of error is *categorically* worse than hallucination. Step 7 explains why the field has left it alone — and that is your opening.

---

## The root cause sentence — final

> **Language models are trained on a corpus where questions have answers, so when the world itself has not decided — when no rule was ever written — the model has no representation for that absence and produces its nearest plausible answer in the same confident register as a settled fact. The failure is undetectable by verification, because there is nothing to verify against.**

**Compressed for the stage:** *An AI can say "I don't know." It cannot say "nobody knows."*

---

# PART 2 — FIRST PRINCIPLES: DECOMPOSING THE PROBLEM

Break it into the smallest independent pieces. Each is a separate problem with a separate solution and a separate failure mode.

| # | Sub-problem | Independent? | Our approach | Hardest part |
|---|---|---|---|---|
| **S1** | **Detecting** that a question has no settled answer | Yes | Corpus-grounded resolution; if the provision doesn't answer it, say so | Distinguishing "no rule exists" from "we didn't retrieve the rule" |
| **S2** | **Representing** the absence in a machine-readable way | Yes | `certainty` enum + `insufficient_evidence` as a first-class value | Preventing downstream code from coercing it into a default |
| **S3** | **Quantifying** how much the absence costs | Yes | Resolve under every defensible method, report the spread | Deciding which methods count as defensible |
| **S4** | **Communicating** it without being useless | Yes | Absence first, range second, never a single number | Making "we don't know" read as authoritative rather than weak |
| **S5** | **Verifying** that the grounding is real | Yes | Mechanical string-match of citations against corpus | Partial and paraphrased citations |
| **S6** | **Calibrating** — abstaining rarely enough to be useful | Yes | Measure and publish the abstention rate | No ground truth for "should have abstained" |

**The decomposition itself is a finding.** Most work in this area treats it as one problem — "make the model more honest." It is six problems, and five of them are solvable with engineering rather than model training. That is why a three-person team can attempt this at all.

**S1 is the intellectually hardest.** "No rule exists" and "we failed to find the rule" produce identical model behaviour. Our answer: bound the corpus. If a provision is not in `/corpus/`, the system does not claim the law is silent — it claims *our corpus is silent* and names the boundary. That is a weaker but honest claim, and honesty is the product.

---

# PART 3 — A TAXONOMY GAP WE CAN CLAIM

The uncertainty literature works with two categories, and they are well established. <cite index="14-1">Epistemic uncertainty is caused by exceeding knowledge boundaries or lack of data and can be reduced by expanding training data; aleatoric uncertainty captures inherent randomness within the experiment and is unavoidable.</cite>

**Neither describes our case.**

| Type | Example | Does a true answer exist? | Reducible? |
|---|---|---|---|
| **Aleatoric** | The next coin flip | Yes — a distribution | No |
| **Epistemic** | A fact the model wasn't trained on | Yes — someone knows it | Yes, with data |
| **⭐ Normative indeterminacy** | The rupee value of a Sunday-night stablecoin receipt | **No. Nobody knows, because no authority has decided** | Only by legislation |

A coin flip has a 50% answer. An unknown fact has a true answer somewhere. **A lacuna has no answer at all** — and no amount of training data, retrieval, or model scale changes that, because the missing thing is a *decision*, not information.

The field has room for this. <cite index="13-1">A 2025 ICLR blogpost argues the aleatoric/epistemic concepts "become even more blurred when we go towards agents that interact with the real world" and are "like clouds that, upon getting closer, lose their exact boundaries."</cite> And a 2026 paper argues directly that <cite index="12-1">uncertainty in question answering arises from fundamentally different sources, that distinguishing them is essential, and that existing abstention work treats refusal as a coarse decision — encouraging a generic "I don't know" — which is increasingly inadequate.</cite>

**This is a genuinely defensible contribution for a high school team: naming a third category the standard taxonomy doesn't cover, and building a system that acts on it.**

---

# PART 4 — WE FOUND THE PRECISE LEGAL TERM (AND IT SHARPENS EVERYTHING)

Jurisprudence has been on this for sixty-five years, and it distinguishes two things we had been blurring together.

**Open texture** — <cite index="21-1">from H.L.A. Hart's *The Concept of Law* (1961): no matter how detailed a legal provision is, some vagueness or indeterminacy always remains, leaving room for reinterpretation and contestation. This is not a flaw of language but an intrinsic feature of laws written in natural language.</cite> <cite index="24-1">A speed limit of 100 km/h is a rule; "drivers must drive safely" is an open-textured norm, whose outcome requires situation-specific inquiry and balancing.</cite>

**Lacuna** — <cite index="25-1">a gap in law where no specific rule exists at all.</cite>

**Our case is a lacuna, not open texture.** Rule 11UA is not vague about digital assets — it says nothing about them. That distinction is precise, it is the correct term, and using it correctly in front of a judge who knows law will land hard.

**Why this matters for the pitch:** it grounds the project in sixty-five years of legal philosophy rather than in a hackathon observation. Hart, Wittgenstein on rule-following, and <cite index="27-1">Gallie's 1956 "essentially contested concepts" — concepts like justice and fairness whose correct application is permanently and legitimately disputed</cite> — all sit behind this. You are not inventing the idea that law is indeterminate. You are the first people to make an AI system act correctly when it is.

---

# PART 5 — PRIOR ART: WHAT EXISTS, AND THE HONEST NEAR-MISSES

Do not overclaim here. Three things come genuinely close.

### Near-miss 1 — AbstentionBench
<cite index="16-1">A benchmark for evaluating whether LLMs abstain under uncertainty, explicitly covering questions with no known answer and false-premise questions, and noting that prior research focused on safety, factuality and hallucination while neglecting other abstention scenarios.</cite> The title is *"Reasoning LLMs Fail on Unanswerable Questions."*

**What it does:** measures whether models abstain. **What it doesn't:** apply this to a live case, or quantify the cost of the gap.
**Use it:** cite it as evidence the failure is real and measured. It strengthens you rather than threatens you.

### Near-miss 2 — Identifying open-texture in regulations using LLMs
<cite index="29-1">A 2025 *Artificial Intelligence and Law* paper on using LLMs to annotate vague, ambiguous, under-specified or abstract terms in regulatory documents, noting that open-texture leads to inconsistent interpretation.</cite>

**This is the closest prior art and you must acknowledge it.** But it is an **annotation task on regulatory text** — labelling which words in a statute are vague. It does not take a real transaction, resolve it, price the disagreement, or produce anything a chartered accountant can act on. <cite index="29-1">The authors themselves note the annotation of open-texture should come as a step in verifying language, "neither of which is a final step in and of itself."</cite>

**Your differentiator, stated precisely:** they annotate the *text*; you resolve the *case* and quantify what the gap costs in rupees.

### Near-miss 3 — Formal-reasoning legal AI
A 2026 framework combining LLM agents with formal reasoning names its own limitation directly: <cite index="28-1">the system "assumes deterministic rule parsing, which prevents it from fully capturing legal provisions that deliberately incorporate normative ambiguity."</cite>

**This is the best possible citation for you.** The state of the art explicitly lists your problem as unsolved future work. Put that line in your documentation.

### What nobody is doing
Applying uncertainty-aware reasoning to a **specific transaction**, in a **lacuna** rather than a vague term, producing a **bounded range with the monetary cost of the disagreement**, for a **practitioner who must file something**.

**Your one-sentence novelty claim:**
> *Existing work detects that legal language is vague, or measures whether models abstain. We resolve a specific case under every defensible method and report what the disagreement costs — because a practitioner cannot file "it's ambiguous," she has to file a number, and she needs to know which number she can defend.*

---

# PART 6 — CROSS-DOMAIN TRANSFER: WHERE THIS IS ALREADY SOLVED

Other fields solved "report a number you cannot know exactly" decades ago. **Two of these should change your build.**

### ⭐ Pattern 1 — Fair value hierarchy (IFRS 13 / ASC 820)

Accounting faced exactly your problem: how do you report the value of something with no observable market price? The answer was not to pick a number silently. It was a **three-level hierarchy**:

- **Level 1** — quoted price in an active market for the identical asset
- **Level 2** — observable inputs, but indirect
- **Level 3** — unobservable inputs, requiring disclosure of the technique **and a sensitivity analysis**

**Transfer directly: tag every output with the observability level of its inputs.** Your FBIL rate on a Tuesday is Level 1. Your Sunday-night valuation is Level 3. This gives you a vocabulary that every accountant and every finance-literate judge already recognises, and it costs almost nothing to implement.

**This is the single most valuable idea in this document. Add it to the schema.**

### ⭐ Pattern 2 — The uncertainty budget (metrology, GUM)

No physicist reports a bare measurement. Every measurement carries an **uncertainty budget**: a decomposition showing how much of the total uncertainty comes from each source.

**Transfer: decompose your ₹41,150 spread.** How much comes from the USDC→USD leg? From USD→INR? From the timestamp being outside publication hours? A judge seeing *"₹41,150 total: ₹38,000 from the domestic premium, ₹2,100 from the fixing window, ₹1,050 from the peg"* sees engineering, not hand-waving.

**Add this to Node 4. It is visual, it is rigorous, and no other team will have it.**

### Pattern 3 — Disclaimer of opinion (auditing)

Auditors have four formal outputs: unqualified, qualified, adverse, and **disclaimer of opinion** — a respected professional product meaning "we cannot form a view." Nobody thinks an auditor failed when they issue one.

**Transfer: the vocabulary and the legitimacy.** This is your complete answer to *"does saying 'it's unclear' actually help?"* — an entire regulated profession is paid to say exactly that, in a formal register, and the market values it.

### Pattern 4 — Option / Maybe types (programming languages)

Tony Hoare called the null reference his "billion dollar mistake." The problem: implicit null lets *absence* masquerade as a *value*, and the compiler doesn't stop you. Languages with `Option`/`Maybe` force you to handle absence explicitly — you cannot accidentally treat "no value" as a value.

**Transfer: your gap detector is a type system for legal reasoning.** `insufficient_evidence` must be a first-class value that downstream nodes are structurally unable to coerce into a default.

**Say this out loud to an engineer judge.** It is precise, it is a shared reference, and it reframes your architecture as a well-understood correctness pattern rather than a novelty.

### Pattern 5 — GRADE (evidence-based medicine)
Certainty in the *evidence* is graded separately from strength of the *recommendation*. **Transfer: two independent axes — confidence in the extracted fact, confidence in the rule application.** A perfectly-read invoice can still hit a lacuna.

### Pattern 6 — Probabilistic weather forecasting
The public learned to read "70% chance of rain" over about thirty years, and forecasters are scored on calibration. **Transfer: users *can* learn to read uncertainty if it is presented consistently — and calibration must be measured, not asserted.**

### Pattern 7 — Cartography
Unsurveyed regions were left blank or marked as unsurveyed. **Blank is a legitimate map feature.** Filling it in with plausible coastline is what got sailors killed.

### Pattern 8 — Wikipedia's `{{citation needed}}`
An inline marker at the point of the unsupported claim, not in a separate report. **Transfer: mark uncertainty inline, where the number appears.**

### Pattern 9 — Structural safety factors
Engineers don't know the exact load, so they design for a range with margin. **Transfer: give the user the range and let them choose their own margin — that is a legitimate, mature product shape.**

### Pattern 10 — Clinical equipoise
Genuine disagreement among experts is the *ethical justification* for running a trial. **Transfer: disagreement between methods is information, not failure.**

---

# PART 7 — TEN DOMAINS WHERE THE ROOT CAUSE APPEARS

*For Sustainability & Scalability and for Bounty 1.*

| # | Domain | The lacuna or open texture |
|---|---|---|
| 1 | **Medical dosing** | No established dose for populations excluded from trials — pregnancy, paediatrics, renal impairment. The guideline is silent, not wrong |
| 2 | **Insurance claims** | "Reasonable and customary" has no published schedule |
| 3 | **Employment classification** | Contractor vs employee is a multi-factor test with no bright line and no formula |
| 4 | **Transfer pricing** | "Arm's length" is explicitly a *range*, not a point — tax authorities say so themselves |
| 5 | **Copyright fair use** | Four factors, no weighting, no formula. Every AI answer here is a guess wearing a suit |
| 6 | **Data protection** | "Legitimate interest" is a balancing test with no scoring rubric |
| 7 | **Building codes** | Novel materials the code predates — no rule exists yet |
| 8 | **Immigration eligibility** | Discretionary criteria, "exceptional ability," officer judgement |
| 9 | **Environmental permitting** | "Best available technology" moves as technology moves |
| 10 | **AI regulation itself** | EU AI Act "high risk" classification applied to systems nobody imagined when it was drafted |
| 11 | **Clinical negligence** | The "reasonable practitioner" standard |
| 12 | **Content moderation** | Policy applied to a case the policy never contemplated |

**The pattern:** every regulated domain contains lacunae, because rules are written before the cases arrive. **The failure mode is universal. Only our case study is specific.**

---

# PART 8 — WHAT A SOLVED WORLD LOOKS LIKE

Useful because it tells you what to build toward and what to write in Bounty 1.

- Any AI answer in a regulated domain arrives tagged with an observability level, the way a financial statement does
- "Nobody knows" is a normal, unembarrassing output that professionals expect
- Disagreement between methods is reported with its cost attached
- Regulators *use* aggregated lacuna reports to see where they need to legislate — **the tool that finds the gaps becomes the input to closing them**
- A practitioner is judged on whether their position was defensible and disclosed, not on whether it matched a number that never existed

**That last bullet is your Bounty 1 five-year vision, and it is genuinely ambitious without being fantasy.**

---

# PART 9 — SOLUTION PATHS COMPARED

We should not assume the workflow is the only shape. Four alternatives, evaluated honestly.

| Path | What it is | For | Against | Verdict |
|---|---|---|---|---|
| **A. Multi-node workflow** *(current)* | Decompose, resolve multiple ways, report divergence | Buildable, demonstrable, no training needed, track-aligned | Slower, more expensive per query | ✅ **Correct for now** |
| **B. Fine-tune for abstention** | Train a model to say "nobody knows" | Elegant; one call | Needs data that doesn't exist; you'd have to *create* the lacuna labels first — which is problem S1 again | ❌ Circular |
| **C. Formal/symbolic rules engine** | Encode statutes as logic; a gap is a failed derivation | Provably correct; a gap is *structurally* visible | <cite index="28-1">Existing formal frameworks admit they assume deterministic rule parsing and cannot capture normative ambiguity</cite>; enormous encoding cost | ⚠️ Right long-term direction |
| **D. Retrieval-only with strict grounding** | Answer only from retrieved text; refuse otherwise | Simple, cheap | Cannot *quantify* the gap — no range, no cost. Refuses without helping | ❌ Insufficient |
| **⭐ E. Hybrid — A now, C later** | Workflow now; formalise the highest-value provisions over time | Ships today, has a real technical roadmap | Two systems to maintain | ✅ **This is the five-year answer** |

**Decision: stay on A. Adopt E as the stated evolution path.** That gives Bounty 1 a technically credible roadmap rather than "more users, more features," which the rubric explicitly scores at 5–6.

---

# PART 10 — WHAT THIS CHANGES FOR THE BUILD

Four concrete changes fall out of this analysis.

| # | Change | Where | Why |
|---|---|---|---|
| **C1** | Add an **observability level** (L1/L2/L3) to every valuation and conclusion | Schema (Step 20) | Borrowed from IFRS 13. Vocabulary finance-literate judges already know. Cheap |
| **C2** | Add an **uncertainty budget** — decompose the ₹41,150 by source | Node 4 (Step 26) | Borrowed from metrology. Visual, rigorous, unique |
| **C3** | Distinguish **lacuna** from **open texture** in the certainty enum | Schema | They are different problems with different responses. Precision that shows understanding |
| **C4** | Reframe the corpus boundary honestly: *"our corpus is silent"* not *"the law is silent"* | Nodes 5a/b/c | Solves sub-problem S1 truthfully. Honesty is the product |

**C1 and C2 are the highest-value additions in this entire document.** Together they take about six hours and they are the kind of detail that makes a judge think *these people know what they're doing.*

---

# PART 11 — WHAT WE STILL DON'T KNOW

Stated explicitly, per the rubric's reward for showing understanding of one's own limits.

| # | Unknown | Why it matters | How to resolve |
|---|---|---|---|
| U1 | Is "normative indeterminacy" already named as a third category somewhere we didn't find? | Affects the novelty claim | Search: "normative uncertainty LLM", "deontic gap language model" |
| U2 | How do we distinguish "no rule" from "we failed to retrieve"? | Sub-problem S1 — the hardest one | C4 is a partial fix, not a solution. State it as a limitation |
| U3 | What abstention rate is actually useful? | Too high = noise, too low = false confidence | Measure; ask the CAs in the Step 6 interviews |
| U4 | Would a practising CA accept L1/L2/L3 tagging? | C1 depends on it | Ask in interviews — it is a two-minute question |
| U5 | Does the ₹41,150 arithmetic hold against the raw cached data? | It's our headline number | Action 16, once the data is pulled |

---

# PART 12 — THE ONE-PARAGRAPH SUMMARY

> Rules are written before the cases arrive, so every regulated domain contains gaps — lacunae where no rule exists, not merely vague rules. Language models are trained on text where questions have answers, so when they meet a lacuna they produce their nearest plausible answer in the same confident register as a settled fact. Unlike hallucination, this is undetectable by verification, because there is no truth to verify against. The uncertainty literature has two categories — the model's ignorance and the world's randomness — and neither covers a third case: the world has not decided. Jurisprudence has understood this since Hart in 1961; the AI field has not operationalised it. We built a workflow that detects the gap, refuses to fill it, resolves the question every defensible way, and reports what the disagreement costs — because a practitioner cannot file "it's ambiguous." She has to file a number, and she needs to know which one she can defend.
