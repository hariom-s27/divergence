"""P10b B: bench_label_sheets + bench_agree on synthetic items/bodies in tmp_path (placeholder words, no law text)."""
import csv
import json
import random
from fractions import Fraction

import pytest

from divergence import bench_agree as ag
from divergence import bench_label_sheets as ls
from divergence.statute_schema import REASON_CLASS, body_sha256

BODIES = {
    "act:1961:X:v1": "Zeta placeholder one. Omicron marker words here.\n",
    "act:1961:X:v2": "Zeta placeholder two. Upsilon marker words there.\n",
}
NUGGET_TEXT = {"S-001-a": "Omicron marker", "S-001-b": "Upsilon marker"}
SECRET_WORDS = ("Zeta", "Omicron", "Upsilon", "marker words")
PRACTICE = ["S-001-a", "S-001-b", "S-003-a", "S-003-b", "S-004-a", "S-004-b", "S-005-a", "S-005-b", "S-006-a",
            "S-006-b", "S-007-single"]


def _item(iid, stratum, status, rid=None, reasons=(), as_of=None, ty=None, act="1961", abstain=False, cat=None):
    return {"item_id": iid, "split": "dev", "slot_id": iid.rsplit("-", 1)[0], "stratum": stratum,
            "question": f"Placeholder question {iid}?", "act": act, "unit": "X", "as_of": as_of, "tax_year": ty,
            "as_known_on": "2026-11-15", "dated": stratum != "undated", "gold_status": status,
            "gold_record_id": rid, "gold_reasons": list(reasons), "should_abstain": abstain,
            "abstain_category": cat}


def make_items():
    return [
        _item("S-001-a", "version_lookup", "FOUND", "act:1961:X:v1", as_of="2024-01-31"),
        _item("S-001-b", "version_lookup", "FOUND", "act:1961:X:v2", as_of="2025-01-31"),
        _item("S-002-a", "version_lookup", "FOUND", "act:1961:X:v1", as_of="2024-02-01"),
        _item("S-002-b", "version_lookup", "FOUND", "act:1961:X:v2", as_of="2025-02-01"),
        _item("S-003-a", "proviso_condition", "FOUND", "act:1961:X:v1", as_of="2024-03-01"),
        _item("S-003-b", "proviso_condition", "FOUND", "act:1961:X:v2", as_of="2025-03-01"),
        _item("S-004-a", "cross_act_counterpart", "FOUND", "act:1961:X:v1", as_of="2024-04-01"),
        _item("S-004-b", "cross_act_counterpart", "FOUND", "act:1961:X:v2", as_of="2026-05-01", act="2025"),
        _item("S-005-a", "cross_year_change", "AMBIGUOUS", reasons=("midyear_effect", "overlap"), ty="2024-25",
              abstain=True, cat="answer_unknown"),
        _item("S-005-b", "cross_year_change", "FOUND", "act:1961:X:v2", ty="2025-26"),
        _item("S-006-a", "abstain_boundary", "NO_APPLICABLE_VERSION", reasons=("before_commencement",),
              as_of="2025-06-01", act="2025", abstain=True, cat="false_premise"),
        _item("S-006-b", "abstain_boundary", "FOUND", "act:1961:X:v2", as_of="2025-06-02"),
        _item("S-007-single", "undated", None, abstain=True, cat="underspecified_intent"),
    ]


def setup(tmp_path):
    root = tmp_path / "statutes"
    for rid, body in BODIES.items():
        stem = rid.replace(":", "_")
        (root / "records" / "1961").mkdir(parents=True, exist_ok=True)
        (root / "_local_text" / "1961").mkdir(parents=True, exist_ok=True)
        rec = {"record_id": rid, "act": "1961", "storage_mode": "local_only", "body_sha256": body_sha256(body)}
        (root / "records" / "1961" / f"{stem}.json").write_text(json.dumps(rec), encoding="utf-8")
        (root / "_local_text" / "1961" / f"{stem}.txt").write_bytes(body.encode("utf-8"))
    items = make_items()
    items_path = tmp_path / "items.jsonl"
    items_path.write_text("".join(json.dumps(i) + "\n" for i in items), encoding="utf-8")
    by_id = {i["item_id"]: i for i in items}
    nug_lines = []
    for iid, phrase in NUGGET_TEXT.items():
        rid = by_id[iid]["gold_record_id"]
        start = BODIES[rid].index(phrase)
        nug_lines.append({"item_id": iid, "n": 1, "phrase": phrase, "record_id": rid,
                          "start": start, "end": start + len(phrase)})
    nuggets = tmp_path / "nuggets.jsonl"
    nuggets.write_text("".join(json.dumps(n) + "\n" for n in nug_lines), encoding="utf-8")
    local = tmp_path / "_local"
    return {"items": items_path, "root": root, "nuggets": nuggets, "local": local,
            "out": local / "labels" / "practice"}


