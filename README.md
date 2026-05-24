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
