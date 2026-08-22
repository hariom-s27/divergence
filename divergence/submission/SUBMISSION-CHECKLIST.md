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
- **Size:** 7,406 bytes
- **Last-modified commit:** `4e95f41`, 2026-08-21 — "Ship-plan response:
  strengthen SAMPLES.md with verified metrics, close remaining named
  sub-criteria, add the three-record comparison page"
- **Phone-readable PDF companion:** [`SAMPLES.pdf`](SAMPLES.pdf) (154,484
  bytes) — same content, exported via `build_pdfs.py` so a judge doesn't
  have to render Markdown.
- Every quote in it is copied verbatim from a real, saved run
  (`runs/21aug/D1_armA.json`, `D1_armB.json`, `D1_final_seed2.json`) —
  the document *is* the comparison, not a summary of one.

## 3. Detailed documentation of the reasoning behind each node, how it works, and any other necessary data

- **File:** [`divergence/DOCUMENTATION.md`](../DOCUMENTATION.md)
- **Size:** 26,076 bytes
- **Last-modified commit:** `a0c25f0`, 2026-08-23 — "S8: capability probe
  -- is response_format a silent no-op?" (a decision-count bump; the
  per-node content itself was last substantively touched adding ⚙ E)
- **Phone-readable PDF companion:** [`DOCUMENTATION.pdf`](DOCUMENTATION.pdf)
  (290,626 bytes) — same content, 11 pages, tables intact.
- Organized exactly as the track's rule text asks: per node, why it
  exists, how it works, the data it needs — plus the model registry the
  track separately asks the flowchart to name.

## Regenerating the two PDFs

```
python divergence/submission/build_pdfs.py
```

Pulls current `SAMPLES.md`/`DOCUMENTATION.md` straight from source —
re-run it any time either file changes before the deadline, so the PDFs
never quietly go stale next to the Markdown they're exported from.
