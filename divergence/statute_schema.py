"""D78 statute records: constants, ID builder, record loading, schema check, span helper.

Pure standard library except `schema_errors`, which imports jsonschema lazily so that
the validator CLI can report a missing jsonschema as a usage error (exit 2) instead
of crashing at import time.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

SCHEMA_VERSION = 1

SOURCE_KINDS = ("act", "rule", "notification", "circular")
ACTS = ("1961", "2025")
STATUSES = ("in_force", "repealed_saved", "never_operative", "prospective", "omitted")
STORAGE_MODES = ("local_only", "public_verbatim")
GAZETTE_VALUES = ("yes", "no", "unknown")
AMENDMENT_KINDS = ("finance_act", "amendment_act", "ordinance", "notification", "other")
COUNTERPART_SOURCES = ("CBDT_official", "SECONDARY")
MODIFIER_KINDS = ("circular", "notification")

RECORD_ID_RE = re.compile(r"^(act|rule|notification|circular):(1961|2025):[A-Za-z0-9.\-]+:v[1-9][0-9]*$")
UNIT_RE = re.compile(r"^[A-Za-z0-9.\-]+$")
TAX_YEAR_RE = re.compile(r"^([0-9]{4})-([0-9]{2})$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = PACKAGE_DIR / "statutes"
SCHEMA_PATH = DEFAULT_ROOT / "schema" / "statute_record.schema.json"

# 1961 Act repealed from 1 April 2026; it still applies to tax years up to 2025-26 (s.536 savings).
REPEAL_LAST_DAY = date(2026, 3, 31)
LAST_1961_TAX_YEAR = "2025-26"
# 2025 Act: first tax year 2026-27; s.1(3) commencement 1 April 2026 "save as otherwise provided".
ACT2025_FIRST_TAX_YEAR = "2026-27"
ACT2025_COMMENCEMENT = date(2026, 4, 1)

_schema_cache: dict | None = None


def build_record_id(source_kind: str, act: str, unit: str, version_id: int) -> str:
    """Return f"{source_kind}:{act}:{unit}:v{version_id}" after checking each part."""
    if source_kind not in SOURCE_KINDS:
        raise ValueError(f"source_kind must be one of {SOURCE_KINDS}: {source_kind!r}")
    if act not in ACTS:
        raise ValueError(f"act must be one of {ACTS}: {act!r}")
    if not isinstance(unit, str) or not UNIT_RE.match(unit):
        raise ValueError(f"unit must match {UNIT_RE.pattern}: {unit!r}")
    if isinstance(version_id, bool) or not isinstance(version_id, int) or version_id < 1:
        raise ValueError(f"version_id must be an int >= 1: {version_id!r}")
    return f"{source_kind}:{act}:{unit}:v{version_id}"


def record_stem(record_id: str) -> str:
    """File stem for a record: ':' replaced by '__'."""
    return record_id.replace(":", "__")


def record_filename(record_id: str) -> str:
    return record_stem(record_id) + ".json"


def body_filename(record_id: str) -> str:
    return record_stem(record_id) + ".txt"


def tax_year_start(tax_year: str) -> int:
    """'2026-27' -> 2026. Raises ValueError on bad format or if second part != (first+1) mod 100."""
    m = TAX_YEAR_RE.match(tax_year) if isinstance(tax_year, str) else None
    if not m:
        raise ValueError(f"tax year must be 'YYYY-YY': {tax_year!r}")
    first, second = int(m.group(1)), int(m.group(2))
    if second != (first + 1) % 100:
        raise ValueError(f"tax year second part must be (first+1) mod 100: {tax_year!r}")
    return first


def tax_year_bounds(tax_year: str) -> tuple[date, date]:
    """First and last day of the tax year: 1 April .. 31 March (inclusive)."""
    y = tax_year_start(tax_year)
    return date(y, 4, 1), date(y + 1, 3, 31)


def parse_date(value: str | None) -> date | None:
    """Parse a strict 'YYYY-MM-DD' string; None stays None."""
    if value is None:
        return None
    if not isinstance(value, str) or not DATE_RE.match(value):
        raise ValueError(f"date must be 'YYYY-MM-DD': {value!r}")
    return date.fromisoformat(value)


def load_schema() -> dict:
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = json.loads(SCHEMA_PATH.read_bytes().decode("utf-8"))
    return _schema_cache


def load_record(path: str | Path) -> dict:
    """Read one metadata record (strict UTF-8, JSON object)."""
    data = json.loads(Path(path).read_bytes().decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: a record must be a JSON object")
    return data


def schema_errors(record: object) -> list[str]:
    """JSON Schema (draft 2020-12) errors for one record, sorted; empty list = valid."""
    import jsonschema  # lazy: see module docstring

    cls = jsonschema.Draft202012Validator
    validator = cls(load_schema(), format_checker=cls.FORMAT_CHECKER)
    out = []
    for err in validator.iter_errors(record):
        out.append(f"{err.json_path}: {err.message}")
    return sorted(out)


def get_span(body: str, start: int, end: int) -> str:
    """Code-point slice [start, end) of the body exactly as stored. No normalisation."""
    for name, v in (("start", start), ("end", end)):
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError(f"{name} must be an int: {v!r}")
    if not (0 <= start < end <= len(body)):
        raise ValueError(f"need 0 <= start < end <= {len(body)}; got start={start}, end={end}")
    return body[start:end]


def body_sha256(text: str) -> str:
    """Lowercase hex SHA-256 of the body's UTF-8 bytes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def modifications(record: dict, index: dict) -> tuple:
    """Records (circulars / notifications) listed in record['modified_by'], in listed order.

    Raises KeyError if a listed record_id is not in the index.
    """
    return tuple(index[rid] for rid in record.get("modified_by") or ())
