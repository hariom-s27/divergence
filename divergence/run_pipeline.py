#!/usr/bin/env python3
"""
RUN PIPELINE — DIVERGENCE
Wires the automated front half together: 🤖 1 EXTRACT -> 🤖 2 GAP DETECTOR ->
⚙ A GAP CONSTRAINT ENFORCER. Folds in ⚙ B's existing output (valuation.json,
from node3_valuation.py — unchanged, still no model, no API) and runs ⚙ C
the citation matcher against any resolver conclusions supplied.

Nodes 3/4/5 (income tax, GST, adversarial) are NOT called here. Per the
STEP21 protocol (step21drop/eval/score.py) they are run by hand, fresh
session, and hand-coded into a run file. Pass that file's "regimes" through
--regimes to have THIS script enforce and validate them against the facts{}
and missing[] this run produced automatically — that is the seam between
the manual arms protocol and the automated part of the pipeline.

    python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" \\
        --text cases/D1/case.txt \\
        --regimes cases/D1/regimes_armC.json \\
        --out runs/D1_armC_pipeline.json

Writes a schema.json-shaped disclosure record: validated against schema.json
if the 'jsonschema' package is installed, structurally checked either way.

ERROR HANDLING (architecture.md): a failed step hard-fails here too. A
pipeline that degrades quietly is the exact failure this project exists to
prevent — this script does not try to be helpful about a broken step.
"""

import os, re, sys, json, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import llm_call                             # noqa: E402
from llm_call import LLMError               # noqa: E402
import node1_extract                        # noqa: E402
import node2_gaps                           # noqa: E402
import gap_enforcer                         # noqa: E402
from citation_matcher import verify as cite_verify  # noqa: E402


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def load_regimes(path):
    if not path:
        return []
    if not os.path.exists(path):
        die(f"--regimes file not found: {path}")
    d = json.load(open(path, encoding="utf-8"))
    return d.get("regimes", d) if isinstance(d, dict) else d


def load_valuation(path):
    if not path or not os.path.exists(path):
        return None
    d = json.load(open(path, encoding="utf-8"))
    return d.get("valuation", d)


def manifest_frozen_at():
    """corpus_frozen_at is required by schema.json (C34) — read it from the
    manifest rather than typing a date that can drift out of sync with it."""
    p = os.path.join(HERE, "corpus", "MANIFEST.md")
    if os.path.exists(p):
        m = re.search(r"Regenerated:\s*(\d{4}-\d{2}-\d{2})", open(p, encoding="utf-8").read())
        if m:
            return m.group(1) + "T00:00:00Z"
    return None


def apply_citation_matcher(regimes, tax_year):
    """⚙ C. accept=False -> conclusion DROPPED, not flagged (architecture.md)."""
    kept, dropped = [], []
    for r in regimes:
        cite = dict(r.get("citation") or {})
        v = cite_verify(cite.get("provision", ""), cite.get("tax_year") or tax_year)
        cite["verified"] = v.accept
        r = dict(r, citation=cite)
        if v.accept:
            kept.append(r)
        else:
            dropped.append({
                "regime": r.get("regime"), "citation": cite.get("provision"),
                "status": v.status, "reason": v.reason,
            })
    return kept, dropped


def validate_schema(record):
    schema_path = os.path.join(HERE, "schema.json")
    try:
        import jsonschema
        schema = json.load(open(schema_path, encoding="utf-8"))
        jsonschema.validate(record, schema)
        print("  schema.json: VALID")
        return
    except ImportError:
        pass
    except Exception as e:
        print(f"  schema.json: INVALID — {e}")
        return

    # no jsonschema installed -- fall back to the checks that matter most
    required = ("record_id", "corpus_frozen_at", "missing", "valuation", "regimes", "limits")
    missing_req = [k for k in required if record.get(k) is None]
    print("  schema.json: 'jsonschema' not installed — ran a structural check only")
    print(f"    required fields present: {'OK' if not missing_req else 'MISSING ' + str(missing_req)}")
    methods = (record.get("valuation") or {}).get("methods")
    if methods is not None and len(methods) < 2:
        print("    valuation.methods has < 2 entries — schema violation (minItems: 2)")
    if not record.get("limits"):
        print("    limits[] is empty — schema violation (minItems: 1)")


