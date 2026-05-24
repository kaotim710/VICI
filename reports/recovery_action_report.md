# Recovery Action Report

Generated: 2026-05-24

Scope: deterministic recovery actions for seed filings with recommended actions.

Recovery actions: 50
Missing filings: 0

Contract version: `recovery_action_v1`

## Status Counts

| Status | Count |
| --- | ---: |
| `blocked` | 1 |
| `deferred` | 26 |
| `inspect_only` | 20 |
| `needs_review` | 1 |
| `needs_user_selection` | 2 |

## Reason Counts

| Reason | Count |
| --- | ---: |
| `external_or_other_document_reference` | 26 |
| `internal_item_toc_detected` | 2 |
| `same_filing_page_reference` | 2 |
| `start_toc_like_signal` | 20 |

## Actions

| Filing | Item | Action | Reason | Severity | User Input | Status | Before | After | Page Range | Selection |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| `aapl_2023_10k` | 9C | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 180958 | none | none | none |
| `jpm_2014_10k` | 7 | `needs_user_confirmation` | `same_filing_page_reference` | `review` | yes | `blocked` | 395 | none | 64-169 | none |
| `jpm_2014_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 253 | none | none | none |
| `jpm_2014_10k` | 8 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 551 | none | none | none |
| `jpm_2023_10k` | 7 | `needs_user_confirmation` | `same_filing_page_reference` | `review` | yes | `needs_review` | 396 | 244421 | 48-161 | none |
| `jpm_2023_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 272 | none | none | none |
| `jpm_2023_10k` | 8 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 370 | none | none | none |
| `bac_2014_10k` | 7 | `needs_user_selection` | `internal_item_toc_detected` | `review` | yes | `needs_user_selection` | 578441 | none | none | none |
| `bac_2014_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 218 | none | none | none |
| `bac_2023_10k` | 7 | `needs_user_selection` | `internal_item_toc_detected` | `review` | yes | `needs_user_selection` | 308102 | none | none | none |
| `bac_2023_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 218 | none | none | none |
| `unh_2014_10k` | 2 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 133299 | none | none | none |
| `unh_2014_10k` | 7 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 219335 | none | none | none |
| `unh_2023_10k` | 2 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 122323 | none | none | none |
| `unh_2023_10k` | 3 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 122298 | none | none | none |
| `unh_2023_10k` | 6 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 165798 | none | none | none |
| `unh_2023_10k` | 7 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 165775 | none | none | none |
| `jnj_2014_10k` | 1A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 546 | none | none | none |
| `jnj_2014_10k` | 7 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 386 | none | none | none |
| `jnj_2014_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 386 | none | none | none |
| `jnj_2014_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 531 | none | none | none |
| `jnj_2014_10k` | 8 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 360 | none | none | none |
| `jnj_2023_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 486 | none | none | none |
| `xom_2014_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 265 | none | none | none |
| `xom_2014_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 510 | none | none | none |
| `xom_2014_10k` | 8 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 780 | none | none | none |
| `xom_2023_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 265 | none | none | none |
| `xom_2023_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 411 | none | none | none |
| `xom_2023_10k` | 8 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 737 | none | none | none |
| `cvx_2014_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 278 | none | none | none |
| `cvx_2014_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 451 | none | none | none |
| `cvx_2014_10k` | 8 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 187 | none | none | none |
| `cvx_2023_10k` | 6 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 262 | none | none | none |
| `cvx_2023_10k` | 7 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 242 | none | none | none |
| `cvx_2023_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 242 | none | none | none |
| `cvx_2023_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 354 | none | none | none |
| `cvx_2023_10k` | 8 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 158 | none | none | none |
| `wmt_2014_10k` | 7 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 413 | none | none | none |
| `wmt_2014_10k` | 7A | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 423 | none | none | none |
| `wmt_2014_10k` | 8 | `needs_external_source` | `external_or_other_document_reference` | `blocked` | yes | `deferred` | 606 | none | none | none |
| `amzn_2014_10k` | 2 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 1253 | none | none | none |
| `amzn_2014_10k` | 3 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 152 | none | none | none |
| `amzn_2014_10k` | 9B | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 34 | none | none | none |
| `amzn_2014_10k` | 10 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 1545 | none | none | none |
| `amzn_2014_10k` | 11 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 484 | none | none | none |
| `amzn_2014_10k` | 12 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 277 | none | none | none |
| `amzn_2023_10k` | 2 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 79315 | none | none | none |
| `amzn_2023_10k` | 3 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 79290 | none | none | none |
| `amzn_2023_10k` | 9C | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 268364 | none | none | none |
| `amzn_2023_10k` | 13 | `inspect_only` | `start_toc_like_signal` | `info` | no | `inspect_only` | 256 | none | none | none |

## Details

### aapl_2023_10k Item 9C - start_toc_like_signal

- Ticker: `AAPL`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `180958`

### jpm_2014_10k Item 7 - same_filing_page_reference

- Ticker: `JPM`
- Fiscal year: `2014`
- Status: `blocked`
- Severity: `review`
- Requires user input: `True`
- Next step: `confirm_referenced_page_extraction`
- Contract version: `recovery_action_v1`
- Message: Page range was parsed, but reliable page locators were not found in the normalized filing text.
- Before length: `395`
- Parsed page range: `64-169`
- Evidence: `parsed pages 64-169, page locators found: 978`

### jpm_2014_10k Item 7A - external_or_other_document_reference

- Ticker: `JPM`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `253`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### jpm_2014_10k Item 8 - external_or_other_document_reference

- Ticker: `JPM`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `551`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### jpm_2023_10k Item 7 - same_filing_page_reference

- Ticker: `JPM`
- Fiscal year: `2023`
- Status: `needs_review`
- Severity: `review`
- Requires user input: `True`
- Next step: `confirm_referenced_page_extraction`
- Contract version: `recovery_action_v1`
- Message: Extracted text from inferred same-filing page range; review required before replacing the original section.
- Before length: `396`
- After length: `244421`
- Parsed page range: `48-161`
- Evidence: `parsed pages 48-161, page locators found: 889`

Recovered start snippet:

> $ 48 $ 22 $ — $ 23 $ 78 $ — $ 1 $ 192 Secured by real estate (in millions) December 31, 2022 Term loans by origination year Revolving loans 2022 2021 2020 2019 2018 Prior to 2018 Within the revolving period Converted...

Recovered end snippet:

> ...19,227 268 5,857 6,125 Non-U.S. 597 10,110 10,707 161 3,265 3,426 Federal funds purchased and securities loaned or sold under repurchase agreements: U.S. 1,293 6,263 7,556 (466) 3,327 2,861 Non-U.S. (480) 2,462 1,982

### jpm_2023_10k Item 7A - external_or_other_document_reference

- Ticker: `JPM`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `272`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### jpm_2023_10k Item 8 - external_or_other_document_reference

- Ticker: `JPM`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `370`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### bac_2014_10k Item 7 - internal_item_toc_detected

- Ticker: `BAC`
- Fiscal year: `2014`
- Status: `needs_user_selection`
- Severity: `review`
- Requires user input: `True`
- Next step: `select_internal_heading`
- Contract version: `recovery_action_v1`
- Message: Choose one internal heading option to extract a subsection.
- Before length: `578441`
- Options: `Management’s Discussion and Analysis of Financial Condition and Results of Operation, Table of Contents, Executive Summary, Financial Highlights, Balance Sheet Overview, Supplemental Financial Data, Business Segment Operations, Consumer & Business Banking, Consumer Real Estate Services, Global Wealth & Investment Management, Global Banking, Global Markets`

### bac_2014_10k Item 7A - external_or_other_document_reference

- Ticker: `BAC`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `218`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### bac_2023_10k Item 7 - internal_item_toc_detected

- Ticker: `BAC`
- Fiscal year: `2023`
- Status: `needs_user_selection`
- Severity: `review`
- Requires user input: `True`
- Next step: `select_internal_heading`
- Contract version: `recovery_action_v1`
- Message: Choose one internal heading option to extract a subsection.
- Before length: `308102`
- Options: `Management's Discussion and Analysis of Financial Condition and Results of Operations, Table of Contents, Executive Summary, Recent Developments, Financial Highlights, Balance Sheet Overview, Supplemental Financial Data, Business Segment Operations, Consumer Banking, Global Wealth & Investment Management, Global Banking, Global Markets`

