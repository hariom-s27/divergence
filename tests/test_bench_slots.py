"""P10a bench slots: synthetic corpus in tmp_path (no real bodies, no law text) + real-spec mapping test."""
import json
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from divergence import bench_slots as bs
from divergence.statute_census import load_records, sweep
from divergence.statute_schema import REASON_CLASS, reason_class

REPO = Path(__file__).resolve().parents[1]
REAL_SPEC = REPO / "divergence" / "bench" / "SPEC-v1.json"
REAL_SWEEP = REPO / "divergence" / "statutes" / "census" / "sweep.json"
CAVEAT_HEADER = "caveat_id,record_id,start,end,unit_label,source,nature,ref_row_id,span_sha16,note\n"


def _rec(act, unit, v, **kw):
    base = {"source_kind": "act", "act": act, "unit": unit, "version_id": v,
            "record_id": f"act:{act}:{unit}:v{v}", "status": "in_force", "in_force_from": None,
            "in_force_to": None, "retrospective_from": None, "enacted_on": None, "supersedes": None,
            "applies_from_tax_year": None, "applies_to_tax_year": None, "basis_category": "charging_ay_rule",
            "lookup_flags": [], "outstanding_effects": [], "storage_mode": "local_only"}
    base.update(kw)
    return base


RECORDS = [
    _rec("1961", "X", 1, in_force_from="2022-01-01", in_force_to="2024-04-01", enacted_on="2021-12-01",
         applies_from_tax_year="2021-22", applies_to_tax_year="2023-24"),
    _rec("1961", "X", 2, in_force_from="2024-04-01", enacted_on="2024-02-01", supersedes="act:1961:X:v1",
         applies_from_tax_year="2024-25"),
    _rec("1961", "Z", 1, in_force_from="2023-04-01", applies_from_tax_year="2023-24"),  # unknown enactment
    _rec("2025", "Y", 1, in_force_from="2026-04-01", enacted_on="2025-08-21", applies_from_tax_year="2026-27"),
    _rec("2025", "W", 1, in_force_from="2026-04-01", enacted_on="2025-08-21", applies_from_tax_year="2026-27"),
]
BODIES = {
    "act:1961:X:v1": "Alpha clause one. Beta proviso applies here. Alpha clause two.",
    "act:1961:X:v2": "Delta text. Epsilon proviso follows. Zeta end.",
    "act:2025:Y:v1": "Eta rule. Theta condition holds.",
    "act:2025:W:v1": "Iota start. Kappa term ends.",
}
PHRASES = {"act:1961:X:v1": "Beta proviso", "act:1961:X:v2": "Epsilon proviso",
           "act:2025:Y:v1": "Theta condition", "act:2025:W:v1": "Kappa term"}


def make_corpus(tmp_path, bodies=True, **spec_overrides):
    root = tmp_path / "statutes"
    for rec in RECORDS:
        path = root / "records" / rec["act"] / f"{rec['unit']}-v{rec['version_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec), encoding="utf-8")
        if bodies and rec["record_id"] in BODIES:
            body = root / "_local_text" / rec["act"] / (path.stem + ".txt")
            body.parent.mkdir(parents=True, exist_ok=True)
            body.write_bytes(BODIES[rec["record_id"]].encode("utf-8"))
    (root / "census").mkdir(parents=True, exist_ok=True)
    (root / "census" / "sweep.json").write_text(json.dumps(sweep(load_records(root / "records"))), encoding="utf-8")
    (root / "census" / "BODY-CAVEATS.csv").write_text(CAVEAT_HEADER, encoding="utf-8")
    (root / "MAPPING.csv").write_text("section_1961,section_2025,operative_2025,utility_date,notes\nX,Y,,,\n",
                                      encoding="utf-8")
    spec = json.loads(REAL_SPEC.read_text(encoding="utf-8"))
    spec.update({"test": {"pairs": 6, "undated": 2}, "dev": {"pairs": 2, "undated": 1},
                 "max_test_items_per_unit": 8})
    spec.update(spec_overrides)
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return root, spec, spec_path


def _rows(data):
    import csv
    import io
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


def _cli(root, spec_path, out, *extra):
    return bs.main(["--spec", str(spec_path), "--out", str(out), "--root", str(root), *extra])


# ---------------------------------------------------------------- real spec / corpus metadata

def test_spec_class_map_equals_reason_class_for_every_corpus_reason():
    spec = bs.load_spec(REAL_SPEC)
    observed = set(json.loads(REAL_SWEEP.read_text(encoding="utf-8"))["reasons"])
    expected = {"before_commencement": "false_premise", "after_repeal": "false_premise",
                "repeal_day_unsettled": "answer_unknown", "overlap": "answer_unknown",
                "applicability_unclear_row": "answer_unknown", "midyear_effect": "underspecified_intent",
                "beyond_corpus_horizon": "stale"}
    assert set(spec["abstain_categories"]) == set(REASON_CLASS.values())
    for reason in sorted(observed):
        if reason in spec["frame_excluded_reasons"]:
            assert reason_class(reason) == "CORPUS"
            continue
        assert bs.abstain_category((reason,), spec) == spec["abstain_categories"][reason_class(reason)]
        if reason in expected:
            assert bs.abstain_category((reason,), spec) == expected[reason], reason
    assert set(spec["frame_excluded_reasons"]) == {"before_coverage", "unknown_enactment_date",
                                                   "unprinted_intermediate"}


