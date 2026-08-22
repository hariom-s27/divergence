# Security

This is a hackathon submission (DIVERGENCE, ReverieHacks 2026). No user
accounts, no database of real people's data, no backend at all — the one
thing served live is the same static HTML this repository already
contains, unmodified, via GitHub Pages. That shapes what "security"
actually means here — this file says what is and is not true, not a
generic policy copied in.

## What is actually true

- **No secrets in the repository, ever.** API keys (Featherless, OpenAI,
  Anthropic, Firecrawl) are read only from environment variables
  (`llm_call.py`, `firecrawl_demand.py`). `divergence/.gitignore` blocks
  `.env`, `*.key`, `*.pem`, `secrets.*`, and anything matching
  `*apikey*`/`api_key*` from ever being tracked. `llm_call.py` also
  refuses to silently fall back to a different provider if the intended
  one's key is missing (decision D44) — a misconfigured key fails loudly,
  it does not quietly start billing a different account.
- **No real user data.** Every case (`divergence/cases/`) is a fictional
  fact pattern — a fictional freelancer, a fictional counterparty, invoice
  numbers made up for the case, not a real transaction or a real person's
  filing.
- **`output-interface.html` and the other generated disclosure pages are
  fully static.** No `fetch(`, no external script, no analytics, no
  network call of any kind — opening them in a browser sends nothing
  anywhere. The one piece of client-side state (`node7_disclosure.py`'s
  election UI, D58) writes to the reader's own browser `localStorage`
  only, never transmitted.
- **Dependencies are scanned.** `pip-audit` runs against
  `divergence/requirements.txt` in CI on every push. Clean as of this
  writing.
- **The one node that reads untrusted document text has two real
  defence layers**, added after this file first shipped without them
  (`DECISION-D62.md`). `injection_scanner.py` — deterministic, no
  model — scans the raw input for known injection phrasings (override
  claims, fake system/role messages, an in-document legal conclusion,
  chat-role delimiters) before it's ever sent, and again on the model's
  own output afterward; both advisory, folded into `extraction_notes`,
  not a hard block. `node1_extract.py` wraps the untrusted text in a
  fresh, random per-call nonce marker and tells the model explicitly
  that text inside those markers is data, never instructions, no matter
  what it claims to be. See the next section for what this does not
  guarantee.
- **The only thing deployed is a static file mirror.** `divergence/` is
  published to GitHub Pages (`.github/workflows/pages.yml`,
  `actions/deploy-pages`) exactly as it sits in this repository — no
  server, no build step beyond copying files, no code that executes on
  request. The pipeline itself (every 🤖/⚙ node) still only ever runs
  locally or in CI, writing files to disk; nothing about *that* changed.
  There is no live endpoint that accepts input, because there is no live
  endpoint that accepts input — only one that serves already-generated,
  already-public files.

## What is genuinely not defended against — said plainly, not hidden

This project's own discipline is to disclose a real limitation rather
than let a reader discover it, and that applies to this file too:

- **The prompt-injection defence is real but not a guarantee.**
  `injection_scanner.py`'s own pattern list is invisible to a phrasing it
  doesn't recognize — an attacker who avoids the ~10 known families this
  scans for is undetected by layer one. Nonce spotlighting narrows what a
  model is willing to do with embedded instructions; it does not formally
  prove the model will never comply with a sufficiently novel one. Tested
  offline against a constructed adversarial case
  (`cases/ADV1-injection/`, `DECISION-D62.md`) covering every pattern
  family at once — both layers behaved as designed. The live check of
  whether the model itself resists the embedded instructions, rather than
  just receiving the spotlighting markers, is recorded as pending in that
  same decision doc, not assumed to pass. The downstream deterministic
  gates (⚙ A/C/E, `gap_enforcer.py`/`citation_matcher.py`/
  `scope_enforcer.py`) still constrain what a resolver's *conclusion* can
  assert against the statutory corpus regardless of what Node 1 produces,
  which bounds the damage even a fully successful injection could do to
  the final disclosure.
- **No rate limiting, no auth, no multi-tenant isolation.** None of these
  apply to a local/CI-run research pipeline with no live endpoint, but
  they would need to exist before this became a real product, and this
  file says so rather than implying otherwise by omission.
