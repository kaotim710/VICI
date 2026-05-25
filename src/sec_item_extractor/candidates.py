from __future__ import annotations

import re
from collections.abc import Iterable

from .models import CrossReferenceEntry, HeadingCandidate, NarrativeBlock, TocEntry, TocProfile


ITEM_ORDER = [
    "1",
    "1A",
    "1B",
    "1C",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "7A",
    "8",
    "9",
    "9A",
    "9B",
    "9C",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
]
TARGET_ITEMS = set(ITEM_ORDER)
NEXT_ITEM_GRAPH = {
    "1": {"1A", "1B", "1C", "2"},
    "1A": {"1B", "1C", "2"},
    "7": {"7A", "8"},
    "8": {"9", "9A", "9B", "9C", "10", "15", "16"},
}

HEADING_RE = re.compile(
    r"(?im)(?:^|\n)[ \t]*(?:part\s+[ivx]+\s*[,:\-–—]?\s*)?"
    r"item\s+"
    r"(?P<item>1a|1b|1c|10|11|12|13|14|15|16|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9)"
    r"(?![a-z0-9])"
    r"\s*(?:[.\-–—:])?\s*"
    r"(?P<title>[^\n]{0,160})"
)

SEC_ITEM_TITLES = {
    "1": "Business",
    "1A": "Risk Factors",
    "1B": "Unresolved Staff Comments",
    "1C": "Cybersecurity",
    "2": "Properties",
    "3": "Legal Proceedings",
    "4": "Mine Safety Disclosures",
    "5": "Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities",
    "6": "Selected Financial Data",
    "7": "Management's Discussion and Analysis of Financial Condition and Results of Operations",
    "7A": "Quantitative and Qualitative Disclosures About Market Risk",
    "8": "Financial Statements and Supplementary Data",
    "9": "Changes in and Disagreements with Accountants on Accounting and Financial Disclosure",
    "9A": "Controls and Procedures",
    "9B": "Other Information",
    "9C": "Disclosure Regarding Foreign Jurisdictions that Prevent Inspections",
    "10": "Directors, Executive Officers and Corporate Governance",
    "11": "Executive Compensation",
    "12": "Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters",
    "13": "Certain Relationships and Related Transactions, and Director Independence",
    "14": "Principal Accountant Fees and Services",
    "15": "Exhibits, Financial Statement Schedules",
    "16": "Form 10-K Summary",
}

EXPECTED_TITLES = {
    "1": ("business",),
    "1A": ("risk factors",),
    "1B": ("unresolved staff comments", "unresolved sec staff comments"),
    "1C": ("cybersecurity",),
    "2": ("properties",),
    "3": ("legal proceedings",),
    "4": ("mine safety",),
    "5": ("market for", "common equity", "equity securities"),
    "6": ("selected financial data", "selected consolidated financial data", "reserved"),
    "7": ("management", "discussion", "analysis"),
    "7A": ("quantitative", "qualitative", "market risk"),
    "8": ("financial statements",),
    "9": ("changes in", "disagreements", "accounting"),
    "9A": ("controls", "procedures"),
    "9B": ("other information",),
    "9C": ("foreign jurisdictions", "prevent inspections"),
    "10": ("directors", "executive officers", "corporate governance"),
    "11": ("executive compensation",),
    "12": ("security ownership",),
    "13": ("certain relationships", "related transactions", "director independence"),
    "14": ("principal accountant", "fees", "services"),
    "15": ("exhibit", "financial statement schedules"),
    "16": ("form 10-k summary",),
}

TOC_REASON_CODES = {
    "TOC_DOT_LEADER_PAGE_NUMBER",
    "TOC_PAGE_NUMBER_PATTERN",
    "TOC_TABLE_ROW_PAGE_NUMBER",
}


