# This is not the canonical case data — read before trusting anything here

**`input.md` in each subfolder here is real and current** — these are the
actual input documents `make_case_docs.py` generated (decision D49),
mechanically, from the already-frozen ground truth.

**`ground_truth.json` in each subfolder here is stale and not used by
anything.** The real, frozen, pre-registration ground truth — the one the
freeze commit (`225ed20b`, quoted in `results.md`) actually updated, and
the one `eval/score.py` actually reads (`CASES = os.path.join(ROOT,
"cases")`, i.e. `divergence/cases/`, not this folder) — lives at
`../../cases/<CASE>/ground_truth.json`.

**Found 21 August, disclosed in [`DECISION-D56.md`](../../DECISION-D56.md):**
these two `ground_truth.json` trees diverged after the real freeze commit
updated `divergence/cases/` but never touched this path. The only field
that actually differs is `citations_expected[]` (facts, `missing[]`,
`elements`, and `methods_expected` are byte-identical) — so no M1/M2/M4/M5
score in `results.md` was ever affected, since scoring has always read
from the real location. What *was* wrong was a claim written into
`results.md` itself, checked against this stale copy instead of the real
one — corrected in the same decision doc.

`divergence/cases/<CASE>/` now has both the real ground truth **and** a
copy of the same `input.md` found here, so it's a complete, canonical
location on its own. Commands elsewhere in this project's docs that point
at `step21drop/cases/<CASE>/input.md` still work correctly — only
`ground_truth.json` was ever the problem, and nothing reads it from here.
