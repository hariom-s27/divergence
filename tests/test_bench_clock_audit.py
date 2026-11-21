"""P10b-D3 bench_clock_audit on the synthetic corpus (placeholder words, no law text)."""
import json
from datetime import date

from divergence import bench_clock_audit as bca
from divergence import bench_slots as bs

from test_bench_slots import _rows, make_corpus


def test_fy_mapping_edges():
    assert bca.fy_of(date(2024, 3, 31)) == "2023-24"
    assert bca.fy_of(date(2024, 4, 1)) == "2024-25"
    assert bca.fy_of(date(1999, 12, 31)) == "1999-00"


def _setup(tmp_path):
    root, spec, spec_path = make_corpus(tmp_path)
    slots = tmp_path / "SLOTS.csv"
    slots.write_bytes(bs.csv_bytes(_rows(bs.generate(spec, root)[0])))
    return root, spec_path, slots


def test_audit_counts_and_no_text(tmp_path):
    root, spec_path, slots = _setup(tmp_path)
    out = tmp_path / "audit" / "clock.json"
    args = ["--slots", str(slots), "--spec", str(spec_path), "--root", str(root), "--out", str(out)]
    assert bca.main(args) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    for c in data["counts"].values():
        assert c["as_of_sides"] == c["agree"] + c["disagree"] + c["both_nonfound"]
        assert c["disagree"] == c["found_found_diff_record"] + c["found_vs_nonfound"]
    assert data["totals"]["as_of_sides"] == sum(len(v) for v in data["sides"].values())
    text = out.read_text(encoding="utf-8")
    assert '"question"' not in text and "gold" not in text
    assert bca.main(args) == 2  # refuses to overwrite


def test_refuses_frozen_runs(tmp_path):
    root, spec_path, slots = _setup(tmp_path)
    frozen = bca.FROZEN_RUNS / "never_written.json"
    assert bca.main(["--slots", str(slots), "--spec", str(spec_path), "--root", str(root),
                     "--out", str(frozen)]) == 2
    assert not frozen.exists()
