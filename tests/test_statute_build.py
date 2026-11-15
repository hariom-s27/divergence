"""Tests for divergence/statute_build.py (P09 Part C2). INVENTED data only; no real law text, no network."""
from divergence import statute_build as sb


def eff(eid, wef, assent="2099-03-30", **kw):
    e = {"effect_id": eid, "act_key": "Act No. 9 of 2099", "target_act": "1961", "target_section": "7",
         "target_unit": "clause (1)", "operation": "substitute", "commencement_source": "s1_default", "wef": wef,
         "deemed_from": "", "assent_date": assent, "applicability_note_present": "no", "corrigendum_flag": "no",
         "instrument_provision": "s.3(a)"}
    e.update(kw)
    return e


def ed(key, knowledge, found=True, pending=()):
    return {"key": key, "knowledge": knowledge, "found": found, "pending": set(pending)}


def test_zero_length_original_is_never_operative():
    effs = [eff("x:s3(a)", "2100-04-01", target_act="2025")]
    rows, before, _ = sb.propose_versions("2025", "7", effs, [ed("e2100", "2100-03-30")], "2100-04-01", None)
    assert (rows[0]["state"], rows[0]["in_force_from"], rows[0]["in_force_to"]) == ("never_operative", "", "")
    assert rows[0]["code_note"].startswith("zero_length; zero-length at 2100-04-01")
    assert rows[0]["basis_category"] == rows[0]["basis"] == ""
    assert rows[1]["state"] == "in_force" and rows[1]["effect_ids"] == "x:s3(a)" and rows[1]["in_force_to"] == ""
    assert rows[1]["record_key"] == "act:2025:7:v2" and before == []


def test_unprinted_intermediate_state_is_ambiguous():
    effs = [eff("x:a", "2099-04-01"), eff("y:b", "2099-10-01", assent="2099-08-01")]
    eds = [ed("e1", "2099-01-01"), ed("e2", "2099-12-31")]       # e1 prints {} ... e2 prints {a, b}
    rows, before, _ = sb.propose_versions("1961", "7", effs, eds, None, None)
    assert before == []
    states = [(r["in_force_from"], r["state"], r["reason_codes"]) for r in rows]
    assert states == [("", "in_force", ""), ("2099-04-01", "", "unprinted_intermediate"),
                      ("2099-10-01", "in_force", "")]


def test_earliest_matching_edition_supplies_the_text():
    effs = [eff("x:a", "2099-04-01")]
    eds = [ed("e1", "2099-01-01"), ed("e2", "2099-05-01"), ed("e3", "2099-06-01")]
    rows, _, _ = sb.propose_versions("1961", "7", effs, eds, None, None)
    assert rows[-1]["code_note"] == "effect_start; text = e2" and rows[-1]["basis"] == ""


def test_pending_effect_excluded_from_printed_state():
    effs = [eff("x:a", "2099-04-01"), eff("x:b", "2100-04-01")]
    eds = [ed("e1", "2099-05-01", pending={"x:b"}), ed("e2", "2100-05-01")]
    rows, _, _ = sb.propose_versions("1961", "7", effs, eds, None, None)
    assert [(r["in_force_from"], r["code_note"]) for r in rows if r["state"] == "in_force"][-2:] == [
        ("2099-04-01", "effect_start; text = e1"), ("2100-04-01", "effect_start; text = e2")]


def test_retro_and_corrigendum_and_applicability_reasons():
    effs = [eff("x:a", "2098-04-01", deemed_from="2098-04-01", corrigendum_flag="yes",
                applicability_note_present="yes")]
    rows, _, _ = sb.propose_versions("1961", "7", effs, [ed("e1", "2099-05-01")], None, None)
    assert rows[-1]["reason_codes"] == "retro_knowledge;corrigendum_open;applicability_unclear"


def test_before_coverage_not_written_as_rows():
    effs = [eff("x:a", "2098-04-01"), eff("x:b", "2099-04-01")]
    rows, before, _ = sb.propose_versions("1961", "7", effs, [ed("e1", "2099-05-01")], None, None)
    assert [b["from"] for b in before] == [None, "2098-04-01"]
    assert [r["in_force_from"] for r in rows] == ["2099-04-01"]


