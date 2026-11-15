# Ensures the repo root is on sys.path for pytest regardless of invocation
# style (bare `pytest` vs `python -m pytest`), so `from divergence.x import y`
# resolves the same way in CI as it does locally.

# P09-48: never collect anything under the git-ignored local text folder (law text, scratch scripts).
collect_ignore = ["divergence/statutes/_local_text"]
