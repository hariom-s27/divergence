# HOW TO RUN EVERYTHING
### All the code we have written, in one place
**6 August 2026**

---

## THE SHORT VERSION

Put every file in one folder, keeping `corpus/` as a sub-folder. Then:

```
python3 run_all.py
```

That runs both scripts and prints a summary. **Nothing to install.** Standard library only.

---

## THE FOLDER MUST LOOK LIKE THIS

```
divergence/
├── run_all.py              ← run this
├── killgate.py
├── citation_matcher.py
├── schema.json
├── corpus/
│   ├── MANIFEST.md
│   ├── tier-a/             ← 17 files
│   └── tier-b/
└── cache/                  ← created automatically
```

**`citation_matcher.py` reads `corpus/tier-a/`. If the folder isn't beside it, it finds nothing.**

---

## STEP 0 — Do you have Python?

```
python3 --version
```

A number like `3.11.4` means yes. On Windows try `python --version` if that fails.
No Python? Download from **python.org**, install, then reopen the terminal.

---

## THE TWO SCRIPTS

### 1. `killgate.py` — needs internet

```
python3 killgate.py
```

**What it does.** Checks whether the rate data our headline demo depends on can actually be retrieved. Probes five CoinDCX pair codes, reports how far the history reaches, pulls the USDC peg from Binance, gets USD/INR from two fallbacks, caches everything to `./cache/`.

**What you read.** The last section. It prints one of three verdicts:

| Verdict | What to do |
|---|---|
| **✅ GO** | Recompute the gap from the real data with `node3_valuation.py`. |
| **⚠️ PARTIAL** | API works, history too short. Try `interval=1h` instead of `1d` inside the file. |
| **⛔ NO-GO** | Switch the headline to the weekend case. Already fully evidenced from the SBI archive. |

**Already run once — result: GO.** Pair is `I-USDT_INR`, history 25 Mar 2025 → 6 Aug 2026. The recomputed range, from `node3_valuation.py`: ₹4,69,750.00 → ₹5,17,618.76 (spread ₹47,868.76, 10.19%, 12 defensible figures).

---

### 2. `citation_matcher.py` — no internet needed

```
python3 citation_matcher.py
```

**What it does.** Validates a citation against the real corpus. Deterministic — no model call anywhere. Returns `accept: True/False`, and **the pipeline drops any conclusion where that is False.**

**Expected output: `15/15 as expected`.** If you see fewer, a corpus file's header has changed — check `current_citation` contains only a citation, no explanatory prose.

**To use it in code:**
```python
from citation_matcher import verify

v = verify("Rule 11UA", tax_year="FY 2026-27")
print(v.status)       # STALE
print(v.should_cite)  # Rule 57, Income-tax Rules, 2026
print(v.accept)       # False  ← the pipeline reads this
```

**The demo worth showing a judge:**
```python
verify("Rule 11UA", "FY 2026-27")   # STALE  — our own error, caught
verify("Rule 11UA", "FY 2025-26")   # VERIFIED — correct for that year
verify("Rule 11UB", "FY 2026-27")   # REJECTED — fabricated
```

Same citation, two years, two answers. That is the whole tax-year point in three lines.

---

## `schema.json` — not run, but load-bearing

The output contract. Every design decision from fifteen steps is in it as a constraint:

- `valuation.methods` has `minItems: 2` — **a single figure is a schema violation**
- `limits[]` has `minItems: 1` — **if it's ever empty, the record is wrong**
- `citation.tax_year` is **required**
- `certainty` separates `lacuna` from `open_texture`

Validate it any time with:
```
python3 -c "import json; json.load(open('schema.json')); print('valid')"
```

---

## IF SOMETHING BREAKS

| Symptom | Cause |
|---|---|
| `Corpus loaded: 0 files` | Run from the folder containing `corpus/`, not from inside it |
| Matcher scores below 15 | A corpus header has prose in `current_citation`. Move it to a `note:` key |
| `killgate.py` all 403 | Blocked network. Try a different connection or a phone hotspot |
| `python3: command not found` | Use `python` instead |

---

## NODES 1, 2, ⚙ A — BUILT, VERIFIED LIVE

**Update, 20 Aug:** `node1_extract.py`, `node2_gaps.py`, `gap_enforcer.py`
and `run_pipeline.py` exist and have now been run against a real, live
model — not just self-tested. **See `PIPELINE-FLOW.md` for the full
plain-language walkthrough**, and `DECISION-D42.md` / `DECISION-D43.md` for
why the model backend works the way it does.

**The model backend is Featherless (open models), not Anthropic**, because
this project runs on competition credits there — Anthropic still works as a
fallback/cost-estimate path if you set `ANTHROPIC_API_KEY` instead. Setup:

```powershell
pip install -r requirements.txt
$env:FEATHERLESS_API_KEY = "rc_..."     # your own key — never in a file, ever
python check_llm.py                     # ~10s, a few hundred tokens — run this FIRST, every session
python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" --text step21drop\cases\D1\case.md
```

`check_llm.py` will tell you immediately if a model slot is broken before
you spend real credits mid-run — it already caught one real problem this way
(a gated Llama model on this account; fixed, see `DECISION-D43.md`).

Nodes 3, 4, 5 (the resolvers and the adversarial checker) are still prompts
only — `step22drop/prompts/03/04/05` — run by hand per the STEP21 evaluation
protocol, not called automatically. `run_pipeline.py --regimes <file>` takes
their hand-coded output and runs it through ⚙ C and ⚙ A.

---

## AFTER YOU RUN ANYTHING

**Write the outcome into `iteration-log.md`.** Even if it failed. **Especially if it failed** — *"tried X, it broke, here's why"* is worth more to the Technical Execution score than *"it worked"*, because it shows testing rather than decorating.
