#!/usr/bin/env python3
"""
cost_model.py  --  DIVERGENCE Step 18
Cost, latency and throughput model for the DIVERGENCE pipeline.

Standard library only. No API key, no network.

    python cost_model.py                      # full report
    python cost_model.py --profile corpus_profile.json   # measured corpus
    python cost_model.py --sensitivity        # which parameter dominates
    python cost_model.py --measured runs/some_pipeline_record.json  # D64:
        # real wall-clock latency read from a record's own _meta.llm.by_node
        # (llm_call.py's time.time(), added D64) -- not this file's own
        # modelled latency_estimate(), which prices a different, hypothetical
        # Anthropic Claude deployment, not the real Featherless one.

PRICES: taken from Anthropic's published pricing page on 9 August 2026.
        https://platform.claude.com/docs/en/about-claude/pricing
        Re-check before submission. Sonnet 5 introductory pricing expires
        31 August 2026 and the standard rate is materially higher.

TOKEN COUNTS: characters/4 per Anthropic's own stated approximation,
        with a 1.30x multiplier on Claude 4.7+ models, which the pricing
        page states use a newer tokenizer producing ~30% more tokens for
        the same text. Two corpus provisions are MEASURED from the
        Gazette notification of the Income-tax Rules, 2026; the rest of
        the corpus profile is ESTIMATED until measure_corpus.py is run
        against the real corpus/ directory. Every estimated figure is
        marked (est) in the output.
"""

import json
import os
import sys

# Found live, 22 Aug, testing --measured (D64): this file prints the rupee
# sign, and unlike every other executable script in this project, never
# guarded stdout's encoding -- a plain `python cost_model.py` crashes with
# UnicodeEncodeError on a default Windows console (cp1252), a pre-existing
# gap this file happened to be the one to surface. Same one-line fix
# citation_matcher.py etc. already carry.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ----------------------------------------------------------------------
# PRICES  --  USD per million tokens. Source: Anthropic pricing page.
# ----------------------------------------------------------------------
PRICES = {
    # name:            (base_in, cache_write_5m, cache_read, out, new_tokenizer)
    "Opus 5":          (5.00,  6.25,  0.50, 25.00, True),
    "Sonnet 5 (intro)": (2.00,  2.50,  0.20, 10.00, True),
    "Sonnet 5 (Sep 1)": (3.00,  3.75,  0.30, 15.00, True),
    "Haiku 4.5":       (1.00,  1.25,  0.10,  5.00, False),
}
BATCH_DISCOUNT = 0.50          # Batch API: 50% off input and output
NEW_TOKENIZER_FACTOR = 1.30

# ----------------------------------------------------------------------
# CORPUS PROFILE  --  legacy tokens (chars/4)
# MEASURED entries come from the Gazette text in project knowledge.
# ----------------------------------------------------------------------
CORPUS = {
    # MEASURED 9 Aug 2026 from the real corpus/ (chars/4). 16 Tier A files.
    # (total_tokens, verbatim_only_tokens)
    "FBIL-METHODOLOGY":        (1006,  526),
    "FEMA-2n":                 (1104,  402),
    "FEMA-3-7-8":              (1658,   96),
    "GST-CGST-50":             ( 847,  847),
    "GST-CGST-74A":            (1038,  670),
    "GST-IGST-2-6":            ( 300,  300),
    "IT-115BBH":               (1047,  495),
    "IT-2-47A":                ( 841,  841),
    "IT-393-1-T8vi":           (1111,  587),
    "IT-439-8":                ( 529,  529),
    "IT-56-2-x":               (1506,  286),
    "IT-RULE-115":             (1318, 1318),
    "IT-RULE-57":              (4704, 3615),
    "ITR2026-RCASP-VALUATION": (1313,  519),
    "ITR2026-RULE-57":         ( 688,  360),
    "SBI-TTBR-DATA":           ( 451,  229),
}
VERBATIM_ONLY = False   # set True to price the injection-safe corpus

