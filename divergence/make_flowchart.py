#!/usr/bin/env python3
"""
MAKE FLOWCHART — DIVERGENCE
Regenerates flowchart.png from scratch via matplotlib (not a Mermaid
export) so the track's literal requirement -- real model names, explicit
human-input markers -- is satisfied inside the image itself, not only in
flowchart.md's alt text. No generator script existed for the original
image (built once, by hand, in a throwaway session); this is that script,
checked in so the next real change to the pipeline's shape doesn't mean
redrawing from a screenshot again.

    python make_flowchart.py

Font note: the 🤖 robot emoji does not render in matplotlib's default font
on this machine -- silently drops to a missing-glyph box. Replaced with a
plain "[LLM]" tag throughout (⚙, the gear character, renders fine and is
kept). Same fix as the first version of this image.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrow

ORANGE_FILL, ORANGE_EDGE, ORANGE_TEXT = "#FBD9BE", "#C2571A", "#7A3200"
GREEN_FILL, GREEN_EDGE, GREEN_TEXT = "#D2F2E0", "#1A7A4C", "#0A3D24"
PURPLE_FILL, PURPLE_EDGE, PURPLE_TEXT = "#E8D9F5", "#6A3FA0", "#3A1F5C"

W = 100.0
FIG_W = 14.0

fig_height_units = 190
fig, ax = plt.subplots(figsize=(FIG_W, FIG_W * fig_height_units / W))
ax.set_xlim(0, W)
ax.set_ylim(0, fig_height_units)
ax.invert_yaxis()
ax.axis("off")

y = 4.0


def box(x0, y0, w, h, fill, edge, lines, textcolor="#111", header_color=None):
    ax.add_patch(FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle="round,pad=0,rounding_size=1.4",
        linewidth=2.4, edgecolor=edge, facecolor=fill, zorder=2))
    cy = y0 + 1.6
    for kind, text in lines:
        if kind == "header":
            ax.text(x0 + w / 2, cy, text, ha="center", va="top",
                     fontsize=15, fontweight="bold", color="#111", zorder=3)
            cy += 2.6
        elif kind == "model":
            ax.text(x0 + w / 2, cy, text, ha="center", va="top",
                     fontsize=11.5, fontweight="bold",
                     color=header_color or "#111", zorder=3)
            cy += 2.3
        elif kind == "gap":
            cy += 1.0
        elif kind == "body":
            ax.text(x0 + w / 2, cy, text, ha="center", va="top",
                     fontsize=10.5, color="#222", zorder=3)
            cy += 1.7
        elif kind == "action":
            ax.text(x0 + w / 2, cy, text, ha="center", va="top",
                     fontsize=9.5, style="italic", color="#444", zorder=3)
            cy += 1.6
    return y0 + h


def arrow(x, y0, y1):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="-|>", color="#555",
                                 lw=2.2, mutation_scale=22), zorder=1)


CX, BW = W / 2, 86

# Title
ax.text(CX, y, "DIVERGENCE — pipeline flowchart", ha="center", va="top",
         fontsize=25, fontweight="bold", color="#111")
y += 3.6
ax.text(CX, y, "Purple = human input required · Orange = LLM call (can be wrong) · "
        "Green = deterministic code (cannot invent)",
        ha="center", va="top", fontsize=11.5, color="#333")
y += 4.5

x0 = (W - BW) / 2

# 1. HUMAN INPUT — REQUIRED
h = 8.0
y1 = box(x0, y, BW, h, PURPLE_FILL, PURPLE_EDGE, [
    ("header", "HUMAN INPUT — REQUIRED"),
    ("gap", ""),
    ("body", "Invoice + payment record, as PDF, photo, or typed text. "
             "The pipeline cannot start without this."),
], header_color=PURPLE_TEXT)
prev_x, prev_bottom = CX, y1
y = y1 + 1.5

# 2. [LLM] 1 EXTRACT
h = 15.5
y1 = box(x0, y, BW, h, ORANGE_FILL, ORANGE_EDGE, [
    ("header", "[LLM] 1  EXTRACT"),
    ("model", "MODEL: Qwen/Qwen2.5-7B-Instruct  (via Featherless)"),
    ("gap", ""),
    ("body", 'QUERY: "Pull structured facts (amount, asset, dates, counterparty) '
             'out of this raw document.'),
    ("body", 'Tag each field with a confidence level and where it came from."'),
    ("gap", ""),
    ("action", "ACTION: writes facts{} — the only step that reads the raw human input directly."),
], header_color=ORANGE_TEXT)
arrow(CX, prev_bottom, y)
prev_bottom = y1
y = y1 + 1.5

# 3. [LLM] 2 GAP DETECTOR
h = 15.5
y1 = box(x0, y, BW, h, ORANGE_FILL, ORANGE_EDGE, [
    ("header", "[LLM] 2  GAP DETECTOR"),
    ("model", "MODEL: Qwen/Qwen2.5-7B-Instruct  (via Featherless)"),
    ("gap", ""),
    ("body", 'QUERY: "Given these facts and what GST/FEMA/income-tax evidence '
             'requirements exist,'),
    ("body", 'what is missing? This runs BEFORE any conclusion is reasoned."'),
    ("gap", ""),
    ("action", "ACTION: writes missing[], each with why it's absent and what it blocks."),
], header_color=ORANGE_TEXT)
arrow(CX, prev_bottom, y)
prev_bottom = y1
y = y1 + 1.5

# 4. SPLIT — [LLM] 3 / [LLM] 4
# Note, 21 Aug: reordered against the ORIGINAL 19 Aug diagram, which drew
# ⚙ A and ⚙ B here, before the resolvers. Checked directly against
# run_pipeline.py while wiring in ⚙ E (D59): node_resolver.resolve()'s own
# signature takes facts/missing/tax_year only, never valuation, and
# gap_enforcer.enforce() is not called until AFTER citation matching, near
# the end of the automated chain. This diagram now matches that call
# order; the previous shape was never actually run this way. See
# PIPELINE-FLOW.md's own 21 Aug correction note for the same finding.
h = 17.0
half_w = BW / 2 - 1.5
lx0 = x0
rx0 = x0 + BW / 2 + 1.5
box(lx0, y, half_w, h, ORANGE_FILL, ORANGE_EDGE, [
    ("header", "[LLM] 3  INCOME TAX RESOLVER"),
    ("model", "MODEL: Qwen/Qwen2.5-72B-Instruct"),
    ("body", 'QUERY: "Given ONLY these verbatim income-tax'),
    ("body", 'provisions + facts + gaps, resolve classification,'),
    ("body", 'valuation method, TDS and penalty — cite what'),
    ("body", 'you rest each conclusion on, and how settled it is."'),
    ("gap", ""),
    ("action", "ACTION: writes regime conclusions with"),
    ("action", "citation + certainty label (settled/lacuna/etc)."),
], header_color=ORANGE_TEXT)
y1r = box(rx0, y, half_w, h, ORANGE_FILL, ORANGE_EDGE, [
    ("header", "[LLM] 4  GST RESOLVER"),
    ("model", "MODEL: Qwen/Qwen2.5-72B-Instruct"),
    ("body", 'QUERY: "Given ONLY these verbatim GST'),
    ("body", 'provisions + facts + gaps, resolve whether this'),
    ("body", 'is an export of services — five conditions,'),
    ("body", 'each checked against the facts."'),
    ("gap", ""),
    ("action", "ACTION: writes GST regime conclusion,"),
    ("action", "same citation + certainty contract."),
], header_color=ORANGE_TEXT)
ax.annotate("", xy=(lx0 + half_w / 2, y - 0.3), xytext=(CX, prev_bottom),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=2.2,
                             mutation_scale=22, connectionstyle="arc3,rad=-0.15"))
ax.annotate("", xy=(rx0 + half_w / 2, y - 0.3), xytext=(CX, prev_bottom),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=2.2,
                             mutation_scale=22, connectionstyle="arc3,rad=0.15"))
prev_bottom = y + h
y = prev_bottom + 2.2

# 7. ⚙ C CITATION MATCHER
h = 10.5
ax.annotate("", xy=(CX, y), xytext=(lx0 + half_w / 2, prev_bottom + 0.3),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=2.2,
                             mutation_scale=22, connectionstyle="arc3,rad=0.15"))
ax.annotate("", xy=(CX, y), xytext=(rx0 + half_w / 2, prev_bottom + 0.3),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=2.2,
                             mutation_scale=22, connectionstyle="arc3,rad=-0.15"))
y1 = box(x0, y, BW, h, GREEN_FILL, GREEN_EDGE, [
    ("header", "⚙ C  CITATION MATCHER   —   NO MODEL. STRING MATCH + DATE CHECK."),
    ("gap", ""),
    ("body", "ACTION: every citation is checked against real corpus text AND the correct tax year."),
    ("body", "If it fails, the WHOLE conclusion resting on it is DROPPED, not flagged."),
], header_color=GREEN_TEXT)
prev_bottom = y1
y = y1 + 1.5

# 8. ⚙ E SCOPE-REACH ENFORCER  (new, 21 Aug, D59)
h = 12.5
y1 = box(x0, y, BW, h, GREEN_FILL, GREEN_EDGE, [
    ("header", "⚙ E  SCOPE-REACH ENFORCER   —   NO MODEL. 3 HAND-VERIFIED RULES."),
    ("gap", ""),
    ("body", "ACTION: drops any KEPT conclusion whose citation exists and is current but"),
    ("body", "doesn't reach these facts (Rule 206/207, Rule 57, Rule 243/247 vs a VDA)."),
    ("action", "Exempts certainty=lacuna — citing a rule to prove it's absent is not the error."),
], header_color=GREEN_TEXT)
arrow(CX, prev_bottom, y)
prev_bottom = y1
y = y1 + 1.5

# 9. ⚙ A GAP CONSTRAINT ENFORCER
h = 10.5
y1 = box(x0, y, BW, h, GREEN_FILL, GREEN_EDGE, [
    ("header", "⚙ A  GAP CONSTRAINT ENFORCER   —   NO MODEL. PLAIN CODE."),
    ("gap", ""),
    ("body", 'ACTION: any conclusion depending on a missing fact has certainty forced to'),
    ("body", '"insufficient_evidence" — in an if-statement, unconditionally, regardless of model confidence.'),
], header_color=GREEN_TEXT)
arrow(CX, prev_bottom, y)
prev_bottom = y1
y = y1 + 1.5

# 10. ⚙ B VALUATION LATTICE
h = 10.5
y1 = box(x0, y, BW, h, GREEN_FILL, GREEN_EDGE, [
    ("header", "⚙ B  VALUATION LATTICE   —   NO MODEL. NO API. PLAIN ARITHMETIC."),
    ("gap", ""),
    ("body", "ACTION: enumerates every combination of official date × market reading × currency"),
    ("body", "proxy from real sourced data (bank rate sheets, exchange candles). Always ≥1 figure, never invented."),
], header_color=GREEN_TEXT)
arrow(CX, prev_bottom, y)
prev_bottom = y1
y = y1 + 1.5

# 11. [LLM] 5 ADVERSARIAL CHECKER
h = 15.5
y1 = box(x0, y, BW, h, ORANGE_FILL, ORANGE_EDGE, [
    ("header", "[LLM] 5  ADVERSARIAL CHECKER"),
    ("model", "MODEL: mistralai/Mistral-Large-Instruct-2411 — DELIBERATELY A DIFFERENT MODEL FAMILY"),
    ("gap", ""),
    ("body", 'QUERY: "Here are every conclusion above, the full statute, the gap list and the'),
    ("body", 'valuation lattice. Attack each conclusion. Say whether your attack landed. Publish it either way."'),
    ("gap", ""),
    ("action", "ACTION: writes attacked[] and checked_and_survived[] — never silently improves the answer, only critiques it on the record."),
], header_color=ORANGE_TEXT)
arrow(CX, prev_bottom, y)
prev_bottom = y1
y = y1 + 1.5

# 10. ⚙ D DISCLOSURE COMPOSER
h = 10.5
y1 = box(x0, y, BW, h, GREEN_FILL, GREEN_EDGE, [
    ("header", "⚙ D  DISCLOSURE COMPOSER   —   NO MODEL. DETERMINISTIC TEMPLATE."),
    ("gap", ""),
    ("body", "ACTION: renders the final page — absence first, the range second, a single figure"),
    ("body", "never, the attacks against it always shown. Ordering is fixed in code, not a model's choice."),
], header_color=GREEN_TEXT)
arrow(CX, prev_bottom, y)
prev_bottom = y1
y = y1 + 1.5

# 11. HUMAN INPUT — OPTIONAL
h = 9.5
y1 = box(x0, y, BW, h, PURPLE_FILL, PURPLE_EDGE, [
    ("header", "HUMAN INPUT — OPTIONAL, NEVER REQUIRED"),
    ("gap", ""),
    ("body", "The taxpayer may tick which figure they end up filing."),
    ("body", "No default is pre-selected — the record is already complete and valid without this."),
], header_color=PURPLE_TEXT)
arrow(CX, prev_bottom, y)
ax.text(x0 + BW + 1, y + h - 1.5, "→ output-\ninterface.html",
        ha="left", va="bottom", fontsize=9.5, style="italic", color="#555")
y = y1 + 6

# Legend
leg_y = y
leg_items = [
    (PURPLE_FILL, PURPLE_EDGE, "Human input point"),
    (ORANGE_FILL, ORANGE_EDGE, "LLM call — can be wrong"),
    (GREEN_FILL, GREEN_EDGE, "Deterministic code — cannot invent"),
]
lx = x0 + 4
for fill, edge, label in leg_items:
    ax.add_patch(FancyBboxPatch((lx, leg_y), 4, 3.2, boxstyle="round,pad=0,rounding_size=0.6",
                                 linewidth=2, edgecolor=edge, facecolor=fill, zorder=2))
    ax.text(lx + 5.2, leg_y + 1.6, label, ha="left", va="center", fontsize=11, color="#222")
    lx += 5.2 + len(label) * 0.62 + 4

fig_total_height = y + 8
ax.set_ylim(fig_total_height, 0)
fig.set_size_inches(FIG_W, FIG_W * fig_total_height / W)

out = "flowchart.png"
plt.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
print(f"written -> {out}")
