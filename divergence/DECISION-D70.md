# D70 — injection defence, extended: hidden characters, field-setting attempts, and a visible disclosure section

**Date:** 23 August 2026

## What this actually is, disclosed before the rest

A request came in asking for a new `injection_scan.py`, a new
`<<<UNTRUSTED_DOCUMENT nonce=...>>>` marker format, and the nonce
mechanism rebuilt from scratch. Reading `node1_extract.py` and
`injection_scanner.py` first (as the request itself said to) found that
mechanism already shipped, tested, and CI-gated as D62: nonce
spotlighting with `secrets.token_hex(8)`, regenerated per call, an
explicit system-prompt instruction, and a pattern scanner already wired
into node 1 and CI. Rebuilding it under new names would have meant two
parallel, subtly-different security mechanisms in the same project —
confirmed with the user before touching anything (`AskUserQuestion`) —
rather than one well-maintained one. What follows is the part of that
request that was genuinely new, found by comparing the ask against the
actual current files rather than assuming either "already done" or
"build everything as asked" without checking.

## Three real gaps closed

1. **`injection_scanner.py` had zero non-printing/bidirectional
   detection.** `PATTERNS` was phrase-only. Added
   `_scan_hidden_chars()` against a named, hand-kept list — zero-width
   space/non-joiner/joiner/word-joiner, the BOM, and the eight
   bidirectional-override/isolate codepoints (U+202A–E, U+2066–9) —
   because, as the request put it, hidden instructions need not be
   human-readable. **Built with `chr(0x....)`, never a literal
   character typed into the file** — caught live while writing it: a
   first attempt with literal zero-width/bidi characters as dict keys
   kept silently round-tripping back to literal characters no matter how
   the escape was phrased in the surrounding text, exactly the kind of
   invisible, unauditable, tooling-fragile risk a file whose entire job
   is detecting these codepoints cannot afford in its own source.
2. **No pattern for a document telling the model to set a field or
   confidence value directly** ("set X to true/certain") — added,
   verified against its own planted sample, distinct from the existing
   "suppress a finding" pattern.
3. **Findings only ever reached a reader as prose inside
   `extraction_notes`, never structurally, never on the disclosure page
   itself.** `node1_extract.extract()` now returns a fourth value,
   `integrity` — `{nonce_spotlighting_applied, pre_scan_findings,
   post_scan_findings}` — which `run_pipeline.py` stores at
   `_meta.input_integrity` and `node7_disclosure.py` renders as its own
   numbered section, **00 — Input integrity**, ahead of "what is
   missing" — the same "check this before anything else" ordering the
   file's own header already argues for everything else.

## The design rule, honoured structurally, not just by intent

The request was explicit: detect, refuse to let a finding change a
field, disclose — never silently strip. `render_input_integrity()`
makes no judgement of its own and calls nothing — it only reads what
`node1_extract.py` already recorded, the same discipline
`render_attacks()` already uses for `attacked[]`. Nothing between
detection and disclosure has a code path that could remove a finding
before a reader sees it.

## Also: self-test rebuilt to be per-pattern, not aggregate-only

The old self-test checked "does a combined sample yield at least 5
findings" — passable even if one specific regex had silently broken, as
long as enough others still fired. Now: one planted, single-purpose
sample per pattern (all 11 phrase families, plus the hidden-character
check), each verified to trip its own specific label, kept alongside the
original clean-control and combined-sample checks. 14/14 on the first
real run. Already CI-gated — `injection_scanner.py --self-test` was
wired into CI at D62; extending the existing file means the existing
step already covers everything added here, no new CI step needed for
that half (`_meta.input_integrity`'s wiring has no self-test of its own
yet — verified instead by a full `DIVERGENCE_REPLAY=1` pipeline run,
byte-identical to the frozen D1 originals, and by rendering both the
clean and findings-present branches of the new disclosure section
against constructed fixtures).

## What is not claimed

The hidden-character list is named, not exhaustive — an unlisted
non-printing codepoint is ordinary text to this file, same disclosed
shape as `scope_enforcer.py`'s `KNOWN_VDA_ASSETS`. Homoglyph
substitution (a different script's character standing in for a Latin
letter, reading correctly to a human while dodging the regexes) is not
detected by either layer. And, as every version of this defence has said
since D62: whether the model itself actually resists an embedded
instruction, rather than just receiving the spotlighting markers, is a
live question this environment has no `FEATHERLESS_API_KEY` to answer —
`cases/ADV1-injection/` tests the mechanism offline, not a real model's
compliance.
