# You're in the actual submission

This folder is the real hackathon submission — everything else in this
repository (`design-process/`, `tests/`) is either historical or plumbing.
GitHub shows you this file automatically because it's sitting right here in
the folder you opened.

## Read this first

**[`START-HERE.md`](START-HERE.md)** — the mental model, every command to
run the pipeline end to end, and all 34 dated design decisions merged into
one chronological read. If you only open one file, open that one.

## The three files required by the track's submission rules

- **[`flowchart.png`](flowchart.png)** — the ML workflow diagram
- **[`SAMPLES.md`](SAMPLES.md)** — workflow vs. a single prompt, same test cases
- **[`DOCUMENTATION.md`](DOCUMENTATION.md)** — reasoning, mechanics, and data per node

## See the result without running anything

**[`index.html`](index.html)** — three real records side by side: twelve
defensible answers on the hard case, one honest answer each on two cases
that genuinely have no dispute. Open it directly in a browser.

## Reproducibility — where it actually comes from

**Not from a seed.** Featherless's own docs, `/v1/chat/completions`,
quoted verbatim: *"Random seed for generation. (Not reliable, as we use
multiple servers)."* `DIVERGENCE_SEED` is still sent through to the API
when set — real, recorded in every run's `_meta.llm.seed` — but nothing
here is built to depend on it doing anything. Two things this project's
reproducibility genuinely rests on instead:

- **The statutory corpus is frozen and hashed** — the same law text,
  provably, run to run (`corpus_hash.py`, `corpus/FREEZE-HASHES.json`,
  `DECISION-D60.md`).
- **The replay cache** — every real model response this project has
  produced is saved, keyed by exactly what was asked: node, system
  prompt, user content, model slot, temperature, max tokens
  (`replay_cache.py`, `DECISION-D63.md`, `DECISION-D72.md`).

Verify it directly — the second command needs no API key at all:

```
python run_pipeline.py --record-id D1-verify --tax-year "FY 2026-27" --text cases/D1/input.md --node5 --out runs/live.json
DIVERGENCE_REPLAY=1 python run_pipeline.py --record-id D1-verify --tax-year "FY 2026-27" --text cases/D1/input.md --node5 --out runs/replayed.json
```

`runs/live.json` and `runs/replayed.json` will be identical in every
field that carries the actual answer — `facts`, `missing`, `regimes`,
`valuation`, `manifest`, `attacked` — because the second run serves the
first run's own real response back verbatim, not a fresh sampling roll.
Two things legitimately differ, and only two: `generated_at` (stamped
fresh at write time either way) and `_meta.llm.replayed`
(`false` then `true`) — the explicit marker (D72) that makes it
impossible for a replayed run to be mistaken for a freshly-generated
one, even though `_meta.llm.by_node` now shows the *real* historical
token counts and model on a replay hit, not a zeroed stand-in.

## What the other ~75 files in this folder actually are

