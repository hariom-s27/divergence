#!/usr/bin/env python3
"""
QA_SCORER -- nugget-level scorer for the tax QA benchmark (DR-3 Q4-Q5).
Deterministic, standard library only. Separate from score.py, which scores
the six hackathon cases; this one scores the new question benchmark.

    python divergence/eval/qa_scorer.py --gold G.jsonl --responses R.jsonl --out O.json

GOLD:      one JSON object per line, shape in gold_schema_draft.json (DRAFT).
RESPONSES: one JSON object per line, {"qid": "...", "response": "<raw model output>"}.

Only the final structured line of a response is scored: the LAST line that
starts with ANSWER: or ABSTAIN:. Every rule, and every decision the spec left
open (D1-D22), is written out with an example in QA_SCORER.md. The D<n> tags
in comments below point there.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import date
from decimal import Decimal, localcontext
from fractions import Fraction

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SPLITS = {"dev", "test"}
ACTS = {"1961", "2025"}
GOVERNING_ACTS = ACTS | {"both", "none"}
STRATA = {"lookup", "proviso", "cross_reference", "cross_year", "computation"}
ABSTAIN_REASONS = {"no_applicable_version", "out_of_scope", "indeterminate", "answerable"}
# The match kind is fixed by the nugget type; the gold file states it anyway
# so a reader of one item sees how it is scored, and load-time validation
# rejects any disagreement.
MATCH_FOR_TYPE = {"rate": "exact", "threshold": "exact", "limit": "exact",
                  "date": "exact", "tax_year": "exact",
                  "section": "section_tuple", "amount": "tolerance"}
SECTION_DEPTHS = {"section": 1, "subsection": 2, "clause": 3}
CELLS = ("N1", "N2", "N3", "N4", "N5")
VARIANTS = ("primary", "sensitivity", "lenient_act")
GOLD_FIELDS = ("qid", "split", "question", "applicable_tax_year", "governing_act",
               "stratum", "nesting_depth", "names_section", "cluster",
               "should_abstain", "abstain_reason", "spans", "nuggets")
# Keys a fixture line may carry besides the gold fields (D19).
FIXTURE_ONLY_FIELDS = {"synthetic", "response"}
NUGGET_FIELDS = {"nid", "type", "gold", "match", "section_depth", "act"}


# ── normalisation ─────────────────────────────────────────────────────
_MD_RE = re.compile(r"\*\*|__|\*|`")          # D13: bold/italic markers, code ticks; a single _ stays
_CURRENCY_RE = re.compile("₹" + r"|\brs\b\.?|\binr\b|\brupees?\b")
_MULT = {"lakh": 10 ** 5, "lakhs": 10 ** 5, "crore": 10 ** 7, "crores": 10 ** 7}
# Integer part in any comma grouping (Indian 1,50,000 or Western 150,000),
# optional decimals, optional lakh/crore word.
_NUMBER_RE = re.compile(
    r"(?<![\w.])(\d{1,3}(?:,\d{2,3})+|\d+)(?:\.(\d+))?(?:\s*(lakhs?|crores?)\b)?(?!\w)")
# D3: "pc" is a percent marker only directly after a number.
_PERCENT_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(?:%|per\s*cent\b|percent\b|pc\b)")
_ACT_RE = re.compile(
    r"income[\s-]*tax\s+act,?\s*(1961|2025)"
    r"|\b(1961|2025)\s+act\b"
    r"|\bact,?\s+(?:of\s+)?(1961|2025)\b")
_SECTION_NUM = r"(\d+[a-z]*)((?:\(\d+[a-z]?\))*)((?:\([a-z]+\))*)"
# The DR-3 regex, applied case-insensitively (text is lower-cased first), with
# the prefixes widened per the owner's D9 answer: section, under section,
# u/s, sec, sec., s, s.
_SECTION_RE = re.compile(
    r"(?:\bu/s|\bunder\s+sections?|\bsections?|\bsec\b\.?|\bs\b\.?)\s*" + _SECTION_NUM)
# D9: a bare token ("393(1)", "80C") counts only inside a section nugget's
# value. At most 3 digits, so years and amounts are never read as sections.
_BARE_SECTION_RE = re.compile(
    r"(?<![\w/(])(?<!\d[.,])(\d{1,3}[a-z]{0,4})((?:\(\d+[a-z]?\))*)((?:\([a-z]+\))*)"
    r"(?!\w|[.,]\d|%|/)")
_MONTHS = {"january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
           "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
           "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9,
           "october": 10, "oct": 10, "november": 11, "nov": 11,
           "december": 12, "dec": 12}
_MON = "(" + "|".join(sorted(_MONTHS, key=len, reverse=True)) + r")\.?"
_DATE_PATTERNS = (
    (re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"), "ymd"),
    (re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b"), "dmy"),   # D4: always day-first
    (re.compile(r"\b(\d{1,2})\s+" + _MON + r"\s+(\d{4})\b"), "d_mon_y"),
    (re.compile(r"\b" + _MON + r"\s+(\d{1,2})\s+(\d{4})\b"), "mon_d_y"),
)
_DASH = "[-–/]"
_AY_RE = re.compile(r"\b(?:ay|a\.y\.|assessment\s+year)\s*(\d{4})\s*" + _DASH + r"\s*(\d{2}|\d{4})\b")
_TY_RE = re.compile(r"(?<![\d-])(\d{4})\s*" + _DASH + r"\s*(\d{2}|\d{4})(?![\d-])")
_PROSE_REFUSAL_RE = re.compile(
    r"\b(?:cannot answer|can't answer|can not answer|unable to (?:answer|determine)"
    r"|cannot be determined|insufficient information|not enough information"
    r"|i don't know|i do not know|no applicable (?:version|provision))\b")
_FINAL_RE = re.compile(r"^(answer|abstain)\s*:(.*)$", re.IGNORECASE)
_KEYED_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*=\s*(.*?)\s*$")


def _strip_md(s):
    return _MD_RE.sub("", s)


def _distinct(values):
    out = []
    for v in values:
        if v not in out:
            out.append(v)
    return out


def normalise_text(s):
    """NFKC, lower-case, markdown bold/italic stripped, whitespace collapsed.
    A curly apostrophe becomes a straight one so "can’t" reads as "can't"."""
    t = unicodedata.normalize("NFKC", str(s)).lower().replace("’", "'")
    t = _strip_md(t)
    return re.sub(r"\s+", " ", t).strip()


def _numbers(t):
    """Every number in already-normalised text, as Decimal, in order.
    Currency markers, section references and Act years are removed first so
    "section 80C limit Rs 1,50,000 under the 1961 Act" yields only 150000."""
    t = _CURRENCY_RE.sub(" ", t)
    t = _SECTION_RE.sub(" ", t)
    t = _ACT_RE.sub(" ", t)
    out = []
    with localcontext() as ctx:
        ctx.prec = 50
        for m in _NUMBER_RE.finditer(t):
            digits = m.group(1).replace(",", "") + ("." + m.group(2) if m.group(2) else "")
            out.append(Decimal(digits) * _MULT.get(m.group(3) or "", 1))
    return out


def parse_number(s):
    """The single number in s (Decimal), or None if there is none or more
    than one distinct value. "Rs. 1.5 lakh" -> Decimal('150000.0')."""
    vals = _distinct(_numbers(normalise_text(s)))
    return vals[0] if len(vals) == 1 else None


def parse_rate(s):
    """A rate as the printed percentage number: "30 per cent" -> 30.
    Percent-marked numbers win; with no marker every number is a candidate,
    flagged rate_unmarked by the caller (D7). A bare value below 1 is
    flagged bare_fraction and is never multiplied by 100."""
    t = normalise_text(s)
    marked = _distinct(Decimal(m.group(1)) for m in _PERCENT_RE.finditer(t))
    if marked:
        values, bare = marked, False
    else:
        values = _distinct(_numbers(t))
        bare = any(Decimal(0) < v < 1 for v in values)
    return {"values": values, "value": values[0] if len(values) == 1 else None,
            "percent_marked": bool(marked), "bare_fraction": bare}


def _dates(s):
    t = normalise_text(s)
    t = re.sub(r"(\d)(?:st|nd|rd|th)\b", r"\1", t).replace(",", " ")
    t = re.sub(r"\s+", " ", t)
    found, invalid = [], 0
    for rx, kind in _DATE_PATTERNS:
        for m in rx.finditer(t):
            g = m.groups()
            if kind == "ymd":
                y, mo, d = int(g[0]), int(g[1]), int(g[2])
            elif kind == "dmy":
                d, mo, y = int(g[0]), int(g[1]), int(g[2])
            elif kind == "d_mon_y":
                d, mo, y = int(g[0]), _MONTHS[g[1]], int(g[2])
            else:
                mo, d, y = _MONTHS[g[0]], int(g[1]), int(g[2])
            try:
                found.append(date(y, mo, d).isoformat())
            except ValueError:
                invalid += 1
    return _distinct(found), invalid


def parse_date(s):
    """ISO YYYY-MM-DD, or None if unparseable, impossible (31/02) or more
    than one distinct date. "1st April, 2026" -> "2026-04-01"."""
    found, _ = _dates(s)
    return found[0] if len(found) == 1 else None


def parse_tax_year(s):
    """Start year of a tax year. "TY 2026-27", "FY 2026-27", "2026-27" -> 2026.
    "AY 2027-28" is an assessment year, a different concept: it is flagged
    and never converted (D11). The end year must be start+1."""
    t = normalise_text(s)
    ay = bool(_AY_RE.search(t))
    t = _AY_RE.sub(" ", t)
    starts, invalid = [], 0
    for m in _TY_RE.finditer(t):
        start, end = int(m.group(1)), m.group(2)
        ok = int(end) == ((start + 1) % 100 if len(end) == 2 else start + 1)
        if ok:
            starts.append(start)
        else:
            invalid += 1
    starts = _distinct(starts)
    return {"start_years": starts, "start_year": starts[0] if len(starts) == 1 else None,
            "assessment_year": ay, "invalid": invalid}


def parse_act(s):
    """"1961", "2025", "both" (both named = an Act hedge) or None (no tag)."""
    acts = {g for m in _ACT_RE.finditer(normalise_text(s)) for g in m.groups() if g}
    if not acts:
        return None
    return "both" if len(acts) > 1 else acts.pop()


def _section_tuple(act, m):
    return (act, m.group(1).upper(), m.group(2) or None, m.group(3) or None)


def parse_sections(s, allow_bare=False):
    """[(act, section, subsection, clause)] for every section reference.
    "s. 80CCD(1b)(ii) of the 1961 Act" -> [("1961", "80CCD", "(1b)", "(ii)")].
    A bare token is read only when allow_bare is set (section nuggets only,
    D9) and only if no prefixed reference was found."""
    t = normalise_text(s)
    act = parse_act(t)
    found = [_section_tuple(act, m) for m in _SECTION_RE.finditer(t)]
    if found or not allow_bare:
        return found
    t = _ACT_RE.sub(" ", t)
    return [_section_tuple(act, m) for m in _BARE_SECTION_RE.finditer(t)]


def amount_tolerance(gold):
    """Half a unit of the last digit printed in the gold string, times its
    lakh/crore word (D5). Read from the gold as printed, before value
    normalisation: "Rs 1,23,450" -> 0.5, "Rs 1.2 lakh" -> 5000."""
    t = _CURRENCY_RE.sub(" ", _strip_md(unicodedata.normalize("NFKC", str(gold)).lower()))
    ms = list(_NUMBER_RE.finditer(t))
    if len(ms) != 1:
        raise ValueError(f"amount gold must print exactly one number: {gold!r}")
    places = len(ms[0].group(2) or "")
    with localcontext() as ctx:
        ctx.prec = 50
        return Decimal(5).scaleb(-(places + 1)) * _MULT.get(ms[0].group(3) or "", 1)


# ── extraction ────────────────────────────────────────────────────────
def extract_final(response):
    """The LAST line starting with ANSWER: or ABSTAIN: (case-insensitive,
    markdown bold stripped). An ABSTAIN marker or an empty ANSWER line is an
    abstention. A prose refusal without the marker is only flagged (D14)."""
    kind = line = value = None
    for raw in str(response or "").splitlines():
        s = _strip_md(raw).strip()
        m = _FINAL_RE.match(s)
        if m:
            kind, line, value = m.group(1).upper(), s, m.group(2).strip()
    empty_answer = kind == "ANSWER" and value == ""
    abstain_marker = kind == "ABSTAIN" or empty_answer
    prose = (not abstain_marker) and bool(_PROSE_REFUSAL_RE.search(normalise_text(response or "")))
    return {"kind": kind, "line": line, "value": value, "no_final_line": kind is None,
            "abstain_marker": abstain_marker, "empty_answer": empty_answer,
            "prose_refusal": prose}


def split_answer(value, nids):
    """"n1=30%; n2=Rs 2 lakh" -> {"n1": ["30%"], "n2": ["Rs 2 lakh"]}.
    Keys match nids case-insensitively. With no known key and exactly one
    nugget, the whole value applies to it; with no known key and several
    nuggets, unkeyed_multi is set and the caller scores every nugget wrong
    (D12). A nid given twice keeps both values, which the matcher then sees
    as a hedge if they differ."""
    lookup = {n.lower(): n for n in nids}
    by_nid = {n: [] for n in nids}
    unknown, unkeyed = [], []
    keyed = False
    for seg in (value or "").split(";"):
        if not seg.strip():
            continue
        m = _KEYED_RE.match(seg)
        if m and m.group(1).lower() in lookup:
            keyed = True
            if m.group(2):          # "n1=" with no value leaves n1 withheld
                by_nid[lookup[m.group(1).lower()]].append(m.group(2))
            continue
        if m:
            unknown.append(m.group(1))
        unkeyed.append(seg.strip())
    unkeyed_multi = False
    if not keyed and (value or "").strip():
        if len(nids) == 1:
            by_nid[nids[0]] = [value.strip()]
        else:
            unkeyed_multi = True
    return {"by_nid": by_nid, "unknown_nids": unknown,
            "unkeyed_segments": unkeyed if keyed else [], "unkeyed_multi": unkeyed_multi}


# ── matching ──────────────────────────────────────────────────────────
def _gold_value(nugget):
    """Parse a nugget's gold string by its type; ValueError if it does not
    parse to exactly one value. Gold errors fail loudly at load time (D4)."""
    typ, gold = nugget["type"], nugget["gold"]
    if typ == "rate":
        v = parse_rate(gold)["value"]
    elif typ in ("threshold", "limit", "amount"):
        v = parse_number(gold)
    elif typ == "date":
        v = parse_date(gold)
    elif typ == "tax_year":
        v = parse_tax_year(gold)["start_year"]
    else:
        n = SECTION_DEPTHS[nugget["section_depth"]]
        keys = _distinct(t[1:1 + n] for t in parse_sections(gold, allow_bare=True))
        v = keys[0] if len(keys) == 1 and None not in keys[0] else None
    if v is None:
        raise ValueError(f"nugget {nugget.get('nid')}: gold {gold!r} does not parse as one {typ}")
    return v


def _act_check(want, got):
    """(ok, flag) for a section nugget's Act. No tag is wrong (D2)."""
    if got is None:
        return False, "act_missing"
    if got == "both":
        return False, "act_hedged"
    if got != want:
        return False, "act_mismatch"
    return True, None


