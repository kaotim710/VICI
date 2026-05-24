from __future__ import annotations

import re
from html import escape as html_escape
from html import unescape


def raw_structure_counts(content: str, item_result) -> dict:
    if item_result.status != "success":
        return {"table_count": 0, "image_count": 0}
    try:
        _, _, fragment = raw_section_fragment(content, item_result)
    except ValueError:
        return {"table_count": 0, "image_count": 0}
    return raw_fragment_structure(fragment)


def raw_fragment_structure(fragment: str) -> dict:
    return {
        "table_count": len(re.findall(r"<table\b", fragment, flags=re.IGNORECASE)),
        "image_count": len(re.findall(r"<img\b", fragment, flags=re.IGNORECASE)),
    }


def raw_fragment_outline(fragment: str, limit: int = 30) -> list[str]:
    return [section["label"] for section in raw_fragment_outline_sections(fragment, limit)]


def raw_fragment_outline_sections(fragment: str, limit: int = 30) -> list[dict]:
    candidates: list[str] = []
    sections: list[dict] = []
    matches = sorted(
        (
            match
            for pattern in (
                r"(?is)<(?:b|strong)\b[^>]*>(.*?)</(?:b|strong)>",
                r"(?is)<h[1-6]\b[^>]*>(.*?)</h[1-6]>",
            )
            for match in re.finditer(pattern, fragment)
        ),
        key=lambda match: match.start(),
    )
    for index, match in enumerate(matches):
        label = _html_text(match.group(1))
        if not _looks_like_outline_label(label):
            continue
        label = label[:140]
        if label.lower() in candidates:
            continue
        candidates.append(label.lower())
        start = match.start()
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(fragment)
        section_html = fragment[start:next_start]
        structure = raw_fragment_structure(section_html)
        sections.append(
            {
                "label": label,
                "text": _truncate(_html_text(section_html), 6000),
                "raw_bytes": len(section_html.encode("utf-8", errors="replace")),
                "table_count": structure["table_count"],
                "image_count": structure["image_count"],
                "raw_start": start,
                "raw_end": next_start,
            }
        )
        if len(sections) >= limit:
            break
    return sections


def raw_fragment_exhibit_links(fragment: str, limit: int = 120) -> dict[str, dict]:
    links: dict[str, dict] = {}
    for row in re.finditer(r"(?is)<tr\b.*?</tr>", fragment):
        row_html = row.group(0)
        row_text = _html_text(row_html)
        number_match = re.match(r"(?P<number>\d+(?:\.\d+)+[A-Z]?)\b", row_text)
        if not number_match:
            continue
        link_match = re.search(r"(?is)<a\b[^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>(?P<label>.*?)</a>", row_html)
        if not link_match:
            continue
        number = number_match.group("number")
        label = _html_text(link_match.group("label"))
        if not label:
            continue
        links[number] = {
            "href": unescape(link_match.group("href")),
            "label": label,
        }
        if len(links) >= limit:
            break
    return links


def raw_fragment_supplemental_chunk(fragment: str, limit: int = 40) -> dict | None:
    supplemental = raw_fragment_supplemental_fragment(fragment)
    if supplemental is None:
        return None
    start, chunk = supplemental
    return _raw_fragment_toc_chunk(chunk, limit, label="Supplemental filing content after Item 15", raw_offset=start)


def raw_fragment_internal_toc_chunk(fragment: str, item_name: str | None = None, limit: int = 40) -> dict | None:
    if item_name and item_name.upper() == "8":
        direct = _raw_fragment_toc_chunk(fragment, limit, label="Internal filing content from item TOC")
        if direct and len(direct.get("sections", [])) >= 5:
            return direct

    supplemental = raw_fragment_supplemental_fragment(fragment)
    if supplemental is not None:
        start, chunk = supplemental
        return _raw_fragment_toc_chunk(
            chunk, limit, label="Internal filing content from item TOC", raw_offset=start, adjust_section_offsets=True
        )

    start = _internal_toc_start(fragment)
    if start is None:
        return None
    chunk = fragment[start:]
    return _raw_fragment_toc_chunk(
        chunk, limit, label="Internal filing content from item TOC", raw_offset=start, adjust_section_offsets=True
    )


