# Recovery Action Report

Generated: 2026-05-24

Scope: deterministic recovery actions for seed filings with recommended actions.

Recovery actions: 13
Missing filings: 0

## Status Counts

| Status | Count |
| --- | ---: |
| `blocked` | 1 |
| `deferred` | 7 |
| `inspect_only` | 2 |
| `needs_review` | 1 |
| `needs_user_selection` | 2 |

## Reason Counts

| Reason | Count |
| --- | ---: |
| `external_or_other_document_reference` | 7 |
| `internal_item_toc_detected` | 2 |
| `same_filing_page_reference` | 2 |
| `start_toc_like_signal` | 2 |

## Actions

| Filing | Item | Action | Reason | Status | Before | After | Page Range | Selection |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| `jpm_2014_10k` | 7 | `needs_user_confirmation` | `same_filing_page_reference` | `blocked` | 395 | none | 64-169 | none |
| `jpm_2023_10k` | 7 | `needs_user_confirmation` | `same_filing_page_reference` | `needs_review` | 396 | 244421 | 48-161 | none |
| `bac_2014_10k` | 7 | `needs_user_selection` | `internal_item_toc_detected` | `needs_user_selection` | 578441 | none | none | none |
| `bac_2023_10k` | 7 | `needs_user_selection` | `internal_item_toc_detected` | `needs_user_selection` | 308102 | none | none | none |
| `unh_2014_10k` | 7 | `inspect_only` | `start_toc_like_signal` | `inspect_only` | 219335 | none | none | none |
| `unh_2023_10k` | 7 | `inspect_only` | `start_toc_like_signal` | `inspect_only` | 165775 | none | none | none |
| `jnj_2014_10k` | 1A | `needs_external_source` | `external_or_other_document_reference` | `deferred` | 546 | none | none | none |
| `jnj_2014_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `deferred` | 386 | none | none | none |
| `xom_2014_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `deferred` | 265 | none | none | none |
| `xom_2023_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `deferred` | 265 | none | none | none |
| `cvx_2014_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `deferred` | 278 | none | none | none |
| `cvx_2023_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `deferred` | 242 | none | none | none |
| `wmt_2014_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `deferred` | 413 | none | none | none |

## Details

### jpm_2014_10k Item 7 - same_filing_page_reference

- Ticker: `JPM`
- Fiscal year: `2014`
- Status: `blocked`
- Message: Page range was parsed, but reliable page locators were not found in the normalized filing text.
- Before length: `395`
- Parsed page range: `64-169`
- Evidence: `parsed pages 64-169, page locators found: 978`

### jpm_2023_10k Item 7 - same_filing_page_reference

- Ticker: `JPM`
- Fiscal year: `2023`
- Status: `needs_review`
- Message: Extracted text from inferred same-filing page range; review required before replacing the original section.
- Before length: `396`
- After length: `244421`
- Parsed page range: `48-161`
- Evidence: `parsed pages 48-161, page locators found: 889`

Recovered start snippet:

> $ 48 $ 22 $ — $ 23 $ 78 $ — $ 1 $ 192 Secured by real estate (in millions) December 31, 2022 Term loans by origination year Revolving loans 2022 2021 2020 2019 2018 Prior to 2018 Within the revolving period Converted...

Recovered end snippet:

> ...19,227 268 5,857 6,125 Non-U.S. 597 10,110 10,707 161 3,265 3,426 Federal funds purchased and securities loaned or sold under repurchase agreements: U.S. 1,293 6,263 7,556 (466) 3,327 2,861 Non-U.S. (480) 2,462 1,982

### bac_2014_10k Item 7 - internal_item_toc_detected

- Ticker: `BAC`
- Fiscal year: `2014`
- Status: `needs_user_selection`
- Message: Choose one internal heading option to extract a subsection.
- Before length: `578441`
- Options: `Management’s Discussion and Analysis of Financial Condition and Results of Operation, Table of Contents, Executive Summary, Financial Highlights, Balance Sheet Overview, Supplemental Financial Data, Business Segment Operations, Consumer & Business Banking, Consumer Real Estate Services, Global Wealth & Investment Management, Global Banking, Global Markets`

### bac_2023_10k Item 7 - internal_item_toc_detected

- Ticker: `BAC`
- Fiscal year: `2023`
- Status: `needs_user_selection`
- Message: Choose one internal heading option to extract a subsection.
- Before length: `308102`
- Options: `Management's Discussion and Analysis of Financial Condition and Results of Operations, Table of Contents, Executive Summary, Recent Developments, Financial Highlights, Balance Sheet Overview, Supplemental Financial Data, Business Segment Operations, Consumer Banking, Global Wealth & Investment Management, Global Banking, Global Markets`

### unh_2014_10k Item 7 - start_toc_like_signal

- Ticker: `UNH`
- Fiscal year: `2014`
- Status: `inspect_only`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `219335`

### unh_2023_10k Item 7 - start_toc_like_signal

- Ticker: `UNH`
- Fiscal year: `2023`
- Status: `inspect_only`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `165775`

### jnj_2014_10k Item 1A - external_or_other_document_reference

- Ticker: `JNJ`
- Fiscal year: `2014`
- Status: `deferred`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `546`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### jnj_2014_10k Item 7 - external_or_other_document_reference

- Ticker: `JNJ`
- Fiscal year: `2014`
- Status: `deferred`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `386`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### xom_2014_10k Item 7 - external_or_other_document_reference

- Ticker: `XOM`
- Fiscal year: `2014`
- Status: `deferred`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `265`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### xom_2023_10k Item 7 - external_or_other_document_reference

- Ticker: `XOM`
- Fiscal year: `2023`
- Status: `deferred`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `265`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### cvx_2014_10k Item 7 - external_or_other_document_reference

- Ticker: `CVX`
- Fiscal year: `2014`
- Status: `deferred`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `278`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### cvx_2023_10k Item 7 - external_or_other_document_reference

- Ticker: `CVX`
- Fiscal year: `2023`
- Status: `deferred`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `242`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### wmt_2014_10k Item 7 - external_or_other_document_reference

- Ticker: `WMT`
- Fiscal year: `2014`
- Status: `deferred`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `413`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`
