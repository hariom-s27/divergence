# STEP 7 — RESEARCH AUDIT AND GAP CLOSURE
### Deliverable · 4 August 2026
*Three gaps closed · one gap nobody spotted · one claim that must be reworded · and a story we did not expect to find*

---

# THE HEADLINE

We went looking for three gaps. We found four. **And the fourth one is the project happening to us.**

We have been citing **Rule 11UA** as the central fact of the entire project — "the rule that covers property, jewellery and shares was never extended to digital assets." That citation was correct. It stopped being correct on **1 April 2026**, when the Income-tax Rules, 1962 were replaced and everything was renumbered.

Rule 11UA is now **Rule 57**.

Our citation was fluent, plausible, well-sourced, and stale. Nobody caught it — not four deep research passes, not the fact-check, not us. **That is exactly the failure our system is being built to detect**, and we just did it to ourselves, on our own headline fact.

This is now one of the best things in the project. More on why below.

---

# PART 1 — THE FOUR GAPS

## GAP 1 — Section numbers under the Income-tax Act, 2025

### ✅ Closed (partially)

**Section 194S is now Section 393(1), Table Sl. No. 8(vi).** <cite index="39-1">The earlier Section 194S of the Income-tax Act, 1961 is now covered under Section 393(1) [Table: Sl. No. 8(vi)], effective from 1 April 2026, retaining the provisions on deduction of tax at source on transfer of virtual digital assets.</cite>

The change is structural, not cosmetic. <cite index="42-1">The 194-series has been eliminated entirely. Sections 392, 393 and 394 replace 194C, 194J, 194I and all other TDS sections. Payments are now identified by table references and serial numbers, and by numeric payment codes (1001–1067), rather than individual section numbers. Rates and thresholds are unchanged — only the referencing format.</cite>

**So the correct citation is:** *Section 393(1), Table Sl. No. 8(vi), Income-tax Act, 2025 (formerly Section 194S, Income-tax Act, 1961).*

### ⚠️ Still unresolved: the new numbers for s.115BBH and s.2(47A)

Every practitioner source we found — including material published in mid-2026 — **still cites the 1961 numbering** for these two. That is itself informative: the profession has not fully migrated, and both numbers remain in active use.

**Do not guess these.** Our approach: cite both, in this form —

> *Section 115BBH, Income-tax Act, 1961 (carried into the Income-tax Act, 2025; new section number to be confirmed against the bare Act at indiacode.nic.in)*

Citing honestly with the gap stated is safer than a confident wrong number — and it is, pleasingly, exactly the behaviour our product is designed to produce.

---

## GAP 2 — Is the data.gov.in RBI resource live?

### ❌ Unresolved — and it cannot be closed by searching

This one needs a hand. Somebody has to register for a free API key, call the endpoint, and see what comes back for a specific date.

**This is now bundled with the kill-gate check.** When P3 pulls the rate data for 28–29 June 2026, they should test data.gov.in in the same sitting.

**Fallback if it fails:** Rule 115 mandates the **SBI Telegraphic Transfer Buying Rate**, not the FBIL rate, for income conversion. <cite index="54-1">Rule 115 removes the guesswork by mandating a single source — you are legally required to use the TTBR of the State Bank of India, and using an average rate is legally incorrect.</cite> So SBI TTBR is arguably the *more* correct source for the income leg anyway, and it is published as a daily chart rather than an API.

**An important wrinkle worth noting in the pitch:** <cite index="54-1">for rare currencies where SBI has no rate, you may need to convert to a major currency first and then to INR, or consult a professional for the RBI-approved secondary method.</cite> **SBI does not quote USDC at all.** So Rule 115 — the one conversion rule that *is* prescribed — does not cleanly apply to our case either. That strengthens the lacuna argument rather than weakening it.

---

## GAP 3 — Do Koinly and KoinX disclose their rate choice?

### ✅ Closed — and our claim was too strong. It must be reworded.

