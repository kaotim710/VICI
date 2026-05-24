from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from .cleaning import parse_document
from .contracts import RECOVERY_ACTION_CONTRACT_VERSION
from .models import ExtractionResult, ItemResult, RecommendedAction


@dataclass(frozen=True)
class RecoveryResult:
    filing_id: str | None
    item: str
    action_type: str
    reason: str
    status: str
    message: str
    before_length: int
    after_length: int | None = None
    extracted_text: str | None = None
    page_range: tuple[int, int] | None = None
    options: list[str] = field(default_factory=list)
    selected_option: str | None = None
    evidence: list[str] = field(default_factory=list)
    severity: str = "review"
    requires_user_input: bool = False
    next_step: str = ""
    contract_version: str = RECOVERY_ACTION_CONTRACT_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def run_recovery_actions(
    content: str,
    extraction: ExtractionResult,
    selections: dict[tuple[str | None, str], str] | None = None,
) -> list[RecoveryResult]:
    selections = selections or {}
    document = parse_document(content)
    results: list[RecoveryResult] = []

    for item in extraction.item_results:
        for action in item.recommended_actions:
            selected = selections.get((extraction.filing_id, item.item)) or selections.get((None, item.item))
            results.append(_run_action(document.text, extraction.filing_id, item, action, selected))

    return results


def _run_action(
    document_text: str,
    filing_id: str | None,
    item: ItemResult,
    action: RecommendedAction,
    selected_option: str | None,
) -> RecoveryResult:
    if action.reason == "same_filing_page_reference":
        return _recover_page_reference(document_text, filing_id, item, action)
    if action.reason == "internal_item_toc_detected":
        return _recover_internal_toc(filing_id, item, action, selected_option)
    if action.reason in {"start_toc_like_signal", "section_reference_detected", "exhibit_index_detected"}:
        return RecoveryResult(
            filing_id=filing_id,
            item=item.item,
            action_type=action.action_type,
            reason=action.reason,
            status="inspect_only",
            message=action.description,
            before_length=len(item.text or ""),
            options=action.options,
            severity=action.severity,
            requires_user_input=action.requires_user_input,
            next_step=action.next_step,
        )
    if action.reason == "external_or_other_document_reference":
        return RecoveryResult(
            filing_id=filing_id,
            item=item.item,
            action_type=action.action_type,
            reason=action.reason,
            status="deferred",
            message="External/reference document recovery is intentionally deferred until source resolution is implemented.",
            before_length=len(item.text or ""),
            options=action.options,
            severity=action.severity,
            requires_user_input=action.requires_user_input,
            next_step=action.next_step,
        )
    return RecoveryResult(
        filing_id=filing_id,
        item=item.item,
        action_type=action.action_type,
        reason=action.reason,
        status="inspect_only",
        message="No deterministic recovery runner is registered for this action.",
        before_length=len(item.text or ""),
        options=action.options,
        severity=action.severity,
        requires_user_input=action.requires_user_input,
        next_step=action.next_step,
    )


def _recover_page_reference(
    document_text: str, filing_id: str | None, item: ItemResult, action: RecommendedAction
) -> RecoveryResult:
    section_text = item.text or ""
    page_range = _find_page_range(section_text)
    if not page_range:
        return RecoveryResult(
            filing_id=filing_id,
            item=item.item,
            action_type=action.action_type,
            reason=action.reason,
            status="blocked",
            message="No page range was found in the cross-reference text.",
            before_length=len(section_text),
            severity=action.severity,
            requires_user_input=action.requires_user_input,
            next_step=action.next_step,
        )

    page_spans = _page_spans(document_text)
    extracted = _extract_page_span(document_text, page_spans, page_range)
    if extracted is None:
        return RecoveryResult(
            filing_id=filing_id,
            item=item.item,
            action_type=action.action_type,
            reason=action.reason,
            status="blocked",
            message="Page range was parsed, but reliable page locators were not found in the normalized filing text.",
            before_length=len(section_text),
            page_range=page_range,
            evidence=[f"parsed pages {page_range[0]}-{page_range[1]}", f"page locators found: {len(page_spans)}"],
            severity=action.severity,
            requires_user_input=action.requires_user_input,
            next_step=action.next_step,
        )

    return RecoveryResult(
        filing_id=filing_id,
        item=item.item,
        action_type=action.action_type,
        reason=action.reason,
        status="needs_review",
        message="Extracted text from inferred same-filing page range; review required before replacing the original section.",
        before_length=len(section_text),
        after_length=len(extracted),
        extracted_text=extracted,
        page_range=page_range,
        evidence=[f"parsed pages {page_range[0]}-{page_range[1]}", f"page locators found: {len(page_spans)}"],
        severity=action.severity,
        requires_user_input=action.requires_user_input,
        next_step=action.next_step,
    )