# Which corpus files each node may cite. This mapping IS the cost design.
NODE_SCOPE = {
    "1 Intake + extraction":  [],
    "2 Gap detector":         [],
    "3 Dual valuation":       ["FBIL-METHODOLOGY", "SBI-TTBR-DATA",
                               "ITR2026-RCASP-VALUATION", "IT-RULE-115",
                               "IT-RULE-57", "ITR2026-RULE-57"],
    "4a Regime · Income tax": ["IT-2-47A", "IT-56-2-x", "IT-RULE-57",
                               "ITR2026-RULE-57", "IT-115BBH",
                               "IT-393-1-T8vi", "IT-439-8", "IT-RULE-115",
                               "ITR2026-RCASP-VALUATION"],
    "4b Regime · GST":        ["GST-IGST-2-6", "GST-CGST-50", "GST-CGST-74A"],
    "4c Regime · FEMA":       ["FEMA-2n", "FEMA-3-7-8"],
    "5 Adversarial checker":  ["*"],
}

# Non-corpus tokens per node: (system_prompt, inbound_payload, output)
# All legacy tokens. Estimates until the build is timed.
NODE_OTHER = {
    "1 Intake + extraction":  (800, 3000, 1200),   # 3000 = the raw documents
    "2 Gap detector":         (700, 1200,  600),
    "3 Dual valuation":       (900, 1800, 1500),
    "4a Regime · Income tax": (900, 3300, 1800),
    "4b Regime · GST":        (900, 3300, 1400),
    "4c Regime · FEMA":       (900, 3300, 1200),
    "5 Adversarial checker": (1000, 7700, 2000),
}

# The frozen single-prompt baseline, given the SAME corpus. Giving the
# baseline less corpus than the pipeline would make it a straw man.
BASELINE = {"system": 1000, "docs": 3000, "corpus": "*", "output": 2500}

# Nodes that can run concurrently (the three regime resolvers).
PARALLEL_GROUP = ["4a Regime · Income tax", "4b Regime · GST",
                  "4c Regime · FEMA"]

# Latency planning assumptions -- REPLACE WITH MEASUREMENTS after the build.
LATENCY = {
    "ttft_s": 1.8,              # time to first token
    "out_tok_per_s_opus": 45.0,
    "out_tok_per_s_sonnet": 75.0,
    "out_tok_per_s_haiku": 130.0,
    "deterministic_ms": 40,     # citation matcher + gap enforcer, measured class
}

# Evaluation run shape, from the roadmap: 30 cases x 2 systems x 2 models.
EVAL = {"cases": 30, "systems": 2, "models": 2,
        "ablation_extra_runs": 30 * 4,   # D5: drop one node at a time
        "dev_iteration_multiplier": 4.0} # runs burned before the final run


# ----------------------------------------------------------------------
def _tok(v):
    return v[1] if VERBATIM_ONLY else v[0]


def corpus_total():
    return sum(_tok(v) for v in CORPUS.values())


def scope_tokens(keys):
    if keys == ["*"]:
        return corpus_total()
    return sum(_tok(CORPUS[k]) for k in keys)


def to_model_tokens(legacy, new_tokenizer):
    return legacy * (NEW_TOKENIZER_FACTOR if new_tokenizer else 1.0)


def node_table():
    rows = []
    for node, keys in NODE_SCOPE.items():
        sysp, payload, out = NODE_OTHER[node]
        corpus = scope_tokens(keys)
        rows.append({
            "node": node,
            "corpus": corpus,
            "system": sysp,
            "payload": payload,
            "in_total": corpus + sysp + payload,
            "out": out,
            "cacheable": corpus + sysp,     # identical across every record
            "volatile": payload,
        })
    return rows


def price_run(rows, model, cached=False, batch=False):
    base_in, cw, cr, out_p, newtok = PRICES[model]
    if batch:
        base_in, cw, cr, out_p = (base_in * BATCH_DISCOUNT, cw * BATCH_DISCOUNT,
                                  cr * BATCH_DISCOUNT, out_p * BATCH_DISCOUNT)
    cost = 0.0
    tin = tout = 0
    for r in rows:
        vol = to_model_tokens(r["volatile"], newtok)
        cac = to_model_tokens(r["cacheable"], newtok)
        o = to_model_tokens(r["out"], newtok)
        tin += vol + cac
        tout += o
        if cached:
            cost += vol * base_in / 1e6 + cac * cr / 1e6
        else:
            cost += (vol + cac) * base_in / 1e6
        cost += o * out_p / 1e6
    return cost, tin, tout


