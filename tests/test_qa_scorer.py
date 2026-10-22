# Tests for divergence/eval/qa_scorer.py. Plain assert functions with no
# pytest-only features (no fixtures, no pytest.raises), so the same file can
# also be run by a tiny stdlib runner on an interpreter without pytest (D21).
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORER = os.path.join(ROOT, "divergence", "eval", "qa_scorer.py")
FIXTURE = os.path.join(ROOT, "divergence", "eval", "fixtures", "qa_scorer_synthetic.jsonl")

# divergence/eval has no __init__.py, so load the module by path.
_spec = importlib.util.spec_from_file_location("qa_scorer", SCORER)
qs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qs)

SHA = "0" * 64


def _n(nid, typ, gold, **extra):
    nug = {"nid": nid, "type": typ, "gold": gold, "match": qs.MATCH_FOR_TYPE[typ]}
    nug.update(extra)
    return nug


def _q(nuggets, should_abstain=False, governing_act="2025", qid="T1", split="dev"):
    return {"qid": qid, "split": split, "question": "SYNTHETIC: test question",
            "applicable_tax_year": "2026-27", "governing_act": governing_act,
            "stratum": "lookup", "nesting_depth": 0, "names_section": False,
            "cluster": "SYN", "should_abstain": should_abstain,
            "abstain_reason": "out_of_scope" if should_abstain else "answerable",
            "spans": [{"corpus_file_sha": SHA, "start": 0, "end": 1}],
            "nuggets": nuggets}


def _state(nugget, value, governing_act="2025"):
    """Score one nugget from a single-nugget ANSWER line; return its dict."""
    row = qs.score_question(_q([nugget], governing_act=governing_act), "ANSWER: " + value)
    return row["nuggets"][0]


