"""D78 validator: the FAKE fixture folder passes; one broken tmp copy per check V01-V16; freeze/verify.

Fixture files are never edited: every negative test works on a copy inside pytest's tmp_path.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from divergence import statute_validate
from divergence.statute_validate import MANIFEST_NAME, main

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "statutes"
F1 = "records/2025/act__2025__sFAKE1__v1.json"
F1_BODY = "text/2025/act__2025__sFAKE1__v1.txt"
F2 = "records/1961/act__1961__sFAKE2__v1.json"
F2_BODY = "_local_text/1961/act__1961__sFAKE2__v1.txt"
F4V2 = "records/1961/act__1961__sFAKE4__v2.json"


@pytest.fixture
def root(tmp_path):
    dst = tmp_path / "statutes"
    shutil.copytree(FIXTURES, dst)
    return dst


def edit(root, rel, fn):
    p = root / rel
    rec = json.loads(p.read_bytes().decode("utf-8"))
    fn(rec)
    p.write_bytes((json.dumps(rec, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def run(capsys, *args):
    code = main([str(a) for a in args])
    return code, capsys.readouterr().out


def run_root(capsys, root, *extra):
    return run(capsys, "--root", root, "--allow-fixtures", *extra)


def has(out, level, rel, check):
    return any(line.startswith(f"{level} {rel}: {check} ") for line in out.splitlines())


# ---- the real fixture folder and the default root ----
def test_fixture_root_exits_0():
    proc = subprocess.run([sys.executable, "-m", "divergence.statute_validate",
                           "--root", "tests/fixtures/statutes", "--allow-fixtures"],
                          cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"WARN {F2}: V10 body_absent_local" in proc.stdout
    assert "statute_validate: 10 records, 0 errors" in proc.stdout


def test_default_root_exits_0(capsys):
    code, out = run(capsys)
    assert code == 0
    assert "statute_validate: 0 records, 0 errors, 0 warnings" in out


def test_default_root_allow_fixtures_exit_2(capsys):
    code, _ = run(capsys, "--allow-fixtures")
    assert code == 2


# ---- one negative test per check ----
def test_v01_schema_invalid(root, capsys):
    edit(root, F1, lambda r: r.pop("heading"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V01")


def test_v01_retrieved_at_z_rejected(root, capsys):
    edit(root, F1, lambda r: r.update(retrieved_at="2026-11-13T00:00:00Z"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V01") and "retrieved_at" in out


def test_v02_id_mismatch(root, capsys):
    edit(root, F1, lambda r: r.update(unit="sFAKE1X"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V02")


def test_v03_filename_mismatch(root, capsys):
    (root / F1).rename(root / "records/2025/wrong_name.json")
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", "records/2025/wrong_name.json", "V03")


def test_v04_duplicate_id(root, capsys):
    dup = root / "records/2025/dup/act__2025__sFAKE1__v1.json"
    dup.parent.mkdir()
    shutil.copyfile(root / F1, dup)
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V04")
    assert has(out, "ERROR", "records/2025/dup/act__2025__sFAKE1__v1.json", "V04")


def test_v05_in_force_order(root, capsys):
    edit(root, F1, lambda r: r.update(in_force_to="2026-01-01"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V05")


def test_v05_tax_year_rule(root, capsys):
    edit(root, F1, lambda r: r.update(applies_to_tax_year="2027-29"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V05")


def test_v06_applies_before_2026_27_error(root, capsys):
    edit(root, F1, lambda r: r.update(applies_from_tax_year="2025-26"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V06")


def test_v06_in_force_before_commencement_warn(root, capsys):
    edit(root, F1, lambda r: r.update(in_force_from="2026-03-01"))
    code, out = run_root(capsys, root)
    assert code == 0 and has(out, "WARN", F1, "V06")


def test_v07_status_consistency(root, capsys):
    edit(root, F2, lambda r: r.update(applies_to_tax_year="2026-27"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F2, "V07")


def test_v08_retrospective_rules(root, capsys):
    edit(root, F4V2, lambda r: r.update(amended_by=[]))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F4V2, "V08")


def test_v09_unresolved_modified_by(root, capsys):
    edit(root, F1, lambda r: r.update(modified_by=["circular:2025:FAKE-CIRC-9:v1"]))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V09")


def test_v09_supersedes_wrong_unit(root, capsys):
    edit(root, F4V2, lambda r: r.update(supersedes="act:1961:sFAKE3:v1"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F4V2, "V09")


def test_v10_body_hash_mismatch(root, capsys):
    p = root / F1_BODY
    p.write_bytes(p.read_bytes() + b"x")
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V10") and "body_sha256 mismatch" in out


def test_v10_public_body_missing(root, capsys):
    (root / F1_BODY).unlink()
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V10") and "body_missing" in out


def test_v10_body_has_cr(root, capsys):
    p = root / F1_BODY
    p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V10") and "CR" in out


def test_v11_json_bom(root, capsys):
    p = root / F1
    p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V11")


def test_v11_json_cr(root, capsys):
    p = root / F1
    p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V11")


def test_v12_empty_acknowledgement(root, capsys):
    edit(root, F1, lambda r: r.update(source_acknowledgement="  "))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V12")


def test_v13_counterpart_bad_source(root, capsys):
    cp = {"ref": "FAKE", "source": "WIKI", "source_url": "https://example.invalid/fake/cp"}
    edit(root, F1, lambda r: r.update(counterpart=cp))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V13")


def test_v14_tracked_local_body_error(root, capsys):
    body = root / F2_BODY
    body.parent.mkdir(parents=True)
    body.write_bytes(b"FAKE FIXTURE - NOT LAW. Section FAKE2. Local-only fake body, deliberately absent.\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "add", "-f", F2_BODY], check=True, capture_output=True)
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F2, "V14")


def test_v14_not_a_git_repo_warn(root, capsys):
    probe = subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True)
    if probe.returncode == 0:
        pytest.skip("tmp_path is inside a git work tree on this machine")
    code, out = run_root(capsys, root)
    assert code == 0 and has(out, "WARN", "(root)", "V14") and "not_a_git_repo" in out


def test_v15_missing_original_note(root, capsys):
    edit(root, F1, lambda r: r.pop("original_note"))
    code, out = run_root(capsys, root)
    assert code == 1 and has(out, "ERROR", F1, "V15")


def test_v16_fixture_without_flag(root, capsys):
    code, out = run(capsys, "--root", root)
    assert code == 1 and has(out, "ERROR", F1, "V16")
    assert sum(1 for line in out.splitlines() if ": V16 " in line) == 10


# ---- freeze / verify (manifests only ever written inside tmp_path) ----
def test_freeze_then_verify_passes(root, capsys):
    code, _ = run_root(capsys, root, "--freeze")
    assert code == 0
    manifest = json.loads((root / MANIFEST_NAME).read_bytes().decode("utf-8"))
    assert manifest["file_count"] == 19 == len(manifest["hashes"])  # 10 records + 9 bodies
    assert all("\\" not in k for k in manifest["hashes"])
    code, out = run_root(capsys, root, "--verify")
    assert code == 0 and "FREEZE" not in out


def test_verify_fails_after_one_byte_change(root, capsys):
    assert run_root(capsys, root, "--freeze")[0] == 0
    p = root / F1
    p.write_bytes(p.read_bytes().replace(b"FAKE heading one", b"FAKE heading onE"))
    code, out = run_root(capsys, root, "--verify")
    assert code == 1 and f"FREEZE changed {F1}" in out


def test_verify_reports_missing_and_extra(root, capsys):
    assert run_root(capsys, root, "--freeze")[0] == 0
    (root / F1_BODY).unlink()
    (root / "text/2025/extra.txt").write_bytes(b"FAKE FIXTURE - NOT LAW. extra\n")
    code, out = run_root(capsys, root, "--verify")
    assert code == 1
    assert f"FREEZE missing {F1_BODY}" in out and "FREEZE extra text/2025/extra.txt" in out


def test_freeze_refused_on_error(root, capsys):
    edit(root, F1, lambda r: r.pop("heading"))
    code, out = run_root(capsys, root, "--freeze")
    assert code == 1 and "freeze refused" in out
    assert not (root / MANIFEST_NAME).exists()


def test_freeze_verify_mutually_exclusive_exit_2(root, capsys):
    code, _ = run_root(capsys, root, "--freeze", "--verify")
    assert code == 2
    assert not (root / MANIFEST_NAME).exists()


def test_missing_jsonschema_exit_2(root, capsys, monkeypatch):
    monkeypatch.setitem(sys.modules, "jsonschema", None)
    code = statute_validate.main(["--root", str(root), "--allow-fixtures"])
    assert code == 2
    assert "jsonschema is required" in capsys.readouterr().err
