"""P09 Part C0: instrument title pages, text layer, corrigenda items and the E2 corrigendum check (report only).

Reads only local PDFs (no network, no environment variables, no model calls) and prints tables:

  --instruments                  title-page facts per instrument read by code: Act number/year (only from a
                                 'NO. N OF YYYY' line; the Gazette issue header 'No. 8]' is never used), assent date
                                 ('received the assent of the President on ...' and the bracketed '[date]' line),
                                 Ordinance promulgation date, corrigendum target Act(s), printed Gazette ID, pages,
                                 text-layer % (row 69: < 95% -> MANUAL NEEDED; no OCR), sha256, source_kind.
  --instruments --check-sources  compare every field written in statutes/SOURCES.json with a fresh read; print
                                 mismatches (0 required before the C0 STOP).
  --e2                           row 70 check E2: the selected corr_ita2025 items, searched in the ITD editions of
                                 the 2025 Act after whitespace-only fold; per hit the page and the section whose
                                 candidate start (extractor find_starts, the locate data) precedes it. Report only.
  --manual-lines                 the MANUAL-SOURCES.txt lines for the Part C files (file . item . URL . date saved).

Nothing here edits law text, SOURCES.json or any PDF. Law words found by --e2 go only to files under _local_text/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

from divergence import statute_extract as se

SOURCES_VERSION = "statute_sources v1"
TEXT_LAYER_MIN = 95.0                       # row 69
MANUAL_REL = Path("2026-11-13") / "manual"  # owner's manual folder (Part A)
PARTC_DIR = se.CENSUS_DIR / "partC"
SOURCES_PATH = se.STATUTES_DIR / "SOURCES.json"

# Approved C0 plan (15 Nov 2026, D2 = a, D3 = a): key -> (folder under _raw/, file, expected kind, source_kind, url)
INSTRUMENTS = {
    "fa_2022": (MANUAL_REL, "fa_2022.pdf", "act", "gazette", "https://egazette.gov.in/WriteReadData/2022/234693.pdf"),
    "fa_2023": (MANUAL_REL, "244830.pdf", "act", "gazette", "https://egazette.gov.in/WriteReadData/2023/244830.pdf"),
    "fa_2024": (MANUAL_REL, "252143.pdf", "act", "gazette", "https://egazette.gov.in/WriteReadData/2024/252143.pdf"),
    "fa2_2024": (MANUAL_REL, "256436.pdf", "act", "gazette", "https://egazette.gov.in/WriteReadData/2024/256436.pdf"),
    "fa_2026": (MANUAL_REL, "fa_2026.pdf", "act", "gazette", "https://egazette.gov.in/WriteReadData/2026/271439.pdf"),
    "fa_2025_gz": (MANUAL_REL, "262125.pdf", "act", "gazette",
                   "https://egazette.gov.in/WriteReadData/2025/262125.pdf"),
    "tola_2026_gz": (MANUAL_REL, "275521.pdf", "act", "gazette",
                     "https://egazette.gov.in/WriteReadData/2026/275521.pdf"),
    "corr_fa2022": (MANUAL_REL, "235358.pdf", "corrigendum", "gazette_corrigendum",
                    "https://egazette.gov.in/WriteReadData/2022/235358.pdf"),
    "corr_fa2023": (MANUAL_REL, "245119.pdf", "corrigendum", "gazette_corrigendum",
                    "https://egazette.gov.in/WriteReadData/2023/245119.pdf"),
    "corr_ita2025": (MANUAL_REL, "269669.pdf", "corrigendum", "gazette_corrigendum",
                     "https://egazette.gov.in/WriteReadData/2026/269669.pdf"),
    "corr_fa2026": (MANUAL_REL, "271980.pdf", "corrigendum", "gazette_corrigendum",
                    "https://egazette.gov.in/WriteReadData/2026/271980.pdf"),
    "fa_2025": (Path("2026-11-13"), "fa_2025.pdf", "act", "itd_reproduction", None),
    "tola_2026": (Path("2026-11-13"), "tola_2026.pdf", "act", "itd_reproduction", None),
    "ord_2_2026": (Path("2026-11-13"), "ord_2_2026.pdf", "ordinance", "itd_reproduction", None),
    "n74_2022": (MANUAL_REL, "n74_2022.pdf", "notification", "notification", None),   # owner's manual copy
    "n75_2022": (MANUAL_REL, "n75_2022.pdf", "notification", "notification", None),
    "n19_2026": (MANUAL_REL, "n19_2026.pdf", "notification", "notification", None),
}
# MANUAL-SOURCES.txt: keys whose line is written in Part C, and the owner's tag (approved fix 4)
MANUAL_LINE_KEYS = ["fa_2023", "fa_2024", "fa2_2024", "corr_fa2022", "corr_fa2023", "corr_ita2025", "corr_fa2026",
                    "fa_2025_gz", "tola_2026_gz"]
OWNER_DOWNLOADED_TAG = {"fa_2025_gz": "downloaded by owner from this URL, 2026-11-15",
                        "tola_2026_gz": "downloaded by owner from this URL, 2026-11-15"}
# Fields written into SOURCES.json from --instruments and compared by --check-sources
CHECK_FIELDS = ("file", "act_no", "act_year", "assent_date", "promulgated_on", "gazette_id", "gazette_date",
                "corrigendum_targets", "sha256", "pages", "text_layer_pct", "source_kind")

# E2 (row 70, D5): corr_ita2025 items chosen by (Gazette page, line(s)); the words come from the parsed corrigendum
E2_ITEMS = [("100", "7"), ("463", "20-21"), ("463", "37"), ("178", "28"), ("371", "37"), ("491", "33")]
E2_EDITIONS = ["ita2025_2026", "ita2025_2025"]

MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
_MON = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
ACT_NO_RE = re.compile(r"(?<![A-Za-z])(?<!Bill )(?<!BILL )(?:ACT\s+)?NO\.?\s*(\d+)\s+OF\s+(\d{4})\b", re.I)
ASSENT_RE = re.compile(r"received the assent of the President on\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+"
                       + _MON + r",?\s+(\d{4})", re.I)
BRACKET_DATE_RE = re.compile(r"\[\s*(\d{1,2})(?:st|nd|rd|th)?\s+" + _MON + r",?\s+(\d{4})\.?\s*\]", re.I)
NEW_DELHI_RE = re.compile(r"New Delhi,?\s+the\s+(\d{1,2})(?:st|nd|rd|th)?\s+" + _MON + r",?\s+(\d{4})", re.I)
HEADER_DATE_RE = re.compile(r"NEW DELHI,\s+[A-Z]+DAY,\s+" + _MON + r"\s+(\d{1,2}),\s+(\d{4})", re.I)
GAZETTE_ID_RE = re.compile(r"CG-DL-E-\d{8}-\d{6}")
SHORT_TITLE_RE = re.compile(r"(?:Act|Ordinance) may be called the (.+?(?:Act|Ordinance),\s*\d{4})", re.I)
PROMULGATE_RE = re.compile(r"President is pleased to promulgate", re.I)
CORR_TARGET_RE = re.compile(r"(?:In the|The)\s+([^\n]{3,160}?(?:Act|Ordinance),\s*\d{4})\s*\((\d+)\s+of\s+(\d{4})\)",
                            re.I)    # C1 Q6: a title may contain parentheses ('X (Amendment of Provisions) Act, YYYY')
NOTIF_NO_RE = re.compile(r"Notification No\.\s*(\d+)\s*/\s*(\d{4})", re.I)
CORR_ROW_RE = re.compile(r"^\s*(\d{1,4})\s+(\d{1,3}(?:\s*[-–]\s*\d{1,3})?)\s+[“\"](.*)$")
CORR_PROSE_RE = re.compile(r"page\s+(\d{1,4}),\s*(?:in\s+)?lines?\s+(\d{1,3}(?:\s*(?:-|–|and|to)\s*\d{1,3})?),?"
                           r"\s*for\s+[“\"](.+?)[”\"],?\s+read\s+[“\"](.+?)[”\"]", re.I | re.S)
CORR_BLOCK_RE = re.compile(r"^\s*CORRIGEND(?:A|UM)\s*$")
WORD_CHAR = re.compile(r"[A-Za-z0-9]")


# ---------------------------------------------------------------- pure helpers (tested with invented text)

def fold_ws(s: str) -> str:
    """Whitespace-only fold: every run of whitespace -> one space, ends stripped. Nothing else changes."""
    return re.sub(r"\s+", " ", s).strip()


def fold_with_map(s: str) -> tuple:
    """(folded, idx) where folded[i] comes from s[idx[i]]; runs of whitespace become one space (not stripped)."""
    out, idx, in_ws = [], [], False
    for i, ch in enumerate(s):
        if ch.isspace():
            if not in_ws:
                out.append(" ")
                idx.append(i)
            in_ws = True
            continue
        in_ws = False
        out.append(ch)
        idx.append(i)
    return "".join(out), idx


def _iso(day: str, month: str, year: str) -> str:
    return date(int(year), MONTHS[month.lower()], int(day)).isoformat()


def title_facts(pages: list) -> dict:
    """Facts read from the first pages' text (pages[0] = page 1). Every value is None when not printed."""
    head = "\n".join(pages[:2])
    folded = fold_ws(head)
    f = {"act_no": None, "act_year": None, "short_title": None, "assent_date": None, "bracket_date": None,
         "promulgated_on": None, "gazette_id": None, "gazette_date": None, "corrigendum_targets": [],
         "notification_no": None, "kind_seen": None}
    m = next((x for x in ACT_NO_RE.finditer(pages[0] if pages else "")), None)
    if m:
        f["act_no"], f["act_year"] = int(m.group(1)), int(m.group(2))
    m = SHORT_TITLE_RE.search(folded + " ")
    if m:
        f["short_title"] = m.group(1)
    m = ASSENT_RE.search(folded)
    if m:
        f["assent_date"] = _iso(*m.groups())
    m = BRACKET_DATE_RE.search(folded)
    if m:
        f["bracket_date"] = _iso(*m.groups())
    if PROMULGATE_RE.search(folded):
        m = NEW_DELHI_RE.search(folded)
        f["promulgated_on"] = _iso(*m.groups()) if m else None
    ids = GAZETTE_ID_RE.findall(head)
    f["gazette_id"] = ids[0] if ids else None
    m = HEADER_DATE_RE.search(folded)
    if m:
        mon, day, year = m.groups()
        f["gazette_date"] = _iso(day, mon, year)
    if re.search(r"\bCORRIGEND(?:A|UM)\b", head):
        f["kind_seen"] = "corrigendum"
        f["corrigendum_targets"] = [f"{t} ({n} of {y})" for t, n, y in
                                    ((fold_ws(a), b, c) for a, b, c in CORR_TARGET_RE.findall(head))]
        m = NEW_DELHI_RE.search(folded)
        if m and not f["gazette_date"]:
            f["gazette_date"] = _iso(*m.groups())
    elif PROMULGATE_RE.search(folded):
        f["kind_seen"] = "ordinance"
    elif re.search(r"\bNOTIFICATION\b", head):
        f["kind_seen"] = "notification"
        m = NOTIF_NO_RE.search(fold_ws("\n".join(pages)))     # the number is printed at the end of the notification
        f["notification_no"] = f"{m.group(1)}/{m.group(2)}" if m else None
    elif f["assent_date"]:
        f["kind_seen"] = "act"
    return f


