# D43 — Which Featherless model fills each slot, and the gated-model finding

**Date:** 20 August 2026
**Builds on D42.** D42 chose *how* the provider is selected (env var, at
runtime). D43 is *which three models* fill `small`/`large`/`adversarial` on
Featherless, and a live-testing finding that changed one of them.

## How the choice was made — not guessed, queried

`llm_call.py`'s three model slots need real, working model IDs. Featherless
hosts 21,000+ models, almost all community fine-tunes not suited to a legal-
reasoning task. Rather than pick names from memory (several plausible-looking
ones — `deepseek-ai/DeepSeek-V3`, `meta-llama/Llama-3.2-11B-Vision-Instruct`
— turned out not to exist on this catalogue at all), the actual account was
queried live:

1. `GET /v1/models` with the real key → 21,741 models, each flagged
   `available_on_current_plan`.
2. Filtered to reputable, official-org instruct models in that set:
   `Qwen/Qwen2.5-7B-Instruct`, `Qwen/Qwen2.5-72B-Instruct`,
   `meta-llama/Llama-3.3-70B-Instruct`, `mistralai/Mistral-Large-Instruct-2411`.
3. Each candidate test-called with a real `chat/completions` request before
   being written into any file.

## Finding: every `meta-llama/*` model 403s on this account

`meta-llama/Meta-Llama-3.1-70B-Instruct` (D42's original `adversarial`
default) — and every other `meta-llama/*` ID tried, including
`Llama-3.3-70B-Instruct` and `Llama-3.1-8B-Instruct` — returned:

```
403 model_gated_needs_oauth
"This model is gated. Connect HuggingFace for this organization at
 https://featherless.ai/models/... to verify access."
```

This is a HuggingFace license gate Featherless passes through, not a
Featherless plan restriction — `available_on_current_plan` was `true` for
these models; the block is one layer further out, and nothing in the `/v1/models`
response signals it in advance. **It would only have been found by actually
calling the model, not by reading the catalogue.**

## Decision: adversarial slot moves to Mistral

`mistralai/Mistral-Large-Instruct-2411` — confirmed working live, no gate —
replaces the Llama default. D41 only requires the adversary be a **different
model family from the resolvers** (`large` = Qwen); Mistral satisfies that
exactly as well as Llama would have. `llm_call.py`'s `PROVIDERS["featherless"]`
updated accordingly, with the finding recorded in a code comment so nobody
re-discovers this by hitting the same 403 later.

**If you want Llama specifically:** the gate is fixable on featherless.ai's
own site (connect a HuggingFace account with the Meta license accepted), not
in this codebase. Until then, `DIVERGENCE_MODEL_ADVERSARIAL` pointed at any
`meta-llama/*` ID will 403 on this account — `check_llm.py` will say so
before a real run does.

## What was NOT pursued: a vision model for node 1

Node 1 (EXTRACT) architecturally accepts a photographed invoice. A vision-
capable small model was investigated for that path:
`Qwen/Qwen2.5-VL-7B-Instruct` returned `503 capacity_exhausted` on three
consecutive live attempts (a Featherless-side cold-start/availability issue
on that specific model, not an account or code problem);
`Qwen/Qwen2.5-VL-72B-Instruct` worked. No vision model is wired into
`llm_call.py`'s default slots — `node1_extract.py` sends images as OpenAI-
format `image_url` blocks and will use whatever model the `small` slot
resolves to, which is text-only on Featherless today. Running node 1 on a
real photographed invoice needs `DIVERGENCE_MODEL_SMALL` pointed at a vision
model by hand for that run — not automated here, because a 7B/72B split this
sharp on a single capability is a decision with cost and reliability
consequences worth a human choosing at the time, not a silent default.

## Verified, live, before this was written

```
python check_llm.py
  small        Qwen/Qwen2.5-7B-Instruct                OK
  large        Qwen/Qwen2.5-72B-Instruct               OK
  adversarial  mistralai/Mistral-Large-Instruct-2411    OK
  D41 OK   resolvers=qwen  adversary=mistralai  (different families)
```
