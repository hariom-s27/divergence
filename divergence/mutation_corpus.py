#!/usr/bin/env python3
"""
MUTATION CORPUS — DIVERGENCE
Deterministic. No model, no API, no marginal cost. Manufactures labelled
should-fail instances by construction, at zero annotation cost, instead of
waiting for a sixth real scope-reach failure to show up on its own.

Seven mutation operators applied to the six real cases' own saved,
already-verified regime conclusions (`runs/21aug/*_pipeline.json`,
`D1_final_seed2.json` for D1 — the frozen record, read-only, never
written to). Each operator is skipped, explicitly, on a case where it
doesn't apply — never forced onto a fact pattern it doesn't fit, which
would manufacture an easier or nonsensical test.

Every mutation is run through the real, already-shipped deterministic
gates (`citation_matcher.verify`, `scope_enforcer.enforce_scope`,
`gap_enforcer.enforce`) — not a simulation of them. Reports PER-OPERATOR
recall, never one blended number: some of these are designed to be
caught, and some are designed to demonstrate a real, honest gap in what
this project's current gates can see. Both kinds of result are reported
the same way.

    python mutation_corpus.py            # full report
    python mutation_corpus.py --json out.json
"""

import os
import sys
import json
import copy
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import citation_matcher                          # noqa: E402
import scope_enforcer                             # noqa: E402
import gap_enforcer                                # noqa: E402

RUNS = os.path.join(HERE, "runs", "21aug")

CASE_FILES = {
    "C1": "C1_pipeline.json",
    "C2": "C2_pipeline.json",
    "C3": "C3_pipeline.json",
    "C4": "C4_pipeline.json",
    "C5": "C5_pipeline.json",
    "D1": "D1_final_seed2.json",
}

# The three provisions scope_enforcer.py already proves don't reach a VDA.
SCOPE_BAD = [
    ("Rule 206, Income-tax Rules, 2026", "ITR2026-RULE-206"),
    ("Rule 57, Income-tax Rules, 2026", "ITR2026-RULE-57"),
    ("Rule 243(8)(e), Income-tax Rules, 2026", "ITR2026-RCASP-VALUATION"),
]


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def load_case(case_id):
    fn = CASE_FILES[case_id]
    p = os.path.join(RUNS, fn)
    if not os.path.exists(p):
        die(f"{p} not found")
    rec = json.load(open(p, encoding="utf-8"))
    return rec["facts"], rec["tax_year"], rec["regimes"]


def _find_renumbered(corpus, provision_text):
    """Does this citation resolve to a corpus entry that has a real
    former_citation (i.e. is eligible for a year-flip / numbering-swap
    mutation)? Returns the corpus entry or None."""
    refs = citation_matcher.extract_refs(provision_text)
    if not refs:
        return None
    for e in corpus:
        cur_refs = citation_matcher.extract_refs(e.get("current_citation") or "")
        if any(citation_matcher._refs_match(c, s) for c in refs for s in cur_refs):
            if e.get("former_citation"):
                return e
    return None


# ─────────────────────────────────────────────────────────────
# Seven operators. Each: (regimes, facts, tax_year, corpus) -> list of
# (mutated_regime, expected_gate, note) or [] if not applicable.
# expected_gate is documentary only -- the actual result is measured, not
# assumed, and the report shows both.
# ─────────────────────────────────────────────────────────────

def op_year_flip(regimes, facts, tax_year, corpus):
    """Cite the CURRENT-numbering form under the tax year that should
    require the FORMER one. citation_matcher's own STALE path."""
    out = []
    for r in regimes:
        cite = r.get("citation") or {}
        entry = _find_renumbered(corpus, cite.get("provision", ""))
        if not entry:
            continue
        wrong_year = "FY 2025-26" if citation_matcher.fy_start_year(tax_year) >= citation_matcher.NEW_ACT_FROM else "FY 2026-27"
        m = copy.deepcopy(r)
        m["citation"]["tax_year"] = wrong_year
        out.append((m, "citation_matcher (STALE)",
                    f"{cite.get('provision')} cited for {wrong_year} instead of {tax_year}"))
        break  # one mutation per case for this operator is enough signal
    return out


