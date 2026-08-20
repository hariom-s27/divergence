# D46 — schema.json changed three times after the ground-truth freeze, disclosed

**Date:** 20 August 2026
**Directly about pre-registration integrity. Read this next to D44 §3, which
established the freeze commit `225ed20b` in the first place.**

## The fact, stated plainly

`schema.json` carries the line *"LOCKED 6 August 2026... Do not add fields
without recording why."* Commit `225ed20b` is the pre-registration point —
ground truth frozen, quoted by hash, before any scored run. The very next
commit, `1b1e9d3` (Step 27/29/31, same day), amends `schema.json` three
times:

| # | Change | Why |
|---|---|---|
| 1 | `date_choice.chosen`: `"string"` → `["string", "null"]` | `node3_valuation.py` had always documented that it sets this field `null` on purpose (R99 — an unresolved date choice) — the schema had simply never been checked against a real record before D1's first end-to-end run, so nobody had noticed it rejected its own documented output |
| 2 | `extracted_field.value`: added `"boolean"` | Every case's `ground_truth.json` already uses boolean facts (`"bank_involved": {"value": false}`); the schema had just never allowed one, same story — never exercised, not deliberately excluded |
| 3 | Added the whole `_meta` object | New capability, not a bug fix — `llm_call.provenance()` needed somewhere to land so `results.md` could quote which models actually produced a record instead of relying on memory (D42) |

## Why this gets said out loud instead of left for someone to find

A project whose entire thesis is *"a confident answer resting on ground that
quietly moved is worse than no answer, because you cannot tell it apart from
a real one"* cannot have an unexamined, undisclosed change to its own output
contract sitting between its pre-registration commit and its results. Not
because the changes were wrong — they were correct, and two of them fixed
real defects the schema had carried since 6 August without anyone noticing.
**Because finding it yourself and saying so is the entire claim of this
project, applied to itself.** Found unsaid, by a judge diffing the freeze
against `HEAD`, it reads as exactly the failure class this project exists to
catch, happening in the one place it would be most damaging to be caught
happening.

## Why none of the three amendments touch the actual pre-registration

The freeze commit's load-bearing content is `cases/*/ground_truth.json` —
`citations_expected[]`, `missing[]`, `elements`, `methods_expected`. None of
that changed after `225ed20b`. All three schema amendments are to the
**output contract** (the shape a disclosure record must have), not to what
counts as a correct answer. Changes #1 and #2 make the schema accept output
it was always supposed to accept and had never been tested against; change
#3 adds a field for provenance data that did not exist at freeze time and
whose absence or presence changes nothing about how any of the five metrics
score a record.

**The distinction that matters:** editing `ground_truth.json` after seeing a
result would corrupt the pre-registration. Fixing `schema.json` — the
contract every arm's output is checked against equally — to match its own
already-documented behaviour does not, provided (as here) it happened before
any scored comparison existed, was found by running real data through it
rather than by looking for a result that needed a favourable rule change,
and is disclosed rather than absorbed silently into the next commit.

## What to say about it

> "Our schema was locked 6 August. Running real data through it for the
> first time on 20 August found three places where the lock had never
> actually been tested — two rejected the pipeline's own documented output,
> one lacked a field for information that did not exist yet. All three are
> in commit `1b1e9d3`, all three are disclosed here and in `results.md`, and
> none of them touch the ground truth the evaluation is scored against."

That is a stronger answer than a schema that happened to be right the first
time, because nobody can tell the difference between "correct by design" and
"never actually tested" from the outside — except by asking whether the team
would have told you if it were the second one.
