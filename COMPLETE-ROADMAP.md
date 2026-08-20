# DIVERGENCE — THE COMPLETE STEP-BY-STEP ROADMAP
### Reverie Hacks 2026 · ML Prompt Engineering Track · 3 people
### 40 steps across 10 phases · Built backwards from the published rubric

---

# ⚠️ READ THIS FIRST — TWO THINGS ARE URGENT

## 1. Bounty 1 may close in days, not weeks

The bounty document says **Bounty 1 opens Day 1 and closes Day 7, 23:59 (UTC−5)**. Reverie Hacks runs 2–17 August. If Day 1 = 2 August, then **Bounty 1 closes on 8 August** — four days from now. Bounty 2 opens Day 8 and closes Day 14, which would be **9–15 August**.

**Post in #questions on Discord today and ask exactly this:** *"For the bounties, what calendar dates do Day 1, Day 7, Day 8 and Day 14 correspond to?"*

Late submissions get zero. Bounties break ties. Do not lose 20 points to a calendar misunderstanding.

## 2. The rubric changes where your effort should go

You now have the real scoring document. It is not the four criteria listed on Devpost — it is six categories worth 105 points, scored by **four independent judges**, plus 20 bounty points scored once by panel consensus.

| Category | Per judge | ×4 judges | Share of 440 |
|---|---|---|---|
| Real-World Problem & Impact | 25 | **100** | 22.7% |
| Technical Execution (track-specific) | 25 | **100** | 22.7% |
| Innovation & Originality | 15 | **60** | 13.6% |
| User Experience & Design | 15 | **60** | 13.6% |
| Sustainability & Scalability | 10 | 40 | 9.1% |
| Presentation & Communication | 10 | 40 | 9.1% |
| Bonus: Exceptionality | 5 | 20 | 4.5% |
| Bounties (panel, not multiplied) | — | 20 | 4.5% |

**Three consequences you must absorb:**

**(a) UX & Design is worth 60 points — as much as Innovation.** Your current plan treats the interface as a Day-11 afterthought. That is a 60-point afterthought. It needs its own design phase.

**(b) The ML track's Technical Execution criterion is written almost exactly like your plan.** Verbatim: *"Quality and structure of the prompt/workflow design; measurable improvement over a naive baseline; documented iteration and testing across inputs and edge cases."* Your 30-case published-baseline evaluation is a direct hit on 100 points. But note **"documented iteration"** — you must keep a log of what you tried, what failed, and what you changed. Most teams have no such record. Make it a first-class deliverable from Step 1.

**(c) There is a live judging slot with scored Q&A.** *"Could the team answer judges' questions with real understanding of their own work?"* This is not a video submission alone. All three of you will be questioned. Prepare for it deliberately (Step 37).

**(d) Real-World Problem & Impact rewards "firsthand insight."** Reading four research reports is not firsthand. Talking to an actual chartered accountant or a freelancer paid in stablecoin is. This also feeds Bounty 2. One activity, two scoring benefits — do it early (Step 6).

---

# HOW TO USE THIS DOCUMENT

Forty numbered steps. Each has: **what · why · brainstorm · research · questions · assumptions · decisions · deliverable · rubric points served · done-when · what could go wrong.**

Steps are ordered by dependency, not by date. Some run in parallel. Each phase ends with a **gate** that all three of you must pass together.

**The core discipline: no step begins until the previous step's deliverable physically exists as a file.** Not "we discussed it." A file.

---

# PHASE A — FOUNDATION AND FRAMING
*Steps 1–6 · The most important phase, and the one teams skip*

---

## STEP 1 — Reverse-engineer the rubric

**What to do**
Build a scoring worksheet. One row per sub-criterion from the rubric. Three columns: *what evidence we will show*, *who owns it*, *is it done*. Print it. Put it on a wall.

**Why**
You have the exact document the judges will fill in. Most teams never read it carefully. Every hour you spend on something that maps to no row is an hour spent on nothing.

**Brainstorm**
For each sub-criterion, ask: *if a judge were being generous, what would they need to see? If hostile, what would they attack?* Write both.

**Questions to answer**
- Which sub-criteria are we currently at zero on? (Answer today: UX visual quality, accessibility, firsthand evidence, iteration documentation, Q&A readiness, both bounties)
- Which are we already strong on? (Evidence & understanding, measurable baseline improvement)
- Where is the cheapest available point? (Presentation and bounties — 60 points that need effort, not genius)

**Decisions**
- [ ] Who owns each of the six categories as a "category champion"
- [ ] The iteration log lives where, in what format, updated when

**Deliverable** `rubric-worksheet.md` — every sub-criterion, evidence planned, owner assigned.

**Rubric served** All of it. This is the map.

**Done when** Every row has a named owner and a planned artifact.

**Could go wrong** You treat this as bureaucracy and skip it. Then on Day 12 you discover accessibility is worth points and you have none.