def _recover_internal_toc(
    filing_id: str | None,
    item: ItemResult,
    action: RecommendedAction,
    selected_option: str | None,
) -> RecoveryResult:
    section_text = item.text or ""
    if not selected_option:
        return RecoveryResult(
            filing_id=filing_id,
            item=item.item,
            action_type=action.action_type,
            reason=action.reason,
            status="needs_user_selection",
            message="Choose one internal heading option to extract a subsection.",
            before_length=len(section_text),
            options=action.options,
            severity=action.severity,
            requires_user_input=action.requires_user_input,
            next_step=action.next_step,
        )

    subsection = _extract_internal_subsection(section_text, action.options, selected_option)
    if subsection is None:
        return RecoveryResult(
            filing_id=filing_id,
            item=item.item,
            action_type=action.action_type,
            reason=action.reason,
            status="blocked",
            message="Selected internal heading was not found in the extracted section.",
            before_length=len(section_text),
            options=action.options,
            selected_option=selected_option,
            severity=action.severity,
            requires_user_input=action.requires_user_input,
            next_step=action.next_step,
        )

    return RecoveryResult(
        filing_id=filing_id,
        item=item.item,
        action_type=action.action_type,
        reason=action.reason,
        status="needs_review",
        message="Extracted selected internal subsection; review required before replacing the original section.",
        before_length=len(section_text),
        after_length=len(subsection),
        extracted_text=subsection,
        options=action.options,
        selected_option=selected_option,
        severity=action.severity,
        requires_user_input=action.requires_user_input,
        next_step=action.next_step,
    )


def _find_page_range(text: str) -> tuple[int, int] | None:
    match = re.search(r"\bpages?\s+(\d+)\s*[–-]\s*(\d+)\b", text, flags=re.IGNORECASE)
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2))
    if end < start:
        return None
    return start, end


def _page_spans(text: str) -> dict[int, tuple[int, int]]:
    markers = []
    for match in re.finditer(r"(?m)^\s*(\d{1,4})\s*$", text):
        page_number = int(match.group(1))
        markers.append((page_number, match.start(), match.end()))
    markers.sort(key=lambda marker: marker[1])

    spans: dict[int, tuple[int, int]] = {}
    for index, (page_number, marker_start, marker_end) in enumerate(markers):
        previous_end = markers[index - 1][2] if index > 0 else 0
        next_start = markers[index + 1][1] if index + 1 < len(markers) else len(text)
        spans[page_number] = (previous_end, next_start)
        if page_number + 1 not in spans:
            spans[page_number + 1] = (marker_end, next_start)
    return spans


def _extract_page_span(text: str, page_spans: dict[int, tuple[int, int]], page_range: tuple[int, int]) -> str | None:
    start_page, end_page = page_range
    if start_page not in page_spans or end_page not in page_spans:
        return None
    start = page_spans[start_page][0]
    end = page_spans[end_page][1]
    if end <= start:
        return None
    extracted = text[start:end].strip()
    return extracted or None


def _extract_internal_subsection(section_text: str, options: list[str], selected_option: str) -> str | None:
    selected_start = _find_heading_offset(section_text, selected_option)
    if selected_start is None:
        return None

    next_offsets = [
        offset
        for option in options
        if option != selected_option
        for offset in [_find_heading_offset(section_text, option)]
        if offset is not None and offset > selected_start
    ]
    selected_end = min(next_offsets) if next_offsets else len(section_text)
    subsection = section_text[selected_start:selected_end].strip()
    return subsection or None


def _find_heading_offset(text: str, heading: str) -> int | None:
    normalized_heading = " ".join(heading.split()).lower()
    for match in re.finditer(re.escape(heading), text, flags=re.IGNORECASE):
        return match.start()
    for line_match in re.finditer(r"(?m)^.*$", text):
        line = " ".join(line_match.group(0).split()).lower()
        if line == normalized_heading:
            return line_match.start()
    return None
