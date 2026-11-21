"""Offline metadata-only C4 timeline sweep and independent result invariants."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from divergence.statute_lookup import FOUND, lookup
from divergence.statute_schema import CORPUS_CHECKED_THROUGH, DEFAULT_ROOT, REPEAL_DAY, parse_date, reason_class

DEFAULT_RECORDS = DEFAULT_ROOT / "records"
GOLDEN_DIR = DEFAULT_ROOT / "census"
DAY = timedelta(days=1)
TIMELINE_FIELDS = ("unit", "from", "to", "status", "records", "reasons", "classes")


def load_records(root):
    """Load only committed JSON metadata; never resolve a body path."""
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(Path(root).glob("*/*.json"))]


def effective_start(record):
    return parse_date(record.get("retrospective_from") or record.get("in_force_from"))


def groups(records):
    result = {}
    for record in records:
        key = (record["source_kind"], record["act"], record["unit"])
        result.setdefault(key, []).append(record)
    return {key: sorted(value, key=lambda r: r["version_id"]) for key, value in sorted(result.items())}


def check_partitions(records):
    """Accept ordinary adjacency or D5's assent-time predecessor end, never a gap."""
    checked = retro = 0
    for unit in groups(records).values():
        dated = [r for r in unit if r["status"] != "never_operative" and effective_start(r) is not None]
        for older, newer in zip(dated, dated[1:]):
            end = parse_date(older["in_force_to"])
            if newer.get("retrospective_from"):
                assert end == parse_date(newer["enacted_on"]) == parse_date(newer["in_force_from"]), newer["record_id"]
                assert effective_start(newer) < end, newer["record_id"]
                retro += 1
            else:
                assert end == effective_start(newer), (older["record_id"], newer["record_id"])
            checked += 1
    return {"adjacencies": checked, "retro_patterns": retro}


def knowledge_dates(records, assents=()):
    """No K plus distinct recorded/effect assent dates, each with its neighbours."""
    dates = {parse_date(r.get("enacted_on")) for r in records} - {None}
    dates.update(parse_date(value) for value in assents if value)
    return [None] + sorted({point + delta * DAY for point in dates for delta in (-1, 0, 1)})


def boundary_points(unit):
    points = set()
    for record in unit:
        for field in ("in_force_from", "in_force_to", "retrospective_from"):
            if record.get(field):
                point = parse_date(record[field])
                points.update(point + delta * DAY for delta in (-1, 0, 1))
    return sorted(points)


def queries(records, start, end, years, assents=()):
    """Daily/TY queries at K=None; boundary +/-1-day queries across the knowledge grid."""
    knowledge = knowledge_dates(records, assents)
    for key, unit in groups(records).items():
        base = dict(zip(("source_kind", "act", "unit"), key))
        point = start
        while point < end:
            yield "daily", dict(base, as_of=point)
            point += DAY
        for year in years:
            yield "tax_year", dict(base, tax_year=year)
        for point in boundary_points(unit):
            for known in knowledge:
                yield "boundary", dict(base, as_of=point, as_known_on=known)


def _check_found(unit, result, query, point):
    by_id = {r["record_id"]: r for r in unit}
    assert len(result.candidates) == 1 and result.record_id == result.candidates[0], (query, result)
    record = by_id[result.record_id]
    assert not result.reasons, (query, result)
    assert record["status"] not in {"unprinted", "never_operative"}, (query, result)
    assert not record.get("lookup_flags"), (query, result)
    assert point <= CORPUS_CHECKED_THROUGH, (query, result)
    assert record["act"] != "1961" or point < REPEAL_DAY, (query, result)
    if "as_of" in query:
        start, end = effective_start(record), parse_date(record["in_force_to"])
        assert start is not None and start <= point and (end is None or point < end), (query, result)
    else:
        year = query["tax_year"]
        assert record.get("applies_from_tax_year") and record["applies_from_tax_year"] <= year, (query, result)
        assert not record.get("applies_to_tax_year") or year <= record["applies_to_tax_year"], (query, result)


def check_result(unit, result, query):
    """Restrictions are independent of the lookup's coverage helpers."""
    point = query.get("as_of") or date(int(query["tax_year"][:4]), 4, 1)
    for reason in result.reasons:
        assert reason_class(reason) in {"LEGAL", "QUERY", "CORPUS", "NO_LAW"}, (query, result)
    if result.status == FOUND:
        _check_found(unit, result, query, point)
    elif result.status == "NO_APPLICABLE_VERSION":
        assert not result.candidates and result.record_id is None, (query, result)
    else:
        assert result.status == "AMBIGUOUS" and result.reasons and result.record_id is None, (query, result)


def signature(result):
    return result.status, result.record_id, tuple(result.candidates), tuple(result.reasons)


def _timeline_row(key, point, result):
    return {"unit": ":".join(key), "from": point.isoformat(), "to": (point + DAY).isoformat(),
            "status": result.status, "records": ";".join(result.candidates),
            "reasons": ";".join(result.reasons),
            "classes": ";".join(sorted({reason_class(r) for r in result.reasons}))}


def _extend_timeline(rows, key, point, result):
    row = _timeline_row(key, point, result)
    fields = ("unit", "status", "records", "reasons", "classes")
    if rows and rows[-1]["to"] == row["from"] and all(rows[-1][field] == row[field] for field in fields):
        rows[-1]["to"] = row["to"]
    else:
        rows.append(row)


