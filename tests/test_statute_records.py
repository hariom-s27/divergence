"""C4: committed metadata only; no test reads local bodies or extraction evidence."""
import copy
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from divergence.statute_lookup import AMBIGUOUS, FOUND, NO_APPLICABLE_VERSION, LookupResult, lookup
from divergence.statute_records import parse_basis_exceptions, project, registered_url
from divergence.statute_schema import body_sha256

ROOT = Path(__file__).resolve().parents[1] / "divergence" / "statutes"


def _csv(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


@pytest.fixture(scope="module")
def inputs():
    return (_csv("VERSION-DATES.csv"), _csv("AMENDMENT-EFFECTS.csv"),
            json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8")), _csv("MAPPING.csv"))


@pytest.fixture(scope="module")
def records(inputs):
    return project(*inputs, knowledge=None, fetch_log=None, dispositions=_csv("CORRIGENDUM-DISPOSITION.csv"))


# Exact C4-A Step 5 owner-approved results. Candidate versions, not merely status, are checked.
CASES = [
    ("1961", "2", "as_of", "2023-03-31", None, "N", (), ("before_coverage",)),
    ("1961", "2", "as_of", "2023-04-01", None, "F", (1,), ()),
    ("1961", "2", "as_of", "2024-03-31", None, "F", (1,), ()),
    ("1961", "2", "as_of", "2024-04-01", None, "A", (2,), ("unprinted_intermediate",)),
    ("1961", "2", "as_of", "2024-07-23", None, "A", (3,), ("unprinted_intermediate",)),
    ("1961", "2", "as_of", "2024-10-01", None, "F", (4,), ()),
    ("1961", "2", "as_of", "2026-03-31", None, "F", (5,), ()),
    ("1961", "2", "as_of", "2026-04-01", None, "A", (6,), ("repeal_day_unsettled",)),
    ("1961", "2", "as_of", "2026-04-02", None, "N", (), ("after_repeal",)),
    ("1961", "56", "as_of", "2024-04-01", None, "F", (2,), ()),
    ("1961", "56", "as_of", "2026-04-01", None, "N", (), ("after_repeal",)),
    ("1961", "158B", "as_of", "2025-02-01", None, "F", (3,), ()),
    ("1961", "158B", "as_of", "2025-02-15", "2025-03-01", "F", (2,), ()),
    ("1961", "158B", "as_of", "2025-02-15", "2025-04-01", "F", (3,), ()),
    ("1961", "194S", "as_of", "2022-06-30", None, "N", (), ("before_coverage",)),
    ("1961", "285BAA", "as_of", "2026-04-01", None, "A", (1,), ("repeal_day_unsettled",)),
    ("2025", "393", "as_of", "2026-03-31", None, "N", (), ("before_commencement",)),
    ("2025", "393", "as_of", "2026-04-01", None, "F", (2,), ()),
    ("2025", "393", "as_of", "2026-06-01", "2026-03-01", "A", (), ("known_text_not_in_corpus",)),
    ("1961", "2", "as_of", "2023-05-01", "2023-03-30", "A", (), ("known_text_not_in_corpus",)),
    ("1961", "3", "as_of", "2024-05-01", "2024-01-01", "A", (1,), ("unknown_enactment_date",)),
    ("1961", "3", "tax_year", "2022-23", None, "F", (1,), ()),
    ("1961", "194S", "tax_year", "2022-23", None, "A", (1,), ("midyear_effect",)),
    ("1961", "2", "tax_year", "2023-24", None, "A", (2,), ("unprinted_intermediate",)),
    ("1961", "2", "tax_year", "2024-25", None, "A", (4, 5), ("midyear_effect", "overlap")),
    ("1961", "56", "tax_year", "2025-26", None, "F", (3,), ()),
    ("1961", "158B", "tax_year", "2021-22", None, "N", (), ("before_coverage",)),
    ("1961", "158B", "tax_year", "2022-23", None, "A", (1,), ("applicability_unclear_row",)),
    ("1961", "285BAA", "tax_year", "2026-27", None, "N", (), ("after_repeal",)),
    ("2025", "1", "tax_year", "2025-26", None, "N", (), ("before_commencement",)),
    ("2025", "393", "tax_year", "2026-27", None, "F", (2,), ()),
    ("2025", "1", "as_of", "2026-11-16", None, "A", (), ("beyond_corpus_horizon",)),
]


@pytest.mark.parametrize("case", CASES, ids=[f"{n:02d}" for n in range(1, 33)])
def test_spec_case(records, case):
    act, unit, mode, point, known, status, versions, reasons = case
    candidates = tuple(f"act:{act}:{unit}:v{n}" for n in versions)
    expected_status = {"F": FOUND, "A": AMBIGUOUS, "N": NO_APPLICABLE_VERSION}[status]
    kwargs = {mode: date.fromisoformat(point) if mode == "as_of" else point}
    result = lookup(records, act=act, unit=unit, as_known_on=date.fromisoformat(known) if known else None, **kwargs)
    assert result == LookupResult(expected_status, candidates[0] if status == "F" else None, candidates, reasons)


@pytest.fixture(scope="module")
def real_records():
    paths = sorted((ROOT / "records").glob("*/*.json"))
    assert len(paths) == 34
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


@pytest.mark.parametrize("case", CASES, ids=[f"{n:02d}" for n in range(1, 33)])
def test_real_spec_case(real_records, case):
    test_spec_case(real_records, case)


def test_project_counts_real_tables(records):
    assert len(records) == 34
    assert Counter(r["status"] for r in records) == {
        "in_force": 20, "repealed_saved": 6, "never_operative": 5, "unprinted": 3}
    assert sum(bool(r["retrospective_from"]) for r in records) == 2
    amendments = [a for r in records for a in r["amended_by"]]
    assert len(amendments) == 127
    assert sum(a["url"] == "" for a in amendments) == 0


def test_all_34_supersedes_links(records):
    assert len(records) == 34
    ids = {r["record_id"] for r in records}
    for rec in records:
        n = rec["version_id"]
        expected = f"{rec['source_kind']}:{rec['act']}:{rec['unit']}:v{n - 1}" if n > 1 else None
        assert rec["supersedes"] == expected
        assert expected is None or expected in ids


def test_projection_is_pure(inputs):
    baseline = copy.deepcopy(inputs)
    first = project(*inputs, knowledge=None, fetch_log=None)
    assert inputs == baseline
    assert first == project(*inputs, knowledge=None, fetch_log=None)


def test_cumulative_registered_provenance(inputs, records):
    vd, effects, sources, _ = inputs
    registry = {r["key"]: r for r in sources["items"] + sources["manual"]}
    rows = {r["record_key"]: r for r in vd}
    for rec in records:
        start = rows[rec["record_id"]]["in_force_from"]
        state = [e for e in effects if e["target_act"] == rec["act"] and e["target_section"] == rec["unit"]
                 and start and e["wef"] and e["wef"] <= start]
        assert {a["ref"] for a in rec["amended_by"]} == {e["effect_id"] for e in state}
        for amendment in rec["amended_by"]:
            item = registry[amendment["ref"].split(":")[0]]
            assert amendment["kind"] == "finance_act"
            assert amendment["url"] == registered_url(item)
            assert not amendment["url"] or amendment["url"] in (item.get("url", "") + item.get("where", ""))
            assert amendment["operation"] in {"substitute", "insert", "omit", "renumber"}


def test_retro_dates_and_registered_assent(inputs, records):
    by_id = {r["record_id"]: r for r in records}
    assert {r["record_id"] for r in records if r["retrospective_from"]} == {"act:1961:2:v3", "act:1961:158B:v3"}
    for rec in records:
        if rec["retrospective_from"]:
            assert rec["in_force_from"] == by_id[rec["supersedes"]]["in_force_to"] == rec["enacted_on"]
    original = next(r for r in inputs[2]["manual"] if r["key"] == "ita2025_gz")
    assert original["assent_date"] == "2025-08-21"
    assert by_id["act:2025:1:v1"]["enacted_on"] == original["assent_date"]
    assert by_id["act:1961:3:v1"]["enacted_on"] is None


def test_owner_target_never_changes_section(inputs):
    changed = copy.deepcopy(inputs)
    rows = [r for r in changed[1] if r.get("owner_target")]
    assert len(rows) == 2
    assert [r["target_section"] for r in rows] == ["56", "2"]
    actual = project(*changed, knowledge=None, fetch_log=None)
    for effect in rows:
        containers = [r for r in actual if any(a["ref"] == effect["effect_id"] for a in r["amended_by"])]
        assert containers and all(r["unit"] == effect["target_section"] for r in containers)
    rows[0]["owner_target"] = "section 999 > clause (1)"
    with pytest.raises(ValueError, match="owner_target changes section"):
        project(*changed, knowledge=None, fetch_log=None)


def test_basis_exceptions_strict(inputs, records):
    exceptions = [x for r in records for x in r["basis_exceptions"]]
    assert exceptions == [{"effect_id": "fa_2023:s3(a)", "category": "procedural"},
                          {"effect_id": "fa_2023:s3(c)", "category": "procedural"},
                          {"effect_id": "fa_2023:s3(d)", "category": "transaction_date"}]
    effects = {e["effect_id"]: e for e in inputs[1]}
    for text in ("except UNKNOWN=procedural", "except fa_2023:s3(a)=UNKNOWN", "except", "except x"):
        with pytest.raises(ValueError):
            parse_basis_exceptions(text, effects)


def test_knowledge_and_fetch_are_arguments(inputs, records):
    # Synthetic dates/provenance, deliberately not read from local evidence.
    knowledge = {r["key"]: "2026-01-01" for r in inputs[2]["items"]}
    fetch = {"entries": [{"key": "ita1961_2026", "url": "https://example.invalid/fake-edition",
                          "finished_at": "2026-01-02T00:00:00+05:30"}]}
    actual = project(*inputs, knowledge=knowledge, fetch_log=fetch)
    for rec in actual:
        if rec["status"] == "unprinted":
            assert rec["text_current_as_of"] == "2026-01-01"
            assert rec["body"] is rec["body_sha256"] is rec["body_chars"] is None
            if rec["act"] == "1961":
                assert rec["source_url"] == fetch["entries"][0]["url"]
                assert rec["retrieved_at"] == fetch["entries"][0]["finished_at"]
        if rec["status"] == "never_operative":
            successor = next(r for r in actual if r["supersedes"] == rec["record_id"])
            assert rec["text_current_as_of"] == successor["enacted_on"]
            assert rec["body"] == "" and rec["body_sha256"] == body_sha256("") and rec["body_chars"] == 0
            assert rec["original_note"] and rec["in_force_from"] is rec["in_force_to"] is None
    assert [r["amended_by"] for r in actual] == [r["amended_by"] for r in records]


def test_counterparts_label_gaps_and_flags(records):
    expected_gaps = {"act:1961:2:v1", "act:1961:56:v1", "act:1961:56:v2"}
    assert {r["record_id"] for r in records if "source_label_gap" in r.get("notes", "")} == expected_gaps
    for rec in records:
        assert rec["storage_mode"] == "local_only" and rec["outstanding_effects"] == []
        assert set(rec["lookup_flags"]) <= {"repeal_day_unsettled", "corrigendum_open"}
        cp = rec["counterpart"]
        if rec["act"] == "2025":
            assert cp is None
        else:
            assert cp["source_url"] == ""
            assert cp["source"] == ("CBDT_official" if rec["unit"] == "194S" else "SECONDARY")
            if rec["unit"] == "194S":
                assert cp["ref"] == "act:2025:393"
                assert cp["notes"] == (
                    "official Act PDF, owner eye check; ITD utility (tool-assisted) also lists 393;397;400")
            if rec["unit"] == "115BBH":
                assert cp["ref"] == "act:2025:194"
                assert cp["notes"] == (
                    "matches ITD 1961-2025 utility (tool-assisted, 2026-11-19): Table Sl. No. 4; "
                    "corroborated by 2 secondary sources; not eye-checked in Act text")
