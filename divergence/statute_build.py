"""P09 Part C2 - edition diffs, two-way cross-check and version proposals for the spine ("statute_build v1").

Inputs: the ledger (AMENDMENT-EFFECTS.csv, act_parse v1), the edition PDFs (extractor v11.1, unchanged), SOURCES.json
(assent dates), the corrigenda. Every output is a PROPOSAL for the owner; nothing here decides a legal reading.

Edition knowledge date (Q4 c): 1961 editions = the assent date of the latest Act(s) named in the parsed convention note
(rule a); the printed '[AS AMENDED BY ...]' title line is compared and mismatches reported. Editions without a note
use the printed title line (resolved through the alias table); if none is printed the date is unknown and the edition
is not used for state matching.

Pending marks (row 78, Q3 b): a footnote that says 'shall be' + inserted/substituted/omitted/renumbered (or their
abbreviations Ins./Sub./Omtt./Renum.) with a w.e.f. date later than the edition's knowledge date ->
pending_change_marked. Applied to the bracket_new_but_text_in_prev apparatus rows (the 23).

Cross-check (row 77, 'corpus consistency'): effect -> evidence (an amendment span or editor note naming the effect's Act
in the section, in an edition that knows the Act; else a diff hunk only; else none) and edition change -> explanation
(marks only / effect / corrigendum / amendment not in ledger / publisher_change proposal).

Versions (row 75): per spine section the boundaries are the effects' start dates. An interval's state = the effects
started on or before its start; its text is the earliest edition whose printed state (effects enacted by its knowledge
date, minus effects it marks as pending) equals that state. No such edition -> AMBIGUOUS unprinted_intermediate (never
rebuilt). Zero-length -> never_operative proposal. 1961 versions from the 2025 Act's commencement (the repeal day) ->
repeal_day_unsettled. Effects with deemed_from -> retro_knowledge. Intervals before the first printed one are
before_coverage (counted, not written as rows).
"""
from __future__ import annotations

import argparse
import bisect
import contextlib
import io
from collections import Counter
from datetime import date
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

from divergence import act_parse as ap
from divergence import statute_extract as se
from divergence import statute_sources as ss

BUILD_VERSION = "statute_build v1"
REASON_CODES = ("unprinted_intermediate", "retro_knowledge", "repeal_day_unsettled", "applicability_unclear",
                "corrigendum_open", "before_coverage")
VERSION_COLUMNS = ["record_key", "in_force_from", "in_force_to", "state", "effect_ids", "reason_codes", "code_note",
                   "applies_from_tax_year", "applies_to_tax_year", "basis_category", "basis", "owner_ok", "owner_note"]
VERSION_OWNER = ("applies_from_tax_year", "applies_to_tax_year", "basis_category", "basis", "owner_ok", "owner_note")
STATES = ("in_force", "repealed_saved", "never_operative", "prospective", "omitted", "")   # D78 status; "" = no text
BASIS_CATEGORIES = ("charging_ay_rule", "procedural", "penalty_default_date", "transaction_date", "ita2025_tax_year",
                    "unclear")


def owner_value(row: dict, column: str) -> bool:
    """Merge carry rule for VERSION-DATES: basis_category only from the owner's closed list; basis only with a valid
    basis_category; other owner columns as written."""
    if column == "basis_category":
        return row.get(column, "") in BASIS_CATEGORIES
    if column == "basis":
        return row.get("basis_category", "") in BASIS_CATEGORIES
    return True


VERSIONS_PATH = se.STATUTES_DIR / "VERSION-DATES.csv"
REPEAL_NOTE = "same-day repeal by s.536 of the 2025 Act; legal status unsettled"
# (edition, section) -> owner's choice of start page for an UNRESOLVED section (data, not a rule)
OWNER_CHOICES = {
    ("ita1961_2023", "56"): {"page": 461, "date": "2026-11-15",
                             "note": "owner eye check: p.461 is the full s.56; p.862 is a partial reprint (C2 D1 = A)"},
}
# Owner relabels of edition changes (C3 E2, 2026-11-15), keyed by (act, section, newer edition, hunk_key) - hash keys,
# no law text. Applied after the rule label; the rule label is kept in the detail.
_E2 = "owner 2026-11-15"
OWNER_RELABELS = {
    **{("1961", "158B", "ita1961_2024n2", k): ("effect", f"{_E2}: fa2_2024:s49 (Chapter XIV-B substituted)") for k in (
        "bfb078fa6a1ceeb5", "8c5ea80fff3446a9", "3455acda137262aa", "4bdb3050f6bedf67", "189f27bc58cdc09e",
        "eb461e132bb43742", "5ef4ba4364eda50f", "ad26bf6ef6f1256c", "77feacb88c77c55d", "4b3aff305dd82e84",
        "7f67ba59530e9afe", "f9375b27ae1c3134", "8c5e708d09e10a44", "3e6e6f21ba1bfbd2")},
    ("1961", "158B", "ita1961_2025", "c8b6d8f8b998691b"): ("publisher_change", f"{_E2}: spelling"),
    ("2025", "393", "ita2025_2026", "d39d354bce4ede77"): ("publisher_change", f"{_E2}: 2026 edition restores Gazette text"),
    ("2025", "393", "ita2025_2026", "b92a3652bf44c2b6"): ("publisher_change", f"{_E2}: 2026 edition restores Gazette text"),
    ("2025", "393", "ita2025_2026", "de849e4b2ad22c44"): ("layout", f"{_E2}: table header moved"),
    ("2025", "393", "ita2025_2026", "880d9faaf9a7abfc"): ("layout", f"{_E2}: table furniture moved"),
    ("2025", "393", "ita2025_2026", "b5c496581f486773"): ("corrigendum", f"{_E2}: corr_ita2025 item 34 (+ glued word)"),
    ("2025", "393", "ita2025_2026", "73016e7da4b200de"): ("corrigendum", f"{_E2}: corr_ita2025 item 33"),
    ("2025", "393", "ita2025_2026", "0106d8a7d004771f"): ("effect", f"{_E2}: fa_2026:s84(d) (sub-section (7) substituted)"),
}
_E2b = "owner 2026-11-16"
OWNER_RELABELS.update({
    ("1961", "56", "ita1961_2024n2", "50ff389378ea6be5"): (
        "publisher_change", f"{_E2b}: official title SEBI (Alternative Investment Funds) Regulations, 2012"),
    ("2025", "393", "ita2025_2026", "9c43db25fc8bf60c"): (
        "publisher_change", f"{_E2b}: Gazette 265620 p.412 has no 'and'; 2026 edition restores the Gazette text"),
    ("2025", "393", "ita2025_2026", "b3c5a81ebbbec24c"): (
        "effect", f"{_E2b}: fa_2026:s84(b)(ii) (item (iv) substituted; Gazette 271439 p.56)"),
})
OWNER_EYE_CHECK = set()                     # rows 16, 22, 23 resolved by the owner (2026-11-16)
PENDING_RE = re.compile(r"(?i)shall\s+be\s+(ins(?:erted|\.)|sub(?:stituted|s?\.)|om(?:itted|tt?\.|it\.)|"
                        r"re-?numbered|renum(?:bered|\.))")
FN_DATE_RE = re.compile(r"w\.(?:r\.)?e\.f\.\s*(\d{1,2})\s*-\s*(\d{1,2})\s*-\s*(\d{4})")
AMENDED_BY_RE = re.compile(r"^\s*\[\s*AS\s+AMENDED\s+BY\s+(.+?)\s*\]\s*$", re.I)
MARKS_ONLY_RE = re.compile(r"[\[\]*\s]")
ALNUM_RE = re.compile(r"[^a-z0-9]")
GLUED_DIGITS_RE = re.compile(r"(?<=[A-Za-z]{2})\d{1,3}\b")
LABEL_RE = re.compile(r"^\[?\(?(?:\d{1,3}[A-Z]{0,4}|[a-z]{1,6}|[A-Z]{1,4})\)\]?$")
RECALL_YEARS = range(2022, 2027)
CTX_WORDS = 3
UNEXPLAINED = ("publisher_change", "amendment_not_in_ledger", "older_act_span", "span_unlinked",
               "owner_eye_check_pending")


# ---------------------------------------------------------------- knowledge dates

def assent_by_act() -> dict:
    """'Act No. N of YYYY' -> assent date from SOURCES.json (Gazette entries; ITD copies without a date are skipped)."""
    data = json.loads(ss.SOURCES_PATH.read_text(encoding="utf-8"))
    out = {}
    for it in data["items"] + data.get("manual", []):
        if it.get("act_no") and it.get("assent_date"):
            out.setdefault(f"Act No. {it['act_no']} of {it['act_year']}", it["assent_date"])
    return out


def resolve_title(name: str):
    """A printed Act title (any case) -> alias key 'Act No. N of YYYY', else the normalised name."""
    n = se.normalise_act(" ".join(name.split()))
    upper = {k.upper(): v for k, v in se.ACT_ALIASES.items()}
    return upper.get(n.upper(), n)


def printed_amended_by(pages: list, first_pages: int = 30):
    """Acts on the edition's '[AS AMENDED BY X AND Y]' title line, as printed, or None."""
    for text in pages[:first_pages]:
        for ln in text.splitlines():
            m = AMENDED_BY_RE.match(ln)
            if m:
                return [a.strip() for a in re.split(r"\s+AND\s+", m.group(1), flags=re.I)]
    return None


def edition_knowledge(conv: dict, printed: list | None, assent: dict, act: str) -> dict:
    """{'date', 'source', 'acts', 'printed_acts', 'mismatch'} (Q4 c)."""
    note = [resolve_title(a) for a in conv.get("latest_acts", [])] if conv.get("status") == "found" else []
    prn = [resolve_title(a) for a in printed] if printed else []
    if act == "1961" and note:
        acts, source = note, "convention_note"
    elif prn:
        acts, source = prn, "printed_title_line"
    elif note:
        acts, source = note, "convention_note"
    else:
        return {"date": None, "source": "unknown", "acts": [], "printed_acts": prn, "mismatch": None}
    dates = [assent.get(a) for a in acts]
    date = max(dates) if dates and all(dates) else None
    mismatch = (sorted(note) != sorted(prn)) if (note and prn) else None
    return {"date": date, "source": source if date else source + " (no assent date held)", "acts": acts,
            "printed_acts": prn, "mismatch": mismatch}


def fn_date(text: str):
    m = FN_DATE_RE.search(text or "")
    if not m:
        return None
    d, mo, y = m.groups()
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"


def pending_rule(fn_text: str | None, knowledge: str | None) -> tuple:
    """(relabel?, reason). relabel iff 'shall be' + verb (abbreviations accepted) and a w.e.f. later than knowledge."""
    if not fn_text:
        return False, "no_footnote_text"
    v = PENDING_RE.search(fn_text)
    if not v:
        return False, "no_pending_wording"
    d = fn_date(fn_text[v.start():]) or fn_date(fn_text)
    if d is None:
        return False, "no_wef_date"
    if knowledge is None:
        return False, "knowledge_unknown"
    return (d > knowledge, f"wef {d} {'>' if d > knowledge else '<='} knowledge {knowledge}")


# ---------------------------------------------------------------- diffs

def word_hunks(old: str, new: str, ctx: int = CTX_WORDS) -> list:
    """Word hunks between two folded bodies: op, old/new words, old index, ctx words before/after on each side
    (ob/oa, nb/na) and 'key' = sha256 of op|old|new|ob|oa (16 hex; stores owner relabels without any law text)."""
    a, b = old.split(), new.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != "equal":
            h = {"op": op, "old": " ".join(a[i1:i2]), "new": " ".join(b[j1:j2]), "at": i1,
                 "ob": " ".join(a[max(0, i1 - ctx):i1]), "oa": " ".join(a[i2:i2 + ctx]),
                 "nb": " ".join(b[max(0, j1 - ctx):j1]), "na": " ".join(b[j2:j2 + ctx])}
            h["key"] = hunk_key(h)
            out.append(h)
    return out


def hunk_key(h: dict) -> str:
    raw = "|".join((h["op"], h["old"], h["new"], h.get("ob", ""), h.get("oa", "")))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def corr_explains(c: dict, h: dict) -> bool:
    """A corrigendum item explains a hunk when, on the hunk with its context words (glued words folded: letters and
    digits only), the 'for' words occur on the old side and the 'read' words on the new side, and the change is real:
    'read' is absent from the old side or 'for' is absent from the new side."""
    f, r = _alnum(c.get("for") or ""), _alnum(c.get("read") or "")
    if not f or not r:
        return False
    old = _alnum(" ".join((h.get("ob", ""), h["old"], h.get("oa", ""))))
    new = _alnum(" ".join((h.get("nb", ""), h["new"], h.get("na", ""))))
    return f in old and r in new and (r not in old or f not in new)


def marks_only(h: dict) -> bool:
    return MARKS_ONLY_RE.sub("", h["old"]) == MARKS_ONLY_RE.sub("", h["new"])


def _cover(needle: str, hay: str) -> float:
    n, hh = se.skeleton(needle), se.skeleton(hay)
    return len(se.covered(n, hh)) / len(n) if n else 0.0


def _alnum(s: str) -> str:
    return ALNUM_RE.sub("", GLUED_DIGITS_RE.sub("", s).lower())


def explain_hunk(h: dict, spans: list, ledger_acts: set, corr: list, realised: list = (),
                 window_effects: list = ()) -> tuple:
    """(label, detail) for one edition change. spans: the newer edition's amendment apparatus entries for the section
    (dicts with cmp_span/span_text, act_key, old_text). corr: parsed corrigendum items for that edition's Act.
    realised: inserted texts of the previous edition's editor notes realised in this edition. window_effects: ledger
    effect ids for the section whose Act was enacted between the two editions' knowledge dates (weaker evidence)."""
    if marks_only(h):
        return "marks_only", ""
    if _alnum(h["old"]) == _alnum(h["new"]):
        return "format_only", "hyphenation / punctuation / spacing / glued marker digits"
    if all(re.fullmatch(r"\d{1,3}", w) for w in (h["old"] + " " + h["new"]).split()):
        return "format_only", "lone number (marker residue)"
    if _alnum(" ".join(w for w in h["old"].split() if not LABEL_RE.match(w.strip(";,.:")))) == \
            _alnum(" ".join(w for w in h["new"].split() if not LABEL_RE.match(w.strip(";,.:")))):
        return "label_only", "clause labels only"
    for c in corr:
        if corr_explains(c, h):
            return "corrigendum", f"page {c['gazette_page']} line {c['gazette_lines']}"
    best = None
    deletion = not _alnum(MARKS_ONLY_RE.sub("", h["new"]))          # deleted, or replaced by a '[***]' mark
    for e in spans:
        if not deletion:
            score = _cover(h["new"], e.get("cmp_span") or e.get("span_text") or "")
        else:
            score = _cover(h["old"], (e.get("old_text") or "") + " " + (e.get("star_words") or "") + " "
                           + (e.get("fn_text") or ""))
        if score >= 0.5 and (best is None or score > best[0]):
            best = (score, e)
    if best is None:
        if h["new"] and any(_cover(h["new"], t) >= 0.5 for t in realised if t):
            return "editor_note_realised", "text of the previous edition's editor note"
        if window_effects:
            return "effect_in_window", ";".join(window_effects)
        return "publisher_change", "no overlapping amendment span"
    act = best[1].get("act_key")
    if act in ledger_acts:
        return "effect", act
    if not act:
        return "span_unlinked", "overlapping amendment span without a linked footnote"
    m = re.search(r"of (\d{4})$", act or "")
    if act and m and int(m.group(1)) in RECALL_YEARS:
        return "amendment_not_in_ledger", act
    return "older_act_span", act or "unlinked"


