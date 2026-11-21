"""P10a bench_validate: one test per rule on synthetic items (placeholder words, no law text)."""
import copy
import json

import pytest

from divergence import bench_build as bb
from divergence import bench_slots as bs
from divergence import bench_validate as bv

from test_bench_build import draft_rows
from test_bench_slots import BODIES, _rows, make_corpus


@pytest.fixture
def world(tmp_path):
    root, spec, _ = make_corpus(tmp_path)
    slot_rows = _rows(bs.generate(spec, root)[0])
    built = {}
    for split in ("dev", "test"):
        _, items, _, status, errors, missing = bb.build(draft_rows(slot_rows, split), slot_rows, spec, root,
                                                        "2026-11-21")
        assert not errors and not missing
        built[split] = (items, status)
    return {"root": root, "spec": spec, "slots": slot_rows, "built": built}


def run(world, split="test", items=None, slots=None, spec=None, caveats=(), status=None, partial=False, root=None):
    base_items, base_status = world["built"][split]
    out, _ = bv.validate(items if items is not None else base_items, slots or world["slots"],
                         spec or world["spec"], root or world["root"], list(caveats),
                         base_status if status is None else status, partial)
    return {rid: entry["status"] for rid, entry in out.items()}


def _item(items, pred):
    return next(i for i in items if pred(i))


def test_valid_dev_and_test_pass(world):
    for split in ("dev", "test"):
        result = run(world, split)
        assert "FAIL" not in result.values(), result
        assert result["R07"] == "PASS" and result["R09"] == "PASS"
    assert run(world, "dev")["R11"] == "SKIP"


def test_r01_schema(world):
    items = copy.deepcopy(world["built"]["test"][0])
    del items[0]["notes"]
    assert run(world, items=items)["R01"] == "FAIL"


def test_r02_slot_match(world):
    items = copy.deepcopy(world["built"]["test"][0])
    _item(items, lambda i: i["dated"])["unit"] = "Q"
    assert run(world, items=items)["R02"] == "FAIL"


def test_r03_lookup_recompute(world):
    items = copy.deepcopy(world["built"]["test"][0])
    slots = copy.deepcopy(world["slots"])
    item = _item(items, lambda i: i["gold_status"] == "FOUND")
    item["gold_record_id"] = "act:1961:X:v9"
    side = item["item_id"].rsplit("-", 1)[1]
    _item(slots, lambda r: (r["slot_id"], r["side"]) == (item["slot_id"], side))["gold_record_id"] = "act:1961:X:v9"
    assert run(world, items=items, slots=slots)["R03"] == "FAIL"


def test_r04_abstain_consistency(world):
    items = copy.deepcopy(world["built"]["test"][0])
    slots = copy.deepcopy(world["slots"])
    item = _item(items, lambda i: i["gold_status"] == "FOUND")
    item["should_abstain"] = True
    side = item["item_id"].rsplit("-", 1)[1]
    _item(slots, lambda r: (r["slot_id"], r["side"]) == (item["slot_id"], side))["should_abstain"] = "true"
    result = run(world, items=items, slots=slots)
    assert result["R04"] == "FAIL" and result["R02"] == "PASS"


def test_r05_dated_question_needs_date(world):
    items = copy.deepcopy(world["built"]["test"][0])
    _item(items, lambda i: i["dated"])["question"] = "Which version applies to this person?"
    assert run(world, items=items)["R05"] == "FAIL"


def test_r06_undated_question_has_no_date(world):
    items = copy.deepcopy(world["built"]["test"][0])
    _item(items, lambda i: not i["dated"])["question"] = "Which version applies for tax year 2024-25?"
    assert run(world, items=items)["R06"] == "FAIL"


def test_r07_nugget_bounds(world):
    items = copy.deepcopy(world["built"]["test"][0])
    nug = _item(items, lambda i: i["nuggets"])["nuggets"][0]
    nug["end"] = len(BODIES[nug["record_id"]]) + 5
    assert run(world, items=items)["R07"] == "FAIL"


def test_r08_nugget_sha16(world):
    items = copy.deepcopy(world["built"]["test"][0])
    _item(items, lambda i: i["nuggets"])["nuggets"][0]["sha16"] = "0" * 16
    assert run(world, items=items)["R08"] == "FAIL"


def _caveat(nug, start, end):
    return {"caveat_id": "C1", "record_id": nug["record_id"], "start": str(start), "end": str(end)}


