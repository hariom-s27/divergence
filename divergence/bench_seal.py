"""P10a/P10b TEST seal (P10-07): hashes of the local TEST items and nuggets files.

--seal TEST NUGGETS writes <bench>/TEST-SEAL.json (refuses to overwrite);
--check TEST NUGGETS verifies it. Never prints item or nugget content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from divergence.bench_slots import BENCH_DIR, DEFAULT_SPEC, load_spec, spec_sha256

SEAL_VERSION = 1
DEFAULT_SEAL = BENCH_DIR / "TEST-SEAL.json"


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def item_count(path):
    return sum(1 for line in Path(path).read_bytes().split(b"\n") if line.strip())


def seal_record(items, nuggets, spec_path):
    return {"seal_version": SEAL_VERSION, "spec_sha256": spec_sha256(load_spec(spec_path)),
            "items_file": Path(items).name, "items_sha256": file_sha256(items), "item_count": item_count(items),
            "nuggets_file": Path(nuggets).name, "nuggets_sha256": file_sha256(nuggets)}


def seal_bytes(record):
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def check(items, nuggets, spec_path, seal_path):
    stored = json.loads(Path(seal_path).read_text(encoding="utf-8"))
    now = seal_record(items, nuggets, spec_path)
    bad = sorted(k for k in set(stored) | set(now) if stored.get(k) != now.get(k))
    return bad


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--seal", nargs=2, metavar=("TEST", "NUGGETS"), type=Path)
    mode.add_argument("--check", nargs=2, metavar=("TEST", "NUGGETS"), type=Path)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--seal-file", type=Path, default=DEFAULT_SEAL)
    args = parser.parse_args(argv)
    if args.seal:
        if args.seal_file.exists():
            print(f"bench seal: ERROR {args.seal_file.name} exists; refusing to overwrite")
            return 2
        record = seal_record(*args.seal, args.spec)
        args.seal_file.parent.mkdir(parents=True, exist_ok=True)
        with open(args.seal_file, "xb") as stream:
            stream.write(seal_bytes(record))
        print(f"bench seal: sealed {record['item_count']} item(s) items {record['items_sha256'][:16]}"
              f" nuggets {record['nuggets_sha256'][:16]}")
        return 0
    if not args.seal_file.is_file():
        print(f"bench seal: ERROR {args.seal_file.name} missing")
        return 2
    bad = check(*args.check, args.spec, args.seal_file)
    if bad:
        print(f"bench seal: MISMATCH fields {', '.join(bad)}")
        return 1
    print("bench seal: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
