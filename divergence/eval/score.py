#!/usr/bin/env python3
"""
SCORE — DIVERGENCE evaluation harness
Implements the five metrics from evaluation-design.md. Deterministic.

    python eval/score.py --run runs/D1_armA_large_seed1.json
    python eval/score.py --all            # every run in runs/, one table
    python eval/score.py --table          # markdown, paste into results.md

A RUN FILE is whatever the arm produced, normalised to:
{
  "case_id": "D1", "arm": "A", "model": "large", "seed": 1,
  "facts":    { "<field>": {"value": ...}, ... },
  "missing":  [ {"item": "..."} , ... ],
  "methods":  [ "<label or description of each valuation method named>", ... ],
  "elements": { "official_date": "open" | "settled", ... },
  "citations":[ {"provision": "Rule 57", "tax_year": "FY 2026-27"}, ... ],
  "raw":      "<the full unedited output>"
}
For arms A and B you fill these by hand from the raw output. That hand-coding
is why the protocol says two scorers independently on the first five.
"""
import os, re, sys, json, glob, argparse, difflib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.dirname(HERE)
CASES = os.path.join(ROOT, "cases")
RUNS  = os.path.join(ROOT, "runs")


def truth(case_id):
    p = os.path.join(CASES, case_id.split("-")[0], "ground_truth.json")
    if not os.path.exists(p):
        raise SystemExit(f"no ground truth for {case_id} at {p}")
    return json.load(open(p, encoding="utf-8"))


def _norm(x):
    return str(x).strip().lower().replace("/", "-").replace(" ", "")


_STOP = {"the","and","for","of","a","an","to","in","on","by","is","no","not",
         "this","that","with","from","its","was","been","only","any"}

def _similar(a, b, thresh=0.72):
    """Fuzzy ratio OR distinctive-keyword overlap.

    Arm A answers in prose. "no FIRC" and "bank certificate of foreign inward
    remittance (FIRC)" are the same gap, and a pure ratio scores them 0.28.
    Under-crediting the baseline is exactly the straw-man failure the whole
    evaluation is designed to avoid, so keyword overlap counts too.
    """
    na, nb = _norm(a), _norm(b)
    if difflib.SequenceMatcher(None, na, nb).ratio() >= thresh:
        return True
    ka = {w for w in re.split(r"[^a-z0-9]+", str(a).lower()) if len(w) >= 4 and w not in _STOP}
    kb = {w for w in re.split(r"[^a-z0-9]+", str(b).lower()) if len(w) >= 4 and w not in _STOP}
    if not ka or not kb:
        return False
    # A shared DISTINCTIVE token. Deliberately no acronym/substring fallback:
    # an earlier version matched "purpose code" to "no FIRC" because both
    # contain a short alpha token, which over-credits the baseline. Both
    # directions of error are bad; this one is worse, because inflating arm A
    # would hide the very failure we are trying to measure.
    return bool(ka & kb)


def _same_date(a, b):
    """Same instant written differently is a normalisation difference, not an
    extraction failure. 28/06/2026 and 2026-06-28 are the same day."""
    da = [g for g in re.findall(r"\d+", str(a)) if len(g) <= 4]
    db = [g for g in re.findall(r"\d+", str(b)) if len(g) <= 4]
    if not da or not db:
        return False
    ya = {g.zfill(2) for g in da[:3]}
    yb = {g.zfill(2) for g in db[:3]}
    return ya == yb


# ── M1 ────────────────────────────────────────────────────────────────
def m1_extraction(run, gt):
    """Per field. Exact match = 1. Date normalisation differences = 1.
    Trade name where legal name was available = 0, not 0.5 (see F10)."""
    got, exp = run.get("facts", {}), gt["facts"]
    rows = []
    for field, spec in exp.items():
        want = spec["value"]
        have = (got.get(field) or {}).get("value", None)
        if have is None:
            rows.append((field, want, None, 0.0, "not extracted")); continue
        if _norm(have) == _norm(want):
            rows.append((field, want, have, 1.0, "")); continue
        # dates: same instant written differently still counts
        if ("datetime" in field or "date" in field) and _same_date(have, want):
            rows.append((field, want, have, 1.0, "normalised differently")); continue
        rows.append((field, want, have, 0.0, "mismatch"))
    score = sum(r[3] for r in rows) / len(rows) if rows else 0.0
    return score, rows


# ── M2 ────────────────────────────────────────────────────────────────
def m2_gaps(run, gt):
    """Recall and precision against the gaps WE planted — genuine ground truth."""
    planted = [m["item"] for m in gt["missing"]]
    reported = [m.get("item", "") if isinstance(m, dict) else str(m)
                for m in run.get("missing", [])]
    if not planted:
        # nothing to find: recall is undefined, every report is a false positive
        return (None, 0.0 if reported else 1.0, [], reported)
    found = [p for p in planted if any(_similar(p, r) for r in reported)]
    real  = [r for r in reported if any(_similar(p, r) for p in planted)]
    recall    = len(found) / len(planted)
    precision = len(real) / len(reported) if reported else 0.0
    missed    = [p for p in planted if p not in found]
    spurious  = [r for r in reported if r not in real]
    return recall, precision, missed, spurious


