from __future__ import annotations

import re
from dataclasses import dataclass, replace

from .candidates import (
    ITEM_ORDER,
    find_heading_candidates,
    infer_cross_reference_entries,
    infer_page_start_offsets,
    infer_toc_profile,
    is_expected_title,
    legal_next_items,
    toc_next_items,
)
from .cleaning import parse_document
from .contracts import recovery_action_contract
from .models import (
    CandidateAttempt,
    ConfidenceComponent,
    CrossReferenceEntry,
    Evidence,
    ExtractionResult,
    HeadingCandidate,
    ItemSpan,
    ItemResult,
    RecommendedAction,
    NarrativeBlock,
    StrategyDecision,
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
    cross_reference_entries = infer_cross_reference_entries(document.blocks)
    page_starts = infer_page_start_offsets(document.blocks)
    item_results = [
        _extract_one_item(text, document.blocks, candidates, item, toc_profile.items, cross_reference_entries, page_starts)
        for item in targets
    ]
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


def _extract_one_item(
    text: str,
    blocks: list[NarrativeBlock],
    candidates: list[HeadingCandidate],
    item: str,
    toc_items: list[str],
    cross_reference_entries: list[CrossReferenceEntry],
    page_starts: dict[int, tuple[int, int]],
) -> ItemResult:
    cross_reference_result = _cross_reference_composite_result(text, blocks, item, cross_reference_entries, page_starts)
    if cross_reference_result:
        return _with_strategy_trace(
            cross_reference_result,
            [
                _strategy_decision(
                    "cross_reference_index",
                    "selected",
                    "Form 10-K cross-reference index supplied item evidence.",
                    [f"strategy={cross_reference_result.strategy_used}", f"pages_or_spans={len(cross_reference_result.spans)}"],
                    cross_reference_result.strategy_used,
                ),
                _strategy_decision(
                    "confidence_scoring",
                    "completed",
                    f"Confidence {cross_reference_result.confidence_level} {cross_reference_result.confidence_score:.2f}.",
                    _confidence_trace_signals(cross_reference_result),
                ),
            ],
        )

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
                strategy_trace=[
                    _strategy_decision(
                        "candidate_retrieval",
                        "miss",
                        "No start heading candidate found for item.",
                        [f"total_candidates={len(candidates)}", "toc_profile_available=true"],
                    ),
                    _strategy_decision(
                        "presence_filter",
                        "selected",
                        "Item is not declared in the detected TOC item list.",
                        [f"toc_items={','.join(toc_items)}"],
                        "toc_presence_filter_v1",
                    ),
                ],
            )
        if _item_absent_from_observed_sequence(item, candidates):
            return ItemResult(
                item=item,
                status="not_present",
                validation_reasons=["ITEM_NOT_DECLARED_IN_OBSERVED_SEQUENCE"],
                confidence_level="medium",
                confidence_score=0.8,
                strategy_used="observed_sequence_presence_filter_v1",
                strategy_trace=[
                    _strategy_decision(
                        "candidate_retrieval",
                        "miss",
                        "No start heading candidate found for item.",
                        [f"total_candidates={len(candidates)}", "observed_sequence_available=true"],
                    ),
                    _strategy_decision(
                        "presence_filter",
                        "selected",
                        "Observed non-TOC item sequence skips this item.",
                        ["legal item order remained coherent"],
                        "observed_sequence_presence_filter_v1",
                    ),
                ],
            )
        return ItemResult(
            item=item,
            status="failed",
            validation_reasons=["START_HEADING_NOT_FOUND"],
            warnings=["No heading candidate found for requested item."],
            strategy_trace=[
                _strategy_decision(
                    "candidate_retrieval",
                    "failed",
                    "No deterministic start candidate was found.",
                    [f"total_candidates={len(candidates)}"],
                ),
            ],
        )

    ranked_starts = sorted(start_candidates, key=_start_rank)
    attempts: list[CandidateAttempt] = []
    for pair in _candidate_pairs(text, candidates, ranked_starts, toc_items):
        if pair.end and not pair.rejection_reasons:
            attempts.append(_attempt_from_pair(item, "selected", pair))
            result = _build_success_result(text, pair.start, pair.end, attempts)
            return _with_strategy_trace(
                result,
                [
                    _strategy_decision(
                        "candidate_retrieval",
                        "completed",
                        "Start heading candidates were retrieved deterministically.",
                        [f"start_candidates={len(start_candidates)}", f"total_candidates={len(candidates)}"],
                    ),
                    _strategy_decision(
                        "candidate_start_ranking",
                        "completed",
                        "Start candidates were ranked by TOC, cross-reference, title, and offset signals.",
                        _rank_trace_signals(ranked_starts),
                    ),
                    _strategy_decision(
                        "boundary_reconstruction",
                        "selected",
                        "Legal next-item boundary was selected.",
                        pair.validation_reasons,
                        result.strategy_used,
                    ),
                    _strategy_decision(
                        "confidence_scoring",
                        "completed",
                        f"Confidence {result.confidence_level} {result.confidence_score:.2f}.",
                        _confidence_trace_signals(result),
                    ),
                ],
            )
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
        strategy_trace=[
            _strategy_decision(
                "candidate_retrieval",
                "completed",
                "Start heading candidates were retrieved deterministically.",
                [f"start_candidates={len(start_candidates)}", f"total_candidates={len(candidates)}"],
            ),
            _strategy_decision(
                "candidate_start_ranking",
                "completed",
                "Start candidates were ranked but no legal end boundary could be selected.",
                _rank_trace_signals(ranked_starts),
            ),
            _strategy_decision(
                "boundary_reconstruction",
                "failed",
                "No legal end boundary was found after bounded candidate attempts.",
                [f"attempts={len(attempts)}"],
            ),
        ],
    )