def text_layer(pages: list) -> tuple:
    """(non-empty pages, total pages, percent rounded to 1 decimal)."""
    n = len(pages)
    ok = sum(1 for t in pages if t.strip())
    return ok, n, round(100.0 * ok / n, 1) if n else 0.0


def _close_cell(part: str) -> tuple:
    """('text before the closing quote', closed?) for a cell that began after an opening quote."""
    m = re.search(r"[”\"]", part)
    return (part[:m.start()], True) if m else (part, False)


def corrigendum_items(pages: list) -> list:
    """Corrigendum rows by code. Table form: 'page line(s) "for" "read"' (a cell may wrap to the next line);
    prose form: 'at page N, in line L, for "x" read "y"'. Each item carries the block's first target Act, the PDF page
    (1-based) and the raw line (1-based) where the row starts. Rows that cannot be split are kept with parsed=False."""
    items, target = [], None
    for idx0, text in enumerate(pages):
        lines = text.splitlines()
        pno = se.page_1based(idx0)
        i = 0
        while i < len(lines):
            ln = lines[i]
            if CORR_BLOCK_RE.match(ln):
                target = None
            if target is None:
                m = CORR_TARGET_RE.search(fold_ws(" ".join(lines[i:i + 3])))
                if m and (ln.lstrip().startswith(("In the", "The")) or "CORRIGEND" in ln):
                    target = f"{fold_ws(m.group(1))} ({m.group(2)} of {m.group(3)})"
            m = CORR_ROW_RE.match(ln)
            if not m:
                i += 1
                continue
            gpage, glines, rest = m.group(1), re.sub(r"\s+", "", m.group(2)).replace("–", "-"), m.group(3)
            parts = re.split(r"[“]|(?<=\s)\"", rest)
            cells = [_close_cell(p) for p in parts[:2]] if len(parts) >= 2 else []
            item = {"target": target, "pdf_page": pno, "pdf_line": i + 1, "gazette_page": gpage,
                    "gazette_lines": glines, "for": None, "read": None, "parsed": False}
            used = 1
            if len(cells) == 2:
                (a, ca), (b, cb) = cells
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                cont, _ = _close_cell(nxt)
                if ca and cb:
                    item.update({"for": a, "read": b, "parsed": True})
                elif not ca and cb and nxt:
                    item.update({"for": f"{a.rstrip()} {cont}", "read": b, "parsed": True})
                    used = 2
                elif ca and not cb and nxt:
                    item.update({"for": a, "read": f"{b.rstrip()} {cont}", "parsed": True})
                    used = 2
            if item["parsed"]:
                item["for"], item["read"] = fold_ws(item["for"]), fold_ws(item["read"])
            items.append(item)
            i += used
        for m in CORR_PROSE_RE.finditer(text):
            items.append({"target": target, "pdf_page": pno, "pdf_line": text[:m.start()].count("\n") + 1,
                          "gazette_page": m.group(1), "gazette_lines": fold_ws(m.group(2)), "for": fold_ws(m.group(3)),
                          "read": fold_ws(m.group(4)), "parsed": True})
    return items


