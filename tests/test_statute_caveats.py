"""P09D-39: invented bodies only; no network or extraction-cache writes."""
import copy
import contextlib
import json

import pytest

from divergence import statute_caveats as sc
from divergence import statute_build as sb


def inputs(body='(1) Alpha beta gamma.\n(2) Delta epsilon.'):
    rid = 'act:2025:77:v2'
    records = {rid: {
        'record_id': rid, 'act': '2025', 'unit': '77', 'status': 'in_force',
        'body_chars': len(body), 'body_sha256': sc.body_sha256(body)}}
    row = {'row_id': 'v2:invented', 'section': '77',
           'origin': 'itd', 'status': 'kept',
           'nature': 'accidental', 'owner_ok': 'yes', 'owner_note': '',
           'evidence_key': 'itd_words:2:3'}
    locations = {row['row_id']: {'record_id': rid, 'spans': [(2, 3)]}}
    return [row], [], records, {rid: body}, locations


def build(data):
    return sc.build_caveats(*data)


def test_exact_unicode_character_slice_and_hash():
    data = inputs('77.\n(1) “Alpha”\u00a0\ufb01sh\n₹12 beta.')
    data[4]['v2:invented']['spans'] = [(2, 3)]
    rid = next(iter(data[2]))
    rows, _ = sc.build_caveats(*data, headings={rid: '77.'})
    row = rows[0]
    assert data[3][rid][row['start']:row['end']] == '\ufb01sh'
    assert row['span_sha16'] == sc.body_sha256('\ufb01sh')[:16]
    assert data[3][rid] == '77.\n(1) “Alpha”\u00a0\ufb01sh\n₹12 beta.'


def test_repeated_words_use_absolute_occurrence():
    data = inputs('Alpha beta Alpha beta')
    data[4]['v2:invented']['spans'] = [(2, 3)]
    rows, summary = build(data)
    assert rows[0]['start'] == 11
    assert summary['coverage'] == {'v2:invented': True}


def test_absence_maps_word_gap_to_body_point():
    data = inputs()
    data[4]['v2:invented']['spans'] = [(2, 2)]
    rows, summary = build(data)
    assert rows[0]['unit_label'] == 's.77(1)'
    body = next(iter(data[3].values()))
    point = body.index('beta')
    assert rows[0]['start'] == rows[0]['end'] == point
    assert 'absence;itd_word_gap:2;point;anchor_window:40' in rows[0]['note']
    assert rows[0]['span_sha16'] == sc.body_sha256(
        body[max(0, point - 20):min(len(body), point + 20)])[:16]
    assert len(summary['absence_caveats']) == 1
    assert summary['absence_caveats'][0]['start'] == point


@pytest.mark.parametrize('point', [0, 1, 20, 40, 59, 60])
def test_point_window_clips_at_body_bounds(point):
    body = ''.join(chr(0x400 + i) for i in range(60))
    window = body[max(0, point - 20):min(len(body), point + 20)]
    assert sc.anchor_window(body, point) == window
    assert sc.caveat_digest(body, point, point, 'absence') == (
        sc.body_sha256(window)[:16])
    assert len(window) <= 40


@pytest.mark.parametrize('point', [-1, 61, True, 1.5])
def test_invalid_point_bounds_rejected(point):
    with pytest.raises(sc.CaveatStop):
        sc.anchor_window('x' * 60, point)


@pytest.mark.parametrize('point', [0, 2, 3, 5, 7])
def test_overlap_requires_strict_point_crossing(point):
    assert sc.span_crosses_point(2, 5, point) == (point == 3)
    assert not sc.span_crosses_point(point, point, point)


@pytest.mark.parametrize('note', ['', 'point;anchor_window:40'])
def test_point_without_absence_note_rejected(note):
    with pytest.raises(sc.CaveatStop, match='absence note'):
        sc.caveat_digest('invented', 2, 2, note)


