"""Pure D78 metadata projection. No file reads, body reconstruction, or persistence.

knowledge is {edition_key: ISO date | {date: ISO date}} or None; fetch_log is
the caller-supplied FETCH-LOG object or None. Missing knowledge/provenance stays
unknown until C4-C supplies it. Printed bodies/headings/hashes are attached by
the ingest caller; no placeholder body is manufactured for a printed record.
"""
from __future__ import annotations

import re
from datetime import timedelta

from divergence.statute_build import LABEL_GAP
from divergence.statute_extract import EDITIONS
from divergence.statute_schema import (
    BASIS_CATEGORIES, LOOKUP_FLAGS, REPEAL_DAY, body_sha256, build_record_id, parse_date,
)


def registered_url(item):
    """Only a literal registered URL, including a URL inside the registry's where label."""
    match = re.search(r"https://[^\s)]+", item.get("where", ""))
    return item.get("url") or (match.group() if match else "")


def parse_basis_exceptions(basis, effects):
    match = re.search(r"\bexcept\s+(.+)$", basis or "")
    if not match:
        if re.search(r"\bexcept\b", basis or ""):
            raise ValueError("empty basis exception tail")
        return []
    out = []
    for text in match.group(1).split(";"):
        effect_id, sep, category = text.strip().partition("=")
        effect_id, category = effect_id.strip(), category.strip()
        if not sep or effect_id not in effects or category not in BASIS_CATEGORIES:
            raise ValueError(f"invalid basis exception: {text!r}")
        out.append({"effect_id": effect_id, "category": category})
    return out


def _state_effects(row, effects, act, unit):
    start = row["in_force_from"]
    return sorted((e for e in effects if e["target_act"] == act and e["target_section"] == unit
                   and e.get("wef") and start and e["wef"] <= start), key=lambda e: e["effect_id"])


def _amendment(effect, registry):
    item = registry[effect["effect_id"].split(":", 1)[0]]
    # Registry item names identify the instrument type; source_kind describes the copy (Gazette/ITD).
    if not item["item"].startswith("Finance "):
        raise ValueError(f"unsupported registered instrument type: {item['key']}")
    operation = effect["operation"]
    if operation not in ("substitute", "insert", "omit", "renumber"):
        raise ValueError(f"invalid amendment operation: {operation}")
    return {"ref": effect["effect_id"], "kind": "finance_act", "operation": operation,
            "url": registered_url(item), "enacted_on": effect.get("assent_date") or None}


def _counterpart(act, unit, mapping):
    if act != "1961":
        return None
    rows = [r for r in mapping if r["section_1961"] == unit]
    if len(rows) != 1 or not rows[0].get("operative_2025"):
        raise ValueError(f"missing or duplicate counterpart for 1961:{unit}")
    out = {"ref": f"act:2025:{rows[0]['operative_2025']}",
           "source": "CBDT_official" if unit == "194S" else "SECONDARY", "source_url": ""}
    if unit == "194S":
        out["notes"] = "official Act PDF, owner eye check"
    elif unit == "115BBH":
        out["notes"] = "unverified"
    return out


def _knowledge_date(knowledge, edition):
    value = (knowledge or {}).get(edition)
    return value.get("date") if isinstance(value, dict) else value


def _provenance(row, act, unit, status, registry, knowledge, fetch):
    match = re.search(r"(?:^|;\s*)text = ([A-Za-z0-9_]+)(?:;|$)", row.get("code_note", ""))
    edition = match.group(1) if match else None
    if status == "unprinted":
        edition = EDITIONS[act][-1]
    if status == "never_operative":
        edition = None
    item, entry = registry.get(edition, {}), fetch.get(edition, {})
    out = {"text_current_as_of": _knowledge_date(knowledge, edition),
           "source_url": entry.get("url") or registered_url(item),
           "source_page_act": item.get("item", ""),
           "source_page_year": edition.rsplit("_", 1)[-1] if edition else None,
           "source_amended_up_to": _knowledge_date(knowledge, edition),
           "retrieved_at": entry.get("finished_at") or entry.get("started_at"),
           "gazette_published": "no" if edition and edition.startswith("ita") and edition != "ita2025_gz" else "unknown",
           "source_acknowledgement": ("Income Tax Department, Government of India" if edition
                                      else "Original text not operative")}
    if (edition, unit) in LABEL_GAP:
        out["notes"] = "source_label_gap"
    return out


def _registered_assent(sources):
    registry = {r["key"]: r for r in sources.get("items", []) + sources.get("manual", [])}
    originals = [r for r in registry.values() if r.get("act_no") == 30 and r.get("act_year") == 2025]
    if len(originals) != 1 or not originals[0].get("assent_date"):
        raise ValueError("Act 30/2025 must have exactly one registered assent date")
    return originals[0]["assent_date"]


