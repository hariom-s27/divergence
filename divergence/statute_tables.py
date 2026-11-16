"""P09 Part C3 - owner tables: counts, checks and the canonical-CSV merge ("table_check v1").

Canonical files: divergence/statutes/AMENDMENT-EFFECTS.csv and VERSION-DATES.csv. The owner edits only these.
Regenerations (act_parse --ledger, statute_build --propose) never touch them: they write
_local_text/census/partC/regen/<NAME>.<stamp>.csv (git-ignored) and print a merge preview. A merge is a separate step
after the owner's yes naming the stamped file:
    --merge-preview STAMPED --into CANONICAL   prints the preview and the canonical file's sha256
    --merge STAMPED --into CANONICAL --canonical-sha SHA
The merge refuses when the canonical file changed since the preview (sha differs); owner columns are taken from the
CURRENT canonical file by key (VERSION-DATES: basis_category only from the closed list, basis only with it).

Checks (C3 rules; rows 81, 82). Rejected rows are listed with reasons; nothing is auto-fixed and code never fills
applicability (P09-23):
- AMENDMENT-EFFECTS: owner_ok in {yes, fix}; fix needs owner_note; the local quote hashes to quote_sha256 and appears
  verbatim (whitespace-only fold; at most 4 pieces in order, for header-inherited quotes) in the instrument's cleaned
  text on the stated page or the page before; dates ISO; deemed_from set iff wef < assent (and equal to wef); enums.
- VERSION-DATES: owner_ok in {yes, fix}; state in the D78 list or empty; dates ISO and from <= to; tax years 'YYYY-YY';
  basis_category in the closed list and basis one line when owner_ok is set; basis_category 'unclear' => applies_*
  empty; in_force / repealed_saved rows need applies_from_tax_year or 'unclear'; D78 V05-V08 on the row as a record.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

from divergence import act_parse as ap
from divergence import statute_build as sb
from divergence import statute_extract as se
from divergence import statute_sources as ss
from divergence import statute_validate as sv
from divergence.statute_schema import parse_date, tax_year_start

TABLES_VERSION = "table_check v1"
OWNER_OK = ("yes", "fix")
QUOTE_PIECES_MAX = 4


def canonical_spec(path: Path) -> tuple:
    """(key column, owner columns, carry rule) by the canonical file's name."""
    name = Path(path).name
    if name.startswith("AMENDMENT-EFFECTS"):
        return "effect_id", ap.OWNER_COLUMNS, None
    if name.startswith("VERSION-DATES"):
        return "record_key", sb.VERSION_OWNER, sb.owner_value
    raise SystemExit(f"not a canonical table: {name}")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def counts(path: Path) -> str:
    rows = ap.read_csv(path)
    key, owner, _ = canonical_spec(path)
    parts = [f"{c} filled {sum(bool(r.get(c)) for r in rows)} / empty {sum(not r.get(c) for r in rows)}" for c in owner]
    return f"{Path(path).name}: rows {len(rows)}; " + "; ".join(parts)


def merge(stamped: Path, canonical: Path) -> tuple:
    """(merged rows, columns, preview lines): stamped rows with the canonical file's CURRENT owner columns."""
    key, owner, carry = canonical_spec(canonical)
    new = ap.read_csv(stamped)
    columns = list(new[0].keys()) if new else []
    merged, preview = ap.merge_preview(ap.read_csv(canonical), new, key, columns,
                                       tuple(c for c in owner if c in columns), carry)
    return merged, columns, preview


def _read_owner_csv(path: Path) -> tuple:
    with Path(path).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        rows = list(reader)
    if not columns or len(set(columns)) != len(columns):
        raise ValueError(f"{path.name}: missing or duplicate column names")
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError(f"{path.name}: row width does not match header")
    return rows, columns


def non_owner_hashes(rows: list, columns: list, owner: tuple) -> list:
    """One digest per row, including names and values of every non-owner column."""
    return [hashlib.sha256(json.dumps([(c, r[c]) for c in columns if c not in owner],
                                     ensure_ascii=False).encode("utf-8")).hexdigest() for r in rows]


def _owner_keys(rows: list, key: str, label: str) -> dict:
    found = {}
    for r in rows:
        value = r[key]
        if not value.strip() or value in found:
            raise ValueError(f"{label}: empty or duplicate {key} {value!r}")
        found[value] = r
    return found


