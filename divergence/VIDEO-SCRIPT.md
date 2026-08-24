# VIDEO SCRIPT — DIVERGENCE (M9)

**Supersedes the earlier draft of this file.** That draft was built to a
different, ad hoc six-block structure. **M9 is the real requirement** —
found in the repo's own MUST list only after being asked for directly
(it existed in neither git history nor any tracked file until specified
directly): a demo video isn't required by the track's own rule text
("Samples: Prepare a video/document that shows the use of workflow" —
`SAMPLES.md` already satisfies that), but Devpost's own craft guidance
says judges get the most scope from video, so it's worth doing anyway,
to their structure — **introduction → problem → components → demo →
close** — not the structure the earlier draft used. This version
replaces it, keeping the real figures and the honest-limitation ending
that earlier draft got right, restructured around the actual spec.

**Target runtime: ~3:00.** No hard requirement from the track itself;
sized to Devpost's own "keep it clear and concise, don't try to pack in
way too much information," against how much real, checkable content this
project actually has to show.

**No live demo, on purpose.** The output is a static HTML file — an
unusual, low-risk demo position most teams don't have. Every screen in
this script is a pre-rendered page, opened from disk. The live pipeline
(a real `python run_pipeline.py` call) is a **backup tab only**, kept
running or ready in case a judge specifically asks to see generation —
never part of the recorded video itself.

**Format: script it, record voice-over onto a clean screen capture
separately.** Not live narration over a live screen — a solo builder
narrating live produces filler; scripted VO over a pre-recorded, edited
capture takes the same total time and is strictly better craft, per
Devpost's own guidance ("Write a script! Try to avoid ChatGPT here if
you can — its output is often too generic.").

**Read every SAY line exactly as written.** Short sentences. No
subordinate clauses. If a sentence needs a breath in the middle, it is
two sentences, not one.

---

## 1. INTRODUCTION — ~0:00–0:15

**SAY:**
> This is DIVERGENCE.
> A resident freelancer gets paid in stablecoin, by a foreign client.
> Indian tax law tells her exactly which day to value that payment.
> It does not tell her how.

**ON SCREEN:** Title card — plain text, "DIVERGENCE" — for the first
2 seconds, then straight into `output-interface.html`'s header:
"Payment received 28 June 2026, 03:14 IST · 5,000 USDC." No logo
animation, no music sting eating the first five seconds.

---

## 2. PROBLEM — ~0:15–0:50

**SAY:**
> A single prompt settles on one number: ₹4,69,750.
> A different method — equally legal, same statute — reads ₹5,17,618.76.
> The gap: ₹47,868.76. Ten point one nine percent of the payment.
> Neither number is wrong.
> Nothing in the market tells you that gap exists.

**ON SCREEN:** `output-interface.html`, section **02 — What it was worth
in rupees**. The two-method dimension line: `₹469,750` left, `₹517,619`
right, the red `₹47,869 · 10.19%` gap label centered. Static, no
scrolling — let the numbers sit.

**SOURCE:** `runs/21aug/D1_final_seed2.json` →
`valuation.methods[1].inr_value` = `469750.0`,
`valuation.methods[4].inr_value` = `517618.76`,
`valuation.spread.inr` = `47868.76`, `.percent` = `10.1903`.

---

## 3. COMPONENTS — ~0:50–1:20

**SAY:**
> Ten steps make this work. Five call a model.
> Five are plain code — code that cannot invent an answer, no matter
> what the model upstream says.
> Every citation a model produces gets checked, right here.
> Real corpus text. Real tax year. If it doesn't match — it's dropped.
> Not flagged. Dropped.

**ON SCREEN:** First ~15s: `flowchart.png`, full frame, held static —
long enough to read the five 🤖 nodes and five ⚙ nodes, not a fast pan.
Next ~15s: cut to `citation_matcher.py`, `verify()` and the `Verdict`
dataclass (lines ~165–183) in an editor, syntax-highlighted, held
static — no scrolling, no typing. This is the ~10 seconds of code
Devpost's own guidance calls for: purposeful, not a tour of the
repository.

**SOURCE:** `divergence/flowchart.png` (regenerated from
`make_flowchart.py`, real model names baked into the image, not a
caption). `divergence/citation_matcher.py`, `verify()` — the function
that returns `Verdict(status=..., accept=...)`; `accept: bool` is the
one field the rest of the pipeline actually reads.

---

