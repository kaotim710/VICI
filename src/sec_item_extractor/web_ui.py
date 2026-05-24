from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .extractor import extract_items
from .raw_structure import (
    raw_fragment_exhibit_links,
    raw_fragment_outline,
    raw_fragment_outline_sections,
    raw_fragment_supplemental_fragment,
    raw_fragment_structure,
    raw_fragment_supplemental_chunk,
    raw_section_fragment,
    raw_section_srcdoc,
    raw_structure_counts,
)
from .recovery import run_recovery_actions


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
INVENTORY_PATH = ROOT / "fixtures" / "gold" / "downloaded_seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"


def filing_options() -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    options = []
    for filing in manifest["filings"]:
        path = RAW_DIR / f"{filing['filing_id']}.html"
        options.append(
            {
                "filing_id": filing["filing_id"],
                "ticker": filing["ticker"],
                "fiscal_year": filing["fiscal_year"],
                "industry": filing["industry"],
                "form": filing["form"],
                "available": path.exists(),
                "bytes": path.stat().st_size if path.exists() else None,
            }
        )
    return options


def raw_filing_metadata(filing_id: str) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filings = {filing["filing_id"]: filing for filing in manifest["filings"]}
    if filing_id not in filings:
        raise KeyError(filing_id)

    path = RAW_DIR / f"{filing_id}.html"
    if not path.exists():
        raise FileNotFoundError(path)

    inventory = _inventory_by_filing_id()
    record = inventory.get(filing_id, {})
    return {
        "filing": filings[filing_id],
        "raw": {
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": record.get("sha256") or _sha256(path),
        },
        "cache_policy": "no-store",
    }


def extract_seed_filing(filing_id: str) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filings = {filing["filing_id"]: filing for filing in manifest["filings"]}
    if filing_id not in filings:
        raise KeyError(filing_id)

    path = RAW_DIR / f"{filing_id}.html"
    if not path.exists():
        raise FileNotFoundError(path)

    started = time.perf_counter()
    content = path.read_text(encoding="utf-8", errors="replace")
    result = extract_items(content, target_items=manifest["items"], filing_id=filing_id)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    result_dict = result.to_dict()
    _attach_raw_structure(result_dict, content, result.item_results)
    _append_supplemental_items(result_dict)
    item_count = len(result_dict.get("item_results", []))
    return {
        "filing": filings[filing_id],
        "elapsed_ms": elapsed_ms,
        "source_bytes": path.stat().st_size,
        "pipeline": {
            "ran": True,
            "cache": "disabled",
            "trigger": "on_demand_extract_request",
            "parser_version": result.parser_version,
        },
        "summary": {
            "status": result.status,
            "candidate_count": result.candidate_count,
            "toc_confidence": result.toc_confidence,
            "item_count": item_count,
        },
        "toc_entries": result_dict["toc_entries"],
        "items": [_item_contract(item, content) for item in result.item_results],
        "result": result_dict,
    }


def recover_seed_filing(filing_id: str, selections: dict[tuple[str | None, str], str] | None = None) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filings = {filing["filing_id"]: filing for filing in manifest["filings"]}
    if filing_id not in filings:
        raise KeyError(filing_id)

    path = RAW_DIR / f"{filing_id}.html"
    if not path.exists():
        raise FileNotFoundError(path)

    started = time.perf_counter()
    content = path.read_text(encoding="utf-8", errors="replace")
    extraction = extract_items(content, target_items=manifest["items"], filing_id=filing_id)
    recoveries = run_recovery_actions(content, extraction, selections=selections)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    return {
        "filing": filings[filing_id],
        "elapsed_ms": elapsed_ms,
        "pipeline": {
            "ran": True,
            "cache": "disabled",
            "trigger": "on_demand_recovery_request",
            "parser_version": extraction.parser_version,
        },
        "summary": {
            "status": extraction.status,
            "recovery_actions": len(recoveries),
        },
        "recoveries": [recovery.to_dict() for recovery in recoveries],
    }


def raw_section_preview(filing_id: str, item: str) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filings = {filing["filing_id"]: filing for filing in manifest["filings"]}
    if filing_id not in filings:
        raise KeyError(filing_id)

    path = RAW_DIR / f"{filing_id}.html"
    if not path.exists():
        raise FileNotFoundError(path)

    item = item.upper()
    content = path.read_text(encoding="utf-8", errors="replace")
    if item.startswith("SUPPLEMENTAL-"):
        return _supplemental_raw_section_preview(filings[filing_id], filing_id, item, content)
    result = extract_items(content, target_items=[item], filing_id=filing_id)
    item_result = result.item_results[0]
    if item_result.status != "success" or not item_result.start_evidence:
        raise ValueError(f"raw section is unavailable for Item {item}")

    start, end, fragment = raw_section_fragment(content, item_result)
    base_url = _archive_base_url(filing_id)
    structure = raw_fragment_structure(fragment)
    return {
        "filing": filings[filing_id],
        "item": item,
        "raw_start": start,
        "raw_end": end,
        "raw_bytes": len(fragment.encode("utf-8", errors="replace")),
        "table_count": structure["table_count"],
        "image_count": structure["image_count"],
        "base_url": base_url,
        "srcdoc": raw_section_srcdoc(fragment, base_url),
    }


def _supplemental_raw_section_preview(filing: dict, filing_id: str, item: str, content: str) -> dict:
    source_item = item.removeprefix("SUPPLEMENTAL-")
    result = extract_items(content, target_items=[source_item], filing_id=filing_id)
    item_result = result.item_results[0]
    if item_result.status != "success" or not item_result.start_evidence:
        raise ValueError(f"raw section is unavailable for Item {item}")

    source_start, _, source_fragment = raw_section_fragment(content, item_result)
    supplemental = raw_fragment_supplemental_fragment(source_fragment)
    if supplemental is None:
        raise ValueError(f"raw section is unavailable for Item {item}")
    relative_start, fragment = supplemental
    start = source_start + relative_start
    end = start + len(fragment)
    base_url = _archive_base_url(filing_id)
    structure = raw_fragment_structure(fragment)
    return {
        "filing": filing,
        "item": item,
        "raw_start": start,
        "raw_end": end,
        "raw_bytes": len(fragment.encode("utf-8", errors="replace")),
        "table_count": structure["table_count"],
        "image_count": structure["image_count"],
        "base_url": base_url,
        "srcdoc": raw_section_srcdoc(fragment, base_url),
    }