---

## STEP 2 — Team constitution

**What to do**
Write down how you will work, before there is anything to argue about.

- **P1 — Domain & Content Lead:** corpus, test documents, ground truth, regime prompts, documentation, interviews
- **P2 — Pipeline Engineer:** schema, nodes, orchestration, citation matcher, repo, iteration log
- **P3 — Data, Evaluation & Presentation Lead:** rate APIs, eval harness, scoring, flowchart, UI, video

Plus: daily 20-minute standup at a fixed time · a shared logbook · a rule for breaking deadlocks (majority, or the category champion decides) · a "disagree and commit" rule so debates end.

**Why**
Three-person teams fail on coordination, not capability. The failure mode is two people building the same thing while a third thing nobody owns goes missing.

**Brainstorm**
What are each person's actual strengths? Not what they want to learn — this is a competition, play to strengths. What is each person's hard time constraint (school, family, other commitments)? Write them down honestly now.

**Decisions**
- [ ] Roles assigned by name
- [ ] Standup time fixed
- [ ] Deadlock rule agreed
- [ ] Each person's unavailable hours mapped

**Deliverable** `team-charter.md`

**Rubric served** Presentation & Communication; Bonus (teamwork under constraints is explicitly named).

**Could go wrong** Roles stay vague, everyone assumes someone else is doing the UI.

---

## STEP 3 — Define the problem and pass the 30-second test

**What to do**
Write the problem statement together. Then each person, separately and without notes, explains it in 30 seconds to the other two.

**The statement to start from:**

> When you ask an AI about tax or law, it gives an answer. It sounds confident. But sometimes the law itself has no answer — the rule was never written, two official methods disagree, or the required document does not exist. In those cases a confident answer is worse than no answer, because you cannot tell it apart from a real one. We built a workflow that finds those situations and says so.

**Why**
The rubric's Presentation category scores clarity, and Q&A tests whether all three of you understand your own work. If one person can't explain it, that person will be asked in the live slot.

**Brainstorm — run all three**
- **The grandmother test:** explain it to someone with no technical background. Where do they get lost?
- **The hostile test:** "isn't this just a tax calculator?" Answer it in one sentence.
- **The 6-word version:** compress it. ("AI invents answers the law lacks.")

**Questions to answer**
- Can we state the problem without the words "crypto," "blockchain" or "stablecoin"? *(You should be able to. If you can't, you're describing the case study, not the problem.)*
- Who is harmed, concretely, and how much?

**Assumptions to validate later**
- A5: generalist judges will follow this

**Decisions**
- [ ] Final one-liner
- [ ] Final 30-second version
- [ ] Final 3-minute version

**Deliverable** `problem-statement.md` with all three lengths.

**Rubric served** Real-World Problem & Impact (10 pts problem significance); Presentation (clarity).

**Done when** All three pass the 30-second test in front of each other.

---

## STEP 4 — Excavate the root cause

**What to do**
Run "five whys" on the surface problem until you hit bedrock.

> *Freelancers can't work out their tax* → why? → *the INR value at receipt is disputed* → why? → *no prescribed method exists for valuing a VDA at a point in time* → why does the AI not say so? → *because it has no way to represent "the law does not say"* → why? → **because language models are trained to produce fluent, singular answers, and fluency and uncertainty are in tension.**

That last line is your project. Everything you build should trace to it.

**Why**
The Innovation category scores originality of *idea*, and Impact scores whether the problem is real rather than invented to fit a demo. A root cause at the model-behaviour level is far more original than one at the tax-confusion level.

**Brainstorm**
- Where else does this root cause appear? (Medical dosing, insurance claims, immigration eligibility, building codes.) List ten. You will use this in Sustainability & Scalability and in Bounty 1.
- What would a world look like where this were solved?

**Decisions**
- [ ] The single root-cause sentence, written and agreed

**Deliverable** Root cause chain + a list of ten other domains where it applies.

**Rubric served** Impact; Innovation; Sustainability (path to scale).

---

## STEP 5 — Map stakeholders and users

**What to do**
For each stakeholder write: what they need · what they currently do · what it costs them · would they pay.

| | Who | Current workaround |
|---|---|---|
| Primary buyer | Chartered accountants with cross-border clients | Manual checklist, Excel, judgement |
| Primary sufferer | Indian freelancers paid in stablecoin | CoinGecko screenshot + hope |
| Adjacent | Anyone applying AI in a regulated domain | Trusting the output |

**Why**
The rubric wants *identifiable people or communities*, not an abstraction. And your red-team research already established the honest, slightly awkward truth: **the person with the pain is not the person with the budget.** Saying that out loud in the pitch reads as maturity and will score, not cost you.

**Brainstorm**
- Write a one-paragraph day-in-the-life for the CA and for the freelancer.
- Who is harmed if this works *badly*? (Someone relies on a wrong abstention.) This matters for Sustainability's "responsible impact."

