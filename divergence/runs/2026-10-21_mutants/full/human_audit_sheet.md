# Human audit sheet: SPECIFIC hits (13) and placebo hits (3)

For the OWNER to judge. Facts in fields 1–4 are extracted by code from `full/*_r<n>.json` and the exact unmutated requests (rebuilt offline, no model call). Field 5 is the agent's suggestion and is **not a verdict**. Excerpts are normalised (lowercase, `Section N` → `s.N`).

## 1. SPECIFIC hit: C1_OVERCLAIM_r1

**(1) Planted change:** gst_export: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `this supply does not meet the conditions for an export of services. || the conclusion depends on the condition that the recipient of service is located outside india, which is listed in the `missing``  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: This supply does not meet the conditions for an export of services. || ATTACK: The conclusion depends on the condition that the recipient of service is located outside India, which is listed in the `missing` list. Since this condition is not met and is explicitly absent, the conclusion that the supply does not meet the conditions for an export of services is not valid. || downgraded_to: insufficient_evidence

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C1_NULL_r1: no attack on this target
- C1_NULL_r2: LANDED TARGET: This supply does not meet the conditions for an export of services. || ATTACK: The reasoning erroneously claims there is insufficient evidence because it did not confirm the place of supply of the service is outside India. This condition relies on FEMSA Section 7 and there
- C1_NULL_r3: survived TARGET: This supply does not meet the conditions for an export of services. || ATTACK: The conclusion states that the supply does not meet the conditions for an export of services due to the recipient being located in India. However, the dependents state that they blocked for no

**(5) AGENT SUGGESTION — not a verdict:** PARTIAL. Aimed at the overclaimed gst_export and restores its true certainty (insufficient_evidence), but the reason is a routine missing-dependency attack; C1_NULL_r2 attacked the same target. Never mentions certainty or 'settled'. OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 2. SPECIFIC hit: C1_OVERCLAIM_r2

**(1) Planted change:** gst_export: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `this supply does not meet the conditions for an export of services.", || the place of supply basis seems ambiguous. thats due, is resolved on recipients location directly might not supported or denied`  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: This supply does not meet the conditions for an export of services.", || ATTACK: The place of supply basis seems ambiguous. Thats due, is resolved on recipients location directly might not supported or denied with review in references. || downgraded_to: open_texture

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C1_NULL_r1: no attack on this target
- C1_NULL_r2: LANDED TARGET: This supply does not meet the conditions for an export of services. || ATTACK: The reasoning erroneously claims there is insufficient evidence because it did not confirm the place of supply of the service is outside India. This condition relies on FEMSA Section 7 and there
- C1_NULL_r3: survived TARGET: This supply does not meet the conditions for an export of services. || ATTACK: The conclusion states that the supply does not meet the conditions for an export of services due to the recipient being located in India. However, the dependents state that they blocked for no

**(5) AGENT SUGGESTION — not a verdict:** NOT CONFIRMED. Attack text is incoherent ('Thats due, is resolved on recipients location directly might not...'); downgrade is to open_texture, not the true level. Nothing shows the overclaim was noticed. OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 3. SPECIFIC hit: C2_OVERCLAIM_r1

**(1) Planted change:** gst_export: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `the supply meets all the conditions for being an export of services. || the conclusion does not consider the requirement for an 'export declaration' as required by the foreign exchange management act,`  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: The supply meets all the conditions for being an export of services. || ATTACK: The conclusion does not consider the requirement for an 'Export Declaration' as required by the Foreign Exchange Management Act, 1999. Without the clarification of this document -- on which the Gap List indicates dependency from valuation angle -- validation matched against FEMA needs evaluation overlap. || downgraded_to: contested

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C2_NULL_r1: ERROR (no verdict)
- C2_NULL_r2: LANDED TARGET: The supply meets all the conditions for being an export of services. || ATTACK: The conclusion depends on the 'place of supply,' which is listed as missing. Given that the 'place of supply' is a crucial condition for determining if the supply qualifies as an export of serv
- C2_NULL_r3: ERROR (no verdict)

**(5) AGENT SUGGESTION — not a verdict:** PARTIAL (weak). Pushes certainty down (contested) on the overclaimed regime, but the reason (an FEMA 'Export Declaration') is dubious and unrelated to the certainty label; C2_NULL_r2 attacked the same target. OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 4. SPECIFIC hit: C2_OVERCLAIM_r3

