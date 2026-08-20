# ITERATION LOG — DIVERGENCE
### Every version, what changed, why, and what the result was.
### Written live, at the moment of each change. Nothing here is reconstructed.

> **Why this file exists.** The ML track's Technical Execution criterion names
> *"documented iteration"* explicitly. Most teams have nothing here — not because
> the work is hard but because nobody writes it down while it is happening. A log
> assembled afterwards reads like one, and a judge can tell.
>
> **Format:** date · component · version · what changed · why · result before → after.

---

## `citation_matcher.py` — v1 → v2 → v3

### v1 · 6 Aug · **12/15**
Whole-string substring matching against the corpus header.

**Three false negatives, all on REAL citations:**

| Cited | Corpus header | Why it failed |
|---|---|---|
| `Section 439(8)(a)` | `Section 439(8), Income-tax Act, 2025` | sub-clause depth |
| `Section 2(6) IGST Act` | `Section 2(6), Integrated Goods and Services Tax Act, 2017` | act-name variant |
| `FEMA section 3` | `Sections 3, 7 and 8, Foreign Exchange Management Act, 1999` | multi-provision file |

**All three were the same underlying error: comparing strings instead of
references.**

### v2 · 6 Aug · **14/15**
Rewrote to parse both sides into `(instrument, base number, bracket chain)`,
with bracket chains matching on prefix. All three v1 failures resolved.

### v3 · 6 Aug · **15/15** — ⭐ and the last bug was not in the code
The remaining failure was in the **data**. A corpus header read:

```
current_citation: "Section 50, CGST Act 2017 — with a note on ss.73, 74 and 74A"
```

Parsing that field pulled out **four** references, and the wrong file matched
first.

> **The data was wrong, not the logic. And only the test found it.**

**Rule adopted:** a citation field contains a citation, not a note about one.
Notes go in a separate `note:` key. Corpus header cleaned.

---

## `citation_matcher.py` — v4 · 19 Aug · three fixes, one of them embarrassing

### v4a — Windows crash
The self-test printed `✓`. Python 3.14 on Windows defaults the console to cp1252
and it raised `UnicodeEncodeError` mid-table. **It had been crashing on every
Windows run and we had only ever run it on one machine.** Added
`sys.stdout.reconfigure(encoding="utf-8")`.

**Result:** runs to completion on Windows. Would have crashed on a judge's laptop.

### v4b — the 4-digit-year false match
`extract_refs()` read the year in *"CGST Act 2017"* as a section number, so
`GST-CGST-50.md` and `GST-CGST-74A.md` both registered a claim on "Section 2017".
Added a guard rejecting a bare `19xx`/`20xx` with no bracket chain.

**Result:** two spurious provision claims removed. Found by `gate0_check.py`, not
by reading.

### v4c — ⭐ **OWN-5: the self-test itself was stale**
This line had been passing since 6 August:

```python
("Rule 115", "FY 2026-27", "VERIFIED", "in corpus (though inapplicable)"),
```

Rule 115 became **Rule 206** under the notified Income-tax Rules, 2026, effective
1 April 2026 — confirmed from the CBDT Navigator, row 206.

> **The test asserted a stale citation was current, and passed 15/15 the entire
> time. Four months. It was not found by anyone reading it — it was found by a
> tool flagging two corpus files claiming the same provision.**

**Before → after:** `Rule 115 · FY 2026-27` returned `VERIFIED`; now returns
`STALE → cite Rule 206`. Corpus: `IT-RULE-206.md` retired to
`_old_corpus_backup/`; `ITR2026-RULE-206.md` carries the former citation and
handles all four year/number combinations on its own.

**This is the fifth stale citation in the project and the first caught by the
process rather than by a person.** That is the version of the story worth telling.

---

## Corpus rebuild · 18–19 Aug

### The problem
`gate0_check.py` found **three pairs of files each claiming one provision.**
`citation_matcher.py` loads `sorted(os.listdir())` and takes the first match, so
in every pair the alphabetically-earlier file **shadowed** the other:

| Shadowing | Shadowed | Effect |
|---|---|---|
| `IT-RULE-57.md` (1962 text) | `ITR2026-RULE-57.md` (gazette) | the gazette file never matched |
| `IT-RULE-207.md` | `ITR2026-RULE-207.md` | same |
| `IT-RULE-206.md` | `ITR2026-RULE-206.md` | `Rule 115` returned VERIFIED for FY 2026-27 |

**15/15 was a property of the folder, not of the code.**

### The fix
Retired the shadowing files. Verified that each surviving file's
`former_citation` handles all four year/number cases alone — tested before
deleting anything, 13/13.

### Two files could never be cited at all
`FBIL-METHODOLOGY.md` and `SBI-TTBR-DATA.md` had no section or rule number in
`current_citation`, so `extract_refs()` returned `[]` and **nothing could ever
match them.** Any conclusion resting on the SBI rate would have been silently
dropped by our own matcher.

- `SBI-TTBR-DATA.md` → `Rule 207(3)(b), Income-tax Rules, 2026` — the only
  provision in the notified Rules that names the State Bank of India