def test_repeal_day_version_is_unsettled_not_never_operative():
    effs = [eff("x:a", "2099-04-01"), eff("x:b", "2101-04-01", assent="2100-03-30")]
    eds = [ed("e1", "2099-05-01"), ed("e2", "2100-05-01")]
    rows, _, _ = sb.propose_versions("1961", "7", effs, eds, None, "2101-04-01", repeal_day="2101-04-01")
    last = rows[-1]
    assert (last["state"], last["in_force_from"], last["in_force_to"]) == ("in_force", "2101-04-01", "2101-04-01")
    assert last["reason_codes"].startswith("repeal_day_unsettled") and sb.REPEAL_NOTE in last["code_note"]
    assert rows[-2]["in_force_to"] == "2101-04-01"


def test_inserted_section_has_no_original_row():
    effs = [eff("x:s4", "2099-07-01", operation="insert", target_unit="", instrument_provision="s.4")]
    rows, before, _ = sb.propose_versions("1961", "7B", effs, [ed("e1", "2099-12-31")], "2099-07-01", None,
                                          inserted=True)
    assert [(r["in_force_from"], r["state"]) for r in rows] == [("2099-07-01", "in_force")] and before == []


def test_unplaced_effect_listed():
    rows, _, unplaced = sb.propose_versions("1961", "7", [eff("x:a", "")], [ed("e1", "2099-05-01")], None, None)
    assert unplaced == ["x:a"]


def test_pending_rule_abbreviations_and_knowledge():
    k = "2099-03-30"
    assert sb.pending_rule("7. Following words shall be Omtt. by Act No. 9 of 2099, w.e.f. 1-4-2100", k)[0]
    assert sb.pending_rule("8. shall be sub. by the Act No. 9 of 2099, w.e.f. 1-4-2100", k)[0]
    assert sb.pending_rule("9. Shall be renumbered by Act No. 9 of 2099, w.e.f. 1-4-2100", k)[0]
    assert sb.pending_rule("10. Shall be Ins. by Act No. 9 of 2099, w.e.f. 1-4-2100", k)[0]
    assert sb.pending_rule("11. Sub. by Act No. 9 of 2099, w.r.e.f. 1-4-2100", k) == (False, "no_pending_wording")
    assert sb.pending_rule("12. shall be omitted by Act No. 9 of 2099, w.e.f. 1-3-2099", k)[0] is False
    assert sb.pending_rule("13. shall be omitted by Act No. 9 of 2099, w.e.f. 1-4-2100", None) == (
        False, "knowledge_unknown")


def test_word_hunks_and_marks_only():
    hs = sb.word_hunks("an [old] alpha rule", "an old beta rule")
    assert [(h["op"], h["old"], h["new"]) for h in hs] == [("replace", "[old] alpha", "old beta")]
    assert sb.marks_only({"old": "[old]", "new": "old"}) and not sb.marks_only(hs[0])


def test_explain_hunk_labels():
    spans = [{"cmp_span": "beta gamma delta", "act_key": "Act No. 9 of 2099", "old_text": None}]
    h = {"op": "replace", "old": "alpha", "new": "beta gamma delta", "at": 0}
    assert sb.explain_hunk(h, spans, {"Act No. 9 of 2099"}, [])[0] == "effect"
    assert sb.explain_hunk(h, [dict(spans[0], act_key="Act No. 4 of 2024")], set(), []) == (
        "amendment_not_in_ledger", "Act No. 4 of 2024")
    assert sb.explain_hunk(h, [dict(spans[0], act_key="Act No. 4 of 2001")], set(), [])[0] == "older_act_span"
    assert sb.explain_hunk(h, [], set(), [])[0] == "publisher_change"
    corr = [{"for": "\"alpha\"", "read": "\"beta gamma delta\"", "gazette_page": "5", "gazette_lines": "2"}]
    assert sb.explain_hunk(h, [], set(), corr)[0] == "corrigendum"
    assert sb.explain_hunk({"op": "replace", "old": "[x]", "new": "x", "at": 0}, [], set(), [])[0] == "marks_only"
    assert sb.explain_hunk({"op": "replace", "old": "Zeta", "new": "Ze ‐ ta", "at": 0}, [], set(), [])[0] == \
        "format_only"
    assert sb.explain_hunk({"op": "insert", "old": "", "new": "(12A)", "at": 0}, [], set(), [])[0] == "label_only"
    assert sb.explain_hunk(h, [dict(spans[0], act_key=None)], set(), [])[0] == "span_unlinked"
    star = {"op": "replace", "old": "an omitted invented phrase", "new": "[***]", "at": 0}
    om = [{"cmp_span": "***", "act_key": "Act No. 9 of 2099", "old_text": None, "star_words": "omitted invented phrase",
           "fn_text": "Omitted by Act No. 9 of 2099"}]
    assert sb.explain_hunk(star, om, {"Act No. 9 of 2099"}, [])[0] == "effect"
    assert sb.explain_hunk({"op": "replace", "old": "28 ;", "new": "28; (vb)", "at": 0}, [], set(), [])[0] == \
        "label_only"
    assert sb.explain_hunk({"op": "replace", "old": "sum16", "new": "sum", "at": 0}, [], set(), [])[0] == "format_only"
    assert sb.explain_hunk(h, [], set(), [], realised=["beta gamma delta epsilon"])[0] == "editor_note_realised"
    assert sb.explain_hunk(h, [], set(), [], window_effects=["x:s3"]) == ("effect_in_window", "x:s3")


