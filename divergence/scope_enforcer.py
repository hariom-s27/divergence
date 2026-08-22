#!/usr/bin/env python3
"""
SCOPE-REACH ENFORCER — ⚙ E — DIVERGENCE
Deterministic. No model call. Same discipline as gap_enforcer.py (⚙ A) and
citation_matcher.py (⚙ C): a prompt instruction is a request, code is a
guarantee.

citation_matcher.py's own LIMITATIONS section says this plainly: "A
VERIFIED citation exists in our corpus and is current. It does NOT mean
the provision supports the proposition it was cited for... Mitigation:
the adversarial node checks support. This checks existence." Node 5 is
that mitigation — an LLM call, probabilistic — and it is exactly how this
project already knows about real scope-reach failures, caught live, never
planted into a test case:

  - runs/21aug/D1-a_attack.json: a draft conclusion valued a USDC receipt
    "as per Rule 11UA" (now Rule 57) — the attack landed; Rule 57 contains
    zero VDA references and its one residual clause (row 7) is scoped to
    s.26(2)(j), never to s.92, the section that actually brought a VDA
    into "property" (ITR2026-RULE-57.md).
  - DECISION-D50.md's addendum: Rule 243(8)(e) / Rule 247 cited as THIS
    taxpayer's valuation method — both govern a Reporting Crypto-Asset
    Service Provider, a regulated intermediary, never the individual whose
    receipt is being valued (ITR2026-RULE-247.md).
  - DECISION-D50.md: Rule 206/207 cited to convert a VDA receipt — both
    rules convert income "in foreign currency," and s.2(111), Income-tax
    Act 2025, defines a VDA as "not being Indian currency or foreign
    currency" (ITR2026-RULE-206.md).

Each was fixed by adding a SCOPE GATE paragraph to prompt 03 (D54, D55) —
a stronger request, still only a request, and still only as reliable as
node 5 happening to run and happening to land the attack. This closes it
in code for exactly these three provisions, no further claim than that: a
fourth misapplied provision this project has never analysed sails straight
through unchanged, same as before. See LIMITATIONS at the bottom.

A fourth candidate — s.393(1) Table Sl. No. 8(vi), "FOR PAYMENTS TO
RESIDENT" — was deliberately left OUT. That failure (DECISION-D55.md, the
inverted-role bug) turns on which DIRECTION a conclusion argues, not on
citation + facts alone: the correct final answer in D1 genuinely does cite
this same provision, correctly, to explain why no obligation arises. A
scope check keyed only to "this provision + these facts" cannot tell that
conclusion apart from the wrong one without reading the outcome text —
and a keyword guess at outcome polarity is exactly the kind of unverified
heuristic this project's own discipline exists to refuse. Left for node 5.

    python scope_enforcer.py --self-test
    from scope_enforcer import enforce_scope
    kept, dropped = enforce_scope(regimes, facts)
"""

import os
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import citation_matcher  # noqa: E402

# Every asset label this project's own cases use for a virtual digital
# asset (see cases/*/case.md). A small, explicit, hand-kept list — not a
# general "what counts as foreign currency" classifier. Guessing at an
# unfamiliar token is exactly the overreach this checker exists to avoid
# committing itself; an asset label not on this list is left untouched by
# every check below, not assumed to be a VDA.
KNOWN_VDA_ASSETS = {"usdc", "usdt", "btc", "bitcoin", "eth", "ethereum",
                    "vda", "virtual digital asset", "crypto", "cryptocurrency"}


def _asset_is_vda(facts):
    asset = (facts.get("asset") or {}).get("value") or ""
    return str(asset).strip().lower() in KNOWN_VDA_ASSETS


def _check_206_207_foreign_currency_only(facts):
    """ITR2026-RULE-206.md, (a): Rule 206/207 converts income "in foreign
    currency". s.2(111) defines a VDA as "not being Indian currency or
    foreign currency" — the rule cannot reach it, for any VDA receipt,
    regardless of the conclusion the citation is used to support."""
    if not _asset_is_vda(facts):
        return True, ""
    return False, (
        "Rule 206/207 converts income 'in foreign currency.' The asset here "
        "is a virtual digital asset; s.2(111), Income-tax Act, 2025 defines "
        "a VDA as 'not being Indian currency or foreign currency,' adopting "
        "FEMA's own definitions. Rule 206/207 does not reach this receipt "
        "at all (ITR2026-RULE-206.md)."
    )


