"""Offline tests for mutate.py's P03 runner: one counted schema-retry,
resume-by-skipping, the error stop line. node5_adversarial.check is
stubbed -- no model call, no replay-cache access."""
from pathlib import Path
import json
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "divergence"))
import mutate  # noqa: E402
from llm_call import LLMError  # noqa: E402

GOOD = ([{"target": "t", "attack": "a", "survived": False}], [], [], {})
SHAPE = LLMError("node5_adversarial: model output has no top-level 'checked_and_survived' array")
TRANSPORT = LLMError("[node5_adversarial] featherless/x transport failure after 3 attempts: boom")


def _stub(monkeypatch, outcomes):
    calls = []

    def fake_check(*args, **kwargs):
        calls.append(1)
        out = outcomes[len(calls) - 1]
        if isinstance(out, Exception):
            raise out
        return out
    monkeypatch.setattr(mutate.node5_adversarial, "check", fake_check)
    return calls


def _run_one(tmp_path, op="NULL"):
    data = mutate.load_case("D1")
    specs = mutate.case_specs("D1", data, mutate.DEFAULT_SEED)
    fn = dict(mutate.OPERATORS + [("NULL", mutate.op_null)])[op]
    return mutate.run_one("D1", op, fn, data, specs, mutate.DEFAULT_SEED, "adversarial",
                          str(tmp_path), rep=1, tag_rep=True)


def test_shape_error_is_retried_once_and_both_attempts_kept(tmp_path, monkeypatch):
    calls = _stub(monkeypatch, [SHAPE, GOOD])
    row = _run_one(tmp_path)
    assert len(calls) == 2 and row["schema_retried"] and row["error"] is None
    assert row["first_attempt_error"].startswith("node5_adversarial:")
    assert [a["attempt"] for a in row["attempts"]] == [1, 2]
    assert row["caught"] is True


def test_shape_error_twice_is_error(tmp_path, monkeypatch):
    calls = _stub(monkeypatch, [SHAPE, SHAPE])
    row = _run_one(tmp_path)
    assert len(calls) == 2 and row["error"] is not None and row["caught"] is None
    assert row["caught_specific"] is None


def test_transport_error_is_not_retried(tmp_path, monkeypatch):
    calls = _stub(monkeypatch, [TRANSPORT, GOOD])
    row = _run_one(tmp_path, op="CITE_SWAP")
    assert len(calls) == 1 and not row["schema_retried"] and row["error"] is not None


def test_existing_file_is_skipped_never_overwritten(tmp_path, monkeypatch):
    out = tmp_path / "D1_NULL_r1.json"
    out.write_text(json.dumps({"case": "D1", "operator": "NULL", "error": None, "caught": True}),
                   encoding="utf-8")
    before = out.read_bytes()
    calls = _stub(monkeypatch, [GOOD])
    row = _run_one(tmp_path)
    assert calls == [] and row["_skipped_existing"] and out.read_bytes() == before


def test_stop_line_counts_against_all_planned_calls(tmp_path, monkeypatch):
    _stub(monkeypatch, [TRANSPORT] * 100)
    # D1 only, 7 ops + NULL = 8 planned; 15% of 8 = 1.2, so the 2nd error stops it
    with pytest.raises(SystemExit):
        mutate.run_live(mutate.DEFAULT_SEED, out_dir=str(tmp_path), cases=["D1"], nulls=True,
                        tag_rep=True, max_error_rate=0.15)
    assert len(list(tmp_path.glob("*.json"))) == 2