**Deliverable** `users.md` — two personas, one anti-persona, the buyer/sufferer split stated plainly.

**Rubric served** Impact (problem significance, solution impact); Sustainability (responsible impact).

---

## STEP 6 — Gather firsthand evidence ⭐ START IMMEDIATELY

**What to do**
Talk to real people. Target: **3 chartered accountants and 3 freelancers who have been paid in crypto.** Even two of each is enough to change your project from researched to grounded.

Where to find them: CAclubindia forums · r/developersIndia · r/IndiaTax · TaxGuru author bylines · local CA offices · college seniors freelancing · crypto Discords.

**Ask, roughly:**
- Walk me through the last time you handled a foreign crypto receipt
- What did you actually do to work out the rupee value?
- Has a client or officer ever challenged that number?
- What would make you distrust a tool that gave you this?
- What do you currently pay for, and how much?

**Why — this is the highest-leverage step in the entire plan**
1. Impact explicitly rewards *"firsthand insight into the problem and who experiences it."* Four research reports are secondhand. One conversation is firsthand.
2. Bounty 2 requires three reviewers who *"plausibly represent the target audience"* with their context made clear. Same people. Recruit once, use twice.
3. Q&A: when a judge asks "have you talked to anyone who has this problem," you want an answer that is not "we read about it."

**Brainstorm**
Write your outreach message before you send any. Keep it short and specific — "we're high school students building a tool for X, can we ask you five questions" works far better than a long explanation.

**Questions to answer**
- Does the problem exist as we described it, or differently?
- Is the valuation ambiguity something they have actually hit?
- What did we get wrong?

**Assumptions to validate**
- That the pain is real outside our research documents
- That a CA would trust or use this

**Decisions**
- [ ] Recruit these same people as Bounty 2 reviewers — ask now, while you have their attention

**Deliverable** `interviews.md` — notes from every conversation, verbatim quotes where possible. **A quote from a real CA is worth more in your pitch than any statistic.**

**Rubric served** Impact (5 pts evidence & understanding, and it strengthens the other 20); Bounty 2 (6 of 10 pts).

**Could go wrong** Nobody replies. Mitigation: message twenty people, expect three. Start today, not on Day 8.

---

### 🚪 GATE A — Do not proceed until:
- [ ] Rubric worksheet exists with owners
- [ ] All three pass the 30-second test
- [ ] Root cause written
- [ ] Bounty day-numbering confirmed on Discord
- [ ] Interview outreach sent to at least 15 people

---

# PHASE B — RESEARCH AND PRIOR ART
*Steps 7–10*

---

## STEP 7 — Audit existing research, fill only the gaps

**What to do**
Do not redo research. Go through the four reports and the build audit; mark each finding **reusable / discard / verify**. Then close only the blocking gaps.

**Blocking gaps to close:**
- Exact section numbers under the Income-tax Act 2025
- Is the data.gov.in RBI resource live and does it cover your dates
- Do Koinly/KoinX disclose their rate choice in the *exported report* or only in help docs (this affects your "every tool picks one silently" line — be precise)

**Deliverable** Updated logbook with gaps closed or marked unresolved.

**Rubric served** Impact (evidence); Technical Execution.

---

## STEP 8 — Verify novelty properly

**What to do**
Search hard for anyone who has built an AI system whose output is *calibrated disagreement rather than an answer*. Search terms: "uncertainty-aware legal AI," "abstention in LLM compliance," "calibrated legal reasoning," "AI that says the law is unclear," "epistemic humility LLM regulated."

**Why**
Innovation & Originality is 60 points and asks whether the idea is *"meaningfully different from existing solutions the judges know of."* If something exists, you need to know now and position against it — that is stronger than being caught out in Q&A.

**Questions to answer**
- Does prior art exist? If yes, what exactly do we do differently?
- Is anyone doing gap-detection-before-reasoning? Adversarial self-refutation nodes?

**Decisions**
- [ ] Our novelty claim, in one sentence, that survives this search

**Deliverable** `novelty.md` — what exists, what doesn't, our precise claim.

**Rubric served** Innovation (all 60); Q&A survivability.

---

## STEP 9 — Build the statutory corpus

**What to do**
Collect the actual text of every provision you will cite, into files.

- IGST s.2(6) — cbic.gov.in
- s.115BBH, s.194S, Rule 11UA, Rule 115 — incometaxindia.gov.in
- FEMA ss.2(n), 7, 8 — indiacode.nic.in
- IRAS Digital Payment Token guidance — Singapore
- UAE Cabinet Decision 100/2024

**Why**
This corpus is what makes citations verifiable. It is also the reason you need **no vector database, no embeddings, no RAG framework** — roughly ten provisions is a few thousand words and fits in the context window. Load it directly into each resolver prompt. The model can then only cite what you gave it, which makes citation verification a string match rather than a research problem.