def _check_57_not_scoped_to_s92_vda(facts):
    """ITR2026-RULE-57.md: rows 1-5 (which serve s.92, the section that
    brought a VDA into "property") cover only jewellery/art/shares; rows
    6-7's residual catch-all is scoped to s.26(2)(j) alone, never to s.92.
    Rule 57 contains zero VDA references, machine-checked against the
    2026 gazette. Historical instance: runs/21aug/D1-a_attack.json cited
    the predecessor "Rule 11UA" as the valuation authority; the attack
    landed for exactly this reason."""
    if not _asset_is_vda(facts):
        return True, ""
    return False, (
        "Rule 57's rows that serve s.92 (the section a VDA was brought "
        "into as 'property') are scoped to jewellery, art, and shares; its "
        "one residual catch-all (row 7) is scoped to s.26(2)(j) alone, "
        "never to s.92. Rule 57 contains zero virtual-digital-asset "
        "references (ITR2026-RULE-57.md). It is not this taxpayer's "
        "valuation method."
    )


def _check_243_247_rcasp_only(facts):
    """ITR2026-RCASP-VALUATION.md's own opening words: scoped to "the
    aggregate-reporting obligations of a reporting crypto-asset service
    provider under section 509" — a regulated intermediary, never the
    individual taxpayer whose receipt is being valued. Does not depend on
    facts the way the other two checks do -- no case this project holds
    describes its taxpayer as an RCASP -- but is still exempted by
    enforce_scope() when certainty is "lacuna", same as the others:
    citing this rule to explain that an RCASP-only method does not reach
    the taxpayer is the correct use, not the error this check exists to
    catch."""
    return False, (
        "Rule 243(8)(e) and Rule 247 govern a Reporting Crypto-Asset "
        "Service Provider's own reporting and valuer-registration "
        "obligations — a regulated intermediary, never the individual "
        "taxpayer whose receipt is being valued (ITR2026-RCASP-VALUATION.md, "
        "DECISION-D50.md's addendum)."
    )


# provision_id -> check_fn. Keyed by the same provision_id citation_matcher
# already assigns each corpus file, so a citation string in any form
# ("Rule 11UA", "Rule 57, Income-tax Rules, 2026") resolves to the same
# entry via the same ref-extraction/matching citation_matcher.py trusts.
SCOPE_CHECKS = {
    "ITR2026-RULE-206": _check_206_207_foreign_currency_only,
    "ITR2026-RULE-207": _check_206_207_foreign_currency_only,
    "ITR2026-RULE-57": _check_57_not_scoped_to_s92_vda,
    "ITR2026-RCASP-VALUATION": _check_243_247_rcasp_only,
    "ITR2026-RULE-247": _check_243_247_rcasp_only,
}


def _match_provision_id(citation_text, corpus):
    """D65: MUST cross-check the instrument (which Act/Rules) before
    trusting a ref match, same as citation_matcher.verify() itself does.
    Found live, 22 Aug, building disagreement_gate.py against this exact
    same pattern copied there: without the instrument check,
    _refs_match()'s "one bracket chain is a prefix of the other" rule
    means a BRACKET-LESS stored reference (Rule 206/207/57 are all bare
    rule numbers, no sub-clause) matches ANY cited reference with the
    same base number, regardless of which Act or Rules it's actually in.
    Confirmed concretely: a GST citation to "Section 2(6)" and a FEMA
    citation to "Section 2, clauses (h)(m)(n)(q)" both matched on bare
    section number 2 without this guard. This function had silently
    carried the same gap since it was written (D59) -- SCOPE_CHECKS is
    keyed to exactly the bracket-less provision_ids (Rule 206/207/57)
    that trigger it, so an unrelated citation sharing one of those base
    numbers under a different Act could have been mismatched into a
    scope-violation drop it had nothing to do with. No evidence this
    happened on any real record (the resolvers' scoped corpora don't
    plausibly produce that collision), but the guard was missing on
    principle, not caught by any test until a second file copied the
    same gap and got checked against real data."""
    cited_refs = citation_matcher.extract_refs(citation_text)
    if not cited_refs:
        return None
    cited_inst = citation_matcher.instrument_of(citation_text)
    for e in corpus:
        cur_txt, old_txt = e.get("current_citation") or "", e.get("former_citation") or ""
        stored_inst = citation_matcher.instrument_of(cur_txt) or citation_matcher.instrument_of(e.get("provision_id") or "")
        if cited_inst and stored_inst and cited_inst != stored_inst:
            continue
        cur_refs = citation_matcher.extract_refs(cur_txt)
        old_refs = citation_matcher.extract_refs(old_txt)
        if any(citation_matcher._refs_match(c, s)
               for c in cited_refs for s in cur_refs + old_refs):
            return e.get("provision_id")
    return None


