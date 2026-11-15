"""P09 Part C1 - amending-instrument ledger for the spine sections ("act_parse v1").

Reads the held Gazette / ITD text of each amending instrument (pypdf page text, local only), and proposes one ledger row
per amending sub-item that touches a spine section. Every value comes from fixed patterns over the printed text; the
owner confirms. Nothing here reads the network, an API key or an environment variable.

Layout clean-up (rows 73/80): page-1 Gazette masthead (English lines + the Hindi line printed just before each),
Devanagari lines, the running head (printed page number kept and checked against the PDF page), and margin-note runs at
the head (just after the running head) or tail of a page (closed starters: 'Amendment of', 'Insertion of new', ...,
'N of YYYY.', 'Act N of YYYY.'; continuation lines short and without a body terminator).

Target Act (row 81): '(hereinafter|herein referred to as X)' binds alias X Act-wide (latest binding wins);
'(hereafter in this Part ... referred to as X)' binds X until the next Part heading ('A.--', 'PART I'). An item head
'... section S of the <phrase>' resolves the phrase: 'Income-tax Act, 1961/2025' literally, else through the bindings.
Anything else (another Act, unresolved alias) is not the Income-tax Act and gives no spine row.

Items and sub-items: numbered items in strict sequence (1, 2, 3, ...); sub-item markers (a)/(i)/(A)/(I) at a line
start after a line that ends with a terminator; quoted inserted blocks (after 'namely:--' / ',--' and an opening quote,
up to the line ending in the matching closing quote + ';' or '.') are never split. One row per leaf sub-item.
'After section X ... inserted' and 'For Chapter C ... substituted' target the section headings inside the inserted text.

Commencement (row 73), first match wins: item_deemed (a 'with effect from <date>' in the leaf's own words),
header_inherited (the nearest ancestor header with one), s1_default (s.1(2) range, both wordings), notification
(a s.1(2) notification range: never a date here -> applicability_unclear + MANUAL NEEDED), else unknown (flagged).
'deemed to have been <verb>' with no date anywhere in the chain -> unknown, flag deemed_without_date. w.e.f. earlier
than the assent date -> deemed_from = w.e.f. (both kept). In-text 'on or after' / 'as it stood' / 'shall not apply on
or after' are applicability_note_present=yes, never commencement.

Public output: AMENDMENT-EFFECTS.csv (hashes and pointers only, no law text). Quotes: _local_text/quotes/ only.
Files are never overwritten: a rerun writes a new dated file and prints a merge preview that keeps the owner columns.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from divergence import statute_extract as se
from divergence import statute_sources as ss

ACT_PARSE_VERSION = "act_parse v1"

# Spine (owner D1 = c; P09 Part C prompt). s.397 is batch 2.
SPINE = {"1961": ["2", "3", "56", "115BBH", "158B", "194S", "285BAA"],
         "2025": ["1", "2", "3", "92", "194", "301", "393", "400", "446", "509", "536"]}
# Amending instruments in date order (SOURCES.json keys; row 88: fa_2025_gz and tola_2026_gz preferred)
INSTRUMENT_KEYS = ["fa_2022", "fa_2023", "fa_2024", "fa2_2024", "fa_2025_gz", "fa_2026", "tola_2026_gz", "ord_2_2026"]
CORRIGENDA = {"fa_2022": "corr_fa2022", "fa_2023": "corr_fa2023", "fa_2026": "corr_fa2026"}

EFFECT_COLUMNS = ["effect_id", "act_key", "instrument_provision", "target_act", "target_section", "target_unit",
                  "operation", "commencement_source", "wef", "deemed_from", "assent_date",
                  "applicability_note_present", "corrigendum_flag", "pdf_page", "quote_sha256", "owner_ok",
                  "owner_note"]
OWNER_COLUMNS = ("owner_ok", "owner_note")
OPERATIONS = ("insert", "substitute", "omit", "renumber", "other")
COMMENCEMENT = ("item_deemed", "header_inherited", "s1_default", "notification", "unknown")
QUOTE_LINE_CAP = 8
LOOKAHEAD_MAX = 8

EFFECTS_PATH = se.STATUTES_DIR / "AMENDMENT-EFFECTS.csv"
QUOTES_PATH = se.LOCAL_DIR / "quotes" / "EFFECT-QUOTES.csv"
PARTC_DIR = se.CENSUS_DIR / "partC"
REGEN_DIR = PARTC_DIR / "regen"                 # stamped regenerations (git-ignored); canonical files are never rewritten
# Owner readings stored as data (dated). E3: one leaf with two coupled operations -> two effects.
OWNER_SPLITS = {
    "fa_2026:s84(c)": {"date": "2026-11-15", "wef": "2027-04-01", "operations": ["renumber", "insert"],
                       "owner_note": "owner reading: coupled operations; ITD footnote agrees (secondary)"},
}

# ---------------------------------------------------------------- layout patterns
DEVANAGARI = re.compile(r"[\u0900-\u097F]")
MASTHEAD_RE = [re.compile(p) for p in (
    r"REGISTERED\s+N\s?O\.", r"^xxxGID[HE]xxx$", r"^EXTRAORDINARY$", r"^PART\s+II\s*[—–-]+\s*Section\s+1$",
    r"^PUBLISHED\s+BY\s+AUTHORITY$", r"^No\.\s*\d+\]\s+NEW DELHI", r"^Separate paging is given", r"CG-DL-E-\d")]
RUNNING_HEAD_RE = re.compile(r"^(?:(\d{1,4})\s+THE\s+GAZETTE\s+OF\s+INDIA\s+EXTRAORDINARY\s*\[\s*P\s?(?:ART|art)\s+II"
                             r"|SEC\.\s*1\]\s+THE\s+GAZETTE\s+OF\s+INDIA\s+EXTRAORDINARY\s+(\d{1,8}))", re.I)
MARGIN_START_RE = re.compile(r"^(?:Amendment(?:\s+of)?|Insertion\s+of(?:\s+new)?|Substitution\s+of(?:\s+new)?|"
                             r"Omission\s+of|Short\s+title\s+and|Amendment\s+of\s+section\s+\S+\.?|"
                             r"\d{1,3}\s+of\s+\d{4}\.|Act\s+\d{1,3}\s+of\s+\d{4}\.)$")
MARGIN_ACTNO_RE = re.compile(r"^(?:Act\s+)?\d{1,3}\s+of\s+\d{4}\.$")
MARGIN_MAX = 34
GLUED_MARGIN_RE = re.compile(r"^commencement\.\s+(?=\d)")
STRUCTURAL_RE = re.compile(r"^(?:CHAPTER\s+[IVXLC]+|PART\s+[IVXLC]+|[A-Z]\.\s*[–—-]+)|^[^a-z0-9]*[A-Z]{3,}[^a-z]*$")
BODY_END_RE = re.compile(r"[;:,—–]\s*$|[—–-]{2}\s*$")

# ---------------------------------------------------------------- item patterns
ITEM_RE = re.compile(r"^\s*(\d{1,3})\s*\.\s*(?:\(\s*1\s*\)\s*)?(?=[A-Z(“‘\"'])")
MARKER_RE = re.compile(r"^\s*\(\s*([a-z]{1,4}|[A-Z]{1,4})\s*\)\s")
TERMINATED_RE = re.compile(r"(?:[;:.—–]|[—–-]{2}|[’'”\"][;.])\s*(?:and|or)?\s*$")
OPEN_QUOTES = "‘'“\""
CLOSE_FOR = {"‘": "’'", "'": "'’", "“": "”\"", "\"": "\"”"}
BLOCK_OPENER_RE = re.compile(r"(?:namely\s*:?\s*[—–-]+|[,:]\s*[—–-]+)\s*$")
VERB_RE = re.compile(r"shall\s+be\s+(inserted|substituted|omitted|renumbered|re-numbered|relettered|re-lettered)")
VERB_MAP = {"inserted": "insert", "substituted": "substitute", "omitted": "omit", "renumbered": "renumber",
            "re-numbered": "renumber", "relettered": "renumber", "re-lettered": "renumber"}
DEEMED_VERB_RE = re.compile(r"deemed\s+to\s+have\s+been\s+(?:inserted|substituted|omitted|renumbered)")
_MON = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
DATE_RE = re.compile(r"(\d{1,2})\s*(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?" + _MON + r",?\s*(\d{4})")
WEF_RE = re.compile(r"with\s+effect\s+from\s+the\s+(\d{1,2}\s*(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?" + _MON
                    + r",?\s*\d{4})")
APPLIC_RE = re.compile(r"on\s+or\s+after|as\s+it\s+stood|shall\s+not\s+apply\s+on\s+or\s+after|beginning\s+on\s+or\s+"
                       r"after|immediately\s+(?:prior|before)\s+to\s+the\s+commencement", re.I)
HEAD_TARGET_RE = re.compile(r"^\s*\d{1,3}\s*\.\s*(?:\(\s*1\s*\)\s*)?(In|After|For|Before|Section|Sections)\s+"
                            r"(sections?|Chapter)?\s*([0-9][0-9A-Z\-]*|[IVXLC]+(?:-[A-Z]{1,3})?)"
                            r"(?:\s+and\s+(?:section\s+)?([0-9][0-9A-Z\-]*))?\s+of\s+the\s+(.{3,90})")
HEAD_SECTION_FIRST_RE = re.compile(r"^\s*\d{1,3}\s*\.\s*(Section|Sections)\s+([0-9][0-9A-Z\-]*)\s+of\s+the\s+(.{3,90})")
ACT_PHRASE_RE = re.compile(r"^((?:[A-Z][\w\-().]*\s+)*?(?:Act|Code|Ordinance)(?:,\s*\d{4})?)")
BIND_RE = re.compile(r"\((hereinafter|herein|hereafter\s+in\s+this\s+(?:Part|Chapter)[^)]*?)\s+referred\s+to\s+as\s+"
                     r"(?:the\s+)?([^)]+?)\)", re.I)
ACT_BEFORE_RE = re.compile(r"((?:[A-Z][\w\-().]*\s+){0,6}?(?:Act|Code|Ordinance)),?\s*(\d{4})"
                           r"(?:\s*\(\s*\d+\s+of\s+\d{4}\s*\))?[,\s]*$")
SPLIT_WORD_RE = re.compile(r"here\s?in\s?af\s?ter|here\s?af\s?ter|re\s?fer\s?red")
PART_HEAD_RE = re.compile(r"^\s*(?:[A-Z]\.\s*[–—-]+|PART\s+[IVXLC]+(?:-[A-Z])?\s*$)")
INNER_HEADING_RE = re.compile(r"^\s*[‘'“\"]?\s*(\d{1,3}[A-Z]{0,6})\s*\.\s+")
UNIT_RE = re.compile(r"\b(?:in|after|for|before|against)\s+(?:the\s+)?(sub-section|sub-clause|clause|item|proviso|"
                     r"Explanation|Table|serial\s+number|column|opening\s+portion|long\s+line|marginal\s+heading|"
                     r"first\s+proviso|second\s+proviso|third\s+proviso)\s*(\(\s*[0-9A-Za-z]+\s*\))?")
S1_CLAUSE_RE = re.compile(r"(sections?\s+[^;]*?)\s+shall\s+(be\s+deemed\s+to\s+have\s+)?come\s+into\s+force\s+on\s+"
                          r"(?:the\s+)?(.{0,160}?)(?:;|\.$|\.\s|$)")
S1_WHOLE_RE = re.compile(r"\b(?:[Ii]t|this\s+Act|this\s+Ordinance)\s+shall\s+(be\s+deemed\s+to\s+have\s+)?come\s+into\s+"
                         r"force\s+on\s+(?:the\s+)?(.{0,40}?\d{4})")


def fold_ws(s: str) -> str:
    return " ".join(s.split())


def quote_sha256(quote: str) -> str:
    """sha256 of the UTF-8 quote after a whitespace-only fold (runs of whitespace -> one space, ends stripped)."""
    return hashlib.sha256(fold_ws(quote).encode("utf-8")).hexdigest()


def iso_date(text: str):
    m = DATE_RE.search(text or "")
    if not m:
        return None
    day, mon, year = m.groups()
    return f"{int(year):04d}-{ss.MONTHS[mon.lower()]:02d}-{int(day):02d}"


def norm_act_phrase(s: str) -> str:
    """'Income -tax Ac t' -> 'Income-tax Act' (pypdf spacing), whitespace folded."""
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\bAc\s+t\b", "Act", s)
    return fold_ws(s)


def act_class(name: str, year: str | None) -> str:
    """'1961' | '2025' | 'other:<name, year>' for an Act name as printed."""
    n = norm_act_phrase(name)
    n = re.sub(r"^(?:the|The)\s+", "", n)
    if n == "Income-tax Act" and year in ("1961", "2025"):
        return year
    return f"other:{n}{', ' + year if year else ''}"


# ---------------------------------------------------------------- layout clean-up

@dataclass
class L:
    page: int
    line: int
    text: str
    printed: int | None = None


@dataclass
class Cleaned:
    lines: list
    log: dict = field(default_factory=lambda: {"masthead": [], "devanagari": [], "running_head": [], "margin": [],
                                               "page_mismatch": []})


def _masthead_hit(t: str) -> bool:
    return any(r.search(t) for r in MASTHEAD_RE)


def _is_margin_cont(t: str) -> bool:
    s = t.strip()
    return (0 < len(s) <= MARGIN_MAX and not BODY_END_RE.search(s) and not STRUCTURAL_RE.match(s)
            and not s.startswith(tuple(OPEN_QUOTES) + ("(",)) and not ITEM_RE.match(s))


def _printed_number(m, pno: int) -> int | None:
    """Printed page number of a running head. Some heads print the number twice, glued ('4141', '33'): the glued
    half counts only when it equals the PDF page; otherwise the raw number is kept (and reported as a mismatch)."""
    g = m.group(1) or m.group(2)
    if not g:
        return None
    half = g[:len(g) // 2] if len(g) % 2 == 0 and g[:len(g) // 2] == g[len(g) // 2:] else None
    return pno if half is not None and int(half) == pno else int(g)


def clean_instrument(pages: list) -> Cleaned:
    """Body lines of an instrument with masthead, Devanagari, running heads and margin-note runs removed (logged)."""
    out = Cleaned([])
    for idx0, text in enumerate(pages):
        pno = idx0 + 1
        raw = text.splitlines()
        drop = set()
        if pno == 1:                                                   # masthead + the Hindi line before each
            for i, t in enumerate(raw):
                if _masthead_hit(t.strip()):
                    drop.add(i)
                    if i > 0 and not _masthead_hit(raw[i - 1].strip()):
                        drop.add(i - 1)
            for i in sorted(drop):
                out.log["masthead"].append((pno, i + 1, raw[i].strip()))
        for i, t in enumerate(raw):
            s = t.strip()
            if i in drop:
                continue
            if s and DEVANAGARI.search(s) and not re.search(r"[A-Za-z]", s):
                drop.add(i)
                out.log["devanagari"].append((pno, i + 1, s))
        printed = None
        first = next((i for i, t in enumerate(raw) if t.strip() and i not in drop), None)
        if first is not None:
            m = RUNNING_HEAD_RE.match(raw[first].strip())
            if m:
                drop.add(first)
                printed = _printed_number(m, pno)
                out.log["running_head"].append((pno, first + 1, raw[first].strip()))
                if printed != pno:
                    out.log["page_mismatch"].append((pno, printed, raw[first].strip()))
        keep = [i for i in range(len(raw)) if i not in drop and raw[i].strip()]
        # head run: just after the running head
        j = 0
        if keep and (MARGIN_START_RE.match(raw[keep[0]].strip()) or GLUED_MARGIN_RE.match(raw[keep[0]].strip())
                     or _is_margin_cont(raw[keep[0]])):
            run, has_start = [], False
            while j < len(keep):
                s = raw[keep[j]].strip()
                if GLUED_MARGIN_RE.match(s):
                    break
                if MARGIN_START_RE.match(s):
                    has_start = True
                elif not _is_margin_cont(s):
                    break
                run.append(keep[j])
                j += 1
            if has_start:
                for i in run:
                    drop.add(i)
                    out.log["margin"].append((pno, i + 1, raw[i].strip()))
            else:
                j = 0
        # tail run: from a margin starter to the page end, all short lines / starters
        keep = [i for i in range(len(raw)) if i not in drop and raw[i].strip()]
        for a in range(len(keep)):
            s = raw[keep[a]].strip()
            if MARGIN_START_RE.match(s) and all(MARGIN_START_RE.match(raw[k].strip()) or _is_margin_cont(raw[k])
                                                for k in keep[a + 1:]):
                for k in keep[a:]:
                    drop.add(k)
                    out.log["margin"].append((pno, k + 1, raw[k].strip()))
                break
        for i, t in enumerate(raw):
            if i in drop or not t.strip():
                continue
            s = t.rstrip()
            g = GLUED_MARGIN_RE.match(s.strip())
            if g:                                                       # 'commencement. 1. (1) This ...' (Ordinance)
                out.log["margin"].append((pno, i + 1, "commencement."))
                s = s.strip()[g.end():]
            out.lines.append(L(pno, i + 1, s, printed))
    return out


# ---------------------------------------------------------------- items, blocks, sub-items

@dataclass
class Node:
    marker: str
    kind: str
    lines: list = field(default_factory=list)        # own lines (L)
    blocks: list = field(default_factory=list)       # list of lists of L (quoted inserted text)
    children: list = field(default_factory=list)
    parent: "Node | None" = None
    skipped: list = field(default_factory=list)      # margin lines skipped before a block (item root only)

    def own_text(self) -> str:
        return fold_ws(" ".join(x.text for x in self.lines))

    def block_text(self) -> str:
        return fold_ws(" ".join(x.text for b in self.blocks for x in b))

    def path(self) -> list:
        out, n = [], self
        while n is not None and n.kind != "item":
            out.append(n.marker)
            n = n.parent
        return out[::-1]

    def chain(self) -> list:
        out, n = [], self.parent
        while n is not None:
            out.append(n)
            n = n.parent
        return out                                     # nearest ancestor first


def split_items(lines: list) -> list:
    """[(number, [L...])] numbered items in strict sequence 1, 2, 3, ... (other numbered lines stay inside items)."""
    items, cur = [], None
    for ln in lines:
        m = ITEM_RE.match(ln.text)
        if m and int(m.group(1)) == (items[-1][0] + 1 if items else 1):
            cur = (int(m.group(1)), [])
            items.append(cur)
        if cur is not None:
            cur[1].append(ln)
    return items


def _marker_kind(tok: str, last_of: dict) -> str:
    """alpha (a) | roman (i) | ALPHA (A) | ROMAN (I). (i)/(v)/(x)/(l) are alpha only right after (h)/(u)/(w)/(k)."""
    lower = tok.islower()
    romans = set("ivxlc" if lower else "IVXLC")
    if len(tok) > 1:
        return ("roman" if lower else "ROMAN") if set(tok) <= romans else ("alpha" if lower else "ALPHA")
    prev = {"i": "h", "v": "u", "x": "w", "l": "k"} if lower else {"I": "H", "V": "U", "X": "W", "L": "K"}
    akind = "alpha" if lower else "ALPHA"
    if tok in prev:
        return akind if last_of.get(akind) == prev[tok] else ("roman" if lower else "ROMAN")
    return akind


LEVEL = {"alpha": 1, "roman": 2, "ALPHA": 3, "ROMAN": 4}


def _block_end(text: str, opener: str) -> bool:
    s = text.rstrip()
    return bool(re.search("[" + re.escape(CLOSE_FOR[opener]) + r"]\s*[;.]\s*(?:and|or)?\s*$", s))


def _roman(tok: str) -> int:
    vals = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
    t, total = tok.lower(), 0
    for k, ch in enumerate(t):
        v = vals[ch]
        total += -v if k + 1 < len(t) and vals[t[k + 1]] > v else v
    return total


def _successor(kind: str, tok: str) -> str:
    """Next marker of the same kind: (a)->(b), (z)->(aa), (i)->(ii), (A)->(B), (I)->(II)."""
    if kind in ("roman", "ROMAN"):
        n, out = _roman(tok) + 1, ""
        for v, r in ((100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"),
                     (1, "i")):
            while n >= v:
                out, n = out + r, n - v
        return out if kind == "roman" else out.upper()
    if len(tok) == 1:
        nxt = "aa" if tok.lower() == "z" else chr(ord(tok.lower()) + 1)
    else:
        nxt = tok[:-1] + chr(ord(tok[-1].lower()) + 1)
    return nxt if kind == "alpha" else nxt.upper()


FIRST = {"alpha": "a", "roman": "i", "ALPHA": "A", "ROMAN": "I"}


def _valid_marker(tok: str, stack: list) -> str | None:
    """The marker's kind if it continues an open level (successor of that level's last marker) or opens a deeper
    level (first marker of a kind deeper than the innermost open level); else None (not a sub-item marker)."""
    for nd in reversed(stack):
        for kind in {_marker_kind(tok, {nd.kind: nd.marker})}:
            if kind == nd.kind and _successor(kind, nd.marker) == tok:
                return kind
    depth = LEVEL[stack[-1].kind] if stack else 0
    for kind, first in FIRST.items():
        if tok == first and LEVEL[kind] > depth:
            return kind
    return None


def build_tree(number: int, lines: list) -> Node:
    """Item tree: own lines per node; quoted blocks attached to the node whose line opened them. A line that starts
    with an out-of-sequence marker right after a block end continues that block (irregular closing quote)."""
    root = Node(str(number), "item")
    stack, cur = [], root
    i, prev_own, after_block = 0, None, None
    while i < len(lines):
        ln = lines[i]
        s = ln.text.strip()
        opener_line = prev_own is not None and BLOCK_OPENER_RE.search(prev_own.text.rstrip())
        if opener_line and s[:1] not in OPEN_QUOTES and _is_margin_cont(s):
            j = i                                       # marginal headings between 'namely:--' and the quote
            while j < len(lines) and j - i < LOOKAHEAD_MAX and _is_margin_cont(lines[j].text):
                j += 1
            if j < len(lines) and lines[j].text.strip()[:1] in OPEN_QUOTES:
                root.skipped += lines[i:j]
                i = j
                continue
        opened = opener_line and s[:1] in OPEN_QUOTES
        m = MARKER_RE.match(s)
        kind = _valid_marker(m.group(1), stack) if m else None
        resume = after_block is not None and m is not None and kind is None
        if opened or resume:
            block = after_block[1] if resume else []
            opener = after_block[0] if resume else s[0]
            while i < len(lines):
                block.append(lines[i])
                if _block_end(lines[i].text, opener) and (len(block) > 1 or len(lines[i].text.strip()) > 2):
                    i += 1
                    break
                i += 1
            if not resume:
                cur.blocks.append(block)
            prev_own, after_block = block[-1], (opener, block)
            continue
        after_block = None
        if m and kind and prev_own is not None and TERMINATED_RE.search(prev_own.text.rstrip()):
            while stack and LEVEL[stack[-1].kind] >= LEVEL[kind]:
                stack.pop()
            parent = stack[-1] if stack else root
            node = Node(m.group(1), kind, parent=parent)
            parent.children.append(node)
            stack.append(node)
            cur = node
        cur.lines.append(ln)
        prev_own = ln
        i += 1
    return root


def leaves(node: Node) -> list:
    if not node.children:
        return [node]
    return [x for c in node.children for x in leaves(c)]


# ---------------------------------------------------------------- s.1(2)

def parse_s1(text: str) -> dict:
    """s.1(2) ranges. {'clauses': [{'sections': set, 'partial': set, 'wording': 'come_into_force' |
    'deemed_come_into_force', 'date': iso | None, 'notification': bool}], 'whole': {...} | None}."""
    t = fold_ws(text)
    out = {"clauses": [], "whole": None}
    for m in S1_CLAUSE_RE.finditer(t):
        subj, deemed, tail = m.group(1), m.group(2), m.group(3)
        partial = set(re.findall(r"clause\s*\(\s*\w+\s*\)\s+of\s+section\s+(\d+)", subj))
        rest = re.sub(r"clause\s*\(\s*\w+\s*\)\s+of\s+section\s+\d+", " ", subj)
        secs = set()
        for a, b in re.findall(r"(\d+)\s+to\s+(\d+)", rest):
            secs.update(str(n) for n in range(int(a), int(b) + 1))
        rest = re.sub(r"\d+\s+to\s+\d+", " ", rest)
        secs.update(re.findall(r"\b(\d+)\b", rest))
        notif = bool(re.match(r"such\s+date", tail))
        out["clauses"].append({"sections": secs, "partial": partial,
                               "wording": "deemed_come_into_force" if deemed else "come_into_force",
                               "date": None if notif else iso_date(tail), "notification": notif})
    w = S1_WHOLE_RE.search(t)
    if w:
        out["whole"] = {"wording": "deemed_come_into_force" if w.group(1) else "come_into_force",
                        "date": iso_date(w.group(2))}
    return out


def s1_for(s1: dict, item: int):
    """(clause, partial?) covering item number, else the whole-Act rule, else None."""
    for c in s1["clauses"]:
        if str(item) in c["sections"]:
            return c, False
        if str(item) in c["partial"]:
            return c, True
    if s1["whole"]:
        return {"sections": set(), "partial": set(), "wording": s1["whole"]["wording"],
                "date": s1["whole"]["date"], "notification": False}, False
    return None, False


# ---------------------------------------------------------------- target Act

class Bindings:
    def __init__(self):
        self.act_wide, self.part = {}, {}

    def part_heading(self):
        self.part = {}

    def scan(self, text: str) -> list:
        found = []
        text = SPLIT_WORD_RE.sub(lambda m: re.sub(r"\s+", "", m.group(0)), text)    # pypdf 'hereinaf ter'
        for m in BIND_RE.finditer(text):
            scope, alias = m.group(1).lower(), norm_act_phrase(m.group(2))
            b = ACT_BEFORE_RE.search(norm_act_phrase(text[:m.start()]))
            cls = act_class(b.group(1), b.group(2)) if b else "other:unresolved"
            (self.part if scope.startswith("hereafter") else self.act_wide)[alias] = cls
            found.append((scope, alias, cls))
        return found

    def resolve(self, phrase: str) -> str:
        p = norm_act_phrase(phrase)
        p = re.sub(r"^(?:the|The)\s+", "", p)
        m = re.match(r"^Income-tax Act,\s*(\d{4})", p)
        if m:
            return act_class("Income-tax Act", m.group(1))
        a = ACT_PHRASE_RE.match(p)
        name = a.group(1) if a else p
        y = re.search(r",\s*(\d{4})$", name)
        if y:                                          # a dated Act name that is not the Income-tax Act
            return act_class(name[:y.start()], y.group(1))
        return self.part.get(name) or self.act_wide.get(name) or f"other:unresolved {name}"


def head_target(head: str, binds: Bindings) -> dict:
    """{'verb': In/After/For/..., 'kind': section/Chapter, 'number', 'number2', 'act'} or {} when the head names no
    section/Chapter."""
    h = norm_act_phrase(head)
    m = HEAD_TARGET_RE.match(h)
    if m:
        verb, kind, num, num2, rest = m.groups()
        kind = "Chapter" if kind == "Chapter" else "section"
        if verb in ("Section", "Sections"):
            kind = "section"
        return {"verb": verb, "kind": kind, "number": num, "number2": num2, "act": binds.resolve(rest)}
    m = re.match(r"^\s*\d{1,3}\s*\.\s*(?:\(\s*1\s*\)\s*)?In\s+the\s+(.{3,90})", h)
    if m:
        return {"verb": "In", "kind": "act", "number": None, "number2": None, "act": binds.resolve(m.group(1))}
    return {}


# ---------------------------------------------------------------- per-instrument parse

def instrument_meta(key: str) -> dict:
    data = json.loads(ss.SOURCES_PATH.read_text(encoding="utf-8"))
    for it in data["items"] + data.get("manual", []):
        if it.get("key") == key:
            return it
    raise KeyError(key)


def act_key_of(meta: dict) -> str:
    kind = "Ordinance" if meta.get("source_kind") == "itd_reproduction" and "Ordinance" in meta.get("item", "") \
        else "Act"
    return f"{kind} No. {meta['act_no']} of {meta['act_year']}"


def corrigendum_rows(key: str) -> list:
    ck = CORRIGENDA.get(key)
    if not ck:
        return []
    folder, fname = ss.INSTRUMENTS[ck][:2]
    return [c for c in ss.corrigendum_items(ss.pdf_pages(se.RAW_DIR / folder / fname)) if c["parsed"]]


def _corr_flag(corr: list, span: list) -> list:
    """Corrigendum items naming a printed page inside the span whose 'for' words occur in the span's text on that
    page (Q5 a)."""
    hits = []
    for c in corr:
        on = [x for x in span if str(x.printed or x.page) == str(c["gazette_page"])]
        if not on:
            continue
        hay = se.fold_for_diff(" ".join(x.text for x in on))
        needle = se.fold_for_diff(c["for"]).strip("\"' ")
        if needle and needle in hay:
            hits.append(c)
    return hits


def parse_instrument(key: str, pages: list | None = None, meta: dict | None = None, corr: list | None = None) -> dict:
    """Ledger rows (spine only) + review data for one instrument. pages/meta/corr may be passed (tests)."""
    if meta is None:
        meta = instrument_meta(key)
    if pages is None:
        folder, fname = ss.INSTRUMENTS[key][:2]
        pages = ss.pdf_pages(se.RAW_DIR / folder / fname)
    if corr is None:
        corr = corrigendum_rows(key)
    cl = clean_instrument(pages)
    items = split_items(cl.lines)
    s1 = {"clauses": [], "whole": None}
    if items and items[0][0] == 1:
        s1 = parse_s1(" ".join(x.text for x in items[0][1]))
    assent = meta.get("assent_date") or meta.get("promulgated_on") or meta.get("gazette_date")
    akey = act_key_of(meta)
    binds = Bindings()
    rows, review, bind_log, item_log = [], [], [], []
    for n, lines in items:
        head_lines = lines[:3]
        head = " ".join(x.text for x in head_lines)
        cut = re.search(r"[,;]\s*[—–-]{1,2}|namely", head)
        head_part = head[:cut.start()] if cut else head
        bind_log += [(key, n, *b) for b in binds.scan(head_part)]
        tgt = head_target(head, binds)
        item_log.append((n, tgt.get("act"), tgt.get("kind"), tgt.get("number")))
        root = build_tree(n, lines)
        rows_n = _rows_for_item(key, akey, n, root, tgt, s1, assent, corr)
        residue = [(x.page, x.line, x.text.strip()) for x in lines if MARGIN_START_RE.match(x.text.strip())]
        for _, rv in rows_n:
            if residue:
                rv["flags"].append("margin_residue")
            rv["skipped_margin"] = [(x.page, x.line, x.text.strip()) for x in root.skipped]
        rows += [r for r, _ in rows_n]
        review += [rv for _, rv in rows_n]
        rest = " ".join(x.text for x in lines)[len(head_part):]
        bind_log += [(key, n, *b) for b in binds.scan(rest)]
        for x in lines:                                 # a Part heading inside the item text closes Part bindings
            if PART_HEAD_RE.match(x.text):
                binds.part_heading()
    return {"key": key, "act_key": akey, "assent": assent, "rows": rows, "review": review, "s1": s1,
            "items": len(items), "last_item": items[-1][0] if items else None, "layout": cl.log,
            "bindings": bind_log, "item_log": item_log, "corr": corr}


def _units(nodes: list) -> str:
    out = []
    for nd in nodes:
        for m in UNIT_RE.finditer(re.sub(r"\s*-\s*", "-", nd.own_text()).split("shall be")[0]):
            u = fold_ws(m.group(1)) + (" " + re.sub(r"\s+", "", m.group(2)) if m.group(2) else "")
            if not out or out[-1] != u:
                out.append(u)
    return " > ".join(out)[:120]


def _inner_targets(root: Node, act: str) -> list:
    """Spine section numbers whose heading starts a line inside the item's inserted blocks."""
    found = []
    for nd in [root] + [x for c in root.children for x in _walk(c)]:
        for b in nd.blocks:
            for x in b:
                m = INNER_HEADING_RE.match(x.text)
                if m and m.group(1) in SPINE.get(act, []) and m.group(1) not in found:
                    found.append(m.group(1))
    return found