def find_heading_candidates(text: str, blocks: list[NarrativeBlock] | None = None) -> list[HeadingCandidate]:
    candidates: list[HeadingCandidate] = []
    block_index = 0
    for match in HEADING_RE.finditer(text):
        start = _first_nonspace(text, match.start(), match.end())
        item = match.group("item").upper()
        raw = text[start : match.end()].strip()
        normalized = _normalize_heading(raw)
        block = None
        if blocks:
            block, block_index = _block_for_offset(start, blocks, block_index)
        reasons = _heading_reasons(item, normalized, start, text, block)
        if blocks and _candidate_followed_by_page_number(match.end(), blocks, block_index):
            reasons.append("TOC_FOLLOWED_BY_PAGE_NUMBER")
        candidates.append(
            HeadingCandidate(
                item=item,
                start=start,
                end=match.end(),
                text=raw,
                normalized_text=normalized,
                is_toc_like=_is_toc_like(reasons),
                reasons=reasons,
                raw_start=_raw_offset(block, start) if block else None,
                raw_end=_raw_offset(block, match.end()) if block else None,
                block_index=block_index if block else None,
                block_tag=block.tag if block else None,
            )
        )
    if blocks and _has_cross_reference_index(text):
        candidates.extend(_cross_reference_page_candidates(blocks, candidates))
        candidates.extend(_cross_reference_body_alias_candidates(blocks, candidates))
        candidates.extend(_cross_reference_alias_candidates(blocks, candidates))
        candidates.sort(key=lambda candidate: (candidate.start, candidate.end, candidate.item))
    return candidates


def infer_cross_reference_entries(blocks: list[NarrativeBlock]) -> list[CrossReferenceEntry]:
    entries: list[CrossReferenceEntry] = []
    footnotes = _cross_reference_footnotes(blocks)
    for start_index, end_index in _cross_reference_ranges(blocks):
        index = start_index + 1
        while index < end_index:
            item = _item_token(blocks[index].text)
            if item is None:
                index += 1
                continue
            region_end = _next_item_token_index(blocks, index + 1, end_index)
            region = blocks[index + 1 : region_end]
            title = _cross_reference_title(region)
            pages = _cross_reference_pages(region)
            note = _cross_reference_note(region, footnotes)
            if title or pages or note:
                entries.append(
                    CrossReferenceEntry(
                        item=item,
                        title=title or SEC_ITEM_TITLES.get(item, ""),
                        pages=pages,
                        note=note,
                        block_index=index,
                    )
                )
            index = region_end
    return entries


def infer_page_start_offsets(blocks: list[NarrativeBlock]) -> dict[int, tuple[int, int]]:
    return _page_start_offsets(blocks)


def legal_next_items(item: str) -> set[str]:
    if item in NEXT_ITEM_GRAPH:
        return NEXT_ITEM_GRAPH[item]
    try:
        index = ITEM_ORDER.index(item)
    except ValueError:
        return set()
    return set(ITEM_ORDER[index + 1 : index + 3])


def infer_toc_profile(candidates: list[HeadingCandidate]) -> TocProfile:
    prefix = _toc_prefix(candidates)
    if len(prefix) < 2:
        return TocProfile(items=[], confidence="none")

    has_toc_signals = any(candidate.is_toc_like for candidate in prefix)
    dense_count = sum("TOC_DENSE_ITEM_CLUSTER" in candidate.reasons for candidate in prefix)
    ordered_count = _ordered_pair_count(prefix)
    if has_toc_signals:
        confidence = "high"
    elif len(prefix) >= 5 and dense_count >= 5 and ordered_count >= len(prefix) - 2:
        confidence = "medium"
    else:
        return TocProfile(items=[], confidence="none")

    return TocProfile(
        items=[candidate.item for candidate in prefix],
        confidence=confidence,
        entries=[_toc_entry(candidate) for candidate in prefix],
        evidence=[f"prefix_items={len(prefix)}", f"dense_items={dense_count}", f"ordered_pairs={ordered_count}"],
    )


def is_expected_title(item: str, heading: str) -> bool:
    expected = EXPECTED_TITLES.get(item, ())
    normalized = heading.lower()
    return bool(expected) and any(token in normalized for token in expected)


def toc_next_items(item: str, toc_items: list[str], limit: int = 3) -> list[str]:
    if item not in toc_items:
        return []
    index = toc_items.index(item)
    return toc_items[index + 1 : index + 1 + limit]


def _toc_entry(candidate: HeadingCandidate) -> TocEntry:
    return TocEntry(
        item=candidate.item,
        title=_toc_title(candidate),
        text=candidate.text,
        offset=candidate.start,
        raw_offset=candidate.raw_start,
        page_number=_toc_page_number(candidate.text),
        reasons=candidate.reasons,
    )


def _normalize_heading(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" .\t\n\r")
    return value


def _toc_page_number(value: str) -> int | None:
    compact = " ".join(value.split())
    match = re.search(r"(?:\.{2,}\s*|\s+)(\d{1,4})\s*$", compact)
    return int(match.group(1)) if match else None


