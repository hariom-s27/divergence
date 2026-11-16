"""D78 exact version lookup. Never returns the nearest version.

lookup(...) answers "which version of <act> <unit> applies at a point?" with
FOUND (exactly one record, no reasons), NO_APPLICABLE_VERSION or AMBIGUOUS.
A later version replaces an earlier one only through an explicit `supersedes` link.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from divergence.statute_schema import (
    ACT2025_COMMENCEMENT,
    CORPUS_CHECKED_THROUGH,
    REPEAL_DAY,
    SOURCE_KINDS,
    covers_date,
    intersects_dates,
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
AFTER_REPEAL = "after_repeal"
BEFORE_COMMENCEMENT = "before_commencement"
BEYOND_CORPUS_HORIZON = "beyond_corpus_horizon"
UNPRINTED_INTERMEDIATE = "unprinted_intermediate"
APPLICABILITY_UNCLEAR_ROW = "applicability_unclear_row"
KNOWN_TEXT_NOT_IN_CORPUS = "known_text_not_in_corpus"
BEFORE_COVERAGE = "before_coverage"
REPEAL_DAY_UNSETTLED = "repeal_day_unsettled"
CORRIGENDUM_OPEN = "corrigendum_open"

__all__ = [
    "FOUND", "NO_APPLICABLE_VERSION", "AMBIGUOUS",
    "MIDYEAR_EFFECT", "OVERLAP", "OUTSTANDING_EFFECT", "UNKNOWN_ENACTMENT_DATE",
    "NEVER_OPERATIVE", "PROSPECTIVE", "NO_VERSION_COVERS_POINT",
    "AFTER_REPEAL", "BEFORE_COMMENCEMENT", "BEYOND_CORPUS_HORIZON",
    "UNPRINTED_INTERMEDIATE", "APPLICABILITY_UNCLEAR_ROW", "KNOWN_TEXT_NOT_IN_CORPUS",
    "BEFORE_COVERAGE", "REPEAL_DAY_UNSETTLED", "CORRIGENDUM_OPEN",
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


def _covers(rec, point, ty_start):
    if ty_start is None:
        return covers_date(_effective_start(rec), parse_date(rec.get("in_force_to")), point)
    a_from, a_to = rec.get("applies_from_tax_year"), rec.get("applies_to_tax_year")
    return (a_from is not None and tax_year_start(a_from) <= ty_start
            and (a_to is None or ty_start <= tax_year_start(a_to)))


def _knowledge(cands, known):
    """Filter against the original unit's successor links, retaining hidden rows for fallback."""
    if known is None:
        return cands, [], set()
    successors = {r["supersedes"]: r for r in cands if r.get("supersedes")}
    kept, hidden, marked = [], [], set()
    for rec in cands:
        enacted = parse_date(rec.get("enacted_on"))
        successor = successors.get(rec["record_id"], {})
        next_enacted = parse_date(successor.get("enacted_on"))
        hindsight = rec.get("status") == "never_operative" and next_enacted is not None and next_enacted > known
        if (enacted is not None and enacted > known) or hindsight:
            hidden.append(rec)
        else:
            kept.append(rec)
            if enacted is None:
                marked.add(rec["record_id"])
    return kept, hidden, marked


def _no_coverage(cands, hidden, dated, point, fy_end, ty_start):
    if ty_start is not None:
        # The extra day deliberately includes a record starting on next 1 April.
        window_end = fy_end + timedelta(days=1)
        for field, value, reason in (("status", "unprinted", UNPRINTED_INTERMEDIATE),
                                     ("basis_category", "unclear", APPLICABILITY_UNCLEAR_ROW)):
            for rec in cands:
                if rec.get(field) == value and intersects_dates(
                        _effective_start(rec), parse_date(rec.get("in_force_to")), point, window_end):
                    return _result(AMBIGUOUS, [rec], {reason})
    if any(_covers(rec, point, ty_start) for rec in hidden):
        return _result(AMBIGUOUS, [], {KNOWN_TEXT_NOT_IN_CORPUS})
    starts = [s for rec in dated if (s := _effective_start(rec)) is not None]
    reason = BEFORE_COVERAGE if starts and point < min(starts) else NO_VERSION_COVERS_POINT
    return _result(NO_APPLICABLE_VERSION, [], {reason})


