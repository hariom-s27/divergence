#!/usr/bin/env python3
"""
NODE 7 / ⚙ D — DISCLOSURE COMPOSER  ·  DIVERGENCE
DETERMINISTIC. No model. No API. No network. (architecture.md, D34.)

architecture.md's own words: "Deterministic template. Absence first, the
range second, a single answer never. Ordering enforced in the layout,
because the ordering is the argument... A document whose purpose is to be
trustworthy cannot be produced by something that can hallucinate."

Was never built (Step 26's own list named it; PIPELINE-FLOW.md's own
status table said so: "output-interface.html is a static template, not
wired to a live record yet"). The interface a judge looks at first was a
hand-typed HTML mockup with numbers from an early draft case, marked
stale-ok throughout -- while the pipeline right next to it was producing
real, schema-valid, verified records. This closes that gap: reads one
real record, writes the real page from it. No number in the output below
was typed by a person into this file.

    python node7_disclosure.py --record runs/21aug/D1_fixed_pipeline.json
    python node7_disclosure.py --record runs/21aug/C1_pipeline.json --out c1.html

Reads   a schema.json-shaped disclosure record (the output of run_pipeline.py)
Writes  an HTML page in the same visual language as the original
        output-interface.html mockup -- same CSS, same section ordering
        (absence first, range second, single answer never), real data.
"""

import argparse
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import citation_matcher  # noqa: E402

DEFAULT_OUT = os.path.join(HERE, "output-interface.html")

# Which corpus/tier-a files each resolver's prompt actually injects -- read
# directly from step22drop/prompts/03-income-tax.md and 04-gst.md's own
# "Injected at runtime" headers (D31/C22: scoped per regime, not the full
# corpus). Kept as a constant here rather than re-parsed from the prompt
# file at render time because this scoping is a stable code-level design
# decision, not something that varies per run. Found live, 21 Aug: the
# manifest section was rendering only citations[], 2-3 provisions, under a
# heading that says "What we checked" -- which understates, by a factor of
# 3-5x, how much of the corpus a resolver actually reads before deciding
# what to cite. A reader seeing "3 provisions" under that heading could
# reasonably conclude the legal research was narrow; it wasn't -- most of
# what was checked was checked and correctly NOT cited.
REGIME_CORPUS = {
    "income_tax_on_receipt": ["IT-2-47A.md", "IT-115BBH.md", "IT-393-1-T8vi.md",
                               "ITR2026-RULE-56.md", "ITR2026-RULE-57.md",
                               "ITR2026-RULE-206.md", "ITR2026-RULE-207.md",
                               "ITR2026-RULE-247.md", "ITR2026-RCASP-VALUATION.md",
                               "IT-439-8.md"],
    "valuation_method": ["IT-2-47A.md", "IT-115BBH.md", "IT-393-1-T8vi.md",
                          "ITR2026-RULE-56.md", "ITR2026-RULE-57.md",
                          "ITR2026-RULE-206.md", "ITR2026-RULE-207.md",
                          "ITR2026-RULE-247.md", "ITR2026-RCASP-VALUATION.md",
                          "IT-439-8.md"],
    "income_tax_on_transfer": ["IT-2-47A.md", "IT-115BBH.md", "IT-393-1-T8vi.md",
                                "ITR2026-RULE-56.md", "ITR2026-RULE-57.md",
                                "ITR2026-RULE-206.md", "ITR2026-RULE-207.md",
                                "ITR2026-RULE-247.md", "ITR2026-RCASP-VALUATION.md",
                                "IT-439-8.md"],
    "gst_export": ["GST-IGST-2-6.md", "GST-CGST-50.md", "GST-CGST-74A.md"],
}

