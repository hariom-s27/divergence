"""Tests for divergence/statute_tables.py (P09 Part C3). INVENTED data only; no real law text, no network."""
import pytest

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


def owner_files(tmp_path, kind="effect", state="in_force", note_column=True):
    if kind == "effect":
        canonical = tmp_path / "AMENDMENT-EFFECTS.csv"
        columns = ap.EFFECT_COLUMNS
        rows = [eff(owner_ok="", target_unit="clause (9)", owner_target=""),
                eff(effect_id="zz_2099:s4", owner_ok="", owner_target="")]
        fields = ["effect_id", "owner_ok", "owner_note", "owner_target"]
        decision = {"effect_id": rows[0]["effect_id"], "owner_ok": "fix", "owner_note": "invented correction",
                    "owner_target": "clause (8)"}
    else:
        canonical = tmp_path / "VERSION-DATES.csv"
        columns = [c for c in sb.VERSION_COLUMNS if note_column or c != "owner_note"]
        rows = [ver(owner_ok="", state=state), ver(record_key="act:1961:7:v2", owner_ok="")]
        fields = ["record_key", "applies_from_tax_year", "applies_to_tax_year", "basis_category", "basis", "owner_ok"]
        decision = {c: ver()[c] for c in fields}
    canonical.write_text(ap.csv_text(rows, columns), encoding="utf-8")
    decisions = tmp_path / "decisions.csv"
    decisions.write_text(ap.csv_text([decision], fields), encoding="utf-8")
    return canonical, decisions, columns, fields, decision


@pytest.mark.parametrize("kind", ["effect", "version"])
def test_apply_owner_valid_changes_only_owner_cells(tmp_path, kind):
    canonical, decisions, columns, fields, decision = owner_files(tmp_path, kind)
    before = canonical.read_bytes()
    original = ap.read_csv(canonical)
    regen = tmp_path / "regen"
    output, count, changed, hashes = st.apply_owner(decisions, canonical, regen)
    assert output.parent == regen and count == 2 and changed == 1
    assert canonical.read_bytes() == before
    rows = ap.read_csv(output)
    assert list(rows[0]) == columns and rows[1] == original[1]
    for c in fields:
        assert rows[0][c] == decision[c]
    owner = st.canonical_spec(canonical)[1]
    assert hashes == st.non_owner_hashes(original, columns, owner) == st.non_owner_hashes(rows, columns, owner)


@pytest.mark.parametrize("case, message", [
    ("unknown_effect", "unknown effect_id"),
    ("unknown_version", "unknown record_key"),
    ("duplicate_effect", "duplicate effect_id"),
    ("duplicate_version", "duplicate record_key"),
    ("empty_key", "empty or duplicate"),
    ("owner_ok_effect", "owner_ok must be yes or fix"),
    ("owner_ok_version", "owner_ok must be yes or fix"),
    ("fix_effect", "fix needs owner_note"),
    ("fix_version", "fix needs owner_note"),
    ("year_format", "YYYY-YY"),
    ("year_consecutive", "consecutive years"),
    ("year_to", "YYYY-YY"),
    ("category", "basis_category"),
    ("unclear_from", "unclear requires empty"),
    ("unclear_to", "unclear requires empty"),
    ("never_operative", "never_operative / empty state"),
    ("empty_state", "never_operative / empty state"),
    ("code_column", "unknown or unavailable decision columns"),
    ("missing_column", "decisions missing columns"),
    ("duplicate_header", "duplicate column names"),
    ("row_width", "row width"),
    ("no_decisions", "no rows"),
    ("wrong_key", "exactly one key column"),
    ("duplicate_canonical", "canonical: empty or duplicate"),
])
def test_apply_owner_invalid_batch_writes_nothing(tmp_path, case, message):
    kind = "effect" if case.endswith("effect") or case in ("empty_key", "code_column", "missing_column",
                                                          "duplicate_header", "row_width", "no_decisions",
                                                          "wrong_key", "duplicate_canonical") else "version"
    state = "never_operative" if case == "never_operative" else "" if case == "empty_state" else "in_force"
    canonical, decisions, columns, fields, decision = owner_files(tmp_path, kind, state)
    key = fields[0]
    if case.startswith("unknown_"):
        decision[key] = "invented:missing"
    elif case == "empty_key":
        decision[key] = ""
    elif case.startswith("owner_ok_"):
        decision["owner_ok"] = "YES"
    elif case.startswith("fix_"):
        decision.update(owner_ok="fix", owner_note="  ")
        if "owner_note" not in fields:
            fields.append("owner_note")
    elif case == "year_format":
        decision["applies_from_tax_year"] = "FY 2099-00"
    elif case == "year_consecutive":
        decision["applies_from_tax_year"] = "2099-01"
    elif case == "year_to":
        decision["applies_to_tax_year"] = "2100-2101"
    elif case == "category":
        decision["basis_category"] = "invented_invalid"
    elif case.startswith("unclear_"):
        decision["basis_category"] = "unclear"
        if case == "unclear_to":
            decision.update(applies_from_tax_year="", applies_to_tax_year="2100-01")
    elif case == "code_column":
        fields.append("target_unit")
        decision["target_unit"] = "invented forbidden code edit"
    elif case == "missing_column":
        fields.remove("owner_target")
    elif case == "duplicate_header":
        fields.append("owner_ok")
    elif case == "wrong_key":
        fields[0] = "version_id"
    elif case == "duplicate_canonical":
        rows = ap.read_csv(canonical)
        canonical.write_text(ap.csv_text(rows + [rows[0]], columns), encoding="utf-8")
    batch = [] if case == "no_decisions" else [decision]
    if case in ("duplicate_effect", "duplicate_version"):
        batch.append(dict(decision))
    if case.startswith("fix_"):
        valid = dict(decision, **{key: ap.read_csv(canonical)[1][key], "owner_ok": "yes", "owner_note": ""})
        batch.insert(0, valid)  # A valid first row must not cause a partial write.
    decisions.write_text(ap.csv_text(batch, fields), encoding="utf-8")
    if case == "row_width":
        with decisions.open("a", encoding="utf-8") as f:
            f.write("too,few\n")
    before = canonical.read_bytes()
    regen = tmp_path / "regen"
    with pytest.raises(ValueError, match=message):
        st.apply_owner(decisions, canonical, regen)
    assert canonical.read_bytes() == before and not regen.exists()


