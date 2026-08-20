# D52 — every run tonight (Blocks A through E1) was actually at temperature 0, the exact protocol violation D45 already fixed once

**Date:** 21 August 2026
**Found while starting Step 4 (three seeds on D1), checking `DIVERGENCE_TEMPERATURE` was actually set before relying on it.**

## The fact, stated plainly

`llm_call.py`'s `temperature()` reads `DIVERGENCE_TEMPERATURE` from the
environment; unset, it returns `0.0` — "dev default: reproducible" by its
own comment, explicitly documented as the wrong setting for a scored run
(`evaluation-design.md`: *"Temperature | default, not zero — that is how a
real user runs it. Five runs at temperature 0 measure one point five
times."*). D45 (an earlier finding this same session) already caught this
exact bug once and added the env var as the fix.

**The fix was never exercised.** Checked directly: `[Environment]::GetEnvironmentVariable("DIVERGENCE_TEMPERATURE", "User")`
returns nothing, and none of tonight's PowerShell invocations across
Blocks A, B, C, D, or E1 ever set it. Checked every saved record's own
`_meta.llm.temperature` field — all 24 records from tonight (`runs/21aug/*.json`,
every arm, every case) plus the pre-existing `runs/*_pipeline.json` records
say `"0 (dev default)"`. Every M1/M2/M3/M4 number in tonight's results.md
tables, every node-5 attack, both ablation runs — all of it ran at
temperature 0.

## Why this is disclosed as its own finding rather than quietly set going forward

The whole discipline this project applies to itself is: a bug found is
written down before it is fixed, not folded into the next commit unlabelled.
D45 already established that temperature 0 for a scored run is a real
protocol violation, not a style choice — reporting it fixed once and then
letting it silently recur, unnoticed, for an entire night of further work
is precisely the failure this project's own thesis is about: confident
output resting on ground that quietly moved, indistinguishable from the
real thing unless someone checks.

## What this does and does not invalidate

**Does not invalidate:** every structural finding from tonight — the M1
fix (real documents + field-name contract), node 5's real catch in D1's
record and the 3/4 ablation score, C1/C5's corrected valuation blocks.
Those are about code, prompts, and documents changing, not about sampling
behavior, and would hold at any temperature.

**Does invalidate one specific claim already written into results.md**,
now corrected in place: the Block B section attributed a small movement in
arm A/B's citation recall (0.150 → 0.100) to *"ordinary run-to-run variance
now that temperature is not pinned to 0."* Temperature was still pinned to
0 throughout. The honest explanation is simpler and was sitting right there
— arms A/B ran against a different input document (`input.md` replacing
`case.md`) between the two measurements, which is sufficient on its own to
move a small-sample metric like this without invoking sampling variance at
all.

**Does mean every number in tonight's tables is a single deterministic
draw, not a variance-representative sample**, exactly as D45 already said
about the numbers before it. This was already the documented state of
things before tonight — D52 does not make the numbers less real, it
corrects a claim that implied a change in that state had already happened
when it had not.

## Fixed for E2, going forward

`$env:DIVERGENCE_TEMPERATURE = "default"` set explicitly and verified
(checked `_meta.llm.temperature` on the first E2 run before trusting the
rest) before any of the three-seed runs below. This is the first point in
the project where a run actually executes at the model's own default
temperature rather than 0.

## What to say about it

> "We fixed the temperature-zero bug once, in code, and then didn't
> actually turn it on for the rest of the night — an entire evaluation
> session ran at temperature 0 again without anyone noticing until we went
> to use the setting for the seed-variance work and checked first. We're
> disclosing that plainly rather than quietly starting to use it correctly
> from here, because the whole argument of this project is that finding
> your own mistake and saying so is the thing that's supposed to happen,
> including when the mistake is 'we already fixed this once and it came
> back.'"