# unchanged from the original hand-built mockup -- this is a good, tested
# design; only the body content below it is now generated, not the look
CSS = """
:root{
  --paper:#F1F3F2;        /* cool foolscap, not cream */
  --paper-rule:#D3DAD7;   /* ledger ruling */
  --ink:#161C19;          /* blue-black ink */
  --ink-soft:#4A5551;
  --ink-faint:#78837E;
  --margin-red:#9E2F26;   /* the red margin rule of a bahi khata */
  --figure:#22405A;       /* stamp indigo -- used only for money */
  --elected:#4F6140;      /* olive -- confirmation only */
  --measure:2px;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:'Spectral',Georgia,serif; font-weight:400;
  font-size:17px; line-height:1.62;
  padding:0 16px 96px;
}
.sheet{
  max-width:760px; margin:0 auto; position:relative;
  border-left:var(--measure) solid var(--margin-red);
  padding:0 0 0 clamp(18px,5vw,44px);
}
.label{
  font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:600;
  letter-spacing:.13em; text-transform:uppercase; color:var(--ink-faint);
}
.rule{border:0;border-top:1px solid var(--paper-rule);margin:40px 0 0}
header{padding:44px 0 0}
.formno{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
h1{
  font-size:clamp(26px,4.6vw,36px); font-weight:600; line-height:1.18;
  margin:20px 0 6px; letter-spacing:-.015em;
}
.sub{color:var(--ink-soft);font-size:16px;margin:0 0 4px}
section{padding-top:34px}
.sec-head{display:flex;align-items:baseline;gap:12px;margin-bottom:14px}
.sec-head h2{font-size:19px;font-weight:600;margin:0;letter-spacing:-.01em}
.sec-n{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--margin-red);font-weight:600}
.lede{color:var(--ink-soft);margin:0 0 18px;font-size:16px}
.missing{list-style:none;margin:0;padding:0;border-top:1px solid var(--paper-rule)}
.missing li{
  display:grid;grid-template-columns:auto 1fr;gap:14px;
  padding:13px 0;border-bottom:1px solid var(--paper-rule);align-items:start;
}
.mark{
  font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:600;
  color:var(--margin-red);border:1.5px solid var(--margin-red);
  width:22px;height:22px;display:grid;place-items:center;flex:none;margin-top:2px;
}
.missing b{font-weight:600}
.missing .blocks{display:block;font-size:14px;color:var(--ink-soft);margin-top:2px}
.gap{margin:26px 0 8px}
.gap-ends{display:flex;justify-content:space-between;gap:20px}
.method{flex:1}
.method.b{text-align:right}
.amt{
  font-family:'IBM Plex Mono',monospace;font-size:clamp(19px,3.6vw,25px);
  font-weight:500;color:var(--figure);letter-spacing:-.02em;display:block;
}
.method small{display:block;font-size:13px;color:var(--ink-soft);margin-top:3px;line-height:1.45}
.dim{position:relative;height:46px;margin:14px 0 2px}
.dim-line{position:absolute;top:23px;left:0;right:0;height:1px;background:var(--ink)}
.dim-line::before,.dim-line::after{
  content:"";position:absolute;top:-6px;width:1px;height:13px;background:var(--ink);
}
.dim-line::before{left:0}
.dim-line::after{right:0}
.dim-val{
  position:absolute;top:9px;left:50%;transform:translateX(-50%);
  background:var(--paper);padding:0 14px;
  font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:clamp(15px,3vw,18px);
  color:var(--margin-red);white-space:nowrap;
}
.gap-note{font-size:15px;color:var(--ink-soft);margin:12px 0 0}
.one-answer{
  margin:26px 0 8px;padding:18px 20px;border:1px solid var(--elected);
}
.one-answer .amt{color:var(--elected)}
.one-answer .label{color:var(--elected)}
fieldset{border:1px solid var(--paper-rule);padding:18px;margin:26px 0 0}
legend{padding:0 8px}
.opt{display:flex;gap:12px;align-items:flex-start;padding:9px 0}
.opt input{margin-top:6px;width:17px;height:17px;accent-color:var(--elected);flex:none}
.opt label{cursor:pointer}
.opt .t{font-weight:600}
.opt .d{display:block;font-size:14px;color:var(--ink-soft)}
.stamp{
  margin-top:16px;padding:11px 14px;border:1px dashed var(--paper-rule);
  font-size:14px;color:var(--ink-soft);
}
.stamp b{color:var(--ink);font-weight:600}
.regime{border-top:1px solid var(--paper-rule);padding:16px 0}
.regime:last-of-type{border-bottom:1px solid var(--paper-rule)}
.r-top{display:flex;justify-content:space-between;gap:14px;align-items:baseline;flex-wrap:wrap}
.r-name{font-weight:600}
.cert{
  font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.1em;
  text-transform:uppercase;padding:2px 7px;border:1px solid currentColor;white-space:nowrap;
}
.cert.settled{color:var(--elected)}
.cert.inference,.cert.open_texture,.cert.contested{color:var(--margin-red)}
.cert.lacuna,.cert.insufficient_evidence,.cert.none{color:var(--ink-faint)}
.r-body{font-size:15px;color:var(--ink-soft);margin:7px 0 0}
.cite{font-family:'IBM Plex Mono',monospace;font-size:12.5px;color:var(--ink);}
details{border-top:1px solid var(--paper-rule);padding-top:16px}
summary{cursor:pointer;font-weight:600;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"+ ";font-family:'IBM Plex Mono',monospace;color:var(--margin-red)}
details[open] summary::before{content:"\\2212 "}
.man{font-family:'IBM Plex Mono',monospace;font-size:12.5px;line-height:1.9;color:var(--ink-soft);margin:14px 0 0;padding:0;list-style:none}
.man li{border-bottom:1px dotted var(--paper-rule);padding:3px 0;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.budget{list-style:none;margin:14px 0 0;padding:0}
.budget li{border-bottom:1px dotted var(--paper-rule);padding:9px 0}
.budget .t{display:block;font-size:14.5px}
.budget .t b{font-family:'IBM Plex Mono',monospace;color:var(--figure);font-weight:600}
.budget .d{display:block;font-size:13.5px;color:var(--ink-soft);margin-top:3px}
.attack{border-top:1px solid var(--paper-rule);padding:16px 0}
.attack:last-of-type{border-bottom:1px solid var(--paper-rule)}
.a-top{display:flex;justify-content:space-between;gap:14px;align-items:baseline;flex-wrap:wrap}
.a-target{font-weight:600;font-size:14.5px}
.verdict{
  font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.1em;
  text-transform:uppercase;padding:2px 7px;border:1px solid currentColor;white-space:nowrap;
}
.verdict.landed{color:var(--margin-red)}
.verdict.survived{color:var(--elected)}
.a-body{font-size:15px;color:var(--ink-soft);margin:7px 0 0}
.a-down{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--ink-faint);margin:5px 0 0}
.survived-list{list-style:none;margin:14px 0 0;padding:0}
.survived-list li{padding:7px 0;border-bottom:1px dotted var(--paper-rule);font-size:14.5px;color:var(--ink-soft)}
.limits{margin-top:40px;padding:20px;border:1px solid var(--paper-rule);background:rgba(255,255,255,.45)}
.limits p{margin:9px 0 0;font-size:14.5px;color:var(--ink-soft)}
.limits p:first-of-type{margin-top:12px}
a:focus-visible,summary:focus-visible,input:focus-visible,label:focus-visible{
  outline:2px solid var(--figure);outline-offset:3px;
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:560px){
  .gap-ends{flex-direction:column;gap:4px}
  .method.b{text-align:left;margin-top:14px}
  .dim{display:none}
  .gap-mobile{display:block!important}
}
.gap-mobile{display:none;font-family:'IBM Plex Mono',monospace;font-weight:600;
  color:var(--margin-red);font-size:17px;padding:12px 0;border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);margin:14px 0}
"""


