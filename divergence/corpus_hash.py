#!/usr/bin/env python3
"""
CORPUS HASH — DIVERGENCE
Deterministic. No model, no API. `corpus/MANIFEST.md` has said "COMPLETE,
hashed" next to several Tier A files since 19 August — nothing ever
recorded what the hash WAS, and nothing ever checked it again. The claim
was true in spirit (nobody had touched the files) and unverifiable in
fact. schema.json's `corpus_frozen_at` field (C34) asserts a freeze
happened; this is what makes that assertion checkable rather than a
timestamp a reader has to take on trust.

    python corpus_hash.py --freeze     # write corpus/FREEZE-HASHES.json
    python corpus_hash.py --verify     # compare current files against it

--verify exits 1 on any drift, addition, or removal — wire into CI the
same way citation_matcher.py and gap_enforcer.py already are. --freeze is
never run automatically; a hash file that updates itself on every commit
verifies nothing. Re-freezing after a real, deliberate corpus edit is the
one legitimate reason to run it again, and it should be its own disclosed
commit, not a side effect of another change.
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import citation_matcher  # noqa: E402

FREEZE_FILE = os.path.join(HERE, "corpus", "FREEZE-HASHES.json")
TIER_A_DIR = os.path.join(HERE, "corpus", "tier-a")


def compute_hashes():
    """SHA-256 of each Tier A file's body — same body citation_matcher.py
    itself reads (front matter stripped), so a hash mismatch means the
    text the pipeline actually cites against has changed, not just a
    comment or a date in the header."""
    out = {}
    for fn in sorted(os.listdir(TIER_A_DIR)):
        if not fn.endswith(".md"):
            continue
        meta = citation_matcher.parse_front_matter(os.path.join(TIER_A_DIR, fn))
        body = meta.get("_text", "")
        out[fn] = hashlib.sha256(body.strip().encode("utf-8", "ignore")).hexdigest()
    return out


def die(msg):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(1)


def freeze():
    hashes = compute_hashes()
    doc = {
        "_comment": (
            "SHA-256 of each Tier A corpus file's body (front matter "
            "stripped), computed by corpus_hash.py --freeze. "
            "corpus_hash.py --verify checks these have not drifted since. "
            "Regenerate deliberately after a real corpus edit, as its own "
            "disclosed commit -- never as a side effect of another change."
        ),
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "file_count": len(hashes),
        "hashes": hashes,
    }
    with open(FREEZE_FILE, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    print(f"\n  Froze {len(hashes)} Tier A file hash(es) -> "
          f"{os.path.relpath(FREEZE_FILE, HERE)}\n")
    for fn, h in hashes.items():
        print(f"    {fn:<32} {h[:16]}…")
    print()


def verify():
    if not os.path.exists(FREEZE_FILE):
        die(f"{os.path.relpath(FREEZE_FILE, HERE)} not found — run "
            f"'python corpus_hash.py --freeze' first")
    frozen = json.load(open(FREEZE_FILE, encoding="utf-8"))["hashes"]
    current = compute_hashes()

    problems = []
    for fn, h in frozen.items():
        if fn not in current:
            problems.append(f"{fn}: present at freeze time, missing now")
        elif current[fn] != h:
            problems.append(f"{fn}: HASH DRIFT — content changed since freeze "
                             f"(was {h[:16]}…, now {current[fn][:16]}…)")
    for fn in current:
        if fn not in frozen:
            problems.append(f"{fn}: new Tier A file, not covered by the freeze — "
                             f"run --freeze to include it deliberately")

    print(f"\n  {len(frozen)} frozen hash(es), {len(current)} current file(s)\n")
    if problems:
        for p in problems:
            print(f"  [XX]  {p}")
        print(f"\n  {len(problems)} problem(s) — corpus drift detected.\n")
        sys.exit(1)

    print("  [OK]  Every Tier A file's content matches its frozen hash. "
          "No drift.\n")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(description="Corpus integrity hashing — Tier A only")
    ap.add_argument("--freeze", action="store_true", help="write corpus/FREEZE-HASHES.json")
    ap.add_argument("--verify", action="store_true", help="check current files against it")
    a = ap.parse_args()

    if a.freeze:
        freeze()
    elif a.verify:
        verify()
    else:
        die("pass --freeze or --verify")


if __name__ == "__main__":
    main()
