import json
import sys
import unittest
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import web_ui
from sec_item_extractor.extractor import extract_items


RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
CASES_PATH = ROOT / "fixtures" / "gold" / "reviewed_issue_cases.json"
START_TOC_WARNING = "Start heading has TOC-like signals."


@lru_cache(maxsize=None)
def _extract(filing_id: str, item: str):
    content = (RAW_DIR / f"{filing_id}.html").read_text(encoding="utf-8", errors="replace")
    result = extract_items(content, target_items=[item], filing_id=filing_id)
    return content, result.item_results[0]


def _raw_structure(filing_id: str, item: str) -> dict:
    content, item_result = _extract(filing_id, item)
    return web_ui._raw_structure_contract(content, item_result)


def _action_keys(item_result) -> set[str]:
    return {f"{action.action_type}:{action.reason}" for action in item_result.recommended_actions}


class ReviewedIssueCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def test_reviewed_front_toc_false_positives_use_body_headings(self):
        for case in self.cases["front_toc_false_positive"]:
            with self.subTest(issue=case["issue"], filing_id=case["filing_id"]):
                _, item = _extract(case["filing_id"], case["item"])
                self.assertEqual(item.status, "success")
                self.assertTrue(item.text.startswith(case["must_start_with"]))
                self.assertNotIn(START_TOC_WARNING, item.warnings)

                _, cross_item = _extract(case["cross_check_filing_id"], case["item"])
                self.assertIn(cross_item.status, {"success", "not_present"})
                if cross_item.status == "success":
                    self.assertNotIn(START_TOC_WARNING, cross_item.warnings)

    def test_reviewed_over_inclusion_cases_stop_before_later_items(self):
        for case in self.cases["over_inclusion"]:
            with self.subTest(issue=case["issue"], filing_id=case["filing_id"]):
                _, item = _extract(case["filing_id"], case["item"])
                self.assertEqual(item.status, "success")
                for forbidden in case["forbid_text"]:
                    self.assertNotIn(forbidden, item.text)

                _, cross_item = _extract(case["cross_check_filing_id"], case["item"])
                self.assertIn(cross_item.status, {"success", "not_present"})
                if cross_item.status == "success":
                    for forbidden in case["forbid_text"]:
                        self.assertNotIn(forbidden, cross_item.text)

    def test_reviewed_internal_toc_cases_are_partitioned(self):
        for case in self.cases["internal_toc_partition"]:
            with self.subTest(issue=case["issue"], filing_id=case["filing_id"]):
                _, item = _extract(case["filing_id"], case["item"])
                self.assertEqual(item.status, "success")
                structure = _raw_structure(case["filing_id"], case["item"])
                self.assert_internal_toc_structure(structure, case)

            with self.subTest(issue=case["issue"], filing_id=case["cross_check_filing_id"]):
                _, cross_item = _extract(case["cross_check_filing_id"], case["item"])
                self.assertIn(cross_item.status, {"success", "not_present"})
                if cross_item.status == "success":
                    structure = _raw_structure(case["cross_check_filing_id"], case["item"])
                    if structure["section_mode"] == "internal_toc":
                        self.assert_internal_toc_structure(structure, case)

    def assert_internal_toc_structure(self, structure: dict, case: dict) -> None:
        labels = [section["label"] for section in structure["sections"]]
        self.assertEqual(structure["section_mode"], "internal_toc")
        self.assertGreaterEqual(len(labels), min(case["min_sections"], 3))
        self.assertTrue(
            any(
                expected.lower() in label.lower()
                for expected in case["expected_labels"]
                for label in labels
            ),
            labels[:10],
        )

    def test_reviewed_same_filing_references_emit_recovery_actions(self):
        for case in self.cases["same_filing_reference_recovery"]:
            with self.subTest(issue=case["issue"], filing_id=case["filing_id"]):
                _, item = _extract(case["filing_id"], case["item"])
                self.assertEqual(item.status, "success")
                self.assertIn(case["required_action"], _action_keys(item))
                self.assertLess(len(item.text), 1200)


if __name__ == "__main__":
    unittest.main()
