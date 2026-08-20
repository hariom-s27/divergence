# STEP 5 — STAKEHOLDERS AND USERS
### Deliverable · 4 August 2026
*Assumption challenged · economic mechanism found · seven stakeholders · two personas · one anti-persona · asymmetric failure design*

---

# PART 1 — THE ASSUMPTION WE CHALLENGED

The red-team concluded the chartered accountant is the buyer because the freelancer won't pay. That is probably right, but the reasoning was weak — it was *"freelancers anchor to ₹115/year, so sell to someone with a budget."*

That reasoning has a hole. **A CA with a budget still won't buy something she doesn't need.** She already knows the law is unclear here. If our pitch to her is "we'll tell you it's ambiguous," she has no reason to pay.

So the real question is not *who has money* but **what does each stakeholder actually lose today, in rupees, and does our output change that number?**

Asking it that way found something we had completely missed.

---

# PART 2 — THE ECONOMIC MECHANISM (THE BIGGEST FINDING IN THIS STEP)

Indian tax law contains a penalty regime that is almost written for this product.

**Section 439 of the Income-tax Act, 2025** (formerly Section 270A of the 1961 Act, renumbered with effect from 1 April 2026) sets two penalty tiers. <cite index="31-1">Ordinary under-reporting draws a penalty of 50% of the tax payable on the under-reported income; misreporting draws 200%.</cite> <cite index="36-1">The misreporting categories are an exclusive list — misrepresentation or suppression of facts, false entries, unsubstantiated expenditure claims, and similar. If a case does not fall within them, the Assessing Officer cannot impose the higher rate.</cite>

**Then Section 439(8) — formerly Section 270A(6) — provides exclusions that read like a specification for our output.** <cite index="38-1">Under-reporting does NOT arise where: the assessee offers an explanation which is bona fide and has disclosed all material facts; the returned income is based on an estimate and the assessee has disclosed the basis; or the additional income is on account of a difference in judicial opinion on a question of law.</cite>

Read those three again.

- *An explanation that is bona fide, with all material facts disclosed* → that is our disclosure record
- *An estimate where the basis was disclosed* → that is our dual valuation with the method named
- *A difference of opinion on a question of law* → **that is a lacuna, exactly**

And there is Supreme Court support for the underlying principle. <cite index="34-1">In *Reliance Petroproducts* [(2010) 322 ITR 158 (SC)] the Court held that merely making a claim which is not sustainable in law does not amount to furnishing inaccurate particulars — logic that remains persuasive under 270A where the taxpayer has made complete disclosure but adopted a disputed legal view.</cite>

## What this is worth, in rupees

Take our ₹41,150 divergence on one $5,000 invoice, at a 30% slab:

| Outcome | Tax on the disputed amount | Penalty | Total exposure |
|---|---|---|---|
| Classified as **misreporting** [s.439(10)] | ₹12,345 | **₹24,690** (200%) | ₹37,035 |
| Classified as **under-reporting** [s.439(9)] | ₹12,345 | ₹6,173 (50%) | ₹18,518 |
| **s.439(8) exclusion applies** | ₹12,345 | **₹0** | ₹12,345 |

**On one invoice. A freelancer billing monthly has twelve.**

*(Add 4% cess to the tax figures; the slab depends on total income. The magnitudes are what matter.)*

## Why this reframes the entire product

We had been building a **calculator**. What we are actually building is **evidence for a statutory defence.**

The value is not "we compute your rupee figure." It is:

> **Large corporations have had a formal framework for uncertain tax positions since 2006 — FIN 48 / ASC 740-10-50 — with an inventory, a measurement, and a mandatory disclosure. Thomson Reuters sells software for it. A freelancer in Pune has a CoinGecko screenshot.**
>
> **We bring that discipline down to the transaction level: we generate the contemporaneous record that qualifies you for the Section 439(8) bona fide exclusion — turning a potential 200% penalty into a 50% penalty, or into none at all.**

