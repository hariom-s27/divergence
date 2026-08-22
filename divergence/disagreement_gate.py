#!/usr/bin/env python3
"""
DISAGREEMENT GATE — DIVERGENCE, Arm D
Deterministic. No model call. Takes k independent resolver samples of the
SAME input (same facts, same missing[], same tax_year -- different
temperature/seed draws) and flags, per regime, whether they actually
agree on the two fields that matter downstream: certainty and citation.
Comparison only -- producing the k samples still needs k real resolver
calls (see LIMITATIONS).

This project already has real, measured evidence that identical-input
resolver calls disagree (Block E2, results.md: node 2's gap recall read
50%/75%/0% across three seeds of the identical D1 case). Nothing
currently turns that instability into a structured, per-field signal a
caller could act on -- results.md reports it as a finding about the
scorer, not something the pipeline itself surfaces about its own output.
This is that signal, built as ordinary code once the samples exist.

    python disagreement_gate.py --self-test
    python disagreement_gate.py runs/21aug/D1_final_seed1.json \\
        runs/21aug/D1_final_seed2.json runs/21aug/D1_final_seed3.json

    from disagreement_gate import check
    verdict = check([regimes_sample1, regimes_sample2, regimes_sample3])
"""

import os
import sys
import json
import argparse
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import citation_matcher  # noqa: E402


def _citation_key(provision_text, corpus):
    """Normalises a citation string to the corpus provision_id it
    resolves to (via the same ref-matching citation_matcher.py already
    trusts), so 'Section 115BBH, Income-tax Act, 2025' and 'Section
    115BBH, Income-tax Act, 1961 -- carried into the Income-tax Act,
    2025' are recognised as the SAME citation, not a disagreement, if
    they resolve to the same provision -- the disagreement that actually
    matters is a different provision, or none found, not a difference in
    which of the two live numbering systems a sample happened to quote.

    MUST cross-check the instrument (which Act/Rules), same as
    citation_matcher.verify() does -- found live, self-testing this
    file: without it, 'Section 2(6), IGST Act' and 'Section 2, clauses
    (h)(m)(n)(q), FEMA' both matched on bare section number 2, because
    _refs_match() treats a bracket-LESS stored reference (FEMA's) as a
    prefix-match for ANY more specific one, with no regard for which Act
    either citation is actually in. citation_matcher.verify() guards
    against exactly this with its own instrument_of() check before ever
    calling _refs_match(); this function had silently omitted the same
    guard, and confidently returned the wrong provision_id for a real GST
    citation until this was caught testing against real data, not a
    synthetic happy-path case."""
    refs = citation_matcher.extract_refs(provision_text or "")
    if not refs:
        return f"UNPARSEABLE:{provision_text!r}"
    cited_inst = citation_matcher.instrument_of(provision_text)
    for e in corpus:
        cur_txt, old_txt = e.get("current_citation") or "", e.get("former_citation") or ""
        stored_inst = citation_matcher.instrument_of(cur_txt) or citation_matcher.instrument_of(e.get("provision_id") or "")
        if cited_inst and stored_inst and cited_inst != stored_inst:
            continue
        cur_refs = citation_matcher.extract_refs(cur_txt)
        old_refs = citation_matcher.extract_refs(old_txt)
        if any(citation_matcher._refs_match(c, s)
               for c in refs for s in cur_refs + old_refs):
            return e.get("provision_id") or provision_text
    return f"NOT_IN_CORPUS:{provision_text!r}"


def check(samples, corpus=None):
    """samples: a list of k `regimes[]` arrays, all real samples of the
    SAME input. Returns {regime_name: verdict_dict}, one entry per regime
    key that appeared in at least one sample."""
    corpus = corpus if corpus is not None else citation_matcher.load_corpus()
    if len(samples) < 2:
        raise ValueError("need at least 2 samples to check for disagreement")

    by_regime = {}
    for k, sample in enumerate(samples):
        for r in sample:
            name = r.get("regime")
            by_regime.setdefault(name, []).append({
                "sample": k,
                "certainty": r.get("certainty"),
                "citation_key": _citation_key((r.get("citation") or {}).get("provision", ""), corpus),
                "citation_raw": (r.get("citation") or {}).get("provision"),
            })

    verdicts = {}
    for regime, entries in by_regime.items():
        n_present = len(entries)
        certainty_counts = Counter(e["certainty"] for e in entries)
        citation_counts = Counter(e["citation_key"] for e in entries)
        certainty_unanimous = len(certainty_counts) == 1 and n_present == len(samples)
        citation_unanimous = len(citation_counts) == 1 and n_present == len(samples)
        verdicts[regime] = {
            "n_samples_with_this_regime": n_present,
            "n_total_samples": len(samples),
            "certainty_unanimous": certainty_unanimous,
            "certainty_distribution": dict(certainty_counts),
            "citation_unanimous": citation_unanimous,
            "citation_distribution": dict(citation_counts),
            "verdict": ("UNANIMOUS" if (certainty_unanimous and citation_unanimous and n_present == len(samples))
                        else "DISAGREEMENT"),
            "entries": entries,
        }
    return verdicts


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def _print_verdicts(verdicts):
    for regime, v in sorted(verdicts.items()):
        mark = "UNANIMOUS " if v["verdict"] == "UNANIMOUS" else "DISAGREE  "
        print(f"  [{mark}] {regime}")
        print(f"             present in {v['n_samples_with_this_regime']}/{v['n_total_samples']} samples")
        print(f"             certainty: {v['certainty_distribution']}")
        print(f"             citation:  {v['citation_distribution']}")


