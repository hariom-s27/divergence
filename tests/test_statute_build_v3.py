"""P09D v3 rules and metadata updates; invented strings and temporary roots only."""
import contextlib
import copy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import pytest
from divergence import act_parse as ap, statute_build as sb, statute_ingest as si
from divergence import statute_records as sr, statute_sources as ss


@pytest.mark.parametrize(
    'knowledge,expected',
    [
        (
            '2026-03-30',
            '2026-04-01'
        ),
        (
            '2026-04-01',
            '2026-04-01'
        ),
        (
            '2026-04-02',
            '2027-04-01'
        ),
        (
            '2026-12-31',
            '2027-04-01'
        )
    ]
)
def test_r2_first_april(knowledge, expected):
    assert sb.v3_first_april(knowledge).isoformat() == expected


@pytest.mark.parametrize(
    'assent,wef,expected',
    [
        (
            '2026-03-30',
            '2026-04-01',
            True
        ),
        (
            '2026-03-31',
            '2026-04-01',
            False
        ),
        (
            '2026-03-30',
            '2027-04-01',
            False
        ),
        (
            '2025-12-01',
            '2026-03-30',
            True
        )
    ]
)
def test_r2_two_dates(assent, wef, expected):
    assert sb.v3_effect_in_date({'assent_date': assent, 'wef': wef}, '2026-03-30') is expected


@pytest.mark.parametrize(
    'a,b,expected',
    [
        (
            'widget',
            'widgets',
            True
        ),
        (
            'box',
            'boxes',
            True
        ),
        (
            'category',
            'categories',
            True
        ),
        (
            'key',
            'keys',
            True
        ),
        (
            'index',
            'indices',
            True
        ),
        (
            'children',
            'child',
            True
        ),
        (
            'one',
            'ones',
            False
        ),
        (
            '1',
            '1s',
            False
        ),
        (
            'first',
            'firsts',
            False
        ),
        (
            'ox',
            'oxen',
            False
        ),
        (
            'widget',
            'gadget',
            False
        )
    ]
)
def test_plural_preregistered(a, b, expected):
    assert sb.v3_plural(a, b) is expected


@pytest.mark.parametrize(
    'text,expected',
    [
        (
            'Start. Invented heading. End.',
            'Start. End.'
        ),
        (
            'Inside Invented heading in prose.',
            'Inside Invented heading in prose.'
        ),
        (
            'Start. invented heading. End.',
            'Start. invented heading. End.'
        )
    ]
)
def test_r1_sentence_only(text, expected):
    result, locations = sb._v3_margin(text, list(range(len(text))), ['Invented heading'])
    assert result == expected
    assert len(locations) == len(result)


def test_r4_complete_rows_only():
    texts = ['A', 'B', 'Invented A within prose', 'A + B', 'A B C']
    lines = [SimpleNamespace(page=1, line=i + 1, text=t) for i, t in enumerate(texts)]
    assert sb._v3_furniture_rows(lines) == {(1, 1), (1, 2), (1, 5)}
    assert sb._v3_furniture_rows([SimpleNamespace(page=1, line=1, text='A')]) == set()


def test_r3_ambiguous_unit_stays_unanchored():
    effect = {'target_unit': 'sub-section (2)', 'scope': 'unit', 'target_section': '77'}
    assert sb._v3_legacy_effect_scope('(2) invented. (2) duplicate.', effect, ap, sb) is None
    assert sb._v3_legacy_effect_scope('(1) first. (2) invented.', effect, ap, sb) is not None


def test_r5_only_authorized_markup():
    assert sb.v3_itd_markup('x [***] y [z] (7 of 2099)') == 'x y z'
    assert sb.v3_itd_markup('(2099) 17 (invented)') == '(2099) 17 (invented)'


class Resource(dict):

    def get_object(self):
        return self


def test_r6_images_and_nested_forms():
    image = Resource({'/Subtype': '/Image'})
    resources = Resource({'/XObject': Resource({'/one': image})})
    form = Resource({'/Subtype': '/Form', '/Resources': resources})
    assert sb.v3_image_on_page({'/Resources': Resource({'/XObject': Resource({'/form': form})})})
    assert not sb.v3_image_on_page({'/Resources': Resource({})})


