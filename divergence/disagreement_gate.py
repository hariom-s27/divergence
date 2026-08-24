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

D75 adds two more functions on top of D65's check() above, built for
real k=5 resolver sampling (node_resolver.resolve_k()) and wired into
run_arms.py as arm D:

    from disagreement_gate import cluster, apply_downgrade
    clusters = cluster([s["regimes"] for s in k_samples])
    # {regime_name: {k, n_present, modal_provisions, agreement,
    #                 certainty_spread, polarity_spread, entries}}
    regimes_out, budget_items = apply_downgrade(k_samples[0]["regimes"], clusters)
    # regimes_out: k_samples[0]'s regimes[], certainty forced to
    #   "contested" wherever the downgrade rule fired (D75)
    # budget_items: new valuation.uncertainty_budget[] entries, one per
    #   downgraded regime, carrying the full k-sample breakdown

check() answers "did these samples agree at all" (a boolean verdict per
regime). cluster()/apply_downgrade() answer "by how much, and what
should the pipeline actually do about it" -- additive to check(), not a
replacement; both stay, both self-tested, both against the same real
D1 seed data where possible (see self_test_cluster()).
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


# ─────────────────────────────────────────────────────────────
# D75: modal-provisions / agreement / certainty-spread clustering, and
# the deterministic downgrade rule built on top of it. Additive to D65's
# check() above, not a replacement -- check() answers "did these k
# samples agree at all" for the CLI/self-test; cluster() below answers
# "what's the mode, what fraction hit it, what's the spread" for a
# caller (run_arms.py's arm D) that needs the actual numbers, not just a
# unanimous/disagreement verdict.
# ─────────────────────────────────────────────────────────────

CONFIDENT_CERTAINTY = {"settled", "inference"}
UNCERTAIN_CERTAINTY = {"lacuna", "contested"}

# Deliberately crude, deliberately disclosed as crude (see LIMITATIONS
# below): a negation-phrase scan, not an NLP model, so "coarse outcome
# polarity" stays code, not a sixth model call. Ordered longest/most
# specific phrase first so "no deduction obligation arises" matches on
# its own phrase rather than falling through to the bare " no ".
_NEGATION_MARKERS = (
    "no deduction obligation", "no obligation arises", "does not arise",
    "does not apply", "does not meet", "is not applicable", "not applicable",
    "cannot be", " no ", " not ",
)


def _coarse_polarity(outcome_text, certainty):
    """Three buckets, code only, no model call.

    'undetermined' for lacuna/insufficient_evidence FIRST -- a lacuna
    conclusion's own outcome text often contains a negation ("no
    provision... prescribes a method") that is not the same claim as an
    affirmative regime finding a negation ("no deduction obligation
    arises"). Certainty already carries that distinction; checking it
    before scanning text avoids collapsing two different kinds of "no"
    into the same bucket."""
    if certainty in ("lacuna", "insufficient_evidence"):
        return "undetermined"
    text = f" {(outcome_text or '').lower()} "
    if any(m in text for m in _NEGATION_MARKERS):
        return "negative"
    return "affirmative"


