#!/usr/bin/env python3
"""
MUTATE — DIVERGENCE
A deterministic, seeded defect-injection harness for node5_adversarial.py
specifically — not the deterministic gates mutation_corpus.py already
covers (citation_matcher, scope_enforcer, gap_enforcer). This project's
own thesis is that a real, current, correctly-quoted citation can still
be wrong in a way nothing but an adversarial LLM pass catches (Silent
Scope Omission, DOCUMENTATION.md §5) — so the thing worth stress-testing
here is node 5 itself: given a corrupted conclusion it has never seen
before, planted on purpose, does it actually attack the right thing?

Seven operators, applied to each of the six real cases' own saved,
already-verified regimes[]/valuation (runs/21aug/*.json — same
CASE_FILES mapping mutation_corpus.py already uses) = 42 mutants,
deterministic given --seed (default 1337): same seed, same 42 mutants,
every run, on every machine — seeded via a plain string
(random.Random(f"{seed}-{case}-{op}")), never a tuple, because Python's
hash() of a str is randomised per-process by default (PYTHONHASHSEED) —
a tuple seed would have made this file silently NOT reproducible across
two different runs, exactly the kind of bug this project's own discipline
exists to catch before shipping, not after.

  CITE_SWAP        a citation's own section/rule number nudged to its
                    numeric neighbour ("Rule 206" -> "Rule 207") --
                    plausible-looking, never a real corpus lookup
  DATE_SHIFT        one valuation method's date_used moved by one day,
                    or reset to the real settlement date -- rate/
                    inr_value left exactly as they were
  RATE_SUB          one method's source swapped for a different real
                    source's name/url, its own label left saying what
                    it used to say
  LABEL_MISMATCH    one method's label swapped for a different label,
                    the figure/source left exactly as they were
  ARITH_CORRUPT     one method's inr_value nudged 0.5-3%, nothing else
                    touched -- no textual signal at all
  SILENT_OMIT       one uncertainty_budget entry (or, where fewer than
                    two exist, one valuation method) deleted outright
  OVERCLAIM         one non-settled regime relabelled "settled" --
                    citation and reasoning left exactly as they were

Each mutant is fed to node5_adversarial.check() completely unchanged
from its real input contract (regimes, missing, valuation, tax_year) --
read that file first; this one never reshapes what it sends. "Caught" is
deliberately coarse and disclosed as such: any landed attack
(survived=False) anywhere in that mutant's own attacked[], not a claim
that node 5 named the specific corrupted field. A free-text matcher
precise enough to credit only an exact hit, across seven mechanically
unrelated kinds of corruption (a citation string, a date, a rupee
figure, a vanished list entry), would manufacture a precision this
project has no evidence for -- the same overclaim this project exists
to refuse elsewhere.

WHAT THIS PROVES, ONCE RUN WITH A LIVE KEY:
  Out of 42 planted, unambiguous defects, how many produce at least one
  landed node-5 attack -- overall (Clopper-Pearson 95% CI, binom_ci.py)
  and per operator. A real, measured mutation score, not an assumed one.

WHAT THIS DOES NOT PROVE:
  That node 5 is reliable on defects unlike these seven shapes. That a
  "caught" mutant was caught FOR the reason this file thinks it planted
  (see the coarse "caught" definition above). Nothing about the
  deterministic gates -- mutation_corpus.py already measures what those
  catch; this file is about the one check that still needs a model at
  all to judge scope reach on an unseen conclusion.

Needs a live FEATHERLESS_API_KEY for the real 42-mutant sweep — 42 real
node-5 calls, same constraint as every other script in this project that
touches node 5 for real (D62 through D68). --self-test needs no key at
all: it checks the harness's OWN correctness two ways that never call
node 5 — see self_test()'s own docstring for exactly what each proves.

Standard library only, plus this project's own existing modules
(node5_adversarial.py, llm_call.py, scope_enforcer.py, citation_matcher.py,
binom_ci.py) — no new third-party dependency.

    python mutate.py                  # the real 42-mutant sweep, needs a key
    python mutate.py --self-test       # offline, no key needed
    python mutate.py --seed 7          # a different, still-deterministic 42
"""

import os
import sys
import json
import copy
import re
import random
import argparse
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import llm_call                    # noqa: E402
from llm_call import LLMError      # noqa: E402
import node5_adversarial           # noqa: E402
import scope_enforcer              # noqa: E402
import citation_matcher            # noqa: E402
import binom_ci                    # noqa: E402

RUNS = os.path.join(HERE, "runs", "21aug")
OUT_DIR = os.path.join(HERE, "runs", "mutants")

