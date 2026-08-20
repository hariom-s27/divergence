#!/usr/bin/env python3
"""
GAP CONSTRAINT ENFORCER — ⚙ A — DIVERGENCE
Deterministic. No model. No API. This is the difference between a hope and
a guarantee.

architecture.md, ⚙ A: "Any conclusion whose depends_on_missing[] is
non-empty has its certainty set to insufficient_evidence. In code.
Unconditionally."

What fails without it. The gap detector becomes a suggestion — a
sufficiently fluent chain of reasoning talks its way past the missing
document, and nothing stops it. "We ask the model to respect the gap list"
is a request; "a conclusion that depends on a missing field cannot be
emitted" is enforced here, in ordinary code that cannot be argued with.

    python gap_enforcer.py --self-test
    python gap_enforcer.py --record runs/D1_armC.json

    from gap_enforcer import enforce
    record, forced = enforce(record)
"""

import os, sys, json, argparse

FORCED_CERTAINTY = "insufficient_evidence"


def enforce(record: dict):
    """Any regime conclusion with a non-empty depends_on_missing[] has its
    certainty forced to FORCED_CERTAINTY, unconditionally — regardless of
    what certainty value was asserted. Returns (record, forced), where
    forced is the audit trail: every override actually applied, so a run
    that changed nothing says so explicitly rather than by omission.
    """
    forced = []
    for regime in record.get("regimes", []):
        deps = regime.get("depends_on_missing") or []
        if deps and regime.get("certainty") != FORCED_CERTAINTY:
            forced.append({
                "regime": regime.get("regime"),
                "was": regime.get("certainty"),
                "depends_on_missing": list(deps),
            })
            regime["certainty"] = FORCED_CERTAINTY
    return record, forced


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────
# Self-test — a fluent, confident conclusion that talks past the gap list,
# and one that has nothing to do with it. Both must come out right.
# ─────────────────────────────────────────────────────────────

SELF_TEST = {
    "regimes": [
        {
            "regime": "gst_export",
            "outcome": "The supply qualifies as an export of services.",
            "certainty": "settled",  # a fluent model asserting past the gap
            "citation": {"provision": "Section 2(6), IGST Act", "tax_year": "FY 2026-27", "verified": True},
            "depends_on_missing": ["bank certificate of foreign inward remittance (FIRC)"],
        },
        {
            "regime": "income_tax_on_receipt",
            "outcome": "Taxable on transfer under s.115BBH.",
            "certainty": "inference",
            "citation": {"provision": "Section 115BBH", "tax_year": "FY 2026-27", "verified": True},
            "depends_on_missing": [],
        },
    ]
}


def self_test():
    record, forced = enforce(json.loads(json.dumps(SELF_TEST)))  # deep copy — never mutate the fixture
    ok1 = record["regimes"][0]["certainty"] == FORCED_CERTAINTY
    ok2 = record["regimes"][1]["certainty"] == "inference"  # untouched — nothing to enforce

    print("\n  SELF-TEST — gap constraint enforcer\n")
    print(f"  {'regime':<24}{'depends_on_missing':<10}{'result':<26}")
    print("  " + "-" * 66)
    print(f"  {'gst_export':<24}{'yes':<10}{record['regimes'][0]['certainty']:<26}{'OK' if ok1 else 'FAIL'}")
    print(f"  {'income_tax_on_receipt':<24}{'no':<10}{record['regimes'][1]['certainty']:<26}{'OK' if ok2 else 'FAIL'}")

    print(f"\n  forced (the audit trail — {len(forced)} override(s)):")
    for f in forced:
        print(f"    {f['regime']:<24} was {f['was']!r:<12} <- depends on {f['depends_on_missing']}")

    passed = int(ok1) + int(ok2)
    print(f"\n  {passed}/2 as expected.")
    print("  Every override above happened in code. Nothing here asked the model nicely.\n")
    if passed != 2:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", help="a JSON file with a top-level 'regimes' array")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--out", help="default: overwrite --record in place")
    a = ap.parse_args()

    if a.self_test or not a.record:
        self_test()
        return

    if not os.path.exists(a.record):
        die(f"{a.record} not found")
    record = json.load(open(a.record, encoding="utf-8"))
    if "regimes" not in record:
        die(f"{a.record} has no top-level 'regimes' array")

    record, forced = enforce(record)

    out_path = a.out or a.record
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print(f"\n  {len(forced)} conclusion(s) forced to {FORCED_CERTAINTY}")
    for x in forced:
        print(f"    {x['regime']:<24} was {x['was']!r:<12} <- depends on {x['depends_on_missing']}")
    print(f"  written -> {os.path.relpath(out_path)}\n")


if __name__ == "__main__":
    main()
