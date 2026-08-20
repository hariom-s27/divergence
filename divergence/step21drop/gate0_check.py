#!/usr/bin/env python3
"""
GATE 0 CHECK — DIVERGENCE
Reads your real folder and reports exactly what is done and what is not.
Changes nothing. Read-only. Safe to run any number of times.

Run from inside the `divergence` folder:

    python gate0_check.py

Needs Python 3.8+. Standard library only. Nothing to install.
"""

import os, re, sys, json, hashlib
from collections import defaultdict

# Windows consoles default to cp1252 and this script prints box-drawing and
# emoji. Same crash citation_matcher.py had. Fix it here too.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "corpus")
TIER_A = os.path.join(CORPUS, "tier-a")
TIER_B = os.path.join(CORPUS, "tier-b")
VERBATIM = os.path.join(CORPUS, "verbatim")

OK, WARN, BAD, INFO = "  [OK]  ", "  [!!]  ", "  [XX]  ", "  [--]  "
problems, warnings = [], []

def head(t):
    print("\n" + "=" * 72); print("  " + t); print("=" * 72)

def bad(msg, fix):
    problems.append((msg, fix)); print(BAD + msg)

def warn(msg, fix):
    warnings.append((msg, fix)); print(WARN + msg)

def ok(msg):
    print(OK + msg)

def info(msg):
    print(INFO + msg)


# ─────────────────────────────────────────────────────────────
def front_matter(path):
    try:
        raw = open(path, encoding="utf-8").read()
    except Exception:
        return {}, ""
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    meta = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        meta[k.strip()] = None if v in ("null", "") else v
    return meta, parts[2]


def md_files(d):
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.lower().endswith(".md"))


# ─────────────────────────────────────────────────────────────
head("1. FOLDER LAYOUT")

for name, path in (("corpus/", CORPUS), ("corpus/tier-a/", TIER_A),
                   ("corpus/tier-b/", TIER_B), ("corpus/verbatim/", VERBATIM)):
    if os.path.isdir(path):
        n = len([f for f in os.listdir(path) if not f.startswith(".")])
        ok(f"{name:<22} exists  ({n} entries)")
    else:
        bad(f"{name} NOT FOUND",
            f"Run this script from inside the folder that contains corpus/")

expected_scripts = ["citation_matcher.py", "killgate.py", "canonical_case.py",
                    "schema.json", "run_all.py"]
optional_scripts = ["split_corpus.py", "cost_model.py", "measure_corpus.py",
                    "node3_valuation.py", "run_pipeline.py"]
for s in expected_scripts:
    (ok if os.path.exists(os.path.join(HERE, s)) else lambda m: bad(m, "missing"))(
        f"{s:<24} present" if os.path.exists(os.path.join(HERE, s)) else f"{s} MISSING")
for s in optional_scripts:
    p = os.path.join(HERE, s)
    print((OK if os.path.exists(p) else INFO) +
          f"{s:<24} {'present' if os.path.exists(p) else 'not built yet'}")


# ─────────────────────────────────────────────────────────────
head("2. CORPUS — duplicates, ids, citability")

a_files = md_files(TIER_A)
b_files = md_files(TIER_B)
print(f"  tier-a: {len(a_files)} files   tier-b: {len(b_files)} files\n")

by_id, by_hash, by_ref = defaultdict(list), defaultdict(list), defaultdict(list)
entries = []

def _split_number(num):
    b = re.match(r"[0-9]+[A-Za-z]*", num)
    b = b.group(0) if b else num
    return b.upper(), tuple(x.strip().lower() for x in re.findall(r"\(([^)]+)\)", num))

def extract_refs(text):
    if not text:
        return []
    t = text.replace("–", "-"); refs = []
    for kind, pat in (("SEC", r"(?:sections?|secs?\.?|s\.)\s*"), ("RULE", r"rules?\s*")):
        for m in re.finditer(pat + r"([0-9A-Za-z()\s,and&-]+)", t, flags=re.I):
            chunk = re.split(r"\bof\b|,\s*(?=income|integrated|central|foreign)",
                             m.group(1), flags=re.I)[0]
            for tok in re.findall(r"[0-9]+[A-Za-z]*(?:\([^)]+\))*", chunk):
                b, br = _split_number(tok)
                # A bare 4-digit 19xx/20xx is the Act's year, not a provision.
                # NOTE: citation_matcher.py has this same bug — fix it there too.
                if re.fullmatch(r"(19|20)\d\d", b) and not br:
                    continue
                refs.append((kind, b, br))
    return list(dict.fromkeys(refs))

for tier, folder, files in (("A", TIER_A, a_files), ("B", TIER_B, b_files)):
    for fn in files:
        p = os.path.join(folder, fn)
        meta, body = front_matter(p)
        h = hashlib.sha256(body.strip().encode("utf-8", "ignore")).hexdigest()[:12]
        pid = meta.get("provision_id") or "(none)"
        cur = re.split(r"\s+[—–-]\s+", meta.get("current_citation") or "", maxsplit=1)[0]
        e = dict(file=fn, tier=tier, pid=pid, meta=meta, body=body, hash=h,
                 cur=cur, refs=extract_refs(cur))
        entries.append(e); by_id[pid].append(fn); by_hash[h].append(fn)
        for r in e["refs"]:
            by_ref[r].append(fn)

