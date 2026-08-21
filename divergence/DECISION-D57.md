# D57 — schema.json's manifest field finally populated, CI gates that were never gates, and a real scoring bug found checking another finding

**Date:** 21 August 2026
**Found doing a detailed review pass against a slightly stale clone (commit `4e95f41`, before D55/D56/the flowchart and uncertainty-budget fixes). Several items in that review were already fixed; this documents the ones that weren't.**

## 1. `schema.json`'s `manifest` object — defined 6 August, populated for the first time tonight

`schema.json` has carried a rich `manifest` object since the original lock — `provisions_checked[]`, `scope_statement`, `not_checked[]` — with its own description reading *"you earn the right to make a negative claim by declaring what you looked at."* It was never in the top-level `required` list, so no record was ever schema-invalid for lacking it, and `run_pipeline.py` never wrote one. Confirmed: 0 of the records checked had a `manifest` key.

The practical effect: `node7_disclosure.py`'s manifest section (fixed last commit to show the full scoped corpus, not just cited provisions) was doing that computation itself, at render time, from a hardcoded `REGIME_CORPUS` mapping — correct, but not what the schema actually describes, and not available to anyone reading the raw JSON record instead of the rendered page.

**Fixed properly:** `run_pipeline.py` gained `build_manifest()` — same `REGIME_CORPUS` mapping, reads `corpus/tier-a/` front matter via `citation_matcher.parse_front_matter`, writes a real, schema-valid `manifest` object into every future record. Verified against a fresh test run (not assumed): `manifest.provisions_checked` populated with 13 real provisions, validated in isolation against `schema.json`'s own definition — valid. `node7_disclosure.py`'s `render_manifest()` now prefers `record["manifest"]` when present, falling back to its own computation for older records — including the frozen `D1_final_seed2.json`, which is **not** regenerated to pick this up, per the hard-stop rule already governing that record.

## 2. Two CI checks that would have been green regardless of whether they passed

`gate0_check.py` and `citation_matcher.py`'s self-test both print pass/fail clearly but neither ever called `sys.exit(1)` on a real failure — every invocation exited 0. Wiring either into CI as written would have produced a green badge whether or not the underlying check actually passed, which is a worse state than not running them at all: a misleading gate reads as more trustworthy than an absent one.

Fixed both to exit 1 on a real failure (`gate0_check.py`: any blocking problem; `citation_matcher.py`: any self-test case not matching its expected verdict), verified locally (both currently exit 0, correctly, since both currently pass), then added both as CI steps.

## 3. "We publish the attack and downgrade the conclusion" was never fully true

Confirmed in two places — `architecture.md`'s prose and `schema.json`'s own field description for `attacked`. `run_pipeline.py` deliberately never applies `downgraded_to` to `regimes[].certainty` (a real, previously-documented, correct engineering decision — fuzzy-matching a free-text attack target back to one specific conclusion was judged more likely to corrupt the wrong entry than to help). The claim said the opposite happens. Fixed in both places: *"we publish the attack and never let it silently improve the answer."*

## 4. A real scoring bug, found checking whether M2's instability was itself real

Hand-checked every ground-truth-gap-to-reported-gap pairing `eval/score.py`'s `_similar()` function actually decided, for all three of D1's Block-E2 seeds, against the raw JSON — not trusting the summary numbers. Seeds 1 (50%) and 3 (0%) hold up exactly. **Seed 2 (75%) doesn't, fully**: `_similar()` has no one-to-one constraint, so a single reported item — *"documentation proving the foreign exchange transaction"* — independently matched two different ground-truth gaps (the FIRC requirement and the official-exchange-rate requirement) via shared tokens, and got credited against both. Seed 2 substantively found two real gaps; the scorer credited three.

**Not fixed tonight.** `_similar()`'s matching logic underlies every M2 number already published in `results.md`, across every arm and every case. Changing it now means re-verifying all of them — exactly the kind of under-pressure scoring change this project's own hard-stop rule exists to prevent. Disclosed instead, in `results.md` and as a code comment on `m2_gaps()` itself, so the next person who reads that function doesn't have to rediscover it.

**Update, same night, once there was room to do it properly: fixed. See [D58](DECISION-D58.md).** Every M2 number this affected was re-scored, not assumed — four cells across the file, listed in D58, everything else confirmed unchanged.

**This does not undermine the instability finding — it narrows one number inside it.** 0% and 50% are both real, independently confirmed low numbers on the identical case, same input, same code. The instability itself stands; the specific claim that one of the three seeds scored *75%* is now qualified rather than asserted flatly.

## 5. Smaller fixes, same pass

- `m4_enumeration()` has no ceiling and can read over 100% (C3: 12/5, 240%) — not a bug, always caused by the same known, disclosed reason (a case scored against D1's borrowed lattice, not its own). Stated explicitly in `results.md` rather than left implicit in the raw number.
- M5's honest answer was buried. C1 and C2's zero-spread, one-method records are the closest thing this project has to real false-abstention evidence — stated at the same prominence as the "M5 is unscoreable" disclosure, not as a footnote to it.
- `node7_disclosure.py` gained an explicit top-of-file warning: never render or show C3/C4's page as a demo, since their `valuation` block is still D1's borrowed lattice.

## What to say about it

> "Reviewing our own repo against an older clone, we found a schema field
> that had been defined since 6 August and never once populated, two CI
> checks that would have shown green regardless of whether they passed, and
> a wording claim repeated in two files that wasn't fully true. All fixed.
> Checking one of those findings — whether our gap-detector instability was
> real or a scoring artifact — we found a genuine third thing: a real
> double-counting bug in our own scorer, inflating one of three published
> numbers. We didn't fix the scorer three days before submission, because
> that ripples into every number already in our results file. We disclosed
> it, in the results file and in the code itself, which is the same
> discipline we've applied to every other self-caught bug in this project."
