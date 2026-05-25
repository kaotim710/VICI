# SEC Data Sources

This project uses official SEC EDGAR endpoints for filing intake.

Sources:

- API overview: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Submissions API: `https://data.sec.gov/submissions/CIK{10-digit-cik}.json`
- Full-text search: `https://efts.sec.gov/LATEST/search-index?q={query}&forms=10-K`
- Filing download: `https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-dashes}/{filename}`
- XBRL Company Facts: `https://data.sec.gov/api/xbrl/companyfacts/CIK{10-digit-cik}.json`

Operational requirements:

- Send a descriptive `User-Agent` header.
- Stay at or below 10 requests per second.
- No API key is required.

Implementation notes:

- The first milestone uses the Submissions API plus direct filing download.
- Full-text search is reserved for later ticker/query discovery.
- Company Facts is reserved for cross-validation, not primary section extraction.
- Raw filing files are ignored by git and stored under `fixtures/filings/raw/` for local evaluation.
- Live intake supports a direct-fetch mode: ticker or CIK plus fiscal year resolves 10-K metadata and
  can download the primary document without persisting raw storage by default.
- Persisted raw files remain an optional evaluation artifact, not a requirement for live extraction.
- Local UI endpoints:
  - `/api/sec/intake-plan?ticker=AAPL&year=2023` resolves metadata only.
  - `/api/sec/extract?ticker=AAPL&year=2023` downloads the filing and runs in-memory extraction.
