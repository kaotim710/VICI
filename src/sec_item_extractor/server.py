from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .extractor import extract_items


DEFAULT_ITEMS = ["1", "1A", "7"]
DEFAULT_MAX_BODY_BYTES = 25 * 1024 * 1024


class PayloadError(ValueError):
    pass


def extract_from_payload(payload: dict[str, Any]) -> dict:
    content = payload.get("content")
    if not isinstance(content, str) or not content.strip():
        raise PayloadError("Field 'content' must be a non-empty string.")

    items = payload.get("items", DEFAULT_ITEMS)
    if not isinstance(items, list) or not items or not all(isinstance(item, str) for item in items):
        raise PayloadError("Field 'items' must be a non-empty list of strings.")

    filing_id = payload.get("filing_id")
    if filing_id is not None and not isinstance(filing_id, str):
        raise PayloadError("Field 'filing_id' must be a string when provided.")

    return extract_items(content, target_items=items, filing_id=filing_id).to_dict()


class ExtractionHandler(BaseHTTPRequestHandler):
    max_body_bytes = DEFAULT_MAX_BODY_BYTES

    def do_GET(self) -> None:
        if self.path == "/health":
            self._write_json(200, {"status": "ok"})
            return
        self._write_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/extract":
            self._write_json(404, {"error": "not_found"})
            return

        try:
            payload = self._read_json_payload()
            result = extract_from_payload(payload)
        except PayloadError as error:
            self._write_json(400, {"error": "bad_request", "message": str(error)})
            return
        except json.JSONDecodeError:
            self._write_json(400, {"error": "bad_request", "message": "Request body must be valid JSON."})
            return

        self._write_json(200, result)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _read_json_payload(self) -> dict[str, Any]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise PayloadError("Content-Length must be an integer.") from error
        if content_length <= 0:
            raise PayloadError("Request body is required.")
        if content_length > self.max_body_bytes:
            raise PayloadError(f"Request body exceeds {self.max_body_bytes} bytes.")

        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except UnicodeDecodeError as error:
            raise PayloadError("Request body must be UTF-8 JSON.") from error
        if not isinstance(payload, dict):
            raise PayloadError("Request body must be a JSON object.")
        return payload

    def _write_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "0.0.0.0", port: int | None = None) -> None:
    resolved_port = port if port is not None else int(os.environ.get("PORT", "8000"))
    max_body_bytes = int(os.environ.get("SEC_EXTRACTOR_MAX_BODY_BYTES", str(DEFAULT_MAX_BODY_BYTES)))
    ExtractionHandler.max_body_bytes = max_body_bytes
    server = ThreadingHTTPServer((host, resolved_port), ExtractionHandler)
    print(f"SEC item extractor listening on {host}:{resolved_port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    run()
