# Node-5 mutation sweep: summary (R=3)

Computed by `runs/2026-10-21_mutants/summarize.py` from the per-call files in this folder. Pre-registration: `../expectations.md` + `../expectations_amendment.md` + `../expectations_amendment_2.md`.

## Headline

| Measure | Result |
|---|---|
| **SPECIFIC, matcher count (primary)** | 13/89 = 14.6% [CI 8.0–23.7%] |
| SPECIFIC, human-confirmed count | 1/89 = 1.1% [CI 0.0–6.1%] |
| SPECIFIC, human partial (not part of the headline) | 8/89 = 9.0% [CI 4.0–16.9%] |
| SPECIFIC, human not_confirmed | 4 of 13 matcher hits |
| Placebo hits judged chance match | 3 of 3 audited |
| SPECIFIC, term-clean subset | 0/53 = 0.0% [CI 0.0–6.7%] |
| ANY-ATTACK (secondary) | 85/89 = 95.5% [CI 88.9–98.8%] |
| Null false-flag rate (ANY-ATTACK) | 15/15 = 100.0% [CI 78.2–100.0%] |
| SPECIFIC placebo (null critiques × each operator's terms) | 3/101 = 3.0% [CI 0.6–8.4%] |
| First-attempt error rate (all calls) | 68/144 = 47.2% [CI 38.9–55.7%] |
| After-retry ERROR rate (all calls) | 35/144 = 24.3% [CI 17.6–32.1%] |

Denominators: 120 real mutants nominal (40 × R; the 2 no-op mutants excluded) minus after-retry ERRORs = 89 scored. Nulls (18) and ERRORs (35) are counted separately. CI = Clopper-Pearson 95% (binom_ci.py).

## Per operator

| Operator | SPECIFIC | ANY-ATTACK | ERRORs |
|---|---|---|---|
| CITE_SWAP | 1/15 = 6.7% [CI 0.2–31.9%] | 13/15 = 86.7% [CI 59.5–98.3%] | 3 |
| DATE_SHIFT | 2/7 = 28.6% [CI 3.7–71.0%] | 7/7 = 100.0% [CI 59.0–100.0%] | 5 |
| RATE_SUB | 1/12 = 8.3% [CI 0.2–38.5%] | 10/12 = 83.3% [CI 51.6–97.9%] | 6 |
| LABEL_MISMATCH | 0/13 = 0.0% [CI 0.0–24.7%] | 13/13 = 100.0% [CI 75.3–100.0%] | 5 |
| ARITH_CORRUPT | 0/16 = 0.0% [CI 0.0–20.6%] | 16/16 = 100.0% [CI 79.4–100.0%] | 2 |
| SILENT_OMIT | 0/14 = 0.0% [CI 0.0–23.2%] | 14/14 = 100.0% [CI 76.8–100.0%] | 4 |
| OVERCLAIM | 9/12 = 75.0% [CI 42.8–94.5%] | 12/12 = 100.0% [CI 73.5–100.0%] | 6 |

## Per case

| Case | SPECIFIC | ANY-ATTACK | ERRORs |
|---|---|---|---|
| C1 | 2/16 = 12.5% [CI 1.6–38.3%] | 14/16 = 87.5% [CI 61.7–98.4%] | 5 |
| C2 | 2/13 = 15.4% [CI 1.9–45.4%] | 12/13 = 92.3% [CI 64.0–99.8%] | 5 |
| C3 | 2/15 = 13.3% [CI 1.7–40.5%] | 14/15 = 93.3% [CI 68.1–99.8%] | 6 |
| C4 | 3/14 = 21.4% [CI 4.7–50.8%] | 14/14 = 100.0% [CI 76.8–100.0%] | 7 |
| C5 | 3/17 = 17.6% [CI 3.8–43.4%] | 17/17 = 100.0% [CI 80.5–100.0%] | 4 |
| D1 | 1/14 = 7.1% [CI 0.2–33.9%] | 14/14 = 100.0% [CI 76.8–100.0%] | 4 |

## Per repetition (no repetition is preferred over another)

| Rep | SPECIFIC | ANY-ATTACK | Null flag |
|---|---|---|---|
| r1 | 5/30 = 16.7% [CI 5.6–34.7%] | 29/30 = 96.7% [CI 82.8–99.9%] | 5/5 = 100.0% [CI 47.8–100.0%] |
| r2 | 3/29 = 10.3% [CI 2.2–27.4%] | 28/29 = 96.6% [CI 82.2–99.9%] | 6/6 = 100.0% [CI 54.1–100.0%] |
| r3 | 5/30 = 16.7% [CI 5.6–34.7%] | 28/30 = 93.3% [CI 77.9–99.2%] | 4/4 = 100.0% [CI 39.8–100.0%] |

## Verdict stability across repetitions: SPECIFIC

Stable 29 · flipping 3 · insufficient valid reps 8 (of 40 real mutants).
- C2/OVERCLAIM: r1=1,r2=0,r3=1
- C5/CITE_SWAP: r1=ERR,r2=1,r3=0
- D1/OVERCLAIM: r1=0,r2=0,r3=1
- insufficient: C1/DATE_SHIFT, C1/LABEL_MISMATCH, C2/ARITH_CORRUPT, C3/RATE_SUB, C3/OVERCLAIM, C4/RATE_SUB, C4/OVERCLAIM, D1/SILENT_OMIT

## Verdict stability across repetitions: ANY-ATTACK

Stable 28 · flipping 4 · insufficient valid reps 8 (of 40 real mutants).
- C1/CITE_SWAP: r1=1,r2=1,r3=0
- C1/RATE_SUB: r1=0,r2=1,r3=1
- C2/RATE_SUB: r1=1,r2=ERR,r3=0
- C3/CITE_SWAP: r1=1,r2=0,r3=ERR
- insufficient: C1/DATE_SHIFT, C1/LABEL_MISMATCH, C2/ARITH_CORRUPT, C3/RATE_SUB, C3/OVERCLAIM, C4/RATE_SUB, C4/OVERCLAIM, D1/SILENT_OMIT

## SPECIFIC hits (matcher) with human audit

| Mutant | Excerpt (normalised) | Human |
|---|---|---|
| C1_OVERCLAIM_r1 | this supply does not meet the conditions for an export of services. // the conclusion depends on the condition that the recipient of service is located outside india, which is listed in the `missing`  | partial: The missing-location objection supports lowering certainty, but the null runs also challenge this conclusion over missing location/place-of-supply evidence; the response is not clearly mutation-specific. |
| C1_OVERCLAIM_r2 | this supply does not meet the conditions for an export of services.", // the place of supply basis seems ambiguous. thats due, is resolved on recipients location directly might not supported or denied | not_confirmed: Beyond saying the place of supply is ambiguous, the explanation is garbled; suggesting open_texture does not establish that it detected the planted certainty change. |
| C2_OVERCLAIM_r1 | the supply meets all the conditions for being an export of services. // the conclusion does not consider the requirement for an 'export declaration' as required by the foreign exchange management act, | partial: It attacks the correct GST conclusion but introduces a FEMA declaration objection rather than identifying the planted overstatement of certainty. |
| C2_OVERCLAIM_r3 | the supply meets all the conditions for being an export of services. // the condition regarding the place of supply being outside india remains unsettled. as mandated by igst act s.2(6) | partial: It directly challenges certainty about the place of supply, but the successful null response raises essentially the same missing-place-of-supply objection. |
| C3_OVERCLAIM_r3 | the receipt of 2000 usdc is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115bbh. the value is determined on the settlement date (2026-06-23) using the telegr | partial: It challenges assertion despite missing evidence, but all three null runs already attack this conclusion; the truncated null text does not establish a distinct mutation-specific objection. |
| C3_RATE_SUB_r1 | it is implied the binance usdc/usdt print substitutability operates in the environs of force marshal law. // the explanation does not adequately address the legal framework governing treatement antici | not_confirmed: The explanation is garbled and never identifies the changed row's source-label mismatch; Binance wording also existed in the original. |
| C4_DATE_SHIFT_r1 |  asset, taxed at 30% under s.115bbh. the valuation date is the date of receipt (2026-06-18). the valuation method is the price that such property would ordinarily fetch on sale in the open market on t | not_confirmed: The attack concerns the TDS citation, not the changed valuation-row date; the matched date already existed in the original target and null responses. |
| C4_DATE_SHIFT_r3 | the valuation date for the receipt is the date of receipt (2026-06-18) as per rule 56, table sl. no. 1, which applies to the date on which the property or consideration is received by the assessee. // | not_confirmed: The attack concerns Rule 56's applicability, not the substitution of June 18 for June 25; absence of an identical null attack does not establish date-change detection. |
| C4_OVERCLAIM_r2 | the supply meets some conditions for export of services but fails the condition regarding the receipt of payment in convertible foreign exchange. // this conclusion depends on the 'declaration of serv | confirmed: It explicitly challenges asserting the conclusion despite a missing dependency and requests a downgrade; the supplied null responses do not repeat that objection. This confirms the confidence challenge, not its legal correctness. |
| C5_CITE_SWAP_r2 | g rate on the last day of the tax year (31 march 2027). // the provision cited, rule 57, does not specify the valuation method for income from other sources directly. the appropriate rule for determin | partial: It explicitly challenges the substituted Rule 57, but the null runs make the equivalent objection against Rule 56 and recommend the same Rule 206 correction. |
| C5_OVERCLAIM_r1 | the supply meets all the conditions for being an export of services. // the outcome stating depends on 'valuation'. notably absent — step skipped saying reached nevertheless. making conclusory asserti | partial: Although awkwardly written, the missing-valuation objection is understandable and substantially repeats the objection in both successful null runs. |
| C5_OVERCLAIM_r3 | the supply meets all the conditions for being an export of services. // the conclusion depends on valuation, which is listed in the 'missing' list. the conclusion is asserted despite the dependency on | partial: The missing-valuation objection and proposed downgrade substantially repeat the successful null responses. |
| D1_OVERCLAIM_r3 | the supply does not meet all conditions for being an export of services. // the place of supply is not explicitly excluded by s.2(6) despite step 3 stating otherwise. there are no grounds to conclude  | partial: It challenges the underlying inference that the place-of-supply condition failed, but does not clearly identify the changed certainty label; a different null objection alone does not establish mutation-specific detection. |

## Placebo hits (null critique matched an operator's terms)

- C1_NULL_r2 × RATE_SUB: ition relies on femsa s.7 and therefore demands more scrutiny. also referencing rbi circular dated 04 may 2026. (human: chance_match yes: The generic RBI keyword matched a circular reference in an untouched case, not detection of a planted reference-rate substitution.)
- C4_NULL_r1 × DATE_SHIFT:  asset, taxed at 30% under s.115bbh. the valuation date is the date of receipt (2026-06-18). the valuation method is the price that such property would ordinarily fetch on sale in the open market on t (human: chance_match yes: The matched date was already in the original target; the attack concerns the applicable Income-tax Act, not a date change.)
- C4_NULL_r3 × DATE_SHIFT:  asset, taxed at 30% under s.115bbh. the valuation date is the date of receipt (2026-06-18). the valuation method is the price that such property would ordinarily fetch on sale in the open market on t (human: chance_match yes: The matched date was already in the original target; the visible attack concerns the exchange-rate rule, not a date change.)

## Surviving mutants (SPECIFIC)

C1/ARITH_CORRUPT/r1, C1/ARITH_CORRUPT/r2, C1/ARITH_CORRUPT/r3, C1/CITE_SWAP/r1, C1/CITE_SWAP/r2, C1/CITE_SWAP/r3, C1/DATE_SHIFT/r3, C1/LABEL_MISMATCH/r3, C1/RATE_SUB/r1, C1/RATE_SUB/r2, C1/RATE_SUB/r3, C1/SILENT_OMIT/r1, C1/SILENT_OMIT/r2, C1/SILENT_OMIT/r3, C2/ARITH_CORRUPT/r3, C2/CITE_SWAP/r1, C2/CITE_SWAP/r2, C2/CITE_SWAP/r3, C2/LABEL_MISMATCH/r1, C2/LABEL_MISMATCH/r2, C2/OVERCLAIM/r2, C2/RATE_SUB/r1, C2/RATE_SUB/r3, C2/SILENT_OMIT/r1, C2/SILENT_OMIT/r3, C3/ARITH_CORRUPT/r1, C3/ARITH_CORRUPT/r2, C3/ARITH_CORRUPT/r3, C3/CITE_SWAP/r1, C3/CITE_SWAP/r2, C3/DATE_SHIFT/r1, C3/DATE_SHIFT/r2, C3/LABEL_MISMATCH/r1, C3/LABEL_MISMATCH/r2, C3/LABEL_MISMATCH/r3, C3/SILENT_OMIT/r1, C3/SILENT_OMIT/r2, C3/SILENT_OMIT/r3, C4/ARITH_CORRUPT/r1, C4/ARITH_CORRUPT/r2, C4/ARITH_CORRUPT/r3, C4/CITE_SWAP/r1, C4/CITE_SWAP/r3, C4/LABEL_MISMATCH/r1, C4/LABEL_MISMATCH/r2, C4/RATE_SUB/r3, C4/SILENT_OMIT/r1, C4/SILENT_OMIT/r2, C4/SILENT_OMIT/r3, C5/ARITH_CORRUPT/r1, C5/ARITH_CORRUPT/r2, C5/ARITH_CORRUPT/r3, C5/CITE_SWAP/r3, C5/DATE_SHIFT/r2, C5/DATE_SHIFT/r3, C5/LABEL_MISMATCH/r1, C5/LABEL_MISMATCH/r2, C5/LABEL_MISMATCH/r3, C5/RATE_SUB/r1, C5/RATE_SUB/r2, C5/RATE_SUB/r3, C5/SILENT_OMIT/r2, C5/SILENT_OMIT/r3, D1/ARITH_CORRUPT/r1, D1/ARITH_CORRUPT/r2, D1/ARITH_CORRUPT/r3, D1/CITE_SWAP/r1, D1/CITE_SWAP/r2, D1/CITE_SWAP/r3, D1/LABEL_MISMATCH/r1, D1/LABEL_MISMATCH/r2, D1/OVERCLAIM/r1, D1/OVERCLAIM/r2, D1/RATE_SUB/r1, D1/RATE_SUB/r2, D1/SILENT_OMIT/r2

## Excluded

- No-op mutants: C2/DATE_SHIFT, D1/DATE_SHIFT
- ERRORs (35): C1_DATE_SHIFT_r1: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(2, 'attack missing or not a string')]; C1_DATE_SHIFT_r2: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(1, "downgraded_to='contested ' not in ['contested', 'i; C1_LABEL_MISMATCH_r1: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(0, 'survived=None is not a boolean')]; C1_LABEL_MISMATCH_r2: node5_adversarial: model output has no top-level 'checked_and_survived' array; C1_OVERCLAIM_r3: [node5_adversarial] featherless/mistralai/Mistral-Large-Instruct-2411 returned unparseable JSON after 3 attempts (no par; C2_ARITH_CORRUPT_r1: node5_adversarial: model output has no top-level 'checked_and_survived' array; C2_ARITH_CORRUPT_r2: node5_adversarial: model output has no top-level 'checked_and_survived' array; C2_LABEL_MISMATCH_r3: node5_adversarial: model output has no top-level 'checked_and_survived' array; C2_NULL_r1: [node5_adversarial] featherless/mistralai/Mistral-Large-Instruct-2411 transport failure after 3 attempts: Connection err; C2_NULL_r3: node5_adversarial: model output has no top-level 'checked_and_survived' array; C2_RATE_SUB_r2: node5_adversarial: model output has no top-level 'checked_and_survived' array; C2_SILENT_OMIT_r2: node5_adversarial: model output has no top-level 'checked_and_survived' array; C3_CITE_SWAP_r3: node5_adversarial: model output has no top-level 'checked_and_survived' array; C3_DATE_SHIFT_r3: node5_adversarial: model output has no top-level 'checked_and_survived' array; C3_OVERCLAIM_r1: node5_adversarial: attacked[] contains 4 malformed entr(y/ies): [(0, 'survived=None is not a boolean'), (2, 'survived=No; C3_OVERCLAIM_r2: node5_adversarial: model output has no top-level 'checked_and_survived' array; C3_RATE_SUB_r2: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(4, "downgraded_to='straightforward indirect sector-spe; C3_RATE_SUB_r3: node5_adversarial: model output has no top-level 'checked_and_survived' array; C4_CITE_SWAP_r2: node5_adversarial: model output has no top-level 'attacked' array; C4_DATE_SHIFT_r2: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(0, "downgraded_to='open_texture_,lacuna' not in ['cont; C4_LABEL_MISMATCH_r3: node5_adversarial: attacked[] contains 4 malformed entr(y/ies): [(1, 'attack missing or not a string'), (2, 'attack miss; C4_OVERCLAIM_r1: node5_adversarial: attacked[] contains 2 malformed entr(y/ies): [(4, "downgraded_to='undefined' not in ['contested', 'in; C4_OVERCLAIM_r3: node5_adversarial: model output has no top-level 'attacked' array; C4_RATE_SUB_r1: node5_adversarial: model output has no top-level 'checked_and_survived' array; C4_RATE_SUB_r2: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(2, 'survived=None is not a boolean')]; C5_CITE_SWAP_r1: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(2, "downgraded_to='insufficient_evidence ' not in ['co; C5_DATE_SHIFT_r1: node5_adversarial: attacked[] contains 2 malformed entr(y/ies): [(0, 'survived=None is not a boolean'), (1, 'not an obje; C5_NULL_r3: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(1, "survived='true' is not a boolean")]; C5_OVERCLAIM_r2: node5_adversarial: attacked[] contains 2 malformed entr(y/ies): [(0, 'survived=None is not a boolean'), (1, 'survived=No; C5_SILENT_OMIT_r1: node5_adversarial: model output has no top-level 'checked_and_survived' array; D1_DATE_SHIFT_r2: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(2, 'survived=None is not a boolean')]; D1_LABEL_MISMATCH_r3: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(1, 'survived=None is not a boolean')]; D1_RATE_SUB_r3: node5_adversarial: attacked[] contains 2 malformed entr(y/ies): [(0, "downgraded_to='incorrect_premise' not in ['contest; D1_SILENT_OMIT_r1: node5_adversarial: attacked[] contains 1 malformed entr(y/ies): [(1, 'target missing or not a string')]; D1_SILENT_OMIT_r3: node5_adversarial: attacked[] contains 2 malformed entr(y/ies): [(1, 'survived=None is not a boolean'), (2, 'survived=No
- Schema-retried calls: 68

## Run metadata

- response_models: ['mistralai/Mistral-Large-Instruct-2411']
- requested_models: ['mistralai/Mistral-Large-Instruct-2411']
- temperature_sent: ['None']
- seed_sent: ['None']
- mutation_seed: [1337]
- seed_note: Featherless: seed 'Not reliable, as we use multiple servers'; none was sent.
- first_start_utc: 2026-10-21T18:51:06.547631+00:00
- last_finish_utc: 2026-10-22T04:30:42.684165+00:00
- api_calls_incl_retries: 212
- total_in_tokens: 2545704
- total_out_tokens: 172823
- total_latency_s: 32536.3
- harness_head: 3e2949e51848f9c478fd1a2652d10508f02e94cf
- harness uncommitted (git status, divergence/ + tests/):
```
M divergence/.gitignore
 M divergence/llm_call.py
 M divergence/mutate.py
 M divergence/replay_cache.py
?? divergence/runs/2026-10-21_mutants/
?? divergence/submission/thesis-4pager.html
?? divergence/submission/thesis-4pager.pdf
?? tests/test_mutate_runner.py
?? tests/test_mutate_specific.py
```
- Kill rule, SPECIFIC (primary), quoted from mutate.py:
```python
def match_specific(attacked, spec, regimes):
    """{"hit": bool, "attack_index": int|None, "excerpt": str|None}.
    Only landed attacks count. "terms": every group needs one matching
    term in the same attack. "overclaim": the attack is aimed at the
    overclaimed regime (its target matches that regime, or the text names
    it) AND it either says "settled" or proposes a downgrade. The excerpt
    is the normalised text, <=200 chars around the first match."""
    miss = {"hit": False, "attack_index": None, "excerpt": None}
    if not spec or not spec.get("groups"):
        return miss
    for idx, a in enumerate(attacked):
        if a.get("survived") is not False:
            continue
        text = _norm(f"{a.get('target', '')} || {a.get('attack', '')}")
        if spec["kind"] == "overclaim":
            aimed = (_target_regime_index(a.get("target"), regimes) == spec["regime_index"]
                     or _term_re(spec["regime"]).search(text) is not None)
            m = _term_re("settled").search(text)
            if aimed and (m is not None or a.get("downgraded_to")):
                start = m.start() if m else 0
                return {"hit": True, "attack_index": idx, "excerpt": text[max(0, start - 80):][:200]}
            continue
        first = None
        for group in spec["groups"]:
            m = next((mm for mm in (_term_re(t).search(text) for t in group) if mm), None)
            if m is None:
                break
            first = first or m
        else:
            return {"hit": True, "attack_index": idx, "excerpt": text[max(0, first.start() - 80):][:200]}
    return miss
```
- Kill rule, ANY-ATTACK (secondary):
```python
def _caught(attacked):
    return any(a.get("survived") is False for a in attacked)
```
