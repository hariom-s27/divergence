"""P10a bench_seal: seal/check on synthetic local files."""
from pathlib import Path

from divergence import bench_seal

REAL_SPEC = Path(__file__).resolve().parents[1] / "divergence" / "bench" / "SPEC-v1.json"


def _files(tmp_path):
    items = tmp_path / "TEST.jsonl"
    nuggets = tmp_path / "nuggets_test.jsonl"  # distinct name: Windows paths are case-insensitive
    items.write_bytes(b'{"item_id": "T-001-a"}\n{"item_id": "T-001-b"}\n')
    nuggets.write_bytes(b'{"item_id": "T-001-a", "n": 1}\n')
    return items, nuggets


def test_seal_then_check_and_changed_byte_detected(tmp_path, capsys):
    items, nuggets = _files(tmp_path)
    seal = tmp_path / "TEST-SEAL.json"
    base = ["--spec", str(REAL_SPEC), "--seal-file", str(seal)]
    assert bench_seal.main(["--seal", str(items), str(nuggets)] + base) == 0
    assert bench_seal.main(["--check", str(items), str(nuggets)] + base) == 0
    assert bench_seal.main(["--seal", str(items), str(nuggets)] + base) == 2  # no overwrite
    data = bytearray(items.read_bytes())
    data[5] ^= 1
    items.write_bytes(bytes(data))
    assert bench_seal.main(["--check", str(items), str(nuggets)] + base) == 1
    out = capsys.readouterr().out
    assert "items_sha256" in out and "T-001" not in out


def test_seal_records_count_and_spec_hash(tmp_path):
    items, nuggets = _files(tmp_path)
    record = bench_seal.seal_record(items, nuggets, REAL_SPEC)
    assert record["item_count"] == 2 and len(record["spec_sha256"]) == 64
    assert record["items_file"] == "TEST.jsonl"
