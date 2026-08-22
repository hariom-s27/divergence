# START HERE — DIVERGENCE, the whole thing, in one file
### The mental model, how to run every part of it, and all 21 decision documents merged into one chronological read — so you don't have to open twenty-one separate files to see how this project actually got built.
### Each entry below still links to its own full `DECISION-D*.md` file for the complete original text. Nothing here replaces those files; this is the fast, ordered path through them.

---

# PART 1 — THE MENTAL MODEL

**The problem, in one sentence.** A resident freelancer in India is paid in
a stablecoin by a foreign client. Indian tax law says exactly which date to
value that payment on — and then does not say how to turn that date into a
rupee figure. That is a real gap in the law, not a hard question nobody
solved yet.

**What this project refuses to do.** Guess. Most tools facing this print
one confident figure with no sign a choice was made. This system computes
every defensible figure honestly and says "no rule found" when that is
what the text actually supports.

**The shape of the pipeline — five model calls, four deterministic
checks.** Every step is either 🤖 (a model call — it predicts tokens, so it
can be wrong) or ⚙ (ordinary Python — an `if` statement, a string match,
arithmetic — so it cannot invent anything, only enforce or compute what was
already there). This distinction is the whole architecture; everything
else is detail. Full diagram: [`flowchart.png`](flowchart.png).

```
input doc → 🤖1 Extract → 🤖2 Gap detector → ⚙A Gap enforcer
                                                    ↓
                                            ⚙B Valuation lattice
                                              ↓           ↓
                                        🤖3 Income tax   🤖4 GST
                                              ↓           ↓
                                          ⚙C Citation matcher
                                                    ↓
                                          🤖5 Adversarial checker
                                                    ↓
                                          ⚙D Disclosure composer
                                                    ↓
                                          output-interface.html
```

**The certainty vocabulary** every conclusion carries one of:
`settled` (the provision says this plainly) · `inference` (built from
provisions read together) · `open_texture` (a rule exists but is vague) ·
**`lacuna`** (no rule exists at all — the strongest, easiest-to-misuse
claim in the schema) · `contested` · `insufficient_evidence` (a fact is
missing, not a rule). `lacuna` and `insufficient_evidence` are different
claims and mixing them up is exactly the kind of mistake this project's
own resolvers made and had to catch in themselves.

**The one finding that recurred five times.** A model given verbatim
statute and a genuinely underdetermined question will confidently reach
for the nearest rule that mentions the right words, even when that rule's
own scope excludes the facts. Confirmed five separate times in this
project's own resolver output — Rule 57, Rule 206, Rule 243, and s.393(1)
twice. Three of the five were caught by this project's own adversarial
checker (🤖5), on data nobody planted, invisible to every accuracy metric
every single time. That pattern — not any one instance of it — is this
project's actual result. Full account: [`DOCUMENTATION.md`](DOCUMENTATION.md) §5.

---

# PART 2 — HOW TO RUN THE WHOLE FLOW

```powershell
cd divergence
pip install -r requirements.txt

# once per terminal session — the key lives in the shell, never in a file
$env:FEATHERLESS_API_KEY = "rc_..."

# ~10 seconds, confirms all three model slots actually work before spending real tokens
python check_llm.py

# the whole pipeline: extract -> gaps -> enforce -> valuation -> resolve -> verify -> attack
python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" `
    --text step21drop\cases\D1\input.md --node5 `
    --out runs\D1_pipeline.json

# render the actual disclosure page from that record
python node7_disclosure.py --record runs\D1_pipeline.json --out output-interface.html
```

**To run the baselines for comparison** (naive prompt, and a token-matched
chain-of-thought prompt — see [`SAMPLES.md`](SAMPLES.md) for what they miss
that the workflow catches):

```powershell
$env:DIVERGENCE_TEMPERATURE = "default"
python run_arms.py --arm A --all-cases
python run_arms.py --arm B --all-cases --token-match runs\
```

**To score everything that exists in `runs/`:**

```powershell
python eval\normalize_runs.py --report
```

**If node 5 was run separately** from `run_pipeline.py --node5` (useful
since it's retriable on its own without re-spending nodes 1–4's tokens):

```powershell
python node5_adversarial.py --regimes runs\D1_pipeline.json `
    --missing runs\D1_pipeline.json --valuation runs\D1_pipeline.json `
    --tax-year "FY 2026-27" --out runs\D1_attack.json

python node7_disclosure.py --record runs\D1_pipeline.json `
    --attack runs\D1_attack.json --out output-interface.html
