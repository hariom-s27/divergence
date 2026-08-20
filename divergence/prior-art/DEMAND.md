# DEMAND — do real people actually hit this question?

**Date checked:** 21 August 2026. Method: Firecrawl's real search API
(`firecrawl_demand.py`, `FIRECRAWL_API_KEY` from the shell, never in a
file), six targeted queries across Reddit, CA practice forums, and
professional blogs. Raw search responses saved in `prior-art/raw/`.
Substitutes for practitioner interviews attempted from 6 August that got
no response in sixteen days — a stated, sourced substitution, not a claim
that interviews happened.

## The question this answers

Not "is crypto tax confusing" — that is well covered and off-topic. The
specific question this project studies is narrower: when a resident
receives a stablecoin or foreign-currency payment on a date with no
official rate, or when the law doesn't name a valuation method at all,
what happens? Do real people and practitioners hit exactly that gap, or is
it a corner case nobody actually reaches?

## Eleven real posts, collected across six searches

**On the exact "no rate published for this date" problem —**

1. [reddit.com/r/IndiaTax — "SBI TT buying rate for 2024"](https://www.reddit.com/r/IndiaTax/comments/1pvg35s/sbi_tt_buying_rate_for_2024/) — a person filing needs the SBI TT buying rate for 30 April and it was not published that day. This is D1's exact fact pattern (a settlement date with no published rate), for a different asset class, found independently on a public forum, not constructed for this project.
2. [reddit.com/r/IndiaTax — "Where to get Historical SBI TT rates and Stock Prices?"](https://www.reddit.com/r/IndiaTax/comments/1mtl3l1/where_to_get_historical_sbi_tt_rates_and_stock/) — someone filing FA/FSI schedules for the first time, unable to locate the historical rate data the return requires at all.
3. [reddit.com/r/IndiaTax — "Computing capital gain tax from sale of US stocks"](https://www.reddit.com/r/IndiaTax/comments/1s72hmv/computing_capital_gain_tax_from_sale_of_us_stocks/) — a reply states the convention as "use SBI TT buying rate for the last date of the month prior to the month in which you sold" — a practitioner-shared workaround stated as fact, not quoting any provision. This is exactly the unsourced-convention pattern `node3_valuation.py`'s own comments warn about ("that workaround has no statutory basis whatsoever").
4. [reddit.com/r/IndiaTax — "Form 67 — Which exchange rate should be used for..."](https://www.reddit.com/r/IndiaTax/comments/1ux5190/form_67_which_exchange_rate_should_be_used_for/) — a resident filing Form 67 for foreign tax credit, asking which exchange rate applies to foreign-sourced income, unresolved in the post itself.
5. [reddit.com/r/IndiaTax — "How to calculate total purchase value and sale..."](https://www.reddit.com/r/IndiaTax/comments/1u4pg7k/title_how_to_calculate_total_purchase_value_and/) — a US brokerage account holder asking how to convert purchase and sale value to INR for capital gains, same underlying question, different asset.

**On crypto/stablecoin receipts specifically —**

6. [caclubindia.com forum — "Freelancer Receiving Payments via Crypto — Tax Classification Help"](https://www.caclubindia.com/forum/freelancer-receiving-payments-via-crypto-tax-classification-help-612904.asp) — a freelancer asking how a crypto payment from a foreign client should be classified for tax, the same fact pattern as D1/C3/C4, on a real CA practitioner forum.
7. [caclubindia.com forum — "Tax on Bitcoin, Earn and investment"](https://www.caclubindia.com/forum/tax-on-botcoin-earn-and-investment-578914.asp) — a reply states the general FMV-on-date-of-receipt principle, without naming a rate source or method — consistent with the corpus finding that no method is prescribed, stated informally by a practitioner rather than derived from a specific rule.
8. [karboncard.com — "Blockchain & stablecoins (legal): What Indian Freelancers Must Know 2026"](https://www.karboncard.com/blog/blockchain-stablecoins-legal-india-freelancers) — a professional advisory blog aimed at exactly this project's user (a resident freelancer paid in stablecoins), general guidance rather than a specific valuation-method answer.
9. [solvlegal.com — "Accepting Crypto Payments from Foreign Clients: What FEMA Allows"](https://solvlegal.com/blogs/accepting-crypto-payments-from-foreign-clients-what-fema-allows/) — a legal advisory covering the FEMA side of the same fact pattern (crypto payment from a foreign client), the regime this project's own FEMA finding touches.

**On the law itself, from a practitioner audience —**

10. [caclubindia.com — "Income Tax Act 2025: Proposed Clauses w.e.f 1st April 2026"](https://www.caclubindia.com/articles/income-tax-act-2025-proposed-clauses-w-e-f-1st-april-2026-55659.asp) — a CA-audience article on the transition this project's own dual-numbering-system finding (D45's citation staleness work) is built around, independent confirmation the transition is a live practitioner concern, not a fictional framing device.
11. [caclubindia.com — "Comprehensive Comparison of Section Numbers: Income Tax Act 1961 vs Income Tax Act 2025"](https://www.caclubindia.com/articles/comprehensive-comparison-of-section-numbers-income-tax-act-1961-vs-income-tax-act-2025-53134.asp) — a practitioner-maintained mapping table between the old and new Act's section numbers, for the exact reason this project's citation matcher tracks `former_citation` per provision.

## What this shows, stated plainly

Every piece above is a real person or a real advisory practice hitting some part of the same problem this project studies: which rate, which date, no prescribed method, an old-to-new Act transition practitioners are actively tracking by hand. None of the eleven cites a single authoritative source for "which rate on which date" — reply #3 states a convention as fact with no provision behind it, which is the same failure mode this project's own thesis names: an unsourced practitioner workaround standing in for a rule that does not exist, indistinguishable from a real one unless someone checks.

No two sources here contradict each other outright — a stronger single finding would have been two CA firms giving opposite advice on the same fact pattern, and this pass did not surface that. What it found instead is arguably the more common real shape: not conflicting authority, but no authority at all, filled quietly by convention, on a public forum, in real filings, this year.

## What was not done

Titles and descriptions were collected via Firecrawl's search endpoint; full page scrapes were not attempted for every result (search already returned enough signal to paraphrase honestly, and several targets — Reddit specifically — are known to resist automated scraping). A deeper pass could fetch full thread content for the strongest candidates (1, 3, 4, 6) if more detail is needed before submission. No usernames or other personal details are included above — URL and date are the citable unit.