def test_real_frame_reasons_are_all_owner_listed():
    """Metadata only: every reason reaching the real frame at as_known_on is owner-listed (P10a D2)."""
    spec = bs.load_spec(REAL_SPEC)
    root = REPO / "divergence" / "statutes"
    timeline = json.loads(REAL_SWEEP.read_text(encoding="utf-8"))["timeline"]
    frame = bs.build_frame(load_records(root / "records"), timeline, spec)
    seen = {r for e in frame["intervals"] + frame["tax_years"] for r in e["reasons"]}
    listed = {"before_commencement", "after_repeal", "repeal_day_unsettled", "overlap",
              "applicability_unclear_row", "midyear_effect", "beyond_corpus_horizon"}
    assert seen <= listed, sorted(seen - listed)


def test_mixed_reasons_use_priority():
    spec = bs.load_spec(REAL_SPEC)
    assert bs.abstain_category(("midyear_effect", "overlap"), spec) == "answer_unknown"
    assert bs.abstain_category(("after_repeal", "repeal_day_unsettled"), spec) == "false_premise"


def test_unmapped_class_is_an_error():
    spec = bs.load_spec(REAL_SPEC)
    spec["abstain_categories"] = {k: v for k, v in spec["abstain_categories"].items() if k != "QUERY"}
    with pytest.raises(bs.SlotError):
        bs.abstain_category(("midyear_effect",), spec)


def test_real_spec_quotas():
    spec = bs.load_spec(REAL_SPEC)
    assert bs.quotas(46, spec) == {"version_lookup": 12, "proviso_condition": 5, "cross_act_counterpart": 9,
                                   "cross_year_change": 11, "abstain_boundary": 9}
    assert bs.quotas(15, spec) == {"version_lookup": 4, "proviso_condition": 1, "cross_act_counterpart": 3,
                                   "cross_year_change": 4, "abstain_boundary": 3}


# ---------------------------------------------------------------- synthetic frame and draw

def test_frame_excludes_corpus_gaps_and_checks_golden_boundaries(tmp_path):
    root, spec, _ = make_corpus(tmp_path)
    records = load_records(root / "records")
    timeline = json.loads((root / "census" / "sweep.json").read_text(encoding="utf-8"))["timeline"]
    frame = bs.build_frame(records, timeline, spec)
    z = [e for e in frame["excluded"] if e["unit"] == "1961:Z"]
    assert {r for e in z for r in e["reasons"].split(";")} == {"before_coverage", "unknown_enactment_date"}
    assert all(i["status"] != "FOUND" for i in frame["intervals"] if i["ukey"] == "1961:Z")
    horizon = [i for i in frame["intervals"] if "beyond_corpus_horizon" in i["reasons"]]
    assert horizon and all(i["category"] == "stale" and i["start"] > date(2026, 11, 15) for i in horizon)
    broken = [row for row in timeline if not (row["unit"] == "act:1961:X" and row["from"] == "2024-04-01")]
    with pytest.raises(bs.SlotError):
        bs.build_frame(records, broken, spec)


def test_rank_prefers_unused_combo_over_lower_unit_load(tmp_path):
    """Owner decision (b): rank by prior combo uses first, unit load second, seeded tie-break."""
    import random
    root, spec, _ = make_corpus(tmp_path)
    timeline = json.loads((root / "census" / "sweep.json").read_text(encoding="utf-8"))["timeline"]
    frame = bs.build_frame(load_records(root / "records"), timeline, spec)
    pool = bs.combos(frame, "abstain_boundary", [])
    on_x = next(c for c in pool if c["a"]["ukey"] == "1961:X")
    on_y = next(c for c in pool if c["a"]["ukey"] == "2025:Y")
    state = bs._State()
    state.loads["test"]["1961:X"] = 5       # X heavily loaded ...
    state.uses[on_y["key"]] = 1             # ... but the Y combo was already used once
    assert bs.combo_score(state, "test", on_x) < bs.combo_score(state, "test", on_y)
    picked = bs._pick_pair(random.Random(1), state, "test", "abstain_boundary", [on_x, on_y], None)
    assert picked[0] is on_x
    # equal scores: the choice depends only on the seed
    ties = [c for c in pool if c["a"]["ukey"] == "2025:W"]
    picks = {bs._pick_pair(random.Random(7), bs._State(), "test", "abstain_boundary", ties, None)[0]["key"]
             for _ in range(3)}
    assert len(picks) == 1


def test_determinism_two_runs_same_bytes(tmp_path):
    root, spec, _ = make_corpus(tmp_path)
    first = bs.generate(spec, root)
    second = bs.generate(spec, root)
    assert first[0] == second[0] and first[1] == second[1]