def effect_evidence(eff: dict, editions: list, apparatus: dict, notes: list, hunks: dict) -> tuple:
    """(label, edition) for one effect. editions: [(key, knowledge date)] in order for the effect's Act."""
    sec, act_key = eff["target_section"], eff["act_key"]
    knowing = [k for k, kd in editions if kd and eff["assent_date"] and kd >= eff["assent_date"]]
    for k in knowing:
        if any(e.get("act_key") == act_key for e in apparatus.get((k, sec), [])):
            return "apparatus", k
        if any(resolve_title(n.get("instrument_as_printed") or "") == act_key for n in notes
               if n["edition"] == k and n.get("target_section", n["section"]) == sec):
            return "editor_note", k
    if knowing and hunks.get((knowing[0], sec)):
        return "diff_only", knowing[0]
    return "none", knowing[0] if knowing else "-"


# ---------------------------------------------------------------- versions

def printed_state(effects: list, knowledge: str | None, pending: set) -> frozenset | None:
    if knowledge is None:
        return None
    return frozenset(e["effect_id"] for e in effects if e["assent_date"] and e["assent_date"] <= knowledge) - pending


def propose_versions(act: str, section: str, effects: list, editions: list, origin: str | None, end: str | None,
                     repeal_day: str | None = None, inserted: bool = False) -> tuple:
    """(rows, before_coverage list, unplaced effect ids). editions: [{'key', 'knowledge', 'found', 'pending'}] in
    edition order. origin: first day the section can be in force (None = open). end: last in_force_to (1961 repeal day)
    or None. repeal_day: 1961 only - versions starting that day are repeal_day_unsettled, not never_operative.
    inserted: the origin is the section's own insertion date (no original text before it)."""
    placed = [e for e in effects if e.get("wef")]
    unplaced = [e["effect_id"] for e in effects if not e.get("wef")]
    starts = sorted({e["wef"] for e in placed})
    points = ([origin] if origin else [None]) + [d for d in starts if origin is None or d > origin]
    zero_at_origin = origin is not None and origin in starts and not inserted
    states = {}
    for ed in editions:
        st = printed_state(placed, ed["knowledge"], ed.get("pending", set()))
        if st is not None and ed["found"]:
            states.setdefault(st, ed["key"])
    know_of = {ed["key"]: ed["knowledge"] for ed in editions}
    rows, before, covered = [], [], False
    n = 0

    def row(frm, to, state, ids, reasons, cat, note, text=None):
        nonlocal n
        n += 1
        if state == "never_operative":                  # V07: never_operative has no in-force dates
            note = f"zero-length at {frm}; {note}"
            frm = to = None
        return {"record_key": f"act:{act}:{section}:v{n}", "in_force_from": frm or "", "in_force_to": to or "",
                "state": state, "effect_ids": ";".join(ids), "reason_codes": ";".join(reasons),
                "code_note": f"{cat}; {note}", "applies_from_tax_year": "", "applies_to_tax_year": "",
                "basis_category": "", "basis": "", "owner_ok": "", "owner_note": "",
                "_text": text}                          # _text: local only, not a CSV column
    if zero_at_origin:
        rows.append(row(origin, origin, "never_operative", [], [], "zero_length",
                        f"original text: effects start on the commencement day {origin}"))
        covered = True
    for i, p in enumerate(points):
        nxt = points[i + 1] if i + 1 < len(points) else end
        state = frozenset(e["effect_id"] for e in placed if p is not None and e["wef"] <= p)
        new = sorted(e["effect_id"] for e in placed if e["wef"] == p)
        reasons = []
        new_effs = [e for e in placed if e["effect_id"] in new]
        if any(e.get("deemed_from") for e in new_effs):
            reasons.append("retro_knowledge")
        if any(e.get("corrigendum_flag") == "yes" for e in new_effs):
            reasons.append("corrigendum_open")
        if any(e.get("applicability_note_present") == "yes" or e.get("commencement_source") in
               ("notification", "unknown") for e in new_effs):
            reasons.append("applicability_unclear")
        text = states.get(state)
        cat = "effect_start" if new else ("act_commencement" if p == origin and p else "open_start")
        if repeal_day and p == repeal_day:
            rows.append(row(p, repeal_day, "in_force", new, ["repeal_day_unsettled"] + reasons, "repeal_day",
                            f"{REPEAL_NOTE}; affects_from {repeal_day}; text = {text or 'not printed'}", text))
            covered = covered or text is not None
            continue
        if nxt is not None and p is not None and nxt <= p:
            rows.append(row(p, nxt, "never_operative", new, reasons, "zero_length", "start equals next start"))
            continue
        if text is None:
            if not covered:
                before.append({"from": p, "to": nxt, "state": sorted(state)})
                continue
            rows.append(row(p, nxt, "", new, ["unprinted_intermediate"] + reasons, cat,
                            "no edition prints this state"))
            continue
        covered = True
        if p is None and know_of.get(text):         # M2: open start -> coverage start (not commencement)
            rows.append(row(know_of[text], nxt, "in_force", new, reasons, "coverage_start",
                            f"coverage start, not commencement (knowledge date of {text}); before_coverage applies "
                            f"to earlier dates; text = {text}", text))
            continue
        rows.append(row(p, nxt, "in_force", new, reasons, cat, f"text = {text}", text))
    return rows, before, unplaced


# ---------------------------------------------------------------- run (local data)

def ledger(path: Path = ap.EFFECTS_PATH) -> list:
    return ap.read_csv(path)


def candidate_bodies(v, number: str) -> list:
    """For an UNRESOLVED section: the body extracted for each candidate start, the other candidates dropped from the
    start list (each bounded by its own end)."""
    out = []
    cands = [s for s in v.starts if s.number == number]
    for s in cands:
        starts = [t for t in v.starts if t.number != number or t is s]
        r = se.extract_section(v.cleaned, starts, number, bold=se._bold(v), italic=se._italic(v), edition=v.key)
        out.append((v.cleaned.lines[s.idx].page, r))
    return out


def build(raw: Path, out_dir: Path, effects: list | None = None, *, write: bool = True) -> dict:
    """All C2 computations; writes the local sheets in out_dir; returns the public rows and the printed summary.
    effects: the ledger rows (default: AMENDMENT-EFFECTS.csv).
    write=False returns the same computations without creating any sheets or directories."""
    effects = ledger() if effects is None else effects
    scope = se.record_scope()
    secs = {act: sorted(set(scope[act]) | set(ap.SPINE[act]), key=se.section_key) for act in ("1961", "2025")}
    views = {k: se.edition_view(raw, k) for act in se.EDITIONS for k in se.EDITIONS[act]}
    cache = {}

    def sect(k, sec):
        if (k, sec) not in cache:
            r = se.extract_view(views[k], sec)
            choice = OWNER_CHOICES.get((k, sec))
            if r["status"] == "UNRESOLVED" and choice:
                r = next(b for p, b in candidate_bodies(views[k], sec) if p == choice["page"])
            cache[(k, sec)] = r
        return cache[(k, sec)]
    assent = assent_by_act()
    conv = {k: se.convention_note(v.pages) for k, v in views.items()}
    know = {}
    for act in se.EDITIONS:
        for k in se.EDITIONS[act]:
            know[k] = edition_knowledge(conv[k], printed_amended_by(views[k].pages), assent, act)
    # apparatus (as v8_reports) over the record scope + spine
    app = {}
    for act in ("1961", "2025"):
        for sec in secs[act]:
            prev = None
            for k in se.EDITIONS[act]:
                r = sect(k, sec)
                if r["status"] == "FOUND":
                    cur = se.section_apparatus(views[k], r, conv[k])
                    pr = sect(prev, sec) if prev else None
                    ok = pr is not None and pr["status"] == "FOUND"
                    se.compare_apparatus(cur, app.get((prev, sec)) if ok else None, pr["body"] if ok else None,
                                         r["body"])
                    for e in cur:
                        if e["status"] == "disagree":
                            e["cause"] = se.disagreement_cause(e, app.get((prev, sec), []))
                    app[(k, sec)] = cur
                prev = k
    notes = se.collect_editor_notes(list(views.values()), {a: secs[a] for a in secs}, sect)
    # pending-23
    pend_rows = []
    for (k, sec), es in app.items():
        for e in es:
            if e.get("cause") == "bracket_new_but_text_in_prev":
                ok, why = pending_rule(e.get("fn_text"), know[k]["date"])
                if ok:
                    e["cause"] = "pending_change_marked"
                pend_rows.append({"edition": k, "section": sec, "page": e["page_1based"], "line": e["line_1based"],
                                  "kind": e["kind"], "act_key": e.get("act_key"), "wef": e.get("wef_as_printed"),
                                  "relabelled": ok, "reason": why, "fn_text": e.get("fn_text") or "",
                                  "span": e.get("span_text", "")})
    # diffs (spine)
    hunks, diffs_md = {}, []
    for act in ("1961", "2025"):
        for sec in ap.SPINE[act]:
            order = se.EDITIONS[act]
            for a, b in zip(order, order[1:]):
                ra, rb = sect(a, sec), sect(b, sec)
                if ra["status"] != "FOUND" or rb["status"] != "FOUND":
                    diffs_md.append(f"- {act} s.{sec} {a} -> {b}: not compared ({ra['status']} / {rb['status']})")
                    continue
                hs = word_hunks(se.fold_for_diff(ra["body"]), se.fold_for_diff(rb["body"]))
                hunks[(b, sec)] = hs
                diffs_md.append(f"- {act} s.{sec} {a} -> {b}: {len(hs)} hunks")
    # corrigenda per edition Act (corr_ita2025 for the 2025 Act editions)
    folder, fname = ss.INSTRUMENTS["corr_ita2025"][:2]
    corr2025 = [c for c in ss.corrigendum_items(ss.pdf_pages(se.RAW_DIR / folder / fname)) if c["parsed"]]
    # cross-check
    by_sec = {}
    for e in effects:
        by_sec.setdefault((e["target_act"], e["target_section"]), []).append(e)
    ev_rows = []
    for e in effects:
        eds = [(k, know[k]["date"]) for k in se.EDITIONS[e["target_act"]]]
        lab, k = effect_evidence(e, eds, app, notes, hunks)
        ev_rows.append((e["effect_id"], e["target_act"], e["target_section"], lab, k))
    ch_rows = []
    for act in ("1961", "2025"):
        for sec in ap.SPINE[act]:
            acts = {e["act_key"] for e in by_sec.get((act, sec), [])}
            order = se.EDITIONS[act]
            for i, k in enumerate(order):
                prev = order[i - 1] if i else None
                realised = [n.get("inserted_text") or "" for n in notes
                            if n["edition"] == prev and n.get("realized_in") == k
                            and n.get("target_section", n["section"]) == sec]
                lo, hi = (know[prev]["date"] if prev else None), know[k]["date"]
                window = [e["effect_id"] for e in by_sec.get((act, sec), []) if hi and e["assent_date"] <= hi
                          and (lo is None or e["assent_date"] > lo)]
                for h in hunks.get((k, sec), []):
                    spans = [x for x in app.get((k, sec), []) if x.get("span_class") == "amendment"]
                    lab, det = explain_hunk(h, spans, acts, corr2025 if act == "2025" else [], realised, window)
                    lab, det = owner_label((act, sec, k, h["key"]), lab, det)
                    ch_rows.append((act, sec, k, lab, det, h))
    # versions
    commence = commencement_2025(sect)
    vrows, before_all, unplaced_all, sec_counts = [], {}, {}, []
    eds_by, body_sha = {}, {}
    for act in ("1961", "2025"):
        for sec in ap.SPINE[act]:
            effs = by_sec.get((act, sec), [])
            eds = []
            for k in se.EDITIONS[act]:
                pend = pending_effects(effs, k, sec, app, notes)
                eds.append({"key": k, "knowledge": know[k]["date"], "found": sect(k, sec)["status"] == "FOUND",
                            "pending": pend})
            eds_by[(act, sec)] = eds
            ins = [e for e in effs if _inserts_section(e) and e["wef"]]
            origin = min(e["wef"] for e in ins) if ins else (commence if act == "2025" else None)
            end = commence if act == "1961" else None
            rows, before, unplaced = propose_versions(act, sec, effs, eds, origin, end,
                                                      repeal_day=commence if act == "1961" else None,
                                                      inserted=bool(ins))
            vrows += rows
            for r in rows:                              # guard data (C3-fix B): sha of the body each version uses
                if r.get("_text"):
                    body = sect(r["_text"], sec)["body"]
                    body_sha[r["record_key"]] = hashlib.sha256(body.encode("utf-8")).hexdigest()
            before_all[(act, sec)] = before
            unplaced_all[(act, sec)] = unplaced
            unexpl = sum(1 for r in ch_rows if r[0] == act and r[1] == sec and r[3] in UNEXPLAINED
                         and not r[4].startswith("owner "))
            unprinted = sum("unprinted_intermediate" in r["reason_codes"] for r in rows)
            sec_counts.append((act, sec, len(effs), len(rows), unprinted,
                               sum(r["state"] == "never_operative" for r in rows),
                               sum("repeal_day_unsettled" in r["reason_codes"] for r in rows),
                               sum("retro_knowledge" in r["reason_codes"] for r in rows), len(before), unexpl))
    ins_check = insertion_checks(effects, vrows, sect)
    s56 = s56_candidates(views["ita1961_2023"])
    sheets = (write_sheets(out_dir, effects, know, pend_rows, diffs_md, ev_rows, ch_rows, vrows, before_all,
                           unplaced_all, s56, commence, hunks, ins_check) if write else [])
    checks = effect_checks(effects, eds_by, sect) if all("position" in e for e in effects) else {}
    return {"effects": effects, "know": know, "pend": pend_rows, "ev": ev_rows, "ch": ch_rows, "versions": vrows,
            "before": before_all, "counts": sec_counts, "s56": s56, "commence": commence, "sheets": sheets,
            "unplaced": unplaced_all, "ins_check": ins_check, "checks": checks, "body_sha": body_sha}


# ---------------------------------------------------------------- per-row edition check (C3-fix B; owner rules 1-5)
TOP_LABEL_RE = re.compile(r"\(\s*(\d+[A-Za-z]*)\s*\)")
OMITTED_MARK_RE = re.compile(r"\s*\[\s*\*{2,}\s*\]")
# Owner data: edition sections whose SOURCE does not print most letter-suffixed labels. The check skips them (B2 d).
LABEL_GAP = {
    ("ita1961_2023", "2"): "owner eye check 2026-11-16: p.4, p.16 do not print letter-suffixed labels (source defect)",
    ("ita1961_2024n1", "2"): "owner eye check 2026-11-16 p.4-5 (source defect)",
    ("ita1961_2024n1", "56"): "owner eye check 2026-11-16 p.336 (source defect)",
    ("ita1961_2024n2", "56"): "owner eye check 2026-11-16 pp.301-305 (source defect)",
    ("ita1961_2023", "56"): "owner eye check 2026-11-16 p.466: (XII)/(XIII) not printed (source defect)",
}


def _bound(label_re: str) -> re.Pattern:
    """A label that starts a unit: at the start or after ; : . — ] (optionally then 'and'/'or'); footnote marks
    allowed (rule 4; B2 a: a free-standing 'and (3)' / '(e) and (f)' is a reference, not a heading)."""
    return re.compile(r"(?:^|[;:.—–\]]\s*(?:(?:and|or)\s+)?)[’'”\"‘“]?\s*(?:\d{1,3}\s*)?\[?\s*" + label_re)


def _paren(label: str) -> str:
    return r"\(\s*" + re.escape(label.strip("()").strip()) + r"\s*\)"


