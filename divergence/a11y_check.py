#!/usr/bin/env python3
"""
A11Y CHECK — DIVERGENCE
Deterministic accessibility audit of a generated disclosure page. Standard
library only, nothing to install — same philosophy as gate0_check.py.

This project claimed real accessibility work (heading hierarchy, a <main>
landmark, aria-labelledby per section, role="img" with a spoken number,
lang, prefers-reduced-motion) since decision D34/D53, but until this script
existed, nothing had actually verified any of it beyond a human reading the
HTML by eye. This checks it mechanically, every time a page is generated.

    python a11y_check.py output-interface.html
    python a11y_check.py --all          # every *.html in this folder

Checks:
  1. Real WCAG contrast ratios, computed from the actual CSS custom
     properties, not just "a color variable exists somewhere."
  2. <html lang="..."> present.
  3. Exactly one <h1>; no heading level skipped (h1 -> h3 with no h2).
  4. A <main> landmark exists.
  5. Every <input> has an associated <label for=...> or an aria-label/
     aria-labelledby.
  6. Every element carrying role="img" has a non-empty aria-label.
  7. Every <button> has visible text content or an aria-label.
  8. prefers-reduced-motion is respected somewhere in the page's CSS.

Exit code: 1 if any check fails, 0 if all pass. Wire into CI the same way
gate0_check.py and citation_matcher.py's self-test already are, if this
should be a real gate rather than a report.
"""

import os
import re
import sys
import argparse
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))

# The actual custom-property colors this project's CSS defines (see
# node7_disclosure.py's :root block). Kept here as a constant, not parsed
# from the generated HTML's inline <style>, so a change to the design
# system is a deliberate, visible diff in two files, not a silent drift.
COLORS = {
    "paper": "#F1F3F2", "paper-rule": "#D3DAD7", "ink": "#161C19",
    "ink-soft": "#4A5551", "ink-faint": "#666F6B", "margin-red": "#9E2F26",
    "figure": "#22405A", "elected": "#4F6140",
}

# (foreground, background, where it's actually used, minimum ratio required)
# 4.5:1 is WCAG AA for normal text; 3:1 for large/bold text (>=18px or
# >=14px bold) -- the .label/.sec-n classes are bold 10-13px monospace,
# treated as normal text here to be conservative rather than borderline.
TEXT_PAIRS = [
    ("ink", "paper", "body text", 4.5),
    ("ink-soft", "paper", "secondary text (.sub, .lede, .r-body)", 4.5),
    ("ink-faint", "paper", "labels (.label, .ink-faint uses)", 4.5),
    ("margin-red", "paper", "section numbers, the dimension value", 4.5),
    ("figure", "paper", "money figures (.amt)", 4.5),
    ("elected", "paper", "the one-answer box, election confirmation", 4.5),
]


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _relative_luminance(hex_color):
    r, g, b = _hex_to_rgb(hex_color)
    r, g, b = _srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex_a, hex_b):
    la, lb = _relative_luminance(hex_a), _relative_luminance(hex_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


class A11yParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.headings = []       # [(level, text_so_far)]
        self.has_main = False
        self.inputs = []         # [(id, has_aria_label)]
        self.labels_for = set()  # ids referenced by <label for="...">
        self.role_imgs = []      # [aria_label or None]
        self.buttons = []        # [(has_text_flag list to fill, has_aria)]
        self._cur_heading_level = None
        self._cur_button = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html" and "lang" in a:
            self.lang = a["lang"]
        if tag == "main":
            self.has_main = True
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._cur_heading_level = int(tag[1])
            self.headings.append([self._cur_heading_level, ""])
        if tag == "input":
            self.inputs.append([a.get("id"), bool(a.get("aria-label") or a.get("aria-labelledby"))])
        if tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])
        if a.get("role") == "img":
            self.role_imgs.append(a.get("aria-label"))
        if tag == "button":
            self._cur_button = [False, bool(a.get("aria-label"))]
            self.buttons.append(self._cur_button)

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._cur_heading_level = None
        if tag == "button":
            self._cur_button = None

    def handle_data(self, data):
        if self._cur_heading_level is not None and self.headings:
            self.headings[-1][1] += data
        if self._cur_button is not None and data.strip():
            self._cur_button[0] = True


