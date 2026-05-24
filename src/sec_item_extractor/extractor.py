from __future__ import annotations

import re
from dataclasses import dataclass

from .candidates import ITEM_ORDER, find_heading_candidates, infer_toc_profile, is_expected_title, legal_next_items, toc_next_items
from .cleaning import parse_document
from .contracts import recovery_action_contract
from .models import (
    CandidateAttempt,
    ConfidenceComponent,
    Evidence,
    ExtractionResult,
    HeadingCandidate,
    ItemResult,
    RecommendedAction,
)

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
    targets = [item.upper() for item in target_items] if target_items else list(ITEM_ORDER)
    candidates = find_heading_candidates(text, document.blocks)
    toc_profile = infer_toc_profile(candidates)
    item_results = [_extract_one_item(text, candidates, item, toc_profile.items) for item in targets]
    resolved = sum(1 for result in item_results if result.status in {"success", "not_present"})
    successful = sum(1 for result in item_results if result.status == "success")
    if resolved == len(item_results):
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
        toc_items=toc_profile.items,
        toc_confidence=toc_profile.confidence,
        toc_entries=toc_profile.entries,
    )


def _extract_one_item(text: str, candidates: list[HeadingCandidate], item: str, toc_items: list[str]) -> ItemResult:
    start_candidates = [candidate for candidate in candidates if candidate.item == item]
    if not start_candidates:
        if toc_items and item not in toc_items:
            return ItemResult(
                item=item,
                status="not_present",
                validation_reasons=["ITEM_NOT_DECLARED_IN_TOC"],
                confidence_level="high",
                confidence_score=1.0,
                strategy_used="toc_presence_filter_v1",
            )
        if _item_absent_from_observed_sequence(item, candidates):
            return ItemResult(
                item=item,
                status="not_present",
                validation_reasons=["ITEM_NOT_DECLARED_IN_OBSERVED_SEQUENCE"],
                confidence_level="medium",
                confidence_score=0.8,
                strategy_used="observed_sequence_presence_filter_v1",
            )
        return ItemResult(
            item=item,
            status="failed",
            validation_reasons=["START_HEADING_NOT_FOUND"],
            warnings=["No heading candidate found for requested item."],
        )

    ranked_starts = sorted(start_candidates, key=_start_rank)
    attempts: list[CandidateAttempt] = []
    for pair in _candidate_pairs(text, candidates, ranked_starts, toc_items):
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
    text: str, candidates: list[HeadingCandidate], starts: list[HeadingCandidate], toc_items: list[str]
) -> list[CandidatePair]:
    pairs = []
    for index, start in enumerate(starts):
        end, end_reasons = _find_end_candidate(text, candidates, start, toc_items)
        section_text = text[start.start : end.start].strip() if end else ""
        validation_reasons = _start_validation_reasons(start) + end_reasons
        rejection_reasons = _pair_rejection_reasons(start, end, section_text, has_later_start=index + 1 < len(starts))
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


def _find_end_candidate(
    text: str, candidates: list[HeadingCandidate], start: HeadingCandidate, toc_items: list[str]
) -> tuple[HeadingCandidate | None, list[str]]:
    if start.item == "16":
        return _terminal_end_candidate(text, start), ["TERMINAL_END_BOUNDARY_USED"]

    toc_next = set(toc_next_items(start.item, toc_items))
    legal_next = legal_next_items(start.item)
    if toc_next:
        later = [candidate for candidate in candidates if candidate.start > start.end and candidate.item in toc_next]
        non_toc = [candidate for candidate in later if not candidate.is_toc_like]
    else:
        later = []
        non_toc = []
    if not toc_next or not non_toc:
        later = [candidate for candidate in candidates if candidate.start > start.end and candidate.item in legal_next]
    if not later:
        if start.item == "15":
            return _terminal_end_candidate(text, start), ["ITEM_15_TERMINAL_END_BOUNDARY_USED"]
        if toc_items and start.item in toc_items and not toc_next:
            return _terminal_end_candidate(text, start), ["TOC_LAST_ITEM_TERMINAL_END_BOUNDARY_USED"]
        return None, ["LEGAL_END_HEADING_NOT_FOUND"]
    non_toc = [candidate for candidate in later if not candidate.is_toc_like]
    if non_toc:
        return min(non_toc, key=lambda candidate: candidate.start), ["LEGAL_END_HEADING_FOUND", "END_NOT_TOC_LIKE"]
    return min(later, key=lambda candidate: candidate.start), ["LEGAL_END_HEADING_FOUND", "END_TOC_LIKE_USED_AS_FALLBACK"]


