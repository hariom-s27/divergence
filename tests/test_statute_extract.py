"""Tests for divergence/statute_extract.py. All text is INVENTED (FAKE FIXTURE - NOT LAW); no PDFs, no network."""
import hashlib
import json

import pytest

from divergence import statute_extract as se

FOOTER = "Income Tax Department\nMinistry of Finance, Government of India"
DL = "Downloaded/Printed on 01/02/2099, 9:15 am from www.incometaxindia.gov.in Page 1 of 2"


def view(*pages):
    cleaned = se.clean_pages(list(pages))
    return cleaned, se.find_starts(cleaned.lines)


def body(pages, number):
    cleaned, starts = view(*pages)
    return se.extract_section(cleaned, starts, number)


# ---------------------------------------------------------------- R1 locate

def test_heading_based_start_is_found():
    r = body(["Invented heading.\n7. (1) Fake text of section seven.\nOther heading.\n8. Fake eight."], "7")
    assert r["status"] == "FOUND" and r["heading"] == "Invented heading."
    assert r["body"] == "7. (1) Fake text of section seven.\n"


@pytest.mark.parametrize("line", ["446 . Fake text after a spaced dot.", "446.", "446. Fake text."])
def test_spaced_dot_and_dot_at_line_end(line):
    r = body([f"Fake penalty heading.\n{line}\nmore fake words.\nNext heading.\n447. Fake."], "446")
    assert r["status"] == "FOUND" and r["body"].startswith("446")


def test_table_row_number_is_not_a_section_start():
    page = ("Definitions.\n2. In this fake Act,—\nTABLE\nA B C\n1. Fake row one.\n2. Fake row two.\n"
            "3. Fake row three.\nExplanation.—Fake.\nTax year.\n3. Fake text of section three.\n")
    cleaned, starts = view(page)
    assert [s.number for s in starts] == ["2", "3"]
    r = se.extract_section(cleaned, starts, "3")
    assert r["status"] == "FOUND" and r["body"] == "3. Fake text of section three.\n"


def test_footnote_line_is_not_a_section_start():
    page = "Fake heading.\n92. Fake text.\n92. Sub. by Act No. 99 of 2099, w.e.f. 1-1-2099."
    cleaned, starts = view(page)
    assert len(starts) == 1 and cleaned.notes[1] == ["92. Sub. by Act No. 99 of 2099, w.e.f. 1-1-2099."]


def test_numbered_line_without_heading_is_not_a_start():
    cleaned, starts = view("Fake text that runs on and\n5. is not a heading start\n")
    assert starts == []


def test_two_candidates_are_unresolved_never_picked():
    r = body(["Fake A.\n5. Fake one.\n", "Fake B.\n5. Fake two.\n"], "5")
    assert r["status"] == "UNRESOLVED" and [c["page_1based"] for c in r["candidates"]] == [1, 2]


def test_not_found():
    assert body(["Fake A.\n5. Fake one.\n"], "6")["status"] == "NOT_FOUND"


def test_letter_suffix_does_not_match_plain_number():
    cleaned, starts = view("Fake heading.\n2A. Fake two A.\n")
    assert se.locate(cleaned.lines, starts, "2")["status"] == "NOT_FOUND"


def test_wrapped_and_bracketed_heading():
    r = body(["[Fake obligation to furnish information on transaction of\ninvented asset.\n285ZZ.\n(1) Fake.\n"], "285ZZ")
    assert r["status"] == "FOUND"
    assert r["heading"] == "Fake obligation to furnish information on transaction of invented asset."   # [Q2]
    assert r["body"].startswith("[285ZZ.") and r["heading_bracket_moved_to_body"] is True


def test_no_space_between_dot_and_subsection():
    r = body(["[Fake obligation heading.\n285ZZ.(1) Fake reporting text.\nNext fake.\n286. Fake."], "285ZZ")
    assert r["status"] == "FOUND" and r["body"] == "[285ZZ.(1) Fake reporting text.\n"


