# SAMPLES — the workflow vs. a single prompt, same test case, same input

**Required by the track:** *"a video/document that shows the use of workflow
for sample test cases as compared to using a single prompt approach with the
same test cases."* This is that document. Every quote below is copied
verbatim from a real, saved run — `runs/21aug/D1_armA.json` (naive single
prompt), `runs/21aug/D1_armB.json` (a token-matched chain-of-thought single
prompt, same token budget as the workflow, still one call), and
`runs/21aug/D1_final_seed2.json` (the real workflow, arm C, this project's
actual submission). Nothing below is paraphrased into a friendlier shape —
if a run said something wrong, it is quoted saying it.

## The same input, three times

**Case D1** (`step21drop/cases/D1/input.md`): a resident freelancer in India
is paid 5,000 USDC by a foreign client, settling at 03:14 IST on Sunday, 28
June 2026 — a date no Indian bank published an official rate for. All three
arms below received the identical facts and the identical corpus of law
text. The only thing that changes is how many calls are made and what
checks run on the answer before it is shown.

| | Arm A | Arm B | Arm C — the workflow |
|---|---|---|---|
| Approach | One prompt, no scaffolding | One prompt, chain-of-thought, same token budget as the workflow | Five model calls + four deterministic checks |
| Model calls | 1 | 1 | 5 (small ×2, large ×2, a *different* model for the adversarial check) |
| Citation verified against real corpus text? | No | No | Yes — every citation, or the conclusion is dropped |
| Valuation dispute reported | ₹250 (0.05%) | ₹250 (0.05%) | **₹47,868.76 (10.19%)** |
| Own answer attacked before publishing? | No | No | Yes — published either way |

---

## 1. The valuation figure — how big a gap does each approach actually surface?

**Arm A** picked a single rate outright:

> *"The income is taxable as professional services income in INR 469,750
> (using the TT BR on 2026-06-29)."* — `certainty: "settled"`

One number. No mention that a second candidate date existed with a
different rate, no mention that the crypto market itself had a price the
entire weekend. The uncertainty this project's real thesis is about —
₹47,868.76 of it — is invisible in Arm A's output. Not disputed. Not seen.

**Arm B**, given more reasoning room, gets slightly further:

> *"The supplier is liable to pay income tax on the receipt of 5,000 USDC,
> valued at INR 469,750 to 470,000 based on the TT BR on 2026-06-25 or
> 2026-06-29."* — `certainty: "inference"`, spread reported: **₹250, 0.05%**

Better — it names two candidate bank rates instead of picking one silently.
But its own `valuation.methods` array has exactly two entries, both SBI
bank rates. It never asks whether the crypto market's own price on that
Sunday is a defensible alternative at all. The **real** spread this receipt
carries — twelve defensible methods, ₹4,69,750 to ₹5,17,618 — is **about
191 times larger** than what Arm B reports (₹47,868.76 ÷ ₹250 = 191.5). Not because Arm B made an
arithmetic error; because nothing in a single prompt forces it to enumerate
every defensible method rather than stop at the first two it thought of.

**Arm C** (`⚙ B`, `node3_valuation.py` — plain arithmetic, no model,
`valuation.methods.minItems` enforced by schema):

> 12 methods. ₹4,69,750.00 → ₹5,17,618.76. Spread: **₹47,868.76 (10.19%)**.

This is not a smarter model finding a bigger number. It is a deterministic
enumeration — 2 official dates × 5 market readings × 2 currency-peg
assumptions — that a single prompt has no structural reason to perform
completely, and two real single-prompt runs on this exact case, above,
didn't.

## 2. The same wrong citation, twice, with nothing to catch it

Both Arm A and Arm B cite **Rule 206(1)** as the provision that both taxes
the receipt *and* prescribes its valuation method:

> Arm A: *"mandated_by": "ITR2026-RULE-206(1)"* (valuation_method regime)
> Arm B: *"provision": "ITR2026-RULE-206(1)"* (valuation_method regime)

This is the exact defect this project's own iteration story documents
finding and fixing in its real resolvers (`ITERATION-STORY.md` item 7,
`DECISION-D50.md`): Rule 206's own opening words scope it to income
received *"in foreign currency,"* and a virtual digital asset is defined
elsewhere as **not** foreign currency. Rule 206 does not reach this receipt
at all. Two independent single-prompt runs made this same scope-reach
mistake — and neither has anything downstream that could catch it. No
citation matcher checks whether Rule 206 actually governs a VDA. No
adversarial pass questions it. It simply ships as `"certainty": "settled"`
(Arm A) or `"inference"` (Arm B).

**Arm C's real workflow record** (`D1_final_seed2.json`), after the same
mistake was found and fixed in its own history (`DECISION-D50.md`,
`DECISION-D54.md`, `DECISION-D55.md`):

> `"regime": "valuation_method"`, `"certainty": "lacuna"`, citation: **Rule
> 57**, outcome: *"Rule 57 does not provide a specific method for valuing
> USDC, a virtual digital asset, under s.92... Rule 206 is not applicable as
> USDC is not defined as foreign currency under s.2(47A)."*

The workflow doesn't just avoid Rule 206's mistake — its own record shows
the *reasoning* for why Rule 206 doesn't reach, in a way a reader can
check against the corpus text directly. Neither single-prompt arm shows
its reasoning as a checkable citation trail at all.

## 3. Was the answer attacked before being shown?

Arm A and Arm B: no. There is no step in a single prompt that questions the
prompt's own output. Whatever the model said in one pass is what a user
would see.

Arm C: `🤖 5` (`node5_adversarial.py`, a **different model family**,
decision D41) ran against the frozen record and published 4 attacks — all
4 landed, including one catching a real, unsupported claim
(`"no deduction obligation... as... the payer is outside India"`) that the
resolver had invented and that nothing else in the pipeline would have
caught. Full text of every attack: `runs/21aug/D1_final_seed2_attack.json`,
rendered on the actual output page in section 05, "What we tried to
break."

## 4. What this comparison is not claiming

This is one case, three real runs, not a claim that single prompts are
always this far off — `results.md`'s "Where we lose" section documents
cases where the naive baseline actually **beat** the workflow (D1's gap
recall, 20-Aug table: Arm A 75% vs. Arm C 25%), and the workflow's own gap
detector scored 0% on three of six cases. The comparison here is specific:
on the exact question this project exists to answer — how much does a
stablecoin receipt's valuation genuinely disagree, and does the law pick
one — a single prompt, run twice with two different prompting strategies,
both missed nearly the entire real uncertainty and both repeated the exact
same wrong-scope citation that took four separate fix cycles to correct in
this project's own workflow — with a fifth instance of the same failure
pattern found and disclosed, not chased, the same night (`DECISION-D55.md`).
Full metrics, every case, every arm, including where the workflow loses:
[`results.md`](results.md).
