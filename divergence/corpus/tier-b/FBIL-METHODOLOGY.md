---
provision_id: FBIL-METHODOLOGY
current_citation: "FBIL Reference Rate — Methodology Document, Version 1, 11 June 2018"
tier: B
citable: false
citability_note: "Not a statutory provision -- no Rule or Section in the corpus names FBIL. Context for why the official reference rate does not answer the question; never usable as cited authority. Demoted from Tier A 2026-08-19."
retrieved: 2026-08-06
source_url: "fbil.org.in — FBIL Reference Rate Methodology Document"
source_type: official
completeness: full
known_limitation: "Version 1 dated June 2018. Check for later versions."
---

# FBIL Reference Rate — Methodology
<!-- VERBATIM-START -->

**4.1** *The USD/INR Reference Rate will be computed based on the data in respect of the actual spot US dollar/Indian rupee transactions taking place on electronic platforms during the **one-hour time window from 11.30 Hours to 12.30 Hours on each business day in Mumbai**. Normally, the data will be sourced from Thomson Reuters and CCIL platforms.*

**4.2** *The transactions data for a **'15 minutes' time-period within the one-hour time window … and selected randomly** will be used for computation of the USD/INR Reference Rate. The threshold criteria of **ten transactions with aggregate amount of USD 25 million** will be required to be met.*

**4.3** *A +/- 3SD rule will be applied … to remove the outliers. The Reference Rate will be set equal to the **volume-weighted average of the surviving transactions**, after the removal of the outliers.*

**5.1** *If the first randomly selected time-period of 15 minutes does not contain adequate number of transactions … a second random time-period of 15 minutes will be generated. **This process will be repeated up to a maximum of 5 times**.*

**5.2** *If all the 5 randomly selected time-periods fail … the transactions data pertaining to the whole one-hour window … will be taken into account.*

**6** *In case of systems/network failures, if adequate transactions data is still not available, the Reference Rate will be computed using **polled submissions** … a minimum of five quotes … the **mean of the surviving polled rates**.*

**11** *The FBIL Reference Rates will be published with effect from **July 10, 2018 at around 13.30 Hours on all business days, i.e., excluding Saturday, Sunday and bank holidays in Mumbai**.*

<!-- VERBATIM-END -->
---

# ⭐ A SIXTH UNDETERMINED ELEMENT — INSIDE THE OFFICIAL RATE ITSELF

Everything we have said about FBIL is now verified from the primary methodology document: **one hour, one rate, business days only, published around 13:30, excluding Saturdays, Sundays and Mumbai bank holidays.**

**But paragraph 4.2 says something we had not noticed.**

The rate is not computed from the whole hour. It is computed from **a 15-minute period selected at random** within that hour.

> ## **Even the official rate is the product of a random choice. A different 15 minutes would have produced a different number, and nothing determines which 15 minutes.**

And it is a **volume-weighted average of surviving transactions after outlier removal** — a statistical construct, not an observed price. And if the threshold is not met, the process reruns with a *different* random window, up to five times. And if that fails, it falls back to polled bank quotes instead of transactions entirely.

**So there is no such thing as "the exchange rate at a moment" even in the official system.** There is a randomly-sampled, outlier-trimmed, volume-weighted average of one quarter-hour, published three hours later, on weekdays only.

**This is the strongest available answer to "why not just use the official rate?"** — because the official rate is itself a choice among defensible constructions, made by a random number generator, and it does not exist at all on the day our payment landed.

## Relevance to our case, stated precisely
- Payment settled **03:14 IST, Sunday 28 June 2026**
- FBIL publishes only on Mumbai business days → **no rate exists for that date**
- Even on a business day, the rate reflects **11:30–12:30**, not 03:14
- **Rule 115 mandates the SBI TT buying rate, not FBIL, for income conversion** — and Rule 115 does not reach a VDA at all

**Four reasons the official rate does not answer the question, and the first two are in this document.**
