# CLAUDE.md — rules for any coding agent in this repo

## Purpose
Working rules for any coding agent (Claude Code or similar) in this repository, every session.
If a request conflicts with a rule here, stop and ask the owner.

## Repo map
- Root: README.md (overview), SECURITY.md, design-process/ (early planning notes),
  tests/ (pytest), .github/workflows/ (CI).
- divergence/: the code package and its docs. Start with divergence/START-HERE.md.
  - Decision records: divergence/DECISION-D41.md … DECISION-D78.md (38 files).
  - Frozen: divergence/corpus/, divergence/replay_cache/, divergence/runs/.
- Reports go IN the repo as logs/P##_report.md (public: no keys, no personal data). Owner decision PD-03, 13 Nov 2026.

## Forbidden
- Commit or push. The owner commits and pushes.
- Auto / auto-accept mode. Every write waits for the owner's approval.
- Editing frozen items without a new decision doc: divergence/corpus/, the replay cache
  (divergence/replay_cache/), anything under divergence/runs/, the pre-registration docs,
  and existing DECISION-D*.md files (report their errors; don't edit them).
- Live runs that write into the frozen replay cache. Redirect with DIVERGENCE_REPLAY_CACHE_DIR
  (added after commit 3e2949e; confirm replay_cache.py reads it before relying on it).
- Sending temperature 0 (D45/D52). Scored runs use the model's own default temperature only.
- Printing or typing API keys: not in commands, files, chat, logs or screenshots.
  Check a key only with [bool]$env:FEATHERLESS_API_KEY.
- meta-llama/* models: they return 403 on this account (D43).
- Fallback providers (D44). Featherless only; never switch provider silently.
- LLM-as-judge scoring. Scores come from deterministic code.
- Deleting or overwriting any file without the owner's explicit yes for that file, by name.

## PLAN GATE
PLAN GATE (each part): Read-only checks first. Then print your PLAN for this part: files to
create/modify (paths), exact commands, number of live/paid calls, expected outputs, risks.
STOP and wait for the owner's "APPROVED" message. Do not edit, write, change git state or make
any live call before that. If the owner approves with changes, follow them exactly.

## PLAIN SUMMARY
Start EVERY report (each part, and each plan) with this PLAIN SUMMARY, in simple words,
before any tables or logs:
- WHAT HAPPENED: 2–4 short lines.
- WHAT IT MEANS: why it matters for the project / resume.
- PROBLEMS: anything failed, surprising or risky (or "none").
- DECISION NEEDED: the choice the owner must make, with 2–3 options and your pick
  (or "none, ready for next part").
- NEXT MESSAGE: the exact text the owner should send to continue.

## SELF-AUDIT (end of every task; write "none" if empty)
1. Steps asked vs done
2. Decisions you made or changed, and why
3. Implementation (files, functions, exact commands)
4. Checks (each command with its real output, pass/fail)
5. Frozen items (corpus hash verify, field-level replay result, sealed test set untouched)
6. Assumed or not checked
7. Errors and retries
8. Safety (no commit/push, no keys, no unapproved deletes or overwrites)
9. git status + git diff --stat (real output)
10. Risks for the next steps

## Checks before any hand-off (key unset; all must pass)
- Repo root: pytest -p no:cacheprovider
- divergence/: python corpus_hash.py --verify
- divergence/: python gate0_check.py
- divergence/: the CI replay check with DIVERGENCE_REPLAY=1 and --out pointed OUTSIDE runs/;
  compare facts, missing and attacked field by field to runs/21aug/D1_final_seed2*.json
  (field-level equality, not byte equality)
- Repo root, flake8 strict: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

## Facts
- core.autocrlf=true: checkout changes line endings, so compare files by hash, never by size.
- CI runs Python 3.10.
- Featherless's seed is not reliable (its docs: "Not reliable, as we use multiple servers").
  Reproducibility = replay cache + hashed corpus, never the seed.

## Truth rules
- Every number is computed by code (D38) and reported with its definition, n, arm, seeds
  and interval.
- Never tune prompts, code or thresholds toward a target number.
- Average seeds/repetitions; never pick the best one; report unstable results as unstable.
- Tag claims: REPO (in a committed file), LOCAL (seen only on this machine),
  INFERENCE (reasoned, not observed), UNVERIFIED (not checked).