def _terminal_end_candidate(text: str, start: HeadingCandidate) -> HeadingCandidate:
    signature = re.search(r"(?im)^signatures\s*$", text[start.end :])
    boundary = start.end + signature.start() if signature else len(text)
    return HeadingCandidate(
        item="EOF",
        start=boundary,
        end=boundary,
        text="SIGNATURES" if signature else "END_OF_DOCUMENT",
        normalized_text="SIGNATURES" if signature else "END_OF_DOCUMENT",
        reasons=["TERMINAL_BOUNDARY"],
    )


def _pair_rejection_reasons(
    start: HeadingCandidate, end: HeadingCandidate | None, section_text: str, has_later_start: bool
) -> list[str]:
    if end is None:
        return ["LEGAL_END_HEADING_NOT_FOUND"]
    if _is_likely_toc_span(start, end, section_text, has_later_start):
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
    accepted_toc_signal = _has_accepted_toc_signal(start, end, section_text)
    accepted_structured_long_section = _has_accepted_structured_long_section(start.item, section_text)
    accepted_placeholder_section = _has_short_placeholder_body(section_text)
    accepted_cross_reference = _is_cross_reference_section(section_text) and _has_strong_boundary_context(start, end)
    confidence_components = [
        ConfidenceComponent(
            name="legal_boundary_pair",
            weight=0.55,
            earned=0.55,
            passed=True,
            reason="Start heading and legal end heading were found.",
        )
    ]

    if not start.is_toc_like or accepted_toc_signal:
        confidence_components.append(
            ConfidenceComponent(
                name="start_not_toc_like",
                weight=0.15,
                earned=0.15,
                passed=True,
                reason="Start heading has no unaccepted TOC-like signals.",
            )
        )
        reasons.append("START_TOC_LIKE_ACCEPTED_BY_SECTION_BODY" if start.is_toc_like else "START_NOT_TOC_LIKE")
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

    if is_expected_title(start.item, start.normalized_text) or accepted_structured_long_section or accepted_placeholder_section:
        confidence_components.append(
            ConfidenceComponent(
                name="start_expected_title",
                weight=0.10,
                earned=0.10,
                passed=True,
                reason="Start heading contains the expected title or an accepted section-specific variant.",
            )
        )
        if not is_expected_title(start.item, start.normalized_text):
            reasons.append("START_TITLE_VARIANT_ACCEPTED_BY_SECTION_CONTEXT")
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

    min_length, max_length = _length_bounds(start.item)
    section_length = len(section_text)
    if min_length <= section_length <= max_length:
        confidence_components.append(
            ConfidenceComponent(
                name="section_length_reasonable",
                weight=0.10,
                earned=0.10,
                passed=True,
                reason="Section length is within the item-specific first-pass expected range.",
            )
        )
        reasons.append("SECTION_LENGTH_REASONABLE")
    elif (
        section_length < min_length
        and (_has_strong_boundary_context(start, end) or accepted_toc_signal or _has_reference_language(section_text))
    ) or accepted_placeholder_section:
        confidence_components.append(
            ConfidenceComponent(
                name="section_length_reasonable",
                weight=0.10,
                earned=0.10,
                passed=True,
                reason="Section is shorter than the first-pass range but is bounded by normal item headings.",
            )
        )
        reasons.append("SECTION_LENGTH_SHORT_ACCEPTED_BY_PLACEHOLDER_OR_BOUNDARY_CONTEXT")
    elif section_length > max_length and accepted_structured_long_section:
        confidence_components.append(
            ConfidenceComponent(
                name="section_length_reasonable",
                weight=0.10,
                earned=0.10,
                passed=True,
                reason="Section is longer than the first-pass range but contains structured exhibit or internal heading content.",
            )
        )
        reasons.append("SECTION_LENGTH_LONG_ACCEPTED_AS_STRUCTURED_SECTION")
    else:
        confidence_components.append(
            ConfidenceComponent(
                name="section_length_reasonable",
                weight=0.10,
                earned=0.0,
                passed=False,
                reason="Section length is outside the item-specific first-pass expected range.",
            )
        )
        warnings.append("Section length is outside the expected first-pass range.")

    if accepted_cross_reference:
        reasons.append("CROSS_REFERENCE_ACCEPTED_BY_BOUNDARY_CONTEXT")
    elif _is_cross_reference_section(section_text):
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

    recommended_actions = _recommended_actions(start, end, section_text, warnings)
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
        recommended_actions=recommended_actions,
    )


def _start_rank(candidate: HeadingCandidate) -> tuple[int, int, int, int]:
    toc_penalty = 1 if candidate.is_toc_like else 0
    dense_penalty = 1 if "TOC_DENSE_ITEM_CLUSTER" in candidate.reasons else 0
    near_toc_penalty = 1 if "NEAR_TABLE_OF_CONTENTS_LABEL" in candidate.reasons else 0
    title_penalty = 0 if is_expected_title(candidate.item, candidate.normalized_text) else 1
    return (toc_penalty, dense_penalty, near_toc_penalty, title_penalty, candidate.start)


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


