# FAILURE CATALOGUE
### Step 10 · Empty and ready to fill
**Owner: P2 · Started 6 August 2026**

---

## HOW TO FILL THIS

Run the frozen baseline (`baseline-prompt.md`) on each input, **five times**, in a **fresh session every time**. Paste the raw output. Then mark what failed.

**Two rules that decide whether this is evidence or decoration:**

1. **Record the successes too.** A file containing only failures is a highlight reel, and a judge will assume it is one.
2. **Sort by whether the user could tell**, not by what went wrong. That is the whole point — see the class definitions below.

---

## THE THREE CLASSES

| Class | Definition | Cost |
|---|---|---|
| **1 — Loud** | User notices immediately | ⚪ Near zero |
| **2 — Checkable** | Wrong, but verifiable with effort | 🟡 Real, a careful CA catches it |
| **3 — Silent** | **Cannot be detected by checking, because there is nothing to check against** | 🔴 **The reason this project exists** |

**The killer question, asked of every failure:**

> *Reading only this output, and not the source documents, would a competent CA have any reason to doubt it?*
>
> **No → Class 3.** Yes with effort → Class 2. Yes immediately → Class 1.

---

## THE INPUTS

| # | Input | Type | Runs done |
|---|---|---|---|
| A1 | Clean invoice PDF + clean transaction record | 🟢 natural | 0/5 |
| A2 | Phone photo at an angle, slightly blurred | 🟢 natural | 0/5 |
| A3 | WhatsApp screenshot, counterparty is a handle only | 🟢 natural | 0/5 |
| B1 | Payment settling 03:14 Sunday 28 June | 🟡 selected | 0/5 |
| B2 | Payment dated 28–29 June 2026 | 🟡 selected | 0/5 |
| B3 | Question whose answer changed on 1 April 2026 | 🔴 constructed | 0/5 |
| B4 | Same input as A1, fast model vs reasoning model | 🟡 selected | 0/5 |
| B5 | Same transaction, February 2026 vs June 2026 | 🔴 constructed | 0/5 |

**Report natural, selected and constructed rates separately.** If every input is a trap you built, you have proved only that you can break a model — which nobody doubts.

---

## PREDICTED FAILURES — registered before running

| # | Failure | Class | Predicted rate | **Observed** |
|---|---|---|---|---|
| F1 | Silent rate selection — one figure, no mention a choice was made | 🔴 3 | ~100% | |
| F1c | Uses a rate source with **no legal standing** (interbank, not SBI TTBR) | 🔴 3 | ~80% | |
| F2 | Answers with no mention that FIRC/counterparty is absent | 🔴 3 | ~90% | |
| F3 | Stale or year-less citation | 🔴 3 | ~95% | |
| F4 | States FEMA as settled rather than inference | 🔴 3 | ~70% | |
| F5 | Fabricated citation | 🟡 2 | ~20% | |
| F6 | Regime collapse — income tax only | 🔴 3 | ~60% | |
| F7 | Single-event tax, misses the two-stage structure | 🟡 2 | ~50% | |
| F8 | Numeric / decimal / currency confusion | 🟡 2 | ~25% | |
| F9 | Date normalisation error | 🟡 2 | ~20% | |
| F10 | Entity confusion — trade vs legal name vs handle | 🟡 2 | ~40% | |
| F11 | Invents a rate for a non-publishing day | 🔴 3 | ~80% | |
| F12 | **Generic hedge instead of naming the real gap** | 🔴 **3** | ~85% | |
| F13 | Malformed output | ⚪ 1 | ~5% | |

**F12 is the experiment.** The prompt asks directly for anything unclear. Does it say *"no method is prescribed and I chose one"* — or does it say *"regulation is evolving, consult a professional"*?

---

## ⭐ OUR OWN FAILURES — naturally occurring, no test needed

These are real, they happened to us, and they belong in the catalogue.

| # | What we did | Class | Why it happened |
|---|---|---|---|
| **OWN-1** | Cited **Rule 11UA** after it became Rule 57 on 1 April 2026 | 🔴 3 | Every source agreed — because they were all reading each other |
| **OWN-2** | Cited **s.270A(6)** after it became s.439(8) | 🔴 3 | Same cause, two days later |
| **OWN-3** | Used the **interbank rate** for the headline figure, when Rule 115 mandates SBI TTBR | 🔴 3 | Took a number from a news report without checking whether its source had legal standing |
| **OWN-4** | Cited provisions **without stating the tax year**, when both numbering systems are live | 🔴 3 | Never occurred to us that the question had two correct answers |
| **OWN-5** | Our own citation matcher's self-test asserted **Rule 115 was current for FY 2026-27**, four months after it became Rule 206 | 🔴 3 | The test passed 15/15 the entire time. Found by `gate0_check.py` flagging two files claiming the same provision — not by anyone reading it |

**All five are Class 3. Four survived four adversarial research passes and were found by us, not by a judge. The fifth was found by the process itself.**

**Say this in the documentation:** *we built a system to catch confident answers on ground that has moved. It caught us four times. Then it caught its own test.*

---

## RAW OUTPUTS

Save every run to `runs/baseline/{model}/{input}/{n}.txt` and reference it here.

### ⬇ ENTRIES BELOW

*(none yet — the catalogue is empty until the first run)*