def cluster(samples, corpus=None):
    """samples: a list of k `regimes[]` arrays, all real samples of the
    SAME input (same shape check() takes). For each regime name present
    in at least one sample, extracts per-sample (provisions, certainty,
    coarse polarity) -- provisions via _citation_key() above, i.e. the
    SAME citation_matcher.py provision-id extraction check() already
    uses, not a second implementation of citation matching.

    Returns {regime_name: {k, n_present, modal_provisions, agreement,
    certainty_spread, polarity_spread, entries}}.

    agreement's denominator is k (total samples requested), not
    n_present (samples where this regime showed up at all) -- a regime
    silently missing from some samples IS disagreement about whether the
    conclusion exists, not a smaller-but-still-valid comparison. Deciding
    otherwise would let a resolver that drops a conclusion outright score
    BETTER than one that reports it inconsistently, which is backwards.
    """
    corpus = corpus if corpus is not None else citation_matcher.load_corpus()
    k = len(samples)
    if k < 2:
        raise ValueError("need at least 2 samples to cluster")

    by_regime = {}
    for i, sample in enumerate(samples):
        for r in sample:
            name = r.get("regime")
            provision_text = (r.get("citation") or {}).get("provision", "")
            key = _citation_key(provision_text, corpus)
            certainty = r.get("certainty")
            by_regime.setdefault(name, []).append({
                "sample": i,
                "provisions": (key,),   # 1-tuple: _citation_key is single-valued (D65);
                                         # kept as a tuple so a future multi-citation
                                         # extraction can drop in without changing this shape
                "certainty": certainty,
                "polarity": _coarse_polarity(r.get("outcome", ""), certainty),
            })

    clusters = {}
    for regime, entries in by_regime.items():
        provision_counts = Counter(e["provisions"] for e in entries)
        modal_tuple, modal_count = provision_counts.most_common(1)[0]
        clusters[regime] = {
            "k": k,
            "n_present": len(entries),
            "modal_provisions": sorted(modal_tuple),
            "agreement": modal_count / k,
            "certainty_spread": sorted({e["certainty"] for e in entries}),
            "polarity_spread": sorted({e["polarity"] for e in entries}),
            "entries": entries,
        }
    return clusters


def apply_downgrade(baseline_regimes, clusters, min_agreement=0.6):
    """The deterministic downgrade rule (D75). Code, not a model --
    same discipline as gap_enforcer.py (⚙ A): a fixed condition,
    checked in Python, overwrites a field unconditionally when it fires.

    Fires per regime when EITHER:
      - agreement < min_agreement (default 0.6), OR
      - certainty_spread contains BOTH a confident label
        (settled/inference) AND an uncertain one (lacuna/contested).

    baseline_regimes is ONE concrete sample's regimes[] to mutate --
    the caller's choice of which sample is "baseline" (arm D uses
    sample 0, disclosed as an arbitrary-but-fixed choice, not a vote).
    This function does not choose a baseline itself; it only decides,
    per regime already present in the one it's given, whether to
    overwrite that regime's certainty to "contested".

    Returns (regimes_out, budget_items). regimes_out is a deep copy of
    baseline_regimes with certainty overwritten where the rule fired,
    each carrying a new "_k_sample_downgrade" field recording why.
    budget_items is a list of new valuation.uncertainty_budget[]-shaped
    dicts, one per downgraded regime, carrying the full k-sample
    breakdown -- not just that samples disagreed, but what each one
    actually said, the same "don't just assert it, show it" discipline
    node7_disclosure.py already applies to everything else on the page.
    """
    import copy
    regimes_out = copy.deepcopy(baseline_regimes)
    budget_items = []
    for r in regimes_out:
        name = r.get("regime")
        c = clusters.get(name)
        if c is None:
            continue
        spread = set(c["certainty_spread"])
        mixed = bool(spread & CONFIDENT_CERTAINTY) and bool(spread & UNCERTAIN_CERTAINTY)
        low_agreement = c["agreement"] < min_agreement
        if not (low_agreement or mixed):
            continue

        if low_agreement and mixed:
            reason = "low_agreement+mixed_confident_uncertain"
        elif low_agreement:
            reason = "low_agreement"
        else:
            reason = "mixed_confident_uncertain"

        original_certainty = r.get("certainty")
        r["certainty"] = "contested"
        r["_k_sample_downgrade"] = {
            "triggered_by": reason,
            "original_certainty": original_certainty,
            "agreement": c["agreement"],
            "min_agreement_threshold": min_agreement,
            "certainty_spread": c["certainty_spread"],
            "k": c["k"],
        }
        budget_items.append({
            "source": f"resolver sampling disagreement ({name})",
            "inr": 0.0,
            "explanation": (
                f"{c['k']} independent samples of this regime's resolver call "
                f"agreed on citation in {c['agreement']:.0%} of draws "
                f"(threshold {min_agreement:.0%} -- {reason}). Certainty labels "
                f"seen across the {c['k']} draws: {', '.join(c['certainty_spread'])}. "
                f"Certainty forced to 'contested' in code (D75), not asserted by "
                f"any single sample."
            ),
            "k_variants": c["entries"],
        })
    return regimes_out, budget_items


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