def _walk(n: Node) -> list:
    return [n] + [x for c in n.children for x in _walk(c)]


def _rows_for_item(key, akey, n, root, tgt, s1, assent, corr) -> list:
    act = tgt.get("act")
    if act not in ("1961", "2025") or tgt.get("kind") not in ("section", "Chapter"):
        return []
    targets = []
    if tgt["verb"] == "After" or tgt["kind"] == "Chapter":
        targets = _inner_targets(root, act)             # H3 / H5: headings inside the inserted text
    else:
        targets = [s for s in (tgt["number"], tgt.get("number2")) if s and s in SPINE[act]]
    if not targets:
        return []
    out = []
    for leaf in leaves(root):
        chain = leaf.chain()
        own = leaf.own_text()
        verbs = {VERB_MAP[v] for v in VERB_RE.findall(own)}
        flags = []
        if len(verbs) == 1:
            op = verbs.pop()
        else:
            op = "other"
            flags.append("no_verb" if not verbs else "multi_verb")
        dates = sorted({iso_date(m.group(1)) for m in WEF_RE.finditer(own)})
        src, wef, header_at = "unknown", None, None
        if len(dates) == 1:
            src, wef = "item_deemed", dates[0]
        elif len(dates) > 1:
            flags.append("multi_date")
        else:
            for anc in chain:
                ad = sorted({iso_date(m.group(1)) for m in WEF_RE.finditer(anc.own_text())})
                if len(ad) == 1:
                    src, wef = "header_inherited", ad[0]
                    header_at = (anc.lines[0].page, anc.lines[0].line) if anc.lines else None
                    break
                if len(ad) > 1:
                    flags.append("multi_date_header")
                    break
            if src == "unknown" and "multi_date_header" not in flags:
                if DEEMED_VERB_RE.search(own) or any(DEEMED_VERB_RE.search(a.own_text()) for a in chain):
                    flags.append("deemed_without_date")
                else:
                    c, partial = s1_for(s1, n)
                    if c is None:
                        flags.append("no_s1_range")
                    elif c["notification"]:
                        src = "notification"
                        flags += ["applicability_unclear", "MANUAL_NEEDED"]
                    else:
                        src, wef = "s1_default", c["date"]
                        if partial:
                            flags.append("s1_partial_range")
                        flags.append("s1:" + c["wording"])
        deemed_from = wef if (wef and assent and wef < assent) else ""
        applic = bool(APPLIC_RE.search(own + " " + leaf.block_text()))
        span = leaf.lines + [x for b in leaf.blocks for x in b]
        corr_hits = _corr_flag(corr, span)
        head_nodes = [a for a in reversed(chain)]
        quote_lines = leaf.lines[:QUOTE_LINE_CAP]
        if len(leaf.lines) > QUOTE_LINE_CAP:
            flags.append("quote_truncated")
        prefix = ""
        if src == "header_inherited":
            prefix = " ".join(a.own_text() for a in head_nodes if a.lines) + " "
        quote = fold_ws(prefix + " ".join(x.text for x in quote_lines))
        for sec in targets:
            path = "".join(f"({p})" for p in leaf.path())
            eid = f"{key}:s{n}{path}" + (f"/{sec}" if len(targets) > 1 else "")
            row = {"effect_id": eid, "act_key": akey, "instrument_provision": f"s.{n}{path}",
                   "target_act": act, "target_section": sec, "target_unit": _units(head_nodes + [leaf]),
                   "operation": op, "commencement_source": src, "wef": wef or "", "deemed_from": deemed_from,
                   "assent_date": assent or "", "applicability_note_present": "yes" if applic else "no",
                   "corrigendum_flag": "yes" if corr_hits else "no",
                   "pdf_page": str(leaf.lines[0].page if leaf.lines else (span[0].page if span else "")),
                   "quote_sha256": quote_sha256(quote), "owner_ok": "", "owner_note": ""}
            rv = {"effect_id": eid, "quote": quote, "flags": flags, "header_at": header_at,
                  "lines": [(x.page, x.line) for x in leaf.lines], "printed_page": leaf.lines[0].printed
                  if leaf.lines else None, "corrigenda": corr_hits,
                  "inserted_block_lines": sum(len(b) for b in leaf.blocks),
                  "block_text": leaf.block_text()}                          # local only (law text)
            out.append((row, rv))
    return out


