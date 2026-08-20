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

## `llm_call.py` — D44 · 20 Aug · removed the Anthropic fallback and the retry-a-403 waste

### The fallback was a live Class 3 hole in the harness itself
D42/D43's `provider_name()` returned whichever key it found — Featherless
first, Anthropic second. That means a shell with `ANTHROPIC_API_KEY` set from
something else, and `FEATHERLESS_API_KEY` simply not set yet, would run the
whole pipeline on Claude, produce a schema-valid record, and nothing would
say so except a field inside `_meta.llm` that nobody is forced to open.
**A confident, correct-looking output resting on ground that quietly
moved — the exact failure this project exists to detect, reproduced inside
the harness that measures it.**

**Fix:** no fallback. `FEATHERLESS_API_KEY` unset is now a hard error.
Running on Claude requires typing `DIVERGENCE_PROVIDER=anthropic` on purpose.
Verified live: with only `ANTHROPIC_API_KEY` set, `check_llm.py` now fails
immediately with the fix in the message, rather than silently proceeding.

**Also fixed:** D43's gated-model hunt cost 9 wasted API calls, because the
retry loop treated `403 model_gated_needs_oauth` as transient and retried it
3× per model. Retries are now limited to actually-transient statuses
(`408/409/425/429/500/502/503/504`); a licence gate raises `GatedModelError`
immediately, with the fix already in the error message.

**Before → after (live, `check_llm.py`):** all three slots still OK, D41
still OK (`resolvers=qwen adversary=mistralai`) — the fix changed failure
behaviour, not the working path.

---

## `node1_extract.py` — 20 Aug · a text-only model can't read an image, so stop letting it try

### The bug
`--file invoice.png` sent an OpenAI `image_url` block to whatever model the
`small` slot resolved to. On Featherless that's `Qwen/Qwen2.5-7B-Instruct` —
**text-only.** The model can't see the block, sees only the trailing
`[the image above is invoice.png]` caption, and returns a plausible
`facts{}` object with `confidence: "certain"` on every field regardless.

> **This is the whole project's thesis happening inside the project.** A
> confident, well-formed, schema-valid extraction, from a document nobody
> read. Nothing in the output says anything went wrong — Class 3, inside
> node 1 itself.

**Fix:** `build_content()` now takes the resolved model and checks
`llm_call.is_vision_model()` before building an image block; a text-only
model hard-fails with the fix in the message rather than silently
extracting from nothing.

### A related, worth-keeping finding from testing the fix
Verified live which Featherless vision models actually work:
`Qwen/Qwen2.5-VL-72B-Instruct` answered a solid-colour test image correctly.
`Qwen/Qwen2.5-VL-32B-Instruct` — reachable, no error — **answered a pure-red
2×2 pixel image "Gray."** Not a crash, not a refusal: a confident wrong
answer on ground truth with zero ambiguity. That is a free data point for
`results.md` if the vision path is demoed: bigger is not always the safe
default even within one model family, and "it responded" is not the same
claim as "it looked."

---

## `citation_matcher.py` — 20 Aug · found while filling ground truth: a bare short citation matches the wrong file

### The bug
Filling `citations_expected[]` for D1/C3/C4 (draft, see below), the natural
citation for the VDA definition is `s.2(111)` — that's the label
`architecture.md`'s own node 3 corpus table uses (*"s.2(111) [was s.2(47A)]"*).
`verify("Section 2(111)", "FY 2026-27")` returns **`VERIFIED`** — but
`v.provision_id` is `FEMA-2n`, not `IT-2-47A`. It matched the wrong file and
said so with full confidence.

### Why
`IT-2-47A.md`'s own `current_citation` field still reads *"Section 2(47A),
Income-tax Act, 1961 — carried into the Income-tax Act, 2025"* — its
`known_limitation` has said *"2025 Act section number unconfirmed"* since 6
August, and nobody had actually tried to cite it as `2(111)` until now. A
bare citation with no Act name (`"Section 2(111)"`, no *"Income-tax Act"*
suffix) doesn't trigger `instrument_of()`'s Act-name detection, so
`_refs_match()` runs against every corpus entry regardless of instrument —
and something in `FEMA-2n.md`'s reference set matched the bracket chain
first.