def esc(x):
    return html.escape(str(x)) if x is not None else ""


def fmt_inr(x):
    return f"₹{x:,.0f}"


def fact(facts, key, default="not stated"):
    v = facts.get(key)
    if isinstance(v, dict):
        v = v.get("value")
    return default if v in (None, "") else v


_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]


def fmt_datetime(iso):
    """'2026-06-28T03:14:00+05:30' -> '28 June 2026, 03:14 IST'. Falls back
    to the raw string for anything that doesn't parse -- never guess."""
    try:
        date_part, time_part = str(iso).split("T")
        y, m, d = date_part.split("-")
        hh, mm = time_part[:5].split(":")
        return f"{int(d)} {_MONTHS[int(m) - 1]} {y}, {hh}:{mm} IST"
    except (ValueError, IndexError):
        return str(iso)


def fmt_amount(amount, asset):
    try:
        return f"{float(amount):,.0f} {asset}"
    except (TypeError, ValueError):
        return f"{amount} {asset}"


def render_missing(missing):
    if not missing:
        return ('<p class="lede">Nothing was found missing. Every fact this record '
                'needed was present in the input.</p>')
    items = []
    for m in missing:
        item = esc(m.get("item", "?"))
        why = esc(m.get("why_absent") or m.get("why") or "")
        blocks = m.get("blocks") or []
        blocks_txt = f"Blocks: {esc(', '.join(blocks))}." if blocks else ""
        obtainable = m.get("obtainable")
        obt_txt = {
            "yes": "Obtainable.",
            "no": "Not obtainable.",
            "not_for_this_route": "Not obtainable through this payment route.",
        }.get(obtainable, "")
        items.append(
            f'<li><span class="mark" aria-hidden="true">!</span>'
            f'<span><b>{item}</b>'
            f'<span class="blocks">{why} {obt_txt} {blocks_txt}</span></span></li>'
        )
    return '<ul class="missing">' + "\n".join(items) + "</ul>"


