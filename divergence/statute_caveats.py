"""P09D-39: deterministic metadata caveats on exact, unchanged stored bodies.

Offsets are Unicode code points, end exclusive. Comparison folding is used only
for locating; spans and hashes always refer to the original body. Explicit
``itd_words:start:end`` evidence is preferred. Historical hashes need
the unchanged v3 comparator's function-local observer fallback.

Absences are points, hashed using the clipped 40-character anchor window.
"""
from __future__ import annotations

import argparse
from collections import Counter
import contextlib
import copy
import csv
import io
import json
from pathlib import Path
import re

from divergence import act_parse as ap
from divergence import statute_build as sb
from divergence import statute_extract as se
from divergence import statute_sources as ss
from divergence.statute_ingest import edition_for, extraction_reader
from divergence.statute_schema import DEFAULT_ROOT, body_sha256, get_span
from divergence.statute_validate import body_path

COLUMNS = ('caveat_id', 'record_id', 'start', 'end', 'unit_label', 'source',
           'nature', 'ref_row_id', 'span_sha16', 'note')
DIFF_COLUMNS = ('section', 'location_sha16', 'kind', 'status', 'rule',
                'origin', 'image_on_page', 'evidence_key')


class CaveatStop(ValueError):
    """Refuse publication; messages contain metadata only."""


def read_csv(path):
    with Path(path).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        if (not reader.fieldnames
                or len(set(reader.fieldnames)) != len(reader.fieldnames)
                or any(None in r or None in r.values() for r in rows)):
            raise CaveatStop('invalid CSV shape')
        return rows


def explicit_spans(row):
    """Absolute ITD word intervals, never infer coordinates from a digest."""
    cells = row['evidence_key'].split(';')
    spans = []
    for cell in cells:
        if cell.startswith('itd_words:'):
            match = re.fullmatch(r'itd_words:(\d+):(\d+)', cell)
            if not match:
                raise CaveatStop('malformed absolute ITD coordinates')
            a, b = map(int, match.groups())
            if a > b or (a, b) in spans:
                raise CaveatStop('invalid or duplicate ITD coordinates')
            spans.append((a, b))
    return spans


def observe_occurrences(run):
    """Delegate unchanged comparator; restore functions/state even on error.

    This fallback is synchronous. Nothing captured is retained in module state.
    The caller supplies the cached-source context and local inputs.
    """
    original = sb._v3_rows
    apply = sb._v3_legacy_apply_effect
    state, results = sb._V3_STATE, sb._V3_RESULTS
    saved_state, saved_results = copy.deepcopy(state), copy.deepcopy(results)
    captured, sections = {}, {}

    def observe(baseline, stages, items, sect, view, witnesses):
        for entry in stages[-1][1]:
            key = sb._v3_occurrence_key(entry)
            if key in captured:
                raise CaveatStop('duplicate observed occurrence')
            captured[key] = copy.deepcopy(entry)
            section = entry['section']
            if section not in sections:
                sections[section] = copy.deepcopy(
                    sect('ita2025_2026', section))
        return original(baseline, stages, items, sect, view, witnesses)

    sb._v3_rows = observe
    try:
        result = run()
        reconciliation = result['occurrence_reconciliation']
        if not reconciliation['all_covered']:
            raise CaveatStop('incomplete occurrence reconciliation')
        return captured, sections, copy.deepcopy(result)
    finally:
        sb._v3_rows = original
        sb._v3_legacy_apply_effect = apply
        sb._V3_STATE, sb._V3_RESULTS = state, results
        state.clear()
        state.update(saved_state)
        results.clear()
        results.update(saved_results)


def comparison_map(body, heading=''):
    """C3 tokens and original character intervals; never edit body."""
    words, offsets = [], []
    for match in re.finditer(r'\S+', body):
        tokens = se.fold_for_diff(match.group()).split()
        words.extend(tokens)
        offsets.extend([(match.start(), match.end())] * len(tokens))
    if words != se.fold_for_diff(body).split():
        raise CaveatStop('C3 tokenisation cannot be mapped exactly')
    prefix = se.fold_for_diff(heading or '').split()
    skip = (len(prefix)
            if prefix and words[:len(prefix)] == prefix else 0)
    return words[skip:], offsets[skip:]


