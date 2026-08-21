# D60 — corpus integrity hashing: the "hashed" claim, made real

**Date:** 21 August 2026
**A deferred "product gap" item, greenlit by name in a relayed planning document (`STATUS-IDEAS-PLAN.md`'s Idea 5), built the same way every other deterministic gate in this project is: standard library only, self-verifying, wired into CI.**

## What was actually there before this

`corpus/MANIFEST.md` has said **"COMPLETE, hashed"** next to a few Tier A
files since 19 August. Nothing behind that word was ever true in a
checkable sense: no hash was recorded anywhere, nothing compared it to
anything, and the word appeared on 3 of 17 rows for no principled reason —
an artifact of whoever wrote that row that day, not a real distinction
between which files had actually been checked. `schema.json`'s
`corpus_frozen_at` field (C34) asserts a freeze happened. Nothing made
that assertion checkable independent of trusting the timestamp.

## What was built

**`corpus_hash.py`** — deterministic, no model, no API, same shape as
`gap_enforcer.py` and `scope_enforcer.py`:

- `--freeze` computes SHA-256 of every Tier A file's *body* (front matter
  stripped — the same text `citation_matcher.py` itself reads) and writes
  `corpus/FREEZE-HASHES.json`. Never run automatically; a hash file that
  updates itself on every commit verifies nothing. Re-freezing after a
  real, deliberate corpus edit is the one legitimate reason to run it
  again, and it should be its own disclosed commit.
- `--verify` recomputes current hashes and compares against the frozen
  file. Fails (exit 1) on drift, on a file present at freeze time now
  missing, or on a new Tier A file not yet covered by the freeze.

**Tested both directions, not just the happy path**: froze all 17 files,
confirmed `--verify` passes clean; then appended a line to
`IT-115BBH.md`, confirmed `--verify` correctly reports `HASH DRIFT` and
exits 1; restored the file byte-for-byte and confirmed `git status` shows
no diff and `--verify` passes again.

**`run_pipeline.py`'s `build_manifest()`** now stamps each
`manifest.provisions_checked[]` entry with `content_hash` — the actual
hash of the provision text this specific record was checked against, not
just today's live corpus. Verified end to end: ran `build_manifest()`
against the real frozen `D1_final_seed2.json` record's regimes, confirmed
every entry got a real hash, confirmed the full record still validates
against `schema.json` with the field present (it's additive — `citation`
never had `additionalProperties: false`, so this required no breaking
schema change, only a documented, dated addition to the `$def`).

**`schema.json`** — `content_hash` added to the `citation` `$def`,
`["string", "null"]`, described as manifest-only (never populated on
`regimes[].citation`, which is a resolver's live output, not a corpus
integrity check).

**`corpus/MANIFEST.md`** — the misleading per-row "hashed" annotations (on
3 of 17 rows, implying a distinction that was never real) removed, replaced
with one clear statement at the top: all 17 files are covered, with a
pointer to `FREEZE-HASHES.json` and the new field.

**CI** — `corpus_hash.py --verify` added as a new gate, alongside
`citation_matcher.py`, `gap_enforcer.py`, `scope_enforcer.py`, and
`a11y_check.py --all`.

## What this proves, and what it doesn't

**Proves**: the corpus text a citation was checked against, at the moment
it was checked, has not silently changed since. A corpus edit that isn't
followed by a deliberate `--freeze` now fails CI, visibly, rather than
silently shipping a record whose citations were checked against text that
no longer exists.

**Does not prove**: that the corpus is *correct* — a hash confirms
unchanged, not accurate. `corpus_hash.py`'s own module docstring says so.
Whether Rule 57's text is transcribed correctly from the gazette is a
different question, answered elsewhere (`gate0_check.py`'s duplicate/
shadow checks, the front-matter `source_url` fields, and ultimately a
human checking against the primary source) — this closes the gap between
what the manifest *claims* ("hashed") and what it can actually *show*, no
more than that.
