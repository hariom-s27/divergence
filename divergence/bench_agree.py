"""P10b B: agreement between two labellers' filled sheets (own Krippendorff alpha, P10b-03).

    python -m divergence.bench_agree --a <labeller1 dir> --b <labeller2 dir> --out <json>

Each dir holds sheet_A.csv and sheet_B.csv from bench_label_sheets. Binary nominal alpha for
  b1_key_supported: YES=1, NO=0; UNSURE or blank = missing (every row);
  a2_answerability: ANSWERABLE=1, UNDERSPECIFIED/INDETERMINATE=0; UNSURE or blank = missing; only rows
                    whose lookup_note is "one version applies" or "no date or tax year given". A filled a2
                    on any other row is ignored, counted and listed by item id.
Alpha is undefined (null, with a reason) when there are fewer than two pairable values or the expected
disagreement is 0. Percentile bootstrap 95% CI: 2,000 resamples of the pairable items, seed 20261121;
resamples with undefined alpha are counted, never dropped silently. Output: codes, counts and ids only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

from divergence.bench_label_sheets import A2_NOTES, SHEET_A, SHEET_B
from divergence.bench_slots import PACKAGE_DIR

SEED = 20261121
RESAMPLES = 2000
B1_CODES = {"YES": 1, "NO": 0, "UNSURE": None, "": None}
A2_CODES = {"ANSWERABLE": 1, "UNDERSPECIFIED": 0, "INDETERMINATE": 0, "UNSURE": None, "": None}
B3_VALUES = ("", "1", "2", "3")
RUNS_DIR = PACKAGE_DIR / "runs"


class AgreeError(ValueError):
    pass


def alpha(units):
    """Krippendorff's alpha (nominal) for a list of per-item value lists (None = missing).

    Returns (Fraction or None, reason or None). Items with fewer than two values are not pairable.
    """
    coinc = Counter()
    for values in units:
        vals = [v for v in values if v is not None]
        m = len(vals)
        if m < 2:
            continue
        for i in range(m):
            for j in range(m):
                if i != j:
                    coinc[(vals[i], vals[j])] += Fraction(1, m - 1)
    n = sum(coinc.values())
    if n < 2:
        return None, "fewer than two pairable values"
    marg = Counter()
    for (c, _), v in coinc.items():
        marg[c] += v
    d_obs = sum(v for (c, k), v in coinc.items() if c != k) / n
    d_exp = sum(marg[c] * marg[k] for c in marg for k in marg if c != k) / (n * (n - 1))
    if d_exp == 0:
        return None, "expected disagreement is 0 (all values identical)"
    return 1 - d_obs / d_exp, None


def percentile(sorted_vals, q):
    """Linear interpolation between closest ranks (q in [0, 1])."""
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def bootstrap(pairable, seed=SEED, resamples=RESAMPLES):
    rng = random.Random(seed)
    m = len(pairable)
    values, undefined = [], 0
    for _ in range(resamples):
        if m == 0:
            undefined += 1
            continue
        a, _ = alpha([pairable[rng.randrange(m)] for _ in range(m)])
        if a is None:
            undefined += 1
        else:
            values.append(float(a))
    values.sort()
    ci = [percentile(values, 0.025), percentile(values, 0.975)] if values else None
    return {"resamples": resamples, "seed": seed, "method": "percentile", "n_defined": len(values),
            "n_undefined": undefined}, ci


def measure(ids, codes_a, codes_b, seed=SEED, resamples=RESAMPLES):
    """codes_x: {item_id: 0/1/None} over the considered ids."""
    pairs = [(i, codes_a[i], codes_b[i]) for i in ids]
    pairable = [[x, y] for _, x, y in pairs if x is not None and y is not None]
    a, reason = alpha([[x, y] for _, x, y in pairs])
    boot, ci = bootstrap(pairable, seed, resamples)
    return {
        "alpha": float(a) if a is not None else None,
        "alpha_fraction": f"{a.numerator}/{a.denominator}" if a is not None else None,
        "alpha_undefined_reason": reason,
        "n_items_considered": len(ids),
        "n_pairable": len(pairable),
        "missing_a": sum(1 for _, x, _ in pairs if x is None),
        "missing_b": sum(1 for _, _, y in pairs if y is None),
        "observed_agreement": {"k": sum(1 for x, y in pairable if x == y), "n": len(pairable)},
        "ci95": ci,
        "bootstrap": boot,
        "disagreements": sorted(i for i, x, y in pairs if x is not None and y is not None and x != y),
    }


def read_sheet(path, fields):
    if not path.is_file():
        raise AgreeError(f"missing {path.name} in {path.parent}")
    data = path.read_bytes()
    reader = csv.DictReader(data.decode("utf-8-sig").splitlines())
    if tuple(reader.fieldnames or ()) != fields:
        raise AgreeError(f"{path.parent.name}/{path.name}: header differs from the sheet columns")
    rows = {}
    for row in reader:
        item_id = (row.get("item_id") or "").strip()
        if item_id in rows:
            raise AgreeError(f"{path.parent.name}/{path.name}: duplicate item id {item_id}")
        rows[item_id] = {k: (v or "").strip() for k, v in row.items()}
    return rows, hashlib.sha256(data).hexdigest()


def read_labeller(d, tag):
    d = Path(d)
    sheet_a, sha_a = read_sheet(d / "sheet_A.csv", SHEET_A)
    sheet_b, sha_b = read_sheet(d / "sheet_B.csv", SHEET_B)
    if set(sheet_a) != set(sheet_b):
        raise AgreeError(f"labeller {tag}: sheet_A and sheet_B item ids differ")
    for item_id in sheet_a:
        for col, allowed, row in (("a2_answerability", A2_CODES, sheet_a[item_id]),
                                  ("b1_key_supported", B1_CODES, sheet_b[item_id]),
                                  ("b3_confidence", B3_VALUES, sheet_b[item_id])):
            if row[col] not in allowed:
                raise AgreeError(f"labeller {tag}: {item_id} {col} has a value outside the allowed set")
    return sheet_a, sheet_b, {"sheet_A.csv": sha_a, "sheet_B.csv": sha_b}


def agree(dir_a, dir_b, seed=SEED, resamples=RESAMPLES):
    a_sheet, a_b, a_sha = read_labeller(dir_a, "a")
    b_sheet, b_b, b_sha = read_labeller(dir_b, "b")
    if set(a_sheet) != set(b_sheet):
        raise AgreeError("the two labellers' item ids differ")
    ids = sorted(a_sheet)
    diff = [i for i in ids if a_sheet[i]["lookup_note"] != b_sheet[i]["lookup_note"]]
    if diff:
        raise AgreeError(f"lookup_note differs between labellers for {diff}")
    a2_ids = [i for i in ids if a_sheet[i]["lookup_note"] in A2_NOTES]
    ignored = {tag: sorted(i for i in ids if i not in a2_ids and sheet[i]["a2_answerability"])
               for tag, sheet in (("a", a_sheet), ("b", b_sheet))}
    b1 = measure(ids, {i: B1_CODES[a_b[i]["b1_key_supported"]] for i in ids},
                 {i: B1_CODES[b_b[i]["b1_key_supported"]] for i in ids}, seed, resamples)
    a2 = measure(a2_ids, {i: A2_CODES[a_sheet[i]["a2_answerability"]] for i in a2_ids},
                 {i: A2_CODES[b_sheet[i]["a2_answerability"]] for i in a2_ids}, seed, resamples)
    per_item = Counter(b1["disagreements"]) + Counter(a2["disagreements"])
    return {
        "tool": "bench_agree", "version": 1, "n_items": len(ids),
        "inputs": {"a": a_sha, "b": b_sha},
        "measures": {"b1_key_supported": b1, "a2_answerability": a2},
        "a2_ignored": {"a": ignored["a"], "b": ignored["b"], "count_a": len(ignored["a"]),
                       "count_b": len(ignored["b"])},
        "disagreement_count_by_item": dict(sorted(per_item.items())),
    }


def write_result(result, out):
    out = Path(out)
    if out.resolve().is_relative_to(RUNS_DIR.resolve()):
        raise AgreeError("refusing to write under divergence/runs/")
    if out.exists():
        raise AgreeError(f"refusing to overwrite {out}")
    data = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--a", type=Path, required=True, help="labeller 1 sheets dir")
    parser.add_argument("--b", type=Path, required=True, help="labeller 2 sheets dir")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = agree(args.a, args.b)
        sha = write_result(result, args.out)
    except AgreeError as exc:
        print(f"bench agree: ERROR {exc}", file=sys.stderr)
        return 2
    for name, m in result["measures"].items():
        print(f"{name}: alpha {m['alpha_fraction'] or 'undefined'} pairable {m['n_pairable']}"
              f"/{m['n_items_considered']} ci95 {m['ci95']} bootstrap undefined {m['bootstrap']['n_undefined']}"
              f" disagreements {len(m['disagreements'])}")
    print(f"a2 ignored: a {result['a2_ignored']['count_a']}, b {result['a2_ignored']['count_b']}")
    print(f"wrote {args.out} sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
