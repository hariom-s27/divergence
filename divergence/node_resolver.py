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


def main():
    ap = argparse.ArgumentParser(description="Node 3/4 -- income tax or GST resolver")
    ap.add_argument("--regime", required=True, choices=list(PROMPT_FILES))
    ap.add_argument("--facts", required=True, help="facts.json written by node1_extract.py")
    ap.add_argument("--missing", required=True, help="missing.json written by node2_gaps.py")
    ap.add_argument("--tax-year", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="large")
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
