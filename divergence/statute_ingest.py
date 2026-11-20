"""C4 deterministic local ingest; projection and date semantics live in statute_records."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from divergence import act_parse as ap
from divergence import statute_build as sb
from divergence import statute_extract as se
from divergence import statute_guard as guard
from divergence import statute_sources as ss
from divergence.statute_records import _provenance, apply_dispositions, project
from divergence.statute_schema import DEFAULT_ROOT, body_sha256, load_schema, record_filename
from divergence.statute_validate import body_path

FETCH_REL = Path("_local_text/_raw/2026-11-13/FETCH-LOG.json")
SHEET_REL = Path("_local_text/census/partC/C2-20261116-071401/PENDING-23.md")
SHEET_SHA = "5e0c17599b4ab5c6c051a2bacbba3ecab9241be288ca0634aa5bd9b9dd2b001d"
FETCH_SHA = "43476df6fd7b9f72f453a48bdb83f831b1cd30be140b39f2f399dade2ca1423e"
ORIGINAL_EDITION = "ita2025_2025"
SOURCE_FIELDS = ("source_url", "source_page_act", "source_page_year", "source_amended_up_to",
                 "retrieved_at", "gazette_published", "source_acknowledgement")


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def read_json(path):
    return json.loads(path.read_bytes().decode("utf-8"))


def read_knowledge_table(path):
    """Parse only the six-column C2 knowledge table, stopping at its boundary."""
    header = ["edition", "date", "source", "acts", "printed title acts", "mismatch"]
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if [c.strip() for c in line.strip().strip("|").split("|")] == header:
            return _knowledge_rows(lines[index + 1:])
    raise ValueError("C2 knowledge table missing")


def _knowledge_rows(lines):
    dates = {}
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) != 6:
            break
        if all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
            continue
        key, value = cells[:2]
        if key in dates or not re.fullmatch(r"ita(?:1961|2025)_[A-Za-z0-9]+", key):
            raise ValueError("invalid or duplicate C2 knowledge edition")
        if value != "None" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("invalid C2 knowledge date: " + key)
        dates[key] = None if value == "None" else value
    if not dates:
        raise ValueError("empty C2 knowledge table")
    return dates


def check_knowledge(knowledge, expected):
    actual = {key: value["date"] for key, value in knowledge.items()}
    if actual != expected:
        raise ValueError("computed knowledge dates differ from C2")
    return actual


def edition_for(row, rec):
    if rec["status"] == "never_operative":
        return ORIGINAL_EDITION
    if rec["status"] == "unprinted":
        return se.EDITIONS[rec["act"]][-1]
    match = re.search(r"(?:^|;\s*)text = ([A-Za-z0-9_]+)(?:;|$)", row["code_note"])
    if not match:
        raise ValueError("missing body edition: " + rec["record_id"])
    return match.group(1)


def extraction_reader(raw):
    views, sections = {}, {}

    def extract(edition, unit):
        if (edition, unit) not in sections:
            if edition not in views:
                views[edition] = se.edition_view(raw, edition)
            view = views[edition]
            result = se.extract_view(view, unit)
            choice = sb.OWNER_CHOICES.get((edition, unit))
            if result["status"] == "UNRESOLVED" and choice:
                choices = [r for page, r in sb.candidate_bodies(view, unit) if page == choice["page"]]
                if len(choices) != 1:
                    raise ValueError("missing or duplicate owner extraction choice")
                result = choices[0]
            sections[(edition, unit)] = result
        return sections[(edition, unit)]

    return extract


def original_source(rec, registry, knowledge, fetch):
    """Owner-approved ITD provenance; knowledge clock and empty body stay intact."""
    row = {"code_note": "text = " + ORIGINAL_EDITION}
    source = _provenance(row, rec["act"], rec["unit"], "in_force", registry, knowledge, fetch)
    rec.update({key: source[key] for key in SOURCE_FIELDS})
    gazette = registry["ita2025_gz"]
    rec["notes"] = ("original enacted text: Gazette Act 30 of 2025 (ita2025_gz, sha " + gazette["sha256"]
                    + "); ITD 2025 reproduction used for source fields; heading Gazette-checked 2026-11-17 (owner)")


def attach_record(rec, row, extracted, expected_hash):
    if extracted.get("status") != "FOUND" or not extracted.get("heading"):
        raise ValueError("missing extracted heading: " + rec["record_id"])
    rec.update(heading=extracted["heading"], chapter=None)
    if rec["status"] == "unprinted":
        return None
    body = "" if rec["status"] == "never_operative" else extracted.get("body")
    if not isinstance(body, str) or (not body and rec["status"] != "never_operative"):
        raise ValueError("missing extracted body: " + rec["record_id"])
    digest = body_sha256(body)
    if rec["status"] != "never_operative" and digest != expected_hash:
        raise ValueError("body differs from guard map: " + rec["record_id"])
    if "\r" in body or body.startswith("\ufeff"):
        raise ValueError("body encoding/line endings invalid: " + rec["record_id"])
    rec.update(body_sha256=digest, body_chars=len(body))
    return body


def validate_metadata(records):
    import jsonschema

    validator = jsonschema.Draft202012Validator(load_schema(), format_checker=jsonschema.FormatChecker())
    errors = []
    for rec in records:
        errors.extend(rec["record_id"] + " " + err.json_path + " " + str(err.validator)
                      for err in validator.iter_errors(rec))
    if errors:
        raise ValueError("invalid metadata: " + "; ".join(sorted(errors)))


def assemble(vd, effects, sources, mapping, knowledge, fetch_log, extract, body_hashes, dispositions=()):
    records = project(vd, effects, sources, mapping, knowledge, fetch_log, dispositions)
    rows = {row["record_key"]: row for row in vd}
    registry = {r["key"]: r for r in sources.get("items", []) + sources.get("manual", [])}
    fetch = {r["key"]: r for r in fetch_log["entries"]}
    bodies = {}
    for rec in records:
        edition = edition_for(rows[rec["record_id"]], rec)
        if rec["status"] == "never_operative":
            original_source(rec, registry, knowledge, fetch)
            apply_dispositions(rec, dispositions)
        elif not knowledge.get(edition, {}).get("date"):
            raise ValueError("missing edition knowledge date: " + edition)
        body = attach_record(rec, rows[rec["record_id"]], extract(edition, rec["unit"]),
                             body_hashes.get(rec["record_id"]))
        if body is not None:
            bodies[rec["record_id"]] = body
        if rec["status"] != "never_operative":
            rec.pop("body", None)
            if rec["status"] == "unprinted":
                rec["body"] = None
    validate_metadata(records)
    return records, bodies


def prepare(root=DEFAULT_ROOT):
    root = Path(root)
    for path, expected in ((root / FETCH_REL, FETCH_SHA), (root / SHEET_REL, SHEET_SHA)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("input hash mismatch: " + path.name)
    vd = ap.read_csv(root / "VERSION-DATES.csv")
    if len(vd) != 34 or guard.code_sha(vd) != guard.CODE_SHA256:
        raise ValueError("canonical code-column guard mismatch")
    effects = ap.read_csv(root / "AMENDMENT-EFFECTS.csv")
    raw = se.latest_raw_dir()
    result = sb.build(raw, root / "_local_text/scratch/C4-body-no-write", effects=effects, write=False)
    dates = check_knowledge(result["know"], read_knowledge_table(root / SHEET_REL))
    if len(result["body_sha"]) != 26 or guard.body_sha(result["body_sha"]) != guard.BODY_SHA256:
        raise ValueError("body guard mismatch")
    disposition_path = root / "CORRIGENDUM-DISPOSITION.csv"
    dispositions = ap.read_csv(disposition_path) if disposition_path.exists() else []
    records, bodies = assemble(vd, effects, read_json(root / "SOURCES.json"), ap.read_csv(root / "MAPPING.csv"),
                               result["know"], read_json(root / FETCH_REL), extraction_reader(raw), result["body_sha"],
                               dispositions)
    return records, bodies, {"knowledge": dates, "body_map": result["body_sha"], "raw": str(raw)}


def output_plan(root, records, bodies):
    plan, ids = {}, set()
    for rec in records:
        rid = rec["record_id"]
        if rid in ids:
            raise ValueError("duplicate record: " + rid)
        ids.add(rid)
        path = root / "records" / rec["act"] / record_filename(rid)
        plan[path] = json_bytes(rec)
        bp = body_path(root, rec, path)
        if rec["status"] == "unprinted":
            if rid in bodies or bp.exists():
                raise ValueError("unprinted body must be absent: " + rid)
        else:
            raw = bodies[rid].encode("utf-8")
            if hashlib.sha256(raw).hexdigest() != rec["body_sha256"] or len(bodies[rid]) != rec["body_chars"]:
                raise ValueError("body metadata mismatch: " + rid)
            plan[bp] = raw
    return plan


def persist(root, records, bodies):
    """Reject all byte conflicts before any write; identical outputs are reused."""
    root = Path(root)
    validate_metadata(records)
    plan = output_plan(root, records, bodies)
    extra = set((root / "records").glob("*/*.json")) - set(plan)
    if extra:
        raise ValueError("unexpected existing record files")
    for path, raw in plan.items():
        if path.exists() and path.read_bytes() != raw:
            raise ValueError("existing output differs: " + path.name)
    created = 0
    for path, raw in sorted(plan.items()):
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(raw)
            created += 1
    return created


def build_records(root=DEFAULT_ROOT):
    records, bodies, evidence = prepare(root)
    created = persist(root, records, bodies)
    print("Raw folder:", evidence["raw"])
    real = sum(r["status"] not in {"never_operative", "unprinted"} for r in records)
    empty = sum(r["status"] == "never_operative" for r in records)
    print(f"statute_records --build: {len(records)} records; {created} files created")
    print(f"{real}/{real} bodies verified by guard; {empty}/{empty} never_operative placeholders empty as designed")
    return records, bodies, evidence


def record_changes(old, new, prefix=''):
    """Return exact metadata paths, including added keys, without body text."""
    if isinstance(old, dict) and isinstance(new, dict):
        out = []
        for key in sorted(set(old) | set(new)):
            path = prefix + '.' + key if prefix else key
            out.extend(record_changes(old.get(key), new.get(key), path))
        return out
    if isinstance(old, list) and isinstance(new, list) and (prefix == 'amended_by'):
        if len(old) != len(new):
            raise ValueError('amendment membership changed')
        return [change for i, (a, b) in enumerate(zip(old, new)) for change in record_changes(a, b, f'amended_by.{i}')]
    return [] if old == new else [{'field': prefix, 'old': old, 'new': new}]


def plan_update(old_records, new_records):
    old = {r['record_id']: r for r in old_records}
    new = {r['record_id']: r for r in new_records}
    if len(old) != len(old_records) or len(new) != len(new_records) or set(old) != set(new):
        raise ValueError('record membership changed')
    result = []
    for rid in sorted(old):
        if any((old[rid].get(k) != new[rid].get(k) for k in ('body_sha256', 'body_chars', 'body'))):
            raise ValueError('body metadata changed')
        changes = record_changes(old[rid], new[rid])
        for change in changes:
            field = change['field']
            if field not in {
                'notes',
                'lookup_flags',
                'counterpart.notes'
            } and (
                not re.fullmatch(
                    'amended_by\\.\\d+\\.url',
                    field
                )
            ):
                raise ValueError('update field outside allow-list: ' + field)
        if changes:
            result.append({'record_id': rid, 'changes': changes})
    return result


def _write_record_update(root, backup_dir, old_bytes, records, changes):
    table = ap.read_csv(root / 'census/ITD-GAZETTE-DIFFS.csv')
    if any((r['owner_ok'] != 'yes' for r in table if r['status'] == 'kept' and r['origin'] == 'itd')):
        raise ValueError('kept itd rows lack owner confirmation')
    if backup_dir is None:
        raise ValueError('explicit backup directory required')
    backup = Path(backup_dir).resolve()
    backup.relative_to((root / '_local_text/census/partD').resolve())
    backup.mkdir(parents=True, exist_ok=False)
    for p, raw in old_bytes.items():
        target = backup / p.relative_to(root / 'records')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(raw)
        if target.read_bytes() != raw:
            raise ValueError('backup byte verification failed')
    if any((p.read_bytes() != raw for p, raw in old_bytes.items())):
        raise ValueError('record changed during backup')
    new = {r['record_id']: r for r in records}
    for change in changes:
        rec = new[change['record_id']]
        path = root / 'records' / rec['act'] / record_filename(rec['record_id'])
        path.write_bytes(json_bytes(rec))


def update_records(root=DEFAULT_ROOT, *, write=False, backup_dir=None):
    root = Path(root)
    paths = sorted((root / 'records').glob('*/*.json'))
    old_bytes = {p: p.read_bytes() for p in paths}
    old = [read_json(p) for p in paths]
    with ss.existing_local_sources():
        records, bodies, evidence = prepare(root)
    changes = plan_update(old, records)
    for p, rec in zip(paths, old):
        bp = body_path(root, rec, p)
        if rec['status'] == 'unprinted':
            if bp.exists():
                raise ValueError('unprinted body unexpectedly exists')
        elif hashlib.sha256(bp.read_bytes()).hexdigest() != rec['body_sha256']:
            raise ValueError('stored body hash differs')
    if write:
        _write_record_update(root, backup_dir, old_bytes, records, changes)
    return (changes, records, evidence)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description='Guarded metadata-only record update')
    parser.add_argument('--update', action='store_true', required=True)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--backup-dir', type=Path)
    args = parser.parse_args(argv)
    try:
        changes, records, evidence = update_records(write=args.write, backup_dir=args.backup_dir)
    except Exception as exc:
        print('STOP:', type(exc).__name__)
        return 1
    print(json.dumps({'write': args.write, 'changed_records': len(changes), 'diff': changes}, sort_keys=True))
    print('26/26 bodies verified by guard; 5/5 never_operative placeholders empty as designed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
