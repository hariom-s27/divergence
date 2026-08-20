# RUBRIC WORKSHEET — DIVERGENCE
### Step 1 deliverable · Reverie Hacks 2026 · ML Prompt Engineering
**Print this. Put it on a wall. Update the STATUS column every day.**

---

## HOW TO READ THIS

26 rows — every scorable sub-criterion in the published rubric.

- **GENEROUS** — what a judge looking for reasons to give points needs to see
- **HOSTILE** — what a judge looking for weakness will attack
- **EVIDENCE** — the specific artifact we will put in front of them
- **OWNER** — one name. Not two.
- **NOW** — honest self-score today, 0–5
- **TARGET** — where it needs to be

Substitute real names for P1/P2/P3 before printing.

---

## THE ARITHMETIC FIRST

| Category | Per judge | ×4 | % of 440 |
|---|---|---|---|
| Real-World Problem & Impact | 25 | **100** | 22.7% |
| Technical Execution (ML track) | 25 | **100** | 22.7% |
| Innovation & Originality | 15 | 60 | 13.6% |
| User Experience & Design | 15 | 60 | 13.6% |
| Sustainability & Scalability | 10 | 40 | 9.1% |
| Presentation & Communication | 10 | 40 | 9.1% |
| Bonus: Exceptionality | 5 | 20 | 4.5% |
| Bounties (panel, ×1 only) | — | 20 | 4.5% |
| **TOTAL** | | **440** | |

**Two structural facts that should change your behaviour:**

**(a) Everything except bounties is multiplied by four.** A one-point gain on a sub-criterion is a four-point gain in reality. Accessibility, worth 5 of the 15 UX points, is really worth 20. That reframes it from "nice to have" to "worth more than the entire Sustainability category is per judge."

**(b) Bounties are the only points not multiplied — but they break ties.** Twenty points is 4.5%, which sounds small, until two teams tie and the bounty score decides it. They cost effort, not genius.

---

# CATEGORY 1 — REAL-WORLD PROBLEM & IMPACT (25 → 100)

### 1.1 Problem significance (10 → 40) — ⚠️ **OUR BIGGEST VULNERABILITY**

**GENEROUS:** A problem that clearly exists, with identifiable people harmed, not reverse-engineered from a demo.

**HOSTILE:** *"How many Indian freelancers actually receive stablecoins for services? Your own research says this number is unknowable from public data. Isn't this a tiny niche you picked because it was interesting?"*

That question is coming, and it is fair. Our own red-team wrote it.

**The answer is structural, not rhetorical: change what the problem IS.**

- ❌ Weak framing: *"Indian freelancers paid in stablecoin can't compute their tax."* → niche, unmeasurable, indefensible
- ✅ Strong framing: *"When AI is used in a regulated domain, it invents answers the law does not have — and the user cannot tell."* → affects anyone using AI for tax, law, medicine, insurance, immigration. The crypto case is the **proof**, not the scope

**EVIDENCE:** General framing in the first 15 seconds of everything · the India case as vivid dated proof · the ten-domains list from Step 4 · 44,057 CBDT enforcement communications · interview quotes

**OWNER:** P1 · **NOW: 3/5** (research is excellent, framing is wrong) · **TARGET: 5/5**

**Action:** Lock the general framing at Step 13. Never open a pitch with the word "crypto."

---

### 1.2 Evidence & understanding (5 → 20)

**GENEROUS:** Research, data, *or firsthand insight* into the problem and who experiences it.

**HOSTILE:** *"Have you actually spoken to anyone who has this problem?"*

**Right now our answer is no.** Four deep research reports are secondhand. This is a 20-point sub-criterion and we are leaving a third of it on the table.

**EVIDENCE:** Four research reports with tiered sourcing · primary statutory text in `/corpus/` · **interview notes with verbatim quotes from CAs and freelancers** · the honest "we could not verify" list

*A quote from a practising CA will do more work in your pitch than any statistic. And publishing a "could not verify" list — showing you know the limits of your own research — is exactly what "understanding" means.*

**OWNER:** P1 · **NOW: 4/5 research, 0/5 firsthand** · **TARGET: 5/5**

**Action:** Interviews start today. Message 20, expect 3.

---

### 1.3 Solution impact (10 → 40)

**GENEROUS:** The solution measurably or plausibly improves things for the people affected.

**HOSTILE:** *"You don't answer the question — you just say it's unclear. How does that help anyone? The CA still has to decide."*

**The answer must be a number, not a philosophy.** Something like: *"In N of 30 cases, the single-prompt system produced a confident rupee figure where no prescribed method exists. It never disclosed that it had chosen. Our system flagged all N and showed both figures and the gap."*

That converts "we surface uncertainty" into "we caught N silent fabrications."

