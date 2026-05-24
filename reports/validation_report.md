# Held-Out Validation Report

Generated: 2026-05-24
Manifest: `fixtures/gold/validation_filings.json`
Evaluated filings: 10
Missing filings: 0
Item attempts: 230

## Aggregate Counts

- Filing status: `{'success': 10}`
- Item status: `{'success': 215, 'not_present': 15}`
- Confidence levels: `{'high': 225, 'medium': 5}`
- Warning categories: `{'length_policy_review': 14, 'title_policy_review': 1, 'toc_signal_review': 4}`

## Filings

| Filing | Status | TOC | Candidates | Actions | Warnings |
| --- | --- | --- | ---: | ---: | --- |
| `nvda_2015_10k` | success | high | 40 | 1 | Section length is outside the expected first-pass range. |
| `nvda_2025_10k` | success | high | 46 | 1 | Section length is outside the expected first-pass range. |
| `googl_2015_10k` | success | high | 40 | 2 | Section length is outside the expected first-pass range., Start heading has TOC-like signals. |
| `googl_2025_10k` | success | high | 46 | 2 | Start heading has TOC-like signals. |
| `meta_2015_10k` | success | high | 40 | 0 | none |
| `meta_2025_10k` | success | high | 46 | 0 | Section length is outside the expected first-pass range. |
| `lly_2015_10k` | success | high | 40 | 1 | Section length is outside the expected first-pass range. |
| `lly_2025_10k` | success | high | 46 | 1 | Section length is outside the expected first-pass range. |
| `pg_2015_10k` | success | none | 20 | 1 | Section length is outside the expected first-pass range. |
| `pg_2025_10k` | success | high | 46 | 1 | Section length is outside the expected first-pass range., Start heading does not contain the expected canonical title. |

## Non-Success Items

### nvda_2015_10k Item 8

- Status: `success`
- Confidence: `high` 0.90
- Text length: 207
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 1

### nvda_2025_10k Item 6

- Status: `success`
- Confidence: `high` 0.90
- Text length: 41
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 0

### nvda_2025_10k Item 8

- Status: `success`
- Confidence: `high` 0.90
- Text length: 207
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 1

### googl_2015_10k Item 1B

- Status: `success`
- Confidence: `medium` 0.75
- Text length: 87177
- Warnings: `Start heading has TOC-like signals., Section length is outside the expected first-pass range.`
- Recommended actions: 1

### googl_2015_10k Item 11

- Status: `success`
- Confidence: `high` 0.85
- Text length: 387
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 1

### googl_2015_10k Item 15

- Status: `success`
- Confidence: `high` 0.90
- Text length: 367163
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 0

### googl_2025_10k Item 6

- Status: `success`
- Confidence: `high` 0.85
- Text length: 175475
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 1

### googl_2025_10k Item 7

- Status: `success`
- Confidence: `high` 0.85
- Text length: 175450
- Warnings: `Start heading has TOC-like signals.`
- Recommended actions: 1

### meta_2025_10k Item 6

- Status: `success`
- Confidence: `high` 0.90
- Text length: 40
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 0

### lly_2015_10k Item 7A

- Status: `success`
- Confidence: `high` 0.90
- Text length: 307
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 1

### lly_2015_10k Item 15

- Status: `success`
- Confidence: `high` 0.90
- Text length: 371275
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 0

### lly_2025_10k Item 6

- Status: `success`
- Confidence: `high` 0.90
- Text length: 18
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 0

### lly_2025_10k Item 7A

- Status: `success`
- Confidence: `high` 0.90
- Text length: 311
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 1

### lly_2025_10k Item 16

- Status: `success`
- Confidence: `high` 0.90
- Text length: 363493
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 0

### pg_2015_10k Item 7A

- Status: `success`
- Confidence: `high` 0.90
- Text length: 308
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 1

### pg_2025_10k Item 6

- Status: `success`
- Confidence: `medium` 0.80
- Text length: 30
- Warnings: `Start heading does not contain the expected canonical title., Section length is outside the expected first-pass range.`
- Recommended actions: 0

### pg_2025_10k Item 7A

- Status: `success`
- Confidence: `high` 0.90
- Text length: 276
- Warnings: `Section length is outside the expected first-pass range.`
- Recommended actions: 1