**⚠️ Stated limitation (C31).** Section 439(8)(b) — the estimate exclusion — applies only where *"the accounts are correct and complete to the satisfaction of the Competent Authority."* The exclusion is not automatic. Our output supports disclosure of the basis; it does not fix bad bookkeeping. Say this out loud.

That is quantifiable, legally grounded, and it is an *insurance* value proposition rather than a *productivity* one. Insurance sells at a completely different price point than productivity software, which is why the ₹115/year anchor stops being relevant.

**It also settles the hardest objection to the whole project.** *"Does saying 'it's unclear' actually help anyone?"* — Yes. Indian tax law explicitly rewards disclosing the basis of an estimate. Statute, not opinion.

---

# PART 3 — THE FULL STAKEHOLDER MAP

We had three. There are seven, and two of the new ones matter.

| # | Stakeholder | What they need | What they do today | What it costs them | Would they pay? |
|---|---|---|---|---|---|
| 1 | **Freelancer / consultant** | A number they can defend | CoinGecko screenshot, an Excel row, hope | ₹0 today; ₹6,000–₹25,000 penalty per disputed invoice later | Not as productivity. **Yes as insurance**, if framed as penalty exposure |
| 2 | **Chartered accountant** | Coverage across every client transaction, and her own defensibility | Manual checklist, judgement, spot checks | Time, and professional exposure when a position she signed is challenged | **Yes** — this is the buyer |
| 3 | **⭐ Assessing officer** | A legible, consistent basis for the figure | Reads the return; asks questions; classifies under 270A | Time spent reconstructing intent | **Never pays — but their acceptance decides whether the product works at all** |
| 4 | **⭐ PI insurer for CAs** | Evidence that members exercised due diligence | Underwrites blind | Claims from negligence findings | **Plausibly** — a real distribution channel |
| 5 | **CBDT / regulator** | To know where the law has gaps | Reacts to disputes case by case | Litigation load, inconsistent outcomes | No — but aggregated lacuna data is a policy asset |
| 6 | **AI vendors** | Not to be the confident source of an indefensible position | Disclaimers | Reputational and eventual legal exposure | Long shot; interesting for year five |
| 7 | **Anyone using AI in a regulated domain** | Not to be silently fabricated at | Trusts the output | Unknown until it fails | The scale story |

## The two new ones, and why they matter

**Stakeholder 3 — the assessing officer — is the one we most underrated.** He never pays us a rupee, and he decides whether the product has any value at all. If our disclosure format is illegible or unfamiliar to him, the 270A(6) defence doesn't land and everything above collapses.

**Design consequence: build for the officer's eye, not just the CA's.** Which means: plain statutory language, the exact provision cited, the basis stated in the form the statute uses. This is a genuine, non-obvious design constraint that came out of mapping properly.

**Stakeholder 4 — the professional indemnity insurer — is a distribution insight.** Insurers already reward documented process in other professions. A CA firm that runs every cross-border receipt through a disclosure tool has an evidence trail. That is a channel where the payer is neither the sufferer nor the practitioner. Worth one line in Bounty 1; not worth building for now.

---

# PART 4 — DAY IN THE LIFE

## Priya — the freelancer

Priya is 29, a backend developer in Pune, four years independent. She bills three overseas clients; the American one started paying in USDC last year because a bank transfer took six days and cost him ninety dollars. It arrives in about forty seconds now and she likes that.

Her system is a spreadsheet. When a payment lands she opens CoinGecko, screenshots the price, pastes the number into a column, and moves on. She is aware this is not rigorous. She does it at eleven at night after client work, and it takes ninety seconds, and it feels like enough.

In July her CA asked what rate she had used. She said "the market rate." He asked which market, and she did not have an answer, and neither did he, and the conversation moved on because there were eleven other things to close before the deadline. She has never heard the word "lacuna." She has heard of the 30% crypto tax and assumes it applies to everything, which is wrong in a direction that could cost her.

