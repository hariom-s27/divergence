#!/usr/bin/env python3
"""
KILL GATE — DIVERGENCE
Can we retrieve the data our headline demo depends on?

Run:  python3 killgate.py
Needs: Python 3.8+. Nothing to install — standard library only.

Writes everything it finds to ./cache/ and prints a GO / NO-GO verdict.
"""

import json, os, ssl, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

CACHE = "cache"
TARGET_START = datetime(2026, 6, 28, tzinfo=timezone.utc)
TARGET_END   = datetime(2026, 6, 30, tzinfo=timezone.utc)

os.makedirs(CACHE, exist_ok=True)
CTX = ssl.create_default_context()
results = {"run_at": datetime.now(timezone.utc).isoformat(), "checks": {}}


def get(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (research; hackathon project)",
        "Accept": "application/json,*/*",
    })
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.status, r.read()


def save(name, obj):
    path = os.path.join(CACHE, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    return path


def hr(title):
    print("\n" + "=" * 62)
    print(title)
    print("=" * 62)


# ─────────────────────────────────────────────────────────────
# CHECK 1 — CoinDCX: USDT/INR, the Indian market price
# ─────────────────────────────────────────────────────────────
hr("CHECK 1  CoinDCX — USDT/INR (the Indian market leg)")

# CoinDCX prefixes markets by source. We don't know which one carries
# the INR pair, so probe several rather than guessing.
PAIRS = ["I-USDT_INR", "B-USDT_INR", "USDTINR", "I-USDC_INR", "I-BTC_INR"]
coindcx_ok, coindcx_pair, coindcx_rows = False, None, None

for pair in PAIRS:
    url = f"https://public.coindcx.com/market_data/candles?pair={pair}&interval=1d&limit=500"
    try:
        status, body = get(url)
        data = json.loads(body)
        if isinstance(data, list) and data:
            coindcx_ok, coindcx_pair, coindcx_rows = True, pair, data
            print(f"  ✓ {pair}: {len(data)} candles returned")
            break
        print(f"  · {pair}: empty response")
    except urllib.error.HTTPError as e:
        print(f"  · {pair}: HTTP {e.code}")
    except Exception as e:
        print(f"  · {pair}: {type(e).__name__}")
    time.sleep(0.4)

covers_target = False
if coindcx_ok:
    # CoinDCX returns epoch milliseconds in 'time'
    stamps = [datetime.fromtimestamp(c["time"] / 1000, tz=timezone.utc)
              for c in coindcx_rows if isinstance(c, dict) and "time" in c]
    if stamps:
        oldest, newest = min(stamps), max(stamps)
        print(f"  History: {oldest.date()} → {newest.date()}")
        covers_target = oldest <= TARGET_START and newest >= TARGET_END
        print(f"  Covers 28–29 June 2026: {'YES' if covers_target else 'NO'}")

        hits = [c for c, t in zip(coindcx_rows, stamps)
                if TARGET_START <= t <= TARGET_END]
        if hits:
            print(f"\n  >>> TARGET DATES FOUND — {len(hits)} candle(s):")
            for c, t in zip(coindcx_rows, stamps):
                if TARGET_START <= t <= TARGET_END:
                    print(f"      {t.date()}  open {c.get('open')}  high {c.get('high')}"
                          f"  low {c.get('low')}  close {c.get('close')}")
            save("coindcx_target.json", hits)
        save(f"coindcx_{coindcx_pair}_daily.json", coindcx_rows)

results["checks"]["coindcx"] = {
    "reachable": coindcx_ok, "pair": coindcx_pair, "covers_target": covers_target,
}

# ─────────────────────────────────────────────────────────────
# CHECK 2 — Binance: USDC/USDT, the peg leg
# ─────────────────────────────────────────────────────────────
hr("CHECK 2  Binance — USDC/USDT (the peg leg)")

start_ms = int(TARGET_START.timestamp() * 1000)
end_ms   = int(TARGET_END.timestamp() * 1000)
binance_ok = False
try:
    url = ("https://api.binance.com/api/v3/klines?symbol=USDCUSDT"
           f"&interval=1h&startTime={start_ms}&endTime={end_ms}")
    status, body = get(url)
    rows = json.loads(body)
    if rows:
        binance_ok = True
        print(f"  ✓ {len(rows)} hourly candles for the target window")
        lows  = [float(r[3]) for r in rows]
        highs = [float(r[2]) for r in rows]
        print(f"  USDC/USDT range: {min(lows):.4f} – {max(highs):.4f}")
        save("binance_usdc_usdt_target.json", rows)
    else:
        print("  · empty — the window may predate the listing")
except urllib.error.HTTPError as e:
    print(f"  ✗ HTTP {e.code} (Binance is geo-blocked in some places — try binance.us or Kraken)")
except Exception as e:
    print(f"  ✗ {type(e).__name__}: {e}")

results["checks"]["binance"] = {"reachable": binance_ok}

# ─────────────────────────────────────────────────────────────
# CHECK 3 — USD/INR, the official leg
# ─────────────────────────────────────────────────────────────
hr("CHECK 3  USD/INR — the official leg")

fx_ok, fx_source = False, None
FX = [
    ("Frankfurter", "https://api.frankfurter.app/2026-06-26..2026-06-30?from=USD&to=INR"),
    ("exchangerate.host", "https://api.exchangerate.host/timeseries?start_date=2026-06-26&end_date=2026-06-30&base=USD&symbols=INR"),
]
for name, url in FX:
    try:
        status, body = get(url)
        data = json.loads(body)
        if data.get("rates"):
            fx_ok, fx_source = True, name
            print(f"  ✓ {name}:")
            for d in sorted(data["rates"]):
                print(f"      {d}  USD/INR = {data['rates'][d].get('INR')}")
            save("usd_inr_target.json", data)
            break
        print(f"  · {name}: no rates in response")
    except Exception as e:
        print(f"  · {name}: {type(e).__name__}")
    time.sleep(0.4)

print("\n  NOTE: these are market rates, NOT the official FBIL fixing.")
print("  For the record you must cite either the FBIL reference rate")
print("  or the SBI TT buying rate (which Rule 115 actually mandates).")
print("  Neither publishes an open API — retrieve by hand and record the source.")

results["checks"]["usd_inr"] = {"reachable": fx_ok, "source": fx_source}

# ─────────────────────────────────────────────────────────────
# VERDICT
# ─────────────────────────────────────────────────────────────
hr("VERDICT")

save("killgate_results.json", results)

if covers_target:
    print("  ✅ GO — headline stays the 28–29 JUNE DIVERGENCE")
    print()
    print("  Next: recompute ₹41,150 from this real data.")
    print("  If the real number differs, USE THE REAL NUMBER everywhere.")
elif coindcx_ok:
    print("  ⚠️  PARTIAL — the API works but history doesn't reach June 2026.")
    print()
    print("  Options, in order of preference:")
    print("    1. Try interval=1h or 4h — different depth limits may apply")
    print("    2. Look for startTime / endTime parameters in CoinDCX's docs")
    print("    3. Cite the news reports (The Block, CoinDesk, 29–30 June 2026)")
    print("       as a secondary source, clearly labelled as such")
    print("    4. Switch the headline to the WEEKEND case")
else:
    print("  ⛔ NO-GO on this route — switch the headline to the WEEKEND CASE.")
    print()
    print("  This is a good outcome, not a disaster:")
    print("    · A payment at 03:14 on a Sunday needs no historical data")
    print("    · FBIL publishes only on Mumbai working days — so no official")
    print("      rate exists for that moment, by design, permanently")
    print("    · It is reproducible forever, and arguably a CLEANER proof")
    print("      that the law has no answer than a one-off market spike")
    print("    · It also sidesteps Objection 3 — the June spike was caused")
    print("      by an enforcement raid, so it doubles as evidence the")
    print("      market is being suppressed")

print(f"\n  Everything saved to ./{CACHE}/")
print("  Record the outcome in STEP-LOG.md today, either way.\n")
