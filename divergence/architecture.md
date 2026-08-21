# ARCHITECTURE — DIVERGENCE
### Step 19 deliverable · written 19 August 2026
### **Five model calls and four deterministic checks.** Never "seven nodes."
### *Update, 21 Aug: was "three" until ⚙ E was added (DECISION-D59.md) — the diagram below and the count are both current as of that addition.*

> **Why the phrasing matters.** A model call and a piece of ordinary code are not the same kind of thing, and calling both "nodes" hides the most reassuring fact about this system: **some parts cannot hallucinate, because they are not models.** When a judge asks *"why so many nodes?"*, the answer is not a number — it is *"five model calls each doing one job, wrapped in four checks that are ordinary code and therefore cannot make things up."*

---

# THE DIAGRAM

**Corrected 21 Aug, alongside ⚙ E: this used to draw ⚙ A right after 🤖 2
and ⚙ B feeding straight into 🤖 3/4. Neither is true of `run_pipeline.py`,
checked directly rather than assumed — `node_resolver.resolve()`'s own
signature takes `facts`/`missing`/`tax_year` only, never a valuation
figure, and `gap_enforcer.enforce()` isn't called until after citation and
scope-reach checking, near the end of the automated chain. The shape below
is the real call order; the old shape was never actually run this way. See
`PIPELINE-FLOW.md`'s matching 21 Aug note and `make_flowchart.py`.**

```
                            ┌──────────────────────────────┐
   invoice + payment ──────▶│  🤖 1  EXTRACT               │
   record (PDF/photo)       │     schema-enforced          │
                            └──────────────┬───────────────┘
                                           │  facts{} — every field carries
                                           │  value · confidence · source_span
                                           ▼
                            ┌──────────────────────────────┐
                            │  🤖 2  GAP DETECTOR          │
                            │     runs BEFORE any reasoning│
                            └──────────────┬───────────────┘
                                           │  missing[] with blocks[]
                          ┌────────────────┴────────────────┐
                          ▼                                 ▼
              ┌───────────────────────┐        ┌───────────────────────┐
              │ 🤖 3  INCOME TAX      │        │ 🤖 4  GST             │
              │    scoped corpus only │        │    scoped corpus only │
              └───────────┬───────────┘        └───────────┬───────────┘
                          └────────────────┬────────────────┘
                                           ▼
                            ╔══════════════════════════════╗
                            ║  ⚙ C  CITATION MATCHER       ║
                            ║     deterministic · 15/15    ║
                            ╚══════════════┬═══════════════╝
                                           │  accept=False -> conclusion DROPPED
                                           ▼
                            ╔══════════════════════════════╗
                            ║  ⚙ E  SCOPE-REACH ENFORCER   ║
                            ║     deterministic · 3 rules  ║
                            ╚══════════════┬═══════════════╝
                                           │  citation exists but doesn't REACH
                                           │  these facts -> conclusion DROPPED
                                           ▼
                            ╔══════════════════════════════╗
                            ║  ⚙ A  GAP CONSTRAINT ENFORCER║
                            ║     deterministic            ║
                            ╚══════════════┬═══════════════╝
                                           │  hard constraint, not advice
                                           ▼
                            ╔══════════════════════════════╗
                            ║  ⚙ B  VALUATION LATTICE      ║
                            ║     deterministic · no model ║
                            ╚══════════════┬═══════════════╝
                                           │  12 figures · range · budget
                                           │
                                (--node5, optional)
                                           ▼
                            ┌──────────────────────────────┐
                            │  🤖 5  ADVERSARIAL CHECKER   │
                            │     different model · fixed  │
                            │     checklist · publishes    │
                            │     the attack               │
                            └──────────────┬───────────────┘
                                           ▼
                            ╔══════════════════════════════╗
                            ║  ⚙ D  DISCLOSURE COMPOSER    ║
                            ║     deterministic template   ║
                            ╚══════════════┬═══════════════╝
                                           ▼
                                  disclosure record
                                  (output-interface.html)

   🤖 = model call, can be wrong        ⚙ = ordinary code, cannot invent
```

**FEMA is a static flagged note, not a resolver** (scope cut D42). The position is settled enough to state and the one open question is named. Building a model call for it would add a hallucination surface for no gain.

---

# NODE BY NODE

Every "what fails without this" traces to a numbered, **pre-registered** failure in `failure-catalogue.md`. The predictions were written before any run and committed with a hash — the node list is derived from the risk register, not from a diagram someone liked.