## 4. DEMO — ~1:20–2:40

### 4a. The lattice and the uncertainty budget (~1:20–1:45)

**SAY:**
> Twelve methods. Real arithmetic, not a guess.
> Lowest, ₹4,69,750. Highest, ₹5,17,618.76.
> The gap breaks into four real parts.
> Domestic premium: ₹44,715.57. The big one.
> Which price in the day. The peg. Which official date.

**ON SCREEN:** `output-interface.html` section 02, click open the
`<details>` "Where the spread actually comes from — decomposed by
source." Hold on the four budget lines.

**SOURCE:** `valuation.uncertainty_budget[]` — domestic premium
`44715.57`, which price within the day `5506.05`, the proxy `565.57`,
which official date `250.0`.

### 4b. The election toggle (~1:45–2:05)

**SAY:**
> Now watch. I tick one box.
> ₹4,69,750 — recorded, right here, in this browser.
> I tick the other. ₹5,17,618.76 — recorded instead.
> Either way, the record stays complete. Nothing was pre-selected.

**ON SCREEN:** The `<fieldset>` at the bottom of section 02. Click
radio `ea` — status line updates live. Click radio `eb` — updates
again. This is real, running JavaScript in the opened file, not a mock.

### 4c. One honest evidence beat (~2:05–2:40)

**SAY:**
> We tested our own adversarial checker with four planted defects.
> It caught three.
> It missed the fourth — a real citation, misapplied, sitting in the
> text it was given.
> We publish that miss at the same weight as the three wins.

**ON SCREEN:** Cut to `results.md`, the ablation table — D1-a, D1-c,
D1-d marked **CAUGHT**, D1-b marked **NOT CAUGHT**, the miss visually
no smaller or greyed-out relative to the three catches.

**SOURCE:** `results.md`, "The ablation — 4 planted defects" — 3/4
caught, D1-b (Rule 57 row 7 misapplied to a s.92 receipt) missed
outright, exact 95% CI [19.4%, 99.4%] disclosed in the same table this
project already publishes.

---

## 5. CLOSE — ~2:40–3:00

**SAY:**
> This scales on concurrency, not on tokens.
> On the open models actually used for this evaluation, this cost zero
> rupees, metered.
> Now the limit. Look at this exact record.
> It still says no deduction applies, because the payer is outside
> India. Our own adversarial checker attacked that claim. The attack
> landed.
> The claim is still in the file. We chose not to fix it. We chose to
> show it to you instead.

**ON SCREEN:** ~5s: `README.md`'s Cost table (`₹0 metered`). Cut to
`runs/21aug/D1_final_seed2.json`, `regimes[0].outcome`, highlight *"No
deduction obligation arises under s.393(1)... the payer is outside
India."* Immediately cut to `runs/21aug/D1_final_seed2_attack.json`,
`attacked[1]`, highlight `"survived": false` and the attack text. **Hold
this final frame, unmoving, for the last 3 seconds.** Fade to black.
No closing card, no logo, no "thank you for watching" slide — the
attacked claim is the last thing on screen.

**SOURCE:** `README.md` Cost table (`₹0 metered — plan-tier access`).
`runs/21aug/D1_final_seed2.json` → `regimes[0].outcome`.
`runs/21aug/D1_final_seed2_attack.json` → `attacked[1].survived == false`.
`results.md`, "Where we lose": *"the frozen demo record, still asserts
an unsupported s.393(1) exemption... Frozen anyway, per the
pre-registered selection rule and the hard-stop."*

---

## Publishing — the one accidental-disqualification risk

**If this is uploaded to YouTube, mark it "Not for Kids."** COPPA
restrictions otherwise block judges from accessing an unmarked video —
a real, avoidable disqualification risk that has nothing to do with the
content, and everything to do with a checkbox in the upload flow. Set
this before the link goes into the submission, not after.

## Full run-through, sanity check

| Section | Approx. duration | Cumulative |
|---|---|---|
| 1. Introduction | 15s | 0:15 |
| 2. Problem | 35s | 0:50 |
| 3. Components | 30s | 1:20 |
| 4. Demo (a+b+c) | 80s | 2:40 |
| 5. Close | 20s | 3:00 |

**Total: ~3:00.** Not a hard deadline the way the earlier draft's 150s
was — trim section 4c first if the edit runs long; it's the one beat
with a natural shorter version (state the 3/4 result without dwelling
on the ablation table visual).
