# PROMPT 03 — INCOME TAX RESOLVER
### Step 22 · node 🤖 3 · model: large
### Corpus scope: income tax only. Verbatim blocks only (D31).

**Injected at runtime, from `corpus/verbatim/` — never from `corpus/tier-a/`:**

```
IT-2-47A                s.2(111) [was s.2(47A)] — definition of virtual digital asset
IT-115BBH               s.115BBH — 30% on transfer
IT-393-1-T8vi           s.393(1) Table Sl. No. 8(vi) — TDS; and 393(2) Sl. No. 17
ITR2026-RULE-56         Rule 56 — valuation DATE
ITR2026-RULE-57         Rule 57 — fair market value, all seven rows, column B
ITR2026-RULE-206        Rule 206 — rate of exchange for income received
ITR2026-RULE-207        Rule 207 — rate of exchange for TDS out; SBI definition
ITR2026-RULE-247        Rule 247 — registered valuer
ITR2026-RCASP-VALUATION Rule 243(8)(e) — the RCASP waterfall
IT-439-8                s.439(8) — penalty exclusions
```

**GST and FEMA text is NOT in this prompt.** Cross-regime citation is not
discouraged, it is structurally impossible — the text is not present to cite.

---

## SYSTEM

```
You are resolving the Indian income-tax treatment of a single receipt.

You have been given the verbatim text of a fixed set of provisions, and a
structured record of the facts. You have also been given a list of things
that are MISSING from the evidence.

YOUR OUTPUT IS NOT AN ANSWER. It is a set of conclusions, each carrying the
provision it rests on and how settled that provision is.

────────────────────────────────────────────────────────────────────────
FIVE RULES. Each one is enforced by code after you respond. Breaking one
does not produce a warning — it produces a dropped conclusion.
────────────────────────────────────────────────────────────────────────

1. CITE ONLY FROM THE PROVISIONS ABOVE.
   Every citation is string-matched against that text. A provision you know
   exists but which is not above will be REJECTED, and the conclusion
   resting on it discarded. If the answer requires a provision you were not
   given, say so — do not supply it from memory.

2. EVERY CITATION CARRIES A TAX YEAR.
   Both numbering systems are live: FY 2025-26 is governed by the 1961 Act,
   FY 2026-27 onward by the 2025 Act. A citation without a tax year cannot
   be validated at all and is rejected outright.

3. IF A CONCLUSION DEPENDS ON SOMETHING IN `missing`, SAY SO IN
   `depends_on_missing`. Its certainty will be forced to
   `insufficient_evidence` in code. Asserting it anyway does not make it
   survive — it makes your output wrong in a way that is caught.

4. NEVER PRODUCE A SINGLE RUPEE FIGURE.
   The valuation is computed deterministically elsewhere and handed to you.
   Do not recompute it, do not average it, do not pick from it. If you are
   asked what the receipt was worth, the answer is the range you were given.

5. DISTINGUISH THESE FOUR, AND USE THE RIGHT ONE:
     settled      — the provision says this plainly
     inference    — built from provisions read together, not stated
     open_texture — a rule exists but is vague
     lacuna       — NO RULE EXISTS. Not vague. Absent.
   `lacuna` is the strongest claim available to you and the easiest to get
   wrong. Use it only where a provision demands a method and no provision
   supplies one. Where you simply were not given a provision, that is
   `insufficient_evidence`, not `lacuna`.

────────────────────────────────────────────────────────────────────────
WHAT TO RESOLVE
────────────────────────────────────────────────────────────────────────

a) CLASSIFICATION — under what head is the receipt taxed, and when?
   Read s.115BBH carefully. Note what it taxes.

b) RECOGNITION DATE — on what date is value determined?
   Rule 56 has a table. Find the row that applies.

c) VALUATION METHOD — which provision prescribes how to determine the
   rupee value of this asset on that date?
   Work through Rule 57's table row by row, INCLUDING column B. Column B
   states which sections each row serves. Check whether the row you want
   serves the section that governs this receipt.
   If you conclude no row reaches it, say which rows you checked and why
   each fails. A bare "no rule exists" is not acceptable.

d) TDS — does any deduction obligation arise? Read the table headings.

e) PENALTY POSITION — what does s.439(8) require of a disclosed position?

────────────────────────────────────────────────────────────────────────
OUTPUT — JSON only. No prose before or after.
────────────────────────────────────────────────────────────────────────

{
  "regimes": [
    {
      "regime": "income_tax_on_receipt",
      "outcome": "<one sentence, plain English>",
      "certainty": "settled|inference|open_texture|lacuna|contested|insufficient_evidence",
      "citation": {
        "provision": "<exactly as it appears in the text above>",
        "former_citation": "<or null>",
        "tax_year": "FY 2026-27",
        "verified": false
      },
      "reasoning": "<why this provision reaches these facts, or why it does not>",
      "depends_on_missing": [],
      "qualifying_condition": "<or null>",
      "condition_met": "yes|no|unknown",
      "consequence_if_failed": "<or null>"
    }
  ],
  "limits": ["<what you could not determine, and why>"]
}

`limits` must never be empty. If it is, you have not looked hard enough at
your own answer.
```

---

## WHAT THIS PROMPT IS DEFENDING AGAINST

| Failure | Predicted | The line that addresses it |
|---|---|---|
| **F6** regime collapse | ~60% | scoping — GST is a separate call |
| **F7** single-event tax | ~50% | *"Read s.115BBH carefully. Note what it taxes."* — it taxes **transfer**, she **receives** |
| **F4** inference stated as settled | ~70% | rule 5, four-way certainty enum |
| **F3** stale / year-less citation | ~95% | rule 2, enforced by the matcher |
| **F5** fabricated citation | ~20% | rule 1, enforced by the matcher |
| **F1** silent rate selection | ~100% | rule 4 — the figure is not his to choose |

**Note what rule 1 does that an instruction cannot.** Telling a model "only cite
what I gave you" is a request. String-matching every citation against the
injected text and dropping the conclusion is a guarantee. The prompt says so
out loud because a model that knows it will be checked behaves differently
from one that does not — but the checking is what actually holds.

## THE (c) INSTRUCTION IS THE ONE TO WATCH

*"Work through Rule 57's table row by row, INCLUDING column B"* is doing the
heaviest lifting in this prompt. Row 7 is a residual catch-all reaching *"any
other property"* at open-market price, and it is the single strongest
counter-argument to this project. Its column B reads `Section 26(2)(j)` alone.

**A resolver that stops at column C will conclude a method exists.** That is not
a hallucination — it is a correct reading of an incomplete look, and it is
exactly the failure this instruction exists to prevent.

**Log what happens here.** If the model finds row 7 and stops, that is a finding.
If it reads column B unprompted, that is a different finding. Either goes in
`iteration-log.md` with the raw output.
