# CONTRASTIVE EXEMPLARS — the three real scope-reach failures, WRONG vs RIGHT

**S4 of a SHOULD list, 22-23 Aug 2026.** Every WRONG side below is a real
model output this project actually produced, not a constructed strawman —
sourced from a saved run file or a decision doc, quoted, not
paraphrased. Every RIGHT side is grounded in the exact corpus text that
makes the wrong answer wrong, quoted the same way.

**Why this exists as a standalone reference rather than three new
few-shot blocks pasted into `03-income-tax.md`**: this project's own
history is that *every* prompt change has surfaced a new, different error
(`ITERATION-STORY.md`), and every one of those changes was verified by a
real run afterward. There is no `FEATHERLESS_API_KEY` in the environment
this was written in to verify a prompt change's actual effect on model
behaviour — the same constraint `DECISION-D62.md`/`D63.md`/`D64.md`/`D65.md`
each already hit. Pasting untested few-shot exemplars into a live prompt
and calling it done would be exactly the "designed for and skipped"
failure this project's own discipline exists to catch. What's safe to
build without a live call: a precise, citable, exemplar-shaped reference
— useful for Q&A prep now, and the literal content to paste into the
prompt the moment someone can verify the result. Not done silently as if
it were the same thing as done and tested.

**Update, 23 Aug 2026:** added the published mechanism these exemplars
implement (Chia et al., contrastive chain-of-thought), the specific
overfitting risk `scope_enforcer.py`'s own LIMITATIONS section already
names, and a pre-registered held-out generalisation test — hold Exemplar
2 out of the few-shot block, see whether the reasoning move still
catches it. Design only; not run, same live-key constraint as everything
else in this file.

---

## Exemplar 1 — Rule 206/207: converts *foreign currency*, and a VDA is defined as not being one

**WRONG** (real, saved: `runs/21aug/D1-a_regimes.json`, the `reasoning`
field):
> *"The fair market value is determined using the telegraphic transfer
> buying rate of USDC on the last day of the tax year (2026-03-31) as per
> Rule 11UA."*

`Rule 11UA` is the pre-2026 name for what is now split across Rule 57
(fair market value) and Rule 206 (rate of exchange) — the underlying
error is the same regardless of which numbering is cited: reaching for
the nearest rule that mentions rate-of-exchange, without checking its own
scope words first.

**RIGHT**, grounded in the rule's own text (`ITR2026-RULE-206.md`):
> *"The rate of exchange for the calculation of the value in rupees of
> any income... in **foreign currency**... shall be the telegraphic
> transfer buying rate."* — Rule 206(1), verbatim.
>
> And separately, the statute's own definition (`IT-2-47A.md`, s.2(111)):
> a virtual digital asset is *"any information or code or number or
> token (**not being Indian currency or foreign currency**)."*

**The gate this project built for it**: `scope_enforcer.py`'s
`_check_206_207_foreign_currency_only` (`DECISION-D59.md`) — drops any
non-lacuna conclusion citing Rule 206/207 against a known VDA asset,
unconditionally, in code.

---

## Exemplar 2 — Rule 57: zero VDA references, and its one residual clause doesn't serve the section that needs it

**WRONG** (real, saved: `runs/21aug/D1-b_regimes.json`, the hand-planted
ablation variant for exactly this defect, `make_ablation_variants.py` —
disclosed as planted, not a spontaneous model error, and worth naming
precisely for a second reason: this is the **one** of four planted
defects node 5's own ablation run **missed outright**, `results.md`'s
ablation table, `DECISION-D50.md`):
> *"Rule 57 row 7, the residual catch-all provision, supplies the
> applicable valuation method for this s.92 receipt where no other row of
> the table reaches it."*

