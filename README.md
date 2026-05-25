# SEC 10-K Item Extraction Pipeline

Production-style deterministic extraction for SEC 10-K narrative sections.

The first milestone intentionally stays small:

- local HTML/text filing input
- deterministic extraction for Item 1, Item 1A, and Item 7
- inspectable evidence, warnings, and confidence
- stdlib-only test runner

Deferred until later milestones:

- SEC ticker/year ingestion
- background jobs and storage
- embeddings
- LLM ambiguity verifier
- Zeabur deployment

## Run Tests

```bash
python3 -m unittest discover -s tests
```

## CLI

```bash
PYTHONPATH=src python3 -m sec_item_extractor path/to/10k.html --items 1 1A 7
```

## Web UI

Run the local review UI:

```bash
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/run_web_ui.py --host 127.0.0.1 --port 8000
```

The UI supports three intake paths:

- seed filings from local fixtures
- live SEC ticker/year extraction without raw persistence
- uploaded HTML/TXT filings extracted in memory without raw persistence

The frontend is a React single-page app served from `frontend/`; the Python server keeps
the extraction APIs and serves the React shell for `/`, `/upload`, `/sec-live`, and
`/filings/...`.

Live SEC requests require `SEC_USER_AGENT`. Uploaded filings do not require SEC credentials.
`MAX_UPLOAD_BYTES` controls the upload limit and defaults to 25 MB.

## Zeabur Deployment

This repo includes a `Dockerfile` for Zeabur. Configure these environment variables:

```bash
HOST=0.0.0.0
PORT=8000
SEC_USER_AGENT="Your Name your.email@example.com"
MAX_UPLOAD_BYTES=26214400
```

Zeabur may provide `PORT` automatically; the web server reads it from the environment.
Without `SEC_USER_AGENT`, live SEC ticker/year intake is blocked, but file upload parsing still works.
Use `/api/health` as the service health check path.

Recommended Zeabur setup:

1. Create a service from the public GitHub repo.
2. Use the repository root as the root directory.
3. Let Zeabur deploy with the root `Dockerfile`.
4. Set `SEC_USER_AGENT` to a descriptive contact string before using live SEC intake.

## Seed Dataset

The first test corpus is planned in [fixtures/gold/seed_filings.json](fixtures/gold/seed_filings.json):

- 5 industries
- 2 companies per industry
- 2 fiscal years per company
- 20 filings total

Boundary labels should follow [fixtures/gold/boundaries.example.json](fixtures/gold/boundaries.example.json).

Fetch the seed filings into ignored local fixtures:

```bash
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/fetch_seed_filings.py
```

Evaluate whatever seed filings are present locally:

```bash
python3 scripts/evaluate_seed.py
```

Export a Markdown extraction report for the seed filings:

```bash
python3 scripts/export_seed_extractions_md.py
```

Export a warning-focused audit report:

```bash
python3 scripts/export_warning_audit_md.py
```

Run deterministic recovery actions for warnings:

```bash
python3 scripts/run_recovery_actions.py
```

For internal Item 7 TOC cases, pass an explicit subsection choice:

```bash
python3 scripts/run_recovery_actions.py --select "bac_2023_10k:7=Executive Summary"
```

Evaluate lightweight gold boundary expectations:

```bash
python3 scripts/evaluate_gold_boundaries.py
```

Generate the combined seed + validation regression report:

```bash
python3 scripts/evaluate_regression.py
```

Fetch and evaluate the held-out validation filings:

```bash
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/fetch_validation_filings.py
python3 scripts/evaluate_validation.py
```

Inspect normalized narrative blocks for a filing:

```bash
python3 scripts/inspect_document.py fixtures/filings/raw/aapl_2023_10k.html --limit 10
```

Inspect item heading candidates:

```bash
python3 scripts/inspect_candidates.py fixtures/filings/raw/aapl_2023_10k.html --limit 25
```

## SEC Intake Sources

The ingestion utilities follow the official SEC EDGAR API shape documented in
[docs/sec-data-sources.md](docs/sec-data-sources.md). Requests require a descriptive
`User-Agent`, are rate-limited to 10 requests per second by default, and do not require
an API key.

## Milestone 2: Block Model

HTML/text cleaning now produces a `CleanDocument` with normalized text plus `NarrativeBlock`
records. Each block includes clean offsets, raw offsets, source type, and the nearest block tag
when available. `html_to_text()` remains available for the deterministic extractor.

## Milestone 3: Candidate Evidence

Candidate retrieval now attaches block/raw metadata to heading candidates and records selected or
rejected candidate attempts in each item result. This keeps boundary decisions inspectable without
introducing embeddings or LLM calls.

## Milestone 4: Confidence Summary

Item results now include `confidence_components`, which break the final score into deterministic,
explainable signals: legal boundary pair, TOC filtering, expected title match, and section length.
`scripts/evaluate_seed.py` also emits aggregate status, confidence-level, and warning counts across
the seed filings.

## Reliability Regression

`scripts/evaluate_regression.py` combines seed and validation filings into a single regression
surface. It records per-item status, confidence, warning categories, raw table/image counts,
supplemental section counts, raw preview availability, and recovery action counts.
