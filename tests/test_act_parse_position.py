"""C3-fix B: target_unit / position / new_units / scope in act_parse. INVENTED instruction sentences only (no law text);
the real-id regressions read the local instrument PDFs and are skipped when they are absent (CI)."""
import pytest

from divergence import act_parse as ap
from divergence import statute_build as sb
from divergence import statute_extract as se
from divergence import statute_sources as ss

ROOT = "9. In section 7 of the Zeta Act,—"


def loc(own, op, heads=(ROOT,), block="", item_level=False, inner=()):
    return ap.locate(list(heads), own, op, block, item_level, list(inner))


def fields(r):
    return r["target_unit"], r["position"], r["new_units"], r["scope"]


# ---------------------------------------------------------------- the census patterns

def test_insert_after_unit_records_anchor_and_new_units():
    r = loc("(c) after clause (9), the following clauses shall be inserted, namely:—", "insert",
            block="'(9A) alpha means a made-up thing; (9B) beta means another made-up thing;'")
    assert fields(r) == ("clause (9)", "after", "(9A);(9B)", "unit")
    assert r["check_status"] == ""


def test_insert_before_unit_with_proviso_block():
    r = loc("(d) in clause (4), before the Explanation, the following proviso shall be inserted, namely:—", "insert",
            block="“Provided that gamma shall apply only to invented cases.”;")
    assert fields(r) == ("clause (4) > Explanation", "before", "proviso", "unit")


def test_substitute_whole_unit():
    r = loc("(e) for sub-clause (b), the following sub-clause shall be substituted, namely:—", "substitute",
            block="'(b) delta, an invented item;'")
    assert fields(r) == ("sub-clause (b)", "for", "", "unit")


def test_substitute_words_is_words_scope_without_unit_level():
    r = loc("(f) in clause (12), for the words “old ones”, the words “new ones” shall be substituted;", "substitute")
    assert fields(r) == ("clause (12)", "for", "", "words")


def test_insert_words_after_words():
    r = loc("(g) in clause (3), in sub-clause (ii), after the figures and letter “71Z,”, the figures and letters "
            "“71ZA,” shall be inserted;", "insert")
    assert fields(r) == ("clause (3) > sub-clause (ii)", "after", "", "words")


def test_omit_unit_object_is_anchor():
    r = loc("(ii) in the long line, item (iv) shall be omitted;", "omit", heads=(ROOT, "(b) in clause (22),—"))
    assert fields(r) == ("clause (22) > long line > item (iv)", "in", "", "unit")
    r = loc("(iv) the third proviso shall be omitted.", "omit", heads=(ROOT, "(b) in clause (5),—"))
    assert fields(r) == ("clause (5) > proviso[3]", "in", "", "unit")


def test_omit_words_variants():
    r = loc("(h) in clause (19), the words and brackets “(other than mu)” shall be omitted;", "omit")
    assert fields(r) == ("clause (19)", "in", "", "words")
    r = loc("(i) in clause (2), the word, brackets and figure “rule (3)” shall be omitted;", "omit")
    assert fields(r) == ("clause (2)", "in", "", "words")


def test_renumber_and_insert_get_their_own_clause():
    own = ("(h) sub-section (6) shall be renumbered as sub-section (6)(a) thereof and after sub-section (6)(a) as so "
           "renumbered, the following sub-section shall be inserted, namely:—")
    blk = "“(b) The invented form may also be sent by post.”;"
    assert fields(loc(own, "renumber", block=blk)) == ("sub-section (6)", "in", "", "unit")
    assert fields(loc(own, "insert", block=blk)) == ("sub-section (6)(a)", "after", "(b)", "unit")


def test_item_level_insert_lists_every_inserted_section():
    r = loc("4. After section 7A of the Zeta Act, the following sections shall be inserted, namely:—", "insert",
            heads=(), block="'7B. Invented. 7C. Also invented.'", item_level=True, inner=["7B", "7C"])
    assert fields(r) == ("", "after", "7B;7C", "unit")
    r = loc("6. For section 8 of the Zeta Act, the following section shall be substituted, namely:—", "substitute",
            heads=(), block="'8. Invented.'", item_level=True, inner=["8"])
    assert fields(r) == ("", "for", "", "unit")


# ---------------------------------------------------------------- positional phrases, ordinals

def test_multi_anchor_container_and_after_x_before_y():
    heads = ("5. In section 9 of the Zeta Act, in sub-section (2),—", "(b) in clause (x),—")
    r = loc("(i) in the proviso occurring below item (D) in sub-clause (f), after clause (IV) and before the "
            "Explanation, the following clauses shall be inserted, namely:—", "insert", heads=heads,
            block="‘(V) by an invented person; (VI) by another invented person. Explanation.—For the purposes of "
                  "clauses (V) and (VI), invented means made up.’;")
    assert fields(r) == ("sub-section (2) > clause (x) > proviso[1] > clause (IV)", "after", "(V);(VI)", "unit")
    r = loc("(ii) in sub-clause (f), after the proviso occurring below item (D) and before the Explanation, the "
            "following proviso shall be inserted, namely:—", "insert", heads=heads,
            block="“Provided further that nothing here applies to invented sums.”;")
    assert fields(r) == ("sub-section (2) > clause (x) > sub-clause (f) > proviso[1]", "after", "proviso", "unit")


