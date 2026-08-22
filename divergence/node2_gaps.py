#!/usr/bin/env python3
"""
NODE 2 — GAP DETECTOR ⭐  ·  DIVERGENCE
Model: "small" — see llm_call.py PROVIDERS for which model that resolves to
on the active provider. Corpus: evidence-requirement extracts only — a
fixed, narrow list, NOT the full resolver corpus nodes 3/4 see.

Establishes what is ABSENT from facts{} before anything reasons about what
is present (F2: silent completeness, predicted ~90% of runs, Class 3 —
invisible to the user). Runs on node 1's output, never on raw documents.

    python node2_gaps.py --facts cases/D1/facts.json
    python node2_gaps.py --facts cases/D1/facts.json --out cases/D1/missing.json

Reads   the SYSTEM block of step22drop/prompts/02-gap-detector.md
        the fixed evidence-requirement files it names, from corpus/verbatim/
Writes  missing.json: {"missing": [...]}  (schema.json properties.missing)
"""

import os, sys, json, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import llm_call  # noqa: E402
from llm_call import LLMError  # noqa: E402

PROMPT_FILE = os.path.join(HERE, "step22drop", "prompts", "02-gap-detector.md")
NODE_NAME = "node2_gaps"

# Named explicitly in 02-gap-detector.md's scope table. Kept in one place so
# the prompt's documented scope and the code's actual scope cannot drift.
EVIDENCE_CORPUS_FILES = [
    "GST-IGST-2-6.md",
    "FEMA-2n.md",
    "FEMA-3-7-8.md",
    "IT-393-1-T8vi.md",
    "ITR2026-RULE-56.md",
]


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def load_system_prompt():
    if not os.path.exists(PROMPT_FILE):
        die(f"{PROMPT_FILE} not found")
    text = open(PROMPT_FILE, encoding="utf-8").read()
    marker = "## SYSTEM"
    if marker not in text:
        die(f"{PROMPT_FILE} has no '## SYSTEM' section")
    fenced = text.split(marker, 1)[1].split("```", 2)
    if len(fenced) < 3:
        die(f"{PROMPT_FILE}'s SYSTEM section is not fenced with ```")
    return fenced[1].strip()


def load_evidence_corpus():
    corpus_dir = os.path.join(HERE, "corpus", "verbatim")
    parts = []
    for fn in EVIDENCE_CORPUS_FILES:
        p = os.path.join(corpus_dir, fn)
        if not os.path.exists(p):
            die(f"evidence-requirement corpus file missing: {p}\n"
                f"  02-gap-detector.md's scope table names it — either restore the file "
                f"or update both the prompt and EVIDENCE_CORPUS_FILES together.")
        parts.append(f"--- {fn} ---\n" + open(p, encoding="utf-8").read())
    return "\n\n".join(parts)


def detect_gaps(facts: dict, model="small"):
    """The reusable entry point — run_pipeline.py calls this directly.
    Returns (missing, meta) — meta is this node's row from
    llm_call.provenance() after the call."""
    system = load_system_prompt()
    corpus_text = load_evidence_corpus()
    user = (
        "FACTS (from node 1):\n" + json.dumps(facts, indent=2) +
        "\n\nEVIDENCE-REQUIREMENT TEXT:\n" + corpus_text
    )
    parsed = llm_call.call_json(system, user, model, node_name=NODE_NAME)
    if "missing" not in parsed or not isinstance(parsed["missing"], list):
        raise LLMError(f"{NODE_NAME}: model output has no top-level 'missing' array\n{parsed}")
    meta = llm_call.provenance()["by_node"].get(NODE_NAME, {})
    return parsed["missing"], meta


def main():
    ap = argparse.ArgumentParser(description="Node 2 — GAP DETECTOR")
    ap.add_argument("--facts", required=True, help="facts.json written by node1_extract.py")
    ap.add_argument("--out", default=None, help="default: alongside --facts, as missing.json")
    ap.add_argument("--model", default="small")
    a = ap.parse_args()

    if not os.path.exists(a.facts):
        die(f"--facts file not found: {a.facts}")
    facts_doc = json.load(open(a.facts, encoding="utf-8"))
    facts = facts_doc.get("facts", facts_doc)  # accept either a facts.json or a bare facts{}

    print(f"  [{NODE_NAME}] provider={llm_call.provider_display()} model={llm_call.model_display(a.model)}")
    try:
        missing, meta = detect_gaps(facts, model=a.model)
    except LLMError as e:
        die(str(e))

    out = {
        "missing": missing,
        "_meta": {
            "node": "2_gaps",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "facts_source": a.facts,
            **meta,
        },
    }

    out_path = a.out or os.path.join(os.path.dirname(os.path.abspath(a.facts)), "missing.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    try:
        shown_path = os.path.relpath(out_path, HERE)
    except ValueError:
        shown_path = out_path  # different drive than HERE on Windows -- relpath can't express it
    print(f"\n  {len(missing)} gap(s) found -> {shown_path}\n")
    for m in missing:
        print(f"    {m.get('item')}")
        print(f"      blocks: {m.get('blocks')}   obtainable: {m.get('obtainable')}")
        print(f"      {m.get('why_absent')}")
    if not missing:
        print("    (none — every evidence requirement in scope is satisfied by the facts given)")
    print()


if __name__ == "__main__":
    main()
