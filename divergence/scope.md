# SCOPE CONTRACT — DIVERGENCE
### Step 14 · 6 August 2026 · Signed by all three
*A record of what the law didn't decide*

---

# PART 1 — WHAT A SCOPE CONTRACT IS ACTUALLY FOR

The obvious answer is "so we don't build too much." That is one job out of four.

| # | Job | Who it serves |
|---|---|---|
| 1 | Stop scope creep | The schedule |
| 2 | **Make refusal cheap** | The team |
| 3 | **Score points** | The rubric |
| 4 | **Protect the user** | The person using it |

**Job 2 is the underrated one.** On 14 August someone will say *"wouldn't it be cool if it also…"* and without a contract, saying no requires a person to argue against a teammate's enthusiasm at 11 p.m. **With a contract, the document says no and nobody has to.** That is worth more than the list itself.

**Job 4 matters because some things are out of scope for reasons that have nothing to do with time.** And that leads to the structural problem with the way this step was specified.

---

# PART 2 — TWO LISTS IS THE WRONG SHAPE

The roadmap said: IN SCOPE and OUT OF SCOPE.

But these two sentences are not the same kind of statement:

> *"We didn't build multi-invoice matching because we ran out of time."*
> *"We will never tell anyone what tax to pay."*

The first is a **deferral**. The second is a **boundary**. Putting them in one list makes the deferrals look like principles (pompous) and the principles look like deferrals (alarming — *"so you'd give tax advice if you had another week?"*).

**Three tiers, not two lists.** And a fourth list nobody writes.

---

# PART 3 — THE DECISION RULE

A list cannot anticipate everything. So the contract needs a **test** any of the three of us can apply alone, at midnight, without a meeting:

> ## Does this help us prove the law had no answer — or does it help us give one?
>
> **If it helps give an answer, it is out.**

Everything we build must trace back to the root cause from Step 4: *models fabricate answers where the world has not decided.* **A feature that does not trace to that sentence is somebody else's product.**

Apply the test to anything not on these lists. It resolves most cases in ten seconds.

---

# PART 4 — IN SCOPE

**One payment. One country. One question.**

| | What |
|---|---|
| **Inputs** | One invoice and one payment record, as PDF or photograph. Typed entry as fallback |
| **Asset** | Stablecoins only (USDC, USDT) |
| **Jurisdiction** | India only |
| **Valuation** | Two methods, the gap in rupees and percent, and the gap decomposed by source |
| **Regimes** | Income tax, GST export, FEMA — each with the provision it rests on and how settled that provision is |
| **Absence** | Missing documents enumerated *before* any reasoning, as a hard constraint |
| **Grounding** | Eleven provisions, dated, frozen, scoped per regime |
| **Verification** | Citations string-matched against the corpus. Deterministic, not a prompt instruction |
| **Output** | A disclosure record, and a visible manifest of what we checked |
| **Evaluation** | 30 cases · 2 models · per-field scoring · published baseline · reported losses |
| **Scalability proof** | One ordinary cross-border bank receipt through the same pipeline, unchanged |

## One in-scope decision worth explaining

**Stablecoins only — and this is a choice, not a limitation.**

A volatile token would make the valuation gap larger and our argument easier. **We are using the hardest case for our own claim on purpose.**

> *"Even a coin designed to be worth exactly one dollar produces a ₹47,869 disagreement on a single invoice. If it happens with the stable one, it happens with all of them."*

Say this out loud. Choosing the hardest case for yourself is a maturity signal, and it costs nothing.

---

# PART 5 — DEFERRED (out because of time)

**Would be in version two. Nothing embarrassing about any of these.**

- Multiple invoices matched to one payment, or one invoice across several payments
- Volatile tokens
- Bulk upload of a whole financial year
- Integration with filing or accounting software
- User accounts, logins, saved history
- Live rate lookup (we use cached data on purpose — never call an API during a demo)
- Automatic corpus updating (frozen and versioned instead)
- Singapore and UAE in the system — one pitch slide only, labelled as research
- Any second domain in the build

---

# PART 6 — PERMANENTLY OUT (out on principle)

**Still out with unlimited time and money. This is the list that scores.**

| # | We will never | Why |
|---|---|---|
| 1 | **Tell anyone what tax to pay** | That is regulated advice. We are three school students |
| 2 | **Claim any flow is compliant** | We cannot make it so, and saying it would be false |
| 3 | **Say the record is legally binding or a certificate** | It is neither. A human-signed certificate is required for electronic evidence and we do not produce one |
| 4 | **Advise whether to accept crypto at all** | Most accountants say don't. They are right. **We are for people who already did** |
| 5 | **Market this as making crypto payments easy or safe** | Dishonest and self-defeating. If a version of this makes taking crypto look sensible, we built the wrong thing |
| 6 | **Predict how a dispute would be decided** | Prediction is a different product. We report that no determinate answer exists — the opposite claim |
| 7 | **Detect evasion or fraud** | Not our job, and claiming it would be dangerous |
| 8 | **Invent a method where none is prescribed** | **This is the entire point.** Filling the gap is the failure we exist to prevent |
| 9 | **Retain the user's documents** | Processed in memory, not stored. Fewer obligations, less risk, simpler build |
| 10 | **Fabricate an interview, a test result, or a source** | Not one line |