def test_quotas_reserves_and_no_unfilled(tmp_path):
    root, spec, _ = make_corpus(tmp_path)
    data, info, state = bs.generate(spec, root)
    info = json.loads(info)
    assert not info["unfilled"]
    for split in ("test", "dev"):
        want = bs.quotas(spec[split]["pairs"], spec)
        assert info["counts"][split]["pairs"] == want
        assert info["counts"][split]["undated"] == spec[split]["undated"]
        for stratum, n in want.items():
            assert info["counts"][split]["reserve_pairs"][stratum] == bs.reserve_count(n, spec["reserve_fraction"])
    rows = _rows(data)
    assert {r["reserve"] for r in rows} == {"true", "false"}
    assert all(r["slot_id"].split("-")[1].startswith("R") == (r["reserve"] == "true") for r in rows)


def test_per_unit_cap_and_unfilled_when_cap_too_small(tmp_path):
    root, spec, _ = make_corpus(tmp_path)
    data, info, _ = bs.generate(spec, root)
    rows = [r for r in _rows(data) if r["split"] == "test" and r["reserve"] == "false"]
    counts = Counter(f"{r['act']}:{r['unit']}" for r in rows)
    assert max(counts.values()) <= spec["max_test_items_per_unit"]
    spec["max_test_items_per_unit"] = 3
    _, info, _ = bs.generate(spec, root)
    assert json.loads(info)["unfilled"]


def test_pair_dates_on_opposite_sides_and_gold_differs(tmp_path):
    root, spec, _ = make_corpus(tmp_path)
    data, _, _ = bs.generate(spec, root)
    pairs = {}
    for row in _rows(data):
        if row["side"] in ("a", "b"):
            pairs.setdefault(row["slot_id"], {})[row["side"]] = row
    assert pairs
    for sid, pair in pairs.items():
        a, b = pair["a"], pair["b"]
        gold = [(r["act"], r["unit"], r["gold_status"], r["gold_record_id"], r["gold_reasons"]) for r in (a, b)]
        assert gold[0] != gold[1], sid
        if a["as_of"] and b["as_of"] and a["unit"] == b["unit"]:
            assert a["as_of"] < a["boundary"] < b["as_of"], sid
        if a["stratum"] in ("cross_year_change", "abstain_boundary"):
            assert "true" in (a["should_abstain"], b["should_abstain"]) or a["stratum"] == "cross_year_change"
        if a["stratum"] == "abstain_boundary":
            assert sorted((a["should_abstain"], b["should_abstain"])) == ["false", "true"], sid


def test_dev_test_never_share_unit_date_keys(tmp_path):
    root, spec, _ = make_corpus(tmp_path)
    data, info, _ = bs.generate(spec, root)
    rows = _rows(data)
    assert not (bs.pair_keys(rows, "dev") & bs.pair_keys(rows, "test"))
    assert json.loads(info)["shared_unit_date_keys_dev_test"] == 0
    assert "shared_record_combos_dev_test" in json.loads(info)


def test_active_slots_pulls_next_reserve_of_same_stratum(tmp_path):
    root, spec, _ = make_corpus(tmp_path)
    rows = _rows(bs.generate(spec, root)[0])
    main = [r for r in rows if r["split"] == "test" and r["reserve"] == "false" and r["side"] == "a"]
    victim = main[0]
    reserves = [r["slot_id"] for r in rows if r["split"] == "test" and r["reserve"] == "true"
                and r["stratum"] == victim["stratum"] and r["side"] in ("a", "single")]
    active, pulled, errors = bs.active_slots(rows, "test", {victim["slot_id"]: "no proviso"}, None)
    assert not errors and pulled == {victim["slot_id"]: reserves[0]}
    assert victim["slot_id"] not in active and reserves[0] in active
    _, _, errors = bs.active_slots(rows, "test", {victim["slot_id"]: "x", reserves[0]: "y"}, None)
    assert errors or len(reserves) > 1


def test_cli_check_writes_nothing_then_matches(tmp_path):
    root, spec, spec_path = make_corpus(tmp_path)
    out = tmp_path / "slots" / "SLOTS.csv"
    assert _cli(root, spec_path, out, "--check") == 1
    assert not out.parent.exists()
    assert _cli(root, spec_path, out) == 0
    before = {p.name: p.read_bytes() for p in out.parent.iterdir()}
    assert sorted(before) == ["SLOTS.csv", "SLOTS.summary.json"]
    assert _cli(root, spec_path, out, "--check") == 0
    out.write_bytes(out.read_bytes().replace(b"\n", b"\r\n"))  # CRLF checkout still matches
    assert _cli(root, spec_path, out, "--check") == 0
    assert _cli(root, spec_path, out) == 2  # refuses to overwrite
    assert sorted(p.name for p in out.parent.iterdir()) == sorted(before)
    tampered = out.read_bytes().replace(b"false", b"true", 1)
    out.write_bytes(tampered)
    assert _cli(root, spec_path, out, "--check") == 1
    assert out.read_bytes() == tampered
