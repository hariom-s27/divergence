# D75 — real k=5 resolver sampling, deterministic clustering, and a downgrade rule wired into arm D

**Date:** 23 August 2026

## A number collision, disclosed before anything else

The request that led to this file asked for a `DECISION-D61.md`. **D61 is
already taken** — `mutation_corpus.py`'s own decision doc (manufacturing
labelled defects for the deterministic gates). This file is `D75`, the
next free number (`D74` was the highest existing decision doc at the time
of writing; grepped directly, not assumed). Renaming or overwriting D61
would have silently rewritten a real, already-cited decision — `results.md`
and `README.md` both point at it by number — so a new number was used
instead and this paragraph exists so nobody has to guess why the number in
the title doesn't match the number that was asked for.

**A second, more load-bearing collision: most of what was asked for
already exists.** `disagreement_gate.py` and `DECISION-D65.md` (22–23
August) already built the deterministic comparison half of this — `check()`,
self-tested against D1's three real seed records, already found and fixed a
real cross-Act citation bug in `scope_enforcer.py` along the way. D65's own
closing section is titled *"What is not built: real k=5 sampling"* and says
plainly that producing five real samples needs five real resolver calls
this environment has no key for. **This file is that missing half** — the
real `resolve_k()` producer, plus the specific `modal_provisions`/
`agreement`/`certainty_spread` schema and downgrade rule the newer request
asked for, which `check()`'s UNANIMOUS/DISAGREEMENT verdict doesn't provide
— built additively next to D65's work, not replacing it. Both self-test
suites still pass independently; `check()` is untouched.

## What was built

**1. `node_resolver.resolve_k(regime, facts, missing, tax_year, k=5, model="large", out_dir=None, record_id="record")`**
— a plain Python `for` loop calling the existing `resolve()` k times.
No `n=` parameter anywhere: Featherless's own `/v1/chat/completions` docs
(already quoted verbatim in `README.md`/`DECISION-D72.md`) do not document
a choices-count parameter the way OpenAI's API does, and inventing a call
shape the provider doesn't document — on the hope it's silently accepted —
is exactly the kind of unverified assumption this project's citation
discipline exists to refuse. Five real, separate, billed calls it is.

