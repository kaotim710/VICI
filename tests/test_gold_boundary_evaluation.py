import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_gold_boundaries import _action_matches, _contains


class GoldBoundaryEvaluationTests(unittest.TestCase):
    def test_contains_is_case_insensitive_and_whitespace_tolerant(self):
        self.assertTrue(_contains("ITEM 7.\n\nMANAGEMENT", "Item 7. Management"))

    def test_action_matches_empty_expectation(self):
        self.assertTrue(_action_matches(set(), {"expected_action_type": None, "expected_action_reason": None}))

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


if __name__ == "__main__":
    unittest.main()