def _item_contract(item, raw_content: str | None = None) -> dict:
    raw_structure = _raw_structure_contract(raw_content, item) if raw_content is not None else {"table_count": 0, "image_count": 0}
    return {
        "item": item.item,
        "status": item.status,
        "confidence": {"level": item.confidence_level, "score": item.confidence_score},
        "warnings": item.warnings,
        "actions": [action.__dict__ for action in item.recommended_actions],
        "evidence": {
            "start": item.start_evidence.__dict__ if item.start_evidence else None,
            "end": item.end_evidence.__dict__ if item.end_evidence else None,
        },
        "text": item.text or "",
        "text_length": len(item.text or ""),
        "raw_structure": raw_structure,
    }


def _inventory_by_filing_id() -> dict[str, dict]:
    if not INVENTORY_PATH.exists():
        return {}
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    return {record["filing_id"]: record for record in inventory.get("files", [])}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_recovery_selections(payload: dict, filing_id: str) -> dict[tuple[str | None, str], str]:
    raw_selections = payload.get("selections", {}) if isinstance(payload, dict) else {}
    if not isinstance(raw_selections, dict):
        return {}
    selections: dict[tuple[str | None, str], str] = {}
    for raw_key, raw_value in raw_selections.items():
        if not isinstance(raw_key, str) or not isinstance(raw_value, str) or not raw_value.strip():
            continue
        if ":" in raw_key:
            selected_filing, item = raw_key.split(":", 1)
            selections[(selected_filing or filing_id, item.upper())] = raw_value
        else:
            selections[(filing_id, raw_key.upper())] = raw_value
    return selections


def _archive_base_url(filing_id: str) -> str | None:
    record = _inventory_by_filing_id().get(filing_id)
    if not record:
        return None
    cik = record.get("cik")
    accession = record.get("accession_number")
    if not cik or not accession:
        return None
    cik_no_padding = str(int("".join(character for character in str(cik) if character.isdigit())))
    accession_no_dashes = str(accession).replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik_no_padding}/{accession_no_dashes}/"


def _attach_raw_structure(result_dict: dict, content: str, item_results: list) -> None:
    for item_payload, item_result in zip(result_dict.get("item_results", []), item_results):
        item_payload["raw_structure"] = _raw_structure_contract(content, item_result)
        item_payload["raw_section_available"] = item_result.status == "success"


def _append_supplemental_items(result_dict: dict) -> None:
    for item_payload in list(result_dict.get("item_results", [])):
        chunk = item_payload.get("raw_structure", {}).get("supplemental_chunk")
        if not chunk:
            continue
        item_payload["raw_structure"]["supplemental_chunk"] = None
        result_dict["item_results"].append(_supplemental_item_payload(item_payload.get("item", ""), chunk))


def _supplemental_item_payload(source_item: str, chunk: dict) -> dict:
    return {
        "item": f"supplemental-{source_item.lower()}",
        "display_label": f"Supplemental after Item {source_item}",
        "title": chunk["label"],
        "status": "success",
        "text": chunk.get("text", ""),
        "start_offset": None,
        "end_offset": None,
        "confidence_level": "high",
        "confidence_score": 1.0,
        "confidence_components": [],
        "start_evidence": None,
        "end_evidence": None,
        "candidate_attempts": [],
        "validation_reasons": ["SUPPLEMENTAL_CHUNK_PARTITIONED_AFTER_ITEM_16"],
        "warnings": [],
        "recommended_actions": [],
        "strategy_used": "raw_supplemental_chunk_v1",
        "raw_section_available": True,
        "raw_structure": {
            "table_count": chunk.get("table_count", 0),
            "image_count": chunk.get("image_count", 0),
            "outline": [section["label"] for section in chunk.get("sections", [])],
            "sections": chunk.get("sections", []),
            "supplemental_chunk": None,
            "raw_bytes": chunk.get("raw_bytes", 0),
        },
    }


def _raw_structure_contract(content: str, item_result) -> dict:
    structure = raw_structure_counts(content, item_result)
    structure["outline"] = []
    structure["sections"] = []
    structure["supplemental_chunk"] = None
    structure["raw_bytes"] = 0
    try:
        _, _, fragment = raw_section_fragment(content, item_result)
    except ValueError:
        return structure
    structure["raw_bytes"] = len(fragment.encode("utf-8", errors="replace"))
    structure["outline"] = raw_fragment_outline(fragment)
    structure["sections"] = raw_fragment_outline_sections(fragment)
    exhibit_links = raw_fragment_exhibit_links(fragment)
    if not structure["sections"] and item_result.text:
        structure["sections"] = _text_outline_sections(item_result.text, exhibit_links)
        structure["outline"] = [section["label"] for section in structure["sections"]]
    elif exhibit_links:
        _attach_exhibit_links(structure["sections"], exhibit_links)
    if _can_partition_supplemental(item_result.item):
        structure["supplemental_chunk"] = raw_fragment_supplemental_chunk(fragment)
    return structure


def _can_partition_supplemental(item_name: str) -> bool:
    return item_name.upper() in {"15", "16"}