```

**Before every real run, once per session:** `check_llm.py`. **Before
every commit:** `python gate0_check.py` — it scans the whole repo for stale
headline numbers, missing required files, and open corpus caveats, and
should say `0 problem(s) that block Gate 0`.

Full detail: [`HOW-TO-RUN.md`](HOW-TO-RUN.md) (setup), [`PIPELINE-FLOW.md`](PIPELINE-FLOW.md)
(what each file does), [`DOCUMENTATION.md`](DOCUMENTATION.md) (reasoning +
mechanics + data per node, plus the real model registry).

---

# PART 3 — EVERY DECISION, IN ORDER

Twenty-one dated documents. D41 predates D42–D58 chronologically (it's been
referenced throughout the project since before this numbered sequence
started) but only got its own file on 21 August, alongside D57 and D58 —
noted here so the numbering makes sense rather than looking like a gap.

## [D41](DECISION-D41.md) — the adversarial checker must be a different model family from the resolvers
Node 5's model slot must never resolve to the same family as the resolvers'
— enforced by `check_llm.py` checking the org prefix of both at session
start. Grounded in two measured results, verified against their own
abstracts before citing (`prior-art/READING-CARDS.md`): Huang et al. (ICLR
2024) found LLMs can't reliably self-correct without external feedback;
Panickssery et al. (NeurIPS 2024) measured that LLM evaluators favor their
own generations, correlated with their ability to recognize their own
output. Node 5's three real, unplanted catches this project made only mean
what they're claimed to mean because this constraint held every time.

## [D42](DECISION-D42.md) — the model provider is chosen at runtime, not hardcoded
`llm_call.py` resolves a provider from whichever API key is in the
environment (Featherless preferred), instead of one hardcoded choice.
`llm_call.provenance()` records the real provider, model IDs, call counts
and retries into every record's `_meta.llm` — so "the eval ran on open
models" is a fact stated in the output file, not just a claim in a log.
D41 (adversarial model must differ from the resolver model) is enforced by
`check_llm.py`, not just documented.

## [D43](DECISION-D43.md) — which real model fills each slot, found by testing, not guessing
Queried the live Featherless catalogue (21,741 models) rather than picking
names from memory — several plausible-looking IDs turned out not to exist.
**Every `meta-llama/*` model 403s on this account** (a HuggingFace license
gate, not a plan restriction, and nothing in the catalogue listing warns
of it in advance). The `adversarial` slot moved to
`mistralai/Mistral-Large-Instruct-2411`, confirmed working live — D41 only
requires a different family from the resolvers (Qwen), which Mistral
satisfies exactly as well as Llama would have.

## [D44](DECISION-D44.md) — Featherless only, a clean repo, one honest freeze hash
Three decisions, one question: what does a judge see cloning this repo,
and is every claim in it true? (1) Removed the silent Anthropic fallback —
a fresh terminal with the wrong key set would otherwise produce a
real-looking record silently attributed to the wrong provider. (2) Purged
duplicate/retired corpus files and zip archives that had been shadowing
the live corpus (the exact bug that made the citation matcher score 15/15
for the wrong reason for four months). (3) Established that the
pre-registration freeze commit must happen **after** `ground_truth.json`
is actually complete, not before — re-initialized git from scratch so the
quoted hash means what it claims to mean.

## [D45](DECISION-D45.md) — the first real end-to-end run found five bugs unit tests couldn't see
Nodes 1–5 had each been unit-tested alone; none had been run as a full
chain against a real model before this. Five real bugs surfaced in the
first two hours: a temperature-protocol violation (`temperature=0` on
every call, contradicting the eval design), two schema fields that had
silently rejected the pipeline's own documented output since 6 August
(`date_choice.chosen`, a nested-shape violation in extraction), a baseline
arm echoing the schema *definition* back instead of producing data, and a
token-budget bug that zeroed out a whole arm's output. **None were visible
reading the code; all were visible in seconds of watching it run** — the
argument for these steps existing at all.

## [D46](DECISION-D46.md) — schema.json amended seven times after the freeze, disclosed
The commit right after the pre-registration freeze amended the output
schema three times (a nullable date field, a boolean fact type, a new
`_meta` provenance object) — later, wiring nodes 3/4, four more of the
same shape. All seven fix the schema's fit to output the pipeline already,
documented, produced; none touch `cases/*/ground_truth.json`. Disclosed
here specifically so a judge diffing the freeze commit finds it stated
first, not discovered.

## [D47](DECISION-D47.md) — the valuation block was hardcoded to one case, silently inherited by all others
`node3_valuation.py` read one file (D1's) and wrote one file, with no
per-case awareness. C2's already-committed record carried D1's entire
crypto valuation dispute verbatim, despite being a plain USD wire with "no
crypto anywhere" by its own case description. Confirmed this doesn't
affect M1–M5 (neither resolver reads the valuation block) but does affect
the record's own honesty. Not fixed this session — disclosed, scoped as
real follow-up work, not patched under deadline pressure.

## [D48](DECISION-D48.md) — a scorer bug and a case-file gap, both found running the pipeline for real
Two findings: (1) `eval/score.py`'s M5 (false abstention — "the metric
that earns trust") was silently returning a fabricated `0.0%, perfect`
whenever a run had no `elements{}` data, which was every run, always —
fixed to return `None` instead. (2) Five of six case files never got the
standalone input document their own checklist required; ground truth
referenced facts (a counterparty name, an invoice number) that existed in
no document any extractor was ever shown. Not patched by editing the case
files immediately — doing so *after* seeing which cases failed would
corrupt the same pre-registration discipline being relied on everywhere
else.

## [D49](DECISION-D49.md) — real input documents generated mechanically from already-frozen ground truth
Built `make_case_docs.py`: reads each case's frozen `ground_truth.json`
and renders a realistic input document from it — never edits the ground
truth, never hand-written (a human writing the document would
unconsciously make it easier to extract from, the exact bias the freeze
exists to prevent). 100% fact coverage verified mechanically, not by eye;
the script exits non-zero if any case is incomplete. The answer key came
first, weeks earlier, frozen; the exam paper was typed up afterward to
match it.

## [D50](DECISION-D50.md) — node 5 ran for the first time: a real catch, a 3/4 ablation, and a calibration gap
The adversarial checker's own documentation had said "this node has never
run" until this point. First real run, against D1's already-committed
record: caught a genuine, previously undisclosed defect — Rule 206's
"last day of the tax year" date pulled onto a VDA receipt Rule 56 had
already (correctly) dated to the date of receipt. Invisible to every
existing metric. The planted-defect ablation (four hand-planted errors)
scored 3 of 4 — the miss reported at the same weight as the catches, not
smoothed over. A calibration concern followed, found only by reading all
five runs together: `checked_and_survived` was empty every time — node 5
attacked everything it was shown rather than discriminating, which is
also the likely reason it missed the fourth planted defect. **Addendum,
same night:** the Rule 206 fix was applied and re-run — node 5
immediately found a *second*, different real defect in the same spot
(Rule 243(8)(e) misapplied), matching ground truth's own expected answer
more precisely than the fix itself did.

## [D51](DECISION-D51.md) — the valuation lattice made per-case; three of five non-headline cases fixed
`node3_valuation.py` gained `--case`/`--out`; D1's own default path
re-verified byte-identical. C5 (shares D1's exact weekend) fixed with data
already on disk — 2 methods, not D1's 12, matching ground truth exactly.
C1 (a plain domestic invoice, no currency conversion at all) needed a real
schema change — `minItems: 2` assumed every case has a dispute, amended to
`minItems: 1` to let a record honestly say "there is exactly one answer
here." **Addendum:** C2 fixed too, using a real GitHub-archived SBI rate
sourced directly rather than typed from memory — and a correction to the
original entry: C3/C4 don't actually need SBI data at all (the same
night's Rule 206 gate fix established Rule 206 never reaches a VDA), they
need crypto market data instead, not yet collected.

## [D52](DECISION-D52.md) — the temperature-zero bug, already fixed once, ran the whole night anyway
D45 fixed this exact protocol violation earlier the same session by adding
an env var. **The fix was never actually turned on** — checked every
record from that entire night, all said `"0 (dev default)"`. Disclosed
plainly rather than silently starting to use the fix correctly from this
point forward. Corrected one specific claim already written into
`results.md` in place (a metric movement had been attributed to "sampling
variance now that temperature isn't pinned to 0" — temperature was still
pinned to 0 the whole time; the real explanation was a changed input
document). Fixed for real for the next block of runs, verified against the
first record's own `_meta.llm.temperature` field before trusting the rest.

## [D53](DECISION-D53.md) — the demo page is generated from a real record now, not hand-typed
`output-interface.html` — the page a judge opens first — was a hand-built
mockup, every number typed by a person into an early draft, marked
`stale-ok` once the real pipeline overtook it. Built `node7_disclosure.py`:
a fully deterministic composer (no model call, ever) that reads one
schema-valid record and renders the page from it, keeping the original
hand-designed CSS unchanged. The page updates by re-running the composer
against a corrected record, not by hand-editing HTML.

## [D54](DECISION-D54.md) — a third scope-reach error, fixed with one generalized rule instead of a third patch
D50's addendum's Rule 243 defect, fixed properly: `corpus/verbatim/ITR2026-RCASP-VALUATION.md`'s
own opening words scope it to reporting service providers, not a taxpayer
who received a payment. This is the **third** confirmed instance of the
identical shape (Rule 57 → Rule 206 → Rule 243), so the fix was one
generalized SCOPE GATE instruction in the prompt — check any provision's
own scope statement before applying it — rather than a third special case.
`valuation_method` also became its own regime object so its certainty
could stop being forced to match the classification's. A deterministic
downgrade guard was built and tested on two independent real examples,
catching node 5 proposing a nonsensical "settled → settled" non-downgrade.

## [D55](DECISION-D55.md) — a fourth and fifth instance; D1 frozen under a pre-registered rule
Re-reading D54's own record before shipping it found a **fourth**
instance: s.393(1)'s TDS conclusion inverted who the section addresses
(the payer, not the recipient) — node 5's own unread attack on the same
record had already said so. Fixed with an S.393(1) SCOPE GATE. Running the
fix surfaced two real `node5_adversarial.py` bugs (a format-handling gap,
and the downgrade guard itself producing schema-invalid output as a side
effect of rejecting a bad value) — both fixed. Three D1 seeds were then
run under a selection rule written down **before** any of them ran (first
schema-valid seed with all three expected regime objects); seed 2 was
selected. Node 5, run against the selected record, found a **fifth**
instance — a different wrong reason for the same TDS question. **Not
fixed with a sixth prompt edit** — disclosed instead, per a hard-stop rule
set in advance: after one final cycle, whatever remains gets said, not
chased. `D1_final_seed2.json` is the frozen demo record on that basis.

## [D56](DECISION-D56.md) — two ground_truth.json trees existed; a claim in this project's own results was wrong
Found doing a GitHub organization pass, not a code review: `cases/` (the
real, frozen ground truth — the freeze commit `225ed20b` updated it, and
`eval/score.py` has always read from it) and `step21drop/cases/` (a stale
copy, last touched at the earlier, rejected pre-freeze commit) had
diverged. The only field that actually differs, across all six cases, is
`citations_expected[]` — facts, gaps, elements and method counts are
byte-identical, so no M1–M5 score anywhere was ever affected. What *was*
wrong: an earlier "correction" written into `results.md` and
`DECISION-D55.md`, checked against the stale copy, claimed
`citations_expected` was empty. The real file has it filled in correctly —
the original instruction those two docs were "correcting" had been right
all along. Fixed in both places. `cases/` was also completed (the real
input documents copied in, verified byte-identical) so it's a
self-contained canonical location, and `step21drop/cases/README.md` now
says plainly which file there is real and which isn't.

## [D57](DECISION-D57.md) — a schema field populated for the first time, two CI checks that were never real gates, a scoring bug found checking another finding
`schema.json`'s `manifest` object had been defined since 6 August and never
once written by `run_pipeline.py` — fixed, verified against a fresh test run
and validated in isolation against its own schema definition.
`gate0_check.py` and `citation_matcher.py`'s self-test both printed
pass/fail but never called `sys.exit(1)`, so wiring either into CI would
have shown green regardless of whether it actually passed — fixed, both now
gate CI for real. A wording claim ("we publish the attack and downgrade the
conclusion") repeated in `architecture.md` and `schema.json` was never
fully true — `downgraded_to` is shown, never auto-applied — fixed in both.
**Hand-checking whether the M2 instability finding itself was real** (not
just trusting the summary numbers) confirmed two of the three seeds hold up
exactly and found a genuine third thing: `eval/score.py`'s gap matcher has
no one-to-one constraint, so one seed's 75% figure double-counts a single
reported item against two different ground-truth gaps. Disclosed without
fixing for one night (D58 fixes it properly, once there was room to).

## [D58](DECISION-D58.md) — four bugs found by deliberately hunting for them, including the M2 scorer fixed properly
Different in kind from the decisions around it: found by being asked to
look for bugs, not by reviewing docs. `schema.json`'s `condition_met`
couldn't be null even though it always should be exactly when
`qualifying_condition` is null — same shape as two earlier amendments that
had already fixed sibling fields, this one was simply missed; retroactively
makes Block F's seed 1 schema-valid too, but the frozen demo record does
**not** change (re-selecting now, with seed 1's content already read and
quoted, would be the exact cherry-picking the pre-registered rule exists to
prevent). The manifest's `verified` field (D57) was hardcoded true — fixed
to run the real check, confirmed meaningful by testing against a wrong tax
year and watching it correctly fail. The election radios never recorded
anything despite saying they would — fixed with browser-local storage, no
network call. **And the M2 scorer bug D57 disclosed was fixed properly**:
real one-to-one bipartite matching, every M2 number in `results.md`
re-scored against it — four cells actually changed, listed with before/after
in D58, everything else confirmed unchanged, not assumed.

## [D59](DECISION-D59.md) — ⚙ E, the scope-reach enforcer: node 5's item 2, turned into code
The one genuine new capability added after the ship-plan work was otherwise
done, not a found bug. Node 5's own checklist names "scope reach" as item 2
and this project already has three real, hand-verified instances of it in
its own history (Rule 206/207 cited against a VDA, Rule 57 cited against a
VDA, Rule 243/247 cited as the taxpayer's own method instead of an RCASP's)
— each caught only because node 5, an LLM call, happened to run and happened
to land the attack that day. `scope_enforcer.py` encodes exactly those three
as deterministic code, dropping any conclusion whose citation doesn't reach
the case's facts, same semantics as ⚙ C. **Caught its own regression before
it shipped**: a first version dropped the project's own frozen demo
record's correct "no rule found" (`certainty: lacuna`) conclusion, because
citing Rule 57 to prove absence looks identical to citing it as authority
without also checking *which* claim it's attached to. Fixed using
`certainty == "lacuna"` — schema.json's own definition of "no rule exists"
— as the discriminator, not a keyword guess at outcome text. A fourth
candidate (s.393(1), D55) was deliberately left out for the identical
reason, disclosed rather than force-fit. Self-test: 7/7, plus both real
records re-checked directly.

## [D60](DECISION-D60.md) — corpus integrity hashing: the "hashed" claim, made real
`corpus/MANIFEST.md` had said "hashed" next to a few Tier A files since 19
August with no hash ever recorded anywhere — true in spirit, unverifiable
in fact. `corpus_hash.py --freeze` records a real SHA-256 per Tier A file
in `FREEZE-HASHES.json`; `--verify` (now a CI gate) fails on drift, a
missing file, or an unfrozen new one. Tested both directions: mutated a
real corpus file, confirmed `--verify` catches it and exits 1; restored it
byte-for-byte, confirmed clean again. Every disclosure record's manifest
now also carries `content_hash` per provision (D60's schema addition,
additive, no breaking change) — proof of exactly what text was checked,
not just that a check happened, independent of whatever the live corpus
looks like later.

## [D61](DECISION-D61.md) — mutation corpus: manufacturing labelled defects at zero cost
Seven mutation operators applied to the six real cases' own saved regime
conclusions — no model call, reproducible, zero marginal cost. Reported
per-operator, never as one blended number: `FABRICATED_CITATION` and
`SCOPE_VIOLATION` both 100% caught (citation matcher, scope enforcer, as
designed); `DEPENDENCY_DROP` **0/6** — `gap_enforcer.py` can only act on a
dependency that's declared, and has no way to notice one was silently
removed; `REGIME_CROSS_CITE` **1/6**, and that one catch is honestly
disclosed as coincidental (an unrelated scope-reach rule firing for its
own reason, not a regime check, which doesn't exist). One catch *is* real
and worth naming: relabelling D1's `lacuna` valuation finding as `settled`
defeats ⚙ E's own lacuna exemption and correctly exposes Rule 57's
underlying scope violation again — the mutation corpus validating that
exemption's precision from the inside, not by accident.

---

## What the decisions add up to

Read end to end, the pattern is not fourteen separate bugs. It's one
recurring shape, showing up at every layer of the project: **something
that had never actually been run, or never actually been checked, was
assumed correct until someone ran it and looked.** A schema untested since
6 August. A fallback provider nobody had actually triggered. A fix that
existed in code but was never turned on. Five confirmed instances of a
resolver citing a real, current, correctly-quoted provision outside its
own scope. The project's own central claim — that a confident answer
resting on ground that quietly moved is worse than no answer, because you
cannot tell it apart from a real one — is what these fourteen documents
are, applied to the project's own construction of itself.
