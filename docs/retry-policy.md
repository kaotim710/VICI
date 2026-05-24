# Retry Policy

This project currently uses bounded deterministic retry, not autonomous agent orchestration.

## Current Contract

- Contract version: `retry_policy_v1`
- Mode: `bounded_deterministic`
- LLM retry: disabled
- Embedding retry: disabled

## Extraction-Time Fallbacks

1. Rank all start candidates for the requested item.
2. Try each ranked candidate pair once.
3. Reject short ordered TOC-like spans and continue to the next candidate.
4. Use TOC next-item order when available.
5. Fall back to the legal item transition graph.
6. Use terminal boundaries for `Item 16`, `Item 15` without `Item 16`, or the final TOC item.
7. If no start heading exists, use TOC absence or observed-sequence absence before returning failure.

Each attempt is recorded in `candidate_attempts` as `selected` or `rejected`.

## Confidence Behavior

Confidence does not trigger autonomous re-extraction today.

- `high`: accept with evidence.
- `medium`: accept with warnings and recommended actions.
- `low`: fail or require recovery/review.

When confidence is weak, the extractor keeps the selected evidence inspectable and emits warnings plus `recommended_actions`.

## Recovery-Time Actions

Recovery only runs when explicitly called through `run_recovery_actions`.

- `same_filing_page_reference`: attempts deterministic page-range extraction, then returns `needs_review` or `blocked`.
- `internal_item_toc_detected`: asks for user selection, then extracts the selected subsection.
- `external_or_other_document_reference`: returns `deferred`.
- `start_toc_like_signal`: returns `inspect_only`.

The recovery result carries `severity`, `requires_user_input`, `next_step`, and `contract_version`.
