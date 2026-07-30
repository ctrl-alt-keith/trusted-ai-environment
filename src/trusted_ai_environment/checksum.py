"""Checksum helpers for evidence bundle files."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

CHECKSUM_FILE = "checksums.sha256"
CHECKSUMMED_FILES = (
    "README.md",
    "bundle.json",
    "sources.jsonl",
    "items.jsonl",
    "chunks.jsonl",
    "relations.jsonl",
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def byte_len(text: str) -> int:
    return len(text.encode("utf-8"))


def compute_checksums(bundle_dir: Path) -> dict[str, str]:
    return {name: file_sha256(bundle_dir / name) for name in CHECKSUMMED_FILES}


def format_checksums(checksums: dict[str, str]) -> str:
    lines = [f"{checksums[name]}  {name}" for name in CHECKSUMMED_FILES]
    return "\n".join(lines) + "\n"


def write_checksums(bundle_dir: Path) -> None:
    checksums = compute_checksums(bundle_dir)
    (bundle_dir / CHECKSUM_FILE).write_text(format_checksums(checksums), encoding="utf-8")


def read_checksum_file(path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"{path}:{line_number}: expected '<sha256>  <filename>'")
        checksum, filename = parts
        if len(checksum) != 64 or any(char not in "0123456789abcdef" for char in checksum):
            raise ValueError(f"{path}:{line_number}: invalid sha256 digest")
        if filename in checksums:
            raise ValueError(f"{path}:{line_number}: duplicate checksum entry for {filename}")
        checksums[filename] = checksum
    return checksums


def verify_checksums(bundle_dir: Path) -> list[str]:
    expected = read_checksum_file(bundle_dir / CHECKSUM_FILE)
    actual = compute_checksums(bundle_dir)
    errors: list[str] = []
    for filename in CHECKSUMMED_FILES:
        if filename not in expected:
            errors.append(f"checksums.sha256 is missing {filename}")
            continue
        if expected[filename] != actual[filename]:
            errors.append(f"checksum mismatch for {filename}")
    extra = sorted(set(expected) - set(CHECKSUMMED_FILES))
    for filename in extra:
        errors.append(f"checksums.sha256 has unexpected entry {filename}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute bundle checksums.")
    parser.add_argument("bundle_dir", type=Path)
    parser.add_argument("--write", action="store_true", help="write checksums.sha256")
    args = parser.parse_args(argv)

    if args.write:
        write_checksums(args.bundle_dir)
        return 0

    print(format_checksums(compute_checksums(args.bundle_dir)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