**What she actually feels is not confusion. It is a low, deferred unease** — the sense of having taken a shortcut she cannot name, on something that might matter later. She will not pay ₹2,000 a year to feel better. She would pay to not receive a notice.

## Rajesh — the chartered accountant

Rajesh is 44, a four-partner firm in Bengaluru, roughly 300 individual clients. Maybe eighteen have foreign receipts, and four of those now involve crypto. He is competent and cautious, and he learned about VDA taxation the way most of his profession did — from webinars, TaxGuru posts, and a two-day scramble in 2022.

He knows the valuation question is unsettled. That is not his problem. **His problem is coverage.** Priya sends him a spreadsheet with forty rows in the second week of July. He cannot verify forty rate lookups against forty timestamps. He picks the largest three, checks those, forms a view, and signs.

The thing that actually keeps him up is not being wrong. It is being wrong *in a way he cannot show he thought about* — because Section 270A distinguishes an honest disputed position from a careless one, and the difference is 200% versus 50% versus nothing, and the evidence for which side you are on is documentation he does not currently have.

**He does not need to be told the law is unclear. He needs the ambiguity found in all forty rows, marked, and recorded — in a form an assessing officer will recognise.**

---

# PART 5 — THE ANTI-PERSONA, AND A REAL ETHICAL PROBLEM

## Who should not use this

**The motivated reasoner.** Someone who has already decided what number they want and needs a document that makes it defensible.

**This is not a hypothetical risk — it is created by our core design choice.** We show a range. A range with two legitimate endpoints is, from a certain angle, a menu. *"The tool said ₹4,73,250 was defensible, so I picked the lower one."*

We are, in effect, handing people a well-researched argument for the position that suits them.

## The mitigation, which turns out to improve the product

Do not just show the range. **Require an election and record it.**

> The output is not *"here is a range."* It is *"here is a range; record which one you are adopting and why; we will record permanently that you knew about the other."*

This changes the shape of the artefact:
- Cherry-picking becomes **disclosed** cherry-picking, which is precisely what s.439(8) rewards — a disclosed basis
- The record shows the taxpayer knew the alternative existed, which supports *bona fide*, not the reverse
- The user must make an active choice rather than accept a default, which is a known-good pattern for consequential decisions

**The risk becomes the feature.** The value was never the number — it was always the recorded reasoning.

**Add to the build: an election step in Node 7. About two hours. It closes the ethical hole and strengthens the legal one.**

## Other anti-personas

| Who | Why not | Response |
|---|---|---|
| Someone with no advisor who mistakes disclosure for compliance | Disclosure is not compliance. We say so — but they may not read it | "Not tax advice" must be structurally prominent, not a footer |
| Someone using "the law is unclear" as cover for aggressive positions | Only works if the ambiguity is real; our citation matcher means we can only claim a gap where the corpus shows one | The mechanical grounding is the guard |
| An enterprise wanting a compliance certificate | We do not issue certificates and never will | Out of scope, stated in `scope.md` |

---

# PART 6 — WHO IS HARMED IF IT WORKS BADLY

Failure modes are not symmetric, and that has a design consequence.

| Failure | Who is harmed | Severity | Design response |
|---|---|---|---|
| **False abstention** — says unclear when the law is clear | User pays for unneeded advice; mild loss of trust | 🟡 Low | Acceptable |
| **False confidence** — says clear when it is a lacuna | User files an indefensible position with no disclosure. **Loses the 270A(6) defence they would otherwise have had** | 🔴 **Severe** | Must be minimised at all costs |
| Fabricated citation accepted | User relies on a rule that does not exist | 🔴 Severe | Mechanical matcher; conclusion rejected on no match |
| Range enables cherry-picking | Revenue; and the user, if it reads as bad faith | 🟠 Medium | Recorded election (Part 5) |
| Wrong extraction, right reasoning | Correct method, wrong number | 🟠 Medium | Field-level confidence; low-confidence fields flagged |
| Corpus out of date after a Finance Act | Everyone, silently | 🟠 Medium | Version and date every corpus file; show the version in the output |

