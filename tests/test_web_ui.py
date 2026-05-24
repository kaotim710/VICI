import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
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

    def test_detail_page_can_render_action_review_snippets(self):
        html = web_ui.render_detail("aapl_2023_10k")

        self.assertIn("review-snippets", html)
        self.assertIn("reviewSnippetsFor", html)
        self.assertIn("exhibit_index_detected", html)

    def test_detail_page_can_load_original_filing_structure(self):
        html = web_ui.render_detail("wmt_2014_10k")

        self.assertIn("Show original filing structure", html)
        self.assertIn("raw-section-frame", html)
        self.assertIn("/raw-section/", html)

    def test_raw_section_preview_preserves_tables_and_archive_base(self):
        payload = web_ui.raw_section_preview("wmt_2014_10k", "15")

        self.assertGreater(payload["table_count"], 0)
        self.assertIn("<table", payload["srcdoc"].lower())
        self.assertIn("<base href=\"https://www.sec.gov/Archives/edgar/data/", payload["srcdoc"])

    def test_extract_endpoint_runs_pipeline_on_demand(self):
        class Result:
            parser_version = "test"
            status = "success"
            candidate_count = 0
            toc_confidence = "none"
            toc_entries = []
            item_results = []

            def to_dict(self):
                return {"status": "success", "toc_entries": [], "item_results": []}

        with patch("sec_item_extractor.web_ui.extract_items", return_value=Result()) as extract_items:
            payload = web_ui.extract_seed_filing("aapl_2014_10k")

        extract_items.assert_called_once()
        self.assertEqual(payload["filing"]["filing_id"], "aapl_2014_10k")
        self.assertEqual(payload["pipeline"]["trigger"], "on_demand_extract_request")
        self.assertEqual(payload["summary"]["status"], "success")
        self.assertEqual(payload["result"]["status"], "success")
        self.assertGreater(payload["source_bytes"], 0)

    def test_raw_metadata_does_not_run_extraction(self):
        with patch("sec_item_extractor.web_ui.extract_items") as extract_items:
            payload = web_ui.raw_filing_metadata("aapl_2014_10k")

        extract_items.assert_not_called()
        self.assertEqual(payload["filing"]["filing_id"], "aapl_2014_10k")
        self.assertEqual(payload["cache_policy"], "no-store")
        self.assertTrue(payload["raw"]["sha256"])

    def test_recover_endpoint_runs_pipeline_and_recovery_on_demand(self):
        extraction = SimpleNamespace(
            parser_version="test",
            status="warning",
            item_results=[],
        )
        recovery = SimpleNamespace(to_dict=lambda: {"item": "7", "status": "needs_review"})

        with patch("sec_item_extractor.web_ui.extract_items", return_value=extraction) as extract_items:
            with patch("sec_item_extractor.web_ui.run_recovery_actions", return_value=[recovery]) as run_recovery:
                payload = web_ui.recover_seed_filing(
                    "aapl_2014_10k", selections={("aapl_2014_10k", "7"): "Management"}
                )

        extract_items.assert_called_once()
        run_recovery.assert_called_once()
        self.assertEqual(payload["pipeline"]["trigger"], "on_demand_recovery_request")
        self.assertEqual(payload["summary"]["recovery_actions"], 1)
        self.assertEqual(payload["recoveries"][0]["status"], "needs_review")


if __name__ == "__main__":
    unittest.main()