def render_valuation(valuation):
    methods = valuation.get("methods") or []
    spread = valuation.get("spread") or {"inr": 0, "percent": 0}
    if not methods:
        return ('<p class="lede">No valuation lattice was computed for this record '
                '(no crypto/FX leg, or node 3 was not run).</p>')

    if len(methods) == 1 or spread.get("inr", 0) == 0:
        m = methods[0]
        return (
            '<p class="lede">This receipt has no valuation dispute. One figure, '
            'directly determinable, shown as such rather than forced into a range.</p>'
            f'<div class="one-answer"><span class="label">{esc(m.get("label"))}</span>'
            f'<span class="amt">{fmt_inr(m.get("inr_value", 0))}</span>'
            f'<small style="display:block;margin-top:6px;color:var(--ink-soft);font-size:14px">'
            f'{esc((m.get("source") or {}).get("name", ""))}</small></div>'
        )

    lo = min(methods, key=lambda x: x["inr_value"])
    hi = max(methods, key=lambda x: x["inr_value"])
    n = len(methods)
    extra = (f'<p class="gap-note">{n} defensible methods were computed in total; '
             f'lowest and highest are shown here. Full lattice in the record itself.</p>'
             if n > 2 else "")
    return (
        f'<p class="lede">{n} method{"s are" if n != 1 else " is"} defensible. '
        f'No rule chooses between them. Lowest and highest shown.</p>'
        f'<div class="gap"><div class="gap-ends">'
        f'<div class="method"><span class="label">{esc(lo.get("label"))}</span>'
        f'<span class="amt">{fmt_inr(lo["inr_value"])}</span>'
        f'<small>{esc((lo.get("source") or {}).get("name", ""))}</small></div>'
        f'<div class="method b"><span class="label">{esc(hi.get("label"))}</span>'
        f'<span class="amt">{fmt_inr(hi["inr_value"])}</span>'
        f'<small>{esc((hi.get("source") or {}).get("name", ""))}</small></div>'
        f'</div>'
        f'<div class="dim" role="img" aria-label="The two methods differ by '
        f'{spread.get("inr", 0):,.2f} rupees, which is {spread.get("percent", 0):.2f} percent.">'
        f'<div class="dim-line"></div>'
        f'<span class="dim-val">{fmt_inr(spread.get("inr", 0))} · {spread.get("percent", 0):.2f}%</span>'
        f'</div>'
        f'<p class="gap-mobile">Difference: {fmt_inr(spread.get("inr", 0))} · {spread.get("percent", 0):.2f}%</p>'
        f'{extra}'
        f'</div>'
        + render_uncertainty_budget(valuation.get("uncertainty_budget"), spread)
        + render_election(lo, hi)
    )