def _raw_fragment_toc_chunk(
    chunk: str, limit: int, label: str, raw_offset: int = 0, adjust_section_offsets: bool = False
) -> dict | None:
    structure = raw_fragment_structure(chunk)
    toc_entries = _supplemental_toc_entries(chunk, limit)
    sections = _supplemental_sections_from_toc(chunk, toc_entries)
    if not sections:
        sections = raw_fragment_outline_sections(chunk, limit)
    if not sections and structure["table_count"] + structure["image_count"] < 20:
        return None
    if raw_offset and adjust_section_offsets:
        sections = [_offset_section(section, raw_offset) for section in sections]
    return {
        "label": label,
        "text": _truncate(_html_text(chunk), 10000),
        "raw_bytes": len(chunk.encode("utf-8", errors="replace")),
        "table_count": structure["table_count"],
        "image_count": structure["image_count"],
        "sections": sections,
        "raw_start": raw_offset,
        "raw_end": raw_offset + len(chunk),
    }


def _offset_section(section: dict, raw_offset: int) -> dict:
    updated = dict(section)
    updated["raw_start"] = int(updated.get("raw_start", 0)) + raw_offset
    updated["raw_end"] = int(updated.get("raw_end", 0)) + raw_offset
    return updated


def raw_fragment_supplemental_fragment(fragment: str) -> tuple[int, str] | None:
    start = _supplemental_toc_start(fragment)
    if start is None:
        return None
    return start, fragment[start:]


def _supplemental_toc_start(fragment: str) -> int | None:
    for match in re.finditer(r"(?is)table\s+of\s+contents", fragment):
        start = _financial_toc_start(fragment, match.start())
        if start is not None:
            return start
    return None


def _internal_toc_start(fragment: str) -> int | None:
    search = fragment[:250000]
    for pattern in (
        r"(?is)table\s+of\s+contents",
        r"(?is)index\s+to\s+(?:audited\s+)?(?:consolidated\s+)?financial\s+statements",
    ):
        match = re.search(pattern, search)
        if match:
            return match.start()
    return None


def _financial_toc_start(fragment: str, toc_offset: int) -> int | None:
    before_raw = fragment[max(0, toc_offset - 1800) : toc_offset]
    after_raw = fragment[toc_offset : toc_offset + 5000]
    before_text = _html_text(before_raw).lower()
    after_text = _html_text(after_raw).lower()

    local_after = after_text[:700]
    local_before = before_text[-220:]
    if "exhibit index" in local_after and "financial" not in local_before:
        return None
    if "signatures" in local_after and "financial" not in local_before:
        return None

    if "financial:" in local_after or "audited financial statements" in local_after:
        return toc_offset
    if "financial table of contents" in (local_before + " " + local_after[:120]):
        return _nearby_financial_heading_start(fragment, toc_offset) or toc_offset
    if "financial section" in (local_before + " " + local_after):
        heading_start = _nearby_financial_heading_start(fragment, toc_offset)
        if heading_start is not None:
            return heading_start
        if "business profile" in local_after or "financial information" in local_after:
            return toc_offset
    return None


def _nearby_financial_heading_start(fragment: str, toc_offset: int) -> int | None:
    search_start = max(0, toc_offset - 1800)
    before_raw = fragment[search_start:toc_offset]
    before_matches = list(re.finditer(r"(?is)financial(?:\s+section)?", before_raw))
    if before_matches:
        return search_start + before_matches[-1].start()

    after_raw = fragment[toc_offset : toc_offset + 5000]
    after_match = re.search(r"(?is)financial\s+section", after_raw)
    if after_match:
        return toc_offset + after_match.start()
    return None


