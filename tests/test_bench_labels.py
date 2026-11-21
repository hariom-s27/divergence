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
    return {"item_id": iid, "split": "dev", "slot_id": iid.rsplit("-", 1)[0], "pair_id": iid.rsplit("-", 1)[0],
            "stratum": stratum,
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


def make_pack(env, ids="practice", out=None, emit=lambda s: None, **kw):
    return ls.run(env["items"], "dev", ids, out or env["out"], root=env["root"], nuggets=env["nuggets"],
                  local_root=env["local"], emit=emit, **kw)


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


# ---------------------------------------------------------------- P10c: seeds, specific agreement, adjudication
import hashlib  # noqa: E402

from divergence import bench_adjudicate as adj  # noqa: E402
from divergence.bench_slots import DEFAULT_SPEC, load_spec  # noqa: E402
from divergence.binom_ci import clopper_pearson  # noqa: E402

ALL_IDS = [i["item_id"] for i in ls.slot_order(make_items())]
FALSE_ABSTAIN = "NO_APPLICABLE_VERSION (not yet in force on this date): no record; should abstain - false premise"
V2_FOUND = ("FOUND (one version applies): Income-tax Act, 1961, section X, version 2 [act:1961:X:v2]; "
            "should not abstain")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(d):
    return {p.relative_to(d).as_posix(): sha(p) for p in sorted(d.rglob("*")) if p.is_file()}


def seeded_pack(env, parent, name, n=3, key_name=None, emit=lambda s: None):
    out = env["local"] / "labels" / parent / name
    key = env["local"] / "labels" / "_keys" / (key_name or f"{parent}_{name}.json")
    make_pack(env, ids="all", out=out, emit=emit, seed_keys=n, seed_key_out=key)
    return out, key, json.loads(key.read_text(encoding="utf-8"))


def test_ids_all_exclude_practice_deterministic(tmp_path):
    items = make_items()
    rest = [i for i in ALL_IDS if i not in PRACTICE]
    assert rest == ["S-002-a", "S-002-b"]
    assert ls.select_ids(items, "dev", "all") == ALL_IDS
    shuffled = items[:]
    random.Random(3).shuffle(shuffled)
    assert ls.select_ids(shuffled, "dev", "all", "practice") == rest == ls.select_ids(items, "dev", "all", "practice")
    with pytest.raises(ls.LabelError, match="dev split only"):
        ls.select_ids(items, "test", "all", "practice")
    with pytest.raises(ls.LabelError, match="exclude"):
        ls.select_ids(items, "dev", "all", "bogus")
    env = setup(tmp_path)
    make_pack(env, ids="all", exclude="practice")
    assert [r["item_id"] for r in read_csv(env["out"] / "sheet_A.csv")[1]] == rest


def test_seed_eligibility_types_and_cross_act_exclusion():
    items = make_items()
    spec = load_spec(DEFAULT_SPEC)
    nug = [{"item_id": i, "n": 1, "phrase": "p"} for i in ("S-001-a", "S-001-b", "S-004-a", "S-004-b")]
    elig = ls.seed_eligibility(items, nug, ALL_IDS, spec)
    assert elig["wrong_version"] == ["S-001-a", "S-001-b"]  # S-004 is cross_act_counterpart: excluded
    assert elig["false_answer"] == ["S-005-a", "S-006-a"]  # S-007-single (undated) not eligible
    assert elig["false_abstain"] == sorted(i for i in ALL_IDS if i not in ("S-005-a", "S-006-a", "S-007-single"))
    relabelled = [dict(i, stratum="version_lookup") if i["slot_id"] == "S-004" else i for i in items]
    assert ls.seed_eligibility(relabelled, nug, ALL_IDS, spec)["wrong_version"] == \
        ["S-001-a", "S-001-b", "S-004-a", "S-004-b"]


def test_seeded_key_wording_per_type():
    by_id = {i["item_id"]: i for i in make_items()}
    nug = [{"item_id": "S-001-b", "n": 1, "phrase": "Upsilon marker"}]
    s, p = ls.seeded_key(by_id["S-001-a"], by_id["S-001-b"], nug, "wrong_version")
    assert (s, p) == (V2_FOUND, "[1] Upsilon marker")
    s, p = ls.seeded_key(by_id["S-005-a"], by_id["S-005-b"], nug, "false_answer")
    assert (s, p) == (V2_FOUND, "")
    s, p = ls.seeded_key(by_id["S-002-a"], by_id["S-002-b"], nug, "false_abstain")
    assert (s, p) == (FALSE_ABSTAIN, "")


def test_seeds_deterministic_eligible_one_per_item_and_sheet_a_texts_unchanged(tmp_path):
    env = setup(tmp_path)
    plain = env["local"] / "labels" / "plain"
    make_pack(env, ids="all", out=plain)
    out1, key1, k1 = seeded_pack(env, "x", "friend")
    out2, key2, k2 = seeded_pack(env, "y", "friend")
    assert k1 == k2 and k1["pack"] == "friend" and k1["seed"] == "20261121-seeds-friend"
    assert k1["items_sha256"] == sha(env["items"])
    seeds = [(s["item_id"], s["type"]) for s in k1["seeds"]]
    assert len(seeds) == 3 and len({i for i, _ in seeds}) == 3
    assert sorted(t for _, t in seeds) == sorted(ls.SEED_TYPES)  # spread: one of each type
    elig = ls.seed_eligibility(make_items(), [json.loads(x) for x in env["nuggets"].read_text().splitlines()],
                               ALL_IDS, load_spec(DEFAULT_SPEC))
    assert all(i in elig[t] for i, t in seeds)
    assert sorted(p.name for p in out1.iterdir()) == ["sheet_A.csv", "sheet_B.csv", "texts"]  # key not in --out
    assert not key1.is_relative_to(out1)
    assert sha(out1 / "sheet_A.csv") == sha(plain / "sheet_A.csv")
    assert tree_hashes(out1 / "texts") == tree_hashes(plain / "texts")
    real_b = {r["item_id"]: r for r in read_csv(plain / "sheet_B.csv")[1]}
    seed_b = {r["item_id"]: r for r in read_csv(out1 / "sheet_B.csv")[1]}
    seeded_ids = {i for i, _ in seeds}
    assert {i for i in ALL_IDS if seed_b[i] != real_b[i]} == seeded_ids
    other, _, k3 = seeded_pack(env, "x", "other_pack", n=12)
    assert len(k3["seeds"]) == 12
    with pytest.raises(ls.LabelError, match="seedable"):
        seeded_pack(env, "z", "too_many", n=13)
    assert not (env["local"] / "labels" / "z" / "too_many").exists()


def test_seed_args_checked_and_console_hides_seeded_ids(tmp_path):
    env = setup(tmp_path)
    labels = env["local"] / "labels"
    with pytest.raises(ls.LabelError, match="both or neither"):
        make_pack(env, ids="all", out=labels / "p1", seed_keys=2)
    with pytest.raises(ls.LabelError, match="both or neither"):
        make_pack(env, ids="all", out=labels / "p1", seed_key_out=labels / "_keys" / "k.json")
    with pytest.raises(ls.LabelError, match="_keys"):
        make_pack(env, ids="all", out=labels / "p1", seed_keys=2, seed_key_out=labels / "k.json")
    with pytest.raises(ls.LabelError, match="not be inside --out"):
        make_pack(env, ids="all", out=labels / "_keys" / "p1", seed_keys=2,
                  seed_key_out=labels / "_keys" / "p1" / "k.json")
    assert not (labels / "p1").exists() and not (labels / "_keys").exists()
    lines = []
    _, key, k = seeded_pack(env, "x", "friend", emit=lines.append)
    with pytest.raises(ls.LabelError, match="overwrite"):
        make_pack(env, ids="all", out=labels / "p2", seed_keys=3, seed_key_out=key)
    assert "seeds: 3 (wrong_version 1, false_answer 1, false_abstain 1)" in lines
    assert f"wrote seed key file: sha256 {sha(key)}" in lines
    for s in k["seeds"]:
        naming = [ln for ln in lines if s["item_id"] in ln]
        assert naming and all(ln.startswith("selected ") for ln in naming)


def codes_2x2(a, b, c, d, missing=0):
    pairs = [(1, 1)] * a + [(1, 0)] * b + [(0, 1)] * c + [(0, 0)] * d + [(1, None)] * missing
    ids = [f"i{n}" for n in range(len(pairs))]
    return ids, {i: p[0] for i, p in zip(ids, pairs)}, {i: p[1] for i, p in zip(ids, pairs)}


def test_specific_agreement_hand_values():
    r = ag.specific_agreement(*codes_2x2(8, 1, 1, 0, missing=2))
    assert r["two_by_two"] == {"yes_yes": 8, "yes_no": 1, "no_yes": 1, "no_no": 0, "n_pairable": 10}
    assert r["p_pos"]["fraction"] == "16/18" and r["p_pos"]["value"] == 16 / 18
    assert r["p_neg"]["fraction"] == "0/2" and r["p_neg"]["value"] == 0
    assert r["yes_share"]["fraction"] == "18/20"
    r = ag.specific_agreement(*codes_2x2(6, 1, 1, 2))
    assert r["p_pos"]["value"] == 12 / 14 and r["p_neg"]["value"] == 4 / 6
    r = ag.specific_agreement(*codes_2x2(10, 0, 0, 0))
    assert r["p_pos"]["value"] == 1 and r["p_neg"]["value"] is None and r["p_neg"]["undefined_reason"]
    r = ag.specific_agreement(*codes_2x2(0, 0, 0, 0, missing=3))
    assert r["yes_share"]["value"] is None and r["two_by_two"]["n_pairable"] == 0


def b1_all(value, **overrides):
    return {**{i: value for i in ALL_IDS}, **overrides}


def test_seed_catch_counts_unsure_and_blank_as_not_caught(tmp_path):
    env = setup(tmp_path)
    plain = env["local"] / "labels" / "plain"
    make_pack(env, ids="all", out=plain)
    out, key, k = seeded_pack(env, "x", "friend")
    s = [x["item_id"] for x in k["seeds"]]
    la = fill(plain, tmp_path / "la", b1=b1_all("YES"))
    lb = fill(out, tmp_path / "lb", b1=b1_all("YES", **{s[0]: "NO", s[1]: "UNSURE", s[2]: "YES"}))
    res = ag.agree(la, lb, [key])
    sc = res["seed_catch"]
    assert (sc["n"], sc["caught"], sc["not_caught"]) == (3, 1, 2)
    assert sc["ids_not_caught"] == sorted(s[1:]) and sc["ci95"] == list(clopper_pearson(1, 3))
    assert res["measures"]["b1_key_supported"]["n_items_considered"] == 10
    assert res["b1_unseeded"]["two_by_two"]["yes_yes"] == 10 and res["seeded"]["n_seed_rows"] == 3
    assert ag.seed_catch(["x", "y"], {"x": "", "y": "NO"})["caught"] == 1
    assert ag.agree(la, lb)["seed_catch"] is None
    bogus = tmp_path / "bogus.json"
    bogus.write_text(json.dumps({"seeds": [{"item_id": "S-999-a", "type": "false_abstain"}]}), encoding="utf-8")
    with pytest.raises(ag.AgreeError, match="not in the sheets"):
        ag.agree(la, lb, [bogus])


def test_multi_dir_inputs_equal_single_dir(tmp_path):
    env = setup(tmp_path)
    labels = env["local"] / "labels"
    first, rest = ALL_IDS[:2], ALL_IDS[2:]
    make_pack(env, ids="all", out=labels / "whole")
    make_pack(env, ids=",".join(first), out=labels / "p1")
    make_pack(env, ids=",".join(rest), out=labels / "p2")
    b1_a = b1_all("YES", **{"S-001-a": "NO", "S-003-b": "NO"})
    b1_b = b1_all("YES", **{"S-001-a": "NO", "S-004-a": "NO"})
    whole = ag.agree(fill(labels / "whole", tmp_path / "wa", b1=b1_a), fill(labels / "whole", tmp_path / "wb", b1=b1_b))
    dirs_a = [fill(labels / p, tmp_path / f"a_{p}", b1=b1_a) for p in ("p1", "p2")]
    dirs_b = [fill(labels / p, tmp_path / f"b_{p}", b1=b1_b) for p in ("p1", "p2")]
    split = ag.agree(dirs_a, dirs_b)
    assert split["measures"] == whole["measures"] and split["b1_unseeded"] == whole["b1_unseeded"]
    assert [x["dir"] for x in split["inputs"]["a"]] == ["a_p1", "a_p2"]
    with pytest.raises(ag.AgreeError, match="repeated across dirs"):
        ag.agree([dirs_a[0], dirs_a[0]], dirs_b)
    assert ag.main(["--a", *map(str, dirs_a), "--b", *map(str, dirs_b), "--out", str(tmp_path / "m.json")]) == 0


def test_adjudication_template_flags_exactly_the_rule_rows(tmp_path, capsys):
    env = setup(tmp_path)
    plain = env["local"] / "labels" / "plain"
    make_pack(env, ids="all", out=plain)
    out, key, k = seeded_pack(env, "x", "friend")
    seeded = [x["item_id"] for x in k["seeds"]]
    notes = {r["item_id"]: r["lookup_note"] for r in read_csv(plain / "sheet_A.csv")[1]}
    found = [i for i in ALL_IDS if notes[i] == ls.ONE_VERSION and i not in seeded]
    a2 = {i: ("ANSWERABLE" if notes[i] == ls.ONE_VERSION else "") for i in ALL_IDS}
    a2_a = {**a2, "S-007-single": "ANSWERABLE", found[1]: "INDETERMINATE"}
    a2_b = {**a2, "S-007-single": "UNDERSPECIFIED", found[1]: "INDETERMINATE"}  # both agree, still flagged
    b1_a = b1_all("YES", **{found[0]: "NO", seeded[0]: "UNSURE"})
    b1_b = b1_all("YES", **{found[2]: "", **{s: "NO" for s in seeded}})  # seeded labeller's NO never flags
    la = fill(plain, tmp_path / "la", a2=a2_a, b1=b1_a)
    lb = fill(out, tmp_path / "lb", a2=a2_b, b1=b1_b)
    rows = adj.template_rows(ag.load_pair(la, lb, [key]))
    assert {r["item_id"]: r["flag"] for r in rows} == {
        found[0]: "B1_NO", found[1]: "A2_FOUND_NOT_ANSWERABLE", found[2]: "B1_UNSURE_OR_BLANK",
        "S-007-single": "A2_UNDATED_NOT_UNDERSPECIFIED", seeded[0]: "B1_UNSURE_OR_BLANK"}
    by = {r["item_id"]: r for r in rows}
    assert by[seeded[0]]["b_b1"] == adj.SEEDED_CELL and by[found[1]]["a_a2"] == "INDETERMINATE"
    assert all(r["outcome"] == r["reason_class"] == r["note"] == "" for r in rows)
    labels = env["local"] / "labels"
    target = labels / "adj.csv"
    assert adj.main(["--template", "--a", str(la), "--b", str(lb), "--seed-key", str(key), "--out", str(target)],
                    local_root=env["local"]) == 0
    assert read_csv(target)[0] == adj.COLUMNS and len(read_csv(target)[1]) == 5
    console = capsys.readouterr().out
    assert "flagged rows: 5" in console
    with pytest.raises(adj.AdjudicateError, match="overwrite"):
        adj.write_template(rows, target, env["local"])
    with pytest.raises(adj.AdjudicateError, match="_local/labels"):
        adj.write_template(rows, tmp_path / "outside.csv", env["local"])
    with pytest.raises(adj.AdjudicateError, match="runs"):
        adj.write_template(rows, ag.RUNS_DIR / "never.csv", env["local"])
    assert not (tmp_path / "outside.csv").exists() and not (ag.RUNS_DIR / "never.csv").exists()


def write_adj(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, adj.COLUMNS, lineterminator="\n")
        writer.writeheader()
        for item_id, outcome, reason in rows:
            writer.writerow({"item_id": item_id, "flag": "B1_NO", "outcome": outcome, "reason_class": reason})
    return path


def test_score_toy_sheets_and_value_errors(tmp_path):
    two = write_adj(tmp_path / "two.csv", [("S-1-a", "KEY_WRONG", "key_wrong"), ("S-2-a", "KEY_WRONG", "key_wrong"),
                                          ("S-3-a", "KEY_OK", ""), ("S-4-a", "CONTESTED", "guide_unclear"),
                                          ("S-5-a", "QUESTION_UNCLEAR", "question_unclear")])
    r = adj.score(two, 121)
    assert r["key_error_rate"] == {"value": 2 / 121, "fraction": "2/121"}
    assert r["ci95"] == list(clopper_pearson(2, 121)) and r["rule_of_three_upper"] is None
    assert r["counts_outcome"] == {"KEY_OK": 1, "KEY_WRONG": 2, "QUESTION_UNCLEAR": 1, "CONTESTED": 1}
    assert r["counts_reason_class"]["blank"] == 1 and r["counts_reason_class"]["key_wrong"] == 2
    assert r["contested_ids"] == ["S-4-a"] and r["question_unclear_ids"] == ["S-5-a"]
    zero = write_adj(tmp_path / "zero.csv", [("S-3-a", "KEY_OK", ""), ("S-4-a", "CONTESTED", "misread")])
    r0 = adj.score(zero, 121)
    assert r0["key_wrong"] == 0 and r0["rule_of_three_upper"] == 3 / 121 and r0["ci95"][0] == 0.0
    for name, rows, match in (("bad1", [("S-9-a", "MAYBE", "misread")], "S-9-a: outcome"),
                              ("bad2", [("S-8-a", "", "")], "S-8-a: outcome"),
                              ("bad3", [("S-7-a", "KEY_WRONG", "")], "S-7-a: reason_class is required"),
                              ("bad4", [("S-6-a", "KEY_OK", "bogus")], "S-6-a: reason_class")):
        with pytest.raises(adj.AdjudicateError, match=match):
            adj.score(write_adj(tmp_path / f"{name}.csv", rows), 121)
    with pytest.raises(adj.AdjudicateError, match="n-audited"):
        adj.score(two, 4)
    out = tmp_path / "score.json"
    assert adj.main(["--score", str(two), "--n-audited", "121", "--out", str(out)]) == 0
    assert adj.main(["--score", str(two), "--n-audited", "121", "--out", str(out)]) == 2  # no overwrite
    with pytest.raises(adj.AdjudicateError, match="runs"):
        adj.write_score(r, ag.RUNS_DIR / "never.json")
    assert not (ag.RUNS_DIR / "never.json").exists()