"""D78 exact lookup against FAKE fixtures; old P08 intent plus C4-B edges.

Inclusive fixture ends shifted to half-open in C4-B:
1961 sFAKE2 v1, sFAKE4 v1 and v2: 2026-03-31 -> 2026-04-01.
2025 sFAKE5 v1: 2026-08-16 -> 2026-08-17. Bodies are unchanged.
"""
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
    assert res == LookupResult(NO_APPLICABLE_VERSION, None, (), ("before_commencement",))


# ---- F2 ----
def test_f2_2024_25_found():
    _found(lookup(RECORDS, act="1961", unit="sFAKE2", tax_year="2024-25"), "act:1961:sFAKE2:v1")


def test_f2_2026_27_no_version():
    res = lookup(RECORDS, act="1961", unit="sFAKE2", tax_year="2026-27")
    assert res.status == NO_APPLICABLE_VERSION and res.record_id is None
    assert res.reasons == ("after_repeal",)


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


def _synthetic(**changes):
    rec = copy.deepcopy(INDEX["act:2025:sFAKE1:v1"])
    rec.update(modified_by=[], in_force_from="2026-05-01", in_force_to="2026-05-03",
               applies_from_tax_year=None, applies_to_tax_year=None, basis_category="procedural")
    rec.update(changes)
    return rec


def _query(recs, point="2026-05-01", **kwargs):
    return lookup(recs, act=recs[0]["act"], unit=recs[0]["unit"],
                  **({"as_of": date.fromisoformat(point)} if "tax_year" not in kwargs else {}), **kwargs)


def test_half_open_start_last_end_days():
    rec = _synthetic()
    assert _query([rec]).status == FOUND
    assert _query([rec], "2026-05-02").status == FOUND
    assert _query([rec], "2026-05-03").reasons == ("no_version_covers_point",)
    assert _query([rec], "2026-04-30").reasons == ("before_coverage",)


def test_null_start_never_covers():
    assert _query([_synthetic(in_force_from=None, in_force_to=None)]).status == NO_APPLICABLE_VERSION


def test_repeal_day_exception_is_unit_specific():
    rec = _synthetic(act="1961", in_force_from="2026-04-01", in_force_to="2026-04-02",
                     lookup_flags=["repeal_day_unsettled"])
    assert _query([rec], "2026-04-01").reasons == ("repeal_day_unsettled",)
    assert _query([rec], "2026-04-02").reasons == ("after_repeal",)
    assert _query([rec], tax_year="2026-27").reasons == ("after_repeal",)
    other = dict(rec, unit="other", in_force_from="2025-04-01")
    result = lookup([rec, other], act="1961", unit="other", as_of=date(2026, 4, 1))
    assert result.reasons == ("after_repeal",)


def test_horizon_and_edge_order():
    rec = _synthetic(in_force_to=None)
    assert _query([rec], "2026-11-15").status == FOUND
    assert _query([rec], "2026-11-16").reasons == ("beyond_corpus_horizon",)
    assert _query([dict(rec, act="1961")], "2026-11-16").reasons == ("after_repeal",)
    assert _query([rec], "2026-03-31").reasons == ("before_commencement",)


def test_retro_with_knowledge_clock_fixture():
    rec = copy.deepcopy(INDEX["act:1961:sFAKE4:v2"])
    point = date.fromisoformat(rec["retrospective_from"])
    old = INDEX["act:1961:sFAKE4:v1"]
    before = lookup([old, rec], act="1961", unit="sFAKE4", as_of=point, as_known_on=date(2025, 1, 1))
    after = lookup([old, rec], act="1961", unit="sFAKE4", as_of=point, as_known_on=date(2026, 4, 1))
    assert before.record_id == old["record_id"]
    assert after.record_id == rec["record_id"]


def test_never_operative_hindsight():
    original = _synthetic(status="never_operative", in_force_from=None, in_force_to=None, enacted_on="2025-08-21")
    successor = _synthetic(record_id="act:2025:sFAKE1:v2", version_id=2, supersedes=original["record_id"],
                           in_force_to=None, enacted_on="2026-03-30")
    result = _query([original, successor], as_known_on=date(2026, 3, 1))
    assert result == LookupResult(AMBIGUOUS, None, (), ("known_text_not_in_corpus",))
    assert _query([original], as_known_on=date(2026, 3, 1)).reasons == ("never_operative",)


def test_tax_year_fallback_window_edges():
    for start, end, covers in (("2026-03-01", "2026-04-01", False),
                               ("2026-04-01", "2026-04-02", True),
                               ("2027-04-01", None, True), ("2027-04-02", None, False)):
        rec = _synthetic(status="unprinted", in_force_from=start, in_force_to=end)
        result = _query([rec], tax_year="2026-27")
        assert (result.reasons == ("unprinted_intermediate",)) == covers


def test_fallback_unprinted_precedes_unclear():
    unclear = _synthetic(basis_category="unclear")
    unprinted = dict(unclear, record_id="act:2025:sFAKE1:v2", status="unprinted")
    result = _query([unclear, unprinted], tax_year="2026-27")
    assert result.candidates == (unprinted["record_id"],)
    assert result.reasons == ("unprinted_intermediate",)
    assert _query([unclear], tax_year="2026-27").reasons == ("applicability_unclear_row",)


def test_charging_skips_midyear_and_strict_fy_edges():
    rec = _synthetic(applies_from_tax_year="2026-27", applies_to_tax_year="2026-27")
    assert _query([rec], tax_year="2026-27").reasons == ("midyear_effect",)
    assert _query([dict(rec, basis_category="charging_ay_rule")], tax_year="2026-27").status == FOUND
    for start, end in (("2026-04-01", "2027-04-01"), ("2026-03-01", "2026-04-01")):
        assert _query([dict(rec, in_force_from=start, in_force_to=end)], tax_year="2026-27").status == FOUND


def test_before_coverage_and_internal_gap():
    first = _synthetic()
    last = dict(first, record_id="act:2025:sFAKE1:v2", in_force_from="2026-06-01", in_force_to=None)
    assert _query([first, last], "2026-04-30").reasons == ("before_coverage",)
    assert _query([first, last], "2026-05-15").reasons == ("no_version_covers_point",)


def test_hidden_text_and_unknown_enactment_marks():
    rec = _synthetic(enacted_on="2026-05-02")
    assert _query([rec], as_known_on=date(2026, 5, 1)).reasons == ("known_text_not_in_corpus",)
    unknown = dict(rec, enacted_on=None)
    assert _query([unknown]).status == FOUND
    assert _query([unknown], as_known_on=date(2026, 5, 1)).reasons == ("unknown_enactment_date",)


def test_reason_class_covers_every_emitted_reason():
    from divergence import statute_lookup as module
    from divergence.statute_schema import LOOKUP_FLAGS, REASON_CLASS, reason_class
    statuses = {FOUND, AMBIGUOUS, NO_APPLICABLE_VERSION}
    exported = {getattr(module, name) for name in module.__all__ if name.isupper()} - statuses
    assert exported == set(REASON_CLASS)
    assert set(LOOKUP_FLAGS) <= exported
    for reason in exported:
        assert reason_class(reason) in {"LEGAL", "QUERY", "CORPUS", "NO_LAW"}
