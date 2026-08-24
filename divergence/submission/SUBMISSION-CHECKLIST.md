# M1 — submission checklist

The ReverieHacks 2026 ML Prompt Engineering track requires exactly three
artifacts. This lists each one, the real file in this repo that satisfies
it, and where it stood as of this check — nothing added beyond those
three; no other requirement is invented here.

## 1. A PNG of the ML workflow flowchart

- **File:** [`divergence/flowchart.png`](../flowchart.png)
- **Size:** 782,612 bytes
- **Last-modified commit:** `12223c1`, 2026-08-21 — "Add scope_enforcer.py
  (⚙ E): deterministic code for 3 real scope-reach bugs Node 5 used to
  catch alone"
- Regenerated from scratch by `make_flowchart.py` (matplotlib, not a
  screenshot or a Mermaid export) — real model names and both human-input
  points baked into the image itself, not a caption.

## 2. A video/document showing the workflow used on sample test cases, vs. a single-prompt approach on the same test cases

- **File:** [`divergence/SAMPLES.md`](../SAMPLES.md)
- **Size:** 10,916 bytes (updated 2026-08-24, submission-finalization pass —
  was 7,406 bytes as of the `4e95f41` check; re-measured directly, not
  carried over)
- **Phone-readable PDF companion:** [`SAMPLES.pdf`](SAMPLES.pdf) (179,993
  bytes, regenerated 2026-08-24 with `build_pdfs.py`'s link-rewriting pass
  — every relative link now resolves to an absolute GitHub URL in the PDF,
  see `build_pdfs.py`'s own docstring) — same content, exported so a judge
  doesn't have to render Markdown.
- Every quote in it is copied verbatim from a real, saved run
  (`runs/21aug/D1_armA.json`, `D1_armB.json`, `D1_final_seed2.json`) —
  the document *is* the comparison, not a summary of one.

## 3. Detailed documentation of the reasoning behind each node, how it works, and any other necessary data

- **File:** [`divergence/DOCUMENTATION.md`](../DOCUMENTATION.md)
- **Size:** 27,679 bytes (updated 2026-08-24, submission-finalization pass —
  was 26,076 bytes as of the `a0c25f0` check; re-measured directly, not
  carried over)
- **Phone-readable PDF companion:** [`DOCUMENTATION.pdf`](DOCUMENTATION.pdf)
  (302,084 bytes, regenerated 2026-08-24, same link-rewriting pass as
  `SAMPLES.pdf` above) — same content, tables intact.
- Organized exactly as the track's rule text asks: per node, why it
  exists, how it works, the data it needs — plus the model registry the
  track separately asks the flowchart to name.

**A note on "Last-modified commit" fields, removed from both rows above
rather than left stale a second time:** naming a specific commit hash
here means it goes stale the instant either file is edited again without
this checklist being updated in the same commit — which is exactly what
happened between the `4e95f41`/`a0c25f0` checks and this one. Sizes are
re-measured directly (`wc -c`) each time this file is touched instead;
`git log -1 -- divergence/SAMPLES.md` (or `DOCUMENTATION.md`) gives the
real current answer to "when was this last touched" without this file
needing to track it separately.

## Regenerating the two PDFs

```
python divergence/submission/build_pdfs.py
```

Pulls current `SAMPLES.md`/`DOCUMENTATION.md` straight from source —
re-run it any time either file changes before the deadline, so the PDFs
never quietly go stale next to the Markdown they're exported from.