**(1) Planted change:** gst_export: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `the supply meets all the conditions for being an export of services. || the condition regarding the place of supply being outside india remains unsettled. as mandated by igst act s.2(6)`  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: The supply meets all the conditions for being an export of services. || ATTACK: The condition regarding the place of supply being outside India remains unsettled. As mandated by IGST Act s.2(6) || downgraded_to: insufficient_evidence

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C2_NULL_r1: ERROR (no verdict)
- C2_NULL_r2: LANDED TARGET: The supply meets all the conditions for being an export of services. || ATTACK: The conclusion depends on the 'place of supply,' which is listed as missing. Given that the 'place of supply' is a crucial condition for determining if the supply qualifies as an export of serv
- C2_NULL_r3: ERROR (no verdict)

**(5) AGENT SUGGESTION — not a verdict:** CONFIRMED (strongest OVERCLAIM item). Says the place-of-supply condition 'remains unsettled' and restores the true certainty (insufficient_evidence) on the regime marked settled. Still does not say 'this is marked settled'. OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 5. SPECIFIC hit: C3_OVERCLAIM_r3

**(1) Planted change:** income_tax_on_receipt: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `the receipt of 2000 usdc is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115bbh. the value is determined on the settlement date (2026-06-23) using the telegr`  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: The receipt of 2,000 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The value is determined on the settlement date (2026-06-23) using the telegraphic transfer buying rate. No TDS is required as the recipient is outside India. Under s.439(8), a bona fide disclosure of the income with all material facts is required to avoid penalties. || ATTACK: This conclusion depends on the 'declaration_of_service_payment', 'income_tax_deduction', and 'valuation_date', all of which are missing. Asserting the conclusion despite these dependencies 

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C3_NULL_r1: LANDED TARGET: The receipt of 2,000 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The value is determined on the settlement date (2026-06-23) using the telegraphic transfer buying rate. No TDS is required as the recipient is outsi
- C3_NULL_r2: LANDED TARGET: The receipt of 2,000 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The value is determined on the settlement date (2026-06-23) using the telegraphic transfer buying rate. No TDS is required as the recipient is outsi
- C3_NULL_r3: LANDED TARGET: The receipt of 2,000 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The value is determined on the settlement date (2026-06-23) using the telegraphic transfer buying rate. No TDS is required as the recipient is outsi

**(5) AGENT SUGGESTION — not a verdict:** NOT CONFIRMED / at most PARTIAL. All three C3 nulls landed an attack on the same target; this one is the same missing-dependency pattern. The downgrade lands on the true level (insufficient_evidence), which is the only overclaim-specific signal. OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 6. SPECIFIC hit: C3_RATE_SUB_r1

**(1) Planted change:** SBI TTBR 2026-06-25 (last published BEFORE the receipt): source silently swapped 'SBI Forex Card Rates sheet, USD/INR TT BUY' -> 'Binance USDC/USDT close', label text left saying the old source

**(2) Matched excerpt:** `it is implied the binance usdc/usdt print substitutability operates in the environs of force marshal law. || the explanation does not adequately address the legal framework governing treatement antici`  
Matched terms: ['binance']  
Full landed attack (≤600 chars): TARGET: It is implied the Binance USDC/USDT print substitutability operates in the environs of Force Marshal law. || ATTACK: The explanation does not adequately address the legal framework governing treatement anticipating incidents materilizing certain susbtainuration measures foregrounding PRCs and how international regulartory compliance meshes or conflicts interactively mutualle An omission glaringly failing attending verification Binance cyrptocurrency revaluing paired comparatively  Save therefore explicit regarding binance absence in legally legitimate actingally is vaguely mapping Subs

**(3) Matched term already in the unmutated (null) request?** terms already in the unmutated request: `Binance USDC/USDT close`, `binance` (absent: 1 other term forms)

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C3_NULL_r1: no attack on this target
- C3_NULL_r2: no attack on this target
- C3_NULL_r3: no attack on this target