def _is_likely_toc_span(
    start: HeadingCandidate, end: HeadingCandidate, section_text: str, has_later_start: bool
) -> bool:
    if len(section_text) >= 800 or _is_cross_reference_section(section_text):
        return False
    if _span_has_body_text(start.item, section_text):
        return False

    explicit_toc_pair = _has_explicit_toc_signal(start) and _has_explicit_toc_signal(end)
    if explicit_toc_pair:
        return True

    dense_pair = "TOC_DENSE_ITEM_CLUSTER" in start.reasons and "TOC_DENSE_ITEM_CLUSTER" in end.reasons
    return has_later_start and (start.is_toc_like or end.is_toc_like or dense_pair)


def _has_explicit_toc_signal(candidate: HeadingCandidate) -> bool:
    return any(
        reason in candidate.reasons
        for reason in ("TOC_DOT_LEADER_PAGE_NUMBER", "TOC_PAGE_NUMBER_PATTERN", "TOC_TABLE_ROW_PAGE_NUMBER")
    )


def _span_has_body_text(item: str, section_text: str) -> bool:
    for line in (" ".join(raw_line.split()) for raw_line in section_text.splitlines()):
        if not line or re.fullmatch(r"\d{1,4}", line):
            continue
        if re.match(r"(?i)^(?:part\s+[ivx]+\s*)?item\s+", line):
            continue
        if _is_placeholder_line(line):
            return True
        if re.search(r"\b(?:see|refer|reference|appears|presented|included|incorporated)\b", line, flags=re.IGNORECASE):
            return True
        if is_expected_title(item, line):
            continue
        if len(line.split()) >= 8:
            return True
    return False


def _item_absent_from_observed_sequence(item: str, candidates: list[HeadingCandidate]) -> bool:
    if item not in ITEM_ORDER:
        return False
    ordered_candidates = [
        candidate
        for candidate in sorted(candidates, key=lambda current: current.start)
        if candidate.item in ITEM_ORDER and not candidate.is_toc_like and is_expected_title(candidate.item, candidate.normalized_text)
    ]
    observed = {candidate.item: candidate for candidate in ordered_candidates}
    if item in observed or len(observed) < 8:
        return False

    index = ITEM_ORDER.index(item)
    previous_items = [previous for previous in reversed(ITEM_ORDER[:index]) if previous in observed]
    next_items = [next_item for next_item in ITEM_ORDER[index + 1 :] if next_item in observed]
    if not previous_items:
        return False
    if next_items:
        return observed[previous_items[0]].start < observed[next_items[0]].start
    return item == ITEM_ORDER[-1] and previous_items[0] == "15"


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


def _has_short_placeholder_body(section_text: str) -> bool:
    compact = " ".join(section_text.split())
    if len(compact) > 800:
        return False
    return any(_is_placeholder_line(line) for line in compact.split(". "))


def _is_placeholder_line(line: str) -> bool:
    normalized = re.sub(r"[^a-z ]+", " ", line.lower())
    normalized = " ".join(normalized.split())
    return normalized in {
        "none",
        "reserved",
        "not applicable",
        "not applicable bank of america",
    } or normalized.endswith(" not applicable") or (normalized.startswith("reserved") and len(normalized.split()) <= 6)


def _has_accepted_toc_signal(start: HeadingCandidate, end: HeadingCandidate, section_text: str) -> bool:
    if not start.is_toc_like:
        return False
    if _has_explicit_toc_signal(start):
        return False
    if end.is_toc_like and _has_explicit_toc_signal(end):
        return False
    return len(section_text) < 1200 and _span_has_body_text(start.item, section_text)


def _has_accepted_structured_long_section(item: str, section_text: str) -> bool:
    _, max_length = _length_bounds(item)
    if len(section_text) <= max_length:
        return False
    if item == "15" and _has_exhibit_language(section_text):
        return True
    return len(_internal_heading_options(section_text, limit=4)) >= 3


def _length_bounds(item: str) -> tuple[int, int]:
    if item in {"1", "1A", "7"}:
        return 1000, 250000
    if item in {"7A", "8"}:
        return 1000, 500000
    if item in {"2", "3", "5", "6", "9A"}:
        return 100, 250000
    if item in {"10", "11", "12", "13", "14", "15", "16"}:
        return 20, 250000
    return 20, 50000


def _has_strong_boundary_context(start: HeadingCandidate, end: HeadingCandidate) -> bool:
    end_title_matches = end.item == "EOF" or is_expected_title(end.item, end.normalized_text)
    return (
        not start.is_toc_like
        and not end.is_toc_like
        and is_expected_title(start.item, start.normalized_text)
        and end_title_matches
    )


