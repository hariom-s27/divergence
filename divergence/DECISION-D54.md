# D54 — the third scope-reach error, fixed with one generalized gate, plus a working downgrade guard

**Date:** 21 August 2026
**Directly continues D50's addendum. Read that first — this fixes what it found.**

## The problem, stated as sharply as it deserves to be

D50's addendum fixed the Rule 206 defect and, in the same run, found a new
one: the corrected record cited `Rule 243(8)(e)` as D1's valuation method,
`certainty: settled`. This is worse than the bug it replaced, not better.
This project's entire thesis is that no method is prescribed for a VDA
received under s.92 — that lacuna is the headline finding, the reason the
12-method lattice exists at all. The record that is supposed to demonstrate
that thesis was, until this fix, asserting the opposite of it, confidently,
on the page a reader opens first (`node7_disclosure.py`, D53, generates
`output-interface.html` directly from this record).

## Why Rule 243(8)(e) doesn't reach a taxpayer

Checked directly against `corpus/verbatim/ITR2026-RCASP-VALUATION.md`'s own
opening words: *"For the purposes of sub-clauses (vi), (vii), (viii) and
(ix) of sub-rule (1)(e)"* — the aggregate-reporting obligations of a
**reporting crypto-asset service provider**. Priya is a resident individual
who received a payment. She is not an RCASP. The rule's own scope gate
excludes her before any of its valuation waterfall (own trading pairs →
book values → third-party aggregators → *"a reasonable estimate may be
applied as a measure of last resort"*) is even relevant.

**This is the third confirmed instance of the identical failure shape:**

| # | Provision | Its own scope | Misapplied to |
|---|---|---|---|
| 1 | Rule 57 row 7 | column B: s.26(2)(j) only | a s.92 receipt |
| 2 | Rule 206 row 3 | "income... in foreign currency" | a s.115BBH VDA receipt |
| 3 | Rule 243(8)(e) | reporting crypto-asset service providers | a taxpayer, not a service provider |

Three different rules, three different kinds of scope statement (a table
column, an opening phrase, an addressee), one mistake. That pattern, not
any one instance of it, is the finding worth stating plainly: a model given
verbatim statute and an underdetermined question reliably finds the
nearest rule that mentions the right words and applies it with confidence.
Two of the three were found by a human reading adversarially or by node 5;
this one was found by node 5 alone, on unplanted, real data, the second
such catch (see below).

## The fix — one generalized gate, not a third patch

`03-income-tax.md` gained a **SCOPE GATE** section stating the general
principle once (check any provision's own scope statement before applying
it — its opening words, its table column, or the entity it addresses),
rather than adding a third special case alongside the Rule 206/207 gate.
Explicit, separate guidance for Rule 243: cite it only as evidence that
even the one prescribed crypto valuation waterfall concedes indeterminacy
(the "last resort" clause), never as the method itself, and never with
`settled` or `inference` certainty on the taxpayer's own question.

**`valuation_method` is now its own regime object, not folded into
`income_tax_on_receipt`.** The original consolidation instruction (D46)
was written to stop the model inventing five fake regime types — a real
fix at the time. It had a side effect: valuation method's certainty was
forced to share whatever certainty the classification got, which meant a
`settled` classification (correct: s.115BBH plainly taxes this) could not
coexist with a `lacuna` valuation method (also correct: no provision
reaches it) in the same record. The JSON example in the prompt now shows
two filled objects, not one — this project's own established practice
(giving models filled instances, not abstract rules) applied to its own
fix.

## The re-run

`runs/21aug/D1_v3_pipeline.json`. `income_tax_on_receipt`: `settled`,
unchanged reasoning. `valuation_method`, new object: **`certainty:
lacuna`**, outcome: *"No provision in the text provided prescribes a
specific method for determining the rupee value of a virtual digital
asset on the valuation date. The closest relevant provision, Rule
243(8)(e), applies to reporting crypto-asset service providers, not
individual taxpayers."* Citation to Rule 243 kept (correctly, as the
closest-but-rejected provision — the same convention this project already
uses when a resolver explains why a checked provision does not reach),
not as the governing rule. Schema-valid, all three citations verified.

**Ran node 5 against it. The `valuation_method` conclusion survived
unattacked** — `checked_and_survived`, not landed — an independent
confirmation from a different model that this answer holds up, not just
that nobody has attacked it yet. Two attacks landed on the other two
regimes, both legitimate scope-reach and missing-evidence points.

`output-interface.html` regenerated from this record (`node7_disclosure.py`,
unchanged code — this is exactly why the composer was worth building the
way it was: the page updates by re-running it against a corrected record,
not by hand-editing HTML). Section 03 now shows a chip reading **"No rule
found"** on the valuation-method line, next to the 12-method, ₹47,868.76
range in section 02. Checked directly for U+FFFD (the replacement
character) named as a risk: not present anywhere in the file, confirmed at
the byte level (the
citation's em-dash is a valid UTF-8 `\xe2\x80\x94`, not a replacement
character) — the same false alarm chased down twice earlier tonight, laid
to rest a third time, specifically on this record.

## The downgrade guard

D50's addendum noted node 5 had once set `downgraded_to: settled` on a
landed attack — an upgrade wearing a downgrade's name, nothing in the
schema stopped it (`downgraded_to` is just a certainty enum value, no
ordering constraint). `node5_adversarial.py` gained
`_reject_upward_revisions()`: for a landed attack (`survived: false`),
matches `target`'s free text back to the regime it quotes by word overlap
(not substring — node 5 paraphrases rather than quoting verbatim, found
while building this: the known bad example's target text shared no
substring with the regime's outcome, only overlapping vocabulary), and
if `downgraded_to` is not strictly *less* certain than that regime's
certainty already was, drops the field and records the rejection in
`limits[]`. Ambiguous matches (no clear single best match) are skipped,
not guessed — the same conservative choice `run_pipeline.py` already made
for not auto-applying downgrades to `regimes[]` itself.

**Tested against the known bad example before trusting it**: the D50
addendum's `settled → settled` "downgrade" is correctly caught and
dropped. **Then verified on a second, independent, fresh case**: the v3
re-run's own node-5 pass produced a different same-level non-downgrade
(`insufficient_evidence → insufficient_evidence`), and the guard caught
that one too, live, on data that did not exist when the guard was
written. Two independent catches, not one replay.

## What to say about it

> "We now have three confirmed instances of the same failure — a real,
> current, correctly-quoted provision applied outside its own scope. That
> is not a bug list; it is a measured result about how a model behaves
> under genuine legal underdetermination, on our own project, three times.
> We fixed it once, generally, instead of three separate patches, and the
> node built to catch exactly this kind of error caught the third instance
> itself, unplanted, the same night it first ran. It also, separately,
> proposed a nonsensical non-downgrade on two different occasions — caught
> and rejected in code both times, the same discipline we apply to every
> other certainty value in this pipeline."
