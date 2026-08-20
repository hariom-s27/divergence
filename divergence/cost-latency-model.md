# COST, LATENCY AND THROUGHPUT MODEL
### DIVERGENCE · Step 18 of 40 · Reverie Hacks 2026 · ML Prompt Engineering
**Built 9 August 2026 · Prices from Anthropic's published rates, retrieved 9 August 2026**
**Status: model built before the pipeline exists. Predictions registered now, to be scored against measurement at Step 26.**

---

## THE ONE NUMBER FOR Q&A

> **₹29.57 per record — about $0.34 — on the mixed-model configuration with prompt caching on.**
> **Roughly three times what a single prompt costs on the same corpus. Not seven times, because six of the seven calls never see the whole corpus.**

If asked for a range: **₹6.59 on Haiku 4.5, ₹42.84 on Opus 5, ₹29.57 on the mixed configuration we would actually deploy.**

---

## WHY THIS MODEL EXISTS AND WHAT IT HONESTLY IS

Step 18 as written says *"time one full pipeline pass."* The pipeline does not exist yet — it is built at Steps 26–31. So this is not a measurement, and calling it one would be the exact failure the project is about: an answer that looks settled and isn't.

What this is instead: **a parametric model, anchored on real measurements where measurement was possible today, with every estimated figure marked as estimated.** At Step 26 the model gets re-run against the built pipeline and **the error between predicted and actual gets published.**

That delta is worth more than a confident number. It is the same discipline as the nine predictions registered before the baseline run.

**Measured today:**

| Quantity | Value | Source |
|---|---|---|
| Rule 56 + Rule 57 (the FMV rule), full text | 8,512 chars → 2,128 tok | Gazette text, project knowledge |
| RCASP valuation waterfall | 2,164 chars → 541 tok | Gazette text, project knowledge |
| Income-tax Rules 2026, complete instrument | 2,253,483 chars → **563,371 tok** | Gazette text, project knowledge |

**Estimated until `measure_corpus.py` is run against the real `corpus/`:** the other 14 corpus files, all system prompt lengths, all inter-node payload sizes, all output lengths, and every latency figure.

---

## FINDING 1 — THE TOKENIZER CHANGE, WHICH MOST COST MODELS WILL MISS

Anthropic's pricing page states that Claude 4.7 and later models use a newer tokenizer producing **approximately 30% more tokens for the same text**, and that Sonnet 4.6 and earlier use the previous one.

Every current model we would use — Opus 5, Sonnet 5, Fable 5 — is on the new tokenizer. **Haiku 4.5 is not.**

A cost model built on the familiar "4 characters per token" rule **understates spend on current models by about a third.** This model applies a 1.30× multiplier to the four models that need it and not to Haiku.

This is a good Q&A answer in itself: it shows the number came from the current price sheet, not from memory.

---

## FINDING 2 — SEVEN API REQUESTS, FIVE STAGES. SAY BOTH.

The locked architecture is *"five model calls and two deterministic checks."* But stage 4 — the regime resolver — **fans out to three calls**, one per regime, each with a different scoped corpus.

So a record costs **seven API requests**, not five.

The pitch language stays. But if a judge asks *"how many model calls per record?"* the answer must be:

> **"Five stages, seven calls. The regime resolver runs three times — income tax, GST and FEMA — because each one gets a different slice of the corpus and must not be able to cite outside it."**

Answering "five" and then quoting a cost figure built on seven is the kind of small inconsistency that costs more credibility than it should.

**⚠️ Open question this surfaced:** the Step 19 roadmap diagram has a **seventh node, `[7] DISCLOSURE COMPOSER`**, which does not appear in the locked five-call architecture. If it is a sixth model call, every figure here rises by roughly 15%. If it was folded into node 5 or made deterministic, the model is right as it stands. **This needs a decision before Step 19, not after.**

---

## FINDING 3 — CORPUS SCOPING IS THE WHOLE COST DESIGN

Injecting all 16 corpus files into all 7 calls would cost **67,347 tokens per record**. Giving each node only the provisions it is permitted to cite costs **21,913**.

**67% saved — and it was never a cost decision.** Scoping exists so a node cannot cite outside its regime. The saving is a side effect of a correctness rule.

And the corpus itself, against its own source:

| | Tokens |
|---|---|
| Income-tax Rules 2026, whole instrument | 563,371 |
| What we extracted from it (Rules 56, 57, RCASP waterfall) | 2,671 |
| **Reduction** | **99.5%** |

> **Step 9 looked like a citation-verification decision. It was also a 99.5% cost reduction. Say this when asked why there is no vector database: at this scale, retrieval infrastructure would cost more than the tokens it saves.**

---

## FINDING 4 — OUTPUT TOKENS DOMINATE, NOT LAW

Sensitivity, one parameter at a time, mixed configuration with caching:

| Change | Cost | Δ |
|---|---|---|
| Output 2× longer | $0.5485 | **+63.2%** |
| Input documents 2× | $0.4445 | +32.3% |
| Corpus 2× larger | $0.3487 | +3.8% |
| System prompts 2× | $0.3385 | +0.7% |
| Corpus 0.5× | $0.3297 | −1.9% |

