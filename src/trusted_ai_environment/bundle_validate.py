"""Validate the Stage 1 evidence bundle contract."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .checksum import CHECKSUMMED_FILES, verify_checksums

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "schemas"
REQUIRED_FILES = (*CHECKSUMMED_FILES, "checksums.sha256")
JSONL_FILES = {
    "sources.jsonl": "source.schema.json",
    "items.jsonl": "item.schema.json",
    "chunks.jsonl": "chunk.schema.json",
    "relations.jsonl": "relation.schema.json",
}
PRIVATE_URL_PATTERN = re.compile(
    r"https?://[^\s)\"']*(localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|internal|intranet|corp)",
    re.IGNORECASE,
)
SUSPICIOUS_MARKERS = (
    "real ticket",
    "real incident",
    "production incident",
    "customer data",
    "do not distribute",
    "confidential",
    "secret=",
    "token=",
    "password=",
)


class ValidationError(Exception):
    """Raised for bundle validation errors."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            row = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path}:{line_number}: invalid JSONL row: {exc}") from exc
        if not isinstance(row, dict):
            raise ValidationError(f"{path}:{line_number}: JSONL row must be an object")
        rows.append(row)
    return rows


def schema_type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__


def check_type(value: Any, expected: str | list[str]) -> bool:
    actual = schema_type_name(value)
    if isinstance(expected, list):
        return any(check_type(value, item) for item in expected)
    if expected == "number":
        return actual in {"integer", "number"}
    return actual == expected


def validate_schema(schema: dict[str, Any], value: Any, path: str) -> list[str]:
    errors: list[str] = []

    expected_type = schema.get("type")
    if expected_type and not check_type(value, expected_type):
        return [f"{path}: expected {expected_type}, got {schema_type_name(value)}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(value) < min_length:
            errors.append(f"{path}: must have length at least {min_length}")
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, value):
            errors.append(f"{path}: does not match pattern {pattern!r}")
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}: invalid date-time")

    if isinstance(value, int) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path}: must be >= {schema['minimum']}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}.{key}: missing required property")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            for key in extra:
                errors.append(f"{path}.{key}: unexpected property")

        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate_schema(child_schema, value[key], f"{path}.{key}"))

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            errors.extend(validate_schema(schema["items"], item, f"{path}[{index}]"))

    return errors


def validate_with_schema(schema_name: str, value: Any, label: str) -> list[str]:
    schema = load_json(SCHEMA_DIR / schema_name)
    if not isinstance(schema, dict):
        raise ValidationError(f"{schema_name}: schema must be an object")
    return validate_schema(schema, value, label)


def require_files(bundle_dir: Path) -> list[str]:
    errors: list[str] = []
    for filename in REQUIRED_FILES:
        path = bundle_dir / filename
        if not path.exists():
            errors.append(f"missing required file: {filename}")
        elif not path.is_file():
            errors.append(f"required path is not a file: {filename}")
    return errors


def find_duplicate_ids(rows: list[dict[str, Any]], key: str, label: str) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str):
            continue
        if value in seen:
            duplicates.append(f"{label}: duplicate {key}: {value}")
        seen.add(value)
    return duplicates


