from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser

from .models import CleanDocument, NarrativeBlock


BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "br",
    "center",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "td",
    "th",
    "tr",
    "ul",
}


class FilingHTMLBlockExtractor(HTMLParser):
    def __init__(self, content: str) -> None:
        super().__init__(convert_charrefs=True)
        self._content = content
        self._line_starts = _line_starts(content)
        self._blocks: list[_RawBlock] = []
        self._current_parts: list[str] = []
        self._current_raw_start: int | None = None
        self._current_raw_end: int | None = None
        self._current_tag: str | None = None
        self._skip_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {name.lower(): value or "" for name, value in attrs}
        style = attr_map.get("style", "").lower().replace(" ", "")
        hidden = (
            tag in {"script", "style", "head", "title", "meta"}
            or "hidden" in attr_map
            or "display:none" in style
            or "visibility:hidden" in style
            or "font-size:0" in style
        )
        if hidden:
            self._flush_block()
            self._skip_stack.append(tag)
            return
        if tag in BLOCK_TAGS:
            self._flush_block()
            self._current_tag = tag

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._skip_stack:
            if self._skip_stack[-1] == tag:
                self._skip_stack.pop()
            return
        if tag in BLOCK_TAGS:
            self._flush_block()

    def handle_data(self, data: str) -> None:
        if self._skip_stack:
            return
        if not data or not data.strip():
            return
        raw_start, raw_end = self._locate_data(data)
        self._current_parts.append(data)
        if raw_start is not None:
            self._current_raw_start = raw_start if self._current_raw_start is None else min(self._current_raw_start, raw_start)
        if raw_end is not None:
            self._current_raw_end = raw_end if self._current_raw_end is None else max(self._current_raw_end, raw_end)

    def get_document(self) -> CleanDocument:
        self._flush_block()
        return _build_clean_document(self._blocks)

    def _flush_block(self) -> None:
        if not self._current_parts:
            self._current_tag = None
            return
        text = normalize_inline_text("".join(self._current_parts))
        if text:
            self._blocks.append(
                _RawBlock(
                    text=text,
                    raw_start=self._current_raw_start,
                    raw_end=self._current_raw_end,
                    tag=self._current_tag,
                )
            )
        self._current_parts = []
        self._current_raw_start = None
        self._current_raw_end = None
        self._current_tag = None

    def _locate_data(self, data: str) -> tuple[int | None, int | None]:
        line, column = self.getpos()
        rough_start = self._line_starts[line - 1] + column if 0 < line <= len(self._line_starts) else 0
        return rough_start, rough_start + len(data)


def html_to_text(content: str) -> str:
    return parse_document(content).text


def parse_document(content: str) -> CleanDocument:
    if not looks_like_html(content):
        text = normalize_text(content)
        block = NarrativeBlock(
            text=text,
            clean_start=0,
            clean_end=len(text),
            raw_start=0,
            raw_end=len(content),
            tag=None,
            source="text",
        )
        return CleanDocument(text=text, blocks=[block] if text else [], warnings=[])

    parser = FilingHTMLBlockExtractor(content)
    parser.feed(content)
    parser.close()
    return parser.get_document()


def looks_like_html(content: str) -> bool:
    sample = content[:5000].lower()
    return "<html" in sample or "<body" in sample or "<div" in sample or "<ix:" in sample


def normalize_text(content: str) -> str:
    text = unescape(content)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_inline_text(content: str) -> str:
    text = unescape(content)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class _RawBlock:
    def __init__(self, text: str, raw_start: int | None, raw_end: int | None, tag: str | None) -> None:
        self.text = text
        self.raw_start = raw_start
        self.raw_end = raw_end
        self.tag = tag


def _build_clean_document(raw_blocks: list[_RawBlock]) -> CleanDocument:
    blocks: list[NarrativeBlock] = []
    parts: list[str] = []
    offset = 0
    for raw_block in raw_blocks:
        if not raw_block.text:
            continue
        if parts:
            parts.append("\n\n")
            offset += 2
        clean_start = offset
        parts.append(raw_block.text)
        offset += len(raw_block.text)
        blocks.append(
            NarrativeBlock(
                text=raw_block.text,
                clean_start=clean_start,
                clean_end=offset,
                raw_start=raw_block.raw_start,
                raw_end=raw_block.raw_end,
                tag=raw_block.tag,
                source="html",
            )
        )
    return CleanDocument(text="".join(parts), blocks=blocks, warnings=[])


def _line_starts(content: str) -> list[int]:
    starts = [0]
    for index, character in enumerate(content):
        if character == "\n":
            starts.append(index + 1)
    return starts