- `FBIL-METHODOLOGY.md` → demoted to Tier B. No provision in the corpus names
  FBIL, so there is no honest handle to give it. It is context for why the
  official rate does not answer the question, never authority.
- `ITR2026-RCASP-VALUATION.md` → `Rule 243(8)(e), Income-tax Rules, 2026`

**Setting `citable: false` alone would not have worked** — neither tool consults
that flag until a citation has already ref-matched, and a file with no number
never gets that far.

---

## `canonical_case.py` — v2 · 19 Aug · removed the headline number

### What changed
Stopped persisting `spread_per_unit`, `spread_pct`, `total_official`,
`total_market`, `total_spread`, `market_leg_raw`, `market_leg_usdc_terms` and
`official_leg_sbi_ttbr` to `canonical_case.json`.

### Why
Each of those baked in **one silently-chosen candle field and one
silently-chosen official date.**

> **That is F1 — silent rate selection — the top-ranked failure in our own risk
> register, sitting in the script that generates our own case.**

The console still prints an illustrative per-candidate spread for a human
sanity check. Nothing single-valued is written to disk. `node3_valuation.py` →
`valuation.json` is now the authoritative source.

### Also fixed
`OFFICIAL_CANDIDATES` labelled **26 June** as *"last published before receipt"*.
The SBI sheet captured at 14:15 on 26 June is headed `Date 25-06-2026` — no rate
had been published for the 26th. Corrected to the 25th.

**The mislabelling was the exact mistake this case is built around, in the code
that builds the case.**

**Before → after:** the JSON carried `spread_pct: 9.515` and
`total_spread: 44720.71`, both wrong relative to the 12-method lattice's real
range of ₹4,69,750 → ₹5,17,618.76 (spread ₹47,868.76 / 10.19%).

---

## `eval/score.py` — v1 → v2 · 19 Aug · the scoring rule itself

### v1 — under-credited the baseline
Gap matching used `difflib` ratio at 0.72. Arm A answers in prose, so
`"no FIRC"` vs `"bank certificate of foreign inward remittance (FIRC)"` scored
**0.28** and counted as a miss.

**Under-crediting arm A is the straw-man failure the entire evaluation is
designed to avoid.** A baseline you score harshly is not a baseline.

### v1.5 — over-corrected
Added a fallback matching short alpha tokens as acronyms. It then matched
`"purpose code"` to `"no FIRC"`, because both contain a short alpha token.

**Recall jumped to 100% on a run that had found one gap out of four.**

### v2 — shared distinctive token only
Requires a shared token of length ≥ 4 that is not a stopword. No acronym or
substring fallback.

**Result on the smoke run:** recall 25%, precision 100% — one of four planted
gaps found, correctly. Verified independently on the real folder with two
planted gaps: each matched only its own counterpart, no cross-contamination.

> **Both directions of error are bad. Inflating arm A is worse, because it hides
> the failure we are trying to measure.** That asymmetry is written into the code
> comment so the next person does not "fix" it back.

---

## Nodes 1, 2, ⚙ A and the orchestrator — 20 Aug · first build

### What was built
`node1_extract.py` (🤖 1), `node2_gaps.py` (🤖 2), `gap_enforcer.py` (⚙ A), and
`run_pipeline.py` to wire them together, plus the prompts they run —
`step22drop/prompts/01-extract.md` and `02-gap-detector.md`, written to match
the style already set by 03/04/05. `gap_enforcer.py` ships with a `--self-test`
in the same shape as `citation_matcher.py`'s: a fluent, confident conclusion
that talks past the gap list, checked against one that has nothing to do with
it. Both come out right — 2/2.

### ⭐ Found while wiring node 2, not by reading: `corpus/verbatim/` was stale
`02-gap-detector.md`'s scope names `ITR2026-RULE-56.md` as an injected file.
Loading it for the first time failed — the file did not exist in
`corpus/verbatim/`. `corpus/tier-a/` picked up four new gazette provisions on
19 Aug (`ITR2026-RULE-206/207/247/56`, per `MANIFEST.md`), but
`corpus/verbatim/` was never regenerated to match. It still held three files
under the old naming (`IT-RULE-115.md`, `IT-RULE-206.md`, `IT-RULE-57.md`) and
`FBIL-METHODOLOGY.md`, demoted to Tier B the same day and no longer citable.

**This means `prompt 03` — written today, in this same drop — named an
injection file that did not exist.** Nobody had tried to actually load
`corpus/verbatim/` against the new prompts yet; the prompt file and the corpus
folder had silently diverged the moment `tier-a/` was regenerated, and nothing
before this checked the two stay in sync.

**Fix:** `python corpus/split_corpus.py corpus` — the project's own
regeneration tool, already written 10 Aug for exactly this — cuts
`corpus/verbatim/` from `corpus/tier-a/`'s `<!-- VERBATIM-START/END -->`
markers. Ran clean, 17/17 files by explicit marker, exit 0. The four orphaned
files (no longer produced by any `tier-a/` source) were then deleted by hand,
since the tool only ever writes, never prunes.