def _raises(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


# ── 1. Indian commas ──────────────────────────────────────────────────
def test_indian_commas_pass():
    assert qs.parse_number("1,50,000") == Decimal("150000")
    assert qs.parse_number("150,000") == Decimal("150000")
    assert _state(_n("n1", "threshold", "1,50,000"), "150,000")["state"] == "correct"


def test_indian_commas_fail():
    assert _state(_n("n1", "threshold", "1,50,000"), "1,50,001")["state"] == "wrong"


# ── 2. lakh / crore ───────────────────────────────────────────────────
def test_lakh_crore_pass():
    assert qs.parse_number("1.5 lakh") == Decimal("150000")
    assert qs.parse_number("2 lakhs") == Decimal("200000")
    assert qs.parse_number("2 crore") == Decimal("20000000")
    assert qs.parse_number("1.25 crores") == Decimal("12500000")
    assert isinstance(qs.parse_number("1.5 lakh"), Decimal)


def test_lakh_crore_fail():
    assert qs.parse_number("1.5 lakh") != Decimal("15000")
    assert _state(_n("n1", "limit", "1.5 lakh"), "15,000")["state"] == "wrong"


# ── 3. currency markers ───────────────────────────────────────────────
def test_currency_markers_pass():
    for s in ("₹1,50,000", "Rs 1,50,000", "Rs. 1,50,000", "INR 1,50,000",
              "1,50,000 rupees", "rs.150000"):
        assert qs.parse_number(s) == Decimal("150000"), s


def test_currency_markers_fail():
    # "rs" inside a word is not a currency marker, and the leftover text
    # still has to parse to the same single number.
    assert qs.parse_number("years 5") == Decimal("5")
    assert _state(_n("n1", "threshold", "₹1,50,000"), "Rs 1,05,000")["state"] == "wrong"


# ── 4. percent markers ────────────────────────────────────────────────
def test_percent_markers_pass():
    for s in ("30%", "30 per cent", "30 percent", "30pc", "30 pc", "30 Per Cent"):
        r = qs.parse_rate(s)
        assert r["value"] == Decimal("30") and r["percent_marked"], s
    assert _state(_n("n1", "rate", "30 per cent"), "30%")["state"] == "correct"


def test_percent_markers_fail():
    # D3: "pc" not right after a number is not a percent marker.
    assert qs.parse_rate("the pc rate is 30")["percent_marked"] is False
    assert _state(_n("n1", "rate", "30%"), "35 per cent")["state"] == "wrong"


# ── 5. bare fraction for a rate ───────────────────────────────────────
def test_rate_unmarked_whole_number_pass():
    st = _state(_n("n1", "rate", "30%"), "30")
    assert st["state"] == "correct" and st["flags"].get("rate_unmarked")


def test_rate_bare_fraction_fail():
    st = _state(_n("n1", "rate", "30%"), "0.30")
    assert st["state"] == "wrong" and st["flags"].get("bare_fraction")
    assert qs.parse_rate("0.30")["value"] == Decimal("0.30")      # never x100


# ── 6. dates ──────────────────────────────────────────────────────────
def test_date_formats_pass():
    for s in ("1st April, 2026", "01/04/2026", "April 1, 2026", "1 April 2026",
              "2026-04-01", "1-4-2026", "Apr. 1, 2026"):
        assert qs.parse_date(s) == "2026-04-01", s


def test_date_day_first_pass():
    assert qs.parse_date("04/01/2026") == "2026-01-04"
    assert _state(_n("n1", "date", "1st April, 2026"), "01/04/2026")["state"] == "correct"


def test_date_wrong_day_fail():
    assert _state(_n("n1", "date", "1st April, 2026"), "2 April 2026")["state"] == "wrong"


def test_date_unparseable_fail():
    st = _state(_n("n1", "date", "1st April, 2026"), "31/02/2026")
    assert st["state"] == "wrong" and st["flags"].get("date_invalid")
    st = _state(_n("n1", "date", "1st April, 2026"), "early April")
    assert st["state"] == "wrong" and st["flags"].get("date_unparsed")
    assert qs.parse_date("31/02/2026") is None


# ── 7. tax year vs assessment year ────────────────────────────────────
def test_tax_year_forms_pass():
    for s in ("2026-27", "TY 2026-27", "FY 2026-27", "tax year 2026-2027", "2026–27"):
        assert qs.parse_tax_year(s)["start_year"] == 2026, s
    assert _state(_n("n1", "tax_year", "2026-27"), "FY 2026-27")["state"] == "correct"


def test_tax_year_with_ay_aside_pass():
    # D11: a valid tax year decides; an AY alongside it is only flagged.
    st = _state(_n("n1", "tax_year", "2026-27"), "TY 2026-27 (AY 2027-28)")
    assert st["state"] == "correct" and st["flags"].get("assessment_year")


def test_assessment_year_fail():
    r = qs.parse_tax_year("AY 2027-28")
    assert r["assessment_year"] and r["start_year"] is None
    st = _state(_n("n1", "tax_year", "2026-27"), "AY 2027-28")
    assert st["state"] == "wrong" and st["flags"].get("assessment_year")


def test_tax_year_bad_end_and_bare_year_fail():
    assert qs.parse_tax_year("2026-28")["start_year"] is None
    st = _state(_n("n1", "tax_year", "2026-27"), "2026")
    assert st["state"] == "wrong" and st["flags"].get("tax_year_unparsed")


# ── 8. section regex depths ───────────────────────────────────────────
def test_section_regex_depths_pass():
    assert qs.parse_sections("section 80C") == [(None, "80C", None, None)]
    assert qs.parse_sections("section 393(1)") == [(None, "393", "(1)", None)]
    assert qs.parse_sections("s. 80CCD(1b)(ii) of the 1961 Act") == [("1961", "80CCD", "(1b)", "(ii)")]
    nug = _n("n1", "section", "section 10(23c)(iv)", section_depth="clause", act="1961")
    assert _state(nug, "section 10(23c)(iv) of the 1961 Act")["state"] == "correct"


def test_section_depth_deeper_response_pass():
    nug = _n("n1", "section", "section 393(1)", section_depth="subsection", act="2025")
    assert _state(nug, "section 393(1)(a) of the 2025 Act")["state"] == "correct"


def test_section_too_shallow_fail():
    nug = _n("n1", "section", "section 393(1)", section_depth="subsection", act="2025")
    st = _state(nug, "section 393 of the 2025 Act")
    assert st["state"] == "wrong" and st["flags"].get("too_shallow")


def test_section_wrong_clause_fail():
    nug = _n("n1", "section", "section 393(1)(a)", section_depth="clause", act="2025")
    assert _state(nug, "section 393(1)(b) of the 2025 Act")["state"] == "wrong"


# ── 8b. D9 section forms: pass and fail for each ──────────────────────
_SEC = _n("n1", "section", "section 901", section_depth="section", act="2025")


def test_form_section_pass():
    assert qs.parse_sections("section 901")[0][1] == "901"
    assert _state(_SEC, "section 901 of the 2025 Act")["state"] == "correct"


def test_form_section_fail():
    assert qs.parse_sections("intersection 901") == []


def test_form_under_section_pass():
    assert qs.parse_sections("under section 901")[0][1] == "901"
    assert _state(_SEC, "under section 901 (2025 Act)")["state"] == "correct"


def test_form_under_section_fail():
    assert qs.parse_sections("under 901") == []


def test_form_us_pass():
    assert qs.parse_sections("u/s 901")[0][1] == "901"
    assert _state(_SEC, "u/s 901, Income-tax Act, 2025")["state"] == "correct"


def test_form_us_fail():
    assert qs.parse_sections("us 901") == []


def test_form_sec_pass():
    assert qs.parse_sections("sec 901")[0][1] == "901"
    assert qs.parse_sections("sec. 901")[0][1] == "901"
    assert _state(_SEC, "Sec. 901 of the 2025 Act")["state"] == "correct"


def test_form_sec_fail():
    assert qs.parse_sections("secretary 901") == []


def test_form_s_pass():
    assert qs.parse_sections("s 901")[0][1] == "901"
    assert qs.parse_sections("s. 901")[0][1] == "901"
    assert _state(_SEC, "s. 901 of the 2025 Act")["state"] == "correct"


def test_form_s_fail():
    assert qs.parse_sections("this 901") == []


def test_form_bare_token_pass():
    assert qs.parse_sections("393(1)", allow_bare=True) == [(None, "393", "(1)", None)]
    assert qs.parse_sections("80C", allow_bare=True) == [(None, "80C", None, None)]
    nug = _n("n1", "section", "393(1)", section_depth="subsection", act="2025")
    assert _state(nug, "393(1) of the 2025 Act")["state"] == "correct"


def test_form_bare_token_fail():
    # Not outside a section nugget, not a year, not an amount.
    assert qs.parse_sections("393(1)") == []
    assert qs.parse_sections("2026", allow_bare=True) == []
    assert qs.parse_sections("₹1,50,000", allow_bare=True) == []
    # Inside a rate nugget a bare "393(1)" is not a section and not a rate.
    assert _state(_n("n1", "rate", "30%"), "393(1)")["state"] == "wrong"


# ── 9. Act mismatch ───────────────────────────────────────────────────
def test_act_match_pass():
    st = _state(_SEC, "section 901 of the Income-tax Act, 2025")
    assert st["state"] == "correct" and st["version_ok"] is True


def test_act_mismatch_fail():
    st = _state(_SEC, "section 901 of the 1961 Act")
    assert st["state"] == "wrong" and st["flags"].get("act_mismatch")
    assert st["version_ok"] is False


def test_act_both_named_fail():
    st = _state(_SEC, "section 901 of the 1961 Act or the 2025 Act")
    assert st["state"] == "wrong" and st["flags"].get("act_hedged")


def test_version_ok_independent_of_number():
    st = _state(_SEC, "section 999 of the 2025 Act")
    assert st["state"] == "wrong" and st["version_ok"] is True


# ── 10. missing Act (D2: primary wrong, lenient inherits) ─────────────
def test_missing_act_fail_primary():
    st = _state(_SEC, "section 901")
    assert st["state"] == "wrong" and st["flags"].get("act_missing")
    assert st["version_ok"] is False


def test_missing_act_lenient_pass():
    st = _state(_SEC, "section 901", governing_act="2025")
    assert st["state_lenient_act"] == "correct" and st["version_ok_lenient_act"] is True
    # governing_act "both" gives nothing to inherit.
    st = _state(_SEC, "section 901", governing_act="both")
    assert st["state_lenient_act"] == "wrong"


def test_missing_act_lenient_aggregate_separate():
    row = qs.score_question(_q([_SEC]), "ANSWER: section 901")
    assert row["cell"] == "N2" and row["cell_lenient_act"] == "N1"
    assert qs.aggregate([row], "primary")["metrics"]["accuracy"] == 0
    assert qs.aggregate([row], "lenient_act")["metrics"]["accuracy"] == 1


# ── 11. amount tolerance from the gold string ─────────────────────────
def test_amount_tolerance_values():
    assert qs.amount_tolerance("₹1,23,450") == Decimal("0.5")
    assert qs.amount_tolerance("₹1.2 lakh") == Decimal("5000")
    assert qs.amount_tolerance("₹2 lakh") == Decimal("50000")


def test_amount_tolerance_pass():
    assert _state(_n("n1", "amount", "₹1,23,450"), "Rs 1,23,450.5")["state"] == "correct"   # edge, inclusive
    assert _state(_n("n1", "amount", "₹1.2 lakh"), "₹1,25,000")["state"] == "correct"       # edge, inclusive
    assert _state(_n("n1", "amount", "₹1.2 lakh"), "₹1,16,000")["state"] == "correct"


def test_amount_tolerance_fail():
    assert _state(_n("n1", "amount", "₹1,23,450"), "Rs 1,23,451")["state"] == "wrong"
    assert _state(_n("n1", "amount", "₹1.2 lakh"), "₹1,25,001")["state"] == "wrong"


# ── 12. hedged two values ─────────────────────────────────────────────
def test_repeated_same_value_pass():
    assert _state(_n("n1", "rate", "30%"), "30% (30 per cent)")["state"] == "correct"


def test_hedged_two_values_fail():
    st = _state(_n("n1", "rate", "30%"), "20% or 30%")
    assert st["state"] == "wrong" and st["flags"].get("hedged")
    st = _state(_n("n1", "date", "1 April 2026"), "1 April 2026 or 1 May 2026")
    assert st["state"] == "wrong" and st["flags"].get("hedged")


# ── 13. multi-part nid= parsing ───────────────────────────────────────
_TWO = [_n("n1", "rate", "12%"), _n("n2", "limit", "₹40,000")]


def test_multipart_pass():
    sp = qs.split_answer("n1=12%; N2 = Rs 40,000", ["n1", "n2"])
    assert sp["by_nid"] == {"n1": ["12%"], "n2": ["Rs 40,000"]}
    row = qs.score_question(_q(_TWO), "ANSWER: n1=12%; n2=Rs 40,000")
    assert [r["state"] for r in row["nuggets"]] == ["correct", "correct"] and row["cell"] == "N1"


def test_single_nugget_unkeyed_pass():
    row = qs.score_question(_q([_n("n1", "rate", "12%")]), "ANSWER: 12%")
    assert row["cell"] == "N1"


def test_multipart_missing_nid_withheld_fail():
    row = qs.score_question(_q(_TWO), "ANSWER: n1=12%")
    assert [r["state"] for r in row["nuggets"]] == ["correct", "withheld"]
    assert row["cell"] == "N2"


def test_multipart_unkeyed_multi_fail():
    row = qs.score_question(_q(_TWO), "ANSWER: 12%, Rs 40,000")
    assert row["unkeyed_multi"] and all(r["state"] == "wrong" for r in row["nuggets"])
    assert row["cell"] == "N2"


def test_multipart_unknown_and_duplicate_nid_fail():
    sp = qs.split_answer("n1=12%; n9=5%", ["n1", "n2"])
    assert sp["unknown_nids"] == ["n9"]
    row = qs.score_question(_q(_TWO), "ANSWER: n1=12%; n1=15%; n2=Rs 40,000")
    assert row["nuggets"][0]["state"] == "wrong" and row["nuggets"][0]["flags"].get("hedged")


# ── 14. ABSTAIN detection ─────────────────────────────────────────────
def test_abstain_detection_pass():
    for resp in ("ABSTAIN: no version applies", "**ABSTAIN:** out of scope",
                 "reasoning\nabstain: unsure", "ANSWER:", "**ANSWER:**   "):
        ext = qs.extract_final(resp)
        assert ext["abstain_marker"], resp
    row = qs.score_question(_q([_n("n1", "rate", "5%")], should_abstain=True), "ABSTAIN: none")
    assert row["cell"] == "N5"


def test_abstain_detection_fail():
    # A list bullet or text before the marker does not make a final line.
    assert qs.extract_final("- ABSTAIN: unsure")["no_final_line"]
    assert qs.extract_final("I will ABSTAIN: unsure")["no_final_line"]
    row = qs.score_question(_q([_n("n1", "rate", "5%")]), "ABSTAIN: unsure")
    assert row["cell"] == "N3"


# ── 15. prose refusal ─────────────────────────────────────────────────
def test_prose_refusal_flag_pass():
    row = qs.score_question(_q([_n("n1", "rate", "5%")]), "I cannot answer this from the material.")
    assert row["prose_refusal"] and row["cell"] == "N2" and row["cell_sensitivity"] == "N3"
    row = qs.score_question(_q([], should_abstain=True), "I don’t know.")
    assert row["prose_refusal"] and row["cell"] == "N4" and row["cell_sensitivity"] == "N5"


def test_prose_refusal_flag_fail():
    assert not qs.extract_final("ANSWER: 5%")["prose_refusal"]
    assert not qs.extract_final("I cannot answer.\nABSTAIN: unsure")["prose_refusal"]


# ── 16. no final line (D1) ────────────────────────────────────────────
def test_no_final_line_answered_wrong():
    row = qs.score_question(_q([_n("n1", "rate", "5%")]), "The rate is 5%.")
    assert row["no_final_line"] and row["nuggets"][0]["state"] == "wrong"
    assert row["nuggets"][0]["flags"]["forced"] == "no_final_line" and row["cell"] == "N2"


def test_no_final_line_should_abstain_is_n4():
    row = qs.score_question(_q([], should_abstain=True), "Some prose with no marker.")
    assert row["no_final_line"] and row["cell"] == "N4"


def test_final_line_present_not_flagged():
    assert not qs.extract_final("ANSWER: 5%")["no_final_line"]


# ── 17. last line wins ────────────────────────────────────────────────
def test_last_line_wins_pass():
    row = qs.score_question(_q([_n("n1", "rate", "11%")]), "ANSWER: 10%\nthinking\nANSWER: 11%")
    assert row["final_value"] == "11%" and row["cell"] == "N1"


def test_last_line_wins_fail():
    row = qs.score_question(_q([_n("n1", "rate", "10%")]), "ANSWER: 10%\nthinking\nANSWER: 11%")
    assert row["cell"] == "N2"
    row = qs.score_question(_q([_n("n1", "rate", "10%")]), "ANSWER: 10%\nABSTAIN: unsure")
    assert row["cell"] == "N3"


# ── 18-22. aggregate metrics on a hand-computed tiny matrix ───────────
def _matrix_rows():
    """N1=3, N2=2, N3=1, N4=2, N5=2 (N=10), one rate nugget per should-answer
    question, no nuggets on should-abstain questions."""
    rate = [_n("n1", "rate", "5%")]
    rows = []
    for i in range(3):
        rows.append(qs.score_question(_q(rate, qid=f"a{i}"), "ANSWER: 5%"))
    for i in range(2):
        rows.append(qs.score_question(_q(rate, qid=f"b{i}"), "ANSWER: 6%"))
    rows.append(qs.score_question(_q(rate, qid="c0"), "ABSTAIN: unsure"))
    for i in range(2):
        rows.append(qs.score_question(_q([], should_abstain=True, qid=f"d{i}"), "ANSWER: 5%"))
    for i in range(2):
        rows.append(qs.score_question(_q([], should_abstain=True, qid=f"e{i}"), "ABSTAIN: none"))
    return rows


def test_matrix_cells():
    c = qs.confusion(_matrix_rows())
    assert (c["N1"], c["N2"], c["N3"], c["N4"], c["N5"], c["N"]) == (3, 2, 1, 2, 2, 10)


def test_wen_metrics_exact():
    m = qs.aggregate(_matrix_rows())["metrics"]
    assert m["accuracy"] == Fraction(5, 10)
    assert m["abstention_precision"] == Fraction(2, 3)
    assert m["abstention_recall"] == Fraction(2, 4)
    assert m["abstention_f1"] == Fraction(4, 7)
    assert m["coverage"] == Fraction(7, 10)
    assert m["abstention_rate"] == Fraction(3, 10)
    assert m["arsp"] == Fraction(1, 6)
    assert m["r_acc"] == Fraction(3, 7)
    assert m["effective_reliability"] == Fraction(-1, 10)
    assert m["nugget_coverage"] == Fraction(5, 6)
    assert m["nugget_precision"] == Fraction(3, 5)


def test_wen_metrics_not_floats():
    m = qs.aggregate(_matrix_rows())["metrics"]
    assert all(v is None or isinstance(v, Fraction) for v in m.values())
    assert m["accuracy"] != Fraction(4, 10)


def test_recall_uses_n4_plus_n5():
    m = qs.aggregate(_matrix_rows())["metrics"]
    assert m["abstention_recall"] == Fraction(2, 2 + 2)


def test_recall_not_printed_typo_formula():
    m = qs.aggregate(_matrix_rows())["metrics"]
    assert m["abstention_recall"] != Fraction(2, 2 + 2 + 2)        # N5/(N2+N4+N5)


def test_none_on_zero_denominators():
    rows = [qs.score_question(_q([_n("n1", "rate", "5%")]), "ANSWER: 5%")]      # one N1 only
    agg = qs.aggregate(rows)
    m, why = agg["metrics"], agg["none_reasons"]
    assert m["abstention_precision"] is None and why["abstention_precision"] == "denominator N3+N5 = 0"
    assert m["abstention_recall"] is None and why["abstention_recall"] == "denominator N4+N5 = 0"
    assert m["abstention_f1"] is None and m["version_accuracy"] is None
    empty = qs.aggregate([])["metrics"]
    assert empty["accuracy"] is None and empty["nugget_phi_1"] is None


def test_zero_value_is_not_none():
    rows = [qs.score_question(_q([_n("n1", "rate", "5%")]), "ANSWER: 6%")]      # one N2
    m = qs.aggregate(rows)["metrics"]
    assert m["accuracy"] == 0 and m["accuracy"] is not None
    assert m["arsp"] == 0 and m["arsp"] is not None


def test_er_sign_positive():
    rate = [_n("n1", "rate", "5%")]
    rows = [qs.score_question(_q(rate, qid=f"p{i}"), "ANSWER: 5%") for i in range(3)]
    rows.append(qs.score_question(_q(rate, qid="w"), "ANSWER: 6%"))
    assert qs.aggregate(rows)["metrics"]["effective_reliability"] == Fraction(2, 4)


def test_er_sign_negative():
    assert qs.aggregate(_matrix_rows())["metrics"]["effective_reliability"] < 0


def test_phi_question_c1_c10():
    m = qs.aggregate(_matrix_rows())["metrics"]
    assert m["question_phi_1"] == Fraction(3 - 4, 10)
    assert m["question_phi_10"] == Fraction(3 - 40, 10)


def test_phi_nugget_c1_c10():
    m = qs.aggregate(_matrix_rows())["metrics"]
    assert m["nugget_phi_1"] == Fraction(3 - 2, 6)
    assert m["nugget_phi_10"] == Fraction(3 - 20, 6)


def test_phi_nugget_partial_question():
    row = qs.score_question(_q(_TWO), "ANSWER: n1=12%; n2=Rs 39,000")       # 1 correct, 1 wrong, k=2
    m = qs.aggregate([row])["metrics"]
    assert m["nugget_phi_1"] == Fraction(0, 2)
    assert m["nugget_phi_10"] == Fraction(1 - 10, 2)
    assert m["question_phi_10"] == Fraction(-10, 1)


def test_phi_abstention_scores_zero():
    m = qs.aggregate([qs.score_question(_q([], should_abstain=True), "ABSTAIN: x")])["metrics"]
    assert m["question_phi_1"] == 0 and m["question_phi_10"] == 0


def test_version_accuracy():
    rows = [qs.score_question(_q([_SEC], qid="v1"), "ANSWER: section 901 of the 2025 Act"),
            qs.score_question(_q([_SEC], qid="v2"), "ANSWER: section 999 of the 2025 Act"),
            qs.score_question(_q([_SEC], qid="v3"), "ANSWER: section 901 of the 1961 Act"),
            qs.score_question(_q([_SEC], qid="v4"), "ANSWER: section 901")]
    assert qs.aggregate(rows)["metrics"]["version_accuracy"] == Fraction(2, 4)
    assert qs.aggregate(rows, "lenient_act")["metrics"]["version_accuracy"] == Fraction(3, 4)


# ── 23. gold validation and the sealed-test guard ─────────────────────
def _write_jsonl(rows):
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return path


def test_sealed_test_split_refused():
    path = _write_jsonl([_q([_n("n1", "rate", "5%")], split="test")])
    try:
        assert _raises(qs.load_gold, path)
        assert len(qs.load_gold(path, allow_test=True)) == 1
    finally:
        os.remove(path)


def test_gold_validation_pass():
    qs.validate_gold_item(_q([_n("n1", "rate", "5%"),
                              _n("n2", "section", "section 901", section_depth="section", act="2025")]))


def test_gold_validation_fail():
    bad = _q([_n("n1", "rate", "5%")])
    bad["stratum"] = "trivia"
    assert _raises(qs.validate_gold_item, bad)
    assert _raises(qs.validate_gold_item, _q([_n("n1", "date", "sometime in April")]))
    assert _raises(qs.validate_gold_item, _q([_n("n1", "rate", "5%", match="tolerance")]))
    assert _raises(qs.validate_gold_item, _q([]))                         # should-answer with no nugget
    assert _raises(qs.validate_gold_item, _q([_n("n1", "section", "section 901")]))   # no depth


# ── 24. fixture and CLI ───────────────────────────────────────────────
def test_fixture_is_synthetic_and_valid():
    items = qs.load_gold(FIXTURE)
    assert 10 <= len(items) <= 20
    for it in items:
        assert it["synthetic"] is True and it["question"].startswith("SYNTHETIC:")
        assert it["split"] == "dev"


def test_cli_end_to_end():
    fd, out = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        proc = subprocess.run([sys.executable, SCORER, "--gold", FIXTURE, "--responses", FIXTURE,
                               "--out", out], capture_output=True, text=True, encoding="utf-8")
        assert proc.returncode == 0, proc.stderr
        rep = json.load(open(out, encoding="utf-8"))
        assert rep["scorer_sha256"] == hashlib.sha256(open(SCORER, "rb").read()).hexdigest()
        assert rep["n"] == len(rep["rows"]) == 18
        assert set(rep["aggregates"]) == {"primary", "sensitivity", "lenient_act"}
        cells = rep["aggregates"]["primary"]["cells"]
        assert (cells["N1"], cells["N2"], cells["N3"], cells["N4"], cells["N5"]) == (8, 6, 1, 2, 1)
    finally:
        os.remove(out)


def test_cli_missing_response_exits_nonzero():
    gold = _write_jsonl([_q([_n("n1", "rate", "5%")], qid="only")])
    resp = _write_jsonl([{"qid": "other", "response": "ANSWER: 5%"}])
    fd, out = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        assert qs.main(["--gold", gold, "--responses", resp, "--out", out]) == 2
    finally:
        for p in (gold, resp, out):
            os.remove(p)
