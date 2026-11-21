"""Tests for divergence/act_parse.py (P09 Part C1). INVENTED text only; no real law text, no network."""
import pytest

from divergence import act_parse as ap
from divergence import statute_extract as se

META = {"key": "zz_2099", "act_no": 9, "act_year": 2099, "assent_date": "2099-03-30", "source_kind": "gazette",
        "item": "Zeta Finance Act, 2099"}

PAGE1 = """REGISTERED NO. DL—(N)04/0007/2003—99xyz
xxxGIDHxxx
xxxGIDExxx
xyz/kkj.k
EXTRAORDINARY
Hkkx  II — [k.M 9
PART II — Section 1
izkf/kdkj
PUBLISHED  BY  AUTHORITY
No. 9]  NEW DELHI, MONDAY, MARCH 30, 2099/CHAITRA 9, 2021 (SAKA)
Separate paging is given to this Part in order that it may be filed as a separate compilation.
THE ZETA FINANCE ACT, 2099
1. (1) This Act may be called the Zeta Finance Act, 2099.
(2) Save as otherwise provided in this Act,—
(a) sections 2 to 5 and 7 shall come into force on the 1st day of April, 2099;
(b) section 6 shall come into force on such date as the Central Government may, by notification in the
Official Gazette, appoint.
2. Income-tax for the year shall be charged under the Income-tax Act, 1961 (hereinafter referred
to as the Income-tax Act) at invented rates.
Short title and
commencement.
CG-DL-E-30032099-999009
"""

PAGE2 = """2 THE GAZETTE OF INDIA EXTRAORDINARY [PART II—
Amendment of
section 7.
3. In section 7 of the Income-tax Act,—
(a) in clause (4), with effect from the 1st day of October, 2099,—
(i) for the word "alpha", the word "beta" shall be substituted;
(ii) the word "gamma" shall be omitted;
(b) in clause (9), for the word "delta", the word "epsilon" shall be substituted and shall be deemed
to have been substituted with effect from the 1st day of April, 2098;
(c) after clause (9), the following clause shall be inserted, namely:—
'(9A) "zeta" means an invented thing used in tests;
(a) of one kind;
(b) of another kind which applies on or after the 1st day of April, 2100;';
(d) in clause (12), the words "theta" shall be rearranged in an invented way;
4. After section 7A of the Income-tax Act, the following section shall be inserted with effect from the
1st day of July, 2099, namely:—
'7B. (1) Any invented person shall do an invented thing.'.
5. In section 3 of the Zeta Levy Act, 2099, for the word "iota", the word "kappa" shall be substituted.
44 of 2099.
"""

PAGE3 = """Sec. 1] THE GAZETTE OF INDIA EXTRAORDINARY 3
6. In section 7 of the Income-tax Act, in clause (20), the word "lambda" shall be omitted.
7. In section 8 of the Income-tax Act, the word "mu" shall be omitted and shall be deemed to have been omitted.
"""

SPINE = {"1961": ["7", "7B", "8"], "2025": []}


@pytest.fixture
def parsed(monkeypatch):
    monkeypatch.setattr(ap, "SPINE", SPINE)
    return ap.parse_instrument("zz_2099", pages=[PAGE1, PAGE2, PAGE3], meta=META, corr=[])


def _row(parsed, eid):
    return next(r for r in parsed["rows"] if r["effect_id"] == eid)


def _rv(parsed, eid):
    return next(r for r in parsed["review"] if r["effect_id"] == eid)


def test_masthead_running_head_and_margin_notes_stripped():
    cl = ap.clean_instrument([PAGE1, PAGE2, PAGE3])
    texts = [x.text.strip() for x in cl.lines]
    for gone in ("EXTRAORDINARY", "xyz/kkj.k", "Hkkx  II — [k.M 9", "Short title and", "commencement.",
                 "Amendment of", "section 7.", "44 of 2099.", "CG-DL-E-30032099-999009"):
        assert gone not in texts
    assert not any("THE GAZETTE OF INDIA" in t for t in texts)
    assert cl.lines[0].text.startswith("THE ZETA FINANCE ACT")
    assert [x[1] for x in cl.log["running_head"]] == [1, 1]
    assert cl.log["page_mismatch"] == []
    assert next(x for x in cl.lines if x.text.startswith("6.")).printed == 3