def test_heading_is_shortest_and_skips_body_chapter_and_part_lines():
    page = ("Fake body line without a full stop\n[Explanation 2. — Fake clarification that wraps\nwhether fake or not\n"
            "[Fake payment heading.\n194ZZ. (1) Fake.\nCHAPTER XIV\nFAKE PROCEDURE\nFake return.\n139. Fake.\n"
            "F.—Fake part heading\nFake other sources.\n56. Fake.")
    cleaned, starts = view(page)
    heads = {s.number: s.heading for s in starts}
    assert heads == {"194ZZ": "[Fake payment heading.", "139": "Fake return.", "56": "Fake other sources."}


def test_no_section_starts_inside_schedules_region():
    page = "Fake heading.\n2. Fake definitions.\nSCHEDULE I\n[See section 2]\nFake schedule item.\n2. Fake schedule row."
    cleaned, starts = view(page)
    assert [(s.number, cleaned.lines[s.idx].text) for s in starts] == [("2", "2. Fake definitions.")]


def test_table_rows_with_nbsp_indent_and_unmarked_tables_are_not_starts():
    page = ("Fake expenses.\n36. (1) Fake,—\nTABLE\n  Sl. No. Fake Fake\n  A B C\n"
            "  1. Fake person. Fake relative.\n  2. Fake company. Fake director.\n"
            "Fake distance from limits\nA B C\n1. More than 10 fake. Two fake.\n2. More than 100 fake. Six fake.\n")
    cleaned, starts = view(page)
    assert [s.number for s in starts] == ["36"]
    marks, _ = se.table_marks(cleaned.lines)
    assert sorted(m[2] for m in marks.values() if m[0] == "row") == [1, 2]


def test_numbered_part_heading_is_not_a_start():
    cleaned, starts = view("Fake schedules.\n2. -Fake income of fake organisation\nFake tax heading.\n2. —Fake part.\n")
    assert starts == []


def test_footer_with_short_us_date_is_furniture():
    dl = "Downloaded/Printed on 5/22/99, 4:32 PM from www.incometaxindia.gov.in"
    cleaned = se.clean_pages([f"Fake heading.\n3. Fake.\nmore.\n{dl}\nIncome Tax Department"])
    assert dl not in [ln.text for ln in cleaned.lines]


# ---------------------------------------------------------------- R2 end

def test_section_ends_at_next_higher_section_and_crosses_pages():
    r = body(["Fake heading.\n10. Fake start\n", "continues on page two.\nNext fake.\n10A. Fake."], "10")
    assert r["pages_1based"] == [1, 2] and r["body"] == "10. Fake start\ncontinues on page two.\n"


def test_section_ends_at_chapter_line_and_at_end_of_file():
    r = body(["Fake heading.\n139. Fake return text.\nCHAPTER I\nPRELIMINARY\nShort title.\n1. Fake."], "139")
    assert r["body"] == "139. Fake return text.\n"
    r2 = body(["Fake heading.\n9. Last fake section."], "9")
    assert r2["body"] == "9. Last fake section.\n"


def test_out_of_order_section_at_front_is_found():
    pages = ["CHAPTER XIV\nFAKE PROCEDURE\nFake return.\n139. Fake displaced text.",
             "FAKE ACT, 2099\nCHAPTER I\nShort title.\n1. Fake.", "Fake disclosure.\n138. Fake.\nFake number.\n139A. Fake."]
    r = body(pages, "139")
    assert r["status"] == "FOUND" and r["pages_1based"] == [1] and r["body"] == "139. Fake displaced text.\n"


def test_lower_numbered_list_inside_section_does_not_end_it():
    r = body(["Fake heading.\n50. Fake text with list.\nFake item heading.\n1. Fake inner item.\nNext fake.\n51. Fake."], "50")
    assert "1. Fake inner item." in r["body"] and "51." not in r["body"]


# ---------------------------------------------------------------- R3 furniture + footnotes

