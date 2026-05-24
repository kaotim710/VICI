import sys
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_regression import evaluate_regression, render_markdown


class RegressionEvaluationTests(unittest.TestCase):
    def test_regression_report_tracks_raw_preview_and_supplemental_sections(self):
        manifest = {
            "items": ["15", "16"],
            "filings": [
                {
                    "filing_id": "xom_2023_10k",
                    "ticker": "XOM",
                    "fiscal_year": 2023,
                    "industry": "Energy",
                    "form": "10-K",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            payload = evaluate_regression([("seed_sample", manifest_path)])
        supplemental = [
            row
            for row in payload["items"]
            if row["filing_id"] == "xom_2023_10k" and row["item"] == "supplemental-16"
        ]

        self.assertTrue(supplemental)
        self.assertGreaterEqual(supplemental[0]["supplemental_sections"], 20)
        self.assertTrue(supplemental[0]["raw_preview_available"])
        self.assertIn("warning_category_counts", payload["summary"])

    def test_regression_markdown_includes_recovery_readiness_sections(self):
        payload = {
            "summary": {
                "generated": "2026-05-25",
                "suites": ["seed"],
                "filings_evaluated": 1,
                "missing_filings": [],
                "item_rows": 1,
                "status_counts": {"success": 1},
                "confidence_level_counts": {"medium": 1},
                "warning_category_counts": {"reference_recovery": 1},
                "raw_preview_available_items": 1,
                "supplemental_items": 0,
                "recovery_action_counts": {"inspect_only:section_reference_detected": 1},
            },
            "items": [
                {
                    "suite": "seed",
                    "filing_id": "sample_10k",
                    "item": "7",
                    "is_supplemental": False,
                    "status": "success",
                    "confidence_level": "medium",
                    "confidence_score": 0.75,
                    "warning_categories": ["reference_recovery"],
                    "warnings": ["warning"],
                    "recommended_actions": [
                        {"action_type": "inspect_only", "reason": "section_reference_detected"}
                    ],
                    "raw_table_count": 2,
                    "raw_image_count": 1,
                    "supplemental_sections": 0,
                    "raw_preview_available": True,
                }
            ],
        }

        markdown = render_markdown(payload)

        self.assertIn("Warning And Recovery Readiness", markdown)
        self.assertIn("reference_recovery", markdown)
        self.assertIn("inspect_only:section_reference_detected", markdown)


if __name__ == "__main__":
    unittest.main()
