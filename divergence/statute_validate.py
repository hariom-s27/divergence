"""D78 statute validator.

    python -m divergence.statute_validate [--root PATH] [--allow-fixtures] [--freeze | --verify]

Exit 0 = OK (warnings allowed), 1 = errors, 2 = usage. One line per finding:
    ERROR|WARN <file>: <check-id> <message>
then a count line. Checks V01-V16 are described in DECISION-D78.md and P08 D6.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

from divergence.statute_schema import (
    ACT2025_COMMENCEMENT,
    ACT2025_FIRST_TAX_YEAR,
    COUNTERPART_SOURCES,
    CORPUS_CHECKED_THROUGH,
    DEFAULT_ROOT,
    LAST_1961_TAX_YEAR,
    MODIFIER_KINDS,
    REPEAL_DAY,
    build_record_id,
    parse_date,
    record_filename,
    schema_errors,
    tax_year_start,
)

MANIFEST_NAME = "STATUTE-HASHES.json"
MANIFEST_VERSION = 1
MANIFEST_FIXED = (
    "VERSION-DATES.csv", "AMENDMENT-EFFECTS.csv", "SOURCES.json", "MAPPING.csv", "SECTION-LIST.json",
    "CORRIGENDUM-DISPOSITION.csv", "census/sweep.json", "census/ITD-GAZETTE-DIFFS.csv",
    "census/LABEL-GAPS.csv", "census/BODY-CAVEATS.csv",
)
MANIFEST_GLOBS = (("records", "*.json"), ("text", "*.txt"), ("schema", "*.json"), ("owner", "*.csv"))
MANIFEST_EXCLUDED = (
    "README.md", "STATUTE-HASHES.json", "census/C4_TIMELINE.md", "census/D80_TIMELINE.md",
    "census/d80_facts.json", "records/.gitkeep", "text/.gitkeep",
)
BOM = b"\xef\xbb\xbf"
ROOT_LABEL = "(root)"

Finding = namedtuple("Finding", "level file check message")
Ctx = namedtuple("Ctx", "root path rel by_id allow_fixtures")


# ---------- small helpers (bad values return None; V01/V05 report them) ----------

def _date(rec: dict, key: str):
    try:
        return parse_date(rec.get(key))
    except ValueError:
        return None


def _ty(value):
    try:
        return tax_year_start(value) if value is not None else None
    except ValueError:
        return None


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _byte_problems(raw: bytes) -> list:
    out = []
    if raw.startswith(BOM):
        out.append("has a UTF-8 BOM")
    if b"\r" in raw:
        out.append("contains CR (must be LF only)")
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as e:
        out.append(f"is not valid UTF-8 ({e.reason} at byte {e.start})")
    return out


# ---------- per-record checks: each returns [(level, message), ...] ----------

def check_v01_schema(rec, ctx):
    return [("ERROR", msg) for msg in schema_errors(rec)]


def check_v02_record_id(rec, ctx):
    try:
        built = build_record_id(rec.get("source_kind"), rec.get("act"), rec.get("unit"), rec.get("version_id"))
    except ValueError as e:
        return [("ERROR", f"cannot build record_id from fields: {e}")]
    if rec.get("record_id") != built:
        return [("ERROR", f"record_id {rec.get('record_id')!r} != built {built!r}")]
    return []


def check_v03_filename(rec, ctx):
    out = []
    rid = rec.get("record_id")
    if isinstance(rid, str) and ctx.path.name != record_filename(rid):
        out.append(("ERROR", f"file name {ctx.path.name!r} != {record_filename(rid)!r}"))
    expected_dir = ctx.root / "records" / str(rec.get("act"))
    if ctx.path.parent != expected_dir:
        out.append(("ERROR", f"file must sit directly under records/{rec.get('act')}/"))
    return out


def check_v05_dates(rec, ctx):
    out = []
    f, t = _date(rec, "in_force_from"), _date(rec, "in_force_to")
    if f and t and f >= t:
        out.append(("ERROR", f"in_force_from {f} must be < in_force_to {t}"))
    starts = {}
    for key in ("applies_from_tax_year", "applies_to_tax_year"):
        v = rec.get(key)
        if v is None:
            continue
        try:
            starts[key] = tax_year_start(v)
        except ValueError as e:
            out.append(("ERROR", f"{key}: {e}"))
    if len(starts) == 2 and starts["applies_from_tax_year"] > starts["applies_to_tax_year"]:
        out.append(("ERROR", "applies_from_tax_year > applies_to_tax_year"))
    return out


def check_v06_act2025(rec, ctx):
    if rec.get("act") != "2025":
        return []
    out = []
    af = _ty(rec.get("applies_from_tax_year"))
    if af is not None and af < tax_year_start(ACT2025_FIRST_TAX_YEAR):
        out.append(("ERROR", f"2025 Act record applies from {rec.get('applies_from_tax_year')} (< {ACT2025_FIRST_TAX_YEAR})"))
    f = _date(rec, "in_force_from")
    if f is not None and f < ACT2025_COMMENCEMENT:
        out.append(("WARN", f"in_force_from {f} is before {ACT2025_COMMENCEMENT} (s.1(3) 'save as otherwise provided')"))
    return out


def check_v07_status(rec, ctx):
    s = rec.get("status")
    f, t = _date(rec, "in_force_from"), _date(rec, "in_force_to")
    out = []
    if s == "in_force":
        if f is None:
            out.append("in_force needs in_force_from")
    elif s == "repealed_saved":
        if rec.get("act") != "1961":
            out.append("repealed_saved needs act 1961")
        if t is None or t > REPEAL_DAY:
            out.append(f"repealed_saved needs in_force_to <= {REPEAL_DAY}")
        at = _ty(rec.get("applies_to_tax_year"))
        if at is None or at > tax_year_start(LAST_1961_TAX_YEAR):
            out.append(f"repealed_saved needs applies_to_tax_year <= {LAST_1961_TAX_YEAR}")
    elif s == "never_operative":
        for key in ("in_force_from", "in_force_to", "applies_from_tax_year", "applies_to_tax_year"):
            if rec.get(key) is not None:
                out.append(f"never_operative needs {key} null")
    elif s == "prospective":
        cur = _date(rec, "text_current_as_of")
        if f is not None and (cur is None or f <= cur):
            out.append("prospective needs in_force_from null or after text_current_as_of")
    elif s == "omitted":
        if t is None:
            out.append("omitted needs in_force_to")
    elif s == "unprinted":
        if f is None:
            out.append("unprinted needs a dated in_force_from (in_force_to may be open)")
        for key in ("body", "body_sha256", "body_chars"):
            if rec.get(key) is not None:
                out.append(f"unprinted needs {key} null")
    return [("ERROR", m) for m in out]


def check_v08_retrospective(rec, ctx):
    r = _date(rec, "retrospective_from")
    if r is None:
        return []
    out = []
    e = _date(rec, "enacted_on")
    if e is None:
        out.append("retrospective_from set but enacted_on is null")
    elif not r < e:
        out.append(f"retrospective_from {r} must be before enacted_on {e}")
    if not rec.get("amended_by"):
        out.append("retrospective_from set but amended_by is empty")
    return [("ERROR", m) for m in out]


def check_v09_links(rec, ctx):
    out = []
    sup = rec.get("supersedes")
    if sup is not None:
        target = ctx.by_id.get(sup)
        if target is None:
            out.append(f"supersedes {sup!r} does not resolve")
        else:
            for key in ("source_kind", "act", "unit"):
                if target.get(key) != rec.get(key):
                    out.append(f"supersedes {sup!r}: {key} differs")
            v, tv = rec.get("version_id"), target.get("version_id")
            if not (isinstance(v, int) and isinstance(tv, int) and tv == v - 1):
                out.append(f"supersedes {sup!r}: version_id must be {v} - 1")
    for mid in rec.get("modified_by") or ():
        target = ctx.by_id.get(mid)
        if target is None:
            out.append(f"modified_by {mid!r} does not resolve")
        elif target.get("source_kind") not in MODIFIER_KINDS:
            out.append(f"modified_by {mid!r} is not a circular or notification")
    return [("ERROR", m) for m in out]


def body_path(root: Path, rec: dict, json_path: Path) -> Path:
    folder = "text" if rec.get("storage_mode") == "public_verbatim" else "_local_text"
    return root / folder / str(rec.get("act")) / (json_path.stem + ".txt")


def check_v10_body(rec, ctx):
    mode = rec.get("storage_mode")
    if mode not in ("public_verbatim", "local_only"):
        return []
    bp = body_path(ctx.root, rec, ctx.path)
    rel_body = bp.relative_to(ctx.root).as_posix()
    if rec.get("status") == "unprinted":
        if bp.exists():
            return [("ERROR", f"unprinted must have no body file: {rel_body}")]
        return []
    if not bp.is_file():
        if mode == "local_only":
            return [("WARN", f"body_absent_local {rel_body}")]
        return [("ERROR", f"body_missing {rel_body}")]
    raw = bp.read_bytes()
    out = [("ERROR", f"body {rel_body} {p}") for p in _byte_problems(raw)]
    if hashlib.sha256(raw).hexdigest() != rec.get("body_sha256"):
        out.append(("ERROR", f"body_sha256 mismatch for {rel_body}"))
    try:
        n = len(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return out
    if n != rec.get("body_chars"):
        out.append(("ERROR", f"body_chars {rec.get('body_chars')!r} != {n} for {rel_body}"))
    return out


def check_v12_acknowledgement(rec, ctx):
    if not _nonempty_str(rec.get("source_acknowledgement")):
        return [("ERROR", "source_acknowledgement is empty or missing")]
    return []


def check_v13_counterpart(rec, ctx):
    cp = rec.get("counterpart")
    if cp is None:
        return []
    if not isinstance(cp, dict) or cp.get("source") not in COUNTERPART_SOURCES:
        return [("ERROR", f"counterpart.source must be one of {COUNTERPART_SOURCES}")]
    return []


def check_v15_original_note(rec, ctx):
    if rec.get("source_kind") == "act" and rec.get("storage_mode") == "public_verbatim":
        if not _nonempty_str(rec.get("original_note")):
            return [("ERROR", "public_verbatim act record needs a non-empty original_note")]
    return []


def check_v16_fixture(rec, ctx):
    if rec.get("fixture") is True and not ctx.allow_fixtures:
        return [("ERROR", "fixture: true is not allowed here (test fixtures only, with --allow-fixtures)")]
    return []


RECORD_CHECKS = (
    check_v01_schema, check_v02_record_id, check_v03_filename, check_v05_dates,
    check_v06_act2025, check_v07_status, check_v08_retrospective, check_v09_links,
    check_v10_body, check_v12_acknowledgement, check_v13_counterpart,
    check_v15_original_note, check_v16_fixture,
)


def _check_id(fn) -> str:
    return fn.__name__.split("_")[1].upper()  # check_v01_schema -> V01


# ---------- file-level and cross-record checks ----------

def check_v11_json_bytes(rel: str, raw: bytes) -> list:
    return [Finding("ERROR", rel, "V11", f"file {p}") for p in _byte_problems(raw)]


def check_v04_unique(seen: dict) -> list:
    out = []
    for rid, rels in sorted(seen.items()):
        if len(rels) > 1:
            for rel in rels:
                out.append(Finding("ERROR", rel, "V04", f"record_id {rid!r} appears {len(rels)} times"))
    return out


def _git(root: Path, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def check_v14_git_untracked(root: Path, local_items: list) -> list:
    """local_items: [(rel_json, rel_body)]. local_only bodies must not be tracked by git."""
    if not local_items:
        return []
    try:
        r = _git(root, "rev-parse", "--is-inside-work-tree")
    except OSError as e:
        return [Finding("WARN", ROOT_LABEL, "V14", f"not_a_git_repo (git not available: {e}); skipped")]
    if r.returncode != 0 or r.stdout.strip() != "true":
        return [Finding("WARN", ROOT_LABEL, "V14", "not_a_git_repo; skipped")]
    out = []
    for rel_json, rel_body in local_items:
        if _git(root, "ls-files", "--error-unmatch", "--", rel_body).returncode == 0:
            out.append(Finding("ERROR", rel_json, "V14", f"local_only body {rel_body} is tracked by git"))
    return out


# ---------- driver ----------

def validate(root: Path, allow_fixtures: bool):
    """Return (findings, record_count)."""
    root = Path(root)
    rec_dir = root / "records"
    paths = sorted(rec_dir.rglob("*.json")) if rec_dir.is_dir() else []
    findings = []
    loaded = []
    seen: dict = {}
    for p in paths:
        rel = p.relative_to(root).as_posix()
        raw = p.read_bytes()
        findings += check_v11_json_bytes(rel, raw)
        text = raw[len(BOM):] if raw.startswith(BOM) else raw
        try:
            rec = json.loads(text.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            findings.append(Finding("ERROR", rel, "V01", f"not valid JSON: {e}"))
            continue
        if not isinstance(rec, dict):
            findings.append(Finding("ERROR", rel, "V01", "a record must be a JSON object"))
            continue
        loaded.append((p, rel, rec))
        rid = rec.get("record_id")
        if isinstance(rid, str):
            seen.setdefault(rid, []).append(rel)
    findings += check_v04_unique(seen)

    by_id = {}
    for _p, _rel, rec in loaded:
        by_id.setdefault(rec.get("record_id"), rec)

    local_items = []
    for p, rel, rec in loaded:
        ctx = Ctx(root, p, rel, by_id, allow_fixtures)
        for fn in RECORD_CHECKS:
            cid = _check_id(fn)
            try:
                results = fn(rec, ctx)
            except Exception as e:  # report, never skip silently
                results = [("ERROR", f"could not evaluate: {type(e).__name__}: {e}")]
            findings += [Finding(level, rel, cid, msg) for level, msg in results]
        if rec.get("storage_mode") == "local_only":
            local_items.append((rel, body_path(root, rec, p).relative_to(root).as_posix()))
    findings += check_v14_git_untracked(root, local_items)
    return findings, len(paths)


def manifest_paths(root: Path) -> list:
    """Sorted POSIX paths in the manifest scope, excluding local-only bodies."""
    root = Path(root)
    out = {rel for rel in MANIFEST_FIXED if (root / rel).is_file()}
    for sub, pattern in MANIFEST_GLOBS:
        d = root / sub
        if d.is_dir():
            paths = d.rglob(pattern) if sub in ("records", "text") else d.glob(pattern)
            out.update(p.relative_to(root).as_posix() for p in paths if p.is_file())
    return sorted(out)


def missing_scope_files(root: Path) -> list:
    root = Path(root)
    missing = [rel for rel in MANIFEST_FIXED if not (root / rel).is_file()]
    if not any(p.is_file() for p in (root / "records").rglob("*.json")):
        missing.append("records/*.json")
    return sorted(missing)


def scope_findings(root: Path, *, strict: bool) -> list:
    """Explicit strictness lets tests enforce default-root rules on temporary metadata."""
    return [Finding("ERROR", rel, "FREEZE", f"missing_scope_file {rel}")
            for rel in missing_scope_files(root)] if strict else []


def compute_manifest(root: Path) -> dict:
    root = Path(root)
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in manifest_paths(root)}


def freeze(root: Path, *, strict=None) -> Path:
    strict = Path(root).resolve() == DEFAULT_ROOT.resolve() if strict is None else strict
    missing = scope_findings(root, strict=strict)
    if missing:
        raise ValueError("; ".join(f.message for f in missing))
    hashes = compute_manifest(root)
    doc = {
        "manifest_version": MANIFEST_VERSION,
        "file_count": len(hashes),
        "corpus_checked_through": CORPUS_CHECKED_THROUGH.isoformat(),
        "hashes": hashes,
    }
    out = Path(root) / MANIFEST_NAME
    out.write_bytes((json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    return out


def verify(root: Path, *, strict=None) -> list:
    strict = Path(root).resolve() == DEFAULT_ROOT.resolve() if strict is None else strict
    out = scope_findings(root, strict=strict)
    mpath = Path(root) / MANIFEST_NAME
    if not mpath.is_file():
        return out + [Finding("ERROR", MANIFEST_NAME, "FREEZE", "no_manifest")]
    try:
        doc = json.loads(mpath.read_bytes().decode("utf-8"))
        if not isinstance(doc, dict):
            raise TypeError("manifest must be an object")
        if type(doc.get("manifest_version")) is not int or doc["manifest_version"] != MANIFEST_VERSION:
            out.append(Finding("ERROR", MANIFEST_NAME, "FREEZE", "manifest_version_mismatch"))
        stored = doc["hashes"]
        if not isinstance(stored, dict):
            raise TypeError("hashes must be an object")
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
        return out + [Finding("ERROR", MANIFEST_NAME, "FREEZE", f"unreadable manifest: {e}")]
    current = compute_manifest(root)
    for rel in sorted(set(stored) | set(current)):
        if rel not in current:
            out.append(Finding("ERROR", MANIFEST_NAME, "FREEZE", f"missing {rel}"))
        elif rel not in stored:
            out.append(Finding("ERROR", MANIFEST_NAME, "FREEZE", f"extra {rel}"))
        elif stored[rel] != current[rel]:
            out.append(Finding("ERROR", MANIFEST_NAME, "FREEZE", f"changed {rel}"))
    return out


def _print(findings: list, n_records: int) -> tuple:
    findings = sorted(findings, key=lambda f: (f.file, f.check, f.level, f.message))
    for f in findings:
        print(f"{f.level} {f.file}: {f.check} {f.message}")
    errors = sum(1 for f in findings if f.level == "ERROR")
    warns = sum(1 for f in findings if f.level == "WARN")
    print(f"statute_validate: {n_records} records, {errors} errors, {warns} warnings")
    return errors, warns


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m divergence.statute_validate",
                                     description="Validate D78 statute records.")
    parser.add_argument("--root", default=None, help="folder to validate (default: divergence/statutes)")
    parser.add_argument("--allow-fixtures", action="store_true", help="accept fixture: true (test folders only)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--freeze", action="store_true", help=f"write <root>/{MANIFEST_NAME} if validation passes")
    mode.add_argument("--verify", action="store_true", help=f"recompute and compare with <root>/{MANIFEST_NAME}")
    mode.add_argument("--preview", action="store_true", help="print scope hashes and missing files without writing")
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code not in (0, None) else 0

    try:
        import jsonschema  # noqa: F401
    except ImportError:
        print("usage error: jsonschema is required (pip install -r divergence/requirements.txt); "
              "no fallback validation is done", file=sys.stderr)
        return 2

    root = Path(args.root) if args.root else DEFAULT_ROOT
    if not root.is_dir():
        print(f"usage error: --root {root} is not a folder", file=sys.stderr)
        return 2
    if args.allow_fixtures and root.resolve() == DEFAULT_ROOT.resolve():
        print("usage error: V16 --allow-fixtures is not allowed with the default root (divergence/statutes)",
              file=sys.stderr)
        return 2

    findings, n = validate(root, args.allow_fixtures)
    strict = root.resolve() == DEFAULT_ROOT.resolve()
    if args.verify:
        findings += verify(root, strict=strict)
    elif args.freeze or args.preview:
        findings += scope_findings(root, strict=strict)
    errors, _w = _print(findings, n)
    if args.preview:
        hashes = compute_manifest(root)
        missing = missing_scope_files(root)
        for rel, digest in hashes.items():
            print(f"{digest[:16]}  {rel}")
        print(f"preview: {len(hashes)} files, {len(missing)} missing scope files")
        for rel in missing:
            print(f"missing_scope_file {rel}")
    if args.freeze:
        if errors:
            print(f"freeze refused: {errors} errors; {MANIFEST_NAME} not written")
            return 1
        out = freeze(root, strict=strict)
        print(f"froze {len(compute_manifest(root))} files -> {out.name}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
