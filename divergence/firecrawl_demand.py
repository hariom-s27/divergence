#!/usr/bin/env python3
"""
FIRECRAWL DEMAND RESEARCH -- DIVERGENCE, Block C2
One-off research script, not part of the pipeline. Uses the real
Firecrawl API (FIRECRAWL_API_KEY from the shell, never in a file) to
search for public evidence that real people hit the valuation question
this project studies -- a substitute for the practitioner interviews
attempted from 6 August that got no response in sixteen days (see
prior-art/OBJ-1.md for the same substitution on the OBJ-1 side).

    python firecrawl_demand.py --query "..." --out raw/some_name.json
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.firecrawl.dev/v1"


def api_key():
    k = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not k:
        print("ERROR: FIRECRAWL_API_KEY not set in this shell.", file=sys.stderr)
        sys.exit(1)
    return k


def post(path, payload):
    req = urllib.request.Request(
        API_BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        raise


def search(query, limit=5, scrape=True):
    payload = {"query": query, "limit": limit}
    if scrape:
        payload["scrapeOptions"] = {"formats": ["markdown"]}
    return post("/search", payload)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    result = search(a.query, limit=a.limit)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