def unit_at(body, point, section):
    """Smallest uniquely bounded line-start structural unit at a gap.

    Numeric subsection boundaries are resolved first. Within that container,
    leaf labels use the established successor rules, with duplicate matches
    rejected. A section is the containing unit when it has no such subdivision.
    """
    start, end, label = 0, len(body), 's.' + section
    numeric = list(re.finditer(r'(?m)^\s*\[?\s*\((\d+[A-Za-z]*)\)', body))
    previous = [m for m in numeric if m.start() <= point]
    if previous:
        parent = previous[-1]
        start = parent.start()
        end = next((m.start() for m in numeric if m.start() > point),
                   len(body))
        label += '(' + parent.group(1) + ')'
    segment = body[start:end]
    candidates = []
    markers = list(re.finditer(r'(?m)^\s*\[?\s*\(([A-Za-z]+)\)', segment))
    for marker in markers:
        if start + marker.start() > point:
            continue
        token = marker.group(1)
        if sum(m.group(1) == token for m in markers) != 1:
            continue
        successors = set(ap.successors(token)) - {token}
        stop = next((m.start() for m in markers
                     if m.start() > marker.start()
                     and m.group(1) in successors), len(segment))
        a, b = start + marker.start(), start + stop
        if a <= point < b:
            candidates.append((a, b, label + '(' + token + ')'))
    if candidates:
        size = min(b - a for a, b, _ in candidates)
        smallest = [item for item in candidates if item[1] - item[0] == size]
        if len(smallest) != 1:
            raise CaveatStop('ambiguous absence unit')
        start, end, label = smallest[0]
    if not start <= point <= end or not start < end:
        raise CaveatStop('absence has no containing body unit')
    return start, end, label


def make_caveat(record_id, start, end, unit, source, nature, ref,
                digest, note):
    identity = [record_id, start, end, unit, source, ref]
    key = body_sha256(json.dumps(identity, separators=(',', ':')))[:16]
    return dict(zip(COLUMNS, [
        'caveat:' + key, record_id, start, end, unit,
        source, nature, ref, digest, note]))


def anchor_window(body, point):
    """At most 20 original code points on either side; endpoints are valid."""
    if (isinstance(point, bool) or not isinstance(point, int)
            or not 0 <= point <= len(body)):
        raise CaveatStop('point outside body')
    return body[max(0, point - 20):min(len(body), point + 20)]


def span_crosses_point(start, end, point):
    """A span crosses a point only in its strict interior."""
    return start < point < end


def caveat_digest(body, start, end, note):
    """Hash the stored slice, or the clipped window for an absence point."""
    offsets = []
    for value in (start, end):
        if isinstance(value, bool) or not (
                isinstance(value, int)
                or isinstance(value, str) and re.fullmatch(r'-?\d+', value)):
            raise CaveatStop('invalid character offset')
        offsets.append(int(value))
    start, end = offsets
    if start == end:
        if 'absence' not in note:
            raise CaveatStop('point requires absence note')
        span = anchor_window(body, start)
    else:
        try:
            span = get_span(body, start, end)
        except (ValueError, TypeError):
            raise CaveatStop('invalid character span') from None
    return body_sha256(span)[:16]


