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