**Koinly does disclose.** <cite index="48-1">For trades where no fiat is involved, Koinly uses average market rates from the largest aggregators such as CoinMarketCap or CoinGecko, and you can see the source of the market rate and which asset's price was used in the transaction details. Where the base currency differs from the fiat currency traded, Koinly uses exchange rates on the day from the European Central Bank.</cite>

And the source label does appear in exports, not only in help documentation — a user forum post quotes a line from a tax report reading <cite index="46-1">"@ CHF0.00 per STT, source: market (StarTerra)"</cite>.

**So "every tool picks one silently" is false as written, and a judge could disprove it in about thirty seconds.** We must change it.

### The reworded claim — which is sharper than the original

> Koinly discloses **which aggregator** it used and converts to INR using **European Central Bank daily forex rates**. It does not tell you that FBIL exists, that Rule 115 mandates the SBI TTBR, that the Indian exchange price differed by 8.5% on 28–29 June, or that the choice between these is unresolved in Indian law.
>
> **It discloses the input. It does not disclose the decision.**

That last line is the whole product in eight words, and it is now defensible rather than exaggerated.

### The detail that makes this land

**Koinly converts to INR using a European central bank's rate.** For an Indian taxpayer that has no standing whatsoever in Indian tax law — FBIL and SBI TTBR do; the ECB does not. Koinly is not doing anything wrong; it is a global tool applying a global default. But an Indian user reading "source: market" has no way to know that the rupee figure was built on a European reference rate.

**This is a much better example than "it picks silently."** It is specific, verifiable from the vendor's own documentation, and not an accusation of bad faith — which makes it credible rather than combative.

---

## GAP 4 — The one nobody listed ⭐

### The Income-tax Rules, 1962 were replaced and renumbered on 1 April 2026

A published rule-mapping table shows the migration. <cite index="56-1">Rule 57 of the 2026 Rules corresponds to Rules 11UA and 11UAA of the 1962 Rules — "Determination of fair market value." Rule 56 corresponds to 11U, Rule 53 to 11UAE, and Rule 52 to 115A.</cite>

**So Rule 11UA is now Rule 57.**

### Why this is a genuine problem

1. **Our corpus was going to contain retired rule numbers.** Our citation matcher would have been matching against the wrong text.
2. **Our headline fact was stated with the wrong citation.** Correct until 1 April 2026, wrong after.
3. **We would have been caught by any judge who checks**, and the fact-check is a thirty-second search.
4. **The new number for Rule 115 itself (rate of exchange for income) is still unconfirmed.** We found 115A → Rule 52, but not 115. Mark unresolved.

### Why it is also the best thing we found

We ran four deep research passes designed to disprove our own thesis. A separate fact-check. A red-team review. **None of them caught this**, because every source we read — including material published in mid-2026 — still says "Rule 11UA," and it all agreed with each other.

That is precisely the failure mode we are building a system to detect: **a confident, fluent, well-sourced answer whose ground has moved.**

**We are the case study.** And that is worth more in a pitch than any abstract argument.

---

# PART 2 — WHAT THIS CHANGES

## C10 — A new test case, and it may be the best one we have

Build a test case where **the correct answer changed on 1 April 2026**.

Ask both systems: *"Which rule prescribes the method for determining fair market value under the Income-tax Rules?"*

The single prompt will almost certainly answer **Rule 11UA** — confidently, because its training data says so, because most of the internet still says so, and because every practitioner article published this year still says so.

Our pipeline, with a dated and versioned corpus, answers **Rule 57 of the Income-tax Rules, 2026**, and can show *when* the change happened.

**Why this test case is exceptional:**
- The failure is **verifiable in thirty seconds** by any judge with a phone
- It is not a trick question — it is the single most-cited rule in this domain
- It demonstrates **staleness**, a failure type distinct from hallucination and distinct from a lacuna, which broadens the argument
- **We can honestly say we found it by catching ourselves**, which is a far better story than "we constructed a test case"

## C11 — Corpus versioning is no longer a nice-to-have

Decision D26 said "version and date every corpus file." We made that decision for a theoretical reason. It now has a concrete one, and every file needs:

