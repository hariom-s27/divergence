#!/usr/bin/env python3
"""
NODE 3 — VALUATION LATTICE  ·  DIVERGENCE
DETERMINISTIC. No model. No API. No network.

Enumerates every defensible INR figure for the receipt by crossing the
undetermined choices, computes the range, and decomposes the spread by
source.

    python node3_valuation.py                        # canonical_case.json (D1)
    python node3_valuation.py --case c5_case.json --out runs/valuation_C5.json
    python node3_valuation.py --units 5000
    python node3_valuation.py --json                  # machine output only

Block E (D51): was hardcoded to canonical_case.json (D1) only -- D47 named
this as a real gap, every non-D1 record's valuation block silently being
D1's. --case fixes it for cases whose facts are actually reachable from
data already on disk. C5 (USD, same 28-June-2026 weekend as D1) needed no
new rate data -- see c5_case.json. C1/C2 have no valuation dispute at all
(a determinate case, not a gap -- see D51) and are not run through this
node.

Reads   the file named by --case (default canonical_case.json)
Writes  the file named by --out (default valuation.json), conforms to
        schema.json -> properties.valuation

WHY THIS IS NOT A MODEL CALL
  The headline number must never be a token prediction. Everything below is
  arithmetic over retrieved inputs, and every input carries its source.

CANDLE/PEG ARE OPTIONAL, ON PURPOSE
  A case with a crypto leg (D1, C3, C4) carries "candle" (a CoinDCX daily
  candle) and "peg" (USDC/USDT at settlement) -- the market leg crosses
  five market readings by two proxy choices. A plain fiat wire with an
  undetermined settlement date but no crypto leg (C5) has neither: only
  the official SBI-TTBR-by-date axis applies. Forcing every case through
  the market leg would either crash (no candle to read) or fabricate a
  proxy question fiat was never asked. Missing candle/peg means "this case
  has no market leg", not "this case is broken."
"""

import json, os, sys, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, "canonical_case.json")
DEFAULT_OUT = os.path.join(HERE, "valuation.json")

# ── the block the script needs, if canonical_case.json does not carry it yet ──
NEEDED = """
  "official_candidates": [
    {
      "date": "2026-06-25",
      "label": "last published BEFORE the receipt",
      "ttbr": 94.00,
      "sheet_datetime": "2026-06-25 11:42",
      "source": "SBI Forex Card Rates sheet, USD/INR TT BUY",
      "file": "2026062614_15.pdf",
      "retrieved": "2026-08-12",
      "note": "Captured from SBI at 14:15 on 26 Jun; the sheet served was still dated 25-06-2026, i.e. no rate had been published for the 26th."
    },
    {
      "date": "2026-06-29",
      "label": "next published AFTER the receipt",
      "ttbr": 93.95,
      "sheet_datetime": "2026-06-29 09:09",
      "source": "SBI Forex Card Rates sheet, USD/INR TT BUY",
      "file": "2026062919_15.pdf",
      "retrieved": "2026-08-12"
    }
  ],
"""


def die(msg, extra=""):
    print("\n  ERROR: " + msg)
    if extra:
        print(extra)
    sys.exit(1)


def load(src):
    if not os.path.exists(src):
        die(f"{src} not found. Run canonical_case.py first.")
    with open(src, encoding="utf-8") as f:
        d = json.load(f)

    if "official_candidates" not in d:
        die(
            f"{os.path.basename(src)} has no 'official_candidates'.\n"
            "  It currently carries a single 'official_leg_sbi_ttbr', which cannot\n"
            "  express the date choice — and the date choice is one of the "
            "undetermined elements this node exists to enumerate.",
            f"\n  Paste this into {os.path.basename(src)} (values read from the SBI "
            "sheets on disk — no number typed from memory):\n" + NEEDED,
        )

    # candle/peg are the market (crypto) leg -- OPTIONAL, see module
    # docstring. Present together or absent together; a case carrying one
    # but not the other is a real authoring error, not a legitimate shape.
    has_candle = "candle" in d
    has_peg = "peg" in d
    if has_candle != has_peg:
        die(f"{os.path.basename(src)} has 'candle' xor 'peg' -- a case with a "
            "market leg needs both, a case without one needs neither.")
    if has_candle:
        c = d["candle"]
        for k in ("open", "high", "low", "close"):
            if k not in c:
                die(f"{os.path.basename(src)} candle is missing '{k}'")
    return d, has_candle


