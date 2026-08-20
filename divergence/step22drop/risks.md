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
| **`citation_matcher.py` resolves a bare "Section 2(111)" (no Act name) against the wrong file, FEMA-2n.md** | Logged, unfixed (found live, D46). Ground truth uses the fully-qualified form everywhere to avoid it — the matcher's own gap is not what any scored record depends on | ⚠️ **unfixed, worked around** |
| **Node 5 attacks nearly every conclusion instead of discriminating** | `checked_and_survived` non-empty exactly once across seven runs. Reported in D50 and results.md's losses section. Node 5's output used for disclosure only — never to auto-revise a certainty | 🔴 **known, disclosed** |
| **Node 5 proposes an upward revision labelled as a downgrade** | `node5_adversarial.py`'s `_reject_upward_revisions` rejects it deterministically — dropped, recorded in `limits[]`. Tested on two independent real examples (D54) | ✅ fixed and tested |
| **Node 5 emits `downgraded_to: ""` instead of omitting it; our own rejection guard was nulling instead of deleting the field** | Both normalized/fixed in code — `schema.json`'s `downgraded_to` has no null member, so either bug alone produced schema-invalid output (D55) | ✅ fixed |
| **Same scope-reach failure recurs a fourth and fifth time (s.393(1), two different readings)** | Fourth fixed with an S.393(1) SCOPE GATE (D55). Fifth (a foreign-payer exemption not in the text) caught by node 5 on the record meant to freeze — disclosed in `results.md`, not fixed, per the hard-stop | 🟡 **known, disclosed, frozen anyway** |

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
| **Custom has already filled the gap** | 🔴 If every CA says *"we use the exchange statement, the department accepts it"*, a de facto standard makes the de jure gap practically irrelevant. **The project pivots to "here is the convention, here is that nothing requires it."** Only practitioners can answer this | ✅ interviews substituted with sourced evidence — `prior-art/OBJ-1.md` |
| **A judge diffs the freeze commit and finds nine-plus schema amendments** | Raise it ourselves first. All nine-plus in D46/D51, output contract only, `cases/*/ground_truth.json` untouched — the freeze commit's load-bearing content never changed | ✅ pre-disclosed |
| **The same scope-reach failure recurs on a fourth rule** | One generalized SCOPE GATE in prompt 03 (D54), not a fourth special-cased patch — named in the documentation as a pattern, not treated as three unrelated bugs | ✅ generalized |
| **C3/C4's valuation blocks belong to a different case** | Disclosed D47/D51/results.md. C1, C2, C5 all now have their own real valuations (D51 addendum). C3/C4 still carry D1's borrowed 12-method lattice — **do not show C3 or C4's generated page as if the valuation section were case-specific until fixed** | 🟡 **2 of 6 cases open** |

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

---

**UPDATE, 21 August — this section is kept as written, not rewritten, per this file's own "no silent update" rule (PROJECT RISKS, above). Current status:**

Row 1 (zero interviews) is no longer zero — sixteen days out, no response arrived, and interviews were substituted with sourced public evidence instead (`prior-art/OBJ-1.md`), disclosed as a substitution, not silently treated as equivalent.

Row 2 (adversarial checker never run) is resolved and then some — it has now run seven times, found two real, previously-undisclosed defects in D1's own record unplanted (D50, D54), and the planted-defect ablation scored 3 of 4 (D50). It also, separately, misbehaved twice (attacking almost everything it's shown; proposing an upward revision labelled as a downgrade) — both disclosed, the second one fixed and tested (D54).

Row 3 (the 29 June candle) has not been revisited tonight.

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
