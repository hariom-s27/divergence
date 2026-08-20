#!/usr/bin/env python3
"""
NODE 5 — ADVERSARIAL CHECKER  ·  DIVERGENCE
Model: "adversarial" (mistralai/Mistral-Large-Instruct-2411, D41) -- a
different model family from the Qwen resolvers, on purpose. Self-critique
by the same model over its own reasoning has documented self-consistency
bias; grounding the check in a different model plus mechanical inputs
(the gap list, the citation-matcher verdicts already baked into regimes[])
is the point, not incidental.

Built Block D, 21 Aug. 05-adversarial.md's own header said "THIS NODE HAS
NEVER RUN" -- everything credited to adversarial review before tonight was
found by a human reading adversarially, not by this. This is what turns
that claim into a demo, or into a documented negative result if it earns
neither -- 05-adversarial.md is explicit that a clean sweep of "caught
nothing" gets reported exactly as prominently as a win, decided before the
run so it can't be dropped quietly afterward.

    python node5_adversarial.py --regimes regimes.json --missing missing.json \\
        --valuation valuation.json --tax-year "FY 2026-27"

Reads   the SYSTEM block of step22drop/prompts/05-adversarial.md
        the FULL verbatim corpus, unscoped -- 05-adversarial.md's own
        header: "Corpus scope: the full verbatim corpus + the gap list +
        the valuation lattice". Node 5's whole job is judging citation
        currency and scope reach across regimes nodes 3/4 kept separate,
        so it gets everything, not a per-regime slice.
Writes  attack.json: {"attacked": [...], "checked_and_survived": [...], "limits": [...]}
"""

import os, sys, json, glob, re, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import llm_call  # noqa: E402
from llm_call import LLMError  # noqa: E402
import citation_matcher  # noqa: E402

PROMPT_FILE = os.path.join(HERE, "step22drop", "prompts", "05-adversarial.md")
CORPUS_DIR = os.path.join(HERE, "corpus", "verbatim")
TIER_A_DIR = os.path.join(HERE, "corpus", "tier-a")

NODE_NAME = "node5_adversarial"

VALID_CERTAINTY = {"settled", "inference", "open_texture", "lacuna", "contested", "insufficient_evidence"}


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


def load_full_corpus():
    """Same heading-by-real-citation fix as node_resolver.py's
    load_scoped_corpus() (found live, 20 Aug: heading a block with the bare
    filename taught the model to cite the FILENAME as if it were the legal
    citation). Node 5's whole job is judging citation currency, so it needs
    the real citation string on every block even more than the resolvers
    do -- feeding it "IT-2-47A.md" as the thing to check for staleness
    would be testing the file naming convention, not the law."""
    files = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.md")))
    if not files:
        die("corpus/verbatim/ is empty. Run corpus/split_corpus.py first.")
    parts = []
    for p in files:
        fn = os.path.basename(p)
        tier_a_p = os.path.join(TIER_A_DIR, fn)
        meta = citation_matcher.parse_front_matter(tier_a_p) if os.path.exists(tier_a_p) else {}
        heading = meta.get("current_citation") or fn
        parts.append(f"--- {heading} ---\n" + open(p, encoding="utf-8").read().strip())
    return "\n\n".join(parts), [os.path.basename(f) for f in files]


def _validate_attack_shape(parsed, raw):
    """Same discipline as node1_extract.py / node_resolver.py: catch a
    contract violation here, not as an opaque schema error three steps
    downstream."""
    if "attacked" not in parsed or not isinstance(parsed["attacked"], list):
        raise LLMError(f"{NODE_NAME}: model output has no top-level 'attacked' array\n{raw}")
    if "checked_and_survived" not in parsed or not isinstance(parsed["checked_and_survived"], list):
        raise LLMError(f"{NODE_NAME}: model output has no top-level 'checked_and_survived' array\n{raw}")
    bad = []
    for i, a in enumerate(parsed["attacked"]):
        if not isinstance(a, dict):
            bad.append((i, "not an object")); continue
        if not isinstance(a.get("target"), str) or not a["target"]:
            bad.append((i, "target missing or not a string")); continue
        if not isinstance(a.get("attack"), str) or not a["attack"]:
            bad.append((i, "attack missing or not a string")); continue
        if not isinstance(a.get("survived"), bool):
            bad.append((i, f"survived={a.get('survived')!r} is not a boolean")); continue
        dg = a.get("downgraded_to")
        if dg is not None and dg not in VALID_CERTAINTY:
            bad.append((i, f"downgraded_to={dg!r} not in {sorted(VALID_CERTAINTY)} or null")); continue
    if bad:
        raise LLMError(f"{NODE_NAME}: attacked[] contains {len(bad)} malformed entr(y/ies): {bad}\nRaw:\n{raw}")


# Most to least certain. D50's addendum: node 5 downgraded one attack TO
# "settled" -- an upgrade wearing a downgrade's name, and nothing stopped
# it, because the schema only checks downgraded_to is a valid enum value,
# not that it is actually a downgrade.
_CERTAINTY_ORDER = ["settled", "inference", "open_texture", "contested", "lacuna", "insufficient_evidence"]


_STOPWORDS = {"the", "a", "an", "and", "or", "of", "to", "is", "in", "on", "for",
              "at", "as", "by", "this", "that", "under", "with", "no", "not"}


def _words(text):
    return {w for w in re.findall(r"[a-z0-9.()]+", text.lower()) if w not in _STOPWORDS}