def _recommended_actions(
    start: HeadingCandidate, end: HeadingCandidate, section_text: str, warnings: list[str]
) -> list[RecommendedAction]:
    actions: list[RecommendedAction] = []
    section_length = len(section_text)
    has_cross_reference_warning = "Section appears to be a cross-reference rather than full narrative text." in warnings
    has_cross_reference = _is_cross_reference_section(section_text)
    has_reference = _has_reference_language(section_text)
    needs_external_reference = (
        section_length < _length_bounds(start.item)[0]
        and start.item in {"1", "1A", "7", "7A", "8"}
        and not has_cross_reference_warning
        and not has_cross_reference
        and has_reference
    )

    if has_cross_reference:
        actions.append(
            _recommended_action(
                action_type="needs_user_confirmation",
                reason="same_filing_page_reference",
                description="Confirm whether to follow the referenced page range and attempt secondary extraction.",
                options=["extract_referenced_pages", "accept_cross_reference_text"],
            )
        )

    if section_length > 250000 and start.item != "15" and (
        "Start heading does not contain the expected canonical title." in warnings
        or _has_accepted_structured_long_section(start.item, section_text)
    ):
        actions.append(
            _recommended_action(
                action_type="needs_user_selection",
                reason="internal_item_toc_detected",
                description="Review likely internal Item 7 headings and choose the subsection to extract.",
                options=_internal_heading_options(section_text),
            )
        )

    if "Start heading has TOC-like signals." in warnings:
        actions.append(
            _recommended_action(
                action_type="inspect_only",
                reason="start_toc_like_signal",
                description="Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.",
            )
        )

    if has_reference and not has_cross_reference_warning and not has_cross_reference and not needs_external_reference:
        actions.append(
            _recommended_action(
                action_type="inspect_only",
                reason="section_reference_detected",
                description="Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.",
                options=["inspect_references", "accept_current_section"],
            )
        )

    if _has_exhibit_language(section_text):
        actions.append(
            _recommended_action(
                action_type="inspect_only",
                reason="exhibit_index_detected",
                description="Review the exhibit-related text or table captured inside this section.",
                options=["inspect_exhibit_index", "accept_current_section"],
            )
        )

    if needs_external_reference:
        actions.append(
            _recommended_action(
                action_type="needs_external_source",
                reason="external_or_other_document_reference",
                description="Short section likely requires a referenced annual report, exhibit, proxy, or other source document.",
                options=["fetch_referenced_document", "upload_reference_document", "accept_short_text"],
            )
        )

    return actions


def _has_reference_language(section_text: str) -> bool:
    compact = " ".join(section_text.split()).lower()
    if not compact:
        return False
    reference_patterns = (
        r"\bincorporated\s+herein\s+by\s+reference\b",
        r"\bsee\s+(?:the\s+)?(?:annual report|proxy statement|exhibit index|note\s+\d+|part\s+[ivx]+|item\s+\d)",
        r"\brefer(?:red|s|ring)?\s+to\s+(?:the\s+)?(?:annual report|proxy statement|exhibit index|note\s+\d+|part\s+[ivx]+|item\s+\d)",
        r"\breference\s+is\s+made\s+to\s+(?:the\s+)?section\s+entitled\b",
        r"\bappears?\s+on\s+pages?\s+\d+",
    )
    return any(re.search(pattern, compact) for pattern in reference_patterns)


def _has_exhibit_language(section_text: str) -> bool:
    compact = " ".join(section_text.split()).lower()
    return bool(re.search(r"\bexhibit(?:s| index)?\b", compact))


def _recommended_action(action_type: str, reason: str, description: str, options: list[str] | None = None) -> RecommendedAction:
    contract = recovery_action_contract(action_type, reason)
    return RecommendedAction(
        action_type=action_type,
        reason=reason,
        description=description,
        options=options or [],
        severity=contract["severity"],
        requires_user_input=contract["requires_user_input"],
        next_step=contract["next_step"],
    )


def _internal_heading_options(section_text: str, limit: int = 12) -> list[str]:
    options = []
    seen = set()
    for raw_line in section_text.splitlines():
        line = " ".join(raw_line.split())
        if not _looks_like_internal_heading(line):
            continue
        normalized = line.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        options.append(line[:120])
        if len(options) >= limit:
            break
    return options


def _looks_like_internal_heading(line: str) -> bool:
    if not 8 <= len(line) <= 140:
        return False
    lower = line.lower()
    if lower.startswith("item "):
        return False
    if re.search(r"\.{2,}\s*\d+\s*$", line):
        return False
    alpha_count = sum(1 for character in line if character.isalpha())
    if alpha_count < 5:
        return False
    uppercase_ratio = sum(1 for character in line if character.isupper()) / max(alpha_count, 1)
    title_like = line[:1].isupper() and not line.endswith(".")
    return uppercase_ratio > 0.55 or title_like
