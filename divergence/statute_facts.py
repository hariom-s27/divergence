"""Deterministic facts from committed statute metadata; never read local bodies or run a sweep."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from divergence.statute_schema import CORPUS_CHECKED_THROUGH, DEFAULT_ROOT


def _label(value):
    return re.sub(r"[^a-z0-9_]+", "_", str(value).lower()).strip("_") or "unspecified"


def _rows(root, relative):
    with (root / relative).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def collect_facts(root):
    """Read the explicit metadata allowlist, without following record body paths."""
    root = Path(root)
    records = [json.loads(path.read_bytes().decode("utf-8"))
               for path in sorted((root / "records").rglob("*.json"))]
    facts = []
    record_source = "records/**/*.json"

    def add(key, value, definition, source):
        facts.append({"key": key, "value": value, "definition": definition, "source": source})

    def counts(prefix, values, definition, source):
        for value, count in sorted(Counter(values).items()):
            labels = value if isinstance(value, tuple) else (value,)
            key = ".".join(_label(label) for label in labels)
            add(f"{prefix}.{key}", count, f"{definition}: {' / '.join(labels)}.", source)

    add("records.total", len(records), "Number of record JSON files.", record_source)
    counts("records.act", (r["act"] for r in records), "Records by Act", record_source)
    counts("records.status", (r["status"] for r in records), "Records by status", record_source)
    add("bodies.nonempty", sum((r.get("body_chars") or 0) > 0 for r in records),
        "Records with body_chars > 0; no body files are read.", record_source)
    add("bodies.empty_placeholders", sum(r.get("body_chars") == 0 for r in records),
        "Records with body_chars == 0; null body_chars are excluded.", record_source)
    add("records.repeal_day_unsettled", sum("repeal_day_unsettled" in r.get("lookup_flags", []) for r in records),
        "Records whose lookup_flags include repeal_day_unsettled.", record_source)
    amendments = [item for record in records for item in record.get("amended_by", [])]
    add("amended_by.items", len(amendments), "Total amended_by array items across records.", record_source)
    add("amended_by.empty_url", sum(not (item.get("url") or "").strip() for item in amendments),
        "amended_by items with missing, null, empty or whitespace-only url; checks amended_by[*].url only.",
        record_source)

    corrigenda = "CORRIGENDUM-DISPOSITION.csv"
    counts("corrigenda.class", (r["class"] for r in _rows(root, corrigenda)), "Corrigenda by class", corrigenda)
    diffs = "census/ITD-GAZETTE-DIFFS.csv"
    diff_rows = _rows(root, diffs)
    add("diffs.total", len(diff_rows), "Number of ITD/Gazette diff rows.", diffs)
    counts("diffs", ((r["status"], r["origin"], r["nature"]) for r in diff_rows),
           "Diff rows by status / origin / nature", diffs)
    caveats = "census/BODY-CAVEATS.csv"
    caveat_rows = _rows(root, caveats)
    add("caveats.total", len(caveat_rows), "Number of body caveat metadata rows.", caveats)
    counts("caveats", ((r["source"], r["nature"]) for r in caveat_rows),
           "Caveat rows by source / nature", caveats)
    gaps = "census/LABEL-GAPS.csv"
    add("label_gaps.rows", len(_rows(root, gaps)), "Number of label-gap rows.", gaps)

    sweep_name = "census/sweep.json"
    sweep_path = root / sweep_name
    sweep_raw = sweep_path.read_bytes() if sweep_path.is_file() else None
    add("sweep.sha256", hashlib.sha256(sweep_raw).hexdigest() if sweep_raw is not None else None,
        "SHA-256 of committed sweep.json bytes; null when absent.", sweep_name)
    result = json.loads(sweep_raw.decode("utf-8")) if sweep_raw is not None else None
    add("sweep.queries.total", sum(result["queries"].values()) if result is not None else None,
        "Sum of sweep query counts across kinds; null when sweep.json is absent.", sweep_name)
    if result is not None:
        for category in ("queries", "statuses", "reasons", "classes"):
            for label, value in sorted(result[category].items()):
                add(f"sweep.{category}.{_label(label)}", value,
                    f"Sweep {category} count for {label}; read from sweep.json without recomputation.", sweep_name)
    add("corpus_checked_through", CORPUS_CHECKED_THROUGH.isoformat(),
        "Inclusive corpus knowledge horizon from CORPUS_CHECKED_THROUGH.",
        "divergence/statute_schema.py:CORPUS_CHECKED_THROUGH")

    manifest_name = "STATUTE-HASHES.json"
    manifest_path = root / manifest_name
    manifest_raw = manifest_path.read_bytes() if manifest_path.is_file() else None
    manifest = json.loads(manifest_raw.decode("utf-8")) if manifest_raw is not None else None
    add("manifest.present", manifest_raw is not None, "Whether STATUTE-HASHES.json exists.", manifest_name)
    add("manifest.sha256", hashlib.sha256(manifest_raw).hexdigest() if manifest_raw is not None else None,
        "SHA-256 of manifest bytes; null when absent.", manifest_name)
    add("manifest.file_count", manifest["file_count"] if manifest is not None else None,
        "Manifest-declared file_count; null when the manifest is absent.", manifest_name)
    return {"facts_version": 1, "facts": sorted(facts, key=lambda fact: fact["key"])}


def facts_bytes(document):
    return (json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def first_differing_key(old, new):
    try:
        old_doc, new_doc = (json.loads(raw.decode("utf-8")) for raw in (old, new))
        if old_doc.get("facts_version") != new_doc["facts_version"]:
            return "facts_version"
        old_facts = {fact["key"]: fact for fact in old_doc["facts"]}
        new_facts = {fact["key"]: fact for fact in new_doc["facts"]}
        for key in sorted(set(old_facts) | set(new_facts)):
            if old_facts.get(key) != new_facts.get(key):
                return key
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return "<document>"
    return "<serialization>"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--print", action="store_true", dest="print_facts")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    if not (args.print_facts or args.out is not None or args.check is not None):
        parser.error("choose --print, --out or --check")
    data = facts_bytes(collect_facts(args.root))
    if args.print_facts:
        print(data.decode("utf-8"), end="")
    if args.check is not None:
        actual = args.check.read_bytes() if args.check.is_file() else None
        if actual != data:
            key = first_differing_key(actual, data) if actual is not None else "<missing>"
            print(f"statute facts: MISMATCH first differing key {key}")
            return 1
        print("statute facts: OK")
    if args.out is not None:
        args.out.write_bytes(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