def build_caveats(diffs, gaps, records, bodies, locations, headings=None):
    """Pure builder on resolved absolute ITD token spans."""
    headings = headings or {}
    output, coverage, absent = [], {}, []
    kept = [row for row in diffs if row['status'] == 'kept']
    if len({r['row_id'] for r in diffs}) != len(diffs):
        raise CaveatStop('duplicate difference row id')
    for row in kept:
        rid = row['row_id']
        if row['origin'] not in {'itd', 'instrument'}:
            raise CaveatStop('unexpected kept origin')
        if row['origin'] == 'itd' and row['owner_ok'] != 'yes':
            raise CaveatStop('ITD row lacks owner confirmation')
        loc = locations.get(rid)
        if not loc:
            raise CaveatStop('missing kept occurrence: ' + rid)
        record_id, spans = loc['record_id'], loc['spans']
        rec = records[record_id]
        body = bodies.get(record_id)
        if not body or rec['status'] in {'never_operative', 'unprinted'}:
            raise CaveatStop('offset caveat on bodyless record: ' + record_id)
        if str(rec['unit']) != row['section'] or str(rec['act']) != '2025':
            raise CaveatStop('occurrence record target differs')
        if (body_sha256(body) != rec['body_sha256']
                or len(body) != rec['body_chars']):
            raise CaveatStop('body metadata differs: ' + record_id)
        _, offsets = comparison_map(body, headings.get(record_id, ''))
        if not spans or len(set(map(tuple, spans))) != len(spans):
            raise CaveatStop('empty or duplicate occurrence spans')
        for a, b in spans:
            if (isinstance(a, bool) or isinstance(b, bool)
                    or not isinstance(a, int) or not isinstance(b, int)):
                raise CaveatStop('noninteger occurrence coordinate')
            if not 0 <= a <= b <= len(offsets):
                raise CaveatStop('occurrence outside body tokens')
            note = ('moved_pair:6-7'
                    if 'moved_pair:6-7' in row['owner_note'] else '')
            if row['origin'] == 'instrument':
                note = 'not owner-confirmed by protocol P09D-38'
            if a == b:
                point = offsets[a][0] if a < len(offsets) else len(body)
                _, _, unit = unit_at(body, point, row['section'])
                start = end = point
                note = ';'.join(filter(None, [
                    note, 'absence;itd_word_gap:' + str(a),
                    'point;anchor_window:40']))
                absent.append({'ref_row_id': rid, 'record_id': record_id,
                               'start': start, 'end': end, 'unit_label': unit})
            else:
                start, end = offsets[a][0], offsets[b - 1][1]
                unit = 's.' + row['section']
            digest = caveat_digest(body, start, end, note)
            source = 'itd_diff' if row['origin'] == 'itd' else 'amended_span'
            output.append(make_caveat(record_id, start, end, unit, source,
                                      row['nature'], rid, digest, note))
        coverage[rid] = True
    for gap in gaps:
        record_id = gap['record_id']
        if record_id not in records:
            raise CaveatStop('label gap record missing')
        ref = 'label-gap:' + body_sha256(json.dumps(gap, sort_keys=True))[:16]
        note = ('source:' + gap['source']
                + ';evidence:' + gap['evidence_key'])
        output.append(make_caveat(record_id, '', '', gap['label'],
                                  'label_gap', '', ref, '', note))
    output.sort(key=lambda r: (r['source'], r['record_id'],
                               r['ref_row_id'], str(r['start'])))
    validate_caveats(output, records, bodies)
    return output, {'counts': dict(Counter(r['source'] for r in output)),
                    'coverage': coverage, 'absence_caveats': absent,
                    'span_hash_checks': sum(
                        r['source'] != 'label_gap' for r in output)}


def validate_caveats(rows, records, bodies):
    seen = set()
    pairs = []
    for row in rows:
        if set(row) != set(COLUMNS) or row['caveat_id'] in seen:
            raise CaveatStop('invalid columns or duplicate caveat id')
        seen.add(row['caveat_id'])
        if row['record_id'] not in records:
            raise CaveatStop('caveat record missing')
        if row['source'] == 'label_gap':
            if any(row[k] != '' for k in ('start', 'end', 'span_sha16')):
                raise CaveatStop('label gap must have empty offsets/hash')
            continue
        if row['source'] not in {'itd_diff', 'amended_span'}:
            raise CaveatStop('invalid caveat source')
        rec = records[row['record_id']]
        body = bodies.get(row['record_id'])
        if not body or rec['status'] in {'unprinted', 'never_operative'}:
            raise CaveatStop('offset caveat on bodyless record')
        if (body_sha256(body) != rec['body_sha256']
                or len(body) != rec['body_chars']):
            raise CaveatStop('body metadata differs')
        digest = caveat_digest(body, row['start'], row['end'], row['note'])
        if digest != row['span_sha16']:
            raise CaveatStop('span hash differs')
        if row['ref_row_id'] in {
                'v2:7d4478c559067e47', 'v2:fb5f97c86c27aa13'}:
            pairs.append(row['note'].split(';')[0])
    if pairs and (len(pairs) != 2 or set(pairs) != {'moved_pair:6-7'}):
        raise CaveatStop('moved pair shared note differs')