**Item 8 is the one to say in the pitch.** A product that refuses to do the most obvious thing a user might want it to do — just tell me the number — is unusual, and the reason is the thesis.

---

# PART 7 — OUT OF SCOPE FOR CLAIMS ⭐

**A list almost nobody writes.** Scope is not only about what you build. It is about what you *say*, and every one of these is a sentence that would be attacked in Q&A.

| We will not say | We will say instead |
|---|---|
| "Every tool picks a rate silently" | "They disclose the input. They do not disclose the decision" |
| "We discovered a third category of uncertainty" | "We think this is a case the standard split doesn't cover" |
| "Our system is accurate" | "Accurate on these fields, in these conditions, and here is where it loses" |
| "The law prescribes no method" | "Within the provisions in our manifest, no method is prescribed" |
| "Receiving crypto is illegal under FEMA" | "Very likely non-compliant **by inference**, not by explicit prohibition" |
| "Nobody has built this" | "These six things exist, we use four, here is the one that doesn't" |
| "This will prevent penalties" | "This produces the kind of contemporaneous record the exclusion rewards" |

**Every row is a claim we already made at some point and had to correct.** That is why the list exists.

---

# PART 8 — THE HARDEST SCOPE QUESTION ⚠️

Writing this contract surfaced a contradiction in our own design.

**Rule 1 says: we will never tell anyone what tax to pay.**

**But decision C54 said: the election is one tap, with a default pre-selected.**

**A default is a recommendation.** This is one of the most reliably demonstrated effects in behavioural science — defaults dominate choice, and the person setting the default is making the decision for most users. So by pre-selecting a valuation method, we would be quietly doing the exact thing we said we would never do.

## Three options

| | Option | Problem |
|---|---|---|
| a | No default; user must choose | Friction, and Objection 5 said friction kills adoption |
| b | Default with a neutral label | **Still a default. Still advice** |
| c | **No default — and the record is already valid without one** | None found |

## Option (c), and why it dissolves the problem rather than trading it off

Ask what the record actually needs to do. Under s.439(8)(a) it must show **a bona fide explanation with all material facts disclosed.** The material fact is *that both figures existed and both were shown.* Which one was filed is already in the return.

**So the election was never required for the record to work.**

That means:
- **The record is complete and valid the moment both figures are displayed**
- **Electing is optional** — it adds strength, it is not a gate
- **There is no friction**, because nothing is being demanded of the user
- **There is no advice**, because nothing is pre-selected

The section becomes: *"If you have already decided which figure you are filing, record it here."* Not a question we ask. A place to put an answer they already have.

**Objection 5 said forcing a decision is friction. The resolution was not to reduce the friction — it was to notice we never needed the decision.**

**Change C65: remove the pre-selected default from the interface.**

---

# PART 9 — WHAT WE SAY OUT LOUD

Thirty seconds in the video, and a slide in the deck.

> **What we didn't build, and why.**
>
> One payment, one country, one question. Stablecoins only — and we chose the *hardest* case for our own argument, because if a coin designed to be worth exactly one dollar produces a ₹47,869 disagreement, the volatile ones are worse.
>
> We don't tell you what to pay. We don't claim anything is compliant. We don't store your documents. And we never fill the gap when the law leaves one — because filling it is the exact failure we built this to catch.
>
> Nine more things are out because we ran out of time, and they're listed. Ten are out on principle, and they'd still be out with a year and a budget.

**The rubric's Bonus is for "unusual maturity."** Knowing the difference between what you ran out of time for and what you would refuse on principle is precisely that.

---

# PART 10 — SIGNED

| | Name | Date |
|---|---|---|
| P1 | Hariom Singh | 21 August 2026 |
| P2 | ________________ | ______ |
| P3 | ________________ | ______ |

**By signing:** changing anything in Part 6 needs all three. Moving something from Deferred to In Scope needs all three plus a named thing being dropped in exchange.

---

# 🚪 GATE C

| | Item | Status |
|---|---|---|
| ✅ | Matrix filled, winner chosen, rationale written | Step 13 — A+B at 665/700, four cross-checks agreed |
| ✅ | Scope contract written | This document — needs three signatures |
| ✅ | Name chosen | **DIVERGENCE** — *a record of what the law didn't decide* |

**Gate C is passable once three people sign. Nothing else is blocking.**

---

# THE THING WORTH REMEMBERING

**A scope contract found a bug in our design.**

We were not looking for one. We were writing a list of what we wouldn't build, and doing it honestly forced us to notice that one of our own decisions contradicted one of our own principles.

**Writing down what you refuse to do makes you check whether you are already doing it.** That is why this step is worth more than the twenty minutes it looks like it needs.
