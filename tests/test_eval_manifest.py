import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor.candidates import ITEM_ORDER


class EvalManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "fixtures" / "gold" / "eval_filings.json").read_text())

    def test_eval_manifest_has_expected_shape(self):
        self.assertEqual(self.manifest["selection_strategy"]["total_companies"], 24)
        self.assertEqual(self.manifest["selection_strategy"]["total_filings"], 48)
        self.assertEqual(len(self.manifest["companies"]), 24)
        self.assertEqual(len(self.manifest["filings"]), 48)
        self.assertEqual(self.manifest["items"], ITEM_ORDER)

    def test_sector_and_market_cap_mix(self):
        by_sector = Counter(company["sector_bucket"] for company in self.manifest["companies"])
        self.assertEqual(
            by_sector,
            {"Technology": 8, "Financials": 8, "Industrials / Energy": 8},
        )

        mix = defaultdict(Counter)
        for company in self.manifest["companies"]:
            mix[company["sector_bucket"]][company["market_cap_bucket"]] += 1

        for sector in ["Technology", "Financials", "Industrials / Energy"]:
            self.assertEqual(mix[sector], {"top_six": 6, "mid_small": 2})

    def test_each_company_has_recent_and_historical_filing(self):
        filings_by_ticker = defaultdict(list)
        for filing in self.manifest["filings"]:
            filings_by_ticker[filing["ticker"]].append(filing)

        self.assertEqual(set(filings_by_ticker), {company["ticker"] for company in self.manifest["companies"]})
        for ticker, filings in filings_by_ticker.items():
            self.assertEqual(len(filings), 2, ticker)
            by_window = {filing["time_window"]: filing for filing in filings}
            self.assertEqual(set(by_window), {"historical", "recent"}, ticker)
            self.assertLess(by_window["historical"]["fiscal_year"], 2020)
            self.assertGreaterEqual(by_window["recent"]["fiscal_year"], 2020)
            self.assertLessEqual(by_window["recent"]["fiscal_year"], 2025)

    def test_eval_manifest_ids_and_identifiers_are_clean(self):
        filing_ids = [filing["filing_id"] for filing in self.manifest["filings"]]
        self.assertEqual(len(filing_ids), len(set(filing_ids)))

        companies_by_ticker = {company["ticker"]: company for company in self.manifest["companies"]}
        for company in self.manifest["companies"]:
            self.assertRegex(company["ticker"], r"^[A-Z][A-Z0-9-]{0,9}$")
            self.assertRegex(company["cik"], r"^\d{10}$")
        for filing in self.manifest["filings"]:
            self.assertIn(filing["ticker"], companies_by_ticker)
            self.assertEqual(filing["cik"], companies_by_ticker[filing["ticker"]]["cik"])
            self.assertRegex(filing["filing_id"], r"^[a-z0-9-]+_\d{4}_eval_10k$")
            self.assertEqual(filing["form"], "10-K")


if __name__ == "__main__":
    unittest.main()
