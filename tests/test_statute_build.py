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
    assert (rows[0]["state"], rows[0]["in_force_from"], rows[0]["in_force_to"]) == (
        "never_operative", "2100-04-01", "2100-04-01")
    assert rows[1]["state"] == "in_force" and rows[1]["effect_ids"] == "x:s3(a)" and rows[1]["in_force_to"] == ""
    assert rows[1]["record_key"] == "act:2025:7:v2" and before == []


def test_unprinted_intermediate_state_is_ambiguous():
    effs = [eff("x:a", "2099-04-01"), eff("y:b", "2099-10-01", assent="2099-08-01")]
    eds = [ed("e1", "2099-01-01"), ed("e2", "2099-12-31")]       # e1 prints {} ... e2 prints {a, b}
    rows, before, _ = sb.propose_versions("1961", "7", effs, eds, None, None)
    assert before == []
    states = [(r["in_force_from"], r["state"], r["reason_codes"]) for r in rows]
    assert states == [("", "in_force", ""), ("2099-04-01", "AMBIGUOUS", "unprinted_intermediate"),
                      ("2099-10-01", "in_force", "")]


def test_earliest_matching_edition_supplies_the_text():
    effs = [eff("x:a", "2099-04-01")]
    eds = [ed("e1", "2099-01-01"), ed("e2", "2099-05-01"), ed("e3", "2099-06-01")]
    rows, _, _ = sb.propose_versions("1961", "7", effs, eds, None, None)
    assert rows[-1]["basis"] == "text = e2"


def test_pending_effect_excluded_from_printed_state():
    effs = [eff("x:a", "2099-04-01"), eff("x:b", "2100-04-01")]
    eds = [ed("e1", "2099-05-01", pending={"x:b"}), ed("e2", "2100-05-01")]
    rows, _, _ = sb.propose_versions("1961", "7", effs, eds, None, None)
    assert [(r["in_force_from"], r["basis"]) for r in rows if r["state"] == "in_force"][-2:] == [
        ("2099-04-01", "text = e1"), ("2100-04-01", "text = e2")]


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
    assert last["reason_codes"].startswith("repeal_day_unsettled") and sb.REPEAL_NOTE in last["basis"]
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
