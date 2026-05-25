import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_validation import render_markdown


class ValidationEvaluationTests(unittest.TestCase):
    def test_validation_markdown_includes_review_details(self):
        payload = {
            "summary": {
                "generated": "2026-05-25",
                "manifest": "fixtures/gold/validation_filings.json",
                "evaluated_filings": 1,
                "missing_filings": [],
                "item_attempts": 2,
                "filing_status_counts": {"success": 1},
                "item_status_counts": {"success": 1, "not_present": 1},
                "confidence_level_counts": {"medium": 1, "high": 1},
                "warning_counts": {"warning": 1},
                "warning_category_counts": {"reference_recovery": 1},
            },
            "evaluation_gate": {
                "passed": False,
                "checks": [
                    {"name": "warning_count", "actual": 1, "expected": "<= 0", "passed": False}
                ],
            },
            "results": [
                {
                    "filing_id": "sample_10k",
                    "status": "success",
                    "toc_confidence": "high",
                    "candidate_count": 3,
                    "recommended_action_count": 1,
                    "warnings": ["warning"],
                    "items": {
                        "7": {
                            "status": "success",
                            "confidence_level": "medium",
                            "confidence_score": 0.75,
                            "text_length": 123,
                            "warnings": ["warning"],
                            "warning_categories": ["reference_recovery"],
                            "validation_reasons": ["START_HEADING_FOUND"],
                            "start_evidence": {
                                "kind": "heading",
                                "offset": 10,
                                "text": "Item 7",
                                "reasons": ["EXPECTED_TITLE_MATCH"],
                            },
                            "end_evidence": None,
                            "start_snippet": "Item 7 start",
                            "end_snippet": "Item 7 end",
                            "recommended_actions": [
                                {
                                    "action_type": "inspect_only",
                                    "reason": "section_reference_detected",
                                }
                            ],
                        },
                        "1C": {
                            "status": "not_present",
                            "confidence_level": "high",
                            "confidence_score": 1.0,
                            "text_length": 0,
                            "warnings": [],
                            "warning_categories": [],
                            "validation_reasons": [],
                            "start_evidence": None,
                            "end_evidence": None,
                            "start_snippet": "",
                            "end_snippet": "",
                            "recommended_actions": [],
                        },
                    },
                }
            ],
        }

        markdown = render_markdown(payload)

        self.assertIn("Warning And Failed Items", markdown)
        self.assertIn("Validation Gate", markdown)
        self.assertIn("warning_count", markdown)
        self.assertIn("reference_recovery", markdown)
        self.assertIn("inspect_only:section_reference_detected", markdown)
        self.assertIn("Start evidence", markdown)
        self.assertIn("Start snippet: Item 7 start", markdown)
        self.assertIn("Not Present Items", markdown)
        self.assertIn("`sample_10k` Item `1C`", markdown)


if __name__ == "__main__":
    unittest.main()
