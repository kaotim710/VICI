from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import extract_items


GOLD_PATH = ROOT / "fixtures" / "gold" / "boundaries.seed.json"
REPORT_PATH = ROOT / "reports" / "gold_boundary_report.md"


def main() -> int:
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    payload = evaluate_gold(gold)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0 if payload["summary"]["failed_checks"] == 0 else 1


def evaluate_gold(gold: dict) -> dict:
    rows = []
    passed_checks = 0
    failed_checks = 0

    for filing in gold["filings"]:
        source_path = ROOT / filing["source_path"]
        content = source_path.read_text(encoding="utf-8", errors="replace")
        result = extract_items(content, target_items=gold["items"], filing_id=filing["filing_id"])
        by_item = {item.item: item for item in result.item_results}

        for item_name, expectation in filing["items"].items():
            actual = by_item[item_name]
            row = _evaluate_item(filing["filing_id"], item_name, expectation, actual)
            rows.append(row)
            passed_checks += row["passed_checks"]
            failed_checks += row["failed_checks"]

    return {
        "summary": {
            "filings": len(gold["filings"]),
            "items": len(rows),
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
        },
        "results": rows,
    }


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Gold Boundary Evaluation",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        f"Filings: {summary['filings']}",
        f"Items: {summary['items']}",
        f"Passed checks: {summary['passed_checks']}",
        f"Failed checks: {summary['failed_checks']}",
        "",
        "| Filing | Item | Pass | Start | End | Action | Failures |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["results"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['filing_id']}`",
                    row["item"],
                    str(row["passed"]),
                    _status(row["start_match"]),
                    _status(row["end_match"]),
                    _status(row["action_match"]),
                    _escape(", ".join(row["failures"]) or "none"),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def _evaluate_item(filing_id: str, item_name: str, expectation: dict, actual) -> dict:
    failures = []
    start_text = actual.start_evidence.text if actual.start_evidence else ""
    end_text = actual.end_evidence.text if actual.end_evidence else ""
    action_pairs = {(action.action_type, action.reason) for action in actual.recommended_actions}

    start_match = _contains(start_text, expectation.get("expected_start_contains"))
    end_match = _contains(end_text, expectation.get("expected_end_contains"))
    action_match = _action_matches(action_pairs, expectation)

    if not start_match:
        failures.append("start_mismatch")
    if not end_match:
        failures.append("end_mismatch")
    if not action_match:
        failures.append("action_mismatch")

    total_checks = 3
    failed_checks = len(failures)
    return {
        "filing_id": filing_id,
        "item": item_name,
        "passed": failed_checks == 0,
        "start_match": start_match,
        "end_match": end_match,
        "action_match": action_match,
        "actual_start": start_text,
        "actual_end": end_text,
        "actual_actions": sorted([f"{action_type}:{reason}" for action_type, reason in action_pairs]),
        "failures": failures,
        "passed_checks": total_checks - failed_checks,
        "failed_checks": failed_checks,
    }


def _contains(actual: str, expected: str | None) -> bool:
    if expected is None:
        return True
    return expected.lower() in " ".join(actual.split()).lower()


def _action_matches(action_pairs: set[tuple[str, str]], expectation: dict) -> bool:
    expected_type = expectation.get("expected_action_type")
    expected_reason = expectation.get("expected_action_reason")
    if expected_type is None and expected_reason is None:
        return not action_pairs
    return (expected_type, expected_reason) in action_pairs


def _status(value: bool) -> str:
    return "pass" if value else "fail"


def _escape(value: str) -> str:
    return value.replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