def score_nugget(nugget, candidates, governing_act=None):
    """State of one nugget: correct / wrong / withheld, with every
    intermediate value. candidates are the raw strings the response gave
    for this nid (none -> withheld). governing_act feeds only the lenient
    Act score (D2)."""
    typ = nugget["type"]
    out = {"nid": nugget["nid"], "type": typ, "gold": nugget["gold"],
           "response_value": "; ".join(candidates) if candidates else None,
           "gold_parsed": None, "parsed": None, "tolerance": None,
           "state": "withheld", "state_lenient_act": "withheld",
           "version_ok": None, "version_ok_lenient_act": None, "flags": {}}
    if not candidates:
        return out
    flags = out["flags"]
    text = " ; ".join(candidates)
    gold = _gold_value(nugget)
    out["gold_parsed"] = str(gold) if typ != "section" else list(gold)
    correct = False

    if typ == "section":
        n = SECTION_DEPTHS[nugget["section_depth"]]
        found = parse_sections(text, allow_bare=True)
        keys = _distinct(t[1:1 + n] for t in found)
        out["parsed"] = [list(t) for t in found]
        if not keys:
            flags["section_unparsed"] = True
        elif len(keys) > 1:
            flags["hedged"] = True
        elif None in keys[0]:
            flags["too_shallow"] = True
        number_ok = len(keys) == 1 and keys[0] == gold
        want = nugget.get("act")
        if want:
            got = parse_act(text)
            act_ok, flag = _act_check(want, got)
            if flag:
                flags[flag] = True
            inherited = got if got is not None else (governing_act if governing_act in ACTS else None)
            act_ok_l, _ = _act_check(want, inherited)
            out["version_ok"], out["version_ok_lenient_act"] = act_ok, act_ok_l
        else:
            act_ok = act_ok_l = True
        out["state"] = "correct" if number_ok and act_ok else "wrong"
        out["state_lenient_act"] = "correct" if number_ok and act_ok_l else "wrong"
        return out

    if typ == "rate":
        r = parse_rate(text)
        vals = r["values"]
        if vals and not r["percent_marked"]:
            flags["rate_unmarked"] = True
        if r["bare_fraction"]:
            flags["bare_fraction"] = True
    elif typ in ("threshold", "limit", "amount"):
        vals = _distinct(_numbers(normalise_text(text)))
    elif typ == "date":
        vals, invalid = _dates(text)
        if invalid and not vals:
            flags["date_invalid"] = True
    else:
        ty = parse_tax_year(text)
        vals = ty["start_years"]
        if ty["assessment_year"]:
            flags["assessment_year"] = True

    if not vals:
        flags["date_unparsed" if typ == "date" else
              "tax_year_unparsed" if typ == "tax_year" else "value_unparsed"] = True
    elif len(vals) > 1:
        flags["hedged"] = True
        out["parsed"] = [str(v) for v in vals]
    else:
        out["parsed"] = str(vals[0])
        if typ == "amount":
            tol = amount_tolerance(nugget["gold"])
            out["tolerance"] = str(tol)
            correct = abs(vals[0] - gold) <= tol
        else:
            correct = vals[0] == gold
    out["state"] = out["state_lenient_act"] = "correct" if correct else "wrong"
    return out