### bac_2023_10k Item 7A - external_or_other_document_reference

- Ticker: `BAC`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `218`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### unh_2014_10k Item 2 - start_toc_like_signal

- Ticker: `UNH`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `133299`

### unh_2014_10k Item 7 - start_toc_like_signal

- Ticker: `UNH`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `219335`

### unh_2023_10k Item 2 - start_toc_like_signal

- Ticker: `UNH`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `122323`

### unh_2023_10k Item 3 - start_toc_like_signal

- Ticker: `UNH`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `122298`

### unh_2023_10k Item 6 - start_toc_like_signal

- Ticker: `UNH`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `165798`

### unh_2023_10k Item 7 - start_toc_like_signal

- Ticker: `UNH`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `165775`

### jnj_2014_10k Item 1A - external_or_other_document_reference

- Ticker: `JNJ`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `546`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### jnj_2014_10k Item 7 - start_toc_like_signal

- Ticker: `JNJ`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `386`

### jnj_2014_10k Item 7 - external_or_other_document_reference

- Ticker: `JNJ`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `386`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### jnj_2014_10k Item 7A - external_or_other_document_reference

- Ticker: `JNJ`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `531`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### jnj_2014_10k Item 8 - external_or_other_document_reference

- Ticker: `JNJ`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `360`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### jnj_2023_10k Item 7A - external_or_other_document_reference

