# OBJ-1 — has software already solved this?

**Date checked:** 21 August 2026. Method: public web search plus direct
fetches of each product's own site, no login, no paid access. Not Firecrawl
(unavailable in this environment) — WebSearch/WebFetch used instead, same
goal: public, dated, independently checkable sources, not paraphrase from
memory. Every claim below is anchored to a URL a reader can open themselves.

## The question this answers

DIVERGENCE's central claim is that Indian tax law does not prescribe a
method for valuing a stablecoin/crypto receipt in INR, and that a system
which says so honestly is more useful than one that silently picks a number.
The obvious objection: commercial crypto-tax software already converts every
crypto receipt to INR for thousands of users. So they must have already
solved this. Do they say how, or do they just print a number?

## Findings, one product at a time

### KoinX — not disclosed
Checked: `koinx.com/in/crypto-tax-guide`, KoinX's own tax-guide and
transactions-page content, and a targeted search of `help.koinx.com`.
Every page that discusses valuation says the same thing at the same level of
generality — tax is computed on "fair market value... on the day you
received them" — and none of them names a price source, an exchange, a
timestamp within the day, or a fallback rule for a day with no published
rate. No page states whether the method used for a given transaction is
shown to the user in their report.
Sources: [koinx.com/in/crypto-tax-guide](https://www.koinx.com/in/crypto-tax-guide), [koinx.com/guides/transactions/how-to-add-analyze-transactions-koinx](https://www.koinx.com/guides/transactions/how-to-add-analyze-transactions-koinx)

### Catax — not disclosed
Checked: `catax.app/products`, India's first dedicated crypto tax product
per its own description (registered with India's MCA, DPIIT-recognised).
The products page states capital gains are computed from fair market value
but gives no price source, exchange, or timestamp, and does not say whether
a transaction's applied method is visible to the user.
Source: [catax.app/products](https://catax.app/products)

### Binocs — inconclusive, not confirmed either way
Checked: search results and the (apparently wrong / redirected) binocs.co
domain, which resolved to an unrelated due-diligence company, not the crypto
tax product. Could not reach Binocs' own help documentation directly in this
pass. Reported here as **not verified**, not as "not disclosed" — those are
different findings and should not be conflated.

**Follow-up, 21 Aug, with Firecrawl's real API (not available for the first
pass):** searched again specifically for Binocs' own methodology pages. The
TechCrunch coverage of Binocs sits behind a Cloudflare challenge page
Firecrawl's scrape could not pass; every other result was a general crypto-tax
guide from an unrelated product, not Binocs' own documentation. Still
**not verified either way** after two independent attempts with two different
tools — reported as a genuine dead end for this method, not left open by
omission.

### Koinly — DISCLOSED, the one exception
Checked: `support.koinly.io`'s own article on how it sets market price
(fetched via search since the help center blocks direct automated fetches
with a 403). Koinly states plainly: for crypto-to-crypto trades it uses
"average market rates from largest market aggregators like CoinMarketCap or
CoinGecko"; where an exchange (e.g. Coinbase) reports its own transaction
value via API, Koinly uses that instead, "as it's usually more accurate";
for base-currency conversion it uses European Central Bank rates; and where
no price is found at all, it shows a "Missing market price" warning and
lets the user manually assign a value rather than silently guessing.
Source: [support.koinly.io — How Koinly sets the market price for your transactions](https://support.koinly.io/en/articles/9489964-how-koinly-sets-the-market-price-for-your-transactions)

Koinly does not go as far as this project does — it does not report a
range or say when a receipt falls into a genuine legal gap, and it does not
specify which exact minute of a day its "average" spans — but it is real,
named, public disclosure of a method, which the other two products checked
do not have.

## What this means, both ways, honestly

**For KoinX and Catax:** they process the same undetermined receipts this
project studies and print a single INR figure without saying which rate
they used or when. That is not a criticism of those products — nothing in
Indian law requires them to say — but it is exactly this project's thesis,
demonstrated in shipping commercial software two Indian users are actually
filing returns with today. That is stronger evidence than an interview
would have been, because it's dated, public, and any reader can check it
themselves.

**For Koinly:** it discloses a method, so this project's contribution
narrows accordingly for a product like it — the gap DIVERGENCE closes for a
Koinly-like tool is less "no one names a source" and more "a single
disclosed average is still a choice among several defensible ones, and nothing
here tells the user when that choice is contested versus routine." That is
a real, narrower claim, not the sweeping one, and it is the honest one.

## Update, 21 Aug — four more products, and the honest narrowing

Each claim below independently verified against the vendor's own help
documentation before being written down, not relayed on trust.

### Four products, four different silent resolutions of the same contested question

The finding from the first pass ("two products print a figure with no
source named") understated it. The fuller picture: even among products
that DO disclose something, every one of them resolves a missing-price
receipt — this project's exact D1 fact pattern — differently, and
silently, with no flag that the resolution was a choice:

- **Koinly**, more precisely than the first pass found: on a genuinely
  missing price, its own help center states plainly, *"If you do not set
  the worth on transactions showing this warning, Koinly assumes $0.00 as
  the value of this transaction."* Disclosed, but the default is to
  erase the receipt's value, not to flag the gap the way this project's
  `missing[]` does.
- **CoinTracker** uses *"the opening price as of 12 AM UTC each day"* — the
  most precise timestamp found anywhere in this scan — and on a missing
  price it *"conservatively assumes the cost basis... based on nearby
  transaction values."* An estimate presented as a value, not a range.
- **CoinLedger**: a transaction with a missing historical price is
  *"skipped and not included in CoinLedger's final tax reporting
  calculations"* until the user manually supplies one. The receipt
  disappears from the report rather than being flagged as open.
- **Kryptos** *"auto-classifies every transaction as VDA income"* — the
  silent classification decision this project's own gap detector and
  resolver refuse to make without checking the facts first.

**Assume zero. Assume a neighbour's price. Drop the row. Auto-classify.**
Four products, four different silent resolutions of the identical
contested question, none of them disclosed as a choice to the filer.

### The honest narrowing — two products already do part of what this project claims as new

Said plainly, because a thesis built on honest disclosure cannot leave its
own novelty claim overstated for someone else to find first:

- **Clearbrief** already ships **patented, non-generative citation
  verification** for US case law: *"a semantic analysis score that
  compares each sentence to its cited source and flags low scores where
  the source does not appear to support the assertion,"* built on
  classical NLP rather than an LLM, specifically to avoid the checking
  tool itself hallucinating. **This project's `citation_matcher.py` is
  not the first mechanically-verified citation check to exist.** What it
  adds is domain and construct: Indian statutes (not US case law), dual
  live numbering systems, tax-year currency, and — with `scope_enforcer.py`
  (⚙ E) — scope reach specifically, which Clearbrief's own semantic-support
  scoring is a different, coarser question from (support vs. reach).
- **Thomson Reuters ONESOURCE Uncertain Tax Positions** has shipped for
  years: it keeps *"an organized inventory of all... positions, calculate[s]
  tax and interest for each one,"* and *"report[s] on them with a full
  audit trail."* **Quantifying the cost of a disputed tax position is not
  novel.** What ONESOURCE does not do, as far as this pass could verify:
  store or verify statutory citations, check numbering-system currency, or
  decline to produce a number when no rule prescribes one — this project's
  actual point of difference is refusing to collapse to a single figure,
  not the act of costing a dispute.

**Consequence for how this project describes itself:** "nobody mechanically
verifies citations" and "nobody quantifies a disputed position" are both
false, checkable in one search each, and should not appear in this
project's own claims. "Nobody does either of those things *for Indian
statutory tax law, with tax-year-aware dual numbering, refusing to collapse
the range to one number*" is the claim the evidence actually supports.

## What was not done, and why it's said here rather than left implicit

- Binocs was not confirmed either way. Do not cite it as a third silent
  case without checking its actual product documentation first.
- This did not check ClearTax's crypto module (named in the original
  instruction) — not reached in this pass. Same caveat: absence of a
  finding is not a finding of absence.
- Firecrawl (the sponsor tool this task was written for) was not available
  in this run; WebSearch/WebFetch were used instead, with the same
  citation discipline. If Firecrawl becomes available, re-running this
  check with it would give fuller page captures, not just search-indexed
  snippets, and is worth doing before final submission if time allows.
