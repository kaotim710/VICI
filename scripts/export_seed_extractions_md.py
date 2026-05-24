from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import extract_items


MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
REPORT_PATH = ROOT / "reports" / "seed_extraction_report.md"
SNIPPET_CHARS = 260


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report = build_report(manifest)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


def build_report(manifest: dict) -> str:
    items = manifest["items"]
    rows = []
    detail_sections = []
    missing = []

    for filing in manifest["filings"]:
        path = RAW_DIR / f"{filing['filing_id']}.html"
        if not path.exists():
            missing.append(filing["filing_id"])
            continue

        content = path.read_text(encoding="utf-8", errors="replace")
        result = extract_items(content, target_items=manifest["items"], filing_id=filing["filing_id"])
        rows.append(_summary_row(filing, result))
        detail_sections.append(_detail_section(filing, result))

    lines = [
        "# Seed 10-K Extraction Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        f"Scope: 20 seed 10-K filings, extracting {len(items)} configured 10-K items.",
        "",
        f"Evaluated filings: {len(rows)}",
        f"Missing filings: {len(missing)}",
        "",
    ]
    if missing:
        lines.extend(["Missing filing IDs:", "", *[f"- `{filing_id}`" for filing_id in missing], ""])

    lines.extend(
        [
            "## Summary",
            "",
            "| Filing | Ticker | Year | Overall | " + " | ".join(f"Item {item}" for item in items) + " |",
            "| --- | --- | ---: | --- | " + " | ".join("---" for _ in items) + " |",
            *rows,
            "",
            "## Details",
            "",
            *detail_sections,
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _summary_row(filing: dict, result) -> str:
    by_item = {item.item: item for item in result.item_results}
    cells = [
        f"`{filing['filing_id']}`",
        filing["ticker"],
        str(filing["fiscal_year"]),
        result.status,
        *[_item_summary_cell(by_item.get(item.item)) for item in result.item_results],
    ]
    return "| " + " | ".join(cells) + " |"


def _item_summary_cell(item) -> str:
    if not item:
        return "missing"
    return f"{item.status} / {item.confidence_level} {item.confidence_score:.2f}"


def _detail_section(filing: dict, result) -> str:
    lines = [
        f"### {filing['filing_id']}",
        "",
        f"- Ticker: `{filing['ticker']}`",
        f"- Fiscal year: `{filing['fiscal_year']}`",
        f"- Overall status: `{result.status}`",
        f"- Candidate count: `{result.candidate_count}`",
        "",
    ]
    for item in result.item_results:
        lines.extend(_item_detail(item))
    return "\n".join(lines)


def _item_detail(item) -> list[str]:
    warnings = ", ".join(f"`{warning}`" for warning in item.warnings) if item.warnings else "none"
    text_length = len(item.text or "")
    lines = [
        f"#### Item {item.item}",
        "",
        f"- Status: `{item.status}`",
        f"- Confidence: `{item.confidence_level}` `{item.confidence_score:.2f}`",
        f"- Text length: `{text_length}`",
        f"- Warnings: {warnings}",
    ]
    if item.start_evidence:
        lines.append(f"- Start evidence: `{_compact(item.start_evidence.text, 120)}`")
    if item.end_evidence:
        lines.append(f"- End evidence: `{_compact(item.end_evidence.text, 120)}`")
    if item.recommended_actions:
        actions = ", ".join(f"`{action.action_type}:{action.reason}`" for action in item.recommended_actions)
        lines.append(f"- Recommended actions: {actions}")
    start_snippet, end_snippet = _edge_snippets(item.text or "", SNIPPET_CHARS)
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


def _edge_snippets(value: str, limit: int) -> tuple[str, str]:
    compacted = " ".join(value.split())
    if not compacted:
        return "", ""
    start = _compact(compacted, limit)
    if len(compacted) <= limit:
        return start, start
    return start, _escape_markdown_cell("..." + compacted[-(limit - 3) :].lstrip())


def _compact(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return _escape_markdown_cell(value)
    return _escape_markdown_cell(value[: limit - 3].rstrip() + "...")


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("`", "'")


if __name__ == "__main__":
    raise SystemExit(main())