def container_segment(body: str, levels: list) -> tuple:
    """(text, scope note) for rule 3: from the top container's digit-led label heading to the next digit-led heading;
    the whole section when there is no such container or it is not found."""
    b = ap.fold_ws(body)
    top = TOP_LABEL_RE.search(levels[0]) if levels else None
    if not top or not top.group(1)[0].isdigit():
        return b, "section"
    m = _bound(_paren(top.group(1))).search(b)
    if not m:
        return b, "section"
    nxt = next((x for x in _bound(r"\(\s*(\d+[A-Za-z]*)\s*\)").finditer(b, m.end())
                if x.group(1) != top.group(1)), None)
    return b[m.start():nxt.start() if nxt else len(b)], f"container ({top.group(1)})"


def _count(seg: str, unit: str) -> int:
    if unit == "proviso":
        return len(_bound(r"Provided\b").findall(seg))
    if unit.startswith("Explanation"):
        n = unit[len("Explanation"):].strip()
        return len(_bound(r"Explanation\s*" + (re.escape(n) + r"\s*" if n else "") + r"\.?\s*[—–-]").findall(seg))
    return sum(1 for m in _bound(_paren(unit)).finditer(seg)       # B2 b: '(iv) [***]' marks an omitted unit
               if not OMITTED_MARK_RE.match(seg, m.end()))


def _pick(eds: list, section: str, want, reverse: bool = False) -> tuple:
    """(edition or None, skipped gap editions): the first edition satisfying want(), in order or reversed, passing
    over editions listed in LABEL_GAP for this section (B2 d)."""
    skipped = []
    for d in (reversed(eds) if reverse else eds):
        if want(d):
            if (d["key"], section) in LABEL_GAP:
                skipped.append(d["key"])
                continue
            return d, skipped
    return None, skipped


def check_effect(e: dict, eds: list, body_of) -> tuple:
    """(check_status, check_note) for one effect. eds: the section's editions in order ({key, knowledge, found,
    pending}); body_of(edition) -> section body. Rule 1: 'after' = first FOUND edition with knowledge >= assent_date
    that does not mark the effect pending; 'before' = last FOUND edition with knowledge < assent_date."""
    if e.get("check_note", "").startswith("unparsed:"):
        return e["check_status"], e["check_note"]
    asn, eid = e["assent_date"], e["effect_id"]
    known = [d for d in eds if d["knowledge"]]
    levels = [x for x in e["target_unit"].split(" > ") if x]
    item_level = e["target_unit"] == "" and e["operation"] == "insert" and e["position"] in ("after", "before")
    if item_level:                                      # whole-section insert: the section itself is the new unit
        if e["target_section"] not in e["new_units"].split(";"):
            return "no_edition", "no_label: target section not among new_units"
        aft = next((d for d in known if d["knowledge"] >= asn and eid not in d["pending"]), None)
        bef = next((d for d in reversed(known) if d["knowledge"] < asn), None)
        if aft is None:
            return "no_edition", "no_edition: no edition after the effect"
        if not aft["found"]:
            return "fail", f"section {e['target_section']} not found in {aft['key']}"
        if bef is not None and bef["found"]:
            return "fail", f"section {e['target_section']} already found in {bef['key']}"
        return "ok", f"section found in {aft['key']}" + (f", absent in {bef['key']}" if bef else "")
    sec = e["target_section"]
    aft, sk_a = _pick(known, sec, lambda d: d["found"] and d["knowledge"] >= asn and eid not in d["pending"])
    bef, sk_b = _pick(known, sec, lambda d: d["found"] and d["knowledge"] < asn, reverse=True)
    skip = "".join(f"; skipped:{k}:source_label_gap" for k in sk_a + sk_b)
    st, note = _check_labels(e, levels, aft, bef, body_of)
    return st, note + skip


def _check_labels(e: dict, levels: list, aft, bef, body_of) -> tuple:
    op, scope, pos = e["operation"], e["scope"], e["position"]
    if op == "insert" and scope == "unit" and e["new_units"]:
        container = levels[:-1] if pos in ("after", "before") else levels
        units = e["new_units"].split(";")
        if aft is None:
            return "no_edition", "no_edition: no edition after the effect"
        sa, where = container_segment(body_of(aft["key"]), container)
        sb_ = container_segment(body_of(bef["key"]), container)[0] if bef else None
        bad = []
        for u in dict.fromkeys(units):
            need = units.count(u)
            na = _count(sa, u)
            nb = _count(sb_, u) if sb_ is not None else None
            if u.startswith("(") and nb is None and na < 1:
                bad.append(f"{u} absent in {aft['key']}")
            elif u.startswith("(") and nb is not None and not na > nb:          # B2 c: the count must rise
                bad.append(f"{u} {aft['key']}:{na} {bef['key']}:{nb}")
            elif not u.startswith("(") and (na < need if nb is None else na - nb < need):
                bad.append(f"{u} count {aft['key']}:{na}" + (f" {bef['key']}:{nb}" if nb is not None else ""))
        if bad:
            return "fail", f"{where}: " + "; ".join(bad)
        return "ok", f"{where}: new units in {aft['key']}" + (f", count rose from {bef['key']}" if bef else "")
    if scope == "words" or (op == "omit" and scope == "unit"):
        lab = re.search(r"\(\s*([0-9A-Za-z]+)\s*\)", levels[-1]) if levels else None
        if lab is None:
            return "no_edition", "no_label: anchor has no label"
        if aft is None:
            return "no_edition", "no_edition: no edition after the effect"
        sa, where = container_segment(body_of(aft["key"]), levels[:-1])     # the anchor's parent container
        na = _count(sa, lab.group(1))
        if scope == "words":
            nb = _count(container_segment(body_of(bef["key"]), levels[:-1])[0], lab.group(1)) if bef else None
            if na < 1 or nb == 0:
                return "fail", f"{where}: anchor ({lab.group(1)}) {aft['key']}:{na}" + (
                    f" {bef['key']}:{nb}" if bef else "")
            return "ok", f"{where}: anchor ({lab.group(1)}) present"
        if na:
            return "fail", f"{where}: omitted ({lab.group(1)}) still in {aft['key']} ({na})"
        return "ok", f"{where}: omitted ({lab.group(1)}) absent in {aft['key']}"
    return "no_edition", "no_rule: no check for this operation/scope"


def effect_checks(effects: list, eds_by: dict, sect) -> dict:
    """{effect_id: (check_status, check_note)} for spine effects; uses build()'s cached section text only."""
    out = {}
    for e in effects:
        if e["target_section"] not in ap.SPINE.get(e["target_act"], []):
            out[e["effect_id"]] = ("no_edition", "no_edition: not a spine section")
            continue
        out[e["effect_id"]] = check_effect(e, eds_by[(e["target_act"], e["target_section"])],
                                           lambda k, s=e["target_section"]: sect(k, s)["body"])
    return out


INSERT_HEAD_RE = re.compile(r"^[‘'“\"]?\s*\d{1,3}[A-Z]{0,6}\s*\.\s*")
INSERT_TAIL_RE = re.compile(r"[’'”\"]\s*[.;]\s*$")


def section_segment(block: str, number: str) -> str:
    """The part of an inserted block from section `number`'s heading to the next inserted section heading."""
    heads = list(re.finditer(r"(?:^|\s)[‘'“\"]?(\d{1,3}[A-Z]{0,6})\s*\.\s+(?=\(1\)|[A-Z])", block))
    for i, m in enumerate(heads):
        if m.group(1) == number:
            end = heads[i + 1].start() if i + 1 < len(heads) else len(block)
            return block[m.start():end].strip()
    return block


def insertion_text_check(block: str, body: str) -> dict:
    """Inserted text in the Act vs the edition body, both folded; the leading 'N.' and the closing quote are dropped,
    and the body's heading (up to its first '(1)' / '—') is dropped. Report only."""
    a = se.fold_for_diff(INSERT_TAIL_RE.sub("", INSERT_HEAD_RE.sub("", block.strip())))
    b = se.fold_for_diff(body)
    m = re.search(r"\(1\)|[—–]", b)
    b_cut = b[m.start():].lstrip("—– ") if m and m.start() < 200 else b
    a_cut = a.lstrip("—– ")
    return {"identical": a_cut == b_cut, "act_covered_by_edition": round(_cover(a_cut, b_cut), 3),
            "edition_covered_by_act": round(_cover(b_cut, a_cut), 3)}


def insertion_checks(effects: list, vrows: list, sect) -> list:
    blocks = {rv["effect_id"]: rv.get("block_text", "") for r in ap.run_ledger()[0] for rv in r["review"]}
    out = []
    for e in effects:
        if not _inserts_section(e):
            continue
        first = next((r for r in vrows if r["record_key"].startswith(f"act:{e['target_act']}:{e['target_section']}:")
                      and r.get("_text")), None)
        if first is None:
            out.append({"effect_id": e["effect_id"], "edition": None})
            continue
        k = first["_text"]
        r = sect(k, e["target_section"])
        seg = section_segment(blocks.get(e["effect_id"], ""), e["target_section"])
        out.append({"effect_id": e["effect_id"], "edition": k, **insertion_text_check(seg, r["body"])})
    return out


def owner_label(key: tuple, lab: str, det: str) -> tuple:
    """Owner relabel (data) over the rule label; eye-check rows get 'owner_eye_check_pending'."""
    if key in OWNER_RELABELS:
        new, note = OWNER_RELABELS[key]
        return new, f"{note}; rule label {lab}"
    if key in OWNER_EYE_CHECK:
        return "owner_eye_check_pending", f"rule label {lab}: {det}"
    return lab, det


def _inserts_section(e: dict) -> bool:
    """A whole-section insertion: an item-level insert ('After section X ... inserted', no sub-item, no unit)."""
    return e["operation"] == "insert" and e["target_unit"] == "" and "(" not in e["instrument_provision"]


def pending_effects(effs: list, k: str, sec: str, app: dict, notes: list) -> set:
    """Effects the edition marks as not yet made: a pending_change_marked row or an editor note naming the effect's Act
    with the effect's w.e.f. date."""
    marks = {(x.get("act_key"), fn_date(x.get("fn_text") or "")) for x in app.get((k, sec), [])
             if x.get("cause") == "pending_change_marked"}
    marks |= {(resolve_title(n.get("instrument_as_printed") or ""), fn_date(n.get("wef_pointer_as_printed") or ""))
              for n in notes if n["edition"] == k and n.get("target_section", n["section"]) == sec}
    return {e["effect_id"] for e in effs if (e["act_key"], e["wef"]) in marks}


def commencement_2025(sect) -> str | None:
    """The 2025 Act's commencement from its own s.1(2) as printed (ita2025_2026, else ita2025_2025)."""
    for k in reversed(se.EDITIONS["2025"]):
        r = sect(k, "1")
        if r["status"] == "FOUND":
            s1 = ap.parse_s1(r["body"])
            if s1["whole"] and s1["whole"]["date"]:
                return s1["whole"]["date"]
    return None


def s56_candidates(v) -> dict:
    """Q1: fold-diff of the two s.56 candidate bodies in ita1961_2023."""
    c = candidate_bodies(v, "56")
    out = {"candidates": [(p, r["status"], r.get("chars")) for p, r in c]}
    if len(c) == 2 and all(r["status"] == "FOUND" for _, r in c):
        a, b = (se.fold_for_diff(r["body"]) for _, r in c)
        hs = word_hunks(a, b)
        first = [{"op": h["op"], "at": h["at"], "old_words": len(h["old"].split()), "new_words": len(h["new"].split()),
                  "old": h["old"][:120], "new": h["new"][:120]} for h in hs[:3]]
        out.update({"identical": a == b, "hunks": len(hs), "first": first})
    return out


# ---------------------------------------------------------------- Gazette check (C3 steps 5-6)

GAZETTE_KEY = "ita2025_gz"
ACT_NO_INLINE_RE = re.compile(r"\(\s*\d{1,3}\s+of\s+\d{4}\s*\)")
TABLE_FURNITURE_RE = re.compile(r"\[Table \d+ Sl\. \d+\]|\b(?:[A-E] ){1,4}[A-E]\b")
MARGIN_SENTENCE_RE = re.compile(r"^(?:[A-Z][^.]{0,70}\.\s*){1,3}$")


def gazette_index(pages: list) -> dict:
    """Cleaned Gazette lines after the enacting formula, with a skeleton-token index (letters/digits, lower case)."""
    lines = ap.clean_instrument(pages).lines
    start = next((i for i, x in enumerate(lines) if "BE it enacted" in x.text), 0)
    lines = lines[start:]
    toks, tline = [], []
    for i, x in enumerate(lines):
        for t in se.skeleton(x.text):
            toks.append(t)
            tline.append(i)
    return {"lines": lines, "toks": toks, "tline": tline}


def _find_tokens(gi: dict, needle: list, from_line: int = 0):
    """Line indexes where the token sequence starts, in order, at or after from_line (generator)."""
    toks, tline, n = gi["toks"], gi["tline"], len(needle)
    first = next((k for k, li in enumerate(tline) if li >= from_line), len(toks))
    for k in range(first, len(toks) - n + 1):
        if toks[k] == needle[0] and toks[k:k + n] == needle:
            yield tline[k]


def opening_tokens(body: str, heading, number: str) -> list:
    """The body's skeleton tokens with its heading, leading number / '(1)' tokens and ITD-added '(N of YYYY)' Act
    numbers dropped (the Gazette does not print them)."""
    w, h = se.skeleton(ACT_NO_INLINE_RE.sub(" ", body)), se.skeleton(heading or "")
    if h and w[:len(h)] == h:
        w = w[len(h):]
    k = 0
    while k < len(w) and (w[k].isdigit() or w[k] == number.lower()):
        k += 1
    return w[k:]


def _number_line(gi: dict, number: str, hit: int, floor: int):
    """A line at hit or up to 3 lines before it where 'N.' starts the line or follows a sentence end (a glued
    marginal heading)."""
    num_re = re.compile(r"(?:^|[.;:]\s+)" + re.escape(number) + r"\s*\.(?:\s|\(|$)")
    for li in range(hit, max(floor, hit - 3) - 1, -1):
        if num_re.search(gi["lines"][li].text.strip()):
            return li
    return None


def locate_gazette(gi: dict, number: str, body: str, heading, from_line: int = 0) -> dict:
    """{'start': line index | None, 'how'}: the first occurrence of the body's opening words that has the 'N.' line
    at or up to 3 lines before it; without any such occurrence the first hit line (how = 'no_number_line')."""
    w = opening_tokens(body, heading, number)
    for n in (10, 7, 5):
        if len(w) < n:
            continue
        hits = list(_find_tokens(gi, w[:n], from_line))
        for hit in hits:
            li = _number_line(gi, number, hit, from_line)
            if li is not None:
                return {"start": li, "how": f"number line ({len(hits)} hit(s) of {n} opening words)"}
        if hits:
            return {"start": hits[0], "how": f"no_number_line ({len(hits)} hit(s) of {n} opening words)"}
    return {"start": None, "how": "opening words not found"}


def gazette_bounds(gi: dict, view, number: str) -> dict:
    """Start and end line of a section in the Gazette: end = the start of section N+1 (opening words, else the first
    line beginning 'N+1.' after the start)."""
    r = se.extract_view(view, number)
    if r["status"] != "FOUND":
        return {"start": None, "end": None, "how": f"edition {r['status']}"}
    st = locate_gazette(gi, number, r["body"], r.get("heading"))
    if st["start"] is None:
        return {"start": None, "end": None, "how": st["how"]}
    nxt = str(int(number) + 1)
    rn = se.extract_view(view, nxt)
    end = None
    if rn["status"] == "FOUND":
        end = locate_gazette(gi, nxt, rn["body"], rn.get("heading"), st["start"] + 1)["start"]
    how = "next section opening words"
    if end is None:
        num_re = re.compile(r"^\s*" + re.escape(nxt) + r"\s*\.(?:\s|\()")
        end = next((i for i in range(st["start"] + 1, len(gi["lines"])) if num_re.match(gi["lines"][i].text)), None)
        how = "next number line" if end is not None else "NOT FOUND"
    if end is None:                                     # last section: the first Schedule heading after the start
        end = next((i for i in range(st["start"] + 1, len(gi["lines"]))
                    if se.SCHEDULE_LINE_RE.match(gi["lines"][i].text.strip().upper())), None)
        how = "first Schedule heading" if end is not None else "NOT FOUND"
    return {"start": st["start"], "end": end, "how": f"start {st['how']}; end {how}", "body": r["body"],
            "heading": r.get("heading")}


