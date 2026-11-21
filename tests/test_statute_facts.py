"""Facts use tiny committed-metadata fixtures; no real local-text files are touched."""
import hashlib
import json

import pytest

from divergence import statute_facts as facts


@pytest.fixture
def root(tmp_path):
    root = tmp_path / "statutes"
    records = root / "records"
    records.mkdir(parents=True)
    samples = [
        {"act": "1961", "status": "in_force", "body_chars": 12,
         "lookup_flags": ["repeal_day_unsettled"], "amended_by": [{"url": "https://example.invalid"}]},
        {"act": "1961", "status": "repealed_saved", "body_chars": 0,
         "amended_by": [{"url": " "}, {"url": ""}]},
        {"act": "2025", "status": "unprinted", "body_chars": None, "amended_by": []},
    ]
    for index, record in enumerate(samples):
        (records / f"record{index}.json").write_bytes(json.dumps(record).encode("utf-8"))
    census = root / "census"
    census.mkdir()
    (root / "CORRIGENDUM-DISPOSITION.csv").write_bytes(b"class\ntypo\ntypo\nsubstantive\n")
    (census / "ITD-GAZETTE-DIFFS.csv").write_bytes(
        b"status,origin,nature\nkept,itd,accidental\nkept,itd,accidental\nremoved,pipeline,substantive\n")
    (census / "BODY-CAVEATS.csv").write_bytes(
        b"source,nature\nlabel_gap,unknown\nitd_diff,accidental\nitd_diff,accidental\n")
    (census / "LABEL-GAPS.csv").write_bytes(b"record_id,label\nr1,a\nr2,b\n")
    sweep = {"queries": {"daily": 5, "tax_year": 2, "boundary": 3},
             "statuses": {"FOUND": 4, "AMBIGUOUS": 6}, "reasons": {"test_reason": 6}, "classes": {"LEGAL": 6}}
    (census / "sweep.json").write_bytes((json.dumps(sweep) + "\n").encode("utf-8"))
    return root


def values(document):
    return {fact["key"]: fact["value"] for fact in document["facts"]}


def test_exact_tiny_fixture_facts(root):
    document = facts.collect_facts(root)
    assert document["facts_version"] == 1
    assert values(document) == {
        "records.total": 3, "records.act.1961": 2, "records.act.2025": 1,
        "records.status.in_force": 1, "records.status.repealed_saved": 1, "records.status.unprinted": 1,
        "bodies.nonempty": 1, "bodies.empty_placeholders": 1, "records.repeal_day_unsettled": 1,
        "amended_by.items": 3, "amended_by.empty_url": 2,
        "corrigenda.class.typo": 2, "corrigenda.class.substantive": 1,
        "diffs.total": 3, "diffs.kept.itd.accidental": 2, "diffs.removed.pipeline.substantive": 1,
        "caveats.total": 3, "caveats.label_gap.unknown": 1, "caveats.itd_diff.accidental": 2,
        "label_gaps.rows": 2, "sweep.sha256": hashlib.sha256((root / "census/sweep.json").read_bytes()).hexdigest(),
        "sweep.queries.total": 10, "sweep.queries.daily": 5, "sweep.queries.tax_year": 2, "sweep.queries.boundary": 3,
        "sweep.statuses.found": 4, "sweep.statuses.ambiguous": 6,
        "sweep.reasons.test_reason": 6, "sweep.classes.legal": 6,
        "corpus_checked_through": "2026-11-15", "manifest.present": False,
        "manifest.sha256": None, "manifest.file_count": None,
    }
    keys = [fact["key"] for fact in document["facts"]]
    assert keys == sorted(keys) and len(keys) == len(set(keys))
    for fact in document["facts"]:
        assert set(fact) == {"key", "value", "definition", "source"}
        assert fact["definition"] and "\n" not in fact["definition"] and fact["source"]
    assert "amended_by[*].url only" in next(
        f["definition"] for f in document["facts"] if f["key"] == "amended_by.empty_url")


def test_deterministic_bytes_and_no_local_text(root, tmp_path, capsys):
    assert not (root / "_local_text").exists()
    first = facts.facts_bytes(facts.collect_facts(root))
    assert first == facts.facts_bytes(facts.collect_facts(root))
    assert b"\r" not in first and first.endswith(b"\n")
    assert first == (json.dumps(json.loads(first), indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    assert facts.main(["--root", str(root), "--print"]) == 0
    assert capsys.readouterr().out == first.decode("utf-8")
    out = tmp_path / "facts.json"
    assert facts.main(["--root", str(root), "--out", str(out)]) == 0
    assert out.read_bytes() == first
    before = out.stat().st_mtime_ns
    assert facts.main(["--root", str(root), "--check", str(out)]) == 0
    assert out.stat().st_mtime_ns == before
    assert not (root / "_local_text").exists()


def test_check_reports_first_changed_key(root, tmp_path, capsys):
    document = facts.collect_facts(root)
    next(fact for fact in document["facts"] if fact["key"] == "records.total")["value"] = 99
    path = tmp_path / "changed.json"
    path.write_bytes(facts.facts_bytes(document))
    before = path.read_bytes(), path.stat().st_mtime_ns
    assert facts.main(["--root", str(root), "--check", str(path)]) == 1
    assert "MISMATCH first differing key records.total" in capsys.readouterr().out
    assert (path.read_bytes(), path.stat().st_mtime_ns) == before


def test_manifest_facts_absent_then_present(root):
    absent = values(facts.collect_facts(root))
    assert absent["manifest.present"] is False
    assert absent["manifest.sha256"] is None and absent["manifest.file_count"] is None
    raw = b'{"manifest_version": 1, "file_count": 7}\n'
    (root / "STATUTE-HASHES.json").write_bytes(raw)
    present = values(facts.collect_facts(root))
    assert present["manifest.present"] is True
    assert present["manifest.file_count"] == 7
    assert present["manifest.sha256"] == hashlib.sha256(raw).hexdigest()


def test_missing_sweep_is_not_recomputed(root):
    (root / "census/sweep.json").unlink()
    document = values(facts.collect_facts(root))
    assert document["sweep.sha256"] is None and document["sweep.queries.total"] is None
    assert not any(key.startswith("sweep.statuses.") for key in document)
