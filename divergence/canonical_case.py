#!/usr/bin/env python3
"""
canonical_case.py  --  DIVERGENCE
Reads ./cache/ (written by killgate.py) and the verified SBI rate sheets,
and writes canonical_case.json -- the RAW RETRIEVED INPUTS for this case.

    python canonical_case.py --units 5000

This script does not compute a headline number. node3_valuation.py reads
canonical_case.json and expands it into the full 12-method lattice
(valuation.json) -- that lattice, not a single spread/total pair, is the
authoritative answer. Earlier versions of this script wrote a single
"spread_pct" / "total_market" straight into the JSON, computed from one
silently-chosen candle field and one silently-chosen official date. That
was itself an instance of F1 (silent rate selection) -- the exact failure
this project exists to catch -- so those fields were removed 2026-08-19.

WHY THIS EXISTS
---------------
Three different percentages (8.5%, 9.27%, 9.394%) and three different rupee   # stale-ok
bases appeared across our own documents. A reviewer found it with a
calculator in under a minute. Numbers that are retyped drift. Numbers that
are computed once and read from a file do not.

RULE: no artifact -- corpus, README, slides, video, disclosure output --
      may contain a headline number that was typed by a human. Every one
      of them reads from valuation.json, produced from this file.

THE PROXY PROBLEM
-----------------
killgate.py probes CoinDCX pairs in this order:
    I-USDT_INR, B-USDT_INR, USDTINR, I-USDC_INR, I-BTC_INR
and takes the FIRST that returns data. So unless the three USDT pairs all
failed, the Indian leg is USDT/INR, and USDC/INR is reached by multiplying
through the Binance USDC/USDT peg.

That is a proxy. Our case asset is USDC. Valuing a USDC receipt with a USDT
price is a silent substitution -- exactly the failure this project exists
to catch. This script refuses to hide it: it reports which pair was used
and, if a proxy was involved, records the proxy as an additional
undetermined choice belonging in the uncertainty budget.

THE OFFICIAL LEG IS NOT ONE NUMBER
-----------------------------------
No SBI rate is published on a Sunday, and 2026-06-28 (the receipt date) was
one. SBI_OFFICIAL_CANDIDATES below is the retrieved evidence: the sheet
last published before the receipt and the sheet first published after it.
Both are written to canonical_case.json. Neither is chosen here -- which
one applies is exactly the "which official date" slice of
node3_valuation.py's uncertainty budget.

Note the 25th, not the 26th: the sheet was captured at 14:15 on 26 Jun, but
the sheet SBI served was still dated 25-06-2026 -- no rate had been
published for the 26th itself. The filename records the capture time; the
"date" field below records what the sheet actually said.
"""

import json
import os
import sys
from datetime import datetime, timezone

CACHE = "cache"
TARGET = "2026-06-28"          # the receipt date
INVOICE_UNITS = None            # set via --units

SBI_OFFICIAL_CANDIDATES = [
    {
        "date": "2026-06-25",
        "label": "last published BEFORE the receipt",
        "ttbr": 94.00,
        "sheet_datetime": "2026-06-25 11:42",
        "source": "SBI Forex Card Rates sheet, USD/INR TT BUY",
        "file": "2026062614_15.pdf",
        "retrieved": "2026-08-12",
        "note": "Captured from SBI at 14:15 on 26 Jun; the sheet served was "
                "still dated 25-06-2026, i.e. no rate had been published for "
                "the 26th.",
    },
    {
        "date": "2026-06-29",
        "label": "next published AFTER the receipt",
        "ttbr": 93.95,
        "sheet_datetime": "2026-06-29 09:09",
        "source": "SBI Forex Card Rates sheet, USD/INR TT BUY",
        "file": "2026062919_15.pdf",
        "retrieved": "2026-08-12",
    },
]
SBI_OFFICIAL_SOURCE = (
    "VERIFIED: SBI Forex Card Rates, USD/INR TT BUY. 25-06-2026 11:42 = "
    "94.00 (file 2026062614_15.pdf, captured 26 Jun 14:15, sheet still "
    "dated 25-06). 29-06-2026 09:09 = 93.95 (file 2026062919_15.pdf)."
)


