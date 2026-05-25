# Live SEC Real Filing Smoke Report

Generated: 2026-05-25
Source: live SEC direct fetch via local /api/sec/extract
Random seed: `20260525`
Year range: `2015-2020`
Selection note: Random seed 20260525 selected JNJ 2015, but SEC report-date lookup had no 10-K match, so JNJ was reselected to 2016 within the requested 2015-2020 window.

## Summary

- Filings tested: `6`
- Errors: `0`
- Status counts: `{'success': 6}`
- Filing status counts: `{'success': 6}`
- Warning total: `0`
- Failed total: `0`
- Recommended action total: `77`

## Filing Results

| Filing | Year | HTTP | Status | Accession | Report date | TOC | Items | Warnings | Failed | Actions | Bytes | Elapsed |
| --- | ---: | ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `XOM` | 2015 | 200 | success | `0000034088-16-000065` | 2015-12-31 | high | 24 | 0 | 0 | 6 | 7694659 | 2803 |
| `JNJ` | 2016 | 200 | success | `0000200406-16-000071` | 2016-01-03 | none | 23 | 0 | 0 | 19 | 3359357 | 2308 |
| `JPM` | 2017 | 200 | success | `0000019617-18-000057` | 2017-12-31 | high | 24 | 0 | 0 | 13 | 15477792 | 30458 |
| `BAC` | 2019 | 200 | success | `0000070858-20-000011` | 2019-12-31 | high | 23 | 0 | 0 | 15 | 19800395 | 11461 |
| `UNH` | 2015 | 200 | success | `0000731766-16-000058` | 2015-12-31 | high | 23 | 0 | 0 | 13 | 3472495 | 2179 |
| `CVX` | 2020 | 200 | success | `0000093410-21-000009` | 2020-12-31 | none | 23 | 0 | 0 | 11 | 6836700 | 2391 |

## Warning And Failed Items

No warning or failed items in this live SEC run.

## Not Present Items

- `XOM 2015`: `1C, 9C, 16`
- `JNJ 2016`: `1C, 9C, 16`
- `JPM 2017`: `1C, 9C, 16`
- `BAC 2019`: `1C, 9C`
- `UNH 2015`: `1C, 9C, 16`
- `CVX 2020`: `1C, 9C`

## Recovery Action Counts

### XOM 2015
- `inspect_only:exhibit_index_detected`: 2
- `inspect_only:section_reference_detected`: 2
- `needs_external_source:external_or_other_document_reference`: 2

### JNJ 2016
- `inspect_only:exhibit_index_detected`: 4
- `inspect_only:section_reference_detected`: 14
- `needs_external_source:external_or_other_document_reference`: 1

### JPM 2017
- `inspect_only:exhibit_index_detected`: 3
- `inspect_only:section_reference_detected`: 8
- `needs_user_confirmation:same_filing_page_reference`: 2

### BAC 2019
- `inspect_only:exhibit_index_detected`: 1
- `inspect_only:section_reference_detected`: 13
- `needs_user_selection:internal_item_toc_detected`: 1

### UNH 2015
- `inspect_only:exhibit_index_detected`: 1
- `inspect_only:section_reference_detected`: 12

### CVX 2020
- `inspect_only:exhibit_index_detected`: 4
- `inspect_only:section_reference_detected`: 6
- `needs_user_selection:internal_item_toc_detected`: 1