def _text_outline_sections(text: str, exhibit_links: dict[str, dict] | None = None, limit: int = 30) -> list[dict]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    starts: list[tuple[int, int, str]] = []
    seen = set()
    for index, line in enumerate(lines):
        label = ""
        content_start = index + 1
        if re.fullmatch(r"\d{1,2}", line) and index + 1 < len(lines) and _looks_like_text_outline_label(lines[index + 1]):
            label = f"{line} {lines[index + 1]}"
            content_start = index + 2
        elif re.fullmatch(r"\d+(?:\.\d+)+[A-Z]?", line) and index + 1 < len(lines):
            label = line
            content_start = index + 1
        elif not (index > 0 and re.fullmatch(r"\d{1,2}", lines[index - 1])) and _looks_like_text_outline_label(line):
            label = line
        if not label:
            continue
        label = label[:140]
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        starts.append((index, content_start, label))
        if len(starts) >= limit:
            break

    sections = []
    for position, (heading_index, content_start, label) in enumerate(starts):
        next_heading_index = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        section_text = "\n".join(lines[content_start:next_heading_index]).strip()
        section = {
            "label": label,
            "text": section_text[:6000] + ("\n[truncated]" if len(section_text) > 6000 else ""),
            "raw_bytes": len(section_text.encode("utf-8", errors="replace")),
            "table_count": 0,
            "image_count": 0,
        }
        _attach_exhibit_link(section, exhibit_links or {})
        sections.append(section)
    return sections


def _attach_exhibit_links(sections: list[dict], exhibit_links: dict[str, dict]) -> None:
    for section in sections:
        _attach_exhibit_link(section, exhibit_links)


def _attach_exhibit_link(section: dict, exhibit_links: dict[str, dict]) -> None:
    number_match = re.match(r"(?P<number>\d+(?:\.\d+)+[A-Z]?)\b", section.get("label", ""))
    if not number_match:
        return
    link = exhibit_links.get(number_match.group("number"))
    if not link:
        return
    section["href"] = link["href"]
    if section["label"] == number_match.group("number"):
        section["label"] = f"{section['label']} {link['label']}"[:180]


def _looks_like_text_outline_label(value: str) -> bool:
    if not 8 <= len(value) <= 180:
        return False
    if value.lower().startswith("item "):
        return False
    if re.fullmatch(r"[\d.,$%() -]+", value):
        return False
    if re.search(r"\.{2,}\s*\d+\s*$", value):
        return False
    alpha_count = sum(1 for character in value if character.isalpha())
    if alpha_count < 5:
        return False
    uppercase_ratio = sum(1 for character in value if character.isupper()) / max(alpha_count, 1)
    return uppercase_ratio > 0.55 or (value[:1].isupper() and not value.endswith("."))


