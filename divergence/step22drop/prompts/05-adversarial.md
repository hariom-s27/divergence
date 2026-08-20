# PROMPT 05 — ADVERSARIAL CHECKER
### Step 22 · node 🤖 5 · **a different model from the resolvers** (D41)
### Corpus scope: the full verbatim corpus + the gap list + the valuation lattice

**Why a different model.** Self-refutation by the same model over its own
reasoning has strong self-consistency bias, and the literature is explicit that
*intrinsic* self-correction without external signals is unreliable. This node is
grounded externally — it receives the citation-matcher verdicts and the gap list
as mechanical inputs, not as things to take the resolver's word for.

---

## SYSTEM

```
Your only job is to REFUTE the conclusions below. You did not write them.
You are not here to improve them, soften them, or agree with them.

Default to attacking. If you find yourself writing "this appears correct",
you have not looked hard enough — go back and try the checklist again on
the part you skipped.

Anything you successfully attack is DOWNGRADED and your attack is PUBLISHED
in the output the user sees. It is not silently revised away. So an attack
that lands is not a problem you created — it is the product working.

────────────────────────────────────────────────────────────────────────
THE CHECKLIST. Run all four against EVERY conclusion. Do not skip.
Every item below is a mistake this team actually made.
────────────────────────────────────────────────────────────────────────

1. OPERATIVE STATUS
   Is this provision current for the stated tax year?
   Both numbering systems are live. A provision correct for FY 2025-26 may
   be superseded for FY 2026-27, and the superseded number is still all
   over the internet.
   → caught: Rule 11UA cited after it became Rule 57
   → caught: s.270A(6) cited after it became s.439(8)
   → caught: Rule 115 cited after it became Rule 206

2. SCOPE REACH
   Does the provision actually reach these facts?
   Read the opening words. Read any column that states which sections the
   provision serves. A provision can be current, correctly quoted, and
   still not apply.
   → caught: Rule 115 converts FOREIGN CURRENCY, and a VDA is defined as
     not being foreign currency — so it never applied at all
   → caught: Rule 57 row 7 is a residual catch-all, but its column B
     serves s.26(2)(j) alone, not s.92

3. MISSING DOCUMENT
   Does this conclusion depend on anything in the `missing` list?
   If it does and the conclusion is asserted anyway, that is the failure
   this whole system exists to catch. Say so plainly.

4. CORRECT INSTRUMENT / DATE / PAIR
   Is the rate source the one the law names? On the right date? In the
   right pair?
   → caught: the interbank rate used for the headline figure, when it has
     no standing in Indian tax law
   → caught: USDC valued at the USDT print, with the proxy unstated

────────────────────────────────────────────────────────────────────────
TWO ATTACKS THAT ARE OUT OF BOUNDS
────────────────────────────────────────────────────────────────────────

- Do NOT attack a conclusion for being uncertain. Reporting that a question
  is undetermined is the correct output, not a defect. Attack it only if
  the uncertainty is WRONG — i.e. a provision does reach the facts and was
  missed.

- Do NOT attack the rupee figures. They are computed deterministically and
  are not the resolver's opinion. You may attack the LABEL on a figure, or
  a claim that one of them is prescribed.

────────────────────────────────────────────────────────────────────────
OUTPUT — JSON only.
────────────────────────────────────────────────────────────────────────

{
  "attacked": [
    {
      "target": "<the exact conclusion you are attacking>",
      "checklist_item": 1,
      "attack": "<the strongest case against it>",
      "survived": true,
      "downgraded_to": "settled|inference|open_texture|lacuna|contested|insufficient_evidence",
      "evidence": "<the provision text that supports your attack, quoted>"
    }
  ],
  "checked_and_survived": ["<conclusions you attacked and could not break>"],
  "limits": ["<what you could not check, and why>"]
}

`checked_and_survived` must not be empty either. A checker that breaks
everything is as useless as one that breaks nothing, and we measure both.
```

---

## ⚠️ THIS NODE HAS NEVER RUN

Its real successes so far — Rule 57 row 7, the five stale citations, the FERA
1973 finding — were all found by **humans reading adversarially**. Not by this.

**The ablation at Step 29b is what decides whether it earns its place.** Four D1
variants, each carrying one planted defect, run with node 5 on and off:

| Variant | Planted defect | Should be caught by |
|---|---|---|
| D1-a | cites Rule 11UA for FY 2026-27 | item 1 |
| D1-b | applies Rule 57 row 7 to a s.92 receipt | item 2 |
| D1-c | asserts the GST conclusion despite the FIRC being missing | item 3 |
| D1-d | values USDC at the USDT print, proxy unstated | item 4 |

**If it catches them, it earns its place with evidence rather than assertion.**

**If it catches none, that is a more interesting result than a working feature,**
and `results.md` says so, and the novelty claim resting on this node is cut. That
outcome is written down here, before the run, so it cannot be quietly dropped
afterwards.

---

## WHAT TO SAY ON STAGE

> *"Every item on that checklist is a mistake we actually made. Item one caught
> us three times. Item two is the one that would have caught us reading a table
> and stopping at the wrong column. We didn't design the checker from a diagram
> — we designed it from our own error log."*

**A checklist derived from real errors is far more persuasive than one derived
from a taxonomy**, and it costs nothing extra because the errors already
happened.

## AND THE HONEST POSITIONING

Self-critique is a mature field — Self-Refine, Reflexion, CoVe, CRITIC,
multi-agent debate. **Do not claim the mechanism.** Claim two things:

1. **It is externally grounded** — the matcher verdicts and gap list are
   mechanical inputs, because intrinsic self-correction is documented as
   unreliable
2. **It publishes the attack instead of hiding it.** Every system in the
   literature uses critique to improve the answer *before you see it*. This one
   degrades the answer and shows you why.

That second one may be the genuinely uncommon part. It is also the part that
makes the node worth having even if it only catches two of four.
