"""P09 statute extractor: edition PDF -> per-section text (deterministic, no model calls).

Run from the repo root:
    python -m divergence.statute_extract --prepare [--jobs N]  build the page-text cache for all editions
    python -m divergence.statute_extract --locate-all     locate every SECTION-LIST / MAPPING section in every edition
    python -m divergence.statute_extract --pilot          extract the Part B pilot sections -> census/pilot/<stamp>/
    python -m divergence.statute_extract --show-rules     print rule examples (before/after) from the pilot text
    python -m divergence.statute_extract --pilot-diff OLD NEW   write NEW/PILOT-DIFF.md (line + word diff per file)

Processing order (fixed, extractor v2): R0 (duplicate pages) -> R3 (page furniture, divider lines,
footnotes) -> R1/R2 (locate start/end) -> per section: M (footnote markers: line, then inline;
editor-note candidates are detected first, never cut) -> R5 (table-row prefixes) -> R4 (whitespace,
hyphen joins) -> B (opening bracket + bracket count). R5 runs before R4 because R5 reads the
indentation that R4 removes, and R4 never joins into a line that starts with a table-row prefix.

Page numbers: every page number written to a file, log or report is the 1-based PDF viewer page
(page 1 = first page, as in Edge), labelled 'page_1based'. Internally pypdf's 0-based index is
converted in ONE place: page_1based() / idx0_from_page() [P09-40]. Line numbers in logs are the
1-based line within the raw pypdf page text ('line_1based').

Extractor v2 changes (owner decisions P09-29 .. P09-41, Part B fix round):
  P09-29/29a/29b  a body line made only of numbers (^\\d+[a-z]?( \\d+[a-z]?)*$) is dropped only if every
      number equals a footnote number: the leading 'N.' / 'Na.' of ANY line inside an R3 footnote
      block on the section's pages or the 1 page after its last page. Unmatched lines stay and are
      listed as unresolved markers.
  P09-30  footnote text is kept as footnotes_raw ({page_1based, number, text}) in the local meta file
      only; never a date source; never in committed files.
  P09-31  R5 labels integer serial rows only ('[Table k Sl. N] '); roman sub-items get no label. A table
      ends at an unindented sub-section line '(n)' / '[(n)', a line starting 'Explanation' /
      '[Explanation', a CHAPTER line, a real section start, or the section end.
  P09-32  a line made only of '_', '-' or '—' (3 or more) is dropped anywhere on a page and logged.
  P09-33/33b  a line ending in an ASCII '-' directly after a letter is joined to the next line with no
      space; the hyphen is kept; never on an em dash or after a digit; never into a table-row line.
  P09-34  stored bodies keep the PDF line breaks (only P09-33 joins); runs of spaces inside a line are
      collapsed. fold v2 additionally collapses all whitespace (spaces and newlines) to one space.
  P09-35  editor's amendment-note blocks ('... shall be inserted/substituted/omitted/renumbered ...' with
      'w.e.f.' within 3 lines, up to the next marker line, sub-section line or the section end) are
      only LISTED as candidates; nothing is removed until the owner confirms the list.
  P09-36  an opening '[' at the start of the heading is moved to the start of the body (stored once;
      the heading field is stored without it). '[' and ']' are counted per section (our own
      '[Table k Sl. N]' prefixes excluded); a difference is a WARN, not a failure.
  P09-41  inline markers: digits glued directly before '[' (\\b\\d+[a-z]?(?=\\[)) are dropped only if they
      equal a footnote number in the P09-29a range; unmatched ones stay and are listed.

Rules (extractor v1, approved by the owner at the P09 Part B STOP):
  R0  a page whose extracted text is identical to an EARLIER page of the same file and has >= 200
      characters (after strip) is dropped (its page number stays, with empty text); the first
      occurrence is kept; every dropped page is listed (edition, page, duplicate-of page). [D1]
  R1  section start: a line 'N.' / 'N .' / 'N.(1)' (dot may end the line) right after a heading
      (shortest first: 1 line, else up to 3 wrapped lines; ends in '.', first line starts with a
      capital, '[' or a quote); no heading line may start with a digit or be a CHAPTER / part /
      Schedule / Act-title / all-caps line; a heading may not start with 'Explanation' or 'Provided'
      [D4]; 'N.--...' is a numbered part heading, not a start; not a table row (R5 state machine),
      not a footnote, not inside the Schedules region (from the first standalone SCHEDULE line to the
      end of the file). Exactly one candidate = FOUND; 0 = NOT_FOUND; 2+ = UNRESOLVED (never picks one).
  R2  section end: the heading of the next valid start with a higher section key, a CHAPTER line,
      a part heading ('F.--...'), a SCHEDULE line, an all-caps Act title line ('INCOME-TAX ACT, 1961'),
      or the end of the file.
  R3  furniture: exact footer lines and patterns, only in the first 2 / last 3 non-empty lines of a
      page. Footnotes: a block starts at a FOOTNOTE_START line and ends at the next heading + section
      start pair or CHAPTER / part / Schedule / Act-title line on the same page, else at the page end
      [D3]; blocks are moved verbatim to amendment_note. Markers in the text are kept exactly.
  R4  (v1; replaced in v2 by P09-33/34) whitespace collapse plus joining unterminated lines.
  R5  tables: a region starts at a line that is only 'TABLE'/'Table'; tables are numbered k = 1, 2, ...
      in order of appearance within the section [D6]; rows 'N.' must be sequential (1, 2, 3 ...) and
      get '[Table k Sl. N] '; a non-sequential numbered line inside a table is listed as unresolved.
      (v1 also labelled roman sub-rows [D2]; v2 does not, P09-31.)

Mechanical fixes made during the Part B pilot and accepted by the owner as part of v1:
  M1  'N.(1)' with no space after the dot is a valid start.
  M2  the footer date pattern accepts 'm/d/yy, h:mm PM' as well as 'dd/mm/yyyy, h:mm am'.
  M3  headings are taken shortest first and never include CHAPTER / part / Schedule / Act-title /
      all-caps lines or a line starting with a digit.
  M4  no section starts inside the Schedules region.
  M5  table rows may be indented with NBSP + space.
  M6  'N.--...' / 'N. -...' is a numbered part heading, not a section start.
  M7  R2 also ends a section at an all-caps Act title line.

fold_for_diff() (fold v2) is for Part C edition diffs only and is never applied to stored bodies.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

EXTRACTOR_VERSION = "v2"
FOLD_VERSION = "v2"

PACKAGE_DIR = Path(__file__).resolve().parent
STATUTES_DIR = PACKAGE_DIR / "statutes"
LOCAL_DIR = STATUTES_DIR / "_local_text"
RAW_DIR = LOCAL_DIR / "_raw"
CACHE_DIR = LOCAL_DIR / "cache" / "pages"
CENSUS_DIR = LOCAL_DIR / "census"

EDITIONS = {
    "1961": ["ita1961_2023", "ita1961_2024n1", "ita1961_2024n2", "ita1961_2025", "ita1961_2026"],
    "2025": ["ita2025_2025", "ita2025_2026"],
}
PILOT = {"1961": ["115BBH", "194S", "2", "285BAA"], "2025": ["194", "393"]}

# ---------------------------------------------------------------- R0 / R3 patterns (printed at the STOP)
DUP_MIN_CHARS = 200
FURNITURE_EXACT = ("Income Tax Department", "Ministry of Finance, Government of India")
FURNITURE_RE = (
    re.compile(r"^Downloaded/Printed on \d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} (?:am|pm|AM|PM) from "
               r"www\.incometaxindia\.gov\.in(?: Page \d+ of \d+)?$"),
    re.compile(r"^\d{1,4}$"),
)
FURNITURE_TOP, FURNITURE_BOTTOM = 2, 3
FOOTNOTE_START = re.compile(
    r"^\s*\d+[a-z]?\.\s+(?:Ins\.|Sub\.|Subs\.|Omtt\.|Omitted by|Inserted by|Substituted by|Substituted for|"
    r"Proviso omtt\.|Italicised words|Words\s+[\"“]|Prior to|Re-numbered|Renumbered|See rule|See also|"
    r"Sections? .{0,80}?inserted by)")

# ---------------------------------------------------------------- R1 / R2 / R5 / R4 patterns
START_RE = re.compile(r"^\s*(\d{1,3}[A-Z]{0,5})\s?\.(?=\s|$|\()")
HEADING_FIRST_RE = re.compile(r"^[A-Z\[“\"‘']")
NOT_HEADING_RE = re.compile(r"^\[?(?:Explanation|Provided)")
ALLCAPS_RE = re.compile(r"^[^a-z]*[A-Z]{3,}[^a-z]*$")
CHAPTER_RE = re.compile(r"^\s*CHAPTER\s+[IVXLC]+(?:[\-–]?[A-Z]{1,3})?\s*$")
PART_RE = re.compile(r"^\s*[A-Z]{1,2}\.\s?[—–-]\s?\S")
ACT_TITLE_RE = re.compile(r"^\s*[A-Z][A-Z\-() ]*ACT, \d{4}\*?\s*$")
SCHEDULE_LINE_RE = re.compile(r"^\s*(?:THE\s+[A-Z]+\s+)?SCHEDULE(?:\s+[IVXL]+)?\s*$")
TABLE_START_RE = re.compile(r"^\s*(?:TABLE|Table)\s*$")
TABLE_END_RE = re.compile(r"^\[?(?:\(\d+[A-Z]*\)\s|Explanation)")          # P09-31 (unindented)
SUBSECTION_LINE_RE = re.compile(r"^\[?\(\d+[A-Z]*\)\s")                       # unindented '(n) ' / '[(n) '
# ---------------------------------------------------------------- v2 patterns (P09-29 .. P09-41)
BARE_MARKER_RE = re.compile(r"^\d+[a-z]?(?: \d+[a-z]?)*$")                    # P09-29 (on the stripped line)
INLINE_MARKER_RE = re.compile(r"\b(\d+[a-z]?)(?=\[)")                         # P09-41
FOOTNOTE_NUMBER_RE = re.compile(r"^\s*(\d+[a-z]?)\.\s")                       # P09-29b (inside footnote blocks)
DIVIDER_RE = re.compile(r"^[_\-—]{3,}$")                                      # P09-32 (on the stripped line)
HYPHEN_END_RE = re.compile(r"[^\W\d_]-$")                                     # P09-33b: ASCII '-' after a letter
EDITOR_NOTE_RE = re.compile(r"shall be (?:inserted|substituted|omitted|renumbered)")   # P09-35
TABLE_PREFIX_RE = re.compile(r"^\[Table \d+ Sl\. \d+\] ")
ROW_RE = re.compile(r"^\s*(\d{1,2})\.\s")
PART_NUMBER_RE = re.compile(r"^\s*\d{1,3}[A-Z]{0,5}\s?\.\s*[—–-]")
NUMBERED_RE = re.compile(r"^\s*\d{1,2}\.\s")
SUBSECTION_RE = re.compile(r"^\s*(?:\d{1,3}[A-Z]{0,5}\s?\.\s*)?\((\d+[A-Z]*)\)\s")
SPACES_RE = re.compile("[ \t  -   　]+")
TERMINAL = (".", ":", ";", "—", "–")


# ---------------------------------------------------------------- data

@dataclass
class Line:
    page: int          # page_1based
    text: str
    line_no: int = 0   # line_1based within the raw pypdf page text


@dataclass
class Cleaned:
    lines: list
    notes: dict                                    # page_1based -> footnote lines (verbatim)
    furniture: list = field(default_factory=list)  # (page_1based, line) removed
    midpage_footnote_pages: list = field(default_factory=list)
    footnote_lines: int = 0
    rule_drops: list = field(default_factory=list)  # (page_1based, line_1based, rule, text) [P09-32]


@dataclass
class Start:
    idx: int
    number: str
    heading: str
    heading_idx: int


@dataclass
class Trace:
    """Before/after examples per rule, for --show-rules."""
    items: dict = field(default_factory=lambda: {"R3-furniture": [], "R3-footnote": [], "R5": [],
                                                 "R4-space": [], "R4-join": []})

    def add(self, rule, before, after):
        if len(self.items[rule]) < 3:
            self.items[rule].append((before, after))


def page_1based(idx0: int) -> int:
    """The ONE conversion from pypdf's 0-based page index to the 1-based viewer page [P09-40]."""
    if idx0 < 0:
        raise ValueError(f"bad 0-based page index {idx0}")
    return idx0 + 1