def self_test_cluster():
    """D75, real data, k=3 (not k=5 -- see DECISION-D75.md: this project
    has three real saved samples of D1 on disk, not five; disclosed as
    three throughout, same discipline check()'s own self-test already
    holds itself to). Exercises cluster() against the identical three
    seed files check()'s self-test already trusts.

    Expectations below were computed by actually running cluster()
    against these three real files and reading the result, not assumed
    from what the disagreement "should" look like. What's actually there:
    all three seeds cite the SAME provision on all three regimes (the
    S.393(1)/Rule 206/243 fix cycle in results.md Block F was already
    applied before any of these three seeds ran -- they are three
    temperature draws of the ALREADY-FIXED prompt, not three points in
    that fix cycle) -- so citation agreement is 100% everywhere, and
    modal_provisions is a single, unanimous entry on every regime.
    What DOES move is certainty: income_tax_on_receipt reads settled,
    settled, then insufficient_evidence; valuation_method reads lacuna,
    lacuna, then insufficient_evidence. Real, measured instability --
    just not the citation-level disagreement a reader might expect from
    the word "disagreement" in this file's own name."""
    if not all(os.path.exists(p) for p in SEED_FILES):
        die("D1's three seed records are missing -- self-test needs "
            f"{SEED_FILES}")
    samples = [json.load(open(p, encoding="utf-8"))["regimes"] for p in SEED_FILES]
    clusters = cluster(samples)

    print("\n  SELF-TEST — cluster(), D1's three real seed records\n")
    for regime, c in sorted(clusters.items()):
        print(f"  {regime}")
        print(f"    modal_provisions   {c['modal_provisions']}")
        print(f"    agreement          {c['agreement']:.0%}  ({c['n_present']}/{c['k']} present)")
        print(f"    certainty_spread   {c['certainty_spread']}")
        print(f"    polarity_spread    {c['polarity_spread']}")

    ok1 = clusters["income_tax_on_receipt"]["agreement"] == 1.0
    ok2 = clusters["income_tax_on_receipt"]["certainty_spread"] == ["insufficient_evidence", "settled"]
    ok3 = clusters["valuation_method"]["agreement"] == 1.0
    ok4 = clusters["valuation_method"]["certainty_spread"] == ["insufficient_evidence", "lacuna"]
    ok5 = clusters["gst_export"]["certainty_spread"] == ["insufficient_evidence"]
    passed = sum([ok1, ok2, ok3, ok4, ok5])
    print(f"\n  {passed}/5 as expected (100% citation agreement on all three "
          f"regimes; certainty spreads as measured above).\n")

    # apply_downgrade() on this same real data -- reported, not forced to
    # show a downgrade. See DECISION-D75.md "An honest negative result":
    # NEITHER trigger condition fires on this real k=3 sample, because
    # (a) citation agreement never drops below 1.0 here, and (b) the
    # observed certainty spreads are settled/insufficient_evidence and
    # lacuna/insufficient_evidence -- insufficient_evidence is, by the
    # spec this was built to, in NEITHER the confident set (settled,
    # inference) NOR the uncertain set (lacuna, contested), so "mixed"
    # never triggers either. This is not a bug being routed around --
    # the mechanical-firing path is separately verified below, on a
    # small constructed fixture, not real case data.
    downgraded, budget_items = apply_downgrade(samples[0], clusters)
    downgraded_names = {r["regime"] for r in downgraded if "_k_sample_downgrade" in r}
    print(f"  apply_downgrade() on this real data: {sorted(downgraded_names) or '(none downgraded)'}"
          f", {len(budget_items)} new budget item(s).")
    print("  Expected: none -- see DECISION-D75.md, 'An honest negative result'.\n")
    ok6 = downgraded_names == set()
    return (passed == 5) and ok6


