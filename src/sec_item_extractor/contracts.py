from __future__ import annotations

from collections import Counter


EVALUATION_CONTRACT_VERSION = "evaluation_contract_v1"
RECOVERY_ACTION_CONTRACT_VERSION = "recovery_action_v1"

WARNING_CATEGORIES = {
    "Section length is outside the expected first-pass range.": "length_policy_review",
    "Start heading has TOC-like signals.": "toc_signal_review",
    "End heading has TOC-like signals.": "toc_signal_review",
    "Start heading does not contain the expected canonical title.": "title_policy_review",
    "Section appears to be a cross-reference rather than full narrative text.": "reference_recovery",
    "No heading candidate found for requested item.": "retrieval_failure",
    "Start heading was found, but no legal end boundary was found.": "boundary_failure",
}

RECOVERY_ACTION_CONTRACTS = {
    ("needs_user_confirmation", "same_filing_page_reference"): {
        "severity": "review",
        "requires_user_input": True,
        "next_step": "confirm_referenced_page_extraction",
    },
    ("needs_user_selection", "internal_item_toc_detected"): {
        "severity": "review",
        "requires_user_input": True,
        "next_step": "select_internal_heading",
    },
    ("needs_external_source", "external_or_other_document_reference"): {
        "severity": "blocked",
        "requires_user_input": True,
        "next_step": "provide_or_fetch_reference_document",
    },
    ("inspect_only", "start_toc_like_signal"): {
        "severity": "info",
        "requires_user_input": False,
        "next_step": "inspect_evidence_only",
    },
}

BASELINE_THRESHOLDS = {
    "evaluated_filings": 20,
    "max_missing_filings": 0,
    "max_failed_items": 0,
    "max_failed_gold_checks": 0,
}


def warning_category(warning: str) -> str:
    return WARNING_CATEGORIES.get(warning, "uncategorized_warning")


def warning_category_counts(warnings: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(warning_category(warning) for warning in warnings).items()))


def recovery_action_contract(action_type: str, reason: str) -> dict:
    fallback = {
        "severity": "review",
        "requires_user_input": False,
        "next_step": "inspect_action",
    }
    return RECOVERY_ACTION_CONTRACTS.get((action_type, reason), fallback)


def evaluation_gate(seed_summary: dict, gold_summary: dict | None = None) -> dict:
    summary = seed_summary.get("summary", seed_summary)
    item_counts = summary.get("item_status_counts", {})
    checks = [
        {
            "name": "seed_filings_evaluated",
            "passed": seed_summary.get("evaluated", summary.get("evaluated", 0)) >= BASELINE_THRESHOLDS["evaluated_filings"],
            "actual": seed_summary.get("evaluated", summary.get("evaluated", 0)),
            "expected": f">= {BASELINE_THRESHOLDS['evaluated_filings']}",
        },
        {
            "name": "missing_filings",
            "passed": len(seed_summary.get("missing", summary.get("missing", []))) <= BASELINE_THRESHOLDS["max_missing_filings"],
            "actual": len(seed_summary.get("missing", summary.get("missing", []))),
            "expected": f"<= {BASELINE_THRESHOLDS['max_missing_filings']}",
        },
        {
            "name": "failed_items",
            "passed": item_counts.get("failed", 0) <= BASELINE_THRESHOLDS["max_failed_items"],
            "actual": item_counts.get("failed", 0),
            "expected": f"<= {BASELINE_THRESHOLDS['max_failed_items']}",
        },
    ]
    if gold_summary is not None:
        checks.append(
            {
                "name": "failed_gold_checks",
                "passed": gold_summary.get("failed_checks", 0) <= BASELINE_THRESHOLDS["max_failed_gold_checks"],
                "actual": gold_summary.get("failed_checks", 0),
                "expected": f"<= {BASELINE_THRESHOLDS['max_failed_gold_checks']}",
            }
        )

    return {
        "contract_version": EVALUATION_CONTRACT_VERSION,
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
    }
