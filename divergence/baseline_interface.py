#!/usr/bin/env python3
"""
BASELINE INTERFACE  --  DIVERGENCE, D74
The single-number control condition for the human-subjects study
(divergence/study/PROTOCOL.md). Same record, same CSS, same header --
the only manipulated variable against output-interface.html is whether
uncertainty is disclosed at all. What this file OMITS on purpose: the
valuation lattice, the uncertainty-budget decomposition, the election
control, sections 00/01/03/04/05 (input integrity, what's missing, what
this triggers, what we checked, what we tried to break) -- everything
except the one number a naive "point estimate" tool would show.

THE SINGLE FIGURE IS THE MEDIAN of the record's own real valuation
lattice, not an arbitrarily-picked method and not methods[0] (which,
checked against D1's real data, sits near the LOW end of the range --
using it here would have quietly biased the control condition toward
under-statement). The median is a standard central-tendency choice in
the uncertainty-visualization literature this study's own protocol cites
(Fernandes et al., CHI 2018) and is disclosed, in the page's own small
print, as computed -- not presented as if sourced from one specific
quote, because it is not. For a record with no real dispute (one
method, zero spread -- C1, C2), the median is that one real figure,
unchanged.

    python baseline_interface.py --record runs/21aug/D1_final_seed2.json
    python baseline_interface.py --record runs/21aug/C5_pipeline.json --out c5-baseline.html
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import node7_disclosure as nd  # noqa: E402 -- reuses CSS/esc/fmt_* so the only
# variable between this page and output-interface.html is what's disclosed,
# never a font, a colour, or a spacing rule drifting independently between them.

DEFAULT_OUT = os.path.join(HERE, "baseline-interface.html")


def median_inr(methods):
    """Same definition as llm_call._median() (D73) -- standard median,
    even-length lists average the two middle values. Duplicated rather
    than imported: llm_call.py is the pipeline's own model-call surface,
    reaching into it from a static-HTML generator for one small function
    would be a stranger coupling than repeating four lines."""
    values = sorted(m["inr_value"] for m in methods)
    n = len(values)
    mid = n // 2
    if n % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2.0


def compose(record):
    facts = record.get("facts", {})
    record_id = record.get("record_id", "?")
    tax_year = record.get("tax_year", "?")
    amount = nd.fact(facts, "amount")
    asset = nd.fact(facts, "asset")
    settle = nd.fact(facts, "settlement_datetime_ist", record.get("generated_at", ""))
    invoice_no = nd.fact(facts, "invoice_no", record_id)
    counterparty = nd.fact(facts, "counterparty_declared", "not stated")

    methods = (record.get("valuation") or {}).get("methods") or []
    if not methods:
        figure_html = (
            '<p class="lede">No valuation lattice was computed for this record '
            '(no crypto/FX leg, or node 3 was not run).</p>'
        )
    else:
        # D74: this small print is participant-facing -- kept neutral, the
        # way a real single-figure tool's own caption would read, on
        # purpose. It does NOT explain that the number is a median or
        # name this as a study condition (either would leak the
        # manipulation and change participant behaviour, exactly the
        # demand-characteristic risk a control condition exists to avoid).
        # The real, precise derivation (median of the lattice, and why
        # median rather than methods[0]) is disclosed instead in
        # study/PROTOCOL.md, for the researcher's own audit trail.
        figure = median_inr(methods)
        figure_html = (
            f'<div class="one-answer"><span class="label">Payable value</span>'
            f'<span class="amt">{nd.fmt_inr(figure)}</span>'
            f'<small style="display:block;margin-top:6px;color:var(--ink-soft);font-size:14px">'
            f'Based on available market and bank rate data for this transaction.</small></div>'
        )

    title = f"Payment received {nd.esc(nd.fmt_datetime(settle))}"
    subtitle = (f"{nd.esc(nd.fmt_amount(amount, asset))} · Invoice {nd.esc(invoice_no)} "
                f"· Counterparty declared as {nd.esc(counterparty)}")

    body = f"""
<main class="sheet">
  <header>
    <div class="formno">
      <span class="label">Disclosure record · {nd.esc(record_id)}</span>
      <span class="label">Corpus frozen {nd.esc((record.get('corpus_frozen_at') or '?')[:10])} · Tax year {nd.esc(tax_year)}</span>
    </div>
    <h1>{title}</h1>
    <p class="sub">{subtitle}</p>
  </header>
  <hr class="rule">

  <section aria-labelledby="s2">
    <div class="sec-head"><h2 id="s2">What it was worth in rupees</h2></div>
    {figure_html}
  </section>
</main>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Disclosure record (baseline) — {nd.esc(invoice_no)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{nd.CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="Baseline (single-number) disclosure page -- study control condition")
    ap.add_argument("--record", required=True, help="path to a run_pipeline.py output record")
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()

    record = json.load(open(a.record, encoding="utf-8"))
    page = compose(record)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"  wrote {a.out} from {a.record}")
    n = len((record.get("valuation") or {}).get("methods") or [])
    if n:
        print(f"  single figure: {nd.fmt_inr(median_inr(record['valuation']['methods']))} "
              f"(median of {n} method(s))")


if __name__ == "__main__":
    main()
