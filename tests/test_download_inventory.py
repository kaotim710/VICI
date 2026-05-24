import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DownloadInventoryTests(unittest.TestCase):
    def test_download_inventory_has_twenty_files(self):
        inventory = json.loads((ROOT / "fixtures" / "gold" / "downloaded_seed_filings.json").read_text())

        self.assertEqual(inventory["total_files"], 20)
        self.assertEqual(len(inventory["files"]), 20)

    def test_download_inventory_matches_total_bytes(self):
        inventory = json.loads((ROOT / "fixtures" / "gold" / "downloaded_seed_filings.json").read_text())
        total = sum(item["bytes"] for item in inventory["files"])

        self.assertEqual(total, inventory["total_bytes"])


if __name__ == "__main__":
    unittest.main()
