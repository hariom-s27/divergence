# D42 — Provider is chosen at runtime, and recorded in the output

**Date:** 20 August 2026
**Supersedes nothing. Implements D35.**

## Decision

`llm_call.py` no longer hardcodes a provider. It resolves one at runtime from
whichever API key is present in the environment, preferring Featherless:

| Provider | Env var | Role |
|---|---|---|
| Featherless (open weights) | `FEATHERLESS_API_KEY` | **the measured eval run** (D35) |
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | cost estimate only, if re-metered |

Model slots default to `Qwen/Qwen2.5-7B-Instruct` (small),
`Qwen/Qwen2.5-72B-Instruct` (large), `meta-llama/Meta-Llama-3.1-70B-Instruct`
(adversarial), and can be overridden per-slot by `DIVERGENCE_MODEL_SMALL` /
`_LARGE` / `_ADVERSARIAL` without editing code — Featherless gates model size
by plan tier.

## Why it is recorded, not just chosen

`llm_call.provenance()` returns provider, the three resolved model ids,
per-node call counts, token totals and **retry counts**, and is folded into
every record's `_meta.llm`. `results.md` quotes the record rather than the
author's memory.

This closes a specific honesty risk in D35. "The eval runs on open models,
the Claude figure is a metered estimate" was, until now, a claim held only in
a decision log — nothing in any output file distinguished the two. Now every
record states which models produced it.

## D41 is enforced, not assumed

The resolvers are Qwen; the adversary is Llama. `check_llm.py` compares the
org prefix of the `large` and `adversarial` model ids and prints a WARNING if
they match. If node 5 runs the same model as node 3, "the adversarial node
found nothing" is a model agreeing with itself, and the control is silently
gone — a Class 3 failure in our own harness.

## Consequences accepted

- The 7B `small` slot will extract less accurately than Haiku did. That
  degradation is a **measurement**, not a defect to conceal; it belongs in
  `results.md` as a finding about running this pipeline on open weights.
- Open models fence and preamble their JSON. `llm_call.py` strips fences,
  scans for the first balanced object, and on failure shows the model its own
  output and re-asks (3 attempts). Retries are counted in `provenance()` so a
  chronically-retrying node is visible rather than silent.

## Key handling

No API key is written to any file in the repo. Keys live in the shell only.
`.gitignore` (covering `.env*`, `*.key`, `secrets.*`) must be committed
**before** `git init` produces the pre-registration hash quoted in
`results.md` — otherwise the hash a judge is asked to trust contains a secret.