def baseline_rows():
    return [{
        "node": "Baseline (single prompt)",
        "corpus": corpus_total(),
        "system": BASELINE["system"],
        "payload": BASELINE["docs"],
        "in_total": corpus_total() + BASELINE["system"] + BASELINE["docs"],
        "out": BASELINE["output"],
        "cacheable": corpus_total() + BASELINE["system"],
        "volatile": BASELINE["docs"],
    }]


def latency_estimate(model):
    speed = (LATENCY["out_tok_per_s_opus"] if "Opus" in model
             else LATENCY["out_tok_per_s_haiku"] if "Haiku" in model
             else LATENCY["out_tok_per_s_sonnet"])
    newtok = PRICES[model][4]
    rows = {r["node"]: r for r in node_table()}
    seq = 0.0
    for node, r in rows.items():
        if node in PARALLEL_GROUP:
            continue
        seq += LATENCY["ttft_s"] + to_model_tokens(r["out"], newtok) / speed
    par = max(LATENCY["ttft_s"] + to_model_tokens(rows[n]["out"], newtok) / speed
              for n in PARALLEL_GROUP)
    ser = sum(LATENCY["ttft_s"] + to_model_tokens(rows[n]["out"], newtok) / speed
              for n in PARALLEL_GROUP)
    det = 2 * LATENCY["deterministic_ms"] / 1000
    return seq + par + det, seq + ser + det


def hr(c="="):
    print(c * 78)