def _cross_reference_composite_result(
    text: str,
    blocks: list[NarrativeBlock],
    item: str,
    entries: list[CrossReferenceEntry],
    page_starts: dict[int, tuple[int, int]],
) -> ItemResult | None:
    entry = next((candidate for candidate in entries if candidate.item == item), None)
    if entry is None:
        return None
    if item in {"1", "1A"}:
        return None

    if not entry.pages and entry.note:
        section_text = f"{entry.title}\n\n{entry.note}".strip()
        evidence = Evidence(
            kind="cross_reference_index",
            item=item,
            offset=blocks[entry.block_index].clean_start if entry.block_index is not None else 0,
            text=entry.title,
            reasons=["CROSS_REFERENCE_INDEX_NOTE"],
            block_index=entry.block_index,
            block_tag=blocks[entry.block_index].tag if entry.block_index is not None else None,
        )
        return ItemResult(
            item=item,
            status="success",
            text=section_text,
            start_offset=evidence.offset,
            end_offset=evidence.offset + len(section_text),
            confidence_level="medium",
            confidence_score=0.7,
            start_evidence=evidence,
            validation_reasons=["CROSS_REFERENCE_NOTE_ONLY_ITEM"],
            warnings=["Item is incorporated or cross-referenced rather than fully contained in this filing."],
            recommended_actions=[
                _recommended_action(
                    action_type="needs_external_source",
                    reason="external_or_other_document_reference",
                    description="Cross-reference index points this item to an incorporated reference.",
                    options=["fetch_referenced_document", "accept_cross_reference_text"],
                )
            ],
            strategy_used="cross_reference_index_note_v1",
        )

    if not entry.pages:
        return None

    spans = _cross_reference_page_spans(text, blocks, item, entry, page_starts)
    if not spans:
        return None

    if len(spans) == 1 and item in {"1", "1A"}:
        return None

    section_text = "\n\n".join(span.text for span in spans if span.text.strip()).strip()
    if not section_text:
        return None
    start_evidence = spans[0].start_evidence
    end_evidence = spans[-1].end_evidence
    components = [
        ConfidenceComponent(
            name="cross_reference_index_pages",
            weight=0.70,
            earned=0.70,
            passed=True,
            reason="Form 10-K cross-reference index supplied page-level evidence.",
        ),
        ConfidenceComponent(
            name="page_boundaries_resolved",
            weight=0.20,
            earned=0.20,
            passed=True,
            reason="Referenced pages were mapped to filing page boundaries.",
        ),
    ]
    score = sum(component.earned for component in components)
    warnings = []
    if len(spans) > 1:
        warnings.append("Item reconstructed from multiple non-contiguous cross-reference pages.")
    return ItemResult(
        item=item,
        status="success",
        text=section_text,
        start_offset=spans[0].start_offset,
        end_offset=spans[-1].end_offset,
        confidence_level="high" if score >= 0.85 else "medium",
        confidence_score=round(score, 2),
        confidence_components=components,
        start_evidence=start_evidence,
        end_evidence=end_evidence,
        validation_reasons=["CROSS_REFERENCE_INDEX_COMPOSITE_ITEM"],
        warnings=warnings,
        recommended_actions=[
            _recommended_action(
                action_type="inspect_only",
                reason="section_reference_detected",
                description="Review cross-reference-derived page spans before accepting the composite item.",
                options=["inspect_composite_spans", "accept_current_section"],
            )
        ]
        if len(spans) > 1
        else [],
        strategy_used="cross_reference_index_composite_v1",
        spans=spans,
    )


