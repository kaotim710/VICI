import unittest

from sec_item_extractor.sec_client import (
    SECClient,
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
        self.assertEqual(
            full_text_search_url("AAPL"),
            "https://efts.sec.gov/LATEST/search-index?q=AAPL&forms=10-K",
        )

    def test_requires_user_agent(self):
        with self.assertRaises(ValueError):
            SECClient(user_agent="")


if __name__ == "__main__":
    unittest.main()
