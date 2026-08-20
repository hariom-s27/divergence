# DIVERGENCE

> When you ask an AI about tax or law, it gives an answer. It sounds confident. But sometimes the law itself has no answer — the rule was never written, two official methods disagree, or the required document does not exist. In those cases a confident answer is worse than no answer, because you cannot tell it apart from a real one. We built a workflow that finds those situations and says so.

A pipeline for resolving the Indian income-tax and GST treatment of a
stablecoin receipt — five model calls, each doing one narrow job, wrapped in
three deterministic checks that cannot hallucinate: a gap detector that runs
*before* any reasoning, a valuation lattice that always returns a range
instead of one number, and a citation matcher that drops any conclusion it
can't verify against the actual corpus text.

**The submission lives in [`divergence/`](divergence/).** Start there:

| File | What it is |
|---|---|
| [`divergence/architecture.md`](divergence/architecture.md) | The five nodes + three checks, and what fails without each one |
| [`divergence/PIPELINE-FLOW.md`](divergence/PIPELINE-FLOW.md) | Plain-language walkthrough of how a run actually goes, file by file |
| [`divergence/HOW-TO-RUN.md`](divergence/HOW-TO-RUN.md) | Setup and exact commands |
| [`divergence/step21drop/evaluation-design.md`](divergence/step21drop/evaluation-design.md) | The five metrics, the three arms, committed before any model ran |
| [`divergence/step22drop/iteration-log.md`](divergence/step22drop/iteration-log.md) | Every version, what broke, why, and what changed — written live |
| [`divergence/DECISION-D42.md`](divergence/DECISION-D42.md), [`D43`](divergence/DECISION-D43.md) | Why the model backend is Featherless, and how the three model slots were actually chosen (queried live, not guessed) |

Everything else at this repo's root (`step1.md` through `step-13-selection.md`,
`COMPLETE-ROADMAP.md`, `STATE-OF-PLAY.md`, and similar) is the design-process
trail from before `divergence/` existed as its own folder — kept for
provenance, not part of the submission itself.

## Quick start

```powershell
cd divergence
pip install -r requirements.txt
$env:FEATHERLESS_API_KEY = "..."        # your own key — never committed
python check_llm.py                      # verify all three model slots work first
python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" --text step21drop\cases\D1\case.md
```
