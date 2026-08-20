# PROJECT LOG — DIVERGENCE
### One running record of everything we have done, found, and changed.
### Updated every session. Nothing is deleted — only struck through, so we can see what we believed and when.

**Last updated: 6 August 2026**

> **Correction (6 Aug):** entries for Steps 1–8 were dated 4 August in error. The work was done 4–6 August. Bounty 1 is therefore closer than earlier entries implied.

## ⏰ CONFIRMED DEADLINES
- **Bounty 1 — Five-Year Vision:** closes **9 Aug 23:59 UTC−5** = **10 Aug 10:29 IST**. Five days.
- **Bounty 2 — Feedback Loop:** opens 9 Aug, closes **15 Aug 23:59 UTC−5** = **16 Aug 10:29 IST**
- **Main project:** 17 Aug 10:30 IST
- Bounty submission is by Google Form, opening 2 days before each deadline
- **Bounty judges are not specialists — explain every technical term**

---

# WHERE WE STARTED AND WHERE WE ARE NOW

**We started with:** a pile of problem statements collected from different hackathons, and one idea of our own about stablecoin payments and blockchain evidence.

**We are now at:** a single sharp project for one hackathon, one track, with the blockchain removed, a verified legal gap at its centre, a quantified economic value, and a 40-step plan.

**The idea travelled a long way. That travel is the work.**

---

# PART A — WHAT WE DID BEFORE THE 40 STEPS

## A1. Chose the hackathon

We looked at Reverie Hacks and its six tracks. We also had Amex-style corporate themes and a Web3 brief in hand.

**What we got:** clarity that Reverie is a high school hackathon, 2–17 August, judged by generalist engineers and product managers from big tech companies.

**What changed:** we dropped the Amex themes completely. They need card data, merchant data and bank systems we do not have. With fake data they would look hollow.

## A2. Found our real asset

We realised the stablecoin brief was written by us, from our own deep research — not given by anyone.

**What we got:** the understanding that our research depth is our main advantage, and we should not throw it away to start something new.

**What changed:** everything after this point builds on that research instead of replacing it.

## A3. Ran four deep research passes

We ran adversarial research designed to *disprove* our own idea, not confirm it.

**What we got:**
- The valuation gap is **real and verified** — no prescribed method exists for valuing a digital asset in rupees at a point in time
- The blockchain part is the **weak** part, not the strong part
- The escrow idea is already built by Circle (open source, April 2025)
- The FEMA problem means a permanent public record is evidence *against* the user
- Immutability proves *when*, not *what*

**What changed:** we learned to attack our own ideas. This later became a feature of the product itself.

## A4. Removed the blockchain

**What we got:** every fatal objection disappeared at once — FEMA self-incrimination, the DPDP privacy conflict, the evidence-law weakness. And we lost nothing, because the valuable part was always the reasoning, not the ledger.

**What changed:** the project became an AI reasoning project instead of a blockchain project.

## A5. Chose the track

**Chose ML Prompt Engineering.** Highest cash prize, internship slots, no build risk, and the track's own wording is almost a description of our plan.

## A6. Got the real rubric

This was a turning point. The four criteria on Devpost are not the real scoring document.

**What we got:** six categories, 105 points, **four independent judges**, plus 20 bounty points. Total 440.

**What changed:** effort moved away from building and toward evidence, presentation and accessibility. Because everything is multiplied by four, a small sub-criterion is worth much more than it looks.

## A7. Built the 40-step roadmap

Ten phases, gates between each, contingencies written in advance.

---

# PART B — THE 40 STEPS

## STEP 1 — Reverse-engineer the rubric
**4 August · Complete**

### What we did
Mapped all 26 scorable sub-criteria. For each one, wrote what a generous judge needs to see and what a hostile judge will attack.

### What we got
- **The 4× multiplier changes priorities.** Accessibility looks like 5 points but is really 20, because four judges each score it. It costs about five hours and most teams score zero on it
- **UX & Design is worth 60 points** — the same as Innovation. We were treating it as an afterthought
- **Six sub-criteria are at absolute zero**, worth about 100 real points, needing roughly 30 hours — and none of it is technical building
- The ML track's Technical Execution wording is almost a description of our plan: *"measurable improvement over a naive baseline; documented iteration and testing across inputs and edge cases"*
- There is a **live judging slot with scored Q&A**. All three of us will be questioned

### What changed
- Accessibility promoted from optional to required
- Iteration log became a first-class deliverable, started immediately
- **New idea: the ablation study.** Run the pipeline with a node removed and show what breaks. This turns "why seven nodes?" from our weakest question into our strongest moment

---

## STEP 3 — Define the problem
**4 August · Statement complete, 30-second test still pending**

### What we did
Stress-tested the draft problem statement through five different voices — a non-technical reader, a hostile judge, a chartered accountant, an engineer, and a pitch-focused reader.

### What we got
- **The draft read as the ordinary "AI is sometimes wrong" complaint.** Every judge has heard that. We would have scored middling on Innovation and deserved it
- **The fix became our core idea:** *An AI can say "I don't know." It cannot say "nobody knows."*
- **Legal undecidability is not intuitive.** Most people assume the rule exists somewhere. The abstraction must always travel with a concrete example
- **Our value proposition was wrong.** A CA already knows the law is unclear — that is her job. What she lacks is **coverage**
- **A much stronger number:** on one $5,000 invoice, ₹5,14,400 one way and ₹4,73,250 the other. **₹41,150 apart, both defensible, no rule choosing**

### What changed
- Pitch now opens with a person, never with the word "crypto"
- Value reframed from revealing ambiguity to finding all of it
- We must measure and report our **abstention rate** — a system that says "unclear" about everything is noise

---

## STEP 4 — Excavate the root cause
**4 August · Complete**

### What we did
Ran the five whys to seven levels. Broke the problem into six sub-problems. Researched the academic literature on AI uncertainty and the legal philosophy of indeterminacy. Studied ten other fields that solved similar problems.

### What we got
- **The chain does not stop at five.** Why 6: this failure is undetectable by checking, because there is no truth to check against. Why 7: nobody fixed it because "correct" is undefined, so normal machine learning has nothing to optimise
- **We were using the wrong legal term.** Hart's *open texture* (1961) = the rule exists but is vague. A **lacuna** = no rule exists at all. **Ours is a lacuna**
- **The uncertainty literature has a gap we can claim.** It has aleatoric (world randomness — a coin flip still has a 50% answer) and epistemic (model ignorance — a true answer exists). Ours is neither: **normative indeterminacy**, where nobody has decided
- **Prior art is closer than we assumed.** A 2025 paper uses AI to annotate vague terms in regulatory text. Our differentiator: *they annotate the text; we resolve the case and price the disagreement*
- **Our best citation:** a 2026 formal-reasoning legal AI paper names our exact problem as its own unsolved limitation
- **Two borrowed patterns worth six hours:** accounting's fair value hierarchy (Level 1/2/3 by input observability) and metrology's uncertainty budget (decompose the spread by source)
- **Two analogies that answer hard questions:** auditors issue a *disclaimer of opinion* — a whole profession is paid to say "we cannot form a view." And Hoare's null-pointer mistake — absence must not be allowed to masquerade as a value

### What changed
- Added observability levels and an uncertainty budget to the design
- Split the certainty labels into *lacuna* and *open texture*
- We now say "our corpus is silent," never "the law is silent" — an honest fix
- Twelve other domains identified where the same failure appears

---

## STEP 4b — Folded the research back into the pitch
**4 August · Complete**

### What we did
Updated the problem statement to v2 with the new findings.

### What we got
A rule we will keep permanently: **the one-liner and 30-second version stay free of jargon.** Depth goes into the 3-minute version and a Q&A reserve. A generalist judge should never have to learn a word to follow the pitch.

### What changed
Four new defences added — against "isn't this just abstention?", "isn't this open texture?", "hasn't someone done this?", and "how is this different from an error bar?"

---

## STEP 5 — Map stakeholders and users
**4 August · Complete**

### What we did
Challenged the assumption that the CA is the buyer. Instead of asking *who has money*, we asked **what does each stakeholder lose in rupees today, and does our output change that number.**

### What we got

**⭐ The biggest finding of the whole project so far.**

**Section 270A(6) of Indian tax law is almost a written specification for our output.** The penalty is 50% of tax on under-reported income, and 200% for misreporting. But 270A(6) excludes three things from under-reporting:
1. A **bona fide explanation with all material facts disclosed** → our disclosure record
2. Income **based on an estimate where the basis was disclosed** → our dual valuation with the method named
3. A **difference of judicial opinion on a question of law** → that is a lacuna, exactly

*Reliance Petroproducts* (2010) 322 ITR 158 (SC) supports the principle: an unsustainable claim is not the same as inaccurate particulars.

**What it is worth**, on our ₹41,150 divergence at a 30% slab:

| Outcome | Total exposure |
|---|---|
| Misreporting (200%) | ₹37,035 |
| Under-reporting (50%) | ₹18,518 |
| 270A(6) exclusion | ₹12,345, no penalty |

On **one** invoice. A monthly biller has twelve.

**Other findings:**
- **The product is insurance, not productivity.** That is a completely different price point, so the ₹115/year anchor stops mattering
- **This settles our hardest objection.** *"Does saying it's unclear help?"* — yes, by statute
- **We had missed a stakeholder who gates everything:** the **assessing officer**. He never pays us and decides whether the product works. If the format is not legible to him, the defence does not land
- **Second missed stakeholder:** professional indemnity insurers for CAs — a distribution channel where the payer is neither sufferer nor practitioner
- **The CA's pain is coverage, not confusion.** Rajesh cannot check forty rate lookups, so he checks the largest three and signs
- **Our range creates an ethical problem.** A range with two legitimate ends is also a menu for someone who has already decided. **Fix: require an election and record that the user knew the alternative existed.** Cherry-picking becomes *disclosed* cherry-picking — which is exactly what 270A(6) rewards. The risk becomes the feature
- **Failure is asymmetric.** False abstention costs a conversation. False confidence costs a statutory defence worth up to 200% of tax

### What changed
- Value proposition rewritten around 270A(6)
- Output must be written for an assessing officer's eye, in the statute's own language
- Recorded election step added to the final node
- **Fail toward abstention** adopted as a stated design principle, with the rate measured and published
- Corpus files must be versioned and dated, with the version shown in the output
- Two new interview questions, now the most valuable we have: *would an assessing officer find this legible?* and *do you already produce a disclosure note for disputed positions?*

---

## STEP 6 — Talking to real people
**4 August · Plan complete, outreach not yet sent**

### What we did
Read the Discord history for bounty rules. Researched the Indian filing calendar to understand recruitment timing. Ranked outreach channels by realistic yield. Wrote the outreach messages. Built a pre-registered prediction bank of 20 expected responses.

### What we got

**From Discord:** bounties are on slide 32 of the opening ceremony deck in `#getting-started`. Submission is by a Google Form that opens **2 days before each deadline**. No pre-registration. Most importantly — an organiser said **bounty judges are not specialists and technical terms should be explained**. Calendar dates for Day 1/7/8/14 are still unanswered, so three questions were drafted to post.

**The filing calendar changes the recruitment plan.** AY 2026-27 introduced staggered deadlines for the first time: ITR-1/2 by 31 July, and **ITR-3/ITR-4 — the forms freelancers file — by 31 August 2026.** So right now every CA in India is in peak season for exactly our target client type.

**That is bad for asking favours and excellent for asking questions.** Our users are doing the thing we're solving *this week*. So the message changes from *"can we interview you about a problem"* to *"you're filing these right now — how are you handling it?"* The first is a favour; the second is an opinion they formed twenty minutes ago.

**The highest-yield channel is the one nobody thinks of: your own family's CA.** Three families, three CAs, three WhatsApp messages. That alone meets the target.

**The second-best is articled assistants (CA trainees)** — because the trainee does the actual Excel reconciliation while the partner forms a view. They feel the pain most directly, they're reachable, and nobody ever asks them anything.

**Third: post a public question on CAclubindia rather than requesting an interview.** CAs answer public questions for reputation — it's marketing for their practice. No scheduling needed.

**The single biggest tactical lever:** put one question *in* the first message. Never ask for a call first. "Reply whenever" costs ten seconds; "schedule 30 minutes" costs a calendar decision.

**We also wrote 20 predicted responses** — clearly labelled as predictions, never to be shown as evidence. The method is pre-registration: write what you expect, then the *surprise* is the finding. It gives a strong Q&A answer: *"we predicted X, we heard Y, we changed Z."*

**The most likely dominant CA answer is "tell them to refuse crypto."** That is not a reason to abandon the project — it is a quote for the pitch: *"they're right, and people accept it anyway because it clears in forty seconds instead of six days. We're for the gap between correct advice and what actually happens."*

### What changed
- **Bounty 1 must be written with zero jargon** — this is now a scoring instruction, not a style choice
- Outreach reframed around live filing season rather than abstract interest
- Recruitment target lowered from 20 cold contacts to 3 warm ones plus public forum posts
- Bounty 2 no longer blocked on CA recruitment — freelancers qualify as target audience
- Five specific findings identified that would change the project, including the dangerous one: *"my CA never asked me about the rate"* would mean the pain is latent, not felt

### The line we will not cross
No fabricated interviews, not one line. If nobody replies, we report that honestly: *"we contacted 24 people during peak filing season, four responded, here is what we could not verify."* A judge who has done real research respects that more than a suspiciously smooth account.

---