def _toc_title(candidate: HeadingCandidate) -> str:
    value = " ".join(candidate.text.split())
    value = re.sub(r"(?i)^part\s+[ivx]+\s*[,:\-–—]?\s*", "", value).strip()
    value = re.sub(rf"(?i)^item\s+{re.escape(candidate.item)}(?![a-z0-9])\s*(?:[.\-–—:])?\s*", "", value).strip()
    value = re.sub(r"(?:\.{2,}\s*|\s+)\d{1,4}\s*$", "", value).strip()
    return value.strip(" .\t\n\r")


def _toc_prefix(candidates: list[HeadingCandidate]) -> list[HeadingCandidate]:
    prefix = []
    seen = set()
    for candidate in sorted(candidates, key=lambda current: current.start):
        if candidate.item not in ITEM_ORDER:
            continue
        if candidate.item in seen:
            break
        prefix.append(candidate)
        seen.add(candidate.item)
    return prefix


def _ordered_pair_count(candidates: list[HeadingCandidate]) -> int:
    positions = [ITEM_ORDER.index(candidate.item) for candidate in candidates if candidate.item in ITEM_ORDER]
    return sum(1 for left, right in zip(positions, positions[1:]) if right > left)


def _first_nonspace(text: str, start: int, end: int) -> int:
    while start < end and text[start].isspace():
        start += 1
    return start


def _heading_reasons(
    item: str, normalized: str, start: int, text: str, block: NarrativeBlock | None = None
) -> list[str]:
    reasons = ["REGEX_ITEM_HEADING"]
    lower = normalized.lower()
    if is_expected_title(item, normalized):
        reasons.append("EXPECTED_TITLE_MATCH")
    if re.search(r"\.{2,}\s*\d+\s*$", normalized):
        reasons.append("TOC_DOT_LEADER_PAGE_NUMBER")
    if re.search(r"\s\d{1,4}\s*$", normalized):
        reasons.append("TOC_PAGE_NUMBER_PATTERN")
    if block and _block_has_toc_page_number(block.text):
        reasons.append("TOC_TABLE_ROW_PAGE_NUMBER")
    window_end = min(len(text), start + 1500)
    window = text[start:window_end].lower()
    if len(re.findall(r"\bitem\s+(?:1a|1b|1c|10|11|12|13|14|15|16|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9)\b", window)) >= 5:
        reasons.append("TOC_DENSE_ITEM_CLUSTER")
    if "table of contents" in text[max(0, start - 1500) : start].lower():
        reasons.append("NEAR_TABLE_OF_CONTENTS_LABEL")
    if "form 10-k cross-reference index" in text[max(0, start - 3000) : start].lower():
        reasons.append("NEAR_CROSS_REFERENCE_INDEX_LABEL")
    if start < min(25000, max(5000, int(len(text) * 0.04))):
        reasons.append("EARLY_DOCUMENT_REGION")
    if "see item" in lower or "refer to item" in lower:
        reasons.append("INLINE_REFERENCE_RISK")
    return reasons


def _block_has_toc_page_number(block_text: str) -> bool:
    compact = " ".join(block_text.split())
    if len(compact) > 240:
        return False
    if not re.search(r"\bitem\s+(?:1a|1b|1c|10|11|12|13|14|15|16|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9)\b", compact, re.IGNORECASE):
        return False
    return bool(re.search(r"(?:\.{2,}\s*|\s{2,})\d{1,4}\s*$", compact))


def _candidate_followed_by_page_number(clean_end: int, blocks: list[NarrativeBlock], block_index: int) -> bool:
    index = max(0, min(block_index, len(blocks) - 1))
    while index + 1 < len(blocks) and blocks[index].clean_end < clean_end:
        index += 1
    for next_index in range(index + 1, min(len(blocks), index + 4)):
        gap = blocks[next_index].clean_start - clean_end
        if gap > 12:
            break
        compact = " ".join(blocks[next_index].text.split())
        if re.fullmatch(r"\d{1,4}\s*[-–—]\s*\d{1,4}", compact):
            return True
        if re.fullmatch(r"\d{1,4}", compact) and _near_next_toc_item(blocks, next_index):
            return True
        if compact and not re.fullmatch(r"part\s+[ivx]+", compact, flags=re.IGNORECASE):
            break
    return False


