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
    assert r["status"] == "UNRESOLVED" and [p for p, _ in r["candidates"]] == [1, 2]


def test_not_found():
    assert body(["Fake A.\n5. Fake one.\n"], "6")["status"] == "NOT_FOUND"


def test_letter_suffix_does_not_match_plain_number():
    cleaned, starts = view("Fake heading.\n2A. Fake two A.\n")
    assert se.locate(cleaned.lines, starts, "2")["status"] == "NOT_FOUND"


def test_wrapped_and_bracketed_heading():
    r = body(["[Fake obligation to furnish information on transaction of\ninvented asset.\n285ZZ.\n(1) Fake.\n"], "285ZZ")
    assert r["status"] == "FOUND"
    assert r["heading"] == "[Fake obligation to furnish information on transaction of invented asset."


def test_no_space_between_dot_and_subsection():
    r = body(["[Fake obligation heading.\n285ZZ.(1) Fake reporting text.\nNext fake.\n286. Fake."], "285ZZ")
    assert r["status"] == "FOUND" and r["body"] == "285ZZ.(1) Fake reporting text.\n"


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
    assert r["pages"] == [1, 2] and r["body"] == "10. Fake start continues on page two.\n"


def test_section_ends_at_chapter_line_and_at_end_of_file():
    r = body(["Fake heading.\n139. Fake return text.\nCHAPTER I\nPRELIMINARY\nShort title.\n1. Fake."], "139")
    assert r["body"] == "139. Fake return text.\n"
    r2 = body(["Fake heading.\n9. Last fake section."], "9")
    assert r2["body"] == "9. Last fake section.\n"


def test_out_of_order_section_at_front_is_found():
    pages = ["CHAPTER XIV\nFAKE PROCEDURE\nFake return.\n139. Fake displaced text.",
             "FAKE ACT, 2099\nCHAPTER I\nShort title.\n1. Fake.", "Fake disclosure.\n138. Fake.\nFake number.\n139A. Fake."]
    r = body(pages, "139")
    assert r["status"] == "FOUND" and r["pages"] == [1] and r["body"] == "139. Fake displaced text.\n"


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


def test_footnote_block_moved_verbatim_and_markers_kept():
    page = ("Fake heading.\n7. Fake 1[inserted words]* and 2text.\n"
            "1. Ins. by Act No. 99 of 2099, w.e.f. 1-4-2099.\n2. Words \"fake\" omtt. by Act No. 98.\n" + FOOTER)
    r = body([page], "7")
    assert r["body"] == "7. Fake 1[inserted words]* and 2text.\n"
    assert r["amendment_note"] == ("[p.1] 1. Ins. by Act No. 99 of 2099, w.e.f. 1-4-2099.\n"
                                   "[p.1] 2. Words \"fake\" omtt. by Act No. 98.")


# ---------------------------------------------------------------- R5 tables

TABLE_PAGE = ("Tax on fake incomes.\n194. (1) Fake text below,—\nTABLE\nSl.\nNo.\nA B C\n"
              "1. Fake person. Fake winnings from—\n(a) fake lottery; or\n2. Fake row two\ncontinued here.\n"
              "3. Fake row three.\n4. Fake capital market\n  (i)  Fake income in respect of\n  (ii)  Fake distributed income\n"
              "(2) Fake sub-section after the table.\nNext fake.\n195. Fake.")


def test_table_rows_and_subrows_are_prefixed():
    r = body([TABLE_PAGE], "194")
    lines = r["body"].splitlines()
    assert "[Table 1 Sl. 4] 4. Fake capital market" in lines
    assert "[Table 1 Sl. 4(i)] (i) Fake income in respect of" in lines
    assert "[Table 1 Sl. 4(ii)] (ii) Fake distributed income" in lines
    assert r["table_rows"] == 6 and r["unresolved"] == []


def test_table_rows_are_never_joined_into_one_line():
    r = body([TABLE_PAGE], "194")
    rows = [ln for ln in r["body"].splitlines() if ln.startswith("[Table 1 Sl.")]
    assert [ln.split("]")[0] for ln in rows] == ["[Table 1 Sl. 1", "[Table 1 Sl. 2", "[Table 1 Sl. 3", "[Table 1 Sl. 4",
                                                 "[Table 1 Sl. 4(i)", "[Table 1 Sl. 4(ii)"]
    assert "[Table 1 Sl. 2] 2. Fake row two continued here." in r["body"].splitlines()
    assert all(ln.count("[Table 1 Sl.") == 1 for ln in rows)


def test_table_sl_8_vi():
    rows = "".join(f"{n}. Fake row {n}\n" for n in range(1, 8))
    subs = "".join(f"  ({r})  Fake sub {r}\n" for r in ("i", "ii", "iii", "iv", "v", "vi"))
    r = body([f"Fake TDS.\n393. (1) Fake,—\nTABLE\n{rows}8. Other fake cases\n{subs}Next fake.\n394. Fake."], "393")
    assert "[Table 1 Sl. 8(vi)] (vi) Fake sub vi" in r["body"].splitlines()


def test_unindented_roman_in_cell_is_not_a_subrow():
    r = body(["Fake.\n393. Fake,—\nTABLE\n1. Fake row\n(i) fake cell item\nNext fake.\n394. Fake."], "393")
    assert "[Table 1 Sl. 1(i)]" not in r["body"]


def test_non_sequential_number_in_table_is_unresolved():
    r = body(["Fake.\n393. Fake,—\nTABLE\n1. Fake row\n5. fake odd number\nNext fake.\n394. Fake."], "393")
    assert len(r["unresolved"]) == 1 and "non-sequential" in r["unresolved"][0]


# ---------------------------------------------------------------- R4

def test_whitespace_collapse_keeps_characters():
    assert se.normalise(["7.  Fake  text\t here.  "]) == "7. Fake text here.\n"
    assert se.normalise(["“Fake” ₹ 5 and Rs. 6 busi-", "ness."]) == "“Fake” ₹ 5 and Rs. 6 busi- ness.\n"


def test_join_rules():
    texts = ["7. (1) Fake text that", "wraps here;", "(a) fake clause", "continued.",
             "Explanation.—Fake", "Provided that fake."]
    assert se.normalise(texts) == ("7. (1) Fake text that wraps here;\n(a) fake clause continued.\n"
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


# ---------------------------------------------------------------- D2 (sub-rows)

def test_nbsp_subrows_must_be_sequential():
    page = ("Fake TDS.\n393. (1) Fake,—\nTABLE\n1. Fake row one\n(i)  Fake sub one\n(ii)  Fake sub two\n"
            "(i)  fake in-cell list item\n2. Fake row two\n(i)  Fake sub of two\nNext fake.\n394. Fake.")
    r = body([page], "393")
    labels = [ln.split("]")[0] + "]" for ln in r["body"].splitlines() if ln.startswith("[Table")]
    assert labels == ["[Table 1 Sl. 1]", "[Table 1 Sl. 1(i)]", "[Table 1 Sl. 1(ii)]", "[Table 1 Sl. 2]", "[Table 1 Sl. 2(i)]"]


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
    assert r["tables"] == [{"table": 1, "page": 1, "subsection": "(1)"}, {"table": 2, "page": 1, "subsection": "(2)"},
                           {"table": 3, "page": 1, "subsection": "(3)"}]


def test_table_prefix_never_joined_to_previous_line():
    out = se.normalise(["Fake text without stop", "[Table 2 Sl. 1] 1. Fake row"])
    assert out == "Fake text without stop\n[Table 2 Sl. 1] 1. Fake row\n"
