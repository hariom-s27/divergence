"""P10b B: labelling sheets for bench items.

    python -m divergence.bench_label_sheets --items divergence/bench/items/DEV.jsonl --split dev \
        --ids practice --out divergence/bench/_local/labels/practice/

Writes, only under divergence/bench/_local/:
  sheet_A.csv  blind sheet (question, date or tax year, plain-words lookup note, empty answer columns)
  sheet_B.csv  gold summary in words + nugget phrases from the local nuggets file, empty check columns
  texts/<item_id>.txt  section text of the version the lookup returns, or a one-line note
Console output is file names, counts and sha256 only, never statute or nugget text.
"practice" = the first slot of each stratum in slot-id order, whole pairs kept together (P10b-02).
"--ids all" = every item of the split; "--exclude practice" drops the practice ids (P10c-07).

P10c seeded keys (friend pack only): --seed-keys N --seed-key-out <file under _local/labels/_keys/>
changes the Sheet B key of N rows in place; Sheet A and texts/ stay byte-identical to an unseeded run.
Seed types (owner decision D1): wrong_version (FOUND row, partner FOUND with another record and nugget
phrases, not cross_act_counterpart: key cites the partner's record and phrases), false_answer (dated
should-abstain row whose partner is FOUND: key claims the partner's record, should not abstain),
false_abstain (FOUND row: key claims no applicable version, should abstain - false premise).
The key file is written only to --seed-key-out; the console never names the seeded ids.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import sys
from collections import Counter
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
SEED_TYPES = ("wrong_version", "false_answer", "false_abstain")
NO_WRONG_VERSION_STRATA = ("cross_act_counterpart",)  # owner decision D1


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


def _practice(items, split):
    if split != "dev":
        raise LabelError("practice is defined for the dev split only")
    return practice_ids(items)


def select_ids(items, split, ids_arg, exclude=None):
    arg = ids_arg.strip()
    if arg == "practice":
        wanted = _practice(items, split)
    elif arg == "all":
        wanted = [i["item_id"] for i in slot_order(items)]
    else:
        wanted = [s.strip() for s in ids_arg.split(",") if s.strip()]
        known = {i["item_id"] for i in items}
        unknown = [w for w in wanted if w not in known]
        if unknown:
            raise LabelError(f"unknown item ids: {unknown}")
        if len(set(wanted)) != len(wanted):
            raise LabelError("duplicate item ids in --ids")
    if exclude is None:
        return wanted
    if exclude != "practice":
        raise LabelError('--exclude accepts only "practice"')
    drop = set(_practice(items, split))
    return [w for w in wanted if w not in drop]


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
                       "nugget_phrases": phrases_text(mine)})
    return rows_a, rows_b, texts, counts


def phrases_text(nugget_rows):
    return " | ".join(f"[{n['n']}] {n['phrase']}" for n in sorted(nugget_rows, key=lambda n: n["n"]))


def partner_of(item, by_id):
    others = [i for i in by_id.values() if i.get("pair_id") == item.get("pair_id") and i["item_id"] != item["item_id"]]
    return others[0] if len(others) == 1 else None


def _found_one_version(item, spec):
    return item["dated"] and item["gold_status"] == "FOUND" and lookup_note(item, spec) == ONE_VERSION


def seed_eligibility(items, nugget_rows, ids, spec):
    """{seed type: sorted item ids eligible for it} over the selected ids (owner decision D1)."""
    by_id = {i["item_id"]: i for i in items}
    has_nuggets = {n["item_id"] for n in nugget_rows}
    eligible = {t: [] for t in SEED_TYPES}
    for item_id in sorted(ids):
        item = by_id[item_id]
        partner = partner_of(item, by_id)
        partner_found = partner is not None and partner["dated"] and partner["gold_status"] == "FOUND"
        if _found_one_version(item, spec):
            eligible["false_abstain"].append(item_id)
            if (partner_found and item["stratum"] not in NO_WRONG_VERSION_STRATA
                    and partner["gold_record_id"] != item["gold_record_id"]
                    and partner["item_id"] in has_nuggets):
                eligible["wrong_version"].append(item_id)
        elif item["should_abstain"] and item["dated"] and partner_found:
            eligible["false_answer"].append(item_id)
    return eligible


def choose_seeds(eligible, n, rng):
    """Type order shuffled once, then cycled; one seed per item. Raises when fewer than n rows are seedable."""
    available = set().union(*eligible.values()) if eligible else set()
    if n > len(available):
        raise LabelError(f"--seed-keys {n} asks for more seeds than the {len(available)} seedable row(s)")
    types = list(SEED_TYPES)
    rng.shuffle(types)
    used, picks = set(), []
    while len(picks) < n:
        progress = False
        for seed_type in types:
            if len(picks) == n:
                break
            pool = [i for i in eligible.get(seed_type, []) if i not in used]
            if pool:
                pick = rng.choice(sorted(pool))
                used.add(pick)
                picks.append((pick, seed_type))
                progress = True
        if not progress:
            raise LabelError(f"could place only {len(picks)} of {n} seeds")
    return picks


def seeded_key(item, partner, nugget_rows, seed_type):
    """Return (gold_summary, nugget_phrases) for a seeded row, in the same wording as real rows."""
    if seed_type == "wrong_version":
        fake = dict(item, gold_record_id=partner["gold_record_id"], act=partner["act"], unit=partner["unit"])
        mine = [n for n in nugget_rows if n["item_id"] == partner["item_id"]]
        return gold_summary(fake, ONE_VERSION), phrases_text(mine)
    if seed_type == "false_answer":
        fake = dict(item, gold_status="FOUND", gold_record_id=partner["gold_record_id"], act=partner["act"],
                    unit=partner["unit"], should_abstain=False, abstain_category=None)
        return gold_summary(fake, ONE_VERSION), ""
    if seed_type == "false_abstain":
        fake = dict(item, gold_status="NO_APPLICABLE_VERSION", should_abstain=True, abstain_category="false_premise")
        return gold_summary(fake, REASON_NOTES["before_commencement"]), ""
    raise LabelError(f"unknown seed type {seed_type}")


def apply_seeds(items, nugget_rows, rows_b, ids, spec, n, pack_name):
    rng = random.Random(f"{spec['seed']}-seeds-{pack_name}")
    picks = choose_seeds(seed_eligibility(items, nugget_rows, ids, spec), n, rng)
    by_id = {i["item_id"]: i for i in items}
    rows = {r["item_id"]: r for r in rows_b}
    for item_id, seed_type in picks:
        item = by_id[item_id]
        summary, phrases = seeded_key(item, partner_of(item, by_id), nugget_rows, seed_type)
        rows[item_id]["gold_summary"] = summary
        rows[item_id]["nugget_phrases"] = phrases
    return sorted(picks)


def _check_seed_args(seed_keys, seed_key_out, out, local_root):
    if seed_keys < 0:
        raise LabelError("--seed-keys must be 0 or more")
    if (seed_keys > 0) != (seed_key_out is not None):
        raise LabelError("--seed-keys and --seed-key-out go together (both or neither)")
    if seed_key_out is None:
        return None
    key = Path(seed_key_out)
    if not inside(key, Path(local_root) / "labels" / "_keys"):
        raise LabelError("--seed-key-out must be inside _local/labels/_keys/")
    if inside(key, out):
        raise LabelError("--seed-key-out must not be inside --out")
    if key.exists():
        raise LabelError(f"refusing to overwrite existing {key.name}")
    return key


def run(items_path, split, ids_arg, out, *, exclude=None, seed_keys=0, seed_key_out=None, root=DEFAULT_ROOT,
        nuggets=None, spec_path=DEFAULT_SPEC, local_root=LOCAL_ROOT, emit=print):
    out = Path(out)
    if not inside(out, local_root):
        raise LabelError(f"--out must be inside {local_root}")
    key_path = _check_seed_args(seed_keys, seed_key_out, out, local_root)
    taken = [name for name in ("sheet_A.csv", "sheet_B.csv", "texts") if (out / name).exists()]
    if taken:
        raise LabelError(f"refusing to overwrite existing {taken} in {out}")
    items_bytes = Path(items_path).read_bytes()
    items = read_jsonl(items_path)
    wrong = sorted({i["item_id"] for i in items if i["split"] != split})
    if wrong:
        raise LabelError(f"items not in split {split}: {wrong}")
    ids = select_ids(items, split, ids_arg, exclude)
    if not ids:
        raise LabelError("no items selected")
    emit(f"selected {len(ids)} item(s): {','.join(ids)}")
    nuggets = Path(nuggets) if nuggets else split_paths(BENCH_DIR, split)["nuggets"]
    nugget_rows = read_jsonl(nuggets) if nuggets.is_file() else []
    spec = load_spec(spec_path)
    rows_a, rows_b, texts, counts = build_pack(items, nugget_rows, root, spec, ids)
    key_data = None
    if key_path is not None:
        pack_name = out.resolve().name
        picks = apply_seeds(items, nugget_rows, rows_b, ids, spec, seed_keys, pack_name)
        key_obj = {"pack": pack_name, "seed": f"{spec['seed']}-seeds-{pack_name}",
                   "items_sha256": hashlib.sha256(items_bytes).hexdigest(),
                   "seeds": [{"item_id": i, "type": t} for i, t in picks]}
        key_data = (json.dumps(key_obj, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (out / "texts").mkdir(parents=True, exist_ok=False)
    for name, data in (("sheet_A.csv", csv_bytes(SHEET_A, rows_a)), ("sheet_B.csv", csv_bytes(SHEET_B, rows_b))):
        (out / name).write_bytes(data)
        emit(f"wrote {name}: rows {len(rows_a)}, sha256 {hashlib.sha256(data).hexdigest()}")
    for item_id, text in texts.items():
        (out / "texts" / f"{item_id}.txt").write_bytes(text.encode("utf-8"))
    emit(f"wrote texts/: {len(texts)} file(s) ({counts['bodies']} section bodies, {counts['notes']} notes); "
         f"nugget phrases {counts['nuggets']}")
    if key_data is not None:
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_bytes(key_data)
        per_type = Counter(t for _, t in picks)
        emit(f"seeds: {len(picks)} (" + ", ".join(f"{t} {per_type.get(t, 0)}" for t in SEED_TYPES) + ")")
        emit(f"wrote seed key file: sha256 {hashlib.sha256(key_data).hexdigest()}")
    return ids


def main(argv=None, **overrides):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--split", choices=("dev", "test"), required=True)
    parser.add_argument("--ids", required=True, help='comma list of item ids, "practice" or "all"')
    parser.add_argument("--exclude", choices=("practice",), default=None)
    parser.add_argument("--seed-keys", type=int, default=0)
    parser.add_argument("--seed-key-out", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        run(args.items, args.split, args.ids, args.out, exclude=args.exclude, seed_keys=args.seed_keys,
            seed_key_out=args.seed_key_out, **overrides)
    except LabelError as exc:
        print(f"bench label sheets: ERROR {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
