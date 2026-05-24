import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_gold_boundaries import _action_matches, _contains, _minimum_match, evaluate_gold


class GoldBoundaryEvaluationTests(unittest.TestCase):
    def test_contains_is_case_insensitive_and_whitespace_tolerant(self):
        self.assertTrue(_contains("ITEM 7.\n\nMANAGEMENT", "Item 7. Management"))

    def test_action_matches_empty_expectation(self):
        expectation = {"expected_action_type": None, "expected_action_reason": None}

        self.assertTrue(_action_matches(set(), expectation))
        self.assertTrue(_action_matches({("inspect_only", "section_reference_detected")}, expectation))
        self.assertFalse(_action_matches({("needs_user_confirmation", "same_filing_page_reference")}, expectation))

    def test_action_matches_expected_pair(self):
        pairs = {("needs_user_confirmation", "same_filing_page_reference")}

        self.assertTrue(
            _action_matches(
                pairs,
                {
                    "expected_action_type": "needs_user_confirmation",
                    "expected_action_reason": "same_filing_page_reference",
                },
            )
        )

    def test_minimum_match_accepts_optional_raw_media_expectations(self):
        self.assertTrue(_minimum_match(0, None))
        self.assertTrue(_minimum_match(2, 1))
        self.assertFalse(_minimum_match(0, 1))

    def test_gold_evaluation_tracks_raw_table_and_image_fidelity(self):
        gold = {
            "items": ["5"],
            "filings": [
                {
                    "filing_id": "wmt_2023_10k",
                    "source_path": "fixtures/filings/raw/wmt_2023_10k.html",
                    "items": {
                        "5": {
                            "expected_start_contains": "ITEM 5. MARKET",
                            "expected_end_contains": "ITEM 6. RESERVED",
                            "expected_action_type": None,
                            "expected_action_reason": None,
                            "expected_raw_tables_min": 1,
                            "expected_raw_images_min": 1,
                        }
                    },
                }
            ],
        }

        payload = evaluate_gold(gold)
        row = payload["results"][0]

        self.assertEqual(payload["summary"]["failed_checks"], 0)
        self.assertTrue(row["raw_table_match"])
        self.assertTrue(row["raw_image_match"])
        self.assertGreaterEqual(row["raw_table_count"], 1)
        self.assertGreaterEqual(row["raw_image_count"], 1)
        self.assertGreater(row["raw_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