**(5) AGENT SUGGESTION — not a verdict:** NOT CONFIRMED. 'binance' matched, but 'Binance USDC/USDT close' already occurs in the unmutated request (other lattice methods use it) and the planted 'swapped' note is not mentioned. The target is invented text and the attack is word salad; it does not identify the swapped method or a label/source mismatch.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 7. SPECIFIC hit: C4_DATE_SHIFT_r1

**(1) Planted change:** SBI TTBR 2026-06-25 (last published BEFORE the receipt): date_used reset to the real transaction date, '2026-06-25' -> '2026-06-18' (rate/inr_value left untouched)

**(2) Matched excerpt:** `asset, taxed at 30% under s.115bbh. the valuation date is the date of receipt (2026-06-18). the valuation method is the price that such property would ordinarily fetch on sale in the open market on t`  
Matched terms: ['2026-06-18']  
Full landed attack (≤600 chars): TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The valuation date is the date of receipt (2026-06-18). The valuation method is the price that such property would ordinarily fetch on sale in the open market on the valuation date. No TDS obligation arises as the recipient is outside India. Under s.439(8), a disclosed position must be bona fide and all material facts must be disclosed. || ATTACK: The provision cited for TDS obligations, s.309(1) Table Sl. No. 8(vi), is not current for the tax year FY 2026-27. The 

**(3) Matched term already in the unmutated (null) request?** terms already in the unmutated request: `2026-06-18` (absent: 9 other term forms)

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C4_NULL_r1: LANDED TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The valuation date is the date of receipt (2026-06-18). The valuation method is the price that such property would ordinarily fetch on sale in the ope
- C4_NULL_r2: LANDED TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. || ATTACK: Section 115BBH specifically applies to the 'transfer' of virtual digital assets. The term 'transfer' is defined in section 2(47A) and typic
- C4_NULL_r3: LANDED TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The valuation date is the date of receipt (2026-06-18). The valuation method is the price that such property would ordinarily fetch on sale in the ope

**(5) AGENT SUGGESTION — not a verdict:** NOT CONFIRMED (chance match). '2026-06-18' sits in the TARGET, which quotes the regime's own outcome ('date of receipt (2026-06-18)'); the identical target appears in C4_NULL_r1/r3 (see items 15–16). The attack is about the s.309(1) TDS citation, not the planted method's date_used.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 8. SPECIFIC hit: C4_DATE_SHIFT_r3

**(1) Planted change:** SBI TTBR 2026-06-25 (last published BEFORE the receipt): date_used reset to the real transaction date, '2026-06-25' -> '2026-06-18' (rate/inr_value left untouched)

**(2) Matched excerpt:** `the valuation date for the receipt is the date of receipt (2026-06-18) as per rule 56, table sl. no. 1, which applies to the date on which the property or consideration is received by the assessee. ||`  
Matched terms: ['2026-06-18']  
Full landed attack (≤600 chars): TARGET: The valuation date for the receipt is the date of receipt (2026-06-18) as per Rule 56, Table Sl. No. 1, which applies to the date on which the property or consideration is received by the assessee. || ATTACK: Rule 56, Table Sl. No. 1 applies to section 92, not section 115BBH. The valuation date for section 115BBH is not specified in Rule 56, making the application of Rule 56 incorrect for this scenario. || downgraded_to: lacuna

**(3) Matched term already in the unmutated (null) request?** terms already in the unmutated request: `2026-06-18` (absent: 9 other term forms)

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C4_NULL_r1: no attack on this target
- C4_NULL_r2: no attack on this target
- C4_NULL_r3: no attack on this target

**(5) AGENT SUGGESTION — not a verdict:** NOT CONFIRMED. The date is the regime's own receipt date, present in the null request; the attack concerns Rule 56's scope (s.92 vs s.115BBH), not the valuation method whose date_used was changed.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 9. SPECIFIC hit: C4_OVERCLAIM_r2

**(1) Planted change:** gst_export: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `the supply meets some conditions for export of services but fails the condition regarding the receipt of payment in convertible foreign exchange. || this conclusion depends on the 'declaration of serv`  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: The supply meets some conditions for export of services but fails the condition regarding the receipt of payment in convertible foreign exchange. || ATTACK: This conclusion depends on the 'declaration_of_service_payment,' which is missing. Since the conclusion is asserted despite this absence, it indicates a failure to acknowledge the dependency on the missing document. || downgraded_to: contested

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C4_NULL_r1: LANDED TARGET: The supply meets some conditions for export of services but fails the condition regarding the receipt of payment in convertible foreign exchange. || ATTACK: The provision s.2(6) cited is from the Integrated Goods and Services Tax Act, 2017, and it is not clear if it has be
- C4_NULL_r2: no attack on this target
- C4_NULL_r3: no attack on this target

