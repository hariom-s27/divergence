#!/usr/bin/env python3
"""
NODE RESOLVER  ·  nodes 🤖 3 (income tax) and 🤖 4 (GST)  ·  DIVERGENCE
Model: "large". Corpus: scoped per regime, verbatim only (D31).

Step 1 of the D46 plan: arm C's regimes[] has been empty on every real run
so far because nothing ever automated prompts 03/04 -- they existed only as
hand-run prompt specs. Every "arm C: 0.000 recall" in the results so far is
an incomplete run, not a measurement. This is what makes it complete.

    python node_resolver.py --regime income_tax --facts facts.json --missing missing.json --tax-year "FY 2026-27"
    python node_resolver.py --regime gst --facts facts.json --missing missing.json --tax-year "FY 2026-27"

One script, not two, because prompts 03 and 04 are the same shape end to
end: a scoped verbatim corpus, the "large" model slot, and the identical
{"regimes": [...], "limits": [...]} output contract. The only real
difference is which corpus files get injected and which prompt file's
SYSTEM block is used -- everything else, including the five rules both
prompts state ("cite only from the text above", "every citation carries a
tax year", certainty enum discipline, never a bare rupee figure, non-empty
limits), is shared, not duplicated per regime.

Reads   the SYSTEM block of step22drop/prompts/03-income-tax.md (income_tax)
        or step22drop/prompts/04-gst.md (gst)
        the fixed, scoped corpus files each prompt documents
Writes  regimes.json: {"regimes": [...], "limits": [...]}  when run standalone
"""

import os, sys, json, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import llm_call  # noqa: E402
from llm_call import LLMError  # noqa: E402
import citation_matcher  # noqa: E402

PROMPT_FILES = {
    "income_tax": os.path.join(HERE, "step22drop", "prompts", "03-income-tax.md"),
    "gst":        os.path.join(HERE, "step22drop", "prompts", "04-gst.md"),
}

# Named explicitly in each prompt's own scope table (03-income-tax.md,
# 04-gst.md). Kept in one place so the prompt's documented scope and the
# code's actual scope cannot drift, same discipline as node2_gaps.py.
CORPUS_FILES = {
    "income_tax": [
        "IT-2-47A.md", "IT-115BBH.md", "IT-393-1-T8vi.md",
        "ITR2026-RULE-56.md", "ITR2026-RULE-57.md", "ITR2026-RULE-206.md",
        "ITR2026-RULE-207.md", "ITR2026-RULE-247.md",
        "ITR2026-RCASP-VALUATION.md", "IT-439-8.md",
    ],
    "gst": [
        "GST-IGST-2-6.md", "GST-CGST-50.md", "GST-CGST-74A.md",
    ],
}

NODE_NAME = {"income_tax": "node3_income_tax", "gst": "node4_gst"}

VALID_CERTAINTY = {"settled", "inference", "open_texture", "lacuna", "contested", "insufficient_evidence"}
VALID_REGIME = {"income_tax_on_receipt", "income_tax_on_transfer", "gst_export", "fema", "valuation_method"}


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def load_system_prompt(regime):
    path = PROMPT_FILES[regime]
    if not os.path.exists(path):
        die(f"{path} not found")
    text = open(path, encoding="utf-8").read()
    marker = "## SYSTEM"
    if marker not in text:
        die(f"{path} has no '## SYSTEM' section")
    fenced = text.split(marker, 1)[1].split("```", 2)
    if len(fenced) < 3:
        die(f"{path}'s SYSTEM section is not fenced with ```")
    return fenced[1].strip()


def load_scoped_corpus(regime):
    """Found live, 20 Aug: heading each block with the bare filename
    ("--- IT-115BBH.md ---") let the model cite the FILENAME as if it were
    the legal citation -- D1's real run produced
    'provision': 'IT-2-47A.md, IT-115BBH.md, ...'. Heading each block with
    its actual current_citation instead (same string citation_matcher.py
    itself would accept) teaches the model the right citation form to use,
    not just the right text to read."""
    corpus_dir = os.path.join(HERE, "corpus", "verbatim")
    tier_a_dir = os.path.join(HERE, "corpus", "tier-a")
    parts = []
    for fn in CORPUS_FILES[regime]:
        p = os.path.join(corpus_dir, fn)
        if not os.path.exists(p):
            die(f"scoped corpus file missing for regime={regime}: {p}\n"
                f"  {os.path.basename(PROMPT_FILES[regime])}'s scope table names it -- either "
                f"restore the file or update both the prompt and CORPUS_FILES together.")
        tier_a_p = os.path.join(tier_a_dir, fn)
        meta = citation_matcher.parse_front_matter(tier_a_p) if os.path.exists(tier_a_p) else {}
        heading = meta.get("current_citation") or fn
        parts.append(f"--- {heading} ---\n" + open(p, encoding="utf-8").read())
    return "\n\n".join(parts)


