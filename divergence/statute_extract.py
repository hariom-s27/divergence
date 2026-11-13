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

Extractor v3 changes (owner decisions P09-42 .. P09-44, approved with Q1 guard, Q2 line markers only):
  P09-42  brackets are matched over the WHOLE edition (kept lines after R0/R3, page order) with a stack.
      Each section records carry_in (open depth at its first heading line), carry_out (depth after its last
      line) and the edition-level orphans inside it (a ']' with nothing open, or a '[' never closed before
      the end of the file). WARN = an orphan only; the v2 per-section count WARN is removed.
  P09-43  job 1: a bare LINE marker token 'Na' (digits + one letter) is also dropped when footnote 'N' or a
      sibling 'N<letter>' exists in the P09-29a range ('matched_by_family', logged). Job 2: markers (body
      order) are linked to footnote entries (block order): by number when the number occurs exactly once in
      the range ('number'); unnumbered entries between numbered entries N and M are assigned in order to the
      unlinked markers between the markers of N and M ONLY when the counts are equal ('assigned_by_order');
      otherwise unresolved. Unnumbered split: a new entry starts after a line ending in '.', except (Q1
      guard) a line after one ending in ':' or a line starting with a quote mark or '(' stays a continuation.
  P09-44  in a footnote block a line starting with '*', '†' or '‡' starts its own footnotes_raw entry
      (field 'symbol'); body symbols stay as printed; both are counted.