**Doubling the entire corpus costs 3.8%. Doubling what the system says costs 63%.**

This is uncomfortable and worth stating out loud: DIVERGENCE is an explanation product. Its cost driver is **how much it says, not how much law it reads.** Every additional sentence of disclosure has a price, and the honest consequence is that *verbosity is the thing to control, not scope.*

It also means prompt caching helps less than people expect — **about 25%, not 90%** — because outputs are never cacheable and outputs are roughly half the bill.

---

## FINDING 5 — THIS IS A BATCH PRODUCT. THE DEMO PLAN HAS TO CHANGE.

Even with the three regime resolvers running in parallel, a single record generates roughly **12,600 output tokens**. On Opus 5 that is **~3.5 minutes**. On Haiku 4.5, ~1 minute.

| Model | Parallel | Fully serial | Saved by parallelism | Records/hr at 8 concurrent |
|---|---|---|---|---|
| Opus 5 | 214s | 293s | 79s | 134 |
| Sonnet 5 | 132s | 181s | 49s | 218 |
| Haiku 4.5 | 64s | 87s | 24s | 452 |

*(Latency figures are planning assumptions, not measurements. They assume 1.8s to first token and 45/75/130 output tokens per second. Replace them at Step 26.)*

The critical path is **five model calls deep, not seven wide** — the three regime resolvers read the same upstream state and never read each other. The two deterministic checks add about **80ms** and cost nothing.

> **⚠️ Do not plan a live cold run on stage.** A judge watching a spinner for three minutes is a worse outcome than a pre-computed result honestly labelled as pre-computed. Step 23's interface needs **staged progress that shows each node completing**, which is also a better demonstration of the architecture than a final screen would be.

---

## THE TABLES

### Token budget per record (legacy tokens; multiply by 1.30 for Opus 5 / Sonnet 5)

| Node | Corpus | System | Payload | IN | OUT | Cacheable |
|---|---|---|---|---|---|---|
| 1 Intake + extraction | 0 | 800 | 3,000 | 3,800 | 1,200 | 800 |
| 2 Gap detector | 0 | 700 | 1,200 | 1,900 | 600 | 700 |
| 3 Dual valuation | 3,671 | 900 | 1,800 | 6,371 | 1,500 | 4,571 |
| 4a Regime · Income tax | 6,221 | 900 | 3,300 | 10,421 | 1,800 | 7,121 |
| 4b Regime · GST | 1,600 | 900 | 3,300 | 5,800 | 1,400 | 2,500 |
| 4c Regime · FEMA | 800 | 900 | 3,300 | 5,000 | 1,200 | 1,700 |
| 5 Adversarial checker | 9,621 | 1,000 | 7,700 | 18,321 | 2,000 | 10,621 |
| **PIPELINE TOTAL** | **21,913** | **6,100** | **23,600** | **51,613** | **9,700** | **28,013** |
| *Baseline, same corpus* | *9,621* | *1,000* | *3,000* | *13,621* | *2,500* | *10,621* |

54% of pipeline input is cacheable — corpus and system prompts are byte-identical on every record.

**The baseline gets the same corpus.** Giving it less would make it a straw man, and the whole comparison would be worthless. This is the Step 16 fairness rule applied to cost.

### Cost per record

| Model | Pipeline | + caching | Baseline | Cached pipeline ÷ baseline | ₹/record |
|---|---|---|---|---|---|
| Opus 5 | $0.6507 | $0.4869 | $0.1698 | 2.9× | ₹42.84 |
| Sonnet 5 (intro rate) | $0.2603 | $0.1947 | $0.0679 | 2.9× | ₹17.14 |
| Sonnet 5 (from 1 Sep) | $0.3904 | $0.2921 | $0.1019 | 2.9× | ₹25.71 |
| Haiku 4.5 | $0.1001 | $0.0749 | $0.0261 | 2.9× | ₹6.59 |

**Sonnet 5's $2/$10 introductory rate expires 31 August 2026 and reverts to $3/$15.** Submission is 17 August, so the hackathon runs on the cheap rate — but **quote the September rate as the steady-state number.** A cost figure that silently depends on a discount expiring in three weeks is the same species of problem as an undisclosed valuation method.

### Mixed-model configuration — the one to deploy

| Node | Model | Cost | Cached |
|---|---|---|---|
| 1 Intake + extraction | Haiku 4.5 | $0.0098 | $0.0091 |
| 2 Gap detector | Haiku 4.5 | $0.0049 | $0.0043 |
| 3 Dual valuation | Sonnet 5 | $0.0541 | $0.0381 |
| 4a Regime · Income tax | Opus 5 | $0.1262 | $0.0846 |
| 4b Regime · GST | Sonnet 5 | $0.0499 | $0.0411 |
| 4c Regime · FEMA | Sonnet 5 | $0.0369 | $0.0369 |
| 5 Adversarial checker | Opus 5 | $0.1841 | $0.1220 |
| **TOTAL** | | **$0.4719** | **$0.3360 · ₹29.57** |