def test_locator_phrases_are_not_levels():
    r = loc("(b) in clause (40C), for the word “omega” occurring at the end and before Explanation 2, the word “psi” "
            "shall be substituted;", "substitute")
    assert fields(r) == ("clause (40C)", "for", "", "words")
    r = loc("(c) in clause (b), after the words “rho, sigma” at both the places where they occur, the words “, tau” "
            "shall be inserted.", "insert")
    assert fields(r) == ("clause (b)", "after", "", "words")
    r = loc("(B) in the first long line below sub-clause (f) as so omitted, for sub-clause (v), the following "
            "sub-clause shall be substituted, namely:—", "substitute", heads=(ROOT, "(b) in clause (40),—"))
    assert fields(r)[:2] == ("clause (40) > long line[1] > sub-clause (v)", "for")


def test_ordinals_and_numbered_units():
    r = loc("(e) in clause (42), in Explanation 1, in clause (i), after sub-clause (hh), the following sub-clause "
            "shall be inserted, namely:—", "insert", block="“(hi) an invented asset;”.")
    assert fields(r) == ("clause (42) > Explanation 1 > clause (i) > sub-clause (hh)", "after", "(hi)", "unit")
    r = loc("(iii) in the second proviso, after the words “had been made”, the words “in an invented year” shall be "
            "inserted;", "insert", heads=(ROOT, "(b) in clause (42),—"))
    assert fields(r) == ("clause (42) > proviso[2]", "after", "", "words")
    r = loc("(c) in the second long line, in sub-clause (E), for item (II), the following item shall be substituted, "
            "namely:—", "substitute")
    assert r["target_unit"] == "long line[2] > sub-clause (E) > item (II)"


def test_proviso_or_explanation_after_leading_label_not_listed():
    blk = "'(9A) alpha means: Provided that beta is invented. Explanation.—Gamma is invented.';"
    assert ap.block_new_units(blk) == ["(9A)"]
    assert ap.block_new_units("“Provided that x: Provided further that y.”") == ["proviso", "proviso"]
    assert ap.block_new_units("‘Explanation 2.—An invented note.’") == ["Explanation 2"]
    assert ap.block_new_units("“(xviic) one invented sum; (xviid) another invented sum;”") == ["(xviic)", "(xviid)"]


def test_successors():
    assert "XIII" in ap.successors("XII") and "xiii" in ap.successors("xii")
    assert ap.successors("xviib") == ["xviic"]
    assert "48" in ap.successors("47") and "47B" in ap.successors("47A")
    assert {"iii", "ij"} <= set(ap.successors("ii"))


# ---------------------------------------------------------------- unparsed -> fail, never guess

@pytest.mark.parametrize("own,op,heads,block,why", [
    ("(d) in clause (12), the words “theta” shall be rearranged;", "other", (ROOT,), "", "no_single_operation"),
    ("(z) the following clause shall be substituted, namely:—", "substitute", ("9. In section 7 of the Zeta Act,—",),
     "'(1) x'", "no_anchor"),
    ("(i) for the words “pi”, the following shall be substituted, namely:—", "substitute", (ROOT,), "'(1) x'",
     "words_and_unit_object"),
    ("(i) in item (A), the word “pi” shall be omitted;", "omit", (ROOT, "(a) after clause (3),—"), "",
     "positional_phrase_in_header"),
    ("(c) after clause (9), the following shall be inserted, namely:—", "insert", (ROOT,), "‘an unlabelled text’",
     "no_new_units"),
])
def test_unclassified_rows_fail_with_reason(own, op, heads, block, why):
    r = loc(own, op, heads=heads, block=block)
    assert (r["check_status"], r["check_note"]) == ("fail", f"unparsed:{why}")
    assert fields(r) == ("", "", "", "")


# ---------------------------------------------------------------- columns, owner_target, merge

def test_columns_and_owner_target_is_an_owner_column():
    c = ap.EFFECT_COLUMNS
    assert c[c.index("target_unit") + 1:c.index("target_unit") + 4] == ["position", "new_units", "scope"]
    assert c[-3:] == ["owner_ok", "owner_note", "owner_target"]
    assert "owner_target" in ap.OWNER_COLUMNS
    assert {"check_status", "check_note"} <= set(c)


