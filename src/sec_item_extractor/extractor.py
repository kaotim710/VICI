from __future__ import annotations

import re
from dataclasses import dataclass

from .candidates import TARGET_ITEMS, find_heading_candidates, is_expected_title, legal_next_items
from .cleaning import parse_document
from .models import CandidateAttempt, ConfidenceComponent, Evidence, ExtractionResult, HeadingCandidate, ItemResult

PARSER_VERSION = "deterministic_text_v1"


@dataclass(frozen=True)
class CandidatePair:
    start: HeadingCandidate
    end: HeadingCandidate | None
    section_text: str
    validation_reasons: list[str]
    rejection_reasons: list[str]


def extract_items(content: str, target_items: list[str] | None = None, filing_id: str | None = None) -> ExtractionResult:
    document = parse_document(content)
    text = document.text
    targets = [item.upper() for item in (target_items or sorted(TARGET_ITEMS))]
    candidates = find_heading_candidates(text, document.blocks)
    item_results = [_extract_one_item(text, candidates, item) for item in targets]
    successful = sum(1 for result in item_results if result.status == "success")
    if successful == len(item_results):
        status = "success"
    elif successful:
        status = "partial"
    else:
        status = "failed"
    warnings = list(document.warnings)
    if not candidates:
        warnings.append("NO_ITEM_HEADINGS_FOUND")
    return ExtractionResult(
        filing_id=filing_id,
        status=status,
        parser_version=PARSER_VERSION,
        item_results=item_results,
        warnings=warnings,
        candidate_count=len(candidates),
        document_warnings=document.warnings,
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
    attempts: list[CandidateAttempt] = []
    for pair in _candidate_pairs(text, candidates, ranked_starts):
        if pair.end and not pair.rejection_reasons:
            attempts.append(_attempt_from_pair(item, "selected", pair))
            return _build_success_result(text, pair.start, pair.end, attempts)
        attempts.append(_attempt_from_pair(item, "rejected", pair))

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
        candidate_attempts=attempts,
    )


def _candidate_pairs(
    text: str, candidates: list[HeadingCandidate], starts: list[HeadingCandidate]
) -> list[CandidatePair]:
    pairs = []
    for start in starts:
        end, end_reasons = _find_end_candidate(candidates, start)
        section_text = text[start.start : end.start].strip() if end else ""
        validation_reasons = _start_validation_reasons(start) + end_reasons
        rejection_reasons = _pair_rejection_reasons(start, end, section_text)
        pairs.append(
            CandidatePair(
                start=start,
                end=end,
                section_text=section_text,
                validation_reasons=validation_reasons,
                rejection_reasons=rejection_reasons,
            )
        )
    return pairs


def _find_end_candidate(candidates: list[HeadingCandidate], start: HeadingCandidate) -> tuple[HeadingCandidate | None, list[str]]:
    legal_next = legal_next_items(start.item)
    later = [candidate for candidate in candidates if candidate.start > start.end and candidate.item in legal_next]
    if not later:
        return None, ["LEGAL_END_HEADING_NOT_FOUND"]
    non_toc = [candidate for candidate in later if not candidate.is_toc_like]
    if non_toc:
        return min(non_toc, key=lambda candidate: candidate.start), ["LEGAL_END_HEADING_FOUND", "END_NOT_TOC_LIKE"]
    return min(later, key=lambda candidate: candidate.start), ["LEGAL_END_HEADING_FOUND", "END_TOC_LIKE_USED_AS_FALLBACK"]


def _pair_rejection_reasons(
    start: HeadingCandidate, end: HeadingCandidate | None, section_text: str
) -> list[str]:
    if end is None:
        return ["LEGAL_END_HEADING_NOT_FOUND"]
    if _is_likely_toc_span(start, end, section_text):
        return ["REJECTED_SHORT_ORDERED_TOC_SPAN"]
    return []


def _attempt_from_pair(item: str, decision: str, pair: CandidatePair) -> CandidateAttempt:
    warnings = _attempt_warnings(pair.start, pair.end)
    if "REJECTED_SHORT_ORDERED_TOC_SPAN" in pair.rejection_reasons:
        warnings.append("Candidate pair is too short and follows an ordered TOC-like transition.")
    return CandidateAttempt(
        item=item,
        decision=decision,
        start_evidence=_evidence("start_heading", pair.start),
        end_evidence=_evidence("end_heading", pair.end) if pair.end else None,
        validation_reasons=pair.validation_reasons + pair.rejection_reasons,
        warnings=warnings,
    )


