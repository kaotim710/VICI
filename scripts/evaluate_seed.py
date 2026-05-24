from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import extract_items
from sec_item_extractor.contracts import evaluation_gate, retry_policy_contract, warning_category_counts


MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
SUMMARY_PATH = ROOT / "reports" / "evaluation_summary.json"


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    payload = evaluate_seed(manifest)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(evaluation_summary(payload), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    return 1 if payload["missing"] or not payload["evaluation_gate"]["passed"] else 0


def evaluate_seed(manifest: dict) -> dict:
    rows = []
    missing = []
    filing_status_counts = Counter()
    item_status_counts = Counter()
    confidence_level_counts = Counter()
    warning_counts = Counter()

    for filing in manifest["filings"]:
        path = RAW_DIR / f"{filing['filing_id']}.html"
        if not path.exists():
            missing.append(filing["filing_id"])
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        result = extract_items(content, target_items=manifest["items"], filing_id=filing["filing_id"])
        filing_status_counts[result.status] += 1
        for item in result.item_results:
            item_status_counts[item.status] += 1
            confidence_level_counts[item.confidence_level] += 1
            warning_counts.update(item.warnings)
        rows.append(
            {
                "filing_id": filing["filing_id"],
                "status": result.status,
                "candidate_count": result.candidate_count,
                "toc_confidence": result.toc_confidence,
                "toc_items": result.toc_items,
                "toc_entries": [
                    {
                        "item": entry.item,
                        "title": entry.title,
                        "page_number": entry.page_number,
                        "offset": entry.offset,
                    }
                    for entry in result.toc_entries
                ],
                "items": {
                    item.item: {
                        "status": item.status,
                        "confidence_level": item.confidence_level,
                        "confidence_score": item.confidence_score,
                        "text_length": len(item.text or ""),
                        "confidence_components": [
                            {
                                "name": component.name,
                                "earned": component.earned,
                                "weight": component.weight,
                                "passed": component.passed,
                            }
                            for component in item.confidence_components
                        ],
                        "warnings": item.warnings,
                        "recommended_actions": [
                            {
                                "action_type": action.action_type,
                                "reason": action.reason,
                                "severity": action.severity,
                                "requires_user_input": action.requires_user_input,
                                "next_step": action.next_step,
                                "options": action.options,
                            }
                            for action in item.recommended_actions
                        ],
                    }
                    for item in result.item_results
                },
            }
        )

    payload = {
        "evaluated": len(rows),
        "missing": missing,
        "summary": {
            "filing_status_counts": dict(filing_status_counts),
            "item_status_counts": dict(item_status_counts),
            "confidence_level_counts": dict(confidence_level_counts),
            "warning_counts": dict(warning_counts),
            "warning_category_counts": warning_category_counts(list(warning_counts.elements())),
        },
        "results": rows,
    }
    payload["evaluation_gate"] = evaluation_gate(payload)
    return payload


def evaluation_summary(payload: dict, gold_payload: dict | None = None) -> dict:
    item_counts = payload["summary"]["item_status_counts"]
    gate = evaluation_gate(payload, gold_payload["summary"] if gold_payload else None)
    summary = {
        "generated": date.today().isoformat(),
        "evaluated_filings": payload["evaluated"],
        "missing_filings": payload["missing"],
        "item_attempts": sum(item_counts.values()),
        "filing_status_counts": payload["summary"]["filing_status_counts"],
        "item_status_counts": item_counts,
        "confidence_level_counts": payload["summary"]["confidence_level_counts"],
        "warning_counts": payload["summary"]["warning_counts"],
        "warning_category_counts": payload["summary"]["warning_category_counts"],
        "retry_policy": retry_policy_contract(),
        "evaluation_gate": gate,
    }
    if gold_payload:
        summary["gold_boundary"] = gold_payload["summary"]
    return summary


if __name__ == "__main__":
    raise SystemExit(main())