def validate_bundle_metadata(
    bundle: dict[str, Any],
    sources: list[dict[str, Any]],
    items: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    contents = bundle.get("contents", {})
    if isinstance(contents, dict):
        expected_counts = {
            "source_count": len(sources),
            "item_count": len(items),
            "chunk_count": len(chunks),
            "relation_count": len(relations),
        }
        for key, expected in expected_counts.items():
            if contents.get(key) != expected:
                errors.append(f"bundle.contents.{key} must be {expected}")

    files = bundle.get("files", {})
    if isinstance(files, dict):
        expected_files = {
            "sources": "sources.jsonl",
            "items": "items.jsonl",
            "chunks": "chunks.jsonl",
            "relations": "relations.jsonl",
            "checksums": "checksums.sha256",
        }
        for key, expected in expected_files.items():
            if files.get(key) != expected:
                errors.append(f"bundle.files.{key} must be {expected}")

    return errors


def endpoint_errors(
    relation_id: str,
    endpoint_name: str,
    endpoint: Any,
    ids_by_type: dict[str, set[str]],
) -> list[str]:
    if not isinstance(endpoint, dict):
        return [f"{relation_id}: {endpoint_name} endpoint must be an object"]
    endpoint_type = endpoint.get("type")
    endpoint_id = endpoint.get("id")
    if endpoint_type not in ids_by_type:
        return [f"{relation_id}: {endpoint_name}.type is invalid: {endpoint_type!r}"]
    if endpoint_id not in ids_by_type[endpoint_type]:
        return [f"{relation_id}: {endpoint_name}.id does not exist: {endpoint_id}"]
    return []


def validate_references(
    bundle: dict[str, Any],
    sources: list[dict[str, Any]],
    items: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    errors.extend(find_duplicate_ids(sources, "source_id", "sources.jsonl"))
    errors.extend(find_duplicate_ids(items, "item_id", "items.jsonl"))
    errors.extend(find_duplicate_ids(chunks, "chunk_id", "chunks.jsonl"))
    errors.extend(find_duplicate_ids(relations, "relation_id", "relations.jsonl"))

    source_ids = {row["source_id"] for row in sources if isinstance(row.get("source_id"), str)}
    item_ids = {row["item_id"] for row in items if isinstance(row.get("item_id"), str)}
    chunk_ids = {row["chunk_id"] for row in chunks if isinstance(row.get("chunk_id"), str)}
    items_by_id = {
        row["item_id"]: row for row in items if isinstance(row.get("item_id"), str)
    }
    ids_by_type = {"source": source_ids, "item": item_ids, "chunk": chunk_ids}
    bundle_id = bundle.get("bundle_id")

    for row in items:
        item_id = row.get("item_id", "<unknown item>")
        source_id = row.get("source_id")
        if source_id not in source_ids:
            errors.append(f"{item_id}: source_id does not exist: {source_id}")
        if "sensitivity" not in row:
            errors.append(f"{item_id}: missing sensitivity")

    for row in chunks:
        chunk_id = row.get("chunk_id", "<unknown chunk>")
        item_id = row.get("item_id")
        source_id = row.get("source_id")
        if row.get("bundle_id") != bundle_id:
            errors.append(f"{chunk_id}: bundle_id must match bundle.bundle_id")
        if item_id not in item_ids:
            errors.append(f"{chunk_id}: item_id does not exist: {item_id}")
        if source_id not in source_ids:
            errors.append(f"{chunk_id}: source_id does not exist: {source_id}")
        parent_item = items_by_id.get(item_id)
        if parent_item and source_id != parent_item.get("source_id"):
            errors.append(f"{chunk_id}: source_id must match parent item.source_id")
        if "sensitivity" not in row:
            errors.append(f"{chunk_id}: missing sensitivity")

    for row in relations:
        relation_id = row.get("relation_id", "<unknown relation>")
        errors.extend(endpoint_errors(relation_id, "from", row.get("from"), ids_by_type))
        errors.extend(endpoint_errors(relation_id, "to", row.get("to"), ids_by_type))
        errors.extend(endpoint_errors(relation_id, "observed_in", row.get("observed_in"), ids_by_type))

    return errors


def scan_public_safety(bundle_dir: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(bundle_dir.iterdir()):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if PRIVATE_URL_PATTERN.search(text):
            errors.append(f"{path.name}: contains an internal-looking URL")
        lower = text.lower()
        for marker in SUSPICIOUS_MARKERS:
            if marker in lower:
                errors.append(f"{path.name}: contains suspicious marker {marker!r}")
    return errors


def validate_bundle(bundle_dir: Path) -> list[str]:
    errors = require_files(bundle_dir)
    if errors:
        return errors

    bundle = load_json(bundle_dir / "bundle.json")
    errors.extend(validate_with_schema("bundle.schema.json", bundle, "bundle.json"))

    rows_by_file: dict[str, list[dict[str, Any]]] = {}
    for filename, schema_name in JSONL_FILES.items():
        rows = load_jsonl(bundle_dir / filename)
        rows_by_file[filename] = rows
        for index, row in enumerate(rows, 1):
            errors.extend(validate_with_schema(schema_name, row, f"{filename}:{index}"))

    errors.extend(
        validate_bundle_metadata(
            bundle,
            rows_by_file["sources.jsonl"],
            rows_by_file["items.jsonl"],
            rows_by_file["chunks.jsonl"],
            rows_by_file["relations.jsonl"],
        )
    )
    errors.extend(
        validate_references(
            bundle,
            rows_by_file["sources.jsonl"],
            rows_by_file["items.jsonl"],
            rows_by_file["chunks.jsonl"],
            rows_by_file["relations.jsonl"],
        )
    )
    errors.extend(verify_checksums(bundle_dir))
    errors.extend(scan_public_safety(bundle_dir))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an evidence bundle.")
    parser.add_argument("bundle_dir", type=Path)
    args = parser.parse_args(argv)

    try:
        errors = validate_bundle(args.bundle_dir)
    except (OSError, ValidationError, ValueError) as exc:
        print(f"bundle validation failed: {exc}")
        return 1

    if errors:
        print("bundle validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"bundle validation passed: {args.bundle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
