# THREE PATCHES TO `citation_matcher.py`

## 1. Windows crash — do this first

Your run died with:
```
UnicodeEncodeError: 'charmap' codec can't encode character '✓'
```
Python 3.14 on Windows defaults the console to cp1252 and the self-test prints `✓`.
**It will crash on a judge's laptop too.** Add this directly under the imports:

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

## 2. The 4-digit-year bug — same one `gate0_check.py` had

`extract_refs()` reads the year in *"CGST Act 2017"* as a section number, so
`GST-CGST-50.md` and `GST-CGST-74A.md` both register a claim on "Section 2017".
Harmless today because nobody cites Section 2017 — but it is a real false match
waiting to happen. Inside `extract_refs`, replace:

```python
            for tok in re.findall(r"[0-9]+[A-Za-z]*(?:\([^)]+\))*", chunk):
                base, br = _split_number(tok)
                refs.append((kind, base, tuple(br)))
```

with:

```python
            for tok in re.findall(r"[0-9]+[A-Za-z]*(?:\([^)]+\))*", chunk):
                base, br = _split_number(tok)
                # A bare 4-digit 19xx/20xx is the Act's year, not a provision.
                if re.fullmatch(r"(19|20)\d\d", base) and not br:
                    continue
                refs.append((kind, base, tuple(br)))
```

## 3. ⭐ The self-test itself is stale — OWN-5

In `CASES`, this line asserts a belief that stopped being true on 1 April 2026:

```python
    ("Rule 115",  "FY 2026-27", "VERIFIED",  "in corpus (though inapplicable)"),
```

Rule 115 became **Rule 206** under the notified Income-tax Rules, 2026 (confirmed
from the CBDT Navigator, row 206). Once `IT-RULE-206.md` is retired and only
`ITR2026-RULE-206.md` remains — carrying `former_citation: "Rule 115, Income-tax
Rules, 1962"` — the correct verdict is **STALE**. Change it to:

```python
    ("Rule 115",  "FY 2026-27", "STALE",     "OUR OWN ERROR #5 — the self-test was stale"),
    ("Rule 115",  "FY 2025-26", "VERIFIED",  "correct FOR THAT YEAR"),
```

**This is not a test you are breaking. It is a test that encoded a stale belief,
and it passed 15/15 the whole time.** Log it in `failure-catalogue.md`:

```
| OWN-5 | Our own citation matcher's self-test asserted Rule 115 was current for
          FY 2026-27, four months after it became Rule 206. | Class 3 | The test
          passed 15/15 throughout. Found by gate0_check.py flagging two files
          claiming the same provision — not by anyone reading it. |
```

**Five stale citations now, and this is the first one caught by a tool rather
than by a human.** That is the strongest possible version of the story: the
process that catches staleness caught its own test.
