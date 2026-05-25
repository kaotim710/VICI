# Held-Out Validation Report

Generated: 2026-05-25
Manifest: `fixtures/gold/validation_filings.json`
Evaluated filings: 10
Missing filings: 0
Item attempts: 230

## Aggregate Counts

- Filing status: `{'success': 10}`
- Item status: `{'success': 215, 'not_present': 15}`
- Confidence levels: `{'high': 227, 'medium': 3}`
- Warnings: `{}`
- Warning categories: `{}`

## Validation Gate

- Passed: `True`

| Check | Actual | Expected | Passed |
| --- | ---: | --- | --- |
| `missing_filings` | 0 | `<= 0` | True |
| `failed_items` | 0 | `<= 0` | True |
| `warning_count` | 0 | `<= 0` | True |

## Filings

| Filing | Status | TOC | Candidates | Actions | Warnings |
| --- | --- | --- | ---: | ---: | --- |
| `nvda_2015_10k` | success | high | 40 | 8 | none |
| `nvda_2025_10k` | success | high | 46 | 8 | none |
| `googl_2015_10k` | success | high | 40 | 13 | none |
| `googl_2025_10k` | success | high | 46 | 15 | none |
| `meta_2015_10k` | success | high | 40 | 6 | none |
| `meta_2025_10k` | success | high | 46 | 9 | none |
| `lly_2015_10k` | success | high | 40 | 8 | none |
| `lly_2025_10k` | success | high | 46 | 7 | none |
| `pg_2015_10k` | success | none | 20 | 5 | none |
| `pg_2025_10k` | success | high | 46 | 5 | none |

## Warning And Failed Items

No warning or failed items in this validation run.

## Not Present Items

- `nvda_2015_10k` Item `1C`
- `nvda_2015_10k` Item `9C`
- `nvda_2015_10k` Item `16`
- `googl_2015_10k` Item `1C`
- `googl_2015_10k` Item `9C`
- `googl_2015_10k` Item `16`
- `meta_2015_10k` Item `1C`
- `meta_2015_10k` Item `9C`
- `meta_2015_10k` Item `16`
- `lly_2015_10k` Item `1C`
- `lly_2015_10k` Item `9C`
- `lly_2015_10k` Item `16`
- `pg_2015_10k` Item `1C`
- `pg_2015_10k` Item `9C`
- `pg_2015_10k` Item `16`