def self_test_downgrade_mechanics():
    """NOT real case data -- a small, hand-constructed fixture, labelled
    as such, existing only to verify apply_downgrade()'s two trigger
    conditions actually fire when their own stated precondition is
    literally true. self_test_cluster() above is the real-data check;
    this is the unit-level check that the mechanism itself works, since
    the one real k=3 sample this project has does not happen to cross
    either threshold (see DECISION-D75.md)."""
    def regime(name, certainty, provision):
        return {"regime": name, "outcome": "x", "certainty": certainty,
                "citation": {"provision": provision, "tax_year": "FY 2026-27"}}

    corpus = citation_matcher.load_corpus()

    # Case 1: low agreement -- 3 samples, 3 different provisions on the
    # same regime -> modal count 1, agreement 1/3, below 0.6.
    low_agreement_samples = [
        [regime("r1", "settled", "Section 115BBH, Income-tax Act, 2025")],
        [regime("r1", "settled", "Rule 57, Income-tax Rules, 2026")],
        [regime("r1", "settled", "Section 2(6), Integrated Goods and Services Tax Act, 2017")],
    ]
    c1 = cluster(low_agreement_samples, corpus=corpus)
    d1, b1 = apply_downgrade(low_agreement_samples[0], c1)
    ok1 = d1[0].get("_k_sample_downgrade", {}).get("triggered_by") == "low_agreement"

    # Case 2: mixed confident/uncertain -- same provision every time
    # (agreement 1.0), certainty alternates settled/lacuna.
    mixed_samples = [
        [regime("r1", "settled", "Rule 57, Income-tax Rules, 2026")],
        [regime("r1", "lacuna", "Rule 57, Income-tax Rules, 2026")],
        [regime("r1", "settled", "Rule 57, Income-tax Rules, 2026")],
    ]
    c2 = cluster(mixed_samples, corpus=corpus)
    d2, b2 = apply_downgrade(mixed_samples[0], c2)
    ok2 = d2[0].get("_k_sample_downgrade", {}).get("triggered_by") == "mixed_confident_uncertain"

    # Case 3: neither condition -- unanimous provision, unanimous
    # certainty -> no downgrade, no budget item.
    unanimous_samples = [
        [regime("r1", "settled", "Rule 57, Income-tax Rules, 2026")],
        [regime("r1", "settled", "Rule 57, Income-tax Rules, 2026")],
        [regime("r1", "settled", "Rule 57, Income-tax Rules, 2026")],
    ]
    c3 = cluster(unanimous_samples, corpus=corpus)
    d3, b3 = apply_downgrade(unanimous_samples[0], c3)
    ok3 = "_k_sample_downgrade" not in d3[0] and len(b3) == 0

    print("\n  SELF-TEST — apply_downgrade() mechanics, constructed fixtures (not real case data)\n")
    print(f"    low_agreement fires when agreement < 0.6:                {ok1}")
    print(f"    mixed_confident_uncertain fires on settled+lacuna:        {ok2}")
    print(f"    neither fires when unanimous:                             {ok3}")
    passed = sum([ok1, ok2, ok3])
    print(f"\n  {passed}/3 as expected.\n")
    return passed == 3