def find_hits(pages: list, words: str) -> list:
    """Exact matches of `words` after whitespace-only fold of both sides, across the whole edition (pages joined by a
    newline). A match counts only when no letter or digit touches it on either side. Returns [(page_1based,
    line_1based, start, end)] with start/end in the folded text."""
    joined = "\n".join(pages)
    folded, idx = fold_with_map(joined)
    needle = fold_ws(words)
    starts = []
    pos = 0
    for t in pages:                     # raw offset where each page begins in `joined`
        starts.append(pos)
        pos += len(t) + 1
    out, k = [], folded.find(needle)
    while k != -1 and needle:
        e = k + len(needle)
        before = folded[k - 1] if k > 0 else " "
        after = folded[e] if e < len(folded) else " "
        if not (WORD_CHAR.match(before) and WORD_CHAR.match(needle[0])) and \
                not (WORD_CHAR.match(after) and WORD_CHAR.match(needle[-1])):
            raw = idx[k]
            p0 = max(i for i, s in enumerate(starts) if s <= raw)
            within = joined[starts[p0]:raw]
            line = len(within.splitlines(True)) if within else 1
            if within.endswith(("\n", "\r")):
                line += 1
            out.append((se.page_1based(p0), max(line, 1), k, e))
        k = folded.find(needle, k + 1)
    return out


