# Held-Out Validation Report

Generated: 2026-05-25
Manifest: `fixtures/gold/validation_filings.json`
Evaluated filings: 10
Missing filings: 0
Item attempts: 230

## Aggregate Counts

- Filing status: `{'success': 10}`
- Item status: `{'success': 215, 'not_present': 15}`
- Confidence levels: `{'high': 226, 'medium': 4}`
- Warning categories: `{'length_policy_review': 1, 'title_policy_review': 1, 'toc_signal_review': 6}`

## Filings

| Filing | Status | TOC | Candidates | Actions | Warnings |
| --- | --- | --- | ---: | ---: | --- |
| `nvda_2015_10k` | success | high | 40 | 7 | none |
| `nvda_2025_10k` | success | high | 46 | 11 | Start heading has TOC-like signals. |
| `googl_2015_10k` | success | high | 40 | 19 | Start heading has TOC-like signals. |
| `googl_2025_10k` | success | high | 46 | 20 | Start heading has TOC-like signals. |
| `meta_2015_10k` | success | high | 40 | 6 | none |
| `meta_2025_10k` | success | high | 46 | 13 | Start heading has TOC-like signals. |
| `lly_2015_10k` | success | high | 40 | 8 | none |
| `lly_2025_10k` | success | high | 46 | 7 | none |
| `pg_2015_10k` | success | none | 20 | 5 | none |
| `pg_2025_10k` | success | high | 46 | 5 | Section length is outside the expected first-pass range., Start heading does not contain the expected canonical title. |

## Non-Success Items

### nvda_2025_10k Item 6

- Status: `success`
- Confidence: `high` 0.85
- Text length: 181862
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 3

### googl_2015_10k Item 1B

- Status: `success`
- Confidence: `high` 0.85
- Text length: 87177
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 3

### googl_2015_10k Item 11

- Status: `success`
- Confidence: `high` 0.85
- Text length: 364375
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 4

### googl_2025_10k Item 6

- Status: `success`
- Confidence: `high` 0.85
- Text length: 175475
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 3

### googl_2025_10k Item 7

- Status: `success`
- Confidence: `high` 0.85
- Text length: 175450
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 3

### meta_2025_10k Item 6

- Status: `success`
- Confidence: `high` 0.85
- Text length: 283798
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 4

### pg_2025_10k Item 6

- Status: `success`
- Confidence: `medium` 0.80
- Text length: 30
- Warnings: `Start heading does not contain the expected canonical title., Section length is outside the expected first-pass range.`
- Recommended actions: 0

