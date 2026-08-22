# Security

This is a hackathon submission (DIVERGENCE, ReverieHacks 2026), not a
deployed service. No live server, no user accounts, no database of real
people's data. That shapes what "security" actually means here — this
file says what is and is not true, not a generic policy copied in.

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
- **Nothing is deployed.** The pipeline runs locally or in CI, writing
  files to disk. There is no live endpoint to attack, because there is no
  live endpoint.

## What is genuinely not defended against — said plainly, not hidden

This project's own discipline is to disclose a real limitation rather
than let a reader discover it, and that applies to this file too:

- **No prompt-injection defence.** `node1_extract.py` (🤖 1) reads a
  user-supplied invoice or payment record and passes its text into an LLM
  call. Nothing here detects or resists a document that contains text
  aimed at the model itself (e.g. instructions embedded in a PDF telling
  the extractor to misreport a field). The downstream deterministic gates
  (⚙ A/C/E, `gap_enforcer.py`/`citation_matcher.py`/`scope_enforcer.py`)
  constrain what a resolver's *conclusion* can assert against the
  statutory corpus, which limits the damage such an attack could do to
  the final disclosure — but nothing in this pipeline is designed to
  catch the injection at the point it enters, at Node 1.
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

## Reporting something

This is a student hackathon project with no dedicated security contact
or bug bounty. If you find something real, open a GitHub issue on this
repository — it's public, and that's consistent with how the rest of
this project already operates (every decision, bug, and limitation is
disclosed in a dated `DECISION-D*.md` file, not handled privately).
