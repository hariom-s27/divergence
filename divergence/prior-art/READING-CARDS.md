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

*Numbers updated 21 Aug — a fuller research pass confirmed the exact
per-tool figures and the annotation statistic this card originally left
general, and explicitly ruled out a "GPT-4 hallucinates 60%+" line I had
already independently declined to use two commits earlier: this paper
reports no per-category percentage for GPT-4 at all, so that figure was
never sourced from here.*

```
PAPER   Magesh, Surani, Dahl, Suzgun, Manning, Ho — Journal of Empirical
        Legal Studies, 2025. arXiv:2405.20362 (Stanford RegLab / HAI)
CLAIM   Commercial AI legal research tools (LexisNexis, Thomson Reuters,
        and others) hallucinate far more than vendors' "hallucination-
        free" claims suggest, and at meaningfully different rates from
        each other.
METHOD  202 preregistered queries (general legal research, jurisdiction/
        time-specific, false-premise, factual recall). Two-axis
        definition — correctness AND groundedness — a response counts as
        hallucinated if EITHER is wrong. Three labellers plus a fourth,
        independent labeller blind-re-scoring a stratified sample of 48
        responses.
NUMBER  Lexis+ AI: 65% accurate / 17% hallucinated / 18% incomplete.
        Westlaw AI-Assisted Research: 41% / 33% / 25%. Ask Practical Law
        AI: 19% accurate / 62% incomplete (its hallucination rate is
        implied, not stated as a figure — do not quote it as ~20%).
        Inter-rater agreement: Cohen's κ = 0.77, 85.4% on the final
        outcome label — both quoted verbatim from the paper's own text.
FOR US  Names the same family of failure this project measures on itself.
        Their own framing (checked directly): a response can be "correct
        but improperly grounded" — retrieval is poor or irrelevant, the
        model still lands on a defensible answer, but falsely asserts an
        unrelated source supports it. Our scope-reach instances are a
        narrower, more specific variant: not an unrelated source, but a
        real, current, correctly-quoted one whose own scope doesn't reach
        the facts — their groundedness axis is a human judgement about
        proposition support, and has no label for a source that genuinely
        supports the proposition but isn't reachable here.
SAY     "This is the same family as Magesh et al.'s (JELS 2025) finding
        that commercial legal-AI tools hallucinate 17-33% of the time —
        Lexis+ AI 17%, Westlaw AI-AR 33% — including citations that are
        real but don't support the claim attached to them. We measured a
        narrower version of that same failure shape in our own output,
        and it has no cell in their own groundedness taxonomy."
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

## 5. Blair-Stanek, Holzenberger, Van Durme — *Can GPT-3 Perform Statutory Reasoning?*

```
PAPER   Andrew Blair-Stanek, Nils Holzenberger, Benjamin Van Durme —
        ICAIL 2023, DOI 10.1145/3594536.3595163. arXiv:2302.06100
CLAIM   GPT-3 beats the prior state of the art on real-statute reasoning,
        but on SYNTHETIC statutes it cannot have memorized, its errors run
        overwhelmingly in one direction: it says a rule applies when it
        doesn't.
METHOD  SARA benchmark (real US Internal Revenue Code sections) plus
        synthetic statutes generated at controlled "width" (number of
        conditions) and "depth" (nesting), so the model is guaranteed
        never to have seen them; zero-shot and few-shot prompting.
NUMBER  Best GPT-3 result on SARA: 71% (71/100), vs prior BERT-based state
        of the art 59% (59/100). On synthetic statutes: of 2,272 total
        errors, 2,204 were false positives (the model asserting a rule
        applies when it does not) against 61 false negatives. Both
        figures independently re-confirmed against the paper's own text,
        not the abstract, which doesn't carry them.