## The design principle this yields

> **Fail toward abstention.** When the system is unsure whether a question has an answer, it must say it does not know rather than guess. The cost of a false abstention is a wasted conversation. The cost of false confidence is the loss of a statutory defence worth up to 200% of the tax.

**This asymmetry should be stated explicitly in the documentation and defended in Q&A.** It is also why the abstention rate must be *measured* rather than merely minimised — we are deliberately biased in one direction and we should own that publicly rather than have a judge discover it.

---

# PART 7 — THE BUYER / SUFFERER SPLIT, STATED PLAINLY

For the pitch. Say this out loud; the rubric rewards it.

> The person with the problem is not the person with the budget. Priya feels the unease; Rajesh carries the liability and pays for software. That split is normal in professional services and it shapes what we build — the interface is for a CA reviewing forty transactions, not for a freelancer reviewing one. And the output has a third audience who never pays us at all: the assessing officer who has to find it legible.

**Three audiences, one artefact, and only one of them is the customer.** Knowing that is the difference between a product and a demo.

---

# PART 8 — WHAT THIS CHANGES FOR THE BUILD

| # | Change | Where | Why |
|---|---|---|---|
| **C5** | Add a **recorded election** step — user picks a method, system records they knew the alternative | Node 7 (Step 26) | Closes the cherry-picking hole; produces exactly what 270A(6) rewards |
| **C6** | Output must be **legible to an assessing officer** — plain statutory language, exact provision, basis stated in the statute's own terms | Node 7 + UX (Step 23) | Stakeholder 3 decides whether the product has value at all |
| **C7** | State **fail-toward-abstention** as an explicit design principle, and measure the rate | Docs + Step 21 | Asymmetric harm; owning the bias beats being caught with it |
| **C8** | **Version and date every corpus file**, and show the version in the output | Corpus (Step 9) | Silent staleness after a Finance Act is a real harm mode |
| **C9** | Reframe the pitch's value line from computation to **270A(6) evidence** | Problem statement (v3) | Quantified, statutory, and it answers the hardest objection |

---

# PART 9 — WHAT WE STILL DON'T KNOW

| # | Unknown | Why it matters | How to resolve |
|---|---|---|---|
| U6 | Would an assessing officer actually find our format legible and persuasive? | Stakeholder 3 gates everything | Ask a CA who has handled an assessment. **Highest-value interview question we now have** |
| U7 | Do CAs already produce anything like a disclosure note for disputed positions? | If yes, we should match their format, not invent one | Interview question |
| U8 | Has 270A(6) actually been invoked successfully on a valuation-method dispute? | Strengthens or weakens the whole economic case | Search ITAT decisions on 270A(6) bona fide + estimate |
| U9 | Would a CA pay, and how much? | The business model | Interview question — ask for a number, not a yes/no |
| U10 | Do PI insurers for Indian CAs reward documented process? | Distribution channel | Low priority; one search |

**U6 and U7 are now the most important questions in the interview script.** They were not in it before this step.

---

# PART 10 — SUMMARY

- **The buyer is the CA**, but not because she has money — because she carries liability she cannot currently evidence
- **The product is insurance, not productivity.** Section 439(8) makes that concrete: bona fide explanation with disclosed basis can mean 0% instead of 50% or 200%
- **There is a third audience who never pays and decides everything** — the assessing officer
- **Our range creates a cherry-picking risk**, and the fix (recorded election) makes the product better rather than merely safer
- **Failure is asymmetric.** False confidence costs a statutory defence; false abstention costs a conversation. Fail toward abstention, measure it, and say so