def sweep(records, *, start=date(2022, 4, 1), end=date(2028, 4, 1),
          years=tuple(f"{y}-{str(y + 1)[-2:]}" for y in range(2021, 2028)), assents=(), lookup_fn=lookup):
    """Return reproducible run-length timelines, query counts and observed reason/class counts."""
    partitions = check_partitions(records)
    units = groups(records)
    counts, reasons, classes, statuses = Counter(), Counter(), Counter(), Counter()
    timeline = []
    for kind, query in queries(records, start, end, years, assents):
        key = tuple(query[k] for k in ("source_kind", "act", "unit"))
        result = lookup_fn(units[key], **query)
        check_result(units[key], result, query)
        counts[kind] += 1
        statuses[result.status] += 1
        reasons.update(result.reasons)
        classes.update(reason_class(reason) for reason in result.reasons)
        if kind == "daily":
            _extend_timeline(timeline, key, query["as_of"], result)
    return {"records": len(records), "units": len(units), "from": start.isoformat(), "to": end.isoformat(),
            "horizon": CORPUS_CHECKED_THROUGH.isoformat(), "queries": dict(counts), "partitions": partitions,
            "statuses": dict(statuses), "reasons": dict(sorted(reasons.items())), "classes": dict(sorted(classes.items())),
            "timeline": timeline}


def timeline_markdown(result):
    lines = ["# C4 metadata timeline", "", "## PLAIN SUMMARY", "",
             f"- What happened: {result['records']} records / {result['units']} units swept; {result['queries']} queries.",
             "- What it means: each run has identical status, candidates, reasons and reason classes.",
             "- Problems: LEGAL/CORPUS/QUERY reasons remain explicit; this is metadata, not law text.",
             "- Decision needed: owner review of unresolved source flags before D80.",
             "- Next message: owner review of the C4-D report.", "", "## Details", "",
             f"Half-open daily range [{result['from']}, {result['to']}); corpus horizon {result['horizon']}.",
             "Knowledge-clock boundary queries are included in counts; runs below describe daily K=None results."]
    last = None
    for row in result["timeline"]:
        if row["unit"] != last:
            lines += ["", "### " + row["unit"], "", "| From | To (exclusive) | Status | Records | Reasons | Classes |",
                      "|---|---|---|---|---|---|"]
            last = row["unit"]
        lines.append("| " + " | ".join(row[field] or "[]" for field in TIMELINE_FIELDS[1:]) + " |")
    lines += ["", "## SELF-AUDIT", "", "1. Plan gate: yes; generated under owner-approved C4-D plan.",
              "2. No commit/push: yes; generation stages nothing.",
              "3. Protected inputs: yes; metadata read only, no bodies/cache/freeze writes.",
              "4. Offline/no secrets: yes; standard-library computation only.",
              "5. Paths: yes; caller chooses approved census paths; no scratch discovery.",
              "6. Determinism/checks: yes; sorted metadata and explicit query ranges; assertions are strict.",
              "7. Public report: yes; metadata labels only.",
              "8. Handoff: yes; run evidence is linked from C4_handoff_D.md."]
    return "\n".join(lines) + "\n"


def sweep_bytes(result):
    return (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")


def timeline_bytes(result):
    return timeline_markdown(result).encode("utf-8")


def write_timeline(result, out, committed):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "TIMELINE.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, TIMELINE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["timeline"])
    for path in (out / "TIMELINE.md", Path(committed)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(timeline_bytes(result))
    with (out / "sweep.json").open("xb") as stream:
        stream.write(sweep_bytes(result))


def golden_files(result):
    return (("sweep.json", sweep_bytes(result)), ("D80_TIMELINE.md", timeline_bytes(result)))


def first_differing_line(old, new):
    old_lines = old.splitlines(keepends=True) if old is not None else []
    new_lines = new.splitlines(keepends=True)
    for index in range(max(len(old_lines), len(new_lines))):
        left = old_lines[index] if index < len(old_lines) else None
        right = new_lines[index] if index < len(new_lines) else None
        if left != right:
            return index + 1, left, right
    return 1, None, None


def check_golden(result, golden_dir):
    mismatched = False
    hashes = []
    for name, expected in golden_files(result):
        path = Path(golden_dir) / name
        actual = path.read_bytes() if path.is_file() else None
        hashes.extend((name, hashlib.sha256(expected).hexdigest()))
        if actual != expected:
            mismatched = True
            line, old, new = first_differing_line(actual, expected)
            print(f"golden sweep: MISMATCH {name} first differing line {line}")
            for label, value in (("golden", old), ("computed", new)):
                text = repr(value.decode("utf-8", errors="replace")) if value is not None else "<missing>"
                print(f"{label}: {text}")
    if mismatched:
        print("golden files change only via --update under a named decision (P09C-25)")
        return 1
    print("golden sweep: OK " + " ".join(hashes))
    return 0


def update_golden(result, golden_dir):
    golden_dir = Path(golden_dir)
    golden_dir.mkdir(parents=True, exist_ok=True)
    for name, data in golden_files(result):
        path = golden_dir / name
        old = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "absent"
        print(f"golden sweep: UPDATE {name} old {old} new {hashlib.sha256(data).hexdigest()}")
        path.write_bytes(data)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--committed", type=Path)
    parser.add_argument("--golden-dir", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--update", action="store_true")
    args = parser.parse_args(argv)
    if args.check or args.update:
        if args.out is not None or args.committed is not None:
            parser.error("--check/--update cannot be combined with --out/--committed")
        result = sweep(load_records(args.records if args.records is not None else DEFAULT_RECORDS))
        golden_dir = args.golden_dir if args.golden_dir is not None else GOLDEN_DIR
        return check_golden(result, golden_dir) if args.check else update_golden(result, golden_dir)
    if args.records is None or args.out is None or args.committed is None or args.golden_dir is not None:
        parser.error("legacy mode requires --records, --out and --committed; --golden-dir needs --check/--update")
    result = sweep(load_records(args.records))
    write_timeline(result, args.out, args.committed)
    print(json.dumps({k: v for k, v in result.items() if k != "timeline"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
