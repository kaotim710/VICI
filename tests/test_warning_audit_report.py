import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_warning_audit_md import _audit_item


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

        class Result:
            status = "success"

        lines = _audit_item({"filing_id": "sample", "ticker": "ABC", "fiscal_year": 2023}, Result(), Item())

        self.assertIn("- No selected candidate attempt recorded.", lines)


if __name__ == "__main__":
    unittest.main()