for pid, fl in by_id.items():
    if len(fl) > 1 and pid != "(none)":
        bad(f"duplicate provision_id '{pid}' in: {', '.join(fl)}",
            "keep one; the matcher is first-hit-wins on sorted filename")
for h, fl in by_hash.items():
    if len(fl) > 1:
        bad(f"identical file bodies: {', '.join(fl)}",
            "delete the duplicate — split_corpus.py rejects duplicates")
for ref, fl in by_ref.items():
    if len(fl) > 1:
        bad(f"TWO FILES CLAIM {ref[0]} {ref[1]}{''.join('('+x+')' for x in ref[2])}: {', '.join(fl)}",
            "the alphabetically-first file wins and shadows the other — retire one")

for e in entries:
    if e["tier"] != "A":
        continue
    if e["pid"] == "(none)":
        bad(f"{e['file']}: no provision_id", "add provision_id to the front matter")
    if not e["refs"]:
        bad(f"{e['file']}: current_citation has no section/rule number -> CAN NEVER BE CITED",
            "give it a citable handle, e.g. 'Rule 243(8)(e), Income-tax Rules, 2026'")
    if e["meta"].get("known_limitation"):
        warn(f"{e['file']}: known_limitation still open -> {e['meta']['known_limitation'][:70]}",
             "close it or state it in the output's limits[]")
    st = (e["meta"].get("source_type") or "").lower()
    if st in ("mapping_table", "unofficial_full_text", "official_superseded"):
        warn(f"{e['file']}: source_type = {st}", "upgrade to official / official_gazette if you can")
    if "VERBATIM-START" not in e["body"]:
        warn(f"{e['file']}: no <!-- VERBATIM-START --> marker", "split_corpus.py needs it")


# ─────────────────────────────────────────────────────────────
head("3. MANIFEST vs FOLDER")

man = os.path.join(CORPUS, "MANIFEST.md")
if not os.path.exists(man):
    bad("corpus/MANIFEST.md not found", "the manifest is what makes a negative claim defensible")
else:
    txt = open(man, encoding="utf-8").read()
    missing = [e["file"] for e in entries if e["tier"] == "A" and e["file"] not in txt
               and e["file"].replace(".md", "") not in txt]
    if missing:
        bad(f"MANIFEST does not list {len(missing)} tier-a file(s): {', '.join(missing)}",
            "manifest must equal folder, exactly")
    else:
        ok("every tier-a file appears in MANIFEST.md")
    m = re.search(r"(\d+)\s*Tier A files", txt)
    if m and int(m.group(1)) != len(a_files):
        bad(f"MANIFEST says '{m.group(1)} Tier A files' but folder has {len(a_files)}",
            f"change the header to {len(a_files)}")


# ─────────────────────────────────────────────────────────────
head("4. STALE NUMBERS")

STALE = {r"43,?633": "43,633", r"9\.27": "9.27%", r"41,?150": "41,150",
         r"8\.5\s*%": "8.5%", r"44,?400": "44,400", r"9\.45": "9.45%",
         r"8\.7\s*percent|8\.7\s*%": "8.7%", r"4,?70,?517": "4,70,517",
         r"44,?720": "44,720", r"9\.515": "9.515%"}

# Anything node3_valuation.py currently emits is LIVE, not stale. Read the
# real figures and drop any pattern that matches one, so the check stays
# correct as the lattice changes instead of going stale itself.
_live = set()
_vj = os.path.join(HERE, "valuation.json")
if os.path.exists(_vj):
    try:
        _v = json.load(open(_vj, encoding="utf-8"))["valuation"]
        for _m in _v["methods"]:
            _live.add(f"{_m['inr_value']:,.2f}"); _live.add(f"{_m['inr_value']:,.0f}")
        _live.add(f"{_v['spread']['inr']:,.2f}"); _live.add(f"{_v['spread']['percent']}")
    except Exception:
        pass
if _live:
    STALE = {p: l for p, l in STALE.items()
             if not any(re.search(p, x) for x in _live)}
SKIP_DIRS = {".git", "__pycache__", "cache", "_old_corpus_backup", "node_modules",
             ".venv", "venv", "site-packages", "divergencegazettecorpus"}
# Docs whose JOB is to quote the retired figures. Reporting them is not a defect.
AUDIT_DOCS = {"audit-18-aug.md", "plan-18-to-25-aug.md", "master-roadmap-v2.md",
              "gazette-findings.md", "step-log.md", "iteration-log.md"}
