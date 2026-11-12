"""D78: statute_schema helpers and the JSON Schema file (FAKE fixtures only)."""
import hashlib
import json
import unicodedata
from datetime import date
from pathlib import Path

import jsonschema
import pytest

from divergence.statute_schema import (
    SCHEMA_PATH,
    body_filename,
    body_sha256,
    build_record_id,
    get_span,
    load_record,
    load_schema,
    modifications,
    record_filename,
    schema_errors,
    tax_year_bounds,
    tax_year_start,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "statutes"


def _all_records():
    return [load_record(p) for p in sorted((FIXTURES / "records").rglob("*.json"))]


def test_build_record_id():
    assert build_record_id("act", "1961", "s194S", 1) == "act:1961:s194S:v1"
    assert build_record_id("circular", "2025", "CBDT-12-2026", 3) == "circular:2025:CBDT-12-2026:v3"
    for bad in (("statute", "1961", "s1", 1), ("act", "1962", "s1", 1),
                ("act", "1961", "s 1", 1), ("act", "1961", "s1", 0), ("act", "1961", "s1", True)):
        with pytest.raises(ValueError):
            build_record_id(*bad)


def test_record_and_body_filename():
    assert record_filename("act:1961:s194S:v1") == "act__1961__s194S__v1.json"
    assert body_filename("act:1961:s194S:v1") == "act__1961__s194S__v1.txt"


def test_tax_year_start_ok():
    assert tax_year_start("2026-27") == 2026
    assert tax_year_start("1999-00") == 1999


@pytest.mark.parametrize("bad", ["2026-28", "2026-7", "26-27", "2026/27", "", None])
def test_tax_year_start_rejects(bad):
    with pytest.raises(ValueError):
        tax_year_start(bad)


def test_tax_year_bounds():
    assert tax_year_bounds("2026-27") == (date(2026, 4, 1), date(2027, 3, 31))


def test_get_span_code_points():
    body = "FAKE — ₹10 fake"
    assert get_span(body, 5, 6) == "—"
    assert get_span(body, 7, 10) == "₹10"
    assert len(body.encode("utf-8")) > len(body)  # offsets are code points, not bytes


@pytest.mark.parametrize("start,end", [(-1, 1), (2, 2), (3, 1), (0, 6)])
def test_get_span_rejects(start, end):
    with pytest.raises(ValueError):
        get_span("abcde", start, end)


def test_get_span_no_normalisation():
    composed = "café"
    decomposed = unicodedata.normalize("NFD", composed)
    assert len(decomposed) == 5
    assert get_span(decomposed, 3, 4) == "e"
    assert get_span(decomposed, 4, 5) == "́"
    assert get_span(composed, 3, 4) == "é"


def test_body_sha256_matches_hashlib():
    text = "FAKE FIXTURE - NOT LAW. — ₹\n"
    assert body_sha256(text) == hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_schema_file_is_valid_2020_12():
    schema = json.loads(SCHEMA_PATH.read_bytes().decode("utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    jsonschema.Draft202012Validator.check_schema(schema)


def test_all_fixtures_pass_schema():
    recs = _all_records()
    assert len(recs) == 10
    for rec in recs:
        assert rec["fixture"] is True
        assert schema_errors(rec) == [], rec["record_id"]


def test_schema_errors_reports_missing_field():
    rec = load_record(FIXTURES / "records" / "2025" / "act__2025__sFAKE1__v1.json")
    del rec["heading"]
    errs = schema_errors(rec)
    assert errs and any("heading" in e for e in errs)


def test_retrieved_at_z_suffix_rejected():
    rec = load_record(FIXTURES / "records" / "2025" / "act__2025__sFAKE1__v1.json")
    rec["retrieved_at"] = "2026-11-13T00:00:00Z"
    assert any("retrieved_at" in e for e in schema_errors(rec))


def test_gold_span_def_validates():
    body = (FIXTURES / "text" / "2025" / "act__2025__sFAKE5__v2.txt").read_bytes().decode("utf-8")
    start = body.index("—")
    text = get_span(body, start, start + 1)
    span = {"record_id": "act:2025:sFAKE5:v2", "subpath": "", "start": start, "end": start + 1,
            "text_sha256": body_sha256(text)}
    gold = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$ref": "#/$defs/gold_span",
            "$defs": load_schema()["$defs"]}
    jsonschema.Draft202012Validator(gold).validate(span)
    bad = dict(span, extra=1)
    assert list(jsonschema.Draft202012Validator(gold).iter_errors(bad))


def test_load_record_reads_fixture():
    rec = load_record(FIXTURES / "records" / "1961" / "act__1961__sFAKE4__v2.json")
    assert rec["record_id"] == "act:1961:sFAKE4:v2"
    assert rec["supersedes"] == "act:1961:sFAKE4:v1"


def test_modifications_returns_circular():
    index = {r["record_id"]: r for r in _all_records()}
    mods = modifications(index["act:2025:sFAKE1:v1"], index)
    assert [m["record_id"] for m in mods] == ["circular:2025:FAKE-CIRC-1:v1"]
    assert modifications(index["act:2025:sFAKE8:v1"], index) == ()
