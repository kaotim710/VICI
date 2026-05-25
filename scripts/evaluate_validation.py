from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import extract_items
from sec_item_extractor.contracts import retry_policy_contract, validation_gate, warning_category, warning_category_counts


MANIFEST_PATH = ROOT / "fixtures" / "gold" / "validation_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
SUMMARY_PATH = ROOT / "reports" / "validation_summary.json"
REPORT_PATH = ROOT / "reports" / "validation_report.md"


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    payload = evaluate_validation(manifest)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 1 if payload["missing"] else 0


def evaluate_validation(manifest: dict) -> dict:
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
        item_payloads = {}
        for item in result.item_results:
            needs_review = item.status not in {"success", "not_present"} or bool(item.warnings)
            payload = {
                "status": item.status,
                "confidence_level": item.confidence_level,
                "confidence_score": item.confidence_score,
                "text_length": len(item.text or ""),
                "warnings": item.warnings,
                "recommended_actions": [
                    {
                        "action_type": action.action_type,
                        "reason": action.reason,
                        "severity": action.severity,
                        "requires_user_input": action.requires_user_input,
                        "next_step": action.next_step,
                    }
                    for action in item.recommended_actions
                ],
            }
            if needs_review:
                payload.update(
                    {
                        "warning_categories": [warning_category(warning) for warning in item.warnings],
                        "validation_reasons": item.validation_reasons,
                        "start_evidence": _evidence_payload(item.start_evidence),
                        "end_evidence": _evidence_payload(item.end_evidence),
                        "start_snippet": _edge_snippets(item.text or "")[0],
                        "end_snippet": _edge_snippets(item.text or "")[1],
                    }
                )
            item_payloads[item.item] = payload
        rows.append(
            {
                "filing_id": filing["filing_id"],
                "ticker": filing["ticker"],
                "fiscal_year": filing["fiscal_year"],
                "status": result.status,
                "candidate_count": result.candidate_count,
                "toc_confidence": result.toc_confidence,
                "warnings": sorted({warning for item in result.item_results for warning in item.warnings}),
                "recommended_action_count": sum(len(item.recommended_actions) for item in result.item_results),
                "items": item_payloads,
            }
        )

    summary = {
        "generated": date.today().isoformat(),
        "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "evaluated_filings": len(rows),
        "missing_filings": missing,
        "item_attempts": sum(item_status_counts.values()),
        "filing_status_counts": dict(filing_status_counts),
        "item_status_counts": dict(item_status_counts),
        "confidence_level_counts": dict(confidence_level_counts),
        "warning_counts": dict(warning_counts),
        "warning_category_counts": warning_category_counts(list(warning_counts.elements())),
        "retry_policy": retry_policy_contract(),
    }
    return {"summary": summary, "evaluation_gate": validation_gate(summary), "missing": missing, "results": rows}


def _evidence_payload(evidence) -> dict | None:
    if evidence is None:
        return None
    return {
        "kind": evidence.kind,
        "offset": evidence.offset,
        "text": _compact(evidence.text, 160),
        "reasons": evidence.reasons,
        "raw_offset": evidence.raw_offset,
        "block_tag": evidence.block_tag,
    }


def _edge_snippets(text: str, limit: int = 220) -> tuple[str, str]:
    compacted = _compact(text, limit * 2)
    if len(compacted) <= limit:
        return compacted, compacted
    return _compact(text[:limit], limit), _compact(text[-limit:], limit)


def _compact(text: str, limit: int = 220) -> str:
    compacted = " ".join(text.split()).replace("|", "\\|").replace("`", "'")
    if len(compacted) <= limit:
        return compacted
    return compacted[: max(0, limit - 3)] + "..."


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Held-Out Validation Report",
        "",
        f"Generated: {summary['generated']}",
        f"Manifest: `{summary['manifest']}`",
        f"Evaluated filings: {summary['evaluated_filings']}",
        f"Missing filings: {len(summary['missing_filings'])}",
        f"Item attempts: {summary['item_attempts']}",
        "",
        "## Aggregate Counts",
        "",
        f"- Filing status: `{summary['filing_status_counts']}`",
        f"- Item status: `{summary['item_status_counts']}`",
        f"- Confidence levels: `{summary['confidence_level_counts']}`",
        f"- Warnings: `{summary['warning_counts']}`",
        f"- Warning categories: `{summary['warning_category_counts']}`",
        "",
        "## Validation Gate",
        "",
        f"- Passed: `{payload['evaluation_gate']['passed']}`",
        "",
        "| Check | Actual | Expected | Passed |",
        "| --- | ---: | --- | --- |",
        *[
            f"| `{check['name']}` | {check['actual']} | `{check['expected']}` | {check['passed']} |"
            for check in payload["evaluation_gate"]["checks"]
        ],
        "",
        "## Filings",
        "",
        "| Filing | Status | TOC | Candidates | Actions | Warnings |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in payload["results"]:
        warnings = ", ".join(row["warnings"]) if row["warnings"] else "none"
        lines.append(
            f"| `{row['filing_id']}` | {row['status']} | {row['toc_confidence']} | "
            f"{row['candidate_count']} | {row['recommended_action_count']} | {warnings} |"
        )
    lines.extend(["", "## Warning And Failed Items", ""])
    problem_count = 0
    for row in payload["results"]:
        for item, item_payload in row["items"].items():
            if item_payload["status"] in {"success", "not_present"} and not item_payload["warnings"]:
                continue
            problem_count += 1
            warnings = ", ".join(item_payload["warnings"]) if item_payload["warnings"] else "none"
            categories = ", ".join(item_payload.get("warning_categories", [])) or "none"
            actions = item_payload["recommended_actions"]
            action_text = (
                ", ".join(f"{action['action_type']}:{action['reason']}" for action in actions) if actions else "none"
            )
            lines.extend(
                [
                    f"### {row['filing_id']} Item {item}",
                    "",
                    f"- Status: `{item_payload['status']}`",
                    f"- Confidence: `{item_payload['confidence_level']}` {item_payload['confidence_score']:.2f}",
                    f"- Text length: {item_payload['text_length']}",
                    f"- Warnings: `{warnings}`",
                    f"- Warning categories: `{categories}`",
                    f"- Recommended actions: `{action_text}`",
                    f"- Validation reasons: `{', '.join(item_payload.get('validation_reasons', [])) or 'none'}`",
                    f"- Start evidence: `{_format_evidence(item_payload.get('start_evidence'))}`",
                    f"- End evidence: `{_format_evidence(item_payload.get('end_evidence'))}`",
                    f"- Start snippet: {item_payload.get('start_snippet') or 'none'}",
                    f"- End snippet: {item_payload.get('end_snippet') or 'none'}",
                    "",
                ]
            )
    if problem_count == 0:
        lines.append("No warning or failed items in this validation run.")
    lines.extend(["", "## Not Present Items", ""])
    not_present = [
        (row["filing_id"], item)
        for row in payload["results"]
        for item, item_payload in row["items"].items()
        if item_payload["status"] == "not_present"
    ]
    if not_present:
        for filing_id, item in not_present:
            lines.append(f"- `{filing_id}` Item `{item}`")
    else:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def _format_evidence(evidence: dict | None) -> str:
    if not evidence:
        return "none"
    reasons = ", ".join(evidence.get("reasons", [])) or "none"
    return f"{evidence['kind']} @ {evidence['offset']}: {evidence['text']} [{reasons}]"


if __name__ == "__main__":
    raise SystemExit(main())
