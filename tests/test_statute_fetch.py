"""Tests for divergence/statute_fetch.py. No network: a fake opener stands in for urllib.
All PDF content is invented (FAKE FIXTURE - NOT LAW)."""
import io
import json
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from divergence import statute_fetch as sf

BASE = sf.BASE


def _pdf_bytes(text: str = "FAKE FIXTURE - NOT LAW") -> bytes:
    """A minimal one-page PDF whose page shows `text` (offsets computed, so pypdf reads it strictly)."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, 1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode() + body + b"\nendobj\n")
    xref = out.tell()
    out.write(f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode())
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return out.getvalue()


class FakeResp:
    def __init__(self, body: bytes, status: int = 200, ctype: str = "application/pdf"):
        self._buf = io.BytesIO(body)
        self.status = status
        self.headers = {"Content-Type": ctype}
        self.closed = False

    def getcode(self):
        return self.status

    def read(self, n=-1):
        return self._buf.read(n)

    def close(self):
        self.closed = True


class FakeOpener:
    """Maps URL -> FakeResp or an exception; records every request and the fake clock time."""

    def __init__(self, routes: dict, clock=None):
        self.routes = routes
        self.requests = []
        self.clock = clock

    def open(self, req, timeout=None):
        self.requests.append((req, self.clock.now if self.clock else None))
        r = self.routes[req.full_url]
        if isinstance(r, Exception):
            raise r
        return r


class FakeClock:
    def __init__(self):
        self.now = 1000.0
        self.slept = []

    def __call__(self):
        return self.now

    def sleep(self, s):
        self.slept.append(s)
        self.now += s


def _items(*keys):
    return [{"key": k, "item": f"Invented item {k}", "slug": f"invented-{k}-pdf", "url": f"{BASE}invented-{k}-pdf"}
            for k in keys]


def _http_error(url, code):
    return urllib.error.HTTPError(url, code, "fake", {"Content-Type": "text/html"}, None)


# ---------------------------------------------------------------- allowlist

@pytest.mark.parametrize("url", [
    "https://www.incometaxindia.gov.in/documents/d/guest/x-pdf",
    "http://wm.incometaxindia.gov.in/documents/d/guest/x-pdf",
    "https://wm.incometaxindia.gov.in.evil.example/documents/d/guest/x-pdf",
    "https://wm.incometaxindia.gov.in:8443/documents/d/guest/x-pdf",
    "https://user@wm.incometaxindia.gov.in/documents/d/guest/x-pdf",
    "https://wm.incometaxindia.gov.in/documents/d/other/x-pdf",
    "https://wm.incometaxindia.gov.in/documents/d/guest/x-pdf?a=1",
    "https://wm.incometaxindia.gov.in/documents/d/guest/x-pdf#f",
    "https://wm.incometaxindia.gov.in/documents/d/guest/a/b",
    "https://wm.incometaxindia.gov.in/documents/d/guest/..",
    "https://example.org/documents/d/guest/x-pdf",
])
def test_check_url_refuses_everything_off_the_allowlist(url):
    with pytest.raises(sf.SourceError):
        sf.check_url(url)


def test_check_url_accepts_base_plus_slug():
    url = BASE + "income-tax-document-invented_2025_en"
    assert sf.check_url(url) == url


def test_real_sources_json_loads_and_is_on_the_allowlist():
    data = sf.load_sources()
    assert len(data["items"]) == 15 <= sf.MAX_REQUESTS
    assert all(it["url"].startswith(BASE) for it in data["items"])
    keys = [it["key"] for it in data["items"] + data["manual"]]
    assert len(keys) == len(set(keys))
    assert {"fa_2022", "fa_2026"} <= {m["key"] for m in data["manual"]}


def _write_sources(tmp_path, **override):
    data = {"schema": 1, "host": sf.ALLOWED_HOST, "base": BASE, "user_agent": sf.USER_AGENT,
            "items": [{"key": "a1", "item": "Invented A", "slug": "invented-a-pdf"}],
            "manual": [{"key": "m1", "item": "Invented M", "where": "invented"}]}
    data.update(override)
    p = tmp_path / "SOURCES.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


@pytest.mark.parametrize("override", [
    {"host": "www.incometaxindia.gov.in"},
    {"user_agent": "Mozilla/5.0"},
    {"items": [{"key": "a1", "item": "A", "slug": "a/../b"}]},
    {"items": [{"key": "a1", "item": "A", "slug": "x"}, {"key": "a1", "item": "B", "slug": "y"}]},
    {"items": [{"key": f"k{i}", "item": "A", "slug": f"s{i}"} for i in range(16)]},
    {"manual": [{"key": "m1", "item": "M", "where": "w", "url": BASE + "x"}]},
])
def test_load_sources_rejects_bad_files(tmp_path, override):
    with pytest.raises(sf.SourceError):
        sf.load_sources(_write_sources(tmp_path, **override))


# ---------------------------------------------------------------- download

def test_download_writes_pdf_hash_and_log(tmp_path):
    body = _pdf_bytes()
    items = _items("a1")
    opener = FakeOpener({items[0]["url"]: FakeResp(body)})
    clock = FakeClock()
    log = sf.download(items, tmp_path, opener=opener, clock=clock, sleep=clock.sleep)
    e = log["entries"][0]
    assert e["outcome"] == "ok" and e["status"] == 200 and e["bytes"] == len(body)
    import hashlib
    assert e["sha256"] == hashlib.sha256(body).hexdigest()
    assert (tmp_path / "a1.pdf").read_bytes() == body
    assert not (tmp_path / "a1.pdf.part").exists()
    saved = json.loads((tmp_path / sf.LOG_NAME).read_text(encoding="utf-8"))
    assert saved["requests"] == 1 and saved["pypdf_version"] and saved["rules"]["retries"] == 0
    assert saved["entries"][0]["started_at"].endswith("+05:30")


def test_download_sends_honest_user_agent_and_no_cookie(tmp_path):
    items = _items("a1")
    opener = FakeOpener({items[0]["url"]: FakeResp(_pdf_bytes())})
    clock = FakeClock()
    sf.download(items, tmp_path, opener=opener, clock=clock, sleep=clock.sleep)
    req = opener.requests[0][0]
    assert req.get_method() == "GET"
    assert req.get_header("User-agent") == "DIVERGENCE-research (github.com/hariom-s27/divergence)"
    assert not req.has_header("Cookie")


def test_download_spaces_requests_at_least_five_seconds(tmp_path):
    items = _items("a1", "a2", "a3")
    clock = FakeClock()
    opener = FakeOpener({it["url"]: FakeResp(_pdf_bytes()) for it in items}, clock=clock)
    sf.download(items, tmp_path, opener=opener, clock=clock, sleep=clock.sleep)
    times = [t for _, t in opener.requests]
    assert len(times) == 3
    assert all(b - a >= sf.MIN_GAP_S for a, b in zip(times, times[1:]))


@pytest.mark.parametrize("code", [403, 429])
def test_refusal_stops_all_downloads_and_still_writes_log(tmp_path, code):
    items = _items("a1", "a2", "a3")
    clock = FakeClock()
    opener = FakeOpener({items[0]["url"]: FakeResp(_pdf_bytes()),
                         items[1]["url"]: _http_error(items[1]["url"], code),
                         items[2]["url"]: FakeResp(_pdf_bytes())})
    with pytest.raises(sf.FetchStop):
        sf.download(items, tmp_path, opener=opener, clock=clock, sleep=clock.sleep)
    assert len(opener.requests) == 2  # a3 never requested
    log = json.loads((tmp_path / sf.LOG_NAME).read_text(encoding="utf-8"))
    assert log["stopped"] and log["entries"][1]["status"] == code
    assert not (tmp_path / "a3.pdf").exists()


def test_no_retry_on_failure(tmp_path):
    items = _items("a1")
    opener = FakeOpener({items[0]["url"]: urllib.error.URLError("fake timeout")})
    clock = FakeClock()
    log = sf.download(items, tmp_path, opener=opener, clock=clock, sleep=clock.sleep)
    assert len(opener.requests) == 1
    assert log["entries"][0]["outcome"] == "manual_needed"
    assert log["entries"][0]["reason"].startswith("no_response")


def test_redirect_is_reported_not_followed(tmp_path):
    items = _items("a1")
    opener = FakeOpener({items[0]["url"]: _http_error(items[0]["url"], 302)})
    clock = FakeClock()
    log = sf.download(items, tmp_path, opener=opener, clock=clock, sleep=clock.sleep)
    assert len(opener.requests) == 1
    assert log["entries"][0]["reason"] == "http_302_redirect_not_followed"
    assert log["entries"][0]["outcome"] == "manual_needed"


def test_real_opener_has_no_redirect_and_no_cookie_handler():
    opener = sf.build_opener()
    kinds = [type(h) for h in opener.handlers]
    assert sf.NoRedirect in kinds
    assert urllib.request.HTTPRedirectHandler not in kinds
    assert urllib.request.HTTPCookieProcessor not in kinds
    req = urllib.request.Request(BASE + "x")
    assert sf.NoRedirect().redirect_request(req, None, 302, "Found", {}, "https://example.org/") is None


def test_html_instead_of_pdf_is_rejected(tmp_path):
    items = _items("a1")
    opener = FakeOpener({items[0]["url"]: FakeResp(b"<html>invented</html>", ctype="text/html")})
    clock = FakeClock()
    log = sf.download(items, tmp_path, opener=opener, clock=clock, sleep=clock.sleep)
    assert log["entries"][0]["reason"] == "not_a_pdf"
    assert not (tmp_path / "a1.pdf").exists() and not (tmp_path / "a1.pdf.part").exists()


def test_refuses_to_overwrite_existing_files(tmp_path):
    items = _items("a1")
    (tmp_path / "a1.pdf").write_bytes(b"existing")
    opener = FakeOpener({items[0]["url"]: FakeResp(_pdf_bytes())})
    with pytest.raises(sf.FetchStop):
        sf.download(items, tmp_path, opener=opener)
    assert opener.requests == []
    assert (tmp_path / "a1.pdf").read_bytes() == b"existing"


def test_cap_of_fifteen_requests(tmp_path):
    items = _items(*[f"k{i}" for i in range(16)])
    opener = FakeOpener({})
    with pytest.raises(sf.FetchStop):
        sf.download(items, tmp_path, opener=opener)
    assert opener.requests == []


def test_off_allowlist_item_is_refused_before_any_request(tmp_path):
    items = _items("a1") + [{"key": "bad", "item": "x", "url": "https://www.incometaxindia.gov.in/documents/d/guest/x"}]
    opener = FakeOpener({})
    with pytest.raises(sf.SourceError):
        sf.download(items, tmp_path, opener=opener)
    assert opener.requests == []


# ---------------------------------------------------------------- offline checks

def _downloaded(tmp_path, keys=("a1",), text="FAKE FIXTURE - NOT LAW"):
    items = _items(*keys)
    clock = FakeClock()
    opener = FakeOpener({it["url"]: FakeResp(_pdf_bytes(text)) for it in items})
    sf.download(items, tmp_path, opener=opener, clock=clock, sleep=clock.sleep)
    return items


def test_verify_ok_then_detects_change(tmp_path):
    _downloaded(tmp_path)
    assert sf.verify(tmp_path) == []
    (tmp_path / "a1.pdf").write_bytes(_pdf_bytes("FAKE FIXTURE - CHANGED"))
    problems = sf.verify(tmp_path)
    assert len(problems) == 1 and "changed" in problems[0]


def test_verify_reports_missing_file_and_missing_log(tmp_path):
    assert sf.verify(tmp_path) and "not found" in sf.verify(tmp_path)[0]
    _downloaded(tmp_path)
    (tmp_path / "a1.pdf").unlink()
    assert sf.verify(tmp_path) == ["a1: file missing"]


def test_compare_logs_reports_changed_same_missing():
    ref = {"entries": [{"key": "a", "outcome": "ok", "sha256": "1" * 64},
                       {"key": "b", "outcome": "ok", "sha256": "2" * 64},
                       {"key": "c", "outcome": "ok", "sha256": "3" * 64}]}
    new = {"entries": [{"key": "a", "outcome": "ok", "sha256": "1" * 64},
                       {"key": "b", "outcome": "ok", "sha256": "9" * 64},
                       {"key": "c", "outcome": "manual_needed", "reason": "http_404"}]}
    lines = sf.compare_logs(ref, new)
    assert lines[0] == "SAME     a"
    assert lines[1].startswith("CHANGED  b")
    assert lines[2].startswith("MISSING  c")


def test_pdf_facts_pages_titles_and_expected_text(tmp_path):
    p = tmp_path / "x.pdf"
    p.write_bytes(_pdf_bytes("FAKE FIXTURE Invented Act, 2099"))
    facts = sf.pdf_facts(p, expect_text="Invented  Act,\n2099")
    assert facts["pages"] == 1 and facts["error"] is None
    assert facts["expect_found"] is True
    assert facts["titles"] and "FAKE FIXTURE" in facts["titles"][0]
    assert sf.pdf_facts(p, expect_text="Invented Act, 2098")["expect_found"] is False


def test_inventory_flags_failed_expect_and_manual_items(tmp_path):
    _downloaded(tmp_path, keys=("fa_x",), text="FAKE FIXTURE Something Else")
    (tmp_path / sf.MANUAL_DIR).mkdir()
    (tmp_path / sf.MANUAL_DIR / "m.pdf").write_bytes(_pdf_bytes())
    sources = {"items": [{"key": "fa_x", "expect_text": "Invented Act, 2099"}],
               "manual": [{"key": "m1", "where": "invented"}]}
    rows, manual = sf.inventory(tmp_path, sources)
    assert [r["key"] for r in rows] == ["fa_x", "manual/m.pdf"]
    assert rows[0]["status"] == 200 and rows[0]["expect_found"] is False
    keys = [k for k, _ in manual]
    assert "fa_x" in keys and "m1" in keys


def test_cli_rejects_unknown_only_key(tmp_path, capsys):
    rc = sf.main(["--download", "--only", "nope", "--dir", str(tmp_path)])
    assert rc == 2 and "unknown keys" in capsys.readouterr().out
    assert not any(Path(tmp_path).iterdir())
