import sys
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import web_ui
from sec_item_extractor.extractor import extract_items


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
        self.assertIn("structure-tag", html)
        self.assertIn("renderStructureTags", html)
        self.assertIn("structure-outline", html)
        self.assertIn("renderStructurePanel", html)
        self.assertIn("structure-section", html)
        self.assertIn("renderStructureSection", html)

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

    def test_extract_endpoint_tags_items_with_raw_tables_and_images(self):
        payload = web_ui.extract_seed_filing("wmt_2023_10k")
        by_item = {item["item"]: item for item in payload["result"]["item_results"]}

        self.assertGreater(by_item["5"]["raw_structure"]["table_count"], 0)
        self.assertGreater(by_item["5"]["raw_structure"]["image_count"], 0)

    def test_extract_endpoint_exposes_raw_outline_for_large_structured_items(self):
        payload = web_ui.extract_seed_filing("jpm_2023_10k")
        by_item = {item["item"]: item for item in payload["result"]["item_results"]}

        self.assertGreater(by_item["15"]["raw_structure"]["raw_bytes"], 250000)
        self.assertIsInstance(by_item["15"]["raw_structure"]["outline"], list)
        self.assertIsInstance(by_item["15"]["raw_structure"]["sections"], list)
        self.assertGreater(len(by_item["15"]["raw_structure"]["sections"]), 0)
        exhibit_section = by_item["15"]["raw_structure"]["sections"][3]
        self.assertIn("Restated Certificate", exhibit_section["label"])
        self.assertIn("href", exhibit_section)
        self.assertIsNone(by_item["15"]["raw_structure"]["supplemental_chunk"])
        self.assertIn("supplemental-15", by_item)
        supplemental = by_item["supplemental-15"]
        self.assertEqual(supplemental["display_label"], "Supplemental after Item 15")
        self.assertTrue(supplemental["raw_section_available"])
        self.assertGreater(supplemental["raw_structure"]["table_count"], 0)
        self.assertGreater(supplemental["raw_structure"]["image_count"], 0)
        self.assertIn("Three-Year Summary", supplemental["raw_structure"]["sections"][0]["label"])
        self.assertNotIn("href", supplemental["raw_structure"]["sections"][0])

    def test_supplemental_raw_section_preview_preserves_own_raw_structure(self):
        payload = web_ui.raw_section_preview("jpm_2023_10k", "supplemental-15")

        self.assertGreater(payload["table_count"], 0)
        self.assertGreater(payload["image_count"], 0)
        self.assertIn("Table of contents", payload["srcdoc"])
        self.assertIn("Three-Year Summary", payload["srcdoc"])

    def test_supplemental_partitioning_runs_across_seed_filings(self):
        expected = {
            "jpm_2014_10k": ["supplemental-15"],
            "jpm_2023_10k": ["supplemental-15"],
            "xom_2014_10k": ["supplemental-15"],
            "xom_2023_10k": ["supplemental-16"],
            "cvx_2014_10k": ["supplemental-15"],
        }
        observed = {}
        manifest = json.loads((ROOT / "fixtures" / "gold" / "seed_filings.json").read_text(encoding="utf-8"))

        for filing in manifest["filings"]:
            filing_id = filing["filing_id"]
            content = (ROOT / "fixtures" / "filings" / "raw" / f"{filing_id}.html").read_text(
                encoding="utf-8", errors="replace"
            )
            result = extract_items(content, target_items=["15", "16"], filing_id=filing_id)
            result_dict = result.to_dict()
            web_ui._attach_raw_structure(result_dict, content, result.item_results)
            web_ui._append_supplemental_items(result_dict)
            supplemental_items = [item["item"] for item in result_dict["item_results"] if item["item"].startswith("supplemental-")]
            if supplemental_items:
                observed[filing_id] = supplemental_items
                for item in supplemental_items:
                    preview = web_ui.raw_section_preview(filing_id, item)
                    self.assertGreater(preview["raw_bytes"], 1000)
                    self.assertGreater(preview["table_count"] + preview["image_count"], 0)
                    self.assertIn("table of contents", preview["srcdoc"].lower())
                    self.assertNotIn("Item 1. Business", preview["srcdoc"][:20000])

        self.assertEqual(observed, expected)

    def test_jpm_item_fifteen_raw_section_starts_at_actual_section(self):
        payload = web_ui.extract_seed_filing("jpm_2023_10k")
        by_item = {item["item"]: item for item in payload["result"]["item_results"]}

        self.assertIn("Exhibit 3.1", by_item["15"]["text"])
        self.assertNotIn("Item 1. Business", by_item["15"]["text"][:1000])

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