## STEP 7 — Audit existing research, close the gaps
**4 August · Complete**

### What we did
Audited every finding from the four research reports as reusable / discard / verify. Researched the three listed blocking gaps. Found a fourth nobody had listed.

### What we got

**⭐ THE FOURTH GAP — and it is the project happening to us.**

We have been citing **Rule 11UA** as the central fact of the whole project. That citation was correct until **1 April 2026**, when the Income-tax Rules, 1962 were replaced and everything was renumbered. **Rule 11UA is now Rule 57.**

Our citation was fluent, plausible, well-sourced and stale. Four adversarial research passes, a fact-check and a red-team review all missed it — because every source we read still says "Rule 11UA," including material published this year, and they were all reading each other.

**That is exactly the failure our system is being built to detect, and we did it to ourselves on our own headline fact.**

**Gap 1 — section numbers.** Section 194S is now **Section 393(1), Table Sl. No. 8(vi)**, effective 1 April 2026. The entire 194-series is eliminated; payments are now identified by numeric codes (1001-1067) and table references under ss.392/393/394. Rates and thresholds unchanged. **Still unresolved:** the new numbers for 115BBH, 2(47A) and 270A — every practitioner source in mid-2026 still uses the 1961 numbering, which is itself informative.

**Gap 2 — data.gov.in.** Cannot be closed by searching. Somebody must register for a key and call the endpoint. Bundled with the kill-gate check. **Fallback discovered:** Rule 115 mandates the **SBI Telegraphic Transfer Buying Rate**, not FBIL, for income conversion — and using an average rate is legally incorrect. Notably, **SBI does not quote USDC at all**, and for currencies SBI does not quote you must convert via a major currency first. So the one prescribed conversion rule does not cleanly apply to our case either — which strengthens the lacuna argument.

**Gap 3 — our competitor claim was too strong and must be reworded.** Koinly *does* disclose: it uses CoinMarketCap/CoinGecko averages, shows the source in transaction details and in the export, and converts to INR using **European Central Bank daily forex rates**. "Every tool picks one silently" is false as written and a judge could disprove it in thirty seconds.

**The reworded version is sharper:** *Koinly discloses which aggregator it used and converts to INR using a European central bank's rate. It does not tell you that FBIL exists, that Rule 115 mandates the SBI TTBR, that the Indian exchange price differed by 8.5%, or that the choice is unresolved in Indian law.* **It discloses the input. It does not disclose the decision.**

That last line is the whole product in eight words — and it is now defensible rather than exaggerated. It is also not an accusation of bad faith, which makes it more credible: Koinly is a global tool applying a global default.

### What changed
- **New test case (C10), possibly our best:** ask both systems which rule prescribes fair market value. The single prompt will almost certainly say Rule 11UA, confidently, because its training data and most of the internet still say so. Ours says Rule 57 and can show when it changed. This demonstrates **staleness** — a third failure type, distinct from both hallucination and a lacuna — and it is verifiable by any judge in thirty seconds
- **Corpus versioning is now mandatory**, with each file recording the current number, the former number, the retrieval date and the supersession date
- Every citation in the pitch needs a re-check pass, in dual form: new number, old number in brackets, date of change
- Competitor claim rewritten everywhere

### The three lessons
1. **Consensus is not verification.** Every source agreed because they were all reading each other. Agreement between secondary sources tells you they share an origin, not that they are right
2. **The question is not "is this true" but "true as of when"**
3. **This is now the best story in the pitch.** Not "AI gets things wrong" — everyone says that. But *"we built a system to catch this, and it caught us"* is specific, honest, verifiable and slightly funny

### Still unresolved
New section numbers for 115BBH / 2(47A) / 270A · new rule number for Rule 115 · whether data.gov.in is live · whether KoinX discloses its source in the export · whether SBI publishes retrievable historical TTBR charts.

**U11 (section numbers) is the priority.** Wrong section numbers in a live Q&A is the most avoidable way to lose credibility in this project.

---

## STEP 8 — Verify novelty properly
**4 August · Complete**

### What we did
Searched hard for prior art on uncertainty-aware legal AI, abstention, self-critique pipelines and legal indeterminacy — deliberately trying to *find* competition rather than confirm we had none.

### What we got

**Two of our three "novel" mechanisms are not novel, and someone published our core diagnosis three months ago.**

- **Abstention is a mature subfield.** AbstentionBench, I-CALM (2026), a full survey on uncertainty quantification, work showing abstention avoids ~50% of hallucinations. Saying "we made an AI that can abstain" would make us look unread
- **Self-critique nodes are very well-trodden.** Self-Refine, Reflexion, CoVe, CRITIC, DeCRIM, DISC, Double-Checker, ALIGNRAG, multi-agent debate. Node 6 is not novel as a mechanism
- **⚠️ Gur-Arieh, "LLMs and the Collapse of Legal Indeterminacy," SSRN, May 2026** — argues legal indeterminacy is a feature not a bug, that LLMs clash with it "more insidiously than rule-based systems," and that indeterminate language "imposes an irreducible burden of judgment, and that burden has to be discharged somewhere." **That is our problem statement, published by a legal academic in May**

**Why the Gur-Arieh paper is a gift rather than a threat.** It independently validates the problem's importance (worth more for Impact than our own assertion), it is a *diagnosis not a system*, and it leaves open exactly the question we answer: **where** the burden gets discharged. Our answer — by the human, visibly, with alternatives priced and the choice recorded — responds directly to an open question a law review posed three months ago. Citing it makes us look informed; being asked about it unprepared would have been fatal.

**A design lesson we would otherwise have got wrong.** The literature is explicit that *intrinsic* self-correction without external signals is fundamentally unreliable, and that "the refinement loop is only as good as the feedback channel." A Node 6 that just asks the model to argue with itself would be a known-weak design. Ours must be grounded externally — mechanical citation matching against the corpus, and checking whether a conclusion depends on a field the gap detector marked missing.

**The reframe that survives everything — and it came from noticing a pattern across the whole literature.**

Every approach treats uncertainty as a property of *the model*, to be reduced or hidden: calibration matches confidence to accuracy, abstention withholds the answer, self-critique fixes mistakes, UQ measures unsureness. **All of it is about the model's relationship to a knowable truth.**

Nobody treats uncertainty as a property of *the world* that must be handed to the user as a decision. When the law has not decided, both standard moves fail — you cannot reduce the uncertainty (the missing thing is a legislative decision, not information), and you cannot abstain (she still has to file by 31 August).

**The third move, not found anywhere: resolve every defensible way, price the difference, require the user to elect one on the record.**

**Name it: from abstention to election.**

| | Abstention | Election |
|---|---|---|
| Trigger | Model is unsure | World has not decided |
| Output | "I don't know" | Both answers + cost of the difference |
| Who decides | Nobody | The user, on the record |
| Value | Avoids a wrong answer | Creates a defensible position |

### What changed
- **C14** Cite Gur-Arieh and answer it directly in the documentation
- **C15** Reposition Node 6 — claim the external grounding and the *published attack*, not the mechanism. Every system in the literature uses critique to improve the answer before you see it; ours degrades the answer and shows you the attack
- **C16** Adopt "from abstention to election" as the headline novelty framing
- **C17** Node 6 must be externally grounded, not intrinsic
- **C18** Soften the third-uncertainty-category claim to "our framing," never "we discovered"
- **C19** Add a prior-art section to the documentation — citing what exists is a strength

### The novelty claim, final
> Existing work on uncertainty in AI tries to reduce it or withhold an answer. When the law itself has not decided, neither is possible — the user must still file a number. We resolve the question every defensible way, quantify what the disagreement costs in rupees, and require the user to elect one on the record — producing exactly the contemporaneous disclosure that Section 270A(6) rewards.

Every clause is defensible. Nothing claims a mechanism we did not invent.

### The lesson
We went in expecting to confirm novelty and found most of our mechanisms are standard. **That is the correct outcome of an honest novelty search.** A team that claims everything is new has not looked. A team that can say "these six things exist, we use four of them, here is precisely the one that doesn't exist yet" is far more credible — and that is exactly what the Innovation criterion asks.

---

## STEP 9 — Build the statutory corpus
**6 August · Design complete, files not yet built**

### What we did
Treated this as a design problem rather than a filing task. Worked out what the corpus is actually for, found a hole in our headline claim, and borrowed the fix from how legal opinions and audit reports are written.

### What we got

**⭐ The silence problem — a genuine hole in our central claim.**

Our system says "our corpus is silent on how to value a VDA in rupees." But **silence only means something if the corpus was supposed to cover it.** If we loaded ten provisions out of an Act with hundreds of sections, "silent" might just mean we didn't load the right one. A judge can ask this in one sentence: *"How do you know there's no rule, rather than that you didn't include it?"* We had no answer.

**The fix comes from two professions that solved this centuries ago.** Legal opinions have a "Scope and Limitations" section. Audit reports have a "Scope of Audit" paragraph. Both say exactly what was reviewed. **You earn the right to make a negative claim by declaring what you looked at.**

So the corpus needs a **MANIFEST.md**, and the silence claim gets scoped: *"Within the provisions listed in our manifest — which we assert cover the valuation of a VDA received as consideration for services under Indian income tax law — no method is prescribed."* Longer, weaker-sounding, and actually defensible.

**To prove a lacuna you must include the rule that fails.** You cannot put an absence in a folder. Rule 57 (formerly 11UA) must be stored **complete and untruncated**, precisely because it is the rule that *doesn't* cover VDAs — the absence is only demonstrable against the full enumeration. And if we truncated it and the omitted part mentioned VDAs, our central finding would be an artifact of our own editing, invisible to us.

**Five conflicting jobs.** Grounding wants more text; citation matching wants exact text; boundary definition wants scope completeness; the context window wants brevity. Resolved by a **Tier A / Tier B split** — verbatim and citable vs summarised and structurally non-citable, with the matcher rejecting any Tier B citation.

**Scoped loading per node — a failure mode we would have shipped.** The roadmap assumed one corpus in every resolver. But if the GST resolver can see FEMA provisions, it will eventually cite them. Cross-regime contamination is likely. Each node now gets only its own regime's text: smaller prompts, contamination structurally impossible, and silence scoped per regime.

**⚠️ A new risk: the current law may be harder to obtain than the superseded law.** Every government page found in Step 7 still shows 1961 Act / 1962 Rules text, four months after the renumbering took effect. So building a corpus of the law *as it stands* is genuinely hard right now. Decision: use the superseded text plus the mapping table, dual-cite, and **state the limitation in the output** via a `known_limitation` field.

**That is the product working on itself.** Asked "how do you know your law is current?", we show a field where we admit exactly where we're unsure. It also explains why the Rule 11UA error happened — not carelessness, but that the accessible record lags the law.

### New brainstorm: the manifest as a product feature
Show the manifest to the user. *"This conclusion reviewed 11 provisions. Here they are, here is when each was checked, here is what we did not look at."* Nothing in this space does that. It answers the trust question before it's asked, makes staleness visible to the user rather than only to us, and puts the disclaimer in the professional form a CA already recognises from every legal opinion she has read. Extends naturally into a public dated corpus changelog for Bounty 1.

### What changed
C20 manifest declaring scope · C21 Tier A/B split, only A citable · C22 scoped loading per node · C23 load-bearing provisions full and hashed, never truncated · C24 `source_type` distinguishing current/superseded/mapping · C25 silence claim scope-limited · C26 manifest as user-visible feature · C27 Singapore and UAE deliberately shallow, labelled indicative

### Validation of earlier steps
- ✅ "No vector DB needed" **holds**, and scoped loading strengthens it — each prompt now sees 1–2k words
- ⚠️ "The model can only cite what you gave it" is **only true with the Tier A/B split plus the matcher**. Without them it will still cite from memory
- ⚠️ s.270A is a 1961 Act section; its 2025 equivalent is still unconfirmed, and our value proposition rests on 270A(6)
- ⚠️ Rule 57 comes from a **mapping table, not the bare Act**. Must be verified before it becomes load-bearing

### New questions
Is the 2025 Act bare text available officially anywhere? · What is the 2025 equivalent of s.270A? · Can Rule 57 be confirmed from a primary source? · What if a provision changes during the hackathon? · Should the manifest appear in the demo?

### One-line summary
**The corpus is not a folder of files. It is a written declaration of what we looked at — which is the only thing that makes "we found no rule" different from "we didn't look."**

---

## RESOLUTION PASS — closing the open questions
**6 August · Complete**

### What we did
Worked every unresolved item from Steps 5, 7, 8 and 9 one by one. Five resolved, three partially, five need a human rather than a search, four became interview questions.

### What we got

**⭐ 1. Section 270A is now Section 439 — and our value proposition cites a sub-section, which also moved.**

s.270A → **s.439**, effective 1 April 2026. s.270AA (immunity) → **s.440**, Form 68 → **Form 161**. And critically:

| Old | New |
|---|---|
| **s.270A(6)** | **s.439(8)** |
| s.270A(6)(a) bona fide + material facts | **s.439(8)(a)** |
| s.270A(6)(b) estimate with basis disclosed | **s.439(8)(b)** |
| s.270A(7) 50% | s.439(9) |
| s.270A(8) 200% | s.439(10) |

**Every mention of "270A(6)" in our material is a stale citation.** That is the second time in three days — but we caught this one ourselves.

**A condition we had missed:** 439(8)(b) requires that *"the accounts are correct and complete."* The exclusion is not automatic. Our output supports disclosure of the basis; it does not fix bad bookkeeping. State this openly.