def contained(span: tuple, others: list) -> bool:
    return any(o[2] <= span[2] and span[3] <= o[3] for o in others)


def e2_label(old_hits: list, new_hits: list) -> tuple:
    """(label, old_only, new_only): a hit inside a hit of the other string is not counted (one may contain the other)."""
    old_only = [h for h in old_hits if not contained(h, new_hits)]
    new_only = [h for h in new_hits if not contained(h, old_hits)]
    label = {(True, False): "old", (False, True): "new", (True, True): "both", (False, False): "neither"}[
        (bool(old_only), bool(new_only))]
    return label, old_only, new_only


def section_at(starts_pos: list, schedules_pos, page: int, line: int) -> str:
    """Section whose candidate start precedes (page, line). starts_pos = [((page, line), number)] sorted; schedules_pos =
    (page, line) of the Schedules region or None."""
    if schedules_pos and (page, line) >= schedules_pos:
        return "Schedules"
    prev = [num for pos, num in starts_pos if pos <= (page, line)]
    return f"s.{prev[-1]}" if prev else "front matter"


# ---------------------------------------------------------------- PDF readers

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path: Path) -> list:
    from pypdf import PdfReader
    return [p.extract_text() or "" for p in PdfReader(str(path)).pages]


def instrument_row(key: str, raw_root: Path = se.RAW_DIR) -> dict:
    folder, fname, kind, source_kind, url = INSTRUMENTS[key]
    path = raw_root / folder / fname
    pages = pdf_pages(path)
    ok, n, pct = text_layer(pages)
    f = title_facts(pages)
    row = {"key": key, "file": (folder / fname).as_posix(), "kind_expected": kind, "kind_seen": f["kind_seen"],
           "act_no": f["act_no"], "act_year": f["act_year"], "short_title": f["short_title"], "assent_date": f["assent_date"],
           "bracket_date": f["bracket_date"], "promulgated_on": f["promulgated_on"], "gazette_id": f["gazette_id"],
           "gazette_date": f["gazette_date"], "corrigendum_targets": f["corrigendum_targets"],
           "notification_no": f["notification_no"], "sha256": sha256_file(path), "pages": n, "text_pages": ok,
           "text_layer_pct": pct, "source_kind": source_kind, "url": url,
           "mtime_date": datetime.fromtimestamp(path.stat().st_mtime).date().isoformat(), "problems": []}
    if pct < TEXT_LAYER_MIN:
        row["problems"].append(f"MANUAL NEEDED: text layer {pct}% < {TEXT_LAYER_MIN}%")
    if f["kind_seen"] != kind:
        row["problems"].append(f"kind seen {f['kind_seen']!r} != expected {kind!r}")
    if kind == "act" and (f["act_no"] is None or f["assent_date"] is None):
        row["problems"].append("Act number or assent date not read")
    if f["bracket_date"] and f["assent_date"] and f["bracket_date"] != f["assent_date"]:
        row["problems"].append(f"bracket date {f['bracket_date']} != assent line {f['assent_date']}")
    return row