**(5) AGENT SUGGESTION — not a verdict:** PARTIAL (weak). Downgrade (contested) on the overclaimed gst_export, for a missing document; C4_NULL_r1 attacked the same target for a different reason. No sign the certainty label was noticed. OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 10. SPECIFIC hit: C5_CITE_SWAP_r2

**(1) Planted change:** income_tax_on_receipt: citation nudged 'Rule 56, Income-tax Rules, 2026' -> 'Rule 57, Income-tax Rules, 2026'

**(2) Matched excerpt:** `g rate on the last day of the tax year (31 march 2027). || the provision cited, rule 57, does not specify the valuation method for income from other sources directly. the appropriate rule for determin`  
Matched terms: ['Rule 57']  
Full landed attack (≤600 chars): TARGET: The receipt is classified as income from other sources, recognized on the date of credit (28 June 2026), valued using the telegraphic transfer buying rate on the last day of the tax year (31 March 2027). || ATTACK: The provision cited, Rule 57, does not specify the valuation method for income from other sources directly. The appropriate rule for determining the valuation method for income from other sources is Rule 206, which specifies the telegraphic transfer buying rate on the last day of the tax year. However, Rule 206 does not mention the specific date of 31 March 2027 for the tax 

**(3) Matched term already in the unmutated (null) request?** terms already in the unmutated request: `Rule 57, Income-tax Rules, 2026`, `Rule 57` (absent: 0 other term forms)

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C5_NULL_r1: LANDED TARGET: The receipt is classified as income from other sources, recognized on the date of credit (28 June 2026), valued using the telegraphic transfer buying rate on the last day of the tax year (31 March 2027), and is subject to TDS at 1% if the threshold is exceeded. The penalty
- C5_NULL_r2: LANDED TARGET: The receipt is classified as income from other sources, recognized on the date of credit (28 June 2026), valued using the telegraphic transfer buying rate on the last day of the tax year (31 March 2027), and is subject to TDS at 1% if the threshold is exceeded. The penalty
- C5_NULL_r3: ERROR (no verdict)

**(5) AGENT SUGGESTION — not a verdict:** PARTIAL. It does attack the mutated field ('The provision cited, Rule 57, does not specify...'), but the C5 nulls attack the ORIGINAL citation (Rule 56) with the same argument ('Rule 206, not Rule 56'). Node 5 attacks whatever rule is cited; nothing shows it noticed the 56->57 change.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 11. SPECIFIC hit: C5_OVERCLAIM_r1

**(1) Planted change:** gst_export: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `the supply meets all the conditions for being an export of services. || the outcome stating depends on 'valuation'. notably absent — step skipped saying reached nevertheless. making conclusory asserti`  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: The supply meets all the conditions for being an export of services. || ATTACK: The outcome stating depends on 'valuation'. Notably absent — step skipped saying reached nevertheless. Making conclusory assertion about total relief dependent valuation, while claiming incomplete field lacks objectivity. || downgraded_to: insufficient_evidence

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C5_NULL_r1: LANDED TARGET: The supply meets all the conditions for being an export of services. || ATTACK: This conclusion depends on the valuation, which is listed in the `missing` list. Since the valuation is missing, this conclusion cannot be asserted.
- C5_NULL_r2: LANDED TARGET: The supply meets all the conditions for being an export of services. || ATTACK: The conclusion depends on the `valuation`, which is listed in the `missing` list. Since the valuation date is not explicitly provided and there is no information about the fair market value of 
- C5_NULL_r3: ERROR (no verdict)

**(5) AGENT SUGGESTION — not a verdict:** PARTIAL (weak). Garbled text; same 'depends on valuation' attack as C5_NULL_r1/r2; downgrade lands on the true level (insufficient_evidence). OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 12. SPECIFIC hit: C5_OVERCLAIM_r3