def _validate_owner_row(row: dict, key: str, columns: list) -> None:
    label = row[key]
    if row["owner_ok"] not in OWNER_OK:
        raise ValueError(f"{label}: owner_ok must be yes or fix")
    if row["owner_ok"] == "fix" and "owner_note" in columns and not row["owner_note"].strip():
        raise ValueError(f"{label}: owner_ok fix needs owner_note")
    if key == "effect_id":
        return
    applies = [row[c] for c in ("applies_from_tax_year", "applies_to_tax_year")]
    for value in applies:
        if value and (not re.fullmatch(r"[0-9]{4}-[0-9]{2}", value) or
                      (int(value[:4]) + 1) % 100 != int(value[-2:])):
            raise ValueError(f"{label}: tax year {value!r} must be YYYY-YY with consecutive years")
    if row["basis_category"] not in sb.BASIS_CATEGORIES:
        raise ValueError(f"{label}: basis_category must be in the closed list")
    if row["basis_category"] == "unclear" and any(applies):
        raise ValueError(f"{label}: unclear requires empty applies_from/to")
    if row["state"] in ("never_operative", "") and any(applies):
        raise ValueError(f"{label}: never_operative / empty state requires empty applies_from/to")


def apply_owner(decisions: Path, canonical: Path | None = None, regen_dir: Path | None = None) -> tuple:
    """Validate a decision batch, guard all code cells, then write only a new regen file."""
    decisions = Path(decisions)
    batch, fields = _read_owner_csv(decisions)
    keys = [k for k in ("effect_id", "record_key") if k in fields]
    if len(keys) != 1:
        raise ValueError("decisions need exactly one key column: effect_id or record_key")
    key = keys[0]
    canonical = Path(canonical) if canonical is not None else (ap.EFFECTS_PATH if key == "effect_id"
                                                            else sb.VERSIONS_PATH)
    table_key, owner, _ = canonical_spec(canonical)
    if table_key != key:
        raise ValueError(f"decision key {key} does not match canonical key {table_key}")
    original, columns = _read_owner_csv(canonical)
    required = ({key, "owner_ok", "owner_note", "owner_target"} if key == "effect_id" else
                {key, "applies_from_tax_year", "applies_to_tax_year", "basis_category", "basis", "owner_ok"})
    if not required.issubset(fields):
        raise ValueError(f"decisions missing columns: {', '.join(sorted(required - set(fields)))}")
    allowed = {key} | (set(owner) & set(columns))
    if set(fields) - allowed:
        raise ValueError(f"unknown or unavailable decision columns: {', '.join(sorted(set(fields) - allowed))}")
    if not batch:
        raise ValueError("decisions contain no rows")
    current = _owner_keys(original, key, "canonical")
    changes = _owner_keys(batch, key, "decisions")
    if changes.keys() - current.keys():
        raise ValueError(f"unknown {key}: {', '.join(sorted(changes.keys() - current.keys()))}")
    before = non_owner_hashes(original, columns, owner)
    updated = []
    for row in original:
        row = dict(row)
        decision = changes.get(row[key])
        if decision is not None:
            row.update({c: decision[c] for c in fields if c != key})
            _validate_owner_row(row, key, columns)
        updated.append(row)
    if non_owner_hashes(updated, columns, owner) != before:
        raise ValueError("non-owner hash guard: code columns changed; nothing written")
    payload = ap.csv_text(updated, columns)
    reader = csv.DictReader(io.StringIO(payload))
    serialized = list(reader)
    if reader.fieldnames != columns or non_owner_hashes(serialized, columns, owner) != before:
        raise ValueError("non-owner hash guard: serialized code columns changed; nothing written")
    regen = Path(regen_dir) if regen_dir is not None else ap.REGEN_DIR
    output = regen / f"{canonical.stem}.{ap.stamp()}.csv"
    regen.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="") as f:
        f.write(payload)
    return output, len(original), len(batch), before


# ---------------------------------------------------------------- checks

def _iso_ok(v: str) -> bool:
    try:
        return v == "" or parse_date(v) is not None
    except ValueError:
        return False


