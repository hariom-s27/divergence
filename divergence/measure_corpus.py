#!/usr/bin/env python3
"""
measure_corpus.py  --  DIVERGENCE Step 18
Measures the real token size of the corpus so the cost model runs on
measured numbers instead of estimates.

Standard library only. No API key required.

Usage:
    python measure_corpus.py ../corpus
    python measure_corpus.py ../corpus --json corpus_profile.json

Output: per-file characters, words, and token estimates under BOTH
Anthropic tokenizers, plus a corpus_profile.json the cost model reads.

WHY TWO TOKENIZERS
------------------
Anthropic's pricing docs state that Claude 4.7 and later models use a newer
tokenizer that produces approximately 30% more tokens for the same text.
Claude Sonnet 4.6 and earlier use the previous tokenizer. A cost model that
ignores this understates spend on Opus 5 / Sonnet 5 by roughly a third.
Source: https://platform.claude.com/docs/en/about-claude/pricing
"""

import json
import os
import sys

# Anthropic docs, Pricing FAQ: "1 token is approximately 4 characters".
CHARS_PER_TOKEN_LEGACY = 4.0
# Newer tokenizer (Claude 4.7+): ~30% more tokens for the same text.
NEW_TOKENIZER_FACTOR = 1.30

# Which corpus files each pipeline node needs. Edit to match the real
# filenames. This mapping is the single biggest cost lever in the design:
# it is the difference between injecting 16 files seven times and
# injecting only what each node can legitimately cite.
DEFAULT_SCOPES = {
    "intake_extract":   [],
    "gap_detector":     [],
    "dual_valuation":   ["rcasp", "rule57", "rule56", "fbil", "sbi"],
    "regime_incometax": ["rule57", "rule56", "s2_47a", "s92", "s115bbh",
                         "s194s", "s439", "rcasp"],
    "regime_gst":       ["igst", "cgst", "s74a", "place_of_supply"],
    "regime_fema":      ["fema"],
    "adversarial":      ["*"],          # must be able to attack any claim
}



# ---------------------------------------------------------------------
# FILE DISCOVERY
# corpus/
#   tier-a/     <- the 16 citable provisions. THIS is the corpus.
#   tier-b/     <- summarised, NOT citable. NEVER injected.
#   verbatim/   <- generated output. Never an input.
#   MANIFEST.md <- our scope statement, not law. Never injected.
# ---------------------------------------------------------------------
SKIP_DIRS = {"verbatim", "tier-b", "tier_b", "__pycache__", ".git"}
SKIP_FILES = {"MANIFEST.md", "README.md"}


def find_corpus_files(root):
    """Walk corpus/, return only citable Tier A .md files."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".md") and fn not in SKIP_FILES:
                found.append(os.path.join(dirpath, fn))
    return sorted(found, key=lambda p: os.path.basename(p))


def tokens_legacy(chars):
    return chars / CHARS_PER_TOKEN_LEGACY


def tokens_current(chars):
    return (chars / CHARS_PER_TOKEN_LEGACY) * NEW_TOKENIZER_FACTOR


def measure_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    chars = len(text)
    return {
        "file": os.path.basename(path),
        "chars": chars,
        "words": len(text.split()),
        "tok_legacy": round(tokens_legacy(chars)),
        "tok_current": round(tokens_current(chars)),
    }


def scope_tokens(files, keys):
    """Sum tokens for the files whose name contains any of the given keys."""
    if keys == ["*"]:
        return (sum(f["tok_legacy"] for f in files),
                sum(f["tok_current"] for f in files),
                len(files))
    legacy = current = 0
    hits = 0
    for f in files:
        name = f["file"].lower()
        if any(k.lower() in name for k in keys):
            legacy += f["tok_legacy"]
            current += f["tok_current"]
            hits += 1
    return legacy, current, hits


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    corpus_dir = sys.argv[1]
    if not os.path.isdir(corpus_dir):
        print(f"ERROR: corpus directory not found: {corpus_dir}")
        print("The matcher failed this way once already. Ship the data "
              "with the code.")
        sys.exit(2)

    paths = find_corpus_files(corpus_dir)
    if not paths:
        print(f"ERROR: no Tier A .md files found under {corpus_dir}")
        print("Looked in subfolders too. Skipped: verbatim/, tier-b/, MANIFEST.md")
        sys.exit(2)

    files = [measure_file(p) for p in paths]

    print("=" * 78)
    print("DIVERGENCE  ·  CORPUS TOKEN CENSUS")
    print("=" * 78)
    print(f"{'file':<40}{'chars':>9}{'words':>8}{'tok(4.6-)':>11}{'tok(4.7+)':>11}")
    print("-" * 78)
    for f in files:
        print(f"{f['file'][:39]:<40}{f['chars']:>9,}{f['words']:>8,}"
              f"{f['tok_legacy']:>11,}{f['tok_current']:>11,}")
    print("-" * 78)
    tot_c = sum(f["chars"] for f in files)
    tot_l = sum(f["tok_legacy"] for f in files)
    tot_n = sum(f["tok_current"] for f in files)
    print(f"{'TOTAL (' + str(len(files)) + ' files)':<40}{tot_c:>9,}"
          f"{sum(f['words'] for f in files):>8,}{tot_l:>11,}{tot_n:>11,}")
    print()

    print("=" * 78)
    print("PER-NODE SCOPED CORPUS  ·  what each node actually needs")
    print("=" * 78)
    scopes = {}
    naive_l = naive_n = 0
    scoped_l = scoped_n = 0
    for node, keys in DEFAULT_SCOPES.items():
        if not keys:
            l = n = hits = 0
        else:
            l, n, hits = scope_tokens(files, keys)
        scopes[node] = {"tok_legacy": l, "tok_current": n, "files": hits}
        scoped_l += l
        scoped_n += n
        naive_l += tot_l
        naive_n += tot_n
        print(f"{node:<22}{hits:>3} files{n:>10,} tok (4.7+)")
    print("-" * 78)
    print(f"{'SCOPED TOTAL':<22}{'':>9}{scoped_n:>10,} tok per record")
    print(f"{'NAIVE (all 16 × 7)':<22}{'':>9}{naive_n:>10,} tok per record")
    if scoped_n:
        print(f"{'SAVED BY SCOPING':<22}{'':>9}"
              f"{naive_n - scoped_n:>10,} tok "
              f"({100 * (1 - scoped_n / naive_n):.1f}% less)")
    print()

    profile = {
        "corpus_dir": os.path.abspath(corpus_dir),
        "n_files": len(files),
        "files": files,
        "total_chars": tot_c,
        "corpus_tok_legacy": tot_l,
        "corpus_tok_current": tot_n,
        "node_scopes": scopes,
        "assumptions": {
            "chars_per_token_legacy": CHARS_PER_TOKEN_LEGACY,
            "new_tokenizer_factor": NEW_TOKENIZER_FACTOR,
            "source": "https://platform.claude.com/docs/en/about-claude/pricing",
        },
    }

    out = "corpus_profile.json"
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(profile, fh, indent=2)
    print(f"Wrote {out} — feed this to cost_model.py --profile {out}")
    print()
    print("LIMITATION: these are character-ratio estimates, not tokenizer "
          "output.\nAnthropic's count_tokens endpoint gives exact counts; "
          "run it once the\nAPI key is live and replace these figures. "
          "Expect them to move by 5-15%.")


if __name__ == "__main__":
    main()