Extractor v4 changes (owner decisions P09-43b, P09-46 with Q1 (b), P09-47):
  P09-46  a bare-digit line in the first 2 / last 3 non-empty lines of a page is no longer removed outright.
      If it equals a footnote number on its page or the next page (family rule) it is a 'marker' and goes to
      the normal marker rule; only the remaining digits can form a page-number sequence (value - page_1based
      constant on >= 5 consecutive pages at the same edge), which is removed as furniture; every other one
      stays in the body ('unresolved'). Every case is logged (PAGE-EDGE-DIGITS.tsv). A bare-number line never
      joins an R3 footnote block.
  P09-43b the unnumbered-entry split also keeps a line as a continuation when it starts with a lowercase
      letter or a digit (in addition to a quote mark, '(' or a line after ':').
  P09-47  --confirm-markers FOLDER: check only. Each dropped marker is labelled confirmed (a pypdf visitor run
      with the same text is raised, or its size is <= 0.85 x the page's most common size), unconfirmed, or
      no_run. Nothing is put back.

Extractor v5 changes (owner decision P09-49, Q1 all 22 SECTION-LIST sections, Q2 keep 'See' / 'Now'):
  P09-49  FOOTNOTE_START keeps the number prefix ('N.' / 'Na.') required and matches the footnote vocabulary
      case-insensitively (ins./sub./subs./omtt./omitt./omitted by/inserted by/substituted by|for/renumbered/
      see/now/words/'Clauses (a) ... sub. for ...' etc.); 'N. [Omitted by ...' (printed omissions) cannot match.
      MOVED-BLOCKS.tsv lists every footnote block v5 creates and v4 did not, flagged when > 40 lines, when it
      holds a line that locate would take as a section start, or a table row. FOOTNOTE-LIKE-IN-BODY.md lists
      body lines that look like footnote text (report only; nothing is moved).

Extractor v6 changes (owner decisions P09-50, P09-51, P09-52 with Q1 move-and-flag, Q2 10-page cap):
  P09-50  range footnotes 'N-M.' start a block when N < M and M - N <= 10 (vocabulary rule unchanged); the entry
      covers N..M for footnote numbers and marker links.
  P09-51  the printed_omission label also covers 'Explanation.—[Omitted' and '<section>. [Omitted' (label only).
  P09-52  a 'read(s) as under' quotation in a footnote that is still open at the page end continues on the next
      page(s): the kept lines from the top through the line that ends with the closing outer quote are footnote
      text, never body (bare-number marker lines stay body). Only moved when the close is found within 10 pages;
      no opening quote / unclosed -> nothing moved, logged. QUOTE-CONTINUATIONS.tsv logs every case with the 2
      kept lines after the close; flags '>40 lines' and 'apostrophe_risk' (a single-quote close right after a letter).

Extractor v7 changes (owner decision P09-53, Q1 yes):
  P09-53  R2 also ends a section at a structural heading line (CHAPTER / PART / SCHEDULE, optionally after a marker
      and/or '['); the heading and everything after it are cut. All-caps title lines are cut only directly after
      such a heading (with it) or directly before the next section heading with no body line between; never
      elsewhere. Every cut is logged in STRUCTURAL-TAILS.tsv. Q1: the Schedules region also starts at '[SCHEDULE ...'.

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

EXTRACTOR_VERSION = "v7"
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
PAGE_DIGIT_RE = FURNITURE_RE[1]       # P09-46: page-edge bare digits -> classify_edge_digits(), not furniture
PAGE_RUN_MIN = 5                      # P09-46: >= 5 consecutive pages, same edge, constant value - page_1based
FOOTNOTE_START_V4 = re.compile(      # kept only for the MOVED-BLOCKS comparison (P09-49)
    r"^\s*\d+[a-z]?\.\s+(?:Ins\.|Sub\.|Subs\.|Omtt\.|Omitted by|Inserted by|Substituted by|Substituted for|"
    r"Proviso omtt\.|Italicised words|Words\s+[\"“]|Prior to|Re-numbered|Renumbered|See rule|See also|"
    r"Sections? .{0,80}?inserted by)")
FOOTNOTE_START = re.compile(         # v5 [P09-49] + v6 range prefix 'N-M.' [P09-50, checked in footnote_start_match]
    r"^\s*\d+[a-z]?(?:-\d+)?\.\s+(?i:Ins[.,]|Subs?\.|Omtt?\.|Omitt\.|Omitted by|Inserted by|Substituted (?:by|for)|"
    r"Proviso omtt\.|Italicised words?|Words?\s+[\"“]|Word and|Prior to|Re-?numbered|Shall be renumbered|"
    r"See\b|Now\b|Original section|Following marginal|Explanation renumbered|"
    r"(?:Sections?|Sub-sections?|Clauses?|Sub-clauses?|Chapters?|Sl\. Nos?\.|Explanations?|"
    r"(?:First |Second |Third )?Provisos?|Schedules?|Items?|Entries|Entry|Words?)\b.{0,80}?"
    r"\b(?:inserted|substituted|omitted|renumbered|re-numbered|ins\.|subs?\.|omtt\.))")
# ---------------------------------------------------------------- P09-49 footnote-like detector (report only)
FOOTNOTE_LIKE = (
    ("wef", re.compile(r"\bw\.(?:r\.)?e\.f\.")),
    ("ins_sub_by", re.compile(r"(?i)\b(?:ins|subs?)\.\s*by\b")),
    ("omitted_by", re.compile(r"(?i)\bomitted by\b")),
    ("act_no", re.compile(r"\bAct No\.\s*\d+\s+of\s+\d{4}")),
    ("finance_act_date", re.compile(r"Finance (?:\(No\. ?\d\) )?Act, \d{4}.{0,40}?\d{1,2}-\d{1,2}-\d{4}")),
)
PRINTED_OMISSION_RE = re.compile(                                   # P09-51: label only
    r"^\s*(?:\([0-9a-zA-Z]+\)\s*|Explanation\s*\d*\s*\.?\s*[—–-]+\s*|\d{1,3}[A-Z]{0,5}\s?\.\s*)?\[Omitted")
MOVED_BLOCK_MAX = 40
FOOTNOTE_RANGE_RE = re.compile(r"^\s*(\d+)-(\d+)\.\s")                         # P09-50
RANGE_MAX_SPAN = 10
READ_AS_UNDER_RE = re.compile(r"reads? as under\s*[:\-—]*\s*", re.I)          # P09-52
QUOTE_PAGE_CAP = 10

# ---------------------------------------------------------------- R1 / R2 / R5 / R4 patterns
START_RE = re.compile(r"^\s*(\d{1,3}[A-Z]{0,5})\s?\.(?=\s|$|\()")
HEADING_FIRST_RE = re.compile(r"^[A-Z\[“\"‘']")
NOT_HEADING_RE = re.compile(r"^\[?(?:Explanation|Provided)")
ALLCAPS_RE = re.compile(r"^[^a-z]*[A-Z]{3,}[^a-z]*$")
CHAPTER_RE = re.compile(r"^\s*CHAPTER\s+[IVXLC]+(?:[\-–]?[A-Z]{1,3})?\s*$")
PART_RE = re.compile(r"^\s*[A-Z]{1,2}\.\s?[—–-]\s?\S")
ACT_TITLE_RE = re.compile(r"^\s*[A-Z][A-Z\-() ]*ACT, \d{4}\*?\s*$")
SCHEDULE_LINE_RE = re.compile(r"^\s*(?:THE\s+[A-Z]+\s+)?SCHEDULE(?:\s+[IVXL]+)?\s*$")
STRUCT_HEADING_RE = re.compile(                    # P09-53: optional marker and '[', then CHAPTER / PART / SCHEDULE
    r"^\s*(?:\d+[a-z]?\s*)?\[?\s*(?:CHAPTER\s+[IVXLC]+(?:\s*[\-–]?\s*[A-Z]{1,3})?|PART\s+[A-Z0-9IVXL]+|"
    r"(?:THE\s+[A-Z]+\s+)?SCHEDULE(?:\s+[IVXL]+)?)\s*\]?\s*$")
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
SYMBOL_RE = re.compile(r"^\s*([*†‡])")                                         # P09-44
FAMILY_TOKEN_RE = re.compile(r"^(\d+)[a-z]$")                                 # P09-43 job 1
NUMBER_BASE_RE = re.compile(r"^(\d+)")
QUOTE_OR_PAREN = ("\"", "“", "'", "‘", "(")                                    # P09-43 Q1 guard
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
    depth_before: list = field(default_factory=list)  # P09-42: open '[' depth before each kept line
    depth_after: list = field(default_factory=list)   # P09-42: open '[' depth after each kept line
    orphans: list = field(default_factory=list)       # P09-42: (line_idx, kind '[' or ']')
    edge_digits: list = field(default_factory=list)   # P09-46: (page_1based, line_1based, edge, value, reason)
    page_runs: list = field(default_factory=list)     # P09-46: (edge, offset, first_page, last_page, n)
    foot_line_objs: list = field(default_factory=list)  # P09-49: Line objects moved to footnotes, in order
    quote_log: list = field(default_factory=list)       # P09-52: quotations open at a page end (moved or not)


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
    """Footer furniture (exact lines + the Downloaded/Printed footer). Bare page-edge digits are NOT decided
    here any more: see classify_edge_digits() [P09-46]."""
    return s in FURNITURE_EXACT or bool(FURNITURE_RE[0].match(s))


def page_number_runs(cands: list) -> tuple:
    """P09-46: cands = [(page_1based, edge, value)] (unmatched page-edge digits). A page-number sequence is a
    run of >= PAGE_RUN_MIN consecutive pages at the same edge where value - page_1based is the same constant.
    Returns (set of (page, edge, value) inside a run, [(edge, offset, first_page, last_page, n)])."""
    inside, runs = set(), []
    for edge in ("top", "bottom"):
        by_page = {}
        for p, e, val in cands:
            if e == edge:
                by_page.setdefault(p, set()).add(val - p)
        for off in sorted({o for offs in by_page.values() for o in offs}):
            ps = sorted(p for p, offs in by_page.items() if off in offs)
            start = 0
            for k in range(1, len(ps) + 1):
                if k == len(ps) or ps[k] != ps[k - 1] + 1:
                    if k - start >= PAGE_RUN_MIN:
                        runs.append((edge, off, ps[start], ps[k - 1], k - start))
                        inside |= {(p, edge, p + off) for p in ps[start:k]}
                    start = k
    return inside, runs


def classify_edge_digits(cands: list, notes: dict) -> tuple:
    """P09-46 with Q1 (b). cands = [(page_1based, line_1based, edge, value, Line)]. A digit that equals a
    footnote number on its page or the next page (family rule) is a 'marker' (left in the body for the marker
    rule); only the remaining digits can form a 'page_number_sequence' (removed as furniture); everything else
    is 'unresolved' (left in the body). Returns (labelled [(page, line, edge, value, reason)], runs, removed Lines)."""
    labelled, unmatched = [], []
    for p, ln_no, edge, val, line in cands:
        nums = footnote_numbers(notes, p, p)
        if str(val) in nums or str(val) in _family_bases(nums):
            labelled.append((p, ln_no, edge, val, "marker", line))
        else:
            unmatched.append((p, ln_no, edge, val, line))
    inside, runs = page_number_runs([(p, e, v) for p, _, e, v, _ in unmatched])
    removed = []
    for p, ln_no, edge, val, line in unmatched:
        if (p, edge, val) in inside:
            labelled.append((p, ln_no, edge, val, "page_number_sequence", line))
            removed.append(line)
        else:
            labelled.append((p, ln_no, edge, val, "unresolved", line))
    labelled.sort(key=lambda x: (x[0], x[1]))
    return [x[:5] for x in labelled], runs, removed


def _body_resumes(page_lines: list, footnote_start=None) -> set:
    """Indices (within one page) where a heading + section start pair or a boundary line begins."""
    fs = footnote_start or FOOTNOTE_START
    out = set()
    for k, ln in enumerate(page_lines):
        if _boundary(ln.text.strip()):
            out.add(k)
            continue
        if START_RE.match(ln.text) and not footnote_start_match(ln.text, fs) and not PART_NUMBER_RE.match(ln.text):
            h = _heading_before(page_lines, k)
            if h:
                out.add(h[1])
    return out


def footnote_start_match(text: str, fs=None):
    """FOOTNOTE_START plus the P09-50 range check: 'N-M.' starts a block only if N < M and M - N <= 10."""
    m = (fs or FOOTNOTE_START).match(text)
    if not m:
        return None
    r = FOOTNOTE_RANGE_RE.match(text)
    if r and not (int(r.group(1)) < int(r.group(2)) and int(r.group(2)) - int(r.group(1)) <= RANGE_MAX_SPAN):
        return None
    return m


def clean_pages(pages: list, trace: Trace | None = None, footnote_start=None, quote_continuation: bool = True) -> Cleaned:
    """R3 on every page. pages[idx0] is the raw text of page page_1based(idx0). footnote_start overrides
    FOOTNOTE_START (used only for the v4/v5 MOVED-BLOCKS comparison); quote_continuation=False switches P09-52
    off (used only for before/after reports)."""
    fs = footnote_start or FOOTNOTE_START
    out, notes, furn, midpage, n_foot, rule_drops, cands = [], {}, [], [], 0, [], []
    foot_ids, page_kept, quote_log = [], [], []
    for idx0, text in enumerate(pages):                    # pass A: furniture, dividers, edge-digit candidates
        pno = page_1based(idx0)
        raw = text.splitlines()
        nonempty = [i for i, ln in enumerate(raw) if ln.strip()]
        top, bottom = set(nonempty[:FURNITURE_TOP]), set(nonempty[-FURNITURE_BOTTOM:])
        edge = top | bottom
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
                line = Line(pno, ln, i + 1)
                kept.append(line)
                if i in edge and PAGE_DIGIT_RE.match(ln.strip()):  # P09-46: decided in pass 2
                    cands.append((pno, i + 1, "top" if i in top else "bottom", int(ln.strip()), line))
        page_kept.append(kept)
    claimed = {}                                            # P09-52: id(Line) -> continuation of a quotation
    for idx0, kept_all in enumerate(page_kept):            # pass B: footnote blocks
        pno = page_1based(idx0)
        cont = [ln for ln in kept_all if id(ln) in claimed]
        kept = [ln for ln in kept_all if id(ln) not in claimed]
        resumes = _body_resumes(kept, fs)
        in_foot, body, foot = False, [], list(cont)
        for k, ln in enumerate(kept):
            if BARE_MARKER_RE.match(ln.text.strip()):              # P09-46: bare numbers never join a block
                body.append(ln)
                continue
            if footnote_start_match(ln.text, fs):
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
            foot_ids += foot
        out.extend(body)
        if quote_continuation and foot:                     # P09-52: a quotation still open at the page end
            own = [ln for ln in foot if id(ln) not in claimed]
            for entry in _open_quotations(own):
                lines, status, after = _find_quote_close(page_kept, idx0, entry, claimed)
                entry.update({"status": status, "lines_moved": len(lines), "after_close": after})
                if status == "closed":
                    for ln in lines:
                        claimed[id(ln)] = entry
                    entry["end_page_1based"], entry["end_line_1based"] = lines[-1].page, lines[-1].line_no
                    entry["moved"] = [(ln.page, ln.line_no) for ln in lines]
                    flags = [f">{MOVED_BLOCK_MAX} lines"] if len(lines) > MOVED_BLOCK_MAX else []
                    if entry["outer"] in "'‘" and re.search(r"[^\W\d_]['’][.;,]?\s*$", lines[-1].text.rstrip()):
                        flags.append("apostrophe_risk")
                    entry["flags"] = flags
                    entry["status"] = "moved_flagged" if flags else "moved"
                quote_log.append(entry)
    edge_digits, runs, removed = classify_edge_digits(cands, notes)  # P09-46 pass 2
    gone = {id(x) for x in removed}
    for x in removed:
        furn.append((x.page, x.text.strip()))
    out = [ln for ln in out if id(ln) not in gone]
    before, after, orphans = bracket_scan(out)
    return Cleaned(out, notes, furn, midpage, n_foot, rule_drops, before, after, orphans, edge_digits, runs, foot_ids,
                   quote_log)


_QUOTE_PAIRS = {'"': '"', "“": "”", "'": "'", "‘": "’"}


def _closes(rest: str, close: str) -> bool:
    """P09-52: a line closes the outer quotation when it ends with the closing mark (optionally + '.', ';', ',')."""
    s = rest.rstrip()
    return s.endswith(close) or s.rstrip(".;,").endswith(close)


def _open_quotations(foot: list) -> list:
    """P09-52: quotations ('read(s) as under' + an opening outer quote) in one page's footnote lines that are still
    open at the page end; also 'no_opening_quote' and 'await_open' (phrase at the very end of the page) cases.
    Returns [{footnote, start_page_1based, start_line_1based, outer, state}]."""
    out, cur, number = [], None, None
    for ln in foot:
        t = ln.text
        mnum = FOOTNOTE_NUMBER_RE.match(t) or FOOTNOTE_RANGE_RE.match(t)
        if mnum:
            number = mnum.group(0).strip().rstrip(".").strip()
        if cur is not None and cur["state"] == "await_open":
            s = t.strip()
            if s[:1] in _QUOTE_PAIRS:
                cur.update({"outer": s[0], "state": "open"})
                if _closes(s[1:], _QUOTE_PAIRS[s[0]]):
                    cur = None
            else:
                cur.update({"state": "no_opening_quote", "outer": ""})
                out.append(cur)
                cur = None
            continue
        if cur is not None and cur["state"] == "open":
            if _closes(t, _QUOTE_PAIRS[cur["outer"]]):
                cur = None
            continue
        m = READ_AS_UNDER_RE.search(t)
        if not m:
            continue
        cur = {"footnote": number, "start_page_1based": ln.page, "start_line_1based": ln.line_no, "outer": "",
               "state": "await_open"}
        rest = t[m.end():].strip()
        if rest:
            if rest[0] in _QUOTE_PAIRS:
                cur.update({"outer": rest[0], "state": "open"})
                if _closes(rest[1:], _QUOTE_PAIRS[rest[0]]):
                    cur = None
            else:
                cur.update({"state": "no_opening_quote"})
                out.append(cur)
                cur = None
    if cur is not None:
        out.append(cur)
    return out


def _find_quote_close(page_kept: list, idx0: int, entry: dict, claimed: dict) -> tuple:
    """P09-52: look ahead (at most QUOTE_PAGE_CAP pages) for the line that closes the quotation. Returns
    (lines to move, status, [the 2 kept lines after the close]). Nothing is moved unless status == 'closed'.
    Bare-number marker lines are skipped (they stay body)."""
    if entry["state"] == "no_opening_quote":
        return [], "no_opening_quote", []
    state, outer, lines = entry["state"], entry["outer"], []
    for j in range(idx0 + 1, min(idx0 + 1 + QUOTE_PAGE_CAP, len(page_kept))):
        for k, ln in enumerate(page_kept[j]):
            if id(ln) in claimed or BARE_MARKER_RE.match(ln.text.strip()):
                continue
            rest = ln.text
            if state == "await_open":
                s = rest.strip()
                if s[:1] not in _QUOTE_PAIRS:
                    return [], "no_opening_quote", []
                outer, state, rest = s[0], "open", s[1:]
                entry["outer"] = outer
            lines.append(ln)
            if _closes(rest, _QUOTE_PAIRS[outer]):
                after = [x.text.strip()[:100] for jj in range(j, min(j + 2, len(page_kept)))
                         for x in (page_kept[jj][k + 1:] if jj == j else page_kept[jj])
                         if not BARE_MARKER_RE.match(x.text.strip())][:2]
                return lines, "closed", after
    return [], "unclosed", []


def bracket_scan(lines: list) -> tuple:
    """P09-42: one stack over all kept lines in page order. Returns (depth_before, depth_after, orphans);
    orphans = [(line_idx, ']')] for a ']' with nothing open, plus [(line_idx, '[')] for every '[' still open
    at the end of the edition."""
    stack, before, after, orphans = [], [], [], []
    for i, ln in enumerate(lines):
        before.append(len(stack))
        for ch in ln.text:
            if ch == "[":
                stack.append(i)
            elif ch == "]":
                if stack:
                    stack.pop()
                else:
                    orphans.append((i, "]"))
        after.append(len(stack))
    orphans += [(i, "[") for i in stack]
    return before, after, sorted(orphans)


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
    """Index of the first standalone SCHEDULE line (Schedules region runs to the end), else len(lines).
    P09-53 Q1: '[SCHEDULE I' / marker + '[SCHEDULE ...' count too."""
    return next((i for i, ln in enumerate(lines) if SCHEDULE_LINE_RE.match(ln.text)
                 or (STRUCT_HEADING_RE.match(ln.text) and "SCHEDULE" in ln.text)), len(lines))


def find_starts(lines: list) -> list:
    marks, _ = table_marks(lines)
    stop = schedules_from(lines)
    starts = []
    for i, ln in enumerate(lines[:stop]):
        m = START_RE.match(ln.text)
        if not m or i in marks or footnote_start_match(ln.text) or PART_NUMBER_RE.match(ln.text):
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
    end, by_next_heading = len(lines), False
    for t in starts:
        if t.idx > s.idx and section_key(t.number) > key:
            end, by_next_heading = t.heading_idx, True
            break
    for j in range(s.idx + 1, end):
        if _boundary(lines[j].text):
            end, by_next_heading = j, False
            break
    tails = []
    for j in range(s.idx + 1, end):                 # P09-53: a structural heading ends the section (cut it + all after)
        if STRUCT_HEADING_RE.match(lines[j].text):
            tails.append(_tail("structural_heading", lines, j, end))
            end, by_next_heading = j, False
            break
    if by_next_heading:                             # P09-53: all-caps title lines right before the next heading
        k = end
        while k - 1 > s.idx and ALLCAPS_RE.match(lines[k - 1].text.strip()):
            k -= 1
        if k < end:
            tails.append(_tail("trailing_caps", lines, k, end))
            end = k
    pages = sorted({ln.page for ln in lines[s.idx:end]})
    return {"status": "FOUND", "internal_line_idx0_start": s.idx, "internal_line_idx0_end": end,
            "internal_heading_line_idx0": s.heading_idx, "heading": s.heading, "pages_1based": pages,
            "candidates": cands, "structural_tails": tails}


def _tail(reason: str, lines: list, a: int, b: int) -> dict:
    """P09-53: one cut (lines a .. b-1) for STRUCTURAL-TAILS.tsv."""
    return {"reason": reason, "heading_page_1based": lines[a].page, "heading_line_1based": lines[a].line_no,
            "heading_text": lines[a].text.strip()[:80], "lines_cut": b - a,
            "first_cut_line": lines[a].text.strip()[:100], "last_cut_line": lines[b - 1].text.strip()[:100]}


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
            rng = _footnote_range(ln)
            if rng:
                out.update(rng[1])                          # P09-50: a range entry covers N..M
    return out


def _footnote_range(line: str):
    """P09-50: ('N-M', ['N', ..., 'M']) for a valid range footnote line (N < M, M - N <= 10), else None."""
    r = FOOTNOTE_RANGE_RE.match(line)
    if not r:
        return None
    a, b = int(r.group(1)), int(r.group(2))
    if not (a < b and b - a <= RANGE_MAX_SPAN):
        return None
    return f"{a}-{b}", [str(n) for n in range(a, b + 1)]


def footnotes_raw(notes: dict, p_first: int, p_last: int) -> list:
    """P09-30/43/44: [{page_1based, number, symbol, text}] in block order over pages p_first .. p_last + 1.
    A new entry starts at a numbered line (P09-29b), at a '*' / '†' / '‡' line (P09-44, field 'symbol'), or
    (P09-43, unnumbered) after a line ending in '.'; Q1 guard + P09-43b: a line after one ending in ':' or a line
    starting with a quote mark, '(', a lowercase letter or a digit stays a continuation. Local meta only; never a
    date source."""
    out, prev = [], ""
    for p in range(p_first, p_last + 2):
        for ln in notes.get(p, []):
            m, sm, rng = FOOTNOTE_NUMBER_RE.match(ln), SYMBOL_RE.match(ln), _footnote_range(ln)
            first = ln.lstrip()[:1]
            starts_new = (not out or m or sm or rng
                          or (prev.endswith(".") and not ln.lstrip().startswith(QUOTE_OR_PAREN)
                              and not first.islower() and not first.isdigit()))      # P09-43b
            if starts_new and rng:
                out.append({"page_1based": p, "number": rng[0], "symbol": None, "text": ln.strip(), "covers": rng[1]})
            elif starts_new:
                out.append({"page_1based": p, "number": m.group(1) if m else None,
                            "symbol": sm.group(1) if (sm and not m) else None, "text": ln.strip()})
            else:
                out[-1]["text"] += "\n" + ln.strip()
            prev = ln.rstrip()
    return out


def _family_bases(numbers: set) -> set:
    return {NUMBER_BASE_RE.match(n).group(1) for n in numbers if NUMBER_BASE_RE.match(n)}


def apply_markers(seg: list, numbers: set) -> tuple:
    """P09-29 (line markers, with the P09-43 job-1 family match) then P09-41 (inline markers, exact only).
    Returns (lines, dropped, unresolved, inline_found); dropped / unresolved entries:
    {type, page_1based, line_1based, pos, numbers, match[, missing][, context]}; match[k] is 'exact' /
    'matched_by_family' / None for numbers[k]."""
    kept, dropped, unresolved, inline_found = [], [], [], 0
    bases = _family_bases(numbers)
    for ln in seg:
        s = ln.text.strip()
        if BARE_MARKER_RE.match(s):
            nums = s.split()
            match = []
            for n in nums:
                fm = FAMILY_TOKEN_RE.match(n)
                match.append("exact" if n in numbers else ("matched_by_family" if fm and fm.group(1) in bases else None))
            missing = [n for n, mt in zip(nums, match) if mt is None]
            entry = {"type": "line", "page_1based": ln.page, "line_1based": ln.line_no, "pos": 0,
                     "numbers": nums, "match": match}
            if missing:
                unresolved.append(dict(entry, missing=missing))
                kept.append(ln)
            else:
                dropped.append(entry)
            continue
        text = ln.text
        for m in reversed(list(INLINE_MARKER_RE.finditer(text))):
            inline_found += 1
            entry = {"type": "inline", "page_1based": ln.page, "line_1based": ln.line_no, "pos": m.start(),
                     "numbers": [m.group(1)], "match": ["exact" if m.group(1) in numbers else None]}
            if m.group(1) in numbers:
                dropped.append(entry)
                text = text[:m.start()] + text[m.end():]
            else:
                unresolved.append(dict(entry, missing=[m.group(1)],
                                       context=text[max(0, m.start() - 25):m.end() + 25].strip()))
        kept.append(ln if text == ln.text else Line(ln.page, text, ln.line_no))
    return kept, dropped, unresolved, inline_found


def _editor_note_blocks(seg: list) -> list:
    """[(i, j)] index ranges of P09-35 candidate blocks in seg (shared by the candidates list and the detector)."""
    out, i = [], 0
    while i < len(seg):
        if EDITOR_NOTE_RE.search(seg[i].text):
            head_end = next((j for j in range(i, min(i + 3, len(seg))) if "w.e.f." in seg[j].text), None)
            if head_end is not None:
                j = head_end + 1
                while j < len(seg) and not BARE_MARKER_RE.match(seg[j].text.strip()) \
                        and not SUBSECTION_LINE_RE.match(seg[j].text):
                    j += 1
                out.append((i, j))
                i = j
                continue
        i += 1
    return out


def editor_note_candidates(seg: list) -> list:
    """P09-35: candidate blocks, listed only (never cut here). A block starts at a line with
    'shall be inserted/substituted/omitted/renumbered' when 'w.e.f.' is on it or on one of the next 2 lines;
    it runs from there to the next bare marker line, unindented sub-section line, or the section end."""
    return [{"page_1based": seg[i].page, "line_1based": seg[i].line_no,
             "text": "\n".join(SPACES_RE.sub(" ", x.text).strip() for x in seg[i:j])} for i, j in _editor_note_blocks(seg)]


def footnote_like_lines(seg: list) -> list:
    """P09-49 detector (report only; nothing is moved): body lines that look like footnote text.
    Returns [{page_1based, line_1based, patterns, label, text}]; label = printed_omission ('[Omitted ...' printed
    in the body) / editor_note_candidate (inside a P09-35 block) / other."""
    in_note = {k for i, j in _editor_note_blocks(seg) for k in range(i, j)}
    out = []
    for k, ln in enumerate(seg):
        pats = [name for name, rx in FOOTNOTE_LIKE if rx.search(ln.text)]
        if not pats:
            continue
        label = ("printed_omission" if PRINTED_OMISSION_RE.match(ln.text)
                 else "editor_note_candidate" if k in in_note else "other")
        out.append({"page_1based": ln.page, "line_1based": ln.line_no, "patterns": pats, "label": label,
                    "text": SPACES_RE.sub(" ", ln.text).strip()[:140]})
    return out


def moved_blocks(kept_pages: list, v5: Cleaned) -> list:
    """P09-49: footnote blocks that v5 creates and v4 did not. A block = consecutive v5 footnote lines (same page)
    that were body under v4. Flags: > MOVED_BLOCK_MAX lines; 'section_start_like' = a line matching locate's start
    pattern (START_RE, not a footnote line, not a part heading); a line that R5 marks as a table row in the v4 lines."""
    v4 = clean_pages(kept_pages, footnote_start=FOOTNOTE_START_V4)
    v4_foot = {(x.page, x.line_no) for x in v4.foot_line_objs}
    marks, _ = table_marks(v4.lines)
    rows = {(v4.lines[i].page, v4.lines[i].line_no) for i, m in marks.items() if m[0] == "row"}
    blocks, cur = [], []
    for pos, ln in enumerate(v5.foot_line_objs):        # pos = order among v5 footnote lines
        new = (ln.page, ln.line_no) not in v4_foot
        if new and cur and cur[-1][1].page == ln.page and cur[-1][0] + 1 == pos:
            cur.append((pos, ln))
        elif new:
            if cur:
                blocks.append([x for _, x in cur])
            cur = [(pos, ln)]
        elif cur:
            blocks.append([x for _, x in cur])
            cur = []
    if cur:
        blocks.append([x for _, x in cur])
    out = []
    for b in blocks:
        flags = []
        if len(b) > MOVED_BLOCK_MAX:
            flags.append(f">{MOVED_BLOCK_MAX} lines")
        # a heading-confirmed start would already have ended the block (R3 resume), so flag any line that LOOKS
        # like a start: START_RE, not a footnote line, not a numbered part heading
        if any(START_RE.match(x.text) and not footnote_start_match(x.text) and not PART_NUMBER_RE.match(x.text)
               for x in b):
            flags.append("section_start_like")
        if any((x.page, x.line_no) in rows for x in b):
            flags.append("table_row")
        out.append({"page_1based": b[0].page, "line_1based": b[0].line_no, "lines": len(b),
                    "first": b[0].text.strip()[:120], "last": b[-1].text.strip()[:120], "flags": flags})
    return out


def _marker_tokens(dropped: list, unresolved: list) -> list:
    """Every marker token in body order: (page_1based, line_1based, pos + k)."""
    toks = []
    for status, entries in (("dropped", dropped), ("unresolved", unresolved)):
        for e in entries:
            for k, n in enumerate(e["numbers"]):
                toks.append({"token": n, "page_1based": e["page_1based"], "line_1based": e["line_1based"],
                             "pos": e.get("pos", 0) + k, "marker_type": e["type"], "status": status,
                             "match": (e.get("match") or [None] * len(e["numbers"]))[k]})
    return sorted(toks, key=lambda t: (t["page_1based"], t["line_1based"], t["pos"]))


def link_markers(dropped: list, unresolved: list, entries: list) -> dict:
    """P09-43 job 2. Links marker tokens (body order) to footnote entries (block order).
    'number': the token equals the number of exactly one entry in the range ('ambiguous' if 2+; never picked).
    'assigned_by_order': unnumbered entries between consecutive numbered entries N and M go, in order, to the
    unlinked tokens after the last token linked to an entry at or before N and before the first token linked
    to an entry at or after M, ONLY if the two counts are equal. Symbol entries are never aligned."""
    toks = _marker_tokens(dropped, unresolved)
    by_num = {}
    for j, e in enumerate(entries):
        if e["number"] is not None:
            for n in e.get("covers") or [e["number"]]:      # P09-50: a range entry answers each covered number
                by_num.setdefault(n, []).append(j)
    unnum_ord = {j: k for k, j in enumerate([j for j, e in enumerate(entries)
                                             if e["number"] is None and e.get("symbol") is None], 1)}
    for t in toks:
        hits = by_num.get(t["token"], [])
        t["entry"], t["link"] = (hits[0], "number") if len(hits) == 1 else (None, "ambiguous" if hits else None)
    numbered = [j for j, e in enumerate(entries) if e["number"] is not None]
    for a, b in zip(numbered, numbered[1:]):
        gap = [j for j in range(a + 1, b) if entries[j]["number"] is None and entries[j].get("symbol") is None]
        if not gap:
            continue
        lo = max((i for i, t in enumerate(toks) if t["entry"] is not None and t["entry"] <= a), default=-1)
        hi = min((i for i, t in enumerate(toks) if t["entry"] is not None and t["entry"] >= b), default=len(toks))
        cands = [i for i in range(lo + 1, hi) if toks[i]["entry"] is None and toks[i]["link"] is None]
        if len(cands) == len(gap):
            for i, j in zip(cands, gap):
                toks[i]["entry"], toks[i]["link"] = j, "assigned_by_order"
    linked = {t["entry"] for t in toks if t["entry"] is not None}

    def label(j):
        e = entries[j]
        return e["number"] if e["number"] is not None else (
            f"symbol {e['symbol']}" if e.get("symbol") else f"unnumbered #{unnum_ord[j]}")
    links = [{k: t[k] for k in ("token", "page_1based", "line_1based", "marker_type", "status", "match", "link")}
             | {"footnote": label(t["entry"]) if t["entry"] is not None else None,
                "footnote_text": entries[t["entry"]]["text"][:100] if t["entry"] is not None else None}
             for t in toks]
    return {"links": links,
            "footnotes_without_marker": [{"footnote": label(j), "page_1based": e["page_1based"], "text": e["text"][:100]}
                                         for j, e in enumerate(entries) if j not in linked and not e.get("symbol")],
            "symbol_notes": [{"symbol": e["symbol"], "page_1based": e["page_1based"], "text": e["text"][:100]}
                             for e in entries if e.get("symbol")],
            "markers_without_footnote": [x for x in links if x["footnote"] is None]}


def section_brackets(cleaned: Cleaned, first: int, end: int) -> dict:
    """P09-42: carry_in / carry_out / orphans for kept lines first .. end-1 of the edition scan."""
    orph = [{"kind": k, "page_1based": cleaned.lines[i].page, "line_1based": cleaned.lines[i].line_no,
             "text": cleaned.lines[i].text.strip()[:160]} for i, k in cleaned.orphans if first <= i < end]
    return {"carry_in": cleaned.depth_before[first], "carry_out": cleaned.depth_after[end - 1],
            "orphans": orph, "warn": bool(orph)}


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
    entries = footnotes_raw(cleaned.notes, p0, p1)
    links = link_markers(m_dropped, m_unres, entries)                     # P09-43 job 2
    first = hidx - 1 if (hidx > 0 and lines[hidx - 1].text.strip() == "[") else hidx
    brackets = section_brackets(cleaned, first, loc["internal_line_idx0_end"])   # P09-42
    for o in brackets["orphans"]:
        earlier = [x for x in links["links"] if (x["page_1based"], x["line_1based"]) < (o["page_1based"], o["line_1based"])]
        o["nearest_earlier_marker"] = earlier[-1] if earlier else None
    loc.update({"heading": heading, "heading_bracket_moved_to_body": opened,
                "body": body, "chars": len(body), "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "table_rows": rows, "unresolved": unresolved, "tables": table_map,
                "amendment_note": "\n".join(note_lines) if note_lines else None,
                "footnotes_raw_note": "local only; never a date source; never in committed files",
                "footnotes_raw": entries,
                "dropped_markers": m_dropped, "unresolved_markers": m_unres, "inline_markers_found": inline_found,
                "marker_links": links,
                "symbol_notes": sum(1 for e in entries if e.get("symbol")),
                "body_symbol_lines": sum(1 for ln in seg if SYMBOL_RE.match(ln.text)),
                "editor_note_candidates": editor, "brackets": brackets,
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


def _edge_tsv(views: list) -> str:
    """P09-46: PAGE-EDGE-DIGITS.tsv (whole editions)."""
    out = ["file\tpage_1based\tline_1based\tedge\tvalue\treason"]
    out += [f"{v.key}.pdf\t{p}\t{ln}\t{e}\t{val}\t{reason}" for v in views for p, ln, e, val, reason in v.cleaned.edge_digits]
    return "\n".join(out) + "\n"


def _moved_blocks_outputs(views: list) -> tuple:
    """P09-49: (MOVED-BLOCKS.tsv text, printed summary with flagged rows per edition)."""
    tsv = ["edition\tpage_1based\tstart_line_1based\tlines_moved\tfirst_line\tlast_line\tflags"]
    summary = []
    for v in views:
        blocks = moved_blocks(drop_duplicate_pages(v.pages)[0], v.cleaned)
        for b in blocks:
            tsv.append(f"{v.key}\t{b['page_1based']}\t{b['line_1based']}\t{b['lines']}\t{_tsv_cell(b['first'])}\t"
                       f"{_tsv_cell(b['last'])}\t{','.join(b['flags']) or '-'}")
        flagged = [b for b in blocks if b["flags"]]
        kinds = {k: sum(1 for b in flagged if any(f.startswith(k) for f in b["flags"]))
                 for k in (f">{MOVED_BLOCK_MAX}", "section_start_like", "table_row")}
        summary.append(f"{v.key:<15} new blocks={len(blocks):>3} lines moved={sum(b['lines'] for b in blocks):>4} "
                       f"flagged={len(flagged):>3} " + " ".join(f"{k}={n}" for k, n in kinds.items()))
    return "\n".join(tsv) + "\n", "\n".join(summary) + "\n"


def _quote_outputs(views: list) -> tuple:
    """P09-52: (QUOTE-CONTINUATIONS.tsv text, printed summary). Sections are named by the last section start
    (heading line) before a line in page order. For no_opening_quote / unclosed cases (nothing moved) the report
    gives the section body that receives the next page's top lines and how many, and whether that section is a
    SECTION-LIST / MAPPING target."""
    tg = targets()
    act_of = {k: a for a in EDITIONS for k in EDITIONS[a]}
    tsv = ["edition\tfootnote\tstart_page_1based\tstart_line_1based\tend_page_1based\tend_line_1based\touter_quote\t"
           "lines_moved\tsections_affected\tstatus\tflags\tafter_close_1\tafter_close_2\tnext_page_body_lines\t"
           "next_page_section\tin_section_list_or_mapping"]
    summary = []
    for v in views:
        act = act_of[v.key]
        heads = sorted((v.cleaned.lines[s.heading_idx].page, v.cleaned.lines[s.heading_idx].line_no, s.number)
                       for s in v.starts)

        def sec_at(pos):
            prev = [h[2] for h in heads if (h[0], h[1]) <= pos]
            return prev[-1] if prev else "-"
        counts = {}
        for e in v.cleaned.quote_log:
            counts[e["status"]] = counts.get(e["status"], 0) + 1
            secs = sorted({sec_at(m) for m in e.get("moved", [])}, key=lambda s: (len(s), s))
            npl, nps, intg = "-", "-", "-"
            if e["status"] in ("no_opening_quote", "unclosed"):
                nxt = e["start_page_1based"] + 1
                page_heads = [(h[0], h[1]) for h in heads if h[0] == nxt]
                top = [ln for ln in v.cleaned.lines if ln.page == nxt
                       and (not page_heads or (ln.page, ln.line_no) < page_heads[0])]
                npl = str(len(top))
                if top:
                    nps = sec_at((top[0].page, top[0].line_no))
                    intg = "yes" if nps in tg[act] else "no"
            after = (e.get("after_close") or []) + ["", ""]
            tsv.append("\t".join(str(x) for x in (
                v.key, e["footnote"], e["start_page_1based"], e["start_line_1based"], e.get("end_page_1based", "-"),
                e.get("end_line_1based", "-"), e["outer"] or "-", e["lines_moved"], ",".join(secs) or "-", e["status"],
                ",".join(e.get("flags", [])) or "-", _tsv_cell(after[0]), _tsv_cell(after[1]), npl, nps, intg)))
        moved = sum(e["lines_moved"] for e in v.cleaned.quote_log if e["status"].startswith("moved"))
        summary.append(f"{v.key:<15} open-at-page-end={len(v.cleaned.quote_log):>3} lines moved={moved:>4} "
                       + " ".join(f"{k}={n}" for k, n in sorted(counts.items())))
    return "\n".join(tsv) + "\n", "\n".join(summary) + "\n"


def _structural_tails_outputs(views: list) -> tuple:
    """P09-53: (STRUCTURAL-TAILS.tsv over all SECTION-LIST sections x editions, printed summary)."""
    sl = json.loads((STATUTES_DIR / "SECTION-LIST.json").read_text(encoding="utf-8"))
    secs = {"1961": [s["section"] for s in sl["sections_1961"]], "2025": [s["section"] for s in sl["sections_2025_only"]]}
    act_of = {k: a for a in EDITIONS for k in EDITIONS[a]}
    tsv = ["edition\tsection\theading_page_1based\theading_line_1based\theading_text\tlines_cut\tfirst_cut_line\t"
           "last_cut_line\treason"]
    summary = []
    for v in views:
        act, n_rows, n_lines = act_of[v.key], 0, 0
        for sec in secs[act]:
            loc = locate(v.cleaned.lines, v.starts, sec)
            for t in loc.get("structural_tails", []):
                n_rows, n_lines = n_rows + 1, n_lines + t["lines_cut"]
                tsv.append(f"{v.key}\t{act} s.{sec}\t{t['heading_page_1based']}\t{t['heading_line_1based']}\t"
                           f"{_tsv_cell(t['heading_text'])}\t{t['lines_cut']}\t{_tsv_cell(t['first_cut_line'])}\t"
                           f"{_tsv_cell(t['last_cut_line'])}\t{t['reason']}")
        summary.append(f"{v.key:<15} cuts={n_rows} lines cut={n_lines}")
    return "\n".join(tsv) + "\n", "\n".join(summary) + "\n"


def _footnote_like_md(views: list) -> tuple:
    """P09-49: FOOTNOTE-LIKE-IN-BODY.md over all SECTION-LIST sections x editions (report only)."""
    sl = json.loads((STATUTES_DIR / "SECTION-LIST.json").read_text(encoding="utf-8"))
    secs = {"1961": [s["section"] for s in sl["sections_1961"]], "2025": [s["section"] for s in sl["sections_2025_only"]]}
    act_of = {k: a for a in EDITIONS for k in EDITIONS[a]}
    summary = ["| act | section | edition | status | lines | printed_omission | editor_note_candidate | other |",
               "|---|---|---|---|---|---|---|---|"]
    detail, tot = [], {"printed_omission": 0, "editor_note_candidate": 0, "other": 0}
    for v in views:
        act = act_of[v.key]
        for sec, (st, a, b) in _section_spans(v, act, secs[act]).items():
            if st != "FOUND":
                summary.append(f"| {act} | {sec} | {v.key} | {st} | - | - | - | - |")
                continue
            hits = footnote_like_lines(v.cleaned.lines[a:b])
            c = {k: sum(1 for h in hits if h["label"] == k) for k in tot}
            for k in tot:
                tot[k] += c[k]
            summary.append(f"| {act} | {sec} | {v.key} | FOUND | {len(hits)} | {c['printed_omission']} | "
                           f"{c['editor_note_candidate']} | {c['other']} |")
            for h in hits:
                detail.append(f"- {v.key}.pdf {act} s.{sec} page_1based {h['page_1based']} line_1based {h['line_1based']} "
                              f"[{h['label']}; {','.join(h['patterns'])}]: {h['text']}")
    head = ["# FOOTNOTE-LIKE LINES IN BODY (P09-49, report only; nothing moved)", "",
            "Body lines (kept lines inside each located SECTION-LIST section) matching footnote-like patterns:",
            ", ".join(f"{n} = {rx.pattern}" for n, rx in FOOTNOTE_LIKE), "",
            f"totals: {sum(tot.values())} lines  " + "  ".join(f"{k}={n}" for k, n in tot.items()), "",
            f"## Summary ({len(secs['1961']) + len(secs['2025'])} SECTION-LIST sections x editions)", ""]
    text = "\n".join(head + summary + ["", "## Lines", ""] + detail) + "\n"
    return text, f"footnote-like body lines (22 sections): {sum(tot.values())} " + \
        " ".join(f"{k}={n}" for k, n in tot.items()) + "\n"


def _edge_summary(views: list) -> str:
    """P09-46: per edition, reasons and page-number sequence runs (edge, offset, pages covered)."""
    rows = []
    for v in views:
        c = {r: sum(1 for x in v.cleaned.edge_digits if x[4] == r) for r in ("marker", "page_number_sequence", "unresolved")}
        runs = "; ".join(f"{e} offset {o} pages {a}-{b} (n={n})" for e, o, a, b, n in v.cleaned.page_runs) or "none"
        rows.append(f"{v.key:<15} edge digits={len(v.cleaned.edge_digits):>4} marker={c['marker']:>4} "
                    f"page_number_sequence={c['page_number_sequence']:>3} unresolved={c['unresolved']:>4} | runs: {runs}")
    return "\n".join(rows) + "\n"


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
    mb_tsv, mb_sum = _moved_blocks_outputs(views)
    qc_tsv, qc_sum = _quote_outputs(views)
    text = ("\n".join(lines_out) + "\n\nR0 / R3 COUNTS\n" + _census_counts(views)
            + "\nP09-46 PAGE-EDGE DIGITS\n" + _edge_summary(views)
            + "\nP09-49 MOVED BLOCKS (current FOOTNOTE_START vs v4)\n" + mb_sum
            + "\nP09-52 QUOTE CONTINUATIONS\n" + qc_sum)
    st_tsv, st_sum = _structural_tails_outputs(views)
    text += "\nP09-53 STRUCTURAL TAILS (SECTION-LIST sections)\n" + st_sum
    print(text, end="")
    _write_new(out_dir / "LOCATE-ALL.txt", text)
    _write_new(out_dir / "MOVED-BLOCKS.tsv", mb_tsv)
    _write_new(out_dir / "QUOTE-CONTINUATIONS.tsv", qc_tsv)
    _write_new(out_dir / "STRUCTURAL-TAILS.tsv", st_tsv)
    _write_new(out_dir / "DROPPED-PAGES.tsv", _dropped_tsv(views))
    _write_new(out_dir / "DROPPED-RULES.tsv", _rules_tsv(views))
    _write_new(out_dir / "PAGE-EDGE-DIGITS.tsv", _edge_tsv(views))
    print(f"written {out_dir / 'LOCATE-ALL.txt'}, DROPPED-PAGES.tsv, DROPPED-RULES.tsv and PAGE-EDGE-DIGITS.tsv")
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
                        unresolved_md.append(f"- BRACKET WARN (edition-level orphans): {len(b['orphans'])}; "
                                             f"carry_in {b['carry_in']}, carry_out {b['carry_out']}")
                    unresolved_md.append("")
                results.append(r)
    found = [r for r in results if r["status"] == "FOUND"]
    _write_new(out_dir / "UNRESOLVED.md", "\n".join(unresolved_md) + "\n")
    _write_new(out_dir / "DROPPED-PAGES.tsv", _dropped_tsv(views))
    _write_new(out_dir / "DROPPED-RULES.tsv", _rules_tsv(views))
    _write_new(out_dir / "PAGE-EDGE-DIGITS.tsv", _edge_tsv(views))
    mb_tsv, mb_sum = _moved_blocks_outputs(views)
    _write_new(out_dir / "MOVED-BLOCKS.tsv", mb_tsv)
    fl_md, fl_sum = _footnote_like_md(views)
    _write_new(out_dir / "FOOTNOTE-LIKE-IN-BODY.md", fl_md)
    qc_tsv, qc_sum = _quote_outputs(views)
    _write_new(out_dir / "QUOTE-CONTINUATIONS.tsv", qc_tsv)
    st_tsv, st_sum = _structural_tails_outputs(views)
    _write_new(out_dir / "STRUCTURAL-TAILS.tsv", st_tsv)
    print("P09-49 moved blocks (current FOOTNOTE_START vs v4):\n" + mb_sum + fl_sum
          + "P09-52 quote continuations:\n" + qc_sum + "P09-53 structural tails (SECTION-LIST sections):\n" + st_sum, end="")
    mk = ["file\tsection\ttype\tpage_1based\tline_1based\tnumbers\tmatch"]
    mk += [f"{r['edition']}.pdf\t{r['act']} s.{r['section']}\t{d['type']}\t{d['page_1based']}\t{d['line_1based']}\t"
           f"{' '.join(d['numbers'])}\t{' '.join(m or '-' for m in d['match'])}"
           for r in found for d in r["dropped_markers"]]
    _write_new(out_dir / "DROPPED-MARKERS.tsv", "\n".join(mk) + "\n")
    _write_new(out_dir / "MARKER-LINKS.md", _marker_links_md(found))
    _write_new(out_dir / "BRACKET-ORPHANS.md", _bracket_orphans_md(views, found))
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


def _marker_links_md(found: list) -> str:
    """P09-43: MARKER-LINKS.md, per pilot section."""
    out = ["# MARKER LINKS (pilot, P09-43)", "",
           "Markers in body order -> footnote entries (pages of the section + 1 page). link: number |",
           "assigned_by_order | ambiguous (number occurs 2+ times; never picked) | none. Footnotes without a marker",
           "may belong to a neighbouring section printed on the same pages.", ""]
    for r in found:
        ml = r["marker_links"]
        if not (ml["links"] or ml["footnotes_without_marker"] or ml["symbol_notes"]):
            continue
        out += [f"## {r['stem']}", "", "| marker | page_1based | line_1based | type | match | link | footnote | text |",
                "|---|---|---|---|---|---|---|---|"]
        for x in ml["links"]:
            txt = (x["footnote_text"] or "").replace("\n", " / ").replace("|", "\\|")
            out.append(f"| {x['token']} | {x['page_1based']} | {x['line_1based']} | {x['marker_type']} | "
                       f"{x['match'] or '-'} | {x['link'] or 'none'} | {x['footnote'] or '-'} | {txt} |")
        out += ["", f"footnote without marker ({len(ml['footnotes_without_marker'])}):"]
        out += [f"- {f['footnote']} (page_1based {f['page_1based']}): {f['text'].replace(chr(10), ' / ')}"
                for f in ml["footnotes_without_marker"]]
        out += ["", f"marker without footnote ({len(ml['markers_without_footnote'])}):"]
        out += [f"- {x['token']} page_1based {x['page_1based']} line_1based {x['line_1based']} ({x['link'] or 'none'})"
                for x in ml["markers_without_footnote"]]
        out += ["", f"symbol notes ({len(ml['symbol_notes'])}):"]
        out += [f"- {s['symbol']} page_1based {s['page_1based']}: {s['text'].replace(chr(10), ' / ')}"
                for s in ml["symbol_notes"]]
        out.append("")
    return "\n".join(out) + "\n"


def _section_spans(v: EditionView, act: str, sections: list) -> dict:
    """{section: (status, first_idx, end_idx)} for bracket summaries (first = heading line, or a bare '[' line)."""
    spans = {}
    for sec in sections:
        loc = locate(v.cleaned.lines, v.starts, sec)
        if loc["status"] != "FOUND":
            spans[sec] = (loc["status"], None, None)
            continue
        h = loc["internal_heading_line_idx0"]
        first = h - 1 if (h > 0 and v.cleaned.lines[h - 1].text.strip() == "[") else h
        spans[sec] = ("FOUND", first, loc["internal_line_idx0_end"])
    return spans


def _bracket_orphans_md(views: list, found: list) -> str:
    """P09-42: BRACKET-ORPHANS.md: summary per edition and per SECTION-LIST section x edition, then every
    edition-level orphan (all 7 editions); pilot sections also get the nearest earlier marker + footnote."""
    sl = json.loads((STATUTES_DIR / "SECTION-LIST.json").read_text(encoding="utf-8"))
    secs = {"1961": [s["section"] for s in sl["sections_1961"]], "2025": [s["section"] for s in sl["sections_2025_only"]]}
    act_of = {k: a for a in EDITIONS for k in EDITIONS[a]}
    out = ["# BRACKET ORPHANS (P09-42)", "",
           "Brackets matched over each whole edition (kept lines after R0/R3, page order). An orphan is a ']' with",
           "nothing open or a '[' never closed before the end of the edition. Report only.", "",
           "## Summary per edition", "", "| edition | orphan ']' | orphan '[' |", "|---|---|---|"]
    for v in views:
        kinds = [k for _, k in v.cleaned.orphans]
        out.append(f"| {v.key} | {kinds.count(']')} | {kinds.count('[')} |")
    out += ["", f"## Summary per SECTION-LIST section x edition ({len(secs['1961']) + len(secs['2025'])} sections)", "",
            "| act | section | edition | status | carry_in | carry_out | orphan ']' | orphan '[' |",
            "|---|---|---|---|---|---|---|---|"]
    owner = {}
    for v in views:
        act = act_of[v.key]
        for sec, (st, a, b) in _section_spans(v, act, secs[act]).items():
            if st != "FOUND":
                out.append(f"| {act} | {sec} | {v.key} | {st} | - | - | - | - |")
                continue
            ks = [k for i, k in v.cleaned.orphans if a <= i < b]
            for i, _ in v.cleaned.orphans:
                if a <= i < b:
                    owner[(v.key, i)] = f"{act} s.{sec}"
            out.append(f"| {act} | {sec} | {v.key} | FOUND | {v.cleaned.depth_before[a]} | {v.cleaned.depth_after[b - 1]} | "
                       f"{ks.count(']')} | {ks.count('[')} |")
    pilot_orph = {(r["edition"], o["page_1based"], o["line_1based"], o["kind"]): o
                  for r in found for o in r["brackets"]["orphans"]}
    for v in views:
        out += ["", f"## {v.key}.pdf: every orphan ({len(v.cleaned.orphans)})", ""]
        for i, k in v.cleaned.orphans:
            ln = v.cleaned.lines[i]
            sec = owner.get((v.key, i), "(not in a SECTION-LIST section)")
            out.append(f"- '{k}' page_1based {ln.page} line_1based {ln.line_no} [{sec}]: {ln.text.strip()[:140]}")
            po = pilot_orph.get((v.key, ln.page, ln.line_no, k))
            if po is not None:
                nm = po.get("nearest_earlier_marker")
                out.append("  - nearest earlier marker: " + (
                    f"{nm['token']} (page_1based {nm['page_1based']} line_1based {nm['line_1based']}) -> "
                    f"{nm['footnote'] or 'no footnote'}: {(nm['footnote_text'] or '').replace(chr(10), ' / ')}"
                    if nm else "none in the section"))
    return "\n".join(out) + "\n"


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
        "line-marker tokens dropped by match: exact="
        f"{sum(1 for r in found for d in r['dropped_markers'] if d['type'] == 'line' for m in d['match'] if m == 'exact')} "
        "matched_by_family="
        f"{sum(1 for r in found for d in r['dropped_markers'] for m in d['match'] if m == 'matched_by_family')}",
        "marker links: " + ", ".join(
            f"{k}={sum(1 for r in found for x in r['marker_links']['links'] if (x['link'] or 'none') == k)}"
            for k in ("number", "assigned_by_order", "ambiguous", "none")),
        f"footnotes without marker: {sum(len(r['marker_links']['footnotes_without_marker']) for r in found)}  "
        f"markers without footnote: {sum(len(r['marker_links']['markers_without_footnote']) for r in found)}",
        f"symbol notes (P09-44): {sum(r['symbol_notes'] for r in found)}  body symbol lines: "
        f"{sum(r['body_symbol_lines'] for r in found)}",
        "edition-level bracket orphans: " + ", ".join(
            f"{v.key}=]{sum(1 for _, k in v.cleaned.orphans if k == ']')}/[{sum(1 for _, k in v.cleaned.orphans if k == '[')}"
            for v in views),
        f"bracket WARNs (pilot sections with edition-level orphans): {sum(1 for r in found if r['brackets']['warn'])} "
        + str([(r["stem"], len(r["brackets"]["orphans"])) for r in found if r["brackets"]["warn"]]),
        f"tables with start/end: {sum(1 for r in found for t in r['tables'] if _has_span(t))}"
        f" of {sum(len(r['tables']) for r in found)}",
        f"hyphen joins: {sum(r['hyphen_joins'] for r in found)}  not joined (table row): "
        f"{sum(r['hyphen_not_joined'] for r in found)}",
    ]
    return "\n".join(lines) + "\n"


def print_pilot(results: list) -> None:
    print(f"{'act':<5} {'sec':<7} {'edition':<15} {'found':<5} {'pages_1based':<12} {'chars':>6} {'tbls':>4} "
          f"{'rows':>4} {'unres':>5} {'mk-':>3} {'mk?':>3} {'ed':>2} {'in/out/orph':>11} sha256")
    for r in results:
        if r["status"] == "FOUND":
            pg = f"{r['pages_1based'][0]}-{r['pages_1based'][-1]}"
            b = r["brackets"]
            br = f"{b['carry_in']}/{b['carry_out']}/{len(b['orphans'])}" + ("!" if b["warn"] else "")
            print(f"{r['act']:<5} {r['section']:<7} {r['edition']:<15} {'yes':<5} {pg:<12} {r['chars']:>6} "
                  f"{len(r['tables']):>4} {r['table_rows']:>4} {len(r['unresolved']):>5} {len(r['dropped_markers']):>3} "
                  f"{len(r['unresolved_markers']):>3} {len(r['editor_note_candidates']):>2} {br:>11} {r['sha256']}")
        else:
            print(f"{r['act']:<5} {r['section']:<7} {r['edition']:<15} {'NO':<5} {r['status']:<12} "
                  f"candidates={[c['page_1based'] for c in r['candidates']]}")


# ---------------------------------------------------------------- P09-47 marker confirmation (check only)

CONFIRM_RATIO, RAISE_FRACTION = 0.85, 0.15


def effective_run(text: str, cm: list, tm: list, font_size: float) -> dict:
    """One pypdf visitor run -> {s, size, x, y}: size = font_size x the vertical scale of tm x cm; (x, y) = the
    translation of tm x cm (PDF units, y upwards)."""
    a, b, c, d, e, f = tm
    A, B, C, D, E, F = cm
    m = (a * A + b * C, a * B + b * D, c * A + d * C, c * B + d * D, e * A + f * C + E, e * B + f * D + F)
    return {"s": text.strip(), "size": (font_size or 0) * (m[2] ** 2 + m[3] ** 2) ** 0.5, "x": m[4], "y": m[5]}


def mark_runs(runs: list) -> float:
    """Adds 'ratio' and 'raised' to each run; returns the page's most common size (weighted by characters).
    raised = baseline >= RAISE_FRACTION x body above the nearest body-size run within one body size vertically
    (None when no such run exists)."""
    weight = {}
    for r in runs:
        weight[round(r["size"], 1)] = weight.get(round(r["size"], 1), 0) + len(r["s"])
    body = max(weight, key=weight.get) if weight else 0
    for r in runs:
        r["ratio"] = r["size"] / body if body else 0
        refs = [q for q in runs if q is not r and q["size"] >= 0.9 * body and abs(q["y"] - r["y"]) <= body]
        if refs and body:
            ref = min(refs, key=lambda q: (abs(q["y"] - r["y"]) > 0.05 * body, abs(q["x"] - r["x"])))
            r["raised"] = (r["y"] - ref["y"]) >= RAISE_FRACTION * body
        else:
            r["raised"] = None
    return body


def classify_marker(runs: list, token: str, line_text: str | None = None) -> dict:
    """P09-47: label one dropped marker token against the page's runs (after mark_runs)."""
    cands = [r for r in runs if r["s"] == token or (line_text and r["s"] == line_text)]
    if not cands:
        return {"ratio": None, "raised": None, "candidates": 0, "label": "no_run"}
    best = next((r for r in cands if r["raised"] or r["ratio"] <= CONFIRM_RATIO), cands[0])
    ok = bool(best["raised"]) or best["ratio"] <= CONFIRM_RATIO
    return {"ratio": round(best["ratio"], 2), "raised": best["raised"], "candidates": len(cands),
            "label": "confirmed" if ok else "unconfirmed"}


def page_visitor_runs(reader, page: int) -> list:
    runs = []

    def vis(text, cm, tm, font_dict, font_size):
        if text and text.strip():
            runs.append(effective_run(text, cm, tm, font_size))
    reader.pages[idx0_from_page(page)].extract_text(visitor_text=vis)
    return runs


def run_confirm_markers(folder: Path, raw: Path) -> Path:
    """P09-47: MARKER-CONFIRM.md for every dropped marker in a pilot folder. Check only; nothing is put back."""
    from pypdf import PdfReader
    readers, cache, rows = {}, {}, []
    for meta_path in sorted(folder.glob("*.meta.json")):
        m = json.loads(meta_path.read_text(encoding="utf-8"))
        if m.get("status") != "FOUND":
            continue
        for d in m["dropped_markers"]:
            key = (m["edition"], d["page_1based"])
            if key not in cache:
                if m["edition"] not in readers:
                    readers[m["edition"]] = PdfReader(str(raw / f"{m['edition']}.pdf"))
                runs = page_visitor_runs(readers[m["edition"]], d["page_1based"])
                mark_runs(runs)
                cache[key] = runs
            for tok in d["numbers"]:
                c = classify_marker(cache[key], tok, " ".join(d["numbers"]))
                rows.append((f"{m['edition']}.pdf", f"{m['act']} s.{m['section']}", d["page_1based"], d["line_1based"],
                             d["type"], tok, c))
    seen, uniq = set(), []
    for r in rows:                                   # a page shared by two pilot sections is reported once
        k = (r[0], r[2], r[3], r[5])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    counts = {lab: sum(1 for r in uniq if r[6]["label"] == lab) for lab in ("confirmed", "unconfirmed", "no_run")}
    out = ["# MARKER CONFIRM (P09-47, check only; nothing put back)", "",
           f"rule: confirmed = a visitor run with the same text is raised, or its size ratio <= {CONFIRM_RATIO} "
           "vs the page's most common size; else unconfirmed; no_run = no run with that text.", "",
           f"tokens: {len(uniq)}  " + "  ".join(f"{k}={v}" for k, v in counts.items()), "",
           "| file | section | page_1based | line_1based | type | token | ratio | raised | candidates | label |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for f, sec, p, ln, typ, tok, c in uniq:
        out.append(f"| {f} | {sec} | {p} | {ln} | {typ} | {tok} | {c['ratio']} | {c['raised']} | {c['candidates']} | "
                   f"{c['label']} |")
    path = folder / "MARKER-CONFIRM.md"
    _write_new(path, "\n".join(out) + "\n")
    print(f"P09-47 tokens={len(uniq)} " + " ".join(f"{k}={v}" for k, v in counts.items()))
    return path


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
    mode.add_argument("--confirm-markers", metavar="PILOT_DIR", help="P09-47 check-only marker report")
    ap.add_argument("--raw-dir", help="download folder (default: newest dated folder under _raw/)")
    ap.add_argument("--jobs", type=int, default=1, help="--prepare: parallel processes")
    args = ap.parse_args(argv)
    if args.confirm_markers:
        path = run_confirm_markers(Path(args.confirm_markers), Path(args.raw_dir) if args.raw_dir else latest_raw_dir())
        print(f"written {path}")
        return 0
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
        print("P09-46 page-edge digits (whole editions):\n" + _edge_summary(views), end="")
        print(f"written {out}")
        return 0
    trace = Trace()
    run_pilot(raw, CENSUS_DIR / "pilot" / f"{stamp}-rules", trace)
    print_rules(trace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