**(1) Planted change:** gst_export: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `the supply meets all the conditions for being an export of services. || the conclusion depends on valuation, which is listed in the 'missing' list. the conclusion is asserted despite the dependency on`  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: The supply meets all the conditions for being an export of services. || ATTACK: The conclusion depends on valuation, which is listed in the 'missing' list. The conclusion is asserted despite the dependency on missing information, which is a critical failure. || downgraded_to: insufficient_evidence

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C5_NULL_r1: LANDED TARGET: The supply meets all the conditions for being an export of services. || ATTACK: This conclusion depends on the valuation, which is listed in the `missing` list. Since the valuation is missing, this conclusion cannot be asserted.
- C5_NULL_r2: LANDED TARGET: The supply meets all the conditions for being an export of services. || ATTACK: The conclusion depends on the `valuation`, which is listed in the `missing` list. Since the valuation date is not explicitly provided and there is no information about the fair market value of 
- C5_NULL_r3: ERROR (no verdict)

**(5) AGENT SUGGESTION — not a verdict:** PARTIAL. Near-verbatim the same attack as C5_NULL_r1/r2 ('depends on valuation... listed in the missing list'); the downgrade to the true level is the only overclaim-specific signal. OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 13. SPECIFIC hit: D1_OVERCLAIM_r3

**(1) Planted change:** gst_export: certainty strengthened 'insufficient_evidence' -> 'settled', citation/reasoning untouched

**(2) Matched excerpt:** `the supply does not meet all conditions for being an export of services. || the place of supply is not explicitly excluded by s.2(6) despite step 3 stating otherwise. there are no grounds to conclude`  
Matched terms: {'settled_in_text': False}  
Full landed attack (≤600 chars): TARGET: The supply does not meet all conditions for being an export of services. || ATTACK: The place of supply is not explicitly excluded by s.2(6) despite Step 3 stating otherwise. There are no grounds to conclude the actual place of supply failed Step A3 altogether. || downgraded_to: open_texture

**(3) Matched term already in the unmutated (null) request?** structural rule (no planted string). 'settled' in null request: True; regime name in null request: True

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- D1_NULL_r1: LANDED TARGET: The supply does not meet all conditions for being an export of services. || ATTACK: This conclusion depends on the missing independent verification of Northbay Systems LLC, which is listed in the gap list. The conclusion is asserted despite this dependency, which is a clea
- D1_NULL_r2: LANDED TARGET: The supply does not meet all conditions for being an export of services. || ATTACK: This finding hinges decisively upon confirming“North” braces Ell’ established deal tact under “is ”point**_did_form but significantly ();(sure was=[ “be]] to know ]attributable temporarily 
- D1_NULL_r3: no attack on this target

**(5) AGENT SUGGESTION — not a verdict:** NOT CONFIRMED / at most PARTIAL. A place-of-supply argument with a downgrade to open_texture (not the true level); D1_NULL_r1 attacked the same target; nothing about certainty. OVERCLAIM matched via the structural rule's downgrade route (the attack text does not contain 'settled'). Note for all OVERCLAIM items: in a null run the same regime is 'insufficient_evidence', and node 5's own _reject_upward_revisions drops any downgrade from that level, so this route can hardly fire on a null -- OVERCLAIM's ~0 placebo is partly built in, not evidence.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 14. PLACEBO hit: C1_NULL_r2 x RATE_SUB

**(1) Planted change:** NONE (null run). Matched against the RATE_SUB terms; that operator's mutant plants: invoice value, INR to INR -- no conversion: source silently swapped 'invoice + NEFT bank credit, both stated in INR directly' -> 'RBI Reference Rate', label text left saying the old source

**(2) Matched excerpt:** `ition relies on femsa s.7 and therefore demands more scrutiny. also referencing rbi circular dated 04 may 2026.`  
Matched terms: ['rbi']  
Full landed attack (≤600 chars): TARGET: This supply does not meet the conditions for an export of services. || ATTACK: The reasoning erroneously claims there is insufficient evidence because it did not confirm the place of supply of the service is outside India. This condition relies on FEMSA Section 7 and therefore demands more scrutiny. Also referencing RBI circular dated 04 May 2026.