- Ticker: `JNJ`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `486`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### xom_2014_10k Item 7 - external_or_other_document_reference

- Ticker: `XOM`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `265`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### xom_2014_10k Item 7A - external_or_other_document_reference

- Ticker: `XOM`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `510`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### xom_2014_10k Item 8 - external_or_other_document_reference

- Ticker: `XOM`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `780`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### xom_2023_10k Item 7 - external_or_other_document_reference

- Ticker: `XOM`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `265`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### xom_2023_10k Item 7A - external_or_other_document_reference

- Ticker: `XOM`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `411`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### xom_2023_10k Item 8 - external_or_other_document_reference

- Ticker: `XOM`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `737`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### cvx_2014_10k Item 7 - external_or_other_document_reference

- Ticker: `CVX`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `278`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### cvx_2014_10k Item 7A - external_or_other_document_reference

- Ticker: `CVX`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `451`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### cvx_2014_10k Item 8 - external_or_other_document_reference

- Ticker: `CVX`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `187`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### cvx_2023_10k Item 6 - start_toc_like_signal

- Ticker: `CVX`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `262`

### cvx_2023_10k Item 7 - start_toc_like_signal

- Ticker: `CVX`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `242`

### cvx_2023_10k Item 7 - external_or_other_document_reference

- Ticker: `CVX`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `242`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### cvx_2023_10k Item 7A - external_or_other_document_reference

- Ticker: `CVX`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `354`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### cvx_2023_10k Item 8 - external_or_other_document_reference

- Ticker: `CVX`
- Fiscal year: `2023`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `158`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### wmt_2014_10k Item 7 - external_or_other_document_reference

- Ticker: `WMT`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `413`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### wmt_2014_10k Item 7A - external_or_other_document_reference

- Ticker: `WMT`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `423`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### wmt_2014_10k Item 8 - external_or_other_document_reference

- Ticker: `WMT`
- Fiscal year: `2014`
- Status: `deferred`
- Severity: `blocked`
- Requires user input: `True`
- Next step: `provide_or_fetch_reference_document`
- Contract version: `recovery_action_v1`
- Message: External/reference document recovery is intentionally deferred until source resolution is implemented.
- Before length: `606`
- Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

### amzn_2014_10k Item 2 - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `1253`

### amzn_2014_10k Item 3 - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `152`

### amzn_2014_10k Item 9B - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `34`

### amzn_2014_10k Item 10 - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `1545`

### amzn_2014_10k Item 11 - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `484`

### amzn_2014_10k Item 12 - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2014`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `277`

### amzn_2023_10k Item 2 - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `79315`

### amzn_2023_10k Item 3 - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `79290`

### amzn_2023_10k Item 9C - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `268364`

### amzn_2023_10k Item 13 - start_toc_like_signal

- Ticker: `AMZN`
- Fiscal year: `2023`
- Status: `inspect_only`
- Severity: `info`
- Requires user input: `False`
- Next step: `inspect_evidence_only`
- Contract version: `recovery_action_v1`
- Message: No deterministic recovery runner is registered for this action.
- Before length: `256`
