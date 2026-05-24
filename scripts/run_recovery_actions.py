from __future__ import annotations

import argparse
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
from sec_item_extractor.recovery import RecoveryResult, run_recovery_actions


MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
REPORT_PATH = ROOT / "reports" / "recovery_action_report.md"
SNIPPET_CHARS = 220


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic recovery actions for seed filings.")
    parser.add_argument(
        "--select",
        action="append",
        default=[],
        metavar="FILING_ID:ITEM=HEADING",
        help="Select an internal heading for one item, for example bac_2023_10k:7=Executive Summary.",
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    selections = _parse_selections(args.select)
    results, missing = evaluate_recovery(manifest, selections)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_markdown(results, missing), encoding="utf-8")
    print(json.dumps(_summary(results, missing), indent=2))
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


def evaluate_recovery(
    manifest: dict, selections: dict[tuple[str | None, str], str] | None = None
) -> tuple[list[tuple[dict, RecoveryResult]], list[str]]:
    rows = []
    missing = []
    for filing in manifest["filings"]:
        path = RAW_DIR / f"{filing['filing_id']}.html"
        if not path.exists():
            missing.append(filing["filing_id"])
            continue

        content = path.read_text(encoding="utf-8", errors="replace")
        extraction = extract_items(content, target_items=manifest["items"], filing_id=filing["filing_id"])
        for recovery in run_recovery_actions(content, extraction, selections=selections):
            rows.append((filing, recovery))
    return rows, missing


def render_markdown(results: list[tuple[dict, RecoveryResult]], missing: list[str]) -> str:
    status_counts = Counter(recovery.status for _, recovery in results)
    reason_counts = Counter(recovery.reason for _, recovery in results)
    lines = [
        "# Recovery Action Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: deterministic recovery actions for seed filings with recommended actions.",
        "",
        f"Recovery actions: {len(results)}",
        f"Missing filings: {len(missing)}",
        "",
        f"Contract version: `{RecoveryResult.__dataclass_fields__['contract_version'].default}`",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
        *[f"| `{status}` | {count} |" for status, count in sorted(status_counts.items())],
        "",
        "## Reason Counts",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
        *[f"| `{reason}` | {count} |" for reason, count in sorted(reason_counts.items())],
        "",
        "## Actions",
        "",
        "| Filing | Item | Action | Reason | Severity | User Input | Status | Before | After | Page Range | Selection |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for filing, recovery in results:
        lines.append(_summary_row(filing, recovery))

    lines.extend(["", "## Details", ""])
    for filing, recovery in results:
        lines.extend(_detail_section(filing, recovery))

    if missing:
        lines.extend(["## Missing Filings", "", *[f"- `{filing_id}`" for filing_id in missing], ""])

    return "\n".join(lines).rstrip() + "\n"


def _summary(results: list[tuple[dict, RecoveryResult]], missing: list[str]) -> dict:
    return {
        "recovery_actions": len(results),
        "missing_filings": len(missing),
        "status_counts": dict(sorted(Counter(recovery.status for _, recovery in results).items())),
        "reason_counts": dict(sorted(Counter(recovery.reason for _, recovery in results).items())),
    }


def _summary_row(filing: dict, recovery: RecoveryResult) -> str:
    page_range = f"{recovery.page_range[0]}-{recovery.page_range[1]}" if recovery.page_range else "none"
    after = str(recovery.after_length) if recovery.after_length is not None else "none"
    selection = _compact(recovery.selected_option or "none", 80)
    cells = [
        f"`{filing['filing_id']}`",
        recovery.item,
        f"`{recovery.action_type}`",
        f"`{recovery.reason}`",
        f"`{recovery.severity}`",
        "yes" if recovery.requires_user_input else "no",
        f"`{recovery.status}`",
        str(recovery.before_length),
        after,
        page_range,
        selection,
    ]
    return "| " + " | ".join(cells) + " |"


def _detail_section(filing: dict, recovery: RecoveryResult) -> list[str]:
    lines = [
        f"### {filing['filing_id']} Item {recovery.item} - {recovery.reason}",
        "",
        f"- Ticker: `{filing['ticker']}`",
        f"- Fiscal year: `{filing['fiscal_year']}`",
        f"- Status: `{recovery.status}`",
        f"- Severity: `{recovery.severity}`",
        f"- Requires user input: `{recovery.requires_user_input}`",
        f"- Next step: `{recovery.next_step or 'none'}`",
        f"- Contract version: `{recovery.contract_version}`",
        f"- Message: {recovery.message}",
        f"- Before length: `{recovery.before_length}`",
    ]
    if recovery.after_length is not None:
        lines.append(f"- After length: `{recovery.after_length}`")
    if recovery.page_range:
        lines.append(f"- Parsed page range: `{recovery.page_range[0]}-{recovery.page_range[1]}`")
    if recovery.selected_option:
        lines.append(f"- Selected option: `{_compact(recovery.selected_option, 120)}`")
    if recovery.options:
        lines.append(f"- Options: `{', '.join(recovery.options)}`")
    if recovery.evidence:
        lines.append(f"- Evidence: `{', '.join(recovery.evidence)}`")

    if recovery.extracted_text:
        start_snippet, end_snippet = _edge_snippets(recovery.extracted_text, SNIPPET_CHARS)
        lines.extend(
            [
                "",
                "Recovered start snippet:",
                "",
                f"> {start_snippet}",
                "",
                "Recovered end snippet:",
                "",
                f"> {end_snippet}",
            ]
        )
    lines.append("")
    return lines


def _parse_selections(raw_values: list[str]) -> dict[tuple[str | None, str], str]:
    selections: dict[tuple[str | None, str], str] = {}
    for raw in raw_values:
        target, _, heading = raw.partition("=")
        filing_and_item = target.split(":", 1)
        if len(filing_and_item) != 2 or not heading:
            raise SystemExit(f"Invalid --select value: {raw}")
        filing_id, item = filing_and_item
        selections[(filing_id or None, item.upper())] = heading
    return selections


if __name__ == "__main__":
    raise SystemExit(main())