- **The statutory corpus is not cryptographically signed against its
  official source**, only hashed against its own frozen copy
  (`corpus_hash.py` — see `DECISION-D60.md`). That catches an accidental
  or malicious edit made *after* the freeze. It does not prove the
  frozen text was transcribed correctly from the gazette in the first
  place; that is checked by other means (`gate0_check.py`'s duplicate/
  shadow-citation checks, human review against `source_url`), not by
  cryptography.

## Threat model, mapped to OWASP Top 10 for LLM Applications 2025

Verified against the official list (two independent sources, since the
canonical `genai.owasp.org` page 403'd a direct fetch) before mapping
anything to it — not assumed from memory. Mapped honestly: several
categories genuinely don't apply to this architecture, and that's stated
as plainly as the ones that do, not padded to look more complete.

| # | Category | This project |
|---|---|---|
| LLM01 | Prompt Injection | **Addressed, not solved.** `injection_scanner.py` + nonce spotlighting, above. Real defence, real stated limits, live verification still pending a key. |
| LLM02 | Sensitive Information Disclosure | **Mostly moot by design.** No real user data exists to disclose (every case is fictional); the one real secret class (API keys) is covered above. Nothing else in this pipeline handles data a disclosure would harm anyone over — the statutory corpus is meant to be public. |
| LLM03 | Supply Chain | **Partial.** `pip-audit` scans `requirements.txt` in CI (clean as of this writing) — but the file pins with `>=`, not `==`, so a dependency update between scans could still land unreviewed. Open; see `DECISION-D66.md`. |
| LLM04 | Data and Model Poisoning | **Not model training — corpus integrity is the real analogue, and it's covered.** No model is trained or fine-tuned here. This pipeline's closest equivalent to a poisoned knowledge base is a tampered statutory corpus, and that's exactly what `corpus_hash.py` (D60) defends against — a corpus edit that isn't followed by a deliberate `--freeze` fails CI, visibly. |
| LLM05 | Improper Output Handling | **This is close to the project's actual thesis, not a gap.** Every model output is validated and cross-checked before it reaches a reader — `citation_matcher.py`, `scope_enforcer.py`, `gap_enforcer.py`, `node5_adversarial.py`'s own `_reject_upward_revisions`. Nothing here treats a model's JSON as trusted just because it parsed. |
| LLM06 | Excessive Agency | **Not applicable — by design, not by luck.** No node has tool access, autonomous action, or the ability to affect anything beyond its own JSON output. Every real decision (drop a citation, force a certainty value) happens in deterministic code that reads a model's output, never in the model itself acting. |
| LLM07 | System Prompt Leakage | **Low stakes, and mostly moot.** Every system prompt this project uses is already public, in this repository, in `step22drop/prompts/*.md` — there is no hidden instruction whose disclosure would matter. The nonce-spotlighting instruction (D62) is a real addition to those prompts and is exactly as public as the rest. |
| LLM08 | Vector and Embedding Weaknesses | **Not applicable.** No vector database, no embeddings, no semantic retrieval anywhere in this pipeline — corpus injection is a fixed, hand-scoped file list per node (D31/C22), not a retrieval step. Also the reason this project cites Cymbler et al.'s static-RAG finding (`prior-art/READING-CARDS.md` #7) as external support for that choice, not just an internal preference. |
| LLM09 | Misinformation | **The project's actual subject, not a side effect.** Hallucinated citations, scope-reach failures, and false confidence are what `citation_matcher.py`, `scope_enforcer.py`, and node 5 exist to catch — documented at length everywhere else in this repository, not just here. |
| LLM10 | Unbounded Consumption | **Partially bounded.** `llm_call.py` caps retries (`MAX_ATTEMPTS = 3`) and output tokens (`max_tokens`) on every call. No cost ceiling or spend alerting exists — moot for a local/CI pipeline with no public endpoint accepting input, but would need to exist before this became a real product, same caveat as rate limiting above. |

## Reporting something

This is a student hackathon project with no dedicated security contact
or bug bounty. If you find something real, open a GitHub issue on this
repository — it's public, and that's consistent with how the rest of
this project already operates (every decision, bug, and limitation is
disclosed in a dated `DECISION-D*.md` file, not handled privately).