def test_r09_span_caveat_crossing_and_gazette_exemption(world):
    items = copy.deepcopy(world["built"]["test"][0])
    item = _item(items, lambda i: i["nuggets"])
    nug = item["nuggets"][0]
    crossing = [_caveat(nug, nug["start"] + 1, nug["end"] + 3)]
    assert run(world, items=items, caveats=crossing)["R09"] == "FAIL"
    outside = [_caveat(nug, nug["end"], nug["end"] + 3)]
    assert run(world, items=items, caveats=outside)["R09"] == "PASS"
    for other in items:
        for n in other["nuggets"]:
            if n["record_id"] == nug["record_id"]:
                n["quotes_gazette"] = True
    assert run(world, items=items, caveats=crossing)["R09"] == "PASS"


def test_r09_point_caveat(world):
    items = copy.deepcopy(world["built"]["test"][0])
    nug = _item(items, lambda i: i["nuggets"])["nuggets"][0]
    assert run(world, items=items, caveats=[_caveat(nug, nug["start"] + 2, nug["start"] + 2)])["R09"] == "FAIL"
    assert run(world, items=items, caveats=[_caveat(nug, nug["start"], nug["start"])])["R09"] == "PASS"


def test_r07_to_r09_skip_without_bodies(world, tmp_path):
    for body in (world["root"] / "_local_text").rglob("*.txt"):
        body.unlink()
    result = run(world)
    assert result["R07"] == result["R08"] == result["R09"] == "SKIP"


def test_r10_quotas_and_partial(world):
    items = world["built"]["test"][0]
    pid = next(i["pair_id"] for i in items if i["pair_id"])
    fewer = [i for i in items if i["pair_id"] != pid]
    assert run(world, items=fewer)["R10"] == "FAIL"
    assert run(world, items=fewer, partial=True)["R10"] == "INFO"


def test_r11_per_unit_cap(world):
    spec = dict(world["spec"], max_test_items_per_unit=2)
    assert run(world, spec=spec)["R11"] == "FAIL"


def test_r12_pair_complete(world):
    items = world["built"]["test"][0]
    drop = next(i["item_id"] for i in items if i["item_id"].endswith("-b"))
    result = run(world, items=[i for i in items if i["item_id"] != drop])
    assert result["R12"] == "FAIL"


def test_r12_pair_gold_must_differ(world):
    items = copy.deepcopy(world["built"]["test"][0])
    a = _item(items, lambda i: i["item_id"].endswith("-a") and i["stratum"] == "version_lookup")
    b = _item(items, lambda i: i["item_id"] == a["item_id"][:-1] + "b")
    for key in ("gold_status", "gold_record_id", "gold_reasons"):
        b[key] = a[key]
    assert run(world, items=items)["R12"] == "FAIL"


def test_r13_duplicates(world):
    items = copy.deepcopy(world["built"]["test"][0])
    assert run(world, items=items + [copy.deepcopy(items[0])])["R13"] == "FAIL"


def test_r14_active_slots_and_reserve_pull(world):
    slots, spec, root = world["slots"], world["spec"], world["root"]
    items = world["built"]["test"][0]
    reserve = next(r for r in slots if r["split"] == "test" and r["reserve"] == "true")
    stray = copy.deepcopy(items[0])
    stray["slot_id"] = reserve["slot_id"]
    assert run(world, items=items + [stray])["R14"] == "FAIL"
    victim = next(r for r in slots if r["split"] == "test" and r["reserve"] == "false"
                  and r["stratum"] == reserve["stratum"])["slot_id"]
    rows = draft_rows(slots, "test")
    for row in rows:
        if row["slot_id"] == victim:
            row["status"], row["unusable_reason"] = "unusable", "no condition in record"
    rows += draft_rows(slots, "test", {reserve["slot_id"]})
    _, new_items, _, status, errors, missing = bb.build(rows, slots, spec, root, "2026-11-21")
    assert not errors and not missing
    assert any(s["slot_id"] == victim and s["pulled_into"] == reserve["slot_id"] for s in status)
    result = run(world, items=new_items, status=status)
    assert "FAIL" not in result.values(), result
    wrong = [dict(s, pulled_into="") if s["slot_id"] == victim else s for s in status]
    assert run(world, items=new_items, status=wrong)["R14"] == "FAIL"