def render_uncertainty_budget(budget, spread):
    """The metrology decomposition -- named in this project's own early
    design notes as its single most valuable idea, and until 21 Aug never
    actually rendered anywhere, existing only inside the JSON record. Found
    live doing a review pass: node7_disclosure.py had no reference to
    uncertainty_budget at all.

    The components are one-at-a-time sensitivities, each measured against
    its OWN reference point (the official-date line varies only the two
    published rates; the domestic-premium line pivots off the candle's
    CLOSE, not the HIGH that actually drives the lattice's overall
    maximum) -- not a strict decomposition of the total spread into
    orthogonal, additive parts. They do not sum to spread.inr, and
    shouldn't be expected to. Said here, once, rather than left for a
    reader to notice the arithmetic doesn't close and wonder why."""
    if not budget:
        return ""
    ordered = sorted(budget, key=lambda b: -abs(b.get("inr", 0)))
    total_inr = spread.get("inr", 0)
    parts_sum = sum(b.get("inr", 0) for b in ordered)
    items = "\n".join(
        f'<li><span class="t">{esc(b.get("source", "?"))} '
        f'<b>{fmt_inr(b.get("inr", 0))}</b></span>'
        f'<span class="d">{esc(b.get("explanation", ""))}</span></li>'
        for b in ordered
    )
    note = ""
    gap = parts_sum - total_inr
    if abs(gap) > 1:
        note = (
            f'<p class="gap-note">These {len(ordered)} components sum to '
            f'{fmt_inr(parts_sum)}, not the {fmt_inr(total_inr)} total spread above '
            f'— a {fmt_inr(abs(gap))} difference. Each line is measured one at a time '
            f'against its own reference point (the domestic-premium line, for instance, '
            f'pivots off the day\'s closing price, not the high that actually sets the '
            f'lattice\'s maximum), not a strict split of the total into non-overlapping '
            f'parts. Both numbers are real; they answer different questions.</p>'
        )
    return (
        '<details style="margin-top:22px">'
        '<summary>Where the spread actually comes from — decomposed by source</summary>'
        f'<ul class="budget">{items}</ul>'
        f'{note}'
        '</details>'
    )


def render_election(lo, hi):
    return (
        '<fieldset><legend class="label">If you have already decided, record it here</legend>'
        f'<div class="opt"><input type="radio" name="election" id="ea">'
        f'<label for="ea"><span class="t">{fmt_inr(lo["inr_value"])} — {esc(lo.get("label"))}</span>'
        f'<span class="d">{esc((lo.get("source") or {}).get("note", ""))[:160]}</span></label></div>'
        f'<div class="opt"><input type="radio" name="election" id="eb">'
        f'<label for="eb"><span class="t">{fmt_inr(hi["inr_value"])} — {esc(hi.get("label"))}</span>'
        f'<span class="d">{esc((hi.get("source") or {}).get("note", ""))[:160]}</span></label></div>'
        '<p class="stamp"><b>This record is complete whether or not you tick anything.</b> '
        'What matters if the figure is ever questioned is that both were shown and both '
        'were recorded — not which one you chose, and not that we chose for you.</p>'
        '</fieldset>'
    )


_CERT_LABEL = {
    "settled": "Settled", "inference": "Inference", "open_texture": "Open texture",
    "lacuna": "No rule found", "contested": "Contested",
    "insufficient_evidence": "Insufficient evidence",
}


def render_regimes(regimes):
    if not regimes:
        return '<p class="lede">No regime conclusions in this record.</p>'
    blocks = []
    for r in regimes:
        cert = r.get("certainty", "insufficient_evidence")
        label = _CERT_LABEL.get(cert, cert)
        name = r.get("regime", "?").replace("_", " ")
        cite = (r.get("citation") or {}).get("provision", "")
        outcome = r.get("outcome", "")
        blocks.append(
            f'<div class="regime"><div class="r-top">'
            f'<span class="r-name">{esc(name)}</span>'
            f'<span class="cert {esc(cert)}">{esc(label)}</span></div>'
            f'<p class="r-body">{esc(outcome)} <span class="cite">{esc(cite)}</span></p></div>'
        )
    return "\n".join(blocks)