def test_insertion_text_check():
    body = "Zeta rule.—(1) An invented person shall do an invented thing."
    assert sb.insertion_text_check("'7B. (1) An invented person shall do an invented thing.'.", body)["identical"]
    r = sb.insertion_text_check("'7B. (1) An invented person shall do another thing.'.", body)
    assert not r["identical"] and r["act_covered_by_edition"] < 1
    two = "'7B. (1) An invented person shall do an invented thing. 7C. (1) A second invented rule.'."
    assert sb.section_segment(two, "7B") == "'7B. (1) An invented person shall do an invented thing."
    assert sb.insertion_text_check(sb.section_segment(two, "7B"), body)["identical"]


def test_crosscheck_counts_two_way():
    ev = [("a", "1961", "7", "apparatus", "e1"), ("b", "1961", "7", "none", "-"), ("c", "1961", "7", "apparatus", "e1")]
    ch = [("1961", "7", "e1", "effect", "x", {}), ("1961", "7", "e1", "publisher_change", "", {})]
    out = sb.crosscheck_counts(ev, ch)
    assert "effects -> evidence (n=3): apparatus 2, none 1" in out
    assert "edition changes -> explanation (n=2 hunks): effect 1, publisher_change 1" in out


def test_effect_evidence_uses_knowing_edition():
    e = eff("x:a", "2099-04-01")
    app = {("e2", "7"): [{"act_key": "Act No. 9 of 2099"}]}
    eds = [("e1", "2099-01-01"), ("e2", "2099-05-01")]
    assert sb.effect_evidence(e, eds, app, [], {}) == ("apparatus", "e2")
    assert sb.effect_evidence(e, eds, {}, [], {("e2", "7"): [{"op": "insert"}]}) == ("diff_only", "e2")
    assert sb.effect_evidence(e, [("e1", None)], {}, [], {}) == ("none", "-")


def test_edition_knowledge_note_vs_printed_title(monkeypatch):
    aliases = {"Zeta Finance Act, 2099": "Act No. 9 of 2099", "Zeta Finance Act, 2100": "Act No. 2 of 2100"}
    monkeypatch.setattr(sb.se, "ACT_ALIASES", aliases)
    assent = {"Act No. 9 of 2099": "2099-03-30", "Act No. 2 of 2100": "2100-02-01"}
    conv = {"status": "found", "latest_acts": ["the Zeta Finance Act, 2099"]}
    k = sb.edition_knowledge(conv, ["ZETA FINANCE ACT, 2100"], assent, "1961")
    assert (k["date"], k["source"], k["mismatch"]) == ("2099-03-30", "convention_note", True)
    k2 = sb.edition_knowledge({"status": "no_note"}, ["ZETA FINANCE ACT, 2100"], assent, "2025")
    assert (k2["date"], k2["source"]) == ("2100-02-01", "printed_title_line")
    k3 = sb.edition_knowledge({"status": "no_note"}, None, assent, "2025")
    assert k3["date"] is None and k3["source"] == "unknown"
    assert sb.printed_amended_by(["x\n[AS AMENDED BY ZETA ACT, 2099 AND ZETA (NO. 2) ACT, 2099]\n"]) == [
        "ZETA ACT, 2099", "ZETA (NO. 2) ACT, 2099"]


