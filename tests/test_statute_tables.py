"""Tests for divergence/statute_tables.py (P09 Part C3). INVENTED data only; no real law text, no network."""
from divergence import act_parse as ap
from divergence import statute_build as sb
from divergence import statute_tables as st

QUOTE = "(b) in clause (9), for the word \"delta\", the word \"epsilon\" shall be substituted"
PAGE = "3. In section 7 of the Zeta Act,— (a) in clause (4), with effect from the 1st day of October, 2099,— " \
       "(i) other words; " + QUOTE + ";"


def eff(**kw):
    r = {"effect_id": "zz_2099:s3(b)", "act_key": "Act No. 9 of 2099", "operation": "substitute",
         "commencement_source": "s1_default", "wef": "2099-04-01", "deemed_from": "", "assent_date": "2099-03-30",
         "applicability_note_present": "no", "corrigendum_flag": "no", "pdf_page": "2",
         "quote_sha256": ap.quote_sha256(QUOTE), "owner_ok": "yes", "owner_note": ""}
    r.update(kw)
    return r


def ver(**kw):
    r = {"record_key": "act:1961:7:v1", "in_force_from": "2099-04-01", "in_force_to": "", "state": "in_force",
         "effect_ids": "zz_2099:s3(b)", "reason_codes": "", "code_note": "effect_start; text = e1",
         "applies_from_tax_year": "2099-00", "applies_to_tax_year": "", "basis_category": "charging_ay_rule",
         "basis": "invented one-line basis", "owner_ok": "yes", "owner_note": ""}
    r.update(kw)
    return r


def check_e(rows, quotes=None, text=PAGE):
    return dict(st.check_effects(rows, quotes or {"zz_2099:s3(b)": QUOTE}, text_of=lambda k, p: text))


def test_effect_accepted_and_owner_ok_required(monkeypatch):
    monkeypatch.setitem(st.ss.INSTRUMENTS, "zz_2099", ("x", "y", "act", "gazette", None))
    assert check_e([eff()]) == {"zz_2099:s3(b)": []}
    assert "owner_ok '' not in yes/fix" in check_e([eff(owner_ok="")])["zz_2099:s3(b)"]
    assert "owner_ok fix needs owner_note" in check_e([eff(owner_ok="fix")])["zz_2099:s3(b)"]


def test_effect_quote_hash_and_verbatim(monkeypatch):
    monkeypatch.setitem(st.ss.INSTRUMENTS, "zz_2099", ("x", "y", "act", "gazette", None))
    w = check_e([eff()], {"zz_2099:s3(b)": QUOTE + " extra"})["zz_2099:s3(b)"]
    assert "quote_sha256 does not match the local quote" in w
    assert any("not verbatim" in x for x in w)


def test_quote_pieces_for_header_inherited_quote():
    header = "(a) in clause (4), with effect from the 1st day of October, 2099,—"
    assert st.quote_pieces(header + " " + QUOTE, PAGE) == [header, QUOTE]
    assert st.quote_pieces("words that are nowhere", PAGE) is None
    assert st.quote_pieces(QUOTE.replace(" ", "  "), PAGE) == [QUOTE]          # whitespace-only fold


def test_effect_date_rules(monkeypatch):
    monkeypatch.setitem(st.ss.INSTRUMENTS, "zz_2099", ("x", "y", "act", "gazette", None))
    w = check_e([eff(wef="2098-04-01")])["zz_2099:s3(b)"]
    assert "wef before assent: deemed_from must equal wef" in w
    assert check_e([eff(wef="2098-04-01", deemed_from="2098-04-01")])["zz_2099:s3(b)"] == []
    assert any("not YYYY-MM-DD" in x for x in check_e([eff(wef="1-4-2099")])["zz_2099:s3(b)"])


def test_version_checks():
    effs = {"zz_2099:s3(b)": eff()}
    ok = ver(applies_from_tax_year="2099-00")
    assert dict(st.check_versions([ok], effs))["act:1961:7:v1"] == []
    bad = dict(st.check_versions([ver(applies_from_tax_year="2099-01", basis_category="effect_start",
                                      state="AMBIGUOUS")], effs))["act:1961:7:v1"]
    assert any("tax year second part" in x for x in bad)
    assert any("basis_category 'effect_start'" in x for x in bad)
    assert any("state 'AMBIGUOUS'" in x for x in bad)
    unclear = dict(st.check_versions([ver(basis_category="unclear")], effs))["act:1961:7:v1"]
    assert "basis_category unclear: applies_from/to must be empty" in unclear
    need = dict(st.check_versions([ver(applies_from_tax_year="")], effs))["act:1961:7:v1"]
    assert "in force: applies_from_tax_year needed, or basis_category unclear" in need


def test_version_d78_v07_never_operative_dates():
    w = dict(st.check_versions([ver(state="never_operative", applies_from_tax_year="", basis_category="unclear",
                                    in_force_to="2099-04-01")], {}))["act:1961:7:v1"]
    assert any(x.startswith("V07: never_operative needs in_force_from null") for x in w)


def test_version_v08_from_effects():
    effs = {"zz_2099:s3(b)": eff(wef="2098-04-01", deemed_from="2098-04-01")}
    rec = st._record(ver(reason_codes="retro_knowledge"), effs)
    want = ("2098-04-01", "2099-03-30", ["Act No. 9 of 2099"])
    assert (rec["retrospective_from"], rec["enacted_on"], rec["amended_by"]) == want


def test_merge_takes_current_owner_columns_and_sha_guard(tmp_path):
    canon = tmp_path / "VERSION-DATES.csv"
    cols = sb.VERSION_COLUMNS
    old = [ver(code_note="", basis_category="procedural", basis="owner basis", owner_ok="yes"),
           ver(record_key="act:1961:7:v2", basis_category="effect_start", basis="text = e1", owner_ok="")]
    canon.write_text(ap.csv_text(old, cols), encoding="utf-8")
    stamped = tmp_path / "VERSION-DATES.20990101-000000.csv"
    new = [ver(code_note="effect_start; text = e2", basis_category="", basis="", owner_ok="", applies_from_tax_year=""),
           ver(record_key="act:1961:7:v2", code_note="x", basis_category="", basis="", owner_ok="")]
    stamped.write_text(ap.csv_text(new, cols), encoding="utf-8")
    merged, columns, preview = st.merge(stamped, canon)
    m = {r["record_key"]: r for r in merged}
    assert m["act:1961:7:v1"]["basis"] == "owner basis" and m["act:1961:7:v1"]["code_note"] == "effect_start; text = e2"
    assert m["act:1961:7:v2"]["basis_category"] == "" and any("not an owner value" in x for x in preview)
    assert st.main(["--merge", str(stamped), "--into", str(canon), "--canonical-sha", "0" * 64]) == 1
    sha = st.sha256_path(canon)
    assert st.main(["--merge", str(stamped), "--into", str(canon), "--canonical-sha", sha]) == 0
    assert st.sha256_path(canon) != sha