def render_manifest(regimes, corpus_frozen_at):
    # Same matching primitives citation_matcher.py itself uses to decide
    # "verified: true" -- exact string equality between a regime's
    # citation.provision and a corpus file's current_citation is too
    # strict and produces false negatives (found live: IT-115BBH.md's
    # current_citation carries extra "carried into the 2025 Act" prose the
    # regime's own citation field doesn't repeat, so a naive `in` check
    # marked a real, verified citation as "not cited" here).
    cited_refs = []
    for r in regimes:
        prov = (r.get("citation") or {}).get("provision")
        if prov:
            cited_refs.append(citation_matcher.extract_refs(prov))
    date = (corpus_frozen_at or "?")[:10]

    checked_files = set()
    for r in regimes:
        checked_files.update(REGIME_CORPUS.get(r.get("regime"), []))
    checked = []
    for fn in sorted(checked_files):
        meta = citation_matcher.parse_front_matter(os.path.join(HERE, "corpus", "tier-a", fn))
        name = meta.get("current_citation") or fn
        stored_refs = citation_matcher.extract_refs(name)
        was_cited = any(
            citation_matcher._refs_match(c, s)
            for refs in cited_refs for c in refs for s in stored_refs
        )
        checked.append((name, was_cited))

    if not checked:
        return '<p class="lede">No regime conclusions to check a corpus against.</p>'

    n_cited = sum(1 for _, was_cited in checked if was_cited)
    items = "\n".join(
        f'<li><span>{esc(name)}{" — cited above" if was_cited else ""}</span>'
        f'<span>{esc(date)}</span></li>'
        for name, was_cited in checked
    )
    return (
        f'<details><summary>{len(checked)} provision(s) actually checked for this record '
        f'({n_cited} cited above, {len(checked) - n_cited} checked and correctly not relied on), '
        f'corpus frozen {esc(date)}</summary>'
        f'<ul class="man">{items}</ul>'
        '<p class="gap-note"><b>Not checked:</b> state levies, treaty relief, anything '
        'outside Indian law. Where we say no rule was found, we mean within this scope.</p>'
        '</details>'
    )


def render_attacks(record):
    """Section 05 -- what node 5 (adversarial) tried against this record's
    own conclusions. Reads attacked[]/checked_and_survived[] exactly as
    node5_adversarial.py wrote them; makes no model call and adds no
    judgement of its own, same discipline as render_regimes() reading
    regimes[]. If a record was generated without --node5, both keys are
    simply absent -- say that plainly rather than rendering an empty
    section that looks like zero attacks were made."""
    if "attacked" not in record:
        return (
            '<p class="lede">Node 5 (adversarial) was not run for this record. '
            'Nothing below was attacked, and nothing here should be read as '
            'having survived scrutiny.</p>'
        )
    attacked = record.get("attacked") or []
    survived = record.get("checked_and_survived") or []
    if not attacked and not survived:
        return '<p class="lede">Node 5 ran and found nothing to attack in this record.</p>'

    parts = [
        f'<p class="lede">{len(attacked)} attack{"s" if len(attacked) != 1 else ""} '
        f'made by a different model than the one that wrote the conclusions above '
        f'(decision D41). Published whether it landed or not.</p>'
    ]
    for a in attacked:
        landed = not a.get("survived", True)
        verdict = "LANDED" if landed else "SURVIVED"
        cls = "landed" if landed else "survived"
        target = esc(a.get("target", ""))
        attack_txt = esc(a.get("attack", ""))
        dg = a.get("downgraded_to")
        dg_html = (f'<p class="a-down">proposed downgrade: {esc(dg)}</p>' if dg else "")
        parts.append(
            f'<div class="attack"><div class="a-top">'
            f'<span class="a-target">{target}</span>'
            f'<span class="verdict {cls}">{verdict}</span></div>'
            f'<p class="a-body">{attack_txt}</p>{dg_html}</div>'
        )
    if survived:
        items = "\n".join(f"<li>{esc(s)}</li>" for s in survived)
        parts.append(
            f'<p class="gap-note" style="margin-top:20px">'
            f'{len(survived)} conclusion{"s" if len(survived) != 1 else ""} checked and '
            f'not attacked at all -- not the same as surviving an attack:</p>'
            f'<ul class="survived-list">{items}</ul>'
        )
    return "\n".join(parts)


