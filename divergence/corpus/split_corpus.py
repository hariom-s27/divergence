#!/usr/bin/env python3
"""
split_corpus.py  --  DIVERGENCE
Builds corpus/verbatim/ : statutory text ONLY, with our own commentary and
front-matter stripped out.

WHY THIS EXISTS
---------------
About 40% of corpus/ by volume is our analysis, not law. If that goes into a
resolver prompt, the model reads our conclusions and hands them back. The
citation matcher passes it, because the citations are real. And the headline
result becomes an artifact of us having told it the answer.

corpus/          -> humans, provenance, and the citation matcher
corpus/verbatim/ -> what prompts are allowed to see

    python split_corpus.py corpus
    python split_corpus.py corpus --audit    # show each cut point

Exit code 0 = every file had explicit markers.
Exit code 1 = at least one file was cut by guesswork. REVIEW IT.

HOW A FILE IS CUT
-----------------
1. If the file contains  <!-- VERBATIM-START -->  and  <!-- VERBATIM-END -->
   the text between them is used. Markers always win.
2. Otherwise: YAML front-matter is dropped, then everything from the first
   commentary heading onwards is dropped. This is a GUESS. The script says so
   and exits 1 so you cannot ship without looking.

The fix for a wrong guess is not to edit this script. Put the markers in the
corpus file. A rule you cannot enforce is not a rule.
"""

import os
import re
import sys

START = "<!-- VERBATIM-START -->"
END = "<!-- VERBATIM-END -->"

# A heading is "commentary" if it carries one of our flags or reads like
# analysis rather than a provision title.
COMMENTARY_HEAD = re.compile(
    r"^#{1,6}\s*(?:[⭐⚠🔴🟡🟢✅❌]|"
    r"(?:AND\b|WHY\b|WHAT\b|THREE\b|TWO\b|THE\s+(?:POINT|GAP|CATCH|CHAIN)|"
    r"HOW\b|SO\b|NOTE\b|LANGUAGE\b|VERIFICATION\b|PROVENANCE\b|"
    r"THIS\b|IT\b|OUR\b))",
    re.IGNORECASE,
)



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


def strip_front_matter(text):
    if not text.lstrip().startswith("---"):
        return text
    parts = text.split("---", 2)
    return parts[2] if len(parts) >= 3 else text


def cut(text):
    """Return (verbatim_text, mode, first_dropped_line)."""
    if START in text and END in text:
        # A file may hold several provisions. Keep EVERY marked block,
        # in order. Keeping only the first silently drops sections 7 and 8.
        blocks = []
        rest = text
        while START in rest and END in rest:
            after = rest.split(START, 1)[1]
            block, rest = after.split(END, 1)
            blocks.append(block.strip())
        return "\n\n".join(blocks), "MARKER", None

    body = strip_front_matter(text)
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if COMMENTARY_HEAD.match(line.strip()):
            return ("\n".join(lines[:i]).strip(), "GUESS", line.strip())
    return body.strip(), "GUESS", None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    corpus = sys.argv[1]
    audit = "--audit" in sys.argv
    out = os.path.join(corpus, "verbatim")

    if not os.path.isdir(corpus):
        print(f"ERROR: no such directory: {corpus}")
        sys.exit(2)
    os.makedirs(out, exist_ok=True)

    paths = find_corpus_files(corpus)

    # DUPLICATE BASENAMES = the same provision living in two places.
    # Whichever is written second silently wins. Refuse to guess.
    seen = {}
    dupes = {}
    for p in paths:
        b = os.path.basename(p)
        if b in seen:
            dupes.setdefault(b, [seen[b]]).append(p)
        else:
            seen[b] = p
    if dupes:
        print("!" * 78)
        print("DUPLICATE FILENAMES — the same provision exists in two places.")
        print("Whichever is processed last would silently overwrite the other.")
        print("!" * 78)
        for b, locs in sorted(dupes.items()):
            print(f"  {b}")
            for L in locs:
                print(f"      {os.path.relpath(L, corpus)}  "
                      f"({os.path.getsize(L):,} bytes)")
        print()
        print("Delete the stale copy. Tier A lives in ONE folder. Then re-run.")
        sys.exit(3)

    if not paths:
        print(f"ERROR: no Tier A .md files found under {corpus}")
        print("Looked in subfolders. Skipped: verbatim/, tier-b/, MANIFEST.md")
        sys.exit(2)

    print("=" * 78)
    print("SPLIT CORPUS  ·  building corpus/verbatim/")
    print("=" * 78)
    print(f"{'file':<30}{'mode':>8}{'kept':>9}{'dropped':>9}{'drop%':>7}")
    print("-" * 78)

    guesses = []
    empties = []
    tk = td = 0

    for src in paths:
        name = os.path.basename(src)
        rel = os.path.relpath(src, corpus)
        with open(src, encoding="utf-8") as fh:
            text = fh.read()

        body, mode, first_dropped = cut(text)
        kept = len(body)
        dropped = len(text) - kept
        tk += kept
        td += dropped

        with open(os.path.join(out, name), "w", encoding="utf-8") as fh:
            fh.write(body + "\n")

        flag = "" if mode == "MARKER" else "  <-- guess"
        pct = 100 * dropped / len(text) if text else 0
        print(f"{rel[:29]:<30}{mode:>8}{kept:>9,}{dropped:>9,}{pct:>6.0f}%{flag}")

        if mode == "GUESS":
            guesses.append((name, first_dropped))
        if kept < 200:
            empties.append((name, kept))

    print("-" * 78)
    total = tk + td
    print(f"{'TOTAL':<30}{'':>8}{tk:>9,}{td:>9,}"
          f"{100 * td / total if total else 0:>6.0f}%")
    print()
    print(f"Verbatim corpus: {tk:,} chars  (~{tk / 4:,.0f} tokens)")
    print(f"Removed:         {td:,} chars of front-matter and commentary")
    print()

    if audit and guesses:
        print("=" * 78)
        print("CUT POINTS  ·  first line dropped from each guessed file")
        print("=" * 78)
        for name, line in guesses:
            print(f"  {name}")
            print(f"      {line if line else '(nothing dropped after front-matter)'}")
        print()

    if empties:
        print("!" * 78)
        print("SUSPICIOUSLY SHORT OUTPUT — the cut is probably in the wrong place")
        for name, kept in empties:
            print(f"  {name}: only {kept} chars kept")
        print("!" * 78)
        print()

    if guesses:
        print("=" * 78)
        print(f"{len(guesses)} of {len(paths)} files were cut by GUESSWORK.")
        print("=" * 78)
        print("Open each one in corpus/verbatim/ and check that it contains the")
        print("provision and nothing of ours. Then put the markers in the SOURCE")
        print("file in corpus/ so the cut is never guessed again:")
        print()
        print(f"    {START}")
        print("    ...the provision, copied and pasted, nothing else...")
        print(f"    {END}")
        print()
        print("Re-run until this message disappears. Only then write prompts.")
        sys.exit(1)

    print("All files cut by explicit markers. corpus/verbatim/ is safe to inject.")
    sys.exit(0)


if __name__ == "__main__":
    main()