def lookup(records, *, source_kind: str = "act", act: str, unit: str,
           as_of: date | None = None, tax_year: str | None = None,
           as_known_on: date | None = None) -> LookupResult:
    """Exact lookup per D78 amendment D9; intervals are half-open."""
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
        point, fy_end = tax_year_bounds(tax_year)
        point_end = fy_end - timedelta(days=1)  # outstanding-effects rule remains unchanged
    else:
        ty_start = None
        point = point_end = as_of
        fy_end = None

    if isinstance(records, Mapping):
        records = records.values()

    # Step 1: same source_kind, act, unit.
    cands = [r for r in records
             if r.get("source_kind") == source_kind and r.get("act") == act and r.get("unit") == unit]
    reasons: set = set()
    dated = cands

    # Steps 2-3: Act edges precede the corpus horizon and the knowledge clock.
    if act == "1961" and point >= REPEAL_DAY:
        exception = (tax_year is None and point == REPEAL_DAY
                     and any(parse_date(r.get("in_force_from")) == REPEAL_DAY for r in cands))
        if not exception:
            return _result(NO_APPLICABLE_VERSION, [], {AFTER_REPEAL})
    if act == "2025" and point < ACT2025_COMMENCEMENT:
        return _result(NO_APPLICABLE_VERSION, [], {BEFORE_COMMENCEMENT})
    if point > CORPUS_CHECKED_THROUGH:
        return _result(AMBIGUOUS, [], {BEYOND_CORPUS_HORIZON})

    # Step 4: knowledge clock and never-operative hindsight.
    cands, hidden, marked = _knowledge(cands, as_known_on)

    # Step 5: never operative; prospective rule unchanged.
    before = len(cands)
    cands = [r for r in cands if r.get("status") != "never_operative"]
    if not cands and before:
        return _result(NO_APPLICABLE_VERSION, [], {NEVER_OPERATIVE})

    # Prospective with no commencement date.
    before = len(cands)
    cands = [r for r in cands if not (r.get("status") == "prospective" and r.get("in_force_from") is None)]
    if not cands and before:
        return _result(NO_APPLICABLE_VERSION, [], {PROSPECTIVE})

    # Step 6: preserve visible dated rows for the no-coverage fallback.
    visible = cands
    cands = [r for r in cands if _covers(r, point, ty_start)]

    # Step 7: explicit supersession and surviving unknown-enactment marks.
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

    # Step 8: only non-charging rows can introduce a mid-year reason.
    if tax_year is not None:
        for r in cands:
            if r.get("basis_category") == "charging_ay_rule":
                continue
            start = _effective_start(r)
            end = parse_date(r.get("in_force_to"))
            if start is not None and point < start < fy_end:
                reasons.add(MIDYEAR_EFFECT)
            if end is not None and point < end < fy_end:
                reasons.add(MIDYEAR_EFFECT)

    # Step 9: outstanding effects, unprinted text, and owner lookup flags.
    for r in cands:
        if r.get("status") == "unprinted":
            reasons.add(UNPRINTED_INTERMEDIATE)
        reasons.update(r.get("lookup_flags") or ())
        for eff in r.get("outstanding_effects") or ():
            affects = parse_date(eff.get("affects_from"))
            if affects is None or affects <= point_end:
                reasons.add(OUTSTANDING_EFFECT)

    # Steps 10-11: ordered no-coverage fallback, then ambiguity or exact result.
    if not cands:
        return _no_coverage(visible, hidden, dated, point, fy_end, ty_start)
    if len(cands) > 1:
        return _result(AMBIGUOUS, cands, reasons | {OVERLAP})
    if reasons:
        return _result(AMBIGUOUS, cands, reasons)
    return _result(FOUND, cands, reasons)
