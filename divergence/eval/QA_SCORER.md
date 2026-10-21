# QA_SCORER — rules of the QA benchmark scorer

`divergence/eval/qa_scorer.py` scores model answers to the tax QA benchmark against gold nuggets. It is separate from `score.py`, which scores the six hackathon cases. It uses only the Python standard library, and it is deterministic: the same files always give the same output.

```
python divergence/eval/qa_scorer.py --gold G.jsonl --responses R.jsonl --out O.json [--allow-test]
```

The gold format is in `gold_schema_draft.json`. **It is a draft, not frozen yet**; a later decision doc will freeze it. Each responses line is `{"qid": "...", "response": "<raw model output>"}`. The output file holds the scorer's SHA-256, one row per question with every intermediate value, and three sets of aggregates: `primary`, `sensitivity` and `lenient_act`.

Examples below use `₹` and plain made-up numbers. None of them is a real tax fact.

---

## 1. What gets scored: the final line

| Rule | Example |
|---|---|
| Only the **last** line that starts with `ANSWER:` or `ABSTAIN:` is scored. Matching is case-insensitive, and markdown bold/italic is stripped first. | `ANSWER: 10%` … `**answer:** 11%` → `11%` is scored |
| Multi-part answers use `nid=value` pairs separated by `;`. | `ANSWER: n1=12%; n2=₹40,000` |
| No `nid=` key and exactly one nugget: the whole value applies to that nugget. | `ANSWER: 12%` with one nugget `n1` |
| Abstention means **only** an `ABSTAIN:` marker or an empty `ANSWER:` line. | `ABSTAIN: no version applies`; `ANSWER:` |
| A prose refusal with no marker is flagged `prose_refusal=true`. It is scored as answered in the primary run and as abstained in the sensitivity run. | `I cannot answer this.` |
| No final line at all: flagged `no_final_line=true` and scored answered-wrong (D1). | `The rate is 12%.` (no `ANSWER:`) |
| Two different values for one nugget: that nugget is wrong (`hedged`). | `ANSWER: 20% or 30%` |

## 2. Normalisation (applied to the response and to the gold alike)

| Rule | Example |
|---|---|
| Unicode NFKC, lower-case, `**` `*` `__` and backticks stripped. A curly apostrophe becomes `'`. | `**Rs. 1,50,000**` → `rs. 1,50,000` |
| Currency markers removed: `₹`, `Rs.`, `Rs`, `INR`, `rupee(s)` (as whole words only). | `INR 5,000` → `5000`; the "rs" inside `years` is left alone |
| Commas removed in any grouping. | `1,50,000` and `150,000` → `150000` |
| `lakh(s)` ×10^5 and `crore(s)` ×10^7, computed in `decimal.Decimal`, never float. | `1.5 lakh` → `150000`; `2 crore` → `20000000` |
| Percent markers `%`, `per cent`, `percent` and `pc` (only right after a number). The rate is stored as the printed percentage. | `30 per cent` → `30` |
| A bare fraction where a rate is expected is wrong, and is never multiplied by 100. | `0.30` for gold `30%` → wrong, `bare_fraction` |
| Dates → ISO `YYYY-MM-DD`. Accepted: `1st April, 2026`, `01/04/2026` (day-first), `April 1, 2026`, `1 April 2026`, `2026-04-01`, `1-4-2026`. | all → `2026-04-01` |
| A tax year is stored as its start year. Accepted: `2026-27`, `2026-2027`, `TY 2026-27`, `FY 2026-27`, `tax year 2026-27`. | → `2026` |
| An assessment year (`AY 2027-28`, `assessment year 2027-28`) is a different concept. It is flagged `assessment_year` and never mapped to a tax year. | `AY 2027-28` for a tax_year nugget → wrong |
| Sections are read as a tuple `(act, section, subsection, clause)`. The prefixes accepted are `section`, `under section`, `u/s`, `sec`, `sec.`, `s` and `s.` (D9). | `s. 80CCD(1b)(ii) of the 1961 Act` → `("1961", "80CCD", "(1b)", "(ii)")` |
| Act tags recognised: `of the 1961 Act`, `Income-tax Act, 2025`, `(2025 Act)`, `1961 Act`, `Act, 2025`. | `u/s 393(1), Income-tax Act, 2025` → act `2025` |

## 3. Matching, by nugget type

| Type | Rule | Example |
|---|---|---|
| `rate`, `threshold`, `limit` | Exact equality of the normalised Decimal values. | gold `₹3,25,000` vs `Rs. 3.25 lakh` → correct |
| `date` | Exact ISO equality. | gold `1st April, 2026` vs `01/04/2026` → correct |
| `tax_year` | Exact start-year equality. | gold `2026-27` vs `FY 2026-27` → correct; vs `AY 2027-28` → wrong |
| `section` | The tuple must match down to `section_depth`, **and** the Act must match. A 1961-Act section given for a 2025-Act nugget is wrong even when the number is the same. | gold `393(1)`/2025/subsection vs `section 393(1) of the 1961 Act` → wrong |
| `amount` | Absolute tolerance = half a unit of the last digit printed in the **gold** string, read before normalisation. The bound is inclusive. | gold `₹1,23,450` → ±0.5; gold `₹1.2 lakh` → ±5,000 |

