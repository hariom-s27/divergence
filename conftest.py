# Ensures the repo root is on sys.path for pytest regardless of invocation
# style (bare `pytest` vs `python -m pytest`), so `from divergence.x import y`
# resolves the same way in CI as it does locally.
