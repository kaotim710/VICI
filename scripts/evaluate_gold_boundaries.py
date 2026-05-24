from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import extract_items
from sec_item_extractor.contracts import warning_category_counts
from sec_item_extractor.raw_structure import raw_section_fragment, raw_structure_counts


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
    warning_counts = Counter()

    for filing in gold["filings"]:
        source_path = ROOT / filing["source_path"]
        content = source_path.read_text(encoding="utf-8", errors="replace")
        target_items = list(filing.get("items", {}).keys()) or gold["items"]
        result = extract_items(content, target_items=target_items, filing_id=filing["filing_id"])
        by_item = {item.item: item for item in result.item_results}

        for item_name, expectation in filing["items"].items():
            actual = by_item[item_name]
            warning_counts.update(actual.warnings)
            row = _evaluate_item(filing["filing_id"], item_name, expectation, content, actual)
            rows.append(row)
            passed_checks += row["passed_checks"]
            failed_checks += row["failed_checks"]

    return {
        "summary": {
            "filings": len(gold["filings"]),
            "items": len(rows),
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "warning_counts": dict(warning_counts),
            "warning_category_counts": warning_category_counts(list(warning_counts.elements())),
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
        f"Warnings: {sum(summary['warning_counts'].values())}",
        "",
        "## Warning Categories",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
    if summary["warning_category_counts"]:
        for category, count in summary["warning_category_counts"].items():
            lines.append(f"| `{category}` | {count} |")
    else:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## Boundary And Raw Structure Checks",
            "",
            "| Filing | Item | Pass | Start | End | Action | Raw tables | Raw images | Raw bytes | Failures |",
            "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
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
                    _raw_status(row["raw_table_count"], row["expected_raw_tables_min"], row["raw_table_match"]),
                    _raw_status(row["raw_image_count"], row["expected_raw_images_min"], row["raw_image_match"]),
                    str(row["raw_bytes"]),
                    _escape(", ".join(row["failures"]) or "none"),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def _evaluate_item(filing_id: str, item_name: str, expectation: dict, content: str, actual) -> dict:
    failures = []
    start_text = actual.start_evidence.text if actual.start_evidence else ""
    end_text = actual.end_evidence.text if actual.end_evidence else ""
    action_pairs = {(action.action_type, action.reason) for action in actual.recommended_actions}
    raw_structure = raw_structure_counts(content, actual)
    raw_bytes = _raw_bytes(content, actual)

    start_match = _contains(start_text, expectation.get("expected_start_contains"))
    end_match = _contains(end_text, expectation.get("expected_end_contains"))
    action_match = _action_matches(action_pairs, expectation)
    expected_raw_tables_min = expectation.get("expected_raw_tables_min")
    expected_raw_images_min = expectation.get("expected_raw_images_min")
    raw_table_match = _minimum_match(raw_structure["table_count"], expected_raw_tables_min)
    raw_image_match = _minimum_match(raw_structure["image_count"], expected_raw_images_min)

    if not start_match:
        failures.append("start_mismatch")
    if not end_match:
        failures.append("end_mismatch")
    if not action_match:
        failures.append("action_mismatch")
    if not raw_table_match:
        failures.append("raw_table_mismatch")
    if not raw_image_match:
        failures.append("raw_image_mismatch")

    total_checks = 3
    if expected_raw_tables_min is not None:
        total_checks += 1
    if expected_raw_images_min is not None:
        total_checks += 1
    failed_checks = len(failures)
    return {
        "filing_id": filing_id,
        "item": item_name,
        "passed": failed_checks == 0,
        "start_match": start_match,
        "end_match": end_match,
        "action_match": action_match,
        "raw_table_match": raw_table_match,
        "raw_image_match": raw_image_match,
        "raw_table_count": raw_structure["table_count"],
        "raw_image_count": raw_structure["image_count"],
        "raw_bytes": raw_bytes,
        "expected_raw_tables_min": expected_raw_tables_min,
        "expected_raw_images_min": expected_raw_images_min,
        "actual_start": start_text,
        "actual_end": end_text,
        "actual_actions": sorted([f"{action_type}:{reason}" for action_type, reason in action_pairs]),
        "warnings": actual.warnings,
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
        return not _user_action_pairs(action_pairs)
    return (expected_type, expected_reason) in action_pairs


def _user_action_pairs(action_pairs: set[tuple[str, str]]) -> set[tuple[str, str]]:
    return {(action_type, reason) for action_type, reason in action_pairs if action_type != "inspect_only"}


def _minimum_match(actual: int, expected_minimum: int | None) -> bool:
    if expected_minimum is None:
        return True
    return actual >= expected_minimum


def _raw_bytes(content: str, actual) -> int:
    try:
        _, _, fragment = raw_section_fragment(content, actual)
    except ValueError:
        return 0
    return len(fragment.encode("utf-8", errors="replace"))


def _status(value: bool) -> str:
    return "pass" if value else "fail"


def _raw_status(actual: int, expected_minimum: int | None, passed: bool) -> str:
    if expected_minimum is None:
        return str(actual)
    return f"{actual} ({'pass' if passed else 'fail'} >= {expected_minimum})"


def _escape(value: str) -> str:
    return value.replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
