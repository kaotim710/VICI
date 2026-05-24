from __future__ import annotations

import re

from .models import HeadingCandidate, NarrativeBlock, TocEntry, TocProfile


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
}

HEADING_RE = re.compile(
    r"(?im)(?:^|\n)[ \t]*(?:part\s+[ivx]+\s*[,:\-–—]?\s*)?"
    r"item\s+"
    r"(?P<item>1a|1b|1c|10|11|12|13|14|15|16|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9)"
    r"(?![a-z0-9])"
    r"\s*(?:[.\-–—:])?\s*"
    r"(?P<title>[^\n]{0,160})"
)

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
    return candidates


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


def _is_toc_like(reasons: list[str]) -> bool:
    reason_set = set(reasons)
    if TOC_REASON_CODES.intersection(reason_set):
        return True
    return "TOC_DENSE_ITEM_CLUSTER" in reason_set and "NEAR_TABLE_OF_CONTENTS_LABEL" in reason_set


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