class WebUiHandler(BaseHTTPRequestHandler):
    server_version = "SecItemExtractorWeb/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/":
            self._send_html(render_home())
            return
        if path.startswith("/filings/"):
            filing_id = unquote(path.removeprefix("/filings/"))
            self._send_html(render_detail(filing_id))
            return
        if path == "/api/filings":
            self._send_json({"filings": filing_options()})
            return
        if path.startswith("/api/filings/") and path.endswith("/raw-metadata"):
            filing_id = unquote(path.removeprefix("/api/filings/").removesuffix("/raw-metadata"))
            self._handle_raw_metadata(filing_id)
            return
        if path.startswith("/api/filings/") and path.endswith("/extract"):
            filing_id = unquote(path.removeprefix("/api/filings/").removesuffix("/extract"))
            self._handle_extract(filing_id)
            return
        if path.startswith("/api/filings/") and "/raw-section/" in path:
            filing_id, item = unquote(path.removeprefix("/api/filings/")).split("/raw-section/", 1)
            self._handle_raw_section(filing_id, item)
            return

        self._send_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path.startswith("/api/filings/") and path.endswith("/recover"):
            filing_id = unquote(path.removeprefix("/api/filings/").removesuffix("/recover"))
            self._handle_recover(filing_id)
            return
        self._send_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return

    def _handle_raw_metadata(self, filing_id: str) -> None:
        try:
            self._send_json(raw_filing_metadata(filing_id))
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)

    def _handle_extract(self, filing_id: str) -> None:
        try:
            self._send_json(extract_seed_filing(filing_id))
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)

    def _handle_raw_section(self, filing_id: str, item: str) -> None:
        try:
            self._send_json(raw_section_preview(filing_id, item))
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except ValueError as error:
            self._send_json({"error": "raw_section_unavailable", "message": str(error)}, status=HTTPStatus.NOT_FOUND)

    def _handle_recover(self, filing_id: str) -> None:
        try:
            payload = self._read_json_body()
            selections = _parse_recovery_selections(payload, filing_id)
            self._send_json(recover_seed_filing(filing_id, selections=selections))
        except json.JSONDecodeError:
            self._send_json({"error": "bad_json"}, status=HTTPStatus.BAD_REQUEST)
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length)
        payload = json.loads(body.decode("utf-8"))
        return payload if isinstance(payload, dict) else {}

    def _send_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self._send_no_cache_headers("text/html; charset=utf-8", len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_no_cache_headers("application/json; charset=utf-8", len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_no_cache_headers(self, content_type: str, content_length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")


def render_home() -> str:
    return _page(
        "SEC 10-K Filing Selector",
        """
        <main class="home-shell">
          <section class="selector-panel">
            <div class="toolbar">
              <div>
                <h1>SEC 10-K Test Filings</h1>
                <p class="muted">Choose a local seed filing. Extraction runs only after you open a filing.</p>
              </div>
              <button id="refresh-filings" class="icon-button" title="Refresh filing list" aria-label="Refresh filing list">R</button>
            </div>
            <div id="filing-list" class="filing-grid" aria-live="polite"></div>
          </section>
        </main>
        <script>
        const list = document.getElementById("filing-list");
        document.getElementById("refresh-filings").addEventListener("click", loadFilings);
        loadFilings();

        async function loadFilings() {
          list.innerHTML = '<div class="loading">Loading filings...</div>';
          const response = await fetch('/api/filings', {cache: 'no-store'});
          const payload = await response.json();
          list.innerHTML = '';
          for (const filing of payload.filings) {
            const link = document.createElement('a');
            link.className = 'filing-card';
            link.href = `/filings/${encodeURIComponent(filing.filing_id)}`;
            link.innerHTML = `
              <span class="ticker">${escapeHtml(filing.ticker)}</span>
              <span class="meta">${escapeHtml(filing.industry)} | ${filing.fiscal_year} | ${escapeHtml(filing.form)}</span>
              <span class="${filing.available ? 'available' : 'missing'}">${filing.available ? 'available' : 'missing raw filing'}</span>
            `;
            list.appendChild(link);
          }
        }
        </script>
        """,
    )


def render_detail(filing_id: str) -> str:
    safe_filing_id = json.dumps(filing_id)
    return _page(
        f"{filing_id} Extraction",
        f"""
        <main class="workspace-shell">
          <aside class="toc-panel">
            <a class="back-link" href="/">Back to filings</a>
            <h1 id="filing-title">{filing_id}</h1>
            <p id="run-meta" class="muted">Pipeline has not run yet.</p>
            <div class="sidebar-actions">
              <button id="run-button" class="primary-button">Run extraction</button>
              <button id="recover-button" class="secondary-button" disabled>Run recovery actions</button>
            </div>
            <nav id="toc-list" class="toc-list" aria-label="Extracted item navigation"></nav>
          </aside>
          <section class="item-panel">
            <div id="status-banner" class="status-banner">Select Run extraction to parse this filing now.</div>
            <section id="metadata-panel" class="metadata-panel"></section>
            <section id="recovery-panel" class="recovery-panel"></section>
            <div id="items" class="items"></div>
          </section>
        </main>
        <script>
        const filingId = {safe_filing_id};
        const runButton = document.getElementById('run-button');
        const recoverButton = document.getElementById('recover-button');
        const tocList = document.getElementById('toc-list');
        const items = document.getElementById('items');
        const statusBanner = document.getElementById('status-banner');
        const runMeta = document.getElementById('run-meta');
        const metadataPanel = document.getElementById('metadata-panel');
        const recoveryPanel = document.getElementById('recovery-panel');
        let lastExtraction = null;

        runButton.addEventListener('click', runExtraction);
        recoverButton.addEventListener('click', runRecovery);
        loadMetadata();

        async function loadMetadata() {{
          metadataPanel.innerHTML = '<div class="loading slim">Loading raw filing metadata...</div>';
          const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/raw-metadata`, {{cache: 'no-store'}});
          const payload = await response.json();
          if (!response.ok) {{
            metadataPanel.innerHTML = `<div class="status-banner error">Metadata failed: ${{escapeHtml(payload.error || 'unknown')}}</div>`;
            return;
          }}
          metadataPanel.innerHTML = `
            <div class="metadata-row">
              <span>${{escapeHtml(payload.raw.path)}}</span>
              <span>${{Number(payload.raw.bytes).toLocaleString()}} bytes</span>
              <span>sha256 ${{escapeHtml(payload.raw.sha256.slice(0, 12))}}</span>
            </div>
          `;
        }}

        async function runExtraction() {{
          runButton.disabled = true;
          recoverButton.disabled = true;
          statusBanner.textContent = 'Running extraction pipeline...';
          tocList.innerHTML = '';
          recoveryPanel.innerHTML = '';
          items.innerHTML = '<div class="loading">Parsing filing and reconstructing item boundaries...</div>';
          try {{
            const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/extract`, {{cache: 'no-store'}});
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.error || 'extract_failed');
            lastExtraction = payload;
            renderExtraction(payload);
          }} catch (error) {{
            statusBanner.textContent = `Extraction failed: ${{error.message}}`;
            items.innerHTML = '';
          }} finally {{
            runButton.disabled = false;
          }}
        }}

        function renderExtraction(payload) {{
          const result = payload.result;
          document.getElementById('filing-title').textContent = `${{payload.filing.ticker}} ${{payload.filing.fiscal_year}}`;
          runMeta.textContent = `${{payload.filing.industry}} | ${{payload.filing.form}} | ${{payload.source_bytes.toLocaleString()}} bytes | ${{payload.elapsed_ms}} ms`;
          statusBanner.textContent = `${{result.status}} | ${{result.item_results.length}} items | TOC ${{result.toc_confidence}}`;
          recoverButton.disabled = !result.item_results.some(item => item.recommended_actions.length);
          renderToc(result);
          renderItems(result.item_results);
          renderRecoveryControls(result.item_results);
        }}

        function renderToc(result) {{
          const titles = new Map((result.toc_entries || []).map(entry => [entry.item, entry.title || entry.text]));
          tocList.innerHTML = '';
          for (const item of result.item_results) {{
            const link = document.createElement('a');
            link.href = `#item-${{cssId(item.item)}}`;
            link.className = `toc-link ${{item.status}} ${{item.confidence_level}}`;
            const label = item.display_label || `Item ${{item.item}}`;
            link.innerHTML = `
              <span>${{escapeHtml(label)}}</span>
              <small>${{escapeHtml(item.title || titles.get(item.item) || item.status)}}</small>
              <em>${{escapeHtml(item.status)}} | ${{escapeHtml(item.confidence_level)}} ${{Number(item.confidence_score).toFixed(2)}}</em>
            `;
            tocList.appendChild(link);
          }}
        }}

        function renderItems(itemResults) {{
          items.innerHTML = '';
          for (const item of itemResults) {{
            const article = document.createElement('article');
            article.className = 'item-card';
            article.id = `item-${{cssId(item.item)}}`;
            const evidenceId = `evidence-${{cssId(item.item)}}`;
            const warningLinks = item.warnings.length
              ? item.warnings.map(warning => `<a href="#${{evidenceId}}" class="warning-chip">${{escapeHtml(warning)}}</a>`).join('')
              : '<span class="empty-chip">none</span>';
            const actionLinks = item.recommended_actions.length
              ? item.recommended_actions.map(action => `<a href="#recovery-panel" class="action-chip ${{escapeHtml(action.severity)}}">${{escapeHtml(action.action_type)}}:${{escapeHtml(action.reason)}}</a>`).join('')
              : '<span class="empty-chip">none</span>';
            const text = item.text || '';
            const isSupplemental = String(item.item || '').startsWith('supplemental-');
            const structureTags = renderStructureTags(item.raw_structure || {{}});
            const rawSections = Array.isArray(item.raw_structure?.sections) ? item.raw_structure.sections : [];
            const structurePanel = isSupplemental ? renderStructurePanel(item) : '';
            const showMainText = !(isSupplemental && rawSections.length);
            const rawTools = item.raw_section_available === false ? '' : `
              <div class="raw-section-tools">
                <button class="secondary-button compact" data-raw-item="${{escapeHtml(item.item)}}">Show original filing structure</button>
                <span class="raw-section-meta"></span>
              </div>
              <div class="raw-section-preview"></div>
            `;
            const heading = item.display_label || `Item ${{item.item}}`;
            article.innerHTML = `
              <header class="item-header">
                <div>
                  <h2>${{escapeHtml(heading)}}</h2>
                  <p class="muted">${{escapeHtml(item.status)}} | ${{escapeHtml(item.confidence_level)}} ${{Number(item.confidence_score).toFixed(2)}} | ${{(item.text || '').length.toLocaleString()}} chars</p>
                </div>
                <div class="item-badges">
                  ${{structureTags}}
                  <span class="pill ${{escapeHtml(item.confidence_level)}}">${{escapeHtml(item.confidence_level)}}</span>
                </div>
              </header>
              <div class="extracted-view">
                <dl id="${{evidenceId}}" class="evidence-grid">
                  <div><dt>Start</dt><dd>${{escapeHtml(item.start_evidence?.text || 'none')}}</dd></div>
                  <div><dt>End</dt><dd>${{escapeHtml(item.end_evidence?.text || 'none')}}</dd></div>
                  <div><dt>Warnings</dt><dd class="chip-row">${{warningLinks}}</dd></div>
                  <div><dt>Actions</dt><dd class="chip-row">${{actionLinks}}</dd></div>
                </dl>
                ${{structurePanel}}
                ${{showMainText ? '<pre class="item-text"></pre>' : ''}}
              </div>
              ${{rawTools}}
            `;
            const itemText = article.querySelector('.item-text');
            if (itemText) itemText.textContent = item.text || '';
            const rawButton = article.querySelector('[data-raw-item]');
            if (rawButton) rawButton.addEventListener('click', () => loadRawSection(item.item, article));
            items.appendChild(article);
          }}
        }}

        function renderRecoveryControls(itemResults) {{
          const actionable = [];
          for (const item of itemResults) {{
            for (const action of item.recommended_actions) {{
              actionable.push({{item, action}});
            }}
          }}
          if (!actionable.length) {{
            recoveryPanel.innerHTML = '';
            return;
          }}
          recoveryPanel.innerHTML = `
            <header class="panel-header">
              <div>
                <h2>Recovery actions</h2>
                <p class="muted">${{actionable.length}} actions generated from current extraction evidence.</p>
              </div>
            </header>
            <div class="recovery-actions"></div>
          `;
          const container = recoveryPanel.querySelector('.recovery-actions');
          for (const entry of actionable) {{
            const item = entry.item;
            const action = entry.action;
            const row = document.createElement('div');
            row.className = `recovery-action ${{escapeHtml(action.severity)}}`;
            const selector = action.reason === 'internal_item_toc_detected'
              ? `<label>Selection<select data-recovery-selection="${{escapeHtml(item.item)}}">${{action.options.map(option => `<option value="${{escapeHtml(option)}}">${{escapeHtml(option)}}</option>`).join('')}}</select></label>`
              : '';
            const reviewSnippets = renderReviewSnippets(item, action);
            row.innerHTML = `
              <div>
                <strong>Item ${{escapeHtml(item.item)}} | ${{escapeHtml(action.action_type)}}:${{escapeHtml(action.reason)}}</strong>
                <p>${{escapeHtml(action.description)}}</p>
                <small>${{escapeHtml(action.severity)}} | user input ${{action.requires_user_input ? 'yes' : 'no'}} | ${{escapeHtml(action.next_step || 'none')}}</small>
              </div>
              ${{reviewSnippets}}
              ${{selector}}
            `;
            container.appendChild(row);
          }}
        }}

        function renderStructureTags(rawStructure) {{
          const tags = [];
          const tableCount = Number(rawStructure.table_count || 0);
          const imageCount = Number(rawStructure.image_count || 0);
          if (tableCount > 0) tags.push(`<span class="structure-tag table">tables ${{tableCount}}</span>`);
          if (imageCount > 0) tags.push(`<span class="structure-tag image">images ${{imageCount}}</span>`);
          return tags.join('');
        }}

        function renderStructurePanel(item) {{
          const rawStructure = item.raw_structure || {{}};
          const rawSections = Array.isArray(rawStructure.sections) ? rawStructure.sections : [];
          const rawOutline = Array.isArray(rawStructure.outline) ? rawStructure.outline : [];
          const textOutline = outlineEntriesForText(item.text || '');
          const outline = rawSections.length ? rawSections.map(section => section.label) : (rawOutline.length ? rawOutline : textOutline);
          const rawBytes = Number(rawStructure.raw_bytes || 0);
          const tableCount = Number(rawStructure.table_count || 0);
          const shouldShow = rawSections.length || outline.length || rawBytes > 250000 || tableCount > 50;
          if (!shouldShow) return '';
          const sectionContent = rawSections.length
            ? `<div class="structure-section-list">${{rawSections.slice(0, 30).map(renderStructureSection).join('')}}</div>`
            : `<ol>${{outline.length ? outline.slice(0, 30).map(label => `<li>${{escapeHtml(label)}}</li>`).join('') : '<li>No bold/internal headings detected; use original filing structure for full review.</li>'}}</ol>`;
          return `
            <details class="structure-outline">
              <summary>Section structure</summary>
              <div class="structure-outline-meta">${{Number(rawBytes).toLocaleString()}} raw bytes | ${{tableCount}} tables | ${{Number(rawStructure.image_count || 0)}} images</div>
              ${{sectionContent}}
            </details>
          `;
        }}

        function renderStructureSection(section, index) {{
          const text = String(section.text || '').trim() || String(section.label || '').trim() || 'No text extracted for this subsection.';
          const tableCount = Number(section.table_count || 0);
          const imageCount = Number(section.image_count || 0);
          const label = section.href
            ? `<a href="${{escapeHtml(section.href)}}" target="_blank" rel="noopener noreferrer">${{escapeHtml(section.label || `Section ${{index + 1}}`)}}</a>`
            : `<span>${{escapeHtml(section.label || `Section ${{index + 1}}`)}}</span>`;
          return `
            <details class="structure-section" ${{index === 0 ? 'open' : ''}}>
              <summary>
                ${{label}}
                <small>${{Number(section.raw_bytes || 0).toLocaleString()}} bytes | ${{tableCount}} tables | ${{imageCount}} images</small>
              </summary>
              <pre>${{escapeHtml(text)}}</pre>
            </details>
          `;
        }}

        function outlineEntriesForText(text) {{
          const result = [];
          const seen = new Set();
          const lines = String(text || '').split(/\\n+/).map(line => line.replace(/\\s+/g, ' ').trim()).filter(Boolean);
          for (const line of lines) {{
            if (result.length >= 30) break;
            if (!looksLikeOutlineLabel(line)) continue;
            const key = line.toLowerCase();
            if (seen.has(key)) continue;
            seen.add(key);
            result.push(line.slice(0, 140));
          }}
          return result;
        }}

        function looksLikeOutlineLabel(line) {{
          if (line.length < 8 || line.length > 160) return false;
          if (/^item\\s+/i.test(line)) return false;
          if (/\\.{2,}\\s*\\d+\\s*$/.test(line)) return false;
          if (/^[\\d.,$%()\\s-]+$/.test(line)) return false;
          const letters = (line.match(/[A-Za-z]/g) || []).length;
          if (letters < 5) return false;
          const uppercase = (line.match(/[A-Z]/g) || []).length / Math.max(letters, 1);
          return uppercase > 0.55 || (/^[A-Z]/.test(line) && !line.endsWith('.'));
        }}

        async function runRecovery() {{
          if (!lastExtraction) return;
          recoverButton.disabled = true;
          const selections = {{}};
          for (const select of document.querySelectorAll('[data-recovery-selection]')) {{
            selections[`${{filingId}}:${{select.dataset.recoverySelection}}`] = select.value;
          }}
          statusBanner.textContent = 'Running deterministic recovery actions...';
          const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/recover`, {{
            method: 'POST',
            cache: 'no-store',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{selections}})
          }});
          const payload = await response.json();
          if (!response.ok) {{
            statusBanner.textContent = `Recovery failed: ${{payload.error || 'unknown'}}`;
            recoverButton.disabled = false;
            return;
          }}
          renderRecoveryResults(payload);
          statusBanner.textContent = `Recovery complete | ${{payload.summary.recovery_actions}} actions | ${{payload.elapsed_ms}} ms`;
          recoverButton.disabled = false;
        }}

        function renderRecoveryResults(payload) {{
          const resultBlock = document.createElement('section');
          resultBlock.className = 'recovery-results';
          resultBlock.innerHTML = '<h2>Recovery results</h2>';
          for (const recovery of payload.recoveries) {{
            const card = document.createElement('article');
            card.className = `recovery-result ${{escapeHtml(recovery.status)}}`;
            card.innerHTML = `
              <h3>Item ${{escapeHtml(recovery.item)}} | ${{escapeHtml(recovery.reason)}}</h3>
              <p>${{escapeHtml(recovery.status)}} | ${{escapeHtml(recovery.severity)}} | ${{escapeHtml(recovery.next_step || 'none')}}</p>
              <p>${{escapeHtml(recovery.message)}}</p>
              <pre></pre>
            `;
            card.querySelector('pre').textContent = recovery.extracted_text ? edgeSnippet(recovery.extracted_text, 'start') + '\\n\\n' + edgeSnippet(recovery.extracted_text, 'end') : '';
            resultBlock.appendChild(card);
          }}
          recoveryPanel.appendChild(resultBlock);
        }}

        async function loadRawSection(itemId, article) {{
          const button = article.querySelector('[data-raw-item]');
          const meta = article.querySelector('.raw-section-meta');
          const preview = article.querySelector('.raw-section-preview');
          const extractedView = article.querySelector('.extracted-view');
          if (article.dataset.rawVisible === 'true') {{
            article.dataset.rawVisible = 'false';
            if (extractedView) extractedView.hidden = false;
            preview.hidden = true;
            button.textContent = 'Show original filing structure';
            meta.textContent = '';
            return;
          }}
          article.dataset.rawVisible = 'true';
          if (extractedView) extractedView.hidden = true;
          preview.hidden = false;
          button.textContent = 'Show extracted view';
          if (preview.dataset.loaded === 'true') {{
            meta.textContent = preview.dataset.meta || '';
            return;
          }}
          button.disabled = true;
          meta.textContent = 'Loading original HTML...';
          preview.innerHTML = '';
          try {{
            const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/raw-section/${{encodeURIComponent(itemId)}}`, {{cache: 'no-store'}});
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.message || payload.error || 'raw_section_failed');
            meta.textContent = `${{payload.table_count}} tables | ${{payload.image_count}} images | ${{Number(payload.raw_bytes).toLocaleString()}} bytes`;
            preview.dataset.meta = meta.textContent;
            const iframe = document.createElement('iframe');
            iframe.className = 'raw-section-frame';
            iframe.setAttribute('sandbox', '');
            iframe.srcdoc = payload.srcdoc;
            preview.appendChild(iframe);
            preview.dataset.loaded = 'true';
          }} catch (error) {{
            meta.textContent = `Original view failed: ${{error.message}}`;
          }} finally {{
            button.disabled = false;
          }}
        }}

        function edgeSnippet(text, mode) {{
          const value = String(text || '').replace(/\\s+/g, ' ').trim();
          if (value.length <= 520) return value;
          return mode === 'end' ? value.slice(-520) : value.slice(0, 520);
        }}

        function renderReviewSnippets(item, action) {{
          if (!['section_reference_detected', 'exhibit_index_detected', 'external_or_other_document_reference'].includes(action.reason)) {{
            return '';
          }}
          const snippets = reviewSnippetsFor(item.text || '', action.reason);
          if (!snippets.length) {{
            return '';
          }}
          return `
            <details class="review-snippets" open>
              <summary>Review snippets</summary>
              ${{snippets.map(snippet => `<pre>${{escapeHtml(snippet)}}</pre>`).join('')}}
            </details>
          `;
        }}

        function reviewSnippetsFor(text, reason) {{
          const patterns = reason === 'exhibit_index_detected'
            ? [/\\bexhibit(?:s| index)?\\b/i, /\\bschedule(?:s)?\\b/i, /\\btable\\b/i]
            : [/\\bincorporated\\s+herein\\s+by\\s+reference\\b/i, /\\bsee\\s+(?:the\\s+)?(?:annual report|proxy statement|exhibit index|note\\s+\\d+|part\\s+[ivx]+|item\\s+\\d)/i, /\\brefer(?:red|s|ring)?\\s+to\\b/i, /\\bappears?\\s+on\\s+pages?\\s+\\d+/i];
          const lines = String(text || '').split(/\\n+/).map(line => line.replace(/\\s+/g, ' ').trim()).filter(Boolean);
          const snippets = [];
          for (let index = 0; index < lines.length && snippets.length < 4; index += 1) {{
            if (!patterns.some(pattern => pattern.test(lines[index]))) continue;
            const start = Math.max(0, index - 1);
            const end = Math.min(lines.length, index + 2);
            snippets.push(lines.slice(start, end).join('\\n'));
          }}
          if (!snippets.length && text.trim()) {{
            snippets.push(edgeSnippet(text, 'start'));
          }}
          return snippets;
        }}
        </script>
        """,
    )


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Cache-Control" content="no-store">
  <title>{title}</title>
  <style>{_styles()}</style>
</head>
<body>
{body}
<script>
function escapeHtml(value) {{
  return String(value ?? '').replace(/[&<>"']/g, character => ({{
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }}[character]));
}}
function cssId(value) {{
  return String(value).replace(/[^a-zA-Z0-9_-]/g, '-');
}}
</script>
</body>
</html>"""


def _styles() -> str:
    return """
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #f6f7f9;
  color: #19212a;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: inherit; text-decoration: none; }
h1, h2, p { margin: 0; }
.muted { color: #647080; }
.home-shell { max-width: 1180px; margin: 0 auto; padding: 32px 24px; }
.selector-panel { display: grid; gap: 24px; }
.toolbar { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.toolbar h1 { font-size: 28px; line-height: 1.15; }
.icon-button, .primary-button {
  border: 1px solid #c9d1da;
  background: #ffffff;
  color: #1e2a36;
  border-radius: 6px;
  min-height: 40px;
  padding: 0 14px;
  cursor: pointer;
}
.primary-button { background: #1769aa; border-color: #1769aa; color: white; width: 100%; }
.secondary-button {
  border: 1px solid #c9d1da;
  background: #ffffff;
  color: #1e2a36;
  border-radius: 6px;
  min-height: 40px;
  padding: 0 14px;
  cursor: pointer;
  width: 100%;
}
.secondary-button.compact {
  width: auto;
  min-height: 34px;
  padding: 0 10px;
}
.primary-button:disabled, .secondary-button:disabled { opacity: 0.55; cursor: wait; }
.filing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.filing-card {
  display: grid;
  gap: 8px;
  min-height: 112px;
  padding: 14px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
}
.filing-card:hover { border-color: #1769aa; }
.ticker { font-size: 22px; font-weight: 700; }
.meta { color: #44515f; }
.available { color: #137333; font-size: 13px; }
.missing { color: #a13b2b; font-size: 13px; }
.workspace-shell {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  min-height: 100vh;
}
.toc-panel {
  position: sticky;
  top: 0;
  align-self: start;
  height: 100vh;
  overflow: auto;
  padding: 18px;
  border-right: 1px solid #d9dee5;
  background: #ffffff;
}
.back-link { display: inline-block; margin-bottom: 18px; color: #1769aa; }
.toc-panel h1 { font-size: 22px; margin-bottom: 6px; overflow-wrap: anywhere; }
.sidebar-actions { display: grid; gap: 8px; margin: 16px 0; }
.toc-list { display: grid; gap: 4px; }
.toc-link {
  display: grid;
  gap: 2px;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid transparent;
}
.toc-link:hover { border-color: #c9d1da; background: #f6f7f9; }
.toc-link span { font-weight: 700; }
.toc-link small { color: #647080; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.toc-link em { color: #647080; font-size: 12px; font-style: normal; }
.toc-link.not_present { opacity: 0.55; }
.toc-link.high { border-left: 3px solid #2d7d46; }
.toc-link.medium { border-left: 3px solid #b87900; }
.toc-link.low { border-left: 3px solid #c14f3d; }
.item-panel { min-width: 0; padding: 18px; }
.status-banner {
  position: sticky;
  top: 0;
  z-index: 2;
  margin-bottom: 12px;
  padding: 12px 14px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
}
.status-banner.error { border-color: #efc1b7; color: #a13b2b; background: #fff0ec; }
.metadata-panel, .recovery-panel { margin-bottom: 12px; }
.metadata-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 12px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
  color: #44515f;
  font-size: 13px;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
  padding: 12px 0;
}
.panel-header h2, .recovery-results h2 { font-size: 18px; margin: 0; }
.recovery-actions, .recovery-results { display: grid; gap: 8px; }
.recovery-action, .recovery-result {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
}
.recovery-action.blocked { border-left: 3px solid #c14f3d; }
.recovery-action.review { border-left: 3px solid #b87900; }
.recovery-action.info { border-left: 3px solid #1769aa; }
.recovery-action p, .recovery-action small, .recovery-result p { margin: 4px 0 0; color: #44515f; }
.recovery-action label { display: grid; gap: 4px; color: #44515f; font-size: 13px; }
.recovery-action select {
  max-width: 420px;
  min-height: 34px;
  border: 1px solid #c9d1da;
  border-radius: 6px;
  background: #ffffff;
  color: #19212a;
}
.review-snippets {
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  background: #fbfcfd;
}
.review-snippets summary { cursor: pointer; padding: 8px 10px; color: #44515f; }
.review-snippets pre {
  max-height: 180px;
  overflow: auto;
  margin: 0;
  padding: 8px 10px;
  border-top: 1px solid #e0e4e9;
  white-space: pre-wrap;
  font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.recovery-result h3 { margin: 0; font-size: 16px; }
.recovery-result pre {
  max-height: 220px;
  overflow: auto;
  margin: 0;
  padding: 10px;
  border-radius: 6px;
  background: #fbfcfd;
  white-space: pre-wrap;
}
.items { display: grid; gap: 14px; }
.item-card {
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}
.item-header { display: flex; justify-content: space-between; gap: 16px; align-items: start; }
.item-header h2 { font-size: 20px; }
.item-badges { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.pill {
  border-radius: 999px;
  padding: 4px 9px;
  font-size: 12px;
  border: 1px solid #c9d1da;
  background: #f6f7f9;
}
.pill.high { color: #137333; background: #edf7ee; border-color: #b8dfbd; }
.pill.medium { color: #8a5a00; background: #fff6dd; border-color: #efd48b; }
.pill.low { color: #a13b2b; background: #fff0ec; border-color: #efc1b7; }
.structure-tag {
  border-radius: 999px;
  padding: 4px 9px;
  font-size: 12px;
  border: 1px solid #c9d1da;
  background: #f6f7f9;
  color: #44515f;
}
.structure-tag.table { color: #155e75; border-color: #a5d8e6; background: #ecfeff; }
.structure-tag.image { color: #7c3d12; border-color: #f2c59b; background: #fff7ed; }
.evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 14px 0;
}
.evidence-grid div {
  min-width: 0;
  padding: 10px;
  border-radius: 6px;
  background: #f6f7f9;
}
dt { font-size: 12px; color: #647080; margin-bottom: 4px; }
dd { margin: 0; overflow-wrap: anywhere; }
.chip-row { display: flex; gap: 6px; flex-wrap: wrap; }
.warning-chip, .action-chip, .empty-chip {
  display: inline-block;
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 12px;
  border: 1px solid #c9d1da;
  background: #ffffff;
}
.warning-chip { color: #8a5a00; border-color: #efd48b; background: #fff6dd; }
.action-chip.blocked { color: #a13b2b; border-color: #efc1b7; background: #fff0ec; }
.action-chip.review { color: #8a5a00; border-color: #efd48b; background: #fff6dd; }
.action-chip.info { color: #1769aa; border-color: #b8d5ee; background: #edf5fb; }
.empty-chip { color: #647080; background: #f6f7f9; }
.snippet-details {
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  margin-bottom: 12px;
  background: #fbfcfd;
}
.snippet-details summary { cursor: pointer; padding: 10px 12px; color: #44515f; }
.snippet-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  padding: 0 12px 12px;
}
.snippet-grid pre {
  margin: 0;
  max-height: 180px;
  overflow: auto;
  white-space: pre-wrap;
  font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.structure-outline {
  border: 1px solid #d8e1ea;
  border-radius: 6px;
  margin-bottom: 12px;
  background: #fbfcfd;
}
.structure-outline summary { cursor: pointer; padding: 10px 12px; color: #304255; }
.structure-outline-meta {
  padding: 0 12px 8px;
  color: #647080;
  font-size: 13px;
}
.structure-outline ol {
  margin: 0;
  padding: 0 12px 12px 32px;
  columns: 2;
  column-gap: 28px;
}
.structure-outline li {
  break-inside: avoid;
  margin-bottom: 5px;
  color: #19212a;
}
.structure-section-list {
  display: grid;
  gap: 8px;
  padding: 0 12px 12px;
}
.structure-section {
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  background: #ffffff;
}
.structure-section summary {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: start;
  padding: 9px 10px;
  cursor: pointer;
}
.structure-section summary span,
.structure-section summary a {
  font-weight: 700;
  overflow-wrap: anywhere;
}
.structure-section summary a {
  color: #1769aa;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.structure-section summary small {
  flex: 0 0 auto;
  color: #647080;
  font-size: 12px;
  white-space: nowrap;
}
.structure-section pre {
  max-height: 260px;
  overflow: auto;
  margin: 0;
  padding: 10px;
  border-top: 1px solid #e0e4e9;
  background: #fbfcfd;
  white-space: pre-wrap;
  font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.raw-section-tools {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.raw-section-meta { color: #647080; font-size: 13px; }
.raw-section-preview { margin-bottom: 12px; }
.raw-section-frame {
  width: 100%;
  min-height: 520px;
  border: 1px solid #c9d1da;
  border-radius: 6px;
  background: #ffffff;
}
.item-text {
  max-height: 460px;
  overflow: auto;
  margin: 0;
  padding: 12px;
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  background: #fbfcfd;
  white-space: pre-wrap;
  font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.loading { padding: 18px; color: #647080; }
.loading.slim { padding: 10px; }
@media (max-width: 820px) {
  .workspace-shell { grid-template-columns: 1fr; }
  .toc-panel { position: relative; height: auto; border-right: 0; border-bottom: 1px solid #d9dee5; }
  .evidence-grid { grid-template-columns: 1fr; }
  .snippet-grid { grid-template-columns: 1fr; }
}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local SEC 10-K extraction review UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), WebUiHandler)
    print(f"serving SEC 10-K extraction UI at http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