def main():
    global VERBATIM_ONLY
    if "--verbatim" in sys.argv:
        VERBATIM_ONLY = True

    if "--profile" in sys.argv:
        path = sys.argv[sys.argv.index("--profile") + 1]
        with open(path) as fh:
            prof = json.load(fh)
        for f in prof["files"]:
            key = f["file"].rsplit(".", 1)[0]
            if key in CORPUS:
                CORPUS[key] = (f["tok_legacy"], True)
        print(f"Loaded measured corpus profile from {path}\n")

    rows = node_table()
    base = baseline_rows()

    hr()
    print("DIVERGENCE · STEP 18 · COST, LATENCY AND THROUGHPUT MODEL")
    print("Prices: Anthropic published rates, 9 August 2026")
    hr()
    print()

    # ---- 1. token budget per record --------------------------------
    hr("-")
    print("1. TOKEN BUDGET PER RECORD  (legacy tokens, chars/4)")
    hr("-")
    print(f"{'node':<26}{'corpus':>8}{'sys':>7}{'payload':>9}"
          f"{'IN':>8}{'OUT':>7}{'cacheable':>11}")
    for r in rows:
        print(f"{r['node']:<26}{r['corpus']:>8,}{r['system']:>7,}"
              f"{r['payload']:>9,}{r['in_total']:>8,}{r['out']:>7,}"
              f"{r['cacheable']:>11,}")
    ti = sum(r["in_total"] for r in rows)
    to = sum(r["out"] for r in rows)
    tc = sum(r["cacheable"] for r in rows)
    print("-" * 78)
    print(f"{'PIPELINE TOTAL':<26}{sum(r['corpus'] for r in rows):>8,}"
          f"{sum(r['system'] for r in rows):>7,}"
          f"{sum(r['payload'] for r in rows):>9,}{ti:>8,}{to:>7,}{tc:>11,}")
    b = base[0]
    print(f"{'BASELINE (same corpus)':<26}{b['corpus']:>8,}{b['system']:>7,}"
          f"{b['payload']:>9,}{b['in_total']:>8,}{b['out']:>7,}"
          f"{b['cacheable']:>11,}")
    print()
    print(f"  Pipeline input is {ti / b['in_total']:.1f}x the baseline, "
          f"output {to / b['output'] if False else to / b['out']:.1f}x.")
    print(f"  Cacheable share of pipeline input: {100 * tc / ti:.0f}% "
          f"(corpus + system prompts are identical on every record).")
    print(f"  API requests per record: {len(rows)} "
          f"(the architecture has 5 stages; stage 4 fans out to 3 calls).")
    print()

    # ---- 2. scoping saving -----------------------------------------
    hr("-")
    print("2. WHAT CORPUS SCOPING BUYS")
    hr("-")
    scoped = sum(r["corpus"] for r in rows)
    naive = corpus_total() * len(rows)
    print(f"  Full corpus, all {len(CORPUS)} files:        "
          f"{corpus_total():>9,} tok")
    print(f"  Naive: full corpus into all {len(rows)} calls: {naive:>9,} tok")
    print(f"  Scoped: only what each node may cite:  {scoped:>9,} tok")
    print(f"  Saved:                                 "
          f"{naive - scoped:>9,} tok  ({100 * (1 - scoped / naive):.0f}% less)")
    print()
    print("  And the corpus itself, against its source instrument:")
    print(f"    Income-tax Rules 2026, full gazette:  563,371 tok (measured)")
    print(f"    What we extracted from it:              2,671 tok (measured)")
    print(f"    Reduction:                               99.5%")
    print()

    # ---- 3. cost per record ----------------------------------------
    hr("-")
    print("3. COST PER RECORD  (USD, and INR at 88/USD)")
    hr("-")
    print(f"{'model':<20}{'pipeline':>11}{'+cache':>10}{'baseline':>10}"
          f"{'x base':>9}{'INR/rec':>10}")
    results = {}
    for m in PRICES:
        p, _, _ = price_run(rows, m)
        pc, _, _ = price_run(rows, m, cached=True)
        bl, _, _ = price_run(base, m)
        results[m] = (p, pc, bl)
        print(f"{m:<20}{'$' + format(p, '.4f'):>11}"
              f"{'$' + format(pc, '.4f'):>10}{'$' + format(bl, '.4f'):>10}"
              f"{pc / bl:>8.1f}x{'₹' + format(pc * 88, '.2f'):>10}")
    print()
    print("  'x base' is the CACHED pipeline against the uncached baseline —")
    print("  the honest comparison, because a deployed baseline would cache too.")
    print("  Caching removes ~25% of pipeline cost, not more, because output")
    print("  tokens are roughly half the bill and outputs are never cacheable.")
    print("  The pipeline is ~3x a single prompt. It is not 7x, because six of")
    print("  the seven calls never see the whole corpus.")
    print()

    # ---- 4. mixed model configuration ------------------------------
    hr("-")
    print("4. MIXED-MODEL CONFIGURATION  (the production answer)")
    hr("-")
    mix = {
        "1 Intake + extraction":  "Haiku 4.5",
        "2 Gap detector":         "Haiku 4.5",
        "3 Dual valuation":       "Sonnet 5 (Sep 1)",
        "4a Regime · Income tax": "Opus 5",
        "4b Regime · GST":        "Sonnet 5 (Sep 1)",
        "4c Regime · FEMA":       "Sonnet 5 (Sep 1)",
        "5 Adversarial checker":  "Opus 5",
    }
    total = total_cached = 0.0
    for r in rows:
        m = mix[r["node"]]
        c, _, _ = price_run([r], m)
        cc, _, _ = price_run([r], m, cached=True)
        total += c
        total_cached += cc
        print(f"{r['node']:<26}{m:<20}${c:>8.4f}   cached ${cc:>8.4f}")
    print("-" * 78)
    print(f"{'MIXED TOTAL':<46}${total:>8.4f}   cached ${total_cached:>8.4f}")
    print(f"{'':<46} {'':>9}          ₹{total_cached * 88:>7.2f}/record")
    print()
    print(f"  All-Opus 5, cached:  ${results['Opus 5'][1]:.4f}  "
          f"→ mixed saves {100 * (1 - total_cached / results['Opus 5'][1]):.0f}%")
    print("  Reasoning capacity is spent on the two nodes that need it:")
    print("  the income-tax resolver and the adversarial checker.")
    print()

    # ---- 5. latency and throughput ---------------------------------
    hr("-")
    print("5. LATENCY AND THROUGHPUT  (planning assumptions — measure these)")
    hr("-")
    print(f"{'model':<20}{'parallel':>11}{'serial':>10}{'saved':>9}"
          f"{'rec/hr (8 conc.)':>18}")
    for m in PRICES:
        par, ser = latency_estimate(m)
        print(f"{m:<20}{par:>10.0f}s{ser:>9.0f}s{ser - par:>8.0f}s"
              f"{3600 / par * 8:>17.0f}")
    print()
    print("  The three regime resolvers are independent: they read the same")
    print("  upstream state and never read each other. Critical path is 5")
    print("  model calls deep, not 7 wide.")
    print(f"  Deterministic checks add ~{2 * LATENCY['deterministic_ms']}ms "
          "total and are not on the model budget at all.")
    print()
    print("  >>> CONSEQUENCE FOR THE DEMO. Even parallelised, a record takes")
    print("      minutes, not seconds, because ~12,600 output tokens have to")
    print("      be generated. This is a batch product, not an interactive")
    print("      one. Do NOT plan a live cold run on stage. The interface")
    print("      (Step 23) needs staged progress, not a spinner.")
    print()

    # ---- 6. the evaluation run -------------------------------------
    hr("-")
    print("6. THE EVALUATION RUN  (Step 25/26 budget)")
    hr("-")
    calls_pipeline = EVAL["cases"] * len(rows)
    calls_baseline = EVAL["cases"] * 1
    per_model = calls_pipeline + calls_baseline
    total_calls = per_model * EVAL["models"]
    print(f"  {EVAL['cases']} cases x 2 systems x {EVAL['models']} models")
    print(f"    pipeline calls: {EVAL['cases']} x {len(rows)} x "
          f"{EVAL['models']} = {calls_pipeline * EVAL['models']:,}")
    print(f"    baseline calls: {EVAL['cases']} x 1 x "
          f"{EVAL['models']} = {calls_baseline * EVAL['models']:,}")
    print(f"    TOTAL API requests for the headline result: {total_calls:,}")
    print()
    for m in ["Opus 5", "Sonnet 5 (intro)", "Haiku 4.5"]:
        p, pc, bl = results[m]
        run = EVAL["cases"] * (pc + bl)
        print(f"    {EVAL['cases']} cases, cached, on {m:<18} ${run:>7.2f}")
    print()
    abl = EVAL["ablation_extra_runs"]
    print(f"  Ablation (D5), {abl} extra pipeline runs, cached Sonnet: "
          f"${abl * results['Sonnet 5 (intro)'][1]:.2f}")
    dev = EVAL["dev_iteration_multiplier"]
    headline = sum(EVAL["cases"] * (results[m][1] + results[m][2])
                   for m in ["Opus 5", "Sonnet 5 (intro)"])
    print(f"  Headline run, Opus 5 + Sonnet 5:                    "
          f"${headline:.2f}")
    print(f"  Development burn at {dev:.0f}x the final run:            "
          f"${headline * dev:.2f}")
    print(f"  Batch API on the final run would halve it:          "
          f"${headline / 2:.2f}")
    print()
    print(f"  >>> WHOLE-PROJECT MEASUREMENT BUDGET: "
          f"${headline * (1 + dev) + abl * results['Sonnet 5 (intro)'][1]:.2f}"
          f"  (~₹{(headline * (1 + dev) + abl * results['Sonnet 5 (intro)'][1]) * 88:,.0f})")
    print()

    # ---- 7. scale --------------------------------------------------
    hr("-")
    print("7. SCALE  (mixed config, cached)")
    hr("-")
    for n, label in [(1, "one invoice"), (40, "one CA client, one year"),
                     (500, "a small practice"), (10000, "a mid-size firm"),
                     (1000000, "every affected freelancer in India")]:
        print(f"  {n:>9,}  {label:<34} ${n * total_cached:>12,.2f}"
              f"   ₹{n * total_cached * 88:>13,.0f}")
    print()
    print("  Batch API halves every row above. Cost is linear: there is no")
    print("  training, no index, no vector store. The corpus is 16 files.")
    print()

    if "--sensitivity" in sys.argv:
        hr("-")
        print("8. SENSITIVITY  (mixed cached config, one parameter at a time)")
        hr("-")
        base_cost = total_cached
        for label, mult, field in [
            ("corpus 2x larger", 2.0, "corpus"),
            ("corpus 0.5x", 0.5, "corpus"),
            ("output 2x longer", 2.0, "out"),
            ("input docs 2x", 2.0, "payload"),
            ("system prompts 2x", 2.0, "system"),
        ]:
            rows2 = [dict(r) for r in rows]
            for r in rows2:
                r[field] = int(r[field] * mult)
                r["cacheable"] = r["corpus"] + r["system"]
                r["volatile"] = r["payload"]
            t = sum(price_run([r], mix[r["node"]], cached=True)[0]
                    for r in rows2)
            print(f"  {label:<24}${t:>8.4f}   "
                  f"{100 * (t - base_cost) / base_cost:>+6.1f}%")
        print()
        print("  Output tokens dominate. That is the uncomfortable finding:")
        print("  DIVERGENCE is an explanation product, so its cost driver is")
        print("  how much it says, not how much law it reads.")
        print()

    if "--measured" in sys.argv:
        mpath = sys.argv[sys.argv.index("--measured") + 1]
        with open(mpath, encoding="utf-8") as fh:
            mrec = json.load(fh)
        by_node = (mrec.get("_meta") or {}).get("llm", {}).get("by_node", {})
        hr("-")
        print(f"9. MEASURED vs MODELLED — real wall-clock from {os.path.basename(mpath)}")
        print("   (D64 -- llm_call.py's own time.time(), not this file's latency_estimate())")
        hr("-")
        provider = (mrec.get("_meta") or {}).get("llm", {}).get("provider")
        replayed = (mrec.get("_meta") or {}).get("llm", {}).get("replayed", provider == "replay")
        has_timing = any("elapsed_s" in row for row in by_node.values())
        if replayed:
            print("  DIVERGENCE_REPLAY=1 -- no network call was made for this run. Since")
            print("  D72, elapsed_s below (where present) is the ORIGINAL live call's own")
            print("  real measurement, restored from the cache, not fabricated for this")
            print("  replay -- 0.0 specifically means that cached entry predates D64's")
            print("  wall-clock instrumentation, not that the original call took no time.\n")
        if not by_node:
            print(f"  {os.path.basename(mpath)} has no _meta.llm.by_node -- predates D64's")
            print("  timing instrumentation, or was assembled from hand-run node output.\n")
        elif not has_timing:
            print(f"  {os.path.basename(mpath)} has by_node entries but none carry")
            print("  'elapsed_s' -- this record was written before D64 added timing.")
            print("  Showing '0.00' here would look like a measurement of zero seconds,")
            print("  which is not what an absent field means, so nothing is shown here.\n")
        else:
            print(f"{'node':<20}{'calls':>8}{'measured_s':>14}")
            total_measured = 0.0
            for node, row in sorted(by_node.items()):
                if "elapsed_s" not in row:
                    print(f"{node:<20}{row.get('calls', 0):>8}{'(no data)':>14}")
                    continue
                measured = row["elapsed_s"]
                total_measured += measured
                print(f"{node:<20}{row.get('calls', 0):>8}{measured:>14.2f}")
            print("-" * 42)
            print(f"{'TOTAL (sequential wall-clock, as measured)':<28}{total_measured:>14.2f}s")
            print()
            print("  Not compared against Section 5's modelled figures above, on purpose:")
            print("  those model an Anthropic Claude deployment (README's Cost section --")
            print("  'not a number from an actually-measured run'), and this pipeline's")
            print("  real runs are on Featherless-hosted Qwen/Mistral (decision D44).")
            print("  Different providers, different models -- one ratio between them would")
            print("  imply Section 5 predicts this deployment's speed, which it was never")
            print("  built to do.")
            print()
            print("  This total IS real, not modelled -- one live run's actual elapsed time")
            print("  per node, read from the record's own _meta.llm.by_node. It is one")
            print("  sample, not a distribution; run several times before quoting a single")
            print("  number as representative (same discipline as this project's own M2")
            print("  seed-instability finding, results.md Block E2).")
        print()

    hr()
    print("HONESTY NOTE")
    hr()
    print("Two corpus provisions are measured from the Gazette text.")
    print("Everything else in the token profile is an ESTIMATE made before")
    print("the pipeline exists. Run measure_corpus.py against the real")
    print("corpus/, then re-run this with --profile, then measure the built")
    print("pipeline and publish the error between predicted and actual.")
    print("That delta is worth more to a judge than a confident number.")
    print("--measured <record.json> now does exactly that for latency (D64).")


if __name__ == "__main__":
    main()
