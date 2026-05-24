from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from export_seed_extractions_md import _compact, _edge_snippets
from sec_item_extractor import extract_items


MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
REPORT_PATH = ROOT / "reports" / "warning_audit_report.md"
SNIPPET_CHARS = 220


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(manifest)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


def build_report(manifest: dict) -> str:
    warning_items = []
    rejected_pair_items = []
    warning_counts = Counter()
    missing = []

    for filing in manifest["filings"]:
        path = RAW_DIR / f"{filing['filing_id']}.html"
        if not path.exists():
            missing.append(filing["filing_id"])
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        result = extract_items(content, target_items=manifest["items"], filing_id=filing["filing_id"])
        for item in result.item_results:
            if item.warnings:
                warning_counts.update(item.warnings)
                warning_items.append((filing, result, item))
            if any(attempt.decision == "rejected" for attempt in item.candidate_attempts):
                rejected_pair_items.append((filing, result, item))

    lines = [
        "# Warning Audit Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: seed 10-K filings with non-empty item warnings.",
        "",
        f"Warning items: {len(warning_items)}",
        f"Items with rejected candidate pairs: {len(rejected_pair_items)}",
        f"Missing filings: {len(missing)}",
        "",
        "## Warning Counts",
        "",
        "| Warning | Count |",
        "| --- | ---: |",
        *[f"| `{warning}` | {count} |" for warning, count in sorted(warning_counts.items())],
        "",
        "## Audit Items",
        "",
    ]

    for filing, result, item in warning_items:
        lines.extend(_audit_item(filing, result, item))

    lines.extend(["## Rejected Candidate Pairs", ""])
    for filing, result, item in rejected_pair_items:
        lines.extend(_rejected_pair_item(filing, result, item))

    return "\n".join(lines).rstrip() + "\n"


def _audit_item(filing: dict, result, item) -> list[str]:
    warnings = ", ".join(f"`{warning}`" for warning in item.warnings)
    start_snippet, end_snippet = _edge_snippets(item.text or "", SNIPPET_CHARS)
    lines = [
        f"### {filing['filing_id']} Item {item.item}",
        "",
        f"- Ticker: `{filing['ticker']}`",
        f"- Fiscal year: `{filing['fiscal_year']}`",
        f"- Overall status: `{result.status}`",
        f"- Confidence: `{item.confidence_level}` `{item.confidence_score:.2f}`",
        f"- Text length: `{len(item.text or '')}`",
        f"- Warnings: {warnings}",
    ]
    if item.start_evidence:
        lines.append(f"- Start evidence: `{_compact(item.start_evidence.text, 160)}`")
        lines.append(f"- Start evidence reasons: `{', '.join(item.start_evidence.reasons)}`")
    if item.end_evidence:
        lines.append(f"- End evidence: `{_compact(item.end_evidence.text, 160)}`")
        lines.append(f"- End evidence reasons: `{', '.join(item.end_evidence.reasons)}`")

    lines.extend(["", "Confidence components:", ""])
    lines.extend(
        [
            "| Component | Earned | Weight | Passed |",
            "| --- | ---: | ---: | --- |",
            *[
                f"| `{component.name}` | {component.earned:.2f} | {component.weight:.2f} | {component.passed} |"
                for component in item.confidence_components
            ],
            "",
            "Selected candidate attempt:",
            "",
        ]
    )
    selected = next((attempt for attempt in item.candidate_attempts if attempt.decision == "selected"), None)
    if selected:
        lines.extend(
            [
                f"- Validation reasons: `{', '.join(selected.validation_reasons)}`",
                f"- Attempt warnings: `{', '.join(selected.warnings) if selected.warnings else 'none'}`",
            ]
        )
    else:
        lines.append("- No selected candidate attempt recorded.")

    lines.extend(
        [
            "",
            "Start snippet:",
            "",
            f"> {start_snippet}",
            "",
            "End snippet:",
            "",
            f"> {end_snippet}",
            "",
        ]
    )
    return lines


def _rejected_pair_item(filing: dict, result, item) -> list[str]:
    rejected_attempts = [attempt for attempt in item.candidate_attempts if attempt.decision == "rejected"]
    lines = [
        f"### {filing['filing_id']} Item {item.item}",
        "",
        f"- Ticker: `{filing['ticker']}`",
        f"- Fiscal year: `{filing['fiscal_year']}`",
        f"- Final status: `{item.status}`",
        f"- Final confidence: `{item.confidence_level}` `{item.confidence_score:.2f}`",
        f"- Final start evidence: `{_compact(item.start_evidence.text, 160) if item.start_evidence else 'none'}`",
        "",
        "| Decision | Start Evidence | End Evidence | Reasons | Warnings |",
        "| --- | --- | --- | --- | --- |",
    ]
    for attempt in rejected_attempts:
        lines.append(
            "| "
            + " | ".join(
                [
                    attempt.decision,
                    f"`{_compact(attempt.start_evidence.text, 100)}`",
                    f"`{_compact(attempt.end_evidence.text, 100) if attempt.end_evidence else 'none'}`",
                    f"`{', '.join(attempt.validation_reasons)}`",
                    f"`{', '.join(attempt.warnings) if attempt.warnings else 'none'}`",
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


if __name__ == "__main__":
    raise SystemExit(main())