def _cross_reference_page_spans(
    text: str,
    blocks: list[NarrativeBlock],
    item: str,
    entry: CrossReferenceEntry,
    page_starts: dict[int, tuple[int, int]],
) -> list[ItemSpan]:
    spans: list[ItemSpan] = []
    for page in entry.pages:
        if page not in page_starts:
            continue
        start, start_block_index = page_starts[page]
        end, end_block_index = _page_end_offset(text, blocks, page, page_starts)
        if end <= start:
            continue
        span_text = text[start:end].strip()
        if not span_text:
            continue
        start_evidence = Evidence(
            kind="cross_reference_page_start",
            item=item,
            offset=start,
            text=f"Page {page}",
            reasons=["CROSS_REFERENCE_INDEX_PAGE"],
            raw_offset=blocks[start_block_index].raw_start,
            block_index=start_block_index,
            block_tag=blocks[start_block_index].tag,
        )
        end_evidence = Evidence(
            kind="cross_reference_page_end",
            item=item,
            offset=end,
            text=f"Page {page + 1}" if page + 1 in page_starts else "END_OF_DOCUMENT",
            reasons=["CROSS_REFERENCE_INDEX_PAGE_BOUNDARY"],
            raw_offset=blocks[end_block_index].raw_start if end_block_index is not None else None,
            block_index=end_block_index,
            block_tag=blocks[end_block_index].tag if end_block_index is not None else None,
        )
        spans.append(
            ItemSpan(
                label=f"{entry.title or f'Item {item}'} - page {page}",
                text=span_text,
                start_offset=start,
                end_offset=end,
                page=page,
                start_evidence=start_evidence,
                end_evidence=end_evidence,
                validation_reasons=["CROSS_REFERENCE_PAGE_SPAN"],
            )
        )
    return _merge_contiguous_spans(spans)


def _page_end_offset(
    text: str, blocks: list[NarrativeBlock], page: int, page_starts: dict[int, tuple[int, int]]
) -> tuple[int, int | None]:
    for next_page in range(page + 1, page + 12):
        if next_page in page_starts:
            return page_starts[next_page][0], page_starts[next_page][1]
    return len(text), None


def _merge_contiguous_spans(spans: list[ItemSpan]) -> list[ItemSpan]:
    if not spans:
        return []
    merged = [spans[0]]
    for span in spans[1:]:
        previous = merged[-1]
        if previous.page is not None and span.page == previous.page + 1 and previous.end_offset == span.start_offset:
            merged[-1] = ItemSpan(
                label=f"{previous.label} to page {span.page}",
                text=f"{previous.text}\n\n{span.text}".strip(),
                start_offset=previous.start_offset,
                end_offset=span.end_offset,
                page=previous.page,
                start_evidence=previous.start_evidence,
                end_evidence=span.end_evidence,
                validation_reasons=["CROSS_REFERENCE_PAGE_RANGE_SPAN"],
            )
        else:
            merged.append(span)
    return merged


