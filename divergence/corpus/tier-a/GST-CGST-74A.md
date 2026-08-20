---
provision_id: GST-CGST-74A
current_citation: "Section 74A, CGST Act 2017"
former_citation: "Sections 73 and 74 — apply only up to FY 2023-24"
change_effective: 2024-08-16
tax_year_applicable: "FY 2024-25 onwards. OUR TRANSACTION IS FY 2026-27, SO THIS IS THE GOVERNING SECTION."
tier: A
citable: true
retrieved: 2026-08-06
source_url: "https://taxinformation.cbic.gov.in"
source_type: official
completeness: full
known_limitation: null
---

# Section 74A — Determination of tax … pertaining to Financial Year 2024-25 onward
<!-- VERBATIM-START -->

**(1)** *Where it appears to the proper officer that any tax has not been paid or short paid or erroneously refunded, or where input tax credit has been wrongly availed or utilised, he shall serve notice … requiring him to show cause as to why he should not pay the amount specified in the notice along with interest payable thereon under section 50 and a penalty leviable…:*
*Provided that no notice shall be issued, if the tax … in a financial year is less than one thousand rupees.*

**(2)** *The proper officer shall issue the notice under sub-section (1) within **forty-two months** from the due date for furnishing of annual return for the financial year to which the tax … relates to or within forty-two months from the date of erroneous refund.*

**(5)** *The penalty …—*
*(i) for any reason, **other than** the reason of fraud or any wilful-misstatement or suppression of facts to evade tax, shall be equivalent to **ten per cent. of tax due … or ten thousand rupees, whichever is higher**;*
*(ii) **for the reason of fraud** or any wilful-misstatement or suppression of facts to evade tax shall be **equivalent to the tax due** from such person.*

**(7)** *The proper officer shall issue the order … within twelve months from the date of issuance of notice … extendable by a maximum of six months.*

**(8)** *[Non-fraud voluntary payment] (i) before service of notice, pay tax + interest … no notice shall be served; (ii) pay tax + interest within **sixty days** of the show cause notice, and on doing so, **no penalty shall be payable**…*

**(9)** *[Fraud] (i) before notice: tax + interest + **15%** penalty; (ii) within sixty days of notice: tax + interest + **25%**; (iii) within sixty days of the order: tax + interest + **50%**.*

**(12)** *The provisions of this section shall be applicable for determination of tax pertaining to the **Financial Year 2024-25 onwards**.*

*Explanation 2.—"suppression" shall mean non-declaration of facts or information which a taxable person is required to declare … or failure to furnish any information on being asked for, in writing, by the proper officer.*

<!-- VERBATIM-END -->
---

# WHAT THIS MEANS FOR OUR CASE — with numbers

If the export zero-rating fails, there is no longer a single invoice value to run this on — `node3_valuation.py` returns a 12-figure lattice, ₹4,69,750.00 to ₹5,17,618.76 (see `canonical_case.json` / `valuation.json`). The exposure below is therefore a band, computed at both ends of that range, not a point:

| | Low end — ₹4,69,750.00 | High end — ₹5,17,618.76 |
|---|---|---|
| IGST @ 18% | **₹84,555** | **₹93,171** |
| Interest under s.50, one year @ 18% | ₹15,220 | ₹16,771 |
| Penalty 74A(5)(i) — **non-fraud** (10% or ₹10,000, higher) | ₹10,000 | ₹10,000 |
| **Total, non-fraud** | **₹1,09,775** | **₹1,19,942** |
| Penalty 74A(5)(ii) — **fraud** (equal to tax) | ₹84,555 | ₹93,171 |
| **Total, fraud** | **₹1,84,330** | **₹2,03,113** |

**On one invoice.** The exposure band moves with the valuation band — a ₹10,167 spread on the non-fraud total, a ₹18,783 spread on the fraud total — because there is no rule that picks a single point in either range.

## ⭐ AND HERE IS WHY DISCLOSURE MATTERS UNDER GST TOO

The difference between the two rows is **₹82,547** — and it turns entirely on whether there was *"fraud or any wilful-misstatement or **suppression of facts**."*

**Explanation 2 defines suppression as** *"non-declaration of facts or information which a taxable person is required to declare … or failure to furnish any information on being asked for."*

> **A contemporaneous record showing the position was disclosed and reasoned is evidence against suppression.**

**This is the same argument as s.439(8)(a) on the income-tax side, arriving independently in a different Act.** Two separate regimes, both of which reward having written down what you knew and why.

**That is a genuinely strong structural point: disclosure is not a nicety in Indian tax law. It is the hinge on which penalty turns, in both regimes.**

## The 42-month clock
Notice may issue within **42 months** of the annual return due date. For FY 2026-27 that runs well into 2031. **The exposure does not close quickly.**