def test_validator_uses_window_hash_and_rejects_empty_span_hash():
    data = inputs()
    data[4]['v2:invented']['spans'] = [(2, 2)]
    rows, _ = build(data)
    sc.validate_caveats(rows, data[2], data[3])
    rows[0]['span_sha16'] = sc.body_sha256('')[:16]
    with pytest.raises(sc.CaveatStop, match='span hash'):
        sc.validate_caveats(rows, data[2], data[3])


def test_generated_points_at_first_and_last_word_boundary():
    for word_point, expected in ((0, 0), (3, 16)):
        data = inputs('Alpha beta gamma')
        data[4]['v2:invented']['spans'] = [(word_point, word_point)]
        rows, _ = build(data)
        assert rows[0]['start'] == rows[0]['end'] == expected


@pytest.mark.parametrize('span', [
    (-1, 1), (0, 100), (3, 2), (True, 2), (1.5, 2)])
def test_bad_coordinates_refused(span):
    data = inputs()
    data[4]['v2:invented']['spans'] = [span]
    with pytest.raises(sc.CaveatStop):
        build(data)


@pytest.mark.parametrize('field,value', [
    ('body_chars', 1), ('body_sha256', 'f' * 64),
    ('status', 'unprinted'), ('status', 'never_operative')])
def test_bad_body_metadata_or_bodyless_record_refused(field, value):
    data = inputs()
    next(iter(data[2].values()))[field] = value
    with pytest.raises(sc.CaveatStop):
        build(data)


def test_missing_mapping_stops_before_any_output():
    data = inputs()
    data[4].clear()
    with pytest.raises(sc.CaveatStop, match='missing kept occurrence'):
        build(data)


def test_instrument_keeps_computed_nature_and_protocol_note():
    data = inputs()
    data[0][0].update(origin='instrument', nature='substantive', owner_ok='')
    rows, summary = build(data)
    assert rows[0]['source'] == 'amended_span'
    assert rows[0]['nature'] == 'substantive'
    assert rows[0]['note'] == 'not owner-confirmed by protocol P09D-38'
    assert summary['counts'] == {'amended_span': 1}


def test_removed_row_excluded_and_owner_nature_retained():
    data = inputs()
    data[0][0]['nature'] = 'substantive'
    data[0].append(dict(data[0][0], row_id='removed', status='removed'))
    rows, summary = build(data)
    assert len(rows) == 1 and rows[0]['nature'] == 'substantive'
    assert 'removed' not in summary['coverage']


def test_unconfirmed_itd_refused():
    data = inputs()
    data[0][0]['owner_ok'] = ''
    with pytest.raises(sc.CaveatStop, match='owner confirmation'):
        build(data)


def test_all_label_gap_evidence_preserved_with_no_offsets():
    data = inputs()
    rid = next(iter(data[2]))
    data[1].extend({'record_id': rid, 'label': '(a)',
                    'source': 'ledger', 'evidence_key': ref}
                   for ref in ('invented:one', 'invented:two'))
    rows, summary = build(data)
    gaps = [r for r in rows if r['source'] == 'label_gap']
    assert len(gaps) == summary['counts']['label_gap'] == 2
    assert len({r['caveat_id'] for r in gaps}) == 2
    assert all(r['start'] == r['end'] == r['span_sha16'] == r['nature'] == ''
               for r in gaps)


def test_moved_pair_shared_note():
    data = inputs()
    first, second = 'v2:7d4478c559067e47', 'v2:fb5f97c86c27aa13'
    data[0][0].update(row_id=first, owner_note='moved_pair:6-7;invented first')
    data[0].append(dict(data[0][0], row_id=second,
                        owner_note='moved_pair:6-7;invented second'))
    loc = data[4].pop('v2:invented')
    data[4][first] = loc
    data[4][second] = dict(loc, spans=[(3, 3)])
    rows, _ = build(data)
    assert {r['note'].split(';')[0] for r in rows} == {'moved_pair:6-7'}
    rows[0]['note'] = 'different'
    with pytest.raises(sc.CaveatStop, match='shared note'):
        sc.validate_caveats(rows, data[2], data[3])