**Version accuracy** is a separate flag on each section nugget that has an `act`: `version_ok` is true when the response's Act is correct, whatever the section number. Example: `section 999 of the 2025 Act` for gold `section 901`/2025 is wrong as a nugget but has `version_ok = true`.

## 4. Per-question states and cells

- Each nugget is **correct**, **wrong** or **withheld**. A nugget that a non-abstaining answer leaves out is withheld.
- **Strict score**: 1 only if every nugget is correct.
- **Question abstained**: an ABSTAIN marker, or every nugget withheld.
- **Cells**: N1 = should-answer, answered and strict-correct · N2 = should-answer, answered and not strict-correct · N3 = should-answer and abstained · N4 = should-abstain and answered · N5 = should-abstain and abstained.

## 5. Metrics (Wen et al. matrix, as in DR-3)

| Metric | Formula |
|---|---|
| Accuracy | (N1+N5)/N |
| Abstention precision | N5/(N3+N5) |
| **Abstention recall** | **N5/(N4+N5)** |
| Abstention F1 | 2PR/(P+R); None if P or R is None; 0 if P = R = 0 |
| Coverage | (N1+N2+N4)/N |
| Abstention rate | (N3+N5)/N |
| ARSP | N3/(N1+N2+N3) |
| R-Acc | N1/(N1+N2+N4) |
| Effective Reliability (ER) | (N1−N2−N4)/N; can be negative |
| Nugget coverage | answered nuggets / all nuggets |
| Nugget precision | correct nuggets / answered nuggets |
| Nugget Φc (c = 1, 10) | mean over questions with k ≥ 1 of (correct − c·wrong)/k |
| Question Φc (Whitehead; c = 1, 10) | mean over N of: +1 if N1, −c if N2 or N4, 0 if N3 or N5 |
| Version accuracy | version_ok / answered section nuggets that have an Act |

**Abstention recall.** It is pre-registered as N5/(N4+N5): of the questions that should be abstained on, the share that were. Wen et al. print N5/(N2+N4+N5). N2 is a should-answer cell and has no place in a recall over should-abstain questions, so the printed formula is treated as a typo. The code comment in `aggregate()` says the same thing.

**Zero denominators.** A metric whose denominator is 0 is reported as `None`, never 0, and `none_reasons` names the empty denominator (for example `"denominator N3+N5 = 0"`). Metrics are exact `fractions.Fraction` values. The JSON gives each one as `"p/q"` plus a rounded float for reading.

## 6. The three aggregate variants

| Variant | What changes | Example |
|---|---|---|
| `primary` | the rules above | `I cannot answer.` → answered, N2 |
| `sensitivity` | a prose refusal counts as an abstention (its nuggets become withheld) | `I cannot answer.` → N3 |
| `lenient_act` | a section with no Act tag inherits the question's `governing_act`, when that is 1961 or 2025 | `section 901` on a 2025 question → correct here, wrong in primary |

## 7. Decisions D1–D22 (owner-approved 2026-10-22)

