# D69 — mutate.py: a deterministic, seeded defect-injection harness for node 5

**Date:** 23 August 2026

## What this is for, and how it differs from `mutation_corpus.py`

`mutation_corpus.py` (D61) already measures what the *deterministic*
gates catch — citation_matcher, scope_enforcer, gap_enforcer — against
seven mutation operators, and found two real, disclosed gaps
(`REGIME_CROSS_CITE`, `DEPENDENCY_DROP`) nothing currently catches.
`mutate.py` is a different, complementary instrument: this project's own
thesis (DOCUMENTATION.md §5, Silent Scope Omission) is that a real,
current, correctly-quoted citation can still be wrong in a way *nothing
but an adversarial LLM pass* catches. The thing worth stress-testing with
seeded, reproducible defects is node 5 itself, not the code around it.

Seven operators — CITE_SWAP, DATE_SHIFT, RATE_SUB, LABEL_MISMATCH,
ARITH_CORRUPT, SILENT_OMIT, OVERCLAIM — applied to each of the six real
cases' own saved, already-verified `regimes[]`/`valuation`
(`runs/21aug/*.json`, the same `CASE_FILES` mapping `mutation_corpus.py`
already uses) = 42 mutants, deterministic given `--seed` (default 1337).
Each mutant is fed to `node5_adversarial.check()` completely unchanged
from its real input contract — read that file first, matched its
signature exactly, never reshaped what it sends.

## A real bug caught before it shipped: hash randomization

First draft seeded each mutant's RNG with `random.Random((seed, case_id,
op_name))` — a tuple. Caught testing, not assumed correct: Python's
`random.seed()` converts `str`/`bytes`/`bytearray` deterministically (no
`PYTHONHASHSEED` involvement), but falls back to the built-in `hash()`
for anything else, including a tuple — and `hash()` of a `str` is salted
per-process by default. That would have made `--seed 1337` silently
produce a *different* 42 mutants on every separate run, exactly the
"deterministic" claim the task exists to satisfy, quietly false.
Fixed by seeding with a plain f-string (`f"{seed}-{case_id}-{op_name}"`)
instead. Verified, not just reasoned about: ran the same seed in two
genuinely separate Python processes and diffed the output —
byte-identical. Also ran all 42 mutants' construction (no live calls) in
one pass and confirmed zero exceptions and zero caller-data mutation
(every operator deep-copies; the original `regimes`/`valuation` compare
equal to a fresh reload after every operator runs).

## The "caught" measure is deliberately coarse, and says so

A mutant counts as caught if `attacked[]` contains *any* landed attack
(`survived: false`) — not specifically one that names the corrupted
field. Building a free-text matcher precise enough to credit only an
exact hit, across seven mechanically unrelated kinds of corruption (a
citation string, a date, a rupee figure, a vanished list entry), would
manufacture a precision this project has no evidence for — the same
overclaim this project exists to refuse everywhere else. Disclosed in
the module docstring, the LIMITATIONS block, and the printed report
itself, not just here.

## `--self-test`: two checks, zero API calls, both actually run

1. **Null mutant.** D1's own real, frozen `(regimes, missing, valuation,
   tax_year)`, deep-copied and handed through with no operator applied,
   must reproduce *exactly* the frozen record's own already-known attack
   result. Runs via `DIVERGENCE_REPLAY=1` against the cache
   `build_replay_cache.py` already seeded from this exact record (D63) —
   the identity transform produces byte-identical request content to
   what was cached, so this is a genuine cache hit, not a mock. Confirms
   this file's own deep-copy/JSON round-tripping introduces no
   incidental corruption before a single real operator is trusted.
2. **The three real scope-reach failures.** A regime shaped exactly the
   way this file's own operators shape one, retargeted onto each of the
   three provisions `scope_enforcer.py` (D59/D65) already proves it
   catches, must still be dropped by `enforce_scope()` — zero API calls,
   the deterministic gate, not node 5.

Both ran clean on the first real attempt: `2/2 as expected`. Wired into
CI (`Mutation harness self-test (mutate.py)`, next to the other gates)
since neither check needs a key.

## What is not claimed

**The actual 42-mutant sweep against a live node 5 has not been run.**
`python mutate.py` correctly fails the same clean way every other
key-needing script in this project does (`FAIL  FEATHERLESS_API_KEY is
not set...`) — confirmed directly, not assumed — because this
environment has no key, the same constraint every S/M item touching real
model behaviour has hit since D62. What this decision closes is
everything answerable without one: the harness is built, its operators
are confirmed to construct valid, non-mutating, JSON-serializable
mutants across all six real cases, its determinism claim is verified
across separate processes (not just reasoned about), and its two
key-free self-checks both pass for real. The overall mutation score,
with its Clopper-Pearson interval, is one `FEATHERLESS_API_KEY` away
from being a real number instead of an unmeasured claim.
