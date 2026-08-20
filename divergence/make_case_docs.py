#!/usr/bin/env python3
"""
MAKE CASE DOCS — DIVERGENCE
Mechanical. No model, no API, no human discretion.

D48 found that five of six case files never got the standalone input
document their own checklist asked for: ground truth expected facts
(a counterparty name, an invoice number) that existed in no document any
extractor was ever shown. C3 was worst -- its case.md restates none of
its own core facts, only "same shape as D1."

This script closes that gap the only way that doesn't corrupt the freeze:
ground_truth.json was frozen first (commit 225ed20b), unchanged since, and
this script reads it -- never writes it -- to mechanically render a
realistic input document. The answer key came first; the exam paper is
being typed up to match it, by a script with no opinions about what makes
a case "easy" or "hard" to extract from. A human hand-writing these
documents would unconsciously make them easier to read, which is exactly
the bias the freeze exists to prevent.

    python make_case_docs.py            # all six cases
    python make_case_docs.py --case C3  # one case

Reads   cases/<CASE>/ground_truth.json   (never written to)
Writes  step21drop/cases/<CASE>/input.md (new file; case.md is untouched)
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "cases")
INPUT_DIR = os.path.join(HERE, "step21drop", "cases")

ALL_CASES = ["C1", "C2", "C3", "C4", "C5", "D1"]

_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]


def _fmt_dt(iso):
    # "2026-06-16T11:20:00+05:30" -> "16 June 2026 at 11:20 IST"
    date_part, time_part = iso.split("T")
    y, m, d = date_part.split("-")
    hh, mm = time_part[:5].split(":")
    return f"{int(d)} {_MONTHS[int(m) - 1]} {y} at {hh}:{mm} IST"


def _fmt_amount(amount, asset):
    if asset == "INR":
        return f"Rs {amount:,.0f}"
    if asset == "USDC":
        return f"{amount:,.0f} USDC"
    return f"{asset} {amount:,.0f}"


def render(case_id, gt):
    f = {k: v["value"] for k, v in gt["facts"].items()}
    used = set()

    def get(key):
        used.add(key)
        return f[key]

    def get_opt(key, default=None):
        if key in f:
            used.add(key)
            return f[key]
        return default

    amount = get("amount")
    asset = get("asset")
    settle_ist = get("settlement_datetime_ist")
    counterparty = get("counterparty_declared")
    verified = get("counterparty_verified")
    invoice_no = get("invoice_no")
    supplier_loc = get("supplier_location")
    recipient_loc = get("recipient_location")
    bank_involved = get("bank_involved")

    utc = get_opt("settlement_datetime_utc")
    usd_amount = get_opt("invoice_amount_usd")
    firc = get_opt("firc_present")
    purpose_code = get_opt("purpose_code")

    invoice_date = settle_ist.split("T")[0]
    settle_fmt = _fmt_dt(settle_ist)
    amount_fmt = _fmt_amount(amount, asset)

    lines = []
    lines.append("# TAX INVOICE")
    lines.append("")
    lines.append(f"Invoice No: {invoice_no}")
    lines.append(f"Invoice Date: {invoice_date}")
    lines.append("")
    lines.append("## Supplier")
    lines.append(f"Resident individual, freelance service provider, {supplier_loc}.")
    lines.append("")
    lines.append("## Recipient")
    lines.append(f"{counterparty}, {recipient_loc}.")
    lines.append("")
    lines.append("## Line item")
    lines.append(f"Professional / consulting services rendered. Invoice value: {amount_fmt}.")
    if usd_amount is not None:
        lines.append(f"Invoice raised in USD equivalent terms: USD {usd_amount:,.0f}.")
    lines.append("")
    lines.append("## Payment confirmation")

    if bank_involved and asset == "INR":
        lines.append(
            f"Payment of {amount_fmt} received by NEFT bank transfer, credited to the "
            f"supplier's account on {settle_fmt}. Domestic transfer, no foreign exchange "
            f"leg involved."
        )
    elif bank_involved:
        para = (
            f"Payment of {amount_fmt} received by SWIFT wire transfer, credited to the "
            f"supplier's account on {settle_fmt}."
        )
        if purpose_code:
            para += f" Purpose code declared on the wire: {purpose_code}."
        if firc:
            para += " Bank has issued a Foreign Inward Remittance Certificate (FIRC) for this credit."
        lines.append(para)
    else:
        para = (
            f"Payment of {amount_fmt} received to the supplier's self-custody wallet on "
            f"{settle_fmt}."
        )
        if utc:
            para += f" ({utc} UTC.)"
        para += " No bank was involved at any point in this transfer."
        lines.append(para)

    lines.append("")
    lines.append("## Counterparty verification")
    if verified:
        lines.append(
            f"{counterparty}'s business identity has been independently confirmed "
            f"(registration / bank KYC check completed at the time of payment)."
        )
    else:
        lines.append(
            f"{counterparty}'s business identity has NOT been independently verified. "
            f"No registration or KYC check has been performed against this name."
        )

    missing = set(f) - used
    return "\n".join(lines) + "\n", missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", choices=ALL_CASES)
    a = ap.parse_args()

    cases = [a.case] if a.case else ALL_CASES
    all_ok = True
    for case_id in cases:
        gt_path = os.path.join(CASES, case_id, "ground_truth.json")
        gt = json.load(open(gt_path, encoding="utf-8"))
        text, missing = render(case_id, gt)

        out_dir = os.path.join(INPUT_DIR, case_id)
        out_path = os.path.join(out_dir, "input.md")
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(text)

        n_facts = len(gt["facts"])
        n_covered = n_facts - len(missing)
        pct = 100.0 * n_covered / n_facts if n_facts else 100.0
        ok = "OK" if not missing else "INCOMPLETE"
        if missing:
            all_ok = False
        print(f"  {case_id}  {n_covered}/{n_facts} facts written  ({pct:.0f}%)  {ok}"
              f"{'  missing: ' + ', '.join(sorted(missing)) if missing else ''}")
        print(f"        -> {out_path}")

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
