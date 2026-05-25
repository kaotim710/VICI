import unittest

from sec_item_extractor.sec_client import (
    SEC_COMPANY_TICKERS_URL,
    SECClient,
    FilingMetadata,
    archive_url,
    company_facts_url,
    format_cik,
    full_text_search_url,
    submissions_url,
)


class SECClientTests(unittest.TestCase):
    def test_formats_cik_for_data_sec_urls(self):
        self.assertEqual(format_cik("320193"), "0000320193")
        self.assertEqual(submissions_url("320193"), "https://data.sec.gov/submissions/CIK0000320193.json")
        self.assertEqual(
            company_facts_url("320193"),
            "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
        )

    def test_builds_archive_url_without_accession_dashes(self):
        self.assertEqual(
            archive_url("0000320193", "0000320193-23-000106", "aapl-20230930.htm"),
            "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm",
        )

    def test_builds_full_text_search_url(self):
        self.assertEqual(SEC_COMPANY_TICKERS_URL, "https://www.sec.gov/files/company_tickers.json")
        self.assertEqual(
            full_text_search_url("AAPL"),
            "https://efts.sec.gov/LATEST/search-index?q=AAPL&forms=10-K",
        )

    def test_requires_user_agent(self):
        with self.assertRaises(ValueError):
            SECClient(user_agent="")

    def test_lookup_ticker_uses_company_ticker_directory(self):
        class FakeClient(SECClient):
            def __init__(self):
                pass

            def get_company_tickers(self):
                return {"0": {"ticker": "AAPL", "title": "Apple Inc.", "cik_str": 320193}}

        match = FakeClient().lookup_ticker("aapl")

        self.assertEqual(match.cik, "0000320193")
        self.assertEqual(match.ticker, "AAPL")

    def test_lookup_cik_uses_company_ticker_directory(self):
        class FakeClient(SECClient):
            def __init__(self):
                pass

            def get_company_tickers(self):
                return {"0": {"ticker": "C", "title": "Citigroup Inc.", "cik_str": 831001}}

        match = FakeClient().lookup_cik("0000831001")

        self.assertEqual(match.cik, "0000831001")
        self.assertEqual(match.ticker, "C")
        self.assertEqual(match.title, "Citigroup Inc.")

    def test_download_10k_for_year_returns_direct_body_without_persisting_raw(self):
        class FakeClient(SECClient):
            def __init__(self):
                pass

            def iter_submission_filings(self, cik):
                return [
                    FilingMetadata(
                        accession_number="0000320193-23-000106",
                        form="10-K",
                        filing_date="2023-11-03",
                        report_date="2023-09-30",
                        primary_document="aapl-20230930.htm",
                    )
                ]

            def fetch_bytes(self, url):
                self.last_url = url
                return b"<html>filing</html>"

        download = FakeClient().download_10k_for_year("320193", 2023)

        self.assertEqual(download.cik, "0000320193")
        self.assertEqual(download.body, b"<html>filing</html>")
        self.assertEqual(
            download.archive_url,
            "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm",
        )
        self.assertEqual(download.metadata.primary_document, "aapl-20230930.htm")


if __name__ == "__main__":
    unittest.main()