FOR US  The published, peer-reviewed precedent for this project's own
        central finding, and a tighter match than card 1 — their errors
        are false positives on invented statutes; ours are the real-
        statute counterpart, three confirmed instances (Rule 206/207,
        Rule 57, Rule 243/247, `DECISION-D59.md`) of a resolver asserting
        a REAL, CURRENT, CORRECTLY-QUOTED provision reaches facts it does
        not — passing every citation-existence check and still wrong, in
        the identical direction this experiment measured.
SAY     "Blair-Stanek, Holzenberger and Van Durme (ICAIL 2023) found that
        when GPT-3 can't have memorized the statute, 2,204 of its 2,272
        errors were false positives — asserting a rule applies when it
        doesn't. We found the real-statute version of the same failure:
        three instances of a resolver citing a real, current, correctly-
        quoted provision whose own scope doesn't reach the facts, which
        is why we built a deterministic scope-reach check rather than
        trusting a bigger model to catch it."
```
*Caution, disclosed rather than smoothed over: a relayed research pass
citing this same paper also carried several more granular sub-figures — a
74%/64% split and a specific title-identification percentage — that did
not match this card's own independent re-verification of the paper's
text. Only the two numbers above are used anywhere in this project for
that reason.*

## 6. Chen, Li, Wan, Yuan — *From Statute to Control Flow: Span-Grounded Deontic Trees for Defeasible Scope Parsing*

```
PAPER   Jian Chen, Siyuan Li, Chucheng Wan, Zixuan Yuan — accepted KDD '26
        (32nd ACM SIGKDD Conference on Knowledge Discovery and Data
        Mining; venue confirmed via independent search, not the arXiv
        abstract page itself, which states no venue). arXiv:2606.08932
CLAIM   Names this project's central failure: "Silent Scope Omission"
        (SSO) — a model applies a general rule but silently drops nested
        exceptions or counter-exceptions, producing output that LOOKS
        compliant but breaks on the cases the exceptions exist for.
        Diagnoses the mechanism as an "Auditability Trap": models retrieve
        the relevant span but fail to attach it to its correct logical
        parent — finding the rule outperforms understanding its scope.
METHOD  NormBench: a benchmark of statutory/policy provisions compiled
        into span-grounded deontic trees, across Chinese law, English
        (including US tax law and GDPR), and corporate policy.
NUMBER  2,290 provision items (independently confirmed). More granular
        figures relayed alongside it (9,019 compiled branches, six
        annotators, agreement 0.76→0.91 / 81.2%→92.4%) were not present on
        the pages this card could independently fetch — not asserted here
        for that reason, though nothing found contradicts them either.
FOR US  BE PRECISE ABOUT THE FIT, not a stretch. SSO as defined is about
        exceptions dropped FROM INSIDE a provision; this project's three
        scope-reach instances (`DECISION-D59.md`) are about a provision's
        OWN governing scope — column B, its opening words, who it
        addresses. Same family — a scope limiter goes missing while the
        citation stays real — not the identical failure. Claim the
        family, not the identity: five (now three, code-closed) anecdotes
        become instances of a phenomenon independently named and
        benchmarked at KDD '26, in a different jurisdiction.
SAY     "The closest name for this in the literature is 'Silent Scope
        Omission,' from a KDD '26 statutory-parsing paper (Chen et al.) —
        theirs is exceptions dropped from inside a provision, ours is the
        provision's own governing scope, but it's the same family: the
        citation stays real while the thing that should have limited it
        goes missing, silently."
```

## 7. Cymbler, Guez, Fabre — *Temporal Misgrounding in Legal RAG: A Versioned-Corpus Benchmark for French Tax Law*

```
PAPER   Rose Cymbler, Daniel Guez, Laurent Fabre — submitted 10 August
        2026. arXiv:2608.09393 (independently verified via the arXiv
        abstract page; word-for-word match on every number below)
CLAIM   Retrieval-augmented legal QA treats its corpus as static. Real
        statutes are versioned over time, and a system that retrieves the
        currently-in-force text when an earlier or later version actually
        governs is confidently citing a real, but inapplicable, version.
