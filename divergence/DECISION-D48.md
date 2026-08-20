# D48 — two findings from running Step 1 to completion: a scorer bug and a case-file gap

**Date:** 20 August 2026
**Found while running nodes 3/4 for the remaining cases (C1, C3, C4, C5) to close
out Step 1. Read next to D45–D47, same family of finding.**

---

## Finding 1 — `eval/score.py`'s M5 silently scored "0.0%, perfect" instead of "not measured"

### The bug

`m5_false_abstention(run, gt)` computed `got = run.get("elements", {})`, then
checked `wrong = [k for k in settled if got.get(k) == "open"]`. When a run
never produces an `elements` key at all — true of every record any node in
this pipeline has ever written, because no prompt asks for the `elements{}`
shape M5 needs — `got` is `{}`, `got.get(k)` is `None` for every settled key,
`wrong` is always `[]`, and the function returns `0.0` — not `None`.

**A metric whose entire purpose is catching false confidence was itself
reporting a confident, wrong answer whenever it had no data to work with.**
`results.md` already said, in prose, "M5 is still undefined on every row." The
code did not agree with the prose: run `eval/normalize_runs.py --report`
before this fix and every row shows `M5 false abst. 0.0%` — a perfect score,
for a metric this project's own materials call "the metric that earns trust."
Anyone pasting that table without reading the prose caveat first would have
published a fabricated finding.

### The fix

`m5_false_abstention` now returns `(None, [])` immediately when
`run.get("elements")` is falsy (absent or empty), before ever comparing
against ground truth. `fmt(None)` already rendered as `—`; no other change
needed. Verified: `eval/normalize_runs.py --report` post-fix shows `—` for M5
on all 18 rows, matching what the prose has said all along. No test in
`tests/` exercises `score.py` (checked: `grep -rl score.py tests/` empty), so
this was caught by re-running the report after Step 1's new records landed,
not by a regression suite — a gap worth naming, not papering over.

`eval/score.py` was deliberately left untouched when `normalize_runs.py` was
built (its own docstring says as much, citing the file's history of
over-correction bugs). This is not a redesign — it is a two-line, narrowly
scoped fix to a function that was producing an actively false signal, and it
is disclosed here rather than folded into a commit silently.

---

## Finding 2 — five of six case files never got the input document their own TO-DO asked for

### The fact, stated plainly

Every `step21drop/cases/*/case.md` carries the same boilerplate:

> "Produce the actual input document(s) for this case in this folder
> (`invoice.pdf` / `payment.png` / `payment.txt`)... Fill `ground_truth.json`.
> **Before any model runs.**"

Checked directly: for C1, C2, C4, C5, `ground_truth.json`'s `facts` block
contains a specific counterparty name and invoice number
(`"Meridian Analytics Pvt Ltd"` / `"2026-101"` for C1,
`"Cascade Data Inc"` / `"2026-104"` for C2, and so on) that **do not appear
anywhere in that case's `case.md`.** No document was ever produced to
contain them — the one-paragraph `case.md` summary is the only input text
any arm has ever been given, and these two fields were invented directly
into the ground truth without a source document to extract them from. No
extractor, baseline or pipeline, could ever score correctly on them.

**C3 is the same problem, more severely.** Its `case.md` body reads "Same
shape as D1 but settled 14:30 IST on Tuesday 23 June 2026" — it never
restates the amount or asset at all, only in the H1 title (`2,000 USDC`),
which `node1_extract.py`'s content builder does not treat as extractable
body text. Running the pipeline on C3 tonight produced **zero extracted
fields** and, cascading from that, node 2 reporting 7 gaps — not because the
gap detector malfunctioned, but because the input it was actually given
contains almost nothing to detect facts *from*. C3's own case file states
its purpose is the opposite: *"the date choice is closed... the system
should report FEWER gaps here than D1. If it reports the same number, it is
not reading the facts."* Tonight it reported more, for a reason that has
nothing to do with whether the pipeline reads facts well.

**D1 is the one case where this was done properly** — its `case.md` is a
full paragraph naming the counterparty (Northbay Systems LLC) and invoice
number (2026-114) in prose, which is why D1 is also the only case whose M1
numbers (9.1%–18.2%) reflect a real attempt at those fields rather than an
unreachable target.

### Why this is not being fixed tonight

`ground_truth.json` was frozen at commit `225ed20b` specifically so it could
not be edited after seeing a result — and it has already been seen (tonight's
run). Editing `case.md` now — after already knowing C3 extracts zero fields
against it — has exactly the same defect even though `case.md` is nominally
the "input" side, not the "answer" side: whoever writes the new sentence
would be writing it with tonight's failure already in mind, which is the
precise harm the freeze exists to prevent. **The correct fix is to produce
real input documents for C1, C2, C3, C4, C5 and re-freeze a new
pre-registration for those cases specifically** — a real, multi-hour,
disclosed redo, not a same-night patch. That is a scope and scheduling
decision, not a code fix, so it is being surfaced here rather than taken
unilaterally under the Step 1/4/5/6 timeline.

### What this means for the table in `results.md` right now

- M1 (extraction accuracy) was already flagged as unfairly low due to
  field-name mismatch (D45). This finding is upstream and larger: for four
  of five non-D1 cases, part of the ground truth is **structurally
  unreachable** from the given input, independent of field naming. Fixing
  field names (Step 2, as originally scoped) will not move C1/C2/C4/C5's M1
  much, because the missing facts were never written into the input at all.
- **C3's entire arm-C row tonight should be read as diagnostic, not
  measurement.** Its M2 "7 gaps / recall 50% / precision 14.3%" numbers
  reflect an almost-empty input, not the gap detector's judgment. It is left
  in the table below with this note attached, not removed silently.
- C1, C2, C4, C5's M1 numbers are real but capped below 100% by
  construction — a perfect extractor could not score higher than the
  fraction of `facts` keys that are actually present in `case.md`, and that
  ceiling is case-specific and currently uncalculated. It is not one of the
  five metrics; it is a caveat on how to read M1 until the case files are
  redone.

### What to say about it

> "Wiring nodes 3 and 4 into the rest of the eval set found that five of our
> six case files never got the standalone input document their own checklist
> asked for — ground truth for those cases includes details, like a
> counterparty name, that exist nowhere any extractor was shown. One case,
> C3, is missing even its core facts from the body text. We are not patching
> the case files tonight, because editing them now, after seeing that C3
> fails, would corrupt the same pre-registration discipline we're relying on
> everywhere else. The real fix is producing actual input documents and
> re-freezing those cases properly, which we're scoping as separate,
> disclosed work rather than doing quietly under tonight's deadline."
