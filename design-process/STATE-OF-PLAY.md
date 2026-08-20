# STATE OF PLAY
### Everything open, as of 6 August 2026
*Kill gate · open questions · remaining brainstorm · validation backlog · engineering feasibility*

---

# PART 1 — THE KILL GATE

**I could not run it.** My sandbox blocks CoinDCX, Binance and data.gov.in — all three returned 403 from the network proxy. Verified, not assumed.

**So it runs on your machine, and it is one command:**

```bash
python3 killgate.py
```

Standard library only. Nothing to install. It probes five possible CoinDCX pair codes (nobody has confirmed which one carries the INR market), reports how far the history actually reaches, pulls the USDC peg from Binance, gets USD/INR from two fallback sources, caches everything to `./cache/`, and prints **GO** or **NO-GO**.

## The decision it produces

| Outcome | Headline becomes |
|---|---|
| History reaches June 2026 | **The 28–29 June divergence.** Recompute ₹44,400 from the real data and use the real number |
| API works, history too short | Try 1h/4h intervals · look for startTime params · cite the news reports as clearly-labelled secondary · else switch |
| Blocked entirely | **The weekend case** |

## Why the fallback is genuinely good, not a consolation

A payment at 03:14 on a Sunday needs **no historical data at all.** FBIL publishes only on Mumbai working days, so no official rate exists for that moment **by design, permanently, and reproducibly.**

It is arguably a *cleaner* proof that the law has no answer than a one-off market spike. And it sidesteps Objection 3 entirely — the June spike was caused by an enforcement raid, so using it as the headline means your best evidence doubles as proof the market is being suppressed.

**Whichever way it goes, write it in the log today.**

---

# PART 2 — EVERY OPEN QUESTION

## 🔴 Blocked on a human, this week

| # | Question | Who | Time |
|---|---|---|---|
| **KG** | Does the rate data exist? | P3 | 20 min — run the script |
| **U6** | Would an assessing officer find our format legible? | P1 | Interview |
| **U7** | Do CAs keep anything like an uncertain-position log? | P1 | Interview |
| **OBJ-1** | **Is there a method everyone already uses in practice?** | P1 | **Interview — this one can change the project** |
| **U9** | Would a CA pay, and how much? | P1 | Interview |
| **U11** | New section numbers for 115BBH and 2(47A) | P1 | 1 hr on indiacode |
| **U12** | New rule number for Rule 115 | P1 | 15 min |
| **U13** | Is data.gov.in's RBI resource live? | P3 | Bundled with the kill gate |
| **U14** | Does KoinX disclose its rate source in the export? | P3 | 45 min, free tier |
| **U15** | Does SBI publish retrievable historical TT buying rates? | P3 | 20 min |
| **Q3** | Confirm Rule 57 from a primary source, not a mapping table | P1 | 30 min |

**Total: about four hours of hands-on work, plus interviews.** That closes almost every factual gap in the project.

## 🟡 Answerable by experiment, during the build

| # | Question | When |
|---|---|---|
| N1 | Do reasoning models fail worse *on our task*? Literature says 24% worse generally | Test case B4 |
| N2 | How much does "tell me what you're uncertain about" close? Literature says partly | Step 16 |
| N3 | Do the two models fail the same way? | During evaluation |
| N4 | Would a CA actually check a citation, in filing season? | Interview |
| A12 | Will our abstention rate be low enough to be useful? | Evaluation |
| A15 | Can we honestly tell "no rule exists" from "we failed to retrieve"? | Partly fixed by scoping the claim to the manifest |

## 🟢 Open but not blocking

U10 (do Indian PI insurers reward documented process — one line in Bounty 1 at most) · Q1 (is the 2025 Act text available officially, or only unofficially) · Q4 (what if a provision changes mid-build — policy decided: freeze and disclose)

---

# PART 3 — REMAINING BRAINSTORM THREADS

Ideas that surfaced and were parked, not killed. **None of these should be built now.** They belong in Bounty 1, the documentation, or a later version.

