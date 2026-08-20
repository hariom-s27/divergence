#!/usr/bin/env python3
"""
RUN-ALL — DIVERGENCE
One command runs every check we have built so far.

    python3 run_all.py

Standard library only. Nothing to install.
"""

import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))

CHECKS = [
    ("1  KILL GATE — can we retrieve the rate data our demo depends on?",
     "killgate.py",
     "Needs internet. Writes to ./cache/. Prints GO / PARTIAL / NO-GO."),
    ("2  CITATION MATCHER — self-test against the real corpus",
     "citation_matcher.py",
     "No internet needed. Should print 15/15."),
]


def rule(ch="─", n=74):
    print(ch * n)


def main():
    print()
    rule("═")
    print("  DIVERGENCE — running all checks")
    rule("═")

    # corpus sanity first
    corpus = os.path.join(HERE, "corpus", "tier-a")
    n = len([f for f in os.listdir(corpus) if f.endswith(".md")]) if os.path.isdir(corpus) else 0
    print(f"\n  Corpus: {n} Tier A files found at ./corpus/tier-a/")
    if n == 0:
        print("  ⛔ No corpus. The citation matcher will fail. Check you are in the right folder.")

    results = []
    for title, script, note in CHECKS:
        path = os.path.join(HERE, script)
        print()
        rule()
        print(f"  {title}")
        print(f"  → {script}   ({note})")
        rule()
        if not os.path.exists(path):
            print(f"  ⛔ {script} not found — skipped")
            results.append((script, "MISSING"))
            continue
        t = time.time()
        try:
            r = subprocess.run([sys.executable, path], cwd=HERE, timeout=300)
            status = "OK" if r.returncode == 0 else f"EXIT {r.returncode}"
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
        except Exception as e:
            status = f"ERROR {type(e).__name__}"
        results.append((script, f"{status}  ({time.time()-t:.1f}s)"))

    print()
    rule("═")
    print("  SUMMARY")
    rule("═")
    for script, status in results:
        print(f"  {script:<26}{status}")
    print()
    print("  Next: write today's outcome into iteration-log.md — even if something failed.")
    print("  Especially if something failed.\n")


if __name__ == "__main__":
    main()
