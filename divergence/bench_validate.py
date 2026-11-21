"""P10a bench item validator (P10-05/06/16). Prints rule results and item ids only; never text.

Body-dependent rules (R07-R09) run only where the local body exists; otherwise SKIP.
Exit 1 on any FAIL.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

from divergence.bench_build import read_body, record_paths
from divergence.bench_slots import (DEFAULT_OUT, DEFAULT_SPEC, UNDATED, abstain_category, active_slots,
                                    load_spec, pair_keys, quotas, read_slots)
from divergence.statute_caveats import span_crosses_point
from divergence.statute_lookup import FOUND, lookup
from divergence.statute_schema import DEFAULT_ROOT, body_sha256, parse_date

SCHEMA_PATH = Path(__file__).resolve().parent / "bench" / "schema" / "bench_item.schema.json"
RULES = (("R01", "schema"), ("R02", "slot_match"), ("R03", "lookup_gold"), ("R04", "abstain_consistency"),
         ("R05", "dated_has_date"), ("R06", "undated_no_date"), ("R07", "nugget_bounds"),
         ("R08", "nugget_sha16"), ("R09", "nugget_caveat"), ("R10", "quotas"), ("R11", "per_unit_cap"),
         ("R12", "pair_complete"), ("R13", "duplicates"), ("R14", "active_slots"), ("R15", "split_disjoint"))
MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December|"
          "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec")
DATE_PATTERNS = tuple(re.compile(p, re.IGNORECASE) for p in (
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{1,2}[/.]\d{1,2}[/.]\d{4}\b",
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:" + MONTHS + r")\.?,?\s+\d{4}\b",
    r"\b(?:" + MONTHS + r")\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b",
    r"\b(?:" + MONTHS + r")\.?,?\s+\d{4}\b",
    r"\b\d{4}\s*[-–/]\s*\d{2}(?:\d{2})?\b",
))


def has_date_expression(text):
    return any(p.search(text or "") for p in DATE_PATTERNS)


def read_jsonl(path):
    lines = Path(path).read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    return [json.loads(line) for line in lines if line.strip()]


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def default_status_path(items_path):
    items_path = Path(items_path)
    return items_path.with_name(items_path.stem + ".status.csv")


class _Result:
    def __init__(self):
        self.out = {rid: {"status": "PASS", "ids": [], "n": 0, "note": ""} for rid, _ in RULES}

    def check(self, rid, ok, ident):
        entry = self.out[rid]
        entry["n"] += 1
        if not ok:
            entry["status"] = "FAIL"
            if ident not in entry["ids"]:
                entry["ids"].append(ident)

    def mark(self, rid, status, note=""):
        if self.out[rid]["status"] != "FAIL":
            self.out[rid]["status"] = status
        self.out[rid]["note"] = note


def _blank(value):
    return "" if value is None else value


def _slot_fields_match(item, slot, spec, side):
    expected = {
        "split": slot["split"], "stratum": slot["stratum"], "act": slot["act"], "unit": slot["unit"],
        "as_of": slot["as_of"], "tax_year": slot["tax_year"], "gold_status": slot["gold_status"],
        "gold_record_id": slot["gold_record_id"], "pair_id": slot["pair_id"],
        "abstain_category": slot["abstain_category"]}
    for key, value in expected.items():
        if _blank(item.get(key)) != value:
            return False
    return (";".join(item.get("gold_reasons") or []) == slot["gold_reasons"]
            and item.get("should_abstain") == (slot["should_abstain"] == "true")
            and item.get("act_post_cutoff") == (slot["act_post_cutoff"] == "true")
            and item.get("dated") == (slot["stratum"] != UNDATED)
            and item.get("as_known_on") == spec["as_known_on"]
            and item.get("abstain_source") == "code"
            and item.get("item_id") == f"{slot['slot_id']}-{side}")


def _gold(item):
    return (item.get("act"), item.get("unit"), item.get("gold_status"), item.get("gold_record_id"),
            tuple(item.get("gold_reasons") or ()))


def validate(items, slot_rows, spec, root, caveat_rows, status_rows, partial=False, schema=None):
    res = _Result()
    split_set = {i.get("split") for i in items}
    split = split_set.pop() if len(split_set) == 1 else None
    by_key = {(r["slot_id"], r["side"]): r for r in slot_rows}
    known = parse_date(spec["as_known_on"])
    recs = record_paths(root)
    records = [rec for rec, _ in recs.values()]

    # R01 schema
    if schema is None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema  # lazy, as in statute_schema
    validator = jsonschema.Draft202012Validator(schema)
    for item in items:
        res.check("R01", not list(validator.iter_errors(item)), item.get("item_id"))

    for item in items:
        iid = item.get("item_id")
        try:
            # R02 slot exists and matches
            side = str(iid).rsplit("-", 1)[-1]
            slot = by_key.get((item.get("slot_id"), side))
            res.check("R02", split is not None and slot is not None and _slot_fields_match(item, slot, spec, side), iid)
            dated = item.get("dated")
            # R03 lookup recompute
            if dated:
                kwargs = ({"as_of": parse_date(item["as_of"])} if item.get("as_of")
                          else {"tax_year": item["tax_year"]})
                r = lookup(records, act=item["act"], unit=item["unit"], as_known_on=known, **kwargs)
                res.check("R03", (r.status, r.record_id, list(r.reasons)) ==
                          (item["gold_status"], item["gold_record_id"], list(item["gold_reasons"])), iid)
            # R04 abstain consistency
            if dated:
                found = item["gold_status"] == FOUND
                cat = None if found else abstain_category(tuple(item["gold_reasons"]), spec)
                res.check("R04", item["should_abstain"] == (not found) and item["abstain_category"] == cat, iid)
                # R05 dated question carries a date / tax-year expression
                res.check("R05", has_date_expression(item.get("question")), iid)
            else:
                res.check("R04", item.get("should_abstain") is True
                          and item.get("abstain_category") == spec["undated_category"], iid)
                res.check("R06", not has_date_expression(item.get("question")), iid)
        except (KeyError, TypeError, ValueError):
            res.check("R02", False, iid)

    # R07-R09 nuggets (body-dependent)
    bodies, skipped, checked = {}, 0, 0
    caveats = {}
    for row in caveat_rows:
        caveats.setdefault(row["record_id"], []).append((int(row["start"]), int(row["end"])))
    for item in items:
        iid = item.get("item_id")
        for nug in item.get("nuggets") or []:
            rid = nug.get("record_id")
            if rid != item.get("gold_record_id") or rid not in recs:
                res.check("R07", False, iid)
                continue
            if rid not in bodies:
                rec, path = recs[rid]
                bodies[rid] = read_body(root, rec, path)
            body = bodies[rid]
            if body is None:
                skipped += 1
                continue
            checked += 1
            start, end = nug.get("start"), nug.get("end")
            inside = isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(body)
            res.check("R07", inside, iid)
            if not inside:
                continue
            res.check("R08", body_sha256(body[start:end])[:16] == nug.get("sha16"), iid)
            clash = False
            for cs, ce in caveats.get(rid, []):
                if cs == ce:
                    clash = clash or span_crosses_point(start, end, cs)
                else:
                    clash = clash or (start < ce and cs < end)
            res.check("R09", nug.get("quotes_gazette") or not clash, iid)
    for rid in ("R07", "R08", "R09"):
        if skipped and not checked:
            res.mark(rid, "SKIP", "skipped (no local bodies)")
        elif skipped:
            res.out[rid]["note"] = f"{skipped} nugget(s) skipped (no local body)"

    # R14 active slots (status file + reserve order)
    unusable = {r["slot_id"]: r.get("reason", "") for r in status_rows if r.get("status") == "unusable"}
    cap = spec.get("max_test_items_per_unit")
    active, pulled, errors = active_slots(slot_rows, split or "", unusable, cap) if split else ([], {}, ["no split"])
    for line in errors:
        res.check("R14", False, line.split(":")[0])
    for r in status_rows:
        if r.get("status") == "unusable":
            res.check("R14", pulled.get(r["slot_id"], "") == (r.get("pulled_into") or ""), r["slot_id"])
    active_set = set(active)
    for item in items:
        res.check("R14", item.get("slot_id") in active_set, item.get("item_id"))
    expected_ids = {f"{r['slot_id']}-{r['side']}" for r in slot_rows if r["slot_id"] in active_set}
    present = {i.get("item_id") for i in items}
    missing = sorted(expected_ids - present)

    # R10 quotas
    if split:
        want = quotas(spec[split]["pairs"], spec)
        got = Counter()
        for pid in {i.get("pair_id") for i in items if i.get("pair_id")}:
            got[next(i["stratum"] for i in items if i.get("pair_id") == pid)] += 1
        undated = sum(1 for i in items if i.get("stratum") == UNDATED)
        ok = all(got[s] == want[s] for s in want) and undated == spec[split]["undated"] and not missing
        if partial and not ok:
            res.mark("R10", "INFO", f"partial: {len(present)}/{len(expected_ids)} items present")
        else:
            res.check("R10", ok, f"strata {dict(got)} undated {undated} missing {len(missing)}")

    # R11 per-unit cap (TEST only)
    if split == "test" and cap is not None:
        counts = Counter(f"{i.get('act')}:{i.get('unit')}" for i in items)
        for unit, n in sorted(counts.items()):
            res.check("R11", n <= cap, unit)
    else:
        res.mark("R11", "SKIP", "dev split: no cap")

    # R12 pairs complete with different gold
    pairs = {}
    for item in items:
        if item.get("pair_id"):
            pairs.setdefault(item["pair_id"], []).append(item)
    for pid, members in sorted(pairs.items()):
        sides = sorted(str(m.get("item_id")).rsplit("-", 1)[-1] for m in members)
        if sides != ["a", "b"]:
            if partial and len(members) == 1:
                res.out["R12"]["note"] = "partial: incomplete pairs allowed"
                continue
            res.check("R12", False, pid)
            continue
        res.check("R12", _gold(members[0]) != _gold(members[1]), pid)

    # R13 duplicates
    ids = Counter(i.get("item_id") for i in items)
    for iid, n in ids.items():
        res.check("R13", n == 1, iid)
    seen = {}
    for item in items:
        key = (item.get("act"), item.get("unit"), item.get("as_of"), item.get("tax_year"),
               " ".join(str(item.get("question", "")).lower().split()))
        res.check("R13", key not in seen, item.get("item_id"))
        seen.setdefault(key, item.get("item_id"))

    # R15 no (unit, date_a, date_b) shared across DEV and TEST slots
    shared = pair_keys(slot_rows, "dev") & pair_keys(slot_rows, "test")
    res.check("R15", not shared, f"{len(shared)} shared slot key(s)")
    return res.out, missing


def report(out, missing, n_items):
    print(f"bench validate: {n_items} item(s); missing active items {len(missing)}")
    failed = False
    for rid, name in RULES:
        entry = out[rid]
        failed = failed or entry["status"] == "FAIL"
        ids = entry["ids"][:20]
        extra = f" ids: {', '.join(str(i) for i in ids)}" + (" ..." if len(entry["ids"]) > 20 else "") if ids else ""
        note = f" [{entry['note']}]" if entry["note"] else ""
        print(f"{rid} {name}: {entry['status']} (checks {entry['n']}){note}{extra}")
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--slots", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--caveats", type=Path, default=None)
    parser.add_argument("--status", type=Path, default=None)
    parser.add_argument("--partial", action="store_true", help="drafting: quotas/pairs incomplete = INFO")
    args = parser.parse_args(argv)
    items = read_jsonl(args.items)
    if not items:
        print("bench validate: ERROR no items")
        return 1
    caveats = args.caveats if args.caveats is not None else args.root / "census" / "BODY-CAVEATS.csv"
    status = args.status if args.status is not None else default_status_path(args.items)
    status_rows = read_csv_rows(status) if status.is_file() else []
    out, missing = validate(items, read_slots(args.slots), load_spec(args.spec), args.root,
                            read_csv_rows(caveats) if caveats.is_file() else [], status_rows, args.partial)
    return report(out, missing, len(items))


if __name__ == "__main__":
    sys.exit(main())
