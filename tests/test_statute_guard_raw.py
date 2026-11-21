"""Raw-folder routing uses a fake build; no PDF or local body is read."""
import pytest

from divergence import statute_guard as guard


def test_raw_with_code_is_usage_error(tmp_path):
    with pytest.raises(SystemExit) as error:
        guard.main(["--code", "--raw", str(tmp_path)])
    assert error.value.code == 2


@pytest.mark.parametrize("existing_file", [False, True])
def test_raw_nonfolder_is_usage_error(tmp_path, existing_file):
    raw = tmp_path / "not-a-folder"
    if existing_file:
        raw.write_bytes(b"metadata\n")
    with pytest.raises(SystemExit) as error:
        guard.main(["--body", "--raw", str(raw)])
    assert error.value.code == 2


def test_raw_override_routes_to_build(tmp_path, monkeypatch, capsys):
    captured = []
    hashes = {"fake-id": "0" * 64}

    def build(raw, out, *, write):
        captured.append((raw, write))
        return {"body_sha": hashes}

    def unexpected_latest():
        pytest.fail("explicit --raw must bypass latest_raw_dir")

    monkeypatch.setattr(guard.sb, "build", build)
    monkeypatch.setattr(guard.se, "latest_raw_dir", unexpected_latest)
    monkeypatch.setattr(guard, "BODY_SHA256", guard.body_sha(hashes))
    assert guard.main(["--body", "--raw", str(tmp_path)]) == 0
    assert captured == [(tmp_path, False)]
    assert f"raw folder: {tmp_path}" in capsys.readouterr().out
