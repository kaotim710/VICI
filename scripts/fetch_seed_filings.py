from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sec_item_extractor.sec_client import SECClient


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
INVENTORY_PATH = ROOT / "fixtures" / "gold" / "downloaded_seed_filings.json"
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
    records = []
    missing = []

    for filing in manifest["filings"]:
        destination = RAW_DIR / f"{filing['filing_id']}.html"
        cik = filing["cik"]
        if cik not in filings_by_cik:
            print(f"fetch submissions for CIK {cik}", flush=True)
            filings_by_cik[cik] = client.iter_submission_filings(cik)

        match = _find_10k_for_year(filings_by_cik[cik], filing["fiscal_year"])
        if not match:
            missing.append(filing["filing_id"])
            print(f"missing {filing['filing_id']}: no 10-K with reportDate in fiscal year", file=sys.stderr)
            continue

        if destination.exists():
            print(f"skip existing {destination.relative_to(ROOT)}", flush=True)
        else:
            body = client.download_filing(filing["cik"], match.accession_number, match.primary_document)
            destination.write_bytes(body)
            print(f"fetched {filing['filing_id']} -> {destination.relative_to(ROOT)}", flush=True)

        records.append(_inventory_record(filing, match, destination))

    inventory = {
        "description": "Local inventory for the 20 downloaded seed 10-K filings. Raw filings are stored under fixtures/filings/raw/ and are intentionally ignored by git.",
        "downloaded_at": date.today().isoformat(),
        "user_agent_note": "Downloaded with SEC_USER_AGENT set locally; do not treat this file as a credential record.",
        "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "total_files": len(records),
        "total_bytes": sum(record["bytes"] for record in records),
        "missing": missing,
        "files": records,
    }
    INVENTORY_PATH.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {INVENTORY_PATH.relative_to(ROOT)}", flush=True)

    return 1 if missing else 0


def _find_10k_for_year(filings: list, fiscal_year: int):
    for filing in filings:
        if filing.form != "10-K":
            continue
        if not filing.report_date.startswith(str(fiscal_year)):
            continue
        return filing
    return None


def _inventory_record(filing: dict, match, path: Path) -> dict:
    return {
        "filing_id": filing["filing_id"],
        "ticker": filing["ticker"],
        "cik": filing["cik"],
        "fiscal_year": filing["fiscal_year"],
        "accession_number": match.accession_number,
        "filing_date": match.filing_date,
        "report_date": match.report_date,
        "primary_document": match.primary_document,
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
