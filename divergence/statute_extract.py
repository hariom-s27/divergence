"""P09 statute extractor: edition PDF -> per-section text (deterministic, no model calls).

Run from the repo root:
    python -m divergence.statute_extract --prepare [--jobs N]  build the page-text cache for all editions
    python -m divergence.statute_extract --locate-all     locate every SECTION-LIST / MAPPING section in every edition
    python -m divergence.statute_extract --pilot          extract the Part B pilot sections -> census/pilot/<stamp>/
    python -m divergence.statute_extract --show-rules     print rule examples (before/after) from the pilot text

Processing order (fixed, extractor v1): R0 (duplicate pages) -> R3 (page furniture + footnotes)
-> R1/R2 (locate start/end) -> R5 (table-row prefixes) -> R4 (whitespace + line joins). R5 runs
before R4 because R5 reads the indentation that R4 removes, and R4 never joins a line that starts
with a table-row prefix.

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
  R4  whitespace only: tabs / NBSP / unicode spaces -> space, runs collapsed, line ends stripped; a line
      is joined to the previous one unless the previous ends in . : ; or a dash, or the line starts
      with a structural marker. No de-hyphenation, no quote/currency/case change.
  R5  tables: a region starts at a line that is only 'TABLE'/'Table'; tables are numbered k = 1, 2, ...
      in order of appearance within the section [D6]; rows 'N.' must be sequential (1, 2, 3 ...) and
      get '[Table k Sl. N] '; a sub-row is an indented '(roman)' or a '(roman)' followed by NBSP, and
      must be sequential within its row ((i), (ii), ...) to get '[Table k Sl. N(roman)] ' [D2]; a
      non-sequential numbered line inside a table is listed as unresolved.

Mechanical fixes made during the Part B pilot and accepted by the owner as part of v1:
  M1  'N.(1)' with no space after the dot is a valid start.
  M2  the footer date pattern accepts 'm/d/yy, h:mm PM' as well as 'dd/mm/yyyy, h:mm am'.
  M3  headings are taken shortest first and never include CHAPTER / part / Schedule / Act-title /
      all-caps lines or a line starting with a digit.
  M4  no section starts inside the Schedules region.
  M5  table rows may be indented with NBSP + space.
  M6  'N.--...' / 'N. -...' is a numbered part heading, not a section start.
  M7  R2 also ends a section at an all-caps Act title line.

fold_for_diff() (fold v1) is for Part C edition diffs only and is never applied to stored bodies.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

EXTRACTOR_VERSION = "v1"
FOLD_VERSION = "v1"

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
TABLE_END_RE = re.compile(r"^(?:\(\d+[A-Z]*\)\s|Explanation)")
ROW_RE = re.compile(r"^\s*(\d{1,2})\.\s")
PART_NUMBER_RE = re.compile(r"^\s*\d{1,3}[A-Z]{0,5}\s?\.\s*[—–-]")
ROMAN = r"((?:x{0,2})(?:ix|iv|v?i{0,3}))"
SUBROW_INDENT_RE = re.compile(r"^\s{2,}\(" + ROMAN + r"\)\s{2,}")
SUBROW_NBSP_RE = re.compile(r"^\s*\(" + ROMAN + r"\)\s* ")
NUMBERED_RE = re.compile(r"^\s*\d{1,2}\.\s")
SUBSECTION_RE = re.compile(r"^\s*(?:\d{1,3}[A-Z]{0,5}\s?\.\s*)?\((\d+[A-Z]*)\)\s")
SPACES_RE = re.compile("[ \t  -   　]+")
TERMINAL = (".", ":", ";", "—", "–")
STRUCTURAL_RE = re.compile(
    r"^(?:\(\d+[A-Z]*\)|\([a-z]{1,4}\)|\([ivxl]+\)|Explanation|Provided|\[Table \d+ Sl\.|TABLE$|Table$|"
    r"\d+[A-Z]*\s?\.(?:\s|$))")
_ROMAN_VALUES = {r: i for i, r in enumerate(
    ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv",
     "xvi", "xvii", "xviii", "xix", "xx"], 1)}


# ---------------------------------------------------------------- data

@dataclass
class Line:
    page: int
    text: str


@dataclass
class Cleaned:
    lines: list
    notes: dict                                    # page -> footnote lines (verbatim)
    furniture: list = field(default_factory=list)  # (page, line) removed
    midpage_footnote_pages: list = field(default_factory=list)
    footnote_lines: int = 0


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


def section_key(num: str) -> tuple:
    m = re.match(r"^(\d+)([A-Z]*)$", num)
    if not m:
        raise ValueError(f"bad section number {num!r}")
    return int(m.group(1)), m.group(2)


# ---------------------------------------------------------------- R0

def drop_duplicate_pages(pages: list) -> tuple:
    """R0: returns (kept_pages, dropped) where dropped = [(page, duplicate_of_page)]; page numbers are kept."""
    first_seen, kept, dropped = {}, [], []
    for pno, text in enumerate(pages, 1):
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
    """R3 on every page. pages[i] is the raw text of page i+1."""
    out, notes, furn, midpage, n_foot = [], {}, [], [], 0
    for pno, text in enumerate(pages, 1):
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
            if ln.strip():
                kept.append(Line(pno, ln))
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
    return Cleaned(out, notes, furn, midpage, n_foot)


# ---------------------------------------------------------------- R5 state machine (shared by R1 and R5)

def table_marks(lines: list) -> tuple:
    """Returns (marks, tables). marks: idx -> ('row', k, N) | ('subrow', k, N, roman) | ('unresolved', reason);
    tables: [(k, idx_of_TABLE_line)] in order of appearance."""
    marks, tables = {}, []
    in_table, last_row, last_sub = False, 0, 0
    for i, ln in enumerate(lines):
        t = ln.text
        if TABLE_START_RE.match(t):
            in_table, last_row, last_sub = True, 0, 0
            tables.append((len(tables) + 1, i))
            continue
        if not in_table:
            continue
        k = len(tables)
        if CHAPTER_RE.match(t) or TABLE_END_RE.match(t):
            in_table = False
            continue
        m = ROW_RE.match(t)
        if m and int(m.group(1)) == last_row + 1:
            last_row, last_sub = last_row + 1, 0
            marks[i] = ("row", k, last_row)
            continue
        s = SUBROW_INDENT_RE.match(t) or SUBROW_NBSP_RE.match(t)
        if s and s.group(1) and last_row:
            if _ROMAN_VALUES.get(s.group(1)) == last_sub + 1:
                last_sub += 1
                marks[i] = ("subrow", k, last_row, s.group(1))
            continue
        if START_RE.match(t) and _heading_before(lines, i):
            in_table = False          # a real section start ends the table
            continue
        if NUMBERED_RE.match(t):
            marks[i] = ("unresolved", f"non-sequential numbered line in table {k} (last row {last_row})")
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
    if len(hits) != 1:
        return {"status": "NOT_FOUND" if not hits else "UNRESOLVED",
                "candidates": [(lines[s.idx].page, s.heading[:60]) for s in hits]}
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
    return {"status": "FOUND", "start": s.idx, "end": end, "heading": s.heading, "pages": pages,
            "candidates": [(lines[s.idx].page, s.heading[:60])]}


# ---------------------------------------------------------------- R5 + R4 on one section

def apply_tables(lines: list, trace: Trace | None = None) -> tuple:
    """R5: returns (texts, rows_prefixed, unresolved, table_map).
    table_map: [{'table': k, 'page': p, 'subsection': '(1)' or None}]."""
    marks, tables = table_marks(lines)
    table_at = {idx: k for k, idx in tables}
    texts, rows, unresolved, table_map = [], 0, [], []
    subsection = None
    for i, ln in enumerate(lines):
        sm = SUBSECTION_RE.match(ln.text)
        if sm and not ln.text.startswith((" ", "\t", " ")):
            subsection = f"({sm.group(1)})"
        if i in table_at:
            table_map.append({"table": table_at[i], "page": ln.page, "subsection": subsection})
        mk = marks.get(i)
        if mk and mk[0] == "row":
            new = f"[Table {mk[1]} Sl. {mk[2]}] " + ln.text.strip()
            rows += 1
        elif mk and mk[0] == "subrow":
            new = f"[Table {mk[1]} Sl. {mk[2]}({mk[3]})] " + ln.text.strip()
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


def normalise(texts: list, trace: Trace | None = None) -> str:
    """R4: whitespace + line joins. Returns the body (LF, ends with one newline)."""
    out = []
    for t in texts:
        s = SPACES_RE.sub(" ", t).strip()
        if trace and s != t.strip():
            before, after = _first_diff_snippet(t.strip(), s)
            trace.add("R4-space", repr(before), repr(after))
        if not s:
            continue
        if out and not out[-1].endswith(TERMINAL) and not STRUCTURAL_RE.match(s):
            if trace:
                trace.add("R4-join", f"{out[-1][-40:]!r} + {s[:40]!r}", repr((out[-1] + ' ' + s)[-80:]))
            out[-1] = out[-1] + " " + s
        else:
            out.append(s)
    return "\n".join(out) + "\n" if out else ""


def extract_section(cleaned: Cleaned, starts: list, number: str, trace: Trace | None = None) -> dict:
    loc = locate(cleaned.lines, starts, number)
    if loc["status"] != "FOUND":
        return loc
    seg = cleaned.lines[loc["start"]:loc["end"]]
    texts, rows, unresolved, table_map = apply_tables(seg, trace)
    body = normalise(texts, trace)
    p0, p1 = loc["pages"][0], loc["pages"][-1]
    note_lines = [f"[p.{p}] {ln.strip()}" for p in range(p0, p1 + 1) for ln in cleaned.notes.get(p, [])]
    loc.update({"body": body, "chars": len(body), "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "table_rows": rows, "unresolved": unresolved, "tables": table_map,
                "amendment_note": "\n".join(note_lines) if note_lines else None})
    return loc


# ---------------------------------------------------------------- fold (Part C diffs only)

_DQ = dict.fromkeys(map(ord, "“”„‟″〝〞＂"), '"')
_SQ = dict.fromkeys(map(ord, "‘’‚‛′＇"), "'")
_LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}
RUPEE_RE = re.compile(r"(?:₹|\bRs\b\.?)\s*")


def fold_for_diff(text: str) -> str:
    """Fold v1 for edition diffs ONLY: curly/straight quotes and apostrophes, '₹'/'Rs.'/'Rs' -> one
    token, ligatures (ﬀ ﬁ ﬂ ﬃ ﬄ) -> letters [D5], NBSP -> space (runs collapsed). Never applied to
    stored bodies."""
    s = text.translate(_DQ).translate(_SQ)
    for lig, letters in _LIGATURES.items():
        s = s.replace(lig, letters)
    s = RUPEE_RE.sub("<RUPEE> ", s)
    s = "\n".join(SPACES_RE.sub(" ", ln).strip() for ln in s.split("\n"))
    return s


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
        for i, t in enumerate(texts, 1):
            f.write(json.dumps({"page": i, "text": t}, ensure_ascii=False) + "\n")
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
    out = ["edition\tpage\tduplicate_of"]
    out += [f"{v.key}\t{p}\t{d}" for v in views for p, d in v.dropped]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- CLI actions

def run_locate_all(raw: Path, out_dir: Path) -> int:
    tg = targets()
    out_dir.mkdir(parents=True, exist_ok=False)
    lines_out = [f"LOCATE-ALL  extractor {EXTRACTOR_VERSION}  pypdf {pypdf_version()}  raw={raw}",
                 f"{'act':<5} {'section':<10} {'edition':<15} {'status':<10} {'n':>2} {'pages':<16} heading"]
    counts, views = {}, []
    for act in ("1961", "2025"):
        for key in EDITIONS[act]:
            v = edition_view(raw, key)
            views.append(v)
            for sec in tg[act]:
                r = locate(v.cleaned.lines, v.starts, sec)
                counts[r["status"]] = counts.get(r["status"], 0) + 1
                if r["status"] == "FOUND":
                    pg = f"{r['pages'][0]}-{r['pages'][-1]}"
                    head = r["heading"][:60]
                else:
                    pg = ",".join(str(p) for p, _ in r["candidates"][:6]) or "-"
                    head = " | ".join(h for _, h in r["candidates"][:3])
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
    print(f"written {out_dir / 'LOCATE-ALL.txt'} and DROPPED-PAGES.tsv")
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
                if r["status"] == "FOUND":
                    _write_new(out_dir / f"{stem}.txt", r["body"])
                    r["page_chars"] = {p: len(v.pages[p - 1]) for p in r["pages"]}
                meta = {k: val for k, val in r.items() if k != "body"}
                meta["extractor_version"] = EXTRACTOR_VERSION
                _write_new(out_dir / f"{stem}.meta.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
                if r["status"] != "FOUND" or r.get("unresolved"):
                    unresolved_md.append(f"## {stem}: {r['status']}")
                    if r["status"] != "FOUND":
                        unresolved_md += [f"- candidate p{p}: {h}" for p, h in r["candidates"]]
                    unresolved_md += [f"- {u}" for u in r.get("unresolved", [])]
                    unresolved_md.append("")
                results.append(r)
    _write_new(out_dir / "UNRESOLVED.md", "\n".join(unresolved_md) + "\n")
    _write_new(out_dir / "DROPPED-PAGES.tsv", _dropped_tsv(views))
    tmap = ["# TABLE MAP (pilot)", ""]
    for r in results:
        if r["status"] == "FOUND" and r["tables"]:
            tmap.append(f"## {r['act']} s.{r['section']} {r['edition']}")
            tmap += [f"- Table {t['table']}: p.{t['page']}, in {t['subsection'] or '(no sub-section)'}" for t in r["tables"]]
            tmap.append("")
    _write_new(out_dir / "TABLE-MAP.md", "\n".join(tmap) + "\n")
    return results


def print_pilot(results: list) -> None:
    print(f"{'act':<5} {'sec':<7} {'edition':<15} {'found':<5} {'pages':<11} {'chars':>6} {'tbls':>4} {'rows':>4} "
          f"{'unres':>5} sha256")
    for r in results:
        if r["status"] == "FOUND":
            pg = f"{r['pages'][0]}-{r['pages'][-1]}"
            print(f"{r['act']:<5} {r['section']:<7} {r['edition']:<15} {'yes':<5} {pg:<11} {r['chars']:>6} "
                  f"{len(r['tables']):>4} {r['table_rows']:>4} {len(r['unresolved']):>5} {r['sha256']}")
        else:
            print(f"{r['act']:<5} {r['section']:<7} {r['edition']:<15} {'NO':<5} {r['status']:<11} "
                  f"candidates={[p for p, _ in r['candidates']]}")


def print_rules(trace: Trace) -> None:
    print(f"EXTRACTOR {EXTRACTOR_VERSION} RULES (order R0 -> R3 -> R1/R2 -> R5 -> R4)")
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
    ap.add_argument("--raw-dir", help="download folder (default: newest dated folder under _raw/)")
    ap.add_argument("--jobs", type=int, default=1, help="--prepare: parallel processes")
    args = ap.parse_args(argv)
    raw = Path(args.raw_dir) if args.raw_dir else latest_raw_dir()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if args.prepare:
        prepare_all(raw, args.jobs)
        return 0
    if args.locate_all:
        return run_locate_all(raw, CENSUS_DIR / "locate" / stamp)
    if args.pilot:
        out = CENSUS_DIR / "pilot" / stamp
        results = run_pilot(raw, out)
        print_pilot(results)
        print(f"written {out}")
        return 0
    trace = Trace()
    run_pilot(raw, CENSUS_DIR / "pilot" / f"{stamp}-rules", trace)
    print_rules(trace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
