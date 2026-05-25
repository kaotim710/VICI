from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass


SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{filename}"
SEC_FULL_TEXT_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
DEFAULT_RATE_LIMIT_PER_SECOND = 10.0


def format_cik(cik: str | int) -> str:
    digits = "".join(character for character in str(cik) if character.isdigit())
    if not digits:
        raise ValueError("CIK must contain digits.")
    if len(digits) > 10:
        raise ValueError("CIK cannot be longer than 10 digits.")
    return digits.zfill(10)


def submissions_url(cik: str | int) -> str:
    return SEC_SUBMISSIONS_URL.format(cik=format_cik(cik))


def company_facts_url(cik: str | int) -> str:
    return SEC_COMPANY_FACTS_URL.format(cik=format_cik(cik))


def archive_url(cik: str | int, accession_number: str, filename: str) -> str:
    cik_no_padding = str(int(format_cik(cik)))
    accession_no_dashes = accession_number.replace("-", "")
    quoted_filename = urllib.parse.quote(filename)
    return SEC_ARCHIVES_URL.format(
        cik=cik_no_padding,
        accession_no_dashes=accession_no_dashes,
        filename=quoted_filename,
    )


def full_text_search_url(query: str, forms: str = "10-K") -> str:
    return f"{SEC_FULL_TEXT_SEARCH_URL}?{urllib.parse.urlencode({'q': query, 'forms': forms})}"


@dataclass
class FilingMetadata:
    accession_number: str
    form: str
    filing_date: str
    report_date: str
    primary_document: str


@dataclass
class TickerMetadata:
    ticker: str
    title: str
    cik: str


@dataclass
class FilingDownload:
    cik: str
    fiscal_year: int
    metadata: FilingMetadata
    archive_url: str
    body: bytes


class RateLimiter:
    def __init__(self, requests_per_second: float = DEFAULT_RATE_LIMIT_PER_SECOND) -> None:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive.")
        self._min_interval = 1.0 / requests_per_second
        self._last_request_at = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_at = time.monotonic()


class SECClient:
    def __init__(self, user_agent: str, requests_per_second: float = DEFAULT_RATE_LIMIT_PER_SECOND) -> None:
        if not user_agent.strip():
            raise ValueError("SEC requests require a descriptive User-Agent.")
        self.user_agent = user_agent
        self.rate_limiter = RateLimiter(requests_per_second=requests_per_second)

    def get_submissions(self, cik: str | int) -> dict:
        return self.fetch_json(submissions_url(cik))

    def get_company_facts(self, cik: str | int) -> dict:
        return self.fetch_json(company_facts_url(cik))

    def get_company_tickers(self) -> dict:
        return self.fetch_json(SEC_COMPANY_TICKERS_URL)

    def lookup_ticker(self, ticker: str) -> TickerMetadata | None:
        target = ticker.strip().upper()
        if not target:
            raise ValueError("ticker is required.")
        for row in self.get_company_tickers().values():
            if str(row.get("ticker", "")).upper() != target:
                continue
            return TickerMetadata(
                ticker=target,
                title=str(row.get("title", "")),
                cik=format_cik(row.get("cik_str", "")),
            )
        return None

    def full_text_search(self, query: str, forms: str = "10-K") -> dict:
        return self.fetch_json(full_text_search_url(query, forms=forms))

    def download_filing(self, cik: str | int, accession_number: str, filename: str) -> bytes:
        return self.fetch_bytes(archive_url(cik, accession_number, filename))

    def iter_submission_filings(self, cik: str | int) -> list[FilingMetadata]:
        submission = self.get_submissions(cik)
        filings = _rows_from_recent(submission.get("filings", {}).get("recent", {}))
        for extra_file in submission.get("filings", {}).get("files", []):
            name = extra_file.get("name")
            if not name:
                continue
            extra_url = urllib.parse.urljoin(submissions_url(cik), name)
            filings.extend(_rows_from_recent(self.fetch_json(extra_url)))
        return filings

    def find_10k_for_year(self, cik: str | int, fiscal_year: int) -> FilingMetadata | None:
        for filing in self.iter_submission_filings(cik):
            if filing.form != "10-K":
                continue
            if filing.report_date.startswith(str(fiscal_year)):
                return filing
        return None

    def download_10k_for_year(self, cik: str | int, fiscal_year: int) -> FilingDownload | None:
        formatted_cik = format_cik(cik)
        filing = self.find_10k_for_year(formatted_cik, fiscal_year)
        if filing is None:
            return None
        url = archive_url(formatted_cik, filing.accession_number, filing.primary_document)
        return FilingDownload(
            cik=formatted_cik,
            fiscal_year=fiscal_year,
            metadata=filing,
            archive_url=url,
            body=self.fetch_bytes(url),
        )

    def fetch_json(self, url: str) -> dict:
        return json.loads(self.fetch_bytes(url).decode("utf-8"))

    def fetch_bytes(self, url: str) -> bytes:
        self.rate_limiter.wait()
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept-Encoding": "identity",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()


def _rows_from_recent(recent: dict) -> list[FilingMetadata]:
    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    accession_numbers = recent.get("accessionNumber", [])
    primary_documents = recent.get("primaryDocument", [])
    rows = []
    for index, form in enumerate(forms):
        rows.append(
            FilingMetadata(
                accession_number=_value_at(accession_numbers, index),
                form=form,
                filing_date=_value_at(filing_dates, index),
                report_date=_value_at(report_dates, index),
                primary_document=_value_at(primary_documents, index),
            )
        )
    return rows


def _value_at(values: list, index: int) -> str:
    if index >= len(values):
        return ""
    return values[index] or ""
