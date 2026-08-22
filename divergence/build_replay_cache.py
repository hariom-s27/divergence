#!/usr/bin/env python3
"""
BUILD REPLAY CACHE — DIVERGENCE
Seeds replay_cache/ for D1 from real, already-verified, frozen data --
runs/21aug/D1_final_seed2.json and its matching D1_final_seed2_attack.json
-- so DIVERGENCE_REPLAY=1 can reproduce the whole D1 run with no API key
at all, on a machine that has never talked to Featherless.

This does NOT invent a response. For each node, it reconstructs the exact
request today's corpus/prompts produce (same functions run_pipeline.py
itself calls) and pairs it with the real output slice from D1's own
frozen, schema-validated record -- disclosed as seeded, not indistinguishable
from a live call (replay_cache.save(..., source="seeded")).

    python build_replay_cache.py

Then, with no FEATHERLESS_API_KEY set at all:

    $env:DIVERGENCE_REPLAY = "1"
    python run_pipeline.py --record-id D1-replay --tax-year "FY 2026-27" `
        --text cases/D1/input.md --node5 --out runs/replay_test.json
"""

import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import replay_cache                     # noqa: E402
import node1_extract                    # noqa: E402
import node2_gaps                       # noqa: E402
import node_resolver                    # noqa: E402
import node5_adversarial                # noqa: E402

D1_INPUT = os.path.join(HERE, "cases", "D1", "input.md")
D1_RECORD = os.path.join(HERE, "runs", "21aug", "D1_final_seed2.json")
D1_ATTACK = os.path.join(HERE, "runs", "21aug", "D1_final_seed2_attack.json")


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def seed_node1(facts):
    nonce = "replay-cache-key-nonce"
    system = node1_extract.load_system_prompt() + node1_extract._spotlight_instruction(nonce)
    content = node1_extract.build_content([D1_INPUT], [], "small", nonce=nonce)
    response = {"facts": facts, "extraction_notes": []}
    key = replay_cache.save("node1_extract", system, content, response, source="seeded")
    print(f"  node1_extract     -> {key[:16]}...")


def seed_node2(facts, missing):
    system = node2_gaps.load_system_prompt()
    corpus_text = node2_gaps.load_evidence_corpus()
    user = ("FACTS (from node 1):\n" + json.dumps(facts, indent=2) +
            "\n\nEVIDENCE-REQUIREMENT TEXT:\n" + corpus_text)
    response = {"missing": missing}
    key = replay_cache.save("node2_gaps", system, user, response, source="seeded")
    print(f"  node2_gaps        -> {key[:16]}...")


def seed_resolvers(facts, missing, tax_year, regimes):
    by_regime_kind = {
        "income_tax": [r for r in regimes if r["regime"] in
                       ("income_tax_on_receipt", "income_tax_on_transfer", "valuation_method")],
        "gst": [r for r in regimes if r["regime"] == "gst_export"],
    }
    for kind, kept_regimes in by_regime_kind.items():
        if not kept_regimes:
            continue
        system = node_resolver.load_system_prompt(kind)
        corpus_text = node_resolver.load_scoped_corpus(kind)
        user = (
            f"TAX YEAR: {tax_year}\n\n"
            f"FACTS (from node 1):\n{json.dumps(facts, indent=2)}\n\n"
            f"MISSING (from node 2 -- any conclusion depending on one of these must set "
            f"depends_on_missing accordingly):\n{json.dumps(missing, indent=2)}\n\n"
            f"STATUTORY TEXT (verbatim, scoped to this regime only):\n{corpus_text}"
        )
        # strip fields citation_matcher/gap_enforcer added post-hoc -- the
        # resolver's OWN raw output never had them
        raw_regimes = []
        for r in kept_regimes:
            r2 = dict(r)
            cite = dict(r2.get("citation") or {})
            cite.pop("verified", None)
            r2["citation"] = cite
            raw_regimes.append(r2)
        response = {"regimes": raw_regimes, "limits": []}
        key = replay_cache.save(node_resolver.NODE_NAME[kind], system, user, response, source="seeded")
        print(f"  node_resolver[{kind}]  -> {key[:16]}...")


def seed_node5(regimes, missing, valuation, tax_year, attack_doc):
    system = node5_adversarial.load_system_prompt()
    corpus_text, corpus_files = node5_adversarial.load_full_corpus()
    user = (
        f"TAX YEAR: {tax_year}\n\n"
        f"CONCLUSIONS TO ATTACK (already through the citation matcher -- "
        f"these are nodes 3/4's kept output, not raw model text):\n"
        f"{json.dumps(regimes, indent=2)}\n\n"
        f"GAP LIST (from node 2):\n{json.dumps(missing, indent=2)}\n\n"
        f"VALUATION LATTICE (from node 3, deterministic arithmetic -- do "
        f"not attack the rupee figures themselves, only a label on one or "
        f"a claim that one is prescribed by law):\n"
        f"{json.dumps(valuation, indent=2)}\n\n"
        f"STATUTORY TEXT (verbatim, full corpus, {len(corpus_files)} file(s)):\n{corpus_text}"
    )
    response = {
        "attacked": attack_doc["attacked"],
        "checked_and_survived": attack_doc["checked_and_survived"],
        "limits": attack_doc.get("limits", []),
    }
    key = replay_cache.save(node5_adversarial.NODE_NAME, system, user, response, source="seeded")
    print(f"  node5_adversarial -> {key[:16]}...")


def main():
    if not os.path.exists(D1_RECORD):
        die(f"{D1_RECORD} not found")
    if not os.path.exists(D1_INPUT):
        die(f"{D1_INPUT} not found")
    rec = json.load(open(D1_RECORD, encoding="utf-8"))

    print("\n  Seeding replay_cache/ from D1's real, frozen record\n")
    seed_node1(rec["facts"])
    seed_node2(rec["facts"], rec["missing"])
    seed_resolvers(rec["facts"], rec["missing"], rec["tax_year"], rec["regimes"])

    if os.path.exists(D1_ATTACK):
        attack_doc = json.load(open(D1_ATTACK, encoding="utf-8"))
        seed_node5(rec["regimes"], rec["missing"], rec["valuation"], rec["tax_year"], attack_doc)
    else:
        print(f"  ({os.path.basename(D1_ATTACK)} not found -- node5 not seeded)")

    s = replay_cache.stats()
    print(f"\n  {s['entries']} cache entr(y/ies) total.\n")


if __name__ == "__main__":
    main()
