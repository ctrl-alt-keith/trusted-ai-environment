from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from trusted_ai_environment.bundle_validate import validate_bundle
from trusted_ai_environment.fake_bundle import create_fake_bundle
from trusted_ai_environment.synthesize_stub import build_report


class BundleValidationTests(unittest.TestCase):
    def test_fake_bundle_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = Path(tmp) / "bundle"
            create_fake_bundle(bundle_dir)
            self.assertEqual(validate_bundle(bundle_dir), [])

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