def make_pack(env, ids="practice", out=None, emit=lambda s: None):
    return ls.run(env["items"], "dev", ids, out or env["out"], root=env["root"], nuggets=env["nuggets"],
                  local_root=env["local"], emit=emit)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return tuple(reader.fieldnames), list(reader)


def fill(src, dst, a2=None, b1=None):
    """Copy a pack's sheets into dst with the given a2 / b1 values per item id."""
    dst.mkdir(parents=True)
    for name, col, values in (("sheet_A.csv", "a2_answerability", a2 or {}),
                              ("sheet_B.csv", "b1_key_supported", b1 or {})):
        fields, rows = read_csv(src / name)
        for row in rows:
            row[col] = values.get(row["item_id"], "")
        with open(dst / name, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    return dst


def test_sheet_columns_exact_and_texts(tmp_path):
    env = setup(tmp_path)
    make_pack(env)
    out = env["out"]
    fields_a, rows_a = read_csv(out / "sheet_A.csv")
    fields_b, rows_b = read_csv(out / "sheet_B.csv")
    assert fields_a == ("item_id", "question", "date_or_ty", "as_known_on", "lookup_note", "a1_my_answer",
                        "a2_answerability", "a3_minutes", "notes")
    assert fields_b == ("item_id", "gold_summary", "nugget_phrases", "b1_key_supported", "b2_reason",
                        "b3_confidence", "notes")
    assert [r["item_id"] for r in rows_a] == PRACTICE == [r["item_id"] for r in rows_b]
    a = {r["item_id"]: r for r in rows_a}
    assert all(not r[c] for r in rows_a for c in ("a1_my_answer", "a2_answerability", "a3_minutes", "notes"))
    assert a["S-001-a"]["lookup_note"] == "one version applies" and a["S-001-a"]["date_or_ty"] == "2024-01-31"
    assert a["S-005-a"]["lookup_note"] == ("two versions possible for this tax year; "
                                           "a change took effect partway through this tax year")
    assert a["S-005-a"]["date_or_ty"] == "previous year 2024-25 (assessment year 2025-26)"
    assert a["S-006-a"]["lookup_note"] == "not yet in force on this date"
    assert a["S-007-single"]["lookup_note"] == "no date or tax year given" and a["S-007-single"]["date_or_ty"] == ""
    b = {r["item_id"]: r for r in rows_b}
    assert b["S-001-a"]["nugget_phrases"] == "[1] Omicron marker" and "act:1961:X:v1" in b["S-001-a"]["gold_summary"]
    assert b["S-006-a"]["nugget_phrases"] == "" and "false premise" in b["S-006-a"]["gold_summary"]
    texts = sorted(p.name for p in (out / "texts").iterdir())
    assert texts == sorted(f"{i}.txt" for i in PRACTICE)
    assert (out / "texts" / "S-001-a.txt").read_bytes().decode("utf-8") == BODIES["act:1961:X:v1"]
    assert (out / "texts" / "S-006-a.txt").read_text(encoding="utf-8") == \
        "no single version applies: not yet in force on this date\n"
    assert (out / "texts" / "S-007-single.txt").read_text(encoding="utf-8") == \
        "no single version applies: no date or tax year given\n"


def test_writes_only_under_local_and_never_overwrites(tmp_path):
    env = setup(tmp_path)
    outside = tmp_path / "elsewhere"
    with pytest.raises(ls.LabelError, match="inside"):
        make_pack(env, out=outside)
    assert not outside.exists()
    sneaky = env["local"] / ".." / "escaped"
    with pytest.raises(ls.LabelError, match="inside"):
        make_pack(env, out=sneaky)
    assert not (tmp_path / "escaped").exists()
    make_pack(env)
    with pytest.raises(ls.LabelError, match="overwrite"):
        make_pack(env)
    assert ls.main(["--items", str(env["items"]), "--split", "dev", "--ids", "practice", "--out", str(outside)],
                   root=env["root"], nuggets=env["nuggets"], local_root=env["local"]) == 2


def test_practice_selection_rule_is_deterministic(tmp_path):
    items = make_items()
    assert ls.practice_ids(items) == PRACTICE
    shuffled = items[:]
    random.Random(7).shuffle(shuffled)
    assert ls.practice_ids(shuffled) == PRACTICE
    assert len({i["stratum"] for i in items if i["item_id"] in PRACTICE}) == 6
    with pytest.raises(ls.LabelError, match="dev split only"):
        ls.select_ids(items, "test", "practice")
    assert ls.select_ids(items, "dev", "S-002-b,S-001-a") == ["S-002-b", "S-001-a"]
    with pytest.raises(ls.LabelError, match="unknown"):
        ls.select_ids(items, "dev", "S-999-a")


def test_lookup_note_covers_every_reason_code():
    spec = {"abstain_categories": {"CORPUS": "stale", "LEGAL": "answer_unknown", "NO_LAW": "false_premise",
                                   "QUERY": "underspecified_intent"},
            "abstain_priority": ["false_premise", "stale", "answer_unknown", "underspecified_intent"]}
    assert set(ls.REASON_NOTES) == set(REASON_CLASS)
    for code in REASON_CLASS:
        item = _item("S-9-a", "version_lookup", "AMBIGUOUS", reasons=(code,), as_of="2025-01-01")
        assert ls.lookup_note(item, spec) == ls.REASON_NOTES[code]
    assert ls.lookup_note(_item("S-9-a", "version_lookup", "AMBIGUOUS", reasons=("overlap",), ty="2024-25"),
                          spec) == "two versions possible for this tax year"
    two = _item("S-9-a", "x", "AMBIGUOUS", reasons=("midyear_effect", "after_repeal"), as_of="2026-05-01")
    assert ls.lookup_note(two, spec) == "after repeal; a change took effect partway through this tax year"
    with pytest.raises(ls.LabelError, match="unknown reason"):
        ls.lookup_note(_item("S-9-a", "x", "AMBIGUOUS", reasons=("made_up",), as_of="2025-01-01"), spec)
    assert ls.lookup_note(_item("S-9-a", "x", "FOUND", "r", as_of="2025-01-01"), spec) == "one version applies"
    assert ls.lookup_note(_item("S-9-single", "undated", None), spec) == "no date or tax year given"


def test_alpha_equals_hand_values():
    a, b = [1, 1, 0, 0, 1], [1, 0, 0, 0, 1]
    assert ag.alpha([[x, y] for x, y in zip(a, b)]) == (Fraction(16, 25), None)
    a, b = [1, 1, 0, 1, 0, 1, 1, None], [1, 0, 0, 1, 0, 1, 0, 0]
    assert ag.alpha([[x, y] for x, y in zip(a, b)]) == (Fraction(11, 24), None)


def test_unsure_is_missing_and_unknown_values_are_errors(tmp_path):
    env = setup(tmp_path)
    make_pack(env)
    ids = PRACTICE
    b1_a = dict(zip(ids, ["YES", "YES", "NO", "NO", "YES", "UNSURE", "YES", "NO", "YES", "NO", "NO"]))
    b1_b = dict(zip(ids, ["YES", "NO", "NO", "NO", "YES", "YES", "", "NO", "YES", "NO", "NO"]))
    la = fill(env["out"], tmp_path / "la", b1=b1_a)
    lb = fill(env["out"], tmp_path / "lb", b1=b1_b)
    res = ag.agree(la, lb)
    m = res["measures"]["b1_key_supported"]
    assert m["n_items_considered"] == 11 and m["n_pairable"] == 9
    assert m["missing_a"] == 1 and m["missing_b"] == 1
    assert m["observed_agreement"] == {"k": 8, "n": 9} and m["disagreements"] == ["S-001-b"]
    bad = fill(env["out"], tmp_path / "bad", b1={**b1_a, "S-001-a": "MAYBE"})
    with pytest.raises(ag.AgreeError, match="outside the allowed set"):
        ag.agree(bad, lb)
    bad_a2 = fill(env["out"], tmp_path / "bad_a2", a2={"S-001-a": "answerable"})
    with pytest.raises(ag.AgreeError, match="outside the allowed set"):
        ag.agree(bad_a2, lb)


def test_a2_rows_rule_ignored_values_are_counted(tmp_path):
    env = setup(tmp_path)
    make_pack(env)
    a2_a = {"S-001-a": "ANSWERABLE", "S-001-b": "ANSWERABLE", "S-003-a": "INDETERMINATE",
            "S-007-single": "UNDERSPECIFIED", "S-005-a": "ANSWERABLE", "S-006-a": "UNSURE"}
    a2_b = {"S-001-a": "ANSWERABLE", "S-001-b": "UNDERSPECIFIED", "S-003-a": "INDETERMINATE",
            "S-007-single": "UNDERSPECIFIED"}
    res = ag.agree(fill(env["out"], tmp_path / "la", a2=a2_a), fill(env["out"], tmp_path / "lb", a2=a2_b))
    m = res["measures"]["a2_answerability"]
    # one-version rows (S-001/S-003/S-004 a+b, S-005-b, S-006-b) + the undated row; abstain rows excluded
    assert m["n_items_considered"] == 9 and m["n_pairable"] == 4
    assert m["disagreements"] == ["S-001-b"]
    assert res["a2_ignored"] == {"a": ["S-005-a", "S-006-a"], "b": [], "count_a": 2, "count_b": 0}
    assert res["disagreement_count_by_item"] == {"S-001-b": 1}


def test_undefined_alpha_and_bootstrap_counts():
    a, reason = ag.alpha([[1, 1], [1, 1], [1, 1]])
    assert a is None and "expected disagreement is 0" in reason
    assert ag.alpha([[1, None], [0, None]]) == (None, "fewer than two pairable values")
    m = ag.measure(["i1", "i2", "i3"], {"i1": 1, "i2": 1, "i3": 1}, {"i1": 1, "i2": 1, "i3": 1})
    assert m["alpha"] is None and m["ci95"] is None
    assert m["bootstrap"]["n_undefined"] == ag.RESAMPLES and m["bootstrap"]["n_defined"] == 0
    ids = [f"i{n}" for n in range(4)]
    m = ag.measure(ids, dict(zip(ids, [1, 1, 1, 0])), dict(zip(ids, [1, 1, 1, 1])))
    boot = m["bootstrap"]
    assert boot["n_defined"] + boot["n_undefined"] == ag.RESAMPLES and boot["n_undefined"] > 0


def test_bootstrap_is_reproducible_with_seed():
    ids = [f"i{n}" for n in range(8)]
    ca = dict(zip(ids, [1, 1, 0, 1, 0, 1, 1, 0]))
    cb = dict(zip(ids, [1, 0, 0, 1, 0, 1, 0, 0]))
    first, second = ag.measure(ids, ca, cb), ag.measure(ids, ca, cb)
    assert first == second and first["ci95"] is not None
    assert first["bootstrap"]["seed"] == 20261121 and first["bootstrap"]["resamples"] == 2000
    lo, hi = first["ci95"]
    assert lo <= first["alpha"] <= hi


def test_agree_refuses_overwrite_and_runs(tmp_path):
    env = setup(tmp_path)
    make_pack(env)
    la, lb = fill(env["out"], tmp_path / "la"), fill(env["out"], tmp_path / "lb")
    out = tmp_path / "agree.json"
    ag.write_result(ag.agree(la, lb), out)
    with pytest.raises(ag.AgreeError, match="overwrite"):
        ag.write_result({}, out)
    with pytest.raises(ag.AgreeError, match="runs"):
        ag.write_result({}, ag.RUNS_DIR / "never_written.json")
    assert not (ag.RUNS_DIR / "never_written.json").exists()


def test_console_shows_no_body_or_nugget_text(tmp_path, capsys):
    env = setup(tmp_path)
    assert ls.main(["--items", str(env["items"]), "--split", "dev", "--ids", "practice", "--out", str(env["out"])],
                   root=env["root"], nuggets=env["nuggets"], local_root=env["local"]) == 0
    b1 = {i: "YES" for i in PRACTICE}
    la = fill(env["out"], tmp_path / "la", b1=b1, a2={"S-001-a": "ANSWERABLE"})
    lb = fill(env["out"], tmp_path / "lb", b1={**b1, "S-001-a": "NO"}, a2={"S-001-a": "UNSURE"})
    assert ag.main(["--a", str(la), "--b", str(lb), "--out", str(tmp_path / "agree.json")]) == 0
    captured = capsys.readouterr()
    console = captured.out + captured.err
    assert "selected 11 item(s)" in console and "b1_key_supported" in console
    for word in SECRET_WORDS:
        assert word not in console
    saved = (tmp_path / "agree.json").read_text(encoding="utf-8")
    for word in SECRET_WORDS:
        assert word not in saved
