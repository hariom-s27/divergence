#!/usr/bin/env python3
"""
P03 sweep summary -- computed only from the per-call files in full/
(plus full/human_audit.json if present). Writes full/summary.json and
full/summary.md. Makes no model call and reads no cache.

    python summarize.py                  # from this folder or anywhere
    python summarize.py <dir>            # same, for another folder of *_r<n>.json files
"""
import glob
import inspect
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIV = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, DIV)
import binom_ci  # noqa: E402
import mutate    # noqa: E402

FULL = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "full")
NAME = re.compile(r"^(C[1-5]|D1)_([A-Z_]+)_r(\d+)\.json$")
OPS = [op for op, _ in mutate.OPERATORS]
CASES = list(mutate.CASE_FILES)

# Pre-registered in expectations.md section 3, before any live call.
TERM_CLEAN = {
    "C1": ["CITE_SWAP", "DATE_SHIFT", "RATE_SUB", "LABEL_MISMATCH", "ARITH_CORRUPT", "SILENT_OMIT"],
    "C2": ["CITE_SWAP", "LABEL_MISMATCH", "ARITH_CORRUPT"],
    "C3": ["CITE_SWAP", "DATE_SHIFT", "ARITH_CORRUPT"],
    "C4": ["CITE_SWAP", "RATE_SUB", "LABEL_MISMATCH", "ARITH_CORRUPT"],
    "C5": ["DATE_SHIFT", "LABEL_MISMATCH", "ARITH_CORRUPT"],
    "D1": ["CITE_SWAP", "RATE_SUB", "LABEL_MISMATCH", "ARITH_CORRUPT"],
}


def rate(k, n):
    if n == 0:
        return {"k": k, "n": n, "pct": None, "ci95": None}
    lo, hi = binom_ci.clopper_pearson(k, n)
    return {"k": k, "n": n, "pct": round(100.0 * k / n, 1), "ci95": [round(100 * lo, 1), round(100 * hi, 1)]}


def fmt(r):
    if r["n"] == 0:
        return f"{r['k']}/0 (n/a)"
    return f"{r['k']}/{r['n']} = {r['pct']}% [CI {r['ci95'][0]}–{r['ci95'][1]}%]"


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=DIV, capture_output=True, text=True).stdout.strip()
    except Exception as e:  # recorded, never fatal
        return f"(git unavailable: {e})"


def load_rows():
    rows = []
    for p in sorted(glob.glob(os.path.join(FULL, "*_r*.json"))):
        m = NAME.match(os.path.basename(p))
        if not m:
            continue
        r = json.load(open(p, encoding="utf-8"))
        r["_file"] = os.path.basename(p)
        r["_id"] = os.path.basename(p)[:-5]
        assert (r["case"], r["operator"], r["rep"]) == (m.group(1), m.group(2), int(m.group(3))), p
        rows.append(r)
    return rows


