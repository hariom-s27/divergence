"""D78 exact lookup against the FAKE fixtures. One test per P08 D7 expectation, plus edge cases."""
import copy
import dataclasses
from datetime import date
from pathlib import Path

import pytest

from divergence.statute_lookup import (
    AMBIGUOUS,
    FOUND,
    NO_APPLICABLE_VERSION,
    LookupResult,
    index_records,
    lookup,
    modifications,
)
from divergence.statute_schema import load_record

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "statutes"
RECORDS = [load_record(p) for p in sorted((FIXTURES / "records").rglob("*.json"))]
INDEX = index_records(RECORDS)


def _with(record_id, **changes):
    """Records list where one record is a modified in-memory copy (fixture files untouched)."""
    out = []
    for r in RECORDS:
        if r["record_id"] == record_id:
            r = copy.deepcopy(r)
            r.update(changes)
        out.append(r)
    return out


def _found(res, record_id):
    assert res == LookupResult(FOUND, record_id, (record_id,), ())


# ---- F1 ----
def test_f1_tax_year_2026_27_found():
    _found(lookup(RECORDS, act="2025", unit="sFAKE1", tax_year="2026-27"), "act:2025:sFAKE1:v1")


def test_f1_as_of_2026_03_31_no_version_not_nearest():
    res = lookup(RECORDS, act="2025", unit="sFAKE1", as_of=date(2026, 3, 31))
    assert res == LookupResult(NO_APPLICABLE_VERSION, None, (), ("no_version_covers_point",))


# ---- F2 ----
def test_f2_2024_25_found():
    _found(lookup(RECORDS, act="1961", unit="sFAKE2", tax_year="2024-25"), "act:1961:sFAKE2:v1")


def test_f2_2026_27_no_version():
    res = lookup(RECORDS, act="1961", unit="sFAKE2", tax_year="2026-27")
    assert res.status == NO_APPLICABLE_VERSION and res.record_id is None
    assert res.reasons == ("no_version_covers_point",)


# ---- F3 ----
def test_f3_never_operative_tax_year():
    res = lookup(RECORDS, act="1961", unit="sFAKE3", tax_year="2020-21")
    assert res == LookupResult(NO_APPLICABLE_VERSION, None, (), ("never_operative",))


def test_f3_never_operative_as_of():
    res = lookup(RECORDS, act="1961", unit="sFAKE3", as_of=date(2020, 6, 1))
    assert res == LookupResult(NO_APPLICABLE_VERSION, None, (), ("never_operative",))


def test_f3_never_operative_with_as_known_on():
    # F3 has enacted_on null: kept and marked at step 2, then dropped at step 3 (owner clarification).
    res = lookup(RECORDS, act="1961", unit="sFAKE3", tax_year="2020-21", as_known_on=date(2026, 1, 1))
    assert res == LookupResult(NO_APPLICABLE_VERSION, None, (), ("never_operative",))


# ---- F4 ----
def test_f4_2020_21_found_v2():
    _found(lookup(RECORDS, act="1961", unit="sFAKE4", tax_year="2020-21"), "act:1961:sFAKE4:v2")


def test_f4_2020_21_as_known_on_2025_01_01_found_v1():
    res = lookup(RECORDS, act="1961", unit="sFAKE4", tax_year="2020-21", as_known_on=date(2025, 1, 1))
    _found(res, "act:1961:sFAKE4:v1")


def test_f4_2016_17_found_v1():
    _found(lookup(RECORDS, act="1961", unit="sFAKE4", tax_year="2016-17"), "act:1961:sFAKE4:v1")


# ---- F5 ----
def test_f5_tax_year_ambiguous_midyear_overlap():
    res = lookup(RECORDS, act="2025", unit="sFAKE5", tax_year="2026-27")
    assert res == LookupResult(AMBIGUOUS, None, ("act:2025:sFAKE5:v1", "act:2025:sFAKE5:v2"),
                               ("midyear_effect", "overlap"))


def test_f5_as_of_2026_05_01_found_v1():
    _found(lookup(RECORDS, act="2025", unit="sFAKE5", as_of=date(2026, 5, 1)), "act:2025:sFAKE5:v1")


def test_f5_as_of_2026_09_01_found_v2():
    _found(lookup(RECORDS, act="2025", unit="sFAKE5", as_of=date(2026, 9, 1)), "act:2025:sFAKE5:v2")


