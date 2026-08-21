# GAZETTE FINDINGS — what four rules of the Income-tax Rules, 2026 actually say

### Source: Notified Income-tax Rules, 2026 — Gazette of India Extraordinary, Part II Sec 3(i), 20 March 2026.
### Every quote below is verbatim text held in `corpus/tier-a/`, between that file's own `<!-- VERBATIM-START/END -->` markers. Nothing here is paraphrase presented as quotation.

---

## 1. Rule 57's catch-all does not reach the case, by the drafter's own column B

Rule 57 opens: *"For the purpose of following sections referred to in **column B** of the Table below, the fair market value of the property of the nature referred to column C shall be determined in the manner provided in column D thereof."*

Row 7 is the residual catch-all: **column B — Section 26(2)(j) only**; column C — *"any other property other than referred to at Sl. Nos. 1 to 6 above."* Column D gives it an open-market-price method.

**Section 92 — the provision that actually taxes this receipt — is not in column B for rows 6 or 7.** A reader who stops at column C sees a catch-all that looks broad enough to reach anything. Column B narrows it to a different section entirely. *(`corpus/tier-a/ITR2026-RULE-57.md`)*

The full research trail behind this finding — the 1962 provenance of each
row (Rule 57 consolidates three older rules, and each row keeps its
parent's scope), the verification status of each claim, and why this holds
across both the 2025 and 2026 tax-year numbering systems — is in
[`RULE-57-RESEARCH-TRAIL.md`](RULE-57-RESEARCH-TRAIL.md). That file is
**not** part of the live corpus (`citation_matcher.py` and the resolvers
only ever read `corpus/tier-a/` and `corpus/verbatim/`) — it is the working
research that fed into the corpus file and this summary, kept visible
rather than deleted once the corpus file itself was finalized. Renamed
21 August, out of `corpus/tier-a/ITR2026-RULE-57.md`'s exact filename, to
remove a real point of confusion: the two files had drifted to different
retrieval dates and different levels of detail, sitting under an identical
name in two different folders — the same *shape* of risk as the shadowing
bug D44 fixed, though not a live one, since no code ever read the root
copy.

---

## 2. Rule 206 cites an Act repealed twenty-six years before this gazette was printed

Rule 206(3), notified 20 March 2026: *"…in accordance with the provisions of the **Foreign Exchange Regulation Act, 1973 (46 of 1973)**."*

FERA 1973 was repealed by the Foreign Exchange Management Act, 1999, effective 1 June 2000. Machine-counted across the entire notified Rules 2026: *"Foreign Exchange Regulation Act, 1973"* appears **once** — Rule 206(3). *"Foreign Exchange Management Act, 1999"* appears **three times**, including in Rule 210, four rules later in the same page range.

**The stale citation sits in the rule that governs converting this freelancer's income into rupees — not in a footnote, in the operative sub-rule.** *(`corpus/tier-a/ITR2026-RULE-206.md`)*

This is logged in `step22drop/iteration-log.md`'s failure catalogue as **DRAFTER-1** — the one stale citation in this project that is not our own error or a commentator's, but the notified instrument's.

---

## 3. Rule 206 borrows Rule 207's definition and leaves Rule 207's remedy behind

Rule 206(2)(a): *"'telegraphic transfer buying rate' shall have the meaning assigned to it in **rule 207**."*

The sentence being borrowed from, Rule 207(1): *"…shall be the telegraphic transfer buying rate of such currency as on the date on which such tax is required to be deducted…; **but where the telegraphic transfer buying rate is not published on such date, the last such published rate may be taken.**"*

Rule 207 (payments **out**, to a non-resident) keeps both halves — the definition and the fallback for an unpublished rate. Rule 206 (receiving, as a resident) reaches into the same sentence for the definition, and stops there. **No fallback survives the crossing.** This is the same asymmetry as Rule 57's column B: a clause that looks like it reaches further than it does, once you check what was actually carried across. *(`corpus/tier-a/ITR2026-RULE-206.md`, `ITR2026-RULE-207.md`)*

---

## 4. Rule 247 names a valuer of virtual digital assets, and gives that valuer nothing

Rule 247(4): *"No person shall qualify for registration as a valuer, other than as a valuer of works of art **or virtual digital assets** or other class of assets as may be specified by the Board in this behalf, if he is employed under Government or any other employer."* Form No. 169, Note 6 repeats the same phrase.

The category is written into the gazette twice. What the category is actually given:

| A valuer of VDAs would need | What the Rules provide |
|---|---|
| A class of asset to register for | Form 169 lists **eleven** classes. VDA is not one of them — the applicant selects "Any other asset" |
| Prescribed qualifications | Rule 247(3): for assets outside sub-rule (2), qualification *"shall be determined by the [Commissioner]… and the decision… **shall be conclusive**"* — officer discretion, no criteria |
| A method to apply once registered | Rule 57 — zero references to virtual digital assets |

**The other locked doors in this project are absences — a rule that never mentions the asset class.** This one is a presence: the drafter wrote "virtual digital assets" into a sub-rule while declining, three sub-rules over, to give that named profession a class, a qualification standard, or a method. *(`corpus/tier-a/ITR2026-RULE-247.md`)*

---

## Why this file exists

Four separate findings, four separate rules, one instrument, one reading pass.
Referenced from `README.md`'s "What the gazette gave us" — this file is the
citations and quotes behind that summary, not a restatement of it.
