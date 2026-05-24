from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser


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


class FilingHTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
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
            self._skip_stack.append(tag)
            return
        if tag in BLOCK_TAGS:
            self._append_newline()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._skip_stack:
            if self._skip_stack[-1] == tag:
                self._skip_stack.pop()
            return
        if tag in BLOCK_TAGS:
            self._append_newline()

    def handle_data(self, data: str) -> None:
        if self._skip_stack:
            return
        if data:
            self._parts.append(data)

    def get_text(self) -> str:
        return normalize_text("".join(self._parts))

    def _append_newline(self) -> None:
        if self._parts and not self._parts[-1].endswith("\n"):
            self._parts.append("\n")


def html_to_text(content: str) -> str:
    if not looks_like_html(content):
        return normalize_text(content)
    parser = FilingHTMLTextExtractor()
    parser.feed(content)
    parser.close()
    return parser.get_text()


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
