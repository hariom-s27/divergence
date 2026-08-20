#!/usr/bin/env python3
"""
canonical_case.py  --  DIVERGENCE
The single source of truth for every number in this project.

    python canonical_case.py

Reads ./cache/ (written by killgate.py), recomputes the headline figures
from the raw candles to four decimal places, and writes canonical_case.json.

WHY THIS EXISTS
---------------
Three different percentages (8.5%, 9.27%, 9.394%) and three different rupee
bases appeared across our own documents. A reviewer found it with a
calculator in under a minute. Numbers that are retyped drift. Numbers that
are computed once and read from a file do not.

RULE: no artifact -- corpus, README, slides, video, disclosure output --
      may contain a headline number that was typed by a human. Every one
      of them reads from canonical_case.json.

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
and, if a proxy was involved, prints the proxy as an additional
undetermined choice belonging in the uncertainty budget.
"""

import json
import os
import sys
from datetime import datetime, timezone

CACHE = "cache"
TARGET = "2026-06-28"          # the receipt date
INVOICE_UNITS = None           # set from the case file, or via --units

# The official leg. Replace with the retrieved SBI TT buying rate for the
# specified date, to four decimals, and record where it came from.
SBI_TTBR = None                # e.g. 94.0000  (the leg used for headline %)

# The official leg has NO value on the receipt date, because no official
# rate is published on a Sunday. These are the candidate dates a
# professional could defensibly use. Fill in the retrieved SBI TT buying
# rate for each. Leave a value as None until you have actually retrieved it.
OFFICIAL_CANDIDATES = {
    # "2026-06-26 (Friday, last published before receipt)": None,
    # "2026-06-29 (Monday, first published after receipt)": None,
}
SBI_TTBR_SOURCE = "SET THIS -- SBI card rate sheet, date and retrieval time"


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
    global INVOICE_UNITS, SBI_TTBR

    for i, a in enumerate(sys.argv):
        if a == "--units":
            INVOICE_UNITS = float(sys.argv[i + 1])
        if a == "--ttbr":
            SBI_TTBR = float(sys.argv[i + 1])

    pair, fn = find_pair_file()
    if not pair:
        die("no coindcx_*_daily.json in cache/ -- run killgate.py first")

    rows = load(fn)
    candle, ts = candle_for(rows, TARGET)
    if not candle:
        die(f"no candle for {TARGET} in {fn}")

    print("=" * 74)
    print("DIVERGENCE  ·  CANONICAL CASE")
    print("=" * 74)
    print(f"  Receipt date          {TARGET}  ({ts.strftime('%A')})")
    print(f"  CoinDCX pair used     {pair}")
    print(f"  Candle                open {candle.get('open')}  high {candle.get('high')}"
          f"  low {candle.get('low')}  close {candle.get('close')}")
    print()

    is_proxy = "USDC" not in pair.upper()
    market_leg = float(candle["close"])
    peg = None
    peg_note = "none -- direct USDC/INR print"

    if is_proxy:
        binance = None
        for fn in sorted(os.listdir(CACHE)):
            if "binance" in fn.lower() or "usdc" in fn.lower():
                binance = load(fn)
                if binance:
                    peg_file = fn
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

        market_leg = float(candle["close"]) * peg

    if SBI_TTBR is None:
        print("  !! SBI_TTBR not set. Set it at the top of this file or pass")
        print("     --ttbr <rate>. Nothing below is publishable until you do.")
        SBI_TTBR = 94.0000
        ttbr_note = "PLACEHOLDER 94.0000 -- NOT RETRIEVED"
    else:
        ttbr_note = SBI_TTBR_SOURCE

    # THE OFFICIAL LEG IS NOT ONE NUMBER.
    # No official rate is published on a Sunday. The candidates are the
    # last working day before and the first working day after. Which one
    # applies is the undetermined question -- so both are computed and
    # neither is chosen here.
    candidates = dict(OFFICIAL_CANDIDATES) if OFFICIAL_CANDIDATES else {}
    if not candidates:
        candidates = {"placeholder": SBI_TTBR}

    spread_per_unit = market_leg - SBI_TTBR
    spread_pct = (spread_per_unit / SBI_TTBR) * 100

    print("-" * 74)
    print("  THE TWO LEGS")
    print("-" * 74)
    print(f"  Market leg  (CoinDCX {pair} close)        {float(candle['close']):>12.4f}")
    if is_proxy:
        print(f"  Peg leg     ({peg_note})")
        print(f"  Market leg in USDC terms                 {market_leg:>12.4f}")
    print(f"  Official leg (SBI TT buying rate)        {SBI_TTBR:>12.4f}")
    print(f"      source: {ttbr_note}")
    print()
    print(f"  Spread per unit                          {spread_per_unit:>12.4f}")
    print(f"  Spread as % of official leg              {spread_pct:>12.4f} %")
    print()

    if len(candidates) > 1:
        print("-" * 74)
        print("  THE OFFICIAL LEG IS UNDETERMINED -- CANDIDATES")
        print("-" * 74)
        vals = {k: v for k, v in candidates.items() if v}
        for label, rate in candidates.items():
            if rate is None:
                print(f"  {label:<52} NOT RETRIEVED")
            else:
                sp = market_leg - rate
                print(f"  {label:<52} {rate:>8.4f}"
                      f"   spread {sp:>7.4f}  ({sp / rate * 100:>6.4f} %)")
        if len(vals) > 1:
            lo, hi = min(vals.values()), max(vals.values())
            print()
            print(f"  Choosing between the candidates alone moves the answer by"
                  f" {abs(hi - lo):.4f}/unit")
            print("  before any question about which market price to use.")
        print()

    if INVOICE_UNITS is None:
        print("-" * 74)
        print("  INVOICE SIZE NOT SET.")
        print("-" * 74)
        print("  Pass --units <n>. Pick the number from the actual test case")
        print("  document, not from a rupee figure you are trying to reach.")
        print()
        print("  For reference, at this spread:")
        for n in (1000, 2500, 5000, 10000):
            print(f"    {n:>7,} units  ->  spread  ₹{n * spread_per_unit:>12,.2f}"
                  f"   base ₹{n * SBI_TTBR:>12,.2f}")
        sys.exit(0)

    total_official = INVOICE_UNITS * SBI_TTBR
    total_market = INVOICE_UNITS * market_leg
    total_spread = total_market - total_official

    print("-" * 74)
    print(f"  ON A {INVOICE_UNITS:,.0f} USDC INVOICE")
    print("-" * 74)
    print(f"  Valued at the official leg               ₹{total_official:>14,.2f}")
    print(f"  Valued at the market leg                 ₹{total_market:>14,.2f}")
    print(f"  DIFFERENCE                               ₹{total_spread:>14,.2f}")
    print(f"  DIFFERENCE                                {spread_pct:>14.4f} %")
    print()

    out = {
        "receipt_date": TARGET,
        "weekday": ts.strftime("%A"),
        "coindcx_pair": pair,
        "is_proxy": is_proxy,
        "proxy_note": peg_note,
        "candle": candle,
        "market_leg_raw": round(float(candle["close"]), 4),
        "peg": round(peg, 4) if peg else None,
        "market_leg_usdc_terms": round(market_leg, 4),
        "official_leg_sbi_ttbr": round(SBI_TTBR, 4),
        "official_leg_source": ttbr_note,
        "spread_per_unit": round(spread_per_unit, 4),
        "spread_pct": round(spread_pct, 4),
        "invoice_units": INVOICE_UNITS,
        "total_official": round(total_official, 2),
        "total_market": round(total_market, 2),
        "total_spread": round(total_spread, 2),
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
    with open("canonical_case.json", "w") as fh:
        json.dump(out, fh, indent=2)

    print("  Wrote canonical_case.json")
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
