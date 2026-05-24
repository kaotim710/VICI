import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sec_item_extractor import extract_items
from sec_item_extractor.cleaning import html_to_text, parse_document


SAMPLE_10K = """
<html>
  <head><title>Sample</title></head>
  <body>
    <div style="display:none">Item 1A. Hidden iXBRL noise</div>
    <h1>Table of Contents</h1>
    <p>Item 1. Business........ 3</p>
    <p>Item 1A. Risk Factors........ 12</p>
    <p>Item 7. Management's Discussion and Analysis........ 44</p>
    <p>Item 8. Financial Statements........ 75</p>

    <h1>Item 1. Business</h1>
    <p>The company operates a platform business with products, services, customers, and markets.</p>
    <p>""" + ("Business narrative. " * 90) + """</p>

    <h1>Item 1A. Risk Factors</h1>
    <p>Investing in our securities involves risks.</p>
    <p>""" + ("Risk factor narrative. " * 90) + """</p>

    <h1>Item 1B. Unresolved Staff Comments</h1>
    <p>None.</p>

    <h1>Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations</h1>
    <p>Management discusses the financial condition and results of operations.</p>
    <p>""" + ("MD&A narrative. " * 110) + """</p>

    <h1>Item 7A. Quantitative and Qualitative Disclosures About Market Risk</h1>
    <p>Market risk disclosure.</p>
  </body>
</html>
"""


class ExtractorTests(unittest.TestCase):
    def test_extracts_requested_items_and_skips_toc(self):
        result = extract_items(SAMPLE_10K, filing_id="sample")
        by_item = {item.item: item for item in result.item_results}

        self.assertEqual(result.status, "success")
        self.assertIn("The company operates", by_item["1"].text)
        self.assertIn("Investing in our securities", by_item["1A"].text)
        self.assertIn("Management discusses", by_item["7"].text)
        self.assertNotIn("Table of Contents", by_item["1"].text)
        self.assertGreater(by_item["1"].start_offset, 0)
        self.assertEqual(by_item["1"].start_evidence.item, "1")
        self.assertIsNotNone(by_item["1"].start_evidence.raw_offset)
        self.assertIsNotNone(by_item["1"].start_evidence.block_index)
        self.assertEqual(by_item["1"].candidate_attempts[0].decision, "selected")
        self.assertIn("START_HEADING_FOUND", by_item["1"].candidate_attempts[0].validation_reasons)
        self.assertEqual(by_item["7"].end_evidence.item, "7A")

    def test_hidden_ixbrl_like_content_is_suppressed(self):
        text = html_to_text(SAMPLE_10K)

        self.assertNotIn("Hidden iXBRL noise", text)

    def test_parse_document_preserves_clean_and_raw_offsets(self):
        document = parse_document(SAMPLE_10K)
        business_block = next(block for block in document.blocks if block.text == "Item 1. Business")

        self.assertEqual(document.text[business_block.clean_start : business_block.clean_end], "Item 1. Business")
        self.assertIsNotNone(business_block.raw_start)
        self.assertIsNotNone(business_block.raw_end)
        self.assertIn("Item 1. Business", SAMPLE_10K[business_block.raw_start : business_block.raw_end])
        self.assertEqual(business_block.tag, "h1")

    def test_missing_end_boundary_fails_explicitly(self):
        result = extract_items("Item 1. Business\n" + ("Only business. " * 80), target_items=["1"])
        item = result.item_results[0]

        self.assertEqual(result.status, "failed")
        self.assertEqual(item.status, "failed")
        self.assertIn("LEGAL_END_HEADING_NOT_FOUND", item.validation_reasons)
        self.assertEqual(item.candidate_attempts[0].decision, "rejected")


if __name__ == "__main__":
    unittest.main()
