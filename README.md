# DIVERGENCE

[![CI](https://github.com/hariom-s27/divergence/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/hariom-s27/divergence/actions/workflows/python-package-conda.yml)

An AI can say "I don't know." It cannot say "the law does not decide one answer."

DIVERGENCE is a tool that reads a real tax question, checks what the law actually says, and if the law gives no clear method, it says so clearly. It gives citations instead of just making up a confident number.

Built for Reverie Hacks 2026, ML Prompt Engineering track.

## The case we use to explain this

An Indian freelancer is paid 5,000 USDC by a client outside India. The payment settles at 03:14 IST on Sunday, 28 June 2026.

To file a tax return she needs one rupee value for this payment. The Income tax Rules, 2026 do tell her, clearly, when to value it. Rule 56(i), Table row 1, says the value should be taken on the date the property is received. But four lines later, Rule 57 lists the types of property for which a valuation method exists. A virtual digital asset is not on that list. There is one leftover clause that might have covered it, but that clause only applies to section 26(2)(j), not section 92, which is the section that actually applies here.

So the law tells her exactly when to value the payment, but does not tell her how.

On that Sunday, the State Bank of India had not published a rate. FBIL had not published a rate either, since it only publishes on weekdays. But the crypto market itself was trading the whole time. So every official source is silent, and the market is not.

We found twelve different ways to value this payment, each one defensible under some reading of the rules. They range from about 4,69,750 rupees to about 5,17,618 rupees. That is a gap of about 47,868 rupees, or about 10 percent of the payment. Every one of the twelve methods can be argued for. None of them is the one method the law prescribes.

DIVERGENCE returns all twelve figures, and explains clearly why there is no thirteenth "correct" figure. Every number in this repository is calculated by code, in `canonical_case.json` and `node3_valuation.py`. No headline number is typed in by a person (see decision D38).

## How it is built: five model calls and three plain code checks

We avoid saying "seven nodes" because that hides an important fact. Some steps use a language model, which can be wrong. Other steps are plain code, which cannot make things up. In the notes below, a step marked (model) uses an AI model. A step marked (code) is ordinary Python with no model involved.

The flow, in order:

1. Extract facts from the invoice and payment record (model)
2. Detect what evidence is missing (model)
3. Enforce the gap rule: if something is missing, the certainty of any related conclusion is forced down, no matter what the model says (code)
4. Build the valuation lattice, using `canonical_case.json`, and produce `valuation.json` with every defensible method (code)
5. Resolve the income tax position (model)
6. Resolve the GST position (model)
7. Check every citation against the real law text and the correct tax year (code)
8. Run an adversarial check on the whole result, using a different model (model)
9. Compose the final disclosure record (code)

The three code only stages are the real point of this project. A model can be talked out of following an instruction. Plain code cannot be talked out of an `if` statement.

Some details on the code only stages:

`gap_enforcer.py`: if a conclusion depends on something listed as missing, its certainty is forced to `insufficient_evidence` in code. It does not matter how confident the model sounded.

`node3_valuation.py`: it works out 2 official dates times 5 market readings times 2 proxies, giving 12 methods. This is plain arithmetic. No model is used.

`citation_matcher.py`: every citation is checked against the actual law text we hold, and against the correct tax year. Two numbering systems are both in use right now. FY 2025-26 is under the old 1961 Act. FY 2026-27 onward is under the new 2025 Act. A citation given with no tax year is rejected automatically. If a citation fails this check, the conclusion resting on it is dropped, not just flagged.

Full walkthrough of how a run actually works: [`PIPELINE-FLOW.md`](divergence/PIPELINE-FLOW.md)

Why each part of the design exists, linked back to a specific predicted failure: [`architecture.md`](divergence/architecture.md)

## Status: what actually runs today, and what a person still has to do

This table is the honest version. We update it after every real step.

| Stage | Is it automated | Has it actually been run |
|---|---|---|
| 1. Extract | Yes, `node1_extract.py` | Yes, full runs on case D1 and case C2, 20 Aug |
| 2. Gap detector | Yes, `node2_gaps.py` | Yes, full runs on case D1 and case C2, 20 Aug |
| 3. Gap enforcer | Yes, `gap_enforcer.py` | Yes, self test 2 out of 2 |
| 4. Valuation lattice | Yes, `node3_valuation.py` | Yes, produces `valuation.json` |
| 5. Income tax resolver | No, this is a prompt run by hand | Not yet |
| 6. GST resolver | No, this is a prompt run by hand | Not yet |
| 7. Citation matcher | Yes, `citation_matcher.py` | Yes, 15 out of 15 self test |
| 8. Adversarial check | No, this is a prompt run by hand | Never run. Every finding credited to it so far was actually found by a person |
| 9. Disclosure composer | No, it is a static HTML page right now | Not connected to a live result yet |
| Baseline arms A and B | Yes, `run_arms.py` | Yes, all 6 cases, 20 Aug. See "First real numbers" below |
| Scoring | Yes, `eval/score.py`, `eval/m3b_citation_coverage.py`, `eval/normalize_runs.py` | Yes, run against all 14 real result files, 20 Aug |
| CI | Yes, GitHub Actions with pytest | Yes, passing. See the badge above |

Steps 5, 6 and 8 join back into the automated flow through `run_pipeline.py --regimes <file>`. Their hand written conclusions are then checked by the citation matcher and the gap enforcer, the same way an automated step's output would be checked.

## First real numbers, from Steps 27, 29 and 31, 20 Aug

This was the first time steps 1 and 2, `run_arms.py`, and the scoring scripts were run together, as one real chain, against a real model. Before this, each piece had only been tested on its own. We found five real bugs in about two hours. None of them were visible just by reading the code. Every one of them became visible within seconds of actually running it.

The full account, with every bug and every before and after result, is here: [`DECISION-D45.md`](divergence/DECISION-D45.md) and [`iteration-log.md`](divergence/step22drop/iteration-log.md)

Here is what we fixed, in short. We had a silent protocol problem, the temperature setting was 0 everywhere, which goes against our own written rule of "default temperature, not zero." We found two gaps in `schema.json` that had existed since 6 August and had simply never been tested against real data: one rejected a `null` value that our own code was supposed to produce on purpose, and one did not allow a true or false value even though every case's ground truth already uses one. We found that a small model's output broke a rule in a way that only showed up as a confusing schema error several steps later. We found that Arm A's first run just copied back the raw JSON schema definition instead of producing real data. And we found that Arm B's token budget math was wrong, it was cutting off a single answer by limiting it to the combined size of two much smaller separate answers.

After fixing all five, here are the real numbers across all 6 cases. M1 is extraction accuracy. M2 is gap recall and precision. M3 is citation validity. M4 is method count found out of methods expected. M5 is false abstention.

| Case | Arm | M1 extract | M2 recall | M2 precision | M3 valid | M4 methods | M5 |
|---|---|---|---|---|---|---|---|
| C1 | A and B | 0.0% | not available | 0.0% | 25.0% | 2 of 1 | not available |
| C2 | A, B and C | 9.1% | not available | 0.0% | 50.0% / not available | 2 of 1 / 12 of 1 | not available |
| C3 | A and B | 0.0% | 0.0% | 0.0% | 25.0% / 20.0% | 2 of 5 | not available |
| C4 | A and B | 0.0% | 0.0% | 0.0% | 50.0% / 100.0% | 2 of 10 | not available |
| C5 | A and B | 0.0% | 100.0% | 100.0% / 33.3% | 50.0% | 2 of 2 | not available |
| D1 | A, B and C | 0.0% / 9.1% | 75.0% / 25.0% / 0.0% | 100.0% / 33.3% / 0.0% | 60.0% / 50.0% / not available | 2 of 12 / 2 of 12 / 12 of 12 | not available |

Please read the notes below before quoting a single number from this table anywhere. M1 and M5 do not mean "the system did badly." They mean these two metrics currently cannot be scored correctly at all, for any arm, given what we have right now.

M1 checks facts by matching field names exactly. No extraction step, not the pipeline, not Arm A, not Arm B, has ever been told to use the exact same field names as `ground_truth.json`. For example the ground truth says "asset" but a real run might say "asset_currency." A correct extraction under a slightly different but equally valid field name gets marked as "not extracted."

M5 is called "the metric that earns trust" in our own evaluation design. It needs a set of fields called `elements`, and right now no prompt anywhere asks any arm to actually produce that in a way we can score.

Arm C's M3 and M4 numbers look unusually strong on case D1 and case C2 (12 out of 12, and 12 out of 1). This is real, but it is because the valuation lattice enumerates methods with plain code, no model involved. It is not the full comparison our evaluation design asks for, because `regimes` is still empty, since steps 5, 6 and 8 have not been run yet. So Arm C's citation numbers show as "not available," not as a real zero score.

The numbers that are genuinely comparable right now are M2 and M3. On case D1, the hardest case, Arm A's gap recall of 75 percent is currently higher than Arm B's 25 percent. This is worth looking into properly, not smoothing over, before it goes into `results.md`.

## Running it

```powershell
cd divergence
pip install -r requirements.txt

# Do this once per terminal session. Put the key in the shell, never in a file.
$env:FEATHERLESS_API_KEY = "rc_..."

# Takes about 10 seconds and a few hundred tokens. Do this before every session.
python check_llm.py

python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" `
    --text step21drop\cases\D1\case.md `
    --out runs\D1_pipeline.json

# Arm A (naive prompt) and Arm B (token matched, step by step prompt), all 6 cases
$env:DIVERGENCE_TEMPERATURE = "default"
python run_arms.py --arm A --all-cases
python run_arms.py --arm B --all-cases --token-match runs\

# Score everything real that exists in runs/
python eval\normalize_runs.py --report
python eval\m3b_citation_coverage.py --all runs\
```

Full setup instructions: [`HOW-TO-RUN.md`](divergence/HOW-TO-RUN.md)

How to handle your API key safely: [`API-KEY-SETUP.md`](divergence/API-KEY-SETUP.md)

We use Featherless only. There is no automatic fallback to Anthropic. This is on purpose, see decision D44 below.

| Model slot | Model used |
|---|---|
| small | Qwen/Qwen2.5-7B-Instruct |
| large | Qwen/Qwen2.5-72B-Instruct |
| adversarial | mistralai/Mistral-Large-Instruct-2411 |

The adversarial check uses a different model family than the resolvers, on purpose (decision D41). If a model checks its own work, it will often just agree with itself, so "the adversarial check found nothing" would not really mean anything in that case. `check_llm.py` will warn you if this rule is ever broken.

## The corpus of law we use

`divergence/corpus/tier-a/` holds the actual statutory text, one law or rule per file. Each file also carries a provision id, the current citation, the older citation if one exists, which tax year it applies to, and which page of the government gazette it came from.

`corpus/verbatim/` holds the same files, but cut down to only the statutory text itself, marked between `<!-- VERBATIM-START -->` tags. This is the only text that gets sent to the models. Our own commentary is never sent to a model (decision D31). An earlier version of this project was accidentally sending our own analysis to the model along with the law, which was about 40 percent of the text by volume, and that was a real mistake we caught and fixed.

Each resolver step only sees the law text for its own area. So a model resolving income tax simply cannot cite a GST section, because that text was never given to it in the first place. This is by design (decision C22), not just a rule we hope the model follows.

Tier B files (`FBIL-METHODOLOGY.md`, `COMMENTARY.md`, `SG-UAE.md`) are background context only. They can never be cited as authority.

## What we found reading the official gazette

We read the actual notified Income tax Rules, 2026 (Gazette, Part II, Section 3(i), dated 20 March 2026). Full detail is here: [`GAZETTE-FINDINGS.md`](divergence/GAZETTE-FINDINGS.md)

A short summary:

Rule 57 has seven rows, and column B of that rule limits the leftover, catch all row so that it does not actually apply to section 92, which is the section relevant to our case.

Rule 206(3) cites the Foreign Exchange Regulation Act, 1973, an Act that was repealed back in 2000. Rule 210, just four rules later, on the same pages of the same gazette, correctly cites FEMA 1999 instead. We counted mentions across the whole notified Rules. The old repealed Act is named exactly once, and it is in the rule that governs converting our freelancer's income into rupees.

Rule 207 has a fallback rule for when a rate has not been published on a given date. Rule 206 borrows its main definition from Rule 207, but does not carry over that fallback rule. On top of that, Rule 207(2) specifically excludes the case of a resident receiving money, so there is no way to argue your way back into using that fallback.

Rule 247(4) names something called "a valuer of virtual digital assets." But Form 169's list of eleven allowed asset classes does not include virtual digital assets at all. Rule 247(3) leaves the actual qualification requirement up to a Commissioner's discretion, with no further rule given, and Rule 57 gives this valuer no defined method to use either. So out of the gaps we found, four of them are simple absences, the law just does not mention the case. This one is different. The law does mention this exact role by name, and then gives it nothing to actually work with.

## Design decisions

| Decision | What it means |
|---|---|
| D31 | Models only ever receive the plain law text in `corpus/verbatim/`, never our own commentary |
| D35 | The evaluation runs on open weight models through Featherless. Any rupee cost we quote for Claude is an estimate of what it would cost if deployed that way, not a number from an actual measured run |
| D38 | No headline number is ever typed in by hand |
| D39 | We test three arms: a naive prompt, a token matched step by step prompt, and the full pipeline |
| D40 | We use five metrics plus a Silent Failure Rate |
| D41 | The adversarial check always uses a different model family than the resolvers |
| [D42](divergence/DECISION-D42.md) | The model provider is chosen automatically at run time, and this choice is recorded inside every result's `_meta.llm` field |
| [D43](divergence/DECISION-D43.md) | Which exact Featherless model fills each role, and the discovery that every `meta-llama` model id is locked behind a license on this account |
| [D44](divergence/DECISION-D44.md) | Featherless only, no silent fallback to another provider, general repo cleanup, and re-freezing the pre-registered ground truth |
| [D45](divergence/DECISION-D45.md) | Steps 27, 29 and 31, the first real end to end runs. Five real bugs found, only by actually running the system, none of them visible just from reading the code |
| [D46](divergence/DECISION-D46.md) | `schema.json` was amended three times after the ground truth freeze commit. Disclosed on purpose, why none of the three touch the actual pre-registration |

## Evaluation

We test three arms (decision D39), across six cases, using five metrics plus a Silent Failure Rate (decision D40).

[`evaluation-design.md`](divergence/step21drop/evaluation-design.md), section 7, states in advance exactly what result would prove our claim wrong. This was written before we ran a single arm.

The ground truth is committed to this repository before any model is run on it, and [`results.md`](divergence/results.md) quotes the exact commit hash as proof. That commit is our pre-registration. See decision D44 for why that hash actually matters, and D46 for the three schema amendments made after that commit and why they are disclosed rather than silent.

## Honest limitations

Six test cases is a small number. This is a hackathon project, built with limited time.

Steps 5, 6 and 8 are prompts run by hand right now, not automated code.

The adversarial check has never actually been run. Every finding credited to it in this repository so far was actually found by a person reading carefully, not by the model.

The small 7B model extracts less accurately than a larger model would. Where that shows up in the results, we treat it as a real measurement about running this pipeline on open weight models, and we report it honestly as that.

Two of our case inputs are typed text, not photographs of real documents.

Seven of our law files still have an open `known_limitation` note in them. These notes are visible in the file itself, not hidden anywhere.

M1, extraction accuracy, cannot be scored correctly yet, for any arm. No extraction prompt is currently tied to the exact field names used in `ground_truth.json`, so a correct extraction under a different field name is marked wrong. See decision D45.

M5, false abstention, is undefined on every run so far. No prompt currently asks any arm to produce the `elements` data that the scorer needs.

Arm C's citation numbers are not real yet either, because `regimes` stays empty until steps 5, 6 and 8 are actually run for a case using `--regimes`.

`citation_matcher.py` currently matches a short, unqualified citation, for example just "Section 2(111)" with no Act name given, against the wrong file in our corpus. We have not fixed this in the matcher itself. For now we work around it by always citing the full, qualified form in our ground truth.

Everything that broke during this project, and what it actually cost us, is written up in [`iteration-log.md`](divergence/step22drop/iteration-log.md). This includes the day our citation matcher scored 15 out of 15 for the wrong reason, because old, retired law files were alphabetically sorted ahead of their replacements. The matching code itself was correct. The folder holding the files was wrong. Nothing in the output told us that at the time.

## How this repository is laid out

The repository is named `divergence`, and the actual hackathon submission lives inside a folder that is also named `divergence/`. Everything inside that folder, the code, the corpus of law, the prompts, the decisions, the results, is the real submission. Start there.

`design-process/` holds the early design and research trail from before `divergence/` existed as its own folder. This includes the step by step planning documents (`step1.md` through `step-13-selection.md`), the roadmap and status files (`COMPLETE-ROADMAP.md`, `STATE-OF-PLAY.md`, `STEP-LOG.md`), and three early prototype scripts (`canonical_case.py`, `citation_matcher.py`, `killgate.py`) that were later rewritten and now live properly inside `divergence/`. We kept all of this for the record, since it shows the actual thinking behind the project, but none of it is part of the submission itself.

`_archive/` is excluded from git tracking. It holds retired or duplicate files that `cleanup_repo.py` moved out of the way. Nothing was deleted, the files were just moved so they do not confuse anyone reading the live corpus.

`tests/` and the `conftest.py` file at the root exist only so that `tests/test_gap_enforcer.py` can be imported correctly during CI, along with `divergence/__init__.py` for the same reason. These are just plumbing to keep the GitHub Actions badge working. They are not part of the actual evaluation.
