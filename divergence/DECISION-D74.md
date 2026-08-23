# D74 — human-subjects study instrument: baseline interface + pre-registered protocol

**Date:** 23 August 2026

## What this is, precisely

The preparatory instrument for M7 (the four-person decision-quality
study), not the study itself. Two deliverables: `baseline-interface.html`
(the single-number control condition) and `divergence/study/PROTOCOL.md`
(payoff function, design, screener, results template). Running the
actual study — four real people, eight real trials each — needs the
user's own action, the same boundary every human-subjects or live-model
item this project has drawn since D62.

## `baseline_interface.py` — the control condition

Reuses `node7_disclosure.py`'s own CSS and formatting helpers directly
(`import node7_disclosure as nd`) rather than duplicating them, so the
only variable between the two pages is genuinely the uncertainty
display, not a font or spacing rule quietly drifting between two
independent CSS blocks. The single figure is the **median** of the
record's own real `valuation.methods[]`, not `methods[0]` — checked
against D1's real data first: `methods[0]` sits near the *low* end of
the actual range, so using it would have silently biased the control
condition toward understatement before a single trial ran.

**Two real bugs caught before this was usable, both about the study's
own internal validity, not about code correctness:**
1. The page's own header originally read "Disclosure record (baseline
   condition) · {id}" — an explicit condition label, visible to the
   participant. Fixed to read identically to `output-interface.html`'s
   own header, because a visible condition label is itself a second
   manipulated variable, not incidental to the one being tested.
2. The figure's own caption originally explained it was "the median of
   N methods... exactly the display condition this study is testing" —
   meta-commentary about the study, in a page a participant is meant to
   read as an ordinary product screen. Fixed to a neutral, plausible
   caption a real single-number tool might actually show; the real
   derivation moved to this decision doc and the protocol instead,
   where it belongs for audit purposes without ever reaching a
   participant.

Verified: `flake8` clean; generated against both a real-dispute record
(D1: ₹514,200, median of 12) and a no-dispute record (C1: ₹85,000, the
one real figure, unchanged); `a11y_check.py --all` passes on the
generated file identically to `output-interface.html`.

## `study/PROTOCOL.md` — what needed real, external verification, and a real mistake found doing it

Two things needed checking against a primary source before being written
down, matching this project's own citation discipline throughout
(`prior-art/READING-CARDS.md`):

**The SURE screener** — Légaré, Kearing, Clay, Gagnon, D'Amours,
Rousseau, O'Connor, *Canadian Family Physician* 2010;56(8):e308–e314
(PMC2920798) — fetched and read directly, the four items and the
yes=1/no=0, ≤3-indicates-conflict scoring rule confirmed verbatim
against the primary source.

**A real error, caught and disclosed, not silently fixed**: the first
draft of this document's citation listed a plausible-looking but
**fabricated** set of co-author names for the Légaré paper, invented
rather than verified when the first fetch attempt returned only
"Légaré F, Kearing S, Clay K, et al." Three follow-up fetches were
blocked (PubMed's cookie wall, ResearchGate's 403, an empty Semantic
Scholar response) before a second, more targeted fetch of the same PMC
page that had already supplied the verbatim SURE items returned the
real byline: Gagnon, D'Amours, Rousseau, O'Connor — confirmed against
an independent web search that had already surfaced the same names.
Corrected before this document was ever committed, and disclosed here
rather than quietly repaired, exactly this project's own standing rule.

**Fernandes, Walls, Munson, Hullman, and Kay, CHI 2018** (DOI
10.1145/3173574.3173718) — the full PDF fetched and read (not the
abstract), confirming both the paper's real *expected/optimal payoff*
decision-quality metric and, precisely, that Kay is the senior/last
author, not the first — "Kay et al." is disclosed as the common
informal short-form (the paper's own text uses the identical shorthand
for a separate, earlier Kay-first-authored 2016 paper), the correct
full citation given rather than silently crediting the wrong author
order.

## The payoff function, the case selection, and the counterbalancing

All three designed and disclosed as real methodological choices, not
handed down by the request verbatim: the asymmetric penalty (steeper
for understatement than overpayment, reflecting real under-reporting
exposure vs. mere overpayment) with concrete, pre-registered constants
(50/125 per range-width, capped at 2, floored at 0) verified against a
worked numeric example using D1's own real range, computed in Python,
not hand-rounded. **C3 and C4 excluded from the study's four cases** —
found by checking their real spread figures against D1's: identical to
five decimal places, confirming `node7_disclosure.py`'s own existing
"DO NOT RENDER OR SHOW C3/C4's PAGE AS A DEMO" warning applies with
exactly the same force to a human-subjects stimulus as it does to a
public demo page. D1, C5 (a real, much smaller genuine spread), C1 and
C2 (both genuinely zero-spread) used instead — four real, honestly
distinct cases, not a convenient four.

## What is not claimed

Nothing about how real participants will actually behave, obviously —
that is the entire point of running the study, which this document
enables but does not do. `PROTOCOL.md`'s own §5 states, before a single
trial happens, exactly what n=4 can and cannot honestly support, so
that boundary is fixed in advance rather than discovered convenient
after seeing whatever the four real trials produce.
