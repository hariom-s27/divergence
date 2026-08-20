#!/usr/bin/env python3
"""
normalize_runs.py  --  adapter between real run output and eval/score.py.

score.py expects a normalised run file (its own docstring):
{
  "case_id": "D1", "arm": "A", "model": "large", "seed": 1,
  "facts": {...}, "missing": [...], "methods": [...],
  "elements": {...}, "citations": [...], "raw": "..."
}
Neither producer we actually have writes that shape:
  run_pipeline.py  -> a schema.json-conforming disclosure record
                      (record_id, facts, missing, valuation.methods[],
                       regimes[].citation, no top-level "elements" or "arm")
  run_arms.py      -> {"arm", "case", "record": <same disclosure-record
                       shape, or null if the model never produced JSON>,
                       "_meta": {...}}

This is the missing conversion. score.py is untouched -- its own history
(v1 under-credited arm A, v1.5 over-corrected to 100% recall) is exactly why
this is a separate, additive file rather than a rewrite.

    python eval/normalize_runs.py            # convert every real run
    python eval/normalize_runs.py --report   # convert, then run score.py
                                              # against the result and print
                                              # both the detail view and the
                                              # --table view

Writes to runs/normalized/ -- NOT runs/*.json directly, so score.py's own
`--all` (which globs runs/*.json) never picks up a normalized file as if it
were a second, different real run.

WHAT THIS CANNOT INVENT
  "elements" -- {classification, recognition_date, official_date,
  valuation_method, proxy, gst_export: "settled"|"open"} -- is a
  ground-truth-only concept today. No prompt (01-05, baseline-prompt.md,
  arm-b-cot.md) asks any arm to report it in a scoreable shape, so it comes
  out empty for every run, every arm, without exception. That is not an
  adapter bug: M5 (false abstention -- "the metric that earns trust",
  evaluation-design.md) genuinely cannot be scored from any output that
  exists today. Reported as a finding, not silently worked around.
"""

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, "runs")
OUT_DIR = os.path.join(RUNS, "normalized")

sys.path.insert(0, HERE)


def _methods(record):
    return [m.get("label", str(m)) for m in (record.get("valuation") or {}).get("methods", [])]


def _citations(record):
    return [r["citation"] for r in record.get("regimes", []) if isinstance(r, dict) and r.get("citation")]


def from_pipeline_record(record, source_file):
    """run_pipeline.py output: a schema.json-conforming disclosure record."""
    llm = (record.get("_meta") or {}).get("llm") or {}
    models = llm.get("models") or {}
    ran_regimes = bool(record.get("regimes"))
    model_note = models.get("small", "?") if not ran_regimes else (
        f"{models.get('small','?')}+{models.get('large','?')}")
    return {
        "case_id": record.get("record_id", "?"),
        "arm": "C",
        "model": model_note + ("" if ran_regimes else " (nodes 1-2 only -- no --regimes was passed)"),
        "seed": 1,
        "facts": record.get("facts", {}),
        "missing": record.get("missing", []),
        "methods": _methods(record),
        "elements": {},   # see module docstring -- not producible from any current output
        "citations": _citations(record),
        "raw": json.dumps(record, ensure_ascii=False),
        "_source_file": os.path.basename(source_file),
    }


def from_arm_output(wrapped, source_file):
    """run_arms.py output: {"arm", "case", "record": <disclosure record or None>, "_meta": {...}}."""
    record = wrapped.get("record") or {}
    llm = (wrapped.get("_meta") or {}).get("llm") or {}
    return {
        "case_id": wrapped.get("case", "?"),
        "arm": wrapped.get("arm", "?"),
        "model": llm.get("models", {}).get("large", "?"),
        "seed": 1,
        "facts": record.get("facts", {}) if record else {},
        "missing": record.get("missing", []) if record else [],
        "methods": _methods(record) if record else [],
        "elements": {},   # see module docstring
        "citations": _citations(record) if record else [],
        "raw": wrapped.get("error") or json.dumps(record, ensure_ascii=False),
        "_source_file": os.path.basename(source_file),
        "_produced_json": wrapped.get("produced_json"),
    }


def convert_one(path):
    d = json.load(open(path, encoding="utf-8"))
    if "record_id" in d:
        return from_pipeline_record(d, path)
    if "arm" in d and "case" in d:
        return from_arm_output(d, path)
    return None  # not a run file we recognise (e.g. an already-normalized file)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true",
                     help="after converting, run score.py against every normalized file")
    ap.add_argument("--dir", default=RUNS,
                     help="source dir of run json files (default: runs/). "
                          "D49/Block B: pass runs/21aug for the re-run against "
                          "input.md instead of the 20-Aug case.md run")
    a = ap.parse_args()

    src_dir = os.path.abspath(a.dir)
    out_dir = OUT_DIR if src_dir == RUNS else os.path.join(src_dir, "normalized")

    os.makedirs(out_dir, exist_ok=True)
    converted = []
    skipped = []
    for path in sorted(glob.glob(os.path.join(src_dir, "*.json"))):
        norm = convert_one(path)
        if norm is None:
            skipped.append(os.path.basename(path))
            continue
        out_name = os.path.basename(path)
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(norm, f, indent=2, ensure_ascii=False)
        converted.append(out_path)

    print(f"  converted {len(converted)} run file(s) -> {os.path.relpath(out_dir, ROOT)}/")
    if skipped:
        print(f"  skipped {len(skipped)} (not a recognised run shape): {skipped}")

    if not a.report:
        return

    import score  # eval/score.py -- untouched, just imported

    print("\n" + "=" * 74)
    print("  DETAIL")
    print("=" * 74)
    rows = []
    for f in converted:
        try:
            r = score.score_run(f)
        except Exception as e:
            print(f"\n  {os.path.basename(f)}: SCORING FAILED -- {e}")
            continue
        rows.append(r)

    for r in rows:
        print(f"\n  {r['case']}  ·  arm {r['arm']}  ·  {r['model']}")
        print(f"    M1 extraction   {score.fmt(r['m1'])}")
        print(f"    M2 gap recall   {score.fmt(r['m2_recall'])}   precision {score.fmt(r['m2_prec'])}")
        print(f"    M3 cite valid   {score.fmt(r['m3_valid'])}   stale {score.fmt(r['m3_stale'])}")
        print(f"    M4 methods      {r['m4_named']}/{r['m4_expected']}   {score.fmt(r['m4'])}")
        print(f"    M5 false abst.  {score.fmt(r['m5'])}"
              + ("   (elements[] empty in every current output -- not scoreable yet)"
                 if r['m5'] is None else ""))

    print("\n" + "=" * 74)
    print("  TABLE  (paste into results.md)")
    print("=" * 74)
    print("| Case | Arm | Model | M1 extract | M2 recall | M2 prec | "
          "M3 valid | M3 stale | M4 methods | M5 false abst |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['case']} | {r['arm']} | {r['model']} | "
              f"{score.fmt(r['m1'])} | {score.fmt(r['m2_recall'])} | {score.fmt(r['m2_prec'])} | "
              f"{score.fmt(r['m3_valid'])} | {score.fmt(r['m3_stale'])} | "
              f"{r['m4_named']}/{r['m4_expected']} | {score.fmt(r['m5'])} |")


if __name__ == "__main__":
    main()