def _supplemental_toc_entries(chunk: str, limit: int) -> list[dict]:
    toc_entries = []
    seen = set()
    no_entry_streak = 0
    for row_match in re.finditer(r"(?is)<tr\b.*?</tr>", chunk[:250000]):
        row_html = row_match.group(0)
        row_text = _html_text(row_html)
        row_lower = row_text.lower()
        if ("annual report" in row_lower or "form 10-k" in row_lower) and toc_entries:
            break
        row_entries = _supplemental_toc_entries_from_row(row_html)
        if toc_entries and not row_entries:
            no_entry_streak += 1
            if no_entry_streak >= 8:
                break
        elif row_entries:
            no_entry_streak = 0
        for entry in row_entries:
            key = entry["label"].lower()
            href_key = entry.get("href", "").lower()
            if key in seen or (href_key and href_key in seen):
                continue
            seen.add(key)
            if href_key:
                seen.add(href_key)
            toc_entries.append(entry)
            if len(toc_entries) >= limit:
                break
        if len(toc_entries) >= limit:
            break
    return toc_entries


def _supplemental_toc_entries_from_row(row_html: str) -> list[dict]:
    row_text = _html_text(row_html)
    entries: list[dict] = []
    row_label = _toc_label_from_row_text(row_text)
    for link_match in re.finditer(r"(?is)<a\b[^>]*href=[\"'](?P<href>#[^\"']+)[\"'][^>]*>(?P<label>.*?)</a>", row_html):
        linked_text = _html_text(link_match.group("label"))
        label = _clean_toc_label(linked_text)
        if re.fullmatch(r"\d+[A-Za-z]?", linked_text):
            label = row_label or re.sub(rf"\s+{re.escape(linked_text)}\s*$", "", row_text).strip()
        elif row_label and len(linked_text) < min(len(row_label), 24):
            label = row_label
        if label.lower().startswith("bank of america"):
            continue
        if not _looks_like_supplemental_label(label):
            continue
        entries.append(
            {
                "label": label[:180],
                "href": unescape(link_match.group("href")),
            }
        )
    if entries:
        return entries
    return _unlinked_supplemental_toc_entries(row_text)


def _unlinked_supplemental_toc_entries(row_text: str) -> list[dict]:
    if "annual report" in row_text.lower():
        return []
    row_label = _toc_label_from_row_text(row_text)
    if row_label and _looks_like_supplemental_label(row_label):
        return [{"label": row_label[:180]}]
    entries = []
    matches = list(re.finditer(r"(?<!\d)(?P<page>\d{1,3})\s+(?P<label>.*?)(?=\s+\d{1,3}\s+|$)", row_text))
    for match in matches:
        label = match.group("label").strip(" :")
        if not _looks_like_supplemental_label(label):
            continue
        entries.append({"label": label[:180]})
    return entries


def _toc_label_from_row_text(row_text: str) -> str | None:
    compact = " ".join(row_text.split()).strip(" :")
    if not compact:
        return None
    match = re.match(r"(?P<label>.+?)\s+(?P<page>\d{1,4}[A-Za-z]?)$", compact)
    if not match:
        return None
    label = match.group("label").strip(" :")
    if re.search(r"\b(?:for the year|total|assets|liabilities|revenue|income|loss)\b", label, flags=re.IGNORECASE):
        return None
    label = _clean_toc_label(label)
    if label.lower().startswith("bank of america"):
        return None
    return label


def _clean_toc_label(label: str) -> str:
    label = " ".join(label.split())
    for _ in range(3):
        label = re.sub(r"\b([A-Za-z])\s+([a-z]{2,})\b", r"\1\2", label)
    label = re.sub(r"(’s)([A-Za-z])", r"\1 \2", label)
    return label


def raw_section_fragment(content: str, item_result) -> tuple[int, int, str]:
    raw_start = item_result.start_evidence.raw_offset if item_result.start_evidence else None
    if raw_start is None:
        raise ValueError(f"raw section has no raw start offset for Item {item_result.item}")
    raw_end = item_result.end_evidence.raw_offset if item_result.end_evidence else None
    start = _raw_container_start(content, raw_start)
    end = _raw_container_start(content, raw_end) if raw_end is not None else len(content)
    if end <= start:
        end = len(content)
    return start, end, content[start:end]


