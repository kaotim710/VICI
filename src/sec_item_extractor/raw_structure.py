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