CASE_FILES = {
    "C1": "C1_pipeline.json", "C2": "C2_pipeline.json", "C3": "C3_pipeline.json",
    "C4": "C4_pipeline.json", "C5": "C5_pipeline.json", "D1": "D1_final_seed2.json",
}

DEFAULT_SEED = 1337


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def load_case(case_id):
    p = os.path.join(RUNS, CASE_FILES[case_id])
    if not os.path.exists(p):
        die(f"{p} not found")
    rec = json.load(open(p, encoding="utf-8"))
    return rec["facts"], rec["tax_year"], rec["missing"], rec["regimes"], rec["valuation"]


# ─────────────────────────────────────────────────────────────
# Seven operators. Each: (regimes, valuation, facts, rng) ->
# (mutated_regimes, mutated_valuation, note). Deep-copies its inputs --
# never mutates the caller's own case data. Confirmed applicable,
# unconditionally, to all six of this project's real cases (every case
# has >=2 regimes and >=1 valuation method, at least one non-settled
# regime -- checked directly against runs/21aug/*.json, not assumed).
# Not a claim that any of these seven always applies to an arbitrary
# future case -- see LIMITATIONS at the bottom.
# ─────────────────────────────────────────────────────────────

_CITE_NUM_PATTERNS = [
    re.compile(r'\bs\.\s*(\d+)'),
    re.compile(r'\bSection\s+(\d+)'),
    re.compile(r'\bRule\s+(\d+)'),
    re.compile(r'(\d+)'),  # fallback: first digit run anywhere
]


def _neighbouring_citation(text):
    """A section/rule number nudged by +1 -- a numeric neighbour in the
    citation STRING, never a real corpus lookup (that would make this a
    scope_enforcer.py rewrite, not a node-5 stress test). Tries s.N,
    "Section N", "Rule N" in that order before falling back to the
    first digit run anywhere, so a citation's YEAR is never the thing
    nudged when an actual section/rule number is present in a
    recognised form earlier in the string."""
    for pat in _CITE_NUM_PATTERNS:
        m = pat.search(text)
        if m:
            n = int(m.group(1))
            return text[:m.start(1)] + str(n + 1) + text[m.end(1):]
    return text


def op_cite_swap(regimes, valuation, facts, rng):
    regimes = copy.deepcopy(regimes)
    r = rng.choice(regimes)
    cite = r.setdefault("citation", {})
    before = cite.get("provision", "")
    cite["provision"] = _neighbouring_citation(before)
    return regimes, valuation, (
        f"{r.get('regime')}: citation nudged {before!r} -> {cite['provision']!r}"
    )


def op_date_shift(regimes, valuation, facts, rng):
    valuation = copy.deepcopy(valuation)
    methods = valuation.get("methods") or []
    m = rng.choice(methods)
    before = m.get("date_used", "")
    to_transaction = rng.random() < 0.5
    if to_transaction:
        txn = (facts.get("settlement_datetime_ist") or {}).get("value", "")[:10] \
            or (facts.get("invoice_date") or {}).get("value", "")
        after = txn or before
        mode = "reset to the real transaction date"
    else:
        try:
            d = datetime.strptime(before, "%Y-%m-%d") + timedelta(days=1)
            after = d.strftime("%Y-%m-%d")
        except ValueError:
            after = before
        mode = "shifted +1 day"
    m["date_used"] = after
    return regimes, valuation, (
        f"{m.get('label')}: date_used {mode}, {before!r} -> {after!r} "
        f"(rate/inr_value left untouched)"
    )


_ALT_SOURCES = [
    {"name": "RBI Reference Rate", "url": "rbi-reference-rate-archive", "tier": "primary_archived"},
    {"name": "Binance USDC/USDT close", "url": "binance-daily-candle-archive", "tier": "market_data"},
    {"name": "SBI Forex Card Rates sheet, USD/INR TT BUY", "url": "sbi-ttbr-archive", "tier": "primary_archived"},
]


def op_rate_sub(regimes, valuation, facts, rng):
    valuation = copy.deepcopy(valuation)
    methods = valuation.get("methods") or []
    m = rng.choice(methods)
    label = m.get("label", "")
    before_source = dict(m.get("source") or {})
    alt = dict(rng.choice(_ALT_SOURCES))
    alt["retrieved"] = before_source.get("retrieved", "")
    alt["note"] = "SOURCE SWAPPED BY mutate.py -- label below was NOT regenerated to match"
    m["source"] = alt
    return regimes, valuation, (
        f"{label}: source silently swapped {before_source.get('name')!r} -> "
        f"{alt['name']!r}, label text left saying the old source"
    )


