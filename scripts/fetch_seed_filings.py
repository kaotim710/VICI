from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_no_dashes}/{document}"


def main() -> int:
    user_agent = os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        print("Set SEC_USER_AGENT before fetching SEC filings, e.g. 'Name email@example.com'.", file=sys.stderr)
        return 2

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for filing in manifest["filings"]:
        destination = RAW_DIR / f"{filing['filing_id']}.html"
        if destination.exists():
            print(f"skip existing {destination.relative_to(ROOT)}")
            continue

        submission = _fetch_json(SEC_SUBMISSIONS_URL.format(cik=filing["cik"].zfill(10)), user_agent)
        match = _find_10k_for_year(submission, filing["fiscal_year"])
        if not match:
            print(f"missing {filing['filing_id']}: no 10-K with reportDate in fiscal year", file=sys.stderr)
            continue

        cik_int = str(int(filing["cik"]))
        accession_no_dashes = match["accessionNumber"].replace("-", "")
        url = SEC_ARCHIVES_URL.format(
            cik_int=cik_int,
            accession_no_dashes=accession_no_dashes,
            document=match["primaryDocument"],
        )
        body = _fetch_bytes(url, user_agent)
        destination.write_bytes(body)
        print(f"fetched {filing['filing_id']} -> {destination.relative_to(ROOT)}")
        time.sleep(0.2)

    return 0


def _find_10k_for_year(submission: dict, fiscal_year: int) -> dict | None:
    recent = submission.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    report_dates = recent.get("reportDate", [])
    accession_numbers = recent.get("accessionNumber", [])
    primary_documents = recent.get("primaryDocument", [])

    for index, form in enumerate(forms):
        if form != "10-K":
            continue
        report_date = report_dates[index] if index < len(report_dates) else ""
        if not report_date.startswith(str(fiscal_year)):
            continue
        return {
            "accessionNumber": accession_numbers[index],
            "primaryDocument": primary_documents[index],
        }
    return None


def _fetch_json(url: str, user_agent: str) -> dict:
    return json.loads(_fetch_bytes(url, user_agent).decode("utf-8"))


def _fetch_bytes(url: str, user_agent: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


if __name__ == "__main__":
    raise SystemExit(main())

