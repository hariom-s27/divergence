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

P10c: --a/--b take one or more dirs (item ids unique across dirs). --seed-key <file...> names the rows whose
Sheet B key was seeded for labeller --seeded (default b). B1 alpha and specific agreement use unseeded rows:
2x2 a=YES/YES, b=YES(a)/NO(b), c=NO(a)/YES(b), d=NO/NO; p_pos = 2a/(2a+b+c), p_neg = 2d/(2d+b+c),
yes_share = (2a+b+c)/(2(a+b+c+d)); null with a reason when a denominator is 0. seed_catch: the seeded
labeller's B1 on seeded rows; NO = caught, YES/UNSURE/blank = not caught; Clopper-Pearson 95% CI.
A2 alpha uses all A2 rows (Sheet A is identical on seeded rows).
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

from divergence.bench_label_sheets import A2_NOTES, SEED_TYPES, SHEET_A, SHEET_B
from divergence.bench_slots import PACKAGE_DIR
from divergence.binom_ci import clopper_pearson

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


def _as_list(dirs):
    return [dirs] if isinstance(dirs, (str, Path)) else list(dirs)


def read_labellers(dirs, tag):
    """Merge one or more pack dirs of one labeller; item ids must be unique across dirs."""
    dirs = _as_list(dirs)
    if not dirs:
        raise AgreeError(f"labeller {tag}: no dirs given")
    sheet_a, sheet_b, inputs = {}, {}, []
    for d in dirs:
        sa, sb, sha = read_labeller(d, tag)
        dup = sorted(set(sa) & set(sheet_a))
        if dup:
            raise AgreeError(f"labeller {tag}: item ids repeated across dirs: {dup}")
        sheet_a.update(sa)
        sheet_b.update(sb)
        inputs.append({"dir": Path(d).name, **sha})
    return sheet_a, sheet_b, inputs


def read_seed_keys(files):
    """{item_id: seed type} from one or more seed key files, plus {file name: sha256}."""
    seeds, shas = {}, {}
    for f in _as_list(files or []):
        f = Path(f)
        if not f.is_file():
            raise AgreeError(f"seed key file {f.name} not found")
        data = f.read_bytes()
        try:
            obj = json.loads(data.decode("utf-8"))
            rows = obj["seeds"]
        except (ValueError, KeyError, TypeError):
            raise AgreeError(f"seed key file {f.name} is not a seed key") from None
        for row in rows:
            item_id, seed_type = row.get("item_id"), row.get("type")
            if seed_type not in SEED_TYPES or not item_id:
                raise AgreeError(f"seed key file {f.name}: bad row")
            if item_id in seeds:
                raise AgreeError(f"seed key files repeat item id {item_id}")
            seeds[item_id] = seed_type
        if f.name in shas:
            raise AgreeError(f"two seed key files named {f.name}")
        shas[f.name] = hashlib.sha256(data).hexdigest()
    return seeds, shas


def load_pair(dirs_a, dirs_b, seed_keys=None, seeded="b"):
    """Read both labellers, check ids and lookup notes, read seed keys. Shared with bench_adjudicate."""
    if seeded not in ("a", "b"):
        raise AgreeError("--seeded must be a or b")
    a_sheet, a_b, a_in = read_labellers(dirs_a, "a")
    b_sheet, b_b, b_in = read_labellers(dirs_b, "b")
    if set(a_sheet) != set(b_sheet):
        raise AgreeError("the two labellers' item ids differ")
    ids = sorted(a_sheet)
    diff = [i for i in ids if a_sheet[i]["lookup_note"] != b_sheet[i]["lookup_note"]]
    if diff:
        raise AgreeError(f"lookup_note differs between labellers for {diff}")
    seeds, key_shas = read_seed_keys(seed_keys)
    missing = sorted(set(seeds) - set(ids))
    if missing:
        raise AgreeError(f"seeded ids not in the sheets: {missing}")
    return {"ids": ids, "sheet_a": {"a": a_sheet, "b": b_sheet}, "sheet_b": {"a": a_b, "b": b_b},
            "inputs": {"a": a_in, "b": b_in}, "seeds": seeds, "key_shas": key_shas, "seeded": seeded}


def _ratio(num, den, reason):
    if den == 0:
        return {"value": None, "fraction": None, "undefined_reason": reason}
    return {"value": num / den, "fraction": f"{num}/{den}", "undefined_reason": None}