@pytest.mark.parametrize(
    'old,new,image,nature',
    [
        (
            'invented,',
            'invented;',
            False,
            'accidental'
        ),
        (
            'widget',
            'widgets',
            False,
            'accidental'
        ),
        (
            '(a)',
            '(b)',
            False,
            'accidental'
        ),
        (
            '10',
            '11',
            False,
            'substantive'
        ),
        (
            'Q + R = S',
            '',
            True,
            'accidental'
        ),
        (
            'Q + R = S',
            '',
            False,
            'substantive'
        ),
        (
            'invented missing prose',
            '',
            True,
            'substantive'
        )
    ]
)
def test_nature_codebook(old, new, image, nature):
    hunk = {'old': old, 'new': new}
    before = copy.deepcopy(hunk)
    assert sb.v3_nature(hunk, image=image)[0] == nature
    assert hunk == before


def test_spelling_requires_certificate():
    hunk = {'old': 'widgte', 'new': 'widget'}
    assert sb.v3_nature(hunk)[0] == 'substantive'
    assert sb.v3_nature(hunk, spelling_pairs=[('widgte', 'widget')])[0] == 'accidental'


def test_editor_crosscheck_does_not_change_r2():
    effect = {
        'effect_id': 'fake:s1',
        'target_unit': 'sub-section (2)',
        'act_key': 'fake',
        'wef': '2027-04-01',
        'assent_date': '2026-03-30'
    }
    result = {'editor_notes': [{'text': '(2) invented note w.e.f. 1-4-2027'}]}
    assert sb._v3_editor_crosscheck(effect, result)['editor_note'] == 'yes'
    assert not sb.v3_effect_in_date(effect, '2026-03-30')
    assert sb._v3_editor_crosscheck(effect, {'editor_notes': []})['editor_note'] == 'no'


def test_reconciliation_uses_coordinates_not_repeated_words():
    assert sb._v3_related({'section': '77', 'span': (3, 5)}, {'section': '77', 'span': (4, 6)})
    assert not sb._v3_related({'section': '77', 'span': (3, 5)}, {'section': '77', 'span': (8, 10)})
    assert sb._v3_related({'section': '77', 'span': (3, 3)}, {'section': '77', 'span': (3, 3)})


def disposition(timing='pre_commencement', kind='typo'):
    start = '2099-04-01'
    return {
        'item_key': 'corr_fake:p1l1',
        'section': '77',
        'unit': '(2)',
        'record_ids': 'fake',
        'old_sha16': 'a' * 16,
        'new_sha16': 'b' * 16,
        'corrigendum_date': '2099-03-01'
        if timing == 'pre_commencement' else start,
        'provision_commencement': start,
        'commencement_source': 'fake',
        'timing': timing,
        'class': kind,
        'owner_ok': 'yes',
        'owner_note': ''
    }


def fake_record():
    return {
        'record_id': 'act:2025:77:v1',
        'act': '2025',
        'section': '77',
        'lookup_flags': [
            'corrigendum_open'
        ],
        'amended_by': [

        ],
        'body': '',
        'body_chars': 0,
        'body_sha256': hashlib.sha256(
            b''
        ).hexdigest(

        )
    }


@pytest.mark.parametrize(
    'timing,kind,opened',
    [
        (
            'pre_commencement',
            'substantive',
            False
        ),
        (
            'post_commencement',
            'typo',
            False
        ),
        (
            'post_commencement',
            'substantive',
            True
        )
    ]
)
def test_timing_class_policy(timing, kind, opened):
    rec = fake_record()
    original = {k: rec[k] for k in ('body', 'body_chars', 'body_sha256')}
    sr.apply_dispositions(rec, [disposition(timing, kind)])
    assert ('corrigendum_open' in rec['lookup_flags']) is opened
    assert {k: rec[k] for k in original} == original
    if not opened:
        assert 'corrigendum_applied:' in rec['notes']