def _near_next_toc_item(blocks: list[NarrativeBlock], page_number_index: int) -> bool:
    for block in blocks[page_number_index + 1 : page_number_index + 6]:
        compact = " ".join(block.text.split())
        if re.fullmatch(r"part\s+[ivx]+", compact, flags=re.IGNORECASE):
            return True
        if re.fullmatch(
            r"item\s+(?:1a|1b|1c|10|11|12|13|14|15|16|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9)\.?.*",
            compact,
            flags=re.IGNORECASE,
        ):
            return True
    return False


def _is_toc_like(reasons: list[str]) -> bool:
    reason_set = set(reasons)
    if TOC_REASON_CODES.intersection(reason_set):
        return True
    if "TOC_FOLLOWED_BY_PAGE_NUMBER" in reason_set and "EARLY_DOCUMENT_REGION" in reason_set:
        return True
    if "TOC_DENSE_ITEM_CLUSTER" in reason_set and "NEAR_CROSS_REFERENCE_INDEX_LABEL" in reason_set:
        return True
    return (
        "TOC_DENSE_ITEM_CLUSTER" in reason_set
        and "NEAR_TABLE_OF_CONTENTS_LABEL" in reason_set
        and "EARLY_DOCUMENT_REGION" in reason_set
    )


def _has_cross_reference_index(text: str) -> bool:
    return "form 10-k cross-reference index" in text.lower()


def _cross_reference_page_candidates(
    blocks: list[NarrativeBlock], existing_candidates: Iterable[HeadingCandidate]
) -> list[HeadingCandidate]:
    existing_keys = {(candidate.item, candidate.start) for candidate in existing_candidates}
    page_starts = _page_start_offsets(blocks)
    candidates: list[HeadingCandidate] = []
    for start_index, end_index in _cross_reference_ranges(blocks):
        index = start_index + 1
        while index < end_index:
            item = _item_token(blocks[index].text)
            if item is None:
                index += 1
                continue
            region_end = _next_item_token_index(blocks, index + 1, end_index)
            title = _cross_reference_title(blocks[index + 1 : region_end])
            page = _first_cross_reference_page(blocks[index + 1 : region_end])
            if title and page and page in page_starts:
                start, block_index = page_starts[page]
                key = (item, start)
                if key not in existing_keys:
                    text = f"Item {item}. {title}"
                    reasons = ["CROSS_REFERENCE_PAGE_FALLBACK"]
                    if is_expected_title(item, text):
                        reasons.append("EXPECTED_TITLE_MATCH")
                    candidates.append(
                        HeadingCandidate(
                            item=item,
                            start=start,
                            end=start + len(text),
                            text=text,
                            normalized_text=_normalize_heading(text),
                            is_toc_like=False,
                            reasons=reasons,
                            raw_start=blocks[block_index].raw_start,
                            raw_end=blocks[block_index].raw_end,
                            block_index=block_index,
                            block_tag=blocks[block_index].tag,
                        )
                    )
                    existing_keys.add(key)
            index = region_end
    return candidates


def _cross_reference_ranges(blocks: list[NarrativeBlock]) -> list[tuple[int, int]]:
    ranges = []
    for index, block in enumerate(blocks):
        if "form 10-k cross-reference index" not in block.text.lower():
            continue
        end = min(len(blocks), index + 260)
        seen_item = False
        for cursor in range(index + 1, end):
            if _item_token(blocks[cursor].text):
                seen_item = True
            if (
                seen_item
                and cursor > index + 4
                and blocks[cursor].tag != "td"
                and re.fullmatch(r"\d{1,4}", " ".join(blocks[cursor].text.split()))
            ):
                end = cursor
                break
            if _item_token(blocks[cursor].text) == "16":
                end = min(len(blocks), cursor + 28)
                break
        ranges.append((index, end))
    return ranges


def _next_item_token_index(blocks: list[NarrativeBlock], start: int, end: int) -> int:
    for index in range(start, end):
        if re.fullmatch(r"\d{1,4}", " ".join(blocks[index].text.split())):
            continue
        if _item_token(blocks[index].text):
            return index
    return end