def main():
    rows = load_rows()
    audit_p = os.path.join(FULL, "human_audit.json")
    audit = json.load(open(audit_p, encoding="utf-8")) if os.path.exists(audit_p) else {}
    reps = sorted({r["rep"] for r in rows})
    errored = [r for r in rows if r["error"] is not None]
    mutants = [r for r in rows if r["operator"] != "NULL" and not r.get("noop")]
    scored = [r for r in mutants if r["error"] is None]
    nulls = [r for r in rows if r["operator"] == "NULL"]
    nulls_ok = [r for r in nulls if r["error"] is None]
    noops = [r for r in rows if r.get("noop")]

    def spec_k(rs):
        return sum(1 for r in rs if r.get("caught_specific"))

    def any_k(rs):
        return sum(1 for r in rs if r["caught"])

    hits = [r for r in scored if r.get("caught_specific")]
    hit_audit = audit.get("hits", {})
    confirmed = [r for r in hits if hit_audit.get(r["_id"], {}).get("verdict") == "confirmed"]
    partial = [r for r in hits if hit_audit.get(r["_id"], {}).get("verdict") == "partial"]
    not_confirmed = [r for r in hits if hit_audit.get(r["_id"], {}).get("verdict") == "not_confirmed"]
    placebo_audit = audit.get("placebo", {})
    pairs = [(r, op, v) for r in nulls_ok for op, v in (r.get("placebo_specific") or {}).items()]
    placebo_hits = [(r, op, v) for r, op, v in pairs if v["hit"]]
    clean = [r for r in scored if r["operator"] in TERM_CLEAN.get(r["case"], [])]

    per_op = {op: {"specific": rate(spec_k([r for r in scored if r["operator"] == op]),
                                     len([r for r in scored if r["operator"] == op])),
                   "any_attack": rate(any_k([r for r in scored if r["operator"] == op]),
                                      len([r for r in scored if r["operator"] == op])),
                   "errors": len([r for r in mutants if r["operator"] == op and r["error"] is not None])}
              for op in OPS}
    per_case = {c: {"specific": rate(spec_k([r for r in scored if r["case"] == c]),
                                     len([r for r in scored if r["case"] == c])),
                    "any_attack": rate(any_k([r for r in scored if r["case"] == c]),
                                       len([r for r in scored if r["case"] == c])),
                    "errors": len([r for r in mutants if r["case"] == c and r["error"] is not None])}
                for c in CASES}
    per_rep = {f"r{n}": {"specific": rate(spec_k([r for r in scored if r["rep"] == n]),
                                          len([r for r in scored if r["rep"] == n])),
                         "any_attack": rate(any_k([r for r in scored if r["rep"] == n]),
                                            len([r for r in scored if r["rep"] == n])),
                         "null_flag": rate(any_k([r for r in nulls_ok if r["rep"] == n]),
                                           len([r for r in nulls_ok if r["rep"] == n]))}
               for n in reps}

    def stability(key):
        out = {"stable": 0, "flipping": 0, "insufficient": 0, "flipping_list": [], "insufficient_list": []}
        for c in CASES:
            for op in OPS:
                rs = [r for r in mutants if r["case"] == c and r["operator"] == op]
                if not rs:
                    continue
                vals = [bool(r[key]) for r in rs if r["error"] is None]
                if len(vals) < 2:
                    out["insufficient"] += 1
                    out["insufficient_list"].append(f"{c}/{op}")
                elif len(set(vals)) == 1:
                    out["stable"] += 1
                else:
                    out["flipping"] += 1
                    out["flipping_list"].append(f"{c}/{op}: " + ",".join(
                        f"r{r['rep']}={'ERR' if r['error'] else int(bool(r[key]))}" for r in rs))
        return out

    attempts = [a for r in rows for a in (r.get("attempts") or [])]
    calls = [a["call"] for a in attempts if a.get("call")]
    first_err = [r for r in rows if r.get("first_attempt_error")]
    summary = {
        "generated_from": f"{len(rows)} per-call files in full/ (*_r<n>.json)",
        "reps": reps,
        "counts": {"files": len(rows), "mutant_rows": len(mutants), "scored_mutants": len(scored),
                   "null_rows": len(nulls), "noop_rows": len(noops), "error_rows": len(errored),
                   "nominal_real_mutants": 40 * len(reps)},
        "primary_specific_matcher": rate(len(hits), len(scored)),
        "primary_specific_human_confirmed": rate(len(confirmed), len(scored)),
        "human_partial_NOT_HEADLINE": rate(len(partial), len(scored)),
        "human_not_confirmed": len(not_confirmed),
        "human_audit_rater": audit.get("rater"),
        "placebo_chance_match_yes": sum(1 for v in placebo_audit.values() if v.get("chance_match") == "yes"),
        "placebo_audited": len(placebo_audit),
        "human_audit_present": bool(hit_audit),
        "human_audit_unaudited_hits": [r["_id"] for r in hits if r["_id"] not in hit_audit],
        "secondary_any_attack": rate(any_k(scored), len(scored)),
        "null_false_flag_any_attack": rate(any_k(nulls_ok), len(nulls_ok)),
        "specific_placebo": rate(len(placebo_hits), len(pairs)),
        "specific_term_clean_subset": rate(spec_k(clean), len(clean)),
        "per_operator": per_op, "per_case": per_case, "per_rep": per_rep,
        "stability_specific": stability("caught_specific"),
        "stability_any_attack": stability("caught"),
        "surviving_mutants_specific": [f"{r['case']}/{r['operator']}/r{r['rep']}"
                                       for r in scored if not r.get("caught_specific")],
        "specific_hits": [{"id": r["_id"], "excerpt": (r.get("specific_match") or {}).get("excerpt"),
                           "human": hit_audit.get(r["_id"])} for r in hits],
        "placebo_hits": [{"id": r["_id"], "operator_terms": op, "excerpt": v.get("excerpt"),
                          "human": audit.get("placebo", {}).get(f"{r['_id']}:{op}")}
                         for r, op, v in placebo_hits],
        "noop_mutants": sorted({f"{r['case']}/{r['operator']}" for r in noops}),
        "errors": [{"id": r["_id"], "first_line": r["error"].splitlines()[0][:200]} for r in errored],
        "error_rates": {"first_attempt": rate(len(first_err), len(rows)),
                        "after_retry": rate(len(errored), len(rows)),
                        "schema_retried_calls": sum(1 for r in rows if r.get("schema_retried"))},
        "metadata": {
            "response_models": sorted({str(c.get("response_model")) for c in calls}),
            "requested_models": sorted({str(c.get("model")) for c in calls}),
            "temperature_sent": sorted({str(r.get("temperature_sent")) for r in rows}),
            "seed_sent": sorted({str(c.get("seed")) for c in calls}),
            "mutation_seed": sorted({r["seed"] for r in rows}),
            "seed_note": "Featherless: seed 'Not reliable, as we use multiple servers'; none was sent.",
            "first_start_utc": min((a["started_utc"] for a in attempts), default=None),
            "last_finish_utc": max((a["finished_utc"] for a in attempts), default=None),
            "api_calls_incl_retries": len(attempts),
            "total_in_tokens": sum(c.get("in_tokens") or 0 for c in calls),
            "total_out_tokens": sum(c.get("out_tokens") or 0 for c in calls),
            "total_latency_s": round(sum(c.get("elapsed_s") or 0 for c in calls), 1),
            "harness_head": git("rev-parse", "HEAD"),
            "harness_uncommitted": git("status", "--porcelain=v1", "--", ".", "../tests"),
            "kill_rule_specific_primary": inspect.getsource(mutate.match_specific),
            "kill_rule_any_attack_secondary": inspect.getsource(mutate._caught),
        },
    }
    with open(os.path.join(FULL, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    s = summary
    md = [f"# Node-5 mutation sweep: summary (R={len(reps)})", "",
          "Computed by `runs/2026-10-21_mutants/summarize.py` from the per-call files in this folder. "
          "Pre-registration: `../expectations.md` + `../expectations_amendment.md` + "
          "`../expectations_amendment_2.md`.", "",
          "## Headline", "",
          "| Measure | Result |", "|---|---|",
          f"| **SPECIFIC, matcher count (primary)** | {fmt(s['primary_specific_matcher'])} |",
          f"| SPECIFIC, human-confirmed count | {fmt(s['primary_specific_human_confirmed'])}"
          + ("" if s["human_audit_present"] else " (audit not yet done)") + " |",
          f"| SPECIFIC, human partial (not part of the headline) | {fmt(s['human_partial_NOT_HEADLINE'])} |",
          f"| SPECIFIC, human not_confirmed | {s['human_not_confirmed']} of {len(hits)} matcher hits |",
          f"| Placebo hits judged chance match | {s['placebo_chance_match_yes']} of {s['placebo_audited']} audited |",
          f"| SPECIFIC, term-clean subset | {fmt(s['specific_term_clean_subset'])} |",
          f"| ANY-ATTACK (secondary) | {fmt(s['secondary_any_attack'])} |",
          f"| Null false-flag rate (ANY-ATTACK) | {fmt(s['null_false_flag_any_attack'])} |",
          f"| SPECIFIC placebo (null critiques × each operator's terms) | {fmt(s['specific_placebo'])} |",
          f"| First-attempt error rate (all calls) | {fmt(s['error_rates']['first_attempt'])} |",
          f"| After-retry ERROR rate (all calls) | {fmt(s['error_rates']['after_retry'])} |", "",
          f"Denominators: {s['counts']['nominal_real_mutants']} real mutants nominal (40 × R; the 2 no-op "
          f"mutants excluded) minus after-retry ERRORs = {s['counts']['scored_mutants']} scored. "
          f"Nulls ({s['counts']['null_rows']}) and ERRORs ({s['counts']['error_rows']}) are counted separately. "
          "CI = Clopper-Pearson 95% (binom_ci.py).", "",
          "## Per operator", "", "| Operator | SPECIFIC | ANY-ATTACK | ERRORs |", "|---|---|---|---|"]
    md += [f"| {op} | {fmt(v['specific'])} | {fmt(v['any_attack'])} | {v['errors']} |" for op, v in per_op.items()]
    md += ["", "## Per case", "", "| Case | SPECIFIC | ANY-ATTACK | ERRORs |", "|---|---|---|---|"]
    md += [f"| {c} | {fmt(v['specific'])} | {fmt(v['any_attack'])} | {v['errors']} |" for c, v in per_case.items()]
    md += ["", "## Per repetition (no repetition is preferred over another)", "",
           "| Rep | SPECIFIC | ANY-ATTACK | Null flag |", "|---|---|---|---|"]
    md += [f"| {k} | {fmt(v['specific'])} | {fmt(v['any_attack'])} | {fmt(v['null_flag'])} |" for k, v in per_rep.items()]
    for key, label in (("stability_specific", "SPECIFIC"), ("stability_any_attack", "ANY-ATTACK")):
        st = s[key]
        md += ["", f"## Verdict stability across repetitions: {label}", "",
               f"Stable {st['stable']} · flipping {st['flipping']} · insufficient valid reps {st['insufficient']} "
               f"(of 40 real mutants)."]
        md += [f"- {x}" for x in st["flipping_list"]]
        if st["insufficient_list"]:
            md += [f"- insufficient: {', '.join(st['insufficient_list'])}"]
    md += ["", "## SPECIFIC hits (matcher) with human audit", "", "| Mutant | Excerpt (normalised) | Human |", "|---|---|---|"]
    md += [f"| {h['id']} | {(h['excerpt'] or '').replace('|', '/')[:200]} | "
           f"{(h['human'] or {}).get('verdict', 'not audited')}: {(h['human'] or {}).get('reason', '')} |"
           for h in s["specific_hits"]]
    md += ["", "## Placebo hits (null critique matched an operator's terms)", ""]
    md += [f"- {p['id']} × {p['operator_terms']}: {(p['excerpt'] or '')[:200]}"
           + (f" (human: {p['human']['verdict']}: {p['human'].get('reason', '')})" if p["human"] else "")
           for p in s["placebo_hits"]] or ["- none"]
    md += ["", "## Surviving mutants (SPECIFIC)", "", ", ".join(s["surviving_mutants_specific"]) or "none",
           "", "## Excluded", "", f"- No-op mutants: {', '.join(s['noop_mutants'])}",
           f"- ERRORs ({len(s['errors'])}): " + ("; ".join(f"{e['id']}: {e['first_line'][:120]}" for e in s["errors"]) or "none"),
           f"- Schema-retried calls: {s['error_rates']['schema_retried_calls']}", "",
           "## Run metadata", ""]
    meta = s["metadata"]
    md += [f"- {k}: {meta[k]}" for k in ("response_models", "requested_models", "temperature_sent", "seed_sent",
                                         "mutation_seed", "seed_note", "first_start_utc", "last_finish_utc",
                                         "api_calls_incl_retries", "total_in_tokens", "total_out_tokens",
                                         "total_latency_s", "harness_head")]
    md += ["- harness uncommitted (git status, divergence/ + tests/):", "```", meta["harness_uncommitted"], "```",
           "- Kill rule, SPECIFIC (primary), quoted from mutate.py:", "```python", meta["kill_rule_specific_primary"].rstrip(), "```",
           "- Kill rule, ANY-ATTACK (secondary):", "```python", meta["kill_rule_any_attack_secondary"].rstrip(), "```", ""]
    with open(os.path.join(FULL, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"summary.json + summary.md written from {len(rows)} files; SPECIFIC "
          f"{fmt(s['primary_specific_matcher'])}; ANY {fmt(s['secondary_any_attack'])}; "
          f"null flag {fmt(s['null_false_flag_any_attack'])}; placebo {fmt(s['specific_placebo'])}; "
          f"errors after retry {len(errored)}")


if __name__ == "__main__":
    main()