> **A recorded `known_limitation` and a citation_matcher gap combined to
> silently verify the wrong provision.** Neither alone would have done it —
> the limitation flag didn't stop anyone citing the number it warned about,
> and the matcher's weak disambiguation on an unqualified citation only
> bites when someone actually tries a bare one.

**Workaround applied to the three ground-truth files:** cite
`"Section 2(47A), Income-tax Act, 1961"` — the form the corpus actually
holds — until `IT-2-47A.md` is updated with the confirmed 2025 Act number.
**Not fixed in `citation_matcher.py` itself** — `instrument_of()` needs to
either require an instrument match before ref-matching, or refuse to
`VERIFIED` a bare citation with no detected instrument at all. Logged here
rather than silently patched, since a resolver prompt could hit the exact
same bare-citation shape live.

---

## Ground truth — `citations_expected[]` filled (draft) for all 6 cases, 20 Aug

`citations_expected[]` had been empty in every case since the fields were
scaffolded (Step 21) — the commit `a267f19` ("ground truth frozen pre-run")
claimed a freeze that wasn't actually complete. Filled from
`architecture.md`'s corpus scoping crossed against each case's own facts;
every citation string verified live against `citation_matcher.py` before
being written (catching the `Section 2(111)` bug above in the process).
Marked `_citations_status: DRAFT` in each file — this is legal-judgment
work `STEP21-README.md` assigns to a human (P1), and a first pass by Claude
is not a substitute for that review, only a faster starting point for it.

**Also found:** `eval/score.py`'s `m3_citations()` does not currently read
`citations_expected[]` at all — it validates whatever a run cites against
`citation_matcher.py`, with no recall/precision comparison to a
pre-registered expected set. Filling the field is still the right thing to
do (the ground truth file's own `_citations_note` commits to it, and future
scoring work may consume it), but it does not change what today's metric 3
actually measures — worth knowing before stating how citations are scored.

**Checked, not just flagged:** C4's case.md cites `s.393(4) Table Sl. No. 12`
as the ₹50,000 TDS threshold — the text for it **is** held verbatim in
`corpus/tier-a/IT-393-1-T8vi.md` (`extract_scope` says so explicitly), but
that file's citable `provision_id`/`current_citation` is keyed only to
`Section 393(1), Table Sl. No. 8(vi)`. `citation_matcher.py`
`REJECTED_NOT_FOUND` every `393(4) Table Sl. No. 12` string tried live —
the sub-rule text is present in the file but not independently citable as
its own provision. C4's `citations_expected[]` cites 393(1)/T8(vi) only, with
this noted in the entry's own reasoning field.

---

## Step 27 — the first real end-to-end run, 20 Aug · broke, exactly as predicted

### The run
```
python run_pipeline.py --record-id D1 --tax-year "FY 2026-27" \
    --text step21drop\cases\D1\case.md --out runs\D1_pipeline.json
```
Nodes 1 and 2 had each run alone before. The whole chain — extract → gap
detector → citation matcher → gap enforcer → schema validation — had never
run once. `STEP-27-AND-29.md`'s own instructions said "expect it to break."

### What actually broke
Not one of the three predicted symptoms (missing `--regimes`, missing
`valuation.json`, an empty `missing[]`). A fourth one, at schema validation:

```
schema.json: INVALID — None is not of type 'string'
  ...valuation.methods[1].date_choice.chosen: None
```

