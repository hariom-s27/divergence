"""P10a bench item builder (P10-05/06/07). Owner draft CSV -> items JSONL.

Gold comes from the slot and is re-checked against lookup(); nugget offsets come from an
exact search of the phrase in the local body of gold_record_id. Nugget phrases are written
only to the git-ignored folder <bench>/_local/nuggets/. Errors name slot ids and nugget
numbers, never phrase or body text. TEST items go to <bench>/_local/items/ until the seal.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

from divergence.bench_slots import (BENCH_DIR, DEFAULT_OUT, DEFAULT_SPEC, UNDATED, active_slots,
                                    load_spec, read_slots)
from divergence.statute_lookup import lookup
from divergence.statute_schema import DEFAULT_ROOT, body_sha256, parse_date
from divergence.statute_validate import body_path

NUGGETS = (1, 2, 3)
MATCHES = ("exact", "regex", "numeric")
AUTHORS = ("owner", "claude-draft")
STATUS_FIELDS = ("slot_id", "status", "pulled_into", "reason")
TRUE = ("true", "yes", "1", "y")
FALSE = ("", "false", "no", "0", "n")


class BuildError(ValueError):
    pass


def record_paths(root):
    """record_id -> (record, json_path); metadata only."""
    out = {}
    for path in sorted((Path(root) / "records").glob("*/*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        out[rec["record_id"]] = (rec, path)
    return out


def read_body(root, rec, path):
    """Body text or None if the local body file is absent."""
    bp = body_path(Path(root), rec, path)
    return bp.read_bytes().decode("utf-8") if bp.is_file() else None


def find_span(body, phrase, occurrence):
    """(start, end) of the occurrence-th exact hit; occurrence None means exactly one hit required."""
    hits, pos = [], body.find(phrase)
    while pos != -1:
        hits.append(pos)
        pos = body.find(phrase, pos + 1)
    if not hits:
        raise BuildError("phrase not found in body")
    if occurrence is None:
        if len(hits) > 1:
            raise BuildError(f"ambiguous: {len(hits)} hits; set nugget_occurrence")
        occurrence = 1
    if not 1 <= occurrence <= len(hits):
        raise BuildError(f"occurrence {occurrence} out of range ({len(hits)} hits)")
    start = hits[occurrence - 1]
    return start, start + len(phrase)


def split_paths(bench_dir, split):
    bench_dir = Path(bench_dir)
    items_dir = bench_dir / "items" if split == "dev" else bench_dir / "_local" / "items"
    name = split.upper()
    return {"items": items_dir / f"{name}.jsonl", "status": items_dir / f"{name}.status.csv",
            "nuggets": bench_dir / "_local" / "nuggets" / f"{split}.jsonl"}


def read_draft(path):
    text = Path(path).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return list(csv.DictReader(io.StringIO(text)))


def _flag(value, where, errors):
    value = (value or "").strip().lower()
    if value in TRUE:
        return True
    if value not in FALSE:
        errors.append(f"{where}: quotes_gazette must be true/false")
    return False


def _none(value):
    return value if value else None


def build(draft_rows, slot_rows, spec, root, created):
    """Return (split, items, nugget_lines, status_rows, errors, missing)."""
    errors, missing = [], []
    by_key = {(r["slot_id"], r["side"]): r for r in slot_rows}
    split_of = {r["slot_id"]: r["split"] for r in slot_rows}
    splits = {split_of.get(r.get("slot_id", "")) for r in draft_rows}
    if None in splits:
        bad = sorted({r.get("slot_id", "") for r in draft_rows if r.get("slot_id", "") not in split_of})
        return None, [], [], [], [f"unknown slot ids: {bad}"], []
    if len(splits) != 1:
        return None, [], [], [], [f"draft mixes splits {sorted(splits)}"], []
    split = splits.pop()
    unusable, rows = {}, {}
    for row in draft_rows:
        key = (row["slot_id"], row.get("side", ""))
        if key not in by_key:
            errors.append(f"{key[0]}/{key[1]}: no such slot side")
            continue
        if key in rows:
            errors.append(f"{key[0]}/{key[1]}: duplicate draft row")
        rows[key] = row
        status = (row.get("status") or "").strip().lower()
        if status == "unusable":
            reason = (row.get("unusable_reason") or "").strip()
            if not reason:
                errors.append(f"{key[0]}: unusable needs unusable_reason")
            unusable[key[0]] = reason
        elif status not in ("", "ok"):
            errors.append(f"{key[0]}/{key[1]}: status must be blank, ok or unusable")
    active, pulled, act_errors = active_slots(slot_rows, split, unusable, spec.get("max_test_items_per_unit"))
    errors.extend(act_errors)
    active_set = set(active)
    for (sid, side), row in rows.items():
        if sid not in active_set and sid not in unusable and (row.get("question") or "").strip():
            errors.append(f"{sid}/{side}: slot is not active (unpulled reserve)")
    recs = record_paths(root)
    records = [rec for rec, _ in recs.values()]
    known = parse_date(spec["as_known_on"])
    bodies, items, nugget_lines = {}, [], []
    for sid in active:
        for slot in [r for r in slot_rows if r["slot_id"] == sid]:
            item_id = f"{sid}-{slot['side']}"
            row = rows.get((sid, slot["side"]))
            if row is None or not (row.get("question") or "").strip():
                missing.append(item_id)
                continue
            dated = slot["stratum"] != UNDATED
            if dated:
                kwargs = {"as_of": parse_date(slot["as_of"])} if slot["as_of"] else {"tax_year": slot["tax_year"]}
                res = lookup(records, act=slot["act"], unit=slot["unit"], as_known_on=known, **kwargs)
                expect = (slot["gold_status"], _none(slot["gold_record_id"]), slot["gold_reasons"])
                if (res.status, res.record_id, ";".join(res.reasons)) != expect:
                    errors.append(f"{item_id}: lookup gold differs from slot")
                    continue
            nuggets = []
            for n in NUGGETS:
                phrase = row.get(f"nugget_phrase_{n}") or ""
                where = f"{item_id} nugget {n}"
                if not phrase:
                    continue
                rid = _none(slot["gold_record_id"])
                if rid is None:
                    errors.append(f"{where}: item has no gold_record_id")
                    continue
                match = (row.get(f"nugget_match_{n}") or "exact").strip().lower()
                if match not in MATCHES:
                    errors.append(f"{where}: match must be one of {MATCHES}")
                    continue
                occ_raw = (row.get(f"nugget_occurrence_{n}") or "").strip()
                if occ_raw and not occ_raw.isdigit():
                    errors.append(f"{where}: occurrence must be a positive integer")
                    continue
                if rid not in bodies:
                    rec, path = recs[rid]
                    bodies[rid] = read_body(root, rec, path)
                body = bodies[rid]
                if body is None:
                    errors.append(f"{where}: body absent for {rid}")
                    continue
                try:
                    start, end = find_span(body, phrase, int(occ_raw) if occ_raw else None)
                except BuildError as exc:
                    errors.append(f"{where}: {exc}")
                    continue
                nuggets.append({"record_id": rid, "start": start, "end": end,
                                "sha16": body_sha256(body[start:end])[:16], "match": match,
                                "quotes_gazette": _flag(row.get(f"quotes_gazette_{n}"), where, errors)})
                nugget_lines.append({"item_id": item_id, "n": n, "record_id": rid, "start": start, "end": end,
                                     "phrase": phrase})
            author = (row.get("author") or "owner").strip()
            if author not in AUTHORS:
                errors.append(f"{item_id}: author must be one of {AUTHORS}")
            items.append({
                "item_id": item_id, "split": split, "pair_id": _none(slot["pair_id"]), "slot_id": sid,
                "stratum": slot["stratum"], "question": row["question"].strip(), "act": slot["act"],
                "unit": slot["unit"], "as_of": _none(slot["as_of"]), "tax_year": _none(slot["tax_year"]),
                "as_known_on": spec["as_known_on"], "dated": dated,
                "gold_status": _none(slot["gold_status"]), "gold_record_id": _none(slot["gold_record_id"]),
                "gold_reasons": [r for r in slot["gold_reasons"].split(";") if r],
                "should_abstain": slot["should_abstain"] == "true",
                "abstain_category": _none(slot["abstain_category"]), "abstain_source": "code",
                "act_post_cutoff": slot["act_post_cutoff"] == "true", "nuggets": nuggets,
                "author": author, "created": created, "notes": (row.get("notes") or "").strip()})
    status_rows = []
    for row in slot_rows:
        sid = row["slot_id"]
        if row["split"] != split or row["side"] not in ("a", "single"):
            continue
        if sid in unusable:
            status_rows.append({"slot_id": sid, "status": "unusable", "pulled_into": pulled.get(sid, ""),
                                "reason": unusable[sid]})
        elif sid in active_set:
            status_rows.append({"slot_id": sid, "status": "active", "pulled_into": "", "reason": ""})
        else:
            status_rows.append({"slot_id": sid, "status": "reserve_unused", "pulled_into": "", "reason": ""})
    return split, sorted(items, key=lambda i: i["item_id"]), nugget_lines, status_rows, errors, missing


def jsonl_bytes(rows):
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")


def status_bytes(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, STATUS_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def needed_bodies_absent(draft_rows, slot_rows, root):
    """Record ids referenced by draft nuggets whose local body file is missing."""
    by_key = {(r["slot_id"], r["side"]): r for r in slot_rows}
    recs = record_paths(root)
    absent = set()
    for row in draft_rows:
        slot = by_key.get((row.get("slot_id"), row.get("side")))
        if slot is None or not slot["gold_record_id"]:
            continue
        if any(row.get(f"nugget_phrase_{n}") for n in NUGGETS):
            rid = slot["gold_record_id"]
            rec, path = recs[rid]
            if not body_path(Path(root), rec, path).is_file():
                absent.add(rid)
    return sorted(absent)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--created", required=True, help="YYYY-MM-DD written to every item")
    parser.add_argument("--slots", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--bench-dir", type=Path, default=BENCH_DIR)
    parser.add_argument("--force", action="store_true", help="replace existing outputs of this split")
    args = parser.parse_args(argv)
    if parse_date(args.created) is None:
        parser.error("--created must be YYYY-MM-DD")
    spec = load_spec(args.spec)
    slot_rows = read_slots(args.slots)
    draft = read_draft(args.draft)
    absent = needed_bodies_absent(draft, slot_rows, args.root)
    if absent:
        print(f"bench build: REFUSED local bodies absent for {len(absent)} record(s): {', '.join(absent)}")
        return 2
    split, items, nuggets, status_rows, errors, missing = build(draft, slot_rows, spec, args.root, args.created)
    if errors:
        for line in errors:
            print(f"bench build: ERROR {line}")
        print(f"bench build: {len(errors)} error(s); nothing written")
        return 1
    paths = split_paths(args.bench_dir, split)
    if not args.force and any(p.exists() for p in paths.values()):
        print(f"bench build: ERROR outputs for {split} exist; rerun with --force to replace them")
        return 2
    for key, payload in (("items", jsonl_bytes(items)), ("status", status_bytes(status_rows)),
                         ("nuggets", jsonl_bytes(nuggets))):
        paths[key].parent.mkdir(parents=True, exist_ok=True)
        paths[key].write_bytes(payload)
    print(f"bench build: {split} items {len(items)}, nuggets {len(nuggets)}, missing {len(missing)}"
          + (f" ({', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''})" if missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