**Deliverable** `/corpus/` with a source URL and retrieval date on every file.

**Rubric served** Technical Execution; Impact (evidence).

---

## STEP 10 — Failure archaeology

**What to do**
Before designing anything, study *how* single prompts fail on this kind of task. Run a good single prompt on five rough inputs and catalogue the failure types.

Expect and look for: numeric/decimal/currency confusion · date normalisation errors · counterparty entity confusion (legal name vs trade name vs handle) · fabricated section citations · silent rate selection · confident answers where a document is missing.

**Why**
Your entire architecture is a set of answers to specific failures. If you design nodes before you have observed failures, you are guessing. The rubric explicitly wants *"testing across inputs and edge cases."*

**Brainstorm**
For each failure you observe, ask: *what kind of node would catch this?* That is how the seven nodes should be derived — from evidence, not from a diagram.

**Deliverable** `failure-catalogue.md` — every failure observed, with the raw output as proof.

**Rubric served** Technical Execution (this is the heart of it); Innovation.

---

### 🚪 GATE B
- [ ] Corpus complete and sourced
- [ ] Novelty claim written and defensible
- [ ] Failure catalogue with real observed outputs

---

# PHASE C — IDEATION AND SELECTION
*Steps 11–14 · Give your idea real competition*

---

## STEP 11 — Divergent brainstorm

**What to do**
Generate at least twelve ideas. Use structured techniques, not staring at a wall.

**Technique 1 — Vary the axis.** Hold the root cause fixed, vary: domain (tax → medical → insurance → immigration) · user (freelancer → CA → the AI itself) · output (report → score → warning → refusal) · timing (before → during → after).

**Technique 2 — Steal the shape.** What does a smoke detector do? A credit score? A second medical opinion? A code linter? Apply each shape to your root cause. *("A linter for AI answers in regulated domains" is a genuinely interesting framing.)*

**Technique 3 — Extremes.** What is the version that takes one day? The version that takes one year? Sometimes the one-day version is better.

**Starters (add eight of your own):**

| | Idea | Claim |
|---|---|---|
| A | DIVERGENCE as scoped | The law has no method; we show both |
| B | Crypto-optional, any cross-border receipt | Bigger, survives regulation change |
| C | Domain-general ambiguity detector | Huge claim, hard to prove in time |
| D | Overconfidence auditor — grades *other AI outputs* | Novel, meta, very demoable |
| E | Dual valuation only, done flawlessly | Low risk, low ceiling |
| F | Domain shift to insurance or medical billing | Relatable, discards your research |

**Rule: no criticism during generation.** Criticism is Step 12.

**Deliverable** Twelve+ ideas, one line each.

**Rubric served** Innovation.

---

## STEP 12 — Inversion and pre-mortem

**What to do**
For each idea, two exercises.

**Inversion:** *how would I guarantee this fails?* Then check whether you are accidentally doing any of those things.

**Pre-mortem:** it is 17 August, you scored 40/105, why? Write the story. Do this for your top three ideas.

**Why**
An idea you cannot attack is one you have not understood. And the rubric's Bonus points go to teams that show unusual maturity — knowing your own weaknesses is exactly that.

**Deliverable** One strongest objection per idea, written.

---

## STEP 13 — Score and select against the real rubric

**What to do**
Build the matrix using the **actual six categories with their real weights**, not a generic one.

| Criterion | Weight | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|
| Real-World Impact | 25 | | | | | | |
| Technical Execution (ML track) | 25 | | | | | | |
| Innovation | 15 | | | | | | |
| UX & Design | 15 | | | | | | |
| Sustainability | 10 | | | | | | |
| Presentation | 10 | | | | | | |
| *Buildable in the time* | ×2 | | | | | | |
| *Generalist-comprehensible* | ×2 | | | | | | |

**My recommendation, to be argued with:** take **A's substance with B's framing.** Pitch the general problem — *"in regulated domains, AI invents answers the law does not have"* — and use the India stablecoin case as the vivid, fully-researched proof. Build so a non-crypto receipt also flows through.

Rationale in rubric terms: the general framing lifts Impact (affects identifiable communities beyond a tiny niche) and Sustainability (credible path to scale), while the specific case keeps your unbeatable evidence — a verified legal gap and a dated 8.5% divergence.

**Decisions to lock**
- [ ] Framing · node count · jurisdictions in demo · project name

**Deliverable** Filled matrix + a written paragraph on why the winner won. **This paragraph is also your Q&A answer to "why this approach?"**

---

## STEP 14 — Write the scope contract

**What to do**
Two lists, signed by all three: **IN SCOPE** and **OUT OF SCOPE (and we will say so out loud)**.

Out of scope should include: multiple invoices against one payment · non-stablecoin tokens · actual tax filing · legal advice of any kind · claiming any flow is compliant.

