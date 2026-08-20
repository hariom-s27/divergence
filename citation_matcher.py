#!/usr/bin/env python3
"""
CITATION MATCHER — DIVERGENCE
Deterministic. No model call. This is the difference between a hope and a guarantee.

Usage:
    python3 citation_matcher.py                 # run the self-test
    from citation_matcher import verify         # use in the pipeline

    verify("Section 115BBH", tax_year="FY 2026-27")
    -> Verdict(status='STALE', ...)

What it checks:   does this citation exist in our corpus, is it CURRENT for the
                  stated tax year, and is it from a citable tier.
What it does NOT: whether the provision actually supports the proposition.
                  Existence is not relevance. See LIMITATIONS at the bottom.
"""

import os, re, json, sys
from dataclasses import dataclass, asdict
from typing import Optional, List

CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus")


# ─────────────────────────────────────────────────────────────
# Normalisation — "s.115BBH", "Section 115BBH", "sec 115BBH" are one thing
# ─────────────────────────────────────────────────────────────

def canon(text: str) -> str:
    """Reduce a citation to a comparable key."""
    t = text.lower().strip()
    t = re.sub(r"\bsections?\b|\bsec\.?\b|\bs\.\s*", "sec ", t)
    t = re.sub(r"\brules?\b|\br\.\s*", "rule ", t)
    t = re.sub(r"\bclause\b|\bcl\.\s*", "", t)
    t = re.sub(r"\bof the\b|\bof\b", " ", t)
    t = re.sub(r"income[- ]tax act,?\s*", "ita ", t)
    t = re.sub(r"income[- ]tax rules,?\s*", "itr ", t)
    t = re.sub(r"\bcgst act,?\s*\d*", "cgst", t)
    t = re.sub(r"\bigst act,?\s*\d*", "igst", t)
    t = re.sub(r"foreign exchange management act,?\s*\d*|\bfema\b", "fema", t)
    t = re.sub(r"[^\w()]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def parse_front_matter(path: str) -> dict:
    """Read the YAML-ish header of a corpus file. No dependency on a YAML lib."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if not raw.startswith("---"):
        return {}
    body = raw.split("---", 2)
    if len(body) < 3:
        return {}
    meta = {}
    for line in body[1].splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        meta[k.strip()] = None if v == "null" else v
    meta["_text"] = body[2]
    meta["_file"] = os.path.basename(path)
    return meta


def load_corpus() -> List[dict]:
    out = []
    for tier in ("tier-a", "tier-b"):
        d = os.path.join(CORPUS, tier)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            m = parse_front_matter(os.path.join(d, fn))
            if m:
                m.setdefault("tier", "A" if tier == "tier-a" else "B")
                out.append(m)
    return out



# ─────────────────────────────────────────────────────────────
# Structured reference parsing
#
# v1 used whole-string substring matching. It failed on three real citations:
#   "Section 439(8)(a)"      vs corpus "Section 439(8), Income-tax Act, 2025"
#   "Section 2(6) IGST Act"  vs corpus "Section 2(6), Integrated Goods and Services Tax Act, 2017"
#   "FEMA section 3"         vs corpus "Sections 3, 7 and 8, Foreign Exchange Management Act, 1999"
# Sub-clause depth, act-name variants, and multi-provision files all broke it.
# v2 parses both sides into (instrument, base number, bracket chain) instead.
# ─────────────────────────────────────────────────────────────

INSTRUMENTS = [
    ("ITA",  r"income[- ]tax act|\bita\b"),
    ("ITR",  r"income[- ]tax rules|\bitr\b"),
    ("IGST", r"integrated goods and services tax|\bigst\b"),
    ("CGST", r"central goods and services tax|\bcgst\b"),
    ("FEMA", r"foreign exchange management|\bfema\b"),
    ("FBIL", r"\bfbil\b"),
    ("SBI",  r"\bsbi\b|telegraphic transfer"),
]

def instrument_of(text: str):
    t = (text or "").lower()
    for name, pat in INSTRUMENTS:
        if re.search(pat, t):
            return name
    return None

def _split_number(num: str):
    """'439(8)(a)' -> ('439', ['8','a']).  '11UA' -> ('11UA', [])."""
    base = re.match(r"[0-9]+[A-Za-z]*", num)
    base = base.group(0) if base else num
    brackets = re.findall(r"\(([^)]+)\)", num)
    return base.upper(), [b.strip().lower() for b in brackets]

def extract_refs(text: str):
    """Pull every (kind, base, brackets) out of a citation or corpus header.
    Handles 'Sections 3, 7 and 8' by expanding the list."""
    if not text:
        return []
    t = text.replace("\u2013", "-")
    refs = []
    for kind, pat in (("SEC", r"(?:sections?|secs?\.?|s\.)\s*"), ("RULE", r"rules?\s*")):
        for m in re.finditer(pat + r"([0-9A-Za-z()\s,and&-]+)", t, flags=re.I):
            chunk = m.group(1)
            chunk = re.split(r"\bof\b|,\s*(?=income|integrated|central|foreign)", chunk, flags=re.I)[0]
            for tok in re.findall(r"[0-9]+[A-Za-z]*(?:\([^)]+\))*", chunk):
                base, br = _split_number(tok)
                refs.append((kind, base, tuple(br)))
    # bare "Rule 57" style already caught; dedupe
    return list(dict.fromkeys(refs))

def _refs_match(cited, stored) -> bool:
    ck, cb, cx = cited
    sk, sb, sx = stored
    cx, sx = list(cx), list(sx)
    if ck != sk or cb != sb:
        return False
    n = min(len(cx), len(sx))
    return cx[:n] == sx[:n]      # one bracket chain is a prefix of the other


# ─────────────────────────────────────────────────────────────
# Tax-year awareness — the part nobody else does
# ─────────────────────────────────────────────────────────────

def fy_start_year(fy: str) -> Optional[int]:
    m = re.search(r"(20\d{2})\s*-\s*(\d{2})", fy or "")
    return int(m.group(1)) if m else None


NEW_ACT_FROM = 2026   # Income-tax Act 2025 / Rules 2026 govern FY 2026-27 onward
GST_74A_FROM = 2024   # CGST s.74A governs FY 2024-25 onward


@dataclass
class Verdict:
    status: str          # VERIFIED | STALE | REJECTED_NOT_FOUND | REJECTED_TIER_B | REJECTED_NO_TAX_YEAR
    cited: str
    matched_file: Optional[str] = None
    provision_id: Optional[str] = None
    should_cite: Optional[str] = None
    reason: str = ""
    accept: bool = False   # ← the pipeline reads THIS. False means the conclusion is dropped.


def verify(citation: str, tax_year: Optional[str] = None, corpus=None) -> Verdict:
    corpus = corpus if corpus is not None else load_corpus()

    if not tax_year:
        return Verdict("REJECTED_NO_TAX_YEAR", citation,
                       reason="Both numbering systems are live. A citation without a tax year "
                              "cannot be validated.", accept=False)

    yr = fy_start_year(tax_year)

    cited_refs = extract_refs(citation)
    cited_inst = instrument_of(citation)

    for e in corpus:
        # v3: strip explanatory prose from citation fields before parsing.
        # A citation field must contain a citation, not a note about one.
        def _clean(x):
            return re.split(r"\s+[—–-]\s+", x or "", maxsplit=1)[0]
        cur_txt, old_txt = _clean(e.get("current_citation")), _clean(e.get("former_citation"))
        cur_refs, old_refs = extract_refs(cur_txt), extract_refs(old_txt)
        stored_inst = instrument_of(cur_txt) or instrument_of(e.get("provision_id") or "")

        if cited_inst and stored_inst and cited_inst != stored_inst:
            continue

        hit_current = any(_refs_match(c, s_) for c in cited_refs for s_ in cur_refs)
        hit_former  = any(_refs_match(c, s_) for c in cited_refs for s_ in old_refs)
        if not (hit_current or hit_former):
            continue

        if str(e.get("tier", "A")).upper().startswith("B") or str(e.get("citable")).lower() == "false":
            return Verdict("REJECTED_TIER_B", citation, e["_file"], e.get("provision_id"),
                           reason="Tier B is context only and may never be cited as authority.",
                           accept=False)

        pid_early = (e.get("provision_id") or "")
        if pid_early == "GST-CGST-74A" and yr and yr < GST_74A_FROM:
            return Verdict("STALE", citation, e["_file"], pid_early,
                           should_cite="CGST ss.73/74",
                           reason="s.74A governs FY 2024-25 onward only.", accept=False)

        # currency check
        if hit_former and yr and yr >= NEW_ACT_FROM and e.get("current_citation"):
            return Verdict("STALE", citation, e["_file"], e.get("provision_id"),
                           should_cite=e["current_citation"],
                           reason=f"This is the superseded numbering. For {tax_year} the current "
                                  f"citation applies.", accept=False)

        if hit_current and yr and yr < NEW_ACT_FROM and e.get("former_citation"):
            return Verdict("STALE", citation, e["_file"], e.get("provision_id"),
                           should_cite=e["former_citation"],
                           reason=f"This is the new numbering. {tax_year} is governed by the "
                                  f"earlier Act.", accept=False)

        # GST demand-section special case
        pid = (e.get("provision_id") or "")
        if pid == "GST-CGST-74A" and yr and yr < GST_74A_FROM:
            return Verdict("STALE", citation, e["_file"], pid,
                           should_cite="CGST ss.73/74",
                           reason="s.74A governs FY 2024-25 onward only.", accept=False)

        return Verdict("VERIFIED", citation, e["_file"], pid,
                       should_cite=e.get("current_citation"),
                       reason="Found in corpus and current for the stated tax year.", accept=True)

    return Verdict("REJECTED_NOT_FOUND", citation,
                   reason="Not present in the corpus. The conclusion resting on it is dropped. "
                          "Note: this means OUR CORPUS does not contain it — not that it does "
                          "not exist in law.", accept=False)


# ─────────────────────────────────────────────────────────────
# Self-test — real citations, stale ones, and fabrications
# ─────────────────────────────────────────────────────────────

CASES = [
    # (citation, tax year, what we expect, why it is in the test set)
    ("Rule 57, Income-tax Rules, 2026", "FY 2026-27", "VERIFIED",   "current, correct year"),
    ("Rule 11UA",                        "FY 2026-27", "STALE",      "OUR OWN ERROR #1"),
    ("Rule 11UA",                        "FY 2025-26", "VERIFIED",   "correct FOR THAT YEAR"),
    ("Section 439(8)(a)",                "FY 2026-27", "VERIFIED",   "current"),
    ("Section 270A(6)",                  "FY 2026-27", "STALE",      "OUR OWN ERROR #2"),
    ("s.115BBH",                         "FY 2026-27", "VERIFIED",   "no renumbering recorded"),
    ("Section 2(6) IGST Act",            "FY 2026-27", "VERIFIED",   "GST unaffected"),
    ("Section 74A CGST",                 "FY 2026-27", "VERIFIED",   "current demand section"),
    ("Section 74A CGST",                 "FY 2022-23", "STALE",      "74A starts FY 2024-25"),
    ("FEMA section 3",                   "FY 2026-27", "VERIFIED",   "the express prohibition"),
    ("Rule 115",                         "FY 2026-27", "VERIFIED",   "in corpus (though inapplicable)"),
    ("Rule 11UB",                        "FY 2026-27", "REJECTED_NOT_FOUND", "🔴 FABRICATED"),
    ("Section 115BBI",                   "FY 2026-27", "REJECTED_NOT_FOUND", "🔴 real section, not loaded"),
    ("Section 56(2)(xiv)",               "FY 2026-27", "REJECTED_NOT_FOUND", "🔴 FABRICATED sub-clause"),
    ("Rule 57",                          None,          "REJECTED_NO_TAX_YEAR", "no year given"),
]


def self_test():
    corpus = load_corpus()
    print(f"Corpus loaded: {len(corpus)} files "
          f"({sum(1 for e in corpus if str(e.get('tier','A')).upper().startswith('A'))} Tier A)\n")
    print(f"{'CITATION':<34}{'YEAR':<12}{'VERDICT':<24}{'OK':<5}NOTE")
    print("-" * 108)
    passed = 0
    for cite, yr, expect, note in CASES:
        v = verify(cite, yr, corpus)
        ok = "✓" if v.status == expect else "✗"
        passed += v.status == expect
        print(f"{cite[:33]:<34}{str(yr or '—'):<12}{v.status:<24}{ok:<5}{note}")
        if v.status == "STALE":
            print(f"{'':<46}→ cite instead: {v.should_cite}")
    print("-" * 108)
    print(f"{passed}/{len(CASES)} as expected\n")

    accepted = sum(1 for c, y, e, n in CASES if verify(c, y, corpus).accept)
    print(f"Conclusions the pipeline would ACCEPT: {accepted}/{len(CASES)}")
    print(f"Conclusions DROPPED:                  {len(CASES)-accepted}/{len(CASES)}")
    print("\nEvery dropped one is dropped by code, not by asking the model nicely.")


if __name__ == "__main__":
    self_test()

# ─────────────────────────────────────────────────────────────
# LIMITATIONS — state these in the documentation. Do not hide them.
#
# 1. EXISTENCE, NOT RELEVANCE.
#    A VERIFIED citation exists in our corpus and is current. It does NOT mean
#    the provision supports the proposition it was cited for. A model can cite
#    a real, current section for a claim it does not support, and this passes.
#    Mitigation: the adversarial node checks support. This checks existence.
#
# 2. FALSE NEGATIVES ARE BY DESIGN.
#    A real provision we did not load is REJECTED. That is the correct direction
#    to fail — we would rather drop a good conclusion than accept a fabricated
#    citation. The manifest declares what we looked at, so the boundary is stated.
#
# 3. GRANULARITY IS COARSE.
#    "Rule 11UA" matches whether the claim rests on sub-rule (1)(a) or (2)(B).
#    Sub-provision matching is future work.
#
# 4. THE TAX-YEAR RULE IS A HEURISTIC.
#    NEW_ACT_FROM = 2026 encodes "the 2025 Act governs FY 2026-27 onward".
#    That is correct for the provisions we hold. It is not a general rule of law.
# ─────────────────────────────────────────────────────────────
