"""P10b B: labelling sheets for bench items.

    python -m divergence.bench_label_sheets --items divergence/bench/items/DEV.jsonl --split dev \
        --ids practice --out divergence/bench/_local/labels/practice/

Writes, only under divergence/bench/_local/:
  sheet_A.csv  blind sheet (question, date or tax year, plain-words lookup note, empty answer columns)
  sheet_B.csv  gold summary in words + nugget phrases from the local nuggets file, empty check columns
  texts/<item_id>.txt  section text of the version the lookup returns, or a one-line note
Console output is file names, counts and sha256 only, never statute or nugget text.
"practice" = the first slot of each stratum in slot-id order, whole pairs kept together (P10b-02).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

from divergence.bench_build import read_body, record_paths, split_paths
from divergence.bench_slots import BENCH_DIR, DEFAULT_SPEC, load_spec
from divergence.statute_schema import DEFAULT_ROOT, REASON_CLASS, body_sha256

SHEET_A = ("item_id", "question", "date_or_ty", "as_known_on", "lookup_note",
           "a1_my_answer", "a2_answerability", "a3_minutes", "notes")
SHEET_B = ("item_id", "gold_summary", "nugget_phrases", "b1_key_supported", "b2_reason",
           "b3_confidence", "notes")
ONE_VERSION = "one version applies"
UNDATED_NOTE = "no date or tax year given"
A2_NOTES = (ONE_VERSION, UNDATED_NOTE)  # rows on which a2 is filled (owner change B3)
OVERLAP_TAX_YEAR = "two versions possible for this tax year"  # owner change B2
REASON_NOTES = {
    "before_commencement": "not yet in force on this date",
    "prospective": "not yet in force on this date",
    "after_repeal": "after repeal",
    "beyond_corpus_horizon": "beyond the date our corpus is checked to",
    "overlap": "two versions possible on this day",
    "midyear_effect": "a change took effect partway through this tax year",
    "never_operative": "this version never came into force",
    "no_version_covers_point": "no version covers this date",
    "outstanding_effect": "a pending amendment may change the text on this date",
    "applicability_unclear_row": "the official table does not settle which version applies",
    "known_text_not_in_corpus": "the applicable text is known but not in our corpus",
    "repeal_day_unsettled": "whether the old Act applies on the repeal day is unsettled",
    "corrigendum_open": "an official correction to this text is still open",
    "before_coverage": "before the start of our corpus",
    "unknown_enactment_date": "the enactment date is not known",
    "unprinted_intermediate": "an intermediate version was never printed",
}
ACT_NAMES = {"1961": "Income-tax Act, 1961", "2025": "Income-tax Act, 2025"}
SIDE_ORDER = {"a": 0, "b": 1, "single": 2}
LOCAL_ROOT = BENCH_DIR / "_local"


class LabelError(ValueError):
    pass


def _side(item):
    return item["item_id"].rsplit("-", 1)[-1]


def slot_order(items):
    return sorted(items, key=lambda i: (i["slot_id"], SIDE_ORDER.get(_side(i), 9)))


def practice_ids(items):
    """First slot of each stratum in slot-id order; every side of that slot is kept."""
    chosen, ids = {}, []
    for item in slot_order(items):
        first = chosen.setdefault(item["stratum"], item["slot_id"])
        if first == item["slot_id"]:
            ids.append(item["item_id"])
    return ids


def select_ids(items, split, ids_arg):
    if ids_arg.strip() == "practice":
        if split != "dev":
            raise LabelError("practice is defined for the dev split only")
        return practice_ids(items)
    wanted = [s.strip() for s in ids_arg.split(",") if s.strip()]
    known = {i["item_id"] for i in items}
    unknown = [w for w in wanted if w not in known]
    if unknown:
        raise LabelError(f"unknown item ids: {unknown}")
    if len(set(wanted)) != len(wanted):
        raise LabelError("duplicate item ids in --ids")
    return wanted


def _priority(spec):
    order = {cat: n for n, cat in enumerate(spec["abstain_priority"])}
    return lambda code: (order[spec["abstain_categories"][REASON_CLASS[code]]], code)


def lookup_note(item, spec):
    if not item["dated"]:
        return UNDATED_NOTE
    reasons = list(item.get("gold_reasons") or [])
    if item["gold_status"] == "FOUND" and not reasons:
        return ONE_VERSION
    if not reasons:
        raise LabelError(f"{item['item_id']}: status {item['gold_status']} without reasons")
    unknown = [r for r in reasons if r not in REASON_NOTES or r not in REASON_CLASS]
    if unknown:
        raise LabelError(f"{item['item_id']}: unknown reason codes {unknown}")
    notes = []
    for code in sorted(reasons, key=_priority(spec)):
        note = OVERLAP_TAX_YEAR if code == "overlap" and item.get("tax_year") else REASON_NOTES[code]
        if note not in notes:
            notes.append(note)
    return "; ".join(notes)


def date_or_ty(item):
    if item.get("as_of"):
        return item["as_of"]
    ty = item.get("tax_year")
    if not ty:
        return ""
    if item["act"] == "1961":
        nxt = int(ty[:4]) + 1
        return f"previous year {ty} (assessment year {nxt}-{(nxt + 1) % 100:02d})"
    return f"tax year {ty}"


def gold_summary(item, note):
    abstain = ("should abstain - " + item["abstain_category"].replace("_", " ")
               if item["should_abstain"] else "should not abstain")
    if not item["dated"]:
        return f"no gold version ({note}); {abstain}"
    if item["gold_status"] == "FOUND":
        rid = item["gold_record_id"]
        version = rid.rsplit(":v", 1)[-1]
        act = ACT_NAMES.get(item["act"], f"Act {item['act']}")
        return f"FOUND ({note}): {act}, section {item['unit']}, version {version} [{rid}]; {abstain}"
    return f"{item['gold_status']} ({note}): no record; {abstain}"


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def inside(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def csv_bytes(fields, rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def build_pack(items, nugget_rows, root, spec, ids):
    """Return (sheet_a_rows, sheet_b_rows, texts{item_id: str}, counts); raises LabelError (ids only)."""
    by_id = {i["item_id"]: i for i in items}
    phrases = {}
    for n in nugget_rows:
        phrases.setdefault(n["item_id"], []).append(n)
    recs = record_paths(root) if any(by_id[i]["gold_status"] == "FOUND" for i in ids) else {}
    rows_a, rows_b, texts = [], [], {}
    counts = {"bodies": 0, "notes": 0, "nuggets": 0}
    for item_id in ids:
        item = by_id[item_id]
        note = lookup_note(item, spec)
        body = None
        if item["dated"] and item["gold_status"] == "FOUND":
            rid = item["gold_record_id"]
            if rid not in recs:
                raise LabelError(f"{item_id}: record {rid} not found")
            rec, path = recs[rid]
            body = read_body(root, rec, path)
            if body is None:
                raise LabelError(f"{item_id}: local body absent for {rid}")
            if rec.get("body_sha256") and body_sha256(body) != rec["body_sha256"]:
                raise LabelError(f"{item_id}: body sha256 differs from record {rid}")
            texts[item_id] = body
            counts["bodies"] += 1
        else:
            texts[item_id] = f"no single version applies: {note}\n"
            counts["notes"] += 1
        mine = sorted(phrases.get(item_id, []), key=lambda n: n["n"])
        for n in mine:
            if body is None or body[n["start"]:n["end"]] != n["phrase"]:
                raise LabelError(f"{item_id}: nugget {n['n']} does not match the gold body span")
        counts["nuggets"] += len(mine)
        rows_a.append({"item_id": item_id, "question": item["question"], "date_or_ty": date_or_ty(item),
                       "as_known_on": item["as_known_on"], "lookup_note": note})
        rows_b.append({"item_id": item_id, "gold_summary": gold_summary(item, note),
                       "nugget_phrases": " | ".join(f"[{n['n']}] {n['phrase']}" for n in mine)})
    return rows_a, rows_b, texts, counts


def run(items_path, split, ids_arg, out, *, root=DEFAULT_ROOT, nuggets=None, spec_path=DEFAULT_SPEC,
        local_root=LOCAL_ROOT, emit=print):
    out = Path(out)
    if not inside(out, local_root):
        raise LabelError(f"--out must be inside {local_root}")
    taken = [name for name in ("sheet_A.csv", "sheet_B.csv", "texts") if (out / name).exists()]
    if taken:
        raise LabelError(f"refusing to overwrite existing {taken} in {out}")
    items = read_jsonl(items_path)
    wrong = sorted({i["item_id"] for i in items if i["split"] != split})
    if wrong:
        raise LabelError(f"items not in split {split}: {wrong}")
    ids = select_ids(items, split, ids_arg)
    if not ids:
        raise LabelError("no items selected")
    emit(f"selected {len(ids)} item(s): {','.join(ids)}")
    nuggets = Path(nuggets) if nuggets else split_paths(BENCH_DIR, split)["nuggets"]
    nugget_rows = read_jsonl(nuggets) if nuggets.is_file() else []
    rows_a, rows_b, texts, counts = build_pack(items, nugget_rows, root, load_spec(spec_path), ids)
    (out / "texts").mkdir(parents=True, exist_ok=False)
    for name, data in (("sheet_A.csv", csv_bytes(SHEET_A, rows_a)), ("sheet_B.csv", csv_bytes(SHEET_B, rows_b))):
        (out / name).write_bytes(data)
        emit(f"wrote {name}: rows {len(rows_a)}, sha256 {hashlib.sha256(data).hexdigest()}")
    for item_id, text in texts.items():
        (out / "texts" / f"{item_id}.txt").write_bytes(text.encode("utf-8"))
    emit(f"wrote texts/: {len(texts)} file(s) ({counts['bodies']} section bodies, {counts['notes']} notes); "
         f"nugget phrases {counts['nuggets']}")
    return ids


def main(argv=None, **overrides):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--split", choices=("dev", "test"), required=True)
    parser.add_argument("--ids", required=True, help='comma list of item ids, or "practice"')
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        run(args.items, args.split, args.ids, args.out, **overrides)
    except LabelError as exc:
        print(f"bench label sheets: ERROR {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