def test_devanagari_line_stripped():
    cl = ap.clean_instrument(["सी.जी.-डी.एल.-अ.-99\nBody text line one.\n"])
    assert [x.text for x in cl.lines] == ["Body text line one."]


def test_glued_margin_commencement_is_removed():
    cl = ap.clean_instrument(["x", "2 THE GAZETTE OF INDIA EXTRAORDINARY [Part II—\nShort title and\n"
                              "commencement. 1. ( 1) This Ordinance may be called the Zeta Ordinance, 2099.\n"])
    assert cl.lines[-1].text.startswith("1. ( 1) This Ordinance")


def test_s1_both_wordings_and_ranges():
    s1 = ap.parse_s1("(a) sections 2 to 5, 9 and 12 shall come into force on the 1st day of April, 2099; "
                     "(b) sections 14 to 15, clause (b) of section 20 and section 22 shall be deemed to have come into "
                     "force on the 1st April, 2098; (c) section 6 shall come into force on such date as the Central "
                     "Government may, by notification, appoint.")
    a, b, c = s1["clauses"]
    assert a["sections"] == {"2", "3", "4", "5", "9", "12"} and a["date"] == "2099-04-01"
    assert a["wording"] == "come_into_force"
    assert b["sections"] == {"14", "15", "22"} and b["partial"] == {"20"} and b["date"] == "2098-04-01"
    assert b["wording"] == "deemed_come_into_force"
    assert c["notification"] and c["date"] is None
    w = ap.parse_s1("(2) It shall be deemed to have come into force on the 1st day of April, 2099.")
    assert w["whole"] == {"wording": "deemed_come_into_force", "date": "2099-04-01"}


def test_header_inherited_date(parsed):
    r = _row(parsed, "zz_2099:s3(a)(i)")
    assert (r["commencement_source"], r["wef"], r["operation"]) == ("header_inherited", "2099-10-01", "substitute")
    assert _rv(parsed, "zz_2099:s3(a)(i)")["header_at"] == (2, 5)
    assert _row(parsed, "zz_2099:s3(a)(ii)")["operation"] == "omit"


def test_item_deemed_date_before_assent_is_deemed_from(parsed):
    r = _row(parsed, "zz_2099:s3(b)")
    assert (r["commencement_source"], r["wef"], r["deemed_from"]) == ("item_deemed", "2098-04-01", "2098-04-01")
    assert r["assent_date"] == "2099-03-30"


def test_s1_default_and_in_text_trigger_not_commencement(parsed):
    r = _row(parsed, "zz_2099:s3(c)")
    assert (r["commencement_source"], r["wef"], r["operation"]) == ("s1_default", "2099-04-01", "insert")
    assert r["applicability_note_present"] == "yes"            # 'on or after' inside the inserted words
    assert "s1:come_into_force" in _rv(parsed, "zz_2099:s3(c)")["flags"]


def test_inserted_block_markers_are_not_sub_items(parsed):
    ids = [r["effect_id"] for r in parsed["rows"]]
    assert "zz_2099:s3(c)(a)" not in ids and "zz_2099:s3(c)(b)" not in ids


def test_unknown_wording_flagged(parsed):
    r = _row(parsed, "zz_2099:s3(d)")
    assert r["operation"] == "other"
    assert "no_verb" in _rv(parsed, "zz_2099:s3(d)")["flags"]


def test_after_section_targets_inserted_heading(parsed):
    r = _row(parsed, "zz_2099:s4")
    assert (r["target_section"], r["operation"], r["wef"]) == ("7B", "insert", "2099-07-01")


def test_other_act_section_ignored(parsed):
    assert not any(r["effect_id"].startswith("zz_2099:s5") for r in parsed["rows"])