**Why**
Scope creep kills hackathon projects. And explicitly naming what you did *not* do is a maturity signal that scores in Bonus and survives Q&A.

**Deliverable** `scope.md`, agreed by all three.

---

### 🚪 GATE C
- [ ] Matrix filled, winner chosen, rationale written
- [ ] Scope contract signed
- [ ] Name chosen

---

# PHASE D — FEASIBILITY
*Steps 15–18 · This phase can kill or reshape the project. That is its job.*

---

## STEP 15 — The kill-gate data check ⛔ DO THIS FIRST, TODAY

**What to do**
Pull USDT/INR from CoinDCX public candles and USD/INR for **28–29 June 2026**. Cache to disk.

**Why**
Your headline demo — the 8.5% divergence, ₹102.88 against ₹94.65 — depends entirely on this data being retrievable. CoinDCX candle history has depth limits nobody has checked.

**If it fails, the contingency is already decided and it is a good one:** switch the headline to the **weekend-settlement case** — a payment landing at 3 a.m. on a Sunday, when FBIL publishes no rate at all. Zero historical data needed, permanently reproducible, and arguably a *cleaner* proof that the law has no answer.

**Decisions**
- [ ] Headline case confirmed: divergence, or weekend

**Deliverable** Cached data on disk, or a written contingency decision.

---

## STEP 16 — Build the baseline early and make it strong

**What to do**
Write the best single mega-prompt you can. Spend real effort on it. Run it on ten inputs. Preserve it unchanged.

**Why — this is a subtle trap and it is worth 100 points**
The rubric says *"measurable improvement over a naive baseline."* If you write the baseline last, after building your pipeline, you will unconsciously weaken it. A judge will sense a straw man and your entire comparison becomes worthless. Written now, before you are invested, it is a genuine competitor — and beating it means something.

**Publish it in full in the documentation.** Teams who hide their baseline look like they are hiding something.

**Deliverable** `baseline-prompt.md` — the prompt, frozen, plus first results.

---

## STEP 17 — Abstention and citation experiments

**What to do**
Two experiments.

**Abstention:** give a model the corpus and a document with a field deliberately removed. Try five prompt variants to make it output `insufficient_evidence` rather than guess. Record which works and which doesn't.

**Citation:** ask a model to cite a provision that does not exist. Watch it comply. Then design the fix.

**The fix must be mechanical.** A function that string-matches every citation against `/corpus/` and **rejects the conclusion if no match.** A prompt instruction enforces nothing. This is the hidden hard problem of the whole project and it must be code, not words.

**Deliverable** Experiment log with raw outputs; the citation-matcher design.

**Rubric served** Technical Execution (documented iteration); Innovation.

---

## STEP 18 — Cost, latency and throughput model

**What to do**
Time one full pipeline pass. Multiply: 30 cases × 2 systems × 2 models. Compute cost in money and minutes.

**Why**
Sustainability & Scalability explicitly asks *"what does it cost to run?"* A team that can answer with a real number scores; a team that shrugs does not.

**Deliverable** A cost/latency table, and a per-record cost figure you can quote in Q&A.

---

### 🚪 GATE D
- [ ] Headline case confirmed (data cached or contingency chosen)
- [ ] Baseline written and frozen
- [ ] Abstention approach known
- [ ] Citation matcher designed
- [ ] Cost model exists

---

# PHASE E — DESIGN
*Steps 19–24 · Still no production code. Design on paper.*

---

## STEP 19 — Architecture

**What to do**
Draw all seven nodes. For each write: input shape · output shape · which model · what it does · **what fails here without it** — citing the failure catalogue from Step 10.

That last field becomes your flowchart caption and half your documentation. Write it now.

```
[1] INTAKE ──▶ [2] EXTRACT ──▶ [3] GAP DETECTOR
                                     │
                                     ▼
                              [4] DUAL VALUATION
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              [5a] INCOME TAX   [5b] GST        [5c] FEMA
                    └────────────────┼────────────────┘
                                     ▼
                          [6] ADVERSARIAL CHECKER
                                     ▼
                          [7] DISCLOSURE COMPOSER
```

**The two non-obvious nodes — say why on stage:**
- **Node 3 runs before any reasoning.** Every pipeline reasons over what is present. Yours first establishes what is *absent* and passes it forward as a hard constraint, so a conclusion depending on a missing document cannot be asserted.
- **Node 6's only job is to refute nodes 2–5.** You produced this project by running four research passes designed to disprove your own thesis. Building that method into the product is coherent, and Step 8 should confirm it is unclaimed.

**Deliverable** Architecture diagram with all seven "what fails without it" captions.

---

## STEP 20 — Schema and contracts

**What to do**
Lock the JSON schema. Every extracted field carries `value`, `confidence`, `source_span`. Certainty enum: `settled | inference | contested | insufficient_evidence`.