def test_footer_removed_only_at_page_edge():
    page = f"Fake heading.\n3. Fake text.\nIncome Tax Department\nfake middle line.\nfake.\nend.\n{FOOTER}\n{DL}"
    cleaned = se.clean_pages([page])
    texts = [ln.text for ln in cleaned.lines]
    assert "Income Tax Department" in texts           # mid-page: kept
    assert DL not in texts and texts[-1] == "end."
    assert len(cleaned.furniture) == 3


def test_bare_page_number_removed_at_edge_only():
    cleaned = se.clean_pages(["12\nFake heading.\n3. Fake.\n45\nfake tail.\nmore.\nlast."])
    texts = [ln.text for ln in cleaned.lines]
    assert "12" not in texts and "45" in texts


def test_footnote_block_moved_verbatim_and_inline_marker_dropped():
    page = ("Fake heading.\n7. Fake 1[inserted words]* and 2text.\n"
            "1. Ins. by Act No. 99 of 2099, w.e.f. 1-4-2099.\n2. Words \"fake\" omtt. by Act No. 98.\n" + FOOTER)
    r = body([page], "7")
    assert r["body"] == "7. Fake [inserted words]* and 2text.\n"     # P09-41: '1[' matches footnote 1; '2text' is no marker
    assert r["amendment_note"] == ("[page_1based 1] 1. Ins. by Act No. 99 of 2099, w.e.f. 1-4-2099.\n"
                                   "[page_1based 1] 2. Words \"fake\" omtt. by Act No. 98.")


# ---------------------------------------------------------------- R5 tables

TABLE_PAGE = ("Tax on fake incomes.\n194. (1) Fake text below,—\nTABLE\nSl.\nNo.\nA B C\n"
              "1. Fake person. Fake winnings from—\n(a) fake lottery; or\n2. Fake row two\ncontinued here.\n"
              "3. Fake row three.\n4. Fake capital market\n  (i)  Fake income in respect of\n  (ii)  Fake distributed income\n"
              "(2) Fake sub-section after the table.\nNext fake.\n195. Fake.")


def test_integer_rows_prefixed_roman_items_unlabelled():
    r = body([TABLE_PAGE], "194")
    lines = r["body"].splitlines()
    assert "[Table 1 Sl. 4] 4. Fake capital market" in lines
    assert "(i) Fake income in respect of" in lines                  # P09-31: no label, own text kept
    assert "(ii) Fake distributed income" in lines
    assert r["table_rows"] == 4 and r["unresolved"] == []


def test_table_rows_are_never_joined_into_one_line():
    r = body([TABLE_PAGE], "194")
    lines = r["body"].splitlines()
    rows = [ln for ln in lines if ln.startswith("[Table 1 Sl.")]
    assert [ln.split("]")[0] for ln in rows] == ["[Table 1 Sl. 1", "[Table 1 Sl. 2", "[Table 1 Sl. 3", "[Table 1 Sl. 4"]
    i = lines.index("[Table 1 Sl. 2] 2. Fake row two")
    assert lines[i + 1] == "continued here."                          # P09-34: PDF line break kept
    assert all(ln.count("[Table 1 Sl.") == 1 for ln in rows)


def test_table_sl_8_vi():
    rows = "".join(f"{n}. Fake row {n}\n" for n in range(1, 8))
    subs = "".join(f"  ({r})  Fake sub {r}\n" for r in ("i", "ii", "iii", "iv", "v", "vi"))
    r = body([f"Fake TDS.\n393. (1) Fake,—\nTABLE\n{rows}8. Other fake cases\n{subs}Next fake.\n394. Fake."], "393")
    lines = r["body"].splitlines()
    assert "[Table 1 Sl. 8] 8. Other fake cases" in lines and "(vi) Fake sub vi" in lines
    assert "Sl. 8(vi)" not in r["body"]