| Group | What's in it |
|---|---|
| `node1_extract.py` … `node7_disclosure.py`, `run_pipeline.py`, `llm_call.py`, etc. | The pipeline itself — one file per node, numbered to match `START-HERE.md`'s diagram |
| `corpus/tier-a/`, `corpus/verbatim/` | The actual statutory text, one provision per file — never the pipeline's own commentary |
| `cases/` | The six evaluation cases (C1–C5, D1) plus four hand-planted-defect variants used for the adversarial-checker ablation |
| `prompts/` | The five prompt files, one per model call |
| `runs/` | Saved, real output records from actual runs — nothing in here is a mockup |
| `eval/` | The scoring scripts (`score.py`, `normalize_runs.py`) |
| `prior-art/` | Two research documents checking whether this problem is already solved, and whether real people actually hit it |
| `DECISION-D41.md` … `DECISION-D74.md` | Thirty-four dated documents, each recording one real design decision or bug — merged into `START-HERE.md`, kept individually for full detail |
| `corpus_hash.py`, `corpus/FREEZE-HASHES.json` | Corpus integrity: a real SHA-256 per Tier A file, checked in CI so a corpus edit that isn't re-frozen deliberately fails loudly instead of shipping silently |
| `make_flowchart.py` | Regenerates `flowchart.png` from scratch (matplotlib, not a screenshot or a Mermaid export) — real model names and human-input markers baked into the image itself |
| `mutation_corpus.py`, `binom_ci.py` | Reports, not gates: 7 mutation operators measuring what the deterministic checks actually catch (D61); exact Clopper-Pearson intervals for this project's own small-n proportions |
| `injection_scanner.py`, `cases/ADV1-injection/`, `cases/ADV1/` | Prompt-injection defence for the one node that reads untrusted text — a CI-gated pattern scanner (11 phrase families plus hidden/non-printing character detection, D70) plus nonce spotlighting in `node1_extract.py`. `ADV1-injection` is the kitchen-sink case (every pattern family at once, D62); `ADV1` is a single surgical attack on `counterparty_verified`/confidence specifically (D71) — both verified offline (scanner + disclosure render), neither yet run against a live model. Findings stored at `_meta.input_integrity`, rendered as their own visible section on the disclosure page, not just folded into prose |
| `replay_cache.py`, `build_replay_cache.py`, `replay_cache/` | Reproduces D1's real run with `DIVERGENCE_REPLAY=1` and zero API calls — a CI gate on every push, in a runner with no key configured at all (D63). Cache key also covers model slot/temperature/max_tokens, not just node/system/user, and a replay hit restores the original call's real provenance (model, tokens, wall-clock, seed) with an explicit `replayed` marker, rather than a zeroed stand-in (D72) |
| `disagreement_gate.py` | Arm D: deterministic k-sample disagreement check on certainty/citation, self-tested against D1's real 3-seed data — and the file that found a real cross-Act citation bug already shipped in `scope_enforcer.py` (D65) |
| `CONTRASTIVE-EXEMPLARS.md` | The three real scope-reach failures as WRONG/RIGHT pairs, each sourced and quoted, not constructed — for Q&A now, and the literal content for a tested prompt change later |
| `CORPUS-PROVENANCE.md` | Why the corpus is hand-curated: six real sources checked directly, including a genuine surprise — India Code's own JSON API exists and works, but indexes catalogue metadata only, never the statute text itself |
| `capability_probe.py` | S8: is `response_format` a silent no-op on this provider? A prompt/flag conflict test isolates the flag's real effect from the model's own willingness to comply — classifier self-tested against five fixtures (D68); the live two-call probe itself needs an API key, so it's a manual tool, not a CI gate |
| `mutate.py` | A deterministic, seeded defect-injection harness for node 5 specifically (not the deterministic gates `mutation_corpus.py` already covers) — 7 operators × 6 real cases = 42 reproducible mutants; `--self-test`'s two checks run for real with zero API calls (D69), the real 42-mutant sweep needs a key |
| `run_all_cases.py` | Runs all six real cases through `run_pipeline.py` (one subprocess per case, unmodified) and builds `results.md`'s "Measured cost and tokens" table — real token counts and costs for all six today, real wall-clock the first time it runs with a working key (no case has ever produced one, D73) |
| `baseline_interface.py`, `baseline-interface.html`, `study/PROTOCOL.md` | The instrument for M7's human-subjects study — a single-number control page (reusing `output-interface.html`'s own CSS so the only real variable is the uncertainty display) plus a pre-registered protocol: payoff function, 8-trial counterbalanced design, the verbatim SURE decisional-conflict screener, and an empty results template (D74). Running the actual study with real participants is the user's own task |
| `results.md`, `ITERATION-STORY.md`, `architecture.md`, `GAZETTE-FINDINGS.md` | The deeper reading — metrics including where the pipeline loses, seven curated moments of what broke, node-by-node rationale, and what the actual gazette text says |
| `step19drop/`, `step21drop/`, `step22drop/` | Earlier project states, kept for the record as the project evolved — not the current submission, but not deleted either |
| `output-interface.html`, `demo-C1.html`, `demo-C2.html` | The generated disclosure pages `index.html` links to |

Full explanation of every one of these, in depth: the root
[`README.md`](../README.md)'s "How this repository is laid out" section.
