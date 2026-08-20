# ITERATION STORY

Not a log. The raw one is `step22drop/iteration-log.md` — read that for detail. This is the seven moments that actually mattered, in the order they matter, each one: what we tried, what broke, what we changed, what number moved.

---

## 1. The corpus was 40% our own opinion, and the matcher couldn't tell

**Tried:** inject the citable corpus straight into the resolver prompts, built from our own research notes on each provision.

**Broke:** ~40% of the corpus by volume turned out to be our own analysis, not statutory text — commentary sitting next to the law it was explaining. A model given that text doesn't need to reason about the gap; it reads our conclusion and hands it back, and `citation_matcher.py` passes the answer because the citation inside it is real. The headline finding would have been us telling the model the answer and then citing ourselves as evidence it found one.

**Changed:** `corpus/verbatim/` — statutory text only, between explicit markers, never commentary (D31). Every resolver prompt now injects from this folder exclusively.

**Number moved:** the entire evaluation's validity moved from "measures our own writing" to "measures a model reading law." Not a metric — a precondition for every metric after it.

## 2. Two retired files shadowed their replacements, and 15/15 passed the whole time

**Tried:** trust the citation-matcher self-test (15/15, green) as evidence the corpus was correct.

**Broke:** `citation_matcher.py` loads `sorted(os.listdir())` and takes the first match. Three pairs of files claimed the same provision — an old `IT-RULE-206.md` alphabetically ahead of the real `ITR2026-RULE-206.md` — so `Rule 115`, superseded in 2026, was returned VERIFIED for FY 2026-27. Four months, 15/15, every time. Not found by anyone reading the test. Found by `gate0_check.py` flagging two files claiming one provision.

**Changed:** retired the shadowing files; verified the surviving ones handle every year/number case alone before deleting anything.

**Number moved:** nothing in the self-test — that's the point. 15/15 was a property of the folder, not the code, both before and after. The fix changed what 15/15 actually meant.

## 3. One citation string, five provisions, four never checked

**Tried:** let a resolver conclusion cite everything it relied on in one `citation.provision` string, semicolon-joined.

**Broke:** `citation_matcher.py` matches the first reference it finds and stops. A string holding five provisions got the first one checked and the record marked `verified: true` for all five. Found live, 20 Aug, on a real D1 run.

**Changed:** one load-bearing citation per conclusion; everything else named in `reasoning`, not the citation field (D46).

**Number moved:** M3 (citation validity) on D1's arm-C record: from a false 100% (four unchecked) to a real 100% (all five, individually verified) — same number, opposite meaning.

## 4. M5 scored a confident 0.0%, and the metric built to catch overconfidence was itself overconfident

**Tried:** run `eval/normalize_runs.py --report` after finally having real records to score.

**Broke:** `m5_false_abstention()` computed `run.get("elements", {})` and checked whether any settled element was wrongly reported open. No arm has ever produced an `elements{}` block, so `got` was always `{}`, the check never fired, and the function returned `0.0` — not "not measured," a literal perfect score. Every row in the table would have read "0.0% false abstention" for a metric this project's own materials call the one that earns trust.

**Changed:** return `None` before comparing, when `elements` is absent or empty (D48).

**Number moved:** M5 across every row, from a fabricated 0.0% to an honest `—`.

## 5. Temperature 0, twice — fixed once, and it came back the same night

**Tried:** the eval's own design doc says plainly: default temperature, never 0, because "five runs at temperature 0 measure one point five times." `DIVERGENCE_TEMPERATURE` was added as the fix.

**Broke:** the fix required actively remembering to set it, every session. It was never set the rest of that same night — Blocks A through E1's entire run, checked directly via each record's own `_meta.llm.temperature`, executed at temperature 0 again (D52).

**Changed:** inverted the default. Model's own temperature is now free; `DIVERGENCE_DEV=1` opts *into* the old reproducible-0 behavior, on purpose, not by omission.

**Number moved:** the class of bug closes. There is no longer a way to silently run a scored eval at temperature 0 — the thing that could be forgotten a third time no longer exists to forget.

## 6. Step 25 was never actually finished, and M1 was measuring an impossible target

**Tried:** score extraction accuracy (M1) against ground truth's own field names.

**Broke:** five of six case files never got the standalone input document their own checklist required. Ground truth expected a counterparty name and invoice number that existed in no document any extractor was shown. C3 was worst — its case file restated none of its own facts, only "same shape as D1," and extracted zero fields as a direct result.

**Changed:** a mechanical script (`make_case_docs.py`) reads each case's already-frozen ground truth and renders a real input document from it — never editing the ground truth, never hand-writing the document either, since both risk the same bias. Combined with an explicit field-name contract in the extraction prompt.

**Number moved:** M1 mean across six cases, arm C: **11.8% → 94.6%**.

## 7. The same scope-reach failure, three times, on our own output

**Tried:** resolve D1's valuation question against the full injected corpus.

**Broke, three separate times:** Rule 57 row 7's own column B serves s.26(2)(j), not s.92 — found by a human. Rule 206's own opening words scope it to foreign currency, which a VDA is defined not to be — the resolver cited it anyway, found by node 5's first real run. Rule 243(8)(e)'s own opening words scope it to a *reporting crypto-asset service provider* — the fix for the second error reached for this one instead, `certainty: settled`, directly contradicting this project's own thesis that no method is prescribed. Found by node 5 again, the same night, on unplanted data.

**Changed:** one generalized SCOPE GATE instruction, not three patches — check any provision's own scope statement before applying it, every time, regardless of which rule it is.

**Number moved:** not a metric. A pattern. Three real, current, correctly-quoted citations, three times outside their own scope, zero of the three visible to M3 or M4 — both stayed at 100% and 12/12 across all three states of the record. Caught only by adversarial reading.

---

We built a system to detect confident statements resting on ground that has moved. It caught us seven times. Then we read the gazette, and it caught the drafter.
