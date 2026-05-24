from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sec_item_extractor.sec_client import SECClient


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"


def main() -> int:
    user_agent = os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        print("Set SEC_USER_AGENT before fetching SEC filings, e.g. 'Name email@example.com'.", file=sys.stderr)
        return 2

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    client = SECClient(user_agent=user_agent)
    filings_by_cik = {}

    for filing in manifest["filings"]:
        destination = RAW_DIR / f"{filing['filing_id']}.html"
        if destination.exists():
            print(f"skip existing {destination.relative_to(ROOT)}", flush=True)
            continue

        cik = filing["cik"]
        if cik not in filings_by_cik:
            print(f"fetch submissions for CIK {cik}", flush=True)
            filings_by_cik[cik] = client.iter_submission_filings(cik)

        match = _find_10k_for_year(filings_by_cik[cik], filing["fiscal_year"])
        if not match:
            print(f"missing {filing['filing_id']}: no 10-K with reportDate in fiscal year", file=sys.stderr)
            continue

        body = client.download_filing(filing["cik"], match.accession_number, match.primary_document)
        destination.write_bytes(body)
        print(f"fetched {filing['filing_id']} -> {destination.relative_to(ROOT)}", flush=True)

    return 0


def _find_10k_for_year(filings: list, fiscal_year: int):
    for filing in filings:
        if filing.form != "10-K":
            continue
        if not filing.report_date.startswith(str(fiscal_year)):
            continue
        return filing
    return None


if __name__ == "__main__":
    raise SystemExit(main())