def sources_fields(row: dict) -> dict:
    """The SOURCES.json fields for one instrument (CHECK_FIELDS that apply to its kind)."""
    out = {"file": row["file"]}
    if row["kind_expected"] in ("act", "ordinance"):
        out.update({"act_no": row["act_no"], "act_year": row["act_year"]})
    if row["kind_expected"] == "act":
        out["assent_date"] = row["assent_date"]
    if row["kind_expected"] == "ordinance":
        out["promulgated_on"] = row["promulgated_on"]
    if row["kind_expected"] == "corrigendum":
        out["corrigendum_targets"] = row["corrigendum_targets"]
    out.update({"gazette_id": row["gazette_id"], "gazette_date": row["gazette_date"], "sha256": row["sha256"],
                "pages": row["pages"], "text_layer_pct": row["text_layer_pct"], "source_kind": row["source_kind"]})
    return out


def check_sources(rows: list, sources_path: Path = SOURCES_PATH) -> list:
    """Every CHECK_FIELDS value written in SOURCES.json vs a fresh read; missing entries and missing fields count."""
    data = json.loads(Path(sources_path).read_bytes().decode("utf-8"))
    by_key = {it["key"]: it for it in data.get("items", []) + data.get("manual", [])}
    out = []
    for row in rows:
        it = by_key.get(row["key"])
        if it is None:
            out.append((row["key"], "-", "entry missing", "-"))
            continue
        for fld, val in sources_fields(row).items():
            if fld not in it:
                out.append((row["key"], fld, "field missing", val))
            elif it[fld] != val:
                out.append((row["key"], fld, it[fld], val))
        for fld in CHECK_FIELDS:
            if fld in it and fld not in sources_fields(row):
                out.append((row["key"], fld, it[fld], "not applicable to this kind"))
    return out