def quote_pieces(quote: str, window: str, max_pieces: int = QUOTE_PIECES_MAX):
    """Split the whitespace-folded quote into at most max_pieces verbatim substrings of window, in order (greedy from
    the end: the longest suffix first). Returns the pieces, or None."""
    q, w = ap.fold_ws(quote), ap.fold_ws(window)
    pieces, end, limit = [], len(q), len(w)
    while end > 0:
        if len(pieces) == max_pieces:
            return None
        start = next((k for k in range(0, end) if q[k:end].strip() and w.rfind(q[k:end].strip(), 0, limit) >= 0
                      and (k == 0 or q[k - 1] == " ")), None)
        if start is None:
            return None
        piece = q[start:end].strip()
        limit = w.rfind(piece, 0, limit)
        pieces.insert(0, piece)
        end = start
    return pieces


_page_cache = {}


def _instrument_text(key: str, page: int) -> str:
    if key not in _page_cache:
        folder, fname = ss.INSTRUMENTS[key][:2]
        _page_cache[key] = ap.clean_instrument(ss.pdf_pages(se.RAW_DIR / folder / fname)).lines
    return " ".join(x.text for x in _page_cache[key] if page - 1 <= x.page <= page)


def check_effects(rows: list, quotes: dict, text_of=_instrument_text) -> list:
    """[(effect_id, [reasons])] for every row (empty reasons = accepted)."""
    out = []
    for r in rows:
        why = []
        if r.get("owner_ok") not in OWNER_OK:
            why.append(f"owner_ok {r.get('owner_ok')!r} not in yes/fix")
        if r.get("owner_ok") == "fix" and not r.get("owner_note"):
            why.append("owner_ok fix needs owner_note")
        if r.get("operation") not in ap.OPERATIONS:
            why.append(f"operation {r.get('operation')!r}")
        if r.get("commencement_source") not in ap.COMMENCEMENT:
            why.append(f"commencement_source {r.get('commencement_source')!r}")
        for c in ("applicability_note_present", "corrigendum_flag"):
            if r.get(c) not in ("yes", "no"):
                why.append(f"{c} {r.get(c)!r}")
        for c in ("wef", "deemed_from", "assent_date"):
            if not _iso_ok(r.get(c, "")):
                why.append(f"{c} not YYYY-MM-DD")
        wef, dfr, asn = r.get("wef", ""), r.get("deemed_from", ""), r.get("assent_date", "")
        if wef and asn and wef < asn and dfr != wef:
            why.append("wef before assent: deemed_from must equal wef")
        if dfr and (dfr != wef or not asn or not dfr < asn):
            why.append("deemed_from set but not (= wef and < assent)")
        q = quotes.get(r["effect_id"]) or quotes.get(r["effect_id"].split("/")[0])
        if q is None:
            why.append("no local quote")
        else:
            if ap.quote_sha256(q) != r.get("quote_sha256"):
                why.append("quote_sha256 does not match the local quote")
            key = r["effect_id"].split(":")[0]
            if key in ss.INSTRUMENTS and r.get("pdf_page", "").isdigit():
                if quote_pieces(q, text_of(key, int(r["pdf_page"]))) is None:
                    why.append(f"quote not verbatim on page {r['pdf_page']} (or the page before)")
        out.append((r["effect_id"], why))
    return out


def _record(r: dict, effects: dict) -> dict:
    """A VERSION-DATES row as a record dict for the D78 V05-V08 checks ('' -> None; state -> status)."""
    rec = {"act": r["record_key"].split(":")[1], "status": r.get("state") or None}
    for c in ("in_force_from", "in_force_to", "applies_from_tax_year", "applies_to_tax_year"):
        rec[c] = r.get(c) or None
    effs = [effects[e] for e in r.get("effect_ids", "").split(";") if e in effects]
    retro = [e for e in effs if e.get("deemed_from")]
    if "retro_knowledge" in r.get("reason_codes", "") and retro:
        rec["retrospective_from"] = min(e["deemed_from"] for e in retro)
        rec["enacted_on"] = max(e["assent_date"] for e in retro)
        rec["amended_by"] = sorted({e["act_key"] for e in retro})
    return rec