def _build_success_result(
    text: str, start: HeadingCandidate, end: HeadingCandidate, attempts: list[CandidateAttempt]
) -> ItemResult:
    section_text = text[start.start : end.start].strip()
    reasons = ["START_HEADING_FOUND", "LEGAL_END_HEADING_FOUND"]
    warnings: list[str] = []
    confidence_components = [
        ConfidenceComponent(
            name="legal_boundary_pair",
            weight=0.55,
            earned=0.55,
            passed=True,
            reason="Start heading and legal end heading were found.",
        )
    ]

    if not start.is_toc_like:
        confidence_components.append(
            ConfidenceComponent(
                name="start_not_toc_like",
                weight=0.15,
                earned=0.15,
                passed=True,
                reason="Start heading has no TOC-like signals.",
            )
        )
        reasons.append("START_NOT_TOC_LIKE")
    else:
        confidence_components.append(
            ConfidenceComponent(
                name="start_not_toc_like",
                weight=0.15,
                earned=0.0,
                passed=False,
                reason="Start heading has TOC-like signals.",
            )
        )
        warnings.append("Start heading has TOC-like signals.")

    if not end.is_toc_like:
        confidence_components.append(
            ConfidenceComponent(
                name="end_not_toc_like",
                weight=0.10,
                earned=0.10,
                passed=True,
                reason="End heading has no TOC-like signals.",
            )
        )
        reasons.append("END_NOT_TOC_LIKE")
    else:
        confidence_components.append(
            ConfidenceComponent(
                name="end_not_toc_like",
                weight=0.10,
                earned=0.0,
                passed=False,
                reason="End heading has TOC-like signals.",
            )
        )
        warnings.append("End heading has TOC-like signals.")

    if is_expected_title(start.item, start.normalized_text):
        confidence_components.append(
            ConfidenceComponent(
                name="start_expected_title",
                weight=0.10,
                earned=0.10,
                passed=True,
                reason="Start heading contains the expected canonical title.",
            )
        )
    else:
        confidence_components.append(
            ConfidenceComponent(
                name="start_expected_title",
                weight=0.10,
                earned=0.0,
                passed=False,
                reason="Start heading does not contain the expected canonical title.",
            )
        )
        warnings.append("Start heading does not contain the expected canonical title.")

    if 1000 <= len(section_text) <= 250000:
        confidence_components.append(
            ConfidenceComponent(
                name="section_length_reasonable",
                weight=0.10,
                earned=0.10,
                passed=True,
                reason="Section length is within the first-pass expected range.",
            )
        )
        reasons.append("SECTION_LENGTH_REASONABLE")
    else:
        confidence_components.append(
            ConfidenceComponent(
                name="section_length_reasonable",
                weight=0.10,
                earned=0.0,
                passed=False,
                reason="Section length is outside the first-pass expected range.",
            )
        )
        warnings.append("Section length is outside the expected first-pass range.")

    if _is_cross_reference_section(section_text):
        confidence_components.append(
            ConfidenceComponent(
                name="not_cross_reference_only",
                weight=0.0,
                earned=0.0,
                passed=False,
                reason="Section appears to cross-reference another page range rather than contain full narrative text.",
            )
        )
        warnings.append("Section appears to be a cross-reference rather than full narrative text.")

    score = sum(component.earned for component in confidence_components)
    confidence_level = "high" if score >= 0.85 else "medium" if score >= 0.60 else "low"
    return ItemResult(
        item=start.item,
        status="success",
        text=section_text,
        start_offset=start.start,
        end_offset=end.start,
        confidence_level=confidence_level,
        confidence_score=round(min(score, 1.0), 2),
        confidence_components=confidence_components,
        start_evidence=_evidence("start_heading", start),
        end_evidence=_evidence("end_heading", end),
        candidate_attempts=attempts,
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
        raw_offset=candidate.raw_start,
        block_index=candidate.block_index,
        block_tag=candidate.block_tag,
    )


def _start_validation_reasons(candidate: HeadingCandidate) -> list[str]:
    reasons = ["START_HEADING_FOUND"]
    if candidate.is_toc_like:
        reasons.append("START_TOC_LIKE")
    else:
        reasons.append("START_NOT_TOC_LIKE")
    if is_expected_title(candidate.item, candidate.normalized_text):
        reasons.append("START_EXPECTED_TITLE_MATCH")
    else:
        reasons.append("START_EXPECTED_TITLE_MISSING")
    return reasons


def _attempt_warnings(start: HeadingCandidate, end: HeadingCandidate | None) -> list[str]:
    warnings = []
    if start.is_toc_like:
        warnings.append("Start heading has TOC-like signals.")
    if not is_expected_title(start.item, start.normalized_text):
        warnings.append("Start heading does not contain the expected canonical title.")
    if end and end.is_toc_like:
        warnings.append("End heading has TOC-like signals.")
    return warnings


def _is_likely_toc_span(start: HeadingCandidate, end: HeadingCandidate, section_text: str) -> bool:
    ordered_toc_like = "TOC_DENSE_ITEM_CLUSTER" in start.reasons and "TOC_DENSE_ITEM_CLUSTER" in end.reasons
    return ordered_toc_like and not _is_cross_reference_section(section_text) and len(section_text) < 800


def _is_cross_reference_section(section_text: str) -> bool:
    compact = " ".join(section_text.split()).lower()
    if len(compact) > 1200:
        return False
    has_page_range = bool(re.search(r"\bpages?\s+\d+\s*[–-]\s*\d+\b", compact))
    has_reference_language = any(
        phrase in compact
        for phrase in (
            "appears on page",
            "appears on pages",
            "is incorporated",
            "such information should be read in conjunction",
        )
    )
    return has_page_range and has_reference_language
