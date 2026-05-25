from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "gold" / "eval_filings.json"
SUMMARY_PATH = ROOT / "reports" / "deployed_eval_summary.json"
REPORT_PATH = ROOT / "reports" / "deployed_eval_report.md"
DEFAULT_BASE_URL = "https://vici-ten.vercel.app"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the 48-filing eval set against a deployed VICI site.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--limit", type=int, default=0, help="Optional number of manifest rows to run.")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds between deployed API calls.")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = manifest["filings"][: args.limit or None]
    payload = run_eval(manifest, rows, base_url=args.base_url.rstrip("/"), sleep_seconds=args.sleep)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 1 if payload["summary"]["failed_requests"] else 0


def run_eval(manifest: dict, rows: list[dict], base_url: str, sleep_seconds: float) -> dict:
    results = []
    request_status_counts = Counter()
    item_status_counts = Counter()
    warning_counts = Counter()
    warning_category_counts = Counter()
    sec_format_status_counts = Counter()

    for index, filing in enumerate(rows):
        if index and sleep_seconds > 0:
            time.sleep(sleep_seconds)
        url = _extract_url(base_url, filing)
        started = time.perf_counter()
        try:
            payload = _fetch_json(url)
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            row = _result_row(filing, url, payload, elapsed_ms)
        except Exception as error:
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            row = {
                "filing_id": filing["filing_id"],
                "ticker": filing["ticker"],
                "fiscal_year": filing["fiscal_year"],
                "url": url,
                "elapsed_ms": elapsed_ms,
                "request_status": "failed",
                "error": str(error),
                "items": {},
                "warning_count": 0,
                "warnings": [],
                "warning_categories": {},
                "sec_format_review_count": 0,
            }
        results.append(row)
        request_status_counts[row["request_status"]] += 1
        warning_counts.update(row.get("warnings", []))
        warning_category_counts.update(row.get("warning_categories", {}))
        for item in row.get("items", {}).values():
            item_status_counts[item["status"]] += 1
            status = item.get("sec_format", {}).get("status")
            if status:
                sec_format_status_counts[status] += 1

    summary = {
        "generated": date.today().isoformat(),
        "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "base_url": base_url,
        "planned_filings": len(manifest["filings"]),
        "evaluated_filings": len(rows),
        "successful_requests": request_status_counts.get("success", 0),
        "failed_requests": request_status_counts.get("failed", 0),
        "request_status_counts": dict(request_status_counts),
        "item_status_counts": dict(item_status_counts),
        "warning_counts": dict(warning_counts),
        "warning_category_counts": dict(warning_category_counts),
        "sec_format_status_counts": dict(sec_format_status_counts),
    }
    return {"summary": summary, "results": results}


def _extract_url(base_url: str, filing: dict) -> str:
    query = urllib.parse.urlencode({"ticker": filing["ticker"], "year": filing["fiscal_year"]})
    return f"{base_url}/api/sec/extract?{query}"


def _fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = response.read().decode("utf-8", errors="replace")
            status = response.status
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {_compact(body, 180)}") from error
    if status >= 400:
        raise RuntimeError(f"HTTP {status}: {_compact(body, 180)}")
    return json.loads(body)


