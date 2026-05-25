import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_seed import evaluation_summary
from sec_item_extractor.contracts import (
    evaluation_gate,
    recovery_action_contract,
    review_feedback_contract,
    retry_policy_contract,
    validation_gate,
    warning_category,
)


class ContractTests(unittest.TestCase):
    def test_warning_category_maps_known_warning(self):
        self.assertEqual(
            warning_category("Section appears to be a cross-reference rather than full narrative text."),
            "reference_recovery",
        )

    def test_recovery_action_contract_marks_user_selection_as_user_input(self):
        contract = recovery_action_contract("needs_user_selection", "internal_item_toc_detected")

        self.assertTrue(contract["requires_user_input"])
        self.assertEqual(contract["next_step"], "select_internal_heading")

    def test_evaluation_gate_fails_on_failed_seed_items(self):
        gate = evaluation_gate(
            {
                "evaluated": 20,
                "missing": [],
                "summary": {"item_status_counts": {"success": 459, "failed": 1}},
            }
        )

        self.assertFalse(gate["passed"])
        self.assertIn("failed_items", [check["name"] for check in gate["checks"]])

    def test_evaluation_summary_can_include_gold_boundary_summary(self):
        seed_payload = {
            "evaluated": 20,
            "missing": [],
            "summary": {
                "filing_status_counts": {"success": 20},
                "item_status_counts": {"success": 426, "not_present": 34},
                "confidence_level_counts": {"high": 447, "medium": 13},
                "warning_counts": {},
                "warning_category_counts": {},
            },
            "evaluation_gate": {"passed": True, "checks": []},
        }
        gold_payload = {"summary": {"filings": 5, "items": 15, "passed_checks": 45, "failed_checks": 0}}

        summary = evaluation_summary(seed_payload, gold_payload)

        self.assertTrue(summary["evaluation_gate"]["passed"])
        self.assertEqual(summary["gold_boundary"]["failed_checks"], 0)
        self.assertEqual(summary["retry_policy"]["contract_version"], "retry_policy_v1")

    def test_retry_policy_is_bounded_and_deterministic(self):
        policy = retry_policy_contract()

        self.assertEqual(policy["mode"], "bounded_deterministic")
        self.assertFalse(policy["llm_enabled"])
        self.assertIn("candidate_start_ranking", [step["name"] for step in policy["steps"]])
        self.assertIn("recovery_action_runner", [step["name"] for step in policy["steps"]])

    def test_review_feedback_contract_is_append_only_and_boundary_aware(self):
        contract = review_feedback_contract()

        self.assertEqual(contract["contract_version"], "review_feedback_v1")
        self.assertEqual(contract["storage_policy"], "append_only_review_records")
        self.assertIn("correct_boundary", contract["decisions"])
        self.assertIn("corrected_start_offset", contract["optional_fields"])

    def test_validation_gate_fails_on_warnings(self):
        gate = validation_gate(
            {
                "missing_filings": [],
                "item_status_counts": {"success": 10},
                "warning_counts": {"Start heading has TOC-like signals.": 1},
            }
        )

        self.assertFalse(gate["passed"])
        self.assertIn("warning_count", [check["name"] for check in gate["checks"]])


class GoldDatasetPlanTests(unittest.TestCase):
    def test_gold_dataset_plan_tracks_target_and_incremental_phases(self):
        plan = json.loads((ROOT / "fixtures" / "gold" / "gold_dataset_plan.json").read_text())

        self.assertEqual(plan["target_shape"]["target_filings"], 125)
        self.assertGreaterEqual(len(plan["phases"]), 4)
        self.assertEqual(plan["phases"][0]["name"], "seed_boundary_lock")


if __name__ == "__main__":
    unittest.main()