def test_merge_keeps_owner_target():
    old = [{"effect_id": "x:s1", "target_unit": "clause (1)", "owner_ok": "yes", "owner_note": "",
            "owner_target": "clause (1) > item (a)"}]
    new = [{"effect_id": "x:s1", "target_unit": "clause (1)", "owner_ok": "", "owner_note": "", "owner_target": ""}]
    merged, _ = ap.merge_preview(old, new, "effect_id", ["effect_id", "target_unit", "owner_ok", "owner_note",
                                                         "owner_target"])
    assert merged[0]["owner_target"] == "clause (1) > item (a)"


def test_owner_split_rows_take_their_own_clause():
    own = ("(c) sub-section (6) shall be renumbered as sub-section (6)(a) thereof and after sub-section (6)(a) as so "
           "renumbered, the following sub-section shall be inserted, namely:—")
    by_op = {o: loc(own, o, block="“(b) invented.”;") for o in ("renumber", "insert")}
    row = dict({c: "" for c in ap.EFFECT_COLUMNS}, effect_id="zz:s1(c)", operation="other", assent_date="2099-03-30",
               **loc(own, "other"))
    res = {"rows": [row], "review": [{"effect_id": "zz:s1(c)", "flags": ["multi_verb"], "loc_by_op": by_op}]}
    ap.apply_owner_splits(res, {"zz:s1(c)": {"date": "2099-01-01", "wef": "2099-04-01",
                                             "operations": ["renumber", "insert"], "owner_note": "n"}})
    got = {r["effect_id"]: (r["target_unit"], r["position"], r["new_units"]) for r in res["rows"]}
    assert got == {"zz:s1(c)/renumber": ("sub-section (6)", "in", ""),
                   "zz:s1(c)/insert": ("sub-section (6)(a)", "after", "(b)")}


# ---------------------------------------------------------------- _inserts_section unchanged (owner decision 3)

PINNED = {"fa_2022:s28", "fa_2022:s60", "fa_2025_gz:s90"}


def test_inserts_section_pinned_on_canonical_ledger():
    rows = ap.read_csv(ap.EFFECTS_PATH)
    assert {r["effect_id"] for r in rows if sb._inserts_section(r)} == PINNED


# ---------------------------------------------------------------- real ids (local PDFs; skipped in CI)

def _have(keys):
    return all((se.RAW_DIR / ss.INSTRUMENTS[k][0] / ss.INSTRUMENTS[k][1]).exists() for k in keys)


@pytest.fixture(scope="module")
def real():
    keys = ["fa_2022", "fa_2023", "fa_2025_gz"]
    if not _have(keys):
        pytest.skip("local instrument PDFs not present")
    out = {}
    for k in keys:
        r = ap.parse_instrument(k)
        ap.apply_owner_splits(r)
        out.update({row["effect_id"]: row for row in r["rows"]})
    return out


REAL = {
    "fa_2022:s3(a)": ("clause (12A)", "for", "", "words"),
    "fa_2022:s3(b)": ("clause (42C)", "for", "", "words"),
    "fa_2022:s3(c)": ("clause (47)", "after", "(47A)", "unit"),
    "fa_2022:s16(a)": ("sub-section (2) > clause (viib) > Explanation > clause (aa)", "after", "", "words"),
    "fa_2022:s16(b)(i)": ("sub-section (2) > clause (x) > proviso[1] > clause (XI)", "after", "(XII);(XIII)", "unit"),
    "fa_2022:s16(b)(ii)": ("sub-section (2) > clause (x) > sub-clause (c) > proviso[1]", "after", "proviso", "unit"),
    "fa_2023:s3(a)": ("clause (19B)", "in", "", "words"),
    "fa_2023:s3(b)": ("clause (24) > sub-clause (xviib)", "after", "(xviic);(xviid)", "unit"),
    "fa_2023:s3(c)": ("clause (28C)", "after", "(28CA)", "unit"),
    "fa_2023:s3(d)": ("clause (37A) > sub-clause (ii)", "after", "", "words"),
    "fa_2023:s3(e)": ("clause (42A) > Explanation 1 > clause (i) > sub-clause (hh)", "after", "(hi)", "unit"),
}


@pytest.mark.parametrize("eid", sorted(REAL))
def test_real_ids(real, eid):
    assert fields(real[eid]) == REAL[eid]
    assert real[eid]["check_status"] == ""


def test_real_inserts_section_and_whole_section_new_units(real):
    assert {e for e, r in real.items() if sb._inserts_section(r)} == PINNED
    assert real["fa_2022:s28"]["new_units"] == "115BBH;115BBI"


def test_real_quote_sha_unchanged(real):
    canon = {r["effect_id"]: r for r in ap.read_csv(ap.EFFECTS_PATH)}
    for eid, r in real.items():
        for c in ("quote_sha256", "wef", "deemed_from", "commencement_source", "operation"):
            assert r[c] == canon[eid][c], (eid, c)
