"""P10a bench slot sampler (P10-04/05/16). Metadata only: never reads a statute body.

Builds the sampling frame from exact lookups at the spec's as_known_on (every frame
boundary inside the window must also be a boundary of the golden D80 timeline), draws
contrast-pair slots per stratum with one random.Random(seed), then undated singles,
then ~reserve_fraction reserve slots per stratum. Writes SLOTS-v1.csv plus
SLOTS-v1.summary.json. --check recomputes and compares (LF-normalised), writing nothing.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import random
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from divergence.statute_census import groups, load_records
from divergence.statute_lookup import FOUND, lookup
from divergence.statute_schema import ACT2025_COMMENCEMENT, DEFAULT_ROOT, parse_date, reason_class

PACKAGE_DIR = Path(__file__).resolve().parent
BENCH_DIR = PACKAGE_DIR / "bench"
DEFAULT_SPEC = BENCH_DIR / "SPEC-v1.json"
DEFAULT_OUT = BENCH_DIR / "slots" / "SLOTS-v1.csv"
DAY = timedelta(days=1)
UNDATED = "undated"
SAME_UNIT_FOUND = ("version_lookup", "proviso_condition")
HORIZON_REASON = "beyond_corpus_horizon"
DATE_TRIES = 25
SLOT_FIELDS = ("slot_id", "split", "stratum", "reserve", "side", "pair_id", "act", "unit", "as_of",
               "tax_year", "boundary", "boundary_kind", "gold_status", "gold_record_id", "gold_reasons",
               "should_abstain", "abstain_category", "act_post_cutoff")
SPLITS = ("test", "dev")


class SlotError(ValueError):
    """The frame or draw cannot be built as specified; never silently repaired."""


# ---------------------------------------------------------------- spec helpers

def load_spec(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def spec_sha256(spec):
    """Hash of canonical JSON, so CRLF checkouts (core.autocrlf) hash the same as LF."""
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def abstain_category(reasons, spec):
    """Map reasons by reason_class() through the spec's class map; pick by spec priority."""
    if not reasons:
        raise SlotError("abstain side without reasons")
    found = set()
    for reason in reasons:
        cls = reason_class(reason)
        if cls not in spec["abstain_categories"]:
            raise SlotError(f"no abstain category for class {cls} (reason {reason})")
        found.add(spec["abstain_categories"][cls])
    for category in spec["abstain_priority"]:
        if category in found:
            return category
    raise SlotError(f"abstain categories {sorted(found)} not in abstain_priority")


def quotas(total, spec):
    """Largest-remainder rounding of strata fractions; ties go in strata_order."""
    order = spec["strata_order"]
    fractions = spec["strata"]
    if sorted(order) != sorted(fractions) or abs(sum(fractions.values()) - 1.0) > 1e-9:
        raise SlotError("strata_order must list every stratum and fractions must sum to 1")
    raw = {s: total * fractions[s] for s in order}
    out = {s: int(math.floor(raw[s] + 1e-9)) for s in order}
    rest = total - sum(out.values())
    ranked = sorted(order, key=lambda s: (-(raw[s] - out[s]), order.index(s)))
    for s in ranked[:rest]:
        out[s] += 1
    return out


def reserve_count(n, fraction):
    return int(math.ceil(n * fraction - 1e-9)) if n > 0 else 0


# ---------------------------------------------------------------- frame

def _entry(key, gold, spec, **extra):
    status, record_id, candidates, reasons = gold
    entry = {"ukey": ":".join(key[1:]), "act": key[1], "unit": key[2], "status": status,
             "record_id": record_id, "candidates": tuple(candidates), "reasons": tuple(reasons),
             "category": None}
    entry.update(extra)
    if status != FOUND:
        entry["category"] = abstain_category(reasons, spec)
    return entry


def _gold(result):
    return result.status, result.record_id, tuple(result.candidates), tuple(result.reasons)


def _daily_runs(recs, key, start, last, known):
    runs = []
    point = start
    while point <= last:
        gold = _gold(lookup(recs, source_kind=key[0], act=key[1], unit=key[2], as_of=point, as_known_on=known))
        if runs and runs[-1]["gold"] == gold:
            runs[-1]["end"] = point + DAY
        else:
            runs.append({"start": point, "end": point + DAY, "gold": gold})
        point += DAY
    return runs