**31% cheaper than all-Opus, and the reasoning capacity is spent where it is needed** — the income-tax resolver, which carries the hardest chain, and the adversarial checker, whose entire job is to be smarter than the nodes it attacks.

Extraction and gap detection are structured, mechanical, schema-constrained tasks. They do not need a flagship model. **Saying this on stage demonstrates that the architecture was reasoned about rather than assembled.**

### Scale

| Records | Who that is | Cost | ₹ |
|---|---|---|---|
| 1 | one invoice | $0.34 | ₹30 |
| 40 | one CA client, one year | $13.44 | ₹1,183 |
| 500 | a small practice | $168 | ₹14,785 |
| 10,000 | a mid-size firm | $3,360 | ₹2,95,691 |
| 1,000,000 | scale ambition | $336,013 | ₹2.96 crore |

Batch API halves every row. Cost is **linear** — no training, no index, no vector store, no embedding refresh. The corpus is sixteen files that change when the law changes.

---

## THE PART THAT AFFECTS YOU THIS WEEK — THE MEASUREMENT BUDGET

Step 25 builds 30 test documents. Step 26 runs 30 cases × 2 systems × 2 models.

- Pipeline calls: 30 × 7 × 2 = **420**
- Baseline calls: 30 × 1 × 2 = **60**
- **480 API requests for the headline result**

| Line | Cost |
|---|---|
| Headline run, Opus 5 + Sonnet 5, cached | $27.58 |
| Ablation study (D5), 120 extra pipeline runs, Sonnet | $23.37 |
| Development burn at 4× the final run | $110.32 |
| **Whole-project measurement budget** | **~$161 (≈₹14,200)** |

**That is not a trivial number for a school team, and it is almost entirely development burn, not the final run.**

Three levers, in order of preference:

1. **Check the sponsor credit allowance before Step 25**, not after. This is the single cheapest thing to find out and it is currently unknown.
2. **Run the headline on Sonnet 5 + Haiku 4.5 instead of Opus 5 + Sonnet 5.** Cost drops to about $11. The comparison is still two models of different capability, which is what the rubric asks for. Opus can be reserved for a small illustrative subset.
3. **Use the Batch API for the final run** — 50% off, stacks with caching. The run is not interactive; there is no reason to pay interactive prices for it. Development iteration stays on the standard API.

**Recommendation: develop on Haiku, measure on Sonnet + one other, batch the final run, and keep Opus for the demo record only.**

---

## LIMITATIONS — STATE THESE BEFORE A JUDGE FINDS THEM

1. **No measurement.** Nothing here was timed. Every figure is arithmetic over estimated token counts and published prices.
2. **Token counts are character-ratio estimates,** not tokenizer output. Anthropic's `count_tokens` endpoint gives exact counts; run it once the key is live. Expect 5–15% movement.
3. **Fourteen of sixteen corpus files were not measured** — the corpus did not make it into project knowledge for this session. `measure_corpus.py` fixes this in one command.
4. **Latency assumptions are unsourced.** Time-to-first-token and output throughput were assumed, not looked up or measured. The *shape* of the latency finding (five deep not seven wide; minutes not seconds) is robust to the assumptions being wrong by a factor of two. The absolute numbers are not.
5. **Retry and failure cost is not modelled.** Schema validation failures force re-calls. A 10% retry rate on the two most expensive nodes adds roughly 3%.
6. **The disclosure composer question is unresolved** (Finding 2). Until it is, every figure carries a possible +15%.
7. **Prices change.** Sonnet 5's rate changes on 1 September 2026. Re-check the pricing page before submission and put the retrieval date on the slide.

---

## WHAT GOES IN THE SUBMISSION

Sustainability & Scalability asks *"what does it cost to run?"* The answer is three sentences:

> **"₹29.57 per record on the configuration we'd deploy — about three times a single prompt, not seven, because six of the seven calls only see the provisions they're allowed to cite. Cost is linear with volume; there's no training and no index. The dominant term is output tokens, so what we control is how much the system says, not how much law it reads."**

Then, if there is time: the tokenizer point, and the fact that the model was built before the pipeline and scored against measurement afterwards.

---

## FILES

| File | What |
|---|---|
| `cost_model.py` | The calculator. Standard library, no network. `--sensitivity` for the parameter sweep. |
| `measure_corpus.py` | Run against the real `corpus/` to replace estimates with measurements. Writes `corpus_profile.json`. |
| `cost-latency-model.md` | This document. |

```
python measure_corpus.py ../corpus --json corpus_profile.json
python cost_model.py --profile corpus_profile.json --sensitivity
```

---

## GATE D STATUS AFTER THIS STEP

- [x] Headline case confirmed — data cached, reproduced on two machines
- [x] Baseline written and frozen
- [x] Abstention approach known — protocol written, five variants, prediction registered
- [x] Citation matcher designed *and built*, 15/15
- [x] **Cost model exists**

**Gate D passes.** Phase E — design — opens at Step 19.