def _forced_wrong(nugget, reason):
    """A nugget scored wrong without matching: no final line (D1) or an
    unkeyed multi-part answer (D12)."""
    section_act = nugget["type"] == "section" and bool(nugget.get("act"))
    return {"nid": nugget["nid"], "type": nugget["type"], "gold": nugget["gold"],
            "response_value": None, "gold_parsed": None, "parsed": None, "tolerance": None,
            "state": "wrong", "state_lenient_act": "wrong",
            "version_ok": False if section_act else None,
            "version_ok_lenient_act": False if section_act else None,
            "flags": {"forced": reason}}


# ── per question ──────────────────────────────────────────────────────
def _cell(should_abstain, abstained, strict):
    if should_abstain:
        return "N5" if abstained else "N4"
    if abstained:
        return "N3"
    return "N1" if strict else "N2"


def _variant(results, state_key, version_key, should_abstain, abstained):
    k = len(results)
    if abstained:
        correct = wrong = 0
    else:
        correct = sum(1 for r in results if r[state_key] == "correct")
        wrong = sum(1 for r in results if r[state_key] == "wrong")
    strict = int(not abstained and k > 0 and correct == k)
    answered_sec = [] if abstained else [
        r for r in results if r[version_key] is not None and r[state_key] != "withheld"]
    return {"k": k, "correct": correct, "wrong": wrong, "withheld": k - correct - wrong,
            "abstained": abstained, "strict": strict,
            "cell": _cell(should_abstain, abstained, strict),
            "version_answered": len(answered_sec),
            "version_ok": sum(1 for r in answered_sec if r[version_key])}


