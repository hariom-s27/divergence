"""Tests for divergence/statute_sources.py (P09 Part C0). INVENTED text only; no real law text, no network."""
import json

import pytest

from divergence import statute_sources as ss

TITLE_ACT = """No. 3] NEW DELHI, TUESDAY, MAY 4, 2099/VAISAKHA 14, 2021 (SAKA)
MINISTRY OF LAW AND JUSTICE
The following Act of Parliament received the assent of the President on the
2nd May, 2099 and is hereby published for general information:—
THE ZETA LEVY ACT, 2099
NO. 5 OF 2099
[2nd May, 2099.]
An Act to invent a levy.
1. (1) This Act may be called the Zeta Levy Act, 2099.
CG-DL-E-04052099-999001
"""

TITLE_BILL_FIRST = """THE OMEGA (AMENDMENT) ACT, 2099
The following Act of Parliament received the assent of the President on the 9th June, 2099 and
Bill No. 77-F of 2099
No. 12 of 2099
"""

TITLE_ORD = """THE ZETA (AMENDMENT) ORDINANCE, 2099
NO 2 OF 2099
Promulgated by the President in the Fiftieth Year.
New Delhi, the 7th July, 2099
WHEREAS ... the President is pleased to promulgate the following Ordinance:-
1. (1) This Ordinance may be called the Zeta (Amendment) Ordinance, 2099.
"""

CORR_TABLE = """MINISTRY OF LAW AND JUSTICE
New Delhi, the 3rd March, 2099
CORRIGENDA
In the Zeta Levy Act, 2099 (5 of 2099) as published in the Gazette,
Page Line(s) For Read
7 4 “invented word” “invented words”
12 30 “first part of a wrapped “short read”
cell”
19 2-3 “short for” “a read that
wraps”
CORRIGENDA
The Omega Act, 2099 (6 of 2099) as published,—
40 1 “alpha” “beta”
"""

CORR_PROSE = """CORRIGENDUM
In the Zeta Levy Act, 2099 (5 of 2099), published in the Gazette, at page 21, in line 9, for “invnted”
read “invented”.
"""


def test_title_facts_act_number_ignores_issue_header_and_reads_assent():
    f = ss.title_facts([TITLE_ACT])
    assert (f["act_no"], f["act_year"]) == (5, 2099)          # not the issue header 'No. 3]'
    assert f["assent_date"] == "2099-05-02" and f["bracket_date"] == "2099-05-02"
    assert f["short_title"] == "Zeta Levy Act, 2099"
    assert f["gazette_id"] == "CG-DL-E-04052099-999001" and f["gazette_date"] == "2099-05-04"
    assert f["kind_seen"] == "act"


def test_title_facts_assent_date_split_across_lines():
    f = ss.title_facts(["The following Act received the assent of the President on the\n2nd\nMay, 2099 and is"])
    assert f["assent_date"] == "2099-05-02"


def test_title_facts_skips_bill_number():
    f = ss.title_facts([TITLE_BILL_FIRST])
    assert (f["act_no"], f["act_year"]) == (12, 2099)
    assert f["assent_date"] == "2099-06-09"


def test_title_facts_ordinance_promulgation_date():
    f = ss.title_facts([TITLE_ORD])
    assert f["kind_seen"] == "ordinance"
    assert (f["act_no"], f["act_year"]) == (2, 2099)
    assert f["promulgated_on"] == "2099-07-07" and f["assent_date"] is None


def test_title_facts_ordinance_date_without_comma_and_numbered_short_title():
    f = ss.title_facts([TITLE_ORD.replace("New Delhi, the", "New Delhi the")])
    assert f["promulgated_on"] == "2099-07-07"
    g = ss.title_facts(["1. (1) This Act may be called the Zeta (No. 2) Act, 2099.\n(2) Save as"])
    assert g["short_title"] == "Zeta (No. 2) Act, 2099"


def test_title_facts_notification_number_on_last_page():
    f = ss.title_facts(["MINISTRY OF ZETA\nNOTIFICATION\nInvented rules.", "more", "[Notification No. 9/2099/F. No. 1]"])
    assert f["kind_seen"] == "notification" and f["notification_no"] == "9/2099"


def test_title_facts_corrigendum_targets():
    f = ss.title_facts([CORR_TABLE])
    assert f["kind_seen"] == "corrigendum"
    assert f["corrigendum_targets"] == ["Zeta Levy Act, 2099 (5 of 2099)", "Omega Act, 2099 (6 of 2099)"]
    assert f["gazette_date"] == "2099-03-03"


