#!/usr/bin/env python3
"""
run_arms.py  --  run baseline arms A and B (D39).

The pipeline arm (C) has been the only thing ever executed. A results table
with one column is not a result. This runs the other two.

    python run_arms.py --arm A --all-cases
    python run_arms.py --arm B --all-cases --token-match runs/

THE EXPERIMENT ONLY MEANS SOMETHING IF THE ARMS DIFFER IN ONE VARIABLE.

  same model      all three arms use the `large` slot -- the same model the
                  pipeline's resolvers use. Otherwise you measure the model,
                  not the structure.
  same corpus     all three arms get the identical corpus/verbatim/ text.
                  A judge WILL ask "did the baseline see the same law?" The
                  answer has to be yes, or arm C wins by having more facts.
  same tokens     arm B's max_tokens is read from arm C's own measured output
                  (--token-match). D39 says "token-matched"; this makes that
                  a number rather than a word.

  DIFFERENT:      arm A = one call, no scaffolding.
                  arm B = one call, "think step by step", same budget as C.
                  arm C = five calls + three deterministic checks.

  What A and B do NOT get: the gap enforcer, the citation matcher, per-regime
  scoping. Those ARE the treatment. Giving them to the baseline would be
  measuring nothing.

Output: runs/<case>_arm<A|B>.json, same shape as a pipeline record where the
model manages it. When it doesn't, that is recorded rather than repaired --
"arm A produced schema-valid output 2 times out of 6" is a finding, and
quietly fixing it up would delete the finding.
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import llm_call                                        # noqa: E402
from llm_call import LLMError                          # noqa: E402
import node_resolver                                   # noqa: E402
import disagreement_gate                                # noqa: E402

CASES = ["D1", "C1", "C2", "C3", "C4", "C5"]
VERBATIM_DIR = os.path.join(HERE, "corpus", "verbatim")
SCHEMA = os.path.join(HERE, "schema.json")

ARM_PROMPTS = {
    "A": [os.path.join(HERE, "baseline-prompt.md"),
          os.path.join(HERE, "prompts", "arm-a-naive.md")],
    "B": [os.path.join(HERE, "prompts", "arm-b-cot.md")],
}

# D45: an EXAMPLE instance, not the raw schema.json -- see run_one() for why.
# Values are illustrative, not this case's real facts. Shaped from schema.json
# directly -- update both together if the schema changes.
SCHEMA_EXAMPLE = """
=== REQUIRED OUTPUT SHAPE ===
Return ONE JSON object shaped exactly like this example. The values below are
illustrative -- fill in this case's real facts. Every field shown is required
unless marked <optional>. No prose outside the JSON.

{
  "record_id": "<string, e.g. case id + invoice no>",
  "generated_at": "<ISO 8601 date-time>",
  "corpus_frozen_at": "<ISO 8601 date-time -- when the statutory text you were given was frozen>",
  "tax_year": "FY 2026-27",
  "facts": {
    "<field_name>": {"value": "<string|number|null>", "confidence": "certain|probable|declared_only|unresolved", "source_span": "<where in the document this came from>"}
  },
  "missing": [
    {"item": "<document or fact absent>", "why_absent": "<why>", "blocks": ["income_tax|gst|fema|valuation", "..."], "obtainable": "yes|no|not_for_this_route"}
  ],
  "valuation": {
    "methods": [
      {"label": "<method name>", "rate": 0.0, "inr_value": 0.0, "observability": "L1|L2|L3",
       "source": {"name": "<source>", "retrieved": "<date>", "tier": "primary_archived|primary_live|reported|derived"},
       "mandated_by": "<provision requiring this method, or null>", "date_used": "<date>"}
    ],
    "spread": {"inr": 0.0, "percent": 0.0, "between": ["<method a label>", "<method b label>"]},
    "uncertainty_budget": [
      {"source": "<what makes this undetermined>", "inr": 0.0, "explanation": "<why>"}
    ]
  },
  "regimes": [
    {"regime": "income_tax_on_receipt|income_tax_on_transfer|gst_export|fema|valuation_method",
     "outcome": "<one sentence>",
     "certainty": "settled|inference|open_texture|lacuna|contested|insufficient_evidence",
     "citation": {"provision": "<exactly as in the statutory text above>", "former_citation": "<or null>",
                  "tax_year": "FY 2026-27", "verified": false},
     "depends_on_missing": ["<item from missing[] above, or omit if none>"]}
  ],
  "limits": ["<what you could not determine, and why -- never empty>"]
}

