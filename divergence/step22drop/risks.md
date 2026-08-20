# RISK, EDGE CASE AND FAILURE REGISTER
### Step 24 · written 19 August 2026
### Every row has a named handling. A row with no handling is not a risk register entry, it is a worry.

---

## EDGE CASES — inputs the system must not choke on

| Case | Handling | Status |
|---|---|---|
| **Weekend / holiday settlement — no official rate exists** | `no_rate_published: true`. **This is a feature, not an error path.** Both candidate dates go into the lattice and neither is chosen | ✅ built — `node3_valuation.py` |
| **Counterparty is a Discord handle only** | `missing[]` with `blocks: ["gst","fema"]`. The gap enforcer forces those conclusions to `insufficient_evidence` | ✅ designed · ⚠️ enforcer not built |
| **Amount below the ₹50,000 TDS threshold** | Different path — no deduction question. Valuation still undetermined | ✅ case C4 |
| **Non-crypto cross-border receipt** | Same pipeline, unchanged. **This is the scalability proof** | ✅ case C2 |
| **Fiat receipt settling on a Sunday** | The date choice is open with no crypto involved at all. **The fallback demo** | ✅ case C5 |
| **Multiple invoices against one payment** | **Out of scope, stated out loud** | ✅ `scope.md` |
| **A daily candle with a suspicious wick** | 29 Jun shows `low 93.50` vs `open 102.84` — 10.52% intraday, fully recovered. **Cited as excluded with a reason, or not cited** | 🔴 **unresolved — see below** |

---

## FAILURE MODES — things that break at runtime

| Failure | Handling | Status |
|---|---|---|
| **Rate API down mid-demo** | Everything is cached. **The demo is recorded, never run live** (D33) | ✅ `cache/` populated |
| **Invalid JSON from a model call** | Retry once → **hard fail with a logged error.** Never a silent wrong answer | ⚠️ `run_pipeline.py` not built |
| **Fabricated citation** | Matcher returns `accept: False` → conclusion **dropped**, not flagged | ✅ 15/15 |
| **Stale citation** | Same path. Catches five of our own historical errors | ✅ |
| **A conclusion depends on a missing document** | `certainty` **forced** to `insufficient_evidence` in code | ⚠️ enforcer not built |
| **Model abstains on everything** | Metric 5 measures it. **Reported honestly whatever it says** | ✅ designed |
| **Two corpus files claim one provision** | `gate0_check.py` fails the build. Was silently shadowing three provisions until 19 Aug | ✅ **fixed and now detected** |
| **A corpus file that can never be cited** | Same check. Two files were in this state — any conclusion resting on the SBI rate was being dropped by our own matcher | ✅ **fixed and now detected** |
| **Windows console crash on non-ASCII** | `sys.stdout.reconfigure(encoding="utf-8")`. **It was crashing on every Windows run and we had only tested on one machine** | ✅ fixed in both scripts |

---

## PROJECT RISKS

| Risk | Handling | Status |
|---|---|---|
| **Judges find it niche** | Specific → widen once → land specific (C58). The widening is now Rule 56 beside Rule 57: *"this rulebook tells you the exact day to value the payment, and four lines later declines to tell you how."* **Checkable in twenty seconds, no crypto required** | ✅ |
| **Straw-man suspicion on the baseline** | Published in full, frozen 6 Aug before the pipeline existed, **plus a token-matched third arm** so the result is not just "more compute helps" | ⚠️ arm B not run |
| **"Rule 57 row 7 covers it"** | ⭐ **The single strongest attack on the project.** Row 7 *is* a residual catch-all reaching "any other property" at open-market price. Its column B reads `Section 26(2)(j)` alone — s.92 cannot reach it. Provenance (11UAB) says the scoping is deliberate. **Raise it yourself before a judge does** | ✅ gazette-verified |
| **A teammate drops out** | P3's presentation work absorbs into P1. Cut to 3 cases, keep D1 + 2 clean | ✅ |
| **Bounty windows did not reopen** | Accept the 20 points are gone. **Do not spend a day on it** | ⏸ awaiting Discord |
| **The adversarial node is theatre** | 🔴 **We have no evidence it works.** The Step 29b ablation decides. If it catches 0 of 4 planted defects we cut the novelty claim resting on it and say so | 🔴 **live, unresolved** |
| **Arm B closes the gap** | Then it is a chain-of-thought result, not an architecture result, **and we say that in the video.** Written into `evaluation-design.md` §7 before any data exists | ✅ pre-committed |
| **A provision changes mid-build** | Corpus frozen at a stated datetime. `corpus_frozen_at` in every output. Changes go in the manifest changelog, never a silent update | ✅ |
| **Custom has already filled the gap** | 🔴 If every CA says *"we use the exchange statement, the department accepts it"*, a de facto standard makes the de jure gap practically irrelevant. **The project pivots to "here is the convention, here is that nothing requires it."** Only practitioners can answer this | 🔴 **zero interviews sent** |

---

## THE THREE UNRESOLVED ROWS

Everything above has a handling. These three do not, and they are ranked.

### 🔴 1 — Zero interviews
Fourteen days outstanding. It is the only item in the plan whose clock we do not
control, it gates Bounty 2 entirely, and it carries the one objection that could
change the project rather than the pitch.

**Mitigation if nobody replies:** report it honestly. *"We contacted N people
during peak filing season, M responded, here is what we could not verify."* A
judge who has done real research respects that far more than a suspiciously
smooth account. **What we do not do is fabricate one line of it.**

### 🔴 2 — The adversarial checker has never run
Every success credited to it — Rule 57 row 7, five stale citations, the FERA
1973 finding — was found by a **human reading adversarially**.

**Mitigation:** the ablation is designed, the four planted defects are written,
and the outcome is pre-committed in both directions. If it catches nothing, that
is reported as a finding and the claim is cut. **Deciding this before the run is
what stops it being decided by whatever the run happens to show.**

### 🟡 3 — The 29 June candle
`low 93.50` against `open 102.84` — a 10.52% intraday collapse that fully
recovered. Almost certainly a thin-book wick.

**It is not in the lattice** (the lattice uses the 28 June candle), so nothing
currently depends on it. **But it must not be cited anywhere until it is
verified or excluded with a stated reason.** A bad print presented as a finding
is the one thing in this project a hostile judge could actually catch.

---

## WHAT WE DELIBERATELY DO NOT HANDLE

Not gaps. Boundaries. From `scope.md`, Part 6 — still out with unlimited time.

- Telling anyone what tax to pay
- Claiming any flow is compliant
- Predicting how a dispute would be decided
- **Inventing a method where none is prescribed** — filling the gap is the exact
  failure this exists to prevent
- Detecting evasion
- Retaining the user's documents

**Item 4 is the one to say in the pitch.** A product that refuses to do the most
obvious thing a user wants — just tell me the number — is unusual, and the reason
it refuses is the thesis.