def score_question(gold, response):
    """One per-question row with every intermediate value."""
    ext = extract_final(response)
    nuggets = gold.get("nuggets") or []
    nids = [n["nid"] for n in nuggets]
    split = {"by_nid": {}, "unknown_nids": [], "unkeyed_segments": [], "unkeyed_multi": False}
    if ext["abstain_marker"]:
        results = [score_nugget(n, []) for n in nuggets]
    elif ext["no_final_line"]:
        results = [_forced_wrong(n, "no_final_line") for n in nuggets]
    else:
        split = split_answer(ext["value"], nids)
        if split["unkeyed_multi"]:
            results = [_forced_wrong(n, "unkeyed_multi") for n in nuggets]
        else:
            results = [score_nugget(n, split["by_nid"].get(n["nid"], []), gold.get("governing_act"))
                       for n in nuggets]

    k = len(results)
    all_withheld = k > 0 and all(r["state"] == "withheld" for r in results)
    abstained = ext["abstain_marker"] or all_withheld
    should = bool(gold["should_abstain"])
    variants = {
        "primary": _variant(results, "state", "version_ok", should, abstained),
        # D14: a prose refusal counts as an abstention in the sensitivity run.
        "sensitivity": _variant(results, "state", "version_ok", should,
                                abstained or ext["prose_refusal"]),
        # D2: a section with no Act tag inherits the question's governing_act.
        "lenient_act": _variant(results, "state_lenient_act", "version_ok_lenient_act",
                                should, abstained),
    }
    return {"qid": gold["qid"], "split": gold["split"], "stratum": gold["stratum"],
            "governing_act": gold.get("governing_act"), "should_abstain": should,
            "final_kind": ext["kind"], "final_line": ext["line"], "final_value": ext["value"],
            "no_final_line": ext["no_final_line"], "abstain_marker": ext["abstain_marker"],
            "empty_answer": ext["empty_answer"], "prose_refusal": ext["prose_refusal"],
            "unkeyed_multi": split["unkeyed_multi"], "unknown_nids": split["unknown_nids"],
            "unkeyed_segments": split["unkeyed_segments"],
            "nuggets": results, "variants": variants,
            "cell": variants["primary"]["cell"],
            "cell_sensitivity": variants["sensitivity"]["cell"],
            "cell_lenient_act": variants["lenient_act"]["cell"]}