def build_frame(records, timeline, spec):
    """Intervals (as_of) and tax-year entries at as_known_on; excluded corpus gaps kept for the summary."""
    w0, w1 = (parse_date(v) for v in spec["window"])
    h0, h1 = (parse_date(v) for v in spec["horizon_window"])
    known = parse_date(spec["as_known_on"])
    if h0 != w1 + DAY:
        raise SlotError("horizon_window must start the day after window end")
    excluded_reasons = set(spec["frame_excluded_reasons"])
    golden = {}
    for row in timeline:
        golden.setdefault(row["unit"], set()).add(parse_date(row["from"]))
    frame = {"intervals": [], "tax_years": [], "excluded": [], "excluded_tax_years": [], "units": [],
             "years": list(spec["tax_years"])}
    for key, recs in groups(records).items():
        frame["units"].append(":".join(key[1:]))
        runs = _daily_runs(recs, key, w0, h1, known)
        for run in runs[1:]:
            if run["start"] <= w1 and run["start"] not in golden.get(":".join(key), set()):
                raise SlotError(f"frame boundary {run['start']} of {':'.join(key)} is not a golden timeline boundary")
        for run in runs:
            start, end, gold = run["start"], run["end"], run["gold"]
            if HORIZON_REASON in gold[3]:
                if start <= w1:
                    raise SlotError(f"{HORIZON_REASON} inside the window for {':'.join(key)}")
            elif start > w1:
                continue
            else:
                end = min(end, w1 + DAY)
            if excluded_reasons & set(gold[3]):
                frame["excluded"].append({"unit": ":".join(key[1:]), "from": start.isoformat(),
                                          "to": end.isoformat(), "reasons": ";".join(gold[3])})
                continue
            entry = _entry(key, gold, spec, query="as_of", start=start, end=end)
            if entry["category"] == "stale" and start <= w1:
                raise SlotError(f"stale category inside the window for {':'.join(key)} ({';'.join(gold[3])})")
            frame["intervals"].append(entry)
        for year in spec["tax_years"]:
            gold = _gold(lookup(recs, source_kind=key[0], act=key[1], unit=key[2], tax_year=year, as_known_on=known))
            if excluded_reasons & set(gold[3]):
                frame["excluded_tax_years"].append({"unit": ":".join(key[1:]), "tax_year": year,
                                                    "reasons": ";".join(gold[3])})
                continue
            entry = _entry(key, gold, spec, query="tax_year", tax_year=year)
            if entry["category"] == "stale":
                raise SlotError(f"stale category for tax year {year} of {':'.join(key)} (horizon window only)")
            frame["tax_years"].append(entry)
    return frame