def idx0_from_page(page: int) -> int:
    """Inverse of page_1based()."""
    if page < 1:
        raise ValueError(f"bad 1-based page {page}")
    return page - 1


def section_key(num: str) -> tuple:
    m = re.match(r"^(\d+)([A-Z]*)$", num)
    if not m:
        raise ValueError(f"bad section number {num!r}")
    return int(m.group(1)), m.group(2)


# ---------------------------------------------------------------- R0

def drop_duplicate_pages(pages: list) -> tuple:
    """R0: returns (kept_pages, dropped) where dropped = [(page_1based, duplicate_of_page_1based)];
    page positions are kept."""
    first_seen, kept, dropped = {}, [], []
    for idx0, text in enumerate(pages):
        pno = page_1based(idx0)
        if len(text.strip()) >= DUP_MIN_CHARS and text in first_seen:
            dropped.append((pno, first_seen[text]))
            kept.append("")
            continue
        first_seen.setdefault(text, pno)
        kept.append(text)
    return kept, dropped


# ---------------------------------------------------------------- R3

def _is_furniture(s: str) -> bool:
    return s in FURNITURE_EXACT or any(r.match(s) for r in FURNITURE_RE)


def _body_resumes(page_lines: list) -> set:
    """Indices (within one page) where a heading + section start pair or a boundary line begins."""
    out = set()
    for k, ln in enumerate(page_lines):
        if _boundary(ln.text.strip()):
            out.add(k)
            continue
        if START_RE.match(ln.text) and not FOOTNOTE_START.match(ln.text) and not PART_NUMBER_RE.match(ln.text):
            h = _heading_before(page_lines, k)
            if h:
                out.add(h[1])
    return out


