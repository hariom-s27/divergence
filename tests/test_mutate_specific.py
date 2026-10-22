"""Offline tests for mutate.py's SPECIFIC kill rule (P03): synthetic
critiques only, no model call, no replay-cache access."""
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "divergence"))
import mutate  # noqa: E402


def _landed(target, attack, **kw):
    return dict(target=target, attack=attack, survived=False, **kw)


def _spec(groups, op="X"):
    return {"operator": op, "kind": "terms", "groups": groups}


def test_cite_terms_section_and_s_dot_forms():
    terms = mutate._cite_terms("Section 2(6), Integrated Goods and Services Tax Act, 2017",
                               "Section 3(6), Integrated Goods and Services Tax Act, 2017")
    spec = _spec([terms])
    for text in ("Section 3(6) of the IGST Act does not define export",
                 "s. 3(6) is not the definition", "IGST s.3(6) cited"):
        assert mutate.match_specific([_landed("gst", text)], spec, [])["hit"], text
    for text in ("Section 2(6) defines export of services", "Section 30(6) is unrelated"):
        assert not mutate.match_specific([_landed("gst", text)], spec, [])["hit"], text


def test_cite_terms_rule_number_needs_keyword():
    terms = mutate._cite_terms("Rule 56, Income-tax Rules, 2026", "Rule 57, Income-tax Rules, 2026")
    assert "57" not in terms
    spec = _spec([terms])
    assert mutate.match_specific([_landed("t", "Rule 57 is about valuation, not this")], spec, [])["hit"]
    assert not mutate.match_specific([_landed("t", "rate of 57 per unit")], spec, [])["hit"]


def test_cite_terms_alphanumeric_token():
    terms = mutate._cite_terms("Section 115BBH, Income-tax Act, 2025", "Section 116BBH, Income-tax Act, 2025")
    spec = _spec([terms])
    assert mutate.match_specific([_landed("t", "there is no 116BBH in the Act")], spec, [])["hit"]
    assert not mutate.match_specific([_landed("t", "Section 115BBH applies")], spec, [])["hit"]


def test_only_landed_attacks_count():
    spec = _spec([["2026-06-30"]])
    survived = dict(target="t", attack="date 2026-06-30 is fine", survived=True)
    assert not mutate.match_specific([survived], spec, [])["hit"]
    assert mutate.match_specific([survived, _landed("t", "date 2026-06-30 is wrong")], spec, [])["attack_index"] == 1


def test_date_variants():
    spec = _spec([mutate._date_terms("2026-06-30")])
    for text in ("dated 30 June 2026", "June 30, 2026 is a day late", "30/06/2026", "the 30th June 2026 rate"):
        assert mutate.match_specific([_landed("t", text)], spec, [])["hit"], text
    assert not mutate.match_specific([_landed("t", "29 June 2026")], spec, [])["hit"]


def test_numbers_indian_and_western_grouping():
    spec = _spec([mutate._num_terms(519295.25)])
    for text in ("INR 5,19,295.25 does not equal", "519,295.25", "about Rs 519295"):
        assert mutate.match_specific([_landed("t", text)], spec, [])["hit"], text
    assert not mutate.match_specific([_landed("t", "INR 5,14,250.00")], spec, [])["hit"]
    assert not mutate.match_specific([_landed("t", "51929525 units")], spec, [])["hit"]


def test_every_group_must_match_in_the_same_attack():
    spec = _spec([["alpha"], ["beta"]])
    split = [_landed("t", "alpha only"), _landed("t", "beta only")]
    assert not mutate.match_specific(split, spec, [])["hit"]
    assert mutate.match_specific([_landed("t", "alpha and beta")], spec, [])["hit"]


def test_empty_spec_never_matches():
    assert not mutate.match_specific([_landed("t", "anything")], _spec([]), [])["hit"]
    assert not mutate.match_specific([_landed("t", "anything")], None, [])["hit"]


def test_overclaim_structural_rule():
    regimes = [
        {"regime": "income_tax_on_receipt", "outcome": "The receipt is classified as income from "
         "the transfer of a virtual digital asset taxed at 30 percent", "certainty": "settled"},
        {"regime": "gst_export", "outcome": "This supply does not meet the conditions for an export "
         "of services", "certainty": "settled"},
    ]
    spec = {"operator": "OVERCLAIM", "kind": "overclaim", "regime_index": 1,
            "regime": "gst_export", "groups": [["settled"]]}
    hit = _landed("This supply does not meet the conditions for export of services",
                  "Marked settled, but the place of supply is unknown")
    assert mutate.match_specific([hit], spec, regimes)["hit"]
    downgrade = _landed("supply does not meet conditions for export of services",
                        "The facts are incomplete", downgraded_to="insufficient_evidence")
    assert mutate.match_specific([downgrade], spec, regimes)["hit"]
    other = _landed("receipt is classified as income from transfer of virtual digital asset",
                    "this is not settled law")
    assert not mutate.match_specific([other], spec, regimes)["hit"]
    named = _landed("export", "The gst_export conclusion cannot be settled on these facts")
    assert mutate.match_specific([named], spec, regimes)["hit"]


def test_real_cases_specs_are_preregistered_and_noops_are_dropped():
    noops = set()
    for case_id in mutate.CASE_FILES:
        data = mutate.load_case(case_id)
        specs = mutate.case_specs(case_id, data, mutate.DEFAULT_SEED)
        for op_name, _fn in mutate.OPERATORS:
            if op_name not in specs:
                noops.add((case_id, op_name))
                continue
            assert specs[op_name]["groups"] and all(specs[op_name]["groups"]), (case_id, op_name)
        # the specs come from the data alone: building them twice gives the same thing
        assert specs == mutate.case_specs(case_id, data, mutate.DEFAULT_SEED)
    assert noops == {("C2", "DATE_SHIFT"), ("D1", "DATE_SHIFT")}


def test_null_operator_is_identity():
    facts, _ty, _missing, regimes, valuation = mutate.load_case("D1")
    r, v, _note = mutate.op_null(regimes, valuation, facts, random.Random(0))
    assert r == regimes and v == valuation and r is not regimes