def test_missing_and_uncovered_reason_kept():
    rec = fake_record()
    sr.apply_dispositions(rec, [])
    assert rec['lookup_flags'] == ['corrigendum_open']
    sr.apply_dispositions(rec, [disposition()], uncovered_reason=True)
    assert rec['lookup_flags'] == ['corrigendum_open']


def test_notes_idempotent_and_original_first():
    rec = fake_record()
    rec['notes'] = 'invented source note; retained metadata'
    a, b = (disposition(), disposition())
    b['item_key'] = 'corr_fake:p2l1'
    sr.apply_dispositions(rec, [b, a])
    before = rec['notes']
    sr.apply_dispositions(rec, [a, b])
    assert rec['notes'] == before
    assert before.startswith('invented source note; retained metadata; ')
    assert before.index(a['item_key']) < before.index(b['item_key'])


def test_amending_correction_follows_effect_not_section():
    row = disposition()
    row['item_key'] = 'corr_fa2023:p29l1'
    first, second = (fake_record(), fake_record())
    first.update(act='1961', section='56')
    second.update(act='1961', section='56', amended_by=[{'ref': 'fa_2023:s32(b)'}])
    assert not sr.disposition_touches(row, first)
    assert sr.disposition_touches(row, second)


@pytest.mark.parametrize('change', ['body_chars', 'body_sha256', 'unit'])
def test_update_refuses_body_and_unapproved_fields(change):
    old = fake_record()
    new = copy.deepcopy(old)
    new[change] = 'invented different'
    with pytest.raises(ValueError):
        si.plan_update([old], [new])


def test_update_dry_run_writes_nothing(tmp_path, monkeypatch):
    root = tmp_path / 'fake-root'
    path = root / 'records/2025/act__2025__77__v1.json'
    path.parent.mkdir(parents=True)
    old = fake_record()
    old.update(status='unprinted', body=None, body_chars=None, body_sha256=None, storage_mode='local_only')
    path.write_bytes(si.json_bytes(old))
    raw = path.read_bytes()
    new = dict(old, notes='invented approved metadata')
    monkeypatch.setattr(si, 'prepare', lambda root: ([new], {}, {}))
    monkeypatch.setattr(ss, 'existing_local_sources', contextlib.nullcontext)
    changes, records, evidence = si.update_records(root)
    assert path.read_bytes() == raw
    assert len(changes) == 1
    assert list(root.rglob('*.json')) == [path]


@pytest.mark.skipif(os.environ.get('P09D_REAL_V3_REGRESSION') != '1', reason='explicit local evidence run only')
def test_local_v3_regression():
    import io
    selected = os.environ.get('P09D_V3_EXPECTED_PATH')
    if not selected:
        pytest.skip('select an immutable local capsule fixture explicitly')
    expected_path = Path(selected)
    expected = json.loads(expected_path.read_text(encoding='utf-8'))
    root = se_root = sb.se.STATUTES_DIR
    baseline = root / '_local_text/census/partD/20261119-172809/ITD-GAZETTE-DIFFS.v2.csv'
    with ss.existing_local_sources(), contextlib.redirect_stdout(io.StringIO()):
        actual = sb.gazette_check_v3(
            sb.se.latest_raw_dir(

            ),
            ap.read_csv(
                baseline
            ),
            ap.read_csv(
                se_root / 'CORRIGENDUM-DISPOSITION.csv'
            )
        )
    for key, value in actual.items():
        assert expected[key] == value


def test_cache_miss_refuses_original_extractor(tmp_path, monkeypatch):
    calls = []

    def original(*args):
        return calls.append(args)
    monkeypatch.setattr(sb.se, "load_pages", original)
    monkeypatch.setattr(sb.se, "file_sha256", lambda p: "a" * 64)
    monkeypatch.setattr(sb.se, "pypdf_version", lambda: "invented")
    with ss.existing_local_sources():
        with pytest.raises(ValueError, match="CACHE MISS"):
            sb.se.load_pages(tmp_path / "invented.pdf", tmp_path)
    assert sb.se.load_pages is original and not calls


