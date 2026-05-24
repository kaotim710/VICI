import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sec_item_extractor import extract_items
from sec_item_extractor.recovery import run_recovery_actions


class RecoveryTests(unittest.TestCase):
    def test_cross_reference_recovery_parses_page_range_and_extracts_inferred_pages(self):
        filing = """
        Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations
        Management's discussion and analysis appears on pages 2-3. Such information should be read in conjunction
        with the Consolidated Financial Statements.
        Item 7A. Quantitative and Qualitative Disclosures About Market Risk
        Market risk text.

        1
        Preface page.
        2
        Referenced MD&A starts here.
        3
        Referenced MD&A continues here.
        4
        After referenced range.
        """
        extraction = extract_items(filing, target_items=["7"], filing_id="sample")

        results = run_recovery_actions(filing, extraction)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].reason, "same_filing_page_reference")
        self.assertEqual(results[0].page_range, (2, 3))
        self.assertEqual(results[0].status, "needs_review")
        self.assertEqual(results[0].severity, "review")
        self.assertTrue(results[0].requires_user_input)
        self.assertEqual(results[0].next_step, "confirm_referenced_page_extraction")
        self.assertIn("Referenced MD&A starts here", results[0].extracted_text)
        self.assertIn("Referenced MD&A continues here", results[0].extracted_text)

    def test_internal_toc_recovery_lists_options_until_user_selects_heading(self):
        filing = """
        Item 7. Company and Subsidiaries
        OVERVIEW
        """ + ("Overview narrative. " * 16000) + """
        RESULTS OF OPERATIONS
        """ + ("Results narrative. " * 14000) + """
        Item 7A. Quantitative and Qualitative Disclosures About Market Risk
        Market risk text.
        """
        extraction = extract_items(filing, target_items=["7"], filing_id="sample")

        pending = run_recovery_actions(filing, extraction)
        selected = run_recovery_actions(filing, extraction, selections={("sample", "7"): "OVERVIEW"})

        self.assertEqual(pending[0].status, "needs_user_selection")
        self.assertIn("OVERVIEW", pending[0].options)
        self.assertEqual(selected[0].status, "needs_review")
        self.assertEqual(selected[0].selected_option, "OVERVIEW")
        self.assertIn("Overview narrative.", selected[0].extracted_text)
        self.assertLess(selected[0].after_length, selected[0].before_length)

    def test_external_reference_recovery_is_deferred(self):
        filing = """
        Item 7. Management's Discussion and Analysis
        See the annual report for management discussion.
        Item 7A. Quantitative and Qualitative Disclosures About Market Risk
        Market risk text.
        """
        extraction = extract_items(filing, target_items=["7"], filing_id="sample")

        results = run_recovery_actions(filing, extraction)

        self.assertEqual(results[0].reason, "external_or_other_document_reference")
        self.assertEqual(results[0].status, "deferred")
        self.assertEqual(results[0].severity, "blocked")
        self.assertEqual(results[0].next_step, "provide_or_fetch_reference_document")
        self.assertIsNone(results[0].extracted_text)


if __name__ == "__main__":
    unittest.main()