# ── M3 ────────────────────────────────────────────────────────────────
def m3_citations(run):
    """Mechanical. Uses the real matcher if importable."""
    cites = run.get("citations", [])
    if not cites:
        return None, None, []
    try:
        sys.path.insert(0, ROOT)
        from citation_matcher import verify
    except Exception:
        return None, None, [("citation_matcher.py not importable", "", "")]
    rows = []
    for c in cites:
        v = verify(c.get("provision", ""), c.get("tax_year"))
        rows.append((c.get("provision", ""), c.get("tax_year"), v.status))
    valid = sum(1 for r in rows if r[2] == "VERIFIED") / len(rows)
    stale = sum(1 for r in rows if r[2] == "STALE") / len(rows)
    return valid, stale, rows


# ── M4 ────────────────────────────────────────────────────────────────
def m4_enumeration(run, gt):
    """Of N pre-registered defensible methods, how many were named?
    Report the raw list too — a judge should see arm A say 'the market rate'."""
    n = gt.get("methods_expected", 0)
    named = run.get("methods", [])
    return (len(named) / n if n else None), len(named), n, named


# ── M5 ────────────────────────────────────────────────────────────────
def m5_false_abstention(run, gt):
    """Per ELEMENT, not per case. The check on the other four metrics:
    a system that flags everything aces M2 and M4 and fails here.

    D48: a run that never produces an "elements" key at all must NOT
    score the same as a run that produced elements{} and got every
    settled one right -- omission is not evidence of zero false
    abstention, it's the absence of the measurement. Only a run that
    actually reports elements{} can be scored here.
    """
    if not run.get("elements"):
        return None, []
    exp, got = gt["elements"], run["elements"]
    settled = [k for k, v in exp.items() if v == "settled"]
    if not settled:
        return None, []
    wrong = [k for k in settled if got.get(k) == "open"]
    return len(wrong) / len(settled), wrong


# ── report ────────────────────────────────────────────────────────────
def score_run(path):
    run = json.load(open(path, encoding="utf-8"))
    gt = truth(run["case_id"])
    m1, m1r = m1_extraction(run, gt)
    rec, prec, missed, spurious = m2_gaps(run, gt)
    valid, stale, crows = m3_citations(run)
    enum, named_n, exp_n, named = m4_enumeration(run, gt)
    fa, fa_wrong = m5_false_abstention(run, gt)
    return dict(file=os.path.basename(path), case=run["case_id"], arm=run["arm"],
                model=run.get("model", "?"), seed=run.get("seed", 1),
                m1=m1, m2_recall=rec, m2_prec=prec, m3_valid=valid, m3_stale=stale,
                m4=enum, m4_named=named_n, m4_expected=exp_n,
                m5=fa, _m1r=m1r, _missed=missed, _spurious=spurious,
                _cites=crows, _named=named, _fa=fa_wrong)


def fmt(x):
    return "  —  " if x is None else f"{x:6.1%}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()

    files = ([a.run] if a.run else sorted(glob.glob(os.path.join(RUNS, "*.json"))))
    if not files:
        raise SystemExit(f"no run files. Put normalised runs in {RUNS}/ — see the "
                         "docstring at the top of this file for the shape.")
    rows = [score_run(f) for f in files]

    if a.table:
        print("| Case | Arm | Model | Seed | M1 extract | M2 recall | M2 prec | "
              "M3 valid | M3 stale | M4 methods | M5 false abst |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['case']} | {r['arm']} | {r['model']} | {r['seed']} | "
                  f"{fmt(r['m1'])} | {fmt(r['m2_recall'])} | {fmt(r['m2_prec'])} | "
                  f"{fmt(r['m3_valid'])} | {fmt(r['m3_stale'])} | "
                  f"{r['m4_named']}/{r['m4_expected']} | {fmt(r['m5'])} |")
        return

    for r in rows:
        print("\n" + "=" * 74)
        print(f"  {r['case']}  ·  arm {r['arm']}  ·  {r['model']}  ·  seed {r['seed']}")
        print("=" * 74)
        print(f"  M1 extraction accuracy      {fmt(r['m1'])}")
        for f, want, have, sc, note in r["_m1r"]:
            if sc < 1:
                print(f"       MISS  {f}: expected {want!r}, got {have!r}  {note}")
        print(f"  M2 gap recall               {fmt(r['m2_recall'])}"
              f"     precision {fmt(r['m2_prec'])}")
        for m in r["_missed"]:
            print(f"       NOT FOUND  {m}")
        for s in r["_spurious"]:
            print(f"       SPURIOUS   {s}")
        print(f"  M3 citation validity        {fmt(r['m3_valid'])}"
              f"     stale {fmt(r['m3_stale'])}")
        for p, y, st in r["_cites"]:
            if st != "VERIFIED":
                print(f"       {st:<22} {p} ({y})")
        print(f"  M4 method enumeration       {r['m4_named']}/{r['m4_expected']}"
              f"   {fmt(r['m4'])}")
        for n in r["_named"]:
            print(f"       named: {n}")
        print(f"  M5 FALSE ABSTENTION         {fmt(r['m5'])}")
        for w in r["_fa"]:
            print(f"       WRONGLY OPEN  {w}  (ground truth says settled)")
        if r["m5"] is not None and r["m5"] > 0.2:
            print("\n  >>> M5 above 20%. This system cries wolf. A high M2/M4 with a")
            print("      bad M5 is a FAILED system, and results.md must say so.")
    print()


if __name__ == "__main__":
    main()
