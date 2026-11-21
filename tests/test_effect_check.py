"""C3-fix B: per-row edition check (statute_build.check_effect / effect_checks). INVENTED section bodies only."""
from divergence import act_parse as ap
from divergence import statute_build as sb

ASSENT = "2099-03-30"


def eds(*specs):
    return [{"key": k, "knowledge": d, "found": f, "pending": set(p)} for k, d, f, p in specs]


TWO = eds(("e1", "2098-06-01", True, ()), ("e2", "2099-06-01", True, ()))


def eff(**kw):
    e = {c: "" for c in ap.EFFECT_COLUMNS}
    e.update(effect_id="zz:s3(c)", target_act="1961", target_section="7", assent_date=ASSENT, wef="2099-04-01",
             operation="insert", scope="unit", position="after", target_unit="clause (9)", new_units="(9A)")
    e.update(kw)
    return e


def run(e, bodies, editions=TWO):
    return sb.check_effect(e, editions, lambda k: bodies[k])


B_OLD = "(9) alpha means an invented thing; (10) beta means another invented thing."
B_NEW = "(9) alpha means an invented thing; 1[(9A) zeta means a made-up thing;] (10) beta means another invented thing."


def test_insert_label_absent_before_present_after_ok():
    st, note = run(eff(), {"e1": B_OLD, "e2": B_NEW})
    assert st == "ok" and "e2" in note and "e1" in note


def test_insert_label_missing_after_fails():
    assert run(eff(), {"e1": B_OLD, "e2": B_OLD})[0] == "fail"
    assert run(eff(), {"e1": B_NEW, "e2": B_NEW})[0] == "fail"          # already there before the effect


def test_reference_is_not_a_unit_start():
    body = "(9) alpha, see clause (9A) of another invented Act; (10) beta."
    assert run(eff(), {"e1": B_OLD, "e2": body})[0] == "fail"


def test_no_edition_after_and_pending_edition_skipped():
    old = eds(("e1", "2098-06-01", True, ()))
    assert run(eff(), {"e1": B_OLD}, old) == ("no_edition", "no_edition: no edition after the effect")
    pend = eds(("e1", "2098-06-01", True, ()), ("e2", "2099-06-01", True, ("zz:s3(c)",)))
    assert run(eff(), {"e1": B_OLD, "e2": B_NEW}, pend)[0] == "no_edition"


def test_no_before_edition_only_checks_after():
    one = eds(("e2", "2099-06-01", True, ()))
    assert run(eff(), {"e2": B_NEW}, one)[0] == "ok"


def test_container_segment_limits_search():
    body = "(22) gamma: (i) one; (ii) two; (23) delta: (i) x; (iv) y."
    e = eff(operation="omit", position="in", target_unit="clause (22) > item (iv)", new_units="")
    assert run(e, {"e1": body, "e2": body})[0] == "ok"                  # (iv) only in clause (23)
    body2 = "(22) gamma: (i) one; (iv) four; (23) delta."
    assert run(e, {"e1": body2, "e2": body2})[0] == "fail"
    seg, where = sb.container_segment(body2, ["clause (22)"])
    assert where == "container (22)" and "(23)" not in seg
    assert sb.container_segment(body2, ["long line[2]"])[1] == "section"


def test_words_scope_anchor_present_both():
    e = eff(scope="words", position="for", target_unit="clause (9)", new_units="")
    assert run(e, {"e1": B_OLD, "e2": B_NEW})[0] == "ok"
    assert run(e, {"e1": "(8) x.", "e2": B_NEW})[0] == "fail"


def test_unlabelled_anchor_is_no_label():
    e = eff(operation="omit", position="in", target_unit="clause (4) > proviso[3]", new_units="")
    assert run(e, {"e1": B_OLD, "e2": B_OLD}) == ("no_edition", "no_label: anchor has no label")


def test_proviso_new_unit_by_count():
    e = eff(target_unit="clause (9) > proviso[1]", new_units="proviso")
    old = "(9) alpha: Provided that x. (10) beta."
    new = "(9) alpha: Provided that x: Provided further that y. (10) beta."
    assert run(e, {"e1": old, "e2": new})[0] == "ok"
    assert run(e, {"e1": old, "e2": old})[0] == "fail"