def check_file(path):
    text = open(path, encoding="utf-8").read()
    p = A11yParser()
    p.feed(text)
    problems, oks = [], []

    # 1. Contrast
    for fg, bg, where, minimum in TEXT_PAIRS:
        ratio = contrast_ratio(COLORS[fg], COLORS[bg])
        if ratio < minimum:
            problems.append(f"contrast {fg} on {bg} ({where}): {ratio:.2f}:1, needs >= {minimum}:1")
        else:
            oks.append(f"contrast {fg} on {bg} ({where}): {ratio:.2f}:1 OK")

    # 2. lang
    if not p.lang:
        problems.append("<html> has no lang attribute")
    else:
        oks.append(f'<html lang="{p.lang}">')

    # 3. Heading hierarchy
    h1s = [h for h in p.headings if h[0] == 1]
    if len(h1s) != 1:
        problems.append(f"expected exactly one <h1>, found {len(h1s)}")
    else:
        oks.append("exactly one <h1>")
    prev = 0
    skipped = False
    for level, _txt in p.headings:
        if prev and level > prev + 1:
            problems.append(f"heading level skipped: h{prev} to h{level}")
            skipped = True
        prev = level
    if not skipped and len(p.headings) > 1:
        oks.append("no heading level skipped")

    # 4. <main>
    if not p.has_main:
        problems.append("no <main> landmark")
    else:
        oks.append("<main> landmark present")

    # 5. Inputs have labels
    unlabelled = 0
    for input_id, has_aria in p.inputs:
        if has_aria:
            continue
        if not input_id or input_id not in p.labels_for:
            unlabelled += 1
            problems.append(f"<input id={input_id!r}> has no associated <label for> or aria-label")
    if p.inputs and unlabelled == 0:
        oks.append(f"all {len(p.inputs)} <input> element(s) properly labelled")

    # 6. role="img" has aria-label
    for label in p.role_imgs:
        if not label:
            problems.append('an element with role="img" has no aria-label')
    if p.role_imgs and all(p.role_imgs):
        oks.append(f'all {len(p.role_imgs)} role="img" element(s) have aria-label')

    # 7. Buttons have accessible text
    for has_text, has_aria in p.buttons:
        if not has_text and not has_aria:
            problems.append("a <button> has neither visible text nor aria-label")
    if p.buttons and all(t or a for t, a in p.buttons):
        oks.append(f"all {len(p.buttons)} <button> element(s) have accessible text")

    # 8. prefers-reduced-motion
    if "prefers-reduced-motion" not in text:
        problems.append("no prefers-reduced-motion media query found")
    else:
        oks.append("prefers-reduced-motion respected")

    return problems, oks


def main():
    ap = argparse.ArgumentParser(description="Deterministic accessibility audit")
    ap.add_argument("files", nargs="*", help="HTML file(s) to check")
    ap.add_argument("--all", action="store_true", help="check every *.html in this folder")
    a = ap.parse_args()

    files = a.files
    if a.all or not files:
        files = sorted(f for f in os.listdir(HERE) if f.endswith(".html"))

    total_problems = 0
    for fn in files:
        path = fn if os.path.isabs(fn) else os.path.join(HERE, fn)
        if not os.path.exists(path):
            print(f"  [--] {fn}: not found")
            continue
        problems, oks = check_file(path)
        print(f"\n{'=' * 72}\n  {fn}\n{'=' * 72}")
        for o in oks:
            print(f"  [OK]  {o}")
        for pr in problems:
            print(f"  [XX]  {pr}")
        if not problems:
            print("  All checks passed.")
        total_problems += len(problems)

    print(f"\n{'=' * 72}\n  {total_problems} problem(s) across {len(files)} file(s)\n{'=' * 72}")
    sys.exit(1 if total_problems else 0)


if __name__ == "__main__":
    main()