def _result_row(filing: dict, url: str, payload: dict, elapsed_ms: int) -> dict:
    if payload.get("status") != "success":
        return {
            "filing_id": filing["filing_id"],
            "ticker": filing["ticker"],
            "fiscal_year": filing["fiscal_year"],
            "url": url,
            "elapsed_ms": elapsed_ms,
            "request_status": "failed",
            "error": payload.get("message") or payload.get("error") or "non_success_payload",
            "items": {},
            "warning_count": 0,
            "warnings": [],
            "warning_categories": {},
            "sec_format_review_count": 0,
        }

    items = {}
    warnings = []
    warning_categories = Counter()
    for item in payload.get("result", {}).get("item_results", []):
        item_warnings = item.get("warnings", [])
        warnings.extend(item_warnings)
        for warning in item_warnings:
            warning_categories[_category_for_warning(warning)] += 1
        items[item["item"]] = {
            "status": item.get("status"),
            "confidence_level": item.get("confidence_level"),
            "confidence_score": item.get("confidence_score"),
            "text_length": len(item.get("text") or ""),
            "warnings": item_warnings,
            "sec_format": item.get("sec_format", {}),
            "strategy_trace": item.get("strategy_trace", []),
        }

    summary = payload.get("summary", {})
    return {
        "filing_id": filing["filing_id"],
        "ticker": filing["ticker"],
        "fiscal_year": filing["fiscal_year"],
        "url": url,
        "elapsed_ms": elapsed_ms,
        "request_status": "success",
        "filing_status": summary.get("status"),
        "toc_confidence": summary.get("toc_confidence"),
        "candidate_count": summary.get("candidate_count"),
        "item_count": summary.get("item_count"),
        "warning_count": len(warnings),
        "warnings": sorted(set(warnings)),
        "warning_categories": dict(warning_categories),
        "sec_format_review_count": summary.get("sec_format_review_count", 0),
        "items": items,
    }


def _category_for_warning(warning: str) -> str:
    if "TOC" in warning or "table of contents" in warning.lower():
        return "toc_boundary_review"
    if "length" in warning.lower() or "short" in warning.lower():
        return "length_policy_review"
    if "reference" in warning.lower() or "incorporated" in warning.lower():
        return "reference_recovery"
    if "title" in warning.lower() or "heading" in warning.lower():
        return "title_policy_review"
    return "other"


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Deployed Eval Set Report",
        "",
        f"Generated: {summary['generated']}",
        f"Manifest: `{summary['manifest']}`",
        f"Base URL: `{summary['base_url']}`",
        f"Evaluated filings: {summary['evaluated_filings']} / {summary['planned_filings']}",
        f"Successful requests: {summary['successful_requests']}",
        f"Failed requests: {summary['failed_requests']}",
        "",
        "## Aggregate Counts",
        "",
        f"- Request status: `{summary['request_status_counts']}`",
        f"- Item status: `{summary['item_status_counts']}`",
        f"- Warnings: `{summary['warning_counts']}`",
        f"- Warning categories: `{summary['warning_category_counts']}`",
        f"- SEC item format statuses: `{summary['sec_format_status_counts']}`",
        "",
        "## Filings",
        "",
        "| Filing | Request | TOC | Candidates | Warnings | SEC format reviews | Error |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["results"]:
        lines.append(
            f"| `{row['filing_id']}` | {row['request_status']} | {row.get('toc_confidence', 'n/a')} | "
            f"{row.get('candidate_count', 0) or 0} | {row.get('warning_count', 0)} | "
            f"{row.get('sec_format_review_count', 0)} | {_compact(row.get('error', ''), 120)} |"
        )

    lines.extend(["", "## Warning Items", ""])
    problem_count = 0
    for row in payload["results"]:
        for item, item_payload in row.get("items", {}).items():
            if item_payload["status"] in {"success", "not_present"} and not item_payload["warnings"]:
                continue
            problem_count += 1
            lines.extend(
                [
                    f"### {row['filing_id']} Item {item}",
                    "",
                    f"- Status: `{item_payload['status']}`",
                    f"- Confidence: `{item_payload['confidence_level']}` {item_payload['confidence_score']}",
                    f"- Text length: {item_payload['text_length']}",
                    f"- Warnings: `{', '.join(item_payload['warnings']) or 'none'}`",
                    f"- SEC format: `{item_payload.get('sec_format', {}).get('status', 'unknown')}`",
                    "",
                ]
            )
    if problem_count == 0:
        lines.append("No warning or failed items in this deployed eval run.")
    return "\n".join(lines) + "\n"


def _compact(text: str, limit: int = 220) -> str:
    compacted = " ".join(str(text or "").split()).replace("|", "\\|").replace("`", "'")
    if len(compacted) <= limit:
        return compacted
    return compacted[: max(0, limit - 3)] + "..."


if __name__ == "__main__":
    raise SystemExit(main())