def test_unindented_roman_in_cell_is_not_a_subrow():
    r = body(["Fake.\n393. Fake,—\nTABLE\n1. Fake row\n(i) fake cell item\nNext fake.\n394. Fake."], "393")
    assert "[Table 1 Sl. 1(i)]" not in r["body"]


def test_non_sequential_number_in_table_is_unresolved():
    r = body(["Fake.\n393. Fake,—\nTABLE\n1. Fake row\n5. fake odd number\nNext fake.\n394. Fake."], "393")
    assert len(r["unresolved"]) == 1 and "non-sequential" in r["unresolved"][0]


# ---------------------------------------------------------------- R4

def test_whitespace_collapse_keeps_characters():
    assert se.normalise(["7.  Fake  text\t here.  "]) == "7. Fake text here.\n"
    assert se.normalise(["“Fake” ₹ 5 and Rs. 6 busi-", "ness."]) == "“Fake” ₹ 5 and Rs. 6 busi-ness.\n"


def test_line_breaks_kept_no_joins():
    texts = ["7. (1) Fake  text that", "wraps here;", "", "(a) fake clause", "continued.",
             "Explanation.—Fake", "Provided that fake."]
    assert se.normalise(texts) == ("7. (1) Fake text that\nwraps here;\n(a) fake clause\ncontinued.\n"
                                   "Explanation.—Fake\nProvided that fake.\n")


