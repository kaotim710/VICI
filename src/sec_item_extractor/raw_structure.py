from __future__ import annotations

import re
from html import escape as html_escape


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
    candidates: list[str] = []
    patterns = (
        r"(?is)<(?:b|strong)\b[^>]*>(.*?)</(?:b|strong)>",
        r"(?is)<h[1-6]\b[^>]*>(.*?)</h[1-6]>",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, fragment):
            text = _html_text(match.group(1))
            if _looks_like_outline_label(text):
                candidates.append(text[:140])
    return _dedupe(candidates, limit)


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
    value = re.sub(r"&nbsp;?", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"&amp;?", "&", value, flags=re.IGNORECASE)
    value = re.sub(r"&lt;?", "<", value, flags=re.IGNORECASE)
    value = re.sub(r"&gt;?", ">", value, flags=re.IGNORECASE)
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


def _dedupe(values: list[str], limit: int) -> list[str]:
    seen = set()
    result = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
        if len(result) >= limit:
            break
    return result
