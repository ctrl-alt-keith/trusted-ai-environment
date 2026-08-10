from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from trusted_ai_environment.bundle_validate import (
    ValidationError,
    load_json as load_bundle_json,
    load_jsonl as load_bundle_jsonl,
    validate_bundle,
)
from trusted_ai_environment.checksum import byte_len, sha256_text, write_checksums
from trusted_ai_environment.fake_bundle import create_fake_bundle
from trusted_ai_environment.synthesize_stub import build_report


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


class BundleValidationTests(unittest.TestCase):
    def test_text_checksum_helpers_use_utf8_bytes(self) -> None:
        self.assertEqual(byte_len("café"), 5)
        self.assertEqual(
            sha256_text("café"),
            "850f7dc43910ff890f8879c0ed26fe697c93a067ad93a7d50f466a7028a9bf4e",
        )

    def test_fake_bundle_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            self.assertEqual(validate_bundle(bundle_dir), [])

    def test_missing_bundle_directory_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "missing-bundle"
            self.assertEqual(
                validate_bundle(bundle_dir),
                [f"bundle directory does not exist: {bundle_dir}"],
            )

    def test_count_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            bundle = load_json(bundle_dir / "bundle.json")
            bundle["contents"]["chunk_count"] = 99
            write_json(bundle_dir / "bundle.json", bundle)
            write_checksums(bundle_dir)
            errors = validate_bundle(bundle_dir)
            self.assertIn("bundle.contents.chunk_count must be 6", errors)

    def test_non_object_bundle_metadata_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            write_json(bundle_dir / "bundle.json", [])
            write_checksums(bundle_dir)

            errors = validate_bundle(bundle_dir)

        self.assertEqual(errors, ["bundle.json: expected object, got array"])

    def test_naive_bundle_timestamp_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            bundle = load_json(bundle_dir / "bundle.json")
            bundle["created_at"] = "2026-01-15T12:00:00"
            write_json(bundle_dir / "bundle.json", bundle)
            write_checksums(bundle_dir)

            errors = validate_bundle(bundle_dir)

        self.assertIn("bundle.json.created_at: date-time must include a timezone", errors)

    def test_invalid_jsonl_after_blank_line_reports_physical_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.jsonl"
            path.write_text('\n{"item_id":\n', encoding="utf-8")

            with self.assertRaisesRegex(
                ValidationError,
                rf"^{re.escape(str(path))}:2: invalid JSONL row:",
            ):
                load_bundle_jsonl(path)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "bundle.json"
            metadata_path.write_text('{"bundle_id":"first","bundle_id":"second"}', encoding="utf-8")
            rows_path = Path(tmp) / "items.jsonl"
            rows_path.write_text('{"item_id":"first","item_id":"second"}\n', encoding="utf-8")

            with self.assertRaisesRegex(ValidationError, "duplicate object key: bundle_id"):
                load_bundle_json(metadata_path)
            with self.assertRaisesRegex(ValidationError, "duplicate object key: item_id"):
                load_bundle_jsonl(rows_path)

    def test_chunk_bundle_id_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            chunks = load_jsonl(bundle_dir / "chunks.jsonl")
            chunks[0]["bundle_id"] = "wrong-bundle"
            write_jsonl(bundle_dir / "chunks.jsonl", chunks)
            write_checksums(bundle_dir)
            errors = validate_bundle(bundle_dir)
            self.assertTrue(any("bundle_id must match bundle.bundle_id" in error for error in errors))

    def test_chunk_source_item_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            chunks = load_jsonl(bundle_dir / "chunks.jsonl")
            chunks[0]["source_id"] = "src-recovery-guide"
            write_jsonl(bundle_dir / "chunks.jsonl", chunks)
            write_checksums(bundle_dir)
            errors = validate_bundle(bundle_dir)
            self.assertTrue(
                any("source_id must match parent item.source_id" in error for error in errors)
            )

    def test_item_source_system_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            items = load_jsonl(bundle_dir / "items.jsonl")
            items[0]["source_ref"]["system"] = "different-synthetic-system"
            write_jsonl(bundle_dir / "items.jsonl", items)
            write_checksums(bundle_dir)

            errors = validate_bundle(bundle_dir)

        self.assertIn(
            "item-stale-runbook: source_ref.system must match parent source.system",
            errors,
        )

    def test_item_content_ref_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            items = load_jsonl(bundle_dir / "items.jsonl")
            items[0]["body"] = f"{items[0]['body']} Extra synthetic sentence."
            write_jsonl(bundle_dir / "items.jsonl", items)
            write_checksums(bundle_dir)
            errors = validate_bundle(bundle_dir)
            self.assertIn("item-stale-runbook: content_ref.sha256 must match body", errors)
            self.assertIn(
                "item-stale-runbook: content_ref.size_bytes must match body byte length",
                errors,
            )

    def test_chunk_hash_and_span_mismatch_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            chunks = load_jsonl(bundle_dir / "chunks.jsonl")
            chunks[0]["text"] = f"{chunks[0]['text']} Extra synthetic sentence."
            write_jsonl(bundle_dir / "chunks.jsonl", chunks)
            write_checksums(bundle_dir)
            errors = validate_bundle(bundle_dir)
            self.assertIn("chunk-stale-runbook-0: chunk_sha256 must match text", errors)
            self.assertIn(
                "chunk-stale-runbook-0: text must match parent item body char span",
                errors,
            )

    def test_missing_nested_relation_endpoint_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            relations = load_jsonl(bundle_dir / "relations.jsonl")
            relations[0]["from"]["id"] = "item-missing-reference"
            write_jsonl(bundle_dir / "relations.jsonl", relations)
            write_checksums(bundle_dir)
            errors = validate_bundle(bundle_dir)
            self.assertTrue(any("from.id does not exist" in error for error in errors))

    def test_duplicate_record_ids_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            duplicate_cases = [
                ("sources.jsonl", "source_id", "source_count", "sources.jsonl: duplicate source_id"),
                ("items.jsonl", "item_id", "item_count", "items.jsonl: duplicate item_id"),
                ("chunks.jsonl", "chunk_id", "chunk_count", "chunks.jsonl: duplicate chunk_id"),
                (
                    "relations.jsonl",
                    "relation_id",
                    "relation_count",
                    "relations.jsonl: duplicate relation_id",
                ),
            ]
            bundle = load_json(bundle_dir / "bundle.json")
            contents = bundle["contents"]
            assert isinstance(contents, dict)
            for filename, _key, count_key, _expected_prefix in duplicate_cases:
                rows = load_jsonl(bundle_dir / filename)
                rows.append(dict(rows[0]))
                write_jsonl(bundle_dir / filename, rows)
                contents[count_key] = len(rows)
            write_json(bundle_dir / "bundle.json", bundle)
            write_checksums(bundle_dir)

            errors = validate_bundle(bundle_dir)

            for filename, key, _count_key, expected_prefix in duplicate_cases:
                rows = load_jsonl(bundle_dir / filename)
                self.assertIn(f"{expected_prefix}: {rows[0][key]}", errors)

    def test_checksum_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            with (bundle_dir / "items.jsonl").open("a", encoding="utf-8") as handle:
                handle.write("\n")
            errors = validate_bundle(bundle_dir)
            self.assertIn("checksum mismatch for items.jsonl", errors)

    def test_duplicate_checksum_entries_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            checksum_path = bundle_dir / "checksums.sha256"
            first_entry = checksum_path.read_text(encoding="utf-8").splitlines()[0]
            with checksum_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{first_entry}\n")

            with self.assertRaisesRegex(ValueError, "duplicate checksum entry for README.md"):
                validate_bundle(bundle_dir)

    def test_missing_checksum_entry_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            checksum_path = bundle_dir / "checksums.sha256"
            lines = checksum_path.read_text(encoding="utf-8").splitlines()
            checksum_path.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")

            errors = validate_bundle(bundle_dir)

        self.assertIn("checksums.sha256 is missing README.md", errors)

    def test_unexpected_checksum_entry_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            checksum_path = bundle_dir / "checksums.sha256"
            with checksum_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{'0' * 64}  notes.md\n")

            errors = validate_bundle(bundle_dir)

        self.assertIn("checksums.sha256 has unexpected entry notes.md", errors)

    def test_missing_reference_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            text = (bundle_dir / "chunks.jsonl").read_text(encoding="utf-8")
            text = text.replace("item-stale-runbook", "item-missing-reference", 1)
            (bundle_dir / "chunks.jsonl").write_text(text, encoding="utf-8")
            errors = validate_bundle(bundle_dir)
            self.assertTrue(any("item_id does not exist" in error for error in errors))

    def test_unexpected_bundle_entries_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            (bundle_dir / "notes.md").write_text("Synthetic sidecar file.\n", encoding="utf-8")
            (bundle_dir / "attachments").mkdir()

            errors = validate_bundle(bundle_dir)

            self.assertIn("unexpected bundle entry: notes.md", errors)
            self.assertIn("unexpected bundle entry: attachments/", errors)

    def test_required_file_symlink_is_rejected_before_bundle_reads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            external = Path(tmp) / "external.json"
            external.write_text('{}\n', encoding="utf-8")
            (bundle_dir / "bundle.json").unlink()
            (bundle_dir / "bundle.json").symlink_to(external)

            errors = validate_bundle(bundle_dir)

        self.assertEqual(
            errors,
            ["bundle entry must not be a symbolic link: bundle.json"],
        )

    def test_unexpected_symlink_is_rejected_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            external = Path(tmp) / "external.txt"
            external.write_text("Synthetic external text.\n", encoding="utf-8")
            (bundle_dir / "notes.md").symlink_to(external)

            errors = validate_bundle(bundle_dir)

        self.assertIn("bundle entry must not be a symbolic link: notes.md", errors)

    def test_public_safety_markers_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            readme = (bundle_dir / "README.md").read_text(encoding="utf-8")
            (bundle_dir / "README.md").write_text(
                f"{readme}\nThis synthetic fixture says Confidential for scanner coverage.\n",
                encoding="utf-8",
            )
            sources = load_jsonl(bundle_dir / "sources.jsonl")
            sources[0]["origin_ref"] = "https://intranet.example.invalid/fake-corpus/doc"
            write_jsonl(bundle_dir / "sources.jsonl", sources)
            write_checksums(bundle_dir)
            errors = validate_bundle(bundle_dir)
            self.assertIn("README.md: contains suspicious marker 'confidential'", errors)
            self.assertIn("sources.jsonl: contains an internal-looking URL", errors)

    def test_synthesis_stub_mentions_outputs_not_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            report = build_report(bundle_dir)
            self.assertIn("Synthetic Synthesis Report", report)
            self.assertIn("This report is an output, not bundle evidence.", report)


if __name__ == "__main__":
    unittest.main()