**EVIDENCE:** That count from the evaluation · the ₹ value of the divergence on a realistic invoice · the missing-documents list as concrete action for a CA · the reframe: *we do not decide, we prevent an undefendable position going into an assessment*

**OWNER:** P3 (measurement) + P1 (framing) · **NOW: 2/5** · **TARGET: 5/5**

**Action:** Define this metric during Step 21 evaluation design, not after results arrive.

---

# CATEGORY 2 — TECHNICAL EXECUTION, ML TRACK (25 → 100)

*Rubric wording: "Quality and structure of the prompt/workflow design; measurable improvement over a naive baseline; documented iteration and testing across inputs and edge cases."*

### 2.1 Quality and structure of workflow design

**GENEROUS:** A deliberate architecture where each node exists for a reason, with clean contracts between them.

**HOSTILE:** *"Why seven nodes? Is this over-engineered? Would three do the same job?"*

**This is the sharpest technical question you will get, and there is a devastating answer almost no hackathon team prepares: an ablation study.**

> Run the pipeline three times — full, without Node 3 (gap detector), without Node 6 (adversarial checker). Show what breaks each time.

If removing Node 3 causes the system to assert GST conclusions that depend on a FIRC that does not exist, you have *proved* the node earns its place instead of asserting it. This is real engineering practice, it takes about four hours, and it converts your weakest question into your strongest moment.

**EVIDENCE:** Architecture diagram with a "what fails without this" caption per node, each traced to an observed failure in the Step 10 catalogue · JSON contracts · **the ablation table**

**OWNER:** P2 · **NOW: 1/5** (design on paper only) · **TARGET: 5/5**

**Action:** Add the ablation study to Step 29. It is new and it matters.

---

### 2.2 Measurable improvement over a naive baseline

**GENEROUS:** A real baseline, a real measurement, a real delta.

**HOSTILE:** *"How do we know your baseline isn't deliberately weak?"*

**EVIDENCE:** Baseline written on Day 3 **before the pipeline existed**, frozen, timestamped in the repo, **published in full in the documentation** · 30 cases · per-field accuracy, not a headline number · **the cases where the baseline wins, reported prominently**

*Publishing the baseline and admitting where it beats you is the entire defence against the straw-man accusation, and it is worth more than a higher score would be.*

**OWNER:** P3 · **NOW: 0/5** · **TARGET: 5/5**

---

### 2.3 Documented iteration and edge-case testing

**GENEROUS:** A record showing the team tried things, measured, and changed course.

**HOSTILE:** *"Did you write these prompts once and stop?"*

**This is the cheapest sub-criterion in the entire rubric and most teams score zero on it** — not because the work is hard but because nobody writes it down. If you log continuously from today, the marginal cost is close to nothing.

**Format for every entry:** version · what changed · why · measured result before → after.

**EVIDENCE:** `iteration-log.md`, curated into a readable narrative · the edge-case register · Step 17's abstention and citation experiments with raw outputs

**OWNER:** P2 · **NOW: 0/5** · **TARGET: 5/5**

**Action:** Create `iteration-log.md` today. First entry is the Step 16 baseline.

---

# CATEGORY 3 — INNOVATION & ORIGINALITY (15 → 60)

### 3.1 Originality

**HOSTILE:** *"Isn't this just RAG with extra steps?"* and *"Does this already exist?"*

**Answer to the first:** RAG retrieves an answer. This retrieves the *absence* of one. The output is not a fact — it is a bounded disagreement with a citation for why the bound exists.

**EVIDENCE:** Step 8 novelty search, written up honestly including near-misses · a one-sentence claim that survives it

**OWNER:** P1 · **NOW: 3/5** · **TARGET: 4/5**

### 3.2 Creative approach

**EVIDENCE:** The two non-obvious moves — **gap detection running before any reasoning** (every other pipeline reasons over what is present; ours first establishes what is absent and passes it forward as a hard constraint) and **a node whose only job is to refute the nodes before it.**

Say on stage that the adversarial node came from your own method: four research passes designed to disprove your thesis. Building the method into the product is a story judges remember.

**OWNER:** P2 · **NOW: 3/5** · **TARGET: 5/5**

### 3.3 Potential to inspire

**EVIDENCE:** The domain-general claim · the ten-domains list · the scalability proof on a non-crypto receipt

**OWNER:** P1 · **NOW: 2/5** · **TARGET: 4/5**

---

# CATEGORY 4 — USER EXPERIENCE & DESIGN (15 → 60) ⚠️ **CURRENTLY OUR WEAKEST**

### 4.1 Ease of use

**GENEROUS:** *"Could the intended user figure it out without the team explaining it?"*