def check_versions(rows: list, effects: dict) -> list:
    out = []
    for r in rows:
        why = []
        if r.get("owner_ok") not in OWNER_OK:
            why.append(f"owner_ok {r.get('owner_ok')!r} not in yes/fix")
        if r.get("owner_ok") == "fix" and not r.get("owner_note"):
            why.append("owner_ok fix needs owner_note")
        if r.get("state", "") not in sb.STATES:
            why.append(f"state {r.get('state')!r} not in {sb.STATES}")
        for c in ("in_force_from", "in_force_to"):
            if not _iso_ok(r.get(c, "")):
                why.append(f"{c} not YYYY-MM-DD")
        for c in ("applies_from_tax_year", "applies_to_tax_year"):
            v = r.get(c, "")
            if v:
                try:
                    tax_year_start(v)
                except ValueError as e:
                    why.append(f"{c}: {e}")
        cat, basis = r.get("basis_category", ""), r.get("basis", "")
        if r.get("owner_ok") in OWNER_OK:
            if cat not in sb.BASIS_CATEGORIES:
                why.append(f"basis_category {cat!r} not in the closed list")
            if not basis.strip() or "\n" in basis:
                why.append("basis must be one non-empty line")
        if cat == "unclear" and (r.get("applies_from_tax_year") or r.get("applies_to_tax_year")):
            why.append("basis_category unclear: applies_from/to must be empty")
        if r.get("state") in ("in_force", "repealed_saved") and r.get("owner_ok") in OWNER_OK and \
                not r.get("applies_from_tax_year") and cat != "unclear":
            why.append("in force: applies_from_tax_year needed, or basis_category unclear")
        rec = _record(r, effects)
        for fn in (sv.check_v05_dates, sv.check_v06_act2025, sv.check_v07_status, sv.check_v08_retrospective):
            for level, msg in fn(rec, {}):
                if level == "ERROR":
                    why.append(f"{fn.__name__.split('_')[1].upper()}: {msg}")
        out.append((r["record_key"], why))
    return out


def report(name: str, results: list) -> str:
    rej = [(k, w) for k, w in results if w]
    lines = [f"{name}: accepted {len(results) - len(rej)}, rejected {len(rej)}"]
    lines += [f"  REJECTED {k}: " + "; ".join(w) for k, w in rej]
    return "\n".join(lines)


def main(argv=None) -> int:
    a = argparse.ArgumentParser(description=TABLES_VERSION)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--counts", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--merge-preview", metavar="STAMPED")
    g.add_argument("--merge", metavar="STAMPED")
    g.add_argument("--apply-owner", metavar="DECISIONS")
    a.add_argument("--into", metavar="CANONICAL")
    a.add_argument("--canonical-sha")
    args = a.parse_args(argv)
    if args.apply_owner:
        try:
            output, rows, changed, hashes = apply_owner(Path(args.apply_owner),
                                                       Path(args.into) if args.into else None)
        except (ValueError, OSError) as e:
            print(f"REFUSED: {e}")
            return 1
        print(f"wrote {output}; rows {rows}; decisions {changed}; non-owner row hashes unchanged {len(hashes)}")
        return 0
    if args.counts:
        print(counts(ap.EFFECTS_PATH))
        print(counts(sb.VERSIONS_PATH))
        return 0
    if args.check:
        effs = ap.read_csv(ap.EFFECTS_PATH)
        quotes = {r["effect_id"]: r["quote"] for r in ap.read_csv(ap.QUOTES_PATH)} if ap.QUOTES_PATH.exists() else {}
        r1 = check_effects(effs, quotes)
        r2 = check_versions(ap.read_csv(sb.VERSIONS_PATH), {e["effect_id"]: e for e in effs})
        print(report(ap.EFFECTS_PATH.name, r1))
        print(report(sb.VERSIONS_PATH.name, r2))
        return 1 if any(w for _, w in r1 + r2) else 0
    stamped = Path(args.merge_preview or args.merge)
    if not args.into:
        raise SystemExit("--into CANONICAL is required")
    canonical = Path(args.into)
    merged, columns, preview = merge(stamped, canonical)
    print("\n".join(preview))
    sha = sha256_path(canonical)
    print(f"canonical {canonical.name} sha256 {sha}")
    if args.merge_preview:
        return 0
    if args.canonical_sha != sha:
        print("REFUSED: the canonical file changed since the preview (or --canonical-sha missing)")
        return 1
    with open(canonical, "w", encoding="utf-8", newline="") as f:
        f.write(ap.csv_text(merged, columns))
    print(f"merged into {canonical.name}; new sha256 {sha256_path(canonical)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
