# STEP 9 — THE STATUTORY CORPUS
### Deliverable · 6 August 2026
*First principles · the silence problem · the manifest · two tiers · scoped loading · a new risk*

---

# WHY THIS IS NOT A FILING TASK

The roadmap said "collect the text of every provision into files." That description is wrong, and following it literally would produce a corpus that quietly breaks three of our central claims.

**The corpus is not a folder. It is the boundary of what we are allowed to say.**

Everything downstream — every citation, every abstention, every "the law does not prescribe a method" — is only as true as this folder is complete and current. Get it wrong and the whole system produces confident, well-formatted, wrong output. Which is, of course, the exact thing we exist to prevent.

---

# PART 1 — WHAT IS THE CORPUS ACTUALLY FOR?

Five distinct jobs. They pull against each other, and nobody notices until the design is already wrong.

| # | Job | What it demands |
|---|---|---|
| 1 | **Grounding** — stop the model inventing law | *More* text. Full context |
| 2 | **Citation verification** — a string to match mechanically | *Exact* text, verbatim, unmodified |
| 3 | **Boundary definition** — makes "our corpus is silent" mean something | *Complete* coverage of a declared scope |
| 4 | **Staleness control** — the Rule 11UA lesson | Versions, dates, supersession records |
| 5 | **Evidence for a judge** | Visible, sourced, checkable |

**The conflicts:**
- Job 1 wants everything; the context window wants little
- Job 2 requires verbatim text; job 1 is tempted to summarise
- Job 3 requires completeness of *scope*, which is different from completeness of *volume*

Three of these tensions produce specific design decisions below. None of them are obvious from "collect the text into files."

---

# PART 2 — THE SILENCE PROBLEM ⭐

This is the deepest issue in the step, and it threatens our headline claim.

Our system will say things like: *"our corpus is silent on how to value a VDA in rupees at a point in time."*

**But silence is only meaningful if the corpus was supposed to cover it.** If we loaded ten provisions out of an Act with several hundred sections, "silent" might just mean *"we didn't load the relevant one."* A judge can ask this in one sentence:

> *"How do you know there's no rule, rather than that you didn't include it?"*

Right now we have no answer. That is a genuine hole.

## The fix, borrowed from two professions

**Legal opinions have a "Scope and Limitations" section.** It states exactly what was reviewed, what was not, and what the opinion therefore does and does not cover. An opinion without one is worthless.

**Audit reports have a "Scope of Audit" paragraph** doing the same job.

Both professions solved this centuries before us: **you earn the right to make a negative claim by declaring what you looked at.**

## So: the corpus needs a manifest

A `MANIFEST.md` that states, in writing:

- **Every provision reviewed**, with source and date
- **Why we believe this set is complete** for the question asked
- **What is deliberately out of scope** — state pricing, GST on the token itself, other jurisdictions
- **The exact form our silence claim may take**

And the silence claim gets scoped precisely:

> ❌ *"The law prescribes no method for valuing a VDA in INR at a point in time."*
>
> ✅ *"Within the provisions listed in our manifest — which we assert cover the valuation of a virtual digital asset received as consideration for services under Indian income tax law — no method is prescribed. Our review is limited to those provisions as retrieved on the dates stated."*

The second is longer, weaker-sounding, and **actually defensible.** The first is a claim we cannot support.

**This is the same discipline as decision D19 ("our corpus is silent," not "the law is silent"), but now with the mechanism that makes it honest.**

---

# PART 3 — TO PROVE A LACUNA, YOU MUST INCLUDE THE RULE THAT FAILS

A subtle trap: you cannot put an absence in a folder.

Our claim is that **Rule 57 (formerly 11UA)** prescribes valuation methods for immovable property, jewellery and shares, and does not extend to virtual digital assets.

That claim is only demonstrable if the model can **read the enumeration and observe that VDAs are not in it.** So Rule 57 must be in the corpus **in full, untruncated** — precisely because it is the rule that *fails*.

**And this creates a hard constraint: no truncation of load-bearing provisions.** If we truncate Rule 57 and the omitted portion happened to mention VDAs, our central finding becomes an artifact of our own editing. That is a research integrity failure, and it would be invisible to us.

**Rule: any provision on which a negative claim rests is stored complete, verbatim, with a hash.**

---

# PART 4 — TWO TIERS

The tension between "more text for grounding" and "exact text for citation" resolves cleanly once you separate the two roles.

### Tier A — Load-bearing. Verbatim, complete, citable.
Provisions we cite, and provisions our negative claims rest on.
- Full official text, no edits, no summarising
- SHA-256 hash recorded at retrieval
- **Only Tier A text is valid for citation matching**

### Tier B — Context. Summarised, marked, never citable.
Background the model may read but must never quote as authority.
- Clearly labelled `TIER_B_CONTEXT_NOT_CITABLE`
- The citation matcher **rejects** any citation resolving to Tier B

**Why this matters:** without the split, a model reads a summary and cites it as if it were the statute. With the split, that failure is structurally impossible — the matcher simply won't validate it.

