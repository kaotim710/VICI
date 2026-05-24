import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_warning_audit_md import _audit_item, _rejected_pair_item


class WarningAuditReportTests(unittest.TestCase):
    def test_audit_item_includes_selected_attempt_placeholder(self):
        class Item:
            item = "7"
            warnings = ["warning"]
            confidence_level = "medium"
            confidence_score = 0.8
            text = "start middle end"
            start_evidence = None
            end_evidence = None
            confidence_components = []
            candidate_attempts = []
            recommended_actions = []

        class Result:
            status = "success"

        lines = _audit_item({"filing_id": "sample", "ticker": "ABC", "fiscal_year": 2023}, Result(), Item())

        self.assertIn("- No selected candidate attempt recorded.", lines)
        self.assertIn("- Warning categories: `uncategorized_warning`", lines)

    def test_rejected_pair_item_lists_rejected_attempts(self):
        class Evidence:
            text = "Item 1. Business"

        class Attempt:
            decision = "rejected"
            start_evidence = Evidence()
            end_evidence = Evidence()
            validation_reasons = ["REJECTED_SHORT_ORDERED_TOC_SPAN"]
            warnings = ["Candidate pair rejected."]

        class Item:
            item = "1"
            status = "success"
            confidence_level = "high"
            confidence_score = 1.0
            start_evidence = Evidence()
            candidate_attempts = [Attempt()]

        class Result:
            status = "success"

        lines = _rejected_pair_item({"filing_id": "sample", "ticker": "ABC", "fiscal_year": 2023}, Result(), Item())

        self.assertTrue(any("REJECTED_SHORT_ORDERED_TOC_SPAN" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