NOTE: "valuation.methods" needs at least 2 entries if the law does not
prescribe a single method -- a single figure with no acknowledgment of a
choice is a schema violation, not a valid answer. "limits" must never be
empty.
"""

DEFAULT_MAX_TOKENS = {"A": 4096, "B": 4096}


def die(msg):
    print("\n  ERROR: %s\n" % msg)
    sys.exit(1)


def load_arm_prompt(arm):
    """First existing candidate wins. baseline-prompt.md is FROZEN -- if it is
    there, it is arm A, and this script does not touch it.

    Two heading conventions in this repo: prompts written from Step 22
    onward use '## SYSTEM' (arm-b-cot.md). baseline-prompt.md (Step 16,
    older, frozen) uses '# THE PROMPT' instead -- and the file also contains
    a 'WHAT WE PREDICT' section naming this exact prompt's predicted failure
    modes. Falling through to "send the whole file" would hand the model
    its own predicted mistakes as context. Try both headings; refuse to
    fall back to the raw file for either -- a silent full-file send is a
    worse failure than a loud one here."""
    for path in ARM_PROMPTS[arm]:
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        for marker in ("## SYSTEM", "# THE PROMPT"):
            if marker in text:
                parts = text.split(marker, 1)[1].split("```", 2)
                if len(parts) >= 3:
                    return parts[1].strip(), path
        die("%s has neither a '## SYSTEM' nor a '# THE PROMPT' fenced block -- "
            "refusing to send the whole file as a prompt (it likely contains "
            "meta-commentary, not just the prompt itself)." % path)
    die("no prompt found for arm %s. Looked for:\n    %s"
        % (arm, "\n    ".join(ARM_PROMPTS[arm])))


def load_corpus():
    files = sorted(glob.glob(os.path.join(VERBATIM_DIR, "*.md")))
    if not files:
        die("corpus/verbatim/ is empty. Run split_corpus.py first -- and note "
            "that a stale verbatim/ has bitten this project once already.")
    chunks = []
    for f in files:
        chunks.append("--- %s ---\n%s" % (os.path.basename(f),
                                          open(f, encoding="utf-8").read().strip()))
    return "\n\n".join(chunks), [os.path.basename(f) for f in files]


def find_case(case):
    # D49: input.md (mechanically generated from frozen ground truth,
    # 21 Aug) is the complete document -- prefer it over case.md, which
    # D48 found was missing facts ground truth expects (counterparty name,
    # invoice number; C3 was missing its own amount/asset). It only ever
    # lives under step21drop/cases/, so check that exact file FIRST, before
    # falling into the case.md search below -- case.md exists in both
    # directories and would otherwise win by directory order alone.
    input_md = os.path.join(HERE, "step21drop", "cases", case, "input.md")
    if os.path.exists(input_md):
        return input_md

    # cases/ before step21drop/cases/ for case.md, same reason as before:
    # it's what eval/score.py and m3b_citation_coverage.py both resolve to
    # (ROOT/cases), the copy citations_expected[] was actually filled into
    # on 20 Aug. step21drop/cases/ is the Step 21 drop snapshot -- checking
    # it first would silently prefer stale ground truth.
    for base in (os.path.join(HERE, "cases"),
                 os.path.join(HERE, "step21drop", "cases")):
        p = os.path.join(base, case, "case.md")
        if os.path.exists(p):
            return p
    die("case.md not found for %s" % case)


def token_budget(arm, case, token_match_dir):
    """Arm B is matched to arm C's MEASURED output tokens for the same case.

    D45 caught a real bug here: arm C's total_out_tokens is the SUM across
    several small node calls (node 1 writes only facts{}, node 2 writes only
    missing[]), each producing a fraction of a full record. Arm B has to
    write the whole record in ONE completion. Floor that at 256 and the
    match silently starves arm B on any case where arm C's current record
    is a partial multi-call pipeline run (today: every case -- regimes[] is
    still empty on all of them, nodes 3/4/5 are hand-run) -- the model gets
    cut off mid-facts{} and never produces parseable JSON at all. That is
    not a finding about arm B's reasoning; it is a budget arithmetic error.
    Floor at DEFAULT_MAX_TOKENS instead: token-match UP when arm C's real
    total exceeds the default (informative), never DOWN below what a
    single-shot completion has already been shown to need."""
    if arm != "B" or not token_match_dir:
        return DEFAULT_MAX_TOKENS[arm], None
    for pat in ("%s_pipeline.json" % case, "%s_*pipeline*.json" % case):
        hits = sorted(glob.glob(os.path.join(token_match_dir, pat)))
        if hits:
            try:
                rec = json.load(open(hits[-1], encoding="utf-8"))
                n = rec.get("_meta", {}).get("llm", {}).get("total_out_tokens")
                if n:
                    floored = max(int(n), DEFAULT_MAX_TOKENS["B"])
                    return floored, os.path.basename(hits[-1])
            except Exception:
                pass
    print("    [warn] no arm-C record for %s in %s -- falling back to %d. "
          "Say so in results.md rather than calling this token-matched."
          % (case, token_match_dir, DEFAULT_MAX_TOKENS["B"]))
    return DEFAULT_MAX_TOKENS["B"], None


def validate(record):
    if not os.path.exists(SCHEMA):
        return None, "schema.json not found"
    try:
        import jsonschema
    except ImportError:
        return None, "jsonschema not installed"
    try:
        jsonschema.validate(record, json.load(open(SCHEMA, encoding="utf-8")))
        return True, None
    except Exception as e:
        return False, str(e).splitlines()[0][:200]


def run_one(arm, case, corpus, corpus_files, tax_year, out_dir, token_match_dir):
    system, prompt_path = load_arm_prompt(arm)
    case_text = open(find_case(case), encoding="utf-8").read()
    max_tokens, matched_from = token_budget(arm, case, token_match_dir)

    # The output contract goes to every arm -- but as an EXAMPLE instance, in
    # the same style prompts 01-05 use (a filled JSON template with
    # <placeholder> markers), not the raw formal schema.json. Tried the raw
    # schema first (D45): the 72B model conflated the schema DEFINITION with
    # a data INSTANCE on 6/6 cases, filling answer values into the schema's
    # own "properties" object instead of producing a record shaped like it.
    # Withholding the contract entirely would make the arm fail on
    # formatting rather than reasoning; handing it the raw Draft-2020-12
    # schema syntax did exactly that anyway, just less obviously. An example
    # instance is the same contract, in the form every other prompt in this
    # project already gives a model successfully.
    schema_text = SCHEMA_EXAMPLE if os.path.exists(SCHEMA) else ""

    user = (
        "TAX YEAR: %s\n\n"
        "=== THE CASE ===\n%s\n\n"
        "=== STATUTORY TEXT (verbatim) ===\n%s\n"
        "%s"
        % (tax_year, case_text, corpus, schema_text)
    )

    print("  arm %s  %-4s  model=%s  max_tokens=%d%s"
          % (arm, case, llm_call.model_id("large"), max_tokens,
             ("  [matched to %s]" % matched_from) if matched_from else ""))

    llm_call.reset_provenance()
    node = "arm%s_%s" % (arm, case)
    err = None
    record = None
    try:
        record = llm_call.call_json(system, user, "large",
                                    max_tokens=max_tokens, node_name=node)
    except LLMError as e:
        err = str(e)
        print("      FAILED TO PRODUCE JSON -- recorded, not repaired")

    ok, why = (None, None) if record is None else validate(record)
    prov = llm_call.provenance()

    out = {
        "arm": arm,
        "case": case,
        "tax_year": tax_year,
        "schema_valid": ok,
        "schema_error": why,
        "produced_json": record is not None,
        "error": err,
        "record": record,
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "prompt_file": os.path.relpath(prompt_path, HERE),
            "corpus_files": corpus_files,
            "max_tokens": max_tokens,
            "token_matched_to": matched_from,
            "scaffolding": "none -- no gap enforcer, no citation matcher, no scoping",
            "schema_given_to_arm": os.path.exists(SCHEMA),
            "llm": prov,
        },
    }

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "%s_arm%s.json" % (case, arm))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    status = "json+schema OK" if ok else ("json, schema FAILED" if record is not None
                                          else "NO JSON")
    print("      -> %s  [%s]  %d out-tokens, %d retries"
          % (os.path.basename(path), status,
             prov["total_out_tokens"],
             sum(r["retries"] for r in prov["by_node"].values())))
    return out


def run_one_d(case, source_path, tax_year, out_dir, k):
    """Arm D (D75): the deterministic k-sample disagreement gate, wired
    in as its own arm so eval/score.py can score it against the same
    ground truth as A/B/C, unmodified.

    UNLIKE arms A/B, arm D does not call the model on raw case text --
    it needs facts{}/missing{} that already exist (nodes 1/2's job, out
    of scope for this file). --source names ONE real, already-produced
    pipeline record to pull facts{}, missing{}, and the valuation lattice
    from -- an explicit file, not a directory glob. find_case()'s own
    history (a stale case.md silently winning by directory order,
    Block B/D49) is exactly the failure mode an explicit --source
    avoids: arm D's ground-truth facts should never be a silent 'closest
    match found in this directory' guess.

    For each regime the source record actually resolved (income_tax_*,
    gst_*, valuation_method, fema -- whatever NODE_NAME's regimes
    actually cover for this case), calls node_resolver.resolve_k() for
    real, k times, THEN disagreement_gate.cluster()/apply_downgrade() on
    the k raw samples. Sample 0 is the fixed baseline apply_downgrade()
    mutates -- an arbitrary but disclosed choice (see
    disagreement_gate.apply_downgrade()'s own docstring), not a vote.
    """
    source = json.load(open(source_path, encoding="utf-8"))
    facts = source.get("facts", {})
    missing = source.get("missing", [])
    if not facts:
        die("%s has no facts{} -- arm D needs a real pipeline record with "
            "nodes 1/2 already run, not a raw case file." % source_path)

    regimes_present = sorted({r.get("regime") for r in source.get("regimes", []) if r.get("regime")})
    regime_keys = []
    if any(r.startswith("income_tax") for r in regimes_present) or "valuation_method" in regimes_present:
        regime_keys.append("income_tax")
    if any(r.startswith("gst") for r in regimes_present):
        regime_keys.append("gst")
    if not regime_keys:
        die("%s's regimes[] names nothing income_tax/gst -- nothing for "
            "arm D to re-sample. regimes present: %r" % (source_path, regimes_present))

    try:
        model_line = llm_call.model_id("large")
    except LLMError:
        model_line = "large"  # diagnostic line only -- the real call below still
                               # raises/is caught properly if the key is genuinely missing
    print("  arm D  %-4s  model=%s  k=%d  regimes=%s"
          % (case, model_line, k, regime_keys))

    ksample_dir = os.path.join(out_dir, "ksamples")
    all_downgraded_regimes = []
    all_budget_items = []
    clusters_by_regime = {}
    manifests_by_regime = {}
    err = None
    try:
        for regime_key in regime_keys:
            samples, manifest = node_resolver.resolve_k(
                regime_key, facts, missing, tax_year, k=k, model="large",
                out_dir=ksample_dir, record_id="%s_armD" % case,
            )
            clusters = disagreement_gate.cluster([s["regimes"] for s in samples])
            baseline = samples[0]["regimes"]
            downgraded, budget_items = disagreement_gate.apply_downgrade(baseline, clusters)
            all_downgraded_regimes.extend(downgraded)
            all_budget_items.extend(budget_items)
            clusters_by_regime[regime_key] = clusters
            manifests_by_regime[regime_key] = manifest
    except (LLMError, RuntimeError, ValueError) as e:
        err = str(e)
        print("      FAILED -- %s -- recorded, not repaired" % err)

    record = None
    if err is None:
        valuation = json.loads(json.dumps(source.get("valuation", {})))  # deep copy
        valuation.setdefault("uncertainty_budget", [])
        valuation["uncertainty_budget"] = valuation["uncertainty_budget"] + all_budget_items
        record = {
            "record_id": source.get("record_id", case),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "corpus_frozen_at": source.get("corpus_frozen_at"),
            "tax_year": tax_year,
            "facts": facts,
            "missing": missing,
            "valuation": valuation,
            "regimes": all_downgraded_regimes,
            "limits": source.get("limits", []) + (
                ["Arm D (D75): certainty on %d regime(s) was overwritten to 'contested' "
                 "by the k-sample disagreement rule; see each regime's own "
                 "_k_sample_downgrade field and the matching uncertainty_budget "
                 "line item for the raw k-sample breakdown." %
                 sum(1 for r in all_downgraded_regimes if "_k_sample_downgrade" in r)]
                if any("_k_sample_downgrade" in r for r in all_downgraded_regimes) else []
            ),
        }

    ok, why = (None, None) if record is None else validate(record)

    out = {
        "arm": "D",
        "case": case,
        "tax_year": tax_year,
        "schema_valid": ok,
        "schema_error": why,
        "produced_json": record is not None,
        "error": err,
        "record": record,
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_file": os.path.relpath(source_path, HERE),
            "k": k,
            "regimes_sampled": regime_keys,
            "scaffolding": "k-sample resolver + deterministic clustering/downgrade "
                           "(D75) -- no gap enforcer, no citation matcher, no "
                           "scope enforcer run on arm D's own output; this arm "
                           "tests resolver stability, not the full pipeline",
            "schema_given_to_arm": os.path.exists(SCHEMA),
            "clusters": clusters_by_regime,
            "sample_manifests": manifests_by_regime,
        },
    }

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "%s_armD.json" % case)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    status = "json+schema OK" if ok else ("json, schema FAILED" if record is not None else "NO JSON")
    n_downgraded = sum(1 for r in all_downgraded_regimes if "_k_sample_downgrade" in r)
    print("      -> %s  [%s]  %d/%d regime(s) downgraded to contested"
          % (os.path.basename(path), status, n_downgraded, len(all_downgraded_regimes)))
    return out


def main():
    ap = argparse.ArgumentParser(description="Run baseline arms A/B, or arm D (D75)")
    ap.add_argument("--arm", required=True, choices=["A", "B", "D"])
    ap.add_argument("--case", action="append", default=[])
    ap.add_argument("--all-cases", action="store_true")
    ap.add_argument("--tax-year", default="FY 2026-27")
    ap.add_argument("--out", default=os.path.join(HERE, "runs"))
    ap.add_argument("--token-match", default=None,
                    help="dir holding arm-C pipeline records (arm B only)")
    ap.add_argument("--source", default=None,
                    help="arm D only: ONE real pipeline record file to pull "
                         "facts{}/missing{} from (e.g. runs/21aug/D1_final_seed2.json)")
    ap.add_argument("--k", type=int, default=5, help="arm D only: samples per regime")
    a = ap.parse_args()

    cases = CASES if a.all_cases else a.case
    if not cases:
        die("give --case D1 (repeatable) or --all-cases")

    if a.arm == "D":
        if not a.source:
            die("--arm D needs --source <real pipeline record>.json -- arm D "
                "resamples an existing record's resolver calls, it does not "
                "run nodes 1/2 itself.")
        if len(cases) != 1:
            die("--arm D takes exactly one --case (it reads facts from a single "
                "--source file, which belongs to one case) -- run it once per case.")
        try:
            provider_line = llm_call.provider_name()
        except LLMError as e:
            die(str(e))
        print("\n  provider : %s" % provider_line)
        print("  arm D    : k=%d, source=%s" % (a.k, a.source))
        print()
        out = run_one_d(cases[0], a.source, a.tax_year, a.out, a.k)
        print("\n  ARM D over 1 case(s)")
        print("    produced parseable JSON : %d/1" % (1 if out["produced_json"] else 0))
        print("    schema-valid            : %d/1" % (1 if out["schema_valid"] else 0))
        print("\n  Normalize and score exactly like A/B/C:")
        print("    python eval/normalize_runs.py --dir %s --report\n" % a.out)
        return

    corpus, corpus_files = load_corpus()
    try:
        provider_line = llm_call.provider_name()
    except LLMError as e:
        die(str(e))
    print("\n  provider : %s" % provider_line)
    print("  corpus   : %d verbatim file(s), %d chars -- identical for every arm"
          % (len(corpus_files), len(corpus)))
    print()

    results = [run_one(a.arm, c, corpus, corpus_files, a.tax_year, a.out,
                       a.token_match) for c in cases]

    n = len(results)
    j = sum(1 for r in results if r["produced_json"])
    s = sum(1 for r in results if r["schema_valid"])
    print("\n  ARM %s over %d case(s)" % (a.arm, n))
    print("    produced parseable JSON : %d/%d" % (j, n))
    print("    schema-valid            : %d/%d" % (s, n))
    print("\n  Put both numbers in results.md. A baseline that cannot hold the")
    print("  output contract is a finding about unstructured prompting, not an")
    print("  embarrassment to smooth over.\n")


if __name__ == "__main__":
    main()