def test_notification_range_is_applicability_unclear(parsed):
    r = _row(parsed, "zz_2099:s6")
    assert r["commencement_source"] == "notification" and r["wef"] == ""
    assert {"applicability_unclear", "MANUAL_NEEDED"} <= set(_rv(parsed, "zz_2099:s6")["flags"])


def test_deemed_without_date_is_unknown(parsed):
    r = _row(parsed, "zz_2099:s7")
    assert r["commencement_source"] == "unknown" and r["wef"] == ""
    assert "deemed_without_date" in _rv(parsed, "zz_2099:s7")["flags"]


def test_chapter_substitution_targets_inner_sections(monkeypatch):
    monkeypatch.setattr(ap, "SPINE", {"1961": ["9B"], "2025": []})
    page = ("1. (1) This Act may be called the Zeta Act, 2099.\n(2) It shall come into force on the 1st day of "
            "April, 2099.\n2. In the Income-tax Act, 1961 (hereinafter referred to as the Income-tax Act), nothing.\n"
            "3. For Chapter IX-B of the Income-tax Act, the following Chapter shall be substituted, namely:—\n"
            "'CHAPTER IX-B\n9B. In this Chapter, an invented rule applies.\n9BA. Another invented rule.'.\n")
    r = ap.parse_instrument("zz_2099", pages=[page], meta=META, corr=[])
    assert [(x["effect_id"], x["target_section"], x["operation"]) for x in r["rows"]] == [
        ("zz_2099:s3", "9B", "substitute")]


def test_part_binding_switches_target_act(monkeypatch):
    monkeypatch.setattr(ap, "SPINE", {"1961": ["5"], "2025": ["5"]})
    page = ("1. (1) This Act may be called the Zeta Act, 2099.\n(2) It shall come into force on the 1st day of "
            "April, 2099.\nA.–– Income-tax under the Income-tax Act, 1961\n"
            "2. In section 5 of the Income-tax Act, 1961 (hereafter in this Part referred to as the Income-tax Act),"
            " the word \"nu\" shall be omitted.\n3. In section 5 of the Income-tax Act, the word \"xi\" shall be "
            "omitted.\nB.–– Income-tax under the Income-tax Act, 2025\n4. In section 5 of the Income-tax Act, 2025 "
            "(hereafter in this Part referred to as the Income-tax Act), the word \"pi\" shall be omitted.\n"
            "5. In section 5 of the Income-tax Act, the word \"rho\" shall be omitted.\n")
    r = ap.parse_instrument("zz_2099", pages=[page], meta=META, corr=[])
    assert [(x["effect_id"], x["target_act"]) for x in r["rows"]] == [
        ("zz_2099:s2", "1961"), ("zz_2099:s3", "1961"), ("zz_2099:s4", "2025"), ("zz_2099:s5", "2025")]


def test_marker_kinds_and_sequence():
    assert ap._marker_kind("i", {"alpha": "h"}) == "alpha"
    assert ap._marker_kind("i", {"alpha": "b"}) == "roman"
    assert ap._marker_kind("I", {}) == "ROMAN" and ap._marker_kind("aa", {}) == "alpha"
    assert ap._successor("roman", "iv") == "v" and ap._successor("ALPHA", "Z") == "AA"


def test_quote_sha_is_whitespace_folded():
    assert ap.quote_sha256("an  invented\n quote ") == ap.quote_sha256("an invented quote")
    assert ap.quote_sha256("an invented quote") != ap.quote_sha256("an invented quotes")


def test_quote_truncated_flag(monkeypatch):
    monkeypatch.setattr(ap, "SPINE", {"1961": ["5"], "2025": []})
    long = "\n".join(f"invented line {k} of a long operative sentence" for k in range(10))
    page = ("1. (1) This Act may be called the Zeta Act, 2099.\n(2) It shall come into force on the 1st day of "
            "April, 2099.\n2. In section 5 of the Income-tax Act, 1961, the words\n" + long
            + "\nshall be omitted.\n")
    r = ap.parse_instrument("zz_2099", pages=[page], meta=META, corr=[])
    assert "quote_truncated" in r["review"][0]["flags"]


