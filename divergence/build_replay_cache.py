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

D72: also passes through D1's own real historical provider/model/token/
retry counts (rec["_meta"]["llm"]["by_node"], the attack doc's own
_meta) as the entry's metadata -- real numbers this project already
measured, never fabricated placeholders. Two real historical fields
this record predates and genuinely does not have: elapsed_s (D64's
wall-clock instrumentation came after this record was frozen) and seed
(D72, this commit) -- both stored as their honest empty value (0.0 /
None), not guessed at. model_key/temperature/max_tokens (the new key
components) are computed fresh against THIS run's own environment via
llm_call.temperature() and each node's own known default max_tokens,
not reconstructed from the historical record's display strings --
they have to match whatever a live lookup would compute right now, not
what the environment looked like the night D1 was frozen.

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
import llm_call                         # noqa: E402
import node1_extract                    # noqa: E402
import node2_gaps                       # noqa: E402
import node_resolver                    # noqa: E402
import node5_adversarial                # noqa: E402

D1_INPUT = os.path.join(HERE, "cases", "D1", "input.md")
D1_RECORD = os.path.join(HERE, "runs", "21aug", "D1_final_seed2.json")
D1_ATTACK = os.path.join(HERE, "runs", "21aug", "D1_final_seed2_attack.json")

DEFAULT_MAX_TOKENS = 4096  # every node's own call_json() call site -- none override it


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def _real_meta(by_node, node_name):
    """D72: the real historical provider/model/tokens/retries for one node,
    from D1's own already-measured _meta -- never fabricated. elapsed_s and
    seed are genuinely absent from this pre-D64/pre-D72 record; returned as
    their honest empty value, not guessed at."""
    m = by_node.get(node_name, {})
    return {
        "provider": "featherless", "model": m.get("model"),
        "in_tokens": m.get("in_tokens", 0), "out_tokens": m.get("out_tokens", 0),
        "retries": m.get("retries", 0), "elapsed_s": 0.0, "seed": None,
    }


def seed_node1(facts, by_node):
    nonce = "replay-cache-key-nonce"
    system = node1_extract.load_system_prompt() + node1_extract._spotlight_instruction(nonce)
    content = node1_extract.build_content([D1_INPUT], [], "small", nonce=nonce)
    response = {"facts": facts, "extraction_notes": []}
    key = replay_cache.save("node1_extract", system, content, response, source="seeded",
                            model_key="small", temperature=llm_call.temperature(),
                            max_tokens=DEFAULT_MAX_TOKENS, **_real_meta(by_node, "node1_extract"))
    print(f"  node1_extract     -> {key[:16]}...")


def seed_node2(facts, missing, by_node):
    system = node2_gaps.load_system_prompt()
    corpus_text = node2_gaps.load_evidence_corpus()
    user = ("FACTS (from node 1):\n" + json.dumps(facts, indent=2) +
            "\n\nEVIDENCE-REQUIREMENT TEXT:\n" + corpus_text)
    response = {"missing": missing}
    key = replay_cache.save("node2_gaps", system, user, response, source="seeded",
                            model_key="small", temperature=llm_call.temperature(),
                            max_tokens=DEFAULT_MAX_TOKENS, **_real_meta(by_node, "node2_gaps"))
    print(f"  node2_gaps        -> {key[:16]}...")


def seed_resolvers(facts, missing, tax_year, regimes, by_node):
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
        node_name = node_resolver.NODE_NAME[kind]
        key = replay_cache.save(node_name, system, user, response, source="seeded",
                                model_key="large", temperature=llm_call.temperature(),
                                max_tokens=DEFAULT_MAX_TOKENS, **_real_meta(by_node, node_name))
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
    # D72: this record's own real historical meta lives at the top level
    # (not nested in by_node -- node5_adversarial.py writes its own output
    # file directly, one node per file, unlike run_pipeline.py's combined
    # record), so read it directly rather than through _real_meta().
    m = attack_doc.get("_meta", {})
    key = replay_cache.save(node5_adversarial.NODE_NAME, system, user, response, source="seeded",
                            model_key="adversarial", temperature=llm_call.temperature(),
                            max_tokens=DEFAULT_MAX_TOKENS, provider="featherless",
                            model=m.get("model"), in_tokens=m.get("in_tokens", 0),
                            out_tokens=m.get("out_tokens", 0), retries=m.get("retries", 0),
                            elapsed_s=0.0, seed=None)
    print(f"  node5_adversarial -> {key[:16]}...")


def main():
    if not os.path.exists(D1_RECORD):
        die(f"{D1_RECORD} not found")
    if not os.path.exists(D1_INPUT):
        die(f"{D1_INPUT} not found")
    rec = json.load(open(D1_RECORD, encoding="utf-8"))
    by_node = rec.get("_meta", {}).get("llm", {}).get("by_node", {})

    print("\n  Seeding replay_cache/ from D1's real, frozen record\n")
    seed_node1(rec["facts"], by_node)
    seed_node2(rec["facts"], rec["missing"], by_node)
    seed_resolvers(rec["facts"], rec["missing"], rec["tax_year"], rec["regimes"], by_node)

    if os.path.exists(D1_ATTACK):
        attack_doc = json.load(open(D1_ATTACK, encoding="utf-8"))
        seed_node5(rec["regimes"], rec["missing"], rec["valuation"], rec["tax_year"], attack_doc)
    else:
        print(f"  ({os.path.basename(D1_ATTACK)} not found -- node5 not seeded)")

    s = replay_cache.stats()
    print(f"\n  {s['entries']} cache entr(y/ies) total.\n")


if __name__ == "__main__":
    main()
