"""P10a bench_build on a synthetic corpus/body in tmp_path (placeholder words, no law text)."""
import json

from divergence import bench_build as bb
from divergence import bench_slots as bs
from divergence.bench_validate import date_words
from divergence.statute_schema import body_sha256

from test_bench_slots import BODIES, PHRASES, _rows, make_corpus


def draft_rows(slot_rows, split, slot_ids=None):
    """One draft row per side of the given (default: main) slots; questions carry slot ids."""
    wanted = slot_ids or {r["slot_id"] for r in slot_rows if r["split"] == split and r["reserve"] == "false"}
    rows = []
    for r in slot_rows:
        if r["split"] != split or r["slot_id"] not in wanted:
            continue
        tag = f"({r['slot_id']} {r['side']})"
        if r["as_of"]:
            question = f"As in force on {date_words(r['as_of'])}, which version applies? {tag}"
        elif r["tax_year"] and r["act"] == "1961":
            nxt = int(r["tax_year"][:4]) + 1
            question = (f"For previous year {r['tax_year']} (assessment year {nxt}-{(nxt + 1) % 100:02d}), "
                        f"which version applies? {tag}")
        elif r["tax_year"]:
            question = f"Which version applies for tax year {r['tax_year']}? {tag}"
        else:
            question = f"Which version of the provision applies? {tag}"
        row = {"slot_id": r["slot_id"], "side": r["side"], "status": "", "unusable_reason": "",
               "question": question, "notes": ""}
        if r["gold_record_id"] in PHRASES:
            row["nugget_phrase_1"] = PHRASES[r["gold_record_id"]]
        rows.append(row)
    return rows


def setup(tmp_path, **kw):
    root, spec, spec_path = make_corpus(tmp_path, **kw)
    slot_rows = _rows(bs.generate(spec, root)[0])
    return root, spec, spec_path, slot_rows


def test_offsets_and_sha16_on_synthetic_body(tmp_path):
    root, spec, _, slot_rows = setup(tmp_path)
    split, items, nuggets, status, errors, missing = bb.build(draft_rows(slot_rows, "dev"), slot_rows, spec,
                                                              root, "2026-11-21")
    assert split == "dev" and not errors and not missing and items
    with_nuggets = [i for i in items if i["nuggets"]]
    assert with_nuggets
    for item in with_nuggets:
        nug = item["nuggets"][0]
        body = BODIES[nug["record_id"]]
        assert body[nug["start"]:nug["end"]] == PHRASES[nug["record_id"]]
        assert nug["sha16"] == body_sha256(body[nug["start"]:nug["end"]])[:16]
        assert nug["record_id"] == item["gold_record_id"]
    assert all("phrase" not in n for i in items for n in i["nuggets"])
    assert {n["item_id"] for n in nuggets} == {i["item_id"] for i in with_nuggets}
    assert all(s["status"] in ("active", "reserve_unused") for s in status)


def test_zero_and_ambiguous_hits_are_errors_without_text(tmp_path):
    root, spec, _, slot_rows = setup(tmp_path)
    rows = draft_rows(slot_rows, "test")
    target = next(r for r in rows if r.get("nugget_phrase_1") == "Beta proviso")
    target["nugget_phrase_1"] = "Missing placeholder words"
    _, _, _, _, errors, _ = bb.build(rows, slot_rows, spec, root, "2026-11-21")
    assert any("not found" in e and target["slot_id"] in e for e in errors)
    assert not any("Missing placeholder" in e for e in errors)
    target["nugget_phrase_1"] = "Alpha clause"  # appears twice in the X v1 body
    _, _, _, _, errors, _ = bb.build(rows, slot_rows, spec, root, "2026-11-21")
    assert any("ambiguous" in e for e in errors) and not any("Alpha" in e for e in errors)
    target["nugget_occurrence_1"] = "2"
    _, items, _, _, errors, _ = bb.build(rows, slot_rows, spec, root, "2026-11-21")
    assert not errors, errors
    item = next(i for i in items if i["item_id"] == f"{target['slot_id']}-{target['side']}")
    assert item["nuggets"][0]["start"] == BODIES["act:1961:X:v1"].rfind("Alpha clause")


def test_gold_mismatch_and_nugget_without_record_are_errors(tmp_path):
    root, spec, _, slot_rows = setup(tmp_path)
    rows = draft_rows(slot_rows, "dev")
    tampered = [dict(r) for r in slot_rows]
    victim = next(r for r in tampered if r["split"] == "dev" and r["gold_status"] == "FOUND")
    victim["gold_record_id"] = "act:1961:X:v9"
    _, _, _, _, errors, _ = bb.build(rows, tampered, spec, root, "2026-11-21")
    assert any("lookup gold differs" in e for e in errors)
    abstain = next(r for r in rows if not r.get("nugget_phrase_1"))
    abstain["nugget_phrase_1"] = "Kappa term"
    _, _, _, _, errors, _ = bb.build(rows, slot_rows, spec, root, "2026-11-21")
    assert any("no gold_record_id" in e for e in errors)


def test_cli_refuses_when_bodies_absent(tmp_path, capsys):
    root, spec, spec_path, slot_rows = setup(tmp_path, bodies=False)
    slots = tmp_path / "SLOTS.csv"
    slots.write_bytes(bs.csv_bytes(slot_rows))
    draft = tmp_path / "draft.csv"
    _write_draft(draft, draft_rows(slot_rows, "dev"))
    code = bb.main(["--draft", str(draft), "--created", "2026-11-21", "--slots", str(slots), "--spec",
                    str(spec_path), "--root", str(root), "--bench-dir", str(tmp_path / "bench")])
    assert code == 2 and "REFUSED" in capsys.readouterr().out
    assert not (tmp_path / "bench").exists()


def test_cli_writes_dev_public_test_local_and_refuses_overwrite(tmp_path):
    root, spec, spec_path, slot_rows = setup(tmp_path)
    slots = tmp_path / "SLOTS.csv"
    slots.write_bytes(bs.csv_bytes(slot_rows))
    bench = tmp_path / "bench"
    for split in ("dev", "test"):
        draft = tmp_path / f"draft_{split}.csv"
        _write_draft(draft, draft_rows(slot_rows, split))
        args = ["--draft", str(draft), "--created", "2026-11-21", "--slots", str(slots), "--spec", str(spec_path),
                "--root", str(root), "--bench-dir", str(bench)]
        assert bb.main(args) == 0
        assert bb.main(args) == 2
        assert bb.main(args + ["--force"]) == 0
    assert (bench / "items" / "DEV.jsonl").is_file()
    assert (bench / "_local" / "items" / "TEST.jsonl").is_file()
    assert not (bench / "items" / "TEST.jsonl").exists()
    public = (bench / "items" / "DEV.jsonl").read_text(encoding="utf-8")
    assert not any(p in public for p in PHRASES.values())
    lines = (bench / "_local" / "nuggets" / "dev.jsonl").read_text(encoding="utf-8").splitlines()
    assert lines and all(json.loads(line)["phrase"] in PHRASES.values() for line in lines)


def _write_draft(path, rows):
    import csv
    fields = ["slot_id", "side", "status", "unusable_reason", "question", "notes"]
    for n in (1, 2, 3):
        fields += [f"nugget_phrase_{n}", f"nugget_occurrence_{n}", f"nugget_match_{n}", f"quotes_gazette_{n}"]
    with open(path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
