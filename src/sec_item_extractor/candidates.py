from __future__ import annotations

import re

from .models import HeadingCandidate


ITEM_ORDER = ["1", "1A", "1B", "1C", "2", "3", "4", "5", "6", "7", "7A", "8", "9", "9A", "9B", "9C"]
TARGET_ITEMS = {"1", "1A", "7"}
NEXT_ITEM_GRAPH = {
    "1": {"1A", "1B", "1C", "2"},
    "1A": {"1B", "1C", "2"},
    "7": {"7A", "8"},
}

HEADING_RE = re.compile(
    r"(?im)(?:^|\n)[ \t]*(?:part\s+[ivx]+\s*[,:\-–—]?\s*)?"
    r"item\s+"
    r"(?P<item>1a|1b|1c|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9)"
    r"\s*(?:[.\-–—:])?\s*"
    r"(?P<title>[^\n]{0,160})"
)

EXPECTED_TITLES = {
    "1": ("business",),
    "1A": ("risk factors",),
    "1B": ("unresolved staff comments",),
    "1C": ("cybersecurity",),
    "7": ("management", "discussion", "analysis"),
    "7A": ("quantitative", "qualitative", "market risk"),
    "8": ("financial statements",),
}


def find_heading_candidates(text: str) -> list[HeadingCandidate]:
    candidates: list[HeadingCandidate] = []
    for match in HEADING_RE.finditer(text):
        item = match.group("item").upper()
        raw = match.group(0).strip()
        normalized = _normalize_heading(raw)
        reasons = _heading_reasons(item, normalized, match.start(), text)
        candidates.append(
            HeadingCandidate(
                item=item,
                start=match.start(),
                end=match.end(),
                text=raw,
                normalized_text=normalized,
                is_toc_like="TOC_DENSE_ITEM_CLUSTER" in reasons or "TOC_PAGE_NUMBER_PATTERN" in reasons,
                reasons=reasons,
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


def is_expected_title(item: str, heading: str) -> bool:
    expected = EXPECTED_TITLES.get(item, ())
    normalized = heading.lower()
    return bool(expected) and any(token in normalized for token in expected)


def _normalize_heading(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" .\t\n\r")
    return value


def _heading_reasons(item: str, normalized: str, start: int, text: str) -> list[str]:
    reasons = ["REGEX_ITEM_HEADING"]
    lower = normalized.lower()
    if is_expected_title(item, normalized):
        reasons.append("EXPECTED_TITLE_MATCH")
    if re.search(r"\.{2,}\s*\d+\s*$", normalized) or re.search(r"\s\d{1,4}\s*$", normalized):
        reasons.append("TOC_PAGE_NUMBER_PATTERN")
    window_start = max(0, start - 500)
    window_end = min(len(text), start + 1500)
    window = text[window_start:window_end].lower()
    if len(re.findall(r"\bitem\s+(?:1a|1b|1c|1|2|3|4|5|6|7a|7|8)\b", window)) >= 5:
        reasons.append("TOC_DENSE_ITEM_CLUSTER")
    if "table of contents" in text[max(0, start - 1500) : start].lower():
        reasons.append("NEAR_TABLE_OF_CONTENTS_LABEL")
    if "see item" in lower or "refer to item" in lower:
        reasons.append("INLINE_REFERENCE_RISK")
    return reasons

