import json
import unittest
from pathlib import Path


class SeedManifestTests(unittest.TestCase):
    def test_seed_manifest_has_twenty_filings(self):
        manifest_path = Path(__file__).resolve().parents[1] / "fixtures" / "gold" / "seed_filings.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["selection_strategy"]["total_filings"], 20)
        self.assertEqual(len(manifest["filings"]), 20)
        self.assertEqual(sorted(manifest["items"]), ["1", "1A", "7"])

    def test_seed_manifest_has_unique_filing_ids(self):
        manifest_path = Path(__file__).resolve().parents[1] / "fixtures" / "gold" / "seed_filings.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        filing_ids = [filing["filing_id"] for filing in manifest["filings"]]

        self.assertEqual(len(filing_ids), len(set(filing_ids)))


if __name__ == "__main__":
    unittest.main()