def read_mapping(path, units):
    """1961 -> 2025 counterpart unit pairs from MAPPING.csv, both present in the corpus."""
    pairs = []
    with open(path, newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            old = f"1961:{row['section_1961'].strip()}"
            for new in row["section_2025"].split(";"):
                new = f"2025:{new.strip()}"
                if old in units and new in units:
                    pairs.append((old, new))
    return sorted(set(pairs))


# ---------------------------------------------------------------- combos

def _sig(entry):
    return entry["status"], entry["record_id"], entry["candidates"], entry["reasons"]


def _boundary_kind(abstain_side):
    reasons = set(abstain_side["reasons"])
    for reason, kind in ((HORIZON_REASON, "horizon"), ("repeal_day_unsettled", "repeal-day"),
                         ("after_repeal", "repeal"), ("before_commencement", "commencement")):
        if reason in reasons:
            return kind
    return "status-change"


def _by_unit(entries):
    out = {}
    for entry in entries:
        out.setdefault(entry["ukey"], []).append(entry)
    return out


def combos(frame, stratum, mapping):
    """Deterministically ordered candidate (a, b) pairs for one stratum."""
    result = []
    intervals = _by_unit(frame["intervals"])
    if stratum in SAME_UNIT_FOUND:
        for ukey in sorted(intervals):
            found = [e for e in intervals[ukey] if e["status"] == FOUND]
            for i, a in enumerate(found):
                for b in found[i + 1:]:
                    if a["record_id"] != b["record_id"]:
                        kind = "version-change" if a["end"] == b["start"] else "version-span"
                        result.append({"a": a, "b": b, "boundary": b["start"], "kind": kind})
    elif stratum == "cross_act_counterpart":
        for old, new in mapping:
            for a in intervals.get(old, []):
                for b in intervals.get(new, []):
                    if a["status"] == FOUND and b["status"] == FOUND:
                        result.append({"a": a, "b": b, "boundary": ACT2025_COMMENCEMENT, "kind": "act-transition"})
    elif stratum == "cross_year_change":
        order = {}
        for entry in frame["tax_years"]:
            order.setdefault(entry["ukey"], {})[entry["tax_year"]] = entry
        spec_years = frame["years"]
        for ukey in sorted(order):
            for y0, y1 in zip(spec_years, spec_years[1:]):
                a, b = order[ukey].get(y0), order[ukey].get(y1)
                if a is None or b is None or _sig(a) == _sig(b):
                    continue
                if FOUND in (a["status"], b["status"]):
                    result.append({"a": a, "b": b, "boundary": date(int(y1[:4]), 4, 1), "kind": "tax-year"})
    elif stratum == "abstain_boundary":
        for ukey in sorted(intervals):
            seq = intervals[ukey]
            for a, b in zip(seq, seq[1:]):
                if a["end"] != b["start"] or _sig(a) == _sig(b):
                    continue
                if (a["category"] is None) != (b["category"] is None):
                    side = a if a["category"] is not None else b
                    result.append({"a": a, "b": b, "boundary": b["start"], "kind": _boundary_kind(side)})
    else:
        raise SlotError(f"unknown stratum {stratum}")
    for index, combo in enumerate(result):
        combo["stratum"] = stratum
        # version_lookup and proviso_condition share combos, so they share use counts.
        combo["key"] = ("found_pair" if stratum in SAME_UNIT_FOUND else stratum, index)
    return result


def date_range(entry, stratum):
    """Allowed as_of range strictly inside the interval; a 1-day interval only for abstain_boundary."""
    if entry["query"] == "tax_year":
        return entry["tax_year"], entry["tax_year"]
    start, end = entry["start"], entry["end"]
    if end - start == DAY:
        return (start, start) if stratum == "abstain_boundary" else None
    lo, hi = start + DAY, end - 2 * DAY
    return (lo, hi) if lo <= hi else None


def _draw_value(rng, entry, bounds):
    if entry["query"] == "tax_year":
        return entry["tax_year"]
    lo, hi = bounds
    return date.fromordinal(rng.randint(lo.toordinal(), hi.toordinal())).isoformat()


# ---------------------------------------------------------------- draw

class _State:
    def __init__(self):
        self.loads = {s: Counter() for s in SPLITS}      # main items (cap applies)
        self.rloads = {s: Counter() for s in SPLITS}     # reserve items (spreading only)
        self.uses = Counter()
        self.used_keys = set()                           # (ukey_a, ukey_b, value_a, value_b), all splits
        self.slots = []
        self.unfilled = []


def _cap_ok(state, split, units, cap):
    if split != "test" or cap is None:
        return True
    need = Counter(units)
    return all(state.loads[split][u] + n <= cap for u, n in need.items())


def _pick_pair(rng, state, split, stratum, pool, cap):
    eligible = []
    for combo in pool:
        ra, rb = date_range(combo["a"], stratum), date_range(combo["b"], stratum)
        if ra is None or rb is None:
            continue
        if _cap_ok(state, split, (combo["a"]["ukey"], combo["b"]["ukey"]), cap):
            eligible.append((combo, ra, rb))
    while eligible:
        def score(item):
            units = {item[0]["a"]["ukey"], item[0]["b"]["ukey"]}
            load = max(state.loads[split][u] + state.rloads[split][u] for u in units)
            return load, state.uses[item[0]["key"]]
        best = min(score(item) for item in eligible)
        group = [item for item in eligible if score(item) == best]
        combo, ra, rb = rng.choice(group)
        for _ in range(DATE_TRIES):
            va, vb = _draw_value(rng, combo["a"], ra), _draw_value(rng, combo["b"], rb)
            key = (combo["a"]["ukey"], combo["b"]["ukey"], va, vb)
            if key not in state.used_keys:
                state.used_keys.add(key)
                return combo, va, vb
        eligible = [item for item in eligible if item[0] is not combo]
    return None


def _side_row(slot_id, split, stratum, reserve, side, combo, entry, value):
    as_of = value if entry["query"] == "as_of" else ""
    tax_year = value if entry["query"] == "tax_year" else ""
    return {"slot_id": slot_id, "split": split, "stratum": stratum, "reserve": reserve, "side": side,
            "pair_id": slot_id, "act": entry["act"], "unit": entry["unit"], "as_of": as_of, "tax_year": tax_year,
            "boundary": combo["boundary"].isoformat(), "boundary_kind": combo["kind"],
            "gold_status": entry["status"], "gold_record_id": entry["record_id"] or "",
            "gold_reasons": ";".join(entry["reasons"]),
            "should_abstain": "true" if entry["status"] != FOUND else "false",
            "abstain_category": entry["category"] or "",
            "act_post_cutoff": "true" if entry["act"] == "2025" else "false"}


def _undated_row(slot_id, split, reserve, ukey, spec):
    act, unit = ukey.split(":", 1)
    return {"slot_id": slot_id, "split": split, "stratum": UNDATED, "reserve": reserve, "side": "single",
            "pair_id": "", "act": act, "unit": unit, "as_of": "", "tax_year": "", "boundary": "",
            "boundary_kind": "", "gold_status": "", "gold_record_id": "", "gold_reasons": "",
            "should_abstain": "true", "abstain_category": spec["undated_category"],
            "act_post_cutoff": "true" if act == "2025" else "false"}


def _ids(prefix):
    count = [0]

    def nxt():
        count[0] += 1
        return f"{prefix}{count[0]:03d}" if not prefix.endswith("R") else f"{prefix}{count[0]:02d}"
    return nxt


def draw(frame, spec, mapping):
    rng = random.Random(spec["seed"])
    cap = spec.get("max_test_items_per_unit")
    state = _State()
    pools = {s: combos(frame, s, mapping) for s in spec["strata_order"]}
    main_id = {split: _ids(split[0].upper() + "-") for split in SPLITS}
    res_id = {split: _ids(split[0].upper() + "-R") for split in SPLITS}
    plan = {split: quotas(spec[split]["pairs"], spec) for split in SPLITS}
    frac = spec["reserve_fraction"]

    def pairs(split, reserve):
        for stratum in spec["strata_order"]:
            n = plan[split][stratum]
            for _ in range(reserve_count(n, frac) if reserve else n):
                picked = _pick_pair(rng, state, split, stratum, pools[stratum], None if reserve else cap)
                if picked is None:
                    state.unfilled.append({"split": split, "stratum": stratum, "reserve": reserve,
                                           "reason": "no eligible combo (cap, dates or uniqueness)"})
                    continue
                combo, va, vb = picked
                state.uses[combo["key"]] += 1
                slot_id = (res_id if reserve else main_id)[split]()
                flag = "true" if reserve else "false"
                loads = state.rloads if reserve else state.loads
                for side, entry, value in (("a", combo["a"], va), ("b", combo["b"], vb)):
                    state.slots.append(_side_row(slot_id, split, stratum, flag, side, combo, entry, value))
                    loads[split][entry["ukey"]] += 1
                state.slots[-1]["_combo"] = combo

    def singles(split, reserve):
        n = spec[split]["undated"]
        for _ in range(reserve_count(n, frac) if reserve else n):
            units = [u for u in frame["units"] if reserve or _cap_ok(state, split, (u,), cap)]
            if not units:
                state.unfilled.append({"split": split, "stratum": UNDATED, "reserve": reserve,
                                       "reason": "every unit at cap"})
                continue
            best = min(state.loads[split][u] + state.rloads[split][u] for u in units)
            ukey = rng.choice([u for u in units if state.loads[split][u] + state.rloads[split][u] == best])
            slot_id = (res_id if reserve else main_id)[split]()
            state.slots.append(_undated_row(slot_id, split, "true" if reserve else "false", ukey, spec))
            (state.rloads if reserve else state.loads)[split][ukey] += 1

    for split in SPLITS:
        pairs(split, False)
    for split in SPLITS:
        singles(split, False)
    for split in SPLITS:
        pairs(split, True)
    for split in SPLITS:
        singles(split, True)
    return state, pools


# ---------------------------------------------------------------- outputs

def csv_bytes(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, SLOT_FIELDS, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    order = {"a": 0, "b": 1, "single": 2}
    for row in sorted(rows, key=lambda r: (r["slot_id"], order[r["side"]])):
        writer.writerow(row)
    return buf.getvalue().encode("utf-8")


def pair_keys(rows, split):
    """(unit_a, unit_b, value_a, value_b) per pair slot of a split; value = as_of or tax_year."""
    sides = {}
    for row in rows:
        if row["split"] == split and row["side"] in ("a", "b"):
            sides.setdefault(row["slot_id"], {})[row["side"]] = row
    out = set()
    for pair in sides.values():
        if "a" in pair and "b" in pair:
            a, b = pair["a"], pair["b"]
            out.add((f"{a['act']}:{a['unit']}", f"{b['act']}:{b['unit']}",
                     a["as_of"] or a["tax_year"], b["as_of"] or b["tax_year"]))
    return out


def _record_combos(rows, split):
    out = set()
    for row in rows:
        combo = row.get("_combo")
        if combo is not None and row["split"] == split and row["reserve"] == "false":
            out.add((combo["a"]["ukey"], _sig(combo["a"]), combo["b"]["ukey"], _sig(combo["b"])))
    return out


def summary(state, frame, pools, spec, data):
    counts, per_unit = {}, {}
    for split in SPLITS:
        rows = [r for r in state.slots if r["split"] == split]
        main = [r for r in rows if r["reserve"] == "false"]
        abstain = sum(r["should_abstain"] == "true" for r in main)
        lo, hi = spec["abstain_share_target"]
        share = round(abstain / len(main), 4) if main else 0.0

        def n_slots(subset, stratum):
            return len({r["slot_id"] for r in subset if r["stratum"] == stratum})
        counts[split] = {
            "items": len(main), "abstain_items": abstain, "abstain_share": share,
            "abstain_share_in_target": lo <= share <= hi,
            "pairs": {s: n_slots(main, s) for s in spec["strata_order"]},
            "undated": n_slots(main, UNDATED),
            "reserve_pairs": {s: n_slots([r for r in rows if r["reserve"] == "true"], s) for s in spec["strata_order"]},
            "reserve_undated": n_slots([r for r in rows if r["reserve"] == "true"], UNDATED),
            "abstain_categories": dict(sorted(Counter(r["abstain_category"] for r in main
                                                      if r["abstain_category"]).items())),
        }
        units = Counter(f"{r['act']}:{r['unit']}" for r in main)
        per_unit[split] = {u: units.get(u, 0) for u in frame["units"]}
    shared = _record_combos(state.slots, "dev") & _record_combos(state.slots, "test")
    return {
        "spec_sha256": spec_sha256(spec),
        "slots_sha256": hashlib.sha256(data).hexdigest(),
        "counts": counts,
        "per_unit_items": per_unit,
        "max_test_items_per_unit_observed": max(per_unit["test"].values()) if per_unit["test"] else 0,
        "unfilled": state.unfilled,
        "excluded_corpus_gap_intervals": {"as_of": frame["excluded"], "tax_year": frame["excluded_tax_years"],
                                          "count_as_of": len(frame["excluded"]),
                                          "count_tax_year": len(frame["excluded_tax_years"])},
        "frame": {"intervals": len(frame["intervals"]), "tax_year_entries": len(frame["tax_years"]),
                  "combos": {s: len(pools[s]) for s in spec["strata_order"]}},
        "shared_record_combos_dev_test": len(shared),
        "shared_unit_date_keys_dev_test": len(pair_keys(state.slots, "dev") & pair_keys(state.slots, "test")),
    }


def summary_bytes(info):
    return (json.dumps(info, indent=2, sort_keys=True) + "\n").encode("utf-8")


def generate(spec, root=DEFAULT_ROOT, sweep_path=None, mapping_path=None):
    root = Path(root)
    records = load_records(root / "records")
    sweep_path = Path(sweep_path) if sweep_path else root / "census" / "sweep.json"
    mapping_path = Path(mapping_path) if mapping_path else root / "MAPPING.csv"
    timeline = json.loads(sweep_path.read_text(encoding="utf-8"))["timeline"]
    frame = build_frame(records, timeline, spec)
    mapping = read_mapping(mapping_path, set(frame["units"]))
    state, pools = draw(frame, spec, mapping)
    data = csv_bytes(state.slots)
    return data, summary_bytes(summary(state, frame, pools, spec, data)), state


def read_slots(path):
    """SLOTS csv -> list of row dicts (tolerates CRLF checkouts)."""
    text = Path(path).read_text(encoding="utf-8").replace("\r\n", "\n")
    return list(csv.DictReader(io.StringIO(text)))


def summary_path(out):
    out = Path(out)
    return out.with_name(out.stem + ".summary.json")


def _lf(path):
    return Path(path).read_bytes().replace(b"\r\n", b"\n") if Path(path).is_file() else None


def _first_diff(old, new):
    old_lines = old.split(b"\n") if old is not None else []
    new_lines = new.split(b"\n")
    for index in range(max(len(old_lines), len(new_lines))):
        a = old_lines[index] if index < len(old_lines) else None
        b = new_lines[index] if index < len(new_lines) else None
        if a != b:
            return index + 1
    return 0


# ---------------------------------------------------------------- active slots (shared by build/validate)

def active_slots(rows, split, unusable, cap=None):
    """Main slots minus unusable ones; each unusable main slot pulls the next unused reserve of the
    same stratum and split in order (skipping reserves that are unusable or would break the TEST cap).
    Returns (active slot ids, {main: reserve}, errors)."""
    slots, order = {}, []
    for row in rows:
        if row["split"] != split:
            continue
        sid = row["slot_id"]
        if sid not in slots:
            slots[sid] = {"stratum": row["stratum"], "reserve": row["reserve"] == "true", "units": Counter()}
            order.append(sid)
        slots[sid]["units"][f"{row['act']}:{row['unit']}"] += 1
    errors = [f"{sid}: not a {split} slot" for sid in sorted(unusable) if sid not in slots]
    main = [s for s in order if not slots[s]["reserve"]]
    active = [s for s in main if s not in unusable]
    loads = Counter()
    for sid in active:
        loads.update(slots[sid]["units"])
    pulled, taken = {}, set()
    for sid in main:
        if sid not in unusable:
            continue
        stratum = slots[sid]["stratum"]
        for rid in order:
            info = slots[rid]
            if not info["reserve"] or info["stratum"] != stratum or rid in taken or rid in unusable:
                continue
            if split == "test" and cap is not None and any(loads[u] + n > cap for u, n in info["units"].items()):
                continue
            taken.add(rid)
            active.append(rid)
            loads.update(info["units"])
            pulled[sid] = rid
            break
        else:
            errors.append(f"{sid}: no usable reserve left for {split}/{stratum}")
    return active, pulled, errors


# ---------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true", help="recompute and compare; write nothing")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="statutes root (tests only)")
    parser.add_argument("--sweep", type=Path, default=None)
    parser.add_argument("--mapping", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        data, info, state = generate(load_spec(args.spec), args.root, args.sweep, args.mapping)
    except (SlotError, KeyError, ValueError) as exc:
        print(f"bench slots: ERROR {exc}")
        return 2
    targets = ((args.out, data), (summary_path(args.out), info))
    if state.unfilled:
        print(f"bench slots: UNFILLED {len(state.unfilled)} slot(s); see summary 'unfilled'")
    if args.check:
        bad = False
        for path, expected in targets:
            actual = _lf(path)
            if actual != expected:
                bad = True
                print(f"bench slots: MISMATCH {path.name} first differing line {_first_diff(actual, expected)}")
        if bad:
            return 1
        print(f"bench slots: OK {args.out.name} sha256 {hashlib.sha256(data).hexdigest()}")
    else:
        for path, _ in targets:
            if path.exists():
                print(f"bench slots: ERROR {path} exists; refusing to overwrite")
                return 2
        args.out.parent.mkdir(parents=True, exist_ok=True)
        for path, payload in targets:
            with open(path, "xb") as stream:
                stream.write(payload)
        print(f"bench slots: wrote {args.out.name} ({len(state.slots)} rows) and {summary_path(args.out).name}")
    return 1 if state.unfilled else 0


if __name__ == "__main__":
    sys.exit(main())
