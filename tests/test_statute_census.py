"""C4-D: real metadata small sweep, owner applicability formulas and invariant sensitivity."""
import csv
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from divergence.statute_census import check_partitions, check_result, load_records, sweep
from divergence.statute_lookup import LookupResult, lookup
from divergence.statute_records import project_dates
from divergence.statute_schema import CORPUS_CHECKED_THROUGH, REPEAL_DAY

ROOT = Path(__file__).resolve().parents[1] / "divergence/statutes"


def test_small_real_sweep():
    records = [r for r in load_records(ROOT / "records") if (r["act"], r["unit"]) == ("1961", "2")]
    result = sweep(records, start=date(2024, 4, 1), end=date(2025, 4, 1), years=("2024-25",))
    assert result["records"] == 6 and result["units"] == 1
    assert result["queries"]["daily"] == 365 and result["queries"]["tax_year"] == 1
    assert result["queries"]["boundary"] > 0
    assert result["partitions"] == {"adjacencies": 5, "retro_patterns": 1}
    assert result["reasons"]["unprinted_intermediate"] > 0
    assert result["reasons"]["repeal_day_unsettled"] > 0
    assert sum(result["statuses"].values()) == sum(result["queries"].values())


@pytest.mark.parametrize("change", ["unprinted", "flagged", "horizon", "repeal", "reason"])
def test_reject_unsafe_found(change):
    record = {"record_id": "act:1961:TEST:v1", "act": "1961", "status": "in_force",
              "in_force_from": "2024-01-01", "in_force_to": None}
    point, reasons = date(2024, 6, 1), ()
    if change == "unprinted":
        record["status"] = "unprinted"
    elif change == "flagged":
        record["lookup_flags"] = ["corrigendum_open"]
    elif change == "horizon":
        point = date(2028, 1, 1)
    elif change == "repeal":
        point = REPEAL_DAY
    else:
        reasons = ("undeclared_reason",)
    result = LookupResult("FOUND", record["record_id"], (record["record_id"],), reasons)
    with pytest.raises((AssertionError, KeyError)):
        check_result([record], result, {"as_of": point})


def test_partition_rejects_gap():
    records = [r for r in load_records(ROOT / "records") if (r["act"], r["unit"]) == ("1961", "194S")]
    records[0]["in_force_to"] = "2025-03-31"
    with pytest.raises(AssertionError):
        check_partitions(records)


@pytest.mark.parametrize("unit", ["1", "2", "3", "92", "194", "301", "393", "400", "446", "509", "536"])
def test_horizon_every_2025_unit(unit):
    result = lookup(load_records(ROOT / "records"), act="2025", unit=unit,
                    as_of=CORPUS_CHECKED_THROUGH + timedelta(days=1))
    assert result == LookupResult("AMBIGUOUS", None, (), ("beyond_corpus_horizon",))


def _read_csv(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _fy(point):
    return point.year if (point.month, point.day) >= (4, 1) else point.year - 1


def _charging_years(start, end):
    # Charging law on AY 1 April maps to the preceding FY. Coverage may begin just before that April.
    first_ay = start.year + ((start.month, start.day) > (4, 1))
    last_ay = _fy(end - timedelta(days=1)) if end else None
    return first_ay - 1, last_ay - 1 if last_ay is not None else None


def _owner_year_result(row, rec, last_version):
    start = date.fromisoformat(rec["in_force_from"])
    end = date.fromisoformat(rec["in_force_to"]) if rec["in_force_to"] else None
    charging = row["basis_category"] == "charging_ay_rule"
    expected = (_charging_years(start, end) if charging
                else (_fy(start), _fy(end - timedelta(days=1)) if end else None))
    actual = tuple(int(row[field][:4]) if row[field] else None
                   for field in ("applies_from_tax_year", "applies_to_tax_year"))
    prefix, version = row["record_key"].rsplit(":v", 1)
    vd4 = charging and prefix.startswith("act:1961:") and end == REPEAL_DAY and int(version) == last_version[prefix]
    adjusted = (expected[0], 2025) if vd4 else expected
    status = "VD-4" if vd4 and actual == adjusted and actual != expected else "OK"
    return {"record_id": row["record_key"], "expected": adjusted, "actual": actual,
            "status": status if actual == adjusted else "DIFF"}


def owner_years_results():
    rows = _read_csv("VERSION-DATES.csv")
    projected = project_dates(rows, _read_csv("AMENDMENT-EFFECTS.csv"),
                              json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8")))
    last_version = {}
    for row in rows:
        prefix, version = row["record_key"].rsplit(":v", 1)
        last_version[prefix] = max(last_version.get(prefix, 0), int(version))
    results = []
    for row in rows:
        rec = projected[row["record_key"]]
        if row["basis_category"] == "unclear" or not rec["in_force_from"]:
            continue
        results.append(_owner_year_result(row, rec, last_version))
    return results


def test_owner_years_projected_ends():
    results = owner_years_results()
    assert len(results) == 24
    assert [r for r in results if r["status"] == "DIFF"] == []
    assert sum(r["status"] == "OK" for r in results) == 21
    assert {r["record_id"] for r in results if r["status"] == "VD-4"} == {
        "act:1961:3:v1", "act:1961:56:v3", "act:1961:115BBH:v1"}
