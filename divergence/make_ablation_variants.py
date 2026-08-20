#!/usr/bin/env python3
"""
MAKE ABLATION VARIANTS — DIVERGENCE, Block D / Step 29b
Deterministic. No model. Plants one real, documented defect into a COPY of
D1's own real regimes[], per the table in step22drop/prompts/05-adversarial.md.
Defects are hand-planted by design (D1-a/b/c/d's own case.md: "one of our
own four real errors, planted deliberately") -- not model-generated, so
there is no risk of the planter and the checker sharing a blind spot.

    python make_ablation_variants.py

Reads   runs/21aug/D1_pipeline.json  (never written to)
Writes  runs/21aug/D1-a_regimes.json .. D1-d_regimes.json
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "runs", "21aug", "D1_pipeline.json")
OUT_DIR = os.path.join(HERE, "runs", "21aug")

d1 = json.load(open(SRC, encoding="utf-8"))
base_regimes = d1["regimes"]


def variant_a():
    """cites Rule 11UA for FY 2026-27 (checklist item 1, operative status).
    Rule 11UA is the pre-2025-Act name for what is now Rule 57 -- citing it
    for FY 2026-27 is exactly the stale-numbering mistake this project's
    own error log records three times over."""
    r = copy.deepcopy(base_regimes)
    r[0]["reasoning"] = r[0]["reasoning"].replace("Rule 206", "Rule 11UA")
    r[0]["outcome"] = r[0]["outcome"].replace("Rule 206", "Rule 11UA")
    r[0]["citation"] = dict(r[0]["citation"], provision="Rule 11UA, Income-tax Rules, 1962",
                             tax_year="FY 2026-27")
    return r


def variant_b():
    """applies Rule 57 row 7 to a s.92 receipt (checklist item 2, scope
    reach). Row 7 is a residual catch-all but its own column B names
    s.26(2)(j) as the section it serves, not s.92 -- current_citation is
    real and current, the claimed reach is not."""
    r = copy.deepcopy(base_regimes)
    r[0]["reasoning"] += (" Rule 57 row 7, the residual catch-all provision, "
                           "supplies the applicable valuation method for this "
                           "s.92 receipt where no other row of the table reaches it.")
    return r


def variant_c():
    """asserts the GST conclusion despite the FIRC being missing (checklist
    item 3, missing document). depends_on_missing[] stays non-empty --
    only certainty is flipped to confident, which is exactly the failure
    gap_enforcer.py exists to prevent mechanically; this variant asks
    whether node 5 catches it a second, independent way."""
    r = copy.deepcopy(base_regimes)
    r[1]["certainty"] = "settled"
    r[1]["outcome"] = ("The supply meets all conditions for being an export of "
                        "services. All conditions are confirmed.")
    return r


def variant_d():
    """values USDC at the USDT print, proxy unstated (checklist item 4,
    correct instrument). USDC and USDT are different issuers with
    different peg mechanics -- substituting one for the other without
    disclosing the substitution is the named historical catch."""
    r = copy.deepcopy(base_regimes)
    r[0]["reasoning"] += (" The fair market value of the USDC receipt was computed "
                           "from the USDT/INR print on the settlement date.")
    r[0]["outcome"] += (" Valued using the USDT/INR print on the settlement date.")
    return r


variants = {"D1-a": variant_a(), "D1-b": variant_b(), "D1-c": variant_c(), "D1-d": variant_d()}

for name, regimes in variants.items():
    out_path = os.path.join(OUT_DIR, f"{name}_regimes.json")
    json.dump({"regimes": regimes}, open(out_path, "w", encoding="utf-8"), indent=2)
    print(f"  {name} -> {out_path}")