def specific_agreement(ids, codes_a, codes_b):
    """2x2 over pairable ids (codes 1=YES, 0=NO, None missing), p_pos, p_neg, yes_share."""
    pairs = [(codes_a[i], codes_b[i]) for i in ids if codes_a[i] is not None and codes_b[i] is not None]
    a = sum(1 for x, y in pairs if x == 1 and y == 1)
    b = sum(1 for x, y in pairs if x == 1 and y == 0)
    c = sum(1 for x, y in pairs if x == 0 and y == 1)
    d = sum(1 for x, y in pairs if x == 0 and y == 0)
    return {
        "two_by_two": {"yes_yes": a, "yes_no": b, "no_yes": c, "no_no": d, "n_pairable": len(pairs)},
        "p_pos": _ratio(2 * a, 2 * a + b + c, "no YES ratings among pairable rows"),
        "p_neg": _ratio(2 * d, 2 * d + b + c, "no NO ratings among pairable rows"),
        "yes_share": _ratio(2 * a + b + c, 2 * len(pairs), "no pairable rows"),
    }


def seed_catch(seed_ids, b1_raw):
    """b1_raw: {item_id: raw B1 string of the seeded labeller}. NO = caught; anything else = not caught."""
    ids = sorted(seed_ids)
    caught = [i for i in ids if b1_raw[i] == "NO"]
    n, k = len(ids), len(caught)
    return {"n": n, "caught": k, "not_caught": n - k, "rate": (k / n) if n else None,
            "rate_fraction": f"{k}/{n}" if n else None,
            "ci95": list(clopper_pearson(k, n)) if n else None, "ci_method": "clopper-pearson",
            "ids_not_caught": [i for i in ids if i not in caught]}


def agree(dirs_a, dirs_b, seed_keys=None, seeded="b", seed=SEED, resamples=RESAMPLES):
    p = load_pair(dirs_a, dirs_b, seed_keys, seeded)
    ids, seeds = p["ids"], p["seeds"]
    a_sheet, b_sheet = p["sheet_a"]["a"], p["sheet_a"]["b"]
    a_b, b_b = p["sheet_b"]["a"], p["sheet_b"]["b"]
    real = [i for i in ids if i not in seeds]
    a2_ids = [i for i in ids if a_sheet[i]["lookup_note"] in A2_NOTES]
    ignored = {tag: sorted(i for i in ids if i not in a2_ids and sheet[i]["a2_answerability"])
               for tag, sheet in (("a", a_sheet), ("b", b_sheet))}
    b1_a = {i: B1_CODES[a_b[i]["b1_key_supported"]] for i in real}
    b1_b = {i: B1_CODES[b_b[i]["b1_key_supported"]] for i in real}
    b1 = measure(real, b1_a, b1_b, seed, resamples)
    a2 = measure(a2_ids, {i: A2_CODES[a_sheet[i]["a2_answerability"]] for i in a2_ids},
                 {i: A2_CODES[b_sheet[i]["a2_answerability"]] for i in a2_ids}, seed, resamples)
    per_item = Counter(b1["disagreements"]) + Counter(a2["disagreements"])
    seeded_b = p["sheet_b"][seeded]
    return {
        "tool": "bench_agree", "version": 2, "n_items": len(ids),
        "inputs": p["inputs"],
        "measures": {"b1_key_supported": b1, "a2_answerability": a2},
        "b1_unseeded": specific_agreement(real, b1_a, b1_b),
        "seeded": {"labeller": seeded, "n_seed_rows": len(seeds), "key_files": p["key_shas"]},
        "seed_catch": (seed_catch(seeds, {i: seeded_b[i]["b1_key_supported"] for i in seeds})
                       if p["key_shas"] else None),
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
    parser.add_argument("--a", type=Path, nargs="+", required=True, help="labeller 1 sheets dir(s)")
    parser.add_argument("--b", type=Path, nargs="+", required=True, help="labeller 2 sheets dir(s)")
    parser.add_argument("--seed-key", type=Path, nargs="+", default=None, help="seed key file(s)")
    parser.add_argument("--seeded", choices=("a", "b"), default="b", help="labeller who got the seeds")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = agree(args.a, args.b, args.seed_key, args.seeded)
        sha = write_result(result, args.out)
    except AgreeError as exc:
        print(f"bench agree: ERROR {exc}", file=sys.stderr)
        return 2
    for name, m in result["measures"].items():
        print(f"{name}: alpha {m['alpha_fraction'] or 'undefined'} pairable {m['n_pairable']}"
              f"/{m['n_items_considered']} ci95 {m['ci95']} bootstrap undefined {m['bootstrap']['n_undefined']}"
              f" disagreements {len(m['disagreements'])}")
    sa = result["b1_unseeded"]
    print(f"b1 unseeded 2x2 {sa['two_by_two']} p_pos {sa['p_pos']['fraction']} p_neg {sa['p_neg']['fraction']}"
          f" yes_share {sa['yes_share']['fraction']}")
    sc = result["seed_catch"]
    if sc is not None:
        print(f"seed catch: caught {sc['caught']}/{sc['n']} ci95 {sc['ci95']}")
    print(f"a2 ignored: a {result['a2_ignored']['count_a']}, b {result['a2_ignored']['count_b']}")
    print(f"wrote {args.out} sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