def _row_dates(row, effects, assent_2025):
    _, act, unit, _ = row["record_key"].split(":")
    state = _state_effects(row, effects, act, unit)
    enacted = max((e["assent_date"] for e in state if e.get("assent_date")), default=None)
    if enacted is None and act == "2025":
        enacted = assent_2025
    start, end = row["in_force_from"] or None, row["in_force_to"] or None
    status = row["state"] or "unprinted"
    if status == "in_force" and act == "1961" and end == REPEAL_DAY.isoformat() and start != end:
        status = "repealed_saved"
    if act == "1961" and start == end == REPEAL_DAY.isoformat():
        end = (REPEAL_DAY + timedelta(days=1)).isoformat()
    retro = start if start and enacted and parse_date(start) < parse_date(enacted) else None
    return {"status": status, "in_force_from": enacted if retro else start, "in_force_to": end,
            "retrospective_from": retro, "enacted_on": enacted}


def project_dates(vd, effects, sources):
    """Pure D3-D5 conversion shared by project() and the table checker.

    Repeal-day equality gets one day only for the 1961 repeal date. All other
    equality remains for strict V05 to reject. Missing predecessors are allowed
    here for row-level checking; project() separately requires complete chains.
    """
    assent_2025 = _registered_assent(sources)
    out = {row["record_key"]: _row_dates(row, effects, assent_2025) for row in vd}
    if len(out) != len(vd):
        raise ValueError("duplicate version row")
    for row in vd:
        kind, act, unit, version = row["record_key"].split(":")
        number = int(version[1:])
        previous = out.get(build_record_id(kind, act, unit, number - 1)) if number > 1 else None
        rec = out[row["record_key"]]
        if rec["retrospective_from"] and previous:
            previous["in_force_to"] = rec["enacted_on"]
    return out


def _effect_index(effects):
    effect_index = {e["effect_id"]: e for e in effects}
    if len(effect_index) != len(effects):
        raise ValueError("duplicate effect id")
    for effect in effects:
        # An owner clause path cannot redirect the section used for cumulative state.
        sections = re.findall(r"(?<!sub-)\bsection\s+(\d+[A-Z]*)\b", effect.get("owner_target", ""), re.I)
        if any(section != effect["target_section"] for section in sections):
            raise ValueError(f"owner_target changes section: {effect['effect_id']}")
    return effect_index


def _project_row(row, effects, registry, mapping, knowledge, fetch, dates, effect_index):
    source_kind, act, unit, version = row["record_key"].split(":")
    number = int(version[1:])
    if build_record_id(source_kind, act, unit, number) != row["record_key"]:
        raise ValueError("invalid version row key")
    if row.get("basis_category") not in BASIS_CATEGORIES:
        raise ValueError(f"invalid basis category: {row.get('basis_category')!r}")
    state = _state_effects(row, effects, act, unit)
    rec = {"schema_version": 1, "record_id": row["record_key"], "source_kind": source_kind,
           "act": act, "unit": unit, "section": unit, "version_id": number,
           "supersedes": build_record_id(source_kind, act, unit, number - 1) if number > 1 else None,
           "applies_from_tax_year": row.get("applies_from_tax_year") or None,
           "applies_to_tax_year": row.get("applies_to_tax_year") or None,
           "basis_category": row["basis_category"],
           "basis_exceptions": parse_basis_exceptions(row.get("basis"), effect_index),
           "lookup_flags": [c for c in row.get("reason_codes", "").split(";") if c in LOOKUP_FLAGS],
           "amended_by": [_amendment(e, registry) for e in state], "modified_by": [],
           "outstanding_effects": [], "counterpart": _counterpart(act, unit, mapping), "storage_mode": "local_only"}
    rec.update(dates)
    rec.update(_provenance(row, act, unit, rec["status"], registry, knowledge, fetch))
    if rec["status"] == "unprinted":
        rec.update(body=None, body_sha256=None, body_chars=None)
    elif rec["status"] == "never_operative":
        rec.update(in_force_from=None, in_force_to=None, body="", body_sha256=body_sha256(""), body_chars=0,
                   original_note="Zero-length original text: amendments began on the commencement day.")
    return rec


def _link_knowledge(out):
    by_id = {r["record_id"]: r for r in out}
    for rec in out:
        previous = by_id.get(rec["supersedes"])
        if rec["supersedes"] and previous is None:
            raise ValueError(f"missing predecessor: {rec['supersedes']}")
        if previous and previous["status"] == "never_operative":
            previous["text_current_as_of"] = rec["enacted_on"]


def project(vd, effects, sources, mapping, knowledge, fetch_log=None):
    """Project exactly one record per version row; all local provenance is passed explicitly.

    With knowledge/fetch_log None the result is suitable for lookup tests, not
    persistence. Printed body fields are deliberately absent until ingest.
    """
    registry = {r["key"]: r for r in sources.get("items", []) + sources.get("manual", [])}
    effect_index = _effect_index(effects)
    dates = project_dates(vd, effects, sources)
    fetch = {r["key"]: r for r in (fetch_log or {}).get("entries", [])}
    out = [_project_row(row, effects, registry, mapping, knowledge, fetch, dates[row["record_key"]], effect_index)
           for row in vd]
    _link_knowledge(out)
    return out