def die(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def load(name):
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def find_pair_file():
    """Which CoinDCX pair actually produced the data?"""
    if not os.path.isdir(CACHE):
        die(f"no {CACHE}/ directory -- run killgate.py first")
    for fn in os.listdir(CACHE):
        if fn.startswith("coindcx_") and fn.endswith("_daily.json"):
            pair = fn[len("coindcx_"):-len("_daily.json")]
            return pair, fn
    return None, None


def candle_for(rows, date_str):
    for c in rows:
        if not isinstance(c, dict) or "time" not in c:
            continue
        t = datetime.fromtimestamp(c["time"] / 1000, tz=timezone.utc)
        if t.date().isoformat() == date_str:
            return c, t
    return None, None


def main():
    global INVOICE_UNITS

    for i, a in enumerate(sys.argv):
        if a == "--units":
            INVOICE_UNITS = float(sys.argv[i + 1])

    pair, fn = find_pair_file()
    if not pair:
        die("no coindcx_*_daily.json in cache/ -- run killgate.py first")

    rows = load(fn)
    candle, ts = candle_for(rows, TARGET)
    if not candle:
        die(f"no candle for {TARGET} in {fn}")

    print("=" * 74)
    print("DIVERGENCE  ·  CANONICAL CASE  ·  raw retrieved inputs")
    print("=" * 74)
    print(f"  Receipt date          {TARGET}  ({ts.strftime('%A')})")
    print(f"  CoinDCX pair used     {pair}")
    print(f"  Candle                open {candle.get('open')}  high {candle.get('high')}"
          f"  low {candle.get('low')}  close {candle.get('close')}")
    print()

    is_proxy = "USDC" not in pair.upper()
    peg = None
    peg_note = "none -- direct USDC/INR print"

    if is_proxy:
        binance = None
        for cache_fn in sorted(os.listdir(CACHE)):
            if "binance" in cache_fn.lower() or "usdc" in cache_fn.lower():
                binance = load(cache_fn)
                if binance:
                    break
        if binance:
            try:
                row = [r for r in binance
                       if datetime.fromtimestamp(r[0] / 1000, tz=timezone.utc)
                       .date().isoformat() == TARGET]
                if row:
                    peg = float(row[0][4])       # close
            except Exception:
                peg = None
        if peg is None:
            print("  !! Binance USDC/USDT peg for the target date not found in")
            print("     cache/. Pass it explicitly or re-run killgate.py.")
            print("     Proceeding with peg = 1.0000 and flagging it.")
            peg = 1.0000
            peg_note = "ASSUMED 1.0000 -- NOT RETRIEVED. Do not ship this."
        else:
            peg_note = f"Binance USDC/USDT close {peg:.4f} on {TARGET}"

    # Illustrative only -- printed for a human sanity-check, never persisted.
    # The candle's "close" is one of four printed readings and is not chosen
    # for you here; node3_valuation.py enumerates all four.
    illustrative_market_leg = float(candle["close"]) * (peg if peg else 1.0)

    print("-" * 74)
    print("  THE OFFICIAL LEG IS UNDETERMINED -- RETRIEVED CANDIDATES")
    print("-" * 74)
    print(f"  Market leg for reference (close, USDC terms)   {illustrative_market_leg:>10.4f}")
    print()
    for c in SBI_OFFICIAL_CANDIDATES:
        sp = illustrative_market_leg - c["ttbr"]
        print(f"  {c['date']}  ({c['label']:<32}) TTBR {c['ttbr']:>8.4f}"
              f"   illustrative spread {sp:>7.4f}  ({sp / c['ttbr'] * 100:>6.4f} %)")
    rates = [c["ttbr"] for c in SBI_OFFICIAL_CANDIDATES]
    if max(rates) != min(rates):
        print()
        print(f"  Choosing between the candidates alone moves the official leg by"
              f" {max(rates) - min(rates):.4f}/unit, before any question of which")
        print("  market price within the day to use.")
    print()

    if INVOICE_UNITS is None:
        print("-" * 74)
        print("  INVOICE SIZE NOT SET.")
        print("-" * 74)
        print("  Pass --units <n>. Pick the number from the actual test case")
        print("  document, not from a rupee figure you are trying to reach.")
        print("  Nothing is written until you do.")
        sys.exit(0)

    out = {
        "receipt_date": TARGET,
        "weekday": ts.strftime("%A"),
        "coindcx_pair": pair,
        "is_proxy": is_proxy,
        "proxy_note": peg_note,
        "candle": candle,
        "peg": round(peg, 4) if peg else None,
        "official_leg_source": SBI_OFFICIAL_SOURCE,
        "official_candidates": SBI_OFFICIAL_CANDIDATES,
        "invoice_units": INVOICE_UNITS,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
    with open("canonical_case.json", "w") as fh:
        json.dump(out, fh, indent=2)

    print("-" * 74)
    print("  Wrote canonical_case.json  (raw inputs only -- no headline number)")
    print("  Run node3_valuation.py for the 12-method lattice and range.")
    print("-" * 74)
    print()
    if is_proxy:
        print("!" * 74)
        print("  PROXY IN USE -- THIS BELONGS IN THE UNCERTAINTY BUDGET")
        print("!" * 74)
        print(f"  The case asset is USDC. The Indian leg retrieved is {pair}.")
        print("  USDC/INR was reached by multiplying through the USDC/USDT peg.")
        print()
        print("  Do NOT switch the case to USDT to make this go away -- CBDT")
        print("  Circular 13/2022 names USDC by name, and that is worth more.")
        print()
        print("  Instead, publish it as a further undetermined choice:")
        print("  USDC is thinly traded on Indian venues, so valuing it requires")
        print("  choosing a proxy, and no instrument prescribes which proxy.")
        print("  That is another instance of the phenomenon, not a weakness.")


if __name__ == "__main__":
    main()
