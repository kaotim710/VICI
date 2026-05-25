import sys
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
FRONTEND_APP = ROOT / "frontend" / "app.js"

from sec_item_extractor import web_ui
from sec_item_extractor.extractor import extract_items
from sec_item_extractor.sec_client import FilingDownload, FilingMetadata, TickerMetadata


class WebUiTests(unittest.TestCase):
    def test_filing_options_lists_seed_filings_without_extraction(self):
        with patch("sec_item_extractor.web_ui.extract_items") as extract_items:
            options = web_ui.filing_options()

        self.assertEqual(len(options), 20)
        self.assertTrue(all("filing_id" in option for option in options))
        extract_items.assert_not_called()

    def test_detail_page_does_not_embed_extracted_item_text(self):
        html = web_ui.render_detail("aapl_2023_10k")
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertIn('id="root"', html)
        self.assertIn("/assets/app.js", html)
        self.assertIn("Run extraction", app)
        self.assertIn("/api/filings/", app)
        self.assertNotIn("The Company designs", html)

    def test_detail_page_can_render_action_review_snippets(self):
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertIn("recommended_actions", app)
        self.assertIn("action-chip", app)
        self.assertIn("Run recovery actions", app)
        self.assertIn("Recovery results", app)

    def test_home_page_exposes_live_sec_intake_without_raw_cache_default(self):
        html = web_ui.render_home()
        app = FRONTEND_APP.read_text(encoding="utf-8")
        with patch.dict("os.environ", {}, clear=True):
            plan = web_ui.sec_intake_plan(ticker="AAPL", fiscal_year=2023)

        self.assertIn('id="root"', html)
        self.assertIn("Check SEC filing", app)
        self.assertIn("search-panel", app)
        self.assertIn("FilingStatusLight", app)
        self.assertIn("filing-status-light", app)
        self.assertIn("Filing found:", app)
        self.assertIn("upload your filing", app)
        self.assertIn("LoadingDots", app)
        self.assertIn("Open testing data", app)
        self.assertIn("/testing", app)
        self.assertIn("/api/sec/intake-plan", app)
        self.assertIn("/api/sec/extract", app)
        self.assertIn("Run live extraction", app)
        self.assertIn("/sec-live?", app)
        self.assertIn("h(\"select\"", app)
        self.assertIn("storedSearchDefaults", app)
        self.assertIn("vici:lastTicker", app)
        self.assertIn("vici:lastFiscalYear", app)
        self.assertIn("rememberSearch(ticker, year)", app)
        self.assertNotIn("setPlan(JSON.stringify", app)
        self.assertNotIn('<input name="year" value="2023"', app)
        self.assertEqual(plan["storage_policy"]["default_mode"], "direct_fetch_then_extract")

    def test_testing_page_exposes_smoke_and_seed_data(self):
        html = web_ui.render_testing()
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertIn("SEC 10-K Testing", html)
        self.assertIn("TestingPage", app)
        self.assertIn("Live smoke raw data", app)
        self.assertIn("Local seed filings", app)
        self.assertIn("/api/live-smoke", app)
        self.assertIn("/api/filings", app)

    def test_live_smoke_data_loads_latest_report_for_frontend_raw_data(self):
        payload = web_ui.live_smoke_data()

        self.assertTrue(payload["available"])
        self.assertIn("summary", payload)
        self.assertIn("filings", payload)
        self.assertEqual(payload["path"], "reports/live_sec_smoke_summary.json")

    def test_health_check_reports_deployment_readiness(self):
        with patch.dict("os.environ", {"SEC_USER_AGENT": "test contact@example.com"}):
            payload = web_ui.health_check()

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "sec-item-extractor")
        self.assertTrue(payload["live_sec_enabled"])

    def test_live_detail_page_auto_runs_sec_extraction_and_renders_items(self):
        html = web_ui.render_live_detail("xom", "2015")
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertIn("Live SEC Extraction", html)
        self.assertIn("/api/sec/extract", app)
        self.assertIn("LiveSecPage", app)
        self.assertIn('params.get("cik")', app)
        self.assertIn("Extracted TOC", app)
        self.assertIn("Raw extraction JSON", app)
        self.assertIn("Show original filing structure", app)
        self.assertIn("Back to testing", app)
        self.assertIn("ItemCard", app)
        self.assertIn("CompositeSegments", app)
        self.assertIn("Composite segments", app)

    def test_upload_page_accepts_filing_without_raw_cache_default(self):
        html = web_ui.render_upload_detail()
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertIn("Upload SEC Filing", html)
        self.assertIn("Run upload extraction", app)
        self.assertIn("type: \"file\"", app)
        self.assertIn("/api/uploads/extract", app)
        self.assertIn("/api/uploads/identify", app)
        self.assertIn("identifyOversizedUpload", app)
        self.assertIn("file.slice", app)
        self.assertIn("const identifier = ticker || cik", app)
        self.assertIn("Back to search", app)
        self.assertIn("No extraction has run yet.", app)
        self.assertIn("Show original filing structure", app)
        self.assertIn("SEC format", app)
        self.assertIn("SecFormatSummary", app)
        self.assertIn("Ticker ${payload.filing.ticker", app)
        self.assertNotIn('<input name="ticker"', html)
        self.assertNotIn('<input name="year"', html)
        self.assertNotIn('<input name="form"', html)

    def test_upload_page_explains_vercel_upload_limit_and_non_json_errors(self):
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertIn("VERCEL_UPLOAD_LIMIT_BYTES", app)
        self.assertIn("4.5 MB", app)
        self.assertIn("parseApiPayload", app)
        self.assertIn("non_json_response", app)
        self.assertIn("Large upload detected", app)
        self.assertIn("Uploaded filing metadata identified", web_ui.identify_uploaded_filing(
            b"""
            <html><body>
            <ix:nonNumeric name="dei:DocumentFiscalYearFocus">2025</ix:nonNumeric>
            <ix:nonNumeric name="dei:DocumentType">10-K</ix:nonNumeric>
            <ix:nonNumeric name="dei:TradingSymbol">TST</ix:nonNumeric>
            </body></html>
            """,
            filename="test.htm",
            original_size=9_000_000,
            partial_upload=True,
        )["message"])

    def test_upload_extract_runs_in_memory_and_includes_raw_preview(self):
        payload = web_ui.extract_uploaded_filing(
            b"""
            <html><body>
            <ix:nonNumeric name="dei:DocumentFiscalYearFocus">2024</ix:nonNumeric>
            <ix:nonNumeric name="dei:DocumentType">10-K</ix:nonNumeric>
            <ix:nonNumeric name="dei:TradingSymbol">TST</ix:nonNumeric>
            <ix:nonNumeric name="dei:EntityRegistrantName">Test Registrant Inc.</ix:nonNumeric>
            <h1>Item 1. Business</h1><p>Business text.</p>
            <h1>Item 1A. Risk Factors</h1><p>Risk text.</p>
            <h1>Item 2. Properties</h1><p>Property text.</p>
            </body></html>
            """,
            filename="../sample-10k.html",
        )

        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["pipeline"]["trigger"], "uploaded_filing_extract")
        self.assertFalse(payload["storage_policy"]["raw_storage_required"])
        self.assertEqual(payload["filing"]["primary_document"], "sample-10k.html")
        self.assertEqual(payload["filing"]["ticker"], "TST")
        self.assertEqual(payload["filing"]["fiscal_year"], 2024)
        self.assertEqual(payload["filing"]["form"], "10-K")
        self.assertEqual(payload["inferred_metadata"]["ticker_source"], "ixbrl_dei:TradingSymbol")
        self.assertEqual(payload["inferred_metadata"]["registrant_name"], "Test Registrant Inc.")
        self.assertTrue(payload["result"]["item_results"][0]["live_raw_section_available"])
        self.assertIn("srcdoc", payload["result"]["item_results"][0]["live_raw_section"])
        sec_format = payload["result"]["item_results"][0]["sec_item_format"]
        self.assertEqual(sec_format["sec_item_label"], "Item 1")
        self.assertEqual(sec_format["expected_title"], "Business")
        self.assertTrue(sec_format["label_matches"])
        self.assertTrue(sec_format["title_matches_expected"])
        self.assertEqual(sec_format["status"], "canonical_match")
        self.assertIn("sec_format_review_count", payload["summary"])

    def test_upload_identify_uses_sample_without_running_extraction(self):
        payload = web_ui.identify_uploaded_filing(
            b"""
            <html><body>
            <ix:nonNumeric name="dei:DocumentFiscalYearFocus">2025</ix:nonNumeric>
            <ix:nonNumeric name="dei:DocumentType">10-K</ix:nonNumeric>
            <ix:nonNumeric name="dei:TradingSymbol">INTC</ix:nonNumeric>
            <ix:nonNumeric name="dei:EntityRegistrantName">Intel Corporation</ix:nonNumeric>
            </body></html>
            """,
            filename="../intc.htm",
            original_size=7_500_000,
            partial_upload=True,
        )

        self.assertEqual(payload["status"], "ready")
        self.assertFalse(payload["pipeline"]["ran"])
        self.assertEqual(payload["pipeline"]["trigger"], "uploaded_filing_identify")
        self.assertEqual(payload["filing"]["ticker"], "INTC")
        self.assertEqual(payload["filing"]["fiscal_year"], 2025)
        self.assertEqual(payload["original_size"], 7_500_000)
        self.assertTrue(payload["partial_upload"])
        self.assertEqual(payload["next_action"]["type"], "live_sec_extract")
        self.assertEqual(payload["next_action"]["url"], "/sec-live?ticker=INTC&year=2025")

    def test_upload_identify_can_route_by_cik_when_ticker_is_missing(self):
        payload = web_ui.identify_uploaded_filing(
            b"""
            <html><body>
            <ix:nonNumeric name="dei:EntityCentralIndexKey">831001</ix:nonNumeric>
            <ix:nonNumeric name="dei:DocumentFiscalYearFocus">2025</ix:nonNumeric>
            <ix:nonNumeric name="dei:DocumentType">10-K</ix:nonNumeric>
            </body></html>
            """,
            filename="citi.htm",
            original_size=12_000_000,
            partial_upload=True,
        )

        self.assertEqual(payload["status"], "ready")
        self.assertIsNone(payload["filing"]["ticker"])
        self.assertEqual(payload["filing"]["cik"], "0000831001")
        self.assertEqual(payload["next_action"]["url"], "/sec-live?cik=0000831001&year=2025")

    def test_upload_identify_can_enrich_cik_from_sec_company_ticker_directory(self):
        class FakeSECClient:
            def __init__(self, user_agent):
                self.user_agent = user_agent

            def lookup_cik(self, cik):
                return TickerMetadata(ticker="C", title="Citigroup Inc.", cik="0000831001")

        payload = web_ui.identify_uploaded_filing(
            b"""
            <html><body>
            <ix:nonNumeric name="dei:EntityCentralIndexKey">831001</ix:nonNumeric>
            <ix:nonNumeric name="dei:DocumentFiscalYearFocus">2025</ix:nonNumeric>
            <ix:nonNumeric name="dei:DocumentType">10-K</ix:nonNumeric>
            </body></html>
            """,
            filename="citi.htm",
            original_size=12_000_000,
            partial_upload=True,
        )

        with patch.dict("os.environ", {"SEC_USER_AGENT": "test contact@example.com"}):
            with patch("sec_item_extractor.web_ui.SECClient", FakeSECClient):
                enriched = web_ui.enrich_identified_upload_from_sec_directory(payload)

        self.assertEqual(enriched["filing"]["ticker"], "C")
        self.assertEqual(enriched["filing"]["title"], "Citigroup Inc.")
        self.assertEqual(enriched["inferred_metadata"]["ticker_source"], "sec_company_tickers:cik")
        self.assertEqual(enriched["directory_lookup"]["status"], "matched")
        self.assertEqual(enriched["next_action"]["url"], "/sec-live?ticker=C&year=2025")

    def test_upload_metadata_falls_back_to_filename(self):
        payload = web_ui.extract_uploaded_filing(
            b"""
            <html><body>
            <h1>Item 1. Business</h1><p>Business text.</p>
            <h1>Item 1A. Risk Factors</h1><p>Risk text.</p>
            <h1>Item 2. Properties</h1><p>Property text.</p>
            </body></html>
            """,
            filename="aapl_2023_10k.html",
        )

        self.assertEqual(payload["filing"]["ticker"], "AAPL")
        self.assertEqual(payload["filing"]["fiscal_year"], 2023)
        self.assertEqual(payload["filing"]["form"], "10-K")
        self.assertEqual(payload["inferred_metadata"]["ticker_source"], "filename")

    def test_multipart_upload_parser_reads_fields_and_file(self):
        boundary = "----test-boundary"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="ticker"\r\n\r\n'
            "TST\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="filing"; filename="../sample.html"\r\n'
            "Content-Type: text/html\r\n\r\n"
            "<h1>Item 1. Business</h1>\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        fields, files = web_ui._parse_multipart_form(f"multipart/form-data; boundary={boundary}", body)

        self.assertEqual(fields["ticker"], "TST")
        self.assertEqual(files["filing"]["filename"], "sample.html")
        self.assertIn(b"Item 1", files["filing"]["content"])

    def test_sec_intake_plan_is_blocked_without_user_agent(self):
        with patch.dict("os.environ", {}, clear=True):
            payload = web_ui.sec_intake_plan(ticker="AAPL", fiscal_year=2023)

        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["storage_policy"]["raw_storage_required"])

    def test_live_sec_extract_downloads_and_extracts_without_raw_persistence(self):
        class FakeSECClient:
            def __init__(self, user_agent):
                self.user_agent = user_agent

            def lookup_ticker(self, ticker):
                return TickerMetadata(ticker="AAPL", title="Apple Inc.", cik="0000320193")

            def download_10k_for_year(self, cik, fiscal_year):
                body = b"""
                Item 1. Business
                Business text.
                Item 1A. Risk Factors
                Risk text.
                Item 2. Properties
                Property text.
                """
                return FilingDownload(
                    cik="0000320193",
                    fiscal_year=fiscal_year,
                    metadata=FilingMetadata(
                        accession_number="0000320193-23-000106",
                        form="10-K",
                        filing_date="2023-11-03",
                        report_date="2023-09-30",
                        primary_document="aapl-20230930.htm",
                    ),
                    archive_url="https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm",
                    body=body,
                )

        with patch.dict("os.environ", {"SEC_USER_AGENT": "test contact@example.com"}):
            with patch("sec_item_extractor.web_ui.SECClient", FakeSECClient):
                payload = web_ui.extract_sec_filing(ticker="AAPL", fiscal_year=2023)

        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["pipeline"]["trigger"], "live_sec_direct_fetch_extract")
        self.assertFalse(payload["storage_policy"]["raw_storage_required"])
        self.assertEqual(payload["filing"]["accession_number"], "0000320193-23-000106")
        self.assertFalse(payload["result"]["item_results"][0]["raw_section_available"])
        self.assertTrue(payload["result"]["item_results"][0]["live_raw_section_available"])
        self.assertIn("srcdoc", payload["result"]["item_results"][0]["live_raw_section"])
        sec_format = payload["result"]["item_results"][0]["sec_item_format"]
        self.assertEqual(sec_format["sec_item_label"], "Item 1")
        self.assertEqual(sec_format["expected_title"], "Business")
        self.assertEqual(sec_format["status"], "canonical_match")
        self.assertGreater(payload["summary"]["item_count"], 0)

    def test_live_sec_extract_resolves_ticker_when_query_uses_cik(self):
        class FakeSECClient:
            def __init__(self, user_agent):
                self.user_agent = user_agent

            def lookup_cik(self, cik):
                return TickerMetadata(ticker="C", title="Citigroup Inc.", cik="0000831001")

            def download_10k_for_year(self, cik, fiscal_year):
                body = b"""
                Item 1. Business
                Business text.
                Item 1A. Risk Factors
                Risk text.
                Item 2. Properties
                Property text.
                """
                return FilingDownload(
                    cik="0000831001",
                    fiscal_year=fiscal_year,
                    metadata=FilingMetadata(
                        accession_number="0000831001-25-000001",
                        form="10-K",
                        filing_date="2026-02-20",
                        report_date="2025-12-31",
                        primary_document="c-20251231.htm",
                    ),
                    archive_url="https://www.sec.gov/Archives/edgar/data/831001/000083100125000001/c-20251231.htm",
                    body=body,
                )

        with patch.dict("os.environ", {"SEC_USER_AGENT": "test contact@example.com"}):
            with patch("sec_item_extractor.web_ui.SECClient", FakeSECClient):
                payload = web_ui.extract_sec_filing(cik="831001", fiscal_year=2025)

        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["query"]["ticker"], "C")
        self.assertEqual(payload["filing"]["ticker"], "C")
        self.assertEqual(payload["filing"]["title"], "Citigroup Inc.")
        self.assertEqual(payload["filing"]["cik"], "0000831001")

    def test_detail_page_can_load_original_filing_structure(self):
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertIn("Show original filing structure", app)
        self.assertIn("Show extracted view", app)
        self.assertIn("extracted-view", app)
        self.assertIn("rawVisible", app)
        self.assertIn("raw-section-frame", app)
        self.assertIn("/raw-section/", app)
        self.assertIn("structure-tag", app)
        self.assertNotIn("Section snippets", app)

    def test_detail_page_limits_structure_panel_to_partitioned_items(self):
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertIn("raw_structure", app)
        self.assertIn("structure-tag", app)

    def test_detail_page_places_recovery_panel_after_items(self):
        app = FRONTEND_APP.read_text(encoding="utf-8")

        self.assertLess(app.index("ExtractionView"), app.index("RecoveryResults"))

    def test_raw_section_preview_preserves_tables_and_archive_base(self):
        payload = web_ui.raw_section_preview("wmt_2014_10k", "15")

        self.assertGreater(payload["table_count"], 0)
        self.assertIn("<table", payload["srcdoc"].lower())
        self.assertIn("<base href=\"https://www.sec.gov/Archives/edgar/data/", payload["srcdoc"])

    def test_extract_endpoint_runs_pipeline_on_demand(self):
        class Result:
            parser_version = "test"
            status = "success"
            candidate_count = 0
            toc_confidence = "none"
            toc_entries = []
            item_results = []

            def to_dict(self):
                return {"status": "success", "toc_entries": [], "item_results": []}

        with patch("sec_item_extractor.web_ui.extract_items", return_value=Result()) as extract_items:
            payload = web_ui.extract_seed_filing("aapl_2014_10k")

        extract_items.assert_called_once()
        self.assertEqual(payload["filing"]["filing_id"], "aapl_2014_10k")
        self.assertEqual(payload["pipeline"]["trigger"], "on_demand_extract_request")
        self.assertEqual(payload["summary"]["status"], "success")
        self.assertEqual(payload["result"]["status"], "success")
        self.assertGreater(payload["source_bytes"], 0)

    def test_extract_endpoint_tags_items_with_raw_tables_and_images(self):
        payload = web_ui.extract_seed_filing("wmt_2023_10k")
        by_item = {item["item"]: item for item in payload["result"]["item_results"]}

        self.assertGreater(by_item["5"]["raw_structure"]["table_count"], 0)
        self.assertGreater(by_item["5"]["raw_structure"]["image_count"], 0)

    def test_extract_endpoint_exposes_raw_outline_for_large_structured_items(self):
        payload = web_ui.extract_seed_filing("jpm_2023_10k")
        by_item = {item["item"]: item for item in payload["result"]["item_results"]}

        self.assertGreater(by_item["15"]["raw_structure"]["raw_bytes"], 250000)
        self.assertIsInstance(by_item["15"]["raw_structure"]["outline"], list)
        self.assertIsInstance(by_item["15"]["raw_structure"]["sections"], list)
        self.assertGreater(len(by_item["15"]["raw_structure"]["sections"]), 0)
        self.assertEqual(by_item["15"]["raw_structure"]["section_mode"], "internal_toc")
        self.assertIn("Three-Year Summary", by_item["15"]["raw_structure"]["sections"][0]["label"])
        self.assertIsNone(by_item["15"]["raw_structure"]["supplemental_chunk"])
        self.assertIn("supplemental-15", by_item)
        supplemental = by_item["supplemental-15"]
        self.assertEqual(supplemental["display_label"], "Supplemental after Item 15")
        self.assertTrue(supplemental["raw_section_available"])
        self.assertGreater(supplemental["raw_structure"]["table_count"], 0)
        self.assertGreater(supplemental["raw_structure"]["image_count"], 0)
        self.assertIn("Three-Year Summary", supplemental["raw_structure"]["sections"][0]["label"])
        self.assertNotIn("href", supplemental["raw_structure"]["sections"][0])

    def test_supplemental_partition_uses_page_number_toc_links(self):
        payload = web_ui.extract_seed_filing("xom_2023_10k")
        by_item = {item["item"]: item for item in payload["result"]["item_results"]}

        supplemental = by_item["supplemental-16"]
        labels = [section["label"] for section in supplemental["raw_structure"]["sections"]]
        self.assertGreaterEqual(len(labels), 20)
        self.assertEqual(labels[0], "Business Profile")
        self.assertIn("Financial Information", labels)
        self.assertIn("Business Results", labels)
        self.assertGreater(supplemental["raw_structure"]["sections"][0]["table_count"], 0)
        self.assertIn("raw_start", supplemental["raw_structure"]["sections"][0])
        self.assertIn("raw_end", supplemental["raw_structure"]["sections"][0])

    def test_supplemental_raw_section_preview_preserves_own_raw_structure(self):
        payload = web_ui.raw_section_preview("jpm_2023_10k", "supplemental-15")

        self.assertGreater(payload["table_count"], 0)
        self.assertGreater(payload["image_count"], 0)
        self.assertIn("Table of contents", payload["srcdoc"])
        self.assertIn("Three-Year Summary", payload["srcdoc"])

    def test_supplemental_raw_section_preview_can_scope_to_subsection(self):
        whole = web_ui.raw_section_preview("xom_2023_10k", "supplemental-16")
        subsection = web_ui.raw_section_preview("xom_2023_10k", "supplemental-16:0")

        self.assertEqual(subsection["section_label"], "Business Profile")
        self.assertGreater(subsection["table_count"], 0)
        self.assertGreater(subsection["raw_bytes"], 1000)
        self.assertLess(subsection["raw_bytes"], whole["raw_bytes"])
        self.assertIn("<table", subsection["srcdoc"].lower())

    def test_internal_toc_items_render_partitioned_sections(self):
        cases = [
            ("bac_2023_10k", "8", "Consolidated Statement of Income"),
            ("bac_2014_10k", "8", "Consolidated Statement of Income"),
            ("unh_2014_10k", "8", "Report of Independent Registered Public Accounting Firm"),
            ("unh_2023_10k", "8", "Report of Independent Registered Public Accounting Firm"),
            ("jnj_2023_10k", "8", "Consolidated"),
            ("jpm_2023_10k", "15", "Three-Year Summary"),
            ("xom_2014_10k", "15", "Financial Summary"),
            ("cvx_2023_10k", "14", "Key Financial Results"),
        ]

        for filing_id, item_name, expected_label in cases:
            with self.subTest(filing_id=filing_id, item=item_name):
                payload = web_ui.extract_seed_filing(filing_id)
                item = {row["item"]: row for row in payload["result"]["item_results"]}[item_name]
                labels = [section["label"] for section in item["raw_structure"]["sections"]]
                self.assertEqual(item["raw_structure"]["section_mode"], "internal_toc")
                self.assertTrue(any(expected_label in label for label in labels))
                self.assertGreaterEqual(len(labels), 3)

    def test_internal_toc_subsection_raw_preview_is_scoped(self):
        payload = web_ui.raw_section_preview("bac_2023_10k", "8:0")

        self.assertEqual(payload["section_label"], "Consolidated Statement of Income")
        self.assertGreater(payload["table_count"], 0)
        self.assertIn("<table", payload["srcdoc"].lower())

    def test_known_front_toc_false_positives_use_body_headings(self):
        cases = [
            ("jpm_2023_10k", "6", "Item 6. Reserved"),
            ("unh_2014_10k", "2", "ITEM 2."),
            ("unh_2014_10k", "7", "ITEM 7."),
            ("unh_2014_10k", "13", "ITEM 13."),
            ("unh_2014_10k", "14", "ITEM 14."),
            ("amzn_2023_10k", "2", "Item 2."),
            ("amzn_2023_10k", "3", "Item 3."),
            ("amzn_2023_10k", "16", "Item 16."),
        ]

        for filing_id, item_name, expected_start in cases:
            with self.subTest(filing_id=filing_id, item=item_name):
                payload = web_ui.extract_seed_filing(filing_id)
                item = {row["item"]: row for row in payload["result"]["item_results"]}[item_name]
                self.assertTrue(item["text"].startswith(expected_start))
                self.assertNotIn("Start heading has TOC-like signals.", item["warnings"])

    def test_supplemental_partitioning_runs_across_seed_filings(self):
        expected = {
            "jpm_2014_10k": ["supplemental-15"],
            "jpm_2023_10k": ["supplemental-15"],
            "xom_2014_10k": ["supplemental-15"],
            "xom_2023_10k": ["supplemental-16"],
            "cvx_2014_10k": ["supplemental-15"],
        }
        observed = {}
        manifest = json.loads((ROOT / "fixtures" / "gold" / "seed_filings.json").read_text(encoding="utf-8"))

        for filing in manifest["filings"]:
            filing_id = filing["filing_id"]
            content = (ROOT / "fixtures" / "filings" / "raw" / f"{filing_id}.html").read_text(
                encoding="utf-8", errors="replace"
            )
            result = extract_items(content, target_items=["15", "16"], filing_id=filing_id)
            result_dict = result.to_dict()
            web_ui._attach_raw_structure(result_dict, content, result.item_results)
            web_ui._append_supplemental_items(result_dict)
            supplemental_items = [item["item"] for item in result_dict["item_results"] if item["item"].startswith("supplemental-")]
            if supplemental_items:
                observed[filing_id] = supplemental_items
                for item in supplemental_items:
                    item_payload = next(result_item for result_item in result_dict["item_results"] if result_item["item"] == item)
                    self.assertGreater(len(item_payload["raw_structure"]["sections"]), 0)
                    preview = web_ui.raw_section_preview(filing_id, item)
                    self.assertGreater(preview["raw_bytes"], 1000)
                    self.assertGreater(preview["table_count"] + preview["image_count"], 0)
                    self.assertIn("table of contents", preview["srcdoc"].lower())
                    self.assertNotIn("Item 1. Business", preview["srcdoc"][:20000])

        self.assertEqual(observed, expected)

    def test_jpm_item_fifteen_raw_section_starts_at_actual_section(self):
        payload = web_ui.extract_seed_filing("jpm_2023_10k")
        by_item = {item["item"]: item for item in payload["result"]["item_results"]}

        self.assertIn("Exhibit 3.1", by_item["15"]["text"])
        self.assertNotIn("Item 1. Business", by_item["15"]["text"][:1000])

    def test_raw_metadata_does_not_run_extraction(self):
        with patch("sec_item_extractor.web_ui.extract_items") as extract_items:
            payload = web_ui.raw_filing_metadata("aapl_2014_10k")

        extract_items.assert_not_called()
        self.assertEqual(payload["filing"]["filing_id"], "aapl_2014_10k")
        self.assertEqual(payload["cache_policy"], "no-store")
        self.assertTrue(payload["raw"]["sha256"])

    def test_recover_endpoint_runs_pipeline_and_recovery_on_demand(self):
        extraction = SimpleNamespace(
            parser_version="test",
            status="warning",
            item_results=[],
        )
        recovery = SimpleNamespace(to_dict=lambda: {"item": "7", "status": "needs_review"})

        with patch("sec_item_extractor.web_ui.extract_items", return_value=extraction) as extract_items:
            with patch("sec_item_extractor.web_ui.run_recovery_actions", return_value=[recovery]) as run_recovery:
                payload = web_ui.recover_seed_filing(
                    "aapl_2014_10k", selections={("aapl_2014_10k", "7"): "Management"}
                )

        extract_items.assert_called_once()
        run_recovery.assert_called_once()
        self.assertEqual(payload["pipeline"]["trigger"], "on_demand_recovery_request")
        self.assertEqual(payload["summary"]["recovery_actions"], 1)
        self.assertEqual(payload["recoveries"][0]["status"], "needs_review")


if __name__ == "__main__":
    unittest.main()
