from __future__ import annotations

from .candidates import TARGET_ITEMS, find_heading_candidates, is_expected_title, legal_next_items
from .cleaning import html_to_text
from .models import Evidence, ExtractionResult, HeadingCandidate, ItemResult

PARSER_VERSION = "deterministic_text_v1"


def extract_items(content: str, target_items: list[str] | None = None, filing_id: str | None = None) -> ExtractionResult:
    text = html_to_text(content)
    targets = [item.upper() for item in (target_items or sorted(TARGET_ITEMS))]
    candidates = find_heading_candidates(text)
    item_results = [_extract_one_item(text, candidates, item) for item in targets]
    successful = sum(1 for result in item_results if result.status == "success")
    if successful == len(item_results):
        status = "success"
    elif successful:
        status = "partial"
    else:
        status = "failed"
    warnings = []
    if not candidates:
        warnings.append("NO_ITEM_HEADINGS_FOUND")
    return ExtractionResult(
        filing_id=filing_id,
        status=status,
        parser_version=PARSER_VERSION,
        item_results=item_results,
        warnings=warnings,
    )


def _extract_one_item(text: str, candidates: list[HeadingCandidate], item: str) -> ItemResult:
    start_candidates = [candidate for candidate in candidates if candidate.item == item]
    if not start_candidates:
        return ItemResult(
            item=item,
            status="failed",
            validation_reasons=["START_HEADING_NOT_FOUND"],
            warnings=["No heading candidate found for requested item."],
        )

    ranked_starts = sorted(start_candidates, key=_start_rank)
    for start in ranked_starts:
        end = _find_end_candidate(candidates, start)
        if end:
            return _build_success_result(text, start, end)

    best = ranked_starts[0]
    return ItemResult(
        item=item,
        status="failed",
        start_offset=best.start,
        start_evidence=_evidence("start_heading", best),
        validation_reasons=["LEGAL_END_HEADING_NOT_FOUND"],
        warnings=["Start heading was found, but no legal end boundary was found."],
        confidence_level="low",
        confidence_score=0.2,
    )


def _find_end_candidate(candidates: list[HeadingCandidate], start: HeadingCandidate) -> HeadingCandidate | None:
    legal_next = legal_next_items(start.item)
    later = [candidate for candidate in candidates if candidate.start > start.end and candidate.item in legal_next]
    non_toc = [candidate for candidate in later if not candidate.is_toc_like]
    pool = non_toc or later
    return min(pool, key=lambda candidate: candidate.start) if pool else None


def _build_success_result(text: str, start: HeadingCandidate, end: HeadingCandidate) -> ItemResult:
    section_text = text[start.start : end.start].strip()
    reasons = ["START_HEADING_FOUND", "LEGAL_END_HEADING_FOUND"]
    warnings: list[str] = []
    score = 0.55

    if not start.is_toc_like:
        score += 0.15
        reasons.append("START_NOT_TOC_LIKE")
    else:
        warnings.append("Start heading has TOC-like signals.")

    if not end.is_toc_like:
        score += 0.10
        reasons.append("END_NOT_TOC_LIKE")
    else:
        warnings.append("End heading has TOC-like signals.")

    if is_expected_title(start.item, start.normalized_text):
        score += 0.10
    else:
        warnings.append("Start heading does not contain the expected canonical title.")

    if 1000 <= len(section_text) <= 250000:
        score += 0.10
        reasons.append("SECTION_LENGTH_REASONABLE")
    else:
        warnings.append("Section length is outside the expected first-pass range.")

    confidence_level = "high" if score >= 0.85 else "medium" if score >= 0.60 else "low"
    return ItemResult(
        item=start.item,
        status="success",
        text=section_text,
        start_offset=start.start,
        end_offset=end.start,
        confidence_level=confidence_level,
        confidence_score=round(min(score, 1.0), 2),
        start_evidence=_evidence("start_heading", start),
        end_evidence=_evidence("end_heading", end),
        validation_reasons=reasons,
        warnings=warnings,
    )


def _start_rank(candidate: HeadingCandidate) -> tuple[int, int, int]:
    toc_penalty = 1 if candidate.is_toc_like else 0
    title_penalty = 0 if is_expected_title(candidate.item, candidate.normalized_text) else 1
    return (toc_penalty, title_penalty, candidate.start)


def _evidence(kind: str, candidate: HeadingCandidate) -> Evidence:
    return Evidence(
        kind=kind,
        item=candidate.item,
        offset=candidate.start,
        text=candidate.text,
        reasons=candidate.reasons,
    )

