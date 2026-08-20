#!/usr/bin/env python3
"""
m3b_citation_coverage.py  --  does the run cite what it was supposed to cite?

WHY THIS FILE EXISTS, SEPARATELY.

`eval/score.py`'s metric 3 checks that the citations a run produced are VALID
(they resolve against the corpus for the stated tax year). It never looks at
`citations_expected[]`. So a run that cites two correct provisions and misses
six scores identically to one that cites all eight.

Valid != complete. Metric 3 measures the first. This measures the second.

Deliberately a separate file: score.py has a history (v1 under-credited arm A,
v1.5 over-corrected to 100% recall, v2 needs a shared distinctive token) and
rewriting it blind, days before a deadline, to add a metric is how that
history repeats. This is additive. score.py is untouched.

    python eval/m3b_citation_coverage.py --run runs/D1_pipeline.json --case D1
    python eval/m3b_citation_coverage.py --all runs/

Reports, per run: recall (of the pre-registered set, how many were cited),
precision (of what was cited, how many were pre-registered), and the actual
misses by name -- because "recall 0.62" tells you nothing you can act on and
"missed Rule 57 and Rule 247(4)" tells you everything.
"""

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# cases/ first: score.py's own ROOT/cases resolution is the single source of
# truth, and it's the copy citations_expected[] was actually filled on 20
# Aug. step21drop/cases/ is the Step 21 drop snapshot, still empty there --
# checking it first would silently score against stale, unfilled ground
# truth instead of the frozen one (commit 225ed20).
CASE_DIRS = [os.path.join(ROOT, "cases"),
             os.path.join(ROOT, "step21drop", "cases")]


def ground_truth(case):
    for base in CASE_DIRS:
        p = os.path.join(base, case, "ground_truth.json")
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8")), p
    return None, None


def key(citation):
    """A comparison key that survives cosmetic variation but NOT a different
    provision. 'Rule 57, Income-tax Rules, 2026' and 'rule 57 of the Income-tax
    Rules 2026' are the same row; Rule 57 and Rule 56 are not.

    Deliberately NOT fuzzy. An earlier scorer in this project was made lenient
    to stop under-crediting the baseline and ended up reporting 100% recall.
    Over-crediting is the worse failure -- it hides the thing being measured."""
    t = (citation or "").lower()
    t = t.replace("—", "-").replace("–", "-")
    nums = re.findall(r"\b(?:rule|section|s\.|r\.)\s*([0-9]+[a-z]*(?:\([^)]*\))*)", t)
    if not nums:
        nums = re.findall(r"\b([0-9]{1,4}[a-z]*(?:\([^)]*\))*)\b", t)
    kind = "rule" if re.search(r"\brule\b|\br\.", t) else (
           "section" if re.search(r"\bsection\b|\bs\.", t) else "other")
    inst = ("igst" if "igst" in t else
            "fema" if "fema" in t else
            "cgst" if "cgst" in t else
            "rules2026" if "rules, 2026" in t or "rules 2026" in t else
            "act2025" if "2025" in t else
            "act1961" if "1961" in t else "?")
    num = nums[0] if nums else t.strip()[:24]
    # (kind, number) is the identity. The instrument is returned alongside so
    # an unqualified citation can be counted as a hit AND flagged, instead of
    # being scored as a miss (which is what score.py v1 did to arm A) or
    # silently waved through (which is what v1.5 did).
    return (kind, num), inst


def collect(obj, found=None):
    """Pull citations out of a record whatever shape it is in. Arm A's output
    shape is not predictable -- that is half of what arm A demonstrates -- so
    this walks the whole tree rather than assuming a path."""
    if found is None:
        found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("provision", "citation", "current_citation") and isinstance(v, str):
                found.append(v)
            elif k == "citations" and isinstance(v, list):
                for c in v:
                    if isinstance(c, str):
                        found.append(c)
                    elif isinstance(c, dict):
                        collect(c, found)
            else:
                collect(v, found)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, found)
    return found


