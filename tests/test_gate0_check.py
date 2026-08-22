from pathlib import Path
import subprocess
import sys


def test_gate0_allows_ci_bound_for_retired_percentage():
    repo_dir = Path(__file__).resolve().parents[1] / "divergence"
    probe = repo_dir / "_tmp_ci_bound_test.md"
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

    assert result.returncode == 0
    assert "'8.5%' appears" not in result.stdout
