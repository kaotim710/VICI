import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_seed import evaluate_seed, evaluation_summary


class SeedEvaluationTests(unittest.TestCase):
    def test_seed_evaluation_tracks_raw_media_counts_for_all_test_filings(self):
        manifest = {
            "items": ["5"],
            "filings": [
                {
                    "filing_id": "wmt_2023_10k",
                    "ticker": "WMT",
                    "fiscal_year": 2023,
                    "industry": "Consumer Staples",
                    "form": "10-K",
                }
            ],
        }

        payload = evaluate_seed(manifest)
        item = payload["results"][0]["items"]["5"]

        self.assertGreaterEqual(item["raw_structure"]["table_count"], 1)
        self.assertGreaterEqual(item["raw_structure"]["image_count"], 1)
        self.assertGreater(item["raw_bytes"], 0)
        self.assertGreaterEqual(payload["summary"]["raw_media_counts"]["items_with_tables"], 1)
        self.assertGreaterEqual(payload["summary"]["raw_media_counts"]["items_with_images"], 1)

    def test_evaluation_summary_includes_raw_media_counts(self):
        payload = {
            "evaluated": 20,
            "missing": [],
            "summary": {
                "filing_status_counts": {"success": 20},
                "item_status_counts": {"success": 426, "not_present": 34},
                "confidence_level_counts": {"high": 447, "medium": 13},
                "warning_counts": {},
                "warning_category_counts": {},
                "raw_media_counts": {
                    "items_with_tables": 10,
                    "items_with_images": 2,
                    "total_tables": 25,
                    "total_images": 3,
                },
            },
            "evaluation_gate": {"passed": True, "checks": []},
        }

        summary = evaluation_summary(payload)

        self.assertEqual(summary["raw_media_counts"]["items_with_tables"], 10)
        self.assertEqual(summary["raw_media_counts"]["items_with_images"], 2)


if __name__ == "__main__":
    unittest.main()