# ---------------------------------------------------------------- E2

def edition_positions(pages: list) -> tuple:
    """Candidate section starts [((page, line), number)] and the Schedules start (page, line) from the extractor."""
    kept, _ = se.drop_duplicate_pages(pages)
    cleaned = se.clean_pages(kept)
    starts = se.find_starts(cleaned.lines)
    pos = sorted(((cleaned.lines[s.idx].page, cleaned.lines[s.idx].line_no), s.number) for s in starts)
    k = se.schedules_from(cleaned.lines)
    sched = (cleaned.lines[k].page, cleaned.lines[k].line_no) if k < len(cleaned.lines) else None
    return pos, sched


def run_e2(raw: Path) -> tuple:
    """(summary rows, hit rows) for E2_ITEMS in E2_EDITIONS."""
    folder, fname = INSTRUMENTS["corr_ita2025"][:2]
    items = corrigendum_items(pdf_pages(se.RAW_DIR / folder / fname))
    chosen = []
    for gp, gl in E2_ITEMS:
        hit = [it for it in items if it["gazette_page"] == gp and it["gazette_lines"] == gl and it["parsed"]]
        chosen.append((gp, gl, hit[0] if len(hit) == 1 else None, len(hit)))
    summary, hits = [], []
    for ed in E2_EDITIONS:
        pages = se.load_pages(raw / f"{ed}.pdf")
        pos, sched = edition_positions(pages)
        for gp, gl, it, nmatch in chosen:
            if it is None:
                summary.append({"item": f"{gp}/{gl}", "edition": ed, "problem": f"{nmatch} parsed rows match"})
                continue
            old, new = find_hits(pages, it["for"]), find_hits(pages, it["read"])
            label, old_only, new_only = e2_label(old, new)
            contain = "yes" if (fold_ws(it["for"]) in fold_ws(it["read"]) or
                                fold_ws(it["read"]) in fold_ws(it["for"])) else "no"
            summary.append({"item": f"{gp}/{gl}", "corr_pdf": f"p{it['pdf_page']} l{it['pdf_line']}",
                            "for": it["for"], "read": it["read"], "edition": ed, "old_hits": len(old),
                            "old_only": len(old_only), "new_hits": len(new), "new_only": len(new_only),
                            "one_contains_other": contain, "label": label})
            for kind, lst, only in (("old", old, old_only), ("new", new, new_only)):
                for h in lst:
                    hits.append({"item": f"{gp}/{gl}", "edition": ed, "words": kind, "page": h[0], "line": h[1],
                                 "section": section_at(pos, sched, h[0], h[1]),
                                 "counted": "yes" if h in only else "no (inside the other string's hit)"})
    return summary, hits


# ---------------------------------------------------------------- output

def _table(rows: list, cols: list) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")).replace("|", "/") for c in cols) + " |")
    return "\n".join(out)