@pytest.mark.parametrize("category", sb.BASIS_CATEGORIES)
def test_apply_owner_version_closed_categories_and_rollover(tmp_path, category):
    canonical, decisions, columns, fields, decision = owner_files(tmp_path, "version")
    decision["basis_category"] = category
    decision["applies_to_tax_year"] = "2100-01"
    if category == "unclear":
        decision.update(applies_from_tax_year="", applies_to_tax_year="")
    decisions.write_text(ap.csv_text([decision], fields), encoding="utf-8")
    output, _, _, _ = st.apply_owner(decisions, canonical, tmp_path / "regen")
    assert ap.read_csv(output)[0]["basis_category"] == category


@pytest.mark.parametrize("note_column", [True, False])
def test_apply_owner_version_fix_uses_existing_note_column_only(tmp_path, note_column):
    canonical, decisions, columns, fields, decision = owner_files(tmp_path, "version", note_column=note_column)
    decision["owner_ok"] = "fix"
    if note_column:
        fields.append("owner_note")
        decision["owner_note"] = "invented correction"
    decisions.write_text(ap.csv_text([decision], fields), encoding="utf-8")
    output, _, _, _ = st.apply_owner(decisions, canonical, tmp_path / "regen")
    assert list(ap.read_csv(output)[0]) == columns
    assert ("owner_note" in ap.read_csv(output)[0]) == note_column


@pytest.mark.parametrize("stage", ["validation", "serialization"])
def test_apply_owner_hash_guard_trip_writes_nothing(tmp_path, monkeypatch, stage):
    canonical, decisions, columns, _, _ = owner_files(tmp_path)
    before = canonical.read_bytes()
    if stage == "validation":
        validate = st._validate_owner_row

        def corrupt(row, key, cols):
            validate(row, key, cols)
            row["target_unit"] = "invented accidental code edit"

        monkeypatch.setattr(st, "_validate_owner_row", corrupt)
    else:
        serialize = ap.csv_text

        def corrupt(rows, cols):
            rows = [dict(r, target_unit="invented serialization error") for r in rows]
            return serialize(rows, cols)

        monkeypatch.setattr(ap, "csv_text", corrupt)
    regen = tmp_path / "regen"
    with pytest.raises(ValueError, match="non-owner hash guard"):
        st.apply_owner(decisions, canonical, regen)
    assert canonical.read_bytes() == before and not regen.exists()


@pytest.mark.parametrize("kind", ["effect", "version"])
def test_apply_owner_cli_infers_table_and_reports_invalid_input(tmp_path, monkeypatch, capsys, kind):
    canonical, decisions, _, fields, decision = owner_files(tmp_path, kind)
    if kind == "effect":
        monkeypatch.setattr(ap, "EFFECTS_PATH", canonical)
    else:
        monkeypatch.setattr(sb, "VERSIONS_PATH", canonical)
    regen = tmp_path / "regen"
    monkeypatch.setattr(ap, "REGEN_DIR", regen)
    assert st.main(["--apply-owner", str(decisions)]) == 0
    assert "non-owner row hashes unchanged 2" in capsys.readouterr().out
    decision[fields[0]] = "invented:missing"
    decisions.write_text(ap.csv_text([decision], fields), encoding="utf-8")
    written = list(regen.iterdir())
    assert st.main(["--apply-owner", str(decisions)]) == 1
    assert "REFUSED: unknown" in capsys.readouterr().out
    assert list(regen.iterdir()) == written


@pytest.mark.parametrize("kind", ["effect", "version"])
def test_regeneration_carries_canonical_owner_and_merge_code_stays_sha_guarded(tmp_path, kind):
    canonical, _, columns, _, _ = owner_files(tmp_path, kind)
    key, owner, carry = st.canonical_spec(canonical)
    rows = ap.read_csv(canonical)
    rows[0].update(owner_ok="fix", owner_note="invented approved note")
    if kind == "effect":
        rows[0]["owner_target"] = "clause (8)"
    canonical.write_text(ap.csv_text(rows, columns), encoding="utf-8")
    canonical_bytes = canonical.read_bytes()
    sha = st.sha256_path(canonical)
    regenerated = [dict(r) for r in rows]
    code_column = "target_unit" if kind == "effect" else "code_note"
    regenerated[0][code_column] = "invented regenerated code value"
    for row in regenerated:
        row.update({c: "" for c in owner if c in columns})
    stamped, _ = ap.write_never_overwrite(canonical, regenerated, columns, key, owner=owner, carry=carry,
                                        regen_dir=tmp_path / "regen")
    assert canonical.read_bytes() == canonical_bytes
    generated = ap.read_csv(stamped)
    assert all(generated[0][c] == rows[0][c] for c in owner if c in columns)
    assert generated[0][code_column] == "invented regenerated code value"
    assert st.main(["--merge", str(stamped), "--into", str(canonical), "--canonical-sha", "0" * 64]) == 1
    assert canonical.read_bytes() == canonical_bytes
    assert st.main(["--merge", str(stamped), "--into", str(canonical), "--canonical-sha", sha]) == 0
    assert ap.read_csv(canonical) == generated
