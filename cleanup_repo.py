#!/usr/bin/env python3
"""
cleanup_repo.py  --  get the repo down to one live copy of everything.

DRY RUN BY DEFAULT. Nothing moves until you pass --apply. Nothing is ever
deleted: things go to _archive/, which .gitignore excludes.

    python cleanup_repo.py                # show me what you'd do
    python cleanup_repo.py --apply        # do it

Run from the folder you want to become the repo root (D44: that's reverie/).

WHY (D44): the first commit staged 212 files including eight zips, a folder of
retired corpus, and a duplicate of the pipeline. The retired corpus is the
dangerous one -- IT-RULE-115.md and IT-RULE-57.md are exactly the files that
alphabetically shadowed their ITR2026-* replacements and made the citation
matcher score 15/15 for the wrong reason. Shipping them back into a public
repo, in a project about detecting stale ground, is the one thing not to do.
"""

import hashlib
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ARCHIVE = "_archive"

# Folders whose whole contents are retired or duplicated.
ARCHIVE_DIRS = [
    "_old_corpus_backup",          # retired shadowing corpus -- the dangerous one
    "drop5featherless",            # second copy of llm_call/check_llm/.gitignore
    "New folder",                  # 171MB PDF, over GitHub's 100MB hard limit
]

# Retired corpus files sitting loose at the repo root. These are the pre-gazette
# versions; the live ones are divergence/corpus/tier-a/ITR2026-*.md
ARCHIVE_ROOT_FILES = [
    "IT-RULE-57.md", "IT-RULE-57 (1).md", "IT-RULE-57 (2).md",
    "IT-RULE-115.md", "IT-RULE-206.md", "IT-RULE-207.md",
    "ITR2026-RULE-57.md",
]

ARCHIVE_SUFFIXES = (".zip",)

# Never touch these, whatever else matches.
KEEP_DIRS = {".git", ARCHIVE, "corpus", "cases", "prompts", "eval", "runs"}
KEEP_NAMES = {"llm_call.py", "check_llm.py", "run_pipeline.py", "schema.json"}


def sha(path, cap=8 * 1024 * 1024):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(1 << 20)
                if not b:
                    break
                h.update(b)
                if f.tell() > cap:
                    break
    except OSError:
        return None
    return h.hexdigest()


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return "%.0f%s" % (n, u)
        n /= 1024.0
    return "%.1fTB" % n


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d != ARCHIVE and d != ".git"
                       and not d.startswith(".")
                       and d != "__pycache__"]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def plan(root):
    moves = []          # (src, reason)
    seen = set()

    def add(p, reason):
        p = os.path.normpath(p)
        if p in seen or not os.path.exists(p):
            return
        seen.add(p)
        moves.append((p, reason))

    # whole folders
    for dirpath, dirnames, _ in os.walk(root):
        if ARCHIVE in dirpath.split(os.sep) or ".git" in dirpath.split(os.sep):
            continue
        for d in list(dirnames):
            if d in ARCHIVE_DIRS:
                add(os.path.join(dirpath, d), "retired/duplicate folder")

    # loose retired corpus at root
    for fn in ARCHIVE_ROOT_FILES:
        add(os.path.join(root, fn), "retired corpus file (live copy is in corpus/tier-a/)")

    # zips
    for p in walk(root):
        if p.lower().endswith(ARCHIVE_SUFFIXES):
            add(p, "zip of a folder that is already in the repo")

    return moves


def duplicates(root):
    """Report only -- identical content at two paths. You decide."""
    by_hash = {}
    for p in walk(root):
        if os.path.basename(p) in KEEP_NAMES:
            pass
        try:
            if os.path.getsize(p) == 0 or os.path.getsize(p) > 8 * 1024 * 1024:
                continue
        except OSError:
            continue
        h = sha(p)
        if h:
            by_hash.setdefault(h, []).append(p)
    return {h: ps for h, ps in by_hash.items() if len(ps) > 1}


def main():
    apply = "--apply" in sys.argv
    root = os.path.abspath(".")
    print("root : %s" % root)
    print("mode : %s\n" % ("APPLY -- moving files" if apply else "DRY RUN -- nothing will move"))

    moves = plan(root)
    total = 0
    if not moves:
        print("nothing to archive.\n")
    else:
        print("TO ARCHIVE  (moved to %s/, not deleted)\n" % ARCHIVE)
        for src, reason in sorted(moves):
            if os.path.isdir(src):
                size = sum(os.path.getsize(os.path.join(dp, f))
                           for dp, _, fs in os.walk(src) for f in fs
                           if os.path.exists(os.path.join(dp, f)))
                kind = "dir "
            else:
                size = os.path.getsize(src)
                kind = "file"
            total += size
            print("  %s  %8s  %-58s  %s"
                  % (kind, human(size), os.path.relpath(src, root), reason))
        print("\n  %d item(s), %s\n" % (len(moves), human(total)))

    dups = duplicates(root)
    if dups:
        print("IDENTICAL CONTENT AT MORE THAN ONE PATH  (reported only -- you choose)\n")
        shown = 0
        for h, ps in sorted(dups.items(), key=lambda kv: -len(kv[1])):
            rels = sorted(os.path.relpath(p, root) for p in ps)
            print("  %s" % rels[0])
            for r in rels[1:]:
                print("    = %s" % r)
            shown += 1
            if shown >= 25:
                print("  ... and %d more duplicate group(s)" % (len(dups) - shown))
                break
        print("\n  Keep the copy the code imports. For prompts that is")
        print("  step22drop/prompts/ -- node1_extract.py hardcodes that path.\n")

    if not apply:
        print("Dry run only. Re-run with --apply to move the archive list.")
        return 0

    os.makedirs(ARCHIVE, exist_ok=True)
    for src, _ in sorted(moves):
        dst = os.path.join(ARCHIVE, os.path.relpath(src, root))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            dst = dst + ".dup"
        shutil.move(src, dst)
        print("  moved  %s" % os.path.relpath(src, root))
    print("\n%d item(s) moved to %s/. Nothing deleted." % (len(moves), ARCHIVE))
    print("Add '_archive/' to .gitignore before you commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