def test_corrigendum_flag_needs_page_and_words(monkeypatch, parsed):
    monkeypatch.setattr(ap, "SPINE", SPINE)
    corr = [{"gazette_page": "2", "for": "\"delta\"", "read": "\"delt\"", "parsed": True},
            {"gazette_page": "3", "for": "\"delta\"", "read": "\"delt\"", "parsed": True}]
    r = ap.parse_instrument("zz_2099", pages=[PAGE1, PAGE2, PAGE3], meta=META, corr=corr)
    flags = {x["effect_id"]: x["corrigendum_flag"] for x in r["rows"]}
    assert flags["zz_2099:s3(b)"] == "yes" and flags["zz_2099:s3(a)(i)"] == "no"


def test_alias_number_year_collision():
    # Two invented Acts with the same number in different years must not share a key
    assert se.normalise_act("Act No. 8 of 2023") != se.normalise_act("Act No. 8 of 2024")


def test_csv_never_overwritten_and_owner_columns_kept(tmp_path):
    p = tmp_path / "EFFECTS.csv"
    regen = tmp_path / "regen"
    cols = ["effect_id", "operation", "owner_ok", "owner_note"]
    ap.write_never_overwrite(p, [{"effect_id": "x:s1", "operation": "omit"}], cols, "effect_id", regen_dir=regen)
    rows = ap.read_csv(p)
    rows[0]["owner_ok"], rows[0]["owner_note"] = "yes", "checked"
    p.write_text(ap.csv_text(rows, cols), encoding="utf-8")
    before = p.read_bytes()
    alt, msg = ap.write_never_overwrite(p, [{"effect_id": "x:s1", "operation": "insert"},
                                            {"effect_id": "x:s2", "operation": "omit"}], cols, "effect_id",
                                        regen_dir=regen)
    assert p.read_bytes() == before and alt.parent == regen
    new = {r["effect_id"]: r for r in ap.read_csv(alt)}
    assert new["x:s1"]["owner_ok"] == "yes" and new["x:s1"]["operation"] == "insert"
    assert msg[1].startswith("MERGE PREVIEW: unchanged 0, changed 1, added 1, removed 0")


def test_merge_preview_carry_filter_and_lost_owner_values():
    old = [{"k": "a", "v": "1", "cat": "effect_start", "owner_ok": ""},
           {"k": "b", "v": "1", "cat": "procedural", "owner_ok": "yes"}]
    merged, lines = ap.merge_preview(old, [{"k": "a", "v": "1"}], "k", ["k", "v", "cat", "owner_ok"],
                                     ("cat", "owner_ok"), carry=lambda r, c: c != "cat" or r[c] == "procedural")
    assert merged[0]["cat"] == "" and any("not an owner value" in x for x in lines)
    assert any(x.startswith("  - b OWNER VALUES WOULD BE LOST") for x in lines)


def test_owner_split_replaces_row():
    res = {"rows": [{"effect_id": "x:s4(c)", "operation": "other", "commencement_source": "item_deemed", "wef": "2100-04-01",
                     "assent_date": "2099-03-30", "owner_note": ""}],
           "review": [{"effect_id": "x:s4(c)", "flags": ["multi_verb"]}]}
    split = {"date": "2099-12-01", "wef": "2100-04-01", "operations": ["renumber", "insert"], "owner_note": "owner reading"}
    ap.apply_owner_splits(res, {"x:s4(c)": split})
    assert [(r["effect_id"], r["operation"], r["wef"], r["owner_note"]) for r in res["rows"]] == [
        ("x:s4(c)/renumber", "renumber", "2100-04-01", "owner reading"),
        ("x:s4(c)/insert", "insert", "2100-04-01", "owner reading")]
    assert res["review"][0]["flags"] == ["owner_split 2099-12-01"]
