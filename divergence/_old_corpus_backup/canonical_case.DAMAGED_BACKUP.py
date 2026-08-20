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
SBI_TTBR = 94.0000

# The official leg has NO value on the receipt date, because no official
# rate is published on a Sunday. These are the candidate dates a
# professional could defensibly use. Fill in the retrieved SBI TT buying
# rate for each. Leave a value as None until you have actually retrieved it.