**EVIDENCE:** Cold-read test with three strangers, documented — what they misread and what we changed

**OWNER:** P3 · **NOW: 0/5** · **TARGET: 4/5**

### 4.2 Visual quality

**GENEROUS:** *"Deliberate and polished rather than default and unfinished."*

**HOSTILE:** Default Bootstrap. Default fonts. Grey boxes.

**EVIDENCE:** A chosen typeface and palette with a written reason · the output ordering as a visible design argument (absence first, range second, single answer never) · **the divergence shown as a visual gap, not two numbers in a table**

*The hardest and most interesting design question in this project: how do you make "we don't know" look authoritative rather than weak? Solve that and the visual quality points follow.*

**OWNER:** P3 · **NOW: 0/5** · **TARGET: 4/5**

### 4.3 Accessibility — ⭐ **HIGHEST POINTS-PER-HOUR IN THE RUBRIC**

**GENEROUS:** *"Does it consider different abilities, devices, or contexts of use?"*

Worth 5 of 15 UX points → **20 points across four judges.** Costs perhaps five hours. **Almost every team will score zero here** because they never read this line.

**EVIDENCE checklist:**
- [ ] Contrast ratios meet WCAG AA (verify with a checker, screenshot it)
- [ ] Full keyboard navigation
- [ ] Semantic HTML, alt text, ARIA labels
- [ ] Works on a phone screen
- [ ] Plain-language labels alongside statutory terms
- [ ] Never colour alone to convey meaning — the divergence needs a label, not just red
- [ ] Low-bandwidth friendly

**OWNER:** P3 · **NOW: 0/5** · **TARGET: 5/5**

---

# CATEGORY 5 — SUSTAINABILITY & SCALABILITY (10 → 40)

### 5.1 Long-term viability

**HOSTILE:** *"Who maintains this after the hackathon, and what does it cost to run?"*

**Answer with a number.** From Step 18: cost per record processed, in rupees. A team that can say "₹X per record, and the statutory corpus needs review twice a year when Finance Acts land" scores. A team that shrugs does not.

**EVIDENCE:** Cost/latency table · a named maintenance burden (corpus review after each Finance Act) · honest statement that the crypto module may need retiring if RBI prohibits stablecoins

**OWNER:** P3 · **NOW: 0/5** · **TARGET: 4/5**

### 5.2 Responsible impact

**HOSTILE — and this one is genuinely hard:** *"If receiving crypto is likely FEMA non-compliant, are you helping people document their own violation?"*

**Prepare this answer properly.** The honest version: we do not encourage the flow; we serve people who have already received the payment. Our output's most valuable line is often a warning, not a certificate. Voluntary disclosure is treated more favourably than discovered non-disclosure. And we never claim any flow is compliant.

Second responsible-impact question: **what if someone relies on a wrong abstention?** Answer: abstention fails safe — it tells the user to check, never that they are fine.

**EVIDENCE:** The "what we do not claim" section · the FEMA warning in the output itself · the fail-safe abstention design

**OWNER:** P1 · **NOW: 3/5** · **TARGET: 5/5**

### 5.3 Path to scale

**EVIDENCE:** Scalability proof — the same pipeline, unchanged, on a non-crypto cross-border receipt · CARF landing April 2027 means demand rises · the ten-domains list

**OWNER:** P2 · **NOW: 1/5** · **TARGET: 4/5**

---

# CATEGORY 6 — PRESENTATION & COMMUNICATION (10 → 40)

### 6.1 Clarity
**EVIDENCE:** The 15-second version · no jargon in the first 30 seconds of anything · the flowchart readable without narration
**OWNER:** P1 · **NOW: 2/5** · **TARGET: 5/5**

### 6.2 Demonstration
**EVIDENCE:** Recorded video, cached data, never live · under 3 minutes · shows the pipeline actually working
**OWNER:** P3 · **NOW: 0/5** · **TARGET: 5/5**

### 6.3 Q&A — *"real understanding of their own work"*
**HOSTILE:** Judges sometimes direct questions at the quietest member.
**EVIDENCE:** Question bank · rehearsal with a hostile stand-in · **every member able to answer the basics**, with primary answerers assigned by topic
**OWNER:** All three · **NOW: 0/5** · **TARGET: 5/5**

---

# BONUS — EXCEPTIONALITY (+5 → 20)

*Rubric says: "Most projects should receive 0 bonus points — that is by design."*

So do not chase it. But note what it names: *"extraordinary execution for the team's experience level"* and *"remarkable teamwork under constraints."*

**Our realistic route:** the honesty. A published baseline, reported losses, an ablation study, a "could not verify" list, and precise legal qualification (`inference`, not `settled`) — from a high school team. That is unusual enough to register.

