---
provision_id: ITR2026-RULE-57
current_citation: "Rule 57, Income-tax Rules, 2026"
former_citation: "Rules 11UA, 11UAA and 11UAB, Income-tax Rules, 1962"
change_effective: 2026-04-01
tax_year_applicable: "FY 2026-27 onwards cite Rule 57. FY 2025-26 and earlier cite Rule 11UA / 11UAA / 11UAB as applicable."
tier: A
citable: true
retrieved: 2026-08-06
revised: 2026-08-09
source_url: "Notified Income-tax Rules, 2026, Gazette of India Extraordinary Part II Sec 3(i), 20 March 2026, pp. 1575-1576"
source_type: official_gazette
completeness: full_table
extract_scope: "Rule 57 opening words and the complete Table, all seven rows, columns B and C. Column D reproduced for rows 6 and 7 only."
known_limitation: "Table read from a text extraction of the gazette PDF, not from the page image. Row-to-column association CORROBORATED independently by the 1962 provenance of each row (see VERIFICATION below), but the page image has still not been read. Recompute text_sha256 after review."
supersedes_note: "Replaces the 2026-08-06 version of this file, which showed rows 1-4 and marked row 5 as inferred. Rows 5, 6 and 7 are now read directly. The earlier version's known_limitation is CLOSED."
---

# Rule 57, Income-tax Rules, 2026 — Determination of fair market value
## ✅ COMPLETE TABLE. All seven rows.

**57. Determination of fair market value.–** *For the purpose of following sections referred to in column B of the Table below, the fair market value of the property of the nature referred to column C shall be determined in the manner provided in column D thereof:*

| Sl. | **B — Section** | **C — Nature of property** | **D — Manner** |
|---|---|---|---|
| 1 | Sections **26(2)(j)** and **92** | Jewellery | open market price / invoice value / registered valuer above ₹50,000 |
| 2 | Sections **26(2)(j)** and **92** | Archaeological collections, drawings, paintings, sculptures or any work of art | as row 1 |
| 3 | Sections **26(2)(j)** and **92** | Quoted shares and securities | stock exchange transaction value, else lowest quoted price |
| 4 | Sections **26(2)(j)**, **72** and **92** | Unquoted equity shares | (A + B + C + D − L) × (PV)/(PE) |
| 5 | Sections **26(2)(j)**, **72** and **92** | Unquoted shares and securities (other than equity shares in a company) which are not listed in any recognised stock exchange | *"The price it would fetch, if sold in the open market on the valuation date and the assessee may obtain a report from a merchant banker or an accountant in respect of such valuation."* |
| 6 | **Section 26(2)(j)** *only* | Immovable property being land or building or both | *"The value adopted or assessed or assessable by any authority of the Central Government or a State Government for the purpose of payment of stamp duty in the respect of such immovable property on the valuation date."* |
| 7 | **Section 26(2)(j)** *only* | **"Any other property other than referred to at Sl. Nos. 1 to 6 above."** | ***"The price that such property would ordinarily fetch on sale in the open market on the valuation date."*** |

---

# ⭐⭐⭐ THE RESIDUAL CLAUSE — AND WHY IT DOES NOT REACH OUR CASE

**Rule 57 contains a residual valuation method.** Row 7 catches *"any other property"* and values it at open market price. Any competent reader — a judge, an assessing officer, a CA in Q&A — will find it and ask why it does not answer our question.

**It does not answer it because of column B.**

Rows 1 to 5 serve **section 26(2)(j) and section 92**. Rows 6 and 7 serve **section 26(2)(j) alone.**

> **For property received under section 92 — the provision the Act expressly extends to virtual digital assets — the table enumerates five property types and stops. The catch-all that would have caught a VDA is, by its own column B, unavailable to that section.**

This is not an argument from silence. **The residual clause exists, and the drafter pointed it somewhere else.**

---

# ⭐ WHY THE ASYMMETRY IS THERE — THE 1962 PROVENANCE

Rule 57 is a **consolidation of three 1962 rules**, and each row keeps the scope its parent rule had. Confirmed from the official rule-mapping table (`navigatorIncometaxRules2026.pdf`, row 57): **"11UA / UAA / UAB"**.

