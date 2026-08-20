# DIVERGENCE

[![CI](https://github.com/hariom-s27/divergence/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/hariom-s27/divergence/actions/workflows/python-package-conda.yml)

Built for Reverie Hacks 2026, ML Prompt Engineering track.

## The problem

A freelancer in India gets paid for her work and needs one rupee number for
her tax return. The tax rules tell her exactly which day to value that
payment on — and then, four lines later, do not tell her how to turn that
day into a number. Two people reading the same rules honestly can file two
different, both-defensible numbers.

Most tools guess anyway and print one figure with no hint that a choice was
made. DIVERGENCE reads the actual law, and when the law genuinely does not
decide, it says so — with every defensible number shown, not one invented
one hidden behind false confidence.

## Run it — one command, real output

```powershell
cd divergence
pip install -r requirements.txt
$env:FEATHERLESS_API_KEY = "rc_..."      # once per terminal session, never in a file
python check_llm.py                       # ~10 seconds, confirms all three model slots work

python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" `
    --text step21drop\cases\D1\input.md --node5 `
    --out runs\D1_pipeline.json

python node7_disclosure.py --record runs\D1_pipeline.json --out output-interface.html
```

That produces a real, schema-validated record and the actual disclosure
page — not a mockup. Full setup: [`HOW-TO-RUN.md`](divergence/HOW-TO-RUN.md).
API key handling: [`API-KEY-SETUP.md`](divergence/API-KEY-SETUP.md).

## What we found — failures first

[`ITERATION-STORY.md`](divergence/ITERATION-STORY.md) is seven real moments
where something we built broke, in the order they happened, each one naming
exactly what changed and which number moved. Three of the seven are about
*our own* mistakes being invisible until we actually ran the system: a
corpus that was 40% our own commentary and not the law, a citation checker
that scored 15/15 for four months against the wrong files, and a metric
built to catch overconfidence that was itself silently returning a
fabricated "0.0%, perfect" score. The other four are about the pipeline
finding real defects in its own legal reasoning — most notably the same
kind of mistake, a real and correctly-quoted provision applied outside its
own scope, confirmed **five separate times** in this project's own output.
One instance was found only by a human, and our own adversarial node
missed it outright when tested directly against it. Two were found only by
that same node, unprompted, on unplanted data. Two more were found by both
independently — a human re-reading the record, and the node's own attack on
it, before the two were ever compared. None of the five were visible to
the metrics that would normally stand in for "is this answer right."

## Architecture

[`flowchart.md`](divergence/flowchart.md) is the current diagram: five
model calls (can be wrong) and four deterministic steps (cannot invent
anything — an `if` statement, a string match, arithmetic), shown as
different shapes so the distinction is visible, not just claimed. Full
node-by-node rationale, each one traced to a pre-registered predicted
failure: [`architecture.md`](divergence/architecture.md). Plain-language
walkthrough of an actual run: [`PIPELINE-FLOW.md`](divergence/PIPELINE-FLOW.md).

We avoid saying "nine nodes" for the same reason — it hides the fact that
some of these steps are ordinary Python, not a model, and cannot make
things up no matter how the model upstream of them was talked into wording
something.

## Results, including where we lose

Full metrics (M1–M5), all three arms (naive, token-matched, the real
pipeline), all six cases: [`results.md`](divergence/results.md). Read its
**"Where we lose"** section before quoting any number from this project —
it states plainly where the naive baseline beat the real pipeline, where
gap detection scored 0% on three of six cases, where our adversarial
checker missed a planted defect outright, and where a metric was
structurally unable to measure anything for the whole project's duration.
Nothing there is softened.

**One evaluated case in short:** twelve defensible ways to value the
freelancer's payment, ranging from about ₹4,69,750 to about ₹5,17,618 — a
spread of about ₹47,869, roughly 10% of the payment. Every method is
arithmetic over a real, sourced input; none is typed in by hand (decision
D38, `canonical_case.json` / `node3_valuation.py`).

## What we do not claim

- Not tax advice, and not a substitute for a professional.
- We do not claim any flow shown here is compliant, or predict how a real
  dispute would be decided.
- We never invent a valuation method where the law does not prescribe
  one — that refusal is the actual point of this project, not a limitation
  of it.
- We do not detect evasion, and we do not retain a user's documents.

Full boundary list, stated the same way before any of this was built:
[`step22drop/risks.md`](divergence/step22drop/risks.md), "WHAT WE
DELIBERATELY DO NOT HANDLE."

## Prior art — has this already been solved?

[`prior-art/OBJ-1.md`](divergence/prior-art/OBJ-1.md) checks whether
commercial crypto-tax software already discloses how it values a receipt
like this one. Two products (KoinX, Catax) print a figure with no source
named; one (Koinly) discloses a real method, narrowing but not closing
this project's claim for a tool like it.
[`prior-art/DEMAND.md`](divergence/prior-art/DEMAND.md) checks whether real
people actually hit this exact question — eleven sourced findings across
Reddit and CA practitioner forums, including one person asking about the
same SBI-rate-not-published problem this project's headline case is built
around, found independently, not constructed for this project.

## Cost

| | |
|---|---|
| Metered (Claude, estimated deployment cost) | ₹29.91 per record |
| Open models actually used for this evaluation (Featherless) | ₹0 metered — plan-tier access, no per-request bill to us |
| vs. a single unstructured prompt | ~2.7× the tokens |

The Claude figure is an estimate of what this architecture would cost if
deployed on a metered provider (decision D35) — it is not a number from an
actually-measured run, and we say so rather than let a precise-looking
rupee figure imply otherwise. The real evaluation in `results.md` ran on
Featherless-hosted open-weight models exclusively (decision D44), where the
marginal cost per record is zero under the plan used.

## Accessibility

Done, not promised: `node7_disclosure.py`'s generated page uses real
heading hierarchy (`<h1>`/`<h2>` per section, not styled `<div>`s), a
`<main>` landmark, `aria-labelledby` tying each section header to its
region, and `aria-label`/`role="img"` on the one purely visual element (the
range dimension-line in section 02) so a screen reader gets the same
number a sighted reader gets from the line. `lang="en"` is set on the page.
This was built into the composer itself (decision D34/D53), not added
afterward — every generated page gets it, not just the one shown in a demo.

## How it is built

Five model calls, four deterministic steps. In order: extract facts from
the input (model) → detect what evidence is missing, before anything
reasons about what's present (model) → force any conclusion depending on a
missing fact down to `insufficient_evidence`, in code, unconditionally
(code) → build the valuation lattice from real sourced data, arithmetic
only (code) → resolve income tax and GST against scoped, verbatim statutory
text (model × 2) → check every citation against real corpus text and the
correct tax year, drop what fails (code) → run an independent, different-
model adversarial check that publishes its attack whether it lands or not
(model) → compose the disclosure record from a deterministic template,
never a model (code). Full detail: [`flowchart.md`](divergence/flowchart.md).

We use Featherless only, with no automatic fallback to another provider —
on purpose, so a run can never silently switch which model produced a row
in a results table (decision D44).

| Model slot | Model used |
|---|---|
| small | Qwen/Qwen2.5-7B-Instruct |
| large | Qwen/Qwen2.5-72B-Instruct |
| adversarial | mistralai/Mistral-Large-Instruct-2411 |

The adversarial checker always uses a different model family than the
resolvers (decision D41) — a model checking its own reasoning has a
documented self-consistency bias, so "the adversarial check found nothing"
would not mean much if it were the same model marking its own work.
`check_llm.py` warns if this rule is ever broken.

## The corpus of law

`divergence/corpus/tier-a/` holds the actual statutory text, one law or
rule per file, each carrying a provision id, current and former citation,
which tax year it governs, and its gazette page. `corpus/verbatim/` holds
the same files cut down to statutory text only — the only text ever sent to
a model (decision D31). An earlier version of this project was
accidentally sending our own commentary alongside the law, about 40% of the
injected text by volume; caught and fixed, full account in
[`ITERATION-STORY.md`](divergence/ITERATION-STORY.md) item 1.

Each resolver only sees the law text for its own regime, so a model
resolving income tax structurally cannot cite a GST section — the text was
never given to it (decision C22).

**Seven corpus files still carry an open `known_limitation` note as of this
writing** — things like an unconfirmed 2025-Act section number pending
dual-citation, or one provision's text sourced from an unofficial full-text
mirror rather than the gazette directly. Each note is written into the file
itself, not hidden in a separate audit doc; `python gate0_check.py` lists
all seven by file and reason on every run.

## What we found reading the official gazette

We read the actual notified Income-tax Rules, 2026 (Gazette, Part II,
Section 3(i), 20 March 2026) rather than relying on a secondary summary.
Full detail: [`GAZETTE-FINDINGS.md`](divergence/GAZETTE-FINDINGS.md).

Rule 57's catch-all row exists but its own column B limits it to a
different section than the one that governs this project's case. Rule
206(3) cites the Foreign Exchange Regulation Act, 1973 — repealed in 2000 —
in the one rule that governs converting this exact payment into rupees,
while a nearby rule four rows later correctly cites FEMA 1999. Rule 247
names a "valuer of virtual digital assets" as a role, then gives that role
no defined qualification and no defined method — the law naming a gap by
name and then not filling it, which is a different and more striking
finding than the ordinary silent absences elsewhere in the same rules.

## Design decisions

| Decision | What it means |
|---|---|
| D31 | Models only ever receive plain law text (`corpus/verbatim/`), never our own commentary |
| D38 | No headline number is ever typed in by hand |
| D41 | The adversarial checker always uses a different model family than the resolvers |
| [D44](divergence/DECISION-D44.md) | Featherless only, no silent fallback to another provider |
| [D46](divergence/DECISION-D46.md) | Nodes 3/4 automated; schema amended after the ground-truth freeze, disclosed, ground truth itself untouched |
| [D50](divergence/DECISION-D50.md) | Node 5 (adversarial) automated and run for the first time; found a real, unplanted scope-reach defect the same night |
| [D54](divergence/DECISION-D54.md) | Third scope-reach defect, fixed with one generalized rule instead of a third patch |
| [D55](divergence/DECISION-D55.md) | Fourth and fifth scope-reach defects; the fifth disclosed rather than chased, per a pre-set hard-stop rule |

Full list: the `divergence/DECISION-D*.md` files — numbered up to D55, though
not every decision number in that range got its own file; several earlier
ones are recorded inline in `architecture.md` and `GAZETTE-FINDINGS.md`
instead.

## Evaluation

Three arms (naive, token-matched chain-of-thought, the real pipeline),
across six cases, five metrics plus a false-abstention check.
[`evaluation-design.md`](divergence/step21drop/evaluation-design.md)
section 7 states, in writing, before a single arm was run, exactly what
result would prove this project's claim wrong.

Ground truth is committed to this repository before any model sees it, and
[`results.md`](divergence/results.md) quotes the exact commit hash as proof
of that ordering. `schema.json` (the output contract, not the ground truth)
has been amended repeatedly since that freeze — every amendment disclosed,
none touching the frozen ground-truth content itself.

## Everything that broke, and what it cost

[`step22drop/iteration-log.md`](divergence/step22drop/iteration-log.md) is
the raw log behind the curated seven moments above. Nothing in this project
that failed was deleted from the record — including the day the citation
matcher scored 15/15 for the wrong reason, for four months, because a
retired file was alphabetically ahead of its replacement, and nothing in
the passing test told anyone that at the time.

## How this repository is laid out

`divergence/` is the actual hackathon submission — code, corpus, prompts,
decisions, results. Start there.

`design-process/` is the early design and research trail from before
`divergence/` existed as its own folder — kept for the record, not part of
the submission.

`_archive/` is excluded from git tracking; it holds retired or duplicate
files `cleanup_repo.py` moved out of the way. Nothing deleted, just moved
so it can't confuse a reader of the live corpus.

`tests/` and the root `conftest.py` exist only so CI can import
`tests/test_gap_enforcer.py` correctly. Plumbing, not evaluation.