def gazette_class(h: dict, corr: list, number: str = "", last: int = -1) -> tuple:
    """(class, detail) of a Gazette (old) vs ITD edition (new) hunk. corr: [(item number, item)]. number: the
    section number (a leading 'N.' only in the edition is a boundary artefact); last: the Gazette span's word count
    (a trailing deleted CHAPTER heading is a boundary artefact)."""
    if marks_only(h) or _alnum(h["old"]) == _alnum(h["new"]):
        return "format", ""
    lead = re.compile(r"^\s*" + re.escape(number) + r"\s*\.\s*") if number else None
    if lead and h["at"] == 0 and lead.match(h["new"]) and _alnum(lead.sub("", h["new"])) == _alnum(h["old"]):
        return "boundary", "section number"
    if not h["new"] and h["old"].startswith("CHAPTER ") and h["at"] + len(h["old"].split()) == last:
        return "boundary", "next CHAPTER heading"
    if h["new"] != h["old"] and _alnum(h["old"]) == _alnum(ACT_NO_INLINE_RE.sub("", h["new"])):
        return "itd_addition", "Act number added"
    if _alnum(TABLE_FURNITURE_RE.sub("", h["old"])) == _alnum(TABLE_FURNITURE_RE.sub("", h["new"])):
        return "itd_addition", "table furniture"
    if not h["new"] and MARGIN_SENTENCE_RE.match(h["old"]):
        return "itd_addition", "Gazette marginal heading text"
    for i, c in corr:
        if corr_explains(c, h):
            return "corrigendum", f"corr_ita2025 item {i}"
    return "content", ""


def gazette_check(raw: Path) -> dict:
    gpath = se.RAW_DIR / ss.INSTRUMENTS[GAZETTE_KEY][0] / ss.INSTRUMENTS[GAZETTE_KEY][1]
    gi = gazette_index(ss.pdf_pages(gpath))
    v5, v6 = se.edition_view(raw, "ita2025_2025"), se.edition_view(raw, "ita2025_2026")
    folder, fname = ss.INSTRUMENTS["corr_ita2025"][:2]
    corr = [c for c in ss.corrigendum_items(ss.pdf_pages(se.RAW_DIR / folder / fname))
            if c["parsed"] and (c["target"] or "").startswith("Income-tax Act, 2025")]
    corr_n = list(enumerate(corr, 1))
    bounds, sections = {}, {}
    for sec in ap.SPINE["2025"]:
        b = gazette_bounds(gi, v5, sec)
        bounds[sec] = b
        if b["start"] is None or b["end"] is None:
            continue
        span = gi["lines"][b["start"]:b["end"]]
        text = re.sub(r"^\s*" + re.escape(sec) + r"\s*\.\s*", "", " ".join(x.text for x in span))
        pages = sorted({x.page for x in span})
        inside = [(i, c) for i, c in corr_n if int(c["gazette_page"]) in pages and _alnum(c["for"]) in _alnum(text)]
        w = se.fold_for_diff(b["body"]).split()
        hd = se.fold_for_diff(b["heading"] or "").split()
        ed = " ".join(w[len(hd):] if hd and w[:len(hd)] == hd else w)
        gtext = se.fold_for_diff(text)
        hs = word_hunks(gtext, ed)
        n_g = len(gtext.split())
        sections[sec] = {"pages": (pages[0], pages[-1]),
                         "hunks": [(h, *gazette_class(h, inside, sec, n_g)) for h in hs],
                         "corr": inside}
    missing = [s for s, b in bounds.items() if b["start"] is None or b["end"] is None]
    items = []
    for i, c in corr_n:
        sec = next((s for s, d in sections.items() if any(j == i for j, _ in d["corr"])), None)
        row = {"item": i, "page": c["gazette_page"], "lines": c["gazette_lines"], "for": c["for"], "read": c["read"],
               "section": sec}
        if sec:
            a = se.fold_for_diff(se.extract_view(v5, sec)["body"])
            b = se.fold_for_diff(se.extract_view(v6, sec)["body"])
            m = [h for h in word_hunks(a, b) if corr_explains(c, h)]
            row.update({"match": bool(m), "hunk_keys": [h["key"] for h in m],
                        "ed2025_read": _alnum(c["read"]) in _alnum(a), "ed2026_read": _alnum(c["read"]) in _alnum(b)})
        items.append(row)
    content = {s: [h for h, k, _ in d["hunks"] if k == "content"] for s, d in sections.items()}
    if missing:
        proposal = "none (bounds missing: " + ", ".join(missing) + ")"
    elif any(content.values()):
        proposal = "none (ITD-vs-Gazette content differences listed for the census)"
    else:
        proposal = "as enacted, Act 30 of 2025"
    return {"bounds": bounds, "sections": sections, "missing": missing, "items": items, "content": content,
            "proposal": proposal, "n_corr": len(corr)}


def gazette_report(g: dict) -> str:
    out = [f"# GAZETTE CHECK (Act 30 of 2025, {GAZETTE_KEY}) vs ita2025_2025, spine sections; local only", "",
           "## Bounds", ""]
    out += [f"- s.{s}: start line {b['start']} end line {b['end']} ({b['how']})" for s, b in g["bounds"].items()]
    out += ["", "## Per section (class counts; content and corrigendum hunks listed)", ""]
    for s, d in g["sections"].items():
        cnt = {}
        for _, k, _ in d["hunks"]:
            cnt[k] = cnt.get(k, 0) + 1
        out.append(f"### s.{s} (Gazette pp.{d['pages'][0]}-{d['pages'][1]}): hunks {len(d['hunks'])} {cnt}"
                   f"{' IDENTICAL' if not d['hunks'] else ''}")
        out += [f"- {k} {det} | {h['op']} @{h['at']}: {_md(h['old'][:140])} => {_md(h['new'][:140])}"
                for h, k, det in d["hunks"] if k in ("content", "corrigendum")]
        out.append("")
    out += [f"## D3: corr_ita2025 items (n={g['n_corr']})", "",
            "| item | Gazette page/line | section | for | read | match (2025->2026 hunk) | 2025 ed has read | "
            "2026 ed has read |", "|---|---|---|---|---|---|---|---|"]
    for r in g["items"]:
        out.append(f"| {r['item']} | {r['page']}/{r['lines']} | {r['section'] or 'not in a spine section'} | "
                   f"{_md(r['for'])} | {_md(r['read'])} | {r.get('match', '-')} | {r.get('ed2025_read', '-')} | "
                   f"{r.get('ed2026_read', '-')} |")
    out += ["", f"ita2025_2025 knowledge proposal: {g['proposal']}"]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- sheets and tables