def _match_target_certainty(target, regimes):
    """Best-effort, conservative match of an attack's free-text `target`
    back to the regime it quotes, to read that regime's certainty BEFORE
    the attack. node 5 paraphrases rather than quoting verbatim (found
    live testing this guard: target was "must offer a bona fide
    explanation... to avoid penalties", the regime's own outcome said
    "must disclose... to substantiate the explanation offered" -- same
    clause, no shared substring), so this matches on word overlap, not
    substring containment. Only trusted when exactly one regime is a
    clear best match (highest overlap, and by a real margin over the
    second-best) -- anything ambiguous returns None and the guard below
    simply skips that attack, the same "don't guess" choice
    run_pipeline.py already made for applying downgrades to regimes[]
    itself."""
    if not target:
        return None
    t_words = _words(target)
    if not t_words:
        return None
    scores = []
    for r in regimes:
        o_words = _words(r.get("outcome") or "")
        if not o_words:
            continue
        overlap = len(t_words & o_words) / len(t_words)
        scores.append((overlap, r.get("certainty")))
    scores.sort(key=lambda x: -x[0])
    if not scores or scores[0][0] < 0.5:
        return None
    if len(scores) > 1 and scores[1][0] >= scores[0][0] - 0.15:
        return None  # too close to call -- ambiguous, don't guess
    return scores[0][1]


def _reject_upward_revisions(attacked, regimes):
    """Deterministic, in code -- the same discipline gap_enforcer.py
    applies to certainty. A landed attack (survived: false) whose
    downgraded_to is NOT strictly less certain than the target's
    certainty already was is not a downgrade -- either a real upgrade, or
    a same-level relabel that is equally nonsensical for something the
    model itself is claiming to have successfully attacked. Drop the
    field and say so, rather than let a malformed "downgrade" pass
    through the schema check untouched. Found live testing this guard:
    D50's addendum example is exactly the tie case (target already
    `settled`, proposed downgraded_to also `settled`) -- a strict
    more-certain-than check misses it; the fix is <=, not <."""
    rejected = []
    for a in attacked:
        dg = a.get("downgraded_to")
        if not dg or a.get("survived") is not False:
            continue
        before = _match_target_certainty(a.get("target"), regimes)
        if before is None or before not in _CERTAINTY_ORDER or dg not in _CERTAINTY_ORDER:
            continue
        if _CERTAINTY_ORDER.index(dg) <= _CERTAINTY_ORDER.index(before):
            rejected.append({"target": a.get("target"), "was": before, "proposed": dg})
            a["downgraded_to"] = None
    return rejected


def check(regimes, missing, valuation, tax_year, model="adversarial"):
    """The reusable entry point -- run_pipeline.py calls this when --node5
    is passed. Returns (attacked, checked_and_survived, limits, meta)."""
    system = load_system_prompt()
    corpus_text, corpus_files = load_full_corpus()
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
    parsed = llm_call.call_json(system, user, model, node_name=NODE_NAME)
    _validate_attack_shape(parsed, parsed)
    rejected = _reject_upward_revisions(parsed["attacked"], regimes)
    limits = list(parsed.get("limits", []))
    for rj in rejected:
        limits.append(
            f"node 5 proposed an upward revision on an attack (was {rj['was']!r}, "
            f"proposed downgraded_to={rj['proposed']!r}); rejected in code, "
            f"attack text kept, downgraded_to dropped. target: {rj['target']!r}"
        )
    meta = llm_call.provenance()["by_node"].get(NODE_NAME, {})
    return parsed["attacked"], parsed["checked_and_survived"], limits, meta


def main():
    ap = argparse.ArgumentParser(description="Node 5 -- adversarial checker")
    ap.add_argument("--regimes", required=True, help="regimes[] from a pipeline record "
                     "(post citation-matcher, e.g. runs/D1_pipeline.json)")
    ap.add_argument("--missing", required=True)
    ap.add_argument("--valuation", required=True)
    ap.add_argument("--tax-year", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="adversarial")
    a = ap.parse_args()

    regimes_doc = json.load(open(a.regimes, encoding="utf-8"))
    regimes = regimes_doc.get("regimes", regimes_doc) if isinstance(regimes_doc, dict) else regimes_doc
    missing_doc = json.load(open(a.missing, encoding="utf-8"))
    missing = missing_doc.get("missing", missing_doc) if isinstance(missing_doc, dict) else missing_doc
    valuation_doc = json.load(open(a.valuation, encoding="utf-8"))
    valuation = valuation_doc.get("valuation", valuation_doc) if isinstance(valuation_doc, dict) else valuation_doc

    print(f"  [{NODE_NAME}] provider={llm_call.provider_name()} model={llm_call.model_id(a.model)}")
    try:
        attacked, survived, limits, meta = check(regimes, missing, valuation, a.tax_year, model=a.model)
    except LLMError as e:
        die(str(e))

    out = {
        "attacked": attacked, "checked_and_survived": survived, "limits": limits,
        "_meta": {"node": NODE_NAME, "generated_at": datetime.now(timezone.utc).isoformat(), **meta},
    }
    out_path = a.out or os.path.join(os.path.dirname(os.path.abspath(a.regimes)), "attack.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"\n  {len(attacked)} attack(s), {len(survived)} survived unattacked -> {out_path}\n")
    for at in attacked:
        landed = "LANDED" if not at.get("survived") else "survived"
        print(f"    [{landed}]  {at.get('target')}")
        print(f"      attack: {at.get('attack')}")
        if at.get("downgraded_to"):
            print(f"      downgraded_to: {at.get('downgraded_to')}")
    print()


if __name__ == "__main__":
    main()