Every node's input and output contract written down. Nodes talk to each other only through these.

**Deliverable** `schema.json` + node contracts.

---

## STEP 21 — Design the evaluation BEFORE the prompts

**What to do**
- Ground truth file format
- Per-field scoring rule — is a partially correct date half a point? Decide now, in writing
- **Draw the empty results table you intend to fill.** Every column.

**Why**
If you don't know how you'll score it, you don't know what you're optimising. And the rubric wants measurable improvement — "measurable" means you defined the measure in advance.

**Deliverable** `evaluation-design.md` + the empty results table.

---

## STEP 22 — Prompt design, node by node

**What to do**
For each node write: system prompt · output schema · the specific failure from Step 10 it addresses · why a single prompt cannot do it.

**Start the iteration log now.** Every version, every change, why you changed it, what the result was. The rubric explicitly scores *"documented iteration."* Most teams have nothing here. This is close to free points and it also makes your documentation write itself.

**Deliverable** Seven prompts on paper + `iteration-log.md` started.

---

## STEP 23 — Output and UX design ⭐ 60 POINTS

**What to do**
Design the interface properly. Wireframe first, on paper, before code.

**The output ordering is the argument, and the design must make that visible:**
1. **What is missing** — first, prominent, impossible to skip
2. **The valuation range** — both numbers, the gap between them shown visually
3. **Regime outcomes** — with citation and certainty label
4. **What this is not** — the disclaimer, visible not buried

**The rubric scores three things here — hit all three:**
- *Ease of use* — could a CA use it without you explaining? Test this on a real person
- *Visual quality* — "deliberate and polished rather than default and unfinished." Choose a typeface. Choose a palette. Do not ship default Bootstrap
- *Accessibility* — contrast ratios, keyboard navigation, plain-language labels, works on a phone. **Almost every team ignores this sub-criterion entirely.** It is nearly free points

**Brainstorm**
- How do you show a *range* rather than a number so it reads as honesty, not vagueness?
- How do you make "we don't know" look authoritative rather than weak? *(This is the hardest design question in the project and the most interesting one.)*
- What does the missing-documents list look like so it feels helpful, not accusatory?

**Deliverable** Wireframes + a chosen visual direction.

---

## STEP 24 — Risk, edge case and failure register

| Type | Case | Handling |
|---|---|---|
| Edge | Weekend/holiday settlement — no FBIL rate exists | `no_rate_published`. This is a feature |
| Edge | Counterparty is a Discord handle | `unresolved`; blocks the GST conclusion |
| Edge | Amount below the 194S threshold | Different path |
| Edge | Multiple invoices, one payment | Out of scope, stated |
| Failure | Rate API down mid-demo | Cached. Record the demo, never run live |
| Failure | Invalid JSON | Schema enforcement + one retry + logged hard fail |
| Failure | Fabricated citation | Matcher rejects the conclusion |
| Failure | Model abstains too often | Tune threshold; report the rate honestly |
| Risk | Judges find it niche | General framing from Step 13 |
| Risk | Straw-man suspicion | Baseline published in full |
| Risk | A teammate drops out | P3's presentation work absorbs into P1; cut to 20 cases |

**Deliverable** `risks.md` — every row with a named handling.

**Rubric served** Technical Execution (edge cases); Sustainability; Q&A.

---

### 🚪 GATE E — THE DESIGN FREEZE
- [ ] Architecture with all captions
- [ ] Schema locked
- [ ] Evaluation designed, empty table drawn
- [ ] Seven prompts on paper
- [ ] Wireframes done
- [ ] Risk register complete
- [ ] Iteration log started

**After this gate, no architectural changes without all three agreeing.**

---

# PHASE F — BUILD
*Steps 25–28*

---

## STEP 25 — Build the test corpus (30 documents)

**What to do**
This is P1's largest job and it is more important than it looks — your entire comparison rests on it.

| Count | Type |
|---|---|
| 8 | Clean, straightforward |
| 8 | Photographed badly — angle, blur, glare, low light |
| 4 | Partial or cropped |
| 3 | Missing counterparty legal name |
| 3 | Weekend or Mumbai bank holiday settlement |
| 2 | Dated 28–29 June 2026 |
| 2 | Non-crypto cross-border receipt (for Step 31) |

**Critical rule: write the ground truth BEFORE running any model on the document.** Otherwise you will unconsciously grade toward whatever the model produced and your accuracy numbers become meaningless.

**Deliverable** 30 documents + 30 ground truth files.

---

## STEP 26 — Build nodes in dependency order

Order: 1 → 2 → 4 → 3 → 5a/b/c → citation matcher → 6 → 7.

Test each node in isolation against ground truth before wiring the next. **Fail fast, fail cheap** — this is also the hackathon's own published advice.

**Log every iteration.** Version, change, reason, result.

---

## STEP 27 — Integration

