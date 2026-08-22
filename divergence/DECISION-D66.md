# D66 — OWASP LLM Top 10 threat-model mapping, and pinning requirements.txt

**Date:** 22-23 August 2026
**S5 and S7 of the SHOULD list, done together since S5's own mapping named the exact gap S7 closes — writing one without the other would have left a stale line the moment the second was fixed.**

## S5 — the mapping

`SECURITY.md` gained a table mapping this project's actual architecture
against the **OWASP Top 10 for LLM Applications 2025** — verified against
two independent sources first (the canonical `genai.owasp.org` page
403'd a direct fetch), not written from memory or an older 2023-edition
list, which has different category names and order.

**Mapped honestly, not padded.** Three categories are marked squarely
not applicable — LLM06 (Excessive Agency: no node has tool access or
autonomous action), LLM08 (Vector and Embedding Weaknesses: no vector DB,
no embeddings, no retrieval step anywhere in this pipeline — corpus
injection is a fixed, hand-scoped file list, D31/C22), and LLM07 (System
Prompt Leakage: every prompt this project uses is already public, in this
repository — there is no hidden instruction whose disclosure would
matter). Two categories are named as close to this project's actual
thesis rather than a gap being covered defensively — LLM05 (Improper
Output Handling: nothing here ever treats a model's JSON as trusted
because it parsed) and LLM09 (Misinformation: hallucinated citations and
false confidence are the subject of this entire project, not a side
risk). LLM01 (Prompt Injection) points back to the real, already-built,
already-limited defence (D62). LLM04 (Data and Model Poisoning) is
reframed honestly for an architecture with no trained model: the real
analogue is corpus integrity, already covered by `corpus_hash.py` (D60).

**LLM03 (Supply Chain) and LLM10 (Unbounded Consumption) are marked
partial, with the specific gap named, not glossed over** — which is what
S7 closes one half of.

## S7 — the gap LLM03 named, closed

`requirements.txt` pinned every dependency to `==`, not `>=`: `openai`,
`anthropic`, `pypdf`, `jsonschema`. Pinned to the exact versions this
project's own work has actually run against all session (checked via
`pip show`, not guessed at "latest") — `openai==2.30.0`,
`anthropic==0.97.0`, `pypdf==6.16.1`, `jsonschema==4.26.0`. `pip-audit`
(already CI-gated, `DECISION-D66.md`'s predecessor commit) re-run against
the pinned file: still clean.

**Why a floor (`>=`) was a real, not theoretical, gap**: `pip-audit`
scans whatever version actually gets installed. A floor means that
version drifts on every fresh install as new releases ship — the thing
being audited isn't a fixed target, so "clean" on one day says nothing
about what installs six months later. A pin makes the audited version
and the installed version the same thing, deliberately, every time, and
a version bump becomes its own visible, disclosed commit rather than an
invisible side effect of when `pip install` happened to run.

**LLM10 (Unbounded Consumption) remains explicitly partial, not
claimed fixed by this commit** — `llm_call.py`'s retry cap
(`MAX_ATTEMPTS = 3`) and per-call `max_tokens` are real, existing bounds,
but no cost ceiling or spend-alerting mechanism exists. Moot for a local/
CI pipeline with no public endpoint, same caveat `SECURITY.md` already
states for rate limiting and auth — stated again here rather than
silently left to look more complete than it is.
