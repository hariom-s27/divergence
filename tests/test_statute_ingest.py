"""Synthetic persistence and provenance tests; no real extraction or body input."""
import copy

import pytest

from divergence import statute_ingest as ingest
from divergence.statute_schema import body_sha256, record_filename
from divergence.statute_validate import body_path


def record(unit="FAKE-C4", status="in_force"):
    out = {
        "schema_version": 1, "record_id": f"act:1961:{unit}:v1", "source_kind": "act", "act": "1961",
        "unit": unit, "section": unit, "heading": "Invented heading", "chapter": None,
        "version_id": 1, "supersedes": None, "status": status,
        "in_force_from": "2024-04-01", "in_force_to": None,
        "applies_from_tax_year": "2024-25", "applies_to_tax_year": None,
        "retrospective_from": None, "enacted_on": "2024-03-01", "amended_by": [], "modified_by": [],
        "text_current_as_of": "2024-03-01", "outstanding_effects": [], "counterpart": None,
        "source_url": "https://example.invalid/edition", "source_page_act": "Invented edition",
        "source_page_year": "2024", "source_amended_up_to": "2024-03-01",
        "retrieved_at": "2026-11-13T06:53:09+05:30", "gazette_published": "no",
        "source_acknowledgement": "Invented source", "storage_mode": "local_only",
        "body_sha256": body_sha256("invented text"), "body_chars": len("invented text"),
    }
    if status == "unprinted":
        out.update(body=None, body_sha256=None, body_chars=None)
    return out


def test_persist_twice_identical_and_no_public_body(tmp_path):
    first, gap = record(), record("FAKE-GAP", "unprinted")
    records, bodies = [first, gap], {first["record_id"]: "invented text"}
    plan = ingest.output_plan(tmp_path, records, bodies)
    assert ingest.persist(tmp_path, records, bodies) == 3
    snapshot = {path: path.read_bytes() for path in plan}
    assert ingest.persist(tmp_path, records, bodies) == 0
    assert snapshot == {path: path.read_bytes() for path in plan}
    public = tmp_path / "records" / first["act"] / record_filename(first["record_id"])
    assert b"invented text" not in public.read_bytes()


def test_conflict_rejected_before_any_new_file(tmp_path):
    rec = record()
    bodies = {rec["record_id"]: "invented text"}
    path = tmp_path / "records" / rec["act"] / record_filename(rec["record_id"])
    path.parent.mkdir(parents=True)
    path.write_bytes(b"existing conflicting metadata")
    with pytest.raises(ValueError, match="existing output differs"):
        ingest.persist(tmp_path, [rec], bodies)
    assert path.read_bytes() == b"existing conflicting metadata"
    assert not body_path(tmp_path, rec, path).exists()


def test_unprinted_must_have_no_body_file(tmp_path):
    rec = record(status="unprinted")
    path = tmp_path / "records" / rec["act"] / record_filename(rec["record_id"])
    bp = body_path(tmp_path, rec, path)
    bp.parent.mkdir(parents=True)
    bp.write_bytes(b"unexpected synthetic body")
    with pytest.raises(ValueError, match="unprinted body must be absent"):
        ingest.persist(tmp_path, [rec], {})
    assert not path.exists()


def test_missing_heading_refused():
    rec = record()
    with pytest.raises(ValueError, match="missing extracted heading"):
        ingest.attach_record(rec, {}, {"status": "FOUND", "body": "invented text"}, rec["body_sha256"])


def test_guard_body_mismatch_refused():
    rec = record()
    with pytest.raises(ValueError, match="body differs from guard map"):
        ingest.attach_record(rec, {}, {"status": "FOUND", "heading": "Invented", "body": "changed text"},
                             rec["body_sha256"])


def test_missing_provenance_refused_before_persistence(tmp_path):
    rec = record()
    rec["retrieved_at"] = None
    with pytest.raises(ValueError, match="retrieved_at"):
        ingest.persist(tmp_path, [rec], {rec["record_id"]: "invented text"})
    assert not (tmp_path / "records").exists()


def test_original_source_preserves_empty_body_and_successor_clock():
    rec = record()
    rec.update(act="2025", status="never_operative", body="", text_current_as_of="2026-03-30")
    registry = {"ita2025_2025": {"item": "Invented original edition"}, "ita2025_gz": {"sha256": "b" * 64}}
    fetch = {"ita2025_2025": {"url": "https://example.invalid/original",
                              "finished_at": "2026-11-13T06:53:09+05:30"}}
    ingest.original_source(rec, registry, {"ita2025_2025": {"date": None}}, fetch)
    assert rec["body"] == "" and rec["text_current_as_of"] == "2026-03-30"
    assert rec["source_url"] == fetch["ita2025_2025"]["url"]
    assert rec["retrieved_at"] == fetch["ita2025_2025"]["finished_at"]
    assert rec["source_amended_up_to"] is None and rec["source_page_year"] == "2025"
    assert "b" * 64 in rec["notes"] and "heading Gazette-checked 2026-11-17 (owner)" in rec["notes"]


def test_empty_original_body_uses_empty_hash():
    rec = record()
    rec["status"] = "never_operative"
    body = ingest.attach_record(rec, {}, {"status": "FOUND", "heading": "Invented", "body": "ignored"}, None)
    assert body == "" and rec["body_sha256"] == body_sha256("") and rec["body_chars"] == 0


def test_knowledge_parser_stops_at_table_boundary(tmp_path):
    path = tmp_path / "knowledge.md"
    path.write_text("| edition | date | source | acts | printed title acts | mismatch |\n"
                    "|---|---|---|---|---|---|\n"
                    "| ita2025_2025 | None | unknown | | | None |\n\n"
                    "| edition | section | unrelated |\n| ita2025_2026 | 2 | unrelated |\n", encoding="utf-8")
    assert ingest.read_knowledge_table(path) == {"ita2025_2025": None}


def test_knowledge_mismatch_is_error_and_inputs_unchanged():
    actual = {"ita2025_2026": {"date": "2026-03-30"}}
    previous = copy.deepcopy(actual)
    with pytest.raises(ValueError, match="differ from C2"):
        ingest.check_knowledge(actual, {"ita2025_2026": "2026-03-29"})
    assert actual == previous
