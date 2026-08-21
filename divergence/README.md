# You're in the actual submission

This folder is the real hackathon submission — everything else in this
repository (`design-process/`, `tests/`) is either historical or plumbing.
GitHub shows you this file automatically because it's sitting right here in
the folder you opened.

## Read this first

**[`START-HERE.md`](START-HERE.md)** — the mental model, every command to
run the pipeline end to end, and all 16 dated design decisions merged into
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
| `DECISION-D42.md` … `DECISION-D57.md` | Sixteen dated documents, each recording one real design decision or bug — merged into `START-HERE.md`, kept individually for full detail |
| `results.md`, `ITERATION-STORY.md`, `architecture.md`, `GAZETTE-FINDINGS.md` | The deeper reading — metrics including where the pipeline loses, seven curated moments of what broke, node-by-node rationale, and what the actual gazette text says |
| `step19drop/`, `step21drop/`, `step22drop/` | Earlier project states, kept for the record as the project evolved — not the current submission, but not deleted either |
| `output-interface.html`, `demo-C1.html`, `demo-C2.html` | The generated disclosure pages `index.html` links to |

Full explanation of every one of these, in depth: the root
[`README.md`](../README.md)'s "How this repository is laid out" section.