def main():
    ap = argparse.ArgumentParser(description="Wire nodes 1, 2 and A (and ⚙ B/⚙ C where available) into one run.")
    ap.add_argument("--record-id", required=True)
    ap.add_argument("--tax-year", required=True)
    ap.add_argument("--text", action="append", default=[])
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--regimes", help="hand-coded output from prompts 03/04/05 (run-file 'regimes' shape)")
    ap.add_argument("--valuation", default=os.path.join(HERE, "valuation.json"),
                     help="output of node3_valuation.py (default: ./valuation.json)")
    ap.add_argument("--model", default="small")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if not a.text and not a.file:
        die("give at least one --text or --file input for node 1")

    print("=" * 74)
    print(f"  RUN PIPELINE — {a.record_id}  ({a.tax_year})")
    print(f"  provider={llm_call.provider_name()}  small={llm_call.model_id('small')}")
    print("=" * 74)

    print("\n  [1/4] 🤖 1 EXTRACT")
    try:
        facts, extraction_notes, m1 = node1_extract.extract(a.text, a.file, model=a.model)
    except LLMError as e:
        die(str(e))
    print(f"        {len(facts)} field(s) extracted "
          f"({m1.get('in_tokens', '?')} in / {m1.get('out_tokens', '?')} out tokens, "
          f"{m1.get('retries', 0)} retr(y/ies))")

    print("\n  [2/4] 🤖 2 GAP DETECTOR")
    try:
        missing, m2 = node2_gaps.detect_gaps(facts, model=a.model)
    except LLMError as e:
        die(str(e))
    print(f"        {len(missing)} gap(s) found "
          f"({m2.get('in_tokens', '?')} in / {m2.get('out_tokens', '?')} out tokens, "
          f"{m2.get('retries', 0)} retr(y/ies))")

    regimes_in = load_regimes(a.regimes)
    print(f"\n  [3/4] ⚙ C CITATION MATCHER  ({len(regimes_in)} conclusion(s) supplied via --regimes)")
    regimes, dropped = apply_citation_matcher(regimes_in, a.tax_year)
    for d in dropped:
        print(f"        DROPPED  {d['regime']:<24} {d['citation']!r:<32} {d['status']} — {d['reason']}")
    print(f"        {len(regimes)} kept, {len(dropped)} dropped")

    print("\n  [4/4] ⚙ A GAP CONSTRAINT ENFORCER")
    for r in regimes:
        r.setdefault("depends_on_missing", [])
    record_stub, forced = gap_enforcer.enforce({"regimes": regimes})
    for f in forced:
        print(f"        FORCED   {f['regime']:<24} was {f['was']!r:<14} <- {f['depends_on_missing']}")
    print(f"        {len(forced)} certainty value(s) forced to insufficient_evidence")

    valuation = load_valuation(a.valuation)

    limits = list(extraction_notes)
    for d in dropped:
        limits.append(f"citation dropped: {d['citation']} ({d['status']}) for regime {d['regime']}")
    if regimes_in and not valuation:
        limits.append("valuation.json not found — run node3_valuation.py first; this record has no valuation block")
    if not a.regimes:
        limits.append("no --regimes supplied — nodes 3/4/5 were not run for this record; regimes[] is empty")
    if not limits:
        limits.append("no limitations recorded by nodes 1/2 — review before trusting this record (limits[] must never be silently empty)")

    record = {
        "record_id": a.record_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus_frozen_at": manifest_frozen_at(),
        "tax_year": a.tax_year,
        "facts": facts,
        "missing": missing,
        "valuation": valuation or {"methods": [], "spread": {"inr": 0, "percent": 0}, "uncertainty_budget": []},
        "regimes": record_stub["regimes"],
        "limits": limits,
    }

    out_path = a.out or os.path.join(HERE, "runs", f"{a.record_id}_pipeline.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print("\n" + "=" * 74)
    validate_schema(record)
    prov = llm_call.provenance()
    print(f"  {prov['total_calls']} model call(s), "
          f"{prov['total_in_tokens']} in / {prov['total_out_tokens']} out tokens "
          f"on {prov['provider']}")
    try:
        shown_path = os.path.relpath(out_path, HERE)
    except ValueError:
        shown_path = out_path  # different drive than HERE on Windows -- relpath can't express it
    print(f"  written -> {shown_path}")
    print("=" * 74 + "\n")


if __name__ == "__main__":
    main()