@pytest.mark.parametrize("image", [True, False])
def test_r6_never_removes_row(monkeypatch, image, tmp_path):
    from pypdf import PdfReader
    import pypdf
    del PdfReader
    page = {"/Resources": Resource({"/XObject": Resource(
        {"/one": Resource({"/Subtype": "/Image"})} if image else {})})}
    monkeypatch.setattr(pypdf, "PdfReader", lambda path: SimpleNamespace(pages=[page]))
    monkeypatch.setattr(sb, "_v3_mapped_pages", lambda *args: [1])
    monkeypatch.setattr(sb.se, "latest_raw_dir", lambda: tmp_path)
    entry = {"section": "77", "span": (0, 0), "hunk": {
        "key": "a" * 16, "old": "Q + R = S", "new": "", "ob": "", "oa": "", "nb": "", "na": ""}}
    stages = [("R" + str(i), [entry]) for i in range(1, 6)]
    rows, reasons = sb._v3_rows([entry], stages, [], None, None, [])
    assert rows[0]["status"] == "kept"
    assert rows[0]["image_on_page"] == ("yes" if image else "no")


def test_repair_r3_validated_scope_survives_repeated_labels():
    text = '(2) invented anchor. (2) invented anchor.'
    effect = {'target_unit': 'sub-section (2)', 'scope': 'words', 'target_section': '77'}
    override = (0, text.index(' (2)'))
    assert sb._v3_legacy_effect_scope(text, effect, ap, sb) is None
    assert sb._v3_validated_scope(text, effect, override) == (override, '')
    assert len(sb._v3_legacy_literal_word_hits(text, 'invented')) == 2
    assert len(sb._v3_legacy_literal_word_hits(text[override[0]:override[1]], 'invented')) == 1


def test_repair_r3_conflicting_or_invalid_witness_rejected():
    text = '(1) first. (2) second. (3) third.'
    effect = {'target_unit': 'sub-section (2)', 'scope': 'unit', 'target_section': '77'}
    assert sb._v3_validated_scope(text, effect, (0, 4)) == (None, 'scope_conflict')
    assert sb._v3_validated_scope(text, effect, (-1, 4)) == (None, 'invalid_scoped_witness')
    duplicate = '(2) first. (2) second.'
    assert sb._v3_validated_scope(duplicate, effect, None) == (None, 'target_not_unique')


def test_repair_r3_contained_witness_is_compatible():
    text = '(1) first. (2) second. (3) third.'
    effect = {'target_unit': 'sub-section (2)', 'scope': 'unit', 'target_section': '77'}
    scope = sb._v3_legacy_effect_scope(text, effect, ap, sb)
    inside = (scope[0] + 1, scope[1] - 1)
    assert sb._v3_validated_scope(text, effect, inside) == (inside, '')


def fake_section(text, heading=''):
    return {'body': text, 'heading': heading, 'internal_heading_line_idx0': 0,
            'internal_line_idx0_end': len(text.splitlines())}


def fake_view(text):
    lines = [SimpleNamespace(page=1, line_no=i + 1, text=value) for i, value in enumerate(text.splitlines())]
    return SimpleNamespace(cleaned=SimpleNamespace(lines=lines))


def test_repair_c3_preparation_retained():
    result = fake_section('Invented heading\nalpha\u00a0[beta] gamma', 'Invented heading')
    words = sb.se.fold_for_diff(result['body']).split()
    heading = sb.se.fold_for_diff(result['heading']).split()
    assert sb._v3_body(result) == ' '.join(words[len(heading):])


@pytest.mark.parametrize('markup', [False, True])
def test_repair_r4_both_sides_and_original_token_map(markup):
    result = fake_section('Heading\nalpha\nA B C\nomega', 'Heading')
    prepared, roots = sb._v3_itd_prepared(result, fake_view(result['body']), True)
    assert prepared == 'alpha omega'
    assert roots == [(0, 1), (4, 5)]
    assert sb._v3_compare_section('alpha omega', result, '77', view=fake_view(result['body']),
                                  furniture=True, markup=markup) == []