_ALT_LABELS = [
    "SBI TTBR (last published BEFORE the receipt)",
    "SBI TTBR (next published AFTER the receipt)",
    "domestic market, low x retrieved peg",
    "domestic market, high x retrieved peg",
]


def op_label_mismatch(regimes, valuation, facts, rng):
    valuation = copy.deepcopy(valuation)
    methods = valuation.get("methods") or []
    m = rng.choice(methods)
    before = m.get("label", "")
    candidates = [x for x in _ALT_LABELS if x != before] or _ALT_LABELS
    after = rng.choice(candidates)
    m["label"] = after
    return regimes, valuation, (
        f"rate/source/inr_value ({m.get('inr_value')}) left untouched, only the "
        f"label swapped {before!r} -> {after!r}"
    )


def op_arith_corrupt(regimes, valuation, facts, rng):
    valuation = copy.deepcopy(valuation)
    methods = valuation.get("methods") or []
    m = rng.choice(methods)
    before = m.get("inr_value")
    pct = rng.uniform(0.5, 3.0) * rng.choice([1, -1])
    after = round(before * (1 + pct / 100.0), 2) if isinstance(before, (int, float)) else before
    m["inr_value"] = after
    return regimes, valuation, (
        f"{m.get('label')}: inr_value perturbed {pct:+.2f}%, {before} -> {after} "
        f"(label/source/rate left exactly as they were -- no textual signal at all)"
    )


def op_silent_omit(regimes, valuation, facts, rng):
    valuation = copy.deepcopy(valuation)
    ub = valuation.get("uncertainty_budget") or []
    methods = valuation.get("methods") or []
    if len(ub) >= 2:
        removed = ub.pop(rng.randrange(len(ub)))
        note = (
            f"uncertainty_budget entry {removed.get('source')!r} "
            f"(INR {removed.get('inr')}) deleted outright"
        )
    else:
        removed = methods.pop(rng.randrange(len(methods)))
        note = f"valuation method {removed.get('label')!r} deleted outright" + (
            " (this case's only method -- the whole lattice, not one of several arms)"
            if not methods else ""
        )
    return regimes, valuation, note


def op_overclaim(regimes, valuation, facts, rng):
    regimes = copy.deepcopy(regimes)
    hedged = [r for r in regimes if r.get("certainty") != "settled"]
    r = rng.choice(hedged)  # IndexError, loudly, if this project ever ships a
    # case with every regime already settled -- an honest crash beats a
    # silent no-op mutation. Never triggered on the real six (checked).
    before = r.get("certainty")
    r["certainty"] = "settled"
    return regimes, valuation, (
        f"{r.get('regime')}: certainty strengthened {before!r} -> 'settled', "
        f"citation/reasoning untouched"
    )


OPERATORS = [
    ("CITE_SWAP", op_cite_swap),
    ("DATE_SHIFT", op_date_shift),
    ("RATE_SUB", op_rate_sub),
    ("LABEL_MISMATCH", op_label_mismatch),
    ("ARITH_CORRUPT", op_arith_corrupt),
    ("SILENT_OMIT", op_silent_omit),
    ("OVERCLAIM", op_overclaim),
]


def _caught(attacked):
    return any(a.get("survived") is False for a in attacked)