# ---- F6 ----
def test_f6_prospective():
    res = lookup(RECORDS, act="2025", unit="sFAKE6", tax_year="2026-27")
    assert res == LookupResult(NO_APPLICABLE_VERSION, None, (), ("prospective",))


# ---- F7 ----
def test_f7_modifications_of_f1():
    res = lookup(RECORDS, act="2025", unit="sFAKE1", tax_year="2026-27")
    assert res.status == FOUND  # modified_by does not change the status
    mods = modifications(INDEX[res.record_id], INDEX)
    assert [m["record_id"] for m in mods] == ["circular:2025:FAKE-CIRC-1:v1"]
    _found(lookup(RECORDS, source_kind="circular", act="2025", unit="FAKE-CIRC-1", as_of=date(2026, 7, 1)),
           "circular:2025:FAKE-CIRC-1:v1")


# ---- F8 ----
def test_f8_as_of_2026_06_01_found():
    _found(lookup(RECORDS, act="2025", unit="sFAKE8", as_of=date(2026, 6, 1)), "act:2025:sFAKE8:v1")


def test_f8_as_of_2026_11_01_outstanding():
    res = lookup(RECORDS, act="2025", unit="sFAKE8", as_of=date(2026, 11, 1))
    assert res == LookupResult(AMBIGUOUS, None, ("act:2025:sFAKE8:v1",), ("outstanding_effect",))


def test_f8_tax_year_outstanding():
    res = lookup(RECORDS, act="2025", unit="sFAKE8", tax_year="2026-27")
    assert res == LookupResult(AMBIGUOUS, None, ("act:2025:sFAKE8:v1",), ("outstanding_effect",))


# ---- edge cases ----
@pytest.mark.parametrize("kwargs", [{}, {"as_of": date(2026, 6, 1), "tax_year": "2026-27"}])
def test_requires_exactly_one_point(kwargs):
    with pytest.raises(ValueError):
        lookup(RECORDS, act="2025", unit="sFAKE1", **kwargs)


@pytest.mark.parametrize("bad", ["2026-28", "2026", "26-27"])
def test_bad_tax_year_raises(bad):
    with pytest.raises(ValueError):
        lookup(RECORDS, act="2025", unit="sFAKE1", tax_year=bad)


def test_unknown_unit_no_version():
    res = lookup(RECORDS, act="2025", unit="sNOPE", tax_year="2026-27")
    assert res == LookupResult(NO_APPLICABLE_VERSION, None, (), ("no_version_covers_point",))


def test_unknown_enactment_date_blocks_found():
    recs = _with("act:2025:sFAKE1:v1", enacted_on=None)
    res = lookup(recs, act="2025", unit="sFAKE1", tax_year="2026-27", as_known_on=date(2026, 12, 1))
    assert res == LookupResult(AMBIGUOUS, None, ("act:2025:sFAKE1:v1",), ("unknown_enactment_date",))


def test_unknown_enactment_on_superseded_version_does_not_block():
    recs = _with("act:1961:sFAKE4:v1", enacted_on=None)
    res = lookup(recs, act="1961", unit="sFAKE4", tax_year="2020-21", as_known_on=date(2026, 12, 1))
    _found(res, "act:1961:sFAKE4:v2")


def test_outstanding_effect_without_date_is_ambiguous():
    eff = [{"ref": "FAKE pending", "kind": "other", "affects_from": None, "note": "FAKE"}]
    recs = _with("act:2025:sFAKE8:v1", outstanding_effects=eff)
    res = lookup(recs, act="2025", unit="sFAKE8", as_of=date(2026, 6, 1))
    assert res == LookupResult(AMBIGUOUS, None, ("act:2025:sFAKE8:v1",), ("outstanding_effect",))


def test_supersession_needs_explicit_link():
    recs = _with("act:1961:sFAKE4:v2", supersedes=None)
    res = lookup(recs, act="1961", unit="sFAKE4", tax_year="2020-21")
    assert res == LookupResult(AMBIGUOUS, None, ("act:1961:sFAKE4:v1", "act:1961:sFAKE4:v2"), ("overlap",))


def test_result_is_frozen():
    res = lookup(RECORDS, act="2025", unit="sFAKE1", tax_year="2026-27")
    with pytest.raises(dataclasses.FrozenInstanceError):
        res.status = AMBIGUOUS


def test_index_rejects_duplicates():
    with pytest.raises(ValueError):
        index_records(RECORDS + [RECORDS[0]])
