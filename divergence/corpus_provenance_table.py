#!/usr/bin/env python3
"""
CORPUS PROVENANCE TABLE -- DIVERGENCE, S3
Generates the per-provision provenance table for CORPUS-PROVENANCE.md
(provision id, current citation, source URL, retrieval date, SHA-256)
directly from each Tier A file's own front matter and
corpus/FREEZE-HASHES.json -- never hand-transcribed, so the table can
never silently drift from the real files it describes the way a
copy-pasted table could.

    python corpus_provenance_table.py            # print the markdown table
    python corpus_provenance_table.py --check    # exit 1 if any Tier A file
                                                   # is missing a hash or a
                                                   # required front-matter field
"""
import os
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import citation_matcher  # noqa: E402

TIER_A_DIR = os.path.join(HERE, "corpus", "tier-a")
FREEZE_HASHES = os.path.join(HERE, "corpus", "FREEZE-HASHES.json")

REQUIRED_FIELDS = ("provision_id", "current_citation", "source_url", "retrieved")


def rows():
    hashes = json.load(open(FREEZE_HASHES, encoding="utf-8"))["hashes"]
    out = []
    for fn in sorted(os.listdir(TIER_A_DIR)):
        if not fn.endswith(".md"):
            continue
        meta = citation_matcher.parse_front_matter(os.path.join(TIER_A_DIR, fn))
        out.append({
            "file": fn,
            "provision_id": meta.get("provision_id"),
            "current_citation": meta.get("current_citation"),
            "source_url": meta.get("source_url"),
            "retrieved": meta.get("retrieved"),
            "known_limitation": meta.get("known_limitation"),
            "sha256": hashes.get(fn),
        })
    return out


def check(rows_):
    problems = []
    for r in rows_:
        for f in REQUIRED_FIELDS:
            if not r.get(f):
                problems.append(f"{r['file']}: missing {f!r}")
        if not r.get("sha256"):
            problems.append(f"{r['file']}: no entry in FREEZE-HASHES.json")
    return problems


def markdown(rows_):
    lines = [
        "| Provision | Current citation | Source | Retrieved | SHA-256 (first 12 hex) |",
        "|---|---|---|---|---|",
    ]
    for r in rows_:
        limit_note = f" — *{r['known_limitation']}*" if r.get("known_limitation") else ""
        sha_short = (r["sha256"] or "MISSING")[:12]
        source = r["source_url"] or "**not recorded in front matter**"
        lines.append(
            f"| `{r['provision_id']}` | {r['current_citation']} | "
            f"{source}{limit_note} | {r['retrieved']} | `{sha_short}…` |"
        )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any Tier A file is missing a required field or hash")
    a = ap.parse_args()

    rs = rows()
    problems = check(rs)
    if a.check:
        if problems:
            print(f"\n  {len(problems)} problem(s):")
            for p in problems:
                print(f"    {p}")
            sys.exit(1)
        print(f"\n  OK -- {len(rs)} Tier A file(s), all carry provision_id/current_citation/"
              f"source_url/retrieved and a FREEZE-HASHES.json entry.\n")
        return

    if problems:
        print(f"  [{len(problems)} field(s) missing -- shown as blank cells below, not silently skipped]")
    print()
    print(markdown(rs))
    print()
    print(f"{len(rs)} Tier A files, {sum(1 for r in rs if r.get('known_limitation'))} "
          f"carrying an open known_limitation note.")


if __name__ == "__main__":
    main()
