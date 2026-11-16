"""C4-B guards: committed CSV only; body behavior uses a synthetic build stub."""
import hashlib

from divergence import act_parse as ap
from divergence import statute_build as sb
from divergence import statute_guard as guard


def test_code_guard_equals_approved_hash():
    rows = ap.read_csv(sb.VERSIONS_PATH)
    assert len(rows) == 34
    assert guard.code_sha(rows) == "b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7"
    assert guard.code_sha(list(reversed(rows))) == guard.CODE_SHA256


def test_code_guard_cli(capsys):
    assert guard.main(["--code"]) == 0
    assert f"34 rows sha256 {guard.CODE_SHA256} PASS" in capsys.readouterr().out


def test_body_guard_uses_historical_serialization():
    hashes = {"FAKE:v2": "b" * 64, "FAKE:v1": "a" * 64}
    expected = hashlib.sha256(repr(sorted(hashes.items())).encode("utf-8")).hexdigest()
    assert guard.body_sha(hashes) == expected


def test_body_guard_stub_never_writes(monkeypatch, capsys):
    calls = []
    hashes = {"FAKE:v1": "a" * 64}

    def fake_build(raw, out_dir, *, write):
        assert write is False
        calls.append((raw, out_dir))
        return {"body_sha": hashes}

    monkeypatch.setattr(sb, "build", fake_build)
    assert guard.main(["--body"]) == 1  # synthetic hash must not pass the approved real corpus guard
    assert len(calls) == 1 and "FAIL" in capsys.readouterr().out
