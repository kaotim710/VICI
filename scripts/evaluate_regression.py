from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import extract_items
from sec_item_extractor.contracts import retry_policy_contract, warning_category, warning_category_counts
from sec_item_extractor.raw_structure import (
    raw_fragment_supplemental_chunk,
    raw_section_fragment,
    raw_structure_counts,
)


RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
SEED_MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
VALIDATION_MANIFEST_PATH = ROOT / "fixtures" / "gold" / "validation_filings.json"
SUMMARY_PATH = ROOT / "reports" / "regression_summary.json"
REPORT_PATH = ROOT / "reports" / "regression_report.md"


def main() -> int:
    suites = [
        ("seed", SEED_MANIFEST_PATH),
        ("validation", VALIDATION_MANIFEST_PATH),
    ]
    payload = evaluate_regression(suites)
    SUMMARY_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 1 if payload["summary"]["missing_filings"] else 0


def evaluate_regression(suites: list[tuple[str, Path]]) -> dict:
    all_rows = []
    missing = []
    status_counts = Counter()
    confidence_counts = Counter()
    warning_counts = Counter()
    warning_categories = []
    recovery_actions = Counter()
    raw_preview_available = 0
    supplemental_rows = []

    for suite_name, manifest_path in suites:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for filing in manifest["filings"]:
            path = RAW_DIR / f"{filing['filing_id']}.html"
            if not path.exists():
                missing.append({"suite": suite_name, "filing_id": filing["filing_id"]})
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            result = extract_items(content, target_items=manifest["items"], filing_id=filing["filing_id"])
            rows = _item_rows(suite_name, filing, content, result.item_results)
            all_rows.extend(rows)
            supplemental_rows.extend(row for row in rows if row["is_supplemental"])

    for row in all_rows:
        status_counts[row["status"]] += 1
        confidence_counts[row["confidence_level"]] += 1
        warning_counts.update(row["warnings"])
        warning_categories.extend(row["warning_categories"])
        raw_preview_available += 1 if row["raw_preview_available"] else 0
        for action in row["recommended_actions"]:
            recovery_actions[f"{action['action_type']}:{action['reason']}"] += 1

    summary = {
        "generated": date.today().isoformat(),
        "suites": [suite_name for suite_name, _ in suites],
        "filings_evaluated": len({(row["suite"], row["filing_id"]) for row in all_rows}),
        "missing_filings": missing,
        "item_rows": len(all_rows),
        "status_counts": dict(status_counts),
        "confidence_level_counts": dict(confidence_counts),
        "warning_counts": dict(warning_counts),
        "warning_category_counts": dict(sorted(Counter(warning_categories).items())),
        "raw_preview_available_items": raw_preview_available,
        "supplemental_items": len(supplemental_rows),
        "supplemental_section_counts": {
            f"{row['suite']}:{row['filing_id']}:{row['item']}": row["supplemental_sections"]
            for row in supplemental_rows
        },
        "recovery_action_counts": dict(sorted(recovery_actions.items())),
        "retry_policy": retry_policy_contract(),
    }
    return {"summary": summary, "items": all_rows}


def _item_rows(suite_name: str, filing: dict, content: str, item_results: list) -> list[dict]:
    rows = []
    for item in item_results:
        rows.append(_normal_item_row(suite_name, filing, content, item))
        supplemental = _supplemental_row(suite_name, filing, content, item)
        if supplemental:
            rows.append(supplemental)
    return rows


def _normal_item_row(suite_name: str, filing: dict, content: str, item) -> dict:
    raw_structure = raw_structure_counts(content, item)
    raw_bytes = _raw_bytes(content, item)
    warnings = item.warnings
    return {
        "suite": suite_name,
        "filing_id": filing["filing_id"],
        "ticker": filing.get("ticker"),
        "fiscal_year": filing.get("fiscal_year"),
        "item": item.item,
        "is_supplemental": False,
        "status": item.status,
        "confidence_level": item.confidence_level,
        "confidence_score": item.confidence_score,
        "text_length": len(item.text or ""),
        "warnings": warnings,
        "warning_categories": [warning_category(warning) for warning in warnings],
        "raw_table_count": raw_structure["table_count"],
        "raw_image_count": raw_structure["image_count"],
        "raw_bytes": raw_bytes,
        "raw_preview_available": item.status == "success" and bool(item.start_evidence),
        "supplemental_sections": 0,
        "recommended_actions": [_action_payload(action) for action in item.recommended_actions],
    }