def run_live(seed, model="adversarial"):
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    for case_id in CASE_FILES:
        facts, tax_year, missing, regimes, valuation = load_case(case_id)
        for op_name, op_fn in OPERATORS:
            rng = random.Random(f"{seed}-{case_id}-{op_name}")  # str seed, not a
            # tuple: random.seed() hashes str/bytes deterministically via its own
            # conversion, but falls back to the built-in hash() for any other
            # type -- and hash() of a str is salted per-process by default
            # (PYTHONHASHSEED), which would have made "--seed 1337" produce a
            # DIFFERENT 42 mutants on every separate run. Checked, not assumed.
            m_regimes, m_valuation, note = op_fn(regimes, valuation, facts, rng)
            try:
                attacked, survived, limits, meta = node5_adversarial.check(
                    m_regimes, missing, m_valuation, tax_year, model=model)
                caught, error = _caught(attacked), None
            except LLMError as e:
                attacked, survived, limits = [], [], []
                caught, error = None, str(e)
            row = {
                "case": case_id, "operator": op_name, "seed": seed, "note": note,
                "mutated_regimes": m_regimes, "mutated_valuation": m_valuation,
                "attacked": attacked, "checked_and_survived": survived, "limits": limits,
                "caught": caught, "error": error,
            }
            rows.append(row)
            out_path = os.path.join(OUT_DIR, f"{case_id}_{op_name}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(row, f, indent=2)
    return rows


def report(rows):
    print("\n" + "=" * 92)
    print("  MUTATE — node5_adversarial.py mutation score (7 operators x 6 cases = 42 mutants)")
    print("=" * 92)

    errored = [r for r in rows if r["error"] is not None]
    scored = [r for r in rows if r["error"] is None]

    by_op = {}
    for row in scored:
        by_op.setdefault(row["operator"], []).append(row)

    for op_name, _ in OPERATORS:
        op_rows = by_op.get(op_name, [])
        caught = [r for r in op_rows if r["caught"]]
        print(f"\n  {op_name}  --  {len(caught)}/{len(op_rows)} caught" if op_rows
              else f"\n  {op_name}  --  0/0 scored (all errored)")
        for r in op_rows:
            mark = "[CAUGHT]" if r["caught"] else "[MISSED]"
            print(f"    {mark}  {r['case']:<4} {r['note']}")

    if errored:
        print(f"\n  {len(errored)} mutant(s) errored before a verdict (full detail in "
              f"runs/mutants/) -- excluded from the score below, not counted either way:")
        for r in errored:
            print(f"    {r['case']:<4} {r['operator']:<16} {r['error'].splitlines()[0]}")

    k = sum(1 for r in scored if r["caught"])
    n = len(scored)
    print(f"\n{'=' * 92}")
    if n == 0:
        print("  0 scored mutants -- nothing to report (see errors above).")
    else:
        lo, hi = binom_ci.clopper_pearson(k, n)
        print(f"  OVERALL: {k}/{n} caught = {k / n:.1%}   95% Clopper-Pearson CI: [{lo:.1%}, {hi:.1%}]")
        print("  'Caught' = any landed attack (survived=False) anywhere in that mutant's own "
              "attacked[] -- not a claim node 5 named the specific corrupted field. Per-operator "
              "breakdown above is the real result; this total is not, any more than "
              "mutation_corpus.py's is.")
    print("=" * 92 + "\n")


# ─────────────────────────────────────────────────────────────
# --self-test — two checks, zero API calls. Neither one asks node 5
# anything; both confirm this harness's OWN plumbing is trustworthy
# before a single one of its 42 real mutants is.
# ─────────────────────────────────────────────────────────────

def _self_test_null_mutant():
    """Check 1/2: the identity transform -- D1's own real, frozen
    (regimes, missing, valuation, tax_year), deep-copied and handed
    straight through with NO operator applied -- must reproduce EXACTLY
    the frozen record's own already-known attack result, not a new or
    different one. Runs entirely through DIVERGENCE_REPLAY=1 against the
    cache build_replay_cache.py already seeded from this exact record
    (D63): the identity transform produces byte-identical request
    content to what was cached, so this is a real cache HIT, zero API
    calls, not a mock. Confirms this file's own deep-copy/JSON
    round-tripping of regimes/valuation/missing introduces no incidental
    corruption of its own before a single real mutation operator is
    ever trusted to mean something."""
    old = os.environ.get("DIVERGENCE_REPLAY")
    os.environ["DIVERGENCE_REPLAY"] = "1"
    ok = False
    try:
        facts, tax_year, missing, regimes, valuation = load_case("D1")
        attacked, survived, limits, meta = node5_adversarial.check(
            copy.deepcopy(regimes), copy.deepcopy(missing), copy.deepcopy(valuation), tax_year)
        frozen = json.load(open(os.path.join(RUNS, "D1_final_seed2_attack.json"), encoding="utf-8"))
        ok = attacked == frozen["attacked"] and survived == frozen["checked_and_survived"]
    except Exception as e:
        print(f"    (error: {e})")
    finally:
        if old is None:
            os.environ.pop("DIVERGENCE_REPLAY", None)
        else:
            os.environ["DIVERGENCE_REPLAY"] = old
    print(f"  {'null mutant reproduces frozen D1 attack (replay, 0 calls)':<62}{'OK' if ok else 'FAIL'}")
    return ok


_SCOPE_BAD = [
    "Rule 206, Income-tax Rules, 2026",
    "Rule 57, Income-tax Rules, 2026",
    "Rule 243(8)(e), Income-tax Rules, 2026",
]


def _self_test_scope_reach_still_caught():
    """Check 2/2: a regime shaped exactly the way this file's own
    operators shape one (real dict, real 'citation'/'certainty' keys) --
    retargeted onto each of the three historical scope-reach defects
    scope_enforcer.py (⚙ E, DECISION-D59.md/D65) already proves it
    catches -- must still be dropped by enforce_scope(). Zero API calls;
    this is the deterministic gate, not node 5. Confirms this file's
    mutants are shaped correctly enough to trigger an already-proven
    catch before any of the 42 real mutants are trusted against node 5,
    which cannot be checked this cheaply."""
    corpus = citation_matcher.load_corpus()
    facts = {"asset": {"value": "USDC"}}
    all_ok = True
    for provision in _SCOPE_BAD:
        r = {"regime": "valuation_method", "outcome": "test", "certainty": "settled",
             "citation": {"provision": provision}}
        kept, dropped = scope_enforcer.enforce_scope([r], facts, corpus)
        ok = bool(dropped)
        all_ok = all_ok and ok
        print(f"  scope-reach still caught: {provision:<42} {'OK' if ok else 'FAIL'}")
    return all_ok


def self_test():
    print("\n  SELF-TEST — mutate.py\n")
    ok1 = _self_test_null_mutant()
    ok2 = _self_test_scope_reach_still_caught()
    passed = int(ok1) + int(ok2)
    print(f"\n  {passed}/2 as expected. Neither check called node 5 for real -- see the "
          f"module docstring for why the 42-mutant sweep itself needs a live key.\n")
    return ok1 and ok2


def main():
    ap = argparse.ArgumentParser(
        description="Deterministic, seeded defect-injection harness for node5_adversarial.py")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--model", default="adversarial")
    a = ap.parse_args()

    if a.self_test:
        sys.exit(0 if self_test() else 1)

    try:
        llm_call.provider_name()
    except LLMError as e:
        print("FAIL  " + str(e))
        sys.exit(1)

    print(f"  provider={llm_call.provider_display()} model={llm_call.model_display(a.model)} seed={a.seed}")
    rows = run_live(a.seed, model=a.model)
    report(rows)
    print(f"  42 mutants written -> {os.path.relpath(OUT_DIR)}/\n")


if __name__ == "__main__":
    main()

# ─────────────────────────────────────────────────────────────
# LIMITATIONS — state these in the documentation. Do not hide them.
#
# 1. "CAUGHT" IS ANY LANDED ATTACK, NOT A TARGETED ONE.
#    A mutant counts as caught if attacked[] contains ANY entry with
#    survived=False -- not specifically an attack that names the
#    corrupted field. A free-text matcher precise enough to credit only
#    an exact hit, across seven mechanically unrelated kinds of
#    corruption, would manufacture a precision this project has no
#    evidence for.
#
# 2. RATE_SUB / LABEL_MISMATCH DRAW FROM A HAND-WRITTEN POOL.
#    _ALT_SOURCES and _ALT_LABELS are fixed, generic strings in this
#    project's own valuation vocabulary (real source/label SHAPES from
#    D1's own lattice), not extracted per-case. A mismatch that reads as
#    slightly domain-incongruous for a given case is the point of the
#    operator, not a flaw in it.
#
# 3. DATE_SHIFT CAN BE A NO-OP, AND SAYS SO WHEN IT IS.
#    "reset to the real transaction date" mode does nothing if the
#    method the RNG picked already carries that exact date_used --
#    checked live: seed 1337, case D1, does exactly this. Not
#    specially avoided (a retry-until-different rule would make the
#    mutant set depend on more than the stated seed+case+operator);
#    the mutant's own "note" always shows before/after verbatim, so a
#    no-op is visible in the output, never silently hidden as a
#    "mutation" that wasn't one.
#
# 4. CITE_SWAP NUDGES A NUMBER, IT DOES NOT LOOK UP A REAL NEIGHBOUR.
#    _neighbouring_citation() increments the first section/rule number
#    it recognises by one. It sometimes lands on a real, different
#    corpus provision (Rule 206 -> Rule 207 is real; Rule 56 -> Rule 57
#    is real) and sometimes on a number nothing in the corpus holds --
#    both are disclosed in the mutant's own "note", neither is
#    specially handled.
#
# 5. --self-test PROVES THE HARNESS'S OWN PLUMBING, NOT NODE 5.
#    Both checks are deliberately zero-API-call: one confirms the
#    identity transform introduces no incidental corruption of its own
#    (replay mode, D63's existing D1 cache entry), the other confirms
#    this file's own regime-shaped mutants still trigger
#    scope_enforcer.py's already-proven catch. Neither checks whether
#    node 5 catches anything real -- only `python mutate.py` with a live
#    key measures that.
# ─────────────────────────────────────────────────────────────