Wire the pipeline. Add error handling: invalid JSON → retry once → hard fail with a logged error. Never let a failure produce a silent wrong answer.

---

## STEP 28 — Curate the iteration log

**What to do**
Turn the raw log into a readable narrative: *we tried X, it failed because Y, we changed to Z, accuracy moved from A to B.*

**Why**
The ML track's Technical Execution criterion names *"documented iteration"* explicitly. This document alone can separate you from teams whose work is equally good but undocumented.

**Deliverable** `iteration-log.md`, curated.

---

### 🚪 GATE F
- [ ] 30 documents with pre-written ground truth
- [ ] Pipeline runs end to end
- [ ] Citation matcher rejects fabrications
- [ ] Iteration log readable

**If behind here: cut to five nodes.** Merge intake and extraction, keep one regime resolver. **Never cut the gap detector or the divergence output — they are the idea.**

---

# PHASE G — MEASURE
*Steps 29–31*

---

## STEP 29 — Full evaluation run

30 cases × 2 systems × 2 models. Fill the table designed in Step 21. Score per field, not just overall — the per-field table is far more persuasive than a headline number.

---

## STEP 30 — Honest analysis, including where you lose

**What to do**
Analyse the results. Find where the baseline beat you. **Report it prominently.**

**Why**
This is the most counterintuitive and most valuable move in the entire plan. Admitting where you lose is what makes every other number believable. The rubric's Bonus is reserved for projects showing unusual maturity — this is exactly that, and four independent judges will each see it.

**Deliverable** `results.md` — the table, the analysis, the losses, the explanation.

---

## STEP 31 — Scalability proof

Run the two non-crypto receipts through the pipeline unchanged. Document that nothing needed to change.

**Rubric served** Sustainability & Scalability (40 pts) — this is the direct evidence for *"credible path to a larger audience."*

---

# PHASE H — BOUNTIES (20 points, and they break ties)
*Steps 32–33 · Deadline-sensitive — see the warning at the top*

---

## STEP 32 — Bounty 1: Five-Year Vision (10 pts)

**What the rubric actually rewards** — read the descriptors carefully:
- 9–10 *"reads like a plan the team has argued about: it names the moment the project might fail, what they'd cut first, and what success actually looks like in numbers"*
- 5–6 describes growth without explaining what has to go right
- 1–2 is the current project with "in five years" attached

**Structure to write:**
- **Year 1** — India module only, CA-facing, ~50 CA firms, free
- **Year 2** — CARF lands April 2027; demand rises; paid tier; second jurisdiction
- **Year 3** — the architecture goes domain-general; second regulated vertical
- **Year 5** — an uncertainty layer that any regulated AI system can call

**Then the part that scores:**
- **Named obstacles:** RBI may prohibit private stablecoins outright, which shrinks the beachhead. Incumbents (Koinly, KoinX) add income-at-receipt the moment the market is big enough. CAs are conservative adopters. Regulators may finally prescribe a valuation method — which would *remove our core problem*
- **What we'd cut first:** the crypto specificity. The reasoning layer works on any cross-border receipt
- **The moment it fails:** if CBDT prescribes a VDA valuation method, the India case dies. Our answer: the root cause — AI inventing answers the law lacks — outlives any single provision
- **Success in numbers:** name them. Firms using it, records processed, disagreements surfaced

**Deliverable** A document or slide deck. Submit before the deadline you confirmed on Discord.

---

## STEP 33 — Bounty 2: Feedback Loop (10 pts)

**What to do**
Build a feedback form. Get **at least 3 detailed reviews** from people who plausibly represent your users — the CAs and freelancers from Step 6.

**Form questions that produce depth rather than ratings:**
- What did you try to do with it?
- Where did you get stuck or confused?
- What did you not believe?
- What would stop you using this?
- What is missing that you expected?

**What the rubric rewards:** *"feedback that stings — real criticism the team didn't sand down — and a response plan that prioritizes honestly (fix this first, defer that, decline this and here's why)."*

**So: do not sand it down.** Include the harshest thing anyone said. Then respond in three buckets:
- **Fixing now** — with what changed
- **Deferring** — with why and when
- **Declining** — with a reasoned case. *Declining something well scores higher than promising to fix everything*

**Make reviewer context explicit:** "Reviewer 2 is a practising CA in Pune with cross-border clients" scores; "a friend" does not.

**Deliverable** Feedback document with quotes, reviewer context, and the prioritised response plan.

---

# PHASE I — PRESENTATION
*Steps 34–38 · 40 points, plus it carries every other category*

---

## STEP 34 — The flowchart PNG

Required deliverable. All seven nodes, human input points, which model per node, what each does. Make it genuinely good-looking — it is also UX evidence.

**Done when** someone reads it without narration and understands the pipeline.

---

## STEP 35 — Documentation