def score_one(run_path):
    raw = json.load(open(run_path, encoding="utf-8"))
    case = raw.get("case") or raw.get("record_id") or \
        os.path.basename(run_path).split("_")[0]
    arm = raw.get("arm", "C")
    record = raw.get("record", raw)

    gt, gt_path = ground_truth(case)
    if gt is None:
        return {"run": os.path.basename(run_path), "case": case, "arm": arm,
                "error": "no ground_truth.json for %s" % case}

    expected = gt.get("citations_expected") or []
    if not expected:
        return {"run": os.path.basename(run_path), "case": case, "arm": arm,
                "expected": 0,
                "note": "citations_expected[] is empty for this case. If that "
                        "is deliberate (a false-abstention control), say so in "
                        "the ground-truth file so it does not read as unfinished."}

    exp_map, exp_inst = {}, {}
    for e in expected:
        prov = e.get("provision") if isinstance(e, dict) else e
        k, inst = key(prov)
        exp_map.setdefault(k, prov)
        exp_inst.setdefault(k, inst)

    got_map, got_inst = {}, {}
    for g in collect(record):
        k, inst = key(g)
        got_map.setdefault(k, g)
        got_inst.setdefault(k, inst)

    hit = set(exp_map) & set(got_map)
    missed = set(exp_map) - set(got_map)
    extra = set(got_map) - set(exp_map)

    # Right provision, but no Act/Rules name on it. Counted as a hit here --
    # this metric asks "was it cited", not "was it cited well". But it is
    # reported, because citation_matcher.py resolves a bare "Section 2(111)"
    # against the WRONG corpus file, so an unqualified citation is a live
    # hazard in this codebase, not a style nit.
    unqualified = sorted(got_map[k] for k in hit
                         if got_inst.get(k) == "?" and exp_inst.get(k) != "?")

    return {
        "run": os.path.basename(run_path), "case": case, "arm": arm,
        "expected": len(exp_map), "cited": len(got_map),
        "recall": round(len(hit) / len(exp_map), 3),
        "precision": round(len(hit) / len(got_map), 3) if got_map else 0.0,
        "missed": sorted(exp_map[k] for k in missed),
        "unexpected": sorted(got_map[k] for k in extra),
        "unqualified": unqualified,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--all", default=None, help="directory of run json files")
    a = ap.parse_args()

    runs = list(a.run)
    if a.all:
        runs += sorted(glob.glob(os.path.join(a.all, "*.json")))
    if not runs:
        print("give --run <file> or --all <dir>")
        return 1

    rows = [score_one(r) for r in runs]

    print("\n  %-26s %-4s %5s %5s %7s %7s" %
          ("run", "arm", "exp", "cite", "recall", "prec"))
    print("  " + "-" * 60)
    for r in rows:
        if "error" in r or "note" in r:
            print("  %-26s %-4s   %s" % (r["run"], r["arm"],
                                         r.get("error") or r.get("note")))
            continue
        print("  %-26s %-4s %5d %5d %7.3f %7.3f"
              % (r["run"], r["arm"], r["expected"], r["cited"],
                 r["recall"], r["precision"]))

    print()
    for r in rows:
        if r.get("missed"):
            print("  %s missed:" % r["run"])
            for m in r["missed"]:
                print("      - %s" % m)
    for r in rows:
        if r.get("unqualified"):
            print("  %s cited without an Act/Rules name (counted as hits, but "
                  "citation_matcher.py mis-resolves these):" % r["run"])
            for u in r["unqualified"]:
                print("      ~ %s" % u)
    print()

    by_arm = {}
    for r in rows:
        if "recall" in r:
            by_arm.setdefault(r["arm"], []).append(r["recall"])
    if len(by_arm) > 1:
        print("  mean recall by arm:")
        for arm in sorted(by_arm):
            v = by_arm[arm]
            print("    arm %s : %.3f  (n=%d)" % (arm, sum(v) / len(v), len(v)))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
