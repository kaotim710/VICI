import json
import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sec_item_extractor.candidates import ITEM_ORDER


class SeedManifestTests(unittest.TestCase):
    def test_seed_manifest_has_twenty_filings(self):
        manifest_path = Path(__file__).resolve().parents[1] / "fixtures" / "gold" / "seed_filings.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["selection_strategy"]["total_filings"], 20)
        self.assertEqual(len(manifest["filings"]), 20)
        self.assertEqual(manifest["items"], ITEM_ORDER)

    def test_seed_manifest_has_unique_filing_ids(self):
        manifest_path = Path(__file__).resolve().parents[1] / "fixtures" / "gold" / "seed_filings.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        filing_ids = [filing["filing_id"] for filing in manifest["filings"]]

        self.assertEqual(len(filing_ids), len(set(filing_ids)))

    def test_validation_manifest_is_held_out_from_seed(self):
        root = Path(__file__).resolve().parents[1]
        seed = json.loads((root / "fixtures" / "gold" / "seed_filings.json").read_text(encoding="utf-8"))
        validation = json.loads((root / "fixtures" / "gold" / "validation_filings.json").read_text(encoding="utf-8"))
        seed_tickers = {filing["ticker"] for filing in seed["filings"]}
        validation_tickers = {filing["ticker"] for filing in validation["filings"]}
        filing_ids = [filing["filing_id"] for filing in validation["filings"]]

        self.assertEqual(validation["selection_strategy"]["total_filings"], 10)
        self.assertEqual(len(validation["filings"]), 10)
        self.assertEqual(validation["items"], ITEM_ORDER)
        self.assertEqual(len(filing_ids), len(set(filing_ids)))
        self.assertFalse(seed_tickers & validation_tickers)
        self.assertEqual({filing["fiscal_year"] for filing in validation["filings"]}, {2015, 2025})


if __name__ == "__main__":
    unittest.main()
