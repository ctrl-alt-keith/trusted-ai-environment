from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from trusted_ai_environment.bundle_validate import validate_bundle
from trusted_ai_environment.checksum import write_checksums
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
    def test_fake_bundle_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            self.assertEqual(validate_bundle(bundle_dir), [])

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

    def test_checksum_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            with (bundle_dir / "items.jsonl").open("a", encoding="utf-8") as handle:
                handle.write("\n")
            errors = validate_bundle(bundle_dir)
            self.assertIn("checksum mismatch for items.jsonl", errors)

    def test_missing_reference_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            text = (bundle_dir / "chunks.jsonl").read_text(encoding="utf-8")
            text = text.replace("item-stale-runbook", "item-missing-reference", 1)
            (bundle_dir / "chunks.jsonl").write_text(text, encoding="utf-8")
            errors = validate_bundle(bundle_dir)
            self.assertTrue(any("item_id does not exist" in error for error in errors))

    def test_synthesis_stub_mentions_outputs_not_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            report = build_report(bundle_dir)
            self.assertIn("Synthetic Synthesis Report", report)
            self.assertIn("This report is an output, not bundle evidence.", report)


if __name__ == "__main__":
    unittest.main()