def clean_pages(pages: list, trace: Trace | None = None) -> Cleaned:
    """R3 on every page. pages[idx0] is the raw text of page page_1based(idx0)."""
    out, notes, furn, midpage, n_foot, rule_drops = [], {}, [], [], 0, []
    for idx0, text in enumerate(pages):
        pno = page_1based(idx0)
        raw = text.splitlines()
        nonempty = [i for i, ln in enumerate(raw) if ln.strip()]
        edge = set(nonempty[:FURNITURE_TOP]) | set(nonempty[-FURNITURE_BOTTOM:])
        kept = []
        for i, ln in enumerate(raw):
            if i in edge and _is_furniture(ln.strip()):
                furn.append((pno, ln.strip()))
                if trace:
                    trace.add("R3-furniture", f"p{pno}: {ln.strip()}", "(removed)")
                continue
            if DIVIDER_RE.match(ln.strip()):                       # P09-32, anywhere on the page
                rule_drops.append((pno, i + 1, "P09-32 divider", ln.strip()))
                continue
            if ln.strip():
                kept.append(Line(pno, ln, i + 1))
        resumes = _body_resumes(kept)
        in_foot, body, foot = False, [], []
        for k, ln in enumerate(kept):
            if FOOTNOTE_START.match(ln.text):
                in_foot = True
                if trace:
                    trace.add("R3-footnote", f"p{pno}: {ln.text.strip()[:90]}", "(moved to amendment_note)")
            elif in_foot and k in resumes:
                in_foot = False
                if pno not in midpage:
                    midpage.append(pno)
            (foot if in_foot else body).append(ln)
        if foot:
            notes[pno] = [ln.text for ln in foot]
            n_foot += len(foot)
        out.extend(body)
    return Cleaned(out, notes, furn, midpage, n_foot, rule_drops)


# ---------------------------------------------------------------- R5 state machine (shared by R1 and R5)

def table_marks(lines: list) -> tuple:
    """Returns (marks, tables). marks: idx -> ('row', k, N) | ('unresolved', reason);
    tables: [{'k', 'start' (idx of the TABLE line), 'end' (idx of the last line inside the table)}].
    v2 [P09-31]: integer rows only; roman sub-items are not labelled; the sequence check is on integers.
    A table ends at an unindented '(n)' / '[(n)' or 'Explanation' line, a CHAPTER line, a real section
    start, or the end of `lines` (the section end when called on one section)."""
    marks, tables = {}, []
    in_table, last_row = False, 0

    def close(i_end):
        tables[-1]["end"] = i_end

    for i, ln in enumerate(lines):
        t = ln.text
        if TABLE_START_RE.match(t):
            if in_table:
                close(i - 1)
            in_table, last_row = True, 0
            tables.append({"k": len(tables) + 1, "start": i, "end": None})
            continue
        if not in_table:
            continue
        k = len(tables)
        if CHAPTER_RE.match(t) or TABLE_END_RE.match(t):
            in_table = False
            close(i - 1)
            continue
        m = ROW_RE.match(t)
        if m and int(m.group(1)) == last_row + 1:
            last_row += 1
            marks[i] = ("row", k, last_row)
            continue
        if START_RE.match(t) and _heading_before(lines, i):
            in_table = False          # a real section start ends the table
            close(i - 1)
            continue
        if NUMBERED_RE.match(t):
            marks[i] = ("unresolved", f"non-sequential numbered line in table {k} (last row {last_row})")
    if in_table:
        close(len(lines) - 1)
    return marks, tables


# ---------------------------------------------------------------- R1 / R2

def _heading_before(lines: list, i: int):
    """(heading, first_idx) if lines[i] is preceded by a valid heading block, else None."""
    j = i - 1
    if j < 0:
        return None
    last = lines[j].text.strip()
    if not last.endswith(".") or len(last) > 200 or last[:1].isdigit():
        return None
    # shortest heading first: the line itself, else wrap back over up to 2 lines that do not end a
    # sentence and are not CHAPTER / part / Schedule / Act-title / all-caps / digit-led lines
    block = [j]
    while True:
        first = lines[block[0]].text.strip()
        if HEADING_FIRST_RE.match(first) and not ALLCAPS_RE.match(first) and not _boundary(first):
            if NOT_HEADING_RE.match(first):
                return None
            text = " ".join(SPACES_RE.sub(" ", lines[b].text).strip() for b in block)
            return text, block[0]
        k = block[0] - 1
        if len(block) >= 3 or k < 0:
            return None
        prev = lines[k].text.strip()
        if prev.endswith(TERMINAL) or ALLCAPS_RE.match(prev) or _boundary(prev) or prev[:1].isdigit():
            return None
        block.insert(0, k)