# ─────────────────────────────────────────────────────────────
# Self-test — real data, not synthetic. D1's own three real, saved,
# already-frozen seed records (results.md Block F) ARE k=3 independent
# samples of the identical input. Real, documented disagreement exists
# between them (seed3 diverges from seed1/seed2 on two regimes) --
# results.md already reports the gap-recall instability this produces;
# this checks whether the gate correctly flags the underlying cause.
# ─────────────────────────────────────────────────────────────

SEED_FILES = [
    os.path.join(HERE, "runs", "21aug", "D1_final_seed1.json"),
    os.path.join(HERE, "runs", "21aug", "D1_final_seed2.json"),
    os.path.join(HERE, "runs", "21aug", "D1_final_seed3.json"),
]


def self_test():
    if not all(os.path.exists(p) for p in SEED_FILES):
        die("D1's three seed records are missing -- self-test needs "
            f"{SEED_FILES}")
    samples = [json.load(open(p, encoding="utf-8"))["regimes"] for p in SEED_FILES]
    verdicts = check(samples)

    print("\n  SELF-TEST — disagreement gate, D1's three real seed records\n")
    _print_verdicts(verdicts)

    # Known, real, hand-verified shape (checked against the raw files
    # directly, not assumed): income_tax_on_receipt and valuation_method
    # both disagree (seed3 diverges); gst_export is unanimous
    # (insufficient_evidence in all three, forced there by gap_enforcer
    # regardless of what the model itself said).
    ok1 = verdicts["income_tax_on_receipt"]["verdict"] == "DISAGREEMENT"
    ok2 = verdicts["valuation_method"]["verdict"] == "DISAGREEMENT"
    ok3 = verdicts["gst_export"]["verdict"] == "UNANIMOUS"
    passed = int(ok1) + int(ok2) + int(ok3)
    print(f"\n  {passed}/3 as expected "
          f"(income_tax_on_receipt DISAGREE, valuation_method DISAGREE, gst_export UNANIMOUS).\n")
    return passed == 3


def main():
    ap = argparse.ArgumentParser(description="Arm D -- deterministic k-sample disagreement gate")
    ap.add_argument("records", nargs="*", help="k record files, each with a top-level 'regimes' array")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test or not a.records:
        ok = self_test()
        sys.exit(0 if ok else 1)

    if len(a.records) < 2:
        die("give at least 2 record files to compare")
    samples = []
    for p in a.records:
        if not os.path.exists(p):
            die(f"{p} not found")
        samples.append(json.load(open(p, encoding="utf-8"))["regimes"])

    verdicts = check(samples)
    print(f"\n  {len(samples)} samples compared\n")
    _print_verdicts(verdicts)
    n_disagree = sum(1 for v in verdicts.values() if v["verdict"] == "DISAGREEMENT")
    print(f"\n  {n_disagree}/{len(verdicts)} regime(s) show disagreement across samples.\n")


if __name__ == "__main__":
    main()

# ─────────────────────────────────────────────────────────────
# LIMITATIONS — state these in the documentation. Do not hide them.
#
# 1. THIS COMPARES SAMPLES. IT DOES NOT PRODUCE THEM.
#    "k=5 resolver sampling" (the item this was built for) means five
#    real resolver calls at real temperature -- five real API calls this
#    session has no FEATHERLESS_API_KEY to make. This file's self-test
#    uses k=3, not k=5, because that's the real sample count this project
#    actually has on disk (D1's three frozen seed records, results.md
#    Block F) -- disclosed as k=3, not silently presented as k=5.
#
# 2. UNANIMOUS IS NOT THE SAME CLAIM AS CORRECT.
#    All k samples agreeing means the resolver is stable on this input,
#    not that the agreed-upon answer is right. Citation currency and
#    scope reach are still ⚙ C's and ⚙ E's job, run after this, same as
#    any single-sample run.
#
# 3. ONLY certainty AND citation ARE COMPARED.
#    Free-text fields (outcome, reasoning) are not diffed -- exact-string
#    comparison on prose would flag trivial rewording as "disagreement"
#    and drown the signal that actually matters (a different legal
#    conclusion, not a different sentence saying the same thing).
# ─────────────────────────────────────────────────────────────