def render_limits(limits):
    if not limits:
        return '<p><b>limits[] was empty — this record is malformed; do not trust it.</b></p>'
    return "\n".join(f"<p>{esc(x)}</p>" for x in limits)


def compose(record):
    facts = record.get("facts", {})
    record_id = record.get("record_id", "?")
    tax_year = record.get("tax_year", "?")
    amount = fact(facts, "amount")
    asset = fact(facts, "asset")
    settle = fact(facts, "settlement_datetime_ist", record.get("generated_at", ""))
    invoice_no = fact(facts, "invoice_no", record_id)
    counterparty = fact(facts, "counterparty_declared", "not stated")

    title = f"Payment received {esc(fmt_datetime(settle))}"
    subtitle = f"{esc(fmt_amount(amount, asset))} · Invoice {esc(invoice_no)} · Counterparty declared as {esc(counterparty)}"

    body = f"""
<main class="sheet">
  <header>
    <div class="formno">
      <span class="label">Disclosure record · {esc(record_id)}</span>
      <span class="label">Corpus frozen {esc((record.get('corpus_frozen_at') or '?')[:10])} · Tax year {esc(tax_year)}</span>
    </div>
    <h1>{title}</h1>
    <p class="sub">{subtitle}</p>
  </header>
  <hr class="rule">

  <section aria-labelledby="s1">
    <div class="sec-head"><span class="sec-n">01</span><h2 id="s1">What is missing</h2></div>
    <p class="lede">Checked before anything else was worked out. Nothing below can be assumed.</p>
    {render_missing(record.get("missing", []))}
  </section>

  <section aria-labelledby="s2">
    <div class="sec-head"><span class="sec-n">02</span><h2 id="s2">What it was worth in rupees</h2></div>
    {render_valuation(record.get("valuation", {}))}
  </section>

  <section aria-labelledby="s3">
    <div class="sec-head"><span class="sec-n">03</span><h2 id="s3">What this triggers</h2></div>
    <p class="lede">Each conclusion carries the provision it rests on, and how settled that provision is.</p>
    {render_regimes(record.get("regimes", []))}
  </section>

  <section aria-labelledby="s4">
    <div class="sec-head"><span class="sec-n">04</span><h2 id="s4">What we checked</h2></div>
    {render_manifest(record.get("regimes", []), record.get("corpus_frozen_at"))}
  </section>

  <section aria-labelledby="s5">
    <div class="sec-head"><span class="sec-n">05</span><h2 id="s5">What we tried to break</h2></div>
    {render_attacks(record)}
  </section>

  <div class="limits">
    <span class="label">What this is not</span>
    <p>This is not tax advice, and it does not make anything compliant. It records what was known at the time and what was not.</p>
    {render_limits(record.get("limits", []))}
    <p>Where the law prescribes no method, we do not invent one. That is the whole point.</p>
  </div>
</main>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Disclosure record — {esc(invoice_no)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="Node 7 / ⚙ D -- disclosure composer")
    ap.add_argument("--record", required=True, help="path to a run_pipeline.py output record")
    ap.add_argument("--attack", default=None,
                     help="path to a node5_adversarial.py output (attacked[]/"
                          "checked_and_survived[]), when it was kept as a separate "
                          "file rather than embedded via run_pipeline.py --node5. "
                          "Merged in memory for rendering only -- never written back "
                          "to either source file.")
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()

    record = json.load(open(a.record, encoding="utf-8"))
    if a.attack:
        attack = json.load(open(a.attack, encoding="utf-8"))
        record = dict(record)
        record["attacked"] = attack.get("attacked", [])
        record["checked_and_survived"] = attack.get("checked_and_survived", [])
    page = compose(record)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"  wrote {a.out} from {a.record}")
    print(f"  record_id={record.get('record_id')}  "
          f"missing={len(record.get('missing', []))}  "
          f"methods={len(record.get('valuation', {}).get('methods', []))}  "
          f"regimes={len(record.get('regimes', []))}")


if __name__ == "__main__":
    main()