# ---------------------------------------------------------------- outputs (never overwrite)

def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def csv_text(rows: list, columns: list) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in columns})
    return buf.getvalue()


def read_csv(path: Path) -> list:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def merge_preview(old: list, new: list, key: str, columns: list, owner: tuple = OWNER_COLUMNS,
                  carry=None) -> tuple:
    """(merged rows with the owner columns carried from old by key, preview lines). carry(row, column) -> bool decides
    whether an old owner value is a real owner value (default: any non-empty value); values not carried are named."""
    o = {r[key]: r for r in old}
    merged, lines = [], []
    added = changed = same = 0
    for r in new:
        prev = o.get(r[key])
        r = dict(r)
        if prev is None:
            added += 1
            lines.append(f"  + {r[key]}")
        else:
            for c in owner:
                v = prev.get(c, "")
                if v and carry is not None and not carry(prev, c):
                    lines.append(f"  ! {r[key]}: {c} {v!r} is not an owner value; not carried")
                    v = ""
                r[c] = v
            diff = [c for c in columns if c not in owner and prev.get(c, "") != r.get(c, "")]
            if diff:
                changed += 1
                lines.append(f"  ~ {r[key]}: " + ", ".join(f"{c} {prev.get(c, '')!r}->{r.get(c, '')!r}" for c in diff))
            else:
                same += 1
        merged.append(r)
    gone = [k for k in o if k not in {r[key] for r in new}]
    for k in gone:
        vals = {c: o[k].get(c, "") for c in owner if o[k].get(c, "") and (carry is None or carry(o[k], c))}
        lines.append(f"  - {k}" + (f" OWNER VALUES WOULD BE LOST: {vals}" if vals else " (no owner values)"))
    head = f"MERGE PREVIEW: unchanged {same}, changed {changed}, added {added}, removed {len(gone)}"
    return merged, [head] + lines