**(3) Matched term already in the unmutated (null) request?** terms already in the unmutated request: none (absent: 4 other term forms)

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C1_NULL_r1: no attack on this target
- C1_NULL_r3: survived TARGET: This supply does not meet the conditions for an export of services. || ATTACK: The conclusion states that the supply does not meet the conditions for an export of services due to the recipient being located in India. However, the dependents state that they blocked for no

**(5) AGENT SUGGESTION — not a verdict:** CHANCE MATCH (placebo behaving as intended). 'rbi' matched an aside ('RBI circular dated 04 May 2026', likely invented) in a GST place-of-supply attack; nothing to do with valuation sources.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 15. PLACEBO hit: C4_NULL_r1 x DATE_SHIFT

**(1) Planted change:** NONE (null run). Matched against the DATE_SHIFT terms; that operator's mutant plants: SBI TTBR 2026-06-25 (last published BEFORE the receipt): date_used reset to the real transaction date, '2026-06-25' -> '2026-06-18' (rate/inr_value left untouched)

**(2) Matched excerpt:** `asset, taxed at 30% under s.115bbh. the valuation date is the date of receipt (2026-06-18). the valuation method is the price that such property would ordinarily fetch on sale in the open market on t`  
Matched terms: ['2026-06-18']  
Full landed attack (≤600 chars): TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The valuation date is the date of receipt (2026-06-18). The valuation method is the price that such property would ordinarily fetch on sale in the open market on the valuation date. No TDS obligation arises as the recipient is outside India. Under s.439(8), a disclosed position must be bona fide and all material facts must be disclosed. || ATTACK: The provision s.115BBH cited is from the Income-tax Act, 1961, and it is not clear if it has been carried into the Inco

**(3) Matched term already in the unmutated (null) request?** terms already in the unmutated request: `2026-06-18` (absent: 9 other term forms)

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C4_NULL_r2: LANDED TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. || ATTACK: Section 115BBH specifically applies to the 'transfer' of virtual digital assets. The term 'transfer' is defined in section 2(47A) and typic
- C4_NULL_r3: LANDED TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The valuation date is the date of receipt (2026-06-18). The valuation method is the price that such property would ordinarily fetch on sale in the ope

**(5) AGENT SUGGESTION — not a verdict:** CHANCE MATCH. Same mechanism as item 7: the target quotes the regime's own '2026-06-18'. Confirms the C4 DATE_SHIFT term is not diagnostic.

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______

## 16. PLACEBO hit: C4_NULL_r3 x DATE_SHIFT

**(1) Planted change:** NONE (null run). Matched against the DATE_SHIFT terms; that operator's mutant plants: SBI TTBR 2026-06-25 (last published BEFORE the receipt): date_used reset to the real transaction date, '2026-06-25' -> '2026-06-18' (rate/inr_value left untouched)

**(2) Matched excerpt:** `asset, taxed at 30% under s.115bbh. the valuation date is the date of receipt (2026-06-18). the valuation method is the price that such property would ordinarily fetch on sale in the open market on t`  
Matched terms: ['2026-06-18']  
Full landed attack (≤600 chars): TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The valuation date is the date of receipt (2026-06-18). The valuation method is the price that such property would ordinarily fetch on sale in the open market on the valuation date. No TDS obligation arises as the recipient is outside India. Under s.439(8), a disclosed position must be bona fide and all material facts must be disclosed. || ATTACK: Rule 206 mandates using 'the telegraphic transfer buying rate' for conversion to rupees of foreign currency, not 'the p

**(3) Matched term already in the unmutated (null) request?** terms already in the unmutated request: `2026-06-18` (absent: 9 other term forms)

**(4) What node 5 said about the same target in this case's null runs (≤300 chars each):**
- C4_NULL_r1: LANDED TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. The valuation date is the date of receipt (2026-06-18). The valuation method is the price that such property would ordinarily fetch on sale in the ope
- C4_NULL_r2: LANDED TARGET: The receipt of 400 USDC is classified as income from the transfer of a virtual digital asset, taxed at 30% under s.115BBH. || ATTACK: Section 115BBH specifically applies to the 'transfer' of virtual digital assets. The term 'transfer' is defined in section 2(47A) and typic

**(5) AGENT SUGGESTION — not a verdict:** CHANCE MATCH. Same as item 15 (C4_NULL_r3).

**OWNER VERDICT:** ______ (confirmed / partial / not_confirmed)  
**OWNER REASON:** ______