def main():
    ap = argparse.ArgumentParser(description="Arm D -- deterministic k-sample disagreement gate")
    ap.add_argument("records", nargs="*", help="k record files, each with a top-level 'regimes' array")
    ap.add_argument("--self-test", action="store_true",
                    help="run all four self-tests: check() (D65), cluster() (D75), "
                         "apply_downgrade() on real data (D75), apply_downgrade() "
                         "mechanics on constructed fixtures (D75)")
    a = ap.parse_args()

    if a.self_test or not a.records:
        results = {
            "check() -- D65": self_test(),
            "cluster()/apply_downgrade() on real D1 seeds -- D75": self_test_cluster(),
            "apply_downgrade() mechanics, constructed fixtures -- D75": self_test_downgrade_mechanics(),
        }
        print("  " + "=" * 60)
        for name, ok in results.items():
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print("  " + "=" * 60 + "\n")
        sys.exit(0 if all(results.values()) else 1)

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
# Full account, including the honest negative result on real data and
# the semantic-entropy caveat: DECISION-D75.md.
#
# 1. THIS COMPARES SAMPLES. IT DOES NOT PRODUCE THEM.
#    node_resolver.resolve_k() (D75) is the producer -- a plain loop over
#    resolve(), no n= API parameter (Featherless doesn't document one).
#    This file's own real-data self-test still uses k=3, not k=5,
#    because D1's three frozen seed records (results.md Block F) are the
#    only real samples this project has on disk with no
#    FEATHERLESS_API_KEY available in this environment -- disclosed as
#    k=3, not silently presented as k=5.
#
# 2. UNANIMOUS IS NOT THE SAME CLAIM AS CORRECT.
#    All k samples agreeing means the resolver is stable on this input,
#    not that the agreed-upon answer is right. Citation currency and
#    scope reach are still ⚙ C's and ⚙ E's job, run after this, same as
#    any single-sample run. Sampling measures STABILITY. It does not and
#    cannot measure correctness -- restated at the top of DECISION-D75.md
#    because it is the single easiest claim to overstate about this file.
#
# 3. ONLY certainty AND citation ARE COMPARED (check()); cluster() also
#    reads a coarse, code-only OUTCOME POLARITY (_coarse_polarity()) --
#    a negation-phrase scan, not an NLP model. Free-text fields (outcome,
#    reasoning) are never diffed verbatim -- exact-string comparison on
#    prose would flag trivial rewording as "disagreement" and drown the
#    signal that actually matters (a different legal conclusion, not a
#    different sentence saying the same thing). _coarse_polarity() is
#    reported in cluster()'s output (polarity_spread) but is NOT part of
#    apply_downgrade()'s trigger condition -- the spec this was built to
#    fires on citation agreement and certainty spread only. A resolver
#    that unanimously agrees on citation and certainty while flipping
#    polarity (e.g. "no obligation arises" vs "an obligation arises",
#    same citation, same certainty label) would currently sail through
#    undowngraded -- reported here as a known gap in the rule's own
#    coverage, not fixed by silently widening the trigger beyond what
#    was specified.
#
# 4. AGREEMENT ON A GENUINE LACUNA IS EXPECTED, NOT EVIDENCE OF
#    RELIABILITY. If every one of k samples correctly reports lacuna
#    (Rule 57 genuinely names no method), 100% agreement is the CORRECT
#    behaviour of a resolver reading a genuinely underdetermined
#    provision -- not proof the resolver is well-calibrated in general.
#    A resolver that always says "lacuna" regardless of the actual text
#    would also score 100% agreement on this input. agreement measures
#    CONSISTENCY, never GROUNDING.
#
# 5. THE DOWNGRADE RULE, AS SPECIFIED, DOES NOT FIRE ON THE ONE REAL
#    SAMPLE THIS PROJECT HAS. See self_test_cluster() and
#    DECISION-D75.md, "An honest negative result" -- income_tax_on_receipt
#    and valuation_method both show real certainty movement across D1's
#    three real seeds (settled/insufficient_evidence,
#    lacuna/insufficient_evidence) that the literal confident={settled,
#    inference} / uncertain={lacuna,contested} rule does not classify as
#    "mixed", because insufficient_evidence sits in neither set. Not
#    silently widened to make the demo show a downgrade -- reported as a
#    real edge in the rule's own precision instead, same discipline this
#    project applies to M5 (report a metric that doesn't work in the
#    system's favour, don't tune until it does).
# ─────────────────────────────────────────────────────────────