---

# PART 5 — SCOPED LOADING PER NODE ⭐ NEW

The roadmap assumed one corpus loaded into every resolver. That is wrong, for a reason that only appears once you think about failure modes.

**If the GST resolver can see the FEMA provisions, it can cite them.** Cross-regime contamination is a real and likely failure — models reach for whatever authoritative-looking text is nearby.

**So each node gets only its own regime's provisions:**

| Node | Corpus scope |
|---|---|
| 5a Income tax | s.115BBH · s.393(1) Table 8(vi) · Rule 57 · Rule 115 · s.270A(6) |
| 5b GST | IGST s.2(6) · CGST s.50 · s.73/74 |
| 5c FEMA | FEMA ss.2(n), 7, 8 · Export Regulations |
| 4 Valuation | Rule 57 · Rule 115 · FBIL methodology |
| 3 Gap detector | The evidence-requirement extracts only |

**Three benefits at once:** each prompt stays small, cross-contamination becomes structurally impossible, and the "corpus is silent" claim gets scoped per regime — which is more precise and more honest than a global claim.

---

# PART 6 — THE VERSIONING SCHEMA

Directly from the Step 7 lesson. Every Tier A file opens with this header:

```yaml
---
provision_id: IT-RULE-57
current_citation: "Rule 57, Income-tax Rules, 2026"
former_citation: "Rule 11UA, Income-tax Rules, 1962"
change_effective: 2026-04-01
change_reason: "1962 Rules replaced by 2026 Rules; renumbered"
tier: A
citable: true
retrieved: 2026-08-06
source_url: "<url>"
source_type: official | official_superseded | mapping_table | commentary
text_sha256: "<hash>"
completeness: full | extract
extract_scope: "n/a"
known_limitation: "2026 bare text not located; 1962 text used with mapping"
---
```

**`source_type` is doing important work.** It records whether we have the *current* official text, the *superseded* official text, or only a *mapping table* telling us the number changed. Those are three different evidence qualities and conflating them is how the Rule 11UA error happened in the first place.

---

# PART 7 — A NEW RISK THE ROADMAP DID NOT ANTICIPATE ⚠️

**The current law may be harder to obtain than the superseded law.**

Every government page we found during Step 7 still displays **1961 Act and 1962 Rules** text. The renumbering took effect 1 April 2026 — four months ago — and the accessible primary text has not caught up.

**This is a practical blocker for building a corpus of the law as it stands today.**

### Options

| Option | For | Against |
|---|---|---|
| A. Wait for official 2026 text | Correct | May not exist in time |
| B. Use 1962 text + mapping table, dual-cite | Available today, honest | Text may have changed, not just the number |
| C. Cite only the 1961/1962 provisions | Simple | **Wrong as of April.** Rejected |
| D. **B, with the limitation stated in the output** | Available, honest, and demonstrates the point | Slightly weakens confidence — correctly |

**Take D.** And note what it gives us: our own corpus will carry a `known_limitation` field saying *"current official text not located; superseded text used with a mapping source."*

**That is the product working on itself.** A judge who asks "how do you know your law is current?" gets shown a field where we admit exactly where we're unsure. That is far stronger than a confident silence.

**It also explains why the Rule 11UA error happened at all** — not carelessness, but that the accessible record lags the law. Which is precisely why staleness is a failure type worth detecting.

---

# PART 8 — VALIDATING EARLIER STEPS

| Step | Claim | Status |
|---|---|---|
| 4 | "No vector DB needed — the corpus fits in context" | ✅ **Holds, and scoped loading makes it stronger.** Indian core ≈ 5–6k words. Per-node scoping means each prompt sees 1–2k |
| 4 | "The model can only cite what you gave it" | ⚠️ **Only true with the Tier A/B split and the matcher.** Without them it will still cite from memory |
| 5 | "270A(6) is the value mechanism" | ⚠️ **270A is a 1961 Act section.** Its 2025 equivalent is unconfirmed — U11, still open |
| 7 | "Rule 11UA is now Rule 57" | ⚠️ **From a mapping table, not the bare Act.** `source_type: mapping_table`. Verify before it becomes load-bearing |
| 3 | "The rule covering property, jewellery and shares was never extended" | ✅ Provable — **but only if Rule 57 is stored in full** |
| 19 (D19) | "Say our corpus is silent" | ✅ **Now has a mechanism** — the manifest |

**Two amber flags.** The 270A 2025 equivalent and the Rule 57 verification both need someone with the bare Act for an hour. Until then, both carry `source_type: mapping_table` and are cited in dual form.

---

# PART 9 — NEW BRAINSTORM: THE MANIFEST AS A PRODUCT FEATURE

This came out of the design and was not in the plan.

**What if the manifest is shown to the user?**

> *"This conclusion was reached by reviewing 11 provisions. Here they are. Here is when each was last checked. Here is what we did not look at."*