---

## 🤖 1 — EXTRACT

| | |
|---|---|
| **In** | invoice + payment record, PDF or photograph |
| **Out** | `facts{}` — each field `{value, confidence, source_span}` |
| **Model** | small |
| **Corpus** | none |

**What it does.** Pulls the structured facts out of messy input. Every field carries where in the document it came from, so the extraction is checkable rather than trusted.

**What fails without it**
- **F8** numeric / decimal / currency confusion — *predicted ~25%*
- **F9** date normalisation error — *predicted ~20%*
- **F10** entity confusion: legal name vs trade name vs handle — *predicted ~40%*

**Why a single prompt cannot do this job as well.** It can — extraction is not the hard part. The value is not the extraction, it is that **`source_span` makes the extraction auditable**, and that the schema forbids a bare value. A single prompt returns prose; this returns a contract.

---

## 🤖 2 — GAP DETECTOR ⭐

| | |
|---|---|
| **In** | `facts{}` + the evidence-requirement extracts only |
| **Out** | `missing[]`, each with `why_absent`, `blocks[]`, `obtainable` |
| **Model** | small |
| **Corpus** | evidence-requirement extracts only |

**What it does.** Establishes what is **absent** — before anything reasons about what is present.

**What fails without it**
- **F2** silent completeness: answers with no mention that the FIRC or the counterparty identity is absent — *predicted ~90%, Class 3*

**Why this is the node that makes the project more than a better prompt.** Every pipeline in this space reasons over what it was given. This one first establishes what it was **not** given, and passes that forward as a hard constraint rather than as context the model may weigh. `obtainable` distinguishes *"the user forgot it"* from *"it cannot exist for this route"* — an FIRC is `not_for_this_route`, and that distinction is the whole GST conclusion.

**The Hoare argument, for an engineer judge.** Implicit null is what lets absence masquerade as a value. `insufficient_evidence` here is an `Option` type for legal reasoning: it cannot be silently coerced into a default, because the coercion is blocked in code (⚙ A), not discouraged in a prompt.

---

## ⚙ A — GAP CONSTRAINT ENFORCER

| | |
|---|---|
| **In** | `missing[]` + every regime conclusion |
| **Out** | the same conclusions, with `certainty` **forced** where required |
| **Model** | **none** |

**What it does.** Any conclusion whose `depends_on_missing[]` is non-empty has its `certainty` set to `insufficient_evidence`. In code. Unconditionally.

**What fails without it.** The gap detector becomes a suggestion. A sufficiently fluent chain of reasoning talks its way past the missing document, and nothing stops it.

> **A rule you cannot enforce is not a rule.** This is the difference between *"we ask the model to respect the gap list"* and *"a conclusion that depends on a missing field cannot be emitted."* One is a hope. The other is a guarantee.

---

## ⚙ B — VALUATION LATTICE ⭐

| | |
|---|---|
| **In** | `canonical_case.json` |
| **Out** | `valuation.json` — 12 methods, range, uncertainty budget |
| **Model** | **none. No API. No network.** |

**What it does.** Enumerates every combination of the three undetermined choices and computes each resulting rupee figure.

```
2 official dates   ×   5 market readings   ×   2 proxies
25 Jun  94.00          open  high  low          retrieved peg 1.0011
29 Jun  93.95          close  typical           assumed par   1.0000
                    ↓
        12 defensible figures
        ₹4,69,750.00  →  ₹5,17,618.76
        spread ₹47,868.76  (10.19%)
```

**Uncertainty budget** — the spread decomposed by contributing source, borrowed from metrology:

| Source | ₹ | Why it is undetermined |
|---|---|---|
| domestic premium | 44,715.57 | the Indian market price against the official rupee rate |
| which price within the day | 5,506.05 | a daily candle is a range with four printed readings |
| the proxy | 565.57 | the retrieved pair is USDT/INR; the receipt was USDC |
| which official date | 250.00 | no rate was published on the settlement date |

**What fails without it**
- **F1** silent rate selection: one figure, no mention a choice was made — *predicted ~100%, Class 3*
- **F1c** uses a rate source with no legal standing — *predicted ~80%, Class 3*
- **F11** invents a rate for a non-publishing day — *predicted ~80%, Class 3*