Include: node-by-node reasoning · what fails without each node · **all prompts published in full, including the baseline** · the iteration log · results with losses · limitations · the "what we do not claim" section.

---

## STEP 36 — The demo video

Record it. Never run live. Use cached data. Rehearse three times.

| Time | Content |
|---|---|
| 0:00–0:20 | The freelancer story. Human, zero jargon |
| 0:20–0:45 | The divergence — two numbers, the gap |
| 0:45–1:30 | Pipeline running. Absence first, then the range |
| 1:30–2:15 | Side by side vs baseline, **including where the baseline wins** |
| 2:15–2:45 | Scalability proof |
| 2:45–3:00 | What we do not claim |

---

## STEP 37 — Live pitch and Q&A preparation ⭐ EXPLICITLY SCORED

**What to do**
There is an assigned judging slot and Q&A is scored on *"real understanding of their own work."* Four judges. All three of you will be asked things.

**Build a question bank and rehearse answers out loud. Expected questions:**

*On the problem*
- Isn't this just a tax calculator?
- How many people actually have this problem? *(Answer honestly: the segment is not measurable from public data. Say so. Then give your interview evidence.)*
- Why would a CA trust your output?

*On the technical work*
- How do we know your baseline isn't deliberately weak? *(Answer: it's published in full, written on day three before the pipeline existed.)*
- What happens if the model hallucinates a section?
- Where does your system perform worse than the baseline?
- Why seven nodes and not three?

*On the domain*
- Is receiving crypto for services even legal in India? *(Answer precisely: it is very likely non-compliant **by inference** from FEMA s.2(n) read with ss.7–8 — not by explicit prohibition. Getting this nuance right in a live answer will impress a judge who knows.)*
- What's your source for the 8.5% figure?

*On scale*
- What does it cost to run per record?
- Who maintains this after the hackathon?

**Assign a primary answerer per category, but every person must be able to answer the basics.** Judges sometimes direct questions at the quietest member.

**Rehearse with someone playing a hostile judge.**

**Deliverable** `qa-prep.md` — questions, agreed answers, assigned answerers.

---

## STEP 38 — Cold-read testing

Find three people outside the team who know nothing about the project. Show them the output with no explanation. Ask what they think it means.

Whatever they get wrong is a design problem, not a them problem. Fix it.

**Rubric served** UX (ease of use); Presentation (clarity).

---

# PHASE J — DELIVERY
*Steps 39–40*

---

## STEP 39 — Pre-submission audit

Run the full quality bar.

**Honesty**
- [ ] Baseline published in full
- [ ] Losses shown
- [ ] FEMA labelled `inference`, never `settled`
- [ ] The figure stated precisely: USDT vs interbank, ₹102.88 vs ₹94.65, 28–29 June 2026
- [ ] No sentence claims the tool makes anything compliant
- [ ] "Not tax, legal or financial advice" visible in output and docs

**Rigor**
- [ ] 30 cases, ground truth written before any model ran
- [ ] Per-field accuracy
- [ ] Every citation mechanically verified
- [ ] Two models tested
- [ ] Iteration log curated

**Rubric coverage**
- [ ] Every row of the Step 1 worksheet has evidence
- [ ] Accessibility addressed
- [ ] Cost-to-run figure exists
- [ ] Both bounties submitted before their deadlines

**Communication**
- [ ] A stranger understood the point in 15 seconds
- [ ] Video under 3 minutes
- [ ] Flowchart readable alone
- [ ] No jargon in the first 30 seconds of anything
- [ ] Every link opens in a fresh browser

---

## STEP 40 — Submit early

Deadline 17 August, 10:30 IST. **Submit by 08:00.** The buffer is for the upload failing, the wrong file format, or a dead link. It happens to someone every time.

---

# PRIORITY ORDER IF EVERYTHING GOES WRONG

Finish in this order:

1. **The divergence output** — two numbers, the gap, why the law doesn't choose
2. **The gap detector** — what is missing, before any reasoning
3. **The measured comparison** — even 10 cases, honestly scored, baseline published
4. **The flowchart** — required
5. **Documentation** — required
6. **Both bounties** — 20 points, low technical effort, tie-breaking
7. **Q&A preparation** — scored, costs only rehearsal time
8. Regime resolvers
9. The interface
10. Adversarial node
11. Scalability proof
12. Third jurisdiction

**Items 1–7 are a genuinely competitive submission.** Note that 6 and 7 rank above building more features — they are worth more points per hour than anything else on this list, and almost every team will under-invest in them.

---

# THE THREE THINGS THAT DECIDE THIS

**1. Confirm the bounty dates today.** Twenty tie-breaking points may be four days from closing.

**2. Start the interviews today.** They serve Impact, Bounty 2, and Q&A simultaneously, and they are the only item here with a lead time you cannot compress.

**3. Write the baseline before you build the pipeline.** One hundred points hinge on a comparison that only means something if the thing you beat was real.