def _validate_regimes_shape(regimes, raw):
    """Same discipline as node1_extract.py's _validate_facts_shape: catch a
    contract violation here, at the node that produced it, not three steps
    downstream as an opaque schema error."""
    bad = []
    for i, r in enumerate(regimes):
        if not isinstance(r, dict):
            bad.append((i, "not an object")); continue
        if r.get("regime") not in VALID_REGIME:
            bad.append((i, f"regime={r.get('regime')!r} not in {sorted(VALID_REGIME)}")); continue
        if r.get("certainty") not in VALID_CERTAINTY:
            bad.append((i, f"certainty={r.get('certainty')!r} not in {sorted(VALID_CERTAINTY)}")); continue
        cite = r.get("citation")
        if not isinstance(cite, dict) or "provision" not in cite or "tax_year" not in cite:
            bad.append((i, "citation missing provision/tax_year")); continue
    if bad:
        raise LLMError(
            f"regimes[] contains {len(bad)} malformed entr(y/ies): {bad}\n"
            f"Raw model output:\n{raw}"
        )


def resolve(regime, facts, missing, tax_year, model="large"):
    """The reusable entry point -- run_pipeline.py calls this directly.
    Returns (regimes, limits, meta) -- meta is this node's row from
    llm_call.provenance() after the call."""
    if regime not in PROMPT_FILES:
        raise ValueError(f"regime must be one of {list(PROMPT_FILES)}, got {regime!r}")
    system = load_system_prompt(regime)
    corpus_text = load_scoped_corpus(regime)
    user = (
        f"TAX YEAR: {tax_year}\n\n"
        f"FACTS (from node 1):\n{json.dumps(facts, indent=2)}\n\n"
        f"MISSING (from node 2 -- any conclusion depending on one of these must set "
        f"depends_on_missing accordingly):\n{json.dumps(missing, indent=2)}\n\n"
        f"STATUTORY TEXT (verbatim, scoped to this regime only):\n{corpus_text}"
    )
    node_name = NODE_NAME[regime]
    parsed = llm_call.call_json(system, user, model, node_name=node_name)
    if "regimes" not in parsed or not isinstance(parsed["regimes"], list):
        raise LLMError(f"{node_name}: model output has no top-level 'regimes' array\n{parsed}")
    _validate_regimes_shape(parsed["regimes"], parsed)
    meta = llm_call.provenance()["by_node"].get(node_name, {})
    return parsed["regimes"], parsed.get("limits", []), meta