def _emit(text: str, out_dir: Path | None, name: str) -> None:
    print(text)
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        with open(path, "x", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
        print(f"written {path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m divergence.statute_sources", description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--instruments", action="store_true")
    mode.add_argument("--e2", action="store_true")
    mode.add_argument("--manual-lines", action="store_true")
    ap.add_argument("--check-sources", action="store_true", help="with --instruments: compare SOURCES.json fields")
    ap.add_argument("--json", action="store_true", help="with --instruments: print the SOURCES.json fields per key")
    ap.add_argument("--out", help="also write the printed text to OUT/<mode>-<stamp>.md (use a _local_text folder)")
    ap.add_argument("--raw-dir", help="edition folder (default: newest dated folder under _raw/)")
    args = ap.parse_args(argv)
    out_dir = Path(args.out) if args.out else None
    if args.instruments or args.manual_lines:
        rows = [instrument_row(k) for k in INSTRUMENTS]
    if args.manual_lines:
        by = {r["key"]: r for r in rows}
        lines = []
        for k in MANUAL_LINE_KEYS:
            r = by[k]
            tag = f" ({OWNER_DOWNLOADED_TAG[k]})" if k in OWNER_DOWNLOADED_TAG else ""
            title = r["short_title"] or "; ".join(r["corrigendum_targets"]) or k
            item = f"Corrigenda, {title}" if r["kind_expected"] == "corrigendum" else title
            no = f" (No. {r['act_no']} of {r['act_year']})" if r["act_no"] else ""
            gid = f", Gazette {r['gazette_id']}" if r["gazette_id"] else ""
            lines.append(f"{Path(r['file']).name} · {item}{no}{gid} · {r['url']}{tag} · {r['mtime_date']}")
        print("\n".join(lines))
        return 0
    if args.instruments:
        cols = ["key", "file", "kind_seen", "act_no", "act_year", "assent_date", "bracket_date", "promulgated_on",
                "gazette_id", "gazette_date", "pages", "text_layer_pct", "source_kind", "sha256"]
        text = [f"INSTRUMENTS  {SOURCES_VERSION}  extractor {se.EXTRACTOR_VERSION}", "",
                _table([dict(r, sha256=r["sha256"][:12]) for r in rows], cols), "",
                _table(rows, ["key", "short_title", "notification_no", "corrigendum_targets"]), ""]
        probs = [(r["key"], p) for r in rows for p in r["problems"]]
        text.append(f"problems: {len(probs)}")
        text += [f"  {k}: {p}" for k, p in probs]
        manual = [k for k, p in probs if p.startswith("MANUAL NEEDED")]
        text.append(f"MANUAL NEEDED: {', '.join(manual) if manual else 'none'}")
        if args.json:
            text += ["", "SOURCES.json fields:"] + [json.dumps({"key": r["key"], **sources_fields(r)},
                                                               ensure_ascii=False) for r in rows]
        if args.check_sources:
            mm = check_sources(rows)
            text += ["", f"CHECK-SOURCES mismatches: {len(mm)}"]
            text += [f"  {k} {fld}: written={w!r} fresh={v!r}" for k, fld, w, v in mm]
        _emit("\n".join(text), out_dir, "INSTRUMENTS")
        return 1 if args.check_sources and check_sources(rows) else 0
    raw = Path(args.raw_dir) if args.raw_dir else se.latest_raw_dir()
    summary, hits = run_e2(raw)
    text = [f"E2  {SOURCES_VERSION}  extractor {se.EXTRACTOR_VERSION}  (report only; never edits text)", "",
            "Search: whitespace-only fold of both sides; a match needs no letter/digit touching either end. 'old_only' /",
            "'new_only' exclude hits that lie inside a hit of the other string. Section = the extractor's candidate",
            "start (find_starts, no bold test) preceding the hit; 'Schedules' after the Schedules start.", "",
            _table(summary, ["item", "corr_pdf", "for", "read", "edition", "old_hits", "old_only", "new_hits",
                             "new_only", "one_contains_other", "label", "problem"]), "",
            f"Hits ({len(hits)}):", "",
            _table(hits, ["item", "edition", "words", "page", "line", "section", "counted"])]
    _emit("\n".join(text), out_dir, "E2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