def recover_locations(root, diffs, baseline):
    """Prefer explicit evidence; fall back for historical digest references."""
    version_rows = {r['record_key']: r
                    for r in read_csv(root / 'VERSION-DATES.csv')}
    record_paths = sorted((root / 'records').glob('*/*.json'))
    records, bodies, targets = {}, {}, {}
    for path in record_paths:
        rec = json.loads(path.read_text(encoding='utf-8'))
        rid = rec['record_id']
        if rid in records:
            raise CaveatStop('duplicate record id')
        records[rid] = rec
        if rec['status'] != 'unprinted':
            bodies[rid] = body_path(root, rec, path).read_bytes().decode(
                'utf-8')
        if (rec['status'] not in {'never_operative', 'unprinted'}
                and str(rec['act']) == '2025'):
            if edition_for(version_rows[rid], rec) == 'ita2025_2026':
                section = str(rec['unit'])
                if section in targets:
                    raise CaveatStop('ambiguous edition target')
                targets[section] = rid
    kept = [r for r in diffs if r['status'] == 'kept']
    locations, headings = {}, {}
    for row in kept:
        if row['section'] not in targets:
            raise CaveatStop('no stored edition target')
        spans = explicit_spans(row)
        if spans:
            locations[row['row_id']] = {
                'record_id': targets[row['section']], 'spans': spans}
    with ss.existing_local_sources():
        reader = extraction_reader(se.latest_raw_dir())
        for row in kept:
            rid = targets[row['section']]
            result = reader('ita2025_2026', row['section'])
            if result['status'] != 'FOUND' or result['body'] != bodies[rid]:
                raise CaveatStop('edition extraction differs from stored body')
            headings[rid] = result.get('heading') or ''
        if len(locations) != len(kept):
            def run():
                return sb.gazette_check_v3(
                    se.latest_raw_dir(), read_csv(baseline),
                    read_csv(root / 'CORRIGENDUM-DISPOSITION.csv'))

            with (contextlib.redirect_stdout(io.StringIO()),
                  contextlib.redirect_stderr(io.StringIO())):
                captured, sections, result = observe_occurrences(run)
            computed = {r['row_id']: r for r in result['rows']}
            if set(computed) != {r['row_id'] for r in diffs}:
                raise CaveatStop('comparison row set differs')
            for row in diffs:
                if any(row[k] != computed[row['row_id']][k]
                       for k in DIFF_COLUMNS):
                    raise CaveatStop(
                        'comparison evidence differs: ' + row['row_id'])
            links = {r['row_id']: r['current_occurrences']
                     for r in result['occurrence_reconciliation']['rows']}
            for row in kept:
                if row['row_id'] in locations:
                    continue
                keys = links.get(row['row_id'], [])
                declared = re.findall(
                    r'(?:^|;)current:([0-9a-f]{16})(?=;|$)',
                    row['evidence_key'])
                if row['row_id'].startswith('v3:') and not declared:
                    declared = [row['row_id'][3:]]
                if sorted(keys) != sorted(declared) or not keys:
                    raise CaveatStop('occurrence identity differs')
                entries = [captured[k] for k in keys]
                if any(e['section'] != row['section'] for e in entries):
                    raise CaveatStop('occurrence section differs')
                rid = targets[row['section']]
                if sections[row['section']]['body'] != bodies[rid]:
                    raise CaveatStop('observed body differs')
                locations[row['row_id']] = {
                    'record_id': rid, 'spans': [e['span'] for e in entries]}
    return records, bodies, locations, headings


def csv_bytes(rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def generate(root=DEFAULT_ROOT, baseline=None):
    root = Path(root)
    diffs = read_csv(root / 'census/ITD-GAZETTE-DIFFS.csv')
    gaps = read_csv(root / 'census/LABEL-GAPS.csv')
    counts = Counter(r['origin'] for r in diffs if r['status'] == 'kept')
    if counts != {'itd': 9, 'instrument': 3}:
        raise CaveatStop('approved kept-reference scope differs')
    if baseline is None:
        baseline = (root / '_local_text/census/partD/20261119-172809'
                    / 'ITD-GAZETTE-DIFFS.v2.csv')
    records, bodies, locations, headings = recover_locations(
        root, diffs, baseline)
    rows, summary = build_caveats(
        diffs, gaps, records, bodies, locations, headings)
    summary['explicit_evidence_rows'] = sum(
        bool(explicit_spans(r)) for r in diffs if r['status'] == 'kept')
    summary['fallback_rows'] = (len(summary['coverage'])
                                - summary['explicit_evidence_rows'])
    return rows, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--baseline', type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        rows, summary = generate(args.root, args.baseline)
        raw = csv_bytes(rows)
        output = args.root / 'census/BODY-CAVEATS.csv'
        if args.write:
            with output.open('wb') as stream:
                stream.write(raw)
        elif args.check and output.read_bytes() != raw:
            raise CaveatStop('BODY-CAVEATS.csv differs')
        mode = 'write' if args.write else 'check' if args.check else 'dry-run'
        print(json.dumps({
            'mode': mode, 'rows': len(rows),
            'sha256': body_sha256(raw.decode('utf-8')), **summary},
            sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        detail = (str(exc) if isinstance(exc, CaveatStop)
                  else type(exc).__name__)
        if isinstance(exc, ValueError) and str(exc).startswith('CACHE MISS:'):
            detail = str(exc)
        print('STOP: ' + detail)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
