# Amendment 2 to expectations.md (P03)

Written **2026-10-21 21:16:14 UTC** while the full sweep (`full/`, R=3) was running. State at writing, from the sweep log: **36/144 calls done, 9 after-retry ERRORs**. Of those 9, 8 failed node 5's output-shape check on both attempts, and 1 (C2_NULL_r1) failed the shape check on attempt 1 and then hit a transport failure on the retry.

`expectations.md` and `expectations_amendment.md` are unchanged. Nothing here changes the SPECIFIC matcher, the operators, the model, the prompt, the temperature or the retry rule.

## Rule

If the 15% stop line triggers, and the ERRORs are confirmed to be node-5 output-shape failures (not harness, cache or transport failures), the sweep is resumed to completion (all 144 planned calls) as a documented deviation. The stop event, the time, the call count at stop, and the final first-attempt and after-retry error rates are reported. ERRORs stay excluded from all denominators.

ERRORs whose final attempt was a transport failure (currently 1: C2_NULL_r1) are reported separately and do not count toward this condition, provided every other ERROR is a shape failure on both attempts and there are no harness or cache failures. If transport-failure ERRORs exceed 3 in total, do NOT resume: STOP and report, because that indicates a provider problem.

**Reason:** the stop line was a guard against a broken setup; the observed errors are model output failures, which are themselves a result.

## How the resume is run

Resume = the same command without `--max-error-rate`, all other flags unchanged, existing files skipped and never overwritten:

```
python -u mutate.py --out-dir runs/2026-10-21_mutants/full --nulls --reps 3 --per-rep-cache
```

with `DIVERGENCE_REPLAY` unset and `DIVERGENCE_REPLAY_CACHE_DIR` = `runs/2026-10-21_mutants/_live_cache` (the same as the original run). `--max-error-rate` is dropped because `mutate.py` counts the ERRORs of files it skips as already done, so the same command with the flag would stop again at once.

Run from D:\sem_iitk\sem9\reverie\divergence (the original working directory); DIVERGENCE_REPLAY_CACHE_DIR is the absolute path D:\sem_iitk\sem9\reverie\divergence\runs\2026-10-21_mutants\_live_cache. *(added 2026-10-22T00:43:17Z, after writing, before resume)*
