import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sec_item_extractor import extract_items
from sec_item_extractor.candidates import ITEM_ORDER, find_heading_candidates, infer_toc_profile
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
        result = extract_items(SAMPLE_10K, target_items=["1", "1A", "7"], filing_id="sample")
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
        self.assertEqual(by_item["1"].confidence_components[0].name, "legal_boundary_pair")
        self.assertAlmostEqual(
            round(sum(component.earned for component in by_item["1"].confidence_components), 2),
            by_item["1"].confidence_score,
        )
        self.assertEqual(by_item["1"].candidate_attempts[0].decision, "selected")
        self.assertIn("START_HEADING_FOUND", by_item["1"].candidate_attempts[0].validation_reasons)
        self.assertEqual(by_item["7"].end_evidence.item, "7A")

    def test_default_target_items_cover_full_supported_10k_item_list(self):
        result = extract_items(SAMPLE_10K, filing_id="sample")

        self.assertEqual([item.item for item in result.item_results], ITEM_ORDER)
        self.assertEqual(result.status, "partial")

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

    def test_cross_reference_section_with_strong_boundaries_is_inspectable_without_warning(self):
        filing = """
        Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations
        Management's discussion and analysis appears on pages 48-161. Such information should be read in conjunction
        with the Consolidated Financial Statements.
        Item 7A. Quantitative and Qualitative Disclosures About Market Risk
        Market risk text.
        """

        result = extract_items(filing, target_items=["7"])
        item = result.item_results[0]

        self.assertNotIn("Section appears to be a cross-reference rather than full narrative text.", item.warnings)
        self.assertIn("CROSS_REFERENCE_ACCEPTED_BY_BOUNDARY_CONTEXT", item.validation_reasons)

    def test_short_unexplained_section_recommends_external_source(self):
        filing = """
        Item 7. Management's Discussion and Analysis
        See the annual report for management discussion.
        Item 7A. Quantitative and Qualitative Disclosures About Market Risk
        Market risk text.
        """

        result = extract_items(filing, target_items=["7"])
        item = result.item_results[0]

        self.assertNotIn("Section length is outside the expected first-pass range.", item.warnings)
        self.assertIn("SECTION_LENGTH_SHORT_ACCEPTED_BY_PLACEHOLDER_OR_BOUNDARY_CONTEXT", item.validation_reasons)
        action_pairs = {(action.action_type, action.reason) for action in item.recommended_actions}
        self.assertIn(("needs_external_source", "external_or_other_document_reference"), action_pairs)

    def test_short_bounded_section_keeps_text_without_length_warning(self):
        filing = """
        Item 8. Financial Statements and Supplementary Data
        The financial statements begin on the following page.
        Item 9. Changes in and Disagreements With Accountants
        None.
        """

        result = extract_items(filing, target_items=["8"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertIn("financial statements begin", item.text)
        self.assertNotIn("Section length is outside the expected first-pass range.", item.warnings)
        self.assertIn("SECTION_LENGTH_SHORT_ACCEPTED_BY_PLACEHOLDER_OR_BOUNDARY_CONTEXT", item.validation_reasons)

    def test_exhibit_section_emits_review_action(self):
        filing = """
        Item 15. Exhibits, Financial Statement Schedules
        Exhibit 10.1 Material agreement
        Exhibit 21 Subsidiaries
        Item 16. Form 10-K Summary
        None.
        """

        result = extract_items(filing, target_items=["15"])
        item = result.item_results[0]
        action_pairs = {(action.action_type, action.reason) for action in item.recommended_actions}

        self.assertIn("Exhibit 10.1", item.text)
        self.assertIn(("inspect_only", "exhibit_index_detected"), action_pairs)

    def test_item_fifteen_skips_toc_heading_followed_by_page_range(self):
        filing = """
        <html><body>
        <div>Table of Contents</div>
        <div>Part IV</div>
        <div>Item 15.</div>
        <div>Exhibits, Financial Statement Schedules.</div>
        <td>40-43</td>
        <div>Part I</div>
        <div>Item 1. Business.</div>
        <div>Business overview text.</div>

        <div>Part IV</div>
        <div>Item 15. Exhibits, Financial Statement Schedules</div>
        <div>Exhibit 10.1 Material agreement</div>
        <div>Exhibit 21 Subsidiaries</div>
        <div>SIGNATURES</div>
        </body></html>
        """

        result = extract_items(filing, target_items=["15"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertNotIn("Item 1. Business", item.text)
        self.assertIn("Exhibit 10.1", item.text)

    def test_item_fifteen_keeps_numbered_exhibit_subsections(self):
        filing = """
        Table of Contents
        Part IV
        Item 15. Exhibits, Financial Statement Schedules
        1
        Financial statements
        The consolidated financial statements are listed in Item 8.
        2
        Exhibit 10.1 Material agreement
        SIGNATURES
        """

        result = extract_items(filing, target_items=["15"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertIn("Financial statements", item.text)
        self.assertIn("Exhibit 10.1", item.text)

    def test_short_administrative_sections_do_not_recommend_external_source(self):
        filing = """
        Item 1B. Unresolved Staff Comments
        None.
        Item 1C. Cybersecurity
        Cybersecurity governance text.
        """

        result = extract_items(filing, target_items=["1B"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertEqual(item.warnings, [])
        self.assertEqual(item.recommended_actions, [])

    def test_item_sixteen_uses_terminal_boundary(self):
        filing = """
        Item 16. Form 10-K Summary
        None.

        SIGNATURES
        Signature text.
        """

        result = extract_items(filing, target_items=["16"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertIn("None.", item.text)
        self.assertNotIn("Signature text.", item.text)
        self.assertEqual(item.end_evidence.item, "EOF")

    def test_item_fifteen_can_use_terminal_boundary_when_item_sixteen_is_absent(self):
        filing = """
        PART IV
        Item 15. Exhibits, Financial Statement Schedules
        Exhibit index text.

        SIGNATURES
        Signature text.
        """

        result = extract_items(filing, target_items=["15"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertIn("Exhibit index text.", item.text)
        self.assertNotIn("Signature text.", item.text)
        self.assertIn("ITEM_15_TERMINAL_END_BOUNDARY_USED", item.candidate_attempts[0].validation_reasons)

    def test_item_absent_from_toc_is_not_treated_as_failed_extraction(self):
        filing = """
        Table of Contents
        Item 1. Business........ 3
        Item 2. Properties........ 9

        Item 1. Business
        Business narrative.
        Item 2. Properties
        Properties narrative.
        """

        result = extract_items(filing, target_items=["1C"])
        item = result.item_results[0]

        self.assertEqual(result.status, "success")
        self.assertEqual(item.status, "not_present")
        self.assertIn("ITEM_NOT_DECLARED_IN_TOC", item.validation_reasons)
        self.assertEqual(item.warnings, [])
        self.assertEqual(result.toc_items, ["1", "2"])
        self.assertEqual(result.toc_confidence, "high")

    def test_item_absent_from_observed_sequence_is_not_failed_without_toc(self):
        spacer = " Long narrative sentence." * 90
        filing = """
        Item 1. Business
        Business narrative.
        """ + spacer + """
        Item 1A. Risk Factors
        Risk narrative.
        """ + spacer + """
        Item 1B. Unresolved Staff Comments
        None.
        Item 2. Properties
        Property narrative.
        """ + spacer + """
        Item 3. Legal Proceedings
        Legal narrative.
        """ + spacer + """
        Item 4. Mine Safety Disclosures
        None.
        Item 5. Market for Registrant's Common Equity
        Market narrative.
        """ + spacer + """
        Item 6. Selected Financial Data
        Selected data narrative.
        """ + spacer + """
        Item 7. Management's Discussion and Analysis
        MD&A narrative.
        """ + spacer + """
        Item 7A. Quantitative and Qualitative Disclosures About Market Risk
        Market risk narrative.
        """ + spacer + """
        Item 8. Financial Statements and Supplementary Data
        Financial statements narrative.
        """

        result = extract_items(filing, target_items=["1C"])
        item = result.item_results[0]

        self.assertEqual(result.status, "success")
        self.assertEqual(item.status, "not_present")
        self.assertIn("ITEM_NOT_DECLARED_IN_OBSERVED_SEQUENCE", item.validation_reasons)

    def test_toc_next_item_can_skip_absent_intermediate_items_for_boundary(self):
        filing = """
        Table of Contents
        Item 1. Business........ 3
        Item 2. Properties........ 9

        Item 1. Business
        Business narrative.
        Item 2. Properties
        Properties narrative.
        """

        result = extract_items(filing, target_items=["1"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertEqual(item.end_evidence.item, "2")
        self.assertIn("Business narrative.", item.text)
        self.assertNotIn("Properties narrative.", item.text)

    def test_toc_profile_preserves_structured_entries(self):
        candidates = find_heading_candidates(
            """
            Table of Contents
            Item 1. Business........ 3
            Item 1A. Risk Factors........ 12
            Item 7. Management's Discussion and Analysis........ 44
            """
        )

        profile = infer_toc_profile(candidates)

        self.assertEqual(profile.confidence, "high")
        self.assertEqual([entry.item for entry in profile.entries], ["1", "1A", "7"])
        self.assertEqual(profile.entries[0].title, "Business")
        self.assertEqual(profile.entries[0].page_number, 3)
        self.assertGreaterEqual(profile.entries[0].offset, 0)

    def test_long_noncanonical_section_recommends_subsection_selection(self):
        filing = """
        Item 7. Company and Subsidiaries
        OVERVIEW
        """ + ("Long narrative. " * 22000) + """
        RESULTS OF OPERATIONS
        """ + ("More long narrative. " * 20000) + """
        Item 7A. Quantitative and Qualitative Disclosures About Market Risk
        Market risk text.
        """

        result = extract_items(filing, target_items=["7"])
        item = result.item_results[0]

        self.assertEqual(item.recommended_actions[0].action_type, "needs_user_selection")
        self.assertIn("OVERVIEW", item.recommended_actions[0].options)

    def test_dense_item_cluster_alone_is_not_toc_like(self):
        text = """
        Item 1A. Risk Factors
        Discussion references Item 2 and Item 3 and Item 4 and Item 5 and Item 6 in ordinary narrative.
        Item 1B. Unresolved Staff Comments
        """

        candidates = find_heading_candidates(text)

        self.assertFalse(candidates[0].is_toc_like)

    def test_dense_item_cluster_near_table_of_contents_is_toc_like(self):
        text = """
        Table of Contents
        Item 1. Business
        Item 1A. Risk Factors
        Item 1B. Unresolved Staff Comments
        Item 2. Properties
        Item 3. Legal Proceedings
        Item 4. Mine Safety Disclosures
        """

        candidates = find_heading_candidates(text)

        self.assertTrue(candidates[0].is_toc_like)

    def test_item_ten_is_not_parsed_as_item_one(self):
        candidates = find_heading_candidates("Item 10. Directors, Executive Officers and Corporate Governance")

        self.assertEqual(candidates[0].item, "10")

    def test_body_heading_after_toc_is_not_marked_toc_like_by_prior_toc_cluster(self):
        text = """
        Table of Contents
        Item 12. Security Ownership
        Item 13. Certain Relationships
        Item 14. Principal Accounting Fees
        Item 15. Exhibits
        Item 16. Form 10-K Summary

        PART I
        Item 1. Business
        This business section starts after the table of contents.
        """

        candidates = find_heading_candidates(text)

        self.assertFalse(candidates[-1].is_toc_like)

    def test_short_dense_toc_span_uses_later_body_candidate(self):
        filing = """
        Item 1. Business
        Item 1A. Risk Factors
        Item 1B. Unresolved Staff Comments
        Item 2. Properties
        Item 3. Legal Proceedings

        Item 1. Business
        """ + ("Business narrative. " * 80) + """
        Item 1A. Risk Factors
        """ + ("Risk narrative. " * 80)

        result = extract_items(filing, target_items=["1"])
        item = result.item_results[0]

        self.assertIn("Business narrative.", item.text)
        self.assertEqual(item.candidate_attempts[-1].decision, "selected")

    def test_short_dense_body_candidate_is_accepted_when_no_later_start_exists(self):
        filing = """
        Table of Contents
        Item 6. Selected Financial Data........ 19
        Item 7. Management's Discussion and Analysis........ 20

        ITEM 6: SELECTED FINANCIAL DATA
        For five-year selected financial data, see page 62.
        ITEM 7: MANAGEMENT'S DISCUSSION AND ANALYSIS
        Discussion narrative.
        """

        result = extract_items(filing, target_items=["6"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertIn("For five-year selected financial data", item.text)
        self.assertEqual(item.candidate_attempts[-1].decision, "selected")

    def test_later_non_toc_duplicate_item_is_preferred_over_near_toc_entry(self):
        filing = """
        Table of Contents
        Item 16. Form 10-K Summary
        Forward-looking statements and exhibit text that should not be part of Item 16.
        """ + ("Earlier page text. " * 120) + """
        Item 16.Form 10-K Summary
        Not applicable.

        SIGNATURES
        Signature text.
        """

        result = extract_items(filing, target_items=["16"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertTrue(item.text.startswith("Item 16.Form 10-K Summary"))
        self.assertIn("Not applicable.", item.text)
        self.assertNotIn("Forward-looking statements", item.text)

    def test_not_applicable_short_item_is_not_rejected_as_toc_span(self):
        filing = """
        Table of Contents
        Item 9B. Other Information........ 72
        Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections........ 73
        Item 10. Directors, Executive Officers, and Corporate Governance........ 73

        Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections
        Not applicable.
        Item 10. Directors, Executive Officers, and Corporate Governance
        Director text.
        """

        result = extract_items(filing, target_items=["9C"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertIn("Not applicable.", item.text)
        self.assertNotIn("Director text.", item.text)
        self.assertEqual(item.warnings, [])

    def test_reserved_item_is_accepted_without_length_warning(self):
        filing = """
        Item 6. [Reserved]
        Item 7. Management's Discussion and Analysis
        Discussion text.
        """

        result = extract_items(filing, target_items=["6"])
        item = result.item_results[0]

        self.assertEqual(item.status, "success")
        self.assertNotIn("Section length is outside the expected first-pass range.", item.warnings)

    def test_long_structured_exhibit_section_uses_review_action_without_length_warning(self):
        filing = """
        Item 15. Exhibits, Financial Statement Schedules
        EXHIBIT INDEX
        """ + ("Exhibit 10.1 Material agreement. " * 12000) + """
        SIGNATURES
        Signature text.
        """

        result = extract_items(filing, target_items=["15"])
        item = result.item_results[0]

        self.assertNotIn("Section length is outside the expected first-pass range.", item.warnings)
        self.assertIn("SECTION_LENGTH_LONG_ACCEPTED_AS_STRUCTURED_SECTION", item.validation_reasons)


if __name__ == "__main__":
    unittest.main()
