# DIVERGENCE

[![CI](https://github.com/hariom-s27/divergence/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/hariom-s27/divergence/actions/workflows/python-package-conda.yml)

Built for Reverie Hacks 2026, ML Prompt Engineering track.

**One file, the whole thing, in order:** [`divergence/START-HERE.md`](divergence/START-HERE.md) —
the mental model, every command to run the full pipeline, and all 24
dated design decisions merged into a single chronological read instead of
24 separate files.

## The problem, stated as a loss, not an abstraction

Two accountants, reading the identical Indian tax rules in good faith,
file two different numbers for the same stablecoin receipt — ₹47,868.76
apart, on a single transaction. Neither is wrong. The rule that names
which *day* to value a foreign receipt on exists; four lines later, the
rule that says *how* to turn that day into rupees does not. That gap
costs money the moment someone has to guess, and worse than the rupee
spread: a wrong classification on the GST side turns an export at
0%-with-refund into 18% owed in cash, sometimes retroactively, sometimes
with a fraud penalty on top of the tax (`architecture.md`'s GST resolver
section, the ₹1,19,205-vs-₹2,01,752 case).

Every commercial tool checked for this project (`prior-art/OBJ-1.md`)
prints one figure anyway. None of them show the reader that a choice was
made, let alone which one. DIVERGENCE reads the statute text directly and,
when it genuinely does not decide, says so — every defensible figure
shown, none invented, none picked to look confident.

**See it in one click, live, no download:**
[hariom-s27.github.io/divergence](https://hariom-s27.github.io/divergence/)
— or open [`divergence/index.html`](divergence/index.html) directly from
this repo, same file either way. Twelve real defensible figures on the
hard case, one real figure each on two cases that genuinely have no
dispute. The same pipeline, unedited output, side by side.

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
mistake, a real and correctly-quoted provision applied outside its
own scope, confirmed **five separate times** in this project's own output.
One instance was found only by a human, and our own adversarial node
missed it outright when tested directly against it. Two were found only by
that same node, unprompted, on unplanted data. Two more were found by both
independently — a human re-reading the record, and the node's own attack on
it, before the two were ever compared. None of the five were visible to
the metrics that would normally stand in for "is this answer right."

**This is not a tax-law-specific failure, and that is the actual finding.**
Nothing about the mechanism is specific to Indian tax rules — it is what
happens whenever a model is given verbatim source text and a genuinely
underdetermined question and asked to resolve it confidently. The same
shape of mistake would show up handing a model a medical guideline and an
edge-case symptom, an insurance policy and a borderline claim, or a
contract and a clause two lawyers would read differently. The fix that
worked here — a second, independent model whose only job is to attack the
first one's citations for scope, published whether the attack lands or
not — doesn't depend on anything about tax law either.

**We tested this in one domain only.** Medical guidelines, insurance
policies and contracts are a hypothesis about where else this shape of
failure shows up, not a second result — we have not run this architecture
against any of them, and are not claiming to have. The five confirmed
instances above are all from Indian tax law, all from this project's own
output. Saying that plainly here is what makes the generalization claim
worth taking seriously rather than a bigger claim than the evidence
supports.

## Architecture

[`flowchart.png`](divergence/flowchart.png) is the submission diagram —
where human input is required, the actual query sent to each model, which
model answers it, and what each step does, for every node in the pipeline.
[`flowchart.md`](divergence/flowchart.md) is the same shape as a Mermaid
source diagram for anyone reading this on GitHub. Full node-by-node
rationale, each one traced to a pre-registered predicted failure:
[`architecture.md`](divergence/architecture.md). Plain-language walkthrough
of an actual run: [`PIPELINE-FLOW.md`](divergence/PIPELINE-FLOW.md).

We avoid saying "nine nodes" for the same reason — it hides the fact that
some of these steps are ordinary Python, not a model, and cannot make
things up no matter how the model upstream of them was talked into wording
something.

## The workflow vs. a single prompt, same test case

[`SAMPLES.md`](divergence/SAMPLES.md) runs the same real input through a
naive single prompt, a token-matched chain-of-thought single prompt, and
the actual workflow, and quotes all three verbatim. The two single-prompt
arms both report a ₹250 valuation spread; the real spread on that receipt
is ₹47,868.76 — about 191× larger, because nothing in a single pass forces
a model to enumerate every defensible method rather than stop at the first
two. Both single-prompt arms also cite the same wrong, out-of-scope
provision this project's own workflow needed four fix cycles to correct.

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
like this one. KoinX and Catax print a figure with no source named at all.
Koinly, CoinTracker, CoinLedger and Kryptos each disclose *something* — and
each silently resolves a missing-price receipt (this project's exact D1
fact pattern) a different way: Koinly assumes ₹0, CoinTracker estimates
from a nearby transaction, CoinLedger drops the row from the report
entirely, Kryptos auto-classifies the transaction type outright. Four
products, four different silent choices on the identical contested
question, none of them flagged to the filer as a choice.

**The honest narrowing, said here rather than left for a judge to find
first:** mechanically-verified citations are not new — Clearbrief already
ships a patented, non-generative semantic-support check for US case law.
Quantifying a disputed tax position is not new either — Thomson Reuters'
ONESOURCE Uncertain Tax Positions has shipped an audited, per-position tax
and interest calculator for years. This project's actual claim is
narrower and more specific than either: Indian statutes, two numbering
systems simultaneously live depending on the tax year, and — the one no
adjacent product does at all — refusing to collapse a genuine dispute to
one figure instead of quantifying and then still picking a number.

**Who would actually pay for this is not the freelancer in the demo
case.** She wants one number for one ITR field, and a ₹1,999 product
already sells her that. The buyer is whoever signs the return and carries
the professional risk for a position they can't yet substantiate — the
same buyer ONESOURCE and Clearbrief already sell contemporaneous
defensibility to, in adjacent professions. The demo case stays a
freelancer because that's the fact pattern this project actually built
and measured; the argument for who would pay for it does not.

[`prior-art/DEMAND.md`](divergence/prior-art/DEMAND.md) checks whether real
people actually hit this exact question — eleven sourced findings across
Reddit and CA practitioner forums, including one person asking about the
same SBI-rate-not-published problem this project's headline case is built
around, found independently, not constructed for this project — plus
independent corroboration from a practising crypto-tax CPA describing the
identical failure shape (a report that looks complete while resting on
unverified input) in the general product category this scan covers.

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

## Sustainability

Three real, measured properties, not aspirations:

**Scoping the corpus cuts token spend by two orders of magnitude.**
Injecting the full corpus into every model call would cost 136,227 tokens
per record; scoping each call to only the law text that call is allowed to
cite (decision C22) cuts that to 46,945 — **66% fewer tokens**, for the
same seven calls. Measured against the source instrument itself, the cut is
starker: the notified Income-tax Rules, 2026 gazette runs 563,371 tokens in
full; what this project actually extracts and injects from it is 2,671 —
a **99.5% reduction**. Both figures are measured, in
[`cost-model-output.txt`](divergence/cost-model-output.txt), not estimated.

**No frontier-model dependency.** The entire evaluation in `results.md` ran
on open-weight models — Qwen2.5-7B and -72B for extraction and resolution,
Mistral-Large for the adversarial check — hosted via Featherless, not a
closed frontier API. The system's central claims (the gap findings, the
scope-reach failures, the metrics) do not rest on access to any single
vendor's model continuing to exist on its current terms.

**Five of the ten pipeline steps run no model at all.** *(Was four of
nine before ⚙ E, the scope-reach enforcer, was added — D59; updated here
rather than left stale.)* The gap enforcer, the valuation lattice, the
citation matcher, the scope-reach enforcer, and the disclosure composer
are plain Python — an `if` statement, arithmetic, a string match, a
template. No API call, no token cost, no inference latency, and (the
reason they exist at all) no possibility of inventing an answer. Exactly
half the pipeline's steps carry zero marginal compute cost by
construction, not by optimization.

**The pipeline is reproducible without a paid API key.** `DIVERGENCE_REPLAY=1`
replays D1's real, already-verified run — every one of the five model
calls — from cached request/response pairs, with zero network calls and
zero marginal cost, verified continuously in this project's own CI
(`DECISION-D63.md`). A demo that only runs for whoever holds a live key
isn't actually reproducible; this one is checked to be, on every push, in
an environment that has no key configured at all.

**Long-term viability doesn't depend on anyone maintaining a model.** The
corpus is dated, versioned, and frozen one provision per file, each file
carrying its own current citation, former citation, and the tax year it
governs. When a provision changes, the fix is replacing that one corpus
file — not retraining anything, not touching the pipeline code — and the
citation matcher catches a citation that's gone stale automatically rather
than needing a human to notice. That isn't a design promise; it's a
property this project has already tested on itself: the matcher caught
five of this project's own historical citation errors this way, including
one where a retired file had been silently shadowing its replacement for
four months (`ITERATION-STORY.md` item 2).

**The social dimension is the same claim the whole project rests on.**
A freelancer who unknowingly files two inconsistent positions across two
tax years because two different tools silently picked two different rates
is a real, avoidable harm — not a hypothetical one; `prior-art/DEMAND.md`
found eleven real people and practitioners hitting some version of this
exact gap. This system's contribution to sustainability isn't only lower
token spend — it's that the honest, disclosed range is something a
freelancer or their accountant can act on consistently over multiple
filing years, where a silently-picked single figure is not.

## Accessibility

Done, not promised: `node7_disclosure.py`'s generated page uses real
heading hierarchy (`<h1>`/`<h2>` per section, not styled `<div>`s), a
`<main>` landmark, `aria-labelledby` tying each section header to its
region, and `aria-label`/`role="img"` on the one purely visual element (the
range dimension-line in section 02) so a screen reader gets the same
number a sighted reader gets from the line. `lang="en"` is set on the page.
This was built into the composer itself (decision D34/D53), not added
afterward — every generated page gets it, not just the one shown in a demo.

**Checkable, not just asserted:** [`divergence/a11y_check.py`](divergence/a11y_check.py)
verifies all of the above mechanically — heading hierarchy, the `<main>`
landmark, label/`aria-label` coverage on every input and button — plus real
WCAG contrast ratios computed from this project's actual CSS colors, not a
visual guess. It found one genuine failure while being built (a label color
at 3.52:1, below the 4.5:1 AA minimum) — fixed, verified at 4.65:1, and the
checker now runs in CI on every push, the same way `gate0_check.py` and
`citation_matcher.py`'s self-test do.

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

Full list: the `divergence/DECISION-D*.md` files — numbered up to D58 (plus D41, which predates the sequence), though
not every decision number in that range got its own file; several earlier
ones are recorded inline in `architecture.md` and `GAZETTE-FINDINGS.md`
instead. **All 14 merged into one chronological read:**
[`divergence/START-HERE.md`](divergence/START-HERE.md) Part 3.

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

## What makes this unusual

Six things, each one checkable against a specific file rather than asserted:

- **Ground truth was committed and hashed before any model ran against
  it.** The commit hash is quoted in [`results.md`](divergence/results.md)'s
  "Pre-registration" section — a reader can check the hash actually
  predates the runs, not just trust that it does.
- **29 dated decision documents**, including the ones that record this
  project's own mistakes — a stale citation, a scoring bug that faked a
  perfect score, three named instances of a resolver citing a real
  provision outside its own scope. None were written after the fact to
  look tidy; each is dated the day the thing happened.
- **A "Where we lose" section that leads with the baseline beating us** —
  the naive single prompt outscored the full pipeline on D1's gap recall,
  and that's the first bullet in the list, not the last.
- **An adversarial checker on a deliberately different model family**
  caught three real, previously-undisclosed defects in this project's own
  resolver output, on data nobody planted — and its own two live failure
  modes (it attacks almost everything it's shown; it has produced
  incoherent output on one run) are published in the same file as its
  wins, not separately. Three of those findings no longer depend on that
  checker being run at all — [`scope_enforcer.py`](divergence/scope_enforcer.py)
  encodes them as deterministic code, and the version that did that
  briefly regressed against this project's own shipped demo record before
  it shipped, caught testing against the real file rather than only the
  synthetic self-test ([`DECISION-D59.md`](divergence/DECISION-D59.md)).
- **Every number on the disclosure page is generated from a record.** None
  is typed by a person — the page that used to be a hand-built mockup with
  placeholder figures is now rendered by `node7_disclosure.py` directly
  from whatever record you point it at.
- **A seed-selection rule was written down before the seeds it selects
  from were run** — [`results.md`](divergence/results.md)'s Block F states
  the exact selection criterion first, then reports all three seeds'
  results regardless of which one it picked, so the choice can't have been
  made by looking at the outcome.

## Where to look, against the actual judging criteria

Written against ReverieHacks' own published rubric for this track
(Innovation · Problem Solving · Sustainability/Scalability · UX & Design ·
Bonus: Exceptionality) rather than an assumed one — the rubric has no
separate "technical execution" or "presentation" category, so this section
exists specifically so that work doesn't get lost between the four it does
have.

| Criterion | Where the evidence is |
|---|---|
| **Innovation** — originality, creativity, potential to inspire | The "law does not decide" framing itself; the adversarial checker that attacks its own system's answers and publishes the attack whether it lands or not ([`architecture.md`](divergence/architecture.md)); the generalization beyond tax law, above. The prior-art check is real and checkable, not asserted — [`prior-art/READING-CARDS.md`](divergence/prior-art/READING-CARDS.md) cites four papers this project's own decisions rest on, each verified against its own abstract, not a title |
| **Problem Solving** — relevance, effectiveness, feasibility | Relevance: real people hitting this exact gap ([`prior-art/DEMAND.md`](divergence/prior-art/DEMAND.md)). Effectiveness: [`results.md`](divergence/results.md), including where it loses. Feasibility: it runs end to end today, CI green, on open models, at [`HOW-TO-RUN.md`](divergence/HOW-TO-RUN.md)'s one command |
| **Sustainability/Scalability** | The [Sustainability](#sustainability) section above; the scalability proof (C2 — same pipeline, unchanged, on an ordinary bank receipt with no crypto in it at all) |
| **UX & Design** — ease of use, aesthetic, accessibility | `output-interface.html` (real, generated, not mocked up); [Accessibility](#accessibility) above, with the actual ARIA markup named, not just claimed |
| **Bonus: Exceptionality** | [What makes this unusual](#what-makes-this-unusual), above — five confirmed, self-caught instances of the identical scope-reach failure, invisible to every accuracy metric, disclosed rather than hidden |

Required track submissions and where each one is: ML workflow PNG —
[`flowchart.png`](divergence/flowchart.png). Samples document —
[`SAMPLES.md`](divergence/SAMPLES.md). Documentation —
[`DOCUMENTATION.md`](divergence/DOCUMENTATION.md).

## Security

[SECURITY.md](SECURITY.md) — what's actually true about secret handling
and data in this repo, and, in the same file, what genuinely isn't
defended against (prompt injection at Node 1, named plainly rather than
implied away). `pip-audit` runs against every push in CI.

## License

[MIT](LICENSE).