def test_whole_section_insert():
    e = eff(target_unit="", target_section="7B", position="after", new_units="7B;7C", effect_id="zz:s4")
    ok = eds(("e1", "2098-06-01", False, ()), ("e2", "2099-06-01", True, ()))
    assert run(e, {}, ok)[0] == "ok"
    bad = eds(("e1", "2098-06-01", False, ()), ("e2", "2099-06-01", False, ()))
    assert run(e, {}, bad)[0] == "fail"


def test_substitute_unit_has_no_rule_and_unparsed_kept():
    e = eff(operation="substitute", position="for", new_units="")
    assert run(e, {"e1": B_OLD, "e2": B_NEW}) == ("no_edition", "no_rule: no check for this operation/scope")
    e = eff(check_status="fail", check_note="unparsed:no_anchor", target_unit="", position="")
    assert run(e, {}) == ("fail", "unparsed:no_anchor")


# ---------------------------------------------------------------- B2 rules (a)-(d)

def test_b2a_reference_with_and_does_not_end_container_or_count():
    body = "(24) omega includes— (i) one, see sub-sections (2) and (3) of section 17 ; (xviic) a sum; (25) psi."
    seg, where = sb.container_segment(body, ["clause (24)"])
    assert where == "container (24)" and "(xviic)" in seg and "(25)" not in seg
    assert sb._count("(a) see regulation 2(1)(e) and (f) of the Code; (g) rho.", "f") == 0
    assert sb._count("(c) one; and (d) two.", "d") == 1                   # '; and (d)' is still a heading


def test_b2b_omitted_marker_counts_as_absent():
    e = eff(operation="omit", position="in", target_unit="clause (22) > item (iv)", new_units="")
    after = "(22) gamma: (iii) three; (iv) [***] (v) five; (23) delta."
    before = "(22) gamma: (iii) three; (iv) four; (v) five; (23) delta."
    assert run(e, {"e1": before, "e2": after})[0] == "ok"


def test_b2c_insert_passes_when_count_rises():
    e = eff(target_unit="clause (22) > Explanation 3 > clause (b)", new_units="(c)")
    before = "(22) x: (a) one; (b) two; (c) three. Explanation 3.—(a) p; (b) q. (23) y."
    after = "(22) x: (a) one; (b) two; (c) three. Explanation 3.—(a) p; (b) q; (c) r. (23) y."
    assert run(e, {"e1": before, "e2": after})[0] == "ok"
    assert run(e, {"e1": before, "e2": before})[0] == "fail"


def test_b2d_label_gap_edition_skipped_with_note(monkeypatch):
    monkeypatch.setattr(sb, "LABEL_GAP", {("gap1", "7"): "test"})
    three = eds(("e0", "2098-06-01", True, ()), ("gap1", "2099-05-01", True, ()), ("e2", "2099-06-01", True, ()))
    st, note = run(eff(), {"e0": B_OLD, "gap1": B_OLD, "e2": B_NEW}, three)
    assert st == "ok" and "e2" in note and note.endswith("skipped:gap1:source_label_gap")
    only_gap = eds(("e0", "2098-06-01", True, ()), ("gap1", "2099-05-01", True, ()))
    st, note = run(eff(), {"e0": B_OLD, "gap1": B_OLD}, only_gap)
    assert st == "no_edition" and "skipped:gap1:source_label_gap" in note
    before_gap = eds(("gap1", "2098-06-01", True, ()), ("e2", "2099-06-01", True, ()))
    st, note = run(eff(), {"gap1": B_NEW, "e2": B_NEW}, before_gap)
    assert st == "ok" and "skipped:gap1:source_label_gap" in note       # no usable before edition


def test_b2d_label_gap_pairs_are_owner_data():
    assert set(sb.LABEL_GAP) == {("ita1961_2023", "2"), ("ita1961_2024n1", "2"), ("ita1961_2024n2", "56"),
                                 ("ita1961_2023", "56"), ("ita1961_2024n1", "56")}


def test_effect_checks_non_spine_section():
    e = eff(target_section="999Z")
    assert sb.effect_checks([e], {}, None)["zz:s3(c)"][0] == "no_edition"