def schedules_from(lines: list) -> int:
    """Index of the first standalone SCHEDULE line (Schedules region runs to the end), else len(lines)."""
    return next((i for i, ln in enumerate(lines) if SCHEDULE_LINE_RE.match(ln.text)), len(lines))


def find_starts(lines: list) -> list:
    marks, _ = table_marks(lines)
    stop = schedules_from(lines)
    starts = []
    for i, ln in enumerate(lines[:stop]):
        m = START_RE.match(ln.text)
        if not m or i in marks or FOOTNOTE_START.match(ln.text) or PART_NUMBER_RE.match(ln.text):
            continue
        h = _heading_before(lines, i)
        if h:
            starts.append(Start(i, m.group(1), h[0], h[1]))
    return starts


def _boundary(t: str) -> bool:
    return bool(CHAPTER_RE.match(t) or PART_RE.match(t) or SCHEDULE_LINE_RE.match(t) or ACT_TITLE_RE.match(t))


def locate(lines: list, starts: list, number: str) -> dict:
    hits = [s for s in starts if s.number == number]
    cands = [{"page_1based": lines[s.idx].page, "heading": s.heading[:60]} for s in hits]
    if len(hits) != 1:
        return {"status": "NOT_FOUND" if not hits else "UNRESOLVED", "candidates": cands}
    s = hits[0]
    key = section_key(number)
    end = len(lines)
    for t in starts:
        if t.idx > s.idx and section_key(t.number) > key:
            end = t.heading_idx
            break
    for j in range(s.idx + 1, end):
        if _boundary(lines[j].text):
            end = j
            break
    pages = sorted({ln.page for ln in lines[s.idx:end]})
    return {"status": "FOUND", "internal_line_idx0_start": s.idx, "internal_line_idx0_end": end,
            "internal_heading_line_idx0": s.heading_idx, "heading": s.heading, "pages_1based": pages,
            "candidates": cands}


# ---------------------------------------------------------------- M: footnote markers + editor notes (one section)

def footnote_numbers(notes: dict, p_first: int, p_last: int) -> set:
    """P09-29a/29b: the leading 'N.' / 'Na.' of ANY line inside an R3 footnote block on pages
    p_first .. p_last + 1 (page_1based)."""
    out = set()
    for p in range(p_first, p_last + 2):
        for ln in notes.get(p, []):
            m = FOOTNOTE_NUMBER_RE.match(ln)
            if m:
                out.add(m.group(1))
    return out


def footnotes_raw(notes: dict, p_first: int, p_last: int) -> list:
    """P09-30: [{page_1based, number, text}] split at every numbered line (P09-29b); a continuation at
    the top of a page joins the previous entry. Local meta only; never a date source."""
    out = []
    for p in range(p_first, p_last + 2):
        for ln in notes.get(p, []):
            m = FOOTNOTE_NUMBER_RE.match(ln)
            if m or not out:
                out.append({"page_1based": p, "number": m.group(1) if m else None, "text": ln.strip()})
            else:
                out[-1]["text"] += "\n" + ln.strip()
    return out


def apply_markers(seg: list, numbers: set) -> tuple:
    """P09-29 (line markers) then P09-41 (inline markers). Returns (lines, dropped, unresolved, inline_found);
    dropped / unresolved entries: {type, page_1based, line_1based, numbers[, missing][, context]}."""
    kept, dropped, unresolved, inline_found = [], [], [], 0
    for ln in seg:
        s = ln.text.strip()
        if BARE_MARKER_RE.match(s):
            nums = s.split()
            missing = [n for n in nums if n not in numbers]
            entry = {"type": "line", "page_1based": ln.page, "line_1based": ln.line_no, "numbers": nums}
            if missing:
                unresolved.append(dict(entry, missing=missing))
                kept.append(ln)
            else:
                dropped.append(entry)
            continue
        text = ln.text
        for m in reversed(list(INLINE_MARKER_RE.finditer(text))):
            inline_found += 1
            entry = {"type": "inline", "page_1based": ln.page, "line_1based": ln.line_no, "numbers": [m.group(1)]}
            if m.group(1) in numbers:
                dropped.append(entry)
                text = text[:m.start()] + text[m.end():]
            else:
                unresolved.append(dict(entry, missing=[m.group(1)],
                                       context=text[max(0, m.start() - 25):m.end() + 25].strip()))
        kept.append(ln if text == ln.text else Line(ln.page, text, ln.line_no))
    return kept, dropped, unresolved, inline_found


def editor_note_candidates(seg: list) -> list:
    """P09-35: candidate blocks, listed only (never cut here). A block starts at a line with
    'shall be inserted/substituted/omitted/renumbered' when 'w.e.f.' is on it or on one of the next 2 lines;
    it runs from there to the next bare marker line, unindented sub-section line, or the section end."""
    out, i = [], 0
    while i < len(seg):
        if EDITOR_NOTE_RE.search(seg[i].text):
            head_end = next((j for j in range(i, min(i + 3, len(seg))) if "w.e.f." in seg[j].text), None)
            if head_end is not None:
                j = head_end + 1
                while j < len(seg) and not BARE_MARKER_RE.match(seg[j].text.strip()) \
                        and not SUBSECTION_LINE_RE.match(seg[j].text):
                    j += 1
                out.append({"page_1based": seg[i].page, "line_1based": seg[i].line_no,
                            "text": "\n".join(SPACES_RE.sub(" ", x.text).strip() for x in seg[i:j])})
                i = j
                continue
        i += 1
    return out


def bracket_counts(body: str) -> dict:
    """P09-36: '[' and ']' in the body, our own '[Table k Sl. N] ' prefixes excluded."""
    plain = "\n".join(TABLE_PREFIX_RE.sub("", ln) for ln in body.split("\n"))
    o, c = plain.count("["), plain.count("]")
    return {"open": o, "close": c, "warn": o != c}


# ---------------------------------------------------------------- R5 + R4 on one section

