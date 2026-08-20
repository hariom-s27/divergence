# CORPUS MANIFEST
### What we looked at — and therefore what our silence means
**Regenerated: 2026-08-19 · 17 Tier A files · ALL COMPLETE**

**Superseded the 2026-08-06 freeze.** The notified Income-tax Rules, 2026 gazette added four more provisions since the original freeze (`ITR2026-RULE-206`, `ITR2026-RULE-207`, `ITR2026-RULE-247`, `ITR2026-RULE-56`), and the corpus was re-audited against `gate0_check.py` on 2026-08-19: two shadow/stale duplicates retired (`IT-RULE-207.md`, and `IT-RULE-206.md` which despite its name held the old Rule 115 text), one non-statutory document demoted to Tier B (`FBIL-METHODOLOGY.md`), and two documents given a citable handle that were previously unmatchable (`ITR2026-RCASP-VALUATION.md`, `SBI-TTBR-DATA.md`). Citing "Rule 115" for FY 2026-27 now correctly resolves `STALE` (redirects to Rule 206) instead of the old file's accidental `VERIFIED` — see `citation_matcher.py`'s self-test, case "OUR OWN ERROR #3".

---

## SCOPE STATEMENT

This corpus covers the provisions relevant to **valuing a stablecoin receipt in INR, received by an Indian resident individual as consideration for professional services rendered to a foreign client, in FY 2026-27.**

**Any claim we make that "no rule prescribes X" means: no rule among the provisions listed below prescribes X.** It does not mean no such rule exists anywhere in Indian law.

That distinction is the reason this file exists. A negative claim is only as good as the declared boundary around it.

---

## DELIBERATELY NOT CHECKED

- State levies
- Double-tax treaty relief
- Anything outside Indian law (Singapore and UAE appear in the pitch as research, never as system output)
- Provisions governing FY 2025-26 and earlier, except where cited in dual form
- GST on the token transfer itself, as distinct from the service supply

---

## TIER A — verbatim, complete, CITABLE

Only Tier A text may be matched by the citation checker. 17 files.

| File | Provision | Status |
|---|---|---|
| `GST-IGST-2-6.md` | IGST s.2(6) — export of services | ✅ **Verbatim text present** |
| `IT-439-8.md` | s.439(8) — penalty exclusions | ✅ **Verbatim (a) and (b) present** |
| `IT-115BBH.md` | 30% on VDA transfer | ✅ **COMPLETE, hashed** |
| `IT-2-47A.md` | Definition of "virtual digital asset" | ✅ **COMPLETE — carries the FEMA cross-reference** |
| `IT-393-1-T8vi.md` | s.393 — TDS on VDA transfer | ✅ **COMPLETE, verbatim, citable** |
| `FEMA-2n.md` | s.2(h)(m)(n)(q) — the currency chain | ✅ **COMPLETE, hashed** |
| `FEMA-3-7-8.md` | **s.3(c) prohibition** · s.7 · s.8 | ✅ **COMPLETE — s.3(c) is the strongest FEMA hook** |
| `GST-CGST-50.md` | s.50 — interest · **ss.73/74 → s.74A catch** | ✅ **COMPLETE** |
| `GST-CGST-74A.md` | s.74A — the governing demand section for FY 2024-25+ | ✅ **COMPLETE** |
| `IT-56-2-x.md` | s.56(2)(x) + the FMV Explanation | ✅ **COMPLETE — current text, chain closed** |
| `SBI-TTBR-DATA.md` | Archived SBI TT BUY rates, cited via **Rule 207(3)(b), Income-tax Rules, 2026** | ✅ **Data present, verified. Citable as of 2026-08-19 — previously had no matchable citation.** |
| `ITR2026-RULE-56.md` | Rule 56 (was Rule 11U) — fixes the valuation **date** for a s.92 receipt to the day of receipt | ✅ **COMPLETE, gazette-sourced** |
| `ITR2026-RULE-57.md` | Rule 57 (was 11UA) — fair market value method; zero VDA references | ✅ **COMPLETE, hashed, machine-checked** |
| `ITR2026-RULE-206.md` | Rule 206 (was Rule 115) — rate of exchange for conversion into rupees; does not reach a VDA; borrows its definition from Rule 207 but not the fallback | ✅ **COMPLETE, gazette-sourced. `IT-RULE-206.md` retired 2026-08-19 — filename said Rule 206, body was the old Rule 115 text; this file is now the sole current AND former-numbering source (via `former_citation`).** |
| `ITR2026-RULE-207.md` | Rule 207 (was Rule 26) — rate of exchange for TDS on payments out; **the only provision naming SBI** (207(3)(b)); has the stale-date fallback Rule 206 lacks | ✅ **COMPLETE, gazette-sourced. `IT-RULE-207.md` retired 2026-08-19 — was a shadow duplicate, same citation, alphabetically shadowed this file.** |
| `ITR2026-RULE-247.md` | Rule 247 — qualification of a registered valuer; names "a valuer of virtual digital assets" and gives that valuer no class, no qualification, no method | ✅ **COMPLETE, gazette-sourced** |
| `ITR2026-RCASP-VALUATION.md` | **Rule 243(8)(e), Income-tax Rules, 2026** — the crypto valuation waterfall that exists for exchanges and not for taxpayers | ✅ **Citable as of 2026-08-19 — citation number confirmed from `ITR2026-RULE-247.md`'s own cross-reference; previously had no Rule/Section number and could never be matched.** |

## TIER B — summarised or non-statutory, NOT citable

| File | What |
|---|---|
| `../tier-b/COMMENTARY.md` | Professional sources for the "no prescribed method" claim |
| `../tier-b/SG-UAE.md` | Singapore and UAE, indicative only |
| `../tier-b/FBIL-METHODOLOGY.md` | FBIL Reference Rate methodology — **demoted from Tier A 2026-08-19.** No Rule or Section in this corpus names FBIL; it is context for why the official reference rate does not answer the question, never citable authority itself. |

---

## THE RULE THAT MUST NOT BE BROKEN

**Never retype a provision. Copy and paste.** A single typo becomes a citation that fails to match, and you will spend an hour debugging the checker when the bug is a missing comma.
