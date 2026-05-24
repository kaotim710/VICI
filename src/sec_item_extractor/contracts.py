from __future__ import annotations

from collections import Counter
from copy import deepcopy


EVALUATION_CONTRACT_VERSION = "evaluation_contract_v1"
RECOVERY_ACTION_CONTRACT_VERSION = "recovery_action_v1"
RETRY_POLICY_CONTRACT_VERSION = "retry_policy_v1"

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
    ("inspect_only", "section_reference_detected"): {
        "severity": "info",
        "requires_user_input": False,
        "next_step": "inspect_references",
    },
    ("inspect_only", "exhibit_index_detected"): {
        "severity": "info",
        "requires_user_input": False,
        "next_step": "inspect_exhibit_index",
    },
}

BASELINE_THRESHOLDS = {
    "evaluated_filings": 20,
    "max_missing_filings": 0,
    "max_failed_items": 0,
    "max_failed_gold_checks": 0,
}

RETRY_POLICY = {
    "contract_version": RETRY_POLICY_CONTRACT_VERSION,
    "mode": "bounded_deterministic",
    "llm_enabled": False,
    "embedding_enabled": False,
    "principle": "Retry only across finite deterministic candidates; low confidence emits evidence and recovery actions instead of autonomous re-extraction.",
    "confidence_thresholds": {
        "high": {"minimum_score": 0.85, "behavior": "accept_with_evidence"},
        "medium": {"minimum_score": 0.60, "behavior": "accept_with_warnings_and_actions"},
        "low": {"minimum_score": 0.0, "behavior": "fail_or_require_recovery"},
    },
    "steps": [
        {
            "name": "candidate_start_ranking",
            "trigger": "start candidates exist for requested item",
            "budget": "one attempt per ranked start candidate",
            "strategy": "rank non-TOC, non-dense, expected-title candidates before earlier weaker candidates",
            "on_failure": "try next ranked start candidate",
            "records": ["candidate_attempts"],
        },
        {
            "name": "toc_presence_filter",
            "trigger": "no start candidate and TOC profile is available",
            "budget": "single deterministic check",
            "strategy": "mark item not_present when item is absent from the TOC item list",
            "on_failure": "fall through to observed sequence filter",
            "records": ["validation_reasons", "strategy_used"],
        },
        {
            "name": "observed_sequence_presence_filter",
            "trigger": "no start candidate and no decisive TOC absence signal",
            "budget": "single deterministic check",
            "strategy": "mark item not_present when a long observed item sequence skips the requested item",
            "on_failure": "return retrieval failure",
            "records": ["validation_reasons", "strategy_used"],
        },
        {
            "name": "toc_boundary_fallback",
            "trigger": "start candidate selected and TOC next item exists",
            "budget": "bounded by TOC next-item window",
            "strategy": "prefer non-TOC candidates for next items declared by the TOC",
            "on_failure": "fall through to legal transition graph",
            "records": ["validation_reasons"],
        },
        {
            "name": "legal_graph_boundary_fallback",
            "trigger": "TOC boundary is missing or weak",
            "budget": "bounded by legal next-item set",
            "strategy": "find the earliest legal next item after the start candidate",
            "on_failure": "try terminal boundary where legally allowed",
            "records": ["validation_reasons"],
        },
        {
            "name": "terminal_boundary_fallback",
            "trigger": "terminal item or final TOC item has no legal next heading",
            "budget": "single SIGNATURES/EOF search",
            "strategy": "use SIGNATURES when present, otherwise EOF",
            "on_failure": "return boundary failure",
            "records": ["validation_reasons"],
        },
        {
            "name": "confidence_scoring",
            "trigger": "a candidate pair is selected",
            "budget": "single deterministic score",
            "strategy": "score legal boundary, TOC signals, expected title, length policy, and cross-reference signals",
            "on_failure": "emit warnings and recommended actions; do not autonomously retry",
            "records": ["confidence_components", "warnings", "recommended_actions"],
        },
        {
            "name": "recovery_action_runner",
            "trigger": "caller explicitly runs recovery actions",
            "budget": "one deterministic runner per recommended action",
            "strategy": "run page-reference extraction, internal heading selection, deferred external-source handling, or inspect-only actions",
            "on_failure": "return blocked/deferred/needs_review status",
            "records": ["RecoveryResult"],
        },
    ],
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


def retry_policy_contract() -> dict:
    return deepcopy(RETRY_POLICY)


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