hits = defaultdict(list)
for root, dirs, files in os.walk(HERE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
    for fn in files:
        if not fn.lower().endswith((".md", ".html", ".py", ".json", ".txt")):
            continue
        if fn == os.path.basename(__file__) or fn.lower() in AUDIT_DOCS:
            continue
        p = os.path.join(root, fn)
        try:
            txt = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for i, line in enumerate(txt.splitlines(), 1):
            if line.strip().startswith("~~"):
                continue                    # struck-through = already retired
            if "stale-ok" in line:
                continue                    # explicitly marked as a historical quote
            for pat, label in STALE.items():
                if re.search(pat, line):
                    hits[label].append(f"{os.path.relpath(p, HERE)}:{i}")

print("  (skipping this script, the audit/plan/log docs, ~~struck-through~~ lines,")
print("   and any line carrying an explicit  stale-ok  marker)")
if _live:
    print(f"  ({len(_live)} live figures read from valuation.json are exempt)")
print()
if not hits:
    ok("no stale headline figures found in live artifacts")
else:
    for label, locs in sorted(hits.items(), key=lambda x: -len(x[1])):
        bad(f"'{label}' appears {len(locs)}x", "purge or strike through")
        for l in locs[:6]:
            print(f"           {l}")
        if len(locs) > 6:
            print(f"           ... and {len(locs)-6} more")


# ─────────────────────────────────────────────────────────────
head("5. canonical_case.json — are the inputs real?")

cc = os.path.join(HERE, "canonical_case.json")
if not os.path.exists(cc):
    bad("canonical_case.json not found", "run canonical_case.py")
else:
    try:
        data = json.load(open(cc, encoding="utf-8"))
        print(json.dumps(data, indent=2)[:2400])
        flat = json.dumps(data)
        src = str(data.get("official_leg_source", ""))
        if re.search(r"temporary|test only|not verified|placeholder|TODO", src, re.I):
            bad(f"official_leg_source says: {src[:80]}",
                "the SBI sheets are on disk — verify and relabel")
        if "official_candidates" not in data:
            bad("canonical_case.json has no 'official_candidates' list",
                "node3_valuation.py needs both dates to enumerate the date choice")
        else:
            ok(f"official_candidates present ({len(data['official_candidates'])} dates)")
        peg_m = re.search(r'"peg"\s*:\s*([0-9.]+)', flat)
        if peg_m and float(peg_m.group(1)) == 1.0:
            bad("peg is exactly 1.0000 — the PLACEHOLDER",
                "read cache/binance_usdc_usdt_target.json instead")
        elif peg_m:
            ok(f"peg = {peg_m.group(1)} — retrieved, not assumed")
        for k in ("placeholder", "PLACEHOLDER", "TODO", "assumed"):
            if k in flat:
                warn(f"the word '{k}' appears in canonical_case.json", "check that field")
    except Exception as e:
        bad(f"canonical_case.json will not parse: {e}", "regenerate it")

cache = os.path.join(HERE, "cache")
if os.path.isdir(cache):
    for f in sorted(os.listdir(cache)):
        info(f"cache/{f}")
else:
    warn("no cache/ folder", "run killgate.py")

for f in sorted(os.listdir(HERE)):
    if re.match(r"2026-06-\d\d", f):
        ok(f"SBI rate sheet on disk: {f}")


# ─────────────────────────────────────────────────────────────
head("6. WHAT IS BUILT vs WHAT SCORES")

CHECK = [
    ("failure-catalogue.md",  "Step 10 · pre-registered failures"),
    ("baseline-prompt.md",    "Step 16 · frozen baseline"),
    ("iteration-log.md",      "documented iteration — a SCORED sub-criterion"),
    ("architecture.md",       "Step 19 · nodes + 'what fails without this'"),
    ("evaluation-design.md",  "Step 21 · the measure, defined in advance"),
    ("risks.md",              "Step 24 · edge cases"),
    ("results.md",            "Step 30 · results incl. losses"),
    ("output-interface.html", "the 60-point UX artifact"),
    ("scope.md",              "Step 14 · scope contract"),
    ("qa-prep.md",            "Step 37 · Q&A bank"),
]
for fn, why in CHECK:
    found = any(os.path.exists(os.path.join(r, fn))
                for r in (HERE, os.path.dirname(HERE)))
    print((OK if found else INFO) + f"{fn:<24} {'present' if found else 'NOT BUILT'}   {why}")

for d in ("prompts", "eval", "cases", "runs"):
    p = os.path.join(HERE, d)
    print((OK if os.path.isdir(p) else INFO) +
          f"{d + '/':<24} {'present' if os.path.isdir(p) else 'NOT BUILT'}")

print((OK if os.path.isdir(os.path.join(HERE, ".git")) else INFO) +
      f"{'.git/':<24} {'present' if os.path.isdir(os.path.join(HERE, '.git')) else 'NOT INITIALISED — pre-registration has no timestamp'}")


# ─────────────────────────────────────────────────────────────
head("VERDICT")

print(f"  {len(problems)} problem(s) that block Gate 0")
print(f"  {len(warnings)} warning(s)\n")
if problems:
    print("  FIX THESE FIRST, IN THIS ORDER:\n")
    for i, (m, f) in enumerate(problems, 1):
        print(f"   {i}. {m}\n      -> {f}")
if warnings:
    print("\n  THEN THESE:\n")
    for i, (m, f) in enumerate(warnings, 1):
        print(f"   {i}. {m}\n      -> {f}")
if not problems:
    print("  GATE 0 CLEAR on everything this script can see.")
print()