| 2026 rows | 1962 parent | Parent's scope |
|---|---|---|
| Rows 1–5 | **Rule 11UA(1)** | *"For the purposes of **section 56** of the Act…"* → s.56(2)(x) → now **s.92** |
| Row 6 | **Rule 11UAB(1)(i)** | s.28(via), inventory converted to capital asset → now **s.26(2)(j)** |
| **Row 7** | **Rule 11UAB(1)(iii)** | **s.28(via) only** |

**Rule 11UAB(1)(iii), inserted by Notification 42/2018 with effect from AY 2019-20:**
> *"being the property, other than those specified in clause (i) and clause (ii), the price that such property would ordinarily fetch on sale in the open market on the date on which the inventory is converted into, or treated, as a capital asset."*

Word for word, row 7's column D — with only the valuation date generalised.

> **The residual method has existed in Indian law since 2018. It has always been attached to inventory conversion, never to the receipt of property. In March 2026 the drafter consolidated both rules into a single table — and left the asymmetry intact.**

**Rule 11UA(1) has no residual clause at all.** Its sub-rule (1) has exactly three limbs: (a) jewellery, (b) artistic work, (c) shares and securities. The phrase *"any other property"* does not appear in it. Machine-checked against `IT-RULE-57.md`: **zero occurrences.**

---

# ✅ VERIFICATION STATUS — the three checks

**1. Read the gazette page image (pp. 1575–1576).** 🟡 **NOT DONE — but corroborated.**
The table was read from a text extraction, and row-to-column association in extracted PDF tables is exactly the thing that mangles silently. **However:** the 1962 provenance above independently predicts the same result — 11UAB contributes precisely an immovable-property row and a residual row, both scoped to s.28(via) alone. Two independent sources agree. **Treat as high-confidence but still read the page before it goes on a slide.**

**2. Confirm sections 92 and 26(2)(j).** ✅ **DONE — and it was already in the corpus.**
Column B of this very table is what established the mapping. **s.92 (2025 Act) = former s.56(2)(x). s.26(2)(j) (2025 Act) = former s.28(via).** Cite as *Section 92, Income-tax Act, 2025 (formerly s.56(2)(x))*.

**3. Check the residual clause in the 1962 rules for FY 2025-26.** ✅ **DONE. No divergence between tax years.**
Rule 11UA (s.56) has no residual. Rule 11UAB(1)(iii) (s.28(via)) has one. Same asymmetry, same allocation, both years. **The hoped-for "the same receipt gets a method in one year and none in the next" finding does not exist.** The position is stable across FY 2025-26 and FY 2026-27, which is a *better* result: nothing to explain away, and the claim holds whichever year the case falls in.

---

# ⚠️ AND THE SECOND SCOPING POINT STILL BITES — our case is not even a section 92 case

Our freelancer received USDC **as consideration for professional services**. That is business income under section 28 of the 1961 Act — not a receipt without consideration.

| Situation | Position |
|---|---|
| VDA received as a **gift** (s.92 / former s.56(2)(x)) | Statute demands a prescribed method. Table stops at row 5. **None prescribed.** |
| VDA received as **payment for services** | **No FMV rule is scoped to this head at all.** Not one that omits VDAs — none. |
| Inventory converted to capital asset (s.26(2)(j)) | ✅ Residual method available, row 7 |

**Our case is the second row. The gift recipient at least has a statute pointing at an incomplete table. She has nothing pointing anywhere — while the person converting stock-in-trade gets a catch-all.**

---

# LANGUAGE

❌ *"Rule 57 says nothing about crypto."*
❌ *"Rule 57 contains zero VDA references."* — true, but it invites *"so use the general principle"*, and there is one.

✅ **"Rule 57 has a residual valuation method for any other property. It is available to section 26(2)(j) and not to section 92. A virtual digital asset received under section 92 falls past the last row of the table — and our case is not even a section 92 case."**

---

## Provenance
- Rule 57 table: Gazette of India Extraordinary Part II Sec 3(i), 20 March 2026, pp. 1575–1576, text extraction
- Rule mapping 57 ← 11UA/11UAA/11UAB: `navigatorIncometaxRules2026.pdf`, official mapping table
- Rule 11UAB text: incometaxindia.gov.in and Notification 42/2018 dated 30 August 2018, retrieved 9 August 2026
- Rule 11UA absence of residual clause: machine-checked against `IT-RULE-57.md`, 0 hits for "any other property"