def resolve_k(regime, facts, missing, tax_year, k=5, model="large",
               out_dir=None, record_id="record"):
    """D75: k independent samples of the SAME resolver call, for
    disagreement_gate.py's cluster()/apply_downgrade() to compare.

    A PLAIN PYTHON LOOP CALLING resolve() k TIMES -- not a batch or n=
    API parameter. Featherless's own /v1/chat/completions docs (quoted
    verbatim in README.md/DECISION-D72.md) do not document an n= choices
    parameter the way OpenAI's API does; inventing a call shape the
    provider doesn't document, on the hope it's silently supported, is
    exactly the kind of unverified assumption this project's own
    citation discipline exists to refuse. Five real, separate, billed
    calls it is.

    TEMPERATURE: deliberately untouched here. llm_call.temperature()
    already returns None -- "send no temperature, the model's own
    default" -- unless DIVERGENCE_DEV=1 or DIVERGENCE_TEMPERATURE is set
    (D52). k samples run at DIVERGENCE_DEV=0/unset are k real draws from
    the model's own default sampling, not k copies of a temperature-0
    determinism check. Calling this with DIVERGENCE_DEV=1 set would
    measure something else entirely (five requests for the same cached
    or near-identical greedy answer) and should not be read as k=5
    disagreement evidence -- checked at the top of this function, not
    left to the caller to remember.

    PERSISTENCE: every one of the k raw outputs is written to disk before
    this function returns anything, not just the aggregate. Featherless's
    own seed parameter is documented as unreliable across servers ("Not
    reliable, as we use multiple servers" -- quoted verbatim in
    README.md's Reproducibility section) -- a specific sample cannot be
    regenerated on demand from a seed the way D1's replay cache
    regenerates a single deterministic call. These k files ARE the
    reproducibility record for this specific run; without them, a later
    reader has no way to audit which citation/certainty combination each
    of the k draws actually produced, only the aggregate this function
    also returns.

    Returns (samples, manifest). samples is a list of k dicts, each
    {"sample_index", "regime", "regimes", "limits", "_meta"} -- the same
    shape resolve() already produces, numbered. manifest records the
    call parameters and the on-disk path of every sample, and is written
    to disk alongside them.
    """
    if k < 2:
        raise ValueError(f"k must be >= 2 to measure disagreement, got {k}")
    if os.environ.get("DIVERGENCE_DEV", "").strip() == "1":
        raise RuntimeError(
            "DIVERGENCE_DEV=1 forces temperature 0 (D52) -- k samples under "
            "that flag are k copies of a determinism check, not k draws of "
            "the model's own default sampling. Unset DIVERGENCE_DEV before "
            "calling resolve_k(), or this measures the wrong thing."
        )

    out_dir = out_dir or os.path.join(HERE, "runs", "ksamples")
    os.makedirs(out_dir, exist_ok=True)

    samples = []
    sample_paths = []
    for i in range(k):
        regimes, limits, meta = resolve(regime, facts, missing, tax_year, model=model)
        sample = {
            "sample_index": i,
            "regime": regime,
            "regimes": regimes,
            "limits": limits,
            "_meta": {
                "record_id": record_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                **meta,
            },
        }
        path = os.path.join(out_dir, f"{record_id}_{regime}_k{k}_sample{i}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2, ensure_ascii=False)
        samples.append(sample)
        sample_paths.append(os.path.relpath(path, HERE))
        print(f"    sample {i+1}/{k}: {len(regimes)} conclusion(s) -> {os.path.basename(path)}")

    manifest = {
        "record_id": record_id,
        "regime": regime,
        "k": k,
        "model": model,
        "tax_year": tax_year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_files": sample_paths,
        "seed_reliability_note": (
            "Featherless's seed parameter is documented unreliable across "
            "servers -- these k files are the only reproducibility record "
            "for this run, not a seed a reader could re-derive them from."
        ),
    }
    manifest_path = os.path.join(out_dir, f"{record_id}_{regime}_k{k}_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    manifest["_manifest_path"] = os.path.relpath(manifest_path, HERE)

    return samples, manifest


def main():
    ap = argparse.ArgumentParser(description="Node 3/4 -- income tax or GST resolver")
    ap.add_argument("--regime", required=True, choices=list(PROMPT_FILES))
    ap.add_argument("--facts", required=True, help="facts.json written by node1_extract.py")
    ap.add_argument("--missing", required=True, help="missing.json written by node2_gaps.py")
    ap.add_argument("--tax-year", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="large")
    ap.add_argument("--k", type=int, default=None,
                    help="if set, call resolve_k(k=...) instead of resolve() once -- "
                         "k independent samples, all persisted, for disagreement_gate.py")
    ap.add_argument("--record-id", default="record", help="used to name --k sample/manifest files")
    a = ap.parse_args()

    facts_doc = json.load(open(a.facts, encoding="utf-8"))
    facts = facts_doc.get("facts", facts_doc)
    missing_doc = json.load(open(a.missing, encoding="utf-8"))
    missing = missing_doc.get("missing", missing_doc)

    try:
        provider_line = f"provider={llm_call.provider_display()} model={llm_call.model_display(a.model)}"
    except LLMError as e:
        die(str(e))
    print(f"  [{NODE_NAME[a.regime]}] {provider_line}")

    if a.k:
        try:
            samples, manifest = resolve_k(a.regime, facts, missing, a.tax_year, k=a.k,
                                          model=a.model, record_id=a.record_id)
        except (LLMError, RuntimeError, ValueError) as e:
            die(str(e))
        print(f"\n  {a.k} sample(s) -> {manifest['_manifest_path']}\n")
        return

    try:
        regimes, limits, meta = resolve(a.regime, facts, missing, a.tax_year, model=a.model)
    except LLMError as e:
        die(str(e))

    out = {
        "regimes": regimes, "limits": limits,
        "_meta": {"node": NODE_NAME[a.regime], "generated_at": datetime.now(timezone.utc).isoformat(), **meta},
    }
    out_path = a.out or os.path.join(os.path.dirname(os.path.abspath(a.facts)), f"regimes_{a.regime}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"\n  {len(regimes)} conclusion(s), {len(limits)} limit(s) -> {out_path}\n")
    for r in regimes:
        print(f"    {r.get('regime')}: {r.get('certainty')} -- {r.get('outcome')}")
        print(f"      cites {r.get('citation', {}).get('provision')}")
    print()


if __name__ == "__main__":
    main()