def test_repair_r4_isolated_formula_variable_kept():
    result = fake_section('alpha\nA\nomega')
    prepared, _ = sb._v3_itd_prepared(result, fake_view(result['body']), True)
    assert prepared == 'alpha A omega'
    assert len(sb._v3_compare_section('alpha omega', result, '77', view=fake_view(result['body']),
                                      furniture=True, markup=True)) == 1


def test_repair_r5_c3_furniture_certificate_survives_brackets():
    result = fake_section('alpha [Table 1 Sl. 1] omega')
    assert sb._v3_compare_section('alpha omega', result, '77') == []
    assert sb._v3_compare_section('alpha omega', result, '77', markup=True) == []


def test_repair_r5_furniture_beside_real_word_change():
    padding = ' '.join('padding' + str(i) for i in range(24))
    old = 'alpha red ' + padding + ' omega'
    result = fake_section('alpha blue ' + padding + ' [Table 1 Sl. 1] omega')
    entries = sb._v3_compare_section(old, result, '77', markup=True)
    assert len(entries) == 1
    assert entries[0]['hunk']['old'] == 'red'
    assert entries[0]['hunk']['new'] == 'blue'


def test_repair_r5_shared_reference_creates_no_content_but_real_omission_stays():
    old = 'alpha (7 of 2099) omega'
    assert sb._v3_compare_section(old, fake_section(old), '77', markup=True) == []
    assert len(sb._v3_compare_section(old, fake_section('alpha omega'), '77', markup=True)) == 1


def repeated_entries():
    left = ' '.join('left' + str(i) for i in range(sb.CTX_WORDS + 2))
    right = ' '.join('right' + str(i) for i in range(sb.CTX_WORDS + 2))
    segment = left + ' red ' + right
    old = 'start ' + segment + ' middle ' + segment + ' end'
    new = old.replace(' red ', ' blue ')
    return sb._v3_compare_section(old, fake_section(new), '77', markup=True)


def test_repair_occurrence_keys_include_absolute_positions_and_section():
    entries = repeated_entries()
    assert len(entries) == 2
    assert entries[0]['hunk']['key'] == entries[1]['hunk']['key']
    keys = [sb._v3_occurrence_key(e) for e in entries]
    assert len(set(keys)) == 2
    assert keys == [sb._v3_occurrence_key(e) for e in repeated_entries()]
    other = dict(entries[0], section='78')
    assert sb._v3_occurrence_key(other) not in keys
    gap = dict(entries[0], span=(3, 3))
    another_gap = dict(gap, span=(4, 4))
    assert sb._v3_occurrence_key(gap) != sb._v3_occurrence_key(another_gap)


def test_repair_reconciliation_consumes_only_matching_occurrence():
    entries = repeated_entries()
    stages = [('R' + str(i), entries) for i in range(1, 6)]
    rows, reasons = sb._v3_rows([entries[0]], stages, [], None, None, [])
    assert len(rows) == 2
    assert rows[0]['row_id'] == 'v2:' + entries[0]['hunk']['key']
    assert rows[1]['row_id'] == 'v3:' + sb._v3_occurrence_key(entries[1])
    assert all(row['status'] == 'kept' and not row['owner_ok'] for row in rows)
    assert len(reasons) == 2
    proof = sb._V3_RESULTS['occurrence_reconciliation']
    assert proof['all_covered'] and proof['covered_occurrences'] == 2


def test_repair_new_rows_repeated_context_have_unique_ids():
    entries = repeated_entries()
    rows, _ = sb._v3_rows([], [('R5', entries)], [], None, None, [])
    assert len(rows) == len({row['row_id'] for row in rows}) == 2


def test_repair_span_certificate_does_not_cover_gap_in_changed_words():
    assert sb._v3_span_covered((1, 5), [(0, 3), (3, 8)])
    assert not sb._v3_span_covered((1, 5), [(0, 2), (3, 8)])
