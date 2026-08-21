# Q&A PREP — the twelve questions likely to actually get asked

**Status: drafted, not rehearsed.** Every answer below is checked against
the actual repo, not written from memory. What this file cannot do is the
part that matters most — saying these out loud, under pressure, with a
hostile judge pushing back. That's still the team's work: pick who answers
each one, say it out loud, and time it. Gate 0 lists this file as the one
required deliverable still missing until it exists with real content — it
now has that; rehearsal is the remaining step.

---

### 1. "Isn't this just a tax calculator?"

No — a calculator produces one number. This produces every defensible
number and refuses to pick one when the law itself doesn't. The headline
case has twelve valid rupee figures, ₹47,868.76 apart, and the system's
whole job is showing the range and saying why it can't be closed — not
computing a single "correct" answer.

### 2. "Isn't this just abstention? That's a solved research area."

Abstention withholds an answer. Our user can't withhold — she has a filing
deadline. So instead of abstaining, the system resolves every defensible
way, prices the disagreement, and lets a human elect one **on the record**
— optionally, since the record is already complete and valid with nothing
elected (`scope.md` Part 8, decision C65: a pre-selected default is a
recommendation, so there isn't one). That's a different move from
abstention, not a rebranding of it. Worth knowing: AbstentionBench
(NeurIPS 2025) found scaling doesn't fix abstention and reasoning
fine-tuning makes it 24% *worse* — see question 12.

### 3. "Self-critique nodes are everywhere — Self-Refine, Reflexion. What's new?"

Every system in that literature uses critique to *improve* the answer
before you see it. We publish the attack and never let it silently improve
the answer — `downgraded_to` is computed and shown, but deliberately never
auto-applied to a conclusion's certainty (the free-text attack target is
too easy to mis-match back to the wrong conclusion; see `results.md`). The
critique is an output a reader cross-checks by eye, not a hidden editing
step. It's also grounded differently: a different model family from the
resolvers (decision D41), justified by two measured results, not instinct
— Huang et al. (ICLR 2024) found LLMs can't reliably self-correct without
external feedback; Panickssery et al. (NeurIPS 2024) measured LLM
evaluators favoring their own generations. Full cards:
`prior-art/READING-CARDS.md`.

### 4. "How do we know your baseline isn't deliberately weak?"

It's frozen and published unedited (`baseline-prompt.md`, since 6 August),
plus a second, token-matched chain-of-thought baseline given the same
token budget as the real pipeline — so the result isn't just "more compute
helps." And the baseline beats us outright on one of our own headline
numbers — see question 5. A team protecting its own result doesn't publish
the case where the naive approach won.

### 5. "Where does your system perform worse than the baseline?"

**Lead with this before they find it.** On D1, the naive baseline scored
75% gap recall against our pipeline's 25%. Arm C also scored 0% gap recall
on three of six cases. Both are in `results.md`'s "Where we lose" section,
first bullet, not buried in an appendix.

### 6. "Your gap detector returned 0%, 50% and 75% on three runs of the same case."

It did — same input, same code, three seeds. We publish all three
individually and quote no mean, because a mean at n=3 with that much
spread implies a smooth distribution that doesn't exist. It's also not an
isolated weak measurement: Blair-Stanek and Van Durme (ICAIL 2025) found
leading LLMs flip their answer to identical legal questions even at
temperature 0, on a different task, same domain. Checking whether our own
instability was fully real or partly a scoring artifact, we hand-verified
every match our scorer made — two of the three numbers hold up exactly;
the third (75%) is inflated by a real double-counting bug in our own
matcher, which we found and disclosed rather than quietly kept (`results.md`,
`DECISION-D57.md`).

### 7. "You amended your own schema nine-plus times after your own freeze commit."

Yes — disclosed in `DECISION-D46.md` and `results.md`, every one to the
output contract, none touching `cases/*/ground_truth.json`. The freeze
commit's load-bearing content — `citations_expected[]`, `missing[]`,
`elements`, `methods_expected` — never changed after the freeze. We'd
rather a judge hear this from us than find it by diffing the commit.

### 8. "Your own output asserted a wrong rule multiple times. Why should we trust it?"

You shouldn't trust any single output — that's the design, not a caveat on
it. Five confirmed instances of the identical failure — a real, current,
correctly-quoted provision applied outside its own scope — in our own
resolver output. Three found by our own adversarial checker on data nobody
planted. **None of the five was visible to any of our five accuracy
metrics** — M3 and M4 stayed at 100% and 12/12 through every version.
That's not our bug list, it's our result: a model given verbatim statute
and an underdetermined question reliably reaches for the nearest rule that
mentions the right words. Full account: `DOCUMENTATION.md` §5.

### 9. "Why nine steps and not one prompt?"

Four of the nine are not model calls at all — they're plain Python. Those
four are exactly the ones that cannot invent anything: the gap enforcer
(an unconditional `if`), the valuation lattice (arithmetic over sourced
data, no API), the citation matcher (string match against real corpus
text), the disclosure composer (a deterministic template). A rule you
can't enforce isn't a rule — that's the whole architecture in one
sentence.

### 10. "Is receiving crypto for services even legal in India?"

Very likely non-compliant **by inference**, not by explicit prohibition —
read from FEMA s.2(n) together with ss.7–8, not a blanket "crypto is
illegal" claim. We're careful about that distinction on purpose: overclaiming
it would itself be exactly the kind of confident-but-unsupported statement
this project exists to catch.

### 11. "What does it cost per record, and who maintains it?"

Metered (a Claude-equivalent deployment estimate, not a measured cost):
₹29.91/record. The actual evaluation ran on open-weight models
(Qwen2.5-7B/72B, Mistral-Large) via Featherless — ₹0 marginal cost on that
plan, no frontier-model dependency. Maintenance: the corpus is one
provision per file, dated and versioned; when a law changes you replace
one file, not the code or any model, and a citation that's gone stale gets
caught automatically — demonstrated on five of this project's own
historical errors, not just claimed.

### 12. "Won't a bigger/newer model just fix this?"

The evidence points the other way. AbstentionBench (NeurIPS 2025, 20
benchmarks) found reasoning fine-tuning degrades abstention by 24% on
average, even on domains those models are explicitly trained for — scaling
and "smarter" reasoning modes don't reliably fix a model's judgment about
when it doesn't actually know. That's a large part of why the boundary in
this project is a declared, checkable manifest (which provisions were
actually checked) rather than trust placed in a bigger model to know when
to stop.

---

## What's still needed before this is actually prep, not just a draft

- Assign a name to each answer above (who on the team owns it).
- Say every one out loud, once, cold — then again with someone playing a
  hostile judge who interrupts.
- Time the 30-second version: can you say what this project does, plainly,
  in 30 seconds, without this file in front of you?
