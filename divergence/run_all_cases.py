#!/usr/bin/env python3
"""
run_all_cases.py -- DIVERGENCE, D73
Runs all six real evaluation cases (C1-C5, D1) through run_pipeline.py --
one subprocess per case, run_pipeline.py itself completely unmodified
(refactoring its already-verified, CI-gated main() into an importable
function was considered and rejected: real risk to already-shipped code,
for a feature that can't even be exercised with real data in an
environment with no API key). Builds the measured-cost table
results.md's own "Measured, per case" section reads.

Per case: tries a real run first, live or replayed -- whatever this
shell's own environment (FEATHERLESS_API_KEY / DIVERGENCE_REPLAY) makes
possible; this script makes no provider decision of its own, llm_call.py
already owns that (D44). If that fails, falls back to the case's own
real historical token counts (runs/21aug/<case>.json's own
_meta.llm.by_node -- never fabricated), clearly labelled as historical
in the table's own Source column, never silently presented as this run's
own number.

WALL-CLOCK NEVER FALLS BACK. It is either a real number from a run that
just happened (live, D64's own time.perf_counter()), or the table says
"not measured" -- no case's historical record has ever carried it, every
one of them predates D64. A replayed run (D1, the only case with a
seeded cache) still shows "not measured" for wall time even though its
tokens ARE freshly re-derived, because a replay hit correctly restores
the ORIGINAL historical call's own honestly-empty elapsed_s (D72), not
this run's.

    python run_all_cases.py                    # tries live/replay per case
    python run_all_cases.py --out table.md      # write the table elsewhere
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cost_model  # noqa: E402 -- reuses PRICES for the Claude-metered figure

CASES = {
    "C1": "C1_pipeline.json", "C2": "C2_pipeline.json", "C3": "C3_pipeline.json",
    "C4": "C4_pipeline.json", "C5": "C5_pipeline.json", "D1": "D1_final_seed2.json",
}
TAX_YEAR = "FY 2026-27"  # every one of the six real cases' own frozen record agrees -- checked
RUNS_DIR = os.path.join(HERE, "runs", "21aug")
OUT_DIR = os.path.join(HERE, "runs", "measured")

FEATHERLESS_PRICES = {
    # USD per million tokens (in, out). Verified directly against
    # Featherless's own live /v1/models catalog, 23 Aug 2026 -- not a
    # third-party aggregator figure (several disagreed with each other
    # and with this catalog when checked, so none of them are used here).
    "mistralai/Mistral-Large-Instruct-2411": (0.125, 1.15),
    # Qwen/Qwen2.5-7B-Instruct, Qwen/Qwen2.5-72B-Instruct: genuinely NOT
    # FOUND in the live catalog as of this check, despite being this
    # project's own configured "small"/"large" slots (llm_call.py
    # PROVIDERS) and having served every real call this project has made.
    # A catalog listing and a model's real serving availability on an
    # existing account are not necessarily the same thing -- the
    # identical gap DECISION-D43.md already documents for meta-llama/*
    # licence gating. Reported below as unpriced, never guessed at.
}


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def _short_reason(raw):
    """llm_call.py's own error strings are genuinely single lines (long
    ones -- see llm_call.py:143's key-not-set message and its replay-miss
    message), not multi-line text that merely looks wrapped in source.
    Classified to a short label for the table's Source column; the full
    text is never lost, just not the thing embedded in a table cell --
    it's still in the record's own directory if `--out` output is kept."""
    if "FEATHERLESS_API_KEY is not set" in raw:
        return "no API key in this shell"
    if "no cached response for this exact request" in raw:
        return "no replay cache entry for this case"
    return (raw[:80] + "...") if len(raw) > 80 else raw


def _run_live_or_replay(case_id):
    """One case, one subprocess, run_pipeline.py completely unmodified.
    Returns (record_dict_or_None, short_reason_or_None)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{case_id}.json")
    cmd = [sys.executable, os.path.join(HERE, "run_pipeline.py"),
           "--record-id", f"{case_id}-measured", "--tax-year", TAX_YEAR,
           "--text", os.path.join(HERE, "cases", case_id, "input.md"),
           "--node5", "--out", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raw = (r.stderr or r.stdout).strip().replace("\n", " ")
        return None, (_short_reason(raw) if raw else "(no output)")
    return json.load(open(out_path, encoding="utf-8")), None


def featherless_cost(by_node):
    """Sums real per-model cost for whatever models have a verified
    price; returns (partial_or_full_total, sorted_missing_models).
    Never nulls out a real, priceable figure (e.g. node5's Mistral cost)
    just because a DIFFERENT node's model is unpriced -- reports exactly
    what's known and exactly what isn't, together."""
    total = 0.0
    missing = set()
    for row in by_node.values():
        model = row.get("model")
        price = FEATHERLESS_PRICES.get(model)
        if price is None:
            missing.add(model)
            continue
        in_p, out_p = price
        total += row.get("in_tokens", 0) * in_p / 1e6 + row.get("out_tokens", 0) * out_p / 1e6
    return total, sorted(missing)


def claude_cost(in_tokens, out_tokens, model="Sonnet 5 (intro)"):
    """Real measured tokens through cost_model.py's own PRICES table.
    No caching assumed -- this project's real calls never use prompt
    caching, unlike price_run()'s cacheable/volatile split, which prices
    a hypothetical MODELLED estimate, not an actual measured run."""
    base_in, _cw, _cr, out_p, newtok = cost_model.PRICES[model]
    it = cost_model.to_model_tokens(in_tokens, newtok)
    ot = cost_model.to_model_tokens(out_tokens, newtok)
    return it * base_in / 1e6 + ot * out_p / 1e6


def _row_for_case(case_id):
    rec, err = _run_live_or_replay(case_id)
    if rec is not None:
        by_node = rec.get("_meta", {}).get("llm", {}).get("by_node", {})
        replayed = rec.get("_meta", {}).get("llm", {}).get("replayed", False)
        has_wall = any(v.get("elapsed_s") for v in by_node.values())
        wall_s = sum(v.get("elapsed_s", 0.0) for v in by_node.values()) if has_wall else None
        source = "measured (this run, replayed)" if replayed else "measured (this run, live)"
    else:
        hist = json.load(open(os.path.join(RUNS_DIR, CASES[case_id]), encoding="utf-8"))
        by_node = hist.get("_meta", {}).get("llm", {}).get("by_node", {})
        wall_s = None
        source = f"historical (frozen record; live/replay attempt failed: {err})"

    in_tok = sum(v.get("in_tokens", 0) for v in by_node.values())
    out_tok = sum(v.get("out_tokens", 0) for v in by_node.values())
    f_cost, f_missing = featherless_cost(by_node)
    c_cost = claude_cost(in_tok, out_tok)
    return {
        "case": case_id, "wall_s": wall_s, "in_tokens": in_tok, "out_tokens": out_tok,
        "featherless_cost": f_cost, "featherless_missing": f_missing,
        "claude_cost": c_cost, "source": source,
    }


def render_table(rows):
    lines = [
        "| Case | Wall (s) | Input tokens | Output tokens | "
        "Cost @ Featherless (USD) | Cost @ Claude, metered (USD) | Source |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        wall = f"{r['wall_s']:.2f}" if r["wall_s"] is not None else "not measured"
        if r["featherless_missing"]:
            fc = f"${r['featherless_cost']:.5f} partial ({', '.join(r['featherless_missing'])} unpriced)"
        else:
            fc = f"${r['featherless_cost']:.5f}"
        cc = f"${r['claude_cost']:.4f}"
        lines.append(f"| {r['case']} | {wall} | {r['in_tokens']:,} | {r['out_tokens']:,} "
                     f"| {fc} | {cc} | {r['source']} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Run all six real cases, build the measured-cost table")
    ap.add_argument("--out", default=os.path.join(HERE, "MEASURED-TABLE.md"))
    a = ap.parse_args()

    rows = []
    for case_id in CASES:
        row = _row_for_case(case_id)
        rows.append(row)
        print(f"  {case_id}: {row['source']}")

    table = render_table(rows)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(table)
    print(f"\n  wrote {a.out}\n")
    print(table)


if __name__ == "__main__":
    main()
