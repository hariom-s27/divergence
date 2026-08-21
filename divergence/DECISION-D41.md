# D41 — the adversarial checker must be a different model family from the resolvers

**Date:** decided before the build, referenced throughout as D41; written up as its own file 21 August 2026 after a review noted it was recorded only inline, in `architecture.md` and `DOCUMENTATION.md`, never as its own document. This is that document — no change in substance, just given a real home.

## The decision

`node5_adversarial.py`'s `adversarial` model slot must never resolve to the
same model family as the `large` slot the income-tax and GST resolvers use.
Today: resolvers run `Qwen/Qwen2.5-72B-Instruct`; the adversarial checker
runs `mistralai/Mistral-Large-Instruct-2411` — a different family entirely
(decision D43 covers *which* model specifically and the licence-gate finding
that led to Mistral). `check_llm.py` checks the org prefix of both resolved
model IDs at the start of every session and prints a warning if they ever
match.

## Why — not an instinct, two measured results

**A model checking its own reasoning cannot be trusted to catch its own
mistakes.** Huang et al., *"Large Language Models Cannot Self-Correct
Reasoning Yet"* (ICLR 2024; [arXiv:2310.01798](https://arxiv.org/abs/2310.01798)):
LLMs struggle to self-correct using only their own internal capability, with
no external signal, and sometimes get *worse* after "correcting" themselves.
Node 5 is grounded externally on purpose — the citation matcher's verdicts
and the gap list are mechanical inputs it did not produce, not just a
different model's opinion.

**Same-model evaluators measurably favor their own output.** Panickssery,
Bowman, and Feng, *"LLM Evaluators Recognize and Favor Their Own
Generations"* (NeurIPS 2024; [arXiv:2404.13076](https://arxiv.org/abs/2404.13076)):
an LLM used as an evaluator scores its own outputs higher than equivalent
outputs from others, even when human annotators judge them equal quality —
and the bias correlates linearly with the model's own ability to recognize
its own output. This is not a hypothesis about what *might* happen if the
resolver and the checker were the same model; it's a measured effect, with
a mechanism identified.

Both papers verified directly against their own abstracts before being
cited here — full reading cards, including what each paper's method and
number actually are: [`prior-art/READING-CARDS.md`](prior-art/READING-CARDS.md).

## What this buys, concretely

If node 5 ever ran the same model family as the resolvers, "the adversarial
check found nothing" would mean almost nothing — a model agreeing with
itself is not evidence the underlying conclusion is sound, per Panickssery
et al.'s own measured self-preference effect. Because the families are
different, and because node 5's three real, unplanted catches this project
made (`DECISION-D50.md`'s addendum, `DECISION-D54.md`, `DECISION-D55.md`)
happened under that constraint, those catches are evidence about the
resolvers' conclusions, not about one model rediscovering its own reasoning.

## What to say about it

> "Our adversarial checker runs a different model family from our
> resolvers, and that's not a design preference — it's grounded in two
> measured results. Huang et al. (ICLR 2024) found LLMs can't reliably
> self-correct without an external signal. Panickssery et al. (NeurIPS
> 2024) measured that LLM evaluators favor their own generations,
> correlated with their ability to recognize their own work. Our checker
> gets a different model family plus mechanical inputs it didn't produce —
> exactly the external grounding both papers say self-correction needs."
