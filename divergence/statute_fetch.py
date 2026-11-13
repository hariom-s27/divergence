"""P09 statute fetcher: download the allowlisted ITD PDFs listed in statutes/SOURCES.json.

Modes (run from the repo root):
    python -m divergence.statute_fetch --download [--only k1,k2]   network: GET each listed URL once
    python -m divergence.statute_fetch --inventory --dir D          offline: bytes, sha256, pages, titles
    python -m divergence.statute_fetch --verify --dir D             offline: re-hash files vs FETCH-LOG.json
    python -m divergence.statute_fetch --rebuild --against D        network: re-download to a new folder, compare

Network rules (P09 standing rules + Part A approval):
- Only https://wm.incometaxindia.gov.in/documents/d/guest/<slug>; any other URL is refused before
  a socket opens. HTTP GET, one request at a time, >= 5 s between request starts.
- Honest user-agent, no cookies, NO retries, NO redirects (a 3xx is reported, never followed).
- Hard cap 15 requests per run. HTTP 403 or 429 stops all remaining downloads.
- Downloads go to the git-ignored statutes/_local_text/_raw/<YYYY-MM-DD>/; nothing is overwritten.
Failures are listed as MANUAL NEEDED for the owner; there is no workaround logic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

IST = timezone(timedelta(hours=5, minutes=30))
ALLOWED_HOST = "wm.incometaxindia.gov.in"
BASE = "https://wm.incometaxindia.gov.in/documents/d/guest/"
BASE_PATH = "/documents/d/guest/"
USER_AGENT = "DIVERGENCE-research (github.com/hariom-s27/divergence)"
MIN_GAP_S = 5.0
MAX_REQUESTS = 15
STOP_STATUSES = (403, 429)
TIMEOUT_S = 120
CHUNK = 1 << 20
PDF_MAGIC = b"%PDF-"
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._\-]*$")
KEY_RE = re.compile(r"^[a-z0-9_]+$")

PACKAGE_DIR = Path(__file__).resolve().parent
STATUTES_DIR = PACKAGE_DIR / "statutes"
SOURCES_PATH = STATUTES_DIR / "SOURCES.json"
RAW_DIR = STATUTES_DIR / "_local_text" / "_raw"
LOG_NAME = "FETCH-LOG.json"
MANUAL_DIR = "manual"


class SourceError(ValueError):
    """SOURCES.json or a URL breaks the allowlist rules."""


class FetchStop(RuntimeError):
    """A refusal (HTTP 403/429) or a broken run rule: stop all downloads."""


# ---------------------------------------------------------------- allowlist

def check_url(url: str) -> str:
    """Return url unchanged if it is exactly BASE + one safe slug; raise SourceError otherwise."""
    if not isinstance(url, str):
        raise SourceError(f"url must be a string: {url!r}")
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise SourceError(f"scheme must be https: {url}")
    if parts.username or parts.password or parts.port is not None:
        raise SourceError(f"no userinfo or port allowed: {url}")
    if parts.hostname != ALLOWED_HOST or parts.netloc != ALLOWED_HOST:
        raise SourceError(f"host not allowed (only {ALLOWED_HOST}): {url}")
    if parts.query or parts.fragment:
        raise SourceError(f"no query or fragment allowed: {url}")
    if not parts.path.startswith(BASE_PATH):
        raise SourceError(f"path must start with {BASE_PATH}: {url}")
    slug = parts.path[len(BASE_PATH):]
    if not SLUG_RE.match(slug) or ".." in slug:
        raise SourceError(f"bad slug: {url}")
    if url != BASE + slug:
        raise SourceError(f"url is not base + slug: {url}")
    return url


def load_sources(path: Path = SOURCES_PATH) -> dict:
    """Read SOURCES.json and check every rule; return the parsed dict with 'url' added per item."""
    data = json.loads(Path(path).read_bytes().decode("utf-8"))
    if data.get("schema") != 1:
        raise SourceError("SOURCES.json: schema must be 1")
    if data.get("host") != ALLOWED_HOST or data.get("base") != BASE or data.get("user_agent") != USER_AGENT:
        raise SourceError("SOURCES.json: host/base/user_agent differ from the code constants")
    items = data.get("items")
    manual = data.get("manual", [])
    if not isinstance(items, list) or not isinstance(manual, list):
        raise SourceError("SOURCES.json: items and manual must be lists")
    if len(items) > MAX_REQUESTS:
        raise SourceError(f"SOURCES.json: {len(items)} items exceed the {MAX_REQUESTS}-request cap")
    seen = set()
    for it in items + manual:
        key = it.get("key")
        if not isinstance(key, str) or not KEY_RE.match(key):
            raise SourceError(f"SOURCES.json: bad key {key!r}")
        if key in seen:
            raise SourceError(f"SOURCES.json: duplicate key {key}")
        seen.add(key)
        if not isinstance(it.get("item"), str) or not it["item"].strip():
            raise SourceError(f"SOURCES.json: {key} needs an item title")
    for it in items:
        it["url"] = check_url(BASE + str(it.get("slug", "")))
    for it in manual:
        if "slug" in it or "url" in it:
            raise SourceError(f"SOURCES.json: manual item {it['key']} must not carry a slug or url")
    return data


# ---------------------------------------------------------------- HTTP layer

class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect: urllib then raises HTTPError with the 3xx code."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


def build_opener():
    """Opener with no redirect following and no cookie processor."""
    return urllib.request.build_opener(NoRedirect())


def now_ist() -> str:
    return datetime.now(IST).isoformat(timespec="seconds")


def pypdf_version() -> str:
    try:
        import pypdf
        return str(pypdf.__version__)
    except Exception as e:  # pragma: no cover - reported, not hidden
        return f"unavailable ({type(e).__name__})"


def _fetch_one(item: dict, out_dir: Path, opener) -> dict:
    """One GET, no retry. Returns a log entry. Raises FetchStop on 403/429 (after filling the entry)."""
    url = check_url(item["url"])
    target = out_dir / f"{item['key']}.pdf"
    part = out_dir / f"{item['key']}.pdf.part"
    entry = {"key": item["key"], "url": url, "status": None, "bytes": None, "sha256": None,
             "content_type": None, "started_at": now_ist(), "finished_at": None,
             "outcome": "manual_needed", "reason": None}
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    resp = None
    try:
        resp = opener.open(req, timeout=TIMEOUT_S)
        entry["status"] = int(getattr(resp, "status", None) or resp.getcode())
        entry["content_type"] = resp.headers.get("Content-Type")
        if entry["status"] != 200:
            entry["reason"] = f"http_{entry['status']}"
            return entry
        h = hashlib.sha256()
        n = 0
        head = b""
        with open(part, "xb") as f:
            while True:
                chunk = resp.read(CHUNK)
                if not chunk:
                    break
                if len(head) < len(PDF_MAGIC):
                    head = (head + chunk)[:len(PDF_MAGIC)]
                h.update(chunk)
                n += len(chunk)
                f.write(chunk)
        entry["bytes"], entry["sha256"] = n, h.hexdigest()
        if head != PDF_MAGIC:
            part.unlink()
            entry["reason"] = "not_a_pdf"
            return entry
        os.rename(part, target)  # fails if target exists: never overwrite
        entry["outcome"], entry["reason"] = "ok", None
        return entry
    except urllib.error.HTTPError as e:
        entry["status"] = int(e.code)
        entry["content_type"] = e.headers.get("Content-Type") if e.headers else None
        entry["reason"] = f"http_{e.code}" + ("_redirect_not_followed" if 300 <= e.code < 400 else "")
        if e.code in STOP_STATUSES:
            entry["finished_at"] = now_ist()
            raise FetchStop(f"HTTP {e.code} for {item['key']}: all downloads stopped") from None
        return entry
    except (urllib.error.URLError, OSError) as e:
        entry["reason"] = f"no_response: {type(e).__name__}: {e}"
        if part.exists():
            part.unlink()
        return entry
    finally:
        if entry["finished_at"] is None:
            entry["finished_at"] = now_ist()
        if resp is not None:
            try:
                resp.close()
            except Exception:
                pass


def download(items: list, out_dir: Path, opener=None, clock=time.monotonic, sleep=time.sleep) -> dict:
    """GET each item once, in order, >= MIN_GAP_S apart. Writes out_dir/FETCH-LOG.json (never overwrites).

    Returns the log dict. A FetchStop is re-raised after the log is written.
    """
    if len(items) > MAX_REQUESTS:
        raise FetchStop(f"{len(items)} items exceed the {MAX_REQUESTS}-request cap")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / LOG_NAME
    clashes = [p.name for p in [log_path] + [out_dir / f"{it['key']}.pdf" for it in items]
               + [out_dir / f"{it['key']}.pdf.part" for it in items] if p.exists()]
    if clashes:
        raise FetchStop(f"refusing to overwrite existing files in {out_dir}: {clashes}")
    for it in items:
        check_url(it["url"])
    opener = opener or build_opener()
    log = {"schema": 1, "tool": "divergence.statute_fetch", "pypdf_version": pypdf_version(),
           "python_version": sys.version.split()[0], "user_agent": USER_AGENT,
           "rules": {"min_gap_s": MIN_GAP_S, "max_requests": MAX_REQUESTS, "retries": 0, "redirects": "not_followed"},
           "started_at": now_ist(), "finished_at": None, "requests": 0, "stopped": None, "entries": []}
    last_start = None
    try:
        for it in items:
            if last_start is not None:
                wait = MIN_GAP_S - (clock() - last_start)
                if wait > 0:
                    sleep(wait)
            if log["requests"] >= MAX_REQUESTS:
                raise FetchStop("request cap reached")
            last_start = clock()
            log["requests"] += 1
            try:
                entry = _fetch_one(it, out_dir, opener)
            except FetchStop as stop:
                log["entries"].append(_stop_entry(it, stop))
                raise
            log["entries"].append(entry)
            print(f"  {entry['key']:<16} status={entry['status']} bytes={entry['bytes']} {entry['outcome']}"
                  + (f" ({entry['reason']})" if entry["reason"] else ""), flush=True)
    except FetchStop as stop:
        log["stopped"] = str(stop)
        raise
    finally:
        log["finished_at"] = now_ist()
        with open(log_path, "x", encoding="utf-8", newline="\n") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return log


def _stop_entry(item: dict, stop: FetchStop) -> dict:
    code = re.search(r"HTTP (\d+)", str(stop))
    return {"key": item["key"], "url": item["url"], "status": int(code.group(1)) if code else None,
            "bytes": None, "sha256": None, "content_type": None, "started_at": None,
            "finished_at": now_ist(), "outcome": "manual_needed", "reason": str(stop)}


# ---------------------------------------------------------------- offline checks

def file_sha256(path: Path) -> tuple:
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            h.update(chunk)
            n += len(chunk)
    return n, h.hexdigest()


def collapse_ws(text: str) -> str:
    return " ".join(text.split())


def pdf_facts(path: Path, expect_text: str | None = None, title_lines: int = 3) -> dict:
    """Page count, first-page title lines, and (optionally) whether expect_text is on pages 1-3."""
    out = {"pages": None, "titles": [], "expect_found": None, "error": None}
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        out["pages"] = len(reader.pages)
        first = (reader.pages[0].extract_text() or "") if out["pages"] else ""
        out["titles"] = [ln.strip()[:90] for ln in first.splitlines() if ln.strip()][:title_lines]
        if expect_text is not None:
            text = " ".join((reader.pages[i].extract_text() or "") for i in range(min(3, out["pages"])))
            out["expect_found"] = collapse_ws(expect_text) in collapse_ws(text)
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def read_log(folder: Path) -> dict | None:
    p = Path(folder) / LOG_NAME
    if not p.exists():
        return None
    return json.loads(p.read_bytes().decode("utf-8"))


def inventory(folder: Path, sources: dict) -> tuple:
    """Return (rows, manual_needed). One row per PDF in folder and folder/manual."""
    folder = Path(folder)
    log = read_log(folder) or {"entries": []}
    by_key = {e["key"]: e for e in log.get("entries", [])}
    expect = {it["key"]: it.get("expect_text") for it in sources["items"]}
    rows, manual_needed = [], []
    for e in log.get("entries", []):
        if e.get("outcome") != "ok":
            manual_needed.append((e["key"], e.get("reason") or "failed"))
    pdfs = sorted(folder.glob("*.pdf")) + sorted((folder / MANUAL_DIR).glob("*.pdf"))
    for p in pdfs:
        key = p.stem if p.parent == folder else f"{MANUAL_DIR}/{p.name}"
        n, sha = file_sha256(p)
        with open(p, "rb") as f:
            magic = f.read(len(PDF_MAGIC)) == PDF_MAGIC
        facts = pdf_facts(p, expect.get(key))
        e = by_key.get(key, {})
        rows.append({"key": key, "status": e.get("status"), "bytes": n, "sha256": sha,
                     "content_type": e.get("content_type"), "pages": facts["pages"], "pdf_magic": magic,
                     "expect_found": facts["expect_found"], "titles": facts["titles"], "error": facts["error"]})
        if facts["error"]:
            manual_needed.append((key, f"pdf_unreadable: {facts['error']}"))
        if facts["expect_found"] is False:
            manual_needed.append((key, f"expected text {expect.get(key)!r} not on pages 1-3"))
        if not magic:
            manual_needed.append((key, "not_a_pdf"))
    for it in sources.get("manual", []):
        manual_needed.append((it["key"], f"manual item: {it['where']}"))
    return rows, manual_needed


def verify(folder: Path) -> list:
    """Re-hash every 'ok' file in FETCH-LOG.json; return a list of problems (empty = OK)."""
    folder = Path(folder)
    log = read_log(folder)
    if log is None:
        return [f"{LOG_NAME} not found in {folder}"]
    problems = []
    for e in log.get("entries", []):
        if e.get("outcome") != "ok":
            continue
        p = folder / f"{e['key']}.pdf"
        if not p.exists():
            problems.append(f"{e['key']}: file missing")
            continue
        n, sha = file_sha256(p)
        if n != e["bytes"] or sha != e["sha256"]:
            problems.append(f"{e['key']}: changed (bytes {e['bytes']} -> {n}, sha256 {e['sha256']} -> {sha})")
    return problems


def compare_logs(reference: dict, fresh: dict) -> list:
    """Rebuild comparison: one line per key; nothing is accepted silently."""
    ref = {e["key"]: e for e in reference.get("entries", []) if e.get("outcome") == "ok"}
    new = {e["key"]: e for e in fresh.get("entries", [])}
    lines = []
    for key in sorted(set(ref) | set(new)):
        a, b = ref.get(key), new.get(key)
        if a is None:
            lines.append(f"NEW      {key}: not in reference")
        elif b is None or b.get("outcome") != "ok":
            lines.append(f"MISSING  {key}: {(b or {}).get('reason', 'not downloaded')}")
        elif a["sha256"] != b["sha256"]:
            lines.append(f"CHANGED  {key}: sha256 {a['sha256']} -> {b['sha256']}")
        else:
            lines.append(f"SAME     {key}")
    return lines


# ---------------------------------------------------------------- CLI

def _print_inventory(folder: Path, rows: list, manual_needed: list) -> None:
    print(f"INVENTORY  folder={folder}")
    print(f"pypdf {pypdf_version()}  python {sys.version.split()[0]}  files={len(rows)}")
    hdr = f"{'key':<34} {'http':>4} {'bytes':>11} {'sha256':<64} {'content_type':<24} {'pages':>5} magic check"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        check = {True: "found", False: "MISSING", None: "-"}[r["expect_found"]]
        print(f"{r['key']:<34} {str(r['status'] or '-'):>4} {r['bytes']:>11} {r['sha256']:<64} "
              f"{str(r['content_type'] or '-')[:24]:<24} {str(r['pages'] if r['pages'] is not None else 'ERR'):>5} "
              f"{'yes' if r['pdf_magic'] else 'NO':<5} {check}")
    print()
    print("FIRST-PAGE TITLE LINES (screen only, not written to any file)")
    for r in rows:
        print(f"  {r['key']}: " + " | ".join(r["titles"]) if r["titles"] else f"  {r['key']}: (no text)")
    print()
    print(f"MANUAL NEEDED ({len(manual_needed)})")
    for key, why in manual_needed:
        print(f"  MANUAL NEEDED  {key}: {why}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m divergence.statute_fetch", description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--download", action="store_true", help="network: GET every SOURCES.json item once")
    mode.add_argument("--inventory", action="store_true", help="offline: list files in --dir")
    mode.add_argument("--verify", action="store_true", help="offline: re-hash files in --dir vs FETCH-LOG.json")
    mode.add_argument("--rebuild", action="store_true", help="network: re-download, compare with --against")
    ap.add_argument("--dir", help="download folder (default: _raw/<today IST>)")
    ap.add_argument("--only", help="comma-separated keys (download/rebuild)")
    ap.add_argument("--against", help="reference folder for --rebuild")
    ap.add_argument("--sources", default=str(SOURCES_PATH))
    args = ap.parse_args(argv)
    try:
        sources = load_sources(Path(args.sources))
    except (SourceError, ValueError, OSError) as e:
        print(f"ERROR sources: {e}")
        return 2
    today = datetime.now(IST).date().isoformat()
    folder = Path(args.dir) if args.dir else RAW_DIR / today

    if args.inventory:
        rows, manual_needed = inventory(folder, sources)
        _print_inventory(folder, rows, manual_needed)
        return 0
    if args.verify:
        problems = verify(folder)
        for p in problems:
            print(f"VERIFY FAIL  {p}")
        print("VERIFY OK" if not problems else f"VERIFY: {len(problems)} problem(s)")
        return 0 if not problems else 1

    items = sources["items"]
    if args.only:
        wanted = [k.strip() for k in args.only.split(",") if k.strip()]
        unknown = sorted(set(wanted) - {it["key"] for it in items})
        if unknown:
            print(f"ERROR unknown keys: {unknown}")
            return 2
        items = [it for it in items if it["key"] in wanted]
    if args.rebuild:
        if not args.against:
            print("ERROR --rebuild needs --against <reference folder>")
            return 2
        reference = read_log(Path(args.against))
        if reference is None:
            print(f"ERROR no {LOG_NAME} in {args.against}")
            return 2
        stamp = datetime.now(IST).strftime("%Y-%m-%d-rebuild-%H%M%S")
        folder = Path(args.dir) if args.dir else RAW_DIR / stamp
    print(f"DOWNLOAD  {len(items)} item(s) -> {folder}  pypdf {pypdf_version()}")
    try:
        log = download(items, folder)
    except FetchStop as stop:
        print(f"STOPPED: {stop}")
        return 3
    print(f"requests={log['requests']}  ok={sum(e['outcome'] == 'ok' for e in log['entries'])}  log={folder / LOG_NAME}")
    if args.rebuild:
        lines = compare_logs(reference, log)
        for ln in lines:
            print(ln)
        return 0 if all(ln.startswith("SAME") for ln in lines) else 1
    return 0 if all(e["outcome"] == "ok" for e in log["entries"]) else 1


if __name__ == "__main__":
    sys.exit(main())