**Why it is not a model call.** The headline number must never be a token prediction (D38). Everything here is arithmetic over retrieved inputs, each carrying its source. It also means **the demo needs no API**, which is why the recorded run cannot fail on stage.

**Why the schema forbids a silently-picked single answer.** `valuation.methods` originally had `minItems: 2` — **a single figure was a schema violation, not a valid output.** Amended to `minItems: 1` (decision D51, C1's real case: a plain domestic invoice genuinely has no currency dispute to enumerate). The distinction the schema now enforces is narrower and more honest: a single method is valid only when `spread.inr == 0` — a real, checkable absence of dispute — never as an incomplete lattice standing in for one. The thesis is still in code; the code got more precise about what it actually forbids.

---

## 🤖 3 — INCOME TAX RESOLVER

| | |
|---|---|
| **Corpus** | s.2(111) · s.115BBH · s.393(1) T8(vi) · **Rule 56** · **Rule 57** · **Rule 206** · **Rule 207** · **Rule 247** · s.439(8) — **verbatim blocks only** |
| **Model** | large |

**What fails without it**
- **F6** regime collapse: answers income tax only, ignores GST and FEMA — *predicted ~60%, Class 3*
- **F7** single-event tax: treats it as one 30% event, missing the two-stage structure — *predicted ~50%*
- **F4** states an inference as settled law — *predicted ~70%, Class 3*

**Scoped loading (C22).** It sees income-tax provisions only. Cross-regime citation contamination is not discouraged — it is **structurally impossible**, because the GST text is not in the prompt.

**Verbatim-only injection (D31).** The prompt receives `corpus/verbatim/` — statutory text between the markers, never our commentary. This was found the hard way: **~40% of the corpus by volume was our own analysis.** Injected, the model reads our conclusions and hands them back, and the citation matcher passes it because the citations are real. The headline result would have been an artifact of us having told it the answer.

---

## 🤖 4 — GST RESOLVER

| | |
|---|---|
| **Corpus** | IGST s.2(6) · CGST s.50 · CGST s.74A |
| **Model** | large |

**Why it is worth building even though it is the fourth priority.** On a ₹1,00,000 invoice the valuation spread is a **disclosure** question worth ~₹9,000. If the receipt fails the *"convertible foreign exchange"* test in IGST s.2(6)(iv), the supply is not an export, not zero-rated, and 18% IGST is **cash out of her own pocket** — possibly after filing an LUT on the assumption it was an export. **₹1,19,205 non-fraud vs ₹2,01,752 fraud**, and the ₹82,547 difference turns entirely on whether facts were disclosed (s.74A Explanation 2).

**That is the same hinge as s.439(8)(a), arrived at independently in a different Act.** Disclosure is not a nicety in Indian tax law — it is what penalty turns on, in both regimes.

---

## ⚙ C — CITATION MATCHER

| | |
|---|---|
| **In** | every citation in every conclusion |
| **Out** | `accept: True/False` |
| **Model** | **none** |

**What it does.** String-matches each citation against Tier A corpus text, checks it is **current for the stated tax year**, and checks the tier. `accept=False` means the conclusion is **dropped**, not flagged.

**What fails without it**
- **F5** fabricated citation — *predicted ~20%, Class 2*
- **F3** stale or year-less citation — *predicted ~95%, Class 3*

**The tax-year check is the unusual part.** Both numbering systems are live: FY 2025-26 is governed by the 1961 Act, FY 2026-27 onward by the 2025 Act. **A citation without a tax year cannot be validated at all** — it returns `REJECTED_NO_TAX_YEAR`. Nothing else in this space does that.

**The demo:**
```
verify("Rule 11UA", "FY 2026-27")  -> STALE     — our own error #1, caught
verify("Rule 11UA", "FY 2025-26")  -> VERIFIED  — correct for that year
verify("Rule 115",  "FY 2026-27")  -> STALE     — our own error #5, caught
verify("Rule 11UB", "FY 2026-27")  -> REJECTED  — fabricated
```
Same citation, two years, two answers. **It catches five of our own historical errors automatically.**

**Stated limitation: existence is not relevance.** A VERIFIED citation exists and is current. It does **not** mean the provision supports the proposition. That was node 5's job alone, until ⚙ E, immediately below, took over three specific instances of it.

---

## ⚙ E — SCOPE-REACH ENFORCER

*Added 21 Aug — DECISION-D59.md. Everything else in this document was written 19 August; this section is the one genuine addition since.*

| | |
|---|---|
| **In** | `regimes[]` (post-⚙ C) and `facts{}` |
| **Out** | matched conclusions **dropped**, same semantics as ⚙ C |
| **Model** | **none** |

**What it does.** Node 5's own checklist, item 2 above, is "scope reach — does column B / the opening words actually reach this fact pattern," and it is item 2 for a reason: this project has already found and fixed three real instances of it, by hand, each after node 5 (an LLM call, probabilistic) happened to catch it and happened to be run. ⚙ E encodes exactly those three, and only those three, as ordinary code:

```
Rule 206/207 cited to value a VDA        -> DROPPED. Converts "foreign currency";
                                             a VDA is defined as not being one (s.2(111)).
Rule 57 cited to value a VDA             -> DROPPED. Zero VDA references; its one
                                             residual clause serves s.26(2)(j), not s.92.
Rule 243(8)(e) / Rule 247 cited as THIS  -> DROPPED. Governs a Reporting Crypto-Asset
  taxpayer's own valuation method            Service Provider, never the taxpayer.
```

**The guard that made this safe to ship, not just plausible.** A first version dropped every citation of these three provisions unconditionally — and, tested against `runs/21aug/D1_final_seed2.json`, the frozen record already live on `output-interface.html`, it dropped the record's own headline `valuation_method` conclusion: *"No provision in the text prescribes a specific method... certainty: lacuna."* That citation of Rule 57 is not a claim that Rule 57 governs — it is the citation being used **as evidence that it does not**, the exact pattern this whole project's thesis is built on. `enforce_scope()` now exempts `certainty == "lacuna"` unconditionally, using schema.json's own definition of that value ("no rule exists") as the discriminator, rather than guessing at outcome polarity from free text. The historical bug this file exists to catch (`runs/21aug/D1-a_regimes.json` — *"the fair market value is determined... as per Rule 11UA,"* certainty `insufficient_evidence`) never carries `lacuna`, so the guard costs nothing against the real catch and prevents a false drop on the project's own correct output. See `scope_enforcer.py`'s self-test, seven cases, for both directions.

**Stated limitation: three provisions, not a scope-reading model.** This is not what "NLI-based scope enforcement" would sound like — it does not read arbitrary statutory text against arbitrary facts. It is three hand-verified findings, encoded once each, so that the *next* time one of these three specific errors would have occurred, it cannot reach the record — no dependence on node 5 having been asked, or on it landing the attack that day. A fourth misapplied provision this project has never analysed is exactly as invisible to this file as it was before. `s.393(1)`'s own scope-reach failure (`DECISION-D55.md`) was deliberately left **out**: that error turns on which direction a conclusion argues (the correct D1 answer legitimately cites the same provision to explain why *no* obligation arises), not on citation + facts alone — telling those two apart from citation and facts alone would need reading the outcome text, and a keyword guess at its polarity was judged more likely to silently drop a correct conclusion than to catch a wrong one. Left for node 5, same as before.

---

## 🤖 5 — ADVERSARIAL CHECKER

| | |
|---|---|
| **In** | everything above |
| **Out** | `attacked[]` — target, attack, survived, downgraded_to |
| **Model** | **a different model from the resolvers** (D41) |

**The fixed checklist. Every item is a mistake we actually made:**

| # | Check | The error it would have caught |
|---|---|---|
| 1 | **Operative status** — current for the stated tax year? | Rule 11UA→57 (OWN-1) · 270A(6)→439(8) (OWN-2) · Rule 115→206 (OWN-5) |
| 2 | **Scope reach** — does column B / the opening words actually reach this fact pattern? | Rule 115 not applying at all · **row 7 of Rule 57** |
| 3 | **Missing document** — does this rest on something in `missing[]`? | — |
| 4 | **Correct instrument / date / pair** | interbank→SBI (OWN-3) · the USDC/USDT proxy |

**Say this on stage.** A checklist derived from four errors we actually made is far more persuasive than one derived from a diagram.

**Why a different model.** Self-refutation by the same model over its own reasoning has strong self-consistency bias, and the literature is explicit that *intrinsic* self-correction without external signals is unreliable. Ours is grounded externally: the citation matcher and the gap list are mechanical inputs to the critique.

**What is unusual is not that we critique — it is what the critique is allowed to do.** Every system in the literature uses critique to *improve* the answer before you see it. **We publish the attack and never let it silently improve the answer.** `downgraded_to` is computed and shown, but deliberately never written back into `regimes[].certainty` (decision from the first real run: fuzzy-matching a free-text attack target back to one specific conclusion was judged more likely to silently corrupt the wrong entry than to help — see `results.md`). The critique is an output a reader cross-checks by eye, not a hidden step that edits the answer for them.

> ⚠️ **This warning box is kept as written, not deleted, because the ablation
> it predicted actually happened — see the update immediately below rather
> than treating this as still-current.** It originally read: *"This node has
> never run. Its real successes so far — Rule 57 row 7, the five stale
> citations, the FERA finding — were all found by humans reading
> adversarially. The ablation at Step 29b is what decides whether it earns
> its place."*
>
> **Update, 21 Aug — no longer accurate, kept for the record:** the node has
> now run repeatedly. The planted-defect ablation scored 3 of 4
> (`DECISION-D50.md`). It went on to catch three real, previously
> undisclosed scope-reach defects in this project's own resolver output, on
> unplanted data, the same night — `DECISION-D50.md`'s addendum,
> `DECISION-D54.md`, `DECISION-D55.md`. It also, separately, produced two
> real failure modes of its own (attacking almost everything it's shown; one
> run of incoherent output) — disclosed in `results.md`'s "Where we lose,"
> not hidden because the node also has real wins.

---

## ⚙ D — DISCLOSURE COMPOSER

| | |
|---|---|
| **Out** | the disclosure record, into `output-interface.html` |
| **Model** | **none** (D34) |

**What it does.** Deterministic template. Absence first, the range second, a single answer never. Ordering enforced in the layout, because **the ordering is the argument**.

**Why not a model call.** *A document whose purpose is to be trustworthy cannot be produced by something that can hallucinate.*

**`limits[]` has `minItems: 1`.** If it is ever empty, the record is wrong.

---

# WHAT THE RISK REGISTER SAYS ABOUT THIS SHAPE

Failures scored **Severity × Occurrence × Detection**, FMEA-style, with Detection weighted so that *harder to detect = higher risk*.

| Rank | Failure | Class | RPN | Caught by |
|---|---|---|---|---|
| 1 | **F1** silent rate selection | 🔴 3 | 125 | ⚙ B |
| 2 | **F2** silent completeness | 🔴 3 | 125 | 🤖 2 + ⚙ A |
| 3 | **F3** stale citation | 🔴 3 | 100 | ⚙ C |
| 4 | **F4** false settledness | 🔴 3 | 75 | 🤖 5 |
| 5 | **F6** regime collapse | 🔴 3 | 60 | 🤖 3 + 🤖 4 |
| 6 | **F11** weekend invention | 🔴 3 | 60 | ⚙ B |
| … | | | | |
| 12 | F12 extraction failure on a bad photo | ⚪ 1 | 6 | 🤖 1 — *and it is visible* |
| 13 | F13 malformed output | ⚪ 1 | 1 | schema |

**Six of the top seven are Class 3 — invisible to the user.** The two failures people naturally worry about — a blurry photo, broken JSON — score near the bottom, because the user can see them.

> ## **This architecture is not designed against the failures that are most common. It is designed against the failures that are most invisible.**

That sentence is the answer to *"why so many nodes?"*, and it is why three of the eight components are ordinary code.

---

# WHAT WE WOULD CUT, IN ORDER

If the build runs short:

1. **GST resolver** → static flagged note *(loses the bigger number, keeps the claim)*
2. **Adversarial checker** → but then say so, and drop the novelty claim that rests on it
3. **Extract** → accept typed input for the demo cases and say so openly

**Never cut:** ⚙ B the valuation lattice · 🤖 2 the gap detector · ⚙ C the citation matcher. **They are the idea. Everything else is decoration.**

---

# ERROR HANDLING

Invalid JSON from any model call → retry once → **hard fail with a logged error**.

**Never let a failure produce a silent wrong answer.** A pipeline that degrades quietly is the failure mode this project exists to prevent, and shipping one would be the most embarrassing possible outcome.

---

# COST

| | |
|---|---|
| Metered (Claude) | **₹29.91 per record** |
| Open models (evaluation) | ₹0 |
| vs a single prompt | **~2.7×** |
| Output tokens per record | ~12,600 |

That last figure is why the demo is **recorded, not run live** (D33). A judge watching a spinner for two minutes is worse than a pre-computed result honestly labelled.