def op_numbering_swap(regimes, facts, tax_year, corpus):
    """Cite the FORMER-numbering form while the tax year requires the
    current one. Same mechanism as op_year_flip, opposite direction --
    exercises citation_matcher's other STALE branch."""
    out = []
    for r in regimes:
        cite = r.get("citation") or {}
        entry = _find_renumbered(corpus, cite.get("provision", ""))
        if not entry:
            continue
        m = copy.deepcopy(r)
        m["citation"]["provision"] = entry["former_citation"].split(" — ")[0]
        out.append((m, "citation_matcher (STALE)",
                    f"cited as {m['citation']['provision']!r} for {tax_year}, "
                    f"which requires the current form"))
        break
    return out


def op_fabricated_citation(regimes, facts, tax_year, corpus):
    """A plausible-sounding section number this corpus does not hold."""
    if not regimes:
        return []
    r = regimes[0]
    m = copy.deepcopy(r)
    m["citation"]["provision"] = "Section 115BBZ, Income-tax Act, 2025"
    return [(m, "citation_matcher (REJECTED_NOT_FOUND)",
             "a real-looking section number that does not exist in this corpus")]


def op_scope_violation(regimes, facts, tax_year, corpus):
    """Only meaningful where the asset is a virtual digital asset --
    cites one of the three provisions scope_enforcer.py already proves
    do not reach one, with certainty NOT lacuna (a real claim, not a
    lacuna citation explaining absence)."""
    asset = (facts.get("asset") or {}).get("value", "")
    if str(asset).strip().lower() not in scope_enforcer.KNOWN_VDA_ASSETS:
        return []
    out = []
    for label, _pid in SCOPE_BAD:
        if not regimes:
            break
        m = copy.deepcopy(regimes[0])
        m["citation"]["provision"] = label
        m["certainty"] = "settled"
        out.append((m, "scope_enforcer (DROPPED)",
                    f"cites {label} as though it reaches a VDA receipt"))
    return out


def op_regime_cross_cite(regimes, facts, tax_year, corpus):
    """Swap one regime's real, current, correctly-cited provision onto a
    DIFFERENT regime in the same case. The citation exists and is
    current -- citation_matcher has nothing to reject. Nothing in this
    project currently checks that a citation belongs to the regime it is
    attached to. Expected to demonstrate a real, disclosed gap."""
    if len(regimes) < 2:
        return []
    out = []
    for i, r in enumerate(regimes):
        other = regimes[(i + 1) % len(regimes)]
        if other.get("regime") == r.get("regime"):
            continue
        m = copy.deepcopy(r)
        m["citation"]["provision"] = (other.get("citation") or {}).get("provision")
        out.append((m, "none currently",
                    f"{r.get('regime')} now cites {other.get('regime')}'s real, "
                    f"current provision"))
    return out[:1]


def op_overconfident_certainty(regimes, facts, tax_year, corpus):
    """Relabel a non-settled conclusion as settled, unchanged otherwise.
    Caught IF AND ONLY IF depends_on_missing is still populated --
    gap_enforcer forces certainty unconditionally in that case regardless
    of what the mutation claims. If depends_on_missing is empty, nothing
    currently re-derives certainty from anything, and this passes
    through silently -- a real, differentiated result, not a single
    yes/no."""
    out = []
    for r in regimes:
        if r.get("certainty") in ("settled",):
            continue
        m = copy.deepcopy(r)
        m["certainty"] = "settled"
        has_deps = bool(m.get("depends_on_missing"))
        out.append((m,
                    "gap_enforcer (forced back)" if has_deps else "none currently",
                    f"{r.get('regime')} relabelled {r.get('certainty')!r} -> 'settled'"
                    f" ({'has' if has_deps else 'has no'} depends_on_missing)"))
    return out


def op_dependency_drop(regimes, facts, tax_year, corpus):
    """Take a conclusion that legitimately depends on a missing fact,
    clear depends_on_missing, and claim settled. gap_enforcer can only
    act on a dependency that is DECLARED -- it has no way to notice one
    was silently removed. Expected to demonstrate a real, disclosed gap."""
    out = []
    for r in regimes:
        if not r.get("depends_on_missing"):
            continue
        m = copy.deepcopy(r)
        m["depends_on_missing"] = []
        m["certainty"] = "settled"
        out.append((m, "none currently",
                    f"{r.get('regime')}'s real dependency on "
                    f"{r.get('depends_on_missing')} silently dropped, claims settled"))
        break
    return out


