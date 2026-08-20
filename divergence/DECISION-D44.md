# D44 — Featherless only, a clean repo, and one honest pre-registration hash

**Date:** 20 August 2026
**Builds on D42 (how the provider is chosen) and D43 (which models).**

Three decisions taken together, because they are one question: *what does a
judge see when they clone this repo, and is every claim in it true?*

---

## 1. Featherless only. The Anthropic fallback is removed.

**Was:** `provider_name()` returned whichever key it found — Featherless first,
Anthropic second.

**Now:** Featherless, or an error. Anthropic requires typing
`DIVERGENCE_PROVIDER=anthropic` on purpose.

### Why the fallback was the bug

Picture a teammate on a fresh terminal. `FEATHERLESS_API_KEY` isn't set;
`ANTHROPIC_API_KEY` is, from something else. They run the pipeline. It works.
It produces a schema-valid record. That record goes in the results table under
"open models."

Nothing crashes. Nothing looks wrong. The `_meta.llm` block says `anthropic`,
truthfully — but only to someone who opens the file and reads it.

**That is Class 3.** A confident, well-formed, correct-looking output resting
on ground that quietly moved. It is the exact failure this project exists to
detect, reproduced inside the harness that measures it. D42 added the *record*
of which provider ran; D44 removes the *opportunity* to run the wrong one.

The rule the project keeps re-learning: recording a hazard is not the same as
removing it. `citable: false` didn't stop uncitable files being relied on. A
`known_limitation` field didn't stop a stale rule being cited. Writing D35 in a
decision log didn't stop the code defaulting to Claude.

### Also changed: a 403 is no longer retried

D43's testing hit `403 model_gated_needs_oauth` three times per model, because
the retry loop treated every exception as transient. A licence gate is not
transient. Retries are now limited to `{408, 409, 425, 429, 500, 502, 503, 504}`;
a gated model raises `GatedModelError` immediately with the fix in the message.
Nine wasted calls in D43's log become three.

---

## 2. The repo ships the corpus that is live, and nothing that shadows it

The first commit staged **212 files**, including:

- eight `.zip` archives of folders that are also present unzipped
- `divergence/_old_corpus_backup/` — containing `IT-RULE-115.md`,
  `IT-RULE-57.md`, `IT-RULE-206.md`, `IT-RULE-207.md`
- `divergence/drop5featherless/` — a second copy of `llm_call.py`,
  `check_llm.py`, `.gitignore`, `requirements.txt`
- root-level `IT-RULE-57.md`, `IT-RULE-57 (1).md`, `IT-RULE-57 (2).md`,
  `IT-RULE-115.md`, `IT-RULE-207.md`, and `(1)`-suffixed copies of a dozen
  step documents

### Why this is not cosmetic

`_old_corpus_backup/` holds the **retired shadowing files** — the ones that
made `citation_matcher.py` score 15/15 for the wrong reason, because
`IT-RULE-57.md` sorted before `ITR2026-RULE-57.md` and won. That bug is the
best story in `iteration-log.md`.

Shipping those files back into the repo means a judge who clones it can find
`IT-RULE-115.md` — a rule superseded on 1 April 2026 — sitting next to the
live corpus, in a project whose entire claim is that it detects exactly this.
It also means the next person to run `split_corpus.py` or a glob over the tree
can silently re-introduce the shadowing.

**Decision:** `_archive/` (gitignored) holds anything retired. Zips are not
committed — the folder is the artifact, the zip is a delivery format. One copy
of each file, at the path the code imports it from.

`cleanup_repo.py` does this as a **dry run by default**, and moves rather than
deletes. Nothing is destroyed.

---

## 3. One pre-registration hash, and it has to mean what it says

Commit `a267f19` carries the message *"corpus, pipeline, ground truth frozen
pre-run."*

**The ground truth in it is not finished.** `citations_expected[]` is unfilled
across the case folders. So one of two things is true, and only one of them is
honest:

| | |
|---|---|
| **(a)** `a267f19` is the freeze — then ground truth may never be edited again, and the eval scores against incomplete expectations | ❌ |
| **(b)** finish the ground truth, commit **that** as the freeze, and quote **that** hash | ✅ |

We take (b). It is also the version that survives the obvious question: *"your
commit says ground truth was frozen — did you edit it after?"*

**The freeze commit must be made before any scored run, and after
`citations_expected[]` is filled.** Since nothing has been pushed yet and the
history is two commits deep, `.git` is re-initialised from scratch rather than
patched — so the pre-registration hash is the hash of a clean tree with no
retired corpus in its history.

`results.md` states the hash, the UTC timestamp of the commit, and the UTC
timestamp of the first scored run, in that order.

---

## What this costs

The Anthropic path is now one env var away rather than automatic — a small
inconvenience if we ever want to re-meter the cost estimate, and the right
trade for not being able to contaminate a results table by accident.

Re-initialising git discards two unpushed commits. No work is lost; the
timestamps in those commits are not evidence of anything, because they predate
the finished ground truth they claimed to freeze.