def raw_section_srcdoc(fragment: str, base_url: str | None) -> str:
    fragment = re.sub(r"(?is)<script\b.*?</script>", "", fragment)
    base = f'<base href="{html_escape(base_url, quote=True)}">' if base_url else ""
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  {base}
  <style>
    body {{ margin: 12px; color: #111827; font-family: Times New Roman, serif; font-size: 13px; }}
    table {{ max-width: 100%; border-collapse: collapse; }}
    img {{ max-width: 100%; height: auto; }}
  </style>
</head>
<body>
{fragment}
</body>
</html>"""


def _raw_container_start(content: str, raw_offset: int) -> int:
    window_start = max(0, raw_offset - 5000)
    window = content[window_start:raw_offset]
    matches = list(re.finditer(r"<(?:div|p|table|tr|h[1-6]|section|article|a)\b", window, flags=re.IGNORECASE))
    if matches:
        return window_start + matches[-1].start()
    return raw_offset


def _html_text(value: str) -> str:
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    value = unescape(value)
    return " ".join(value.split())


def _looks_like_outline_label(value: str) -> bool:
    if not 4 <= len(value) <= 160:
        return False
    lower = value.lower()
    if lower.startswith("item "):
        return False
    if re.fullmatch(r"[\d.,$%() -]+", value):
        return False
    alpha_count = sum(1 for character in value if character.isalpha())
    if alpha_count < 4:
        return False
    uppercase_ratio = sum(1 for character in value if character.isupper()) / max(alpha_count, 1)
    return uppercase_ratio > 0.55 or (value[:1].isupper() and not value.endswith("."))


def _looks_like_supplemental_label(value: str) -> bool:
    if not 4 <= len(value) <= 220:
        return False
    if re.fullmatch(r"[\d.,$%() -]+", value):
        return False
    if value.lower().startswith(("item ", "part ")):
        return False
    alpha_count = sum(1 for character in value if character.isalpha())
    return alpha_count >= 6


def _supplemental_sections_from_toc(chunk: str, toc_entries: list[dict]) -> list[dict]:
    starts = []
    seen_offsets = set()
    for entry in toc_entries:
        offset = _toc_entry_offset(chunk, entry)
        if offset is None or offset in seen_offsets:
            continue
        seen_offsets.add(offset)
        starts.append((offset, entry["label"]))
    starts.sort(key=lambda current: current[0])

    sections = []
    for index, (start, label) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else len(chunk)
        section_html = chunk[start:end]
        structure = raw_fragment_structure(section_html)
        sections.append(
            {
                "label": label,
                "text": _truncate(_html_text(section_html), 6000),
                "raw_bytes": len(section_html.encode("utf-8", errors="replace")),
                "table_count": structure["table_count"],
                "image_count": structure["image_count"],
                "raw_start": start,
                "raw_end": end,
            }
        )
    return sections


def _toc_entry_offset(chunk: str, entry: dict) -> int | None:
    href = entry.get("href")
    if href:
        return _anchor_offset(chunk, href)
    return _label_text_offset(chunk, entry["label"])


def _anchor_offset(chunk: str, href: str) -> int | None:
    if not href.startswith("#"):
        return None
    anchor = re.escape(href[1:])
    match = re.search(rf"(?is)\b(?:id|name)=[\"']{anchor}[\"']", chunk)
    if not match:
        return None
    tag_start = chunk.rfind("<", 0, match.start())
    return tag_start if tag_start >= 0 else match.start()


def _label_text_offset(chunk: str, label: str) -> int | None:
    tokens = re.findall(r"[A-Za-z0-9]+", label)
    if not tokens:
        return None
    separator = r"(?:\s|&nbsp;|&#160;|<[^>]+>)+"
    pattern = separator.join(re.escape(token) for token in tokens[:10])
    search_start = min(100000, max(len(chunk) // 20, 0))
    match = re.search(pattern, chunk[search_start:], flags=re.IGNORECASE)
    if not match:
        return None
    start = search_start + match.start()
    tag_start = chunk.rfind("<", 0, start)
    return tag_start if tag_start >= 0 else start


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "\n[truncated]"