| # | Decision | Rule | Example |
|---|---|---|---|
| D1 | No final line | Scored as answered-wrong: `no_final_line=true`, every nugget wrong (`forced`), cell N2 or N4. | `The rate is 5%.` → N2 |
| D2 | Missing Act | **Primary:** a section nugget whose `act` is set and whose response has no Act tag is wrong, with `act_missing=true`. **Lenient (reported separately):** the Act is inherited from `governing_act` when that is 1961 or 2025. With `both`/`none` there is nothing to inherit, so it stays wrong. **Every arm's prompt MUST tell the model to name the Act for each section it cites.** | `ANSWER: section 901` on a 2025 question → primary wrong, lenient correct |
| D3 | "pc" | It is a percent marker only directly after a number. | `30pc` → 30; `the pc rate is 30` → unmarked |
| D4 | Unparseable dates | An unparseable or impossible response date makes the nugget wrong (`date_unparsed` / `date_invalid`). An unparseable gold date stops the load with ValueError. Dates with slashes are always day-first. | `31/02/2026` → wrong; `04/01/2026` → 2026-01-04 |
| D5 | Decimal tolerance | Exact Decimal arithmetic in a 50-digit context, with no rounding. tol = 0.5 × 10^(−decimals printed) × multiplier. Inclusive. Trailing zeros count as printed digits. | `₹2 lakh` → ±50,000; `₹1,20,000` → ±0.5 |
| D6 | Hedges | Two or more **distinct** normalised values in a nugget = `hedged` → wrong. The same value written twice is fine. | `20% or 30%` → wrong; `30% (30 per cent)` → correct |
| D7 | Rate with no marker | Accepted and flagged `rate_unmarked`. A value below 1 is flagged `bare_fraction` and, for a percentage gold, is wrong. | `30` for `30%` → correct; `0.30` → wrong |
| D8 | Threshold/limit with money words | Compared as Decimal values after full normalisation, with no tolerance. | `₹1.5 lakh` = `1,50,000` |
| D9 | Section forms | Prefixes accepted: `section(s)`, `under section`, `u/s`, `sec`, `sec.`, `s`, `s.`. Each must start a word, so `intersection 901` and `this 901` are not sections. A bare token (`393(1)`, `80C`; at most 3 digits) is read **only** inside a section nugget's value, and only when no prefixed reference is present. Years and amounts are never read as bare sections. | `u/s 901` → 901; bare `393(1)` in a section nugget → 393(1); `₹1,50,000` → no section |
| D10 | Section depth | Compared down to `section_depth`. A deeper response is fine; a shallower one is wrong (`too_shallow`). Clause parens `(a)(ii)` are compared as one string. Two distinct sections = hedge. Naming both Acts = `act_hedged` → wrong. | gold `393(1)`/subsection vs `393(1)(a)` → correct; vs `393` → wrong |
| D11 | Tax years | The end year must be start+1. A bare `2026` is not a tax year. An AY alone → wrong (`assessment_year`). If a valid tax year is also present, the tax year decides and the AY is only flagged. | `TY 2026-27 (AY 2027-28)` → 2026, flagged; `2026-28` → wrong |
| D12 | Unkeyed multi-part | With no **known** nid key and more than one nugget, every nugget is wrong (`unkeyed_multi`). It is not withheld, so a malformed answer can't become an abstention. Unknown keys are ignored and listed in `unknown_nids`. The same nid given twice with different values is a hedge. With one nugget and no known key, the whole value applies to that nugget, even if it contains another `x=` key. | `ANSWER: 12%, ₹40,000` with two nuggets → both wrong |
| D13 | Markdown | `**`, `*`, `__` and backticks are stripped. A single `_` stays (nids may contain `_`). A list bullet before the marker means it is not a final line. | `**ANSWER:** 5%` → final line; `- ANSWER: 5%` → not one |
| D14 | Prose refusal | Fixed phrase list, checked over the whole response only when there is no abstain marker: cannot answer, can't answer, unable to answer/determine, cannot be determined, insufficient information, not enough information, I don't know, I do not know, no applicable version/provision. | `I don't know.` → `prose_refusal=true` |
| D15 | Question Φc | Whitehead: +1 for N1, −c for N2 or N4, 0 for N3 or N5. A correct abstention earns 0, not +1. Nugget Φc is averaged over questions with k ≥ 1. | N1=3, N2=2, N4=2, N=10 → Φ1 = −1/10 |
| D16 | Nugget population | All nuggets of all questions. An abstained question's nuggets count as withheld. | an ABSTAIN on a 2-nugget question adds 2 withheld nuggets |
| D17 | Sealed test split | `load_gold` refuses any `split=test` row unless `--allow-test` is given. | `split: "test"` → ValueError |
| D18 | Imports | Stdlib only: re, decimal, unicodedata, datetime, json, hashlib, plus argparse, os, sys and fractions. All exist in 3.10. `dataclasses` turned out not to be needed. | metrics are `Fraction(2, 3)`, not 0.666… |
| D19 | Fixture responses | Each fixture line carries a `response` field (and `synthetic: true`). `load_responses` reads `qid`+`response`, so `--responses` can point at the fixture itself. | `--gold F --responses F` |
| D20 | gate0 | No number in this file or the fixture matches gate0's retired-figure patterns, so no `stale-ok` markers are needed. | `python gate0_check.py` reports no stale-number hits |
| D21 | 3.10/3.11 check | The tests are plain `assert` functions with no pytest-only features, so they also run under a small stdlib runner on an interpreter without pytest. CI on 3.10 is the real check. | — |
| D22 | Missing responses | A gold qid with no response → the CLI exits 2 and lists the qids. Extra response qids are ignored with a warning. | gold `Q1`, responses only `Q2` → exit 2 |

### Further choices made while implementing (no spec rule covered them)

| # | Choice | Example |
|---|---|---|
| I1 | Number extraction removes section references and Act years first, so they are not counted as a second value. | `limit u/s 901 is ₹40,000` → 40000 only |
| I2 | A nugget forced wrong (D1/D12) on a section with an Act counts as answered with `version_ok=false`. | no final line on a section question → version miss |
| I3 | Version accuracy counts only **answered** section nuggets that have an `act`. Withheld ones carry no Act, so they are left out. | 4 answered, 2 right Act → 2/4 |
| I4 | The output carries `scorer_sha256` (raw bytes) and `scorer_sha256_lf` (CRLF→LF first). With `core.autocrlf=true`, a Windows checkout and CI hash the raw file differently. The LF hash is the same on both, so the freeze should cite it. | — |
| I5 | Gold validation also checks: `should_abstain` ⇔ `abstain_reason != answerable`; a should-answer question has ≥ 1 nugget; `match` agrees with `type`; nids are unique; every gold string parses as one value; no unknown keys apart from `synthetic`/`response`. | `match: tolerance` on a rate → ValueError |