**OWNER:** whole team · **NOW: 2/5** · **TARGET: 3/5**

---

# BOUNTY 1 — FIVE-YEAR VISION (10) ⏰ **MAY CLOSE 8 AUGUST**

| Sub | Pts | What scores | Owner | Now |
|---|---|---|---|---|
| Ambition & vision | 3 | Real growth in users, scope or impact — not "we keep the demo running" | P1 | 0 |
| **Grounded reality** | **4** | **Named obstacles and responses — the largest single sub-criterion in either bounty** | P1 | 0 |
| Roadmap specifics | 3 | Identifiable stages, milestones, decision points | P1 | 0 |

**The 9–10 descriptor is the instruction:** *"names the moment the project might fail, what they'd cut first, and what success actually looks like in numbers."*

**So write:** the moment it fails = *CBDT prescribes a VDA valuation method and our core problem disappears.* What we'd cut first = *the crypto specificity; the reasoning layer works on any cross-border receipt.* Success in numbers = *name them.*

---

# BOUNTY 2 — FEEDBACK LOOP (10) ⏰ **OPENS ~9 AUGUST**

| Sub | Pts | What scores | Owner | Now |
|---|---|---|---|---|
| Quality of feedback | 4 | Detailed and specific — what they tried, what frustrated them | P1 | 0 |
| Reviewer relevance | 2 | Plausibly the target audience, context made clear to judges | P1 | 0 |
| Response plan | 3 | Concrete, prioritised — **including a reasoned case for NOT changing something** | P2 | 0 |
| Presentation | 1 | Organised | P3 | 0 |

**The 9–10 descriptor:** *"feedback that stings — real criticism the team didn't sand down."*

**So: include the harshest thing anyone says.** And respond in three buckets — fixing now / deferring with a date / **declining with a reason.** Declining something well scores higher than promising to fix everything.

**Reviewers = the CAs and freelancers from the Step 6 interviews.** Recruit once, use twice. This is why interviews start today.

---

# HONEST AUDIT — WHERE WE ARE AT ZERO

| Sub-criterion | Real points at stake | Hours to fix | ROI |
|---|---|---|---|
| Firsthand evidence (1.2) | 20, plus lifts 1.1 and 1.3 | 6 + lead time | ⭐⭐⭐ |
| Documented iteration (2.3) | part of 100 | ~0 if continuous | ⭐⭐⭐ |
| Accessibility (4.3) | 20 | 5 | ⭐⭐⭐ |
| Q&A readiness (6.3) | part of 40 | 4 | ⭐⭐⭐ |
| Bounty 1 | 10 + tiebreak | 4 | ⭐⭐⭐ |
| Bounty 2 | 10 + tiebreak | 6 + lead time | ⭐⭐⭐ |
| Baseline measurement (2.2) | part of 100 | built into plan | ⭐⭐ |
| Visual quality (4.2) | part of 60 | 10 | ⭐⭐ |
| Ease of use (4.1) | part of 60 | 3 | ⭐⭐ |
| Cost-to-run (5.1) | part of 40 | 2 | ⭐⭐ |
| Ablation study (2.1) | part of 100 | 4 | ⭐⭐⭐ |
| Third jurisdiction | marginal | 8 | ⭐ |
| Cases beyond 30 | marginal | 6 | ⭐ |

**The pattern is unambiguous: the highest-return work left is not more technical building.** It is interviews, accessibility, Q&A rehearsal, the two bounties, the iteration log, and the ablation study. Together those are roughly 30 hours and they touch every category.

---

# CATEGORY CHAMPIONS

| Category | Champion | Responsibility |
|---|---|---|
| 1 — Impact | **P1** | Framing, interviews, impact metric |
| 2 — Technical Execution | **P2** | Architecture, ablation, iteration log |
| 3 — Innovation | **P1** | Novelty search, the two non-obvious nodes |
| 4 — UX & Design | **P3** | Interface, accessibility, cold reads |
| 5 — Sustainability | **P2** | Cost model, scalability proof, responsible impact |
| 6 — Presentation | **P3** | Video, flowchart · Q&A is all three |
| Bounty 1 | **P1** | |
| Bounty 2 | **P1** lead, **P2** response plan | |

**A champion does not do all the work — they are accountable for the score in that category and they raise the alarm if it slips.**

---

# THE ITERATION LOG — DECISION

- **Lives at:** `iteration-log.md` in the repo root
- **Format:** one entry per change — `date · node · version · what changed · why · result before → after`
- **Updated:** every time a prompt or node changes, at the moment of change, not retrospectively
- **Owner:** P2, but everyone writes their own entries
- **Curated into a narrative:** Step 28

**Start it today.** Retrospective reconstruction is both harder and less credible.
