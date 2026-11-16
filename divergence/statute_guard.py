"""Deterministic C3-fix guards. --body computes in memory; it never writes build sheets."""
import argparse
import hashlib

from divergence import act_parse as ap
from divergence import statute_build as sb
from divergence import statute_extract as se

CODE_SHA256 = "b7b8fa369ef009d2a32fa77452ee3b5b2e767a5a360d405fa3af17c182c71ab7"
BODY_SHA256 = "aebe8deb174f8c1a7f13058d1b2200c0b4c910e826508f055bf587f18be97a4d"


def code_sha(rows):
    columns = [c for c in sb.VERSION_COLUMNS if c not in sb.VERSION_OWNER]
    text = ap.csv_text(sorted(rows, key=lambda r: r["record_key"]), columns)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def body_sha(hashes):
    """Exact historical guard_b.py serialization (not a new JSON serialization)."""
    return hashlib.sha256(repr(sorted(hashes.items())).encode("utf-8")).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--code", action="store_true")
    group.add_argument("--body", action="store_true")
    args = parser.parse_args(argv)
    if args.code:
        rows = ap.read_csv(sb.VERSIONS_PATH)
        actual, expected, count = code_sha(rows), CODE_SHA256, len(rows)
        label = "code"
    else:
        raw = se.latest_raw_dir()
        print(f"statute_guard --body raw folder: {raw}")
        result = sb.build(raw, se.STATUTES_DIR / "_local_text" / "scratch" / "C4-body-no-write", write=False)
        actual, expected, count = body_sha(result["body_sha"]), BODY_SHA256, len(result["body_sha"])
        label = "body"
    print(f"statute_guard --{label}: {count} {'rows' if args.code else 'bodies'} sha256 {actual} "
          f"{'PASS' if actual == expected else 'FAIL'}")
    return 0 if actual == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