def enforce_scope(regimes, facts, corpus=None):
    """Mirrors apply_citation_matcher() in run_pipeline.py: a scope
    violation DROPS the conclusion, the same "REJECTED, not flagged"
    semantics as a failed existence/staleness check — a citation whose own
    scope does not reach these facts is exactly as invalid as a fabricated
    one (citation_matcher.py's LIMITATIONS point 1: existence is not
    relevance; this is the code-level answer for the three provisions this
    project has actually proven, by hand, do not reach a VDA receipt).

    certainty == "lacuna" is exempted, unconditionally. Caught testing
    against a real record, not the self-test below: runs/21aug/
    D1_final_seed2.json — the frozen, already-shipped demo record — cites
    exactly "Rule 57, Income-tax Rules, 2026" on its valuation_method
    regime, and a first version of this function dropped it. Its outcome
    is "No provision in the text prescribes a specific method..."; its
    certainty is "lacuna" — schema.json's own definition of that value is
    "no rule exists". That citation is not a claim that Rule 57 GOVERNS,
    it is the citation being used AS EVIDENCE that it does not — the exact
    use pattern this project's whole thesis is built on (see
    ITR2026-RULE-57.md's "five locked doors"). The historical bug this
    file exists to catch (runs/21aug/D1-a_regimes.json, certainty
    "insufficient_evidence", outcome asserting the rate IS "determined ...
    as per Rule 11UA") never carries certainty "lacuna" — a lacuna finding
    and an affirmative one are never the same regime entry, so this guard
    costs nothing against the real catch below and prevents a false drop
    on the project's own correct output.

    Returns (kept, dropped) — dropped rows carry regime/citation/reason so
    the caller can fold them into limits[] the same way ⚙ C's drops are.
    """
    corpus = corpus if corpus is not None else citation_matcher.load_corpus()
    kept, dropped = [], []
    for r in regimes:
        if r.get("certainty") == "lacuna":
            kept.append(r)
            continue
        cite = r.get("citation") or {}
        pid = _match_provision_id(cite.get("provision", ""), corpus)
        check = SCOPE_CHECKS.get(pid)
        if check:
            ok, reason = check(facts)
            if not ok:
                dropped.append({
                    "regime": r.get("regime"), "citation": cite.get("provision"),
                    "provision_id": pid, "reason": reason,
                })
                continue
        kept.append(r)
    return kept, dropped


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────
# Self-test — real facts shapes (node1_extract.py's own field names),
# real historical misfires, and a control proving the check is
# fact-conditional rather than a blanket ban on the provision.
# ─────────────────────────────────────────────────────────────

VDA_FACTS = {"asset": {"value": "USDC"}}
FOREIGN_CURRENCY_FACTS = {"asset": {"value": "USD"}}  # e.g. case C2 — a real wire, no crypto

SELF_TEST_REGIMES = [
    {  # historical: runs/21aug/D1-a_regimes.json valued a VDA "as per Rule 11UA"
        "regime": "income_tax_on_receipt", "certainty": "insufficient_evidence",
        "citation": {"provision": "Rule 11UA", "tax_year": "FY 2025-26"},
        "_expect_dropped": True, "_facts": VDA_FACTS,
    },
    {  # current-numbering form of the same error
        "regime": "valuation_method", "certainty": "settled",
        "citation": {"provision": "Rule 206, Income-tax Rules, 2026", "tax_year": "FY 2026-27"},
        "_expect_dropped": True, "_facts": VDA_FACTS,
    },
    {  # DECISION-D50.md's addendum
        "regime": "valuation_method", "certainty": "inference",
        "citation": {"provision": "Rule 243(8)(e), Income-tax Rules, 2026", "tax_year": "FY 2026-27"},
        "_expect_dropped": True, "_facts": VDA_FACTS,
    },
    {  # control: same provision, genuine foreign currency (not a VDA) — must NOT drop
        "regime": "valuation_method", "certainty": "settled",
        "citation": {"provision": "Rule 206, Income-tax Rules, 2026", "tax_year": "FY 2026-27"},
        "_expect_dropped": False, "_facts": FOREIGN_CURRENCY_FACTS,
    },
    {  # control: an unrelated, always-valid citation — must NOT drop
        "regime": "income_tax_on_receipt", "certainty": "inference",
        "citation": {"provision": "Section 115BBH", "tax_year": "FY 2026-27"},
        "_expect_dropped": False, "_facts": VDA_FACTS,
    },
    {  # REGRESSION, found testing against the real record, not this fixture set:
       # runs/21aug/D1_final_seed2.json (the frozen, shipped demo) cites Rule 57
       # to explain there IS NO method -- certainty "lacuna", schema.json's own
       # "no rule exists". Must NOT drop. See enforce_scope()'s docstring.
        "regime": "valuation_method", "certainty": "lacuna",
        "citation": {"provision": "Rule 57, Income-tax Rules, 2026", "tax_year": "FY 2026-27"},
        "_expect_dropped": False, "_facts": VDA_FACTS,
    },
    {  # same citation, NOT a lacuna finding -- must still drop
        "regime": "valuation_method", "certainty": "settled",
        "citation": {"provision": "Rule 57, Income-tax Rules, 2026", "tax_year": "FY 2026-27"},
        "_expect_dropped": True, "_facts": VDA_FACTS,
    },
]


