# PROMPT 04 — GST RESOLVER
### Step 22 · node 🤖 4 · model: large
### Corpus scope: GST only.

**Injected from `corpus/verbatim/`:**

```
GST-IGST-2-6    IGST s.2(6) — export of services, five cumulative conditions
GST-CGST-50     CGST s.50 — interest
GST-CGST-74A    CGST s.74A — the governing demand section for FY 2024-25 onward
```

**No income-tax or FEMA text is present.** Rule 57, s.439(8) and FEMA s.3(c) are
not available to cite here, by construction.

---

## SYSTEM

```
You are resolving the GST treatment of a single supply of services.

The same five rules apply as in the income-tax resolver: cite only from the
text above, attach a tax year to every citation, declare any dependency on a
missing item, never produce a single rupee figure, and use the certainty enum
precisely.

────────────────────────────────────────────────────────────────────────
WHAT TO RESOLVE
────────────────────────────────────────────────────────────────────────

a) IS THIS AN EXPORT OF SERVICES?

   s.2(6) sets out conditions. Take them ONE AT A TIME. For each, state
   whether it is met, not met, or cannot be determined, and why.

   Do not summarise the test. Do not conclude "this is an export" or "this
   is not an export" until you have walked every condition. A conclusion
   that skips a condition is worse than no conclusion, because it looks
   complete.

   Pay particular attention to the condition about how payment was
   received, and quote it exactly rather than paraphrasing it.

b) IF ANY CONDITION IS NOT MET OR CANNOT BE DETERMINED —
   what follows? Which section governs a demand for the relevant period?
   Read the applicability sub-section before you cite it.

c) WHAT TURNS ON DISCLOSURE?
   s.74A sets penalty at different levels depending on the reason for the
   short payment. Identify what distinguishes the levels and quote the
   definition that governs it.

────────────────────────────────────────────────────────────────────────
OUTPUT — JSON only.
────────────────────────────────────────────────────────────────────────

{
  "regimes": [
    {
      "regime": "gst_export",
      "outcome": "<one sentence>",
      "certainty": "settled|inference|open_texture|lacuna|contested|insufficient_evidence",
      "citation": {"provision": "...", "tax_year": "FY 2026-27", "verified": false},
      "conditions": [
        {"condition": "<quote the condition>", "met": "yes|no|unknown", "why": "..."}
      ],
      "depends_on_missing": [],
      "consequence_if_failed": "<what happens if the supply is not zero-rated>"
    }
  ],
  "limits": ["..."]
}
```

---

## WHY THIS RESOLVER IS WORTH BUILDING

It is fourth in the build order, and it is where the **bigger number** lives.

On a ₹1,00,000 invoice:

| | |
|---|---|
| valuation spread @ ~10% | ~₹10,000 — **a disclosure question** |
| IGST exposure @ 18% | ~₹18,000 — **cash out of her own pocket, unrecoverable** |

If the receipt fails the payment condition in s.2(6), the supply is not an
export, is not zero-rated, and the tax is owed — **possibly after she filed an
LUT on the assumption that it was.**

## THE STRUCTURAL POINT THIS RESOLVER PRODUCES

Instruction (c) exists to surface something the project found late and has not
yet used well: **s.74A's penalty turns on suppression, and "suppression" is
defined as non-declaration of facts a taxable person is required to declare.**

That is the same hinge as s.439(8)(a) on the income-tax side — **arrived at
independently, in a different Act, by a different drafter.**

> Disclosure is not a nicety in Indian tax law. It is what penalty turns on,
> in both regimes, and the two regimes got there separately.

**That is the strongest structural argument in the project and it is currently
buried in a corpus file.** If this resolver runs and produces it from primary
text, it belongs in the video.

## WHAT THIS PROMPT IS DEFENDING AGAINST

| Failure | The line that addresses it |
|---|---|
| **F6** regime collapse | this call exists at all |
| Summarising a cumulative test | *"Take them ONE AT A TIME… a conclusion that skips a condition is worse than no conclusion, because it looks complete"* |
| **F3** citing ss.73/74 | *"Read the applicability sub-section before you cite it"* — they stop at FY 2023-24, and this was our own fourth stale citation |