def write_never_overwrite(path: Path, rows: list, columns: list, key: str, owner: tuple = OWNER_COLUMNS,
                          carry=None, regen_dir: Path | None = None) -> tuple:
    """Write the canonical file if absent. Otherwise never touch it: write regen/<name>.<stamp>.csv (git-ignored) with
    the owner columns carried, and return the merge preview. Merging into the canonical file is a separate step
    (statute_tables --merge) after the owner's yes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "x", encoding="utf-8", newline="") as f:
            f.write(csv_text(rows, columns))
        return path, [f"wrote new file {path.name} ({len(rows)} rows)"]
    owner = tuple(c for c in owner if c in columns)
    merged, preview = merge_preview(read_csv(path), rows, key, columns, owner, carry)
    regen = regen_dir or REGEN_DIR
    regen.mkdir(parents=True, exist_ok=True)
    alt = regen / f"{path.stem}.{stamp()}{path.suffix}"
    with open(alt, "x", encoding="utf-8", newline="") as f:
        f.write(csv_text(merged, columns))
    return alt, [f"{path.name} exists: not overwritten; wrote {alt}"] + preview


def _md(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def review_md(results: list) -> str:
    md = [f"# EFFECTS REVIEW ({ACT_PARSE_VERSION}; local only: quotes are law text)", ""]
    for r in results:
        md += [f"## {r['key']} ({r['act_key']}, assent {r['assent']}): items {r['items']}, last item {r['last_item']}, "
               f"spine rows {len(r['rows'])}", ""]
        md.append("### s.1(2)")
        for c in r["s1"]["clauses"]:
            secs = sorted(c["sections"], key=int)
            rng = f"{secs[0]}..{secs[-1]} ({len(secs)} sections)" if secs else "-"
            md.append(f"- {c['wording']}: {rng}; partial {sorted(c['partial']) or '-'}; date {c['date']}; "
                      f"notification {c['notification']}")
        if r["s1"]["whole"]:
            md.append(f"- whole instrument: {r['s1']['whole']}")
        md += ["", "### Layout removed (count; first 3)"]
        for k, v in r["layout"].items():
            md.append(f"- {k}: {len(v)}" + "".join(f"\n  - {_md(x)}" for x in v[:3]))
        md += ["", "### Bindings (scope, alias, class)"]
        md += [f"- item {b[1]}: {b[2]} | {b[3]} | {b[4]}" for b in r["bindings"]]
        md += ["", "### Rows", "", "| effect_id | target | unit | op | source | wef | deemed_from | applic | corr | "
               "pdf_page | printed | flags | quote |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for row, rv in zip(r["rows"], r["review"]):
            src = row["commencement_source"]
            if rv["header_at"]:
                src += f" (header p{rv['header_at'][0]} l{rv['header_at'][1]})"
            md.append(f"| {row['effect_id']} | {row['target_act']} s.{row['target_section']} | "
                      f"{_md(row['target_unit'])} | {row['operation']} | {src} | {row['wef']} | {row['deemed_from']} | "
                      f"{row['applicability_note_present']} | {row['corrigendum_flag']} | {row['pdf_page']} | "
                      f"{rv['printed_page']} | {' '.join(rv['flags']) or '-'} | {_md(rv['quote'])} |")
        skipped = sorted({x for rv in r["review"] for x in rv.get("skipped_margin", [])})
        if skipped:
            md += ["", "### Margin lines skipped between 'namely' and a quoted block (spine items)"]
            md += [f"- p{x[0]} l{x[1]}: {_md(x[2])}" for x in skipped]
        corr_hits = [(rv["effect_id"], c) for rv in r["review"] for c in rv["corrigenda"]]
        if corr_hits:
            md += ["", "### Corrigendum matches (page + 'for' words in the effect's text)"]
            md += [f"- {e}: page {c['gazette_page']} line(s) {c['gazette_lines']} for {_md(c['for'])} read "
                   f"{_md(c['read'])}" for e, c in corr_hits]
        md.append("")
    return "\n".join(md) + "\n"


def apply_owner_splits(result: dict, splits: dict | None = None) -> None:
    """Replace a row named in OWNER_SPLITS by one row per operation (effect_id + '/' + operation), with the owner's
    w.e.f. (commencement_source item_deemed: the date printed in the item) and owner_note. In place."""
    splits = OWNER_SPLITS if splits is None else splits
    rows, review = [], []
    for row, rv in zip(result["rows"], result["review"]):
        sp = splits.get(row["effect_id"])
        if not sp:
            rows.append(row)
            review.append(rv)
            continue
        for op in sp["operations"]:
            eid = f"{row['effect_id']}/{op}"
            wef = sp["wef"]
            rows.append(dict(row, effect_id=eid, operation=op, commencement_source="item_deemed", wef=wef,
                             deemed_from=wef if row["assent_date"] and wef < row["assent_date"] else "",
                             owner_note=sp["owner_note"]))
            review.append(dict(rv, effect_id=eid, flags=[f for f in rv["flags"] if f != "multi_verb"]
                               + [f"owner_split {sp['date']}"]))
    result["rows"], result["review"] = rows, review


def run_ledger(keys: list = INSTRUMENT_KEYS) -> tuple:
    results = [parse_instrument(k) for k in keys]
    for r in results:
        apply_owner_splits(r)
    rows = [row for r in results for row in r["rows"]]
    ids = [r["effect_id"] for r in rows]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(f"duplicate effect_id: {dup}")
    return results, rows


def counts_table(results: list) -> str:
    out = [f"{'instrument':<14} {'items':>5} {'last':>5} {'rows':>5} {'masthead':>8} {'margin':>6} {'runhead':>7} "
           f"{'pg_mismatch':>11} {'corr_items':>10}"]
    for r in results:
        lg = r["layout"]
        out.append(f"{r['key']:<14} {r['items']:>5} {str(r['last_item']):>5} {len(r['rows']):>5} "
                   f"{len(lg['masthead']):>8} {len(lg['margin']):>6} {len(lg['running_head']):>7} "
                   f"{len(lg['page_mismatch']):>11} {len(r['corr']):>10}")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=ACT_PARSE_VERSION)
    ap.add_argument("--ledger", action="store_true", help="parse all instruments; write the ledger (never overwrite)")
    ap.add_argument("--dry-run", action="store_true", help="print counts and rows only; write nothing")
    a = ap.parse_args(argv)
    if not (a.ledger or a.dry_run):
        ap.print_help()
        return 2
    results, rows = run_ledger()
    print(ACT_PARSE_VERSION)
    print(counts_table(results))
    print(f"spine rows: {len(rows)}")
    for r in rows:
        print("  " + " | ".join(r[c] for c in EFFECT_COLUMNS[:14]))
    if a.dry_run:
        return 0
    path, msg = write_never_overwrite(EFFECTS_PATH, rows, EFFECT_COLUMNS, "effect_id")
    print("\n".join(msg))
    quotes = [{"effect_id": rv["effect_id"], "quote": rv["quote"]} for r in results for rv in r["review"]]
    qpath, qmsg = write_never_overwrite(QUOTES_PATH, quotes, ["effect_id", "quote"], "effect_id")
    print("\n".join(qmsg))
    PARTC_DIR.mkdir(parents=True, exist_ok=True)
    rp = PARTC_DIR / f"EFFECTS-REVIEW-{stamp()}.md"
    se._write_new(rp, review_md(results))
    print(f"review: {rp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
