(function () {
  const h = React.createElement;
  const { useEffect, useMemo, useState } = React;
  const VERCEL_UPLOAD_LIMIT_BYTES = 4.5 * 1024 * 1024;
  const LOCAL_UPLOAD_LIMIT_BYTES = 25 * 1024 * 1024;

  function apiJson(url, options) {
    return fetch(url, { cache: "no-store", ...(options || {}) }).then(async (response) => {
      const payload = await parseApiPayload(response);
      if (!response.ok) {
        throw new Error(payload.message || payload.error || payload.raw || "request_failed");
      }
      return payload;
    });
  }

  async function parseApiPayload(response) {
    const contentType = response.headers.get("content-type") || "";
    const raw = await response.text();
    if (!raw) return {};
    if (contentType.includes("application/json")) {
      try {
        return JSON.parse(raw);
      } catch (error) {
        return { error: "invalid_json", message: `Invalid JSON response: ${error.message}`, raw: raw.slice(0, 240) };
      }
    }
    return {
      error: response.status === 413 ? "upload_too_large" : "non_json_response",
      message: response.status === 413
        ? "Upload is too large for this deployment. Vercel Functions accept request bodies up to 4.5 MB."
        : raw.slice(0, 240),
      raw: raw.slice(0, 240),
    };
  }

  function uploadLimitBytes() {
    return window.location.hostname.endsWith(".vercel.app") ? VERCEL_UPLOAD_LIMIT_BYTES : LOCAL_UPLOAD_LIMIT_BYTES;
  }

  function formatBytes(bytes) {
    if (!Number.isFinite(bytes)) return "unknown size";
    const units = ["bytes", "KB", "MB", "GB"];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex += 1;
    }
    return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
  }

  function uploadLimitMessage(file) {
    const limit = uploadLimitBytes();
    if (!file || file.size <= limit) return "";
    return `${file.name} is ${formatBytes(file.size)}, which exceeds this deployment's ${formatBytes(limit)} upload limit. Use live SEC ticker/year extraction for large public filings, or run the Docker/local server for large file uploads.`;
  }

  function cssId(value) {
    return String(value || "").replace(/[^a-zA-Z0-9_-]/g, "-");
  }

  function yearOptions() {
    const current = new Date().getFullYear();
    const years = [];
    for (let year = current; year >= 1994; year -= 1) years.push(year);
    return years;
  }

  function App() {
    const path = window.location.pathname;
    if (path === "/testing") return h(TestingPage);
    if (path === "/upload") return h(UploadPage);
    if (path === "/sec-live") return h(LiveSecPage);
    if (path.startsWith("/filings/")) {
      return h(SeedFilingPage, { filingId: decodeURIComponent(path.replace("/filings/", "")) });
    }
    return h(HomePage);
  }

  function HomePage() {
    const [ticker, setTicker] = useState("AAPL");
    const [year, setYear] = useState("2023");
    const [filingStatus, setFilingStatus] = useState(null);
    const [busy, setBusy] = useState(false);

    async function checkPlan(event) {
      event.preventDefault();
      setBusy(true);
      setFilingStatus({ state: "checking", message: "Checking SEC filing availability..." });
      try {
        const params = new URLSearchParams({ ticker, year });
        const payload = await apiJson(`/api/sec/intake-plan?${params.toString()}`);
        const filing = payload.filing || {};
        setFilingStatus({
          state: payload.status === "ready" ? "ready" : "error",
          message: payload.status === "ready"
            ? `Filing found: ${filing.accession_number || ticker} (${filing.primary_document || "10-K"})`
            : payload.message || "Filing was not found.",
        });
      } catch (error) {
        setFilingStatus({ state: "error", message: error.message });
      } finally {
        setBusy(false);
      }
    }

    function runLiveExtraction(event) {
      event.preventDefault();
      const params = new URLSearchParams({ ticker, year });
      window.location.href = `/sec-live?${params.toString()}`;
    }

    return h("main", { className: "home-shell" },
      h("section", { className: "hero-panel" },
        h("div", null,
          h("p", { className: "eyebrow" }, "SEC 10-K item extraction"),
          h("h1", null, "Inspectable filing intake"),
          h("p", { className: "hero-copy" }, "Run deterministic section extraction from SEC ticker/year or an uploaded filing.")
        )
      ),
      h("section", { className: "search-section" },
        h("form", { className: "search-panel", onSubmit: runLiveExtraction },
          h("div", { className: "search-fields" },
            h("label", null, "Ticker", h("input", { value: ticker, onChange: (event) => setTicker(event.target.value.toUpperCase()), autoComplete: "off" })),
            h("label", null, "Fiscal year", h("select", { value: year, onChange: (event) => setYear(event.target.value) },
              yearOptions().map((option) => h("option", { key: option, value: String(option) }, option))
            ))
          ),
          h("div", { className: "search-actions" },
            h("button", { className: "secondary-button", type: "button", disabled: busy, onClick: checkPlan }, busy ? h(LoadingDots, { label: "Checking" }) : "Check SEC filing"),
            h("button", { className: "primary-button", type: "submit" }, "Run live extraction")
          )
        ),
        filingStatus ? h(FilingStatusLight, { status: filingStatus }) : null,
        h("div", { className: "upload-prompt" },
          h("span", null, "or"),
          h("a", { className: "upload-link", href: "/upload" }, "upload your filing")
        ),
        h("a", { className: "testing-link", href: "/testing" }, "Open testing data")
      )
    );
  }

  function FilingStatusLight({ status }) {
    const state = status.state || "error";
    return h("div", { className: `filing-status ${state}`, role: "status" },
      h("span", { className: "filing-status-light", "aria-hidden": "true" }),
      h("span", null, status.message || "No filing check has run.")
    );
  }

  function TestingPage() {
    const [filings, setFilings] = useState([]);
    const [filingError, setFilingError] = useState("");
    const [smoke, setSmoke] = useState(null);
    const [smokeError, setSmokeError] = useState("");

    useEffect(() => {
      loadFilings();
      apiJson("/api/live-smoke").then(setSmoke).catch((error) => setSmokeError(error.message));
    }, []);

    function loadFilings() {
      setFilingError("");
      apiJson("/api/filings")
        .then((payload) => setFilings(payload.filings || []))
        .catch((error) => setFilingError(error.message));
    }

    return h("main", { className: "home-shell testing-shell" },
      h("a", { className: "back-link", href: "/" }, "Back to search"),
      h("section", { className: "testing-header" },
        h("p", { className: "eyebrow" }, "Testing"),
        h("h1", null, "Validation raw data"),
        h("p", { className: "hero-copy" }, "Review live smoke output and local seed filings without running extraction until a filing is selected.")
      ),
      h("section", { className: "apple-card" },
        h("div", { className: "card-heading" },
          h("h2", null, "Live smoke raw data"),
          h("p", null, "Latest direct-fetch smoke report.")
        ),
        smokeError ? h("p", { className: "error-text" }, smokeError) : h(SmokeSummary, { smoke })
      ),
      h("section", { className: "apple-card" },
        h("div", { className: "list-heading" },
          h("div", null, h("h2", null, "Local seed filings"), h("p", null, "Extraction runs only after you open a filing.")),
          h("button", { className: "icon-button", onClick: loadFilings, title: "Refresh filing list" }, "R")
        ),
        filingError ? h("p", { className: "error-text" }, filingError) : h("div", { className: "filing-grid" },
          filings.length ? filings.map((filing) => h("a", { className: "filing-card", href: `/filings/${encodeURIComponent(filing.filing_id)}`, key: filing.filing_id },
            h("strong", null, filing.ticker),
            h("span", null, `${filing.industry} | ${filing.fiscal_year} | ${filing.form}`),
            h("em", { className: filing.available ? "ok" : "warn" }, filing.available ? "available" : "missing raw filing")
          )) : h(LoadingCard, { label: "Loading filings" })
        )
      )
    );
  }

  function LoadingDots({ label }) {
    return h("span", { className: "loading-dots", "aria-label": label || "Loading" },
      label ? h("span", null, label) : null,
      h("i", null),
      h("i", null),
      h("i", null)
    );
  }

  function LoadingCard({ label }) {
    return h("div", { className: "loading-card" }, h(LoadingDots, { label }));
  }

  function isLoadingText(text) {
    return /loading|fetching|running|uploading|parsing|resolving/i.test(String(text || ""));
  }

  function SmokeSummary({ smoke }) {
    if (!smoke) return h(LoadingCard, { label: "Loading live smoke report" });
    if (!smoke.available) return h("p", { className: "muted" }, "No live smoke report has been generated yet.");
    const summary = smoke.summary || {};
    const filings = smoke.filings || [];
    return h(React.Fragment, null,
      h("div", { className: "metric-row" },
        h("span", null, `${summary.filings_tested || 0} filings`),
        h("span", null, `${summary.warning_total || 0} warnings`),
        h("span", null, `${summary.failed_total || 0} failed`),
        h("span", null, `${summary.recommended_action_total || 0} actions`)
      ),
      h("div", { className: "smoke-grid" },
        filings.map((filing) => h("a", { key: `${filing.ticker}-${filing.year}`, href: `/sec-live?ticker=${encodeURIComponent(filing.ticker)}&year=${encodeURIComponent(filing.year)}` },
          h("strong", null, `${filing.ticker} ${filing.year}`),
          h("span", null, `${filing.filing_status} | warnings ${filing.warning_count} | actions ${filing.recommended_action_count}`)
        ))
      ),
      h("details", { className: "json-details" }, h("summary", null, "Raw JSON"), h("pre", null, JSON.stringify(smoke, null, 2)))
    );
  }

  function UploadPage() {
    const [payload, setPayload] = useState(null);
    const [status, setStatus] = useState("Choose a filing file to parse.");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);
    const [fileWarning, setFileWarning] = useState("");

    async function submitUpload(event) {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const selectedFile = form.get("filing");
      const limitWarning = uploadLimitMessage(selectedFile);
      if (limitWarning) {
        setError(limitWarning);
        setFileWarning(limitWarning);
        setPayload(null);
        setStatus(`Upload extraction blocked: ${limitWarning}`);
        return;
      }
      setBusy(true);
      setError("");
      setFileWarning("");
      setPayload(null);
      setStatus("Uploading filing and running extraction...");
      try {
        const result = await apiJson("/api/uploads/extract", { method: "POST", body: form });
        setPayload(result);
        setStatus(`${result.summary.status} | ${result.summary.item_count} items | TOC ${result.summary.toc_confidence} | warnings ${result.summary.warning_count}`);
      } catch (uploadError) {
        setError(uploadError.message);
        setStatus(`Upload extraction failed: ${uploadError.message}`);
      } finally {
        setBusy(false);
      }
    }

    const sidebar = h("form", { className: "upload-form", onSubmit: submitUpload },
      h("label", null, "Filing file", h("input", {
        name: "filing",
        type: "file",
        accept: ".html,.htm,.txt,text/html,text/plain",
        required: true,
        onChange: (event) => setFileWarning(uploadLimitMessage(event.target.files && event.target.files[0])),
      })),
      h("p", { className: fileWarning ? "error-text" : "muted" }, fileWarning || `Upload limit on this deployment: ${formatBytes(uploadLimitBytes())}`),
      h("button", { className: "primary-button", type: "submit", disabled: busy }, busy ? h(LoadingDots, { label: "Parsing" }) : "Run upload extraction")
    );

    return h(WorkspaceShell, {
      title: payload ? `${payload.filing.ticker || "Unknown"} ${payload.filing.fiscal_year || ""}`.trim() : "Upload filing",
      subtitle: payload ? `${payload.filing.form || "Unknown form"} | ${payload.filing.primary_document}` : "Upload HTML/TXT and extract in memory.",
      backHref: "/",
      backLabel: "Back to search",
      sidebarControls: sidebar,
      result: payload ? payload.result : null,
    }, h(StatusBanner, { text: status, error: !!error }),
      error ? h("p", { className: "error-text" }, error) : null,
      payload ? h(UploadMetadata, { payload }) : null,
      payload ? h(ExtractionView, { payload, source: "upload" }) : null
    );
  }

  function UploadMetadata({ payload }) {
    const metadata = payload.inferred_metadata || {};
    return h("section", { className: "metadata-strip" },
      h("span", null, payload.filing.primary_document),
      h("span", null, `Ticker ${payload.filing.ticker || "unknown"} (${metadata.ticker_source || "not_found"})`),
      h("span", null, `Fiscal year ${payload.filing.fiscal_year || "unknown"} (${metadata.fiscal_year_source || "not_found"})`),
      h("span", null, `Form ${payload.filing.form || "unknown"} (${metadata.form_source || "not_found"})`),
      h("span", null, `Registrant ${metadata.registrant_name || "unknown"}`),
      h("span", null, payload.source_sha256 ? payload.source_sha256.slice(0, 12) : "no hash")
    );
  }

  function LiveSecPage() {
    const [payload, setPayload] = useState(null);
    const [status, setStatus] = useState("Fetching SEC filing and running extraction...");
    const [error, setError] = useState("");
    const params = useMemo(() => new URLSearchParams(window.location.search), []);
    const ticker = params.get("ticker") || "";
    const year = params.get("year") || "";

    useEffect(() => {
      const query = new URLSearchParams({ ticker, year });
      apiJson(`/api/sec/extract?${query.toString()}`)
        .then((result) => {
          setPayload(result);
          setStatus(`${result.summary.status} | ${result.summary.item_count} items | TOC ${result.summary.toc_confidence} | warnings ${result.summary.warning_count}`);
        })
        .catch((loadError) => {
          setError(loadError.message);
          setStatus(`Live extraction failed: ${loadError.message}`);
        });
    }, [ticker, year]);

    return h(WorkspaceShell, {
      title: payload ? `${payload.filing.ticker} ${payload.filing.fiscal_year}` : `${ticker} ${year}`.trim() || "Live SEC filing",
      subtitle: payload ? `${payload.filing.form} | ${payload.filing.accession_number} | ${Number(payload.source_bytes || 0).toLocaleString()} bytes | ${payload.elapsed_ms} ms` : "Direct SEC fetch, no raw persistence.",
      backHref: "/",
      backLabel: "Back to search",
      result: payload ? payload.result : null,
    }, h(StatusBanner, { text: status, error: !!error }),
      error ? h("p", { className: "error-text" }, error) : null,
      payload ? h("section", { className: "metadata-strip" },
        h("span", null, payload.filing.title || payload.filing.ticker),
        h("span", null, `CIK ${payload.filing.cik}`),
        h("span", null, `Report ${payload.filing.report_date}`),
        payload.filing.download_url ? h("a", { href: payload.filing.download_url, target: "_blank", rel: "noreferrer" }, "SEC source") : null
      ) : null,
      payload ? h(ExtractionView, { payload, source: "live" }) : null
    );
  }

  function SeedFilingPage({ filingId }) {
    const [metadata, setMetadata] = useState(null);
    const [payload, setPayload] = useState(null);
    const [recoveries, setRecoveries] = useState(null);
    const [status, setStatus] = useState("Select Run extraction to parse this filing now.");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    useEffect(() => {
      apiJson(`/api/filings/${encodeURIComponent(filingId)}/raw-metadata`).then(setMetadata).catch(() => null);
    }, [filingId]);

    async function runExtraction() {
      setBusy(true);
      setError("");
      setRecoveries(null);
      setStatus("Running extraction pipeline...");
      try {
        const result = await apiJson(`/api/filings/${encodeURIComponent(filingId)}/extract`);
        setPayload(result);
        setStatus(`${result.summary.status} | ${result.result.item_results.length} items | TOC ${result.summary.toc_confidence}`);
      } catch (loadError) {
        setError(loadError.message);
        setStatus(`Extraction failed: ${loadError.message}`);
      } finally {
        setBusy(false);
      }
    }

    async function runRecovery() {
      if (!payload) return;
      setStatus("Running deterministic recovery actions...");
      try {
        const result = await apiJson(`/api/filings/${encodeURIComponent(filingId)}/recover`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ selections: {} }),
        });
        setRecoveries(result.recoveries || []);
        setStatus(`Recovery complete | ${result.summary.recovery_actions} actions | ${result.elapsed_ms} ms`);
      } catch (recoveryError) {
        setStatus(`Recovery failed: ${recoveryError.message}`);
      }
    }

    const hasActions = !!payload && (payload.result.item_results || []).some((item) => (item.recommended_actions || []).length);
    const controls = h("div", { className: "sidebar-actions" },
      h("button", { className: "primary-button", onClick: runExtraction, disabled: busy }, busy ? h(LoadingDots, { label: "Running" }) : "Run extraction"),
      h("button", { className: "secondary-button", onClick: runRecovery, disabled: !hasActions }, "Run recovery actions")
    );

    return h(WorkspaceShell, {
      title: payload ? `${payload.filing.ticker} ${payload.filing.fiscal_year}` : filingId,
      subtitle: payload ? `${payload.filing.industry} | ${payload.filing.form} | ${Number(payload.source_bytes || 0).toLocaleString()} bytes | ${payload.elapsed_ms} ms` : "Pipeline has not run yet.",
      backHref: "/testing",
      backLabel: "Back to testing",
      sidebarControls: controls,
      result: payload ? payload.result : null,
    }, h(StatusBanner, { text: status, error: !!error }),
      error ? h("p", { className: "error-text" }, error) : null,
      metadata ? h("section", { className: "metadata-strip" },
        h("span", null, metadata.raw.path),
        h("span", null, `${Number(metadata.raw.bytes).toLocaleString()} bytes`),
        h("span", null, `sha256 ${metadata.raw.sha256.slice(0, 12)}`)
      ) : null,
      payload ? h(ExtractionView, { payload, source: "seed", filingId }) : null,
      recoveries ? h(RecoveryResults, { recoveries }) : null
    );
  }

  function WorkspaceShell({ title, subtitle, backHref, backLabel, sidebarControls, result, children }) {
    const items = result ? result.item_results || [] : [];
    return h("main", { className: "workspace-shell" },
      h("aside", { className: "toc-panel" },
        h("a", { className: "back-link", href: backHref || "/" }, backLabel || "Back to search"),
        h("h1", null, title),
        h("p", { className: "muted" }, subtitle),
        sidebarControls,
        h("h2", { className: "toc-heading" }, "Extracted TOC"),
        items.length ? h("nav", { className: "toc-list", "aria-label": "Extracted item navigation" },
          items.map((item) => h("a", { key: item.item, className: `toc-link ${item.status} ${item.confidence_level}`, href: `#item-${cssId(item.item)}` },
            h("span", null, item.display_label || `Item ${item.item}`),
            h("small", null, item.title || item.status),
            h("em", null, `${item.status} | ${item.confidence_level} ${Number(item.confidence_score || 0).toFixed(2)}`)
          ))
        ) : h("p", { className: "empty-toc" }, "No extraction has run yet.")
      ),
      h("section", { className: "item-panel" }, children)
    );
  }

  function StatusBanner({ text, error }) {
    return h("div", { className: `status-banner ${error ? "error" : ""}` },
      isLoadingText(text) ? h(LoadingDots, { label: text }) : text
    );
  }

  function ExtractionView({ payload, source, filingId }) {
    const items = payload.result ? payload.result.item_results || [] : [];
    return h(React.Fragment, null,
      h("div", { className: "items" }, items.map((item) => h(ItemCard, { key: item.item, item, source, filingId }))),
      h("details", { className: "json-details" },
        h("summary", null, source === "upload" ? "Upload extraction raw data" : "Raw extraction JSON"),
        h("pre", null, JSON.stringify(payload, null, 2))
      )
    );
  }

  function ItemCard({ item, source, filingId }) {
    const [rawVisible, setRawVisible] = useState(false);
    const [rawPayload, setRawPayload] = useState(item.live_raw_section || null);
    const [rawError, setRawError] = useState("");
    const warnings = item.warnings || [];
    const actions = item.recommended_actions || [];
    const rawStructure = item.raw_structure || {};
    const secFormat = item.sec_item_format || null;
    const rawAvailable = !!item.live_raw_section_available || (source === "seed" && item.raw_section_available !== false);

    async function toggleRaw() {
      if (rawVisible) {
        setRawVisible(false);
        return;
      }
      setRawVisible(true);
      if (rawPayload || source !== "seed") return;
      try {
        const payload = await apiJson(`/api/filings/${encodeURIComponent(filingId)}/raw-section/${encodeURIComponent(item.item)}`);
        setRawPayload(payload);
      } catch (error) {
        setRawError(error.message);
      }
    }

    return h("article", { id: `item-${cssId(item.item)}`, className: "item-card" },
      h("header", { className: "item-header" },
        h("div", null,
          h("h2", null, item.display_label || `Item ${item.item}`),
          h("p", { className: "muted" }, `${item.status} | ${item.confidence_level} ${Number(item.confidence_score || 0).toFixed(2)} | ${String(item.text || "").length.toLocaleString()} chars`)
        ),
        h("div", { className: "item-badges" },
          Number(rawStructure.table_count || 0) ? h("span", { className: "structure-tag table" }, `tables ${rawStructure.table_count}`) : null,
          Number(rawStructure.image_count || 0) ? h("span", { className: "structure-tag image" }, `images ${rawStructure.image_count}`) : null,
          h("span", { className: `pill ${item.confidence_level}` }, item.confidence_level)
        )
      ),
      !rawVisible ? h("div", { className: "extracted-view" },
        h("dl", { className: "evidence-grid" },
          h("div", null, h("dt", null, "SEC format"), h("dd", { className: "chip-row" }, h(SecFormatSummary, { format: secFormat }))),
          h("div", null, h("dt", null, "Start"), h("dd", null, item.start_evidence ? item.start_evidence.text : "none")),
          h("div", null, h("dt", null, "End"), h("dd", null, item.end_evidence ? item.end_evidence.text : "none")),
          h("div", null, h("dt", null, "Warnings"), h("dd", { className: "chip-row" }, warnings.length ? warnings.map((warning) => h("span", { className: "warning-chip", key: warning }, warning)) : h("span", { className: "empty-chip" }, "none"))),
          h("div", null, h("dt", null, "Actions"), h("dd", { className: "chip-row" }, actions.length ? actions.map((action, index) => h("span", { className: `action-chip ${action.severity}`, key: index }, `${action.action_type}:${action.reason}`)) : h("span", { className: "empty-chip" }, "none")))
        ),
        h("pre", { className: "item-text" }, item.text || "")
      ) : h(RawPreview, { rawPayload, rawError }),
      rawAvailable ? h("div", { className: "raw-section-tools" },
        h("button", { className: "secondary-button compact", onClick: toggleRaw }, rawVisible ? "Show extracted view" : "Show original filing structure"),
        rawVisible && rawPayload ? h("span", { className: "raw-section-meta" }, `${rawPayload.table_count || 0} tables | ${rawPayload.image_count || 0} images | ${Number(rawPayload.raw_bytes || 0).toLocaleString()} bytes`) : null
      ) : null
    );
  }

  function SecFormatSummary({ format }) {
    if (!format) return h("span", { className: "empty-chip" }, "not checked");
    const label = format.sec_item_label || format.item || "unknown item";
    const title = format.expected_title || "virtual partition";
    const heading = format.start_heading || format.heading_context || "no extracted heading";
    return h(React.Fragment, null,
      h("span", { className: `format-chip ${format.status || "unknown"}` }, format.status || "unknown"),
      h("span", { className: "empty-chip" }, `${label} | ${title}`),
      h("span", { className: "empty-chip" }, heading)
    );
  }

  function RawPreview({ rawPayload, rawError }) {
    if (rawError) return h("p", { className: "error-text" }, `Original view failed: ${rawError}`);
    if (!rawPayload) return h(LoadingCard, { label: "Loading original HTML" });
    return h("div", { className: "raw-section-preview" },
      h("iframe", { className: "raw-section-frame", sandbox: "", srcDoc: rawPayload.srcdoc || "<!doctype html><p>Original section unavailable.</p>" })
    );
  }

  function RecoveryResults({ recoveries }) {
    return h("section", { className: "recovery-panel" },
      h("h2", null, "Recovery results"),
      recoveries.map((recovery, index) => h("article", { className: "recovery-result", key: index },
        h("h3", null, `Item ${recovery.item} | ${recovery.reason}`),
        h("p", null, `${recovery.status} | ${recovery.severity} | ${recovery.next_step || "none"}`),
        h("p", null, recovery.message || ""),
        recovery.extracted_text ? h("pre", null, recovery.extracted_text.slice(0, 1200)) : null
      ))
    );
  }

  ReactDOM.createRoot(document.getElementById("root")).render(h(App));
})();
