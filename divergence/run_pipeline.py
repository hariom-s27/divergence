#!/usr/bin/env python3
"""
RUN PIPELINE — DIVERGENCE
Wires the full automated chain: 🤖 1 EXTRACT -> 🤖 2 GAP DETECTOR ->
🤖 3/4 INCOME TAX + GST RESOLVERS -> ⚙ C CITATION MATCHER ->
⚙ A GAP CONSTRAINT ENFORCER. Folds in ⚙ B's existing output (valuation.json,
from node3_valuation.py — unchanged, still no model, no API).

D46 Step 1: nodes 3/4 used to be hand-run only, so regimes[] was empty on
every real record and every arm-C citation number in the results table was
an incomplete run, not a measurement. They are automated now, via
node_resolver.py, and run by default. Node 5 (adversarial) is still not
called here — it needs a full assembled record as input and is its own
step (Step 5), not this one.

--regimes still exists, ADDITIVELY: pass a hand-run or hand-planted file
(e.g. the D1-a/b/c/d ablation variants, or a node 5 adversarial pass once
that exists) and its conclusions are merged in alongside the two automated
resolvers', then both go through the same citation matcher and gap
enforcer. --skip-resolvers turns the automated pair off entirely, for
testing just nodes 1/2 the way earlier runs did.

    python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" \\
        --text cases/D1/case.txt \\
        --out runs/D1_pipeline.json

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
import node_resolver                        # noqa: E402
import node5_adversarial                    # noqa: E402
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
    if methods is not None and len(methods) < 1:
        print("    valuation.methods is empty — schema violation (minItems: 1, D51)")
    if not record.get("limits"):
        print("    limits[] is empty — schema violation (minItems: 1)")


def main():
    ap = argparse.ArgumentParser(description="Wire nodes 1, 2, 3, 4, ⚙ C and ⚙ A into one run.")
    ap.add_argument("--record-id", required=True)
    ap.add_argument("--tax-year", required=True)
    ap.add_argument("--text", action="append", default=[])
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--regimes", help="ADDITIONAL hand-coded conclusions (e.g. a planted-defect "
                     "variant, or a node 5 pass), merged in alongside nodes 3/4's own output")
    ap.add_argument("--skip-resolvers", action="store_true",
                     help="don't call nodes 3/4 — test just nodes 1/2, regimes[] stays empty "
                          "unless --regimes supplies something")
    ap.add_argument("--valuation", default=os.path.join(HERE, "valuation.json"),
                     help="output of node3_valuation.py (default: ./valuation.json)")
    ap.add_argument("--model", default="small")
    ap.add_argument("--resolver-model", default="large")
    ap.add_argument("--node5", action="store_true",
                     help="Step 5: run the adversarial checker on the assembled regimes[] "
                          "before writing the record. Off by default so every existing run "
                          "stays reproducible without it.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if not a.text and not a.file:
        die("give at least one --text or --file input for node 1")

    N = 6 if a.node5 else 5

    print("=" * 74)
    print(f"  RUN PIPELINE — {a.record_id}  ({a.tax_year})")
    print(f"  provider={llm_call.provider_name()}  small={llm_call.model_id('small')}"
          f"  large={llm_call.model_id('large')}")
    print("=" * 74)

    print(f"\n  [1/{N}] 🤖 1 EXTRACT")
    try:
        facts, extraction_notes, m1 = node1_extract.extract(a.text, a.file, model=a.model)
    except LLMError as e:
        die(str(e))
    print(f"        {len(facts)} field(s) extracted "
          f"({m1.get('in_tokens', '?')} in / {m1.get('out_tokens', '?')} out tokens, "
          f"{m1.get('retries', 0)} retr(y/ies))")

    print(f"\n  [2/{N}] 🤖 2 GAP DETECTOR")
    try:
        missing, m2 = node2_gaps.detect_gaps(facts, model=a.model)
    except LLMError as e:
        die(str(e))
    print(f"        {len(missing)} gap(s) found "
          f"({m2.get('in_tokens', '?')} in / {m2.get('out_tokens', '?')} out tokens, "
          f"{m2.get('retries', 0)} retr(y/ies))")

    resolver_limits = []
    regimes_in = list(load_regimes(a.regimes))
    if not a.skip_resolvers:
        print(f"\n  [3/{N}] 🤖 3/4 INCOME TAX + GST RESOLVERS")
        for regime in ("income_tax", "gst"):
            try:
                r_regimes, r_limits, m34 = node_resolver.resolve(regime, facts, missing, a.tax_year,
                                                                  model=a.resolver_model)
            except LLMError as e:
                die(str(e))
            print(f"        {regime:<11} {len(r_regimes)} conclusion(s), {len(r_limits)} limit(s) "
                  f"({m34.get('in_tokens', '?')} in / {m34.get('out_tokens', '?')} out tokens, "
                  f"{m34.get('retries', 0)} retr(y/ies))")
            regimes_in.extend(r_regimes)
            resolver_limits.extend(r_limits)
    else:
        print(f"\n  [3/{N}] 🤖 3/4 INCOME TAX + GST RESOLVERS  (skipped, --skip-resolvers)")

    print(f"\n  [4/{N}] ⚙ C CITATION MATCHER  ({len(regimes_in)} conclusion(s) total)")
    regimes, dropped = apply_citation_matcher(regimes_in, a.tax_year)
    for d in dropped:
        print(f"        DROPPED  {d['regime']:<24} {d['citation']!r:<32} {d['status']} — {d['reason']}")
    print(f"        {len(regimes)} kept, {len(dropped)} dropped")

    print(f"\n  [5/{N}] ⚙ A GAP CONSTRAINT ENFORCER")
    for r in regimes:
        r.setdefault("depends_on_missing", [])
    record_stub, forced = gap_enforcer.enforce({"regimes": regimes})
    for f in forced:
        print(f"        FORCED   {f['regime']:<24} was {f['was']!r:<14} <- {f['depends_on_missing']}")
    print(f"        {len(forced)} certainty value(s) forced to insufficient_evidence")

    valuation = load_valuation(a.valuation)

    attacked = None
    if a.node5:
        print(f"\n  [6/{N}] 🤖 5 ADVERSARIAL CHECKER")
        try:
            attacked, survived, a5_limits, m5 = node5_adversarial.check(
                regimes, missing, valuation or {}, a.tax_year)
        except LLMError as e:
            die(str(e))
        landed = [x for x in attacked if not x.get("survived")]
        print(f"        {len(attacked)} attack(s), {len(landed)} landed, "
              f"{len(survived)} conclusion(s) checked and survived "
              f"({m5.get('in_tokens', '?')} in / {m5.get('out_tokens', '?')} out tokens, "
              f"{m5.get('retries', 0)} retr(y/ies))")
        for at in landed:
            print(f"        LANDED   {at.get('target')!r:<40} -> {at.get('downgraded_to')}")

    limits = list(extraction_notes) + resolver_limits
    for d in dropped:
        limits.append(f"citation dropped: {d['citation']} ({d['status']}) for regime {d['regime']}")
    if regimes_in and not valuation:
        limits.append("valuation.json not found — run node3_valuation.py first; this record has no valuation block")
    if a.skip_resolvers and not a.regimes:
        limits.append("--skip-resolvers was set and no --regimes supplied — regimes[] is empty")
    if a.node5:
        limits.extend(a5_limits)
        if any(not x.get("survived") for x in attacked):
            limits.append(
                "node 5 landed at least one attack (see attacked[].downgraded_to) — this is "
                "NOT auto-applied to regimes[].certainty above. Matching attacked[].target "
                "(free text) back to a specific regimes[] entry was judged more likely to "
                "silently corrupt the wrong entry than to help; cross-reference by eye."
            )
    if not limits:
        limits.append("no limitations recorded by nodes 1/2/3/4 — review before trusting this record (limits[] must never be silently empty)")

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
        "_meta": {"llm": llm_call.provenance()},
    }
    if a.node5:
        record["attacked"] = attacked

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