def test_r15_split_disjoint(world):
    slots = copy.deepcopy(world["slots"])
    test_pair = {r["side"]: r for r in slots if r["split"] == "test" and r["slot_id"] == "T-001"}
    dev_id = next(r["slot_id"] for r in slots if r["split"] == "dev" and r["side"] == "a")
    for r in slots:
        if r["slot_id"] == dev_id:
            src = test_pair[r["side"]]
            r.update({k: src[k] for k in ("act", "unit", "as_of", "tax_year")})
    assert run(world, slots=slots)["R15"] == "FAIL"


def test_date_expression_patterns():
    for text in ("on 2024-05-01?", "on 1 April 2025", "on April 1, 2025", "in May 2025", "for 2024-25",
                 "for FY 2024/25", "on 01/04/2025"):
        assert bv.has_date_expression(text), text
    for text in ("under the Income-tax Act, 1961", "under section 194S", "the 2025 Act", "(T-013 a)"):
        assert not bv.has_date_expression(text), text


def test_r16_clock_phrase():
    base = {"dated": True, "act": "1961", "as_of": "2025-09-05", "tax_year": None}
    ok = dict(base, question="As in force on 5 September 2025, which version applies?")
    assert bv.clock_phrase_ok(ok)
    assert bv.clock_phrase_ok(dict(ok, question="AS IN FORCE ON 5  September 2025, which version?"))
    assert not bv.clock_phrase_ok(dict(base, question="Which version applies on 5 September 2025?"))
    assert not bv.clock_phrase_ok(dict(base, question="As in force on 6 September 2025, which version?"))
    assert not bv.clock_phrase_ok(dict(base, question="As in force on 05 September 2025, which version?"))
    ty = {"dated": True, "act": "1961", "as_of": None, "tax_year": "2024-25"}
    assert bv.clock_phrase_ok(dict(ty, question="For previous year 2024-25 (assessment year 2025-26), which?"))
    assert not bv.clock_phrase_ok(dict(ty, question="For previous year 2024-25, which version applies?"))
    assert not bv.clock_phrase_ok(dict(ty, question="For tax year 2024-25, which version applies?"))
    assert bv.clock_phrase_ok({"dated": True, "act": "2025", "as_of": None, "tax_year": "2026-27",
                               "question": "Which version applies for tax year 2026-27?"})
    assert bv.clock_phrase_ok({"dated": False, "act": "1961", "as_of": None, "tax_year": None,
                               "question": "Which version of the provision applies?"})
    assert bv.date_words("2024-01-31") == "31 January 2024"


def test_r16_integration(world):
    assert run(world)["R16"] == "PASS"
    items = copy.deepcopy(world["built"]["test"][0])
    item = _item(items, lambda i: i["dated"] and i["as_of"])
    item["question"] = item["question"].replace("As in force on", "Which version applied on")
    result = run(world, items=items)
    assert result["R16"] == "FAIL" and result["R05"] == "PASS"


def test_offsetless_caveat_rows_skipped(world):
    items = world["built"]["test"][0]
    nug = _item(items, lambda i: i["nuggets"])["nuggets"][0]
    gap = {"caveat_id": "G1", "record_id": nug["record_id"], "start": "", "end": ""}
    out, _ = bv.validate(items, world["slots"], world["spec"], world["root"], [gap],
                         world["built"]["test"][1], False)
    assert out["R09"]["status"] == "PASS" and "1 offset-less caveat row(s) skipped" in out["R09"]["note"]
    crossing = [gap, _caveat(nug, nug["start"] + 1, nug["end"] + 3)]
    assert run(world, items=items, caveats=crossing)["R09"] == "FAIL"


def test_cli_exit_codes(world, tmp_path, capsys):
    items, status = world["built"]["test"]
    path = tmp_path / "TEST.jsonl"
    path.write_bytes(bb.jsonl_bytes(items))
    (tmp_path / "TEST.status.csv").write_bytes(bb.status_bytes(status))
    slots = tmp_path / "SLOTS.csv"
    slots.write_bytes(bs.csv_bytes(world["slots"]))
    spec = tmp_path / "spec2.json"
    spec.write_text(json.dumps(world["spec"]), encoding="utf-8")
    args = ["--items", str(path), "--slots", str(slots), "--spec", str(spec), "--root", str(world["root"])]
    assert bv.main(args) == 0
    out = capsys.readouterr().out
    assert "Which version" not in out and "proviso" not in out.lower()
    bad = copy.deepcopy(items)
    bad[0]["notes"] = 5
    path.write_bytes(bb.jsonl_bytes(bad))
    assert bv.main(args) == 1
