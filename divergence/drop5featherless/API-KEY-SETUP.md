# Where the Featherless key goes — and where it must never go

**Short answer: nowhere in the repo. It goes in your shell, as an environment
variable called `FEATHERLESS_API_KEY`. `llm_call.py` reads it at runtime.**

You paste the real key once, into a terminal. No file, no commit, no
screenshot in the demo video.

---

## Why this matters for *this* project specifically

You are about to `git init` and quote a commit hash in `results.md` as proof
the ground truth was frozen before any model ran. That hash is your
pre-registration. If a key is in the first commit, it is in the hash you are
asking a judge to trust, and it stays in the history even if you delete the
file later.

---

# STEP 1 — Put the files in place

Copy these four into your `divergence/` folder, overwriting what's there:

| File | What changed |
|---|---|
| `llm_call.py` | **replaces** the Anthropic-only one. Two providers now. |
| `requirements.txt` | adds `openai` |
| `.gitignore` | **new** — must exist *before* `git init` |
| `check_llm.py` | **new** — smoke test, run it before spending credits |

`node1_extract.py`, `node2_gaps.py`, `gap_enforcer.py` and `run_pipeline.py`
do **not** change. `call_json(system, user_content, model_key, ...)` has the
same signature it had.

---

# STEP 2 — Install the openai package

```powershell
pip install -r requirements.txt
```

---

# STEP 3 — Set the key in your shell

**Windows PowerShell** (what you're using):

```powershell
$env:FEATHERLESS_API_KEY = "rc_PASTE_YOUR_FULL_REAL_KEY_HERE"
```

Check it took:

```powershell
$env:FEATHERLESS_API_KEY.Length
```

Prints a number if it took, nothing if it didn't. Check the length, never
print the key itself — you will be screen-sharing this terminal during the
demo.

> **This lasts only as long as that PowerShell window.** Close it, the key is
> gone and you set it again. That is the correct behaviour, not a bug. If you
> want it to persist on your own machine:
> `setx FEATHERLESS_API_KEY "rc_..."` — then **open a new window**, because
> `setx` does not affect the window you typed it in.

**Windows CMD:** `set FEATHERLESS_API_KEY=rc_...`
**Mac / Linux (your two teammates):** `export FEATHERLESS_API_KEY="rc_..."`

Each of the three of you needs their own key set in their own shell. Do not
put one key in a shared file for the team.

---

# STEP 4 — Smoke-test it before spending anything

```powershell
python check_llm.py
```

What good looks like:

```
provider : featherless
base_url : https://api.featherless.ai/v1
key env  : FEATHERLESS_API_KEY  [set]

  small        Qwen/Qwen2.5-7B-Instruct                         OK
  large        Qwen/Qwen2.5-72B-Instruct                        OK
  adversarial  meta-llama/Meta-Llama-3.1-70B-Instruct           OK

D41 OK   resolvers=qwen  adversary=meta-llama  (different families)

smoke-test spend: 3 calls, 84 in / 21 out tokens
```

Total cost of that: about a hundred tokens. Do this *first*, every time you
sit down, before running the pipeline.

### If a model line says FAIL

Most likely cause: **that model size isn't on your Featherless plan tier.**
Featherless gates by parameter count. You do not edit `llm_call.py` to fix
this — you point an env var at a model you *can* serve:

```powershell
$env:DIVERGENCE_MODEL_LARGE = "Qwen/Qwen2.5-14B-Instruct"
$env:DIVERGENCE_MODEL_ADVERSARIAL = "meta-llama/Meta-Llama-3.1-8B-Instruct"
```

Then re-run `check_llm.py`. Browse https://featherless.ai/models for exact
IDs — they are HuggingFace `org/name` strings, copied verbatim.

> ⚠ **One rule when you override: keep the adversary in a different family
> from the resolvers.** `check_llm.py` prints a WARNING if you break it.
> D41 exists because a model checking its own work agrees with itself. If
> node 5 is the same model as node 3, "the adversarial node found nothing"
> means nothing, and a judge who knows this will ask.

---

# STEP 5 — Run the pipeline

Nothing new. Same command:

```powershell
python run_pipeline.py --case cases/D1 --regimes income_tax,gst,fema
```

`llm_call.py` sees `FEATHERLESS_API_KEY`, picks Featherless, and goes.

---

# STEP 6 — Record which models actually ran (do this, it's 5 lines)

This is the honesty half of the change, and it's the half that shows up in
your write-up.

In `run_pipeline.py`, near the top:

```python
import llm_call
```

and where you build the `_meta` block, add one key:

```python
record["_meta"]["llm"] = llm_call.provenance()
```

You now get, in every output record:

```json
"llm": {
  "provider": "featherless",
  "models": {
    "small": "Qwen/Qwen2.5-7B-Instruct",
    "large": "Qwen/Qwen2.5-72B-Instruct",
    "adversarial": "meta-llama/Meta-Llama-3.1-70B-Instruct"
  },
  "by_node": { "node1_extract": {"calls": 1, "in_tokens": 3812, "out_tokens": 606, "retries": 0}, ... },
  "total_calls": 5,
  "note": "Figures above are the MEASURED run on this provider. Any Claude
           rupee-per-record figure quoted elsewhere is a metered deployment
           estimate, not this run."
}
```

**Why you want this.** D35 says the eval runs on open models and the Claude
₹/record figure is a *metered estimate*. Right now that distinction lives in
a decision log. After this it lives in the output file, per record, and
`results.md` can quote it instead of you remembering to say it. The sentence
that survives Q&A is:

> *"Every number in the results table was produced by the open models named
> in the record's own `_meta` block. The Claude cost figure is a deployment
> estimate and is labelled as one."*

That is a much better answer than "we used Claude, roughly."

---

# STEP 7 — Then, and only then, git init

```powershell
git init
git add .gitignore
git commit -m "gitignore before anything else"
git add .
git status          # <-- READ THIS. No .env, no key file, nothing odd.
git commit -m "DIVERGENCE: corpus, pipeline, ground truth frozen pre-run"
git rev-parse HEAD  # <-- this hash goes in results.md
```

`git status` before the second commit is not optional. Look at the list.

---

## Two things to expect on open models that you did not see on Claude

1. **JSON comes back wrapped in ```json fences, or with "Sure, here you go"
   in front.** Handled — `llm_call.py` strips fences, finds the first
   balanced object, and if it still can't parse, shows the model its own bad
   output and asks again (up to 3 attempts). The retry count lands in
   `provenance()`, so if a node is retrying constantly you'll see it rather
   than guess.

2. **Extraction quality on the 7B `small` slot will be worse than Haiku.**
   That is not a problem to hide — it is a measurement. If node 1's
   extraction accuracy drops, that is a real finding about running this
   pipeline on open weights, and it belongs in `results.md`. If it drops so
   far the pipeline is meaningless, move `small` up to 14B/32B and say in
   the write-up that you did, and why.

---

## What I did NOT do

I did not write your key into any file, and neither should you. The string
you pasted is not in `llm_call.py`, `check_llm.py`, `.gitignore`,
`requirements.txt`, or this document. Search the folder if you want to
confirm:

```powershell
Select-String -Path *.py,*.md,*.txt,*.json -Pattern "rc_" 
```

Should return nothing.