METHOD  32,436 article-versions of the French tax code spanning 93 years
        (1938-2031). 209 expert-reviewed questions over 33 articles.
        Deterministic regex-with-numeric-tolerance scoring, explicitly
        NOT LLM-as-judge, to avoid inheriting the same temporal bias into
        the evaluator itself.
NUMBER  Parametric knowledge alone: 3.0% mean strict accuracy. Static RAG
        over the current-version corpus: 2.7% — and static RAG retrieves
        the date-applicable version 0% of the time. A multi-version
        retriever reaches 98.3%; an oracle-article ablation reaches 99.1%
        (so the residual error, once the version is right, is article
        retrieval, not version selection).
FOR US  The strongest available external justification for a decision
        already made independently (D31/C22): a frozen, verbatim corpus
        with an explicit tax-year currency check (`citation_matcher.py`),
        not embedding-based retrieval. Their contrast also defines this
        project's own contribution precisely: with the right version,
        they reach 98.3%. This project HAS the right version, the right
        article, the right quotation — and still produces no determinate
        figure for D1. That residual is what their benchmark cannot
        express, and is the actual thesis.
SAY     "Static RAG retrieves the date-applicable version of a statute 0%
        of the time (Cymbler et al., 2026) — which is exactly why this
        project uses a frozen, verbatim corpus with an explicit tax-year
        check instead of embedding retrieval. But even with the right
        version, the right article, and the right quotation — which their
        benchmark shows is the hard 97% of the problem — this project's
        hardest case still has no determinate figure. That's the part no
        retrieval benchmark can measure."
```

## 8. Guerdan, Barocas, Holstein, Wallach, Wu, Chouldechova — *Validating LLM-as-a-Judge Systems under Rating Indeterminacy*

```
PAPER   Luke Guerdan, Solon Barocas, Kenneth Holstein, Hanna Wallach,
        Zhiwei Steven Wu, Alexandra Chouldechova — NeurIPS 2025.
        arXiv:2503.05965
CLAIM   Many rating tasks admit more than one defensible answer ("rating
        indeterminacy"). Forcing a single forced-choice label anyway, then
        validating a judge system against it, selects a WORSE judge system
        than validating against the full set of defensible answers.
METHOD  11 real-world rating tasks, 9 commercial LLMs. Compares
        forced-choice validation against their own multi-label
        "response-set" validation, which keeps every rating a reasonable
        person could defend instead of collapsing to one.
NUMBER  Forced-choice validation selects judge systems performing as much
        as 31% worse than response-set validation, across the 11 tasks
        and 9 models tested.
FOR US  The honest competitor to this project's `certainty` enum, not an
        analogy to wave past. Their indeterminacy and this project's are
        NOT the same thing, and the difference is the whole argument:
        theirs lives in the RUBRIC — a better-written rating instruction
        can resolve it. This project's `lacuna`/`open_texture`/`contested`
        distinctions (`schema.json`, C22) live in the LAW ITSELF — no
        better-written prompt closes a gap Parliament left. Theirs is
        fixable by a better rubric; this project's is fixable only by a
        legislature. Their own method — keep the full defensible set
        rather than force one label — is also the right shape for scoring
        this project's own 12-figure valuation lattice, which is a
        response set in their exact sense.
SAY     "Rating indeterminacy (Guerdan et al., NeurIPS 2025) is the
        nearest named concept to what we measure, and the distinction
        matters: theirs is indeterminacy in the measurement rubric,
        fixable by a better question. Ours is indeterminacy in the law
        itself — three named certainty values (lacuna, open_texture,
        contested), none of which a better prompt can resolve, because
        the gap is in the statute, not in how we're asking about it."
```

---

## What this file is for

`novelty.md`'s one real weakness was citations with no identifier a judge
could check — every reference there is an inline marker, not a link. This
file exists specifically to fix that for the papers this project's own
decisions actually rest on. Linked from
[`DOCUMENTATION.md`](../DOCUMENTATION.md)'s prior-art section.