OPERATORS = [
    ("YEAR_FLIP", op_year_flip),
    ("NUMBERING_SYSTEM_SWAP", op_numbering_swap),
    ("FABRICATED_CITATION", op_fabricated_citation),
    ("SCOPE_VIOLATION", op_scope_violation),
    ("REGIME_CROSS_CITE", op_regime_cross_cite),
    ("OVERCONFIDENT_CERTAINTY", op_overconfident_certainty),
    ("DEPENDENCY_DROP", op_dependency_drop),
]


def check_caught(mutated_regime, facts, tax_year, corpus):
    """Run one mutated regime through the three real deterministic gates.
    Returns (caught: bool, by: str) -- by names which gate, or 'none'."""
    cite = mutated_regime.get("citation") or {}
    v = citation_matcher.verify(cite.get("provision", ""), cite.get("tax_year") or tax_year, corpus)
    if not v.accept:
        return True, f"citation_matcher ({v.status})"

    kept, dropped = scope_enforcer.enforce_scope([mutated_regime], facts, corpus)
    if dropped:
        return True, "scope_enforcer (DROPPED)"

    pre_certainty = mutated_regime.get("certainty")
    rec, forced = gap_enforcer.enforce({"regimes": [copy.deepcopy(mutated_regime)]})
    post_certainty = rec["regimes"][0].get("certainty")
    if forced and post_certainty != pre_certainty:
        return True, "gap_enforcer (forced back)"

    return False, "none"


def run():
    corpus = citation_matcher.load_corpus()
    rows = []
    for case_id in CASE_FILES:
        facts, tax_year, regimes = load_case(case_id)
        for op_name, op_fn in OPERATORS:
            mutations = op_fn(regimes, facts, tax_year, corpus)
            if not mutations:
                rows.append({"case": case_id, "operator": op_name, "applicable": False})
                continue
            for mutated, expected, note in mutations:
                caught, by = check_caught(mutated, facts, tax_year, corpus)
                rows.append({
                    "case": case_id, "operator": op_name, "applicable": True,
                    "expected": expected, "note": note,
                    "caught": caught, "caught_by": by,
                })
    return rows


def report(rows):
    print("\n" + "=" * 92)
    print("  MUTATION CORPUS — per-operator recall (7 operators x 6 cases)")
    print("=" * 92)
    by_op = {}
    for row in rows:
        by_op.setdefault(row["operator"], []).append(row)

    for op_name, _ in OPERATORS:
        op_rows = by_op[op_name]
        applicable = [r for r in op_rows if r["applicable"]]
        caught = [r for r in applicable if r["caught"]]
        n_a = len(op_rows) - len(applicable)
        print(f"\n  {op_name}")
        if not applicable:
            print(f"    not applicable to any of the 6 cases")
            continue
        print(f"    {len(caught)}/{len(applicable)} caught"
              + (f"  ({n_a} case(s) N/A)" if n_a else ""))
        for r in applicable:
            mark = "[CAUGHT]" if r["caught"] else "[MISSED]"
            print(f"      {mark}  {r['case']:<4} {r['note']}")
            print(f"                caught_by={r['caught_by']}  expected={r['expected']}")

    total_applicable = sum(1 for r in rows if r["applicable"])
    total_caught = sum(1 for r in rows if r["applicable"] and r["caught"])
    print(f"\n{'=' * 92}")
    print(f"  {total_caught}/{total_applicable} applicable mutations caught overall. "
          f"Per-operator breakdown above is the real result -- this total is not.")
    print("=" * 92 + "\n")


def main():
    ap = argparse.ArgumentParser(description="Mutation-testing coverage report")
    ap.add_argument("--json", help="also write the raw rows to this path")
    a = ap.parse_args()
    rows = run()
    report(rows)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        print(f"  raw rows -> {a.json}\n")


if __name__ == "__main__":
    main()
