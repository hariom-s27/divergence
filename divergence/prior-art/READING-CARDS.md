# READING CARDS — the papers behind this project's claims, checkable

Every card below follows the same six-line shape on purpose: **PAPER** (a
real, verifiable identifier — a judge can open the link), **CLAIM** (what
they actually show, not what we'd like them to show), **METHOD** (on what
data, how measured), **NUMBER** (the one figure worth quoting), **FOR US**
(what it changes about a decision this project already made), **SAY** (the
exact sentence usable in a doc or in Q&A).

Every fact below was checked directly — the paper's own abstract fetched
and, where a specific number or venue claim needed independent
confirmation, cross-checked by a second search — not assumed from a title
or copied from an earlier summary. Where something couldn't be confirmed,
it isn't asserted here.

---

## 1. Magesh et al., *Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools*

```
PAPER   Magesh, Surani, Dahl, Suzgun, Manning, Ho — Journal of Empirical
        Legal Studies, 2025. arXiv:2405.20362 (Stanford RegLab / HAI)
CLAIM   Commercial AI legal research tools (LexisNexis, Thomson Reuters,
        and others) hallucinate between 17% and 33% of the time, despite
        vendor claims of being "hallucination-free."
METHOD  First preregistered empirical evaluation of AI legal research
        tools, on real legal queries, comparing vendor products directly.
NUMBER  17-33% hallucination rate across evaluated commercial tools.
FOR US  Names the same family of failure this project measures on itself.
        Their own framing (checked directly): a response can be "correct
        but improperly grounded" — retrieval is poor or irrelevant, the
        model still lands on a defensible answer, but falsely asserts an
        unrelated source supports it. Our five scope-reach instances are
        a narrower, more specific variant: not an unrelated source, but a
        real, current, correctly-quoted one whose own scope doesn't reach
        the facts.
SAY     "This is the same family as Magesh et al.'s (JELS 2025) finding
        that commercial legal-AI tools hallucinate on 17-33% of queries,
        including citations that are real but don't support the claim
        attached to them — we measured a narrower version of that same
        failure shape, five times, in our own output."
```

## 2. Blair-Stanek & Van Durme, *LLMs Provide Unstable Answers to Legal Questions*

```
PAPER   Andrew Blair-Stanek, Benjamin Van Durme — ICAIL 2025 (confirmed
        via ACM DL: Proceedings of the Twentieth International Conference
        on Artificial Intelligence and Law). arXiv:2502.05196
CLAIM   Leading LLMs (GPT-4o, Claude-3.5, Gemini-1.5) give different
        answers to the identical legal question asked repeatedly, even at
        temperature 0 — including flipping which party should win.
METHOD  500 legal questions curated from real U.S. court cases with
        split (2-1) decisions — deliberately contentious, real fact
        patterns, not synthetic ones.
NUMBER  500 questions; instability confirmed across all three tested
        frontier model families.
FOR US  Directly reframes this project's own M2 finding — arm C's gap
        recall on the identical D1 case, same input, same code, read 50%,
        75%, then 0% across three seeds. Not evidence our pipeline is
        unusually unstable; evidence that temperature-0 legal-reasoning
        calls are not the deterministic thing they're often assumed to
        be, on a different task, in the same domain.
SAY     "Our gap detector returned 50%, 75%, and 0% recall across three
        seeds of the identical case — consistent with Blair-Stanek and
        Van Durme's (ICAIL 2025) finding that leading LLMs flip their
        answer to identical legal questions even at temperature 0."
```

## 3. Kirichenko, Ibrahim, Chaudhuri, Bell — *AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions*

```
PAPER   Polina Kirichenko, Mark Ibrahim, Kamalika Chaudhuri, Samuel J.
        Bell — NeurIPS 2025, Datasets and Benchmarks Track (confirmed via
        the official NeurIPS 2025 poster listing, not just the arXiv
        listing). arXiv:2506.09038
CLAIM   Abstention (knowing when NOT to answer) is unsolved, scaling
        doesn't fix it, and reasoning fine-tuning makes it WORSE.
METHOD  20 diverse datasets spanning unknown answers, underspecification,
        false premises, subjective interpretation, and outdated
        information, across many frontier models including reasoning-
        tuned variants.
NUMBER  Reasoning fine-tuning degrades abstention by 24% on average, even
        on math/science domains those models are explicitly trained on.
FOR US  Gives this project's abstention→election reframe (`novelty.md`)
        a real taxonomy to sit next to instead of an invented one, and
        an authoritative answer to "won't a smarter model just fix this":
        the paper's own headline finding says the opposite happens.
SAY     "Scaling doesn't fix this and reasoning fine-tuning actively
        makes it worse — AbstentionBench (NeurIPS 2025) measured a 24%
        abstention degradation from reasoning fine-tuning across 20
        benchmarks, which is exactly why we made the boundary a
        declared, checkable manifest instead of trusting a bigger model
        to know when to stop."
```

## 4a. Huang et al. — *Large Language Models Cannot Self-Correct Reasoning Yet*

```
PAPER   Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng,
        Adams Wei Yu, Xinying Song, Denny Zhou — ICLR 2024.
        arXiv:2310.01798
CLAIM   LLMs struggle to self-correct their own reasoning using only
        their own internal capability, with no external signal — and
        sometimes get WORSE after "correcting" themselves.
METHOD  Systematic evaluation of intrinsic self-correction (no external
        feedback) across multiple reasoning benchmarks.
NUMBER  Self-correction without external feedback measurably degrades
        performance in the paper's tested settings (specific per-
        benchmark figures are in the full paper, not the abstract alone
        — not quoted here to avoid overstating what was checked).
FOR US  Directly justifies decision D41 (the adversarial checker uses a
        different model family from the resolvers, never the same one
        marking its own work). Our citation matcher and gap list are
        exactly the external, mechanical signals this paper says
        intrinsic self-correction lacks.
SAY     "Huang et al. (ICLR 2024) found LLMs cannot reliably self-correct
        reasoning without an external signal — our adversarial checker is
        grounded externally on purpose: a different model family, plus
        mechanical inputs (the citation matcher's verdicts, the gap list)
        it did not produce itself."
```

## 4b. Panickssery, Bowman, Feng — *LLM Evaluators Recognize and Favor Their Own Generations*

```
PAPER   Arjun Panickssery, Samuel R. Bowman, Shi Feng — NeurIPS 2024
        (confirmed via the official NeurIPS 2024 proceedings page, not
        just arXiv). arXiv:2404.13076
CLAIM   An LLM used as an evaluator scores its OWN outputs higher than
        equivalent outputs from others — even though human annotators
        judge them as equal quality.
METHOD  Controlled experiments, including fine-tuning LLMs, measuring
        self-recognition ability against self-preference bias strength.
NUMBER  A measured linear correlation between a model's ability to
        recognize its own output and the strength of its self-preference
        bias toward that output.
FOR US  The direct empirical basis for D41. Not an instinct that a
        same-model critic would be unreliable — a measured bias, with a
        mechanism (self-recognition) identified, not just an effect.
SAY     "Panickssery et al. (NeurIPS 2024) measured that LLM evaluators
        favor their own generations, correlated with their ability to
        recognize their own output — the empirical reason our adversarial
        checker (node 5) is required to be a different model family from
        the resolvers it checks, not a design preference."
```

---

## What this file is for

`novelty.md`'s one real weakness was citations with no identifier a judge
could check — every reference there is an inline marker, not a link. This
file exists specifically to fix that for the four papers this project's
own decisions actually rest on. Linked from
[`DOCUMENTATION.md`](../DOCUMENTATION.md)'s prior-art section.