# ── aggregates ────────────────────────────────────────────────────────
def confusion(rows, variant="primary"):
    cells = {c: 0 for c in CELLS}
    for r in rows:
        cells[r["variants"][variant]["cell"]] += 1
    cells["N"] = len(rows)
    return cells


def aggregate(rows, variant="primary", costs=(1, 10)):
    """Every metric as an exact Fraction, or None with a reason when its
    denominator is 0 (None, never 0: an undefined metric is not a bad one)."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}")
    vs = [r["variants"][variant] for r in rows]
    cells = confusion(rows, variant)
    n1, n2, n3, n4, n5, n = (cells[c] for c in CELLS + ("N",))
    metrics, why = {}, {}

    def put(name, num, den, label):
        if den == 0:
            metrics[name], why[name] = None, f"denominator {label} = 0"
        else:
            metrics[name] = Fraction(num, den)

    put("accuracy", n1 + n5, n, "N")
    put("abstention_precision", n5, n3 + n5, "N3+N5")
    # Abstention recall = N5/(N4+N5): of the questions that SHOULD be
    # abstained on, the share that were. Pre-registered. Wen et al. print
    # N5/(N2+N4+N5); N2 is a should-answer cell and has no place in a recall
    # over should-abstain questions, so the printed formula is treated as a
    # typo (QA_SCORER.md, "Abstention recall").
    put("abstention_recall", n5, n4 + n5, "N4+N5")
    p, r = metrics["abstention_precision"], metrics["abstention_recall"]
    if p is None or r is None:
        metrics["abstention_f1"], why["abstention_f1"] = None, "precision or recall is None"
    else:
        metrics["abstention_f1"] = Fraction(0) if p + r == 0 else 2 * p * r / (p + r)
    put("coverage", n1 + n2 + n4, n, "N")
    put("abstention_rate", n3 + n5, n, "N")
    put("arsp", n3, n1 + n2 + n3, "N1+N2+N3")
    put("r_acc", n1, n1 + n2 + n4, "N1+N2+N4")
    put("effective_reliability", n1 - n2 - n4, n, "N")

    total = sum(v["k"] for v in vs)
    answered = sum(v["correct"] + v["wrong"] for v in vs)
    put("nugget_coverage", answered, total, "all nuggets")
    put("nugget_precision", sum(v["correct"] for v in vs), answered, "answered nuggets")
    with_k = [v for v in vs if v["k"] > 0]
    for c in costs:
        name = f"nugget_phi_{c}"
        if with_k:
            metrics[name] = sum((Fraction(v["correct"] - c * v["wrong"], v["k"]) for v in with_k),
                                Fraction(0)) / len(with_k)
        else:
            metrics[name], why[name] = None, "no question has a nugget"
        # D15 (Whitehead): +1 answered and strict-correct, -c answered
        # otherwise, 0 abstained -- a correct abstention earns 0, not +1.
        q = sum(1 if v["cell"] == "N1" else -c if v["cell"] in ("N2", "N4") else 0 for v in vs)
        put(f"question_phi_{c}", q, n, "N")
    put("version_accuracy", sum(v["version_ok"] for v in vs),
        sum(v["version_answered"] for v in vs), "answered section nuggets with an Act")
    return {"variant": variant, "cells": cells, "metrics": metrics, "none_reasons": why}


def _jsonable(agg):
    out = {"variant": agg["variant"], "cells": agg["cells"], "metrics": {},
           "none_reasons": agg["none_reasons"]}
    for name, v in agg["metrics"].items():
        # float is for reading only; the fraction is the exact value.
        out["metrics"][name] = None if v is None else {
            "fraction": f"{v.numerator}/{v.denominator}", "float": round(float(v), 6)}
    return out


# ── I/O ───────────────────────────────────────────────────────────────
def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def validate_gold_item(item):
    """Structural check of one gold item against the draft schema, plus the
    cross-field rules a JSON Schema cannot say. ValueError names the field."""
    qid = item.get("qid", "<no qid>") if isinstance(item, dict) else "<not an object>"

    def need(cond, msg):
        if not cond:
            raise ValueError(f"gold {qid}: {msg}")

    need(isinstance(item, dict), "item is not a JSON object")
    for f in GOLD_FIELDS:
        need(f in item, f"missing field {f!r}")
    extra = set(item) - set(GOLD_FIELDS) - FIXTURE_ONLY_FIELDS
    need(not extra, f"unknown fields {sorted(extra)}")
    need(isinstance(item["qid"], str) and item["qid"], "qid must be a non-empty string")
    need(item["split"] in SPLITS, "split must be dev|test")
    need(isinstance(item["question"], str) and item["question"], "question must be a non-empty string")
    need(item["applicable_tax_year"] is None or isinstance(item["applicable_tax_year"], str),
         "applicable_tax_year must be a string or null")
    need(item["governing_act"] in GOVERNING_ACTS, "governing_act must be 1961|2025|both|none")
    need(item["stratum"] in STRATA, f"stratum must be one of {sorted(STRATA)}")
    need(_is_int(item["nesting_depth"]) and item["nesting_depth"] >= 0, "nesting_depth must be an int >= 0")
    need(isinstance(item["names_section"], bool), "names_section must be a bool")
    need(isinstance(item["cluster"], str), "cluster must be a string")
    need(isinstance(item["should_abstain"], bool), "should_abstain must be a bool")
    need(item["abstain_reason"] in ABSTAIN_REASONS, f"abstain_reason must be one of {sorted(ABSTAIN_REASONS)}")
    need(item["should_abstain"] == (item["abstain_reason"] != "answerable"),
         "should_abstain must be true exactly when abstain_reason is not 'answerable'")
    need(isinstance(item["spans"], list), "spans must be a list")
    for sp in item["spans"]:
        need(isinstance(sp, dict) and set(sp) == {"corpus_file_sha", "start", "end"},
             "each span is {corpus_file_sha, start, end}")
        need(isinstance(sp["corpus_file_sha"], str) and re.fullmatch(r"[0-9a-f]{64}", sp["corpus_file_sha"]),
             "corpus_file_sha must be 64 lower-case hex characters")
        need(_is_int(sp["start"]) and _is_int(sp["end"]) and 0 <= sp["start"] <= sp["end"],
             "span start/end must be ints with 0 <= start <= end")
    need(isinstance(item["nuggets"], list), "nuggets must be a list")
    need(item["should_abstain"] or item["nuggets"], "a should-answer question needs at least one nugget")
    seen = set()
    for nug in item["nuggets"]:
        need(isinstance(nug, dict), "each nugget is an object")
        need(not set(nug) - NUGGET_FIELDS, f"nugget has unknown fields {sorted(set(nug) - NUGGET_FIELDS)}")
        for f in ("nid", "type", "gold", "match"):
            need(f in nug, f"nugget missing {f!r}")
        need(isinstance(nug["nid"], str) and nug["nid"] and nug["nid"] not in seen,
             f"nid {nug.get('nid')!r} must be a unique non-empty string")
        seen.add(nug["nid"])
        need(nug["type"] in MATCH_FOR_TYPE, f"nugget type must be one of {sorted(MATCH_FOR_TYPE)}")
        need(isinstance(nug["gold"], str) and nug["gold"], "nugget gold must be a non-empty string")
        need(nug["match"] == MATCH_FOR_TYPE[nug["type"]],
             f"nugget {nug['nid']}: type {nug['type']} is matched by {MATCH_FOR_TYPE[nug['type']]}")
        if nug["type"] == "section":
            need(nug.get("section_depth") in SECTION_DEPTHS, "section nugget needs section_depth")
            need("act" not in nug or nug["act"] in ACTS, "section nugget act must be 1961|2025")
        else:
            need("section_depth" not in nug and "act" not in nug,
                 "section_depth/act are only for section nuggets")
        try:
            _gold_value(nug)
            if nug["type"] == "amount":
                amount_tolerance(nug["gold"])
        except ValueError as e:
            need(False, str(e))


def _read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8-sig") as fh:
        for i, line in enumerate(fh, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(f"{path}:{i}: not valid JSON ({e})")
    return rows


def load_gold(path, allow_test=False):
    """Validated gold items. A split=test row is refused unless allow_test
    (D17), so the sealed test set is never scored by accident."""
    items, seen = [], set()
    for item in _read_jsonl(path):
        validate_gold_item(item)
        if item["split"] == "test" and not allow_test:
            raise ValueError(f"gold {item['qid']}: split=test is sealed; pass --allow-test to score it")
        if item["qid"] in seen:
            raise ValueError(f"gold {item['qid']}: duplicate qid")
        seen.add(item["qid"])
        items.append(item)
    return items


def load_responses(path):
    """{qid: response} from lines carrying "qid" and "response"."""
    out = {}
    for row in _read_jsonl(path):
        if not isinstance(row, dict) or "qid" not in row or "response" not in row:
            raise ValueError(f"{path}: every line needs 'qid' and 'response'")
        if row["qid"] in out:
            raise ValueError(f"{path}: duplicate response for {row['qid']}")
        out[row["qid"]] = row["response"] if row["response"] is not None else ""
    return out


def file_sha256(path, lf=False):
    """SHA-256 of the file bytes. lf=True first turns CRLF into LF, so the
    hash is the same on a Windows checkout (core.autocrlf) and on CI."""
    data = open(path, "rb").read()
    if lf:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score QA responses against gold nuggets.")
    ap.add_argument("--gold", required=True)
    ap.add_argument("--responses", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-test", action="store_true",
                    help="score split=test rows (sealed set; only when deliberately unsealing)")
    a = ap.parse_args(argv)

    gold = load_gold(a.gold, allow_test=a.allow_test)
    responses = load_responses(a.responses)
    missing = [g["qid"] for g in gold if g["qid"] not in responses]
    if missing:
        print(f"no response for {len(missing)} gold qid(s): {', '.join(missing)}", file=sys.stderr)
        return 2
    extra = sorted(set(responses) - {g["qid"] for g in gold})
    if extra:
        print(f"warning: ignoring {len(extra)} response(s) with no gold item: {', '.join(extra)}",
              file=sys.stderr)

    rows = [score_question(g, responses[g["qid"]]) for g in gold]
    aggs = {v: aggregate(rows, v) for v in VARIANTS}
    me = os.path.abspath(__file__)
    report = {"scorer": "divergence/eval/qa_scorer.py",
              "scorer_sha256": file_sha256(me),
              "scorer_sha256_lf": file_sha256(me, lf=True),
              "gold_path": a.gold, "gold_sha256": file_sha256(a.gold),
              "responses_path": a.responses, "responses_sha256": file_sha256(a.responses),
              "n": len(rows), "rows": rows,
              "aggregates": {v: _jsonable(aggs[v]) for v in VARIANTS}}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    agg = aggs["primary"]
    print(f"scored {len(rows)} question(s) -> {a.out}")
    print(f"scorer sha256 {report['scorer_sha256']}  (LF-normalised {report['scorer_sha256_lf']})")
    print("cells (primary): " + "  ".join(f"{c}={agg['cells'][c]}" for c in CELLS + ("N",)))
    for name, v in agg["metrics"].items():
        shown = (f"{v.numerator}/{v.denominator} = {float(v):.4f}" if v is not None
                 else f"None ({agg['none_reasons'][name]})")
        print(f"  {name:<24} {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
