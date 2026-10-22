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


# (line, label it must raise, or None). Every retired figure is checked both
# ways: on its own it is flagged, as the tail of a longer number it is not.
_BOUNDARY_PROBE = [
    ("8.5%", "8.5%"),
    ("(8.5%)", "8.5%"),
    ("8.5 %", "8.5%"),
    ("38.5%", None),
    ("18.5%", None),
    ("108.5%", None),
    ("0.85%", None),
    ("43,633", "43,633"), ("143,633", None),
    ("9.27%", "9.27%"), ("19.27%", None),
    ("41,150", "41,150"), ("141,150", None),
    ("44,400", "44,400"), ("144,400", None),
    ("9.45%", "9.45%"), ("19.45%", None),
    ("8.7%", "8.7%"), ("8.7 percent", "8.7%"), ("18.7%", None),
    ("4,70,517", "4,70,517"), ("14,70,517", None),
    ("44,720", "44,720"), ("144,720", None),
    ("9.515%", "9.515%"), ("19.515%", None),
]


def _all_stale_counts(output: str) -> dict:
    return {m.group(1): int(m.group(2))
            for m in re.finditer(r"'([^']+)' appears (\d+)x", output)}


def _run_gate0(repo_dir):
    return subprocess.run([sys.executable, "gate0_check.py"], cwd=repo_dir,
                          check=False, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def test_gate0_stale_figures_need_a_left_boundary():
    repo_dir = Path(__file__).resolve().parents[1] / "divergence"
    probe = repo_dir / "_tmp_stale_boundary_test.md"
    baseline = _all_stale_counts(_run_gate0(repo_dir).stdout)
    probe.write_text("".join(f"Probe figure {text}.\n" for text, _ in _BOUNDARY_PROBE),
                     encoding="utf-8")
    try:
        result = _run_gate0(repo_dir)
    finally:
        probe.unlink(missing_ok=True)

    expected = dict(baseline)
    for _, label in _BOUNDARY_PROBE:
        if label:
            expected[label] = expected.get(label, 0) + 1
    assert _all_stale_counts(result.stdout) == expected
    listed = set(int(n) for n in re.findall(r"_tmp_stale_boundary_test\.md:(\d+)", result.stdout))
    for i, (text, label) in enumerate(_BOUNDARY_PROBE, 1):
        if label is None:
            assert i not in listed, f"{text!r} was flagged"
