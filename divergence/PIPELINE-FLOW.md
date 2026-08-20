# PIPELINE FLOW — how DIVERGENCE actually runs, end to end
### Plain-language walkthrough. For the "why", see `architecture.md`. This file is the "how."

---

## The one-sentence version

An invoice and a payment record go in. Five things a model reads happen,
three things ordinary code checks happen, and one disclosure record comes
out — and at every step, if something is missing or uncertain, the code
downgrades the answer instead of letting the model talk past it.

---

## The whole chain, in order

```
 invoice/payment          "small" model              "small" model
     text or image  ──▶  🤖 1 EXTRACT   ──▶  facts{}  ──▶  🤖 2 GAP DETECTOR ──▶ missing[]
                       node1_extract.py                    node2_gaps.py
                                                                  │
                                                                  ▼
                                                    ⚙ A GAP CONSTRAINT ENFORCER
                                                        gap_enforcer.py
                                                     (no model — plain code)
                                                                  │
      canonical_case.json                                        │
             │                                                    │
             ▼                                                    │
    ⚙ B VALUATION LATTICE                                         │
      node3_valuation.py  ──▶  valuation.json                     │
      (no model — plain code)                                     │
             │                                                    │
             └──────────────────────┬─────────────────────────────┘
                                     ▼
                      run_pipeline.py assembles ONE record
                      (facts + missing + valuation + regimes + limits)
                                     │
                                     ▼
                          ⚙ C CITATION MATCHER
                          citation_matcher.py  (no model)
                    drops any conclusion whose citation
                       doesn't check out for the tax year
                                     │
                                     ▼
                    schema.json validation, then written
                          to runs/<record-id>_pipeline.json
```

**Nodes 3, 4 and 5** — the actual income-tax resolver, GST resolver, and
adversarial checker — are prompts today (`step22drop/prompts/03/04/05.md`),
not code. They're run by hand in a fresh chat session per
`step21drop/evaluation-design.md`'s protocol, and their output is hand-coded
into a JSON file with a `"regimes"` array. `run_pipeline.py --regimes
<that file>` is where they rejoin the automated part — it runs their
conclusions through the citation matcher and the gap enforcer exactly like
an automated node's output would go through them.

---

## What each file actually does, one at a time

**1. `node1_extract.py` — reads the raw document**
You give it `--text case.txt` (typed transcript) or `--file invoice.png`
(a photo — sent as an image). It asks a small model to pull out fields like
amount, asset, date, counterparty — each one tagged with how confident the
model is and where in the document it came from. Writes `facts.json`.

**2. `node2_gaps.py` — reads the facts, finds what's absent**
Takes `facts.json`, plus a small fixed set of law-text excerpts about what
evidence GST/FEMA/income-tax actually require (a bank certificate, a
purpose code, and so on). Asks a small model: given these facts, what's
missing that the law would need? Writes `missing.json`. This runs *before*
anything tries to reach a conclusion — so a missing document is established
as a fact, not discovered as an afterthought.

**3. `gap_enforcer.py` — the part that isn't a model at all**
Takes any conclusion that says "I depend on something in `missing[]`" and
forcibly sets its certainty to `insufficient_evidence`, in plain Python, no
matter how confidently the model worded the conclusion. A model can be
talked into ignoring an instruction. Code can't be talked into skipping an
`if` statement.

**4. `node3_valuation.py` — the twelve prices (already built, no model)**
Reads `canonical_case.json` (the frozen facts of the headline case: candle
prices, official rates, the USDC/USDT proxy), enumerates every combinationof
date × market-reading × proxy, and writes `valuation.json` — always at least
two figures, never one. Pure arithmetic.

**5. `run_pipeline.py` — wires 1, 2 and A together, pulls in B and C**
This is the one you actually run. It calls node 1, then node 2, then folds
in whatever `valuation.json` already has, then (if you pass `--regimes`)
runs those hand-coded resolver conclusions through the citation matcher and
the gap enforcer, then writes one JSON file that matches `schema.json` and
tells you whether it validated.

**6. `citation_matcher.py` — checks every citation is real and current**
Every citation any resolver produces gets checked against the actual corpus
text and the stated tax year. If it doesn't match, the whole conclusion it
was attached to gets dropped — not flagged, dropped.

---

## Which model actually answers each call

`llm_call.py` is the only file that talks to a model. It picks a provider at
runtime from whichever API key is set in your shell (Featherless preferred,
Anthropic as a fallback/cost-estimate path — see `DECISION-D42.md`), and
resolves `"small"` / `"large"` / `"adversarial"` to real model IDs — see
`DECISION-D43.md` for exactly which ones and why. Run `python check_llm.py`
before any real pipeline run — it costs a few hundred tokens and tells you
if all three slots actually work on your account *before* you spend real
money finding out mid-run.

---

## A run, start to finish

```powershell
# once per terminal session
$env:FEATHERLESS_API_KEY = "rc_..."

# ten seconds, a few hundred tokens — do this first, every time
python check_llm.py

# the automated front half: extract -> find gaps -> enforce
python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" `
    --text step21drop\cases\D1\case.md `
    --out runs\D1_pipeline.json

# to also fold in a hand-run resolver's output (arm C, from prompts 03/04/05):
python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" `
    --text step21drop\cases\D1\case.md `
    --regimes step21drop\cases\D1\regimes_armC.json `
    --out runs\D1_armC_pipeline.json
```

Whatever happens — success or a hard failure — goes in
`step22drop/iteration-log.md`. That's not optional; it's how this project
tells the difference between "we built it" and "we watched it work."

---

## What's automated today vs. what's still done by hand

| Step | Automated? |
|---|---|
| 🤖 1 Extract | **Yes** — `node1_extract.py`, real API call |
| 🤖 2 Gap detector | **Yes** — `node2_gaps.py`, real API call |
| ⚙ A Gap enforcer | **Yes** — plain code, always was |
| ⚙ B Valuation lattice | **Yes** — plain code, always was |
| 🤖 3/4 Income-tax & GST resolvers | **No** — hand-run prompt, fed in via `--regimes` |
| ⚙ C Citation matcher | **Yes** — plain code, always was |
| 🤖 5 Adversarial checker | **No** — hand-run prompt, never run yet at all |
| ⚙ D Disclosure composer | **No** — `output-interface.html` is a static template, not wired to a live record yet |

See `step22drop/iteration-log.md`'s "Still open" section for the up-to-date
version of this list — this file describes the shape of the pipeline, that
one tracks what's actually been run.