def test_deterministic_output():
    a = body([TABLE_PAGE], "194")
    b = body([TABLE_PAGE], "194")
    assert a["sha256"] == b["sha256"] == hashlib.sha256(a["body"].encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- fold (diffs only)

def test_fold_quotes_rupee_nbsp():
    assert se.fold_for_diff("“fake” ‘x’ it’s") == se.fold_for_diff('"fake" \'x\' it\'s')
    assert se.fold_for_diff("₹  50000") == se.fold_for_diff("Rs. 50000") == se.fold_for_diff("Rs 50000")
    assert se.fold_for_diff("a b") == "a b"
    assert se.fold_for_diff("Rsfake officeRs") == "Rsfake officeRs"


def test_fold_keeps_substantive_differences():
    assert se.fold_for_diff("Rs. 50000") != se.fold_for_diff("Rs. 75000")
    assert se.fold_for_diff("fake shall") != se.fold_for_diff("fake may")


def test_fold_is_never_used_on_bodies():
    r = body(["Fake.\n7. “Fake” ₹ 5.\n"], "7")
    assert r["body"] == "7. “Fake” ₹ 5.\n"


# ---------------------------------------------------------------- cache

def test_cache_never_overwritten_and_inconsistent_cache_refused(tmp_path, monkeypatch):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-fake")
    sha = hashlib.sha256(b"%PDF-fake").hexdigest()
    monkeypatch.setattr(se, "pypdf_version", lambda: "9.9.9")
    cache = tmp_path / f"{sha}__pypdf-9.9.9.jsonl"
    cache.write_text(json.dumps({"pdf_sha256": sha, "pypdf_version": "9.9.9", "pages": 1}) + "\n"
                     + json.dumps({"page": 1, "text": "FAKE"}) + "\n", encoding="utf-8")
    assert se.load_pages(pdf, cache_dir=tmp_path) == ["FAKE"]
    cache.write_text(json.dumps({"pdf_sha256": sha, "pypdf_version": "9.9.9", "pages": 2}) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        se.load_pages(pdf, cache_dir=tmp_path)


def test_cache_name_carries_pypdf_version(tmp_path, monkeypatch):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-fake")
    sha = hashlib.sha256(b"%PDF-fake").hexdigest()
    monkeypatch.setattr(se, "pypdf_version", lambda: "1.0.0")
    (tmp_path / f"{sha}__pypdf-1.0.0.jsonl").write_text(
        json.dumps({"pdf_sha256": sha, "pypdf_version": "1.0.0", "pages": 1}) + "\n"
        + json.dumps({"page": 1, "text": "OLD"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(se, "pypdf_version", lambda: "2.0.0")
    with pytest.raises(Exception):      # a different pypdf version must re-extract (here: fake PDF fails to parse)
        se.load_pages(pdf, cache_dir=tmp_path)
    assert (tmp_path / f"{sha}__pypdf-1.0.0.jsonl").read_text(encoding="utf-8").count("OLD") == 1


# ---------------------------------------------------------------- D1 (R0 duplicate pages)

FAKE_LONG = "Fake heading.\n7. " + "Fake words repeated for length. " * 10 + "\n"


def test_identical_page_dropped_first_kept_and_listed():
    other = "Other fake heading.\n8. " + "Different fake words. " * 12
    kept, dropped = se.drop_duplicate_pages([FAKE_LONG, other, FAKE_LONG, FAKE_LONG])
    assert dropped == [(3, 1), (4, 1)]
    assert kept == [FAKE_LONG, other, "", ""]          # page numbers keep their positions


def test_short_identical_pages_are_kept():
    short = "Fake.\n9. Short fake page."                # < 200 characters
    kept, dropped = se.drop_duplicate_pages([short, short])
    assert dropped == [] and kept == [short, short]


def test_near_identical_pages_are_kept():
    kept, dropped = se.drop_duplicate_pages([FAKE_LONG, FAKE_LONG.replace("Fake words", "Fake wordz", 1)])
    assert dropped == []


# ---------------------------------------------------------------- D2 -> P09-31 (roman items not labelled)

def test_roman_items_never_labelled_and_sequence_is_integer_only():
    page = ("Fake TDS.\n393. (1) Fake,\u2014\nTABLE\n1. Fake row one\n(i)\u00a0 Fake sub one\n"
            "(iii)\u00a0 Fake out of order\n(i)\u00a0 fake in-cell list item\n2. Fake row two\n"
            "(i)\u00a0 Fake sub of two\nNext fake.\n394. Fake.")
    r = body([page], "393")
    labels = [ln.split("]")[0] + "]" for ln in r["body"].splitlines() if ln.startswith("[Table")]
    assert labels == ["[Table 1 Sl. 1]", "[Table 1 Sl. 2]"]
    assert "(iii) Fake out of order" in r["body"].splitlines() and r["unresolved"] == []


# ---------------------------------------------------------------- D3 (footnotes)

@pytest.mark.parametrize("note", ["80. Sections 115ZZ and 115ZY inserted by the Fake Act, 2099, w.e.f. 1-4-2099.",
                                  "76. Substituted for \"fake words\" by the Fake Act, 2099.",
                                  "75. See rule 99ZZ.", "74. See also fake circular."])
def test_older_footnote_wordings(note):
    cleaned = se.clean_pages([f"Fake heading.\n7. Fake text.\n{note}"])
    assert cleaned.notes[1] == [note]


def test_midpage_footnote_block_ends_at_next_heading_and_start():
    page = ("Fake heading.\n44ZZ. Fake text of the earlier section.\n76. Substituted for \"x\" by the Fake Act.\n"
            "continuation of the fake footnote.\nSpecial fake provision heading.\n44ZY. (1) Fake body after the footnote.")
    cleaned, starts = view(page)
    assert cleaned.notes[1] == ["76. Substituted for \"x\" by the Fake Act.", "continuation of the fake footnote."]
    assert [s.number for s in starts] == ["44ZZ", "44ZY"]
    assert cleaned.midpage_footnote_pages == [1] and cleaned.footnote_lines == 2


def test_quoted_old_text_inside_footnote_stays_in_footnote():
    page = ("Fake heading.\n7. Fake.\n70. Sub. by the Fake Act. Prior to its substitution, section 7 read as under:\n"
            "7. Fake old text.")
    cleaned, starts = view(page)
    assert len(cleaned.notes[1]) == 2 and [s.number for s in starts] == ["7"]


# ---------------------------------------------------------------- D4

@pytest.mark.parametrize("head", ["Explanation.—For the purposes of this fake section, fake.",
                                  "Provided that the fake proviso applies.", "[Explanation 2.—Fake.]."])
def test_explanation_or_proviso_is_never_a_heading(head):
    cleaned, starts = view(f"\"Previous year\" fake defined.\n3. Fake.\n{head}\n3. Fake instalment text.")
    assert [cleaned.lines[s.idx].text for s in starts] == ["3. Fake."]


# ---------------------------------------------------------------- D5

def test_fold_ligatures_diff_only():
    assert se.fold_for_diff("Deﬁnitions oﬀ ﬂow suﬃx baﬄe") == "Definitions off flow suffix baffle"
    r = body(["Fake.\n7. Deﬁnitions fake.\n"], "7")
    assert "ﬁ" in r["body"]                           # bodies keep the ligature as printed


# ---------------------------------------------------------------- D6 (table ordinals + map)

def test_tables_numbered_in_order_with_subsection_map():
    page = ("Fake TDS.\n393. (1) Fake first,—\nTABLE\n1. Fake row\n2. Fake row\n(2) Fake second,—\nTABLE\n"
            "1. Fake row\n(3) Fake third.\nExplanation.—Fake.\nTABLE\n1. Fake row\nNext fake.\n394. Fake.")
    r = body([page], "393")
    heads = [ln.split("]")[0] + "]" for ln in r["body"].splitlines() if ln.startswith("[Table")]
    assert heads == ["[Table 1 Sl. 1]", "[Table 1 Sl. 2]", "[Table 2 Sl. 1]", "[Table 3 Sl. 1]"]
    assert [(t["table"], t["page_1based"], t["subsection"]) for t in r["tables"]] == [
        (1, 1, "(1)"), (2, 1, "(2)"), (3, 1, "(3)")]


def test_table_prefix_never_joined_to_previous_line():
    out = se.normalise(["Fake text without stop", "[Table 2 Sl. 1] 1. Fake row"])
    assert out == "Fake text without stop\n[Table 2 Sl. 1] 1. Fake row\n"


# ---------------------------------------------------------------- v2: P09-40 page helper

def test_page_helper_is_one_based_and_round_trips():
    assert se.page_1based(0) == 1 and se.idx0_from_page(1) == 0
    assert all(se.idx0_from_page(se.page_1based(i)) == i for i in range(50))
    with pytest.raises(ValueError):
        se.page_1based(-1)
    with pytest.raises(ValueError):
        se.idx0_from_page(0)


def test_line_numbers_are_one_based_raw_lines():
    cleaned = se.clean_pages(["Fake heading.\n\n7. Fake."])
    assert [(ln.page, ln.line_no) for ln in cleaned.lines] == [(1, 1), (1, 3)]


# ---------------------------------------------------------------- v2: P09-29 / 29a / 29b markers

FILL = "\nfake filler one.\nfake filler two.\nfake filler three."


def test_line_marker_dropped_when_all_numbers_are_footnotes():
    page = ("Fake heading.\n7. Fake text here.\n3 4\nmore fake." + FILL
            + "\n3. Ins. by the Fake Act, 2099.\n4. Sub. by the Fake Act, 2099.")
    r = body([page], "7")
    assert "3 4" not in r["body"].splitlines()
    assert r["dropped_markers"] == [{"type": "line", "page_1based": 1, "line_1based": 3, "numbers": ["3", "4"]}]
    assert r["unresolved_markers"] == []


def test_marker_matched_by_footnote_on_page_after_last_page():
    p1 = "Fake heading.\n7. Fake text.\n81\nmore fake text." + FILL
    p2 = "Other fake heading.\n8. Fake eight.\n81. Sub. by the Fake Act, 2099."
    r = body([p1, p2], "7")
    assert r["pages_1based"] == [1] and "81" not in r["body"].splitlines()
    assert [d["numbers"] for d in r["dropped_markers"]] == [["81"]]


def test_marker_kept_and_listed_when_a_number_has_no_footnote():
    page = "Fake heading.\n7. Fake text.\n3 9\nmore fake." + FILL + "\n3. Ins. by the Fake Act, 2099."
    r = body([page], "7")
    assert "3 9" in r["body"].splitlines() and r["dropped_markers"] == []
    assert r["unresolved_markers"][0]["missing"] == ["9"]


def test_marker_kept_when_footnote_is_outside_the_range():
    p1 = "Fake heading.\n7. Fake text.\n81\nmore fake text." + FILL
    p2 = "Other fake heading.\n8. Fake eight." + FILL
    p3 = "Third fake heading.\n9. Fake nine.\n81. Sub. by the Fake Act, 2099."
    r = body([p1, p2, p3], "7")
    assert "81" in r["body"].splitlines() and r["unresolved_markers"][0]["numbers"] == ["81"]


def test_any_numbered_line_in_footnote_block_counts_and_footnotes_raw_split():
    page = ("Fake heading.\n7. Fake text.\n83 84\nmore fake." + FILL
            + "\n83. Sub. by the Fake Act. Prior to fake:\n\"(iv) fake old words\n"
            "84. Shall be renumbered as fake (v) by the Fake Act.")
    r = body([page], "7")
    assert "83 84" not in r["body"].splitlines()
    fr = r["footnotes_raw"]
    assert [(f["page_1based"], f["number"]) for f in fr] == [(1, "83"), (1, "84")]
    assert fr[0]["text"] == "83. Sub. by the Fake Act. Prior to fake:\n\"(iv) fake old words"
    assert "never a date source" in r["footnotes_raw_note"]


def test_footnotes_raw_continuation_on_next_page_joins_previous_entry():
    raw = se.footnotes_raw({1: ["5. Ins. by the Fake Act,"], 2: ["w.e.f. 1-4-2099.", "6. Sub. fake."]}, 1, 1)
    assert raw == [{"page_1based": 1, "number": "5", "text": "5. Ins. by the Fake Act,\nw.e.f. 1-4-2099."},
                   {"page_1based": 2, "number": "6", "text": "6. Sub. fake."}]


# ---------------------------------------------------------------- v2: P09-41 inline markers

def test_inline_marker_matched_is_dropped():
    page = "Fake heading.\n7. Fake rate of 24[30 per cent] fake." + FILL + "\n24. Sub. by the Fake Act, 2099."
    r = body([page], "7")
    assert r["body"].splitlines()[0] == "7. Fake rate of [30 per cent] fake."
    assert r["dropped_markers"] == [{"type": "inline", "page_1based": 1, "line_1based": 2, "numbers": ["24"]}]
    assert r["inline_markers_found"] == 1


def test_inline_marker_unmatched_is_kept_and_listed():
    page = "Fake heading.\n7. Fake rate of 24[30 per cent] fake." + FILL + "\n5. Sub. by the Fake Act, 2099."
    r = body([page], "7")
    assert "24[30 per cent]" in r["body"] and r["dropped_markers"] == []
    u = r["unresolved_markers"][0]
    assert u["type"] == "inline" and u["missing"] == ["24"] and "24[30" in u["context"]


def test_real_number_before_bracket_not_matching_a_footnote_is_kept():
    page = "Fake heading.\n7. Fake sum of Rs. 50[fake] here." + FILL + "\n24. Sub. by the Fake Act, 2099."
    r = body([page], "7")
    assert "Rs. 50[fake]" in r["body"] and r["dropped_markers"] == []


# ---------------------------------------------------------------- v2: P09-31 table end + map

def test_table_ends_at_bracketed_subsection_explanation_and_section_end():
    page = ("Fake TDS.\n393. (1) Fake,—\nTABLE\n1. Fake row\n2. Fake row\n[(7) Fake text after.\nTABLE\n"
            "1. Fake row\nExplanation.—Fake.\nTABLE\n1. Fake row\n2. Fake last row")
    r = body([page], "393")
    spans = [(t["table"], t["subsection"], t["start_body_line_1based"], t["end_body_line_1based"]) for t in r["tables"]]
    assert spans == [(1, "(1)", 2, 4), (2, "(7)", 6, 7), (3, "(7)", 9, 11)]
    lines = r["body"].splitlines()
    assert lines[4] == "[(7) Fake text after." and lines[7].startswith("Explanation")


# ---------------------------------------------------------------- v2: P09-32 divider lines

def test_divider_lines_dropped_and_logged():
    cleaned = se.clean_pages(["Fake heading.\n7. Fake.\n___\n-----\n———\n--\na---b" + FILL])
    texts = [ln.text for ln in cleaned.lines]
    assert "--" in texts and "a---b" in texts
    expected = [(1, 3, "___"), (1, 4, "-----"), (1, 5, "———")]
    assert [(p, ln, t) for p, ln, _, t in cleaned.rule_drops] == expected


# ---------------------------------------------------------------- v2: P09-33 / 33b hyphen joins

def test_hyphen_join_only_after_a_letter_and_never_into_a_table_row():
    texts = ["fake sub-", "section text", "year 2024-", "25 fake", "fake—", "next", "row lead-",
             "[Table 1 Sl. 2] 2. Fake row"]
    out, _, joins, not_joined = se.normalise_lines(texts)
    assert out == ["fake sub-section text", "year 2024-", "25 fake", "fake—", "next", "row lead-",
                   "[Table 1 Sl. 2] 2. Fake row"]
    assert (joins, not_joined) == (1, 1)


def test_hyphen_is_never_deleted():
    assert se.normalise(["fake well-", "known"]).count("-") == 1


# ---------------------------------------------------------------- v2: P09-34 fold collapses all whitespace

def test_fold_v2_collapses_newlines():
    assert se.fold_for_diff("fake\ntext  here\n") == "fake text here"
    assert se.fold_for_diff("a b\nc") == se.fold_for_diff("a b c")


# ---------------------------------------------------------------- v2: P09-35 editor-note candidates

def test_editor_note_block_listed_not_removed():
    page = ("Fake TDS.\n393. (6) Fake text.\nFollowing clause (b) shall be inserted after clause (a) of sub-section (6)\n"
            "by the Fake Act, 2099, w.e.f. 1-4-2099:\n(b) Fake inserted clause text\ncontinues here.\n"
            "[(7) Fake next sub-section.]" + FILL)
    r = body([page], "393")
    c = r["editor_note_candidates"]
    assert len(c) == 1 and c[0]["page_1based"] == 1 and c[0]["line_1based"] == 3
    assert c[0]["text"].splitlines()[-1] == "continues here." and len(c[0]["text"].splitlines()) == 4
    assert "Following clause (b) shall be inserted" in r["body"]       # never cut automatically


def test_editor_note_inside_footnote_block_is_not_a_candidate():
    page = ("Fake TDS.\n393. Fake text." + FILL + "\n5. Ins. by the Fake Act. Following fake shall be inserted\n"
            "w.e.f. 1-4-2099.")
    r = body([page], "393")
    assert r["editor_note_candidates"] == []


# ---------------------------------------------------------------- v2: P09-36 opening bracket + counts

def test_bracket_line_before_heading_moves_to_body():
    r = body(["[\nFake heading.\n7. Fake text.]" + FILL], "7")
    assert r["body"].startswith("[7. Fake text.]") and r["heading"] == "Fake heading."
    assert r["brackets"] == {"open": 1, "close": 1, "warn": False}


def test_bracket_warn_when_counts_differ_and_table_prefixes_excluded():
    assert se.bracket_counts("[Table 1 Sl. 1] 1. Fake [row\n") == {"open": 1, "close": 0, "warn": True}
    assert se.bracket_counts("[Table 2 Sl. 3] 3. Fake row\n[fake]\n") == {"open": 1, "close": 1, "warn": False}