def market_prices(c):
    """The four printed values, plus the typical price.

    A daily candle is not a price. It is a range with several defensible
    readings. True VWAP needs intraday prints we do not hold, so the fifth
    reading is the typical price (H+L+C)/3 — a standard proxy — and it is
    labelled 'derived' so nobody mistakes it for an observed print.
    """
    typ = (c["high"] + c["low"] + c["close"]) / 3.0
    return [
        ("open",    c["open"],  "L1", "primary_live", "opening print of the daily candle"),
        ("high",    c["high"],  "L1", "primary_live", "highest print of the day"),
        ("low",     c["low"],   "L1", "primary_live", "lowest print of the day"),
        ("close",   c["close"], "L1", "primary_live", "closing print of the daily candle"),
        ("typical", typ,        "L2", "derived",      "(H+L+C)/3 — proxy for VWAP, which a daily candle does not carry"),
    ]


def proxies(d):
    peg = float(d["peg"])
    return [
        ("retrieved peg", peg,  "L2", "primary_live",
         d.get("proxy_note") or "USDC/USDT at settlement"),
        ("assumed par",   1.0,  "L3", "derived",
         "USDC treated as exactly one dollar — what a stablecoin is designed to be, and what most workflows assume"),
    ]


def build(d, units, has_candle):
    officials = d["official_candidates"]
    mkts = market_prices(d["candle"]) if has_candle else []
    pxs = proxies(d) if has_candle else []
    pair = d.get("coindcx_pair", "?")

    methods = []

    # ── the official leg: one method per published date ──────────────────
    # Independent of the market reading. Crossing them would double-count.
    for off in officials:
        methods.append({
            "label": f"SBI TTBR {off['date']} ({off['label']})",
            "rate": round(float(off["ttbr"]), 6),
            "inr_value": round(float(off["ttbr"]) * units, 2),
            "observability": "L2",
            "source": {
                "name": off["source"], "url": off.get("file"),
                "retrieved": off.get("retrieved", "unknown"),
                "tier": "primary_archived", "note": off.get("note", ""),
            },
            "mandated_by": None,
            "date_used": off["date"],
            "date_choice": {
                "reason": "The receipt settled on a Sunday. The SBI telegraphic transfer buying rate "
                          "was not published on that date. Rule 206 provides no fallback; Rule 207(1) "
                          "does, for payments out — and Rule 206 borrows its definition from Rule 207 "
                          "without borrowing that sentence.",
                "candidates": [{"date": o["date"], "ttbr": o["ttbr"], "label": o["label"]}
                               for o in officials],
                "chosen": None,
                "prescribed_by": None,
                "difference_inr": round(abs(officials[0]["ttbr"] - officials[-1]["ttbr"]) * units, 2),
            },
        })

    # ── the market leg: reading x proxy ──────────────────────────────────
    for mname, mrate, mobs, mtier, mnote in mkts:
        for pname, pval, pobs, ptier, pnote in pxs:
            rate = mrate * pval
            methods.append({
                "label": f"domestic market, {mname} x {pname}",
                "rate": round(rate, 6),
                "inr_value": round(rate * units, 2),
                "observability": max(mobs, pobs),
                "source": {
                    "name": f"CoinDCX {pair} daily candle ({mname}); peg: {pname}",
                    "retrieved": (d.get("computed_at") or "")[:10] or "unknown",
                    "tier": mtier if mtier == ptier else "derived",
                    "note": f"{mnote}; {pnote}",
                },
                "mandated_by": None,
                "date_used": d.get("receipt_date"),
            })

    return methods, officials, mkts, pxs


