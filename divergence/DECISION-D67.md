# D67 — factored (draft-blind) verification in node 5, opt-in and verified not to regress

**Date:** 22-23 August 2026
**S6 of the SHOULD list.**

## The real exposure this closes part of

`node5_adversarial.check()` has always sent each conclusion's full
JSON to the model, including its own `reasoning` field — schema.json's
own description of that field: *"why this provision reaches these facts,
or why it does not."* That is the resolver's own persuasive case for its
own conclusion, read by the same step that's supposed to independently
check it. This project already cites the exact mechanism this risks —
Panickssery et al. (NeurIPS 2024, `prior-art/READING-CARDS.md` #4b): an
LLM evaluator measurably favours output that reads like its own
reasoning. D41 grounds the *cross-model-family* requirement in that
result. Nothing before this addressed the narrower, still-real version of
the same risk: even a different model can be anchored by reading the
original producer's own argument before forming an independent one.

## What was built

`node5_adversarial.check(..., draft_blind=False)` — an opt-in parameter,
same on `node5_adversarial.py --draft-blind` and `run_pipeline.py
--node5 --draft-blind`. When set, `_strip_draft_fields()` removes
`reasoning` from a deep copy of each conclusion (never mutating the
caller's own `regimes[]`, which downstream disclosure still needs it in)
before it's ever included in the prompt, and an explicit note tells the
model why: check the outcome/citation/certainty against the statutory
text directly, not against the reasoning that used to be there.

## Verified three ways before trusting it, not shipped on the strength of reading the diff

1. **The default path is provably unchanged.** Reconstructed the exact
   pre-existing prompt string `build_replay_cache.py` seeded the replay
   cache with, and confirmed `draft_blind=False` still resolves to the
   identical cache key — the string-concatenation change (adding an
   empty `blind_note` when off) produces byte-identical output to before.
2. **`_strip_draft_fields()`'s claimed correctness properties, checked
   directly**: the caller's original `regimes[]` list is unmutated after
   the call: confirmed equal to a pre-call deep copy. Every stripped
   entry lacks `reasoning`; every original entry still has it.
3. **End to end, both flags, via replay**: `draft_blind=False` still hits
   the real seeded D1 cache entry (4 attacked entries, matching the
   frozen original exactly). `draft_blind=True` correctly **misses** —
   raises `LLMError` naming the new, different cache key — proving the
   prompt actually changed rather than silently doing nothing. Then ran
   the full `run_pipeline.py --node5` end to end in replay mode and
   confirmed `facts`/`missing`/`attacked` all still byte-identical to the
   frozen originals — the new flag touches nothing outside the one path
   that opts into it.

## What is not claimed

**Whether draft-blind verification actually changes what node 5 catches
is not answered here.** That needs the model to actually receive both
versions of the prompt and be compared — a live question, not a code
question, and this environment has no `FEATHERLESS_API_KEY` to ask it,
the same constraint every S/M item touching a live call has hit
(D62/D63/D64/D65/D66). What this decision closes is the part that was
answerable without one: the flag exists, defaults to off, provably
doesn't disturb any existing behaviour, and is one flag away from a real
comparison the moment someone can run it.
