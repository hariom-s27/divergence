# You're in the actual submission

This folder is the real hackathon submission — everything else in this
repository (`design-process/`, `tests/`) is either historical or plumbing.
GitHub shows you this file automatically because it's sitting right here in
the folder you opened.

## Read this first

**[`START-HERE.md`](START-HERE.md)** — the mental model, every command to
run the pipeline end to end, and all 31 dated design decisions merged into
one chronological read. If you only open one file, open that one.

## The three files required by the track's submission rules

- **[`flowchart.png`](flowchart.png)** — the ML workflow diagram
- **[`SAMPLES.md`](SAMPLES.md)** — workflow vs. a single prompt, same test cases
- **[`DOCUMENTATION.md`](DOCUMENTATION.md)** — reasoning, mechanics, and data per node

## See the result without running anything

**[`index.html`](index.html)** — three real records side by side: twelve
defensible answers on the hard case, one honest answer each on two cases
that genuinely have no dispute. Open it directly in a browser.

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
| `DECISION-D41.md` … `DECISION-D71.md` | Thirty-one dated documents, each recording one real design decision or bug — merged into `START-HERE.md`, kept individually for full detail |
| `corpus_hash.py`, `corpus/FREEZE-HASHES.json` | Corpus integrity: a real SHA-256 per Tier A file, checked in CI so a corpus edit that isn't re-frozen deliberately fails loudly instead of shipping silently |
| `make_flowchart.py` | Regenerates `flowchart.png` from scratch (matplotlib, not a screenshot or a Mermaid export) — real model names and human-input markers baked into the image itself |
| `mutation_corpus.py`, `binom_ci.py` | Reports, not gates: 7 mutation operators measuring what the deterministic checks actually catch (D61); exact Clopper-Pearson intervals for this project's own small-n proportions |
| `injection_scanner.py`, `cases/ADV1-injection/`, `cases/ADV1/` | Prompt-injection defence for the one node that reads untrusted text — a CI-gated pattern scanner (11 phrase families plus hidden/non-printing character detection, D70) plus nonce spotlighting in `node1_extract.py`. `ADV1-injection` is the kitchen-sink case (every pattern family at once, D62); `ADV1` is a single surgical attack on `counterparty_verified`/confidence specifically (D71) — both verified offline (scanner + disclosure render), neither yet run against a live model. Findings stored at `_meta.input_integrity`, rendered as their own visible section on the disclosure page, not just folded into prose |
| `replay_cache.py`, `build_replay_cache.py`, `replay_cache/` | Reproduces D1's real run with `DIVERGENCE_REPLAY=1` and zero API calls — a CI gate on every push, in a runner with no key configured at all (D63) |
| `disagreement_gate.py` | Arm D: deterministic k-sample disagreement check on certainty/citation, self-tested against D1's real 3-seed data — and the file that found a real cross-Act citation bug already shipped in `scope_enforcer.py` (D65) |
| `CONTRASTIVE-EXEMPLARS.md` | The three real scope-reach failures as WRONG/RIGHT pairs, each sourced and quoted, not constructed — for Q&A now, and the literal content for a tested prompt change later |
| `CORPUS-PROVENANCE.md` | Why the corpus is hand-curated: six real sources checked directly, including a genuine surprise — India Code's own JSON API exists and works, but indexes catalogue metadata only, never the statute text itself |
| `capability_probe.py` | S8: is `response_format` a silent no-op on this provider? A prompt/flag conflict test isolates the flag's real effect from the model's own willingness to comply — classifier self-tested against five fixtures (D68); the live two-call probe itself needs an API key, so it's a manual tool, not a CI gate |
| `mutate.py` | A deterministic, seeded defect-injection harness for node 5 specifically (not the deterministic gates `mutation_corpus.py` already covers) — 7 operators × 6 real cases = 42 reproducible mutants; `--self-test`'s two checks run for real with zero API calls (D69), the real 42-mutant sweep needs a key |
| `results.md`, `ITERATION-STORY.md`, `architecture.md`, `GAZETTE-FINDINGS.md` | The deeper reading — metrics including where the pipeline loses, seven curated moments of what broke, node-by-node rationale, and what the actual gazette text says |
| `step19drop/`, `step21drop/`, `step22drop/` | Earlier project states, kept for the record as the project evolved — not the current submission, but not deleted either |
| `output-interface.html`, `demo-C1.html`, `demo-C2.html` | The generated disclosure pages `index.html` links to |

Full explanation of every one of these, in depth: the root
[`README.md`](../README.md)'s "How this repository is laid out" section.