def test_output_stable_and_does_not_mutate_inputs():
    data = inputs()
    before = copy.deepcopy(data)
    a, _ = build(data)
    b, _ = build(data)
    assert sc.csv_bytes(a) == sc.csv_bytes(b)
    assert data == before


@pytest.mark.parametrize('field,value', [
    ('start', -1), ('end', 999), ('span_sha16', '0' * 16)])
def test_stored_csv_span_tamper_refused(field, value):
    data = inputs()
    rows, _ = build(data)
    rows[0][field] = value
    with pytest.raises(sc.CaveatStop):
        sc.validate_caveats(rows, data[2], data[3])


def test_explicit_coordinates_preferred_and_digests_not_coordinates():
    evidence = {'evidence_key': 'C3;itd_words:3:4;itd_words:7:7'}
    assert sc.explicit_spans(evidence) == [(3, 4), (7, 7)]
    evidence = {'evidence_key': 'current:0123456789abcdef'}
    assert sc.explicit_spans(evidence) == []
    with pytest.raises(sc.CaveatStop):
        sc.explicit_spans({'evidence_key': 'itd_words:4:3'})


def fake_root(tmp_path):
    data = inputs()
    rid = next(iter(data[2]))
    rec = data[2][rid]
    rec['storage_mode'] = 'local_only'
    (tmp_path / 'records/2025').mkdir(parents=True)
    (tmp_path / '_local_text/2025').mkdir(parents=True)
    stem = rid.replace(':', '__')
    (tmp_path / 'records/2025' / (stem + '.json')).write_text(
        json.dumps(rec), encoding='utf-8')
    (tmp_path / '_local_text/2025' / (stem + '.txt')).write_text(
        data[3][rid], encoding='utf-8', newline='')
    (tmp_path / 'VERSION-DATES.csv').write_text(
        'record_key,code_note\n' + rid + ',text = ita2025_2026\n',
        encoding='utf-8')
    return data


def test_explicit_evidence_recovers_without_observer(tmp_path, monkeypatch):
    data = fake_root(tmp_path)
    monkeypatch.setattr(sc.ss, 'existing_local_sources',
                        contextlib.nullcontext)
    monkeypatch.setattr(sc.se, 'latest_raw_dir', lambda: tmp_path)
    monkeypatch.setattr(sc, 'extraction_reader', lambda raw: lambda *args: {
        'status': 'FOUND', 'body': next(iter(data[3].values())),
        'heading': ''})

    def forbidden(*args):
        pytest.fail('observer must not run for explicit evidence')

    monkeypatch.setattr(sc, 'observe_occurrences', forbidden)
    _, _, locations, _ = sc.recover_locations(
        tmp_path, data[0], tmp_path / 'unused-baseline.csv')
    assert locations == data[4]


def test_ambiguous_edition_target_refused(tmp_path):
    data = fake_root(tmp_path)
    rec = dict(next(iter(data[2].values())), record_id='act:2025:77:v3')
    (tmp_path / 'records/2025/duplicate.json').write_text(
        json.dumps(rec), encoding='utf-8')
    (tmp_path / '_local_text/2025/duplicate.txt').write_text(
        next(iter(data[3].values())), encoding='utf-8')
    with (tmp_path / 'VERSION-DATES.csv').open('a', encoding='utf-8') as f:
        f.write('act:2025:77:v3,text = ita2025_2026\n')
    with pytest.raises(sc.CaveatStop, match='ambiguous edition target'):
        sc.recover_locations(tmp_path, data[0], tmp_path / 'unused')