```
Provision: Rule 57, Income-tax Rules, 2026
Formerly: Rule 11UA, Income-tax Rules, 1962
Retrieved: 2026-08-04
Source: <url>
Superseded on: 2026-04-01 (1962 Rules replaced)
```

The output should show the corpus version. This is also the honest answer to *"how do we know your rules aren't out of date?"* — you don't, but you can see exactly when we last checked.

## C12 — Every citation in the pitch needs a re-check pass

Not just the ones we found. Anything citing the 1962 Rules or the 1961 Act needs the dual form: **new number, old number in brackets, and the date the change took effect.**

## C13 — Rewrite the competitor claim everywhere

"Every tool picks one silently" → **"They disclose the input. They do not disclose the decision."**

---

# PART 3 — AUDIT STATUS OF THE EXISTING RESEARCH

| Finding | Status | Action |
|---|---|---|
| No prescribed VDA valuation method exists | ✅ **Reusable** — the substance holds | Update citation to Rule 57 (formerly 11UA) |
| FBIL publishes daily, weekdays only, random 11:30–12:30 window | ✅ Reusable | None |
| USDT ₹102.88 vs interbank ₹94.65, 28–29 June 2026 | ✅ Reusable | Verify against raw data when pulled |
| ₹41,150 on a $5,000 invoice | ⚠️ **Verify** | Recompute from cached data |
| Two-stage income tax treatment | ✅ Reusable | None |
| s.194S → **s.393(1), Table Sl. No. 8(vi)** | ✅ **Corrected** | Use the new citation |
| s.115BBH, s.2(47A) new numbers | ❌ **Unresolved** | Cite both forms with the gap stated |
| Rule 11UA → **Rule 57** | ✅ **Corrected** | Update corpus and all pitch material |
| Rule 115 new number | ❌ **Unresolved** | Check indiacode |
| IGST s.2(6) five conditions | ✅ Reusable | GST law unaffected by this renumbering |
| FEMA ss.2(n), 7, 8 | ✅ Reusable | Unaffected |
| Section 270A(6) exclusions | ⚠️ **Verify** — 270A is a 1961 Act section; it has a 2025 equivalent | Find the new number |
| 44,057 CBDT communications | ✅ Reusable | None |
| Koinly "picks silently" | 🔴 **Discard and rewrite** | Use the reworded claim |
| Blockchain, EAS, DPDP, evidence law | ⏸ Not needed for this track | Archive |

---

# PART 4 — WHAT IS STILL UNRESOLVED

Stated openly, because the rubric rewards knowing the limits of your own research.

| # | Unresolved | How to close |
|---|---|---|
| U11 | New section numbers for 115BBH, 2(47A), 270A under the 2025 Act | indiacode.nic.in bare Act — one careful hour |
| U12 | New rule number for Rule 115 (rate of exchange for income) | Same mapping table, extended |
| U13 | Is data.gov.in's RBI resource live and does it cover our dates | Register for a key and call it — cannot be searched |
| U14 | Does KoinX (India-specific) disclose its rate source in the export? | Sign up for the free tier and generate a report |
| U15 | Does SBI publish historical TTBR charts we can retrieve? | Check sbi.co.in |

**U11 is the one to do first.** Wrong section numbers in a live Q&A is the single most avoidable way to lose credibility in this project.

---

# PART 5 — THE LESSON WE ACTUALLY LEARNED

We built a system to catch AI giving confident answers on ground that has moved. Then we did it ourselves, with our own headline fact, despite four adversarial research passes specifically designed to find our errors.

**Three things follow from that:**

1. **Consensus is not verification.** Every source we read agreed with each other, and all of them were reading each other. Agreement between secondary sources tells you they share a source, not that they are right.

2. **Dates matter more than we treated them.** Not "is this true" but "**true as of when**" — which is why corpus versioning moved from a nice-to-have to a requirement.

3. **This is now the best story in the pitch.** Not *"AI gets things wrong"* — everyone says that. But *"we built a system to catch this, and it caught us"* is specific, honest, verifiable, and slightly funny. Judges remember that.

**Use it as the opening of the Technical Execution section of the documentation.**