**Before → after:** `corpus/verbatim/` held 17 files, 4 of them stale/orphaned
and missing the 4 newest provisions → 17 files, exactly mirroring `tier-a/`.
`citation_matcher.py` self-test unaffected (15/15 — it reads `tier-a/`, not
`verbatim/`, so this bug was invisible to the one check that already runs
every time). `gate0_check.py`: 0 blocking problems, 7 pre-existing warnings,
unchanged.

> **The corpus-regeneration tool and the prompt-writing step are two different
> people's work on two different days, and nothing connected them until a node
> actually tried to read the file.** Same shape as OWN-5: caught by a build
> step trying to run, not by anyone reading either file.

---

## Provider swap: Anthropic → Featherless — 20 Aug · D42/D43

### What changed
`llm_call.py` rewritten to pick a provider at runtime from whichever key is
set (`FEATHERLESS_API_KEY` preferred, `ANTHROPIC_API_KEY` as a fallback/
cost-estimate path) rather than hardcoding Anthropic. Reason: the eval runs
on competition credits at Featherless, not metered Claude — see
`DECISION-D42.md`. `node1_extract.py` / `node2_gaps.py` updated to the new
`call_json()` interface and provenance tracking; `node1_extract.py`'s
multimodal input switched from Anthropic's `image`/`document` blocks to
OpenAI-format `image_url` blocks (Featherless has no native PDF block, so a
`--file` PDF is now text-extracted via `pypdf` instead — a scanned PDF with
no text layer hard-fails with an explicit message rather than silently
sending nothing).

### ⭐ Found by `check_llm.py`, before any real run: the default adversarial model is gated
D42's default `adversarial` slot, `meta-llama/Meta-Llama-3.1-70B-Instruct`,
403'd: `model_gated_needs_oauth`. Every other `meta-llama/*` model tried
(`Llama-3.3-70B-Instruct`, `Llama-3.1-8B-Instruct`) 403'd the same way — a
HuggingFace license gate Featherless passes through, invisible in the
`/v1/models` listing (`available_on_current_plan` was `true` for all of
them). **Only calling the model surfaced it.**

**Fix (D43):** `adversarial` moved to `mistralai/Mistral-Large-Instruct-2411`
— confirmed working live, still a different model family from the `large`
(Qwen) resolvers, so D41's independence requirement holds. `check_llm.py`
re-run clean after the fix: all three slots OK, D41 OK.

**Before → after:** `check_llm.py` — 2/3 slots OK, `adversarial` FAIL → 3/3
OK. `node2_gaps.py` run live end-to-end on a synthetic fact set (connectivity
smoke test, not a real case): valid `missing[]` returned, provenance
recorded (`Qwen/Qwen2.5-7B-Instruct`, 2639 in / 81 out tokens, 0 retries).

> **This is the same shape as the `corpus/verbatim/` staleness bug above and
> as OWN-5: a real, load-bearing problem that only running the thing found,
> sitting in code written the same day and never executed once before this.**

---

## Design decisions that changed the build

| Date | Change | Why |
|---|---|---|
| 18 Aug | Test set cut 30 → **6** (1 deep + 5 clean) | Depth beats breadth for this claim. 6 cases prove both halves of the capability; 30 shallow ones prove neither, and 30 was sized for eleven days |
| 18 Aug | Metric 5 scored **per element**, not per case | C3 and C4 are *partially* determinate. A USDC receipt on a Tuesday still has no prescribed valuation method. Marking them "clean" would have trained the system to give a wrong answer |
| 18 Aug | Third evaluation arm added — **token-matched CoT** | Without it the honest reading of any result is *"more compute helps"*, and a judge will say it if we don't |
| 19 Aug | Valuation moved from a model call to **deterministic code** | The headline number must never be a token prediction. Also means the demo needs no API and cannot fail on stage |
| 19 Aug | Node 6 → **a different model** from the resolvers | Self-consistency bias. Intrinsic self-correction is documented as unreliable |

---

## Still open

- **Nodes 1 and 2 have run live (Featherless, `Qwen/Qwen2.5-7B-Instruct`)
  only as connectivity smoke tests** — a synthetic fact set through node 2,
  not yet a real case's invoice/payment record through the full
  `run_pipeline.py` chain end to end. That real first run, on a real case,
  still needs doing and still goes in this log.
- **Nodes 3, 4, 5 are still prompts only** (`03/04/05`), run by hand per the
  STEP21 protocol — not wired into `run_pipeline.py`. `--regimes` accepts
  their hand-coded output so `run_pipeline.py` can enforce and cite-check it,
  but nothing calls them automatically yet.
- **The adversarial checker has never run.** Everything it is credited with
  finding was found by humans. The Step 29b ablation decides whether it stays.
- **The baseline has never run**, frozen since 6 August. 100 points rest on an
  unexecuted comparison.
- **Zero interviews.** The only item on the board whose clock we do not control.