def budget(d, officials, mkts, pxs, units, has_candle):
    """Decompose the spread by contributing source. Metrology, not hand-waving."""
    lo_off = min(o["ttbr"] for o in officials)
    hi_off = max(o["ttbr"] for o in officials)

    lines = [
        {"source": "which official date",
         "inr": round((hi_off - lo_off) * units, 2),
         "explanation": f"No rate was published on the settlement date. Stepping back to {officials[0]['date']} "
                        f"or forward to {officials[-1]['date']} is undetermined — Rule 206 does not say which."},
    ]
    if not has_candle:
        return lines

    c = d["candle"]; peg = float(d["peg"])
    mid_mkt = c["close"]
    lines.extend([
        {"source": "domestic premium",
         "inr": round((mid_mkt * peg - hi_off) * units, 2),
         "explanation": "The Indian market price of the token against the official rupee rate for a dollar. "
                        "This is the bulk of the gap and it is the part everyone argues about."},
        {"source": "which price within the day",
         "inr": round((c["high"] - c["low"]) * peg * units, 2),
         "explanation": "A daily candle is not a price. It is a range with four printed readings and no rule "
                        "choosing between them."},
        {"source": "the proxy",
         "inr": round(abs(peg - 1.0) * mid_mkt * units, 2),
         "explanation": "The retrieved pair is USDT/INR. The receipt was USDC. The figure is "
                        "USDT/INR x USDC/USDT, and treating the peg as exactly 1.0000 is a further choice."},
    ])
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=DEFAULT_SRC,
                     help="case JSON to read (default: canonical_case.json, D1)")
    ap.add_argument("--out", default=None,
                     help="where to write the valuation (default: valuation.json "
                          "if --case was not given, else <case-stem>_valuation.json)")
    ap.add_argument("--units", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    out_path = a.out
    if out_path is None:
        out_path = DEFAULT_OUT if a.case == DEFAULT_SRC else (
            os.path.splitext(os.path.basename(a.case))[0] + "_valuation.json")

    d, has_candle = load(a.case)
    units = a.units if a.units else float(d.get("invoice_units") or 0)
    if not units:
        die(f"no invoice_units in {a.case} and no --units given")

    methods, officials, mkts, pxs = build(d, units, has_candle)
    vals = [m["inr_value"] for m in methods]
    lo_m = min(methods, key=lambda m: m["inr_value"])
    hi_m = max(methods, key=lambda m: m["inr_value"])
    spread = hi_m["inr_value"] - lo_m["inr_value"]

    valuation = {
        "methods": methods,
        "spread": {
            "inr": round(spread, 2),
            "percent": round(spread / lo_m["inr_value"] * 100, 4),
            "between": [lo_m["label"], hi_m["label"]],
        },
        "uncertainty_budget": budget(d, officials, mkts, pxs, units, has_candle),
        "no_rate_published": True,
    }

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "invoice_units": units,
            "receipt_date": d.get("receipt_date"),
            "weekday": d.get("weekday"),
            "valuation": valuation,
        }, f, indent=2)

    if a.json:
        print(json.dumps(valuation, indent=2)); return

    # ── human output ──
    W = 78
    print("\n" + "=" * W)
    print(f"  VALUATION LATTICE — {units:,.0f} units received {d.get('receipt_date')} ({d.get('weekday')})")
    print("=" * W)
    print(f"  {len(officials)} official dates  +  {len(mkts)} market readings x {len(pxs)} proxies")
    print(f"  {len(methods)} defensible figures. No rule chooses between them.\n")

    print(f"  {'INR value':>14}   {'rate':>9}  {'obs':<4} method")
    print("  " + "-" * (W - 4))
    for m in sorted(methods, key=lambda x: x["inr_value"]):
        mark = " <-- lowest" if m is lo_m else (" <-- highest" if m is hi_m else "")
        print(f"  {m['inr_value']:>14,.2f}   {m['rate']:>9.4f}  {m['observability']:<4} {m['label']}{mark}")

    print("\n" + "=" * W)
    print(f"  RANGE   Rs {lo_m['inr_value']:,.2f}  to  Rs {hi_m['inr_value']:,.2f}")
    print(f"  SPREAD  Rs {spread:,.2f}   ({valuation['spread']['percent']:.4f}%)")
    print("=" * W)

    print("\n  UNCERTAINTY BUDGET — where the gap comes from\n")
    for b in sorted(valuation["uncertainty_budget"], key=lambda x: -abs(x["inr"])):
        print(f"    Rs {b['inr']:>12,.2f}   {b['source']}")
        print(f"    {'':>15}  {b['explanation'][:96]}")
    print()
    print("  What would settle this: a prescribed valuation source and timestamp")
    print("  convention for virtual digital assets received by a resident.\n")
    print(f"  written -> {os.path.relpath(out_path, HERE)}")
    print("  Every figure above is arithmetic over retrieved inputs. No model was called.\n")


if __name__ == "__main__":
    main()
