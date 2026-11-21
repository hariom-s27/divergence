"""P10c: adjudication of flagged real keys, and the key error rate.

    python -m divergence.bench_adjudicate --template --a <dirs> --b <dirs> [--seed-key <files>] [--seeded b] \
        --out divergence/bench/_local/labels/<name>.csv
    python -m divergence.bench_adjudicate --score <filled csv> --n-audited <int> --out <json>

Template: one row per flagged real item (owner decision D2). Flags, joined by ";":
  B1_NO                          either labeller's B1 is NO on a real key
  B1_UNSURE_OR_BLANK             either labeller's B1 is UNSURE or blank on a real key
  A2_FOUND_NOT_ANSWERABLE        FOUND row (lookup note "one version applies"): either a2 is not ANSWERABLE
                                 (blank/UNSURE included), even when both agree
  A2_UNDATED_NOT_UNDERSPECIFIED  undated row: either a2 is not UNDERSPECIFIED (blank/UNSURE included)
On a seeded row the seeded labeller's B1 is about a planted key: it never creates a flag and is shown as
SEEDED. outcome, reason_class and note are left empty for the owner.
Score: outcome in OUTCOMES (blank or unknown = error naming the id); reason_class in REASON_CLASSES, blank only
for KEY_OK (owner decision D3). Key error rate = KEY_WRONG / n_audited, Clopper-Pearson 95% CI; when
KEY_WRONG = 0 also rule_of_three_upper = 3 / n_audited. Codes, counts and ids only. The tool only reads gold.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from pathlib import Path

from divergence.bench_agree import RUNS_DIR, AgreeError, load_pair
from divergence.bench_label_sheets import LOCAL_ROOT, ONE_VERSION, UNDATED_NOTE, inside
from divergence.binom_ci import clopper_pearson

COLUMNS = ("item_id", "flag", "a_b1", "b_b1", "a_a2", "b_a2", "outcome", "reason_class", "note")
OUTCOMES = ("KEY_OK", "KEY_WRONG", "QUESTION_UNCLEAR", "CONTESTED")
REASON_CLASSES = ("key_wrong", "question_unclear", "misread", "guide_unclear")
FLAGS = ("B1_NO", "B1_UNSURE_OR_BLANK", "A2_FOUND_NOT_ANSWERABLE", "A2_UNDATED_NOT_UNDERSPECIFIED")
SEEDED_CELL = "SEEDED"


class AdjudicateError(ValueError):
    pass


def flags_for(item_id, pair):
    seeded_here = item_id in pair["seeds"]
    b1 = [pair["sheet_b"][tag][item_id]["b1_key_supported"] for tag in ("a", "b")
          if not (seeded_here and tag == pair["seeded"])]
    a2 = [pair["sheet_a"][tag][item_id]["a2_answerability"] for tag in ("a", "b")]
    note = pair["sheet_a"]["a"][item_id]["lookup_note"]
    flags = []
    if "NO" in b1:
        flags.append("B1_NO")
    if any(v in ("UNSURE", "") for v in b1):
        flags.append("B1_UNSURE_OR_BLANK")
    if note == ONE_VERSION and any(v != "ANSWERABLE" for v in a2):
        flags.append("A2_FOUND_NOT_ANSWERABLE")
    if note == UNDATED_NOTE and any(v != "UNDERSPECIFIED" for v in a2):
        flags.append("A2_UNDATED_NOT_UNDERSPECIFIED")
    return flags


def template_rows(pair):
    rows = []
    for item_id in pair["ids"]:
        flags = flags_for(item_id, pair)
        if not flags:
            continue
        row = {"item_id": item_id, "flag": ";".join(flags), "outcome": "", "reason_class": "", "note": ""}
        for tag in ("a", "b"):
            seeded_cell = item_id in pair["seeds"] and tag == pair["seeded"]
            row[f"{tag}_b1"] = SEEDED_CELL if seeded_cell else pair["sheet_b"][tag][item_id]["b1_key_supported"]
            row[f"{tag}_a2"] = pair["sheet_a"][tag][item_id]["a2_answerability"]
        rows.append(row)
    return rows


def _refuse(out):
    out = Path(out)
    if inside(out, RUNS_DIR):
        raise AdjudicateError("refusing to write under divergence/runs/")
    if out.exists():
        raise AdjudicateError(f"refusing to overwrite {out.name}")
    return out


def write_template(rows, out, local_root=LOCAL_ROOT):
    out = _refuse(out)
    if not inside(out, Path(local_root) / "labels"):
        raise AdjudicateError("--out must be inside _local/labels/")
    buf = io.StringIO()
    writer = csv.DictWriter(buf, COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = buf.getvalue().encode("utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def score(csv_path, n_audited):
    path = Path(csv_path)
    if not path.is_file():
        raise AdjudicateError(f"{path.name} not found")
    data = path.read_bytes()
    reader = csv.DictReader(data.decode("utf-8-sig").splitlines())
    if tuple(reader.fieldnames or ()) != COLUMNS:
        raise AdjudicateError("header differs from the adjudication columns")
    rows, seen = [], set()
    for raw in reader:
        row = {k: (v or "").strip() for k, v in raw.items()}
        item_id = row["item_id"]
        if not item_id or item_id in seen:
            raise AdjudicateError(f"blank or repeated item id {item_id!r}")
        seen.add(item_id)
        if row["outcome"] not in OUTCOMES:
            raise AdjudicateError(f"{item_id}: outcome blank or not one of {list(OUTCOMES)}")
        rc = row["reason_class"]
        if rc and rc not in REASON_CLASSES:
            raise AdjudicateError(f"{item_id}: reason_class not one of {list(REASON_CLASSES)}")
        if not rc and row["outcome"] != "KEY_OK":
            raise AdjudicateError(f"{item_id}: reason_class is required when outcome is not KEY_OK")
        rows.append(row)
    if not isinstance(n_audited, int) or n_audited < 1 or n_audited < len(rows):
        raise AdjudicateError(f"--n-audited must be at least 1 and at least the {len(rows)} adjudicated row(s)")
    outcomes = Counter(r["outcome"] for r in rows)
    reasons = Counter(r["reason_class"] or "blank" for r in rows)
    k = outcomes.get("KEY_WRONG", 0)
    return {
        "tool": "bench_adjudicate", "version": 1, "input_sha256": hashlib.sha256(data).hexdigest(),
        "n_adjudicated": len(rows), "n_audited": n_audited, "key_wrong": k,
        "key_error_rate": {"value": k / n_audited, "fraction": f"{k}/{n_audited}"},
        "ci95": list(clopper_pearson(k, n_audited)), "ci_method": "clopper-pearson",
        "rule_of_three_upper": (3 / n_audited) if k == 0 else None,
        "counts_outcome": {o: outcomes.get(o, 0) for o in OUTCOMES},
        "counts_reason_class": {c: reasons.get(c, 0) for c in REASON_CLASSES + ("blank",)},
        "contested_ids": sorted(r["item_id"] for r in rows if r["outcome"] == "CONTESTED"),
        "question_unclear_ids": sorted(r["item_id"] for r in rows if r["outcome"] == "QUESTION_UNCLEAR"),
    }


def write_score(result, out):
    out = _refuse(out)
    data = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def main(argv=None, local_root=LOCAL_ROOT):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--template", action="store_true")
    mode.add_argument("--score", type=Path)
    parser.add_argument("--a", type=Path, nargs="+")
    parser.add_argument("--b", type=Path, nargs="+")
    parser.add_argument("--seed-key", type=Path, nargs="+", default=None)
    parser.add_argument("--seeded", choices=("a", "b"), default="b")
    parser.add_argument("--n-audited", type=int)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.template:
            if not args.a or not args.b:
                raise AdjudicateError("--template needs --a and --b")
            rows = template_rows(load_pair(args.a, args.b, args.seed_key, args.seeded))
            sha = write_template(rows, args.out, local_root)
            per_flag = Counter(f for r in rows for f in r["flag"].split(";"))
            print(f"flagged rows: {len(rows)} (" + ", ".join(f"{f} {per_flag.get(f, 0)}" for f in FLAGS) + ")")
        else:
            if args.n_audited is None:
                raise AdjudicateError("--score needs --n-audited")
            result = score(args.score, args.n_audited)
            sha = write_score(result, args.out)
            print(f"key wrong {result['key_wrong']}/{result['n_audited']} ci95 {result['ci95']}"
                  f" rule_of_three_upper {result['rule_of_three_upper']} outcomes {result['counts_outcome']}")
    except (AdjudicateError, AgreeError) as exc:
        print(f"bench adjudicate: ERROR {exc}", file=sys.stderr)
        return 2
    print(f"wrote {args.out.name} sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