def test_states_and_owner_carry_rule():
    effs = [eff("x:a", "2099-04-01"), eff("y:b", "2099-10-01", assent="2099-08-01")]
    rows, _, _ = sb.propose_versions("1961", "7", effs, [ed("e1", "2099-01-01"), ed("e2", "2099-12-31")], None, None)
    assert {r["state"] for r in rows} <= set(sb.STATES) and list(rows[0])[:13] == sb.VERSION_COLUMNS
    assert sb.owner_value({"basis_category": "procedural"}, "basis_category")
    assert not sb.owner_value({"basis_category": "effect_start"}, "basis_category")
    assert not sb.owner_value({"basis_category": "effect_start", "basis": "text = e1"}, "basis")


def test_corrigendum_context_and_glued_word():
    h = sb.word_hunks("tax on interest creditor paid to him", "tax on interest credited or paid to him")[0]
    c = {"for": "interest credit", "read": "interest credited", "gazette_page": "9", "gazette_lines": "1"}
    assert sb.corr_explains(c, h) and sb.explain_hunk(h, [], set(), [c])[0] == "corrigendum"
    d = sb.word_hunks("where shall such income is", "where such income is")[0]
    assert sb.corr_explains({"for": "shall such income", "read": "such income"}, d)
    assert not sb.corr_explains({"for": "zeta", "read": "eta"}, d)
    assert len(h["key"]) == 16 and h["key"] == sb.hunk_key(h)


def test_owner_label_data_over_rule(monkeypatch):
    monkeypatch.setattr(sb, "OWNER_RELABELS", {("1961", "7", "e2", "k1"): ("layout", "owner 2099-01-01: moved")})
    monkeypatch.setattr(sb, "OWNER_EYE_CHECK", {("1961", "7", "e2", "k2")})
    assert sb.owner_label(("1961", "7", "e2", "k1"), "effect_in_window", "x") == (
        "layout", "owner 2099-01-01: moved; rule label effect_in_window")
    assert sb.owner_label(("1961", "7", "e2", "k2"), "span_unlinked", "d")[0] == "owner_eye_check_pending"
    assert sb.owner_label(("1961", "7", "e2", "k3"), "effect", "Act") == ("effect", "Act")


GZ = ("THE ZETA ACT, 2099\nBE it enacted by Parliament as follows:—\n"
      "1. (1) This Act may be called the Zeta Act, 2099 and applies to invented levies everywhere.\n"
      "Definitions. 2. In this Act, unless the context otherwise requires, an invented word means a thing.\n"
      "3. (1) The Zeta Levy Act, 2098 is hereby repealed for every invented purpose at once.\n"
      "THE FIRST SCHEDULE\n")


def test_gazette_locator_number_line_and_schedule_end():
    gi = sb.gazette_index([GZ])
    body2 = "Definitions.—In this Act, unless the context otherwise requires, an invented word means a thing."
    r = sb.locate_gazette(gi, "2", body2, "Definitions.")
    assert gi["lines"][r["start"]].text.startswith("Definitions. 2.") and r["how"].startswith("number line")
    body3 = "(1) The Zeta Levy Act, 2098 (4 of 2098) is hereby repealed for every invented purpose at once."
    r3 = sb.locate_gazette(gi, "3", body3, None)                  # ITD-added '(4 of 2098)' is ignored
    assert gi["lines"][r3["start"]].text.startswith("3. (1)")
    assert sb.locate_gazette(gi, "9", "(1) Nothing like this exists in the invented text at all.", None)["start"] is None


def test_gazette_classes():
    k = sb.gazette_class
    assert k({"op": "replace", "old": "1992;", "new": "1992 (15 of 1992);", "at": 5}, [])[0] == "itd_addition"
    assert k({"op": "replace", "old": "A B C D", "new": "[Table 1 Sl. 2]", "at": 5}, [])[0] == "itd_addition"
    assert k({"op": "insert", "old": "", "new": "92.", "at": 0}, [], "92")[0] == "boundary"
    assert k({"op": "delete", "old": "CHAPTER II BASIS", "new": "", "at": 7}, [], "3", 10)[0] == "boundary"
    assert k({"op": "replace", "old": "Centers", "new": "Centres", "at": 3}, [])[0] == "content"
    c = [(5, {"for": "on after", "read": "on or after"})]
    h = sb.word_hunks("applies on after the date", "applies on or after the date")[0]
    assert k(h, c) == ("corrigendum", "corr_ita2025 item 5")
