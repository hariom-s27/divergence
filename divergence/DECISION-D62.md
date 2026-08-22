# D62 — prompt-injection scanner + nonce spotlighting: closing the gap SECURITY.md disclosed

**Date:** 22 August 2026
**M4 of a same-day priority list. Closes a limitation this project disclosed about itself two commits earlier (`b83b072`, `SECURITY.md`): "No prompt-injection defence... nothing here detects or resists a document that contains text aimed at the model itself."**

## Two layers, because one alone is a losing game

`injection_scanner.py` — a deterministic, standard-library-only pattern
scanner (10 pattern families: override claims, fake role/system messages,
persona reassignment, suppress-a-field instructions, an in-document legal
conclusion, chat-role delimiters, model-specific control tokens). Run on
the raw `--text` input before it's sent, advisory not blocking (folded
into `extraction_notes`, same discipline as every other disclosed-not-
enforced finding this project makes), and again on the model's own
output afterward, since a pattern surviving into the extracted facts is a
stronger signal than one merely present in the input.

Self-tested against a clean real case sample (0 findings) and a
constructed multi-family injection sample (6 findings, all correctly
labelled).

**`node1_extract.py`'s own text says why a pattern list isn't enough on
its own**: reworded around, it's invisible. The second layer, nonce
spotlighting, doesn't try to recognize injection attempts — it removes
the ambiguity a successful one depends on. Every call generates a fresh
random nonce (`secrets.token_hex(8)`, never hardcoded, never guessable in
advance); the untrusted document text is wrapped in
`<<<DOCUMENT-{nonce}-START/END>>>` markers; the system prompt is given an
explicit instruction (appended in code, not baked into
`01-extract.md`'s own fenced block, so the addition is a visible diff)
that text between those exact markers is data, never instructions,
regardless of what it claims to be — and that if such text is found, it
should be extracted verbatim as a field value with `confidence:
"unresolved"` and logged, not obeyed.

## The adversarial case

`cases/ADV1-injection/input.md` — a fabricated invoice covering every
pattern family at once: an override claim, a fake role reassignment, a
fake system acknowledgement, an in-document tax-exemption assertion, a
fake chat-role closing tag, an instruction to suppress the TDS gap and
report everything `settled`.

**Verified offline, both fully checkable without a model call:**
- `injection_scanner.scan()` on the raw document: **7 findings**, every
  pattern family represented, positions and matched text confirmed by
  hand against the source file.
- `node1_extract.build_content()`, called with a nonce, correctly wraps
  the entire document body in the `<<<DOCUMENT-{nonce}-START/END>>>`
  markers — confirmed by reading the actual returned content block, not
  assumed from the code.

**Not yet verified: whether the model actually complies with the
spotlighting instruction when it receives this document.**
`FEATHERLESS_API_KEY` was not set in the environment this was built in —
only an `OPENAI_API_KEY`, and `llm_call.py` is deliberately built (D44)
to refuse falling back to any provider other than Featherless rather than
silently using whatever key happens to be present. That guard did its
job here: it is the reason this session could not accidentally spend
against an unrelated account to finish this demonstration. **The live
run — `python node1_extract.py --text cases/ADV1-injection/input.md` with
a real `FEATHERLESS_API_KEY` set, then checking whether `facts{}` shows
any sign of having followed the embedded instructions (an exempt/settled
conclusion, a fabricated Section 999 citation) — is the next step**, and
is stated here as pending, not silently skipped or assumed to pass.

## What this does and does not prove

**Does**: raises the cost of a successful injection meaningfully above
what it was — an attacker's text now has to survive both a pattern scan
and a model that has been told, explicitly and specifically, that this
exact block of text is data. Every finding either layer produces is
disclosed in the final record's `limits[]`, not silently absorbed.

**Does not**: guarantee the model resists a sufficiently novel attack.
`injection_scanner.py`'s own `LIMITATIONS` section says this outright — a
phrasing that matches no pattern here is invisible to layer one, and
spotlighting narrows a model's willingness to comply with embedded
instructions, it does not formally prove it will never comply. SECURITY.md
updated to reflect exactly this — two real layers, stated precisely, not
oversold as "solved."