| # | Thread | Where it belongs |
|---|---|---|
| B1 | **Corpus completeness as a measurable property** — feed it questions with known answers and see whether the corpus supports them. A real completeness check rather than an assertion | Documentation, as future work. **Genuinely interesting** |
| B2 | **Corpus diff** — show a CA what changed since she last filed | Bounty 1 |
| B3 | **Community-maintained corpus** — who keeps it current, what stops it rotting | Bounty 1, year 5 |
| B4 | **The Lacuna List** — one public page, "the 12 places Indian tax law has no answer for crypto" | **Could be built in a day. Strong demo asset regardless** |
| B5 | **The Divergence Index** — publish the gap daily and publicly | Bounty 1 |
| B6 | **Sell to the department** — an officer wants a legible basis too | Bounty 1, and one Q&A line |
| B7 | **The Checklist** — the no-AI version | Documentation, as "what we'd do if we weren't in an AI track" |
| B8 | **Second Opinion** — paste any AI answer, get told what it hid | Documentation as future work. Killed as a main path in Step 12 |
| B9 | **Uncertainty budget visualisation** — decompose the gap by source | ✅ **Already in the interface** |
| B10 | **Observability levels (L1/L2/L3)** borrowed from IFRS 13 | Schema, Step 20 |

## The one thread I would actually pull

**B1 — testing whether the corpus is complete.**

Every other product in this space asserts its coverage. Nobody measures it. The method is simple: write ten questions whose answers you know are *in* the eleven provisions, run them, and see whether the system finds them. If it misses one, either the corpus has a hole or the retrieval does.

**It turns "we checked eleven provisions" into "we checked eleven provisions and verified they answer the questions we claim they answer."** Two hours, and it is the kind of thing a judge does not expect.

---

# PART 4 — VALIDATION BACKLOG

**What is proven, what is assumed, and what would change if the assumption broke.**

| Claim | Status | If wrong |
|---|---|---|
| No prescribed method exists for valuing a VDA in INR | ✅ Verified across four passes | Project ends |
| **Custom has not filled the gap in practice** | 🔴 **UNVALIDATED** | **Project pivots** — becomes "here's the convention, here's that nothing requires it" |
| Rule 11UA → Rule 57 | ⚠️ Mapping table only | Citation wrong, easily fixed |
| s.270A → s.439, and (6) → (8)(a) | ⚠️ Secondary source | Value proposition citation wrong |
| The two methods differ materially | ⚠️ News reports; kill gate pending | Fall back to the weekend case |
| FBIL publishes weekdays only | ✅ Primary source | — |
| Reasoning models are worse at abstention | ✅ NeurIPS 2025, 20 models | The longevity argument weakens |
| A prompt helps but doesn't fix it | ✅ Same paper | Our pipeline becomes a prompt result — **and we'd say so** |
| The bona fide exclusion works in practice | ✅ Multiple tribunal decisions | Economic case weakens |
| **A CA would use and pay for this** | 🔴 **UNVALIDATED** | Business model unproven — survivable for a hackathon |
| **An officer would find our format legible** | 🔴 **UNVALIDATED** | The 439(8) story weakens |
| Our baseline will lose on Class 3 failures | 🟡 Predicted, not measured | Report honestly either way |

**Three red rows. All three are answered by talking to accountants. That is the whole validation backlog.**

---

# PART 5 — ENGINEERING FEASIBILITY

## The build, honestly sized

| # | Component | Type | Est. | Risk |
|---|---|---|---|---|
| 1 | Intake + extraction, schema-enforced | 🤖 Model | 6 h | 🟡 OCR on bad photos |
| 2 | Gap detector | 🤖 Model | 4 h | 🟢 |
| 3 | Dual valuation + gap decomposition | 🤖 + arithmetic | 5 h | 🔴 **Depends on the kill gate** |
| 4 | Regime resolver ×3, scoped corpus per pass | 🤖 Model | 8 h | 🟡 Prompt quality |
| 5 | Adversarial checker | 🤖 Model | 4 h | 🟢 |
| ✓ | **Citation matcher** | ⚙️ Deterministic | 3 h | 🟢 |
| ✓ | **Gap constraint enforcer** | ⚙️ Deterministic | 2 h | 🟢 |
| — | Orchestration, error handling, retries | Code | 4 h | 🟢 |
| — | Corpus assembly, 11 provisions | Manual | 4 h | 🟡 Text availability |
| — | 30 test documents + ground truth | Manual | **8 h** | 🔴 **Always underestimated** |
| — | Evaluation harness + scoring | Code | 5 h | 🟡 |
| — | Interface | ✅ **Done** | 0 h | 🟢 |
| — | Flowchart, documentation, video | Manual | 8 h | 🟡 |