def apply_tables(lines: list, trace: Trace | None = None) -> tuple:
    """R5: returns (texts, rows_prefixed, unresolved, table_map).
    table_map: [{'table': k, 'page_1based', 'end_page_1based', 'subsection', 'start_idx', 'end_idx'}]
    (start_idx / end_idx index `lines`; extract_section converts them to body lines)."""
    marks, tables = table_marks(lines)
    table_map = []
    texts, rows, unresolved = [], 0, []
    subsection = None
    by_start = {t["start"]: t for t in tables}
    for i, ln in enumerate(lines):
        sm = SUBSECTION_RE.match(ln.text.lstrip("["))
        if sm and not ln.text.startswith((" ", "\t", " ")):
            subsection = f"({sm.group(1)})"
        if i in by_start:
            t = by_start[i]
            table_map.append({"table": t["k"], "page_1based": ln.page, "end_page_1based": lines[t["end"]].page,
                              "subsection": subsection, "start_idx": t["start"], "end_idx": t["end"]})
        mk = marks.get(i)
        if mk and mk[0] == "row":
            new = f"[Table {mk[1]} Sl. {mk[2]}] " + ln.text.strip()
            rows += 1
        else:
            new = ln.text
            if mk:
                unresolved.append(f"p{ln.page}: {mk[1]}: {ln.text.strip()[:70]}")
        if trace and new != ln.text:
            trace.add("R5", ln.text.strip()[:70], new[:90])
        texts.append(new)
    return texts, rows, unresolved, table_map


def _first_diff_snippet(a: str, b: str, width: int = 60) -> tuple:
    i = next((k for k, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    lo = max(0, i - width // 2)
    return a[lo:lo + width], b[lo:lo + width]


def normalise_lines(texts: list, trace: Trace | None = None) -> tuple:
    """R4 v2 [P09-33/33b/34]: keep line breaks; collapse runs of spaces inside a line; drop empty lines;
    the ONLY join: a line ending in an ASCII '-' directly after a letter is joined to the next line with no
    space (hyphen kept), never into a line that starts with a table-row prefix.
    Returns (lines, idx_map, hyphen_joins, hyphen_not_joined); idx_map: input index -> body_line_1based."""
    out, idx_map, joins, not_joined, pending = [], {}, 0, 0, False
    for i, t in enumerate(texts):
        s = SPACES_RE.sub(" ", t).strip()
        if trace and s != t.strip():
            before, after = _first_diff_snippet(t.strip(), s)
            trace.add("R4-space", repr(before), repr(after))
        if not s:
            idx_map[i] = max(len(out), 1)
            continue
        if pending and TABLE_PREFIX_RE.match(s):
            not_joined += 1
            out.append(s)
        elif pending:
            if trace:
                trace.add("R4-join", f"{out[-1][-40:]!r} + {s[:40]!r}", repr((out[-1] + s)[-80:]))
            out[-1] = out[-1] + s
            joins += 1
        else:
            out.append(s)
        idx_map[i] = len(out)
        pending = bool(HYPHEN_END_RE.search(out[-1]))
    return out, idx_map, joins, not_joined


def normalise(texts: list, trace: Trace | None = None) -> str:
    """R4 v2 as a body string (LF, ends with one newline)."""
    out = normalise_lines(texts, trace)[0]
    return "\n".join(out) + "\n" if out else ""


def extract_section(cleaned: Cleaned, starts: list, number: str, trace: Trace | None = None) -> dict:
    loc = locate(cleaned.lines, starts, number)
    if loc["status"] != "FOUND":
        return loc
    lines = cleaned.lines
    seg = lines[loc["internal_line_idx0_start"]:loc["internal_line_idx0_end"]]
    p0, p1 = loc["pages_1based"][0], loc["pages_1based"][-1]
    numbers = footnote_numbers(cleaned.notes, p0, p1)
    editor = editor_note_candidates(seg)                                   # P09-35: listed, not cut
    seg, m_dropped, m_unres, inline_found = apply_markers(seg, numbers)    # P09-29 / P09-41
    texts, rows, unresolved, table_map = apply_tables(seg, trace)          # R5
    out, idx_map, joins, not_joined = normalise_lines(texts, trace)        # R4
    heading, opened = loc["heading"], False                                # P09-36
    hidx = loc["internal_heading_line_idx0"]
    if heading.startswith("["):
        heading, opened = heading[1:], True
    elif hidx > 0 and lines[hidx - 1].text.strip() == "[":
        opened = True
    if opened and out:
        out[0] = "[" + out[0]
    body = "\n".join(out) + "\n" if out else ""
    for t in table_map:
        t["start_body_line_1based"] = idx_map.get(t.pop("start_idx"))
        t["end_body_line_1based"] = idx_map.get(t.pop("end_idx"))
    note_lines = [f"[page_1based {p}] {ln.strip()}" for p in range(p0, p1 + 1) for ln in cleaned.notes.get(p, [])]
    loc.update({"heading": heading, "heading_bracket_moved_to_body": opened,
                "body": body, "chars": len(body), "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "table_rows": rows, "unresolved": unresolved, "tables": table_map,
                "amendment_note": "\n".join(note_lines) if note_lines else None,
                "footnotes_raw_note": "local only; never a date source; never in committed files",
                "footnotes_raw": footnotes_raw(cleaned.notes, p0, p1),
                "dropped_markers": m_dropped, "unresolved_markers": m_unres, "inline_markers_found": inline_found,
                "editor_note_candidates": editor, "brackets": bracket_counts(body),
                "hyphen_joins": joins, "hyphen_not_joined": not_joined})
    return loc


# ---------------------------------------------------------------- fold (Part C diffs only)

_DQ = dict.fromkeys(map(ord, "“”„‟″〝〞＂"), '"')
_SQ = dict.fromkeys(map(ord, "‘’‚‛′＇"), "'")
_LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}
RUPEE_RE = re.compile(r"(?:₹|\bRs\b\.?)\s*")


def fold_for_diff(text: str) -> str:
    """Fold v2 for edition diffs ONLY: curly/straight quotes and apostrophes, '₹'/'Rs.'/'Rs' -> one
    token, ligatures (ﬀ ﬁ ﬂ ﬃ ﬄ) -> letters [D5], and ALL whitespace (spaces, NBSP, newlines) collapsed
    to one space [P09-34]. Never applied to stored bodies."""
    s = text.translate(_DQ).translate(_SQ)
    for lig, letters in _LIGATURES.items():
        s = s.replace(lig, letters)
    s = RUPEE_RE.sub("<RUPEE> ", s)
    return " ".join(SPACES_RE.sub(" ", s).split())


# ---------------------------------------------------------------- page cache

def pypdf_version() -> str:
    import pypdf
    return str(pypdf.__version__)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pages(pdf: Path, cache_dir: Path = CACHE_DIR) -> list:
    """Raw pypdf text per page, cached as <sha>__pypdf-<ver>.jsonl (never overwritten)."""
    sha, ver = file_sha256(pdf), pypdf_version()
    cache = cache_dir / f"{sha}__pypdf-{ver}.jsonl"
    if cache.exists():
        rows = [json.loads(x) for x in cache.read_text(encoding="utf-8").splitlines()]
        head = rows[0]
        if head.get("pdf_sha256") == sha and head.get("pypdf_version") == ver and len(rows) - 1 == head["pages"]:
            return [r["text"] for r in rows[1:]]
        raise RuntimeError(f"cache file {cache.name} is inconsistent; not overwriting it")
    from pypdf import PdfReader
    reader = PdfReader(str(pdf))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    cache_dir.mkdir(parents=True, exist_ok=True)
    part = cache.with_suffix(".jsonl.part")
    with open(part, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"pdf_sha256": sha, "pypdf_version": ver, "pages": len(texts), "source": pdf.name}) + "\n")
        for idx0, t in enumerate(texts):      # cache format unchanged: "page" is 1-based
            f.write(json.dumps({"page": page_1based(idx0), "text": t}, ensure_ascii=False) + "\n")
    part.rename(cache)
    return texts


