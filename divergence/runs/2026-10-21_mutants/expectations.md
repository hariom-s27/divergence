# Node-5 mutation sweep: pre-registered expectations (P03)

Written 2026-10-21, **before any live node-5 call** in this folder (pilot or full). Harness: `mutate.py` at HEAD 3e2949e plus the uncommitted P03 edits. Seed 1337. Adversarial slot `mistralai/Mistral-Large-Instruct-2411` on Featherless. No temperature and no seed are sent (the model's own default). The SPECIFIC matcher below is **frozen once the pilot starts**.

## 1. Kill rules

**PRIMARY: SPECIFIC.** A mutant is caught only if ONE landed attack (`survived: false`) points at the planted change. Code: `mutate.py` `build_spec()` derives the spec from original-vs-mutated data only, never from node 5's answer, and `match_specific()` applies it:

```python
for idx, a in enumerate(attacked):
    if a.get("survived") is not False:
        continue
    text = _norm(f"{a.get('target', '')} || {a.get('attack', '')}")
    if spec["kind"] == "overclaim":
        aimed = (_target_regime_index(a.get("target"), regimes) == spec["regime_index"]
                 or _term_re(spec["regime"]).search(text) is not None)
        m = _term_re("settled").search(text)
        if aimed and (m is not None or a.get("downgraded_to")):
            return hit
        continue
    # "terms": every group needs >=1 term found in this same attack's text
```
- `_norm` lowercases the text, `section N`/`s. N` → `s.N`, `_` → space, and digit-grouping commas are removed (`5,19,295.25` → `519295.25`).
- Terms match on alphanumeric boundaries.

Terms per operator:

| Operator | Terms |
|---|---|
| CITE_SWAP | the new provision string, its `Section N` / `s.N` / `Rule N` form, and the bare token if not all digits |
| DATE_SHIFT | the new date in 11 written forms |
| RATE_SUB | the substituted source name, a short alias, and `swapped` (the operator's own planted note says "SOURCE SWAPPED BY mutate.py") |
| LABEL_MISMATCH | the new label |
| ARITH_CORRUPT | the new figure as .2f, as-is, rounded and truncated |
| SILENT_OMIT | the removed entry's source or label |
| OVERCLAIM | structural: the attack is aimed at the overclaimed regime (same target/outcome word-overlap rule and thresholds as `node5_adversarial._match_target_certainty`, or it names the regime) AND it says "settled" or proposes `downgraded_to` |

The full pre-registered terms are in §5. The rule is unit-tested offline on synthetic critiques in `tests/test_mutate_specific.py` (11 tests).

**SECONDARY: ANY-ATTACK** (the original rule, unchanged), `mutate.py`:
```python
def _caught(attacked):
    return any(a.get("survived") is False for a in attacked)
```

## 2. Exclusions
- **No-op mutants:** C2 DATE_SHIFT (`'2026-06-17' -> '2026-06-17'`) and D1 DATE_SHIFT (`'2026-06-28' -> '2026-06-28'`). The request is byte-identical to the null, so nothing was planted. They are excluded from every denominator, still called, saved with `noop: true`, and listed in the summary. **Real mutants = 40 per repetition.**
- **ERROR:** a call that still fails after the harness's own retries is recorded as ERROR (`caught: null`) and is excluded from every denominator. It is counted separately, never as caught or survived. If more than 10% of calls error, the run stops.
- **NULL rows** are never in the mutation-score denominator.

## 3. Null and placebo definitions
- **Null mutant:** one per case per repetition (`op_null`, the identity transform), sent live like any mutant.
- **Null false-flag rate (ANY-ATTACK)** = nulls with ≥1 landed attack ÷ (6 × R).
- **SPECIFIC placebo (chance-match) rate:** each case's null critique is run through that case's own SPECIFIC spec for every real operator (`placebo_specific` in each NULL file). Rate = (null, operator) pairs that hit ÷ (40 × R) pairs. It estimates how often the SPECIFIC rule credits a "hit" when nothing was planted.
- **Term-clean subset** (pre-registered here, from §5's columns, before any call): the terms-kind mutants whose terms cannot already be found in the unmutated request. For SILENT_OMIT the condition is instead "term absent from the mutant request". 23 mutants:
  - C1: CITE_SWAP, DATE_SHIFT, RATE_SUB, LABEL_MISMATCH, ARITH_CORRUPT, SILENT_OMIT
  - C2: CITE_SWAP, LABEL_MISMATCH, ARITH_CORRUPT
  - C3: CITE_SWAP, DATE_SHIFT, ARITH_CORRUPT
  - C4: CITE_SWAP, RATE_SUB, LABEL_MISMATCH, ARITH_CORRUPT
  - C5: DATE_SHIFT, LABEL_MISMATCH, ARITH_CORRUPT
  - D1: CITE_SWAP, RATE_SUB, LABEL_MISMATCH, ARITH_CORRUPT

  SPECIFIC on this subset is reported beside the full-40 figure. It is a reporting cut, not a change to the matcher.

## 4. Predictions (written before the pilot)

| Operator | SPECIFIC, predicted | Why |
|---|---|---|
| CITE_SWAP | moderate–high (40–80%) | Node 5's core job is judging citations against the full corpus. `3(6)` and `116BBH` are not the cited provisions. C5's `Rule 57` is a real, different rule and is harder. |
| DATE_SHIFT | low (0–25%) | A one-day shift (or a reset onto the transaction date) inside a 12-method lattice. Nothing in the prompt invites date checks. |
| RATE_SUB | moderate (25–60%), **inflated** | The swapped source carries the operator's own note "SOURCE SWAPPED BY mutate.py -- label below was NOT regenerated to match". That is a textual giveaway, not a subtle defect. |
| LABEL_MISMATCH | low–moderate (10–40%) | The prompt allows attacking "a label on one", but the new labels are plausible lattice labels. |
| ARITH_CORRUPT | **low (0–15%)** | Node 5's user prompt says "do not attack the rupee figures themselves" (`node5_adversarial.py`, VALUATION LATTICE line). |
| SILENT_OMIT | low (0–20%) | An omission leaves nothing to point at. C1/C2 delete the only method, which is more visible. 5 of 6 specs are not term-clean. |
| OVERCLAIM | moderate–high (40–80%) | Certainty downgrades are node 5's main output, and the regime's reasoning still argues a hedged conclusion. |
| **ANY-ATTACK, all operators** | **very high (85–100%)** | The frozen unmutated D1 already drew 4/4 landed attacks. |
| **Null ANY-ATTACK false-flag** | **very high (80–100%)** | Same reason. If true, ANY-ATTACK cannot tell mutants from nulls. |
| SPECIFIC placebo | low (≤10%) overall | Higher where terms already occur in the request (C2/C3/C5 RATE_SUB names, SILENT_OMIT "the proxy", C5 Rule 57, C4 2026-06-18). |
| Overall SPECIFIC | ~25–45% of 40 | |

## 5. Pre-registered SPECIFIC specs (seed 1337; computed offline from the exact requests)

`in null request` / `in mutant request` = which terms already occur in the exact (normalised) text node 5 would receive.

| case | operator | kind | terms (any-of) | in null request | in mutant request |
|---|---|---|---|---|---|
| C1 | CITE_SWAP | terms | `Section 3(6), Integrated Goods and Services Tax `; `Section 3(6)`; `3(6)` | none | `Section 3(6), Integrated Goods and Services Tax `; `Section 3(6)`; `3(6)` |
| C1 | DATE_SHIFT | terms | `2026-06-17`; `17 june 2026`; `17th june 2026`; `june 17, 2026`; `june 17 2026`; `17 jun 2026` +4 more | none | `2026-06-17` |
| C1 | RATE_SUB | terms | `RBI Reference Rate`; `rbi reference rate`; `rbi`; `swapped` | none | `RBI Reference Rate`; `rbi reference rate`; `rbi`; `swapped` |
| C1 | LABEL_MISMATCH | terms | `domestic market, low x retrieved peg` | none | `domestic market, low x retrieved peg` |
| C1 | ARITH_CORRUPT | terms | `82492.90`; `82492.9`; `82493`; `82492` | none | `82492.9`; `82492` |
| C1 | SILENT_OMIT | terms | `invoice value, INR to INR -- no conversion` | `invoice value, INR to INR -- no conversion` | none |
| C1 | OVERCLAIM | overclaim | regime #1 `gst_export` aimed-at + (`settled` or downgraded_to) | n/a | n/a |
| C2 | CITE_SWAP | terms | `IGST Act, 2017, s.3(6)`; `s. 3(6)`; `3(6)` | none | `IGST Act, 2017, s.3(6)`; `s. 3(6)`; `3(6)` |
| C2 | DATE_SHIFT | NO-OP | (excluded) | | |
| C2 | RATE_SUB | terms | `SBI Forex Card Rates sheet, USD/INR TT BUY`; `tt buy`; `swapped` | `SBI Forex Card Rates sheet, USD/INR TT BUY`; `tt buy` | `SBI Forex Card Rates sheet, USD/INR TT BUY`; `tt buy`; `swapped` |
| C2 | LABEL_MISMATCH | terms | `SBI TTBR (last published BEFORE the receipt)` | none | `SBI TTBR (last published BEFORE the receipt)` |
| C2 | ARITH_CORRUPT | terms | `384932.05`; `384932` | none | `384932.05`; `384932` |
| C2 | SILENT_OMIT | terms | `SBI TTBR 2026-06-17 (published on the settlement` | `SBI TTBR 2026-06-17 (published on the settlement` | `SBI TTBR 2026-06-17 (published on the settlement` |
| C2 | OVERCLAIM | overclaim | regime #1 `gst_export` aimed-at + (`settled` or downgraded_to) | n/a | n/a |
| C3 | CITE_SWAP | terms | `Section 116BBH, Income-tax Act, 1961 — carried i`; `Section 116BBH`; `116BBH` | none | `Section 116BBH`; `116BBH` |
| C3 | DATE_SHIFT | terms | `2026-06-30`; `30 june 2026`; `30th june 2026`; `june 30, 2026`; `june 30 2026`; `30 jun 2026` +4 more | none | `2026-06-30` |
| C3 | RATE_SUB | terms | `Binance USDC/USDT close`; `binance`; `swapped` | `Binance USDC/USDT close`; `binance` | `Binance USDC/USDT close`; `binance`; `swapped` |
| C3 | LABEL_MISMATCH | terms | `domestic market, low x retrieved peg` | `domestic market, low x retrieved peg` | `domestic market, low x retrieved peg` |
| C3 | ARITH_CORRUPT | terms | `504966.97`; `504967`; `504966` | none | `504966.97`; `504966` |
| C3 | SILENT_OMIT | terms | `the proxy` | `the proxy` | `the proxy` |
| C3 | OVERCLAIM | overclaim | regime #0 `income_tax_on_receipt` aimed-at + (`settled` or downgraded_to) | n/a | n/a |
| C4 | CITE_SWAP | terms | `Section 116BBH, Income-tax Act, 2025`; `Section 116BBH`; `116BBH` | none | `Section 116BBH, Income-tax Act, 2025`; `Section 116BBH`; `116BBH` |
| C4 | DATE_SHIFT | terms | `2026-06-18`; `18 june 2026`; `18th june 2026`; `june 18, 2026`; `june 18 2026`; `18 jun 2026` +4 more | `2026-06-18` | `2026-06-18` |
| C4 | RATE_SUB | terms | `RBI Reference Rate`; `rbi reference rate`; `rbi`; `swapped` | none | `RBI Reference Rate`; `rbi reference rate`; `rbi`; `swapped` |
| C4 | LABEL_MISMATCH | terms | `SBI TTBR (next published AFTER the receipt)` | none | `SBI TTBR (next published AFTER the receipt)` |
| C4 | ARITH_CORRUPT | terms | `522444.83`; `522445`; `522444` | none | `522444.83`; `522444` |
| C4 | SILENT_OMIT | terms | `the proxy` | `the proxy` | `the proxy` |
| C4 | OVERCLAIM | overclaim | regime #1 `gst_export` aimed-at + (`settled` or downgraded_to) | n/a | n/a |
| C5 | CITE_SWAP | terms | `Rule 57, Income-tax Rules, 2026`; `Rule 57` | `Rule 57, Income-tax Rules, 2026`; `Rule 57` | `Rule 57, Income-tax Rules, 2026`; `Rule 57` |
| C5 | DATE_SHIFT | terms | `2026-06-30`; `30 june 2026`; `30th june 2026`; `june 30, 2026`; `june 30 2026`; `30 jun 2026` +4 more | none | `2026-06-30` |
| C5 | RATE_SUB | terms | `SBI Forex Card Rates sheet, USD/INR TT BUY`; `tt buy`; `swapped` | `SBI Forex Card Rates sheet, USD/INR TT BUY`; `tt buy` | `SBI Forex Card Rates sheet, USD/INR TT BUY`; `tt buy`; `swapped` |
| C5 | LABEL_MISMATCH | terms | `SBI TTBR (last published BEFORE the receipt)` | none | `SBI TTBR (last published BEFORE the receipt)` |
| C5 | ARITH_CORRUPT | terms | `275979.76`; `275980`; `275979` | none | `275979.76`; `275979` |
| C5 | SILENT_OMIT | terms | `SBI TTBR 2026-06-29 (next published AFTER the re` | `SBI TTBR 2026-06-29 (next published AFTER the re` | `SBI TTBR 2026-06-29 (next published AFTER the re` |
| C5 | OVERCLAIM | overclaim | regime #1 `gst_export` aimed-at + (`settled` or downgraded_to) | n/a | n/a |
| D1 | CITE_SWAP | terms | `Section 3(6), Integrated Goods and Services Tax `; `Section 3(6)`; `3(6)` | none | `Section 3(6), Integrated Goods and Services Tax `; `Section 3(6)`; `3(6)` |
| D1 | DATE_SHIFT | NO-OP | (excluded) | | |
| D1 | RATE_SUB | terms | `RBI Reference Rate`; `rbi reference rate`; `rbi`; `swapped` | none | `RBI Reference Rate`; `rbi reference rate`; `rbi`; `swapped` |
| D1 | LABEL_MISMATCH | terms | `SBI TTBR (last published BEFORE the receipt)` | none | `SBI TTBR (last published BEFORE the receipt)` |
| D1 | ARITH_CORRUPT | terms | `519295.25`; `519295` | none | `519295.25`; `519295` |
| D1 | SILENT_OMIT | terms | `the proxy` | `the proxy` | `the proxy` |
| D1 | OVERCLAIM | overclaim | regime #2 `gst_export` aimed-at + (`settled` or downgraded_to) | n/a | n/a |

(C3 CITE_SWAP's full-provision term is absent from the request only because `json.dumps` escapes `—` as `—`; its other two terms are present.)
