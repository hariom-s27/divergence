"""D78 exact version lookup. Never returns the nearest version.

lookup(...) answers "which version of <act> <unit> applies at a point?" with
FOUND (exactly one record, no reasons), NO_APPLICABLE_VERSION or AMBIGUOUS.
A later version replaces an earlier one only through an explicit `supersedes` link.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime

from divergence.statute_schema import (
    SOURCE_KINDS,
    modifications,
    parse_date,
    tax_year_bounds,
    tax_year_start,
)

FOUND = "FOUND"
NO_APPLICABLE_VERSION = "NO_APPLICABLE_VERSION"
AMBIGUOUS = "AMBIGUOUS"

MIDYEAR_EFFECT = "midyear_effect"
OVERLAP = "overlap"
OUTSTANDING_EFFECT = "outstanding_effect"
UNKNOWN_ENACTMENT_DATE = "unknown_enactment_date"
NEVER_OPERATIVE = "never_operative"
PROSPECTIVE = "prospective"
NO_VERSION_COVERS_POINT = "no_version_covers_point"

__all__ = [
    "FOUND", "NO_APPLICABLE_VERSION", "AMBIGUOUS",
    "MIDYEAR_EFFECT", "OVERLAP", "OUTSTANDING_EFFECT", "UNKNOWN_ENACTMENT_DATE",
    "NEVER_OPERATIVE", "PROSPECTIVE", "NO_VERSION_COVERS_POINT",
    "LookupResult", "index_records", "lookup", "modifications",
]


@dataclass(frozen=True)
class LookupResult:
    status: str
    record_id: str | None
    candidates: tuple
    reasons: tuple


def index_records(records) -> dict:
    """record_id -> record. Raises ValueError on a duplicate record_id."""
    index: dict = {}
    for rec in records:
        rid = rec["record_id"]
        if rid in index:
            raise ValueError(f"duplicate record_id: {rid}")
        index[rid] = rec
    return index


def _effective_start(rec: dict) -> date | None:
    """retrospective_from if set, else in_force_from."""
    return parse_date(rec.get("retrospective_from")) or parse_date(rec.get("in_force_from"))


def _result(status: str, remaining: list, reasons: set) -> LookupResult:
    ids = tuple(sorted(r["record_id"] for r in remaining))
    rid = ids[0] if status == FOUND else None
    return LookupResult(status, rid, ids, tuple(sorted(reasons)))


def lookup(records, *, source_kind: str = "act", act: str, unit: str,
           as_of: date | None = None, tax_year: str | None = None,
           as_known_on: date | None = None) -> LookupResult:
    """Exact lookup as specified in DECISION-D78 / P08 D5 (with the owner's step-2 clarification)."""
    if (as_of is None) == (tax_year is None):
        raise ValueError("give exactly one of as_of or tax_year")
    if as_of is not None and (isinstance(as_of, datetime) or not isinstance(as_of, date)):
        raise ValueError(f"as_of must be a datetime.date: {as_of!r}")
    if as_known_on is not None and (isinstance(as_known_on, datetime) or not isinstance(as_known_on, date)):
        raise ValueError(f"as_known_on must be a datetime.date: {as_known_on!r}")
    if source_kind not in SOURCE_KINDS:
        raise ValueError(f"source_kind must be one of {SOURCE_KINDS}: {source_kind!r}")
    if not act or not unit:
        raise ValueError("act and unit are required")

    if tax_year is not None:
        ty_start = tax_year_start(tax_year)
        point, point_end = tax_year_bounds(tax_year)  # 1 April .. 31 March
    else:
        ty_start = None
        point = point_end = as_of

    if isinstance(records, Mapping):
        records = records.values()

    # Step 1: same source_kind, act, unit.
    cands = [r for r in records
             if r.get("source_kind") == source_kind and r.get("act") == act and r.get("unit") == unit]
    reasons: set = set()

    # Step 2: knowledge clock. Drop records enacted after as_known_on; keep and mark unknown dates.
    marked: set = set()
    if as_known_on is not None:
        kept = []
        for r in cands:
            enacted = parse_date(r.get("enacted_on"))
            if enacted is None:
                marked.add(r["record_id"])
                kept.append(r)
            elif enacted <= as_known_on:
                kept.append(r)
        cands = kept

    # Step 3: never operative.
    before = len(cands)
    cands = [r for r in cands if r.get("status") != "never_operative"]
    if not cands and before:
        return _result(NO_APPLICABLE_VERSION, [], {NEVER_OPERATIVE})

    # Step 4: prospective with no commencement date.
    before = len(cands)
    cands = [r for r in cands if not (r.get("status") == "prospective" and r.get("in_force_from") is None)]
    if not cands and before:
        return _result(NO_APPLICABLE_VERSION, [], {PROSPECTIVE})

    # Steps 5-7: coverage of the query point. A null start never covers (no -infinity).
    covering = []
    for r in cands:
        if as_of is not None:
            start = _effective_start(r)
            end = parse_date(r.get("in_force_to"))
            if start is not None and start <= as_of and (end is None or as_of <= end):
                covering.append(r)
        else:
            a_from = r.get("applies_from_tax_year")
            a_to = r.get("applies_to_tax_year")
            if a_from is None:
                continue
            if tax_year_start(a_from) <= ty_start and (a_to is None or ty_start <= tax_year_start(a_to)):
                covering.append(r)
    cands = covering

    # Step 8: supersession, only through explicit links, only once the newer version has started.
    dropped = set()
    for y in cands:
        target = y.get("supersedes")
        y_start = _effective_start(y)
        if target and y_start is not None and y_start <= point:
            dropped.add(target)
    cands = [r for r in cands if r["record_id"] not in dropped]

    # After supersession: a surviving candidate with an unknown enactment date blocks FOUND.
    if any(r["record_id"] in marked for r in cands):
        reasons.add(UNKNOWN_ENACTMENT_DATE)

    # Step 9 (tax_year only): change inside the tax year.
    if tax_year is not None:
        for r in cands:
            start = _effective_start(r)
            end = parse_date(r.get("in_force_to"))
            if start is not None and point < start <= point_end:
                reasons.add(MIDYEAR_EFFECT)
            if end is not None and point <= end < point_end:
                reasons.add(MIDYEAR_EFFECT)

    # Step 10: known amendments not yet applied to the stored text.
    for r in cands:
        for eff in r.get("outstanding_effects") or ():
            affects = parse_date(eff.get("affects_from"))
            if affects is None or affects <= point_end:
                reasons.add(OUTSTANDING_EFFECT)

    # Step 11: result.
    if not cands:
        return _result(NO_APPLICABLE_VERSION, [], reasons | {NO_VERSION_COVERS_POINT})
    if len(cands) > 1:
        return _result(AMBIGUOUS, cands, reasons | {OVERLAP})
    if reasons:
        return _result(AMBIGUOUS, cands, reasons)
    return _result(FOUND, cands, reasons)
