# DIVERGENCE

[![Python Package using Conda](https://github.com/hariom-s27/divergence/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/hariom-s27/divergence/actions/workflows/python-package-conda.yml)

**An AI can say "I don't know." It cannot say "the law does not determine one answer."**

DIVERGENCE is a pipeline that reads a real tax question, works out what the
rulebook actually provides, and — when the rulebook provides no method —
says so, with citations, instead of producing a confident number.

Built for Reverie Hacks 2026, ML Prompt Engineering track.

---

## The case

An Indian freelancer is paid **5,000 USDC** by an overseas client. It settles
at **03:14 IST on Sunday 28 June 2026**.

To file a return she needs one rupee figure. The Income-tax Rules, 2026 tell
her, to the day, *when* to value it — **Rule 56(i), Table row 1: the date the
property is received.** Four lines later, **Rule 57** lists the property types
for which a valuation method is prescribed. A virtual digital asset is not
among them, and the one residual clause that would have caught it is scoped to
section 26(2)(j), not section 92.

> **The rulebook asks a question of itself and, four lines later, declines to answer it.**

On that Sunday, SBI had published nothing (25 June, then a gap to the 29th),
FBIL had published nothing (weekdays only), and the market had a continuous
price. Every official source is silent and the market is not.

Twelve defensible methods survive. They span **₹4,69,750.00 to ₹5,17,618.76** —
a **₹47,868.76** spread, **10.19%** of the payment. Every one of the twelve is
arguable. None is prescribed.

**DIVERGENCE returns all twelve, and the reason there is no thirteenth that is
the right one.** Every figure in this repo is computed from
`canonical_case.json` by `node3_valuation.py`; no headline number is typed by
a human (D38).

---

## Architecture — five model calls and three deterministic checks

Never "seven nodes." 🤖 = a model that can be wrong. ⚙ = ordinary Python that
cannot hallucinate.

```
 invoice / payment ──▶ 🤖 1 EXTRACT ──▶ 🤖 2 GAP DETECTOR ──▶ ⚙ A GAP ENFORCER
                                                                    │
    canonical_case.json ──▶ ⚙ B VALUATION LATTICE ──▶ valuation.json │
                                                                    ▼
                              🤖 3 income-tax  🤖 4 GST  ──▶  ⚙ C CITATION MATCHER
                                                                    │
                                          🤖 5 ADVERSARIAL ──▶ disclosure record
```

The three ⚙ stages are the point. A model can be talked out of an instruction.
It cannot be talked out of an `if` statement.

- **⚙ A `gap_enforcer.py`** — any conclusion depending on something in
  `missing[]` has its certainty forced to `insufficient_evidence`, in code,
  regardless of how confidently the model worded it.
- **⚙ B `node3_valuation.py`** — enumerates 2 official dates + (5 market
  readings × 2 proxies) = 12 methods. Pure arithmetic, no model.
- **⚙ C `citation_matcher.py`** — every citation is checked against the corpus
  *and the tax year*. Both numbering systems are live (FY 2025-26 → the 1961
  Act; FY 2026-27 → the 2025 Act). A citation with no tax year is `REJECTED_NO_TAX_YEAR`.
  A conclusion whose citation fails is **dropped, not flagged**.

Full walkthrough: **[`PIPELINE-FLOW.md`](divergence/PIPELINE-FLOW.md)**.
Why each component exists, traced to a pre-registered failure:
**[`architecture.md`](divergence/architecture.md)**.

---

## Status — what actually runs, and what is still a human

This table is the honest version. Update it after every step.

| Stage | Automated? | Has it ever run for real? |
|---|---|---|
| 🤖 1 Extract | ✅ `node1_extract.py` | ✅ full end-to-end runs on D1 and C2, 20 Aug |
| 🤖 2 Gap detector | ✅ `node2_gaps.py` | ✅ full end-to-end runs on D1 and C2, 20 Aug |
| ⚙ A Gap enforcer | ✅ `gap_enforcer.py` | ✅ self-test 2/2 |
| ⚙ B Valuation lattice | ✅ `node3_valuation.py` | ✅ produces `valuation.json` |
| 🤖 3 Income-tax resolver | ❌ hand-run prompt | ❌ not yet |
| 🤖 4 GST resolver | ❌ hand-run prompt | ❌ not yet |
| ⚙ C Citation matcher | ✅ `citation_matcher.py` | ✅ 15/15 self-test |
| 🤖 5 Adversarial check | ❌ hand-run prompt | ❌ **never run — every finding credited to it was found by a human** |
| ⚙ D Disclosure composer | ❌ static HTML template | ❌ not wired to a live record |
| Arms A/B (baseline, CoT) | ✅ `run_arms.py` | ✅ all 6 cases, 20 Aug — see **First real numbers** below |
| Scoring | ✅ `eval/score.py` + `eval/m3b_citation_coverage.py` + `eval/normalize_runs.py` | ✅ run against all 14 real records, 20 Aug |
| CI | ✅ GitHub Actions, pytest | ✅ green — badge above |

Nodes 3/4/5 rejoin the automated path through
`run_pipeline.py --regimes <file>`, which runs their hand-coded conclusions
through the citation matcher and gap enforcer exactly as an automated node's
output would be.

---

## First real numbers — Steps 27/29/31, 20 Aug

The first time any of nodes 1–2, `run_arms.py`, or the scorers ran as a
whole chain against a real model, instead of in isolation. Five real bugs
found in two hours — none visible from reading the code, all visible in
seconds of watching it run. Full account, every bug, every before/after:
**[`DECISION-D45.md`](divergence/DECISION-D45.md)** ·
**[`iteration-log.md`](divergence/step22drop/iteration-log.md)**.

**Fixed along the way, not before shipping:** a silent protocol violation
(`temperature=0` contradicting the pre-registered "default, not zero"), two
`schema.json` gaps that had existed since 6 August and simply never been
exercised (`date_choice.chosen` rejecting its own documented `null`;
`extracted_field.value` never allowing boolean, though every case's ground
truth already uses one), a 7B model's contract violation reaching a schema
error three steps downstream of its real cause, arm A's first run echoing
the raw JSON-Schema definition back instead of producing data, and arm B's
token-match arithmetic starving a single completion by capping it at the
sum of two much smaller separate calls.

**After all five fixes, real numbers, all 6 cases:**

| Case | Arm | M1 extract | M2 recall | M2 prec | M3 valid | M4 methods | M5 |
|---|---|---|---|---|---|---|---|
| C1 | A / B | 0.0% | — | 0.0% | 25.0% | 2/1 | — |
| C2 | A / B / C | 9.1% | — | 0.0% | 50.0% / — | 2/1 / 12/1 | — |
| C3 | A / B | 0.0% | 0.0% | 0.0% | 25.0% / 20.0% | 2/5 | — |
| C4 | A / B | 0.0% | 0.0% | 0.0% | 50.0% / 100.0% | 2/10 | — |
| C5 | A / B | 0.0% | 100.0% | 100.0% / 33.3% | 50.0% | 2/2 | — |
| D1 | A / B / C | 0.0% / 9.1% | 75.0% / 25.0% / 0.0% | 100.0% / 33.3% / 0.0% | 60.0% / 50.0% / — | 2/12 / 2/12 / 12/12 | — |

**Read this before quoting a single cell.** M1 and M5 are not "the system
scored badly" — they currently **cannot be computed correctly from any
output that exists**, for any arm:

- **M1** compares `facts{}` by field name, and no extractor (pipeline,
  arm A, or arm B) has ever been told to use `ground_truth.json`'s exact
  vocabulary — `asset` vs `asset_currency`, `settlement_datetime_ist` vs
  `settlement_datetime`, and so on. A real extraction scores as "not
  extracted" if it used a different, equally correct field name.
- **M5** ("the metric that earns trust," `evaluation-design.md`) needs
  `elements{}` — no prompt anywhere currently asks any arm to report it.
- **Arm C's M3/M4 look strong on D1/C2** (12/12, 12/1) because ⚙ B's
  valuation lattice enumerates methods deterministically, no model
  involved — real, but not the full comparison D40 asks for, since
  `regimes[]` is still empty (nodes 3/4/5 haven't run) so arm C's citation
  numbers read `—`, not zero-and-losing.
- **M2/M3 are the genuinely comparable numbers here**, and on D1 — the
  deep case — arm A's gap recall (75%) currently *beats* arm B's (25%).
  Worth investigating, not smoothing over, before it goes in `results.md`.

---

## Running it

```powershell
cd divergence
pip install -r requirements.txt

# once per terminal. Key in the shell, never in a file.
$env:FEATHERLESS_API_KEY = "rc_..."

# ~10 seconds, a few hundred tokens. Do this before every session.
python check_llm.py

python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" `
    --text step21drop\cases\D1\case.md `
    --out runs\D1_pipeline.json

# arms A (naive) and B (token-matched CoT), all 6 cases
$env:DIVERGENCE_TEMPERATURE = "default"    # the scored protocol -- default, not zero
python run_arms.py --arm A --all-cases
python run_arms.py --arm B --all-cases --token-match runs\

# score everything real that exists in runs/
python eval\normalize_runs.py --report
python eval\m3b_citation_coverage.py --all runs\
```

Full instructions: **[`HOW-TO-RUN.md`](divergence/HOW-TO-RUN.md)** ·
key handling: **[`API-KEY-SETUP.md`](divergence/APIKEYSETUP.md)**

**Featherless only.** There is no automatic fallback to Anthropic, on purpose
— see D44 below.

| Slot | Model |
|---|---|
| `small` | `Qwen/Qwen2.5-7B-Instruct` |
| `large` | `Qwen/Qwen2.5-72B-Instruct` |
| `adversarial` | `mistralai/Mistral-Large-Instruct-2411` |

The adversary is a different model family from the resolvers by design (D41).
A model checking its own work agrees with itself; "the adversarial node found
nothing" would then mean nothing. `check_llm.py` warns if you break it.

---

## Corpus

`divergence/corpus/tier-a/` holds statutory text, one provision per file, with
a `provision_id`, the current and former citation, the tax year each applies
to, and the gazette page it came from. `corpus/verbatim/` is the same files cut
down to statutory text only, between `<!-- VERBATIM-START -->` markers — that
is what prompts receive. Commentary is never injected (D31); an earlier build
was injecting roughly 40% our own analysis back into the model as if it were
law.

Each resolver sees only its own regime's text (C22), so citing across regimes
is structurally impossible rather than discouraged.

Tier B (`FBIL-METHODOLOGY.md`, `COMMENTARY.md`, `SG-UAE.md`) is context and is
never citable.

---

## What the gazette gave us

Read from the notified Income-tax Rules, 2026 (Gazette, Part II Sec 3(i),
20 March 2026) — **[`GAZETTE-FINDINGS.md`](divergence/GAZETTE-FINDINGS.md)**:

- **Rule 57** — seven rows, and column B scopes the residual clause away from s.92
- **Rule 206(3)** cites the **Foreign Exchange Regulation Act, 1973** — repealed
  in 2000. Rule 210, four rules later on the same pages, cites FEMA 1999.
  Machine-counted: FERA appears once in the whole instrument, in the rule that
  governs converting our freelancer's income.
- **Rule 207** has the fallback for an unpublished rate. **Rule 206 imports the
  definition from Rule 207 and leaves the remedy behind** — and Rule 207(2)
  excludes a resident receiving, so you cannot argue your way into it.
- **Rule 247(4)** names *"a valuer of virtual digital assets"* — then Form 169's
  eleven asset classes don't include one, Rule 247(3) leaves the qualification
  to a Commissioner's conclusive discretion, and Rule 57 gives that valuer no
  method. **Four locked doors are absences. This one is a nameplate with no room behind it.**

---

## Decisions

| | |
|---|---|
| **D31** | prompts receive `corpus/verbatim/` only, never commentary |
| **D35** | the eval runs on Featherless open weights; the Claude ₹/record figure is a *metered deployment estimate*, not a measured run |
| **D38** | no headline number is typed by a human |
| **D39** | three arms: naive · token-matched CoT · pipeline |
| **D40** | five metrics + Silent Failure Rate |
| **D41** | node 5 runs on a different model family from the resolvers |
| **[D42](divergence/DECISION-D42.md)** | provider chosen at runtime and **recorded** in every record's `_meta.llm` |
| **[D43](divergence/DECISION-D43.md)** | which Featherless model fills each slot — and the finding that every `meta-llama/*` id is licence-gated on this account |
| **[D44](divergence/DECISION-D44.md)** | Featherless only, no silent fallback; repo hygiene; pre-registration re-freeze |
| **[D45](divergence/DECISION-D45.md)** | Steps 27/29/31: the first real end-to-end runs — five real bugs found only by running the thing, none visible from reading the code |

---

## Evaluation

Three arms (D39), six cases, five metrics (D40), plus Silent Failure Rate.
**[`evaluation-design.md`](divergence/step21drop/evaluation-design.md) §7 states in
advance what result would falsify the claim** — written before any arm was run.

Ground truth is committed before any model runs, and `results.md` quotes the
commit hash. That is the pre-registration; see D44 for why the hash matters.

---

## Honest limitations

- Six cases is small. It is a hackathon.
- Nodes 3/4/5 are prompts run by hand, not code.
- **Node 5 has never run.** Everything attributed to adversarial review in this
  repo was found by a person.
- The 7B `small` slot extracts less accurately than a frontier model would.
  Where it does, that is a **measurement** about running this pipeline on open
  weights, and it is reported as one.
- Two case inputs are typed transcripts rather than photographed documents.
- Seven corpus files carry open `known_limitation` fields. They are in the
  frontmatter, not hidden.
- **M1 (extraction accuracy) cannot be scored correctly yet, for any arm.**
  No extraction prompt is pinned to `ground_truth.json`'s exact field
  vocabulary, so a correct extraction under a different field name scores
  as a miss. See D45.
- **M5 (false abstention) is undefined on every run so far** — no prompt
  asks any arm to report the `elements{}` shape the scorer needs.
- **Arm C's citation numbers aren't real yet either** — `regimes[]` is
  empty until nodes 3/4/5 actually run for a case via `--regimes`.
- `citation_matcher.py` mis-resolves a bare, unqualified citation (e.g.
  `"Section 2(111)"` with no Act name) against the wrong corpus file. Not
  fixed — worked around in ground truth by citing the qualified form.

Everything that broke, and what it cost, is in
**[`iteration-log.md`](divergence/step22drop/iteration-log.md)** — including the
day the citation matcher scored 15/15 because retired corpus files were
alphabetically shadowing their replacements. The code was right. The folder was
wrong. Nothing in the output said so.

---

## Repo layout

Everything under `divergence/` is the submission. Root-level files
(`step1.md` through `step-13-selection.md`, `COMPLETE-ROADMAP.md`,
`STATE-OF-PLAY.md`, and similar) are the design-process trail from before
`divergence/` existed as its own folder — kept for provenance, not part of
the submission itself. `_archive/` (gitignored) holds retired/duplicate
files moved there by `cleanup_repo.py` — nothing was deleted, just gotten
out of the way of anyone reading the live corpus.

`tests/` and the root `conftest.py` exist only to make `tests/test_gap_enforcer.py`
importable in CI (`divergence/__init__.py` too) — they're plumbing for the
GitHub Actions badge above, not part of the evaluation itself.