**⭐ 2. The biggest prior art yet, and we had completely missed it: FIN 48.**

**Thomson Reuters ONESOURCE Uncertain Tax Positions** (formerly TaxStream FIN 48) keeps an inventory of uncertain positions, calculates tax and interest per position, maintains a full audit trail, and supports deciding what to disclose — under **ASC 740-10-50 / IAS 37**. Structurally our product, shipped, for corporations, since around 2007.

**The concept of a formally managed, quantified, disclosed uncertain tax position is not new. It is an accounting standard.**

**But this makes us stronger, not weaker.** We are not first to think tax uncertainty should be quantified and disclosed — we are first to bring it where it is missing:

| | FIN 48 / ONESOURCE | Us |
|---|---|---|
| Who | Corporations with tax directors | Individuals and their CAs |
| Detection | **A human decides it is uncertain** | **The system finds it** |
| Granularity | Position level, annual cycle | **Transaction level, at the moment** |
| India, individuals | **No equivalent exists** | |

**The reframe:** *"Large corporations have had a formal framework for uncertain tax positions since 2006 — a standard, an inventory, a reserve, a disclosure. A freelancer in Pune has a CoinGecko screenshot. We are bringing an established professional discipline down to the transaction level, for the people who never got it."*

Far more credible than claiming to invent a category. And it pre-answers *"isn't this just FIN 48?"* — yes, conceptually, and that is the point.

**3. Partial evidence that the penalty exclusions are live.** A tribunal quashed a 270A penalty where the notice failed to specify which limb applied and where income arose from legislative deeming. Tribunals do scrutinise the classification. **Not yet found:** the exclusion succeeding specifically on a valuation-method dispute. Claim the mechanism, not the precedent.

**4. 2025 Act text is obtainable** from unofficial full-text sources with faithful sub-section structure. Flag as `unofficial_full_text`, verify against indiacode before anything load-bearing rests on it. This resolves the Step 9 dilemma better than expected — we are not stuck with superseded text.

**5. Decided: Q4 corpus freeze policy.** Freeze at a stated datetime; every output carries `corpus_frozen_at`; changes go in the manifest changelog, never a silent update. **Q5: yes, the manifest goes in the demo.**

### What changed
C28 recite 439(8)(a)/(b) everywhere, dual form · C29 adopt the FIN 48 lineage as the primary value framing · C30 add ONESOURCE to prior art · C31 state the "accounts correct and complete" condition as a limitation · C32 demote the third-uncertainty-category claim to a footnote · C33 corpus may use 2025 Act text pending verification · C34 corpus freeze policy · C35 rewrite interview question U7 around uncertain-position logs

### Three hours of human work closes almost everything left
data.gov.in key test · KoinX export check · SBI TTBR archive · Rule 57 primary confirmation · verify 2025 Act text against indiacode. One focused sitting.

### The pattern worth noticing
**Twice now our headline citation has been stale — and both times we found it ourselves.** Rule 11UA → 57, and now 270A(6) → 439(8). It will keep happening, which makes corpus versioning practical rather than theoretical. And a judge asking *"how do you know your citations are current?"* now gets a real answer: *"we have caught ourselves twice, here is the process that caught us, and here is the field that tells you when we last checked."*

**Every strong claim in this project now has a professional ancestor** — IFRS 13 for observability levels, metrology for the uncertainty budget, auditing for the disclaimer of opinion, legal opinions for the scope manifest, FIN 48 for uncertain positions. That is not coincidence. **It means the problem is real, because serious people already solved it — for someone else.**

---

## C28–C35 APPLIED
**6 August**

Updated five files: `users.md` (270A→439 throughout, FIN 48 framing, the "accounts correct and complete" limitation), `novelty.md` (ONESOURCE/FIN 48 added as closest prior art; third-uncertainty-category claim demoted to a footnote), `problem-statement.md` (3-minute pitch now leads the value section with the FIN 48 lineage), `step-6-interviews.md` (U7 rewritten around uncertain-position logs), `step-9-corpus.md` (C33 unofficial 2025 text as primary route, C34 `corpus_frozen_at`).

---

## STEP 10 — Failure archaeology
**6 August · Protocol complete, experiments not yet run**

### What we did
Designed the experiment rather than running it — no live model access here, and inventing observed failures would poison the most important evidence in the submission. Same line we drew on interviews.

### What we got

**⭐ The reframe: sort failures by DETECTABILITY, not by type.**

The roadmap's list — numeric confusion, date errors, fabricated citations, silent rate selection — sorts by *what went wrong*. That is natural and wrong for us. Sort instead by *whether the user can tell*:

| Class | Example | Cost |
|---|---|---|
| **1 Loud** | Malformed output, obvious nonsense | ⚪ Near zero — user notices |
| **2 Checkable** | Fabricated section, wrong date, misread figure | 🟡 Real, but a careful CA catches it |
| **3 Silent** | Confident rupee figure where no method is prescribed; no mention a choice was made | 🔴 **The whole reason this project exists** |

**Three reasons this is the most valuable thing in the step:**
1. **It defines our territory.** Everyone builds for Class 2 — fact-checkers, citation verifiers. Almost nobody builds for Class 3, *because Class 3 has no ground truth to check against*. That is why it is unaddressed and why we can address it
2. **It gives us a metric nobody else will report:** **Silent Failure Rate** — the fraction of failures a competent CA would *not* have caught. "87% accurate" is one of many. *"The single prompt produced 11 silent failures in 30 cases; ours produced 1 and disclosed the other 10"* is not
3. **It rescues the evaluation if the baseline performs well.** A good single prompt might match us on extraction. It **cannot** win on Class 3, because those failures are structural, not accuracy-related. The comparison holds even against an excellent baseline

**Borrowed pattern #5: FMEA.** Engineering has scored failures as **Severity × Occurrence × Detection** for seventy years, with Detection weighted so that *harder to detect = higher risk*. **FMEA independently arrived at our reframe.** Aerospace, automotive and medical devices all treat the invisible failure as the top priority.

**What the pre-registered risk table already shows, before any run:** six of the top seven failures by risk score are Class 3. And the failures people naturally worry about — a blurry photo, broken JSON — score near the bottom, because the user can see them.

> **Our architecture is not designed against the failures that are most common. It is designed against the failures that are most invisible.**

That one sentence explains, in Q&A, why seven nodes and not three.

**Our own errors are data.** Twice this project has cited a retired provision — Rule 11UA after it became Rule 57, and s.270A(6) after it became s.439(8). Both are stale-citation failures. Both were invisible. Both survived four adversarial research passes. **Put them in the catalogue with evidence:** it proves the failure type without constructing a test, shows it affects careful motivated humans and not just models, and makes the staleness test case the most defensible in the set — we are asking the model the exact question we got wrong ourselves.

**The baseline prompt is written and frozen today**, before anything is built, so it cannot be unconsciously weakened later. It deliberately includes *"anything the taxpayer should be aware of"* — so if the model still does not say "the law prescribes no method here and I chose one," the failure is structural, not a prompt artifact.

### What changed
C36 sort by detectability · C37 FMEA scoring · C38 Silent Failure Rate as a headline metric · C39 five runs per input, record successes too · C40 label inputs natural/selected/constructed and report separately · C41 write and freeze the baseline today, publish in full · C42 include our own two stale citations · C43 node justification comes from risk score, not from the diagram

### Two questions that could hurt us, so run them first
**N1 — does a stronger reasoning model produce fewer Class 3 failures, or the same number more convincingly?** If more convincingly, our case strengthens as models improve.
**N2 — does adding one sentence, *"tell me what you were uncertain about,"* close most of F1?** If yes, a large part of our argument is a prompt-engineering result rather than an architecture result. **We need to know before a judge asks.** And the honest answer would still be good: *"one extra sentence closes 40%. Our pipeline closes 90%, quantifies the gap in rupees, and produces a record. But we'll tell you the cheap fix partly works, because pretending otherwise is exactly the behaviour we built this to prevent."*

### One-line summary
**Do not catalogue failures by what went wrong. Catalogue them by whether the user could tell — because the failures nobody can see are the only ones worth building a system against.**

---

## N-QUESTIONS + REMAINING UNKNOWNS — RESOLUTION
**6 August**

### ⭐ N1 — the strongest finding in the project

**Reasoning models are WORSE at this, not better. By 24%.**

AbstentionBench (arXiv 2506.09038, NeurIPS 2025), across 20 frontier LLMs: abstention is an unsolved problem, **scaling models is of little use**, and **reasoning fine-tuning degrades abstention by 24% on average** — even on the math and science domains reasoning models are explicitly trained for.

**And the mechanism, which is the part that matters:** reasoning models give *"definitive final answers even when their reasoning chains express uncertainty."*

**The model knows. The doubt exists inside the reasoning. It is destroyed on the way to the output.**

| | What happens to the uncertainty |
|---|---|
| Single prompt | Doubt appears in reasoning → final summarisation flattens it → **doubt is lost** |
| Our pipeline | Each node emits a typed output with a **mandatory certainty field** → doubt is a required value → **cannot be flattened** |

**New claim, and it is much better than what we had:** *"We don't make the model more uncertain. We stop its uncertainty being thrown away."* That is a mechanism, not a slogan, and it is grounded in published research.

**What this does:** answers the obsolescence question every judge is silently asking — *"won't GPT-6 fix this?"* The published answer is no, and the trend runs the other way. It also gives us a test case: same input through a fast model and a reasoning model; the literature predicts the reasoning model will be more elaborate, more confident, and more wrong.

### ⭐ N2 — answered by the same paper, honestly
*"A carefully crafted system prompt can boost abstention in practice, but it does not resolve models' fundamental inability to reason about uncertainty."*

**Partly yes, fundamentally no** — exactly the answer we prepared for. Our response: *"a better prompt helps and we'll show it. It doesn't fix the underlying problem, and a NeurIPS benchmark across 20 models says so. And a prompt still cannot compute the value two ways, mechanically verify a citation, check whether a required document exists, or produce a record the taxpayer signs. Those are system problems, not prompt problems."*

### N3 — cross-model disagreement
Worth adopting as a cheap flag: if two models disagree on a field, flag it. No calibration needed. **But claim the application, not the mechanism** — ensemble disagreement is established. And state the limitation: it catches Class 2 well and **Class 3 badly**, because two models can agree perfectly and both be silently wrong, having been trained on the same internet. *Agreement is not correctness* — the same lesson as *consensus is not verification* from Step 7.

### ⭐ U8 — RESOLVED, favourably, plus a correction

**The exclusion works in practice, repeatedly.** ITAT: penalty under this provision is *"discretionary, not automatic, and cannot be levied where the addition is based on a **difference in legal view or computational methodology** rather than suppression of income."* And: *"a bona fide, fully disclosed, debatable tax position cannot be penalised merely because the Revenue disagrees. Penalty provisions are not meant to punish differences in interpretation."*

**"Difference in computational methodology" is a valuation-method disagreement, in a tribunal's own words.**

Supporting: *Sangrur Vanaspati Mills* (SC, no penalty on estimate-based additions) · *T. Ashok Pai v. CIT* (SC, bona fide explanation discharges the burden; penalty quasi-criminal, mens rea essential) · *Samson Perinchery*, 392 ITR 4 (Bom HC, penalty cannot be levied on a different limb than initiated) · ITAT Bangalore ITA 676/BANG/2026.

**⚠️ CORRECTION to Step 5 — we cited the wrong limb.** Reading the verbatim text: limb **(b)** is about the *AO* estimating because the taxpayer's accounting method doesn't allow income to be deduced. Not our situation. **Our limb is (a) — bona fide explanation with all material facts disclosed** — and it is the better one, because that is where all the case law sits.

### What changed
C44 cite AbstentionBench prominently · C45 adopt the "we stop uncertainty being thrown away" mechanism · C46 correct to s.439(8)(a) · C47 add the case law language to the value proposition · C48 fast-model vs reasoning-model test case · C49 cross-model disagreement as a cheap flag, with its Class 3 limitation stated · C50 prepare the N2 answer · C51 add "would you actually check the section, in filing season?" to interviews

### The pattern, again
Every one of the last four research passes had the same shape: **we went looking to confirm something, found we were partly wrong, and the corrected version was stronger.** Abstention research supports us rather than undercutting us. A good prompt helps but doesn't fix it. We cited the wrong sub-limb and the right one has better case law. We thought we were inventing a category and we're extending a twenty-year-old accounting discipline.

**Being wrong quickly, in private, on purpose, is the whole method. It is also exactly what the product does.**

---

## C48–C51 APPLIED · STEP 11 — DIVERGENT BRAINSTORM
**6 August**

### C48–C51 applied
Test case B4 added (same input, fast model vs reasoning model — the literature predicts the reasoning model gives a longer, more confident, more citation-dense answer to a question with no answer). Cross-model disagreement added as a cheap flag, with its Class 3 limitation stated. Two new defences added to the pitch — the "just add a line to the prompt" question and the "won't better models fix this" question. Interview script now asks *"would you actually check the section, in filing season?"*

### Step 11 — 34 ideas from seven techniques

**The rule, and it is harder than it sounds: no judging at all during generation.** Evaluating and generating use opposite postures. Judging while generating kills the strange ideas first — and the obvious ones will still be there in an hour, while the odd ones vanish the moment you frown at them.