# ---------------------------------------------------------------- inputs

def latest_raw_dir() -> Path:
    dated = sorted(p for p in RAW_DIR.iterdir() if p.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", p.name))
    if not dated:
        raise FileNotFoundError(f"no dated folder in {RAW_DIR}")
    return dated[-1]


def targets() -> dict:
    """{'1961': [sections], '2025': [sections], 'schedules': [roman]} from SECTION-LIST.json + MAPPING.csv."""
    sl = json.loads((STATUTES_DIR / "SECTION-LIST.json").read_text(encoding="utf-8"))
    s1961 = [s["section"] for s in sl["sections_1961"]]
    s2025, sched = [], []
    with open(STATUTES_DIR / "MAPPING.csv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            for ref in row["section_2025"].split(";") + [row["operative_2025"]]:
                ref = ref.strip()
                if ref.startswith("Schedule "):
                    sched.append(ref.split()[1])
                elif ref:
                    s2025.append(ref)
    s2025 += [s["section"] for s in sl["sections_2025_only"]]
    return {"1961": s1961, "2025": sorted(set(s2025), key=section_key),
            "schedules": sorted(set(sched), key=lambda x: (len(x), x))}


def _prepare(args):
    key, pdf = args
    pages = load_pages(Path(pdf))
    return key, len(pages)


def prepare_all(raw: Path, jobs: int) -> None:
    work = [(k, str(raw / f"{k}.pdf")) for act in EDITIONS for k in EDITIONS[act]]
    if jobs <= 1:
        for w in work:
            print("cached", *_prepare(w), flush=True)
        return
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        for key, n in ex.map(_prepare, work):
            print("cached", key, n, flush=True)


@dataclass
class EditionView:
    key: str
    pages: list
    dropped: list
    cleaned: Cleaned
    starts: list


def edition_view(raw: Path, key: str, trace: Trace | None = None) -> EditionView:
    pages = load_pages(raw / f"{key}.pdf")
    kept, dropped = drop_duplicate_pages(pages)
    cleaned = clean_pages(kept, trace)
    return EditionView(key, pages, dropped, cleaned, find_starts(cleaned.lines))


def _write_new(path: Path, text: str) -> None:
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _census_counts(views: list) -> str:
    rows = [f"{'edition':<15} {'pages':>5} {'R0 dropped':>10} {'R3 midpage-footnote pages':>25} {'R3 footnote lines':>17}"]
    for v in views:
        rows.append(f"{v.key:<15} {len(v.pages):>5} {len(v.dropped):>10} {len(v.cleaned.midpage_footnote_pages):>25} "
                    f"{v.cleaned.footnote_lines:>17}")
    return "\n".join(rows) + "\n"


def _dropped_tsv(views: list) -> str:
    out = ["edition\tpage_1based\tduplicate_of_page_1based"]
    out += [f"{v.key}\t{p}\t{d}" for v in views for p, d in v.dropped]
    return "\n".join(out) + "\n"


def _rules_tsv(views: list) -> str:
    """P09-32: DROPPED-RULES.tsv (whole editions)."""
    out = ["file\tpage_1based\tline_1based\trule\ttext"]
    out += [f"{v.key}.pdf\t{p}\t{ln}\t{rule}\t{text}" for v in views for p, ln, rule, text in v.cleaned.rule_drops]
    return "\n".join(out) + "\n"


def _tsv_cell(s: str) -> str:
    return s.replace("\t", " ").replace("\n", " / ")


# ---------------------------------------------------------------- CLI actions

def run_locate_all(raw: Path, out_dir: Path) -> int:
    tg = targets()
    out_dir.mkdir(parents=True, exist_ok=False)
    lines_out = [f"LOCATE-ALL  extractor {EXTRACTOR_VERSION}  pypdf {pypdf_version()}  raw={raw}",
                 f"{'act':<5} {'section':<10} {'edition':<15} {'status':<10} {'n':>2} {'pages_1based':<16} heading"]
    counts, views = {}, []
    for act in ("1961", "2025"):
        for key in EDITIONS[act]:
            v = edition_view(raw, key)
            views.append(v)
            for sec in tg[act]:
                r = locate(v.cleaned.lines, v.starts, sec)
                counts[r["status"]] = counts.get(r["status"], 0) + 1
                if r["status"] == "FOUND":
                    pg = f"{r['pages_1based'][0]}-{r['pages_1based'][-1]}"
                    head = r["heading"][:60]
                else:
                    pg = ",".join(str(c["page_1based"]) for c in r["candidates"][:6]) or "-"
                    head = " | ".join(c["heading"] for c in r["candidates"][:3])
                lines_out.append(f"{act:<5} {sec:<10} {key:<15} {r['status']:<10} {len(r['candidates']):>2} {pg:<16} {head}")
            if act == "2025":
                for roman in tg["schedules"]:
                    pat = re.compile(r"^\s*SCHEDULE\s+" + roman + r"\s*$")
                    hits = sorted({ln.page for ln in v.cleaned.lines if pat.match(ln.text)})
                    st = "FOUND" if len(hits) == 1 else ("NOT_FOUND" if not hits else "UNRESOLVED")
                    counts[st] = counts.get(st, 0) + 1
                    lines_out.append(f"{act:<5} {'Sch ' + roman:<10} {key:<15} {st:<10} {len(hits):>2} "
                                     f"{','.join(map(str, hits)) or '-':<16}")
    lines_out.append("totals: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    text = "\n".join(lines_out) + "\n\nR0 / R3 COUNTS\n" + _census_counts(views)
    print(text, end="")
    _write_new(out_dir / "LOCATE-ALL.txt", text)
    _write_new(out_dir / "DROPPED-PAGES.tsv", _dropped_tsv(views))
    _write_new(out_dir / "DROPPED-RULES.tsv", _rules_tsv(views))
    print(f"written {out_dir / 'LOCATE-ALL.txt'}, DROPPED-PAGES.tsv and DROPPED-RULES.tsv")
    return 0


def run_pilot(raw: Path, out_dir: Path, trace: Trace | None = None) -> list:
    out_dir.mkdir(parents=True, exist_ok=False)
    results, views, unresolved_md = [], [], ["# UNRESOLVED (pilot)", ""]
    for act, secs in PILOT.items():
        for key in EDITIONS[act]:
            v = edition_view(raw, key, trace)
            views.append(v)
            for sec in secs:
                r = extract_section(v.cleaned, v.starts, sec, trace)
                r.update({"act": act, "section": sec, "edition": key})
                stem = f"{act}__s{sec}__{key}"
                r["stem"] = stem
                if r["status"] == "FOUND":
                    _write_new(out_dir / f"{stem}.txt", r["body"])
                    r["page_chars_1based"] = {p: len(v.pages[idx0_from_page(p)]) for p in r["pages_1based"]}
                meta = {k: val for k, val in r.items() if k not in ("body", "stem")}
                meta["extractor_version"] = EXTRACTOR_VERSION
                _write_new(out_dir / f"{stem}.meta.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
                warn = r.get("brackets", {}).get("warn")
                if r["status"] != "FOUND" or r.get("unresolved") or warn:
                    unresolved_md.append(f"## {stem}: {r['status']}")
                    if r["status"] != "FOUND":
                        unresolved_md += [f"- candidate page_1based {c['page_1based']}: {c['heading']}"
                                          for c in r["candidates"]]
                    unresolved_md += [f"- {u}" for u in r.get("unresolved", [])]
                    if warn:
                        b = r["brackets"]
                        unresolved_md.append(f"- BRACKET WARN: '[' = {b['open']}, ']' = {b['close']}")
                    unresolved_md.append("")
                results.append(r)
    found = [r for r in results if r["status"] == "FOUND"]
    _write_new(out_dir / "UNRESOLVED.md", "\n".join(unresolved_md) + "\n")
    _write_new(out_dir / "DROPPED-PAGES.tsv", _dropped_tsv(views))
    _write_new(out_dir / "DROPPED-RULES.tsv", _rules_tsv(views))
    mk = ["file\tsection\ttype\tpage_1based\tline_1based\tnumbers"]
    mk += [f"{r['edition']}.pdf\t{r['act']} s.{r['section']}\t{d['type']}\t{d['page_1based']}\t{d['line_1based']}\t"
           f"{' '.join(d['numbers'])}" for r in found for d in r["dropped_markers"]]
    _write_new(out_dir / "DROPPED-MARKERS.tsv", "\n".join(mk) + "\n")
    um = ["# UNRESOLVED MARKERS (pilot)", "",
          "Bare-number lines and inline markers whose numbers are not all footnote numbers on the section's",
          "pages + 1 page (P09-29a/29b, P09-41). They stay in the body.", ""]
    for r in found:
        if r["unresolved_markers"]:
            um.append(f"## {r['stem']}")
            for u in r["unresolved_markers"]:
                ctx = f" | context: {u['context']}" if u.get("context") else ""
                um.append(f"- {u['type']} page_1based {u['page_1based']} line_1based {u['line_1based']}: "
                          f"numbers {' '.join(u['numbers'])}; missing {' '.join(u['missing'])}{ctx}")
            um.append("")
    _write_new(out_dir / "UNRESOLVED-MARKERS.md", "\n".join(um) + "\n")
    ed = ["# EDITOR-NOTES CANDIDATES (pilot, P09-35)", "",
          "Listed only; nothing has been removed from any body. Owner confirms before any move.", ""]
    for r in found:
        for c in r["editor_note_candidates"]:
            ed += [f"## {r['edition']}.pdf  {r['act']} s.{r['section']}  page_1based {c['page_1based']}  "
                   f"line_1based {c['line_1based']}", "", "```", c["text"], "```", ""]
    _write_new(out_dir / "EDITOR-NOTES-CANDIDATES.md", "\n".join(ed) + "\n")
    tmap = ["# TABLE MAP (pilot)", ""]
    for r in found:
        if r["tables"]:
            tmap.append(f"## {r['act']} s.{r['section']} {r['edition']}")
            tmap += [f"- Table {t['table']}: page_1based {t['page_1based']}-{t['end_page_1based']}, "
                     f"in {t['subsection'] or '(no sub-section)'}, body_line_1based "
                     f"{t['start_body_line_1based']}-{t['end_body_line_1based']}" for t in r["tables"]]
            tmap.append("")
    _write_new(out_dir / "TABLE-MAP.md", "\n".join(tmap) + "\n")
    return results, views


def _has_span(t: dict) -> bool:
    return bool(t["start_body_line_1based"] and t["end_body_line_1based"])


def pilot_counts(results: list, views: list) -> str:
    found = [r for r in results if r["status"] == "FOUND"]

    def n(kind, field_, cond=lambda d: True):
        return sum(1 for r in found for d in r[field_] if d["type"] == kind and cond(d))
    lines = [
        f"markers dropped: line={n('line', 'dropped_markers')} inline={n('inline', 'dropped_markers')}",
        f"unresolved markers: line={n('line', 'unresolved_markers')} inline={n('inline', 'unresolved_markers')}",
        f"inline markers: before={sum(r['inline_markers_found'] for r in found)} "
        f"after (left in bodies)={n('inline', 'unresolved_markers')}",
        "divider lines dropped (whole editions): "
        + ", ".join(f"{v.key}={len(v.cleaned.rule_drops)}" for v in views),
        f"editor-note candidates: {sum(len(r['editor_note_candidates']) for r in found)}",
        f"bracket WARNs: {sum(1 for r in found if r['brackets']['warn'])} "
        + str([r["stem"] for r in found if r["brackets"]["warn"]]),
        f"tables with start/end: {sum(1 for r in found for t in r['tables'] if _has_span(t))}"
        f" of {sum(len(r['tables']) for r in found)}",
        f"hyphen joins: {sum(r['hyphen_joins'] for r in found)}  not joined (table row): "
        f"{sum(r['hyphen_not_joined'] for r in found)}",
    ]
    return "\n".join(lines) + "\n"


def print_pilot(results: list) -> None:
    print(f"{'act':<5} {'sec':<7} {'edition':<15} {'found':<5} {'pages_1based':<12} {'chars':>6} {'tbls':>4} "
          f"{'rows':>4} {'unres':>5} {'mk-':>3} {'mk?':>3} {'ed':>2} {'[]':>5} sha256")
    for r in results:
        if r["status"] == "FOUND":
            pg = f"{r['pages_1based'][0]}-{r['pages_1based'][-1]}"
            b = r["brackets"]
            br = f"{b['open']}/{b['close']}" + ("!" if b["warn"] else "")
            print(f"{r['act']:<5} {r['section']:<7} {r['edition']:<15} {'yes':<5} {pg:<12} {r['chars']:>6} "
                  f"{len(r['tables']):>4} {r['table_rows']:>4} {len(r['unresolved']):>5} {len(r['dropped_markers']):>3} "
                  f"{len(r['unresolved_markers']):>3} {len(r['editor_note_candidates']):>2} {br:>5} {r['sha256']}")
        else:
            print(f"{r['act']:<5} {r['section']:<7} {r['edition']:<15} {'NO':<5} {r['status']:<12} "
                  f"candidates={[c['page_1based'] for c in r['candidates']]}")


def _word_diff(old: str, new: str, context: int = 6) -> list:
    a, b = old.split(), new.split()
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        pre = " ".join(a[max(0, i1 - context):i1])
        post = " ".join(a[i2:i2 + context])
        out.append(f"- ...{pre} [-{' '.join(a[i1:i2])}-] {post}...")
        out.append(f"+ ...{pre} {{+{' '.join(b[j1:j2])}+}} {post}...")
    return out


def pilot_diff(old_dir: Path, new_dir: Path) -> Path:
    """PILOT-DIFF.md: per pilot body, a unified line diff (old vs new) and a word-level diff [Q1]."""
    names = sorted({p.name for p in old_dir.glob("*.txt")} | {p.name for p in new_dir.glob("*.txt")})
    out = ["# PILOT DIFF", "", f"old: {old_dir}", f"new: {new_dir}", ""]
    for name in names:
        po, pn = old_dir / name, new_dir / name
        old = po.read_text(encoding="utf-8") if po.exists() else ""
        new = pn.read_text(encoding="utf-8") if pn.exists() else ""
        out += [f"## {name}", ""]
        if old == new:
            out += ["identical", ""]
            continue
        out += ["### line diff", "", "```diff"]
        udiff = difflib.unified_diff(old.splitlines(), new.splitlines(), f"old/{name}", f"new/{name}", lineterm="")
        out += [ln.rstrip("\n") for ln in udiff]
        out += ["```", "", "### word diff (whitespace and line breaks ignored)", "", "```"]
        wd = _word_diff(old, new)
        out += wd if wd else ["no word-level change (line breaks / spacing only)"]
        out += ["```", ""]
    path = new_dir / "PILOT-DIFF.md"
    _write_new(path, "\n".join(out) + "\n")
    return path


def print_rules(trace: Trace) -> None:
    print(f"EXTRACTOR {EXTRACTOR_VERSION} RULES (order R0 -> R3 -> R1/R2 -> M -> R5 -> R4 -> B)")
    print("R0 duplicate pages: identical extracted text to an earlier page and >=", DUP_MIN_CHARS, "chars")
    print("R3 furniture exact:", list(FURNITURE_EXACT))
    print("R3 furniture patterns:", [r.pattern for r in FURNITURE_RE],
          f"(first {FURNITURE_TOP} / last {FURNITURE_BOTTOM} lines)")
    print("R3 footnote start:", FOOTNOTE_START.pattern)
    for rule, items in trace.items.items():
        print(f"-- {rule}")
        for before, after in items:
            print(f"   before: {before}")
            print(f"   after:  {after}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m divergence.statute_extract", description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true", help="build the page-text cache for all editions")
    mode.add_argument("--locate-all", action="store_true")
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument("--show-rules", action="store_true")
    mode.add_argument("--pilot-diff", nargs=2, metavar=("OLD_DIR", "NEW_DIR"))
    ap.add_argument("--raw-dir", help="download folder (default: newest dated folder under _raw/)")
    ap.add_argument("--jobs", type=int, default=1, help="--prepare: parallel processes")
    args = ap.parse_args(argv)
    if args.pilot_diff:
        path = pilot_diff(Path(args.pilot_diff[0]), Path(args.pilot_diff[1]))
        print(f"written {path}")
        return 0
    raw = Path(args.raw_dir) if args.raw_dir else latest_raw_dir()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if args.prepare:
        prepare_all(raw, args.jobs)
        return 0
    if args.locate_all:
        return run_locate_all(raw, CENSUS_DIR / "locate" / stamp)
    if args.pilot:
        out = CENSUS_DIR / "pilot" / stamp
        results, views = run_pilot(raw, out)
        print_pilot(results)
        print(pilot_counts(results, views), end="")
        print(f"written {out}")
        return 0
    trace = Trace()
    run_pilot(raw, CENSUS_DIR / "pilot" / f"{stamp}-rules", trace)
    print_rules(trace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