def test_text_layer_threshold():
    assert ss.text_layer(["a", "b", " ", "c"]) == (3, 4, 75.0)
    assert ss.text_layer([]) == (0, 0, 0.0)


def test_corrigendum_table_rows_with_wrapped_cells_and_blocks():
    items = ss.corrigendum_items([CORR_TABLE])
    got = [(i["target"], i["gazette_page"], i["gazette_lines"], i["for"], i["read"], i["parsed"]) for i in items]
    assert got == [
        ("Zeta Levy Act, 2099 (5 of 2099)", "7", "4", "invented word", "invented words", True),
        ("Zeta Levy Act, 2099 (5 of 2099)", "12", "30", "first part of a wrapped cell", "short read", True),
        ("Zeta Levy Act, 2099 (5 of 2099)", "19", "2-3", "short for", "a read that wraps", True),
        ("Omega Act, 2099 (6 of 2099)", "40", "1", "alpha", "beta", True),
    ]
    assert items[0]["pdf_page"] == 1 and items[0]["pdf_line"] == 6


def test_corrigendum_prose_form():
    items = ss.corrigendum_items([CORR_PROSE])
    assert [(i["gazette_page"], i["gazette_lines"], i["for"], i["read"]) for i in items] == [
        ("21", "9", "invnted", "invented")]


def test_find_hits_whitespace_fold_and_boundaries():
    pages = ["see section 5 and section 56 and\nsection   5(1)", "section\n5"]
    hits = ss.find_hits(pages, "section 5")
    assert [(p, ln) for p, ln, _, _ in hits] == [(1, 1), (1, 2), (2, 1)]   # 'section 56' is not a hit
    assert ss.find_hits(pages, "ection 5") == []                           # letter touches the start


def test_e2_label_excludes_contained_hits():
    pages = ["alpha 9 and beta 4 here; alpha 9 alone"]
    old = ss.find_hits(pages, "alpha 9 and beta 4")
    new = ss.find_hits(pages, "alpha 9")
    label, old_only, new_only = ss.e2_label(old, new)
    assert (label, len(old_only), len(new_only)) == ("both", 1, 1)
    assert ss.e2_label([], [])[0] == "neither"
    assert ss.e2_label(old, [])[0] == "old"


def test_section_at_uses_preceding_candidate_start():
    pos = [((2, 1), "1"), ((3, 10), "2"), ((5, 1), "3")]
    assert ss.section_at(pos, (9, 1), 3, 9) == "s.1"
    assert ss.section_at(pos, (9, 1), 3, 10) == "s.2"
    assert ss.section_at(pos, (9, 1), 9, 4) == "Schedules"
    assert ss.section_at(pos, None, 1, 1) == "front matter"


def test_check_sources_reports_missing_and_changed_fields(tmp_path):
    row = {"key": "zz_1", "file": "zz.pdf", "kind_expected": "act", "act_no": 5, "act_year": 2099,
           "assent_date": "2099-05-02", "gazette_id": None, "gazette_date": None, "sha256": "ab", "pages": 2,
           "text_layer_pct": 100.0, "source_kind": "gazette"}
    good = {"key": "zz_1", "item": "Invented", "where": "x", **ss.sources_fields(row)}
    p = tmp_path / "SOURCES.json"
    p.write_text(json.dumps({"items": [], "manual": [good]}), encoding="utf-8")
    assert ss.check_sources([row], p) == []
    bad = dict(good, pages=3)
    del bad["sha256"]
    p.write_text(json.dumps({"items": [], "manual": [bad]}), encoding="utf-8")
    assert sorted(m[1] for m in ss.check_sources([row], p)) == ["pages", "sha256"]
    p.write_text(json.dumps({"items": [], "manual": []}), encoding="utf-8")
    assert ss.check_sources([row], p) == [("zz_1", "-", "entry missing", "-")]


def test_blank_pdf_has_no_text_layer(tmp_path):
    pypdf = pytest.importorskip("pypdf")
    w = pypdf.PdfWriter()
    w.add_blank_page(width=200, height=200)
    path = tmp_path / "blank.pdf"
    with open(path, "wb") as f:
        w.write(f)
    assert ss.text_layer(ss.pdf_pages(path))[2] == 0.0 < ss.TEXT_LAYER_MIN