**Techniques used:** vary the axis (domain / user / output / timing) · steal the shape (linter, smoke detector, black box, devil's advocate, checklist, git blame) · extremes (one hour / one day / one year) · invert the beneficiary · remove the central component · make it a data product · combine two ideas.

**34 ideas generated against a target of twelve.**

### Four that surprised me

**#19 Second Opinion** — paste any AI tax answer, get told what it hid. **No document parsing at all.** A dramatically smaller build than the seven-node pipeline, and a 90-second demo: paste a ChatGPT answer on stage and watch the tool dismantle it.

**#23 The Checklist — with no AI whatsoever.** A one-page forcing structure for a CA. Only appears as an idea if you deliberately delete the component you are most attached to. Shape stolen from aviation pre-flight and the surgical safety checklist — the value is that it makes you stop at exactly the points people skip under time pressure.

**#26 The Lacuna List** — a single public page: *"The 12 places Indian tax law has no answer for crypto."* The one-day version might be more useful to real people than the full product, and it is a demo asset whatever else we build.

**#28 Sell to the Department** — **we assumed an adversary for eight steps without ever checking.** An assessing officer wants a legible basis as much as the taxpayer does; it saves him two letters and a dispute. A disclosure format the department itself endorsed would be adopted overnight.

### The structural observation about our own idea

Our current idea sits at one point in a large space: *tax domain · freelancer/CA user · full report output · at-filing timing · AI-centred · single-user.*

**All six coordinates were chosen without ever being examined.** They may all be right. But we now know they were choices rather than givens — which is the entire purpose of this step.

### Not done today
Criticism. That is Step 12: for each idea, *"how would I guarantee this fails?"* — then check whether we are accidentally doing any of those things to our current idea.

---

## STEP 12 — INVERSION AND PRE-MORTEM
**6 August · Complete**

### What we did
One strongest objection per idea, for all 34. Then turned inversion on ourselves. Then wrote three pre-mortems as stories in the past tense — a technique that produces far more candid reasons than asking people to predict risks, because the past tense unlocks honesty the future tense doesn't.

### What we got

**Three clusters of objection kept repeating:** cannot be validated in eleven days (anything needing an institution to cooperate) · wrong track or thin technically (the low-AI ideas) · **undermines its own thesis**.

**That third cluster is evidence FOR our direction.** Five separate alternatives failed *because* they contradicted a commitment we had already made — the Uncertainty Score compresses away the reasoning we're selling, the Refusal Router refuses when our user has a deadline, the Post-Notice Remediator abandons contemporaneity. Our core commitments are load-bearing, not arbitrary. We did not know that before.

### ⚠️ THE MIRROR TEST — the most useful thing this step produced

Asked how we would guarantee our *own* idea fails, then checked:

| To guarantee failure I would… | Doing it? |
|---|---|
| Leave the interface as default HTML | 🔴 **YES — zero design work. 60 points** |
| Miss the bounties while building | 🔴 **YES — Bounty 1 closes in three days, no draft** |
| Let one person carry it so only one can answer questions | 🔴 **YES — explicitly the arrangement** |
| Underestimate the 30 test documents | 🔴 **YES — not started, biggest single task** |
| Never speak to a real user | 🔴 **YES — zero interviews sent** |
| Open with Indian crypto tax and lose non-Indian judges | ⚠️ Partly — fixed on paper, video doesn't exist |
| Ship stale citations | ⚠️ Two caught, probably more |
| Design seven nodes, finish three | ⚠️ Live risk |
| Overclaim novelty | ✅ Fixed in Step 8 |

> **Of nine ways to guarantee failure, we are doing five and partly doing three. Not one is a thinking problem. Every one is an execution problem.**

**We have spent eleven steps making the idea sharper, and the idea was never the risk.**

### The three pre-mortems
**DIVERGENCE-Tax at 40/105:** pipeline worked; test corpus took six days not three so evaluation ran on nine cases; interface was a white page with Times New Roman; video spent 90 seconds on Indian tax law and lost two judges; one person answered all Q&A; Bounty 1 closed while everyone was writing prompts. **Nothing in the story is about the idea being wrong.**

**Second Opinion at 40/105:** demoed beautifully in 90 seconds, then a judge asked *"so it's a prompt that criticises another prompt?"* and there was no answer. Without documents there is nothing missing to detect, no two valuations, no budget, no election — every node that made the architecture interesting had nothing to operate on. **Too easy to build, and that shows in the only category that measures building.**

**The Checklist at 40/105:** three CAs said they'd use it. One asked for a copy. And it was submitted to the ML Prompt Engineering track with no prompt, no workflow and no baseline. **84 points forfeited on day one by choosing the wrong container for a good idea.**

### The five deep objections to our own idea

**⚠️ 1 — Custom may have already filled the gap.** A statutory gap and a practical gap are different things. If every CA says *"we use the exchange statement value, the department accepts it"* then convention has filled the lacuna even though statute hasn't — and a de facto standard makes a de jure gap practically irrelevant. **This could end the project, and only practitioners can answer it. It is now the single most important interview question.** If practice has converged, we pivot to *"here is the convention everyone uses, here is that it has no statutory basis, here is what happens when an officer challenges it."*

**2 — The insurance adoption problem.** Value is realised only if challenged: low probability, years away. People systematically under-buy protection against low-probability, high-cost, delayed harms — it's why flood insurance is under-purchased in flood zones. **This is the real reason the buyer must be the CA:** she sees 300 clients, so for her it isn't low-probability at all. We reached the right conclusion in Step 5 for a weaker reason; now we have the mechanism.

**3 — Our best example is evidence the market is dying.** The 8.5% spike happened *because* the ED raided crypto payment firms. The more vivid the illustration, the more it shows the flow is under attack. **Use the spike to make the gap visible; never make it the argument.** The gap exists at the normal 3–4% premium too.

**4 — Our most honest output is "you shouldn't have done this."** Harm reduction only. **We can never frame this as "crypto payments made easy"** — dishonest and self-defeating.

**5 — Nobody has to decide, and forcing a decision is friction.** Changes the design: **the election is one tap with a default**, not a form. Show the recommended method pre-selected, the alternative beside it, and record that both were displayed. **The record we need is "you were shown both," not "you agonised."** A better design, produced by an objection.

### What changed
C52 interviews must test Objection 1 first · C53 fix the five execution failures this week · C54 election is one tap with a default · C55 harm reduction framing only, never "made easy" · C56 the 8.5% spike is illustration not argument · C57 add the insurance-adoption mechanism to the buyer rationale

### The conclusion
The idea survived. Every alternative had a fatal objection, and five failed by contradicting commitments we'd already made — which is evidence those commitments are real.

**But: we are extremely well prepared and have not started.** The next thing that should happen is not more thinking. It is three WhatsApp messages, a bounty draft, and someone opening a design tool.

---

## EXECUTION PASS — closing the five failures
**6 August**

### What we did
Stopped thinking and started making. Three of the five guaranteed-failure routes are now closed by artifacts that exist.

### ✅ The interface — `output-interface.html`

**60 points that were sitting at zero.**

Design direction taken deliberately, and it is grounded in the subject rather than in software convention: **it looks like a document a professional would file, not a dashboard.** The second reader is an assessing officer, and a dashboard says "software output" while a document says "working paper" — one of which he already knows how to read.

Materials borrowed from Indian ledger stationery: cool grey foolscap rather than white, blue-black ink, and the red margin rule that runs down the left of a bahi khata. Money set in monospace because money is data. Labels set like the headings on a statutory form. Deliberately avoids the cream-and-terracotta look that AI design defaults to.

**Signature element: the divergence drawn as an engineering dimension line** — the kind used on a technical drawing to mark a measured distance, with tick marks at each end and the figure in the gap. Not a chart. A measurement. Because that is exactly what it is: a measured distance between two defensible positions, which ties back to the metrology ancestor from Step 4.

**Order enforced in the layout:** missing things first, the range second, a single answer never. The ordering *is* the argument.

**Accessibility done, not promised** — semantic HTML, visible keyboard focus, text labels beside every colour marker (never colour alone), phone width, reduced-motion respected. Roughly 20 points that most teams score zero on because nobody reads that line of the rubric.

**Election implemented as C54 specified:** one tap, default pre-selected, alternative beside it, and the line that matters — *"either way, this record states that both figures were shown to you."*

### ✅ Bounty 1 — `BOUNTY-1-five-year-vision.md`
Full draft, deliberately jargon-free because an organiser confirmed bounty judges are not specialists. Built around the rubric's own 9–10 descriptor: names the moment it might fail (a regulator publishes an official method), what we would cut first (everything except the record that both figures were shown), and success in numbers — with the honest note that **the only row that matters is "cases where the record was used in a real dispute."**

Includes all five deep objections from Step 12 as named obstacles with responses, because **grounded reality is 4 of the 10 points — the largest single sub-criterion in either bounty.**

### ✅ Execution guide — `EXECUTION-GUIDE.md`
Task 0 through Task 4, in order, with a dated schedule and a five-item done-check. Written so any of the three can pick it up.

### 🔧 Two that only humans can close
**Q&A readiness** — the 30-second test, recorded, three attempts each, plus the five questions split three ways. 45 minutes.
**The three messages** — and this is the only item whose clock we do not control.

### The single most important sentence in the outreach
> *"Is there a method everyone uses, or does each person decide?"*

That is Objection 1 from Step 12, in the form a busy accountant can answer in ten seconds. If the answer is *"everyone uses the exchange price"*, habit has already filled the gap we built around, and the product changes this week rather than in the last 48 hours.

### The state of play
Everything else on the list can be done at 2 a.m. on the 16th if it has to be. **A conversation with a chartered accountant cannot.**

---

## STEP 13 — SCORE AND SELECT
**6 August · Decision gate passed**

### What we did
Scored six surviving options against the real rubric weights — then, because a scoring matrix can be nudged to say whatever you already wanted, ran three cross-checks that use no scores at all.

### What we got

**A+B wins at 665/700, and all four checks agree.** The two rows that decided it:

**Generalist-comprehensible: A scores 2.** Two of four judges are likely not Indian and have never filed an Indian return. Ninety seconds of Indian crypto tax and half the panel is gone — and the damage propagates, because a disengaged judge scores everything lower.

**Sustainability: A scores 2.** *"Path to scale"* is in the rubric. A tool for a market enforcement is actively shrinking scores badly there — 40 points across four judges.

**Cross-check 1 (regret test):** A+B's regret — *"we may have oversold the general claim"* — is the only one on the list **fixable by wording**. Every other regret is structural.

**Cross-check 2 (what must be true):** A+B is the only option whose required belief is an established form of argument rather than a hope. *A specific verified case supporting a general claim* is how a medical case report, a legal precedent and an engineering failure analysis all work.

**Cross-check 3 (what gets discarded):** A+B discards nothing. Every other option throws away either the evidence, the depth, or twelve steps of research.

### ⭐ The recommendation was incomplete, and fixing it is the real finding

*"A's substance with B's framing"* does not say **when** to be which — and that ambiguity gets you the worst of both. Fully general loses "identifiable people," which the rubric names explicitly. Fully specific loses the panel.

**The answer is sequencing, not blending: open specific · widen once · land specific.**

Open with a person and a number (Priya, ₹41,150). Widen **once**, for thirty seconds, to say why it happens — rules are written before the situations arrive, so every regulated field has gaps and AI fills them by guessing. **Do not keep widening; that is where overclaim lives.** Then land back on the measurement.

The specific ends give *identifiable people* and *checkable numbers*. The wide middle gives *scale* and *comprehension*. Neither framing alone can do both.

### The four decisions, locked

**1. Framing** — specific → general → specific. One widening. Never open with "crypto."

**2. Node count — "five model calls and two deterministic checks," never "seven nodes."** That description was wrong and it was costing us. A model call and a piece of deterministic code are not the same kind of thing, and lumping them together hid the most reassuring fact about the architecture: **some parts cannot hallucinate, because they are not models.** Intake merges with extraction; 5a/b/c collapse into one resolver run three times with the corpus scoped per pass, which keeps the contamination protection. In Q&A, *"why seven nodes?"* becomes *"five model calls each doing one job, wrapped in two checks that are ordinary code and therefore cannot make things up."*

**3. Jurisdictions — India only in the system.** Singapore and UAE cut from the build entirely; kept as one pitch slide labelled as research. Zero build cost, zero risk of the system producing a wrong foreign answer, keeps the 2/1/0 visual. **The scalability proof is the non-crypto receipt — one proof done properly beats two done thinly.**

**4. Name stays.** DIVERGENCE names the symptom, not the product, but renaming costs consistency across a dozen documents and buys little. Fixed with a line instead: ***"DIVERGENCE — a record of what the law didn't decide."***

### What changed
C58 framing sequence locked · C59 five model calls + two deterministic checks · C60 intake merged, resolvers collapsed · C61 SG/UAE cut from build · C62 one scalability proof · C63 descriptor added · C64 architecture diagram must visually separate model calls from deterministic checks

### The thing worth remembering
**The winning option required no change to what gets built.** We spent the step choosing between six products and found the real choice was about **the order we say things in** — which costs nothing, changes no code, and moves two of the biggest scoring rows.

**Before optimising what you make, check whether the cheaper win is in how you explain it.** It usually is, and almost nobody looks there first.

---

## STEP 14 — SCOPE CONTRACT · GATE C
**6 August · Complete, pending three signatures**

### What we did
Wrote the scope contract — and doing it honestly surfaced a contradiction in our own design.

### What we got

**Two lists is the wrong shape.** *"We didn't build multi-invoice matching because we ran out of time"* and *"we will never tell anyone what tax to pay"* are not the same kind of statement. One is a **deferral**, one is a **boundary**. In a single list the deferrals look pompous and the principles look alarming — *"so you'd give tax advice if you had another week?"*

**Three tiers instead: In Scope · Deferred (time) · Permanently Out (principle).** Plus a fourth list nobody writes.

**A list can't anticipate everything, so the contract needs a test** any one of us can apply alone at midnight without a meeting:

> **Does this help us prove the law had no answer — or does it help us give one? If it helps give an answer, it is out.**

**The underrated job of a scope contract is making refusal cheap.** On 14 August someone will say *"wouldn't it be cool if…"*, and without a contract saying no means arguing against a teammate's enthusiasm at 11 p.m. **With one, the document says no and nobody has to.**

### ⭐ The fourth list: OUT OF SCOPE FOR CLAIMS
Scope is not only what you build — it is what you *say*. Seven sentences we will not use, each with its replacement. **Every row is a claim we actually made at some point and had to correct**: "every tool picks silently" → "they disclose the input, not the decision"; "we discovered a third category" → "we think this is a case the standard split doesn't cover"; "the law prescribes no method" → "within the provisions in our manifest".

### ⚠️ THE CONTRADICTION THE CONTRACT FOUND

**Rule 1: we will never tell anyone what tax to pay.**
**Decision C54: the election is one tap, with a default pre-selected.**

**A default is a recommendation.** Defaults dominate choice — it is one of the most reliably demonstrated effects in behavioural science. By pre-selecting a valuation method we would be quietly doing the exact thing we said we would never do.

**Resolution — and it dissolves the problem rather than trading it off.** Ask what the record actually needs: under s.439(8)(a), a bona fide explanation with all material facts disclosed. **The material fact is that both figures existed and both were shown.** Which one was filed is already in the return.

**So the election was never required for the record to work.** It is optional, the record is valid without it, there is no friction because nothing is demanded, and there is no advice because nothing is pre-selected. The section becomes *"if you have already decided, record it here"* — a place to put an answer they already have, not a question we ask.

**Objection 5 said forcing a decision is friction. The resolution wasn't to reduce the friction — it was to notice we never needed the decision.**

**C65 applied: pre-selected default removed from `output-interface.html`.**

### One in-scope choice worth saying out loud
**Stablecoins only is a choice, not a limitation.** A volatile token would make the gap bigger and our argument easier. We are using the hardest case for our own claim on purpose: *"even a coin designed to be worth exactly one dollar produces a ₹41,150 disagreement on a single invoice."*

### 🚪 GATE C
✅ Matrix filled, winner chosen, rationale written · ✅ Scope contract written · ✅ Name chosen — **DIVERGENCE, *a record of what the law didn't decide***

**Passable once three people sign. Nothing else blocking.**

### The thing worth remembering
**Writing down what you refuse to do makes you check whether you are already doing it.** We weren't looking for a bug. We were writing a list, honestly, and the honesty found one.

---

## STEP 15 — KILL GATE
**6 August · Script written, NOT YET RUN**

### What happened
**I could not run it.** My sandbox blocks CoinDCX, Binance and data.gov.in — all three returned HTTP 403 from the network proxy. Tested, not assumed.

So `killgate.py` was written to run on your machine: standard library only, nothing to install, one command. It probes five possible CoinDCX pair codes (nobody has confirmed which carries the INR market), reports how far history actually reaches, pulls the USDC peg from Binance, gets USD/INR from two fallbacks, caches to `./cache/`, and prints GO or NO-GO.

### The decision it produces
- **History reaches June 2026** → headline stays the divergence. **Recompute ₹41,150 from real data and use the real number**
- **API works, history too short** → try 1h/4h intervals, look for startTime params, or cite the news reports as clearly-labelled secondary
- **Blocked** → switch to the weekend case

### Why the fallback is genuinely good
A payment at 03:14 on a Sunday needs **no historical data at all.** FBIL publishes only on Mumbai working days, so no official rate exists for that moment **by design, permanently, reproducibly.** Arguably a cleaner proof that the law has no answer than a one-off market spike — and it sidesteps Objection 3, since the June spike was caused by an enforcement raid and therefore doubles as evidence the market is being suppressed.

**Status: UNRESOLVED. Record the outcome today either way.**

---

## STATE OF PLAY — consolidated
**6 August**

### Open questions
**Eleven items blocked on a human this week**, totalling about four hours of hands-on work plus interviews: the kill gate · section numbers 115BBH/2(47A)/Rule 115 · Rule 57 from a primary source · data.gov.in · KoinX export · SBI historical rates · and five interview questions.

**Six answerable by experiment during the build** — N1 through N4, abstention rate, and whether we can honestly distinguish "no rule exists" from "we failed to retrieve."

### Remaining brainstorm — parked, not killed
Ten threads logged for Bounty 1, documentation, or later. **The one worth actually pulling: B1, corpus completeness as a measurable property.** Write ten questions whose answers you know are in the eleven provisions, run them, see whether the system finds them. **Every product in this space asserts its coverage; nobody measures it.** Two hours, and it turns "we checked eleven provisions" into "we checked eleven provisions and verified they answer the questions we claim they answer."

### Validation backlog — three red rows
**All three are answered by the same conversation:**
- Custom has not filled the gap in practice → **project pivots if wrong**
- A CA would use and pay for this → business model unproven
- An officer would find our format legible → the 439(8) story weakens

Everything else is verified or predicted-and-testable.

### Engineering feasibility
**≈61 hours total, three people, eleven days — about two hours each per day.** Feasible with real slack, which is the right position because every estimate is optimistic.

**Five real risks:** rate data (resolved today) · **test documents always take longer than anyone believes** · OCR on bad photos · 600 model calls (cache by input hash, never re-run) · corpus text availability (partly solved).

**Three decisions that already lowered risk:** no vector DB or RAG framework (deletes chunking, retrieval tuning and embedding drift as bug categories, and makes citations *more* reliable) · no orchestration framework (five sequential functions is not a framework problem) · **deterministic checks are ordinary code, not model calls** — the difference between *"we ask the model to verify"* and *"we string-match and reject on no match."* One is a hope, the other is a guarantee.

**Build order rule: test data before code.** Build the pipeline first and you'll unconsciously shape the ground truth to fit what it already does.

### The honest summary
**Thinking: essentially complete.** Fourteen steps, five deep research passes, three corrections to our own headline claims, a scope contract that found a bug in our own design.

**Building: not started. Validating: three red rows, one conversation.**

**We are as well-prepared as any team in this competition and further from a submission than most.**

---

## RESEARCH RESULTS — open questions worked
**6 August**

### ⭐ I retrieved the real rate data

SBI does not archive its own rates. But an independent GitHub project (`sahilgupta/sbi-fx-ratekeeper`) has stored the daily SBI forex PDFs and CSVs since January 2020, with a link to each original PDF for verification. **GitHub is reachable from the sandbox, so I pulled it.**

| Date | Day | SBI TT BUY |
|---|---|---|
| 25 Jun 2026 | Thursday | **94.00** |
| 26 Jun 2026 | Friday | **not published** |
| 27–28 Jun | Sat–**Sun** | — |
| 29 Jun 2026 | Monday | **93.95** |

**A four-day hole.** SBI skipped the Friday too. **The weekend case is now verified from archived data with a PDF link for every figure**, and needs nothing further.

### ⭐ The headline number was wrong, and the real one is bigger

**₹41,150 was computed from the interbank rate, which has no standing in Indian tax law.** Rule 115 mandates the **SBI TT buying rate**, and CBDT's own ITR instructions make that specific rate mandatory — not RBI's reference rate.

Recomputed on $5,000 with the rate the law actually requires:

| Method | Rate | INR |
|---|---|---|
| A — Indian market | 102.88 | ₹5,14,400 |
| **B — Rule 115 SBI TTBR (25 Jun)** | 94.00 | **₹4,70,000** |
| ~~interbank~~ | 94.65 | ₹4,73,250 |

**New headline: ₹44,400 on one $5,000 invoice. 9.45%.**

**Using the legally correct rate made the gap bigger and the claim more defensible at the same time.** Say that out loud: *we switched to the rate the law actually mandates, and the disagreement grew.*

Caveat to state honestly: the ₹102.88 leg is still news-reported. The B leg is now archived primary data. **Run `killgate.py` to put them on the same footing.**

### ⭐ A third choice nobody prescribes — the gap has a gap

Do the correct thing, use Rule 115's SBI TTBR — **and there is no rate for 28 June.** So you must choose between the last published before (25 Jun, ₹94.00) and the next published after (29 Jun, ₹93.95). **Nothing prescribes which.** ₹250 on this invoice.

₹250 is small. **That it exists at all is not** — it shows the indeterminacy is structural, not a one-off. Now a third line in the uncertainty budget.

### ⭐ U11 resolved differently, and it reframes our "stale citation" story

Three searches failed to find a new number for s.115BBH. The fourth explained why: **both numbering systems are simultaneously live.**

*"Your ITR for FY 2025-26, filed in July 2026, still uses the old 1961 Act and its old section numbers. The new numbers apply from Tax Year 2026-27 onwards — returns you'll file in July 2027."*

| Income in | Filed | Cite |
|---|---|---|
| FY 2025-26 | July 2026 (now) | 1961 Act — 115BBH, 194S, 270A(6), Rule 11UA |
| **FY 2026-27** | July 2027 | 2025 Act — 393(1) T8(vi), 439(8)(a), Rule 57 |

**Our demo payment is 29 June 2026 — FY 2026-27 — so the 2025 numbering is correct for it.**

**So we were not simply stale. We were citing without saying which tax year.** More precise, more defensible, and more interesting — it converts an embarrassment into a demonstration.

**New test case (C70):** same transaction in February 2026 and June 2026. Does either system notice the section numbers differ? Almost certainly not. Verifiable, not a trick, and a failure type with nothing to do with hallucination — applying one framework to a period governed by another.

**And a CoinDCX guide published within the last week still leads with "Section 115BBH of the Income-tax Act, 1961."** Four months after the new Act took effect. Not sloppiness — the 1961 numbering is still correct for the return being filed this month. **The ambiguity is real, and it is exactly what gets flattened into a confident wrong answer.**

### Official mapping sources exist, including a .gov one
**incometax.gov.in** publishes a *Guide to IT Act 2025 forms* mapping PDF. **ICAI** published a tabular mapping of all sections and schedules. Plus taxbizmantra (searchable, downloadable Excel), tax2win, cleartax, caalokkumar.com. **Thirty minutes closes U11, U12 and Q3 — and ICAI is a better source tier than the blog mapping we were using.**

### A fourth undetermined choice, noted in passing
For days SBI does not publish, the practitioner workaround is to take the RBI reference rate and adjust by the "standard delta" of 20–30 paise. **Entirely reasonable, and with no statutory basis whatsoever.** One line in the pitch.

### What changed
C66 headline is ₹44,400 / 9.45% on SBI TTBR · C67 label the A leg as reported until confirmed · C68 third choice into the uncertainty budget · C69 **cite provisions with the tax year attached** · C70 Feb-vs-June test case · C71 download ICAI mapping and taxbizmantra Excel · C72 the RBI-delta workaround as a fourth choice · C73 sbi-fx-ratekeeper as a corpus data source

**All numbers updated across eight files and the interface.**

### The pattern, one more time
We went to check a number and found **the number we had been using came from a source with no legal standing.** Correcting it made the gap larger and the claim safer. Correcting it then surfaced a **third** undetermined choice we did not know existed. Chasing a section number revealed **both numbering systems are simultaneously correct**, depending on a fact we had never specified.

**Every check has found something, and no check has weakened the project.** Strong enough now to say in Q&A: *the more carefully we look, the more gaps we find — which is the thesis.*

---

## OBJ-1 PARTIAL · STEP 16 BASELINE FROZEN · SCHEMA LOCKED
**6 August**

### OBJ-1 — negative evidence only, still red
Searched for what practitioners publicly say about which rate to use. **The search mostly returned noise — "VDA" collides with a token called Verida, a search-hygiene lesson worth remembering.**

But one real signal: **across every guide read in this entire project — CoinDCX, ClearTax, Cointelegraph, CAclubindia, KoinX — not one names a rate source for INR valuation.** They all cover the 30%, the 1% TDS, thresholds, Schedule VDA. **They all skip the single most practical question a reader has: which price do I use?**

**If a settled convention existed, these guides would state it** — it is the first thing a reader needs. That is negative evidence and it is worth something. **But absence in guides is not proof of absence in practice.** OBJ-1 stays 🔴 and only a practitioner closes it.

**Stopped searching this.** The marginal value has dropped and the answer lives in a WhatsApp reply.

### ⭐ Step 16 — the baseline prompt, written and frozen
**Written 6 August, before any pipeline code exists**, precisely so it cannot be weakened in hindsight. Not through dishonesty — through ordinary bias. After a week building a pipeline, nobody writes a genuinely strong single prompt.

**Every line exists to make it harder to beat.** It explicitly asks the model to do the four things our pipeline exists to do:
- *"and the basis on which you arrived at that figure"* → disclose the valuation method
- *"and any that appear to be missing"* → absence detection
- *"including anything you are uncertain about or where the law is unclear"* → flag the lacuna
- *"where you make an assumption, state it"* → disclosure

**If it still fails, the failure is structural, not a prompt artifact.** That is the whole fairness argument, and this prompt is what proves it.

**Nine predictions registered in advance.** P3 is the experiment: *does it mention that no method is prescribed, despite being asked directly?* Everything else is supporting detail. **If P3 is wrong, a large part of our argument is a prompt-engineering result and we say so** — then pivot emphasis to what a prompt cannot do: compute both figures, decompose the gap, mechanically verify citations, produce a record.

**Rules: do not edit it, publish it in full, report every case where it wins.** *A baseline you adjusted after seeing its score is not a baseline — it is a target you moved.*

### ⭐ Schema locked — `schema.json`
Every decision from fifteen steps now sits in one machine-readable contract:

- **`tax_year` is required on every citation** (C69) — both numbering systems are live, so no provision may be cited without it
- **`missing[]` carries `blocks[]`** — and `depends_on_missing` **forces** certainty to `insufficient_evidence` in deterministic code, not by asking nicely
- **`valuation.methods` has `minItems: 2`** — a single figure is a schema violation, not a valid output
- **`date_choice`** captures the gap-inside-the-gap (R99) — where the mandated source did not publish, record the second undetermined choice, never resolve it silently
- **`uncertainty_budget[]`** decomposes the spread by source (metrology)
- **`observability` L1/L2/L3** (IFRS 13) — vocabulary any finance-literate reader knows
- **`certainty` separates `lacuna` from `open_texture`** — no rule exists vs a rule exists but is vague. FEMA is always `inference`, never `settled`
- **`attacked[]`** publishes the attack rather than silently revising (R35)
- **`election` is nullable** — the record is valid without it (C65), because a default is a recommendation
- **`citation.verified`** is set by the string matcher; false means **rejected**, not flagged
- **`limits[]` has `minItems: 1`** — if it is ever empty, the record is wrong

---

## BASELINE REHEARSAL + SCORING SHEET
**6 August**

### The methodological caveat that came first
**I cannot run the baseline as a clean experiment — I am a contaminated observer.** Having spent this project learning that no method is prescribed, that Rule 11UA became Rule 57, that SBI published nothing from 25 to 29 June, anything I produce drifts toward the pipeline's answer and **understates the baseline's failure.** Wrong direction for the evidence.

**A real run needs a fresh session with no prior context, five times, on two models.** So what was produced is a **rehearsal, clearly labelled as illustrative and never to appear in the submission as a result.**

### What the rehearsal shows
An illustrative single-prompt output, then the failure map. The output is fluent, well organised, and **mostly correct** — two-stage income tax right, GST risk identified, missing FIRC caught. **It would pass most reviews.**

**Nine failures, and seven are Class 3 — invisible to the reader:**
- One figure, no mention another defensible one exists
- *"The prevailing market exchange rate"* — **which market is never named**
- ₹94.65 is the **interbank rate, which has no standing in Indian tax law**. Not one of several options — a source the law does not recognise
- *"Standard approach"* asserted, uncited, and untrue
- Settlement was 03:14 Sunday; it reports Monday and applies a rate as if one existed
- 115BBH and 194S cited **with no tax year**
- **"Non-compliant with FEMA" stated flatly** when it is an inference

### ⭐ The one that matters — §6
The prompt asked in plain English for *"anything you are uncertain about or where the law is unclear."*

It returned **"crypto regulation in India is evolving"** and **"consult a professional."** True, general, useless — and a liability hedge rather than a disclosure.

**It did not say: no method is prescribed, I chose one, another defensible choice gives a different number.**

**The model was asked directly and still could not say "nobody knows."** That is the thesis in one paragraph.

### And what it does well — say this out loud
The correct parts are correct. **That is precisely the danger. A wrong answer that looks wrong is harmless. This looks right.**

### The scoring sheet
One page per run, 30 runs per model. Structured around **what the output does not say**, not how it reads. Two numbers come out: **Silent Failure Rate** (Class 3 per run, baseline vs pipeline — the headline metric nobody else will report) and **P3 hit rate** (how often it names the missing method when asked directly).

**Protocol: fresh session every time, no follow-ups, save every raw output including the good ones, two scorers independently on the first five.** Contamination is the easiest way to ruin this and it is invisible once it happens.

### The warning printed at the bottom of the sheet
*You are about to read thirty responses that all look competent. The temptation will be to score them as passes, because they are well written and mostly correct. **That temptation is the reason your project exists.** Score against what the output does not say, not against how it reads.*

---

## STEP 17 — CITATION MATCHER BUILT AND TESTED · ABSTENTION PROTOCOL
**6 August · The citation half is done in code**

### What we built
`citation_matcher.py` — deterministic, no model call, standard library only. It validates a citation against the real 14-file corpus and returns `accept: True/False`. **The pipeline reads that boolean. False means the conclusion is dropped, not flagged.**

**What it checks:** does the citation exist in our corpus, is it **current for the stated tax year**, is it from a citable tier.
**What it does not:** whether the provision actually *supports* the proposition. **Existence is not relevance.** Stated as limitation #1.

### The tax-year check is the unusual part
Because both numbering systems are live, **a citation without a tax year cannot be validated at all** — it returns `REJECTED_NO_TAX_YEAR`. Nothing else in this space does that, and it falls straight out of the finding that FY 2025-26 and FY 2026-27 are governed by different Acts.

### The self-test — and it catches our own two errors

| Citation | Year | Verdict |
|---|---|---|
| Rule 57 | FY 2026-27 | ✅ VERIFIED |
| **Rule 11UA** | **FY 2026-27** | ⛔ **STALE → cite Rule 57** *(our error #1)* |
| **Rule 11UA** | **FY 2025-26** | ✅ **VERIFIED — correct for that year** |
| **Section 270A(6)** | FY 2026-27 | ⛔ **STALE → cite s.439(8)** *(our error #2)* |
| Section 74A CGST | FY 2022-23 | ⛔ STALE → ss.73/74 |
| **Rule 11UB** | — | 🔴 **REJECTED — fabricated** |
| **Section 115BBI** | — | 🔴 **REJECTED — real section, not in corpus** |
| **Section 56(2)(xiv)** | — | 🔴 **REJECTED — fabricated sub-clause** |
| Rule 57 | *none given* | ⛔ REJECTED — no tax year |

**15/15. 8 accepted, 7 dropped. Every drop by code.**

**The matcher catches both of our own historical errors automatically** — and correctly accepts Rule 11UA when the tax year makes it right. That is the demo: paste in our own mistake and watch it get caught.

### ⭐ Three versions, and the third bug is the interesting one

**v1 — 12/15.** Substring matching. Three false negatives on *real* citations: sub-clause depth (`439(8)(a)`), act-name variants (`IGST Act` vs `Integrated Goods and Services Tax Act`), and multi-provision files (`Sections 3, 7 and 8`).

**v2 — 14/15.** Rewrote to parse every citation into `(instrument, base number, bracket chain)`, with bracket chains matching on prefix. All three v1 failures were the same underlying error: **comparing strings instead of references.**

**v3 — 15/15.** The last failure **was not in the code.** The corpus header read `"Section 50, CGST Act 2017 — with a note on ss.73, 74 and 74A"` — so parsing that field pulled out **four** references and the wrong file matched first.

> **The data was wrong, not the logic. And only the test found it.**

**Rule adopted: a citation field contains a citation, not a note about one.** Notes go in a separate key. Corpus header cleaned.

**All three versions are in `iteration-log.md`** — which is exactly what the rubric's *"documented iteration"* clause asks for, and it is real rather than reconstructed.

### The abstention half — protocol only, no model access
Five prompt variants to test, in increasing order of enforcement:
1. Plain instruction — *"say insufficient_evidence if a required field is missing"*
2. Instruction + the gap list injected into context
3. JSON schema with `insufficient_evidence` as a required enum value
4. Schema + a post-check that **rejects** any conclusion depending on a field marked missing
5. Cross-model: run twice, disagreement forces abstention

**Prediction: 1 and 2 fail, 3 helps, 4 is the one that works.** Published research says a crafted prompt boosts abstention but does not resolve the underlying inability — so expect the enforcement, not the instruction, to do the work. **The same lesson as the citation matcher: a rule you can't enforce isn't a rule.**

### Where this leaves us
**The citation half of Step 17 is complete and demonstrable.** The abstention half needs a live model, so it belongs with the build.

---

## ⭐⭐⭐ THE PROJECT FILES CONTAINED THE NOTIFIED 2026 RULES — THREE FINDINGS
**6 August · Corpus 16 files · All code bundled**

Searched the project knowledge. `En-Notified-IT-Rules-2026-20-03-2026.pdf` is **the actual Gazette of India notification of the Income-tax Rules, 2026.** It was sitting in the project the whole time.

### 1. ✅ Rule 57 confirmed from the gazette — no longer an inference

**"57. Determination of fair market value.– For the purpose of following sections referred to in column B of the Table below…"**

| Sl. | Section | Nature of property |
|---|---|---|
| 1 | ss.26(2)(j), 92 | Jewellery |
| 2 | ss.26(2)(j), 92 | Archaeological collections, drawings, paintings, sculptures, work of art |
| 3 | ss.26(2)(j), 92 | Quoted shares and securities |
| 4 | ss.26(2)(j), 72, 92 | *(unquoted shares)* |
| 5 | — | *(per rule 53's cross-reference)* |

`source_type` upgrades from `mapping_table` to **`official_gazette`**.

### 2. ⭐ U11 CLOSED — the section mapping, from column B

**Rule 57's column B names the sections it serves. s.56(2)(x) → SECTION 92.**

| 1961 Act | 2025 Act |
|---|---|
| s.56(2)(x) | **s.92** |
| s.28(via) inventory conversion | **s.26(2)(j)** |
| Rule 11U | Rule 56 |
| Rule 11UAE / slump sale | Rule 53, s.77 |
| s.55A valuation officer | s.91(1)(b), Rule 55 |

**And the list still contains no virtual digital asset.** The 2026 Rules were notified **20 March 2026**, four years after VDAs entered the Act. **The drafter rewrote this rule from scratch and still did not add them.**

> **This is no longer an old rule nobody updated. It is a NEW rule, written in 2026, that leaves the same gap.**

### 3. ⭐⭐⭐ INDIA HAS PRESCRIBED A CRYPTO VALUATION METHOD — AND IT IS NOT FOR THE TAXPAYER

The 2026 Rules contain a full valuation waterfall for **reporting crypto-asset service providers** under s.509:

| Step | Method |
|---|---|
| (ii) | The crypto/INR trading pairs **it maintains** |
| (iii)(A) | Its **internal accounting book values** |
| (iii)(B) | **Third-party aggregator websites** |
| (iii)(C) | Its **most recent valuation** |
| **(iii)(D)** | ***"a reasonable estimate may be applied as a measure of last resort"*** |

**Three consequences, and each is large.**

**(a) The thesis gets sharper, not weaker.** Not *"nobody has worked out how to value crypto in rupees."* Rather: **the government worked out a four-step method, wrote it into the Rules, and applied it only to exchanges. The person who has to file got nothing.**

**(b) ⭐⭐⭐ The prescribed method ends in an admission.**
> **The only crypto valuation method India has ever prescribed ends by saying: make a reasonable estimate.**

**We no longer assert the question has no settled answer. The Rules say so, in the last line of the only method they contain.**

**(c) ⭐⭐⭐ Sub-clause (iv) is our product, already mandated.**
> *"the method shall be indicated in Form No. 167"*

**Method disclosure — required by Indian law, for crypto valuation, in force from 1 April 2026 — for exchanges.**

| | Exchanges | Our freelancer |
|---|---|---|
| Prescribed waterfall | ✅ | ❌ |
| Duty to disclose the method used | ✅ **Form 167** | ❌ |

**Our product is not a novel idea. It is the discipline India already imposes on exchanges, applied to the person who actually has to file.**

**This is FIN 48 again — an established discipline that never reached the individual — except this time it is Indian law, about crypto, in force this year.**

### Handling the counter: "so use the RCASP waterfall"
1. **Scoped by its own terms** to s.509 reporting, not to computing taxable income
2. **She cannot follow it.** Three of four steps need *"trading pairs it maintains"*, *"internal accounting book values"*, *"the most recent valuation by the RCASP."* **She is not an exchange**
3. **The one step she could use is (iii)(B) — third-party aggregator websites — which is exactly the CoinGecko screenshot everyone already takes.** The Rules would bless the practice, if only they applied to her

**Say all three. The third lands hardest.**

### Code bundled
`run_all.py` (one command runs everything) · `HOW-TO-RUN.md` (folder layout, step 0, troubleshooting) · `killgate.py` · `citation_matcher.py` · `schema.json`.

**Matcher re-tested against the expanded 16-file corpus: still 15/15.** 8 accepted, 7 dropped.

---

# STEPS 18-40
*Not started.*

---

# PART C — HOW THE IDEA CHANGED OVER TIME

| Stage | What we thought it was | What killed or changed it |
|---|---|---|
| Start | On-chain evidence layer for stablecoin payments | Four adversarial research passes |
| After research | Same, but with the fatal problems visible | FEMA makes the record self-incriminating; DPDP conflicts with immutability; timestamps prove *when* not *what* |
| After track choice | An AI reasoning workflow, no blockchain | Every fatal objection vanished; nothing of value was lost |
| After Step 3 | "AI is confidently wrong about tax" | Too generic — sounded like the usual hallucination complaint |
| After Step 4 | "AI cannot represent a lacuna in law" | Grounded in Hart 1961 and a third uncertainty category |
| **After Step 5** | **"We produce the evidence that qualifies you for a statutory penalty exclusion"** | Not a calculator. Insurance |

**The pattern:** every time we attacked our own idea, it got smaller, sharper and more defensible.

---

# PART D — KEY FACTS AND NUMBERS WE CAN USE

| Fact | Where it came from |
|---|---|
| No prescribed method exists for valuing a digital asset in rupees at a point in time. Rule 11UA was never amended | Verified across four research passes |
| The official rate is published once a day, weekdays only, from a random window between 11:30 and 12:30 | FBIL methodology |
| USDT ₹102.88 vs interbank ₹94.65 on 28–29 June 2026 — 8.5% apart | The Block / CoinDesk / Economic Times |
| On a $5,000 invoice that is **₹41,150** | Our own arithmetic — still to be verified against raw data |
| Penalty: 50% under-reporting, 200% misreporting, 0% under the 270A(6) exclusion | Section 270A |
| CBDT issued **44,057** communications for under-reporting in this exact area | Parliament reply, December 2025 |
| GST failure means 18% IGST + 18% interest + penalty | IGST s.2(6), CGST s.50 |
| FEMA non-compliance is an **inference**, not an explicit ban | FEMA s.2(n) with ss.7–8 |

---

# PART E — DECISIONS MADE

| # | Decision | Why |
|---|---|---|
| D1 | Category champions assigned | Accountability per category |
| D2 | Iteration log format and cadence fixed | The rubric scores documented iteration |
| D3 | Problem reframed to the general form | Fixes the 40-point significance weakness |
| D4 | Accessibility required, not optional | 20 real points for about five hours |
| D5 | Ablation study added | Pre-empts "why seven nodes?" |
| D6 | Interviews are top priority | Longest lead time; serves three scoring areas |
| D7 | Team charter deferred; async working accepted | Availability. Q&A risk noted |
| D8 | Lead with "I don't know" vs "nobody knows" | Separates us from the generic hallucination point |
| D9 | Abstraction never travels without an example | Undecidability is not intuitive |
| D10 | Value reframed from revelation to coverage | CAs already know the law is unclear |
| D11 | Open with the person; land ₹41,150 fast | Concrete beats conceptual |
| D12 | Never open a pitch with "crypto" | The case study is not the scope |
| D13 | Root cause extended to why-7 | Explains undetectability and why the field left it alone |
| D14 | Lacuna vs open texture as distinct terms | Ours is a lacuna |
| D15 | Claim normative indeterminacy as a third category | Neither aleatoric nor epistemic covers it |
| D16 | Acknowledge nearest prior art with our differentiator | Honesty beats being caught in Q&A |
| D17 | Observability levels L1/L2/L3 in the schema | IFRS 13 pattern; recognised vocabulary |
| D18 | Uncertainty budget in the valuation node | Metrology pattern; visual and rigorous |
| D19 | Say "our corpus is silent," never "the law is silent" | Honest |
| D20 | Workflow now; formal hybrid as the five-year path | Ships now, credible roadmap for Bounty 1 |
| D21 | One-liner and 30-second version stay jargon-free permanently | Judges should not have to learn a word |
| D22 | Value reframed to 270A(6) evidence | Quantified and statutory |
| D23 | Recorded election step added | Closes the cherry-picking hole |
| D24 | Output legible to an assessing officer | He gates whether the product works |
| D25 | Fail toward abstention, and measure it | Asymmetric harm; own the bias publicly |
| D26 | Version and date every corpus file | Silent staleness is a real harm |
| D27 | Buyer is the CA on liability grounds, not budget grounds | She has exposure she cannot evidence |

---

# PART F — ASSUMPTIONS STILL UNTESTED

| # | Assumption | How we test it |
|---|---|---|
| A1 | Historical rate data for 28–29 June 2026 is retrievable | Pull it — this is the kill gate |
| A2 | The single-prompt baseline will lose on messy inputs | Run it early |
| A3 | Models can be made to abstain reliably | Prompt experiment |
| A4 | Citations can be mechanically verified | Build the matcher |
| A5 | Generalist judges will follow the argument | Cold reads with strangers |
| A7 | Bounty Day 1 is 2 August | Ask on Discord |
| A8 | General framing beats niche framing | Test both on strangers |
| A9 | We can recruit 3+ relevant reviewers in a week | Message 20, expect 3 |
| A10 | Removing a node will visibly degrade output | Ablation study |
| A11 | "I don't know / nobody knows" is understood without explanation | Test on 3 non-technical people |
| A12 | The abstention rate will be low enough to be useful | Measure it |
| A13 | "Normative indeterminacy" is not already claimed elsewhere | Search |
| A14 | A CA would accept L1/L2/L3 tagging | Interview question |
| A15 | We can honestly tell "no rule exists" from "we failed to retrieve" | Partly fixed by D19; state as a limitation |
| A16 | An assessing officer would find our format legible | **Interview — most important question we have** |
| A17 | CAs do not already produce a standard disclosure note | Interview question |
| A18 | 270A(6) has been successfully invoked on a valuation dispute | Search tribunal decisions |
| A19 | A CA would pay, and enough to matter | Ask for a number, not a yes/no |

---

# PART G — WHAT IS STILL OPEN

**Most urgent, and nothing else depends on more than these three:**
1. Confirm the bounty calendar dates on Discord — Bounty 1 may close around 8 August
2. Send interview outreach to twenty people — this is the only thing with a lead time we cannot compress
3. Pull and cache the rate data for 28–29 June 2026 — the kill gate

**Also open:** create the iteration log · all three complete the recorded 30-second test · verify the ₹41,150 arithmetic · search whether normative indeterminacy is already claimed · draft Bounty 1 · search tribunal decisions on 270A(6) · rewrite the pitch value line around 270A(6) · add the two new interview questions.

**Fold-back work:** the problem statement needs a v3 pass to lead with the 270A(6) value proposition.

---

# PART H — THINGS TO REMEMBER AT THE END
*For the documentation, the pitch, the video and the bounties.*

| # | Remember | Use it in |
|---|---|---|
| R1 | *"An AI can say 'I don't know.' It cannot say 'nobody knows.'"* | Opening line of everything |
| R2 | ₹5,14,400 vs ₹4,73,250 — **₹41,150 apart on one invoice**, both defensible | Within 30 seconds of every pitch |
| R3 | Ours is a **lacuna**, not open texture. The rule doesn't say something vague — it says nothing | Q&A, documentation |
| R4 | Hallucination = a knowable thing got wrong. Ours = an answer to a question with none. Undetectable by checking | The core defence |
| R5 | Hart, *The Concept of Law*, 1961. Sixty-five years of jurisprudence behind us | Innovation |
| R6 | A 2026 paper names our exact problem as its own unsolved limitation | Novelty claim |
| R7 | Auditors issue a **disclaimer of opinion**. A whole profession is paid to say "we cannot form a view" | "Does saying it's unclear help?" |
| R8 | Hoare's billion-dollar mistake — absence must not masquerade as a value | Engineer judges |
| R9 | IFRS 13 Level 1/2/3 already solves "report a value with no observable price" | Schema, finance-literate judges |
| R10 | The CA needs **coverage**, not revelation. She cannot check all forty rows | Value proposition |
| R11 | Never open with "crypto." Open with the person | Every pitch |
| R12 | Report where the baseline beats us, prominently | Technical Execution, Bonus |
| R13 | Regulators could use aggregated lacuna reports to see where to legislate | Bounty 1 |
| R14 | Twelve domains carry the same root cause | Sustainability, Bounty 1 |
| R15 | **270A(6):** bona fide + disclosed basis + difference of opinion = no penalty. 200% vs 50% vs 0% | The value proposition |
| R16 | ₹37,035 vs ₹18,518 vs ₹12,345 on one invoice | Impact, quantified |
| R17 | *Reliance Petroproducts* (2010) 322 ITR 158 (SC) | Q&A depth |
| R18 | The **assessing officer** never pays us and decides everything. Build for his eye | UX, responsible impact |
| R19 | Rajesh does not need ambiguity revealed — he needs coverage | The CA persona |
| R20 | A range is also a menu. Fix: **record the election** | Responsible impact |
| R21 | **Fail toward abstention.** False confidence costs a statutory defence | Design principle |
| R22 | The person with the pain is not the person with the budget — say it out loud | Maturity signal |
| R23 | Every time we attacked our own idea, it got sharper. That method is now inside the product | The story judges remember |
| R24 | **Rule 11UA is now Rule 57** (Income-tax Rules, 2026, from 1 April 2026). We cited the old number for weeks and nobody caught it | The best story in the pitch |
| R25 | s.194S is now **s.393(1), Table Sl. No. 8(vi)**. The whole 194-series is gone | Citation accuracy |
| R26 | **"They disclose the input. They do not disclose the decision."** Koinly names its aggregator; it does not name the choice | The reworded competitor claim |
| R27 | Koinly converts to INR using **European Central Bank** rates — no standing in Indian tax law. Not bad faith, just a global default | The vivid competitor example |
| R28 | SBI does not quote USDC, so even Rule 115 does not cleanly apply | Strengthens the lacuna argument |
| R29 | **Consensus is not verification.** Every source agreed because they were reading each other | Q&A, documentation |
| R30 | Three failure types now, not two: hallucination, lacuna, and **staleness** | Broadens the argument |
| R31 | **From abstention to election.** Abstention withholds; election hands the user a priced, recorded choice | The novelty claim |
| R32 | **Gur-Arieh, SSRN, May 2026** — "the burden of judgment has to be discharged somewhere." We answer *where* | Innovation, Q&A |
| R33 | Abstention and self-critique are mature fields. **We claim the objective, not the mechanism** | Q&A survival |
| R34 | Intrinsic self-critique is documented as unreliable. Ours is externally grounded | Technical Execution |
| R35 | Everyone else uses critique to improve the answer before you see it. **We publish the attack** | Node 6 positioning |
| R36 | Citing prior art is a strength. A team that claims everything is new has not looked | Documentation, Innovation |
| R37 | **You earn the right to make a negative claim by declaring what you looked at.** Legal opinions and audits both do this | The manifest, Q&A |
| R38 | To prove a lacuna you must store the rule that **fails**, complete and untruncated | Corpus integrity |
| R39 | The current law is harder to obtain than the superseded law. Four months on, .gov pages still show 1962 text | Why staleness happens |
| R40 | **Show the manifest to the user.** "You don't have to trust us — here's the list and the dates" | UX, trust, Bounty 1 |
| R41 | **s.270A(6) is now s.439(8)(a) and (b).** s.270AA → s.440. Form 68 → Form 161 | Every citation |
| R42 | **439(8)(b) requires "accounts are correct and complete."** The exclusion is not automatic | Stated limitation |
| R43 | **FIN 48 / ASC 740-10-50 and ONESOURCE Uncertain Tax Positions already do this — for corporations, since ~2007** | Prior art, must acknowledge |
| R44 | *"Corporations got a framework in 2006. A freelancer in Pune has a CoinGecko screenshot."* | The value proposition |
| R45 | FIN 48: a **human** decides a position is uncertain. Ours: the **system finds it**, at transaction level | The differentiator |
| R46 | Every claim we have now has a professional ancestor. That is evidence the problem is real | Q&A, documentation |
| R47 | **Three failure classes: Loud, Checkable, Silent.** Everyone builds for Checkable. Nobody builds for Silent | The product's territory |
| R48 | **Silent Failure Rate** — the fraction a competent CA would not have caught. Better than accuracy | Headline metric |
| R49 | **FMEA scores Detection so that invisible = higher risk.** Engineering reached our conclusion 70 years ago | Borrowed ancestor #5 |
| R50 | *"Our architecture is designed against the most invisible failures, not the most common."* | Answers "why seven nodes?" |
| R51 | Class 3 failures are **structural, not accuracy-related** — so the comparison holds even against an excellent baseline | Evaluation robustness |
| R52 | Our own two stale citations go **in** the failure catalogue as naturally occurring evidence | Honesty, and it proves F3 |
| R53 | **Reasoning fine-tuning degrades abstention by 24%.** Scaling is of little use. AbstentionBench, NeurIPS 2025 | The obsolescence answer |
| R54 | Models give definitive answers **even when their reasoning chains express uncertainty** | The mechanism |
| R55 | *"We don't make the model more uncertain. We stop its uncertainty being thrown away."* | The best one-line technical claim we have |
| R56 | A good prompt **helps and does not fix it** — published, across 20 models | The N2 answer |
| R57 | ITAT: penalty cannot be levied on *"a difference in legal view or **computational methodology**"* | Our fact pattern, in a tribunal's words |
| R58 | Our limb is **s.439(8)(a)**, not (b). (b) is about the AO estimating | Citation accuracy |
| R59 | Two models agreeing is not correctness — both trained on the same internet | Cross-model limitation |
| R60 | **Generating and judging use opposite postures.** Judge while generating and you kill the strange ideas first | Method |
| R61 | **Second Opinion (#19)** — paste any AI answer, get told what it hid. No document parsing needed | Alternative path |
| R62 | **The Checklist (#23)** — the no-AI version. Found only by deleting the component we were most attached to | Alternative path |
| R63 | **The Lacuna List (#26)** — one public page, one day's work, possibly more useful than the product | Demo asset regardless |
| R64 | **#28 — we assumed an adversary for eight steps without checking.** The officer wants a legible basis too | Stakeholder blind spot |
| R65 | Our idea sits at six coordinates, none of which were ever examined until now | Why divergent thinking matters |
| R66 | **Of nine ways to guarantee failure, we are doing five. None is a thinking problem** | The mirror test |
| R67 | **We are extremely well prepared and have not started** | The honest state of play |
| R68 | ⚠️ **Custom may have filled the gap.** A de facto standard makes a de jure gap irrelevant. Only practitioners can answer | The interview question that could end the project |
| R69 | Insurance adoption: people under-buy protection against low-probability delayed harms. **That is why the buyer is the CA — she sees 300 clients** | Buyer rationale |
| R70 | The 8.5% spike happened *because* of an enforcement raid. Use it as illustration, never as the argument | Framing discipline |
| R71 | **Election is one tap with a default.** The record we need is "you were shown both," not "you agonised" | Design, from an objection |
| R72 | Five alternatives failed by contradicting commitments we'd already made — **evidence those commitments are load-bearing** | Why the idea survived |
| R73 | **The output looks like a document, not a dashboard** — because the second reader is an assessing officer | Design rationale, Q&A |
| R74 | **The divergence is drawn as an engineering dimension line.** Not a chart — a measurement | The signature element |
| R75 | Accessibility is done, not promised. Say it out loud in the video — most teams score zero there | ~20 points |
| R76 | *"Either way, this record states that both figures were shown to you."* | The election, C54 |
| R77 | Bounty 1's biggest sub-criterion is **grounded reality (4 of 10)** — the failure section is where the marks are | Don't delete it to sound confident |
| R78 | **Open specific · widen once · land specific.** One widening only — more is where overclaim lives | The pitch structure |
| R79 | **"Five model calls and two deterministic checks."** Never "seven nodes" | The Q&A answer to "why so many?" |
| R80 | Some parts of the system **cannot hallucinate, because they are not models.** Show that split in the diagram | Technical Execution |
| R81 | *"DIVERGENCE — a record of what the law didn't decide."* | The descriptor line |
| R82 | A scoring matrix can be nudged to say what you wanted. **Always run cross-checks that use no scores** | Method |
| R83 | **The winning option changed nothing about what we build — only the order we say things in** | The cheapest win available |
| R84 | **Deferrals and boundaries are different statements.** Three tiers, not two lists | Scope contract |
| R85 | **"Does this help prove the law had no answer, or help give one?"** The test that settles future arguments | Decision rule |
| R86 | A scope contract's underrated job is **making refusal cheap** — the document says no so a person doesn't have to | Team |
| R87 | **Out of scope for CLAIMS** — seven sentences we won't say, each one we already had to correct | Q&A protection |
| R88 | **A default is a recommendation.** We removed the pre-selection; the record is valid without an election | C65 |
| R89 | **Stablecoins only is a choice, not a limitation** — the hardest case for our own argument | Maturity signal |
| R90 | Writing down what you refuse to do makes you check whether you are already doing it | Method |
| R91 | **The weekend case needs no historical data and is reproducible forever** — a cleaner proof than a one-off spike | Kill-gate fallback |
| R92 | **B1 — measure corpus completeness.** Everyone asserts coverage; nobody tests it | Two hours, unexpected |
| R93 | Deterministic check vs model check: **one is a hope, the other is a guarantee** | Technical Execution |
| R94 | **Test data before code** — build first and you'll shape the ground truth to fit the pipeline | Build order |
| R95 | Cache every model response by input hash. 600 calls, never re-run one | Cost control |
| R96 | **₹44,400 · 9.45% · one $5,000 invoice.** SBI TT buy ₹94.00 (25 Jun) vs Indian market ₹102.88 | The headline, corrected |
| R97 | **SBI published 25 Jun, skipped 26th, next was 29th — a four-day hole.** Verified from archived PDFs | The weekend case, evidenced |
| R98 | *"We switched to the rate the law actually mandates, and the disagreement grew."* | The correction, as a strength |
| R99 | **The gap has a gap** — even under Rule 115 you must choose 25 Jun or 29 Jun. ₹250. Nothing prescribes it | Third undetermined choice |
| R100 | **Both numbering systems are live.** FY 2025-26 → 1961 Act; FY 2026-27 → 2025 Act. Cite with the tax year attached | We were unspecific, not stale |
| R101 | A guide published this week still leads with "115BBH of the 1961 Act" — **and is correct, for this year's return** | Evidence the ambiguity is real |
| R102 | **Every check has found something and none has weakened the project.** The more carefully we look, the more gaps we find | Q&A |
| R103 | **No guide anywhere names a rate source.** They all cover 30%, TDS, thresholds — and skip the one practical question | Negative evidence for OBJ-1 |
| R104 | *"A baseline you adjusted after seeing its score is not a baseline — it's a target you moved."* | Why it's frozen |
| R105 | The baseline **explicitly asks** for the method, the missing documents, and anything unclear. **If it still fails, the failure is structural** | The fairness argument |
| R106 | `minItems: 2` on valuation methods — **a single figure is a schema violation, not an output** | The thesis, in code |
| R107 | `limits[]` has `minItems: 1` — **if it's ever empty, the record is wrong** | Enforced humility |
| R108 | **A wrong answer that looks wrong is harmless. This looks right.** | The danger, in one line |
| R109 | Asked directly for what was unclear, it said *"regulation is evolving"* and *"consult a professional."* **A hedge, not a disclosure** | The P3 failure |
| R110 | **Score against what the output does not say, not how it reads** | Scoring discipline |
| R111 | Fresh session every run. **Contamination is the easiest way to ruin this and it is invisible once it happens** | Protocol |
| R112 | **₹43,633 · 9.27% · one invoice.** CoinDCX close 102.83 vs SBI TTBR 94.00. **Retrieved, not reported** | The headline, measured |
| R113 | **29 June intraday range: 10.52%.** Low 93.50 — the market briefly touched the official rate | The gap is not constant |
| R114 | *"The disagreement is a function of when you look."* | Stronger than "two methods differ" |
| R115 | **A daily candle is not a price. It is a range with four defensible readings** — ₹5,500 | Fourth choice |
| R116 | **03:14 IST Sunday = 21:44 UTC Saturday.** Chain records UTC, tax operates in IST. Different day, different rate | Fifth choice |
| R117 | **Rule 11UA is scoped to section 56.** Our receipt is section 28 business income. **For business income in kind, no rule prescribes FMV at all** | The sharpest version of the claim |
| R118 | Rule 11UAB borrows 11UA's method by reference for inventory. **Nobody extended it to VDAs** | The drafter extends where he means to |
| R119 | ⭐⭐ **The gap is a closed chain, not an absence.** s.56 includes VDAs → says FMV is "the method prescribed" → no method prescribed | **The best finding in the project** |
| R120 | *"The Act asks a question of itself and does not answer."* | The one-line version |
| R121 | Rule 11UA statutory text: **zero** occurrences of virtual digital / crypto / token / digital asset. **Machine-checked** | Demonstrable, not asserted |
| R122 | A law firm, **June 2026**: *"the methods of valuation of VDA are yet to be prescribed"* | Best external validation we have |
| R123 | **The gap is doubled.** Gift recipients have a statute pointing at an empty rule. Our freelancer has nothing pointing anywhere | s.28 vs s.56 |
| R124 | ⭐⭐ **s.2(47A) defines a VDA as "not being Indian currency or foreign currency" and expressly adopts FEMA's definitions.** The exclusion is statutory, not inferred | The FEMA claim, upgraded |
| R125 | *"The only inference left is the consequence, not the characterisation."* | New FEMA language |
| R126 | **The section that taxes crypto at 30% does not contain the word "value".** Machine-checked: 0 occurrences | s.115BBH |
| R127 | **115BBH taxes "transfer". She receives. So it does not apply at receipt** — the two-stage model is on the face of the statute | Not commentary |
| R128 | **s.2(22B) defines FMV only "in relation to a capital asset", and points at rules that don't cover VDAs.** Same closed loop, second direction | The gap, doubly proved |
| R129 | FEMA (h) "currency" is a **closed list plus whatever the RBI notifies. The RBI has notified nothing** | The chain, from the text |
| R130 | s.2(47A)(d) inserted **w.e.f. 1 April 2026** — Feb 2026 and June 2026 payments are governed by different definitions | Third date-dependent example |
| R131 | ⛔ **Rule 115 converts FOREIGN CURRENCY. A VDA is defined as not being foreign currency. It does not apply** | We had this wrong |
| R132 | **Four doors, all locked, each for a different reason** — Rule 11UA, s.2(22B), s.115BBH, Rule 115. That is a pattern, not an oversight | The strongest framing yet |
| R133 | Even if Rule 115 applied, business income uses **the last day of the previous year** — 31 Mar 2027 for a 29 Jun 2026 receipt | Absurdity, from the text |
| R134 | **"The export proceeds have not been realised. Not late — unrealised. And the clock is running"** | The FEMA claim, precise |
| R135 | **194S fails only because her client is abroad** — not because she receives rather than transfers. The Department treats the professional as the buyer | Corrects Step 5 |
| R136 | 🔴 **Section 195 may apply.** Probably not — but "probably not" is what we exist to surface, not resolve | New open question |
| R137 | **CBDT Circular 13 names USDC by name** as a "Primary VDA" | Official document, our exact asset |
| R138 | ⭐⭐ **FEMA s.3(c) is an EXPRESS PROHIBITION** on receiving any payment from abroad otherwise than through an authorised person | We read the wrong sections for 15 steps |
| R139 | **s.3(c) says "any payment", not "foreign exchange."** s.3(a) and s.8 use the narrow term. The drafter chose | Our own best argument doesn't defeat it |
| R140 | The only FEMA question left: **is a stablecoin transfer a "payment"?** One narrow question, not a chain | Much stronger position |
| R141 | s.9 exempts from ss.4 and 8 — **not from s.3** | Pre-empts a counter |
| R142 | **s.393(1) is headed FOR PAYMENTS TO RESIDENT.** Her client is abroad, so it never engages | Settled from statute |
| R143 | 🔴 **s.393(2) Sl.17 catches "any other sum chargeable" paid to a non-resident.** Flag, do not resolve | New open question |
| R144 | ⛔ **CGST ss.73/74 apply only up to FY 2023-24. Ours is s.74A** | Fourth stale citation |
| R145 | *"We read the section and the section told us it had been superseded."* | The staleness story, strongest form |
| R146 | ⭐⭐⭐ **"fair market value … MEANS the value determined in accordance with the method as may be prescribed."** Read the verb | The sentence the thesis needed |
| R147 | **No method prescribed = no fair market value in law. Not uncertain — none** | Strongest form of the claim |
| R148 | s.2(22B) has a fallback (open market price). **s.56 has none** — straight to the prescribed method and stop | The difference matters |
| R149 | **FBIL uses a RANDOMLY SELECTED 15 minutes** of the 11:30–12:30 hour. Up to five re-draws. Then polled quotes | Sixth undetermined element |
| R150 | *"Even the official rate is the product of a random choice"* | Answer to "why not use the official rate?" |
| R151 | **CGST s.74A: ₹1,19,205 non-fraud vs ₹2,01,752 fraud** on one invoice. ₹82,547 turns on "suppression" | GST exposure, quantified |
| R152 | **Disclosure is the hinge in BOTH regimes** — s.439(8)(a) and CGST s.74A Explanation 2, arrived at independently | Structural point |
| R153 | Fifth stale text caught — s.56 version predates the Finance Act 2022 VDA amendment | Resolved: current text now held |
| R154 | ⭐⭐⭐ **In one Explanation, limb (b) was extended to include VDAs and limb (a) — fair market value — was not** | The omission, inside one amended sentence |
| R155 | *"Parliament brought VDAs into section 56 by name. Section 56 says their value is whatever the prescribed method says. Four years later, no method has been prescribed."* | The claim, final form |
| R156 | **All five links are primary text in the corpus.** A judge can verify the chain from five files without leaving the folder | Nothing is asserted |
| R157 | **A citation without a tax year cannot be validated at all.** Both numbering systems are live | The unusual check |
| R158 | The matcher **catches both of our own historical errors automatically** — and accepts Rule 11UA when the year makes it right | The demo |
| R159 | v1 12/15 → v2 14/15 → v3 15/15. **The last bug was in the data, not the code, and only the test found it** | Documented iteration |
| R160 | **A citation field contains a citation, not a note about one** | Data rule |
| R161 | *"Existence is not relevance."* The matcher checks the citation exists, not that it supports the claim | Stated limitation |
| R162 | **A rule you can't enforce isn't a rule** — same lesson in the matcher and in abstention | Design principle |
| R163 | ⭐⭐⭐ **India prescribed a crypto valuation waterfall — for EXCHANGES, not taxpayers** | Rules 2026, gazette |
| R164 | ⭐⭐⭐ **The prescribed method ends: *"a reasonable estimate may be applied as a measure of last resort."*** The State conceded indeterminacy | The strongest line in the project |
| R165 | ⭐⭐⭐ ***"the method shall be indicated in Form No. 167"*** — **method disclosure is already Indian law. For exchanges** | Our product, already mandated |
| R166 | **Rule 57 confirmed from the GAZETTE.** Notified 20 March 2026 — a NEW rule that still omits VDAs | Not an un-updated old rule |
| R167 | **s.56(2)(x) → SECTION 92** of the 2025 Act. From Rule 57 column B. U11 closed | Citation accuracy |
| R168 | The only RCASP step she could use is **third-party aggregator websites — the CoinGecko screenshot everyone already takes** | The counter-argument answer |
