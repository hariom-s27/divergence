from pathlib import Path
import re
import subprocess
import sys


def _count_stale_hits(output: str) -> int:
    match = re.search(r"'8\.5%' appears (\d+)x", output)
    return int(match.group(1)) if match else 0


def test_gate0_allows_ci_bound_for_retired_percentage():
    repo_dir = Path(__file__).resolve().parents[1] / "divergence"
    probe = repo_dir / "_tmp_ci_bound_test.md"
    baseline = subprocess.run(
        [sys.executable, "gate0_check.py"],
        cwd=repo_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    baseline_hits = _count_stale_hits(baseline.stdout)
    probe.write_text(
        "Exact 95% CI [8.5%, 75.5%] (`python binom_ci.py 3 8`).\n",
        encoding="utf-8",
    )
    try:
        result = subprocess.run(
            [sys.executable, "gate0_check.py"],
            cwd=repo_dir,
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        probe.unlink(missing_ok=True)

    assert _count_stale_hits(result.stdout) == baseline_hits
    assert "_tmp_ci_bound_test.md" not in result.stdout
