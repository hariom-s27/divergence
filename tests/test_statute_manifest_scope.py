"""Manifest coverage uses metadata only and prunes the real local-text folder before descent."""
import json
import os
import shutil
from pathlib import Path

import pytest

from divergence import statute_validate as validator

ROOT = Path(__file__).resolve().parents[1] / "divergence" / "statutes"


def metadata_paths(root):
    paths = []
    for directory, folders, files in os.walk(root):
        folders[:] = [name for name in folders if name != "_local_text"]
        paths.extend((Path(directory) / name).relative_to(root).as_posix() for name in files)
    return sorted(paths)


def test_real_root_scope_covers_every_metadata_file():
    scope = set(validator.manifest_paths(ROOT))
    stray = sorted(set(metadata_paths(ROOT)) - scope - set(validator.MANIFEST_EXCLUDED))
    assert not stray, "Files outside manifest scope/exclusions: " + ", ".join(stray)


def test_real_root_scope_has_no_excluded_paths():
    assert not set(validator.manifest_paths(ROOT)) & set(validator.MANIFEST_EXCLUDED)


@pytest.fixture
def complete_metadata_root(tmp_path):
    root = tmp_path / "metadata"
    for relative in validator.manifest_paths(ROOT):
        source, target = ROOT / relative, root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    # Step 2 has no real golden sweep yet; strictness tests need a complete temporary scope.
    sweep = root / "census" / "sweep.json"
    if not sweep.exists():
        sweep.write_bytes(b"{}\n")
    return root


def test_strict_freeze_twice_is_byte_identical(complete_metadata_root):
    root = complete_metadata_root
    assert validator.missing_scope_files(root) == []
    first = validator.freeze(root, strict=True).read_bytes()
    second = validator.freeze(root, strict=True).read_bytes()
    assert first == second and b"\r" not in first
    document = json.loads(first)
    assert set(document) == {"manifest_version", "file_count", "corpus_checked_through", "hashes"}
    assert "frozen_at" not in document
    assert document["manifest_version"] == 1
    assert document["corpus_checked_through"] == "2026-11-15"
    assert document["file_count"] == len(document["hashes"])
    assert first == (json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    assert validator.verify(root, strict=True) == []


def test_strict_missing_fixed_file_refuses_freeze(complete_metadata_root):
    root = complete_metadata_root
    (root / "MAPPING.csv").unlink()
    assert validator.missing_scope_files(root) == ["MAPPING.csv"]
    findings = validator.scope_findings(root, strict=True)
    assert [(f.level, f.message) for f in findings] == [("ERROR", "missing_scope_file MAPPING.csv")]
    with pytest.raises(ValueError, match="missing_scope_file MAPPING.csv"):
        validator.freeze(root, strict=True)
    assert not (root / validator.MANIFEST_NAME).exists()


def test_strict_verify_reports_scope_and_manifest_missing_file(complete_metadata_root):
    root = complete_metadata_root
    validator.freeze(root, strict=True)
    (root / "MAPPING.csv").unlink()
    messages = [f.message for f in validator.verify(root, strict=True)]
    assert "missing_scope_file MAPPING.csv" in messages
    assert "missing MAPPING.csv" in messages


def test_strict_cli_refuses_missing_scope_and_preview_is_read_only(complete_metadata_root, monkeypatch, capsys):
    root = complete_metadata_root
    (root / "MAPPING.csv").unlink()
    monkeypatch.setattr(validator, "DEFAULT_ROOT", root)
    # Isolate scope behavior from V01-V16 and prevent any body-resolution work in this new test.
    monkeypatch.setattr(validator, "validate", lambda root, allow_fixtures: ([], 34))
    before = {rel: (root / rel).stat().st_mtime_ns for rel in metadata_paths(root)}
    assert validator.main(["--freeze"]) == 1
    assert "freeze refused" in capsys.readouterr().out
    assert validator.main(["--preview"]) == 1
    output = capsys.readouterr().out
    assert "missing_scope_file MAPPING.csv" in output and "1 missing scope files" in output
    assert {rel: (root / rel).stat().st_mtime_ns for rel in metadata_paths(root)} == before
    assert not (root / validator.MANIFEST_NAME).exists()
