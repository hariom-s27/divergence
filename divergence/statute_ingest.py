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
from divergence.statute_records import _provenance, project
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
                    + "); ITD 2025 reproduction used for source fields; heading_not_gazette_checked")


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


def assemble(vd, effects, sources, mapping, knowledge, fetch_log, extract, body_hashes):
    records = project(vd, effects, sources, mapping, knowledge, fetch_log)
    rows = {row["record_key"]: row for row in vd}
    registry = {r["key"]: r for r in sources.get("items", []) + sources.get("manual", [])}
    fetch = {r["key"]: r for r in fetch_log["entries"]}
    bodies = {}
    for rec in records:
        edition = edition_for(rows[rec["record_id"]], rec)
        if rec["status"] == "never_operative":
            original_source(rec, registry, knowledge, fetch)
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
    records, bodies = assemble(vd, effects, read_json(root / "SOURCES.json"), ap.read_csv(root / "MAPPING.csv"),
                               result["know"], read_json(root / FETCH_REL), extraction_reader(raw), result["body_sha"])
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
    print(f"statute_records --build: {len(records)} records; {len(bodies)} local bodies; "
          f"{len(records) - len(bodies)} unprinted; {created} files created")
    return records, bodies, evidence