def _candidate_pairs(
    text: str, candidates: list[HeadingCandidate], starts: list[HeadingCandidate], toc_items: list[str]
) -> list[CandidatePair]:
    pairs = []
    for start in starts:
        end, end_reasons = _find_end_candidate(text, candidates, start, toc_items)
        section_text = text[start.start : end.start].strip() if end else ""
        validation_reasons = _start_validation_reasons(start) + end_reasons
        has_later_start = any(candidate.start > start.start for candidate in starts)
        rejection_reasons = _pair_rejection_reasons(start, end, section_text, has_later_start=has_later_start)
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


def _with_strategy_trace(result: ItemResult, trace: list[StrategyDecision]) -> ItemResult:
    return replace(result, strategy_trace=trace)


def _strategy_decision(
    step: str,
    status: str,
    summary: str,
    signals: list[str] | None = None,
    selected_strategy: str | None = None,
) -> StrategyDecision:
    return StrategyDecision(
        step=step,
        status=status,
        summary=summary,
        signals=signals or [],
        selected_strategy=selected_strategy,
    )


def _rank_trace_signals(ranked_starts: list[HeadingCandidate]) -> list[str]:
    signals = [f"ranked_start_count={len(ranked_starts)}"]
    for index, candidate in enumerate(ranked_starts[:3], start=1):
        reasons = ",".join(candidate.reasons[:4]) if candidate.reasons else "none"
        signals.append(f"{index}:{candidate.text[:80]} | reasons={reasons}")
    return signals


def _confidence_trace_signals(result: ItemResult) -> list[str]:
    signals = [
        f"warnings={len(result.warnings)}",
        f"recommended_actions={len(result.recommended_actions)}",
    ]
    for component in result.confidence_components:
        status = "pass" if component.passed else "fail"
        signals.append(f"{component.name}:{status}:{component.earned:.2f}/{component.weight:.2f}")
    return signals


def _start_rank(candidate: HeadingCandidate) -> tuple[int, int, int, int, int, int, int, int]:
    toc_penalty = 1 if candidate.is_toc_like else 0
    source_penalty = _start_source_penalty(candidate)
    dense_penalty = 1 if "TOC_DENSE_ITEM_CLUSTER" in candidate.reasons else 0
    near_toc_penalty = 1 if "NEAR_TABLE_OF_CONTENTS_LABEL" in candidate.reasons else 0
    followed_page_penalty = 1 if "TOC_FOLLOWED_BY_PAGE_NUMBER" in candidate.reasons else 0
    early_penalty = 1 if "EARLY_DOCUMENT_REGION" in candidate.reasons else 0
    title_penalty = 0 if is_expected_title(candidate.item, candidate.normalized_text) else 1
    return (
        toc_penalty,
        source_penalty,
        followed_page_penalty,
        early_penalty,
        dense_penalty,
        near_toc_penalty,
        title_penalty,
        candidate.start,
    )


def _start_source_penalty(candidate: HeadingCandidate) -> int:
    if "CROSS_REFERENCE_BODY_ALIAS_FALLBACK" in candidate.reasons:
        return 0
    if "NEAR_CROSS_REFERENCE_INDEX_LABEL" in candidate.reasons and "REGEX_ITEM_HEADING" in candidate.reasons:
        return 2
    if "CROSS_REFERENCE_PAGE_FALLBACK" in candidate.reasons:
        return 1
    return 0


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
    if _has_short_placeholder_body(section_text):
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
        if is_expected_title(item, line) and len(line.split()) <= 12:
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
            "appear on page",
            "appear on pages",
            "included on page",
            "included on pages",
            "refer to",
            "see pages",
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
    normalized = re.sub(r"^(?:part [ivx]+ )?item (?:1a|1b|1c|10|11|12|13|14|15|16|1|2|3|4|5|6|7a|7|8|9a|9b|9c) ", "", normalized)
    return normalized in {
        "none",
        "reserved",
        "intentionally omitted",
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