def _test_instrument_cross_check(corpus):
    """D65 regression. Real corpus data, real collision: 'Section 2(6),
    Integrated Goods and Services Tax Act, 2017' and FEMA-2n's own
    'Section 2, clauses (h), (m), (n), (q), Foreign Exchange Management
    Act, 1999' both extract base section number 2 -- and FEMA-2n's
    reference carries no bracket suffix, which _refs_match()'s own
    "one bracket chain is a prefix of the other" rule treats as a
    prefix-match for ANY more specific citation to the same base number,
    in ANY Act, without the instrument cross-check this test exists to
    lock in. Confirmed live, 22 Aug, building disagreement_gate.py: this
    function returned 'FEMA-2n' for a GST citation until fixed."""
    gst_pid = _match_provision_id("Section 2(6), Integrated Goods and Services Tax Act, 2017", corpus)
    fema_pid = _match_provision_id("Section 2, clauses (h)(m)(n)(q), Foreign Exchange Management Act, 1999", corpus)
    ok = gst_pid == "GST-IGST-2-6" and fema_pid == "FEMA-2n" and gst_pid != fema_pid
    print(f"  {'instrument cross-check (D65)':<38}{'':<8}{'':<24}"
          f"{'GST≠FEMA':<10}{gst_pid + '/' + str(fema_pid):<10}{'OK' if ok else 'FAIL'}")
    return ok


def self_test():
    corpus = citation_matcher.load_corpus()
    print("\n  SELF-TEST — scope-reach enforcer\n")
    print(f"  {'citation':<38}{'asset':<8}{'certainty':<24}{'expect':<10}{'got':<10}{'result'}")
    print("  " + "-" * 104)
    passed = 0
    for case in SELF_TEST_REGIMES:
        kept, dropped = enforce_scope([case], case["_facts"], corpus)
        got_dropped = bool(dropped)
        ok = got_dropped == case["_expect_dropped"]
        passed += ok
        asset = (case["_facts"]["asset"]["value"])
        print(f"  {case['citation']['provision'][:37]:<38}{asset:<8}{case['certainty']:<24}"
              f"{'DROP' if case['_expect_dropped'] else 'keep':<10}"
              f"{'DROP' if got_dropped else 'keep':<10}{'OK' if ok else 'FAIL'}")
        if dropped:
            print(f"    -> {dropped[0]['reason']}")
    passed += _test_instrument_cross_check(corpus)
    total = len(SELF_TEST_REGIMES) + 1
    print(f"\n  {passed}/{total} as expected.")
    print("  Every DROP above happened in code, keyed to a real historical "
          "misfire. Nothing here asked the model nicely.\n")
    return passed == total


def main():
    ap = argparse.ArgumentParser(description="⚙ E — scope-reach enforcer")
    ap.add_argument("--record", help="a JSON file with top-level 'regimes' and 'facts'")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test or not a.record:
        ok = self_test()
        sys.exit(0 if ok else 1)

    if not os.path.exists(a.record):
        die(f"{a.record} not found")
    record = json.load(open(a.record, encoding="utf-8"))
    kept, dropped = enforce_scope(record.get("regimes", []), record.get("facts", {}))
    print(f"\n  {len(kept)} kept, {len(dropped)} dropped for scope-reach")
    for d in dropped:
        print(f"    DROPPED  {d['regime']:<24} {d['citation']!r}")
        print(f"      {d['reason']}")
    print()


if __name__ == "__main__":
    main()

# ─────────────────────────────────────────────────────────────
# LIMITATIONS — state these in the documentation. Do not hide them.
#
# 1. THREE PROVISIONS, NOT A GENERAL SCOPE-READER.
#    This checks exactly the provisions this project has, by hand, already
#    proven do not reach a VDA receipt. A fourth misapplied provision this
#    project has never analysed is invisible to this file. It is not an
#    NLI model reading arbitrary statutory text against arbitrary facts —
#    it is three hand-verified facts, encoded once each.
#
# 2. THE VDA ASSET LIST IS HAND-KEPT.
#    KNOWN_VDA_ASSETS is a fixed list. A token this project has never seen
#    is treated as NOT a VDA (the safe direction — a false negative here
#    just means node 5 is the only backstop, same as before this file
#    existed) rather than guessed at.
#
# 3. s.393(1) WAS DELIBERATELY LEFT OUT.
#    See the module docstring. That failure turns on outcome polarity, not
#    citation + facts, and a keyword guess at polarity was judged more
#    likely to drop a CORRECT conclusion than to catch a wrong one.
# ─────────────────────────────────────────────────────────────
