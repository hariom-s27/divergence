"""P10b-D3 clock audit: for every 1961 slot side with an as_of date, compare the record lookup()
returns by date (as_of=d) with the record it returns by the financial year containing d
(tax_year=FY(d)). Also counts 1961 version boundaries and slot dates in the 12 months before a
1 April boundary on the same unit.

Reads only slot_id, split, side, reserve, act, unit, as_of, tax_year from the slots file (no gold
columns, no questions). Output JSON: definitions, counts, ids and record ids only; never text.
Refuses to write under divergence/runs/ (frozen) and refuses to overwrite an existing file.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from divergence.bench_build import record_paths
from divergence.bench_slots import BENCH_DIR, DEFAULT_OUT, DEFAULT_SPEC, load_spec
from divergence.statute_lookup import FOUND, lookup
from divergence.statute_schema import DEFAULT_ROOT, parse_date

DEFAULT_AUDIT = BENCH_DIR / "audit" / "2026-11-21_clock_audit.json"
FROZEN_RUNS = Path(__file__).resolve().parent / "runs"
SLOT_COLUMNS = ("slot_id", "split", "side", "reserve", "act", "unit", "as_of", "tax_year")
GROUPS = tuple((split, kind) for split in ("dev", "test") for kind in ("main", "reserve"))
DEFINITIONS = {
    "fy_of_date": "FY(d) = 'Y-(Y+1)' with Y = d.year if d.month >= 4 else d.year - 1; the financial-year label "
                  "used by statute_schema.tax_year_bounds (1 April Y .. 1 April Y+1).",
    "by_date": "lookup(act='1961', unit, as_of=d, as_known_on=SPEC.as_known_on)",
    "by_ty": "lookup(act='1961', unit, tax_year=FY(d), as_known_on=SPEC.as_known_on)",
    "agree": "both FOUND with the same record_id",
    "disagree": "both FOUND with different record_id, or exactly one FOUND",
    "boundary": "each later distinct in_force_from of a 1961 act unit's versions (first start excluded)",
    "window": "B - 12 months <= d < B for a 1 April boundary B on the same unit; tax_year slots tested with "
              "1 April of the FY's first year",
    "scope": "1961 slot sides in SLOTS (main and reserve counted separately); tax_year and undated sides have no "
             "date and are counted as not applicable",
}


def fy_of(d: date) -> str:
    y = d.year if d.month >= 4 else d.year - 1
    return f"{y}-{(y + 1) % 100:02d}"


def _fmt(res) -> str:
    return res.record_id if res.status == FOUND else f"{res.status}({';'.join(res.reasons)})"


def read_slot_columns(path):
    with open(path, newline="", encoding="utf-8") as stream:
        return [{c: row[c] for c in SLOT_COLUMNS} for row in csv.DictReader(stream)]


def boundaries(records):
    units = defaultdict(set)
    for rec in records:
        if rec.get("act") == "1961" and rec.get("source_kind") == "act":
            start = parse_date(rec.get("in_force_from"))
            if start is not None:
                units[rec["unit"]].add(start)
    return {unit: sorted(starts)[1:] for unit, starts in units.items()}


def audit(slot_rows, records, known):
    bounds = boundaries(records)
    all_b = [b for bs in bounds.values() for b in bs]
    counts = {f"{s}_{k}": Counter() for s, k in GROUPS}
    sides = {f"{s}_{k}": [] for s, k in GROUPS}
    window = {f"{s}_{k}": {"as_of": [], "tax_year": []} for s, k in GROUPS}
    for slot in slot_rows:
        if slot["act"] != "1961":
            continue
        group = f"{slot['split']}_{'reserve' if slot['reserve'] == 'true' else 'main'}"
        sid = f"{slot['slot_id']}-{slot['side']}"
        april = [b for b in bounds.get(slot["unit"], []) if (b.month, b.day) == (4, 1)]
        point = parse_date(slot["as_of"]) if slot["as_of"] else (
            date(int(slot["tax_year"][:4]), 4, 1) if slot["tax_year"] else None)
        if point is not None:
            hit = [b for b in april if date(b.year - 1, 4, 1) <= point < b]
            if hit:
                window[group]["as_of" if slot["as_of"] else "tax_year"].append(f"{sid}@{hit[0].isoformat()}")
        if not slot["as_of"]:
            counts[group]["na_tax_year" if slot["tax_year"] else "na_undated"] += 1
            continue
        d = parse_date(slot["as_of"])
        by_date = lookup(records, act="1961", unit=slot["unit"], as_of=d, as_known_on=known)
        by_ty = lookup(records, act="1961", unit=slot["unit"], tax_year=fy_of(d), as_known_on=known)
        counts[group]["as_of_sides"] += 1
        if by_date.status == FOUND and by_ty.status == FOUND:
            kind = "agree" if by_date.record_id == by_ty.record_id else "found_found_diff_record"
        elif by_date.status == FOUND or by_ty.status == FOUND:
            kind = "found_vs_nonfound"
        else:
            kind = "both_nonfound"
        counts[group][kind] += 1
        sides[group].append({"id": sid, "date": d.isoformat(), "fy": fy_of(d), "by_date": _fmt(by_date),
                             "by_ty": _fmt(by_ty), "result": kind})
    keys = ("as_of_sides", "agree", "found_found_diff_record", "found_vs_nonfound", "both_nonfound",
            "na_tax_year", "na_undated")
    out_counts = {g: {k: c[k] for k in keys} for g, c in counts.items()}
    for g in out_counts:
        out_counts[g]["disagree"] = out_counts[g]["found_found_diff_record"] + out_counts[g]["found_vs_nonfound"]
        out_counts[g]["window_as_of"] = len(window[g]["as_of"])
        out_counts[g]["window_tax_year"] = len(window[g]["tax_year"])
    total = {k: sum(c[k] for c in out_counts.values()) for k in ("as_of_sides", "agree", "disagree", "both_nonfound")}
    return {
        "boundaries": {"units_1961": len(bounds), "total": len(all_b),
                       "on_1_april": sum(1 for b in all_b if (b.month, b.day) == (4, 1)),
                       "per_unit": {u: [b.isoformat() for b in bs] for u, bs in sorted(bounds.items()) if bs}},
        "counts": out_counts, "totals": total,
        "sides": {g: sorted(v, key=lambda e: e["id"]) for g, v in sides.items()},
        "window_ids": {g: {k: sorted(v) for k, v in w.items()} for g, w in window.items()},
    }


def _refuse(out: Path):
    resolved = out.resolve()
    if resolved == FROZEN_RUNS or FROZEN_RUNS in resolved.parents:
        return "refusing to write under divergence/runs/ (frozen)"
    if resolved.exists():
        return f"refusing to overwrite existing {out}"
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--slots", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_AUDIT)
    args = parser.parse_args(argv)
    why = _refuse(args.out)
    if why:
        print(f"bench clock audit: ERROR {why}")
        return 2
    spec = load_spec(args.spec)
    known = parse_date(spec["as_known_on"])
    records = [rec for rec, _ in record_paths(args.root).values()]
    result = audit(read_slot_columns(args.slots), records, known)
    payload = {"audit": "P10b-D3 clock audit (by date vs by financial year)", "as_known_on": spec["as_known_on"],
               "slots_sha256": hashlib.sha256(Path(args.slots).read_bytes()).hexdigest(),
               "records": len(records), "definitions": DEFINITIONS, **result}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes((json.dumps(payload, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    b = result["boundaries"]
    print(f"bench clock audit: 1961 boundaries {b['total']} (on 1 April {b['on_1_april']}); totals {result['totals']}")
    for g, c in result["counts"].items():
        print(f"  {g}: as_of {c['as_of_sides']} agree {c['agree']} disagree {c['disagree']} "
              f"(found/found {c['found_found_diff_record']}, found/non {c['found_vs_nonfound']}) "
              f"both_nonfound {c['both_nonfound']} na_ty {c['na_tax_year']} na_undated {c['na_undated']} "
              f"window as_of {c['window_as_of']} ty {c['window_tax_year']}")
    print(f"  wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