def _item_token(value: str) -> str | None:
    compact = " ".join(value.split()).strip()
    match = re.fullmatch(
        r"(?:part\s+[ivx]+\s*)?(?:item\s*(?P<prefixed>1a|1b|1c|10|11|12|13|14|15|16|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9)\.?:?|(?P<bare>1a|1b|1c|10|11|12|13|14|15|16|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9)\.)",
        compact,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return (match.group("prefixed") or match.group("bare")).upper()


def _cross_reference_alias_candidates(
    blocks: list[NarrativeBlock], existing_candidates: Iterable[HeadingCandidate]
) -> list[HeadingCandidate]:
    existing = {(candidate.item, candidate.start) for candidate in existing_candidates}
    aliases = {
        "15": {"exhibit index"},
    }
    candidates: list[HeadingCandidate] = []
    for index, block in enumerate(blocks):
        normalized = " ".join(block.text.lower().split()).strip(" :")
        for item, labels in aliases.items():
            if normalized not in labels:
                continue
            key = (item, block.clean_start)
            if key in existing:
                continue
            text = f"Item {item}. {block.text.strip()}"
            is_toc_like = _alias_is_toc_like(blocks, index)
            if is_toc_like:
                continue
            candidates.append(
                HeadingCandidate(
                    item=item,
                    start=block.clean_start,
                    end=block.clean_start + len(block.text),
                    text=text,
                    normalized_text=_normalize_heading(text),
                    is_toc_like=is_toc_like,
                    reasons=["CROSS_REFERENCE_ALIAS_FALLBACK", "EXPECTED_TITLE_MATCH"],
                    raw_start=block.raw_start,
                    raw_end=block.raw_end,
                    block_index=index,
                    block_tag=block.tag,
                )
            )
            existing.add(key)
            break
    return candidates


def _cross_reference_body_alias_candidates(
    blocks: list[NarrativeBlock], existing_candidates: Iterable[HeadingCandidate]
) -> list[HeadingCandidate]:
    existing = {(candidate.item, candidate.start) for candidate in existing_candidates}
    aliases = {
        "1": {"our business"},
        "1A": {"risk factors"},
    }
    candidates: list[HeadingCandidate] = []
    for index, block in enumerate(blocks):
        normalized = " ".join(block.text.lower().split()).strip(" :")
        item = next((candidate_item for candidate_item, labels in aliases.items() if normalized in labels), None)
        if item is None:
            continue
        if _body_alias_is_toc_or_running_header(blocks, index):
            continue
        key = (item, block.clean_start)
        if key in existing:
            continue
        text = f"Item {item}. {block.text.strip()}"
        candidates.append(
            HeadingCandidate(
                item=item,
                start=block.clean_start,
                end=block.clean_start + len(block.text),
                text=text,
                normalized_text=_normalize_heading(text),
                is_toc_like=False,
                reasons=["CROSS_REFERENCE_BODY_ALIAS_FALLBACK", "EXPECTED_TITLE_MATCH"],
                raw_start=block.raw_start,
                raw_end=block.raw_end,
                block_index=index,
                block_tag=block.tag,
            )
        )
        existing.add(key)
    return candidates


def _body_alias_is_toc_or_running_header(blocks: list[NarrativeBlock], index: int) -> bool:
    prior_context = " ".join(block.text.lower() for block in blocks[max(0, index - 30) : index])
    if "form 10-k cross-reference index" in prior_context:
        return True
    next_texts = [" ".join(block.text.split()) for block in blocks[index + 1 : min(len(blocks), index + 4)]]
    if next_texts and _looks_like_page_reference(next_texts[0]):
        return True
    if len(next_texts) >= 2 and re.fullmatch(r"\d{1,4}", next_texts[0]) and next_texts[1].lower() == "table of contents":
        return True
    return False


def _alias_is_toc_like(blocks: list[NarrativeBlock], index: int) -> bool:
    window = " ".join(block.text.lower() for block in blocks[max(0, index - 12) : min(len(blocks), index + 12)])
    prior_context = " ".join(block.text.lower() for block in blocks[max(0, index - 220) : index])
    if "cross-reference index" in window or "form 10-k cross-reference index" in prior_context:
        return True
    if "table of contents" not in window:
        return False
    page_refs = sum(1 for block in blocks[index + 1 : min(len(blocks), index + 8)] if _looks_like_page_reference(block.text))
    return page_refs >= 2


def _cross_reference_title(blocks: list[NarrativeBlock]) -> str:
    parts = []
    for block in blocks[:6]:
        compact = " ".join(block.text.split()).strip()
        if not compact or _is_part_label(compact) or _looks_like_page_reference(compact):
            continue
        if len(compact) > 180:
            break
        parts.append(compact)
        if is_expected_title("", compact) or len(parts) >= 2:
            break
    return " ".join(parts).strip(" :")


def _first_cross_reference_page(blocks: list[NarrativeBlock]) -> int | None:
    pages = _cross_reference_pages(blocks)
    return pages[0] if pages else None


def _cross_reference_pages(blocks: list[NarrativeBlock]) -> list[int]:
    pages: list[int] = []
    for block in blocks[:18]:
        compact = " ".join(block.text.split()).strip()
        if not _looks_like_page_reference(compact):
            continue
        for left, right in re.findall(r"(\d{1,4})(?:\s*[–-]\s*(\d{1,4}))?", compact):
            start = int(left)
            end = int(right) if right else start
            if end < start or end - start > 80:
                continue
            pages.extend(range(start, end + 1))
    seen = set()
    for page in pages:
        if page in seen:
            continue
        seen.add(page)
    return sorted(seen)


def _cross_reference_note(blocks: list[NarrativeBlock], footnotes: dict[str, str]) -> str | None:
    for block in blocks[:8]:
        compact = " ".join(block.text.split()).strip().lower()
        if compact in footnotes:
            return footnotes[compact]
    return None


def _cross_reference_footnotes(blocks: list[NarrativeBlock]) -> dict[str, str]:
    notes: dict[str, str] = {}
    for start_index, end_index in _cross_reference_ranges(blocks):
        for block in blocks[start_index:end_index]:
            compact = " ".join(block.text.split()).strip()
            match = re.match(r"^(\([a-z]\))\s+(.+)$", compact, flags=re.IGNORECASE)
            if match:
                notes[match.group(1).lower()] = compact
    return notes


def _looks_like_page_reference(value: str) -> bool:
    compact = value.strip()
    if compact.lower() in {"none", "not applicable", "(a)"}:
        return True
    if re.search(r"(?i)\bpages?\b", compact):
        return bool(re.search(r"\d{1,4}", compact))
    return bool(re.fullmatch(r"\d{1,4}(?:\s*[–-]\s*\d{1,4})?(?:,\s*\d{1,4}(?:\s*[–-]\s*\d{1,4})?)*,?", compact))


def _is_part_label(value: str) -> bool:
    return bool(re.fullmatch(r"part\s+[ivx]+", value.strip(), flags=re.IGNORECASE))


def _page_start_offsets(blocks: list[NarrativeBlock]) -> dict[int, tuple[int, int]]:
    starts: dict[int, tuple[int, int]] = {}
    max_page = 500
    for page in range(2, max_page + 1):
        footer_index = _best_page_footer_index(blocks, page - 1)
        if footer_index is None or footer_index + 1 >= len(blocks):
            continue
        starts[page] = (blocks[footer_index + 1].clean_start, footer_index + 1)
    return starts


def _best_page_footer_index(blocks: list[NarrativeBlock], page: int) -> int | None:
    page_text = str(page)
    best: tuple[int, int] | None = None
    for index, block in enumerate(blocks[:-1]):
        if block.text.strip() != page_text:
            continue
        score = _page_footer_score(blocks, index)
        if score <= 0:
            continue
        if best is None or score > best[0]:
            best = (score, index)
    return best[1] if best else None


def _page_footer_score(blocks: list[NarrativeBlock], index: int) -> int:
    block = blocks[index]
    if block.tag == "td":
        return -1
    window = blocks[max(0, index - 8) : min(len(blocks), index + 9)]
    numeric_neighbors = sum(1 for current in window if re.fullmatch(r"\d{1,4}", current.text.strip()))
    previous_text = " ".join(current.text.lower() for current in blocks[max(0, index - 8) : index])
    next_block = blocks[index + 1] if index + 1 < len(blocks) else None
    score = 4
    if block.tag == "div":
        score += 3
    if next_block and not re.fullmatch(r"\d{1,4}", next_block.text.strip()):
        score += 2
    if any(len(current.text.split()) >= 8 for current in blocks[max(0, index - 4) : index]):
        score += 2
    if "table of contents" in previous_text:
        score -= 2
    score -= numeric_neighbors
    return score


def _block_for_offset(
    offset: int, blocks: list[NarrativeBlock], start_index: int
) -> tuple[NarrativeBlock | None, int]:
    index = max(0, min(start_index, len(blocks) - 1))
    while index + 1 < len(blocks) and blocks[index].clean_end <= offset:
        index += 1
    while index > 0 and blocks[index].clean_start > offset:
        index -= 1
    block = blocks[index]
    if block.clean_start <= offset <= block.clean_end:
        return block, index
    return None, index


def _raw_offset(block: NarrativeBlock, clean_offset: int) -> int | None:
    if block.raw_start is None:
        return None
    return block.raw_start + max(0, clean_offset - block.clean_start)
