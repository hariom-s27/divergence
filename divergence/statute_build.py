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
import difflib
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
VERSION_COLUMNS = ["record_key", "in_force_from", "in_force_to", "state", "effect_ids", "reason_codes",
                   "applies_from_tax_year", "applies_to_tax_year", "basis_category", "basis", "owner_ok", "owner_note"]
VERSIONS_PATH = se.STATUTES_DIR / "VERSION-DATES.csv"
REPEAL_NOTE = "same-day repeal by s.536 of the 2025 Act; legal status unsettled"
OWNER_CHOICES = {}          # (edition, section) -> chosen start page; s.56 ita1961_2023: pending owner choice (Q1)
PENDING_RE = re.compile(r"(?i)shall\s+be\s+(ins(?:erted|\.)|sub(?:stituted|s?\.)|om(?:itted|tt?\.|it\.)|"
                        r"re-?numbered|renum(?:bered|\.))")
FN_DATE_RE = re.compile(r"w\.(?:r\.)?e\.f\.\s*(\d{1,2})\s*-\s*(\d{1,2})\s*-\s*(\d{4})")
AMENDED_BY_RE = re.compile(r"^\s*\[\s*AS\s+AMENDED\s+BY\s+(.+?)\s*\]\s*$", re.I)
MARKS_ONLY_RE = re.compile(r"[\[\]*\s]")
ALNUM_RE = re.compile(r"[^a-z0-9]")
GLUED_DIGITS_RE = re.compile(r"(?<=[A-Za-z]{2})\d{1,3}\b")
LABEL_RE = re.compile(r"^\[?\(?(?:\d{1,3}[A-Z]{0,4}|[a-z]{1,6}|[A-Z]{1,4})\)\]?$")
RECALL_YEARS = range(2022, 2027)
UNEXPLAINED = ("publisher_change", "amendment_not_in_ledger", "older_act_span", "span_unlinked")


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

def word_hunks(old: str, new: str) -> list:
    """Word hunks between two folded bodies: (op, old_words, new_words, old_index)."""
    a, b = old.split(), new.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != "equal":
            out.append({"op": op, "old": " ".join(a[i1:i2]), "new": " ".join(b[j1:j2]), "at": i1})
    return out


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
        if c.get("read") and se.fold_for_diff(c["read"]).strip("\"' ") in h["new"] and \
                se.fold_for_diff(c["for"]).strip("\"' ") in h["old"]:
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
    rows, before, covered = [], [], False
    n = 0

    def row(frm, to, state, ids, reasons, cat, basis, text=None):
        nonlocal n
        n += 1
        return {"record_key": f"act:{act}:{section}:v{n}", "in_force_from": frm or "", "in_force_to": to or "",
                "state": state, "effect_ids": ";".join(ids), "reason_codes": ";".join(reasons),
                "applies_from_tax_year": "", "applies_to_tax_year": "", "basis_category": cat, "basis": basis,
                "owner_ok": "", "owner_note": "", "_text": text}          # _text: local only, not a CSV column
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
            rows.append(row(p, nxt, "AMBIGUOUS", new, ["unprinted_intermediate"] + reasons, cat,
                            "no edition prints this state"))
            continue
        covered = True
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


def build(raw: Path, out_dir: Path, effects: list | None = None) -> dict:
    """All C2 computations; writes the local sheets in out_dir; returns the public rows and the printed summary.
    effects: the ledger rows (default: AMENDMENT-EFFECTS.csv)."""
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
                r = next(b for p, b in candidate_bodies(views[k], sec) if p == choice)
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
                    ch_rows.append((act, sec, k, lab, det, h))
    # versions
    commence = commencement_2025(sect)
    vrows, before_all, unplaced_all, sec_counts = [], {}, {}, []
    for act in ("1961", "2025"):
        for sec in ap.SPINE[act]:
            effs = by_sec.get((act, sec), [])
            eds = []
            for k in se.EDITIONS[act]:
                pend = pending_effects(effs, k, sec, app, notes)
                eds.append({"key": k, "knowledge": know[k]["date"], "found": sect(k, sec)["status"] == "FOUND",
                            "pending": pend})
            ins = [e for e in effs if _inserts_section(e) and e["wef"]]
            origin = min(e["wef"] for e in ins) if ins else (commence if act == "2025" else None)
            end = commence if act == "1961" else None
            rows, before, unplaced = propose_versions(act, sec, effs, eds, origin, end,
                                                      repeal_day=commence if act == "1961" else None,
                                                      inserted=bool(ins))
            vrows += rows
            before_all[(act, sec)] = before
            unplaced_all[(act, sec)] = unplaced
            unexpl = sum(1 for r in ch_rows if r[0] == act and r[1] == sec and r[3] in UNEXPLAINED)
            sec_counts.append((act, sec, len(effs), len(rows), sum(r["state"] == "AMBIGUOUS" for r in rows),
                               sum(r["state"] == "never_operative" for r in rows),
                               sum("repeal_day_unsettled" in r["reason_codes"] for r in rows),
                               sum("retro_knowledge" in r["reason_codes"] for r in rows), len(before), unexpl))
    ins_check = insertion_checks(effects, vrows, sect)
    s56 = s56_candidates(views["ita1961_2023"])
    sheets = write_sheets(out_dir, effects, know, pend_rows, diffs_md, ev_rows, ch_rows, vrows, before_all,
                          unplaced_all, s56, commence, hunks, ins_check)
    return {"effects": effects, "know": know, "pend": pend_rows, "ev": ev_rows, "ch": ch_rows, "versions": vrows,
            "before": before_all, "counts": sec_counts, "s56": s56, "commence": commence, "sheets": sheets,
            "unplaced": unplaced_all, "ins_check": ins_check}


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
          f"{r['reason_codes']} | {_md(r['basis'])} |" for r in vrows]
    v += ["", "## before_coverage (not written as rows)"]
    v += [f"- {a} s.{s}: {b}" for (a, s), b in before_all.items() if b]
    v += ["", "## Effects without a date (not placed on the timeline)"]
    v += [f"- {a} s.{s}: {u}" for (a, s), u in unplaced_all.items() if u]
    v += ["", "## Whole-section insertions: Act text vs first edition text (report only)"]
    v += [f"- {x}" for x in ins_check]
    v += ["", "## s.56 ita1961_2023 candidates (Q1; pending owner choice)", "", f"- {s56}"]
    for name, lines in (("PENDING-23.md", p), ("DIFFS.md", d), ("CROSSCHECK.md", c), ("VERSIONS.md", v)):
        se._write_new(out_dir / name, "\n".join(lines) + "\n")
        files.append(out_dir / name)
    return files


def main(argv=None) -> int:
    ap_ = argparse.ArgumentParser(description=BUILD_VERSION)
    ap_.add_argument("--propose", action="store_true", help="diffs, cross-check, versions; write VERSION-DATES.csv")
    ap_.add_argument("--counts", action="store_true", help="print the per-section count table of the last proposal")
    ap_.add_argument("--dry-run", action="store_true", help="compute and print; write the local sheets only")
    a = ap_.parse_args(argv)
    if not (a.propose or a.counts or a.dry_run):
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
    effects = ap.run_ledger()[1] if a.dry_run else None          # dry run: the ledger computed in memory
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
        path, msg = ap.write_never_overwrite(VERSIONS_PATH, res["versions"], VERSION_COLUMNS, "record_key")
        print("\n".join(msg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
