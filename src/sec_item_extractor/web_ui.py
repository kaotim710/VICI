from __future__ import annotations

import argparse
import hashlib
import json
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .extractor import extract_items
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
            "item_count": len(result.item_results),
        },
        "toc_entries": result_dict["toc_entries"],
        "items": [_item_contract(item) for item in result.item_results],
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


def _item_contract(item) -> dict:
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
            link.innerHTML = `
              <span>Item ${{escapeHtml(item.item)}}</span>
              <small>${{escapeHtml(titles.get(item.item) || item.status)}}</small>
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
            const startSnippet = edgeSnippet(text, 'start');
            const endSnippet = edgeSnippet(text, 'end');
            article.innerHTML = `
              <header class="item-header">
                <div>
                  <h2>Item ${{escapeHtml(item.item)}}</h2>
                  <p class="muted">${{escapeHtml(item.status)}} | ${{escapeHtml(item.confidence_level)}} ${{Number(item.confidence_score).toFixed(2)}} | ${{(item.text || '').length.toLocaleString()}} chars</p>
                </div>
                <span class="pill ${{escapeHtml(item.confidence_level)}}">${{escapeHtml(item.confidence_level)}}</span>
              </header>
              <dl id="${{evidenceId}}" class="evidence-grid">
                <div><dt>Start</dt><dd>${{escapeHtml(item.start_evidence?.text || 'none')}}</dd></div>
                <div><dt>End</dt><dd>${{escapeHtml(item.end_evidence?.text || 'none')}}</dd></div>
                <div><dt>Warnings</dt><dd class="chip-row">${{warningLinks}}</dd></div>
                <div><dt>Actions</dt><dd class="chip-row">${{actionLinks}}</dd></div>
              </dl>
              <details class="snippet-details" open>
                <summary>Section snippets</summary>
                <div class="snippet-grid">
                  <pre></pre>
                  <pre></pre>
                </div>
              </details>
              <pre class="item-text"></pre>
            `;
            const snippets = article.querySelectorAll('.snippet-grid pre');
            snippets[0].textContent = startSnippet;
            snippets[1].textContent = endSnippet;
            article.querySelector('.item-text').textContent = item.text || '';
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
            row.innerHTML = `
              <div>
                <strong>Item ${{escapeHtml(item.item)}} | ${{escapeHtml(action.action_type)}}:${{escapeHtml(action.reason)}}</strong>
                <p>${{escapeHtml(action.description)}}</p>
                <small>${{escapeHtml(action.severity)}} | user input ${{action.requires_user_input ? 'yes' : 'no'}} | ${{escapeHtml(action.next_step || 'none')}}</small>
              </div>
              ${{selector}}
            `;
            container.appendChild(row);
          }}
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

        function edgeSnippet(text, mode) {{
          const value = String(text || '').replace(/\\s+/g, ' ').trim();
          if (value.length <= 520) return value;
          return mode === 'end' ? value.slice(-520) : value.slice(0, 520);
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