`node3_valuation.py` sets `date_choice.chosen = None` **on purpose** — its
own docstring: *"R99 — THE GAP HAS A GAP... never resolve it silently."*
`schema.json`'s `date_choice.chosen` required `{"type": "string", "format":
"date"}` — no null allowed — while the field right next to it,
`prescribed_by`, was correctly typed `["string", "null"]`. The schema simply
missed one field when documenting its own null case.

**Nobody had validated a real record against the schema before this run.**
`node3_valuation.py`'s self-test writes `valuation.json` directly and never
runs it through `jsonschema.validate()`; `run_pipeline.py`'s own
`validate_schema()` was written and self-tested against a hand-built
synthetic record (Step 22) that happened not to exercise this branch.

**Fix:** `schema.json` — `"chosen": {"type": ["string", "null"], "format":
"date"}`. One line.

### Before → after
```
schema.json: INVALID — None is not of type 'string'
```
→
```
schema.json: VALID
```
2 model calls (extract + gap detector), 3986 in / 607 out tokens, 0 retries
either node. `_meta.llm.provider` = `featherless`, models = Qwen/Qwen/Mistral
as expected, `temperature` recorded per the fix above.

---

## Step 31 — C2 through the pipeline · not quite "unchanged," and the honest version is more interesting

The plan called this the best ratio on the board: run C2 (USD bank receipt,
no crypto) unchanged, and if nothing needs to change, that sentence alone is
the scalability argument.

**Something did need to change — but not in C2, and not in the pipeline's
scope logic.** First run: `schema.json: INVALID`. `node1_extract.py`
(Qwen2.5-7B) had nested `"extraction_notes": ["Typed input provided; no
actual documents available."]` **inside** `facts{}` — a bare list where the
schema requires every `facts{}` value to be `{value, confidence, ...}`. This
is syntactically valid JSON, so `call_json()`'s retry-on-bad-JSON path never
fires; it only surfaced as an opaque schema failure at the very end of
`run_pipeline.py`, after both model calls had already run.

**Fix:** `node1_extract.py` now validates every `facts{}` value's shape
immediately after the model call, before returning — `_validate_facts_shape()`.
A malformed field now hard-fails at node 1, with the offending field named,
instead of failing three steps later with a schema-validator stack trace
that doesn't say which node caused it.

**Re-ran C2 after the fix: schema VALID, on the model's own output, no
retry needed.** The malformed shape did not reproduce — same case, same
model, same temperature (dev default, 0) two calls apart, one nested the
notes wrong and one didn't. **That inconsistency is itself the finding**:
even at temperature 0, this 7B model's adherence to an exact multi-key JSON
contract is not fully stable run to run. The scope logic (facts extracted,
one gap found, no VDA-specific citations reached) was identical both times —
the pipeline's *structure* generalised to a non-crypto case exactly as
predicted. Its *small-model reliability* did not, on the first try.

**What to say about it:** not "C2 ran unchanged" — "C2's pipeline structure
required no change; C2's first run caught a real small-model contract
violation that D1 hadn't, and fixing it made node 1 fail loud instead of
failing three steps downstream." That is a better sentence than the clean
one would have been.

---

## `run_arms.py` — D45 · 20 Aug · arm A's first run: 6/6 JSON, 0/6 schema-valid, and it wasn't a reasoning failure

### The run
```
python run_arms.py --arm A --all-cases
```
First real execution of a baseline arm, ever. 6/6 produced parseable JSON.
0/6 validated against `schema.json`.

### What actually happened — checked before writing it down as a finding
Every one of the 6 records had this shape at the top level:
`["$schema", "$id", "title", "description", "type", "required",
"additionalProperties", "properties"]` — **the model returned the schema
document itself**, not a record shaped like it. Looking closer: it filled
real answer values into the schema's own `"properties"` key —
`"properties": {"record_id": "CASE_D1_2026-114", "generated_at": "2023-...",
...}` — conflating the schema *definition* with a data *instance*.
Identical failure mode, 6/6, on Qwen2.5-72B.

**This is not the finding it looks like.** `run_arms.py` was appending the
raw `schema.json` — full Draft-2020-12 syntax, `$schema`/`$defs`/`required`
keywords — as "the output shape." Every prompt this project has actually
gotten working (01 through 05) instead shows a filled *example* JSON object
with `<placeholder>` markers, never the formal schema. Handing arm A the raw
schema and calling that "the same contract" is exactly the "fail on
formatting rather than on reasoning" trap `run_arms.py`'s own docstring says
it wants to avoid — it just failed at it in a way that looked like a
finding about the model instead of a bug in the harness.

**Fix:** `SCHEMA_EXAMPLE` — a filled example instance, same style as the
node prompts, generated from `schema.json`'s own structure. Replaces the raw
schema dump for every arm.

> **Why this matters beyond one bug.** Publishing "arm A: 0/6 schema-valid"
> without catching this would have been exactly the straw-man baseline
> `evaluation-design.md` §2 exists to prevent — not because the prompt was
> weakened, but because the *harness* handed arm A a more confusing output
> contract than arm C's own nodes ever see. Caught before the number went in
> `results.md`, not after.

**Re-run with `SCHEMA_EXAMPLE`: 6/6 JSON, 4/6 schema-valid.** Output tokens
dropped from 2290–2709 to 1097–1611 per case — the model stopped padding
its answer with a copy of the schema, which is itself confirmation the
first run's failure was about the prompt, not the reasoning.

### Second failure, checked the same way before accepting it
C2 and C4 both failed with `True`/`False is not of type 'string', 'number',
'null'` — a boolean `value` in a `facts{}` field.
**Also not an arm A defect.** `extracted_field.value`'s type union never
included `boolean` — and every single case's `ground_truth.json` already
uses boolean values (`"bank_involved": {"value": false, ...}`). The
pipeline's own node 1 simply hadn't happened to extract a boolean-valued
fact in either of the two real runs so far (D1, C2) to trip over it.
**Fix:** `schema.json` — `extracted_field.value` type now `["string",
"number", "boolean", "null"]`. Re-validated the two stored records against
the fixed schema without re-calling the model (the output didn't change,
only the schema did) — both now valid, noted honestly in each file's
`_meta.revalidated_note` rather than silently rewritten.

### The corrected number
**Arm A: 6/6 produced parseable JSON, 6/6 schema-valid**, once the harness
gave it a fair, correctly-typed contract. Two harness bugs found chasing
this number down, neither one a finding about naive prompting — and both
would eventually have hit the real pipeline too (the raw-schema confound
never would have, since nodes 1-5 never see raw schema.json; the boolean
gap absolutely would have, on the first D1/C2-style case that extracts a
boolean fact).

> **Say this, not "arm A held the schema 6/6."** The honest sentence is:
> "arm A holds the output contract when given it fairly — and getting the
> contract fair took two rounds of catching our own bugs first." That is a
> better line for Q&A than a clean number with an unexamined asterisk.

---

## `run_arms.py` — arm B, 20 Aug · a third bug, in the token-match arithmetic itself

First run of arm B (`--token-match runs\`): D1 and C2 — the only two cases
with an arm-C pipeline record to match against — both got `max_tokens` set
to arm C's *measured* `total_out_tokens` (577 for D1, 444 for C2) and both
**produced zero output tokens**, unparseable. C1/C3/C4/C5 (no arm-C record
yet, fell back to the 4096 default) mostly succeeded.

**Checked before writing it down as a finding about arm B:** the raw output
for D1 was mid-sentence inside `facts{}` — genuine truncation, not an empty
response. `total_out_tokens` from `llm_call.provenance()` is the **sum**
across every node call in that run — node 1 wrote *only* `facts{}` (488
tokens), node 2 wrote *only* `missing[]` (89 tokens). Arm B has to write
`facts` + `missing` + `valuation` + `regimes` + `limits` in **one**
completion. Capping that single completion at the sum of two much smaller
partial-output calls starves it structurally — nothing about reasoning
quality, pure budget arithmetic.

**Fix:** `token_budget()` now floors the match at `DEFAULT_MAX_TOKENS`
rather than at 256 — token-match **up** when arm C's measured total
genuinely exceeds the default (informative), never down below a budget a
single-shot completion has already been shown to need. Re-ran D1 and C2
only: both now `json+schema OK`.

**Also worth saying plainly:** there is no genuine token-match possible yet.
Every arm-C record so far is a partial run — `regimes[]` is empty on all of
them, since nodes 3/4/5 are still hand-run and no `--regimes` file has been
passed to any run. Until a full 5-node record exists, "token-matched"
reduces to "given the same 4096-token default everything else gets" — true,
but not what D39 means by the phrase. Say so in `results.md` rather than
letting the field name imply more than it currently delivers.

### Final numbers, all 6 cases, both bugs fixed
| Arm | JSON produced | Schema-valid | Genuine failures (not a harness bug) |
|---|---|---|---|
| A | 6/6 | 6/6 | none |
| B | 6/6 | 4/6 | C4: a `null` rate on a correctly-enumerated second method · C5: `"valuation_method"` (a `regime` value) used where `blocks[]` wanted `"income_tax"/"gst"/"fema"/"valuation"` — a genuine mix-up between two similarly-shaped schema enums |

C4 and C5's failures were checked the same way as everything above and are
real — the model attempted the right structure and got two different
specific things wrong. Worth keeping exactly as they are.

---

## Scoring — two more gaps found running the actual scorers, 20 Aug

### `m3b_citation_coverage.py --all runs/` ran clean, and surfaced something
that must not go in `results.md` unqualified: **arm C's citation recall is
0.000 on both D1 and C2.** Not because the pipeline underperforms the
baseline — `D1_pipeline.json`/`C2_pipeline.json` only ever ran nodes 1+2
(extract, gap detector). No `--regimes` file has been passed to
`run_pipeline.py` for any case yet, so `regimes[]` — the only place a
citation can come from — is empty on every arm-C record that exists.
**Arm C has not been given the chance to cite anything.** Reporting
"arm C: 0.000 recall" without this sentence attached would be exactly the
misleading-baseline-comparison failure `evaluation-design.md` §2 exists to
prevent, aimed at ourselves instead of at arm A. Nodes 3/4/5 (hand-run, fed
in via `--regimes`) have to actually happen before arm C's citation
numbers mean anything.

### `eval/score.py --all` did not run against any real output — now it can
```
KeyError: 'case_id'
```
`score.py` expects a normalised run file: `{"case_id", "arm", "model",
"seed", "facts", "missing", "methods", "elements", "citations", "raw"}` —
written (per its own docstring) for arms A/B to be **hand-coded** into that
shape from raw prose output. Neither `run_pipeline.py`'s schema-conforming
records (`record_id`, citations nested inside `regimes[]`) nor
`run_arms.py`'s wrapped output (`case`, everything nested under `record`)
match it.

**Built `eval/normalize_runs.py`** — the missing adapter, additive,
`score.py` itself untouched (same reasoning as `m3b_citation_coverage.py`:
`score.py`'s history of over-correction bugs is exactly why nobody should
touch it under time pressure). Converts both real shapes into what
`score.py` reads, writes to `runs/normalized/` (not `runs/*.json` directly,
so `score.py --all`'s own glob never double-counts a normalized file as a
second real run), then imports `score.py` and runs its actual scoring
functions — no reimplementation of the metrics.

**Ran it. Numbers came back — and one of them is a real finding, not
noise.** M1 (extraction accuracy) scored **0.0% on almost every row,
including the real pipeline run (arm C) already hand-verified as sensible
earlier tonight.** Checked before writing it down: compared
`cases/D1/ground_truth.json`'s `facts` keys against `runs/D1_pipeline.json`'s
actual keys —

```
ground truth:  asset · settlement_datetime_ist · counterparty_declared ·
               invoice_no · bank_involved · counterparty_verified
pipeline:      asset_currency · settlement_datetime · counterparty_name ·
               invoice_number · bank_reference · (no equivalent)
```

Only `amount`, `recipient_location`, `supplier_location` match exactly.
**`01-extract.md` never specifies field names** — it lists example concepts
("amount, asset/currency, settlement date and time...") and leaves the
model to choose its own labels, which drift from `ground_truth.json`'s
naming on nearly every field. `m1_extraction()` compares `facts` by field
NAME, so a correct extraction under a different name scores as "not
extracted" — 0, not partial credit.

**This is real and it is not specific to one arm.** M1 is 0% (or near it)
for arm A, arm B, and arm C alike, on every case — because none of the
three was ever told to use the ground truth's exact vocabulary. **Not fixed
here.** Two live options, and choosing between them is a real design
decision, not a mechanical patch:
1. Rewrite `01-extract.md` to name the exact fields `ground_truth.json`
   uses, so the prompt matches the pre-registered contract (matches how
   `SCHEMA_EXAMPLE` was fixed earlier tonight — give the model the exact
   shape, don't leave it to infer one).
2. Add synonym/fuzzy field matching to `m1_extraction()` — riskier: this is
   the same shape of mistake `eval/score.py`'s own v1.5 made on gap-matching
   (over-correcting a "no credit" bug into an over-crediting one).

**M2/M3/M4 scored for real, for the first time, across all 14 runs** — see
the table below. **M5 (false abstention) is `None` — undefined — on every
single row.** Not a bug either: `elements{}` (per-element settled/open) is a
ground-truth-only concept today; no prompt anywhere (01–05, baseline,
arm-b-cot) asks any arm to report it in a scoreable shape. `evaluation-design.md`
calls M5 *"the metric that earns trust"* — it cannot be computed from any
output that exists right now, for any arm.

| Case | Arm | M1 extract | M2 recall | M2 prec | M3 valid | M3 stale | M4 methods | M5 false abst |
|---|---|---|---|---|---|---|---|---|
| C1 | A |   0.0% |   — |   0.0% |  25.0% |   0.0% | 2/1 |   — |
| C1 | B |   0.0% |   — |   0.0% |  25.0% |   0.0% | 2/1 |   — |
| C2 | A |   9.1% |   — |   0.0% |  50.0% |   0.0% | 2/1 |   — |
| C2 | B |   9.1% |   — |   0.0% |  50.0% |   0.0% | 2/1 |   — |
| C2 | C |   9.1% |   — |   0.0% |    — |    — | 12/1 |   — |
| C3 | A |   0.0% |   0.0% |   0.0% |  25.0% |   0.0% | 2/5 |   — |
| C3 | B |   0.0% |   0.0% |   0.0% |  20.0% |   0.0% | 2/5 |   — |
| C4 | A |   0.0% |   0.0% |   0.0% |  50.0% |   0.0% | 2/10 |   — |
| C4 | B |   0.0% |   0.0% |   0.0% | 100.0% |   0.0% | 2/10 |   — |
| C5 | A |   0.0% | 100.0% | 100.0% |  50.0% |   0.0% | 2/2 |   — |
| C5 | B |   0.0% | 100.0% |  33.3% |  50.0% |   0.0% | 2/2 |   — |
| D1 | A |   0.0% |  75.0% | 100.0% |  60.0% |   0.0% | 2/12 |   — |
| D1 | B |   9.1% |  25.0% |  33.3% |  50.0% |   0.0% | 2/12 |   — |
| D1 | C |   9.1% |   0.0% |   0.0% |    — |    — | 12/12 |   — |

**Read this table carefully before quoting a single cell of it in
`results.md`.** M1 and M5 are not "the pipeline scored badly" — they are
"these metrics cannot be computed correctly from any output that exists
yet." C2/D1 arm C's M4 (12/1, 12/12) look strong because arm C's valuation
lattice enumerates methods deterministically (⚙ B, no model involved) —
that is real, but M3 shows `—` on the same rows because `regimes[]` is
still empty, so it is not the full comparison D40 asks for either.

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