**RIGHT**, grounded in the rule's own table (`ITR2026-RULE-57.md`):
> Column B for rows 1–5 (the rows that serve s.92, the section a VDA was
> brought into as "property") — rows 1–3: *"Sections 26(2)(j) and 92"*;
> rows 4–5: *"Sections 26(2)(j), 72 and 92"* — jewellery, art, quoted and
> unquoted shares. Rows 6–7's residual catch-all: column B reads
> *"Section 26(2)(j)"* alone — **s.92 is not in column B for the residual
> row**. Machine-counted against the 2026 gazette: *"'virtual digital' /
> 'crypto' / 'token' / 'digital asset' in Rule 57 ...... 0
> occurrences."*

**The gate this project built for it**:
`_check_57_not_scoped_to_s92_vda` — same file, same mechanism.

---

## Exemplar 3 — Rule 243(8)(e) / Rule 247: an RCASP's own reporting rule, not a taxpayer's valuation method

**WRONG** (real, saved: `runs/21aug/D1-fixed_pipeline.json`, live for
several hours before being found and fixed, `DECISION-D50.md`):
> *"...the value is determined using the fair market value method as
> specified in Rule 243(8)(e)."* Certainty asserted: `settled`.

**RIGHT**, grounded in the rule's own opening words
(`ITR2026-RCASP-VALUATION.md`):
> *"For the purposes of sub-clauses (vi), (vii), (viii) and (ix) of
> sub-rule (1)(e)"* — the aggregate-**reporting** obligations of **"a
> reporting crypto-asset service provider"** under section 509. Not the
> individual whose receipt is being valued. Rule 247(4) separately names
> *"a valuer of virtual digital assets"* as a real, registrable category —
> and gives that valuer no class of asset, no stated qualification, and no
> method (`DECISION-D50.md`'s addendum, `ITR2026-RULE-247.md`).

**The gate this project built for it**: `_check_243_247_rcasp_only` — same
file, unconditional (doesn't depend on facts, since no case this project
holds is ever an RCASP).

---

## The one pattern across all three

Every WRONG side cites a **real, current, correctly-quoted** provision —
`citation_matcher.py` (⚙ C) would accept every one of them; none is
fabricated, none is stale. What makes each one wrong is invisible to
citation-existence and citation-currency checks alike: the provision's
*own* scope words don't reach the facts it was cited for. That is the
precise, narrow claim `scope_enforcer.py` (⚙ E, `DECISION-D59.md`) closes
in code for exactly these three, and the reason this project cites
Blair-Stanek, Holzenberger & Van Durme's false-positive result
(`prior-art/READING-CARDS.md` #5) rather than a citation-fabrication
benchmark: the failure here is never that the citation is fake.

## Why WRONG-then-RIGHT pairs, not just RIGHT exemplars — and the risk that comes with it

Chia, Chen, Tuan, Poria and Bing, *"Contrastive Chain-of-Thought
Prompting"* (arXiv:2311.09277), name the exact gap these three exemplars
are built to close: *"the conventional chain of thought does not inform
language models on what mistakes to avoid,"* and propose supplying both
valid and invalid reasoning demonstrations rather than only the correct
one. **Their abstract states no per-benchmark numbers — UNVERIFIED on
magnitude.** Nothing here claims a percentage-point improvement sourced
from that paper; what's taken is the mechanism, not a figure — recommended
on the argument (a model shown only correct answers has no signal about
what specifically goes wrong when it's wrong) plus this project's own
independent evidence (below), not on an unverified effect size.

**The specific risk this project's own code already confesses, named
before it's papered over:** `scope_enforcer.py`'s own `LIMITATIONS`
section says plainly that its three deterministic checks are "three
provisions, not a scope-reading model... a fourth misapplied provision
this project has never analysed is exactly as invisible to this file as
it was before." Pasting these same three WRONG/RIGHT pairs into
`03-income-tax.md` as few-shot exemplars risks teaching the identical
narrow lesson one level up — *avoid Rule 206, avoid Rule 57, avoid Rule
243(8)(e) specifically* — rather than the general reasoning move each
pair is meant to demonstrate: *find the provision that actually defines
or scopes the category in question, and check the fact pattern against
that predicate before citing the rule that merely mentions the right
words.* A model that memorises three rule numbers to avoid has learned
nothing that helps on a fourth, never-seen misapplication; a model that
learns the move has learned something `scope_enforcer.py` structurally
cannot check for.

## The held-out test — worth more than the other three combined

**Design, matched to infrastructure that already exists and already has
a measured baseline, not a new harness invented for this:**
`make_ablation_variants.py` already plants Exemplar 2's own WRONG side —
Rule 57 row 7 applied to a s.92 receipt — into `runs/21aug/D1-b_regimes.json`,
a hand-planted copy of D1's real `regimes[]`, built specifically to be
read by `node5_adversarial.py` against `step22drop/prompts/05-adversarial.md`.
That is the real intervention point for these exemplars where node 5 is
concerned (§ "Where to actually use these" below covers the resolver-side
use in `03-income-tax.md` separately). The held-out test: build node 5's
own few-shot block from only **two** of the three exemplars — 1
(Rule 206/207) and 3 (Rule 243(8)(e)/247) — deliberately holding
**Exemplar 2 (Rule 57)** out, paste that block into `05-adversarial.md`,
and re-run `node5_adversarial.py` against the unmodified
`D1-b_regimes.json`. Score whether node 5 now catches the Rule 57
misapplication it was never shown a Rule-57-specific exemplar for.

**Why Rule 57/D1-b specifically, not an arbitrary choice of which one to
hold out:** this is the one case this project already has real, measured
evidence about the *untaught* baseline for. `results.md`'s ablation
table records D1-b as the **one of four planted defects node 5's own
adversarial pass missed outright** — with zero few-shot exemplars in
play at all, its five attacks that night never mentioning the planted
defect once. Holding out exactly this one means the test isn't asking
"can the model catch a defect it's never had any signal about" in the
abstract; it's asking a sharper, pre-registered question this project
already has a documented negative baseline to compare against: *does
seeing the move demonstrated on two OTHER provisions transfer to the one
specific case this project has already watched the system fail on once,
unprompted?*

**What would count as the move generalising, stated before running it so
the criterion can't be picked after seeing the result:** node 5's attack
on the `valuation_method` conclusion in `D1-b_regimes.json` names Rule 57
row 7 as not reaching a s.92 VDA receipt, and the attack text itself
references checking column B / the row's own scope against the facts —
not a citation-string match to "Rule 57," and not language lifted from
Exemplar 1 or 3's own specific provisions. **What would count as
memorisation instead, not generalisation:** node 5 correctly attacks
conclusions shaped like Exemplars 1/3 (if planted the same way) but
reproduces its own original miss on `D1-b` exactly — proving the two
in-prompt exemplars taught "these two citation strings are suspicious"
and nothing about the underlying move at all.

**Not run here.** Same constraint as everywhere else a live model call
would be needed to know the actual result (`FEATHERLESS_API_KEY` not set
in this environment) — the design, the exact existing artifact
(`D1-b_regimes.json`) and command (`node5_adversarial.py`), and the
pre-registered pass/fail criterion above are what's safe to commit to
paper without a key; running it and reporting whichever way it comes out
is the literal next step the moment one is available, not a result
quietly assumed favourable in the meantime.

## Where to actually use these

- **Now**: `qa-prep.md` — a judge asking "give me a concrete example of
  the scope-reach failure" gets one of these three, verbatim, sourced.
- **Next, once verifiable**: paste **two** of the three (holding out Rule
  57, per the design above) as a few-shot block into `03-income-tax.md`'s
  own prompt, run `cases/D1-b` and the full six-case suite, and confirm —
  via `eval/score.py` and a fresh `node5_adversarial.py` pass — three
  things at once: adding the block doesn't change M1–M4 on the six cases,
  it does reduce (not just relocate) the rate at which node 5 has to
  catch this same shape again on the two provisions actually shown, and
  the held-out test above resolves one way or the other, reported
  honestly either way. Not attempted here without a way to verify the
  result.
