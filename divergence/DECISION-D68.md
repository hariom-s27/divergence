# D68 — capability probe: is `response_format` a silent no-op?

**Date:** 23 August 2026
**S8, the last SHOULD item.**

## The real exposure this checks for

Every resolver call sets `response_format={"type": "json_object"}`
(`llm_call.py`'s `_raw_call`). If Featherless's OpenAI-compatible layer
hard-rejects that field, `_raw_call` already catches it and retries
without it — a loud, already-handled failure. Nothing before this
checked the quieter case: the field is accepted without complaint, but
the actual open-weight model behind Featherless's proxy never
implemented grammar-constrained JSON decoding, and just ignores it. No
exception, no signal — the pipeline would look identical either way,
because today's real reliability comes mostly from the prompt asking for
JSON (every system prompt in `prompts/` says so), not provably from the
flag. Checked first whether any existing doc already claimed
`response_format` as a guarantee it hadn't verified — grepped every
`.md` in the project for "JSON mode" / "response_format": zero hits.
Nothing to correct; this is a gap to close, not an overclaim to walk
back.

## The test built

`capability_probe.py` fires the same prompt twice per model slot — one
short line asking explicitly for **plain prose, not JSON** — once with
`response_format` set (call A), once without it (call B, the control).
If the flag is doing real work, it should win against an instruction
that directly contradicts it: A comes back as JSON despite being told
not to, while B (no flag, same contrary instruction) comes back as the
prose it was asked for. If A comes back as prose too, identical to the
unflagged control, the flag demonstrably changed nothing observable for
that model.

Deliberately **not** a "reply in JSON only" system prompt, and
deliberately **not** this project's own resolver prompts: either would
let the model's own voluntary instruction-following manufacture a false
ENFORCED verdict. Setting the flag in direct conflict with the prompt's
own words is what isolates the flag's effect from the model just being
generally JSON-friendly when asked.

Five possible verdicts, each with a plain-English reason attached:
`REJECTED` (provider error naming the field — already handled elsewhere
in the pipeline), `ENFORCED`, `APPARENT NO-OP`, `INCONCLUSIVE` (control
call also came back as JSON, so the test can't isolate the flag's
effect for that model), `ERROR` (an unrelated failure).

Bypasses `call_json()`'s retry-and-repair loop on purpose — that loop's
own "that was not valid JSON, try again" follow-up would coerce a JSON
object out of the model on a second attempt regardless of whether the
flag did anything, masking exactly the signal this probe needs to see
on the first, unrepaired response.

## What was verified without a live key

The classifier (`classify()`) is a pure function — text/error in,
verdict out, no network call — so it is fully testable offline. Built
five hand-constructed fixtures, one per verdict, run via `--self-test`:
all five pass. Also added `llm_call.try_parse_json()`, a small public,
side-effect-free wrapper around the pipeline's own existing relaxed
parser (`_extract_json` — fence-stripping, brace-matching, not just
strict `json.loads`), so the probe judges "is this JSON" by the exact
same standard the real pipeline would use, not a stricter or looser one
of its own. Confirmed the addition is purely additive: `git diff` on
`llm_call.py` is a clean 14-line insertion, and the four pre-existing
non-gating flake8 complexity/style warnings in that file are unchanged
in substance (one shifted line number, from the insertion sitting above
it — not a new warning). Confirmed the live-probe path fails the same
clear, existing way `check_llm.py` does with no key set (`FAIL
FEATHERLESS_API_KEY is not set...`), rather than a confusing traceback.
The classifier self-test itself needs no key, so it is CI-gated
alongside the other pure self-tests; `main()`'s actual two-call probe is
not, and cannot be — CI has no key, the same reason `DIVERGENCE_REPLAY`
exists at all (D63).

## What is not claimed

**Which verdict any of the three real model slots actually gets is not
answered here.** That is the entire point of the probe and it needs a
live `FEATHERLESS_API_KEY` this environment does not have — the same
constraint every S/M item touching real model behaviour has hit
(D62/D63/D64/D65/D66/D67). What this decision closes is the part that
was answerable without one: a fair, bypass-proof test exists, its
classification logic is proven correct against five known-shape
fixtures, and it costs a few hundred tokens to actually run the moment
someone with a key does.