Nothing else in this space does that. Koinly does not tell you which rules it consulted. Neither does any tax tool we found.

**Three things it buys:**

1. **It answers the trust question before it is asked.** "How do I know your rules are current?" → "You don't have to trust us. Here's the list and the dates."
2. **It makes staleness visible to the user, not just to us.** A CA can see that a provision was last checked in March and decide for herself.
3. **It is the natural home for the disclaimer** — not a footer nobody reads, but a scope statement in the professional form a CA already recognises from every legal opinion she has ever read.

**And it extends into the five-year vision:** a public, dated corpus changelog. When a provision changes, everyone who relied on it can be told. That is a real product, and it grew out of an error we made.

**Add to Bounty 1.**

---

# PART 10 — BUILD INSTRUCTIONS

## Directory
```
/corpus/
  MANIFEST.md
  /tier-a/
    IT-115BBH.md          # 30% VDA rate
    IT-393-1-T8vi.md      # TDS (formerly 194S)
    IT-RULE-57.md         # FMV (formerly 11UA) — FULL TEXT, NO TRUNCATION
    IT-RULE-115.md        # Rate of exchange, SBI TTBR
    IT-270A.md            # Penalty + the (6) exclusions
    GST-IGST-2-6.md       # Five export conditions
    GST-CGST-50.md        # Interest
    FEMA-2n.md            # "Foreign exchange" definition
    FEMA-7-8.md           # Declaration, realise & repatriate
    FBIL-METHODOLOGY.md   # Publication rules
  /tier-b/
    SG-IRAS-DPT.md        # Extract only, not citable
    UAE-CD-100-2024.md    # Art. 42 extract, not citable
    COMMENTARY.md         # "No prescribed method" — professional sources
```

## The order to build in

**Do the load-bearing three first:** `IT-RULE-57`, `GST-IGST-2-6`, `FEMA-2n`. Those three carry most of the argument. If time runs short, everything else can be Tier B.

## One rule that must not be broken

**Never retype a provision. Copy and paste, then hash it.** A typo in the corpus becomes a citation that fails to match, and you will spend an hour debugging the matcher when the bug is a missing comma.

---

# PART 11 — A TRADE-OFF TO DECIDE

**Should Singapore and UAE be in the corpus at all?**

**For:** the 2/1/0 taxable-event visual is genuinely striking, and it serves Scalability (40 points).

**Against:** it triples the legal research; the IRAS and UAE documents are long; we might get them wrong; and **we already have a scalability proof** — the non-crypto cross-border receipt. Two proofs of the same point is redundant.

**Recommendation: keep them, but deliberately shallow.** Tier B, extracts only, event *count* only — never full resolution. And label them on screen as **indicative, not resolved.**

That preserves the visual, costs a fraction of the work, and the honesty of the label is itself a scoring point. Deliberately limiting your own claim reads as judgment, not weakness.

---

# PART 12 — WHAT CHANGED, AND WHAT NEW QUESTIONS AROSE

## Changes

| # | Change | Why |
|---|---|---|
| **C20** | Corpus needs a `MANIFEST.md` declaring scope | Silence is meaningless without a declared boundary |
| **C21** | Tier A / Tier B split; only Tier A is citable | Prevents a summary being cited as statute |
| **C22** | **Scoped loading per node** | Prevents cross-regime citation contamination |
| **C23** | Load-bearing provisions stored full and hashed, never truncated | A negative claim needs the complete enumeration |
| **C24** | `source_type` field distinguishing current / superseded / mapping | The evidence-quality distinction that caused the Rule 11UA error |
| **C25** | Silence claim rewritten to be scope-limited | Defensible instead of overclaiming |
| **C26** | Manifest becomes a user-visible product feature | Answers the trust question before it's asked |
| **C27** | SG/UAE deliberately shallow, labelled indicative | Preserves the visual at a fraction of the cost |

## New questions to answer

| # | Question | Why it matters |
|---|---|---|
| Q1 | Is the 2025 Act bare text available anywhere official? | Determines whether option D is temporary or permanent |
| Q2 | What is the 2025 equivalent of s.270A? | Our value proposition rests on 270A(6) |
| Q3 | Can Rule 57 be confirmed from a primary source, not a mapping table? | It is our headline citation |
| Q4 | How do we handle a provision that changes *during* the hackathon? | Unlikely, but the manifest should have a policy |
| Q5 | Should the manifest be part of the demo? | Probably yes — it is unusual and it is trust-building |

## New brainstorm threads worth pulling later
- **Corpus completeness as a measurable property.** Could we test it — feed questions we know the answer to and see whether the corpus supports them? That would be a real completeness check rather than an assertion
- **A "corpus diff" feature** — show what changed since the CA last filed
- **Community-maintained corpus** — the five-year version. Who keeps it current, and what stops it rotting?

---

# THE ONE-LINE SUMMARY

**The corpus is not a folder of files. It is a written declaration of what we looked at — which is the only thing that makes "we found no rule" different from "we didn't look."**
