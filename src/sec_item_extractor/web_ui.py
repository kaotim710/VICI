from __future__ import annotations

import argparse
import json
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .extractor import extract_items


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
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
    return {
        "filing": filings[filing_id],
        "elapsed_ms": elapsed_ms,
        "source_bytes": path.stat().st_size,
        "result": result.to_dict(),
    }


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
        if path.startswith("/api/filings/") and path.endswith("/extract"):
            filing_id = unquote(path.removeprefix("/api/filings/").removesuffix("/extract"))
            self._handle_extract(filing_id)
            return

        self._send_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return

    def _handle_extract(self, filing_id: str) -> None:
        try:
            self._send_json(extract_seed_filing(filing_id))
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)

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
            <button id="run-button" class="primary-button">Run extraction</button>
            <nav id="toc-list" class="toc-list" aria-label="Extracted item navigation"></nav>
          </aside>
          <section class="item-panel">
            <div id="status-banner" class="status-banner">Select Run extraction to parse this filing now.</div>
            <div id="items" class="items"></div>
          </section>
        </main>
        <script>
        const filingId = {safe_filing_id};
        const runButton = document.getElementById('run-button');
        const tocList = document.getElementById('toc-list');
        const items = document.getElementById('items');
        const statusBanner = document.getElementById('status-banner');
        const runMeta = document.getElementById('run-meta');

        runButton.addEventListener('click', runExtraction);

        async function runExtraction() {{
          runButton.disabled = true;
          statusBanner.textContent = 'Running extraction pipeline...';
          tocList.innerHTML = '';
          items.innerHTML = '<div class="loading">Parsing filing and reconstructing item boundaries...</div>';
          try {{
            const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/extract`, {{cache: 'no-store'}});
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.error || 'extract_failed');
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
          renderToc(result);
          renderItems(result.item_results);
        }}

        function renderToc(result) {{
          const titles = new Map((result.toc_entries || []).map(entry => [entry.item, entry.title || entry.text]));
          tocList.innerHTML = '';
          for (const item of result.item_results) {{
            const link = document.createElement('a');
            link.href = `#item-${{cssId(item.item)}}`;
            link.className = `toc-link ${{item.status}}`;
            link.innerHTML = `<span>Item ${{escapeHtml(item.item)}}</span><small>${{escapeHtml(titles.get(item.item) || item.status)}}</small>`;
            tocList.appendChild(link);
          }}
        }}

        function renderItems(itemResults) {{
          items.innerHTML = '';
          for (const item of itemResults) {{
            const article = document.createElement('article');
            article.className = 'item-card';
            article.id = `item-${{cssId(item.item)}}`;
            const warnings = item.warnings.length ? item.warnings.map(escapeHtml).join(' | ') : 'none';
            const actions = item.recommended_actions.length
              ? item.recommended_actions.map(action => `${{escapeHtml(action.action_type)}}:${{escapeHtml(action.reason)}}`).join(' | ')
              : 'none';
            article.innerHTML = `
              <header class="item-header">
                <div>
                  <h2>Item ${{escapeHtml(item.item)}}</h2>
                  <p class="muted">${{escapeHtml(item.status)}} | ${{escapeHtml(item.confidence_level)}} ${{Number(item.confidence_score).toFixed(2)}} | ${{(item.text || '').length.toLocaleString()}} chars</p>
                </div>
                <span class="pill ${{escapeHtml(item.confidence_level)}}">${{escapeHtml(item.confidence_level)}}</span>
              </header>
              <dl class="evidence-grid">
                <div><dt>Start</dt><dd>${{escapeHtml(item.start_evidence?.text || 'none')}}</dd></div>
                <div><dt>End</dt><dd>${{escapeHtml(item.end_evidence?.text || 'none')}}</dd></div>
                <div><dt>Warnings</dt><dd>${{warnings}}</dd></div>
                <div><dt>Actions</dt><dd>${{actions}}</dd></div>
              </dl>
              <pre class="item-text"></pre>
            `;
            article.querySelector('.item-text').textContent = item.text || '';
            items.appendChild(article);
          }}
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
.primary-button:disabled { opacity: 0.55; cursor: wait; }
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
.toc-panel .primary-button { margin: 16px 0; }
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
.toc-link.not_present { opacity: 0.55; }
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
@media (max-width: 820px) {
  .workspace-shell { grid-template-columns: 1fr; }
  .toc-panel { position: relative; height: auto; border-right: 0; border-bottom: 1px solid #d9dee5; }
  .evidence-grid { grid-template-columns: 1fr; }
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
