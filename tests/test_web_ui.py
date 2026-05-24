import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import web_ui


class WebUiTests(unittest.TestCase):
    def test_filing_options_lists_seed_filings_without_extraction(self):
        with patch("sec_item_extractor.web_ui.extract_items") as extract_items:
            options = web_ui.filing_options()

        self.assertEqual(len(options), 20)
        self.assertTrue(all("filing_id" in option for option in options))
        extract_items.assert_not_called()

    def test_detail_page_does_not_embed_extracted_item_text(self):
        html = web_ui.render_detail("aapl_2023_10k")

        self.assertIn("Run extraction", html)
        self.assertIn("/api/filings/", html)
        self.assertNotIn("The Company designs", html)

    def test_extract_endpoint_runs_pipeline_on_demand(self):
        class Result:
            def to_dict(self):
                return {"status": "success", "item_results": []}

        with patch("sec_item_extractor.web_ui.extract_items", return_value=Result()) as extract_items:
            payload = web_ui.extract_seed_filing("aapl_2014_10k")

        extract_items.assert_called_once()
        self.assertEqual(payload["filing"]["filing_id"], "aapl_2014_10k")
        self.assertEqual(payload["result"]["status"], "success")
        self.assertGreater(payload["source_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