def _supplemental_row(suite_name: str, filing: dict, content: str, item) -> dict | None:
    if item.item.upper() not in {"15", "16"} or item.status != "success":
        return None
    try:
        _, _, fragment = raw_section_fragment(content, item)
    except ValueError:
        return None
    chunk = raw_fragment_supplemental_chunk(fragment)
    if not chunk:
        return None
    return {
        "suite": suite_name,
        "filing_id": filing["filing_id"],
        "ticker": filing.get("ticker"),
        "fiscal_year": filing.get("fiscal_year"),
        "item": f"supplemental-{item.item.lower()}",
        "source_item": item.item,
        "is_supplemental": True,
        "status": "success",
        "confidence_level": "high",
        "confidence_score": 1.0,
        "text_length": len(chunk.get("text", "")),
        "warnings": [],
        "warning_categories": [],
        "raw_table_count": chunk.get("table_count", 0),
        "raw_image_count": chunk.get("image_count", 0),
        "raw_bytes": chunk.get("raw_bytes", 0),
        "raw_preview_available": True,
        "supplemental_sections": len(chunk.get("sections", [])),
        "recommended_actions": [],
    }


def _raw_bytes(content: str, item) -> int:
    try:
        _, _, fragment = raw_section_fragment(content, item)
    except ValueError:
        return 0
    return len(fragment.encode("utf-8", errors="replace"))


def _action_payload(action) -> dict:
    return {
        "action_type": action.action_type,
        "reason": action.reason,
        "severity": action.severity,
        "requires_user_input": action.requires_user_input,
        "next_step": action.next_step,
        "options": action.options,
    }


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Regression Evaluation Report",
        "",
        f"Generated: {summary['generated']}",
        f"Suites: `{', '.join(summary['suites'])}`",
        f"Evaluated filings: {summary['filings_evaluated']}",
        f"Missing filings: {len(summary['missing_filings'])}",
        f"Item rows: {summary['item_rows']}",
        "",
        "## Aggregate Counts",
        "",
        f"- Status: `{summary['status_counts']}`",
        f"- Confidence: `{summary['confidence_level_counts']}`",
        f"- Warning categories: `{summary['warning_category_counts']}`",
        f"- Raw preview available items: `{summary['raw_preview_available_items']}`",
        f"- Supplemental items: `{summary['supplemental_items']}`",
        f"- Recovery action counts: `{summary['recovery_action_counts']}`",
        "",
        "## Supplemental Coverage",
        "",
        "| Filing | Item | Sections | Tables | Images | Raw preview |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    supplemental = [row for row in payload["items"] if row["is_supplemental"]]
    if supplemental:
        for row in supplemental:
            lines.append(
                f"| `{row['suite']}:{row['filing_id']}` | `{row['item']}` | "
                f"{row['supplemental_sections']} | {row['raw_table_count']} | "
                f"{row['raw_image_count']} | {row['raw_preview_available']} |"
            )
    else:
        lines.append("| none | - | 0 | 0 | 0 | false |")

    lines.extend(
        [
            "",
            "## Warning And Recovery Readiness",
            "",
            "| Filing | Item | Confidence | Warnings | Actions | Raw media |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    problem_rows = [
        row
        for row in payload["items"]
        if row["warnings"] or row["recommended_actions"] or row["status"] not in {"success", "not_present"}
    ]
    if problem_rows:
        for row in problem_rows:
            warnings = ", ".join(row["warning_categories"]) if row["warning_categories"] else "none"
            actions = ", ".join(f"{action['action_type']}:{action['reason']}" for action in row["recommended_actions"]) or "none"
            lines.append(
                f"| `{row['suite']}:{row['filing_id']}` | `{row['item']}` | "
                f"{row['confidence_level']} {row['confidence_score']:.2f} | {warnings} | "
                f"{actions} | {row['raw_table_count']} tables / {row['raw_image_count']} images |"
            )
    else:
        lines.append("| none | - | - | none | none | 0 tables / 0 images |")

    lines.extend(
        [
            "",
            "## Per-Item Matrix",
            "",
            "| Filing | Item | Status | Confidence | Warnings | Tables | Images | Supplemental sections | Raw preview |",
            "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["items"]:
        warnings = ", ".join(row["warning_categories"]) if row["warning_categories"] else "none"
        lines.append(
            f"| `{row['suite']}:{row['filing_id']}` | `{row['item']}` | {row['status']} | "
            f"{row['confidence_level']} {row['confidence_score']:.2f} | {warnings} | "
            f"{row['raw_table_count']} | {row['raw_image_count']} | "
            f"{row['supplemental_sections']} | {row['raw_preview_available']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