@pytest.mark.parametrize('fail', [False, True])
def test_fallback_restores_functions_and_state(monkeypatch, fail):
    state = {'invented': ['before']}
    results = {'sentinel': {'value': 1}}
    monkeypatch.setattr(sb, '_V3_STATE', state)
    monkeypatch.setattr(sb, '_V3_RESULTS', results)
    entry = {'section': '77', 'span': (1, 2), 'gazette_span': (1, 2),
             'hunk': {'key': 'invented', 'at': 1,
                      'old': 'alpha', 'new': 'beta'}}
    original_apply = sb._v3_legacy_apply_effect
    delegated = []

    def original(*args):
        delegated.append(True)
        return [], {}

    monkeypatch.setattr(sb, '_v3_rows', original)

    def run():
        sb._V3_STATE.clear()
        sb._V3_RESULTS['changed'] = True
        sb._v3_legacy_apply_effect = object()
        sb._v3_rows([], [('R5', [entry])], [],
                    lambda *a: {'body': 'invented'}, None, [])
        if fail:
            raise sc.CaveatStop('invented refusal')
        return {'occurrence_reconciliation': {'all_covered': True}}

    if fail:
        with pytest.raises(sc.CaveatStop, match='invented refusal'):
            sc.observe_occurrences(run)
    else:
        captured, sections, _ = sc.observe_occurrences(run)
        assert captured[sb._v3_occurrence_key(entry)]['span'] == (1, 2)
        assert sections == {'77': {'body': 'invented'}}
    assert delegated == [True]
    assert sb._v3_rows is original
    assert sb._v3_legacy_apply_effect is original_apply
    assert sb._V3_STATE is state and state == {'invented': ['before']}
    assert sb._V3_RESULTS is results and results == {'sentinel': {'value': 1}}


def test_cli_modes_and_regenerate(tmp_path, monkeypatch, capsys):
    data = inputs()
    rows, summary = build(data)
    monkeypatch.setattr(sc, 'generate', lambda *args: (rows, summary))
    (tmp_path / 'census').mkdir()
    table = tmp_path / 'census/BODY-CAVEATS.csv'
    assert sc.main(['--root', str(tmp_path)]) == 0
    assert not table.exists()
    assert sc.main(['--root', str(tmp_path), '--write']) == 0
    assert sc.main(['--root', str(tmp_path), '--check']) == 0
    assert sc.main(['--root', str(tmp_path), '--write']) == 0
    table.write_bytes(table.read_bytes() + b'changed')
    assert sc.main(['--root', str(tmp_path), '--check']) == 1
    assert 'STOP' in capsys.readouterr().out


def test_cli_ambiguity_never_creates_output(tmp_path, monkeypatch, capsys):
    def refuse(*args):
        raise sc.CaveatStop('ambiguous occurrence')
    monkeypatch.setattr(sc, 'generate', refuse)
    assert sc.main(['--root', str(tmp_path), '--write']) == 1
    assert not (tmp_path / 'census/BODY-CAVEATS.csv').exists()
    assert 'ambiguous occurrence' in capsys.readouterr().out


def test_regeneration_refusal_preserves_existing_output(
        tmp_path, monkeypatch, capsys):
    (tmp_path / 'census').mkdir()
    table = tmp_path / 'census/BODY-CAVEATS.csv'
    table.write_bytes(b'invented prior table\n')

    def refuse(*args):
        raise sc.CaveatStop('ambiguous occurrence')

    monkeypatch.setattr(sc, 'generate', refuse)
    assert sc.main(['--root', str(tmp_path), '--write']) == 1
    assert table.read_bytes() == b'invented prior table\n'


def test_cli_cache_miss_reports_file_page_and_writes_nothing(
        tmp_path, monkeypatch, capsys):
    message = 'CACHE MISS: invented.pdf; page=7; kind=text'

    def refuse(*args):
        raise ValueError(message)

    monkeypatch.setattr(sc, 'generate', refuse)
    assert sc.main(['--root', str(tmp_path), '--write']) == 1
    assert not (tmp_path / 'census/BODY-CAVEATS.csv').exists()
    assert message in capsys.readouterr().out