def _md(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def count_table(counts: list) -> str:
    out = [f"{'act':<5} {'section':<8} {'effects':>7} {'versions':>8} {'unprinted':>9} {'never_op':>8} "
           f"{'repeal_day':>10} {'retro':>5} {'before_cov':>10} {'unexplained':>11}"]
    out += [f"{a:<5} {s:<8} {e:>7} {v:>8} {u:>9} {n:>8} {r:>10} {t:>5} {b:>10} {x:>11}"
            for a, s, e, v, u, n, r, t, b, x in counts]
    return "\n".join(out)


def s2_table(effects: list) -> str:
    rows = {}
    for e in effects:
        if e["target_section"] == "2":
            m = re.match(r"(clause \([^)]+\))", e["target_unit"])
            key = (e["target_act"], m.group(1) if m else (e["target_unit"] or "(no clause)"))
            rows[key] = rows.get(key, 0) + 1
    out = [f"{'act':<5} {'clause':<16} {'effects':>7}"]
    out += [f"{a:<5} {c:<16} {n:>7}" for (a, c), n in sorted(rows.items())]
    out.append(f"total s.2 effects: {sum(rows.values())}")
    return "\n".join(out)


def crosscheck_counts(ev_rows: list, ch_rows: list) -> str:
    ev, ch = {}, {}
    for r in ev_rows:
        ev[r[3]] = ev.get(r[3], 0) + 1
    for r in ch_rows:
        ch[r[3]] = ch.get(r[3], 0) + 1
    return ("corpus consistency: effects -> evidence (n=" + str(len(ev_rows)) + "): "
            + ", ".join(f"{k} {v}" for k, v in sorted(ev.items())) + "\n"
            + "corpus consistency: edition changes -> explanation (n=" + str(len(ch_rows)) + " hunks): "
            + ", ".join(f"{k} {v}" for k, v in sorted(ch.items())))


def write_sheets(out_dir, effects, know, pend_rows, diffs_md, ev_rows, ch_rows, vrows, before_all, unplaced_all,
                 s56, commence, hunks, ins_check=()) -> list:
    out_dir.mkdir(parents=True, exist_ok=False)
    files = []
    kn = ["# Edition knowledge dates (Q4 c)", "", "| edition | date | source | acts | printed title acts | mismatch |",
          "|---|---|---|---|---|---|"]
    kn += [f"| {k} | {v['date']} | {v['source']} | {'; '.join(v['acts'])} | {'; '.join(v['printed_acts'])} | "
           f"{v['mismatch']} |" for k, v in know.items()]
    p = ["# PENDING-23 (row 78; rule: 'shall be' + verb incl. abbreviations, w.e.f. > edition knowledge)", ""] + kn + [
        "", f"rows: {len(pend_rows)}; relabelled pending_change_marked: {sum(r['relabelled'] for r in pend_rows)}", "",
        "| edition | section | page | line | kind | act_key | wef | relabelled | reason | footnote | span |",
        "|---|---|---|---|---|---|---|---|---|---|---|"]
    p += [f"| {r['edition']} | {r['section']} | {r['page']} | {r['line']} | {r['kind']} | {r['act_key']} | {r['wef']} | "
          f"{r['relabelled']} | {r['reason']} | {_md(r['fn_text'][:200])} | {_md(r['span'][:80])} |" for r in pend_rows]
    d = ["# DIFFS (fold_for_diff v2, word hunks; spine sections, consecutive editions)", ""] + diffs_md + [""]
    for (k, sec), hs in hunks.items():
        if hs:
            d.append(f"## s.{sec} -> {k} ({len(hs)} hunks)")
            d += [f"- {h['op']} @{h['at']}: {_md(h['old'][:160])} => {_md(h['new'][:160])}" for h in hs]
            d.append("")
    c = ["# CROSSCHECK (row 77)", "", crosscheck_counts(ev_rows, ch_rows), "", "## Effect -> evidence", "",
         "| effect_id | act | section | evidence | edition |", "|---|---|---|---|---|"]
    c += [f"| {a} | {b} | {s} | {lab} | {k} |" for a, b, s, lab, k in ev_rows]
    c += ["", "## Edition change -> explanation", "", "| act | section | edition | label | detail | op | old | new |",
          "|---|---|---|---|---|---|---|---|"]
    c += [f"| {a} | {s} | {k} | {lab} | {_md(det)} | {h['op']} | {_md(h['old'][:120])} | {_md(h['new'][:120])} |"
          for a, s, k, lab, det, h in ch_rows]
    v = ["# VERSIONS (row 75 proposals; owner confirms)", "", f"2025 Act commencement (its s.1(2) as printed): "
         f"{commence}", "", "| record_key | from | to | state | effect_ids | reasons | basis |",
         "|---|---|---|---|---|---|---|"]
    v += [f"| {r['record_key']} | {r['in_force_from']} | {r['in_force_to']} | {r['state']} | {r['effect_ids']} | "
          f"{r['reason_codes']} | {_md(r['code_note'])} |" for r in vrows]
    v += ["", "## before_coverage (not written as rows)"]
    v += [f"- {a} s.{s}: {b}" for (a, s), b in before_all.items() if b]
    v += ["", "## Effects without a date (not placed on the timeline)"]
    v += [f"- {a} s.{s}: {u}" for (a, s), u in unplaced_all.items() if u]
    v += ["", "## Whole-section insertions: Act text vs first edition text (report only)"]
    v += [f"- {x}" for x in ins_check]
    v += ["", "## s.56 ita1961_2023 candidates (Q1)", "", f"- owner choice: "
          f"{OWNER_CHOICES.get(('ita1961_2023', '56'), 'pending')}", f"- {s56}"]
    for name, lines in (("PENDING-23.md", p), ("DIFFS.md", d), ("CROSSCHECK.md", c), ("VERSIONS.md", v)):
        se._write_new(out_dir / name, "\n".join(lines) + "\n")
        files.append(out_dir / name)
    return files


def main(argv=None) -> int:
    ap_ = argparse.ArgumentParser(description=BUILD_VERSION)
    ap_.add_argument("--propose", action="store_true", help="diffs, cross-check, versions; write VERSION-DATES.csv")
    ap_.add_argument("--counts", action="store_true", help="print the per-section count table of the last proposal")
    ap_.add_argument("--dry-run", action="store_true", help="compute and print; write the local sheets only")
    ap_.add_argument("--effects", metavar="CSV", help="ledger file to use (default: the canonical AMENDMENT-EFFECTS.csv)")
    ap_.add_argument("--gazette-check", action="store_true", help="C3: Act 30 of 2025 Gazette vs ita2025_2025 + D3 map")
    ap_.add_argument("--check-effects", action="store_true",
                     help="C3-fix: per-row edition check; writes regen/AMENDMENT-EFFECTS.<stamp>.csv (never canonical)")
    ap_.add_argument("--gazette-check-v3", action="store_true")
    ap_.add_argument("--baseline-v2", type=Path)
    ap_.add_argument("--out", type=Path)
    ap_.add_argument("--audit-dir", type=Path)
    ap_.add_argument("--regression-out", type=Path)
    a = ap_.parse_args(argv)
    if a.gazette_check_v3:
        return _v3_cli(a)
    if a.gazette_check:
        g = gazette_check(se.latest_raw_dir())
        rep = gazette_report(g)
        d = ap.PARTC_DIR / f"C3-{ap.stamp()}"
        d.mkdir(parents=True, exist_ok=False)
        se._write_new(d / "GAZETTE-CHECK.md", rep)
        print(rep, end="")
        print(f"sheet: {d / 'GAZETTE-CHECK.md'}")
        return 1 if g["missing"] else 0
    if not (a.propose or a.counts or a.dry_run or a.gazette_check or a.check_effects):
        ap_.print_help()
        return 2
    if a.counts:
        runs = sorted(ap.PARTC_DIR.glob("C2-*/COUNTS.txt"))
        if not runs:
            print("no C2 run found")
            return 1
        print(f"{runs[-1]}\n" + runs[-1].read_text(encoding="utf-8"), end="")
        return 0
    out_dir = ap.PARTC_DIR / f"C2-{ap.stamp()}"
    effects = ap.run_ledger()[1] if a.dry_run else (ledger(Path(a.effects)) if a.effects else None)
    print(f"ledger: {'in memory (dry run)' if a.dry_run else (a.effects or ap.EFFECTS_PATH)}")
    res = build(se.latest_raw_dir(), out_dir, effects)
    print(BUILD_VERSION)
    print("knowledge dates:")
    for k, v in res["know"].items():
        print(f"  {k}: {v['date']} ({v['source']}; acts {v['acts']}; printed {v['printed_acts']}; "
              f"mismatch {v['mismatch']})")
    print(f"2025 Act commencement: {res['commence']}")
    print(f"pending rows: {len(res['pend'])}; relabelled: {sum(r['relabelled'] for r in res['pend'])}")
    print(crosscheck_counts(res["ev"], res["ch"]))
    recall = [r for r in res["ch"] if r[3] == "amendment_not_in_ledger"]
    print(f"RECALL: changes naming a 2022-2026 Act not in the ledger: {len(recall)}")
    for r in recall:
        print(f"  {r[0]} s.{r[1]} {r[2]}: {r[4]}")
    counts = (count_table(res["counts"]) + "\n\ns.2 effects per clause:\n" + s2_table(res["effects"]) + "\n\n"
              + crosscheck_counts(res["ev"], res["ch"]) + "\n")
    se._write_new(out_dir / "COUNTS.txt", counts)
    print(counts, end="")
    print(f"s.56 ita1961_2023: {res['s56']}")
    print("whole-section insertions (Act text vs first edition text):")
    for x in res["ins_check"]:
        print(f"  {x}")
    print("sheets: " + ", ".join(str(f) for f in res["sheets"]))
    if a.propose:
        path, msg = ap.write_never_overwrite(VERSIONS_PATH, res["versions"], VERSION_COLUMNS, "record_key",
                                             owner=VERSION_OWNER, carry=owner_value)
        print("\n".join(msg))
    if a.check_effects:
        if not res["checks"]:
            print("--check-effects: the ledger has no position column (run act_parse --ledger first)")
            return 1
        rows = [dict(e, check_status=res["checks"][e["effect_id"]][0], check_note=res["checks"][e["effect_id"]][1])
                for e in res["effects"]]
        tally = {}
        for r in rows:
            n = r["check_note"].split(":")[0] if r["check_status"] == "no_edition" else r["check_status"]
            tally[n] = tally.get(n, 0) + 1
        print("check: " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
        path, msg = ap.write_never_overwrite(ap.EFFECTS_PATH, rows, ap.EFFECT_COLUMNS, "effect_id")
        print("\n".join(msg))
    return 0


# Audited Part A compatibility path; v3 policies are applied separately below.
_V3_STATE = {}
_V3_RESULTS = {}


class V3Stop(ValueError):
    pass


def _v3_legacy_canonical(text, se):
    return ' '.join(se.fold_for_diff(text).replace('[', '').replace(']', '').split())


def _v3_legacy_literal_word_hits(text, phrase):
    if not phrase:
        return []
    pieces = []
    for index, char in enumerate(phrase):
        if char.isspace():
            previous = phrase[index - 1] if index else ''
            following = phrase[index + 1] if index + 1 < len(phrase) else ''
            optional = previous and (not previous.isalnum()) or (following and (not following.isalnum()))
            pieces.append('\\s*' if optional else '\\s+')
        elif not char.isalnum():
            pieces.append(('\\s*' if index else '') + re.escape(char) + ('\\s*' if index + 1 < len(phrase) else ''))
        else:
            pieces.append(re.escape(char))
    pattern = ''.join(pieces)
    if phrase[0].isalnum():
        pattern = '(?<![A-Za-z0-9])' + pattern
    if phrase[-1].isalnum():
        pattern += '(?![A-Za-z0-9])'
    return list(re.finditer(pattern, text))


def _v3_legacy_clean_block(block, se):
    block = _v3_legacy_canonical(block, se).strip()
    opening = block[:1]
    if opening in {'"', "'"}:
        block = block[1:]
        block = re.sub(re.escape(opening) + '[;.]?$', '', block)
    return block.strip()


def _v3_legacy_label_span(text, label, ap, sb, leaf=True):  # noqa: C901
    matches = list(sb._bound(sb._paren(label)).finditer(text))
    if not matches and re.match('^\\s*\\(\\s*\\d+[A-Za-z]*\\s*\\)', text):
        matches = list(re.finditer('(?<=\\))\\s*' + sb._paren(label), text))
    literals = list(re.finditer(sb._paren(label), text))
    if not matches and len(literals) == 1:
        candidate = literals[0]
        prefix = text[max(0, candidate.start() - 40):candidate.start()]
        if not re.search('(?:sub-section|sub-clause|section|clause|item|paragraph)\\s*$', prefix, re.I):
            matches = literals
    if len(matches) != 1:
        _V3_STATE[
            'last_locator_counts'
        ] = {
            'label': '(' + label + ')',
            'heading_matches': len(
                matches
            ),
            'literal_matches': len(
                literals
            ),
            'container_chars': len(
                text
            )
        }
        return None
    match = matches[0]
    label_match = re.search(sb._paren(label), text[match.start():match.end()])
    start = match.start() + label_match.start()
    successor_matches = []
    for successor in ap.successors(label):
        if successor == label:
            continue
        successor_matches.extend(sb._bound(sb._paren(successor)).finditer(text, match.end()))
    end = min((m.start() for m in successor_matches), default=len(text))
    if not label[0].isdigit():
        roots = list(sb._bound('\\(\\s*(\\d{1,3}[A-Za-z]*)\\s*\\)').finditer(text, 0, start))
        if roots:
            parent = max(roots, key=lambda m: (int(re.match('\\d+', m.group(1)).group()), m.start()))
            following = []
            for root_successor in ap.successors(parent.group(1)):
                following.extend(sb._bound(sb._paren(root_successor)).finditer(text, match.end(), end))
            if following:
                end = min(end, min((m.start() for m in following)))
    if leaf and (not label[0].isdigit()):
        semi = text.find(';', match.end(), end)
        if semi >= 0 and (not sb._bound('\\(\\s*[0-9A-Za-z]+\\s*\\)').search(text, match.end(), semi)):
            end = semi + 1
    return (start, end)


def _v3_legacy_effect_scope(text, effect, ap, sb):
    start, end = (0, len(text))
    levels = effect.get('target_unit', '').split(' > ')
    for level_index, level in enumerate(levels):
        labels = re.findall('\\(\\s*([0-9A-Za-z]+)\\s*\\)', level)
        if not labels:
            if re.match('Note\\s+\\d+', level):
                marker = re.search('Note\\s+(\\d+)', level).group(1)
                matches = list(re.finditer('\\bNote\\s*' + marker + '\\s*[.:\\u2014-]', text[start:end], re.I))
                if len(matches) != 1:
                    return None
                start += matches[0].start()
            continue
        segment = text[start:end]
        if ' and ' in level and len(labels) > 1:
            first, last = (
                _v3_legacy_label_span(
                    segment,
                    labels[
                        0
                    ],
                    ap,
                    sb
                ),
                _v3_legacy_label_span(
                    segment,
                    labels[
                        -1
                    ],
                    ap,
                    sb
                )
            )
            if first is None or last is None:
                return None
            end = start + last[1]
            start += first[0]
        else:
            for label_index, label in enumerate(labels):
                is_leaf = level_index == len(levels) - 1 and label_index == len(labels) - 1
                span = _v3_legacy_label_span(text[start:end], label, ap, sb, leaf=is_leaf)
                if span is None:
                    return None
                end = start + span[1]
                start += span[0]
    return (start, end)


def _v3_legacy_amendment_leaf(key, effect, pages, ap):
    match = re.match('s\\.(\\d+)((?:\\([0-9A-Za-z]+\\))*)$', effect['instrument_provision'])
    if not match:
        raise V3Stop('Amendment provision locator unsupported: ' + effect['effect_id'])
    number = int(match.group(1))
    path = re.findall('\\(([0-9A-Za-z]+)\\)', match.group(2))
    items = ap.split_items(ap.clean_instrument(pages).lines)
    roots = [ap.build_tree(n, lines) for n, lines in items if n == number]
    if len(roots) != 1:
        raise V3Stop('Amending Act item locator differs: ' + effect['effect_id'])
    leaves = [leaf for leaf in ap.leaves(roots[0]) if leaf.path() == path]
    if len(leaves) != 1:
        raise V3Stop('Amending Act leaf locator differs: ' + effect['effect_id'])
    return leaves[0]


def _v3_legacy_primary_block_scope(  # noqa: C901
        before, latest, block, effect, se, ap, sb, witness_source='primary_act_replacement'):
    (
        'Use the primary replacement block as an exact normalized-word witness.'
        '\n\n    The edition locates the primary block; unchanged-word alignment '
        'locates its\n    old Gazette boundary. No edition wording is copied int'
        'o the replacement.\n    '
    )

    def words(text):
        return [(match, key) for match in re.finditer('\\S+', text) if (key := sb._alnum(match.group()))]
    old_words, new_words, block_words = (words(before), words(latest), words(block))
    keys = [key for _, key in block_words]
    if not keys or not old_words or (not new_words):
        return None
    new_keys = [key for _, key in new_words]
    new_stream, block_stream = (''.join(new_keys), ''.join(keys))
    starts = [m.start() for m in re.finditer(re.escape(block_stream), new_stream)]
    witness = {
        'effect_id': effect[
            'effect_id'
        ],
        'primary_block_chars': len(
            block
        ),
        'normalized_block_chars': len(
            block_stream
        ),
        'new_edition_matches': len(
            starts
        ),
        'locator_source': witness_source
    }
    _V3_RESULTS.setdefault('A3_primary_block_witnesses', []).append(witness)
    if len(starts) != 1:
        return None
    cumulative = [0]
    for key in new_keys:
        cumulative.append(cumulative[-1] + len(key))
    first = bisect.bisect_right(cumulative, starts[0]) - 1
    last = bisect.bisect_left(cumulative, starts[0] + len(block_stream))
    opcodes = sb.difflib.SequenceMatcher(None, [key for _, key in old_words], new_keys, autojunk=False).get_opcodes()

    def project(index, right):
        for tag, a1, a2, b1, b2 in opcodes:
            if b1 <= index <= b2 and b1 != b2:
                if tag == 'equal':
                    return a1 + index - b1
                if index == b1:
                    return a1
                if index == b2:
                    return a2
                return a2 if right else a1
        return len(old_words) if index == len(new_words) else None
    left_index, right_index = (project(first, False), project(last, True))
    if left_index is None or right_index is None or left_index > right_index:
        return None
    left = old_words[left_index][0].start() if left_index < len(old_words) else len(before)
    right = old_words[right_index][0].start() if right_index < len(old_words) else len(before)
    if effect['operation'] == 'insert' and effect['scope'] == 'unit':
        if left != right:
            return None
    elif left_index == right_index:
        return None
    else:
        label = re.match('\\(\\s*([0-9A-Za-z]+)\\s*\\)', block)
        if label and effect['scope'] == 'unit':
            candidates = list(re.finditer(sb._paren(label.group(1)), before[left:right]))
            if len(candidates) != 1:
                witness['projected_old_label_count'] = len(candidates)
                return None
            left += candidates[0].start()
        elif effect['scope'] == 'unit' and old_words[left_index][1] != keys[0]:
            return None
    levels = effect['target_unit'].split(' > ')
    if levels and re.search('\\(\\d', levels[0]):
        parent = _v3_legacy_effect_scope(before, dict(effect, target_unit=levels[0]), ap, sb)
        if parent is None:
            witness['numeric_parent_check'] = (
                'nested number labels ambiguous; unique full-text witness and old-label/old-'
                'word verification required'
            )
        elif left < parent[0] or right > parent[1]:
            return None
    return (left, right)


def _v3_legacy_apply_effect(text, effect, leaf, se, ap, sb, scope_override=None, retain_long_line=False):  # noqa: C901
    own = _v3_legacy_canonical(leaf.own_text(), se)
    operation = effect['operation']
    block = _v3_legacy_clean_block(leaf.block_text(), se)
    quoted = re.findall('"([^\\"]*)"', own)
    scope = scope_override if scope_override is not None else _v3_legacy_effect_scope(text, effect, ap, sb)
    if scope is None and effect['scope'] == 'words' and (len(quoted) >= 2):
        levels = effect['target_unit'].split(' > ')
        for count in range(len(levels) - 1, -1, -1):
            parent = _v3_legacy_effect_scope(text, dict(effect, target_unit=' > '.join(levels[:count])), ap, sb)
            if parent is not None and len(_v3_legacy_literal_word_hits(text[parent[0]:parent[1]], quoted[-2])) == 1:
                scope = parent
                break
    if scope is not None and operation == 'omit' and retain_long_line and (scope_override is None):
        left, right = scope
        segment = text[left:right]
        candidates = [
            m
            for m in re.finditer(
                '[,;]\\s*but\\b',
                segment,
                re.I
            )
            if re.search(
                sb._paren(
                    'i'
                ),
                segment[
                    m.end(

                    ):
                ]
            )
            and re.search(
                sb._paren(
                    'v'
                ),
                segment[
                    m.end(

                    ):
                ]
            )
        ]
        _V3_RESULTS[
            'A3_unlabelled_tail_boundary'
        ] = {
            'effect_id': effect[
                'effect_id'
            ],
            'candidate_count': len(
                candidates
            ),
            'original_scope_chars': len(
                segment
            )
        }
        if len(candidates) != 1:
            raise V3Stop('A3 omitted leaf / unlabelled tail boundary is not unique: ' + effect['effect_id'])
        scope = (left, left + candidates[0].start())
        _V3_RESULTS['A3_unlabelled_tail_boundary']['retained_tail_chars'] = right - scope[1]
    if scope is None:
        _V3_RESULTS[
            'A3_locator_stop'
        ] = {
            'effect_id': effect[
                'effect_id'
            ],
            'target_unit': effect[
                'target_unit'
            ],
            'counts': _V3_STATE.get(
                'last_locator_counts',
                {

                }
            )
        }
        raise V3Stop('A3 amendment target cannot be located uniquely: ' + effect['effect_id'])
    start, end = scope
    segment = text[start:end]
    if effect['scope'] == 'words':
        if len(quoted) < 2:
            raise V3Stop('A3 amendment words parser lacks anchor/replacement: ' + effect['effect_id'])
        old, new = quoted[-2:]
        old_hits = _v3_legacy_literal_word_hits(segment, old)
        if len(old_hits) != 1:
            raise V3Stop('A3 amendment word anchor is not unique: ' + effect['effect_id'])
        at = old_hits[0]
        if operation == 'substitute':
            changed = segment[:at.start()] + new + segment[at.end():]
        elif operation == 'insert':
            replacement = old + ' ' + new if effect['position'] == 'after' else new + ' ' + old
            changed = segment[:at.start()] + replacement + segment[at.end():]
        elif operation == 'omit':
            changed = segment[:at.start()] + segment[at.end():]
        else:
            raise V3Stop('A3 unsupported word operation: ' + effect['effect_id'])
    elif operation == 'substitute' and block:
        if not effect['target_unit']:
            block = re.sub('^\\s*' + re.escape(effect['target_section']) + '\\s*\\.\\s*', '', block)
        changed = block
    elif operation == 'omit':
        changed = ''
    elif operation == 'insert' and block:
        changed = segment + ' ' + block if effect['position'] == 'after' else block + ' ' + segment
    elif operation == 'renumber':
        match = re.search('renumbered\\s+as\\s+(?:sub-section|clause)\\s*((?:\\([0-9A-Za-z]+\\)\\s*)+)', own)
        current = re.match('\\([0-9A-Za-z]+\\)', segment)
        if match is None or current is None:
            raise V3Stop('A3 renumber parser incomplete: ' + effect['effect_id'])
        changed = match.group(1).strip() + segment[current.end():]
    else:
        raise V3Stop('A3 unsupported unit operation: ' + effect['effect_id'])
    return _v3_legacy_canonical(text[:start] + ' ' + changed + ' ' + text[end:], se)


def _v3_legacy_probe_a3(raw, effects, parsed, items, baseline, gi, sect, se, ss, sb, ap, policy=None):  # noqa: C901
    corrected = {}
    origins = {}
    correction_stats = []
    for sec, bound in baseline['bounds'].items():
        span = gi['lines'][bound['start']:bound['end']]
        furniture = _v3_furniture_rows(span) if policy and policy['R4'] else set()
        chunks, positions = ([], [])
        for line in span:
            if (line.page, line.line) in furniture:
                continue
            chunk = _v3_legacy_canonical(line.text, se)
            if not chunk:
                continue
            location = (int(line.printed or line.page), line.line)
            if chunks:
                positions.append(location)
            chunks.append(chunk)
            positions.extend([location] * len(chunk))
        text = ' '.join(chunks)
        lead = re.match('^\\s*' + re.escape(sec) + '\\s*\\.\\s*', text)
        skip = lead.end() if lead else 0
        corrected[sec] = text[skip:]
        origins[sec] = positions[skip:]
        if policy and policy['R1']:
            corrected[sec], origins[sec] = _v3_margin(corrected[sec], origins[sec], policy['headings'])
    for item in items:
        if item['act'] != '2025':
            continue
        sec = item['section']
        old, new = (_v3_legacy_canonical(item['for'], se), _v3_legacy_canonical(item['read'], se))
        hits = [m.start() for m in _v3_legacy_literal_word_hits(corrected[sec], old)]
        page_hits = [hit for hit in hits if origins[sec][hit][0] == int(item['gazette_page'])]
        selection = 'unique on referenced Gazette page'
        if len(page_hits) > 1:
            numbers = [int(n) for n in re.findall('\\d+', item['gazette_lines'])]
            target_lines = range(min(numbers), max(numbers) + 1)
            distances = [(min((abs(origins[sec][hit][1] - n) for n in target_lines)), hit) for hit in page_hits]
            distances.sort()
            if distances[0][0] <= 3 and distances[0][0] < distances[1][0]:
                page_hits = [distances[0][1]]
                selection = 'unique nearest referenced Gazette line; raw-line delta=' + str(distances[0][0])
        if len(page_hits) == 1:
            at = page_hits[0]
            location = origins[sec][at]
            corrected[sec] = corrected[sec][:at] + new + corrected[sec][at + len(old):]
            origins[sec][at:at + len(old)] = [location] * len(new)
            outcome = 'applied'
        elif not hits and new in corrected[sec]:
            outcome = 'already_new'
        else:
            _V3_RESULTS[
                'A3_corrigendum_location_stop'
            ] = {
                'item_key': item[
                    'item_key'
                ],
                'section_old_occurrences': len(
                    hits
                ),
                'referenced_page_old_occurrences': len(
                    page_hits
                ),
                'section_new_occurrences': corrected[
                    sec
                ].count(
                    new
                )
            }
            raise V3Stop('A3 corrigendum target not unique/present: ' + item['item_key'])
        correction_stats.append({'item_key': item['item_key'], 'outcome': outcome, 'selection': selection})
    _V3_RESULTS['A3_corrigendum_application'] = correction_stats
    effect_stats = []
    _V3_RESULTS['A3_amendment_application'] = effect_stats
    current_view = se.edition_view(raw, 'ita2025_2026')
    current_convention = se.convention_note(current_view.pages)
    apparatus_cache = {}
    for effect in effects:
        prefix = effect['effect_id'].split(':', 1)[0]
        if effect['target_act'] != '2025' or prefix not in {'fa_2026', 'tola_2026', 'tola_2026_gz'}:
            continue
        source = parsed.get(prefix)
        if source is None:
            source = parsed.get('tola_2026_gz') if prefix == 'tola_2026' else None
        if source is None:
            raise V3Stop('A3 missing parsed primary amendment: ' + effect['effect_id'])
        reviews = [rv for rv in source['review'] if rv['effect_id'] == effect['effect_id']]
        if len(reviews) != 1 or ap.quote_sha256(reviews[0]['quote']) != effect['quote_sha256']:
            raise V3Stop('A3 ledger quote hash differs: ' + effect['effect_id'])
        folder, name = ss.INSTRUMENTS[source['key']][:2]
        pages = ss.pdf_pages(se.RAW_DIR / folder / name)
        leaf = _v3_legacy_amendment_leaf(source['key'], effect, pages, ap)
        sec = effect['target_section']
        before = corrected[sec]
        scope_override, boundary_evidence = (None, '')
        block = _v3_legacy_clean_block(leaf.block_text(), se)
        if effect['scope'] == 'words':
            quotes = re.findall('"([^\\"]*)"', _v3_legacy_canonical(leaf.own_text(), se))
            if len(quotes) >= 2:
                old_key, new_key = (sb._alnum(quotes[-2]), sb._alnum(quotes[-1]))
                if sec not in apparatus_cache:
                    apparatus_cache[sec] = se.section_apparatus(current_view, sect('ita2025_2026', sec), current_convention)
                located = {}
                unit_labels = set(re.findall('\\(\\s*([0-9A-Za-z]+)\\s*\\)', effect['target_unit']))
                note_labels = set(re.findall('Note\\s+(\\d+)', effect['target_unit']))
                for entry in apparatus_cache[sec]:
                    if entry.get('act_key') != effect['act_key'] or entry.get('span_class') != 'amendment':
                        continue
                    locator_span = _v3_legacy_canonical(entry.get('cmp_span') or entry.get('span_text') or '', se)
                    span_key = sb._alnum(locator_span)
                    old_meta_key = sb._alnum(_v3_legacy_canonical(entry.get('old_text') or '', se))
                    first_label = re.match('\\s*["\\\']?\\s*\\(\\s*([0-9A-Za-z]+)\\s*\\)', locator_span)
                    first_note = re.match('\\s*Note\\s*(\\d+)', locator_span)
                    ancestor_span = first_label is not None and first_label.group(
                        1
                    ) in unit_labels or (
                        first_note is not None
                        and first_note.group(
                            1
                        ) in note_labels
                    )
                    containing_span = bool(new_key) and span_key.count(new_key) == 1 and ancestor_span
                    if span_key != new_key and (not old_key or old_meta_key != old_key) and (not containing_span):
                        continue
                    location = f"ita2025_2026:p{entry['page_1based']}l{entry['line_1based']}"
                    if containing_span:
                        projected = _v3_legacy_primary_block_scope(
                            before,
                            _v3_legacy_canonical(
                                sect(
                                    'ita2025_2026',
                                    sec
                                )[
                                    'body'
                                ],
                                se
                            ),
                            locator_span,
                            effect,
                            se,
                            ap,
                            sb,
                            'C3 linked ancestor body span; location only; ' + location
                        )
                        if projected is not None and len(
                            _v3_legacy_literal_word_hits(
                                before[
                                    projected[
                                        0
                                    ]:projected[
                                        1
                                    ]
                                ],
                                quotes[
                                    -2
                                ]
                            )
                        ) == 1:
                            located[projected] = location
                            continue
                    indices = [
                        i
                        for i,
                        line in enumerate(
                            current_view.cleaned.lines
                        )
                        if line.page == entry[
                            'page_1based'
                        ]
                        and line.line_no == entry[
                            'line_1based'
                        ]
                    ]
                    if len(indices) != 1:
                        continue
                    current_result = sect('ita2025_2026', sec)
                    for width in (0, 1, 2):
                        lo = max(current_result['internal_heading_line_idx0'], indices[0] - width)
                        hi = min(current_result['internal_line_idx0_end'], indices[0] + width + 1)
                        context = _v3_legacy_canonical(
                            se.fold_plain(
                                ' '.join(
                                    (
                                        line.text
                                        for line in current_view.cleaned.lines[
                                            lo:hi
                                        ]
                                    )
                                )
                            ),
                            se
                        )
                        location = f"ita2025_2026:p{entry['page_1based']}l{entry['line_1based']}"
                        projected = _v3_legacy_primary_block_scope(
                            before,
                            _v3_legacy_canonical(
                                current_result[
                                    'body'
                                ],
                                se
                            ),
                            context,
                            effect,
                            se,
                            ap,
                            sb,
                            'C3 linked printed-line context; location only; ' + location
                        )
                        if projected is not None and len(
                            _v3_legacy_literal_word_hits(
                                before[
                                    projected[
                                        0
                                    ]:projected[
                                        1
                                    ]
                                ],
                                quotes[
                                    -2
                                ]
                            )
                        ) == 1:
                            located[projected] = location
                            break
                _V3_RESULTS.setdefault(
                    'A3_word_locator_counts',
                    [

                    ]
                ).append(
                    {
                        'effect_id': effect[
                            'effect_id'
                        ],
                        'distinct_Gazette_boundaries': len(
                            located
                        )
                    }
                )
                if len(located) == 1:
                    scope_override, location = next(iter(located.items()))
                    boundary_evidence = (
                        'C3 linked printed-line context locates Gazette old words uniquely; all new '
                        'words from primary Act; '
                    ) + location
        if effect['scope'] == 'unit' and effect['operation'] in {'substitute', 'insert'} and block and effect['target_unit']:
            scope_override = _v3_legacy_primary_block_scope(
                before,
                _v3_legacy_canonical(
                    sect(
                        'ita2025_2026',
                        sec
                    )[
                        'body'
                    ],
                    se
                ),
                block,
                effect,
                se,
                ap,
                sb
            )
            if scope_override is not None:
                boundary_evidence = (
                    'primary replacement block uniquely matched in ITD; Gazette boundary aligned'
                    ' and label/parent checked; source words copied only from primary Act'
                )
            else:
                wanted = re.match('\\(\\s*([0-9A-Za-z]+)\\s*\\)', block)
                if wanted:
                    if sec not in apparatus_cache:
                        apparatus_cache[
                            sec
                        ] = se.section_apparatus(
                            current_view,
                            sect(
                                'ita2025_2026',
                                sec
                            ),
                            current_convention
                        )
                    candidates = {}
                    linked_count = 0
                    for entry in apparatus_cache[sec]:
                        if entry.get('act_key') != effect['act_key'] or entry.get('span_class') != 'amendment':
                            continue
                        locator = _v3_legacy_canonical(entry.get('cmp_span') or entry.get('span_text') or '', se)
                        label = re.match('\\s*["\\\']?\\s*\\(\\s*([0-9A-Za-z]+)\\s*\\)', locator)
                        if label is None or label.group(1) != wanted.group(1):
                            continue
                        linked_count += 1
                        location = f"ita2025_2026:p{entry['page_1based']}l{entry['line_1based']}"
                        projected = _v3_legacy_primary_block_scope(
                            before,
                            _v3_legacy_canonical(
                                sect(
                                    'ita2025_2026',
                                    sec
                                )[
                                    'body'
                                ],
                                se
                            ),
                            locator,
                            effect,
                            se,
                            ap,
                            sb,
                            'printed amendment span; location only; ' + location
                        )
                        if projected is not None:
                            candidates[projected] = location
                    _V3_RESULTS.setdefault(
                        'A3_apparatus_locator_counts',
                        [

                        ]
                    ).append(
                        {
                            'effect_id': effect[
                                'effect_id'
                            ],
                            'label': '(' + wanted.group(
                                1
                            ) + ')',
                            'linked_printed_spans': linked_count,
                            'distinct_Gazette_boundaries': len(
                                candidates
                            )
                        }
                    )
                    if len(candidates) == 1:
                        scope_override, location = next(iter(candidates.items()))
                        boundary_evidence = (
                            'C3 printed-body amendment span linked to the registered Act; location only;'
                            ' primary Act supplies all replacement words; '
                        ) + location
        if effect['operation'] == 'omit' and effect['scope'] == 'unit':
            levels = effect['target_unit'].split(' > ')
            labels = re.findall('\\(\\s*([0-9A-Za-z]+)\\s*\\)', levels[-1])
            if len(labels) == 1:
                parent_effect = dict(effect, target_unit=' > '.join(levels[:-1]))
                parent_scope = _v3_legacy_effect_scope(before, parent_effect, ap, sb)
                old_edition = before
                new_edition = _v3_legacy_canonical(sect('ita2025_2026', sec)['body'], se)
                hints = []
                for hunk in sb.word_hunks(old_edition, new_edition):
                    if sb._alnum(hunk['new']):
                        continue
                    marker = re.search(sb._paren(labels[0]), hunk['old'])
                    if marker is None or parent_scope is None:
                        continue
                    fragment = hunk['old'][marker.start():]
                    left, right = parent_scope
                    hay = before[left:right]
                    if hay.count(fragment) == 1:
                        start = left + hay.index(fragment)
                        hints.append(((start, start + len(fragment)), hunk['key']))
                if len(hints) == 1:
                    scope_override, key = hints[0]
                    boundary_evidence = (
                        'Gazette-to-edition deletion boundary witness; exact Gazette match; primary '
                        'omission instruction; hunk='
                    ) + key
        parent_unit = ' > '.join(effect['target_unit'].split(' > ')[:-1])
        retain_long_line = effect[
            'operation'
        ] == 'omit' and effect[
            'scope'
        ] == 'unit' and any(
            (
                other[
                    'target_act'
                ] == effect[
                    'target_act'
                ]
                and other[
                    'target_section'
                ] == sec
                and other[
                    'target_unit'
                ].startswith(
                    parent_unit + ' > long line['
                )
                for other in effects
            )
        )
        if policy and policy['R3']:
            unique, failure = _v3_validated_scope(before, effect, scope_override)
            if unique is None:
                policy['unanchored'].append({'effect_id': effect['effect_id'], 'reason': failure})
                continue
            if effect['scope'] == 'words':
                words = re.findall('"([^"]*)"', _v3_legacy_canonical(leaf.own_text(), se))
                if len(words) < 2 or len(_v3_legacy_literal_word_hits(before[unique[0]:unique[1]], words[-2])) != 1:
                    policy['unanchored'].append({'effect_id': effect['effect_id'], 'reason': 'word_anchor_not_unique'})
                    continue
            if scope_override is not None:
                policy.setdefault('scoped_witnesses', []).append({
                    'effect_id': effect['effect_id'], 'span': list(unique), 'source': boundary_evidence})
        corrected[sec] = _v3_legacy_apply_effect(before, effect, leaf, se, ap, sb, scope_override, retain_long_line)
        effect_stats.append(
            {
                'effect_id': effect[
                    'effect_id'
                ],
                'applied': corrected[
                    sec
                ] != before,
                'boundary_evidence': boundary_evidence
                or 'primary ledger hierarchy and unit boundaries',
                'before_chars': len(
                    before
                ),
                'after_chars': len(
                    corrected[
                        sec
                    ]
                ),
                'before_sha16': _v3_legacy_hash16(
                    before
                ),
                'after_sha16': _v3_legacy_hash16(
                    corrected[
                        sec
                    ]
                )
            }
        )
        print('A3 applied ' + effect['effect_id'] + '; changed_chars=' + str(len(corrected[sec]) - len(before)), flush=True)
    rows = []
    per_section = {}
    for sec in ap.SPINE['2025']:
        result = sect('ita2025_2026', sec)
        if result['status'] != 'FOUND':
            raise V3Stop('A3 current edition section not found: ' + sec)
        differences = []
        entries = _v3_compare_section(corrected[sec], result, sec, view=current_view,
                                      furniture=bool(policy and policy['R4']), markup=bool(policy and policy['R5']))
        for entry in entries:
            hunk = entry['hunk']
            proposed = 'unexplained'
            row_kind = 'word' if hunk['old'] and hunk['new'] else 'missing'
            row = {
                'section': sec,
                'location_sha16': hunk[
                    'key'
                ],
                'kind': row_kind,
                'proposed_class': proposed,
                'evidence_key': 'ita2025_gz+ita2025_2026',
                'owner_class': '',
                'owner_ok': '',
                'owner_note': ''
            }
            rows.append(row)
            differences.append(hunk)
        per_section[sec] = len(differences)
    reconciliation = Counter()
    for sec, hunks in baseline['content'].items():
        latest = _v3_legacy_canonical(sect('ita2025_2026', sec)['body'], se)
        for hunk in hunks:
            corr = [
                item
                for item in items
                if item[
                    'act'
                ] == '2025'
                and item[
                    'section'
                ] == sec
                and sb.corr_explains(
                    item,
                    hunk
                )
            ]
            if corr:
                classification = 'corrigendum'
            elif sb._alnum(
                hunk[
                    'old'
                ]
            ) and sb._alnum(
                hunk[
                    'old'
                ]
            ) in sb._alnum(
                latest
            ) and (
                sb._alnum(
                    hunk[
                        'new'
                    ]
                ) not in sb._alnum(
                    latest
                )
            ):
                classification = 'itd_error'
            elif sb.marks_only(hunk) or sb._alnum(hunk['old']) == sb._alnum(hunk['new']):
                classification = 'itd_editorial'
            else:
                classification = 'unexplained'
            reconciliation[classification] += 1
    _V3_RESULTS[
        'A3'
    ] = {
        'sections_compared': len(
            per_section
        ),
        'residual_rows': len(
            rows
        ),
        'residual_per_section': per_section,
        'residual_classes': dict(
            Counter(
                (
                    row[
                        'proposed_class'
                    ]
                    for row in rows
                )
            )
        ),
        'corrigendum_application': correction_stats,
        'amendment_application': effect_stats,
        'C3_reconciliation_total': sum(
            reconciliation.values(

            )
        ),
        'C3_reconciliation_classes': {
            name: reconciliation.get(
                name,
                0
            )
            for name in (
                'corrigendum',
                'amendment',
                'itd_editorial',
                'itd_error',
                'unexplained'
            )
        }
    }
    print(
        'A3 reconciliation/residual counts: ' + json.dumps(
            {
                k: _V3_RESULTS[
                    'A3'
                ][
                    k
                ]
                for k in (
                    'residual_rows',
                    'residual_per_section',
                    'C3_reconciliation_total',
                    'C3_reconciliation_classes'
                )
            }
        ),
        flush=True
    )
    return (rows, corrected)


V3_COLUMNS = [
    'row_id',
    'section',
    'location_sha16',
    'kind',
    'status',
    'rule',
    'origin',
    'nature',
    'image_on_page',
    'evidence_key',
    'owner_ok',
    'owner_note'
]
V3_IRREGULAR = {'index': 'indices', 'analysis': 'analyses', 'basis': 'bases', 'child': 'children', 'person': 'people'}
V3_NUMBER_WORDS = set((
        'zero one two three four five six seven eight nine ten eleven twelve thirtee'
        'n fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty '
        'fifty sixty seventy eighty ninety hundred thousand million billion first se'
        'cond third fourth fifth sixth seventh eighth ninth tenth'
    ).split())
V3_RULES = {
    'R1': (
        'Remove exact derived headings only as complete sentences; preserve embedded'
        ' words.'
    ),
    'R2': (
        'assent <= knowledge AND wef <= first 1 April on or after knowledge; otherwi'
        'se deferred.'
    ),
    'R3': (
        'Require unique target unit and word anchor; otherwise unanchored and do not'
        ' apply.'
    ),
    'R4': (
        'Remove complete column-header rows and page-break furniture only.'
    ),
    'R5': (
        'Ignore ITD square brackets, omission markers, and inline (N of YYYY) refere'
        'nces.'
    ),
    'R6': (
        'Image-XObject evidence for Gazette-only missing text; never removes a row.'
    ),
    'plural': (
        'Alphabetic nonnumeric +s, s/x/z/ch/sh +es, consonant-y to ies; fixed irregu'
        'lar map.'
    ),
    'nature': (
        'Only certified spelling/plural, punctuation, labels, markup, Act-reference '
        'or missing-formula+image differences are accidental; otherwise proposed sub'
        'stantive.'
    ),
}


def v3_first_april(knowledge):
    point = date.fromisoformat(knowledge)
    current = date(point.year, 4, 1)
    return current if current >= point else date(point.year + 1, 4, 1)


def v3_effect_in_date(effect, knowledge):
    cutoff = v3_first_april(knowledge)
    return date.fromisoformat(
        effect[
            'assent_date'
        ]
    ) <= date.fromisoformat(
        knowledge
    ) and date.fromisoformat(
        effect[
            'wef'
        ]
    ) <= cutoff


def v3_plural(a, b):
    a, b = (a.casefold(), b.casefold())
    if not a.isalpha() or not b.isalpha() or a in V3_NUMBER_WORDS or (b in V3_NUMBER_WORDS):
        return False
    for singular, plural in ((a, b), (b, a)):
        if V3_IRREGULAR.get(singular) == plural:
            return True
        if singular.endswith('y') and len(singular) > 1 and (singular[-2] not in 'aeiou'):
            if singular[:-1] + 'ies' == plural:
                return True
        elif singular.endswith(('s', 'x', 'z', 'ch', 'sh')):
            if singular + 'es' == plural:
                return True
        elif singular + 's' == plural:
            return True
    return False


def v3_itd_markup(text):
    text = re.sub('\\[\\s*\\*{3}\\s*\\]', '', text)
    text = re.sub('\\(\\s*\\d+\\s+of\\s+\\d{4}\\s*\\)', '', text)
    return ' '.join(text.replace('[', '').replace(']', '').split())


def _v3_margin(text, origins, headings):
    spans = []
    for heading in headings:
        heading = heading.rstrip('.!?')
        if not heading:
            continue
        for match in re.finditer(re.escape(heading), text):
            left, right = (text[:match.start()].rstrip(), text[match.end():].lstrip())
            if (not left or left[-1] in '.!?') and (not right or right[0] in '.!?'):
                end = match.end()
                if right:
                    end += len(text[match.end():]) - len(right) + 1
                spans.append((match.start(), end))
    removed = set((i for a, b in spans for i in range(a, b)))
    chars = [(c, origins[i]) for i, c in enumerate(text) if i not in removed]
    output, locations = ([], [])
    for c, location in chars:
        if c.isspace():
            if output and output[-1] != ' ':
                output.append(' ')
                locations.append(location)
        else:
            output.append(c)
            locations.append(location)
    if output and output[-1] == ' ':
        output.pop()
        locations.pop()
    return (''.join(output), locations)


def _v3_furniture_rows(lines):
    result = set()
    for i, line in enumerate(lines):
        value = ' '.join(line.text.split())
        if TABLE_FURNITURE_RE.fullmatch(value):
            result.add(_v3_line_key(line))
        elif re.fullmatch('[A-E]', value):
            adjacent = [lines[j].text.strip() for j in (i - 1, i + 1) if 0 <= j < len(lines)]
            if any((re.fullmatch('[A-E]', other) and other != value for other in adjacent)):
                result.add(_v3_line_key(line))
    return result


def _v3_line_key(line):
    return line.page, getattr(line, 'line', getattr(line, 'line_no', None))


def _v3_validated_scope(text, effect, override):
    """Use the earlier validated primary-text witness; reject conflicting bounds."""
    generic = _v3_legacy_effect_scope(text, effect, ap, sys.modules[__name__])
    if override is None:
        return generic, '' if generic is not None else 'target_not_unique'
    a, b = override
    if not 0 <= a <= b <= len(text):
        return None, 'invalid_scoped_witness'
    if generic is not None:
        c, d = generic
        if not (c <= a <= b <= d or a <= c <= d <= b):
            return None, 'scope_conflict'
    return override, ''


def v3_image_on_page(page):

    def images(resources, seen):
        if resources is None:
            return False
        resources = resources.get_object()
        objects = resources.get('/XObject', {})
        objects = objects.get_object() if hasattr(objects, 'get_object') else objects
        for reference in objects.values():
            obj = reference.get_object()
            if id(obj) in seen:
                continue
            seen.add(id(obj))
            if obj.get('/Subtype') == '/Image':
                return True
            if obj.get('/Subtype') == '/Form' and images(obj.get('/Resources'), seen):
                return True
        return False
    return images(page.get('/Resources'), set())


def v3_nature(hunk, *, image=False, spelling_pairs=()):
    old, new = (hunk['old'], hunk['new'])
    if _alnum(old) == _alnum(new):
        return ('accidental', 'punctuation_or_markup')
    if v3_itd_markup(old) == v3_itd_markup(new):
        return ('accidental', 'markup_or_act_reference')
    if re.fullmatch('(?:\\(?[A-Za-z0-9]+\\)[.]?|\\d+[.])', old) and re.fullmatch('(?:\\(?[A-Za-z0-9]+\\)[.]?|\\d+[.])', new):
        return ('accidental', 'unit_label')
    a, b = (old.split(), new.split())
    if len(a) == len(b):
        changed = [(x, y) for x, y in zip(a, b) if x != y]
        if changed and all((v3_plural(x, y) for x, y in changed)):
            return ('accidental', 'regular_or_irregular_plural')
        if changed and all(((x, y) in spelling_pairs or (y, x) in spelling_pairs for x, y in changed)):
            return ('accidental', 'certified_spelling')
    formula = (
        '\\s*\\(?\\s*(?:[A-Za-z]|\\d+(?:[.]\\d+)?)\\s*(?:[-+=*/\\u2212\\u00d7\\u00f7]\\s*\\(?\\s'
        '*(?:[A-Za-z]|\\d+(?:[.]\\d+)?)\\s*\\)?\\s*)+'
    )
    if old and (not new) and image and re.fullmatch(formula, old):
        return ('accidental', 'missing_formula_with_image')
    return ('substantive', 'no_accidental_certificate')


def _v3_section(view, number):
    result = se.extract_view(view, number)
    if result['status'] == 'UNRESOLVED' and (view.key, number) in OWNER_CHOICES:
        page = OWNER_CHOICES[view.key, number]['page']
        matches = [r for p, r in candidate_bodies(view, number) if p == page]
        if len(matches) == 1:
            return matches[0]
    if result['status'] != 'FOUND':
        raise V3Stop('section unresolved: ' + number)
    return result


def _v3_body(result, markup=False):
    words = se.fold_for_diff(result['body']).split()
    heading = se.fold_for_diff(result.get('heading') or '').split()
    text = ' '.join(words[len(heading):] if heading and words[:len(heading)] == heading else words)
    return v3_itd_markup(text) if markup else text


def _v3_word_span(roots, start, end, total):
    if start == end:
        point = roots[start][0] if start < len(roots) else total
        return point, point
    return min(x[0] for x in roots[start:end]), max(x[1] for x in roots[start:end])


def _v3_itd_prepared(result, view, furniture):
    """C3 preparation plus physical-row R4, retaining original ITD token coordinates."""
    original = _v3_body(result)
    words = original.split()
    roots = [(i, i + 1) for i in range(len(words))]
    if not furniture:
        return original, roots
    if view is None:
        raise V3Stop('R4 requires physical ITD lines')
    lines = view.cleaned.lines[result['internal_heading_line_idx0']:result['internal_line_idx0_end']]
    excluded = _v3_furniture_rows(lines)
    source, locations = [], []
    for line in lines:
        tokens = se.fold_for_diff(se.fold_plain(line.text)).split()
        source.extend(tokens)
        locations.extend([_v3_line_key(line)] * len(tokens))
    drop = set()
    for block in difflib.SequenceMatcher(None, source, words, autojunk=False).get_matching_blocks():
        drop.update(block.b + i for i in range(block.size) if locations[block.a + i] in excluded)
    kept = [i for i in range(len(words)) if i not in drop]
    return ' '.join(words[i] for i in kept), [roots[i] for i in kept]


def _v3_project_words(before, after, roots, total):
    mapped = []
    for op, a, b, c, d in difflib.SequenceMatcher(None, before.split(), after.split(), autojunk=False).get_opcodes():
        if op == 'equal':
            mapped.extend(roots[a:b])
        else:
            mapped.extend([_v3_word_span(roots, a, b, total)] * (d - c))
    return mapped


def _v3_classified_ops(old, new, section):
    operations = difflib.SequenceMatcher(None, old.split(), new.split(), autojunk=False).get_opcodes()
    hunks = iter(word_hunks(old, new))
    result = []
    for op in operations:
        if op[0] == 'equal':
            result.append((op, None, 'equal'))
        else:
            hunk = next(hunks)
            kind, _ = gazette_class(hunk, [], section, len(old.split()))
            result.append((op, hunk, kind))
    if next(hunks, None) is not None:
        raise V3Stop('word-hunk opcode mismatch')
    return result


def _v3_span_covered(span, intervals):
    cursor, end = span
    if cursor == end:
        return True
    for a, b in sorted(intervals):
        if b <= cursor:
            continue
        if a > cursor:
            return False
        cursor = max(cursor, b)
        if cursor >= end:
            return True
    return False


def _v3_occurrence_key(entry):
    hunk = entry['hunk']
    start = hunk.get('at', 0)
    old_span = entry.get('gazette_span', (start, start + len(hunk['old'].split())))
    identity = [entry['section'], list(old_span), list(entry['span']), hunk['key']]
    return hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()[:16]


def _v3_compare_section(old, result, section, *, view=None, furniture=False, markup=False):
    original_count = len(_v3_body(result).split())
    prepared, roots = _v3_itd_prepared(result, view, furniture)
    before = _v3_classified_ops(old, prepared, section)
    certified = [((op[1], op[2]), _v3_word_span(roots, op[3], op[4], original_count))
                 for op, _, kind in before if kind != 'content']
    classified = before
    if markup:
        normalized = v3_itd_markup(prepared)
        roots = _v3_project_words(prepared, normalized, roots, original_count)
        classified = _v3_classified_ops(old, normalized, section)
    entries = []
    for op, hunk, kind in classified:
        if kind != 'content':
            continue
        old_span = op[1], op[2]
        span = _v3_word_span(roots, op[3], op[4], original_count)
        if markup and _v3_span_covered(old_span, [a for a, _ in certified]) and _v3_span_covered(
                span, [b for _, b in certified]):
            continue
        entry = {'section': section, 'hunk': hunk, 'span': span, 'gazette_span': old_span}
        entry['occurrence_key'] = _v3_occurrence_key(entry)
        entries.append(entry)
    return entries


def _v3_hunks(corrected, sect, markup=False, furniture=False, view=None):
    return [entry for section in ap.SPINE['2025'] for entry in _v3_compare_section(
        corrected[section], sect('ita2025_2026', section), section,
        view=view, furniture=furniture, markup=markup)]


def _v3_editor_crosscheck(effect, result, apparatus=()):
    """Same target label plus effective-date evidence in a linked editor/footnote entry."""
    labels = re.findall('\\(([0-9A-Za-z]+)\\)', effect['target_unit'])
    notes = result.get('editor_notes', [])
    notes = [notes] if isinstance(notes, (str, dict)) else list(notes)
    notes += [entry for entry in apparatus if entry.get('act_key') == effect['act_key']]
    matched = []
    year, month, day = map(int, effect['wef'].split('-'))
    numeric = re.compile('(?<!\\d)' + str(day) + '\\s*-\\s*' + str(month) + '\\s*-\\s*' + str(year) + '(?!\\d)')
    for note in notes:
        text = note if isinstance(note, str) else ' '.join((str(v) for v in note.values() if isinstance(v, str)))
        date_matches = fn_date(text) == effect['wef'] or bool(numeric.search(text)) or effect['wef'] in text
        if date_matches and (not labels or any((re.search(_paren(label), text) for label in labels))):
            matched.append(note)
    return {
        'effect_id': effect[
            'effect_id'
        ],
        'wef': effect[
            'wef'
        ],
        'editor_note': 'yes'
        if matched else 'no',
        'agreement': bool(
            matched
        )
    }


def _v3_instruments():
    results = {}
    original = ap.run_ledger

    def collect(*args, **kwargs):
        value = original(*args, **kwargs)
        results.update({entry['key']: entry for entry in value[0]})
        return value
    ap.run_ledger = collect
    try:
        from divergence import statute_guard as guard
        built = build(se.latest_raw_dir(), se.CENSUS_DIR / 'partD', write=False)
        if len(built['body_sha']) != 26 or guard.body_sha(built['body_sha']) != guard.BODY_SHA256:
            raise V3Stop('body guard differs')
        if guard.code_sha(ap.read_csv(VERSIONS_PATH)) != guard.CODE_SHA256:
            raise V3Stop('code guard differs')
    finally:
        ap.run_ledger = original
    return (results, built)


def _v3_items(dispositions):
    by_key = {}
    for key in ('corr_ita2025_sep', 'corr_ita2025', 'corr_fa2023'):
        folder, name = ss.INSTRUMENTS[key][:2]
        for item in ss.corrigendum_items_v3(ss.pdf_pages(se.RAW_DIR / folder / name)):
            if not item['parsed']:
                raise V3Stop('unparsed corrigendum')
            ident = f"{key}:p{item['gazette_page']}l{item['gazette_lines']}"
            by_key[ident] = item
    result = []
    for row in dispositions:
        item = dict(
            by_key[
                row[
                    'item_key'
                ]
            ],
            item_key=row[
                'item_key'
            ],
            section=row[
                'section'
            ],
            unit=row[
                'unit'
            ],
            act='1961'
            if row[
                'item_key'
            ].startswith(
                'corr_fa2023:'
            ) else '2025'
        )
        if (_v3_legacy_hash16(item['for']), _v3_legacy_hash16(item['read'])) != (row['old_sha16'], row['new_sha16']):
            raise V3Stop('corrigendum phrase hash differs')
        result.append(item)
    return result


def _v3_related(a, b):
    """Compare exact source intervals in the unchanged ITD extraction, including gap anchors."""
    if a['section'] != b['section']:
        return False
    left, right = (a['span'], b['span'])
    if left[0] == left[1] or right[0] == right[1]:
        return left == right
    return max(left[0], right[0]) < min(left[1], right[1])


def _v3_mapped_pages(entry, sect, view):
    sec = entry['section']
    result = sect('ita2025_2026', sec)
    source, pages = ([], [])
    lines = view.cleaned.lines[result['internal_heading_line_idx0']:result['internal_line_idx0_end']]
    for line in lines:
        words = se.fold_for_diff(se.fold_plain(line.text)).split()
        source.extend(words)
        pages.extend([line.page] * len(words))
    target = _v3_body(result).split()
    mapped = [None] * len(target)
    for block in difflib.SequenceMatcher(None, source, target, autojunk=False).get_matching_blocks():
        for i in range(block.size):
            mapped[block.b + i] = pages[block.a + i]
    a, b = entry['span']
    selected = mapped[a:b] if b > a else mapped[max(0, a - 1):a + 1]
    found = sorted({p for p in selected if p is not None})
    if not found:
        raise V3Stop('missing row has no mapped ITD page')
    return found


def _v3_effect_witness(entry, witnesses):
    section, hunk = entry['section'], entry['hunk']
    for witness in witnesses:
        if witness['section'] != section:
            continue
        forward = {'for': witness['old'], 'read': witness['new']}
        backward = {'for': witness['new'], 'read': witness['old']}
        if corr_explains(forward, hunk) or corr_explains(backward, hunk):
            return witness['effect_id']
    return ''


def _v3_row_image(entry, sect, view, readers):
    hunk = entry['hunk']
    if not hunk['old'] or hunk['new']:
        return ''
    from pypdf import PdfReader
    pdf = se.latest_raw_dir() / 'ita2025_2026.pdf'
    if pdf not in readers:
        readers[pdf] = PdfReader(str(pdf))
    pages = _v3_mapped_pages(entry, sect, view)
    return 'yes' if any(v3_image_on_page(readers[pdf].pages[p - 1]) for p in pages) else 'no'


def _v3_make_row(entry, ident, key, items, sect, view, readers, witnesses, removed=''):
    hunk, section = entry['hunk'], entry['section']
    image = _v3_row_image(entry, sect, view, readers)
    spelling = [(i['for'], i['read']) for i in items if i['item_key'] == 'corr_fa2023:p29l1']
    nature, reason = v3_nature(hunk, image=image == 'yes', spelling_pairs=spelling)
    corr = next((i['item_key'] for i in items if i['section'] == section and corr_explains(i, hunk)), '')
    applied = _v3_effect_witness(entry, witnesses)
    origin = ('pipeline' if removed in {'R1', 'R2', 'R3', 'R4'}
              else 'instrument' if removed == 'R5' or corr or applied else 'itd')
    evidence = ('corr:' + corr if corr else 'effect:' + applied if applied else 'C3') + ';nature:' + reason
    value = dict(zip(V3_COLUMNS, [
        ident, section, key, 'word' if hunk['old'] and hunk['new'] else 'missing',
        'removed' if removed else 'kept', removed or 'none', origin, nature, image, evidence, '', '']))
    return value, reason


def _v3_merge_rows(entry, matches, items, sect, view, readers, witnesses):
    key = entry['hunk']['key']
    candidates = [_v3_make_row(e, 'v2:' + key, key, items, sect, view, readers, witnesses) for e in matches]
    value = dict(candidates[0][0])
    values = [v for v, _ in candidates]
    value['nature'] = 'substantive' if any(v['nature'] == 'substantive' for v in values) else 'accidental'
    value['origin'] = 'itd' if any(v['origin'] == 'itd' for v in values) else 'instrument'
    value['image_on_page'] = ('yes' if any(v['image_on_page'] == 'yes' for v in values)
                              else 'no' if any(v['image_on_page'] == 'no' for v in values) else '')
    value['evidence_key'] = ';'.join(sorted({v['evidence_key'] for v in values}))
    value['evidence_key'] += ';current:' + '|'.join(_v3_occurrence_key(e) for e in matches)
    return value, '|'.join(sorted({reason for _, reason in candidates}))


def _v3_removal_rule(entry, stages):
    for rule, entries in stages:
        if not any(_v3_related(entry, other) for other in entries):
            return rule
    raise V3Stop('baseline reconciliation failed')


def _v3_rows(baseline, stages, items, sect, view, effect_witnesses):
    final, readers = stages[-1][1], {}
    output, reasons, used, reconciliation = [], {}, set(), []
    final_keys = [_v3_occurrence_key(entry) for entry in final]
    if len(set(final_keys)) != len(final_keys):
        raise V3Stop('final occurrence keys are not unique')
    for entry in baseline:
        key = entry['hunk']['key']
        matches = [other for other in final if _v3_related(entry, other)]
        current = [_v3_occurrence_key(other) for other in matches]
        if matches:
            used.update(current)
            value, reason = _v3_merge_rows(entry, matches, items, sect, view, readers, effect_witnesses)
        else:
            value, reason = _v3_make_row(entry, 'v2:' + key, key, items, sect, view, readers,
                                         effect_witnesses, _v3_removal_rule(entry, stages))
        output.append(value)
        reasons[value['row_id']] = reason
        reconciliation.append({'row_id': value['row_id'], 'current_occurrences': current})
    for entry in final:
        key = _v3_occurrence_key(entry)
        if key not in used:
            value, reason = _v3_make_row(entry, 'v3:' + key, key, items, sect, view, readers, effect_witnesses)
            output.append(value)
            reasons[value['row_id']] = reason
            reconciliation.append({'row_id': value['row_id'], 'current_occurrences': [key]})
            used.add(key)
    if len({value['row_id'] for value in output}) != len(output) or used != set(final_keys):
        raise V3Stop('row identity or occurrence coverage differs')
    _V3_RESULTS['occurrence_reconciliation'] = {
        'rows': reconciliation, 'final_occurrences': len(final_keys),
        'covered_occurrences': len(used), 'all_covered': True}
    return output, reasons


def _v3_sections(raw):
    view_cache, section_cache = ({}, {})

    def sect(key, sec):
        if key not in view_cache:
            view_cache[key] = se.edition_view(raw, key)
        if (key, sec) not in section_cache:
            section_cache[key, sec] = _v3_section(view_cache[key], sec)
        return section_cache[key, sec]
    return (sect, view_cache)


def gazette_check_v3(raw, baseline_v2, dispositions):
    """Pure returned metadata; wording stays in memory. Caller installs cache/write guards."""
    from divergence.statute_ingest import read_knowledge_table, SHEET_REL
    from divergence.statute_records import validate_dispositions
    validate_dispositions(dispositions)
    knowledge = read_knowledge_table(se.STATUTES_DIR / SHEET_REL)['ita2025_2026']
    effects = ledger()
    selected = [
        e
        for e in effects
        if e[
            'target_act'
        ] == '2025'
        and e[
            'effect_id'
        ].split(
            ':',
            1
        )[
            0
        ] in {
            'fa_2026',
            'tola_2026',
            'tola_2026_gz'
        }
    ]
    registry = {row['key']: row for row in json.loads(ss.SOURCES_PATH.read_text(encoding='utf-8'))['manual']}
    for effect in selected:
        prefix = effect['effect_id'].split(':', 1)[0]
        registered = registry.get(prefix, registry.get('tola_2026_gz') if prefix == 'tola_2026' else None)
        if registered is None or registered.get('assent_date') != effect['assent_date']:
            raise V3Stop('instrument assent provenance differs')
    eligible = [e for e in selected if v3_effect_in_date(e, knowledge)]
    deferred = [e for e in selected if not v3_effect_in_date(e, knowledge)]
    sect, view_cache = _v3_sections(raw)
    parsed, built = _v3_instruments()
    items = _v3_items(dispositions)
    old = gazette_check(raw)
    if old['missing'] or sum(map(len, old['content'].values())) != 17:
        raise V3Stop('historical C3 baseline differs')
    gi = gazette_index(ss.pdf_pages(se.RAW_DIR / ss.INSTRUMENTS[GAZETTE_KEY][0] / ss.INSTRUMENTS[GAZETTE_KEY][1]))
    headings = sorted({se.fold_for_diff(b['heading'] or '') for b in old['bounds'].values()} - {''})
    _V3_STATE.clear()
    _V3_RESULTS.clear()
    args = (raw, effects, parsed, items, old, gi, sect, se, ss, sys.modules[__name__], ap)
    _, initial = _v3_legacy_probe_a3(*args)
    base_hunks = _v3_hunks(initial, sect)
    if [(e['section'], e['hunk']['key']) for e in base_hunks] != [(r['section'], r['location_sha16']) for r in baseline_v2]:
        raise V3Stop('fifteen-row v2 baseline differs')
    stages, unanchored, witnesses = ([], [], [])
    original_apply = _v3_legacy_apply_effect

    def witnessed(text, effect, *args, **kwargs):
        after = original_apply(text, effect, *args, **kwargs)
        for h in word_hunks(text, after):
            witnesses.append(
                {
                    'effect_id': effect[
                        'effect_id'
                    ],
                    'section': effect[
                        'target_section'
                    ],
                    'old': h[
                        'old'
                    ],
                    'new': h[
                        'new'
                    ]
                }
            )
        return after
    for number in range(1, 6):
        policy = {'headings': headings, 'unanchored': [], **{'R' + str(i): i <= number for i in (1, 3, 4, 5)}}
        current_effects = effects if number == 1 else [e for e in effects if e not in deferred]
        if number == 5:
            globals()['_v3_legacy_apply_effect'] = witnessed
        _, corrected = _v3_legacy_probe_a3(
            raw,
            current_effects,
            parsed,
            items,
            old,
            gi,
            sect,
            se,
            ss,
            sys.modules[
                __name__
            ],
            ap,
            policy=policy
        )
        stages.append(('R' + str(number), _v3_hunks(
            corrected, sect, markup=number >= 5, furniture=number >= 4, view=view_cache['ita2025_2026'])))
        if number == 5:
            unanchored = policy['unanchored']
    globals()['_v3_legacy_apply_effect'] = original_apply
    rows, reasons = _v3_rows(base_hunks, stages, items, sect, view_cache['ita2025_2026'], witnesses)
    convention = se.convention_note(view_cache['ita2025_2026'].pages)
    crosschecks = [
        _v3_editor_crosscheck(
            e,
            sect(
                'ita2025_2026',
                e[
                    'target_section'
                ]
            ),
            se.section_apparatus(
                view_cache[
                    'ita2025_2026'
                ],
                sect(
                    'ita2025_2026',
                    e[
                        'target_section'
                    ]
                ),
                convention
            )
        )
        for e in deferred
    ]
    counts = Counter(((r['status'], r['rule']) for r in rows))
    return {
        'rows': rows,
        'nature_reasons': reasons,
        'knowledge_date': knowledge,
        'wef_cutoff': v3_first_april(
            knowledge
        ).isoformat(

        ),
        'heading_count': len(
            headings
        ),
        'eligible': [
            e[
                'effect_id'
            ]
            for e in eligible
        ],
        'deferred': crosschecks,
        'unanchored': unanchored,
        'scoped_witnesses': policy.get('scoped_witnesses', []),
        'occurrence_reconciliation': _V3_RESULTS['occurrence_reconciliation'],
        'rule_counts': {
            status + ':' + rule: count
            for (
                status,
                rule
            ),
            count in sorted(
                counts.items(

                )
            )
        },
        'distinct_final_hunks': len(
            stages[
                -1
            ][
                1
            ]
        ),
        'guard_body_count': len(
            built[
                'body_sha'
            ]
        )
    }


def _v3_legacy_hash16(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]


def run_v3_cli(baseline_path, output_path, audit_dir, regression_out=None):
    import inspect
    audit_dir = Path(audit_dir)
    rules = json.loads((audit_dir / 'rules.json').read_text(encoding='utf-8'))
    for name, expected in rules['functions'].items():
        actual = hashlib.sha256(inspect.getsource(globals()[name]).encode()).hexdigest()
        if actual != expected:
            raise V3Stop('preregistered rule changed: ' + name)
    repository = se.STATUTES_DIR.parent.parent
    for path, expected in rules['code_files'].items():
        if hashlib.sha256((repository / path).read_bytes()).hexdigest() != expected:
            raise V3Stop('preregistered code changed')
    if hashlib.sha256(inspect.getsource(gazette_check).encode()).hexdigest() != rules['C3_sha256']:
        raise V3Stop('historical C3 changed')
    inputs = json.loads((audit_dir / 'input-hashes.json').read_text(encoding='utf-8'))
    repository = se.STATUTES_DIR.parent.parent
    if any((hashlib.sha256((repository / p).read_bytes()).hexdigest() != digest for p, digest in inputs.items())):
        raise V3Stop('preregistered input changed')
    with ss.existing_local_sources(), contextlib.redirect_stdout(io.StringIO()):
        result = gazette_check_v3(
            se.latest_raw_dir(

            ),
            ap.read_csv(
                baseline_path
            ),
            ap.read_csv(
                se.STATUTES_DIR / 'CORRIGENDUM-DISPOSITION.csv'
            )
        )
    result['inputs'] = inputs
    result['rules_sha256'] = hashlib.sha256(json.dumps(rules, sort_keys=True).encode()).hexdigest()
    with Path(output_path).open('x', encoding='utf-8', newline='') as stream:
        stream.write(ap.csv_text(result['rows'], V3_COLUMNS))
    with (audit_dir / 'v3-summary.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    if regression_out:
        with Path(regression_out).open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, sort_keys=True, indent=2)
            stream.write('\n')
    return result


def _v3_cli(args):
    try:
        result = run_v3_cli(args.baseline_v2, args.out, args.audit_dir, args.regression_out)
    except Exception as exc:
        print('STOP:', type(exc).__name__)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