**Total ≈ 61 hours. Three people, eleven days.** That is about two hours each per day. **Feasible with real slack** — which is exactly the position you want, because the estimate is optimistic and everyone's always is.

## The five real technical risks

**1. 🔴 Rate data.** Everything in node 3 depends on it. **Resolved today by running the script.**

**2. 🔴 Test documents take longer than anyone believes.** Writing ground truth for a blurry photograph is slow, dull, and unavoidable. **Mitigation: start today, and one invoice can become three cases — clean, photographed badly, cropped.**

**3. 🟡 OCR on bad photos.** Mitigation: accept typed input for two cases and say so openly. An honest limitation beats a hidden failure.

**4. 🟡 Cost and time per run.** 30 cases × 2 systems × 2 models = 120 pipeline runs, each 5 model calls. Roughly 600 calls. **Mitigation: cache every response by input hash. Never re-run what you've already run.**

**5. 🟢 Corpus text availability.** Partly solved — unofficial full text exists with faithful sub-section structure. Flag as pending verification.

## Three engineering decisions already made, and why they lower risk

**No vector database, no embeddings, no RAG framework.** Eleven provisions is a few thousand words; it fits in context. Load it directly. **This deletes an entire category of bugs** — chunking, retrieval tuning, embedding drift — and makes citations *more* reliable, because the model can only cite what you handed it.

**No orchestration framework.** Five sequential Python functions is not a framework problem. LangGraph would add a dependency, a mental model, and debugging surface for zero benefit at this size.

**Deterministic checks are ordinary code, not model calls.** This is the difference between "we ask the model to verify its citation" and "we string-match against the corpus and reject on no match." **One is a hope. The other is a guarantee** — and it is the thing to say when a judge asks how you know the citations are real.

## Build order

```
Day 1   Corpus (4h) + test cases 1-10 (3h)
Day 2   Test cases 11-30 (5h)          ← the boring one, do it early
Day 3   Node 1 extraction + schema
Day 4   Node 3 valuation + node 2 gaps  ← needs the kill gate resolved
Day 5   Node 4 resolvers + citation matcher
Day 6   Node 5 adversarial + orchestration + constraint enforcer
Day 7   Evaluation harness, first full run
Day 8   Full run × 2 models, results table
Day 9   Flowchart, documentation
Day 10  Video, cold-read test, Q&A rehearsal
Day 11  Buffer — and you will need it
```

**Test data before code.** Everything downstream is judged against it, and building the pipeline first means you'll shape the ground truth to fit what the pipeline already does.

---

# PART 6 — THE FIVE THINGS THAT MATTER TODAY

1. **Run `killgate.py`** — 20 minutes, and it decides your headline
2. **Send the three messages** — the only clock you don't control
3. **Start the test documents** — the most underestimated task in the project
4. **Read and personalise Bounty 1** — closes in three days
5. **All three do the 30-second test** — 45 minutes, protects up to 40 points

**Everything else can wait. These five cannot.**

---

# THE HONEST SUMMARY

**Thinking: essentially complete.** Fourteen steps, five deep research passes, three corrections to our own headline claims, a scope contract that found a bug in our own design.

**Building: not started.**

**Validating: three red rows, all answered by the same conversation.**

You are as well-prepared as any team in this competition and further from a submission than most. **That gap closes with hands, not with more analysis** — and the single highest-value action available to you right now is a WhatsApp message to your family's accountant asking one question:

> *"Is there a method everyone uses, or does each person decide?"*