- Refuses to run at all if `DIVERGENCE_DEV=1` is set (raises `RuntimeError`
  before making any call) — that flag forces temperature 0 (D52); k copies
  of a determinism check are not k draws of the model's own default
  sampling, and would silently mean something different from what this
  function's own name promises. `DIVERGENCE_TEMPERATURE`/`DIVERGENCE_DEV`
  left unset (the default for any real terminal session, D52's own fix) is
  exactly the state that makes `llm_call.temperature()` return `None` —
  "send no temperature parameter, take the model's own default" — so
  nothing in `resolve_k()` itself needs to set or check a temperature
  value beyond refusing the one flag that would silently defeat the point.
- **Every one of the k raw outputs is written to disk before the function
  returns anything**, one file per sample plus a manifest. Featherless's
  own seed parameter is documented unreliable across servers — quoted
  verbatim in `README.md`'s Reproducibility section: *"Random seed for
  generation. (Not reliable, as we use multiple servers.)"* — so a specific
  sample cannot be regenerated on demand the way D1's replay cache
  regenerates one deterministic call. These k files are the only
  reproducibility record for a given `resolve_k()` run; without them a
  later reader has no way to audit which citation/certainty combination
  each of the k draws actually produced, only whatever aggregate a caller
  chose to keep.

**2. `disagreement_gate.cluster(samples, corpus=None)`** — deterministic,
no model call. For each regime name present in at least one sample,
extracts per-sample `(provisions, certainty, coarse polarity)` and reports
`modal_provisions`, `agreement = count(modal)/k`, `certainty_spread`,
`polarity_spread`. Provision extraction reuses `_citation_key()` — D65's
own `citation_matcher.py`-backed normalization, already fixed to
cross-check instrument (which Act/Rules) before matching — not a second
implementation. `agreement`'s denominator is `k` (total samples), not
`n_present` (samples where the regime showed up at all): a regime silently
missing from some samples is itself disagreement about whether the
conclusion exists, and scoring it against a smaller denominator would let
a resolver that drops a conclusion outright score *better* than one that
reports it inconsistently.

*Coarse outcome polarity* is a negation-phrase scan
(`_NEGATION_MARKERS`), not a sixth model call — three buckets
(`undetermined` for lacuna/insufficient_evidence, else `negative`/
`affirmative` by phrase match on `outcome`). Reported in `cluster()`'s
output; **deliberately not part of `apply_downgrade()`'s trigger
condition**, because the spec this was built to fires on citation
agreement and certainty spread only. A resolver that agrees on citation
and certainty while flipping polarity would sail through this rule
undowngraded today — a real, disclosed gap in the rule's own coverage
(`disagreement_gate.py`'s own `LIMITATIONS` block, item 3), not silently
patched by widening the trigger beyond what was specified.

**3. `disagreement_gate.apply_downgrade(baseline_regimes, clusters, min_agreement=0.6)`**
— the downgrade rule, in code, same discipline as `gap_enforcer.py` (⚙ A):
a fixed condition, checked in Python, overwrites a field unconditionally
when it fires. Per regime, fires when `agreement < 0.6` OR
`certainty_spread` contains both a confident label (`settled`/`inference`)
and an uncertain one (`lacuna`/`contested`) — exactly the two conditions
specified, no others added. When it fires: `certainty` is overwritten to
`"contested"` on a deep copy of one caller-chosen baseline sample (arm D
uses sample 0 — an arbitrary but disclosed choice, not a vote), a
`_k_sample_downgrade` field records why (`triggered_by`,
`original_certainty`, `agreement`, `certainty_spread`, `k`), and a new
`valuation.uncertainty_budget[]`-shaped entry is returned carrying the
full k-sample breakdown (`k_variants`) — not just that the samples
disagreed, but what each one actually said, the same "don't just assert
it, show it" discipline `node7_disclosure.py` already applies everywhere
else on the page.

**4. Wired into `run_arms.py` as arm D** (`run_one_d()`,
`--arm D --case <C> --source <real pipeline record>.json --k 5`). Unlike
arms A/B, arm D does not call a model on raw case text — it needs
`facts{}`/`missing{}` that already exist, so `--source` names **one**
explicit, already-produced pipeline record to pull them from, rather than
a directory glob. This is deliberate: `find_case()`'s own history (a stale
`case.md` silently winning by directory order, Step 21/Block B/D49) is
exactly the failure mode an explicit `--source` avoids — arm D's facts
should never be a silent "closest match found in this directory" guess.
For each regime the source record actually resolved, calls
`resolve_k()` for real, clusters, downgrades, and assembles a
schema-shaped record with the extended `uncertainty_budget`. Output is
written in the identical `{"arm", "case", "record", "_meta", ...}`
wrapper shape `run_one()` already writes for A/B, so
**`eval/normalize_runs.py` and `eval/score.py` needed zero changes** —
`from_arm_output()` already reads `wrapped["arm"]` correctly instead of
assuming a value, which is exactly what let arm D drop in.

## Two real bugs found by actually running it, same class D71 already named

`DECISION-D71.md` (23 August, the same day) found and fixed five files
where a startup diagnostic print called `llm_call.provider_display()`/
`model_display()` directly, uncaught, and confirmed the identical pattern
in `node2_gaps.py`, `node_resolver.py`, `node_resolver.py`'s own sibling
files, `node5_adversarial.py`, and `run_pipeline.py`. **`run_arms.py` was
not on that list, and had the same class of bug in two places** — found
here by actually running `python run_arms.py --arm D ...` with no key set,
not by code review:

1. `main()`'s existing arm-A/B path and the new arm-D path both called
   `llm_call.provider_name()` directly inside a `print(...)`, uncaught.
   With no key set, this crashed with a raw Python traceback instead of
   this project's own clean `ERROR:` message — reproduced live, both
   places, before being fixed.
2. `run_one_d()`'s own diagnostic print called `llm_call.model_id("large")`
   directly, also uncaught, also crashing with a raw traceback — found
   the same way, one function call later, while writing this file's own
   verification script.

**Fixed in both places**, `run_arms.py` only (the five files D71 already
fixed were not touched again here): `provider_name()` calls now go through
`try/except LLMError: die(str(e))`, matching the guarded pattern
`node_resolver.py`'s own `main()` already uses; `model_id()`'s diagnostic
call falls back to a plain string on `LLMError` rather than crashing,
since it is a print-only convenience and the real call immediately after
it is still properly guarded. Verified: `python run_arms.py --arm D
--case D1 --source runs/21aug/D1_final_seed2.json --k 5` now fails with
the expected clean `ERROR: FEATHERLESS_API_KEY is not set...` message, not
a traceback, with no key set.

## What was actually verified, and how, with no live key available

Same constraint every D62-onward decision doc in this project has
disclosed: no `FEATHERLESS_API_KEY` in this environment, so the real
k=5 sweep against a live model has not run. What *was* run, for real,
and is reported here rather than only asserted:

- **`python disagreement_gate.py --self-test`** — all three suites pass
  (verified by actually running it, output kept below verbatim):
  - `check()` (D65, unchanged): 3/3 — `income_tax_on_receipt` and
    `valuation_method` DISAGREE, `gst_export` UNANIMOUS, on D1's three
    real seed records.
  - `cluster()` (D75) on the same three real records: 5/5 — 100%
    citation agreement on all three regimes (all three seeds cite the
    same provision per regime; `_citation_key()`'s Act-aware
    normalization is doing real work here, not a coincidence — seed3's
    `"Section 115BBH, Income-tax Act, 1961 — carried into the
    Income-tax Act, 2025"` and seed1/seed2's `"Section 115BBH,
    Income-tax Act, 2025"` correctly resolve to the same provision id).
    Measured `certainty_spread`: `income_tax_on_receipt` →
    `['insufficient_evidence', 'settled']`; `valuation_method` →
    `['insufficient_evidence', 'lacuna']`; `gst_export` →
    `['insufficient_evidence']` only.
  - `apply_downgrade()` mechanics (D75) on three small, explicitly
    labelled *constructed* fixtures (not real case data): 3/3 —
    `low_agreement` fires when three samples cite three different real
    corpus provisions on the same regime; `mixed_confident_uncertain`
    fires on a settled/lacuna/settled spread with unanimous citation;
    neither fires when both are unanimous.
- **An honest negative result, on the one real sample this project has.**
  `apply_downgrade()` run against `cluster()`'s real output on D1's three
  real seeds **does not downgrade anything** — verified by running it,
  printed plainly in `self_test_cluster()`'s own output: *"apply_downgrade()
  on this real data: (none downgraded), 0 new budget item(s)."* Why, checked
  rather than assumed: citation agreement never drops below 100% on this
  data (the S.393(1)/Rule 206/243 fix cycle in `results.md` Block F was
  already applied before any of these three seeds ran — they are three
  temperature draws of the *already-fixed* prompt, not three points in that
  fix cycle), and the observed certainty spreads
  (`settled`/`insufficient_evidence`, `lacuna`/`insufficient_evidence`) do
  not cross the literal confident/uncertain boundary the spec defines,
  because `insufficient_evidence` sits in neither `{settled, inference}`
  nor `{lacuna, contested}`. **Not silently widened to make the demo show a
  downgrade.** Real, measured certainty instability exists in this data
  (`check()` already reports both regimes as DISAGREEMENT) — the specific
  rule as specified just doesn't happen to classify this particular spread
  as disagreement worth downgrading over. Reported as a real edge in the
  rule's own precision, same discipline this project holds M5 to below.
- **An end-to-end smoke test of arm D's wiring**, `resolve_k()` mocked
  (no key available) to return D1's three real seed records cycled to
  k=5, run through the real `run_one_d()` → `validate()` →
  `eval/normalize_runs.py` → `eval/score.py` chain, all real code, only
  the model call itself replaced: produced a schema-valid record, correct
  `"arm": "D"` normalization, and real M1–M4 scores (M1 100%, M2 recall
  50%/precision 66.7%, M3 100%, M4 100%) with **M5 correctly `None`** —
  see below. Not committed to the repo; this was a throwaway verification
  script, deleted after running, same as any other manual check this
  project's decision docs report without keeping the scratch file.

## M5 as the primary guard — the guard cannot fire yet, and this feature does not fix that

**This is the caveat that matters most for anyone reading `results.md`
next to this file.** The instruction behind this work named M5 (false
abstention) as the primary guard on the downgrade rule: if arm D's M5
worsens relative to arm C, the rule is too aggressive and that must be
reported, not tuned away. **M5 cannot be computed for arm D, but not
because of anything specific to arm D — it cannot be computed for *any*
arm today.** `eval/normalize_runs.py`'s own docstring already says this,
disclosed before this file existed: `"elements"` — the field M5 actually
scores — *"is a ground-truth-only concept today. No prompt (01-05,
baseline-prompt.md, arm-b-cot.md) asks any arm to report it in a
scoreable shape, so it comes out empty for every run, every arm, without
exception."* The smoke test above confirms this empirically for arm D
specifically: `m5: None`, identical to every M5 cell in every table in
`results.md`.

**What this means in practice:** the guard this feature was supposed to
report against is not wired to anything yet, project-wide, and building
arm D does not change that. Two options were available here: (a)
fabricate an `elements{}` field for arm D alone so its M5 would compute,
making arm D the *only* scoreable arm on this metric — which would create
a misleading asymmetry, not fix the underlying gap, and would be exactly
the kind of invented data this project's own discipline refuses
elsewhere; or (b) leave arm D's M5 `None`, identical to A/B/C, and say so
plainly. **(b) was chosen.** The guard is prepared — the moment any
resolver prompt is extended to report `elements{}` in a scoreable shape
(a real, separate piece of work, out of scope here), arm D's M5 will
compute automatically alongside every other arm's, with no further
change to this file's code. Until then, "M5 as the primary guard" is
correctly described as *not yet armed*, not as passing.

## Honest caveats — stated here, not left implicit

**Sampling measures stability. It does not and cannot measure
correctness.** All k samples agreeing that Rule 57 names no method is the
resolver being *consistent*, not the resolver being *right* — citation
currency and scope reach are still ⚙ C's and ⚙ E's job, run downstream of
this exactly as they are downstream of any single-sample run. A resolver
that always answers `lacuna` regardless of the actual text fed to it would
score 100% agreement on every input, exactly the same way a correct
resolver reading a genuinely underdetermined provision would. `agreement`
cannot distinguish those two resolvers. Nothing built here tries to.

**Agreement on a genuine lacuna is expected, and is not evidence of
reliability.** D1's `valuation_method` conclusion is `lacuna` in this
project's own frozen demo record because Rule 57 genuinely does not name a
method for a virtual digital asset (`GAZETTE-FINDINGS.md` #1) — that is
the correct legal reading, independently verified against the gazette
text, not an artifact of resolver uncertainty. If five independent samples
all correctly land on `lacuna` for this exact reason, that is five correct
answers to a genuinely open question, not five uncertain guesses that
happen to coincide. Reading high agreement on a real lacuna as "the system
is well-calibrated here" would quietly convert a fact about the *statute*
into a claim about the *resolver* — precisely the confusion `⚙ E`'s own
`lacuna` exemption (D59) already had to be built to avoid at the citation
layer, now restated at the sampling layer.

**The Nature semantic-entropy result does not transfer here, and hasn't
been checked to.** Farquhar, Kossen, Kuhn and Gal, *"Detecting
hallucinations in large language models using semantic entropy"*
(*Nature*, 2024), report an AUROC of **0.790** for semantic-entropy-based
hallucination detection — a genuinely different method from this file's
own citation/certainty clustering, and measured on **free-form question
answering**, not statutory reasoning over verbatim legal text. **This
project has not independently re-verified that 0.790 figure against the
paper's own primary text** (unlike the other citations this project's
decision docs hold to that standard — Blair-Stanek, Magesh, Chen et al.,
all independently re-checked before being quoted); it is stated here as
supplied, with that gap disclosed rather than smoothed over. Even taking
0.790 at face value, nothing about it licenses treating this file's own
`agreement`/`certainty_spread` numbers as similarly discriminative on a
completely different task (deterministic clustering over structured
citation/certainty fields, not entropy over free-form generated text) and
a completely different domain (six hand-built Indian tax cases, not the
paper's own QA benchmarks). The transfer is unmeasured, named as
unmeasured, not assumed favourable.

## What is not built

- **The real k=5 sweep against a live model.** Same constraint as D65,
  D69, D71, D73: no `FEATHERLESS_API_KEY` in this environment. Everything
  above that could be verified without one, was — the self-tests, the
  mocked end-to-end wiring check, the honest negative result on real
  k=3 data. The first real k=5 run is the next thing to do the moment a
  key is available; `resolve_k()`'s own persistence (every raw sample plus
  a manifest, before returning) means that run's own audit trail will
  exist from the first call, not be reconstructed after the fact.
- **A working M5 guard.** Disclosed above, at length, on purpose — this is
  the caveat most likely to be skipped by a reader in a hurry, so it is
  not left to a single line.
- **A polarity-aware downgrade trigger.** `cluster()` computes
  `polarity_spread`; `apply_downgrade()` does not read it. Left out
  because the spec named citation agreement and certainty spread only —
  adding a third trigger condition not asked for would be scope creep in
  the same downgrade rule this file is elsewhere careful not to overreach.
