# Warning Audit Report

Generated: 2026-05-24

Scope: seed 10-K filings with non-empty item warnings.

Warning items: 66
Items with rejected candidate pairs: 20
Missing filings: 0

## Warning Counts

| Warning | Count |
| --- | ---: |
| `End heading has TOC-like signals.` | 2 |
| `Section appears to be a cross-reference rather than full narrative text.` | 2 |
| `Section length is outside the expected first-pass range.` | 47 |
| `Start heading does not contain the expected canonical title.` | 4 |
| `Start heading has TOC-like signals.` | 20 |

## Audit Items

### aapl_2014_10k Item 15

- Ticker: `AAPL`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `302976`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Part IV Item 15. Exhibits, Financial Statement Schedules`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `SIGNATURES`
- End evidence reasons: `TERMINAL_BOUNDARY`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, ITEM_15_TERMINAL_END_BOUNDARY_USED`
- Attempt warnings: `none`

Start snippet:

> Part IV Item 15. Exhibits, Financial Statement Schedules 85 Table of Contents This Annual Report on Form 10-K (“Form 10-K”) contains forward-looking statements, within the meaning of the Private Securities Litigation...

End snippet:

> ...601 of Regulation S-K The information required by this Section (a)(3) of Item 15 is set forth on the exhibit index that follows the Signatures page of this Form 10-K. Apple Inc. \| 2014 Form 10-K \| 85 Table of Contents

### aapl_2023_10k Item 6

- Ticker: `AAPL`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `52`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 6. [Reserved]`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 6. [Reserved] Apple Inc. \| 2023 Form 10-K \| 19

End snippet:

> Item 6. [Reserved] Apple Inc. \| 2023 Form 10-K \| 19

### aapl_2023_10k Item 9C

- Ticker: `AAPL`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `medium` `0.75`
- Text length: `180958`
- Warnings: `Start heading has TOC-like signals.`, `Section length is outside the expected first-pass range.`
- Start evidence: `Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `PART III Item 10. Directors, Executive Officers and Corporate Governance`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections 53 Part III Item 10. Directors, Executive Officers and Corporate Governance 53 Item 11. Executive Compensation 53 Item 12. Security Ownershi...

End snippet:

> ...ms’ plan will expire on December 15, 2024, subject to early termination for certain specified events set forth in the plans. Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections Not applicable.

### msft_2023_10k Item 6

- Ticker: `MSFT`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `23`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 6. [Reserved]`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`
- End evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 6. [Reserved] 39

End snippet:

> Item 6. [Reserved] 39

### jpm_2014_10k Item 1B

- Ticker: `JPM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `45`
- Warnings: `Start heading does not contain the expected canonical title.`
- Start evidence: `ITEM 1B: UNRESOLVED SEC STAFF COMMENTS`
- Start evidence reasons: `REGEX_ITEM_HEADING`
- End evidence: `ITEM 2: PROPERTIES`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.00 | 0.10 | False |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MISSING, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading does not contain the expected canonical title.`

Start snippet:

> ITEM 1B: UNRESOLVED SEC STAFF COMMENTS None.

End snippet:

> ITEM 1B: UNRESOLVED SEC STAFF COMMENTS None.

### jpm_2014_10k Item 3

- Ticker: `JPM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `99`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 3: LEGAL PROCEEDINGS`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `ITEM 4: MINE SAFETY DISCLOSURES`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 3: LEGAL PROCEEDINGS For a description of the Firm’s material legal proceedings, see Note 31.

End snippet:

> ITEM 3: LEGAL PROCEEDINGS For a description of the Firm’s material legal proceedings, see Note 31.

### jpm_2014_10k Item 7

- Ticker: `JPM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `395`
- Warnings: `Section length is outside the expected first-pass range.`, `Section appears to be a cross-reference rather than full narrative text.`
- Start evidence: `ITEM 7: MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`
- End evidence: `ITEM 7A: QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_user_confirmation` / `same_filing_page_reference`: Confirm whether to follow the referenced page range and attempt secondary extraction.
  Options: `extract_referenced_pages, accept_cross_reference_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |
| `not_cross_reference_only` | 0.00 | 0.00 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 7: MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS Management’s discussion and analysis of financial condition and results of operations, entitled “Management’s discussion an...

End snippet:

> ...ns, entitled “Management’s discussion and analysis,” appears on pages 64–169. Such information should be read in conjunction with the Consolidated Financial Statements and Notes thereto, which appear on pages 172–306.

### jpm_2014_10k Item 7A

- Ticker: `JPM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `253`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 7A: QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Part II ITEM 8: FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 7A: QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK For a discussion of the quantitative and qualitative disclosures about market risk, see the Market Risk Management section of Management’s discussion...

End snippet:

> ...IVE DISCLOSURES ABOUT MARKET RISK For a discussion of the quantitative and qualitative disclosures about market risk, see the Market Risk Management section of Management’s discussion and analysis on pages 131–136. 19

### jpm_2014_10k Item 8

- Ticker: `JPM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `551`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Part II ITEM 8: FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `ITEM 9: CHANGES IN AND DISAGREEMENTS WITH ACCOUNTANTS ON ACCOUNTING AND FINANCIAL DISCLOSURE`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Part II ITEM 8: FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA The Consolidated Financial Statements, together with the Notes thereto and the report thereon dated February 24, 2015, of PricewaterhouseCoopers LLP, the Fir...

End snippet:

> ...full quarter within the two years ended December 31, 2014, are included on pages 307–308 in the table entitled “Selected quarterly financial data (unaudited).” Also included is a “Glossary of terms’’ on pages 309–313.

### jpm_2014_10k Item 15

- Ticker: `JPM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `1274373`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Part IV Item 15 Exhibits, financial statement schedules`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `SIGNATURES`
- End evidence reasons: `TERMINAL_BOUNDARY`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, ITEM_15_TERMINAL_END_BOUNDARY_USED`
- Attempt warnings: `none`

Start snippet:

> Part IV Item 15 Exhibits, financial statement schedules 24–27 Part I ITEM 1: BUSINESS Overview JPMorgan Chase & Co.,(“JPMorgan Chase” or the “Firm”) a financial holding company incorporated under Delaware law in 1968,...

End snippet:

> ...than $100,000, and with maturities of 270 days or less. Other borrowed funds consist of demand notes, term federal funds purchased, and various other borrowings that generally have maturities of one year or less. 329

### jpm_2023_10k Item 6

- Ticker: `JPM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `21`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 6. Reserved`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`
- End evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations.`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 6. Reserved 35

End snippet:

> Item 6. Reserved 35

### jpm_2023_10k Item 7

- Ticker: `JPM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `396`
- Warnings: `Section length is outside the expected first-pass range.`, `Section appears to be a cross-reference rather than full narrative text.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations.`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`
- End evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk.`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_user_confirmation` / `same_filing_page_reference`: Confirm whether to follow the referenced page range and attempt secondary extraction.
  Options: `extract_referenced_pages, accept_cross_reference_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |
| `not_cross_reference_only` | 0.00 | 0.00 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations. Management’s discussion and analysis of financial condition and results of operations, entitled “Management’s discussion a...

End snippet:

> ...ns, entitled “Management’s discussion and analysis,” appears on pages 48–161. Such information should be read in conjunction with the Consolidated Financial Statements and Notes thereto, which appear on pages 166–309.

### jpm_2023_10k Item 7A

- Ticker: `JPM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `272`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk.`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 8. Financial Statements and Supplementary Data.`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7A. Quantitative and Qualitative Disclosures About Market Risk. Refer to the Market Risk Management section of Management’s discussion and analysis on pages 135–143 for a discussion of quantitative and qualitativ...

End snippet:

> ...out Market Risk. Refer to the Market Risk Management section of Management’s discussion and analysis on pages 135–143 for a discussion of quantitative and qualitative disclosures about market risk. 35 Parts II and III

### jpm_2023_10k Item 8

- Ticker: `JPM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `370`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 8. Financial Statements and Supplementary Data.`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 9. Changes in and Disagreements With Accountants on Accounting and Financial Disclosure.`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 8. Financial Statements and Supplementary Data. The Consolidated Financial Statements, together with the Notes thereto and the report thereon dated February 16, 2024, of PricewaterhouseCoopers LLP, the Firm’s ind...

End snippet:

> ...d February 16, 2024, of PricewaterhouseCoopers LLP, the Firm’s independent registered public accounting firm (PCAOB ID 238), appear on pages 163–309. The “Glossary of Terms and Acronyms’’ is included on pages 315-321.

### jpm_2023_10k Item 15

- Ticker: `JPM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `1246677`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Part IV Item 15. Exhibits, Financial Statement Schedules.`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `SIGNATURES`
- End evidence reasons: `TERMINAL_BOUNDARY`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, ITEM_15_TERMINAL_END_BOUNDARY_USED`
- Attempt warnings: `none`

Start snippet:

> Part IV Item 15. Exhibits, Financial Statement Schedules. 40-43 Part I Item 1. Business. Overview JPMorgan Chase & Co. (“JPMorgan Chase” or the “Firm”, NYSE: JPM), a financial holding company incorporated under Delawa...

End snippet:

> ...rum VIEs: Variable interest entities Warehouse loans: Consist of prime mortgages originated with the intent to sell that are accounted for at fair value and classified as loans. JPMorgan Chase & Co./2023 Form 10-K 321

### bac_2014_10k Item 7

- Ticker: `BAC`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `medium` `0.80`
- Text length: `578441`
- Warnings: `Start heading does not contain the expected canonical title.`, `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. Bank of America Corporation and Subsidiaries`
- Start evidence reasons: `REGEX_ITEM_HEADING`
- End evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_user_selection` / `internal_item_toc_detected`: Review likely internal Item 7 headings and choose the subsection to extract.
  Options: `Management’s Discussion and Analysis of Financial Condition and Results of Operation, Table of Contents, Executive Summary, Financial Highlights, Balance Sheet Overview, Supplemental Financial Data, Business Segment Operations, Consumer & Business Banking, Consumer Real Estate Services, Global Wealth & Investment Management, Global Banking, Global Markets`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.00 | 0.10 | False |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MISSING, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading does not contain the expected canonical title.`

Start snippet:

> Item 7. Bank of America Corporation and Subsidiaries Management’s Discussion and Analysis of Financial Condition and Results of Operation Table of Contents Page Executive Summary 23 Financial Highlights 25 Balance She...

End snippet:

> ...mortgage-backed securities SBLCs Standby letters of credit SEC Securities and Exchange Commission SLR Supplementary leverage ratio TDR Troubled debt restructurings VIE Variable interest entity 139 Bank of America 2014

### bac_2014_10k Item 7A

- Ticker: `BAC`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `218`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 8. Financial Statements and Supplementary Data`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7A. Quantitative and Qualitative Disclosures About Market Risk See Market Risk Management on page 99 in the MD&A and the sections referenced therein for Quantitative and Qualitative Disclosures about Market Risk.

End snippet:

> Item 7A. Quantitative and Qualitative Disclosures About Market Risk See Market Risk Management on page 99 in the MD&A and the sections referenced therein for Quantitative and Qualitative Disclosures about Market Risk.

### bac_2014_10k Item 8

- Ticker: `BAC`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `569098`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 8. Financial Statements and Supplementary Data`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 9. Changes in and Disagreements with Accountants on Accounting and Financial Disclosure`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 8. Financial Statements and Supplementary Data Table of Contents Page Consolidated Statement of Income 143 Consolidated Statement of Comprehensive Income 144 Consolidated Balance Sheet 145 Consolidated Statement...

End snippet:

> ...for any of the periods presented. (3) Substantially reflects the U.S. (4) Amounts include pretax gains of $753 million ($474 million net-of-tax) on the sale of common shares of CCB during 2013. Bank of America 2014264

### bac_2014_10k Item 15

- Ticker: `BAC`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `1286930`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Part IV Item 15. Exhibits, Financial Statement Schedules`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `SIGNATURES`
- End evidence reasons: `TERMINAL_BOUNDARY`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, ITEM_15_TERMINAL_END_BOUNDARY_USED`
- Attempt warnings: `none`

Start snippet:

> Part IV Item 15. Exhibits, Financial Statement Schedules 270 1 Bank of America 2014 Part I Bank of America Corporation and Subsidiaries Item 1. Business Bank of America Corporation (together, with its consolidated sub...

End snippet:

> ...-1 through E-4). With the exception of the information expressly incorporated herein by reference, the 2015 Proxy Statement shall not be deemed filed as part of this Annual Report on Form 10-K. Bank of America 2014270

### bac_2023_10k Item 6

- Ticker: `BAC`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `38`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 6. [Reserved]`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 7. Bank of America Corporation and Subsidiaries`
- End evidence reasons: `REGEX_ITEM_HEADING`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 6. [Reserved] 23 Bank of America

End snippet:

> Item 6. [Reserved] 23 Bank of America

### bac_2023_10k Item 7

- Ticker: `BAC`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `medium` `0.80`
- Text length: `308102`
- Warnings: `Start heading does not contain the expected canonical title.`, `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. Bank of America Corporation and Subsidiaries`
- Start evidence reasons: `REGEX_ITEM_HEADING`
- End evidence: `Item 7A. Quantitative and Qualitative Disclosures about Market Risk`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_user_selection` / `internal_item_toc_detected`: Review likely internal Item 7 headings and choose the subsection to extract.
  Options: `Management's Discussion and Analysis of Financial Condition and Results of Operations, Table of Contents, Executive Summary, Recent Developments, Financial Highlights, Balance Sheet Overview, Supplemental Financial Data, Business Segment Operations, Consumer Banking, Global Wealth & Investment Management, Global Banking, Global Markets`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.00 | 0.10 | False |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MISSING, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading does not contain the expected canonical title.`

Start snippet:

> Item 7. Bank of America Corporation and Subsidiaries Management's Discussion and Analysis of Financial Condition and Results of Operations Table of Contents Page Executive Summary 26 Recent Developments 26 Financial H...

End snippet:

> ...al measures to GAAP financial measures. For more information on non-GAAP financial measures and ratios we use in assessing the results of the Corporation, see Supplemental Financial Data on page 29. 85 Bank of America

### bac_2023_10k Item 7A

- Ticker: `BAC`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `218`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7A. Quantitative and Qualitative Disclosures about Market Risk`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 8. Financial Statements and Supplementary Data`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7A. Quantitative and Qualitative Disclosures about Market Risk See Market Risk Management on page 73 in the MD&A and the sections referenced therein for Quantitative and Qualitative Disclosures about Market Risk.

End snippet:

> Item 7A. Quantitative and Qualitative Disclosures about Market Risk See Market Risk Management on page 73 in the MD&A and the sections referenced therein for Quantitative and Qualitative Disclosures about Market Risk.

### bac_2023_10k Item 16

- Ticker: `BAC`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `903069`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 16. Form 10-K Summary`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `SIGNATURES`
- End evidence reasons: `TERMINAL_BOUNDARY`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, TERMINAL_END_BOUNDARY_USED`
- Attempt warnings: `none`

Start snippet:

> Item 16. Form 10-K Summary 178 1 Bank of America Part I Bank of America Corporation and Subsidiaries Item 1. Business Bank of America Corporation is a Delaware corporation, a bank holding company (BHC) and a financial...

End snippet:

> ...nge Act of 1934. (5)The instance document does not appear in the interactive data file because its XBRL tags are embedded within the inline XBRL document. Item 16. Form 10-K Summary Not applicable. Bank of America 178

### unh_2014_10k Item 2

- Ticker: `UNH`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `133299`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 2. Properties`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 3. LEGAL PROCEEDINGS`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 2. Properties 24 Item 3. Legal Proceedings 24 Item 4. Mine Safety Disclosures 24 Part II Item 5. Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities 24 Ite...

End snippet:

> ...arious reportable segments use these facilities for their respective business purposes, and we believe these current facilities are suitable for their respective uses and are adequate for our anticipated future needs.

### unh_2014_10k Item 7

- Ticker: `UNH`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `219335`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations 29 Item 7A. Quantitative and Qualitative Disclosures About Market Risk 47 Item 8. Financial Statements 48 Item 9. Changes i...

End snippet:

> ...nt that the amounts are deemed probable of recovery. Currently, the reinsurer is rated by A.M. Best as “A+.” As of December 31, 2014, there were no other significant concentrations of credit risk. 46 Table of Contents

### unh_2023_10k Item 2

- Ticker: `UNH`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `122323`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 2. Properties`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 4.MINE SAFETY DISCLOSURES`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 2. Properties 22 Item 3. Legal Proceedings 22 Item 4. Mine Safety Disclosures 22 Part II Item 5. Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities 22 Ite...

End snippet:

> ...captions “Legal Matters” and “Government Investigations, Audits and Reviews” in Note 12 of the Notes to the Consolidated Financial Statements included in Part II, Item 8, “Financial Statements and Supplementary Data”

### unh_2023_10k Item 3

- Ticker: `UNH`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `122298`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 3. Legal Proceedings`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 4.MINE SAFETY DISCLOSURES`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 3. Legal Proceedings 22 Item 4. Mine Safety Disclosures 22 Part II Item 5. Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities 22 Item 6. Reserved 23 Item...

End snippet:

> ...captions “Legal Matters” and “Government Investigations, Audits and Reviews” in Note 12 of the Notes to the Consolidated Financial Statements included in Part II, Item 8, “Financial Statements and Supplementary Data”

### unh_2023_10k Item 6

- Ticker: `UNH`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `165798`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 6. Reserved`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 6. Reserved 23 Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations 24 Item 7A. Quantitative and Qualitative Disclosures About Market Risk 33 Item 8. Financial Statements...

End snippet:

> ...respect to accounts receivable are limited due to the large number of employer groups and other customers constituting our client base. As of December 31, 2023, there were no significant concentrations of credit risk.

### unh_2023_10k Item 7

- Ticker: `UNH`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `165775`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations 24 Item 7A. Quantitative and Qualitative Disclosures About Market Risk 33 Item 8. Financial Statements and Supplementary Da...

End snippet:

> ...respect to accounts receivable are limited due to the large number of employer groups and other customers constituting our client base. As of December 31, 2023, there were no significant concentrations of credit risk.

### jnj_2014_10k Item 1A

- Ticker: `JNJ`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `546`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 1A. RISK FACTORS`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 1B. UNRESOLVED STAFF COMMENTS`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 1A. RISK FACTORS The Company faces a number of uncertainties and risks that are difficult to predict and many of which are outside of the Company's control. In addition to the other information in this Report and...

End snippet:

> ...t 99 to this Report on Form 10-K. Investors should realize that if known or unknown risks or uncertainties materialize, the Company’s business, results of operations or financial condition could be adversely affected.

### jnj_2014_10k Item 7

- Ticker: `JNJ`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `medium` `0.75`
- Text length: `386`
- Warnings: `Start heading has TOC-like signals.`, `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 7. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS The information called for by this item is incorporated herein by reference to the narrative and tabular material under the...

End snippet:

> ...ce to the narrative and tabular material under the caption “Management’s Discussion and Analysis of Results of Operations and Financial Condition” of the Annual Report, filed as Exhibit 13 to this Report on Form 10-K.

### jnj_2014_10k Item 7A

- Ticker: `JNJ`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `531`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK The information called for by this item is incorporated herein by reference to the material under the caption “Management’s Discussion and Analysis o...

End snippet:

> ...nd Market Risk” and Note 1 “Summary of Significant Accounting Policies — Financial Instruments” under “Notes to Consolidated Financial Statements” of the Annual Report, filed as Exhibit 13 to this Report on Form 10-K.

### jnj_2014_10k Item 8

- Ticker: `JNJ`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `360`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 9. CHANGES IN AND DISAGREEMENTS WITH ACCOUNTANTS ON ACCOUNTING AND FINANCIAL DISCLOSURE`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA The information called for by this item is incorporated herein by reference to the Audited Consolidated Financial Statements and Notes thereto and the material under...

End snippet:

> ...d Consolidated Financial Statements and Notes thereto and the material under the caption “Report of Independent Registered Public Accounting Firm” of the Annual Report, filed as Exhibit 13 to this Report on Form 10-K.

### jnj_2023_10k Item 6

- Ticker: `JNJ`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `40`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 6. Reserved`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 7. Management’s discussion and analysis of results of operations and financial condition`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 6. Reserved 2023 Annual Report 21

End snippet:

> Item 6. Reserved 2023 Annual Report 21

### jnj_2023_10k Item 7A

- Ticker: `JNJ`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `486`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7A. Quantitative and qualitative disclosures about market risk`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 8. Financial statements and supplementary data`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7A. Quantitative and qualitative disclosures about market risk The information called for by this item is incorporated herein by reference to Item 7. Management’s discussion and analysis of results of operations...

End snippet:

> ...sources - Financing and market risk of this Report; and Note 1 Summary of significant accounting policies - Financial instruments of the Notes to Consolidated Financial Statements included in Item 8 of this Report. 42

### xom_2014_10k Item 7

- Ticker: `XOM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `265`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations Reference is made to the section entitled “Management’s Discussion and Analysis of Financial Condition and Results of Opera...

End snippet:

> ...Financial Condition and Results of Operations Reference is made to the section entitled “Management’s Discussion and Analysis of Financial Condition and Results of Operations” in the Financial Section of this report.

### xom_2014_10k Item 7A

- Ticker: `XOM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `510`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`
- End evidence: `Item 8. Financial Statements and Supplementary Data`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7A. Quantitative and Qualitative Disclosures About Market Risk Reference is made to the section entitled “Market Risks, Inflation and Other Uncertainties”, excluding the part entitled “Inflation and Other Uncerta...

End snippet:

> ...n historical information incorporated in this Item 7A are forward-looking statements. The actual impact of future market changes could differ materially due to, among other things, factors discussed in this report. 30

### xom_2014_10k Item 8

- Ticker: `XOM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `780`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 8. Financial Statements and Supplementary Data`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 9. Changes in and Disagreements With Accountants on Accounting and Financial Disclosure`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 8. Financial Statements and Supplementary Data Reference is made to the following in the Financial Section of this report: · Consolidated financial statements, together with the report thereon of PricewaterhouseC...

End snippet:

> ...nd · “Frequently Used Terms” (unaudited). Financial Statement Schedules have been omitted because they are not applicable or the required information is shown in the consolidated financial statements or notes thereto.

### xom_2023_10k Item 7

- Ticker: `XOM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `265`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`
- End evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS Reference is made to the section entitled “Management’s Discussion and Analysis of Financial Condition and Results of Opera...

End snippet:

> ...FINANCIAL CONDITION AND RESULTS OF OPERATIONS Reference is made to the section entitled “Management’s Discussion and Analysis of Financial Condition and Results of Operations” in the Financial Section of this report.

### xom_2023_10k Item 7A

- Ticker: `XOM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `411`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`
- End evidence: `ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK Reference is made to the section entitled “Market Risks” in the Financial Section of this report. All statements, other than historical information i...

End snippet:

> ...historical information incorporated in this Item 7A, are forward-looking statements. The actual impact of future market changes could differ materially due to, among other things, factors discussed in this report. 30

### xom_2023_10k Item 8

- Ticker: `XOM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `737`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `ITEM 9. CHANGES IN AND DISAGREEMENTS WITH ACCOUNTANTS ON ACCOUNTING AND FINANCIAL DISCLOSURE`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA Reference is made to the following in the Financial Section of this report: •Consolidated financial statements, together with the report thereon of PricewaterhouseCo...

End snippet:

> ...and •“Frequently Used Terms” (unaudited). Financial Statement Schedules have been omitted because they are not applicable or the required information is shown in the consolidated financial statements or notes thereto.

### cvx_2014_10k Item 7

- Ticker: `CVX`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `278`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`
- End evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations The index to Management’s Discussion and Analysis of Financial Condition and Results of Operations, Consolidated Financial...

End snippet:

> ...ndition and Results of Operations The index to Management’s Discussion and Analysis of Financial Condition and Results of Operations, Consolidated Financial Statements and Supplementary Data is presented on page FS-1.

### cvx_2014_10k Item 7A

- Ticker: `CVX`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `451`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 8. Financial Statements and Supplementary Data`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7A. Quantitative and Qualitative Disclosures About Market Risk The company’s discussion of interest rate, foreign currency and commodity price market risk is contained in Management’s Discussion and Analysis of F...

End snippet:

> ...on and Results of Operations — “Financial and Derivative Instrument Market Risk,” on page FS-15 and in Note 10 to the Consolidated Financial Statements, “Financial and Derivative Instruments,” beginning on page FS-35.

### cvx_2014_10k Item 8

- Ticker: `CVX`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `187`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 8. Financial Statements and Supplementary Data`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `Item 9. Changes in and Disagreements With Accountants on Accounting and Financial Disclosure`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 8. Financial Statements and Supplementary Data The index to Management’s Discussion and Analysis, Consolidated Financial Statements and Supplementary Data is presented on page FS-1.

End snippet:

> Item 8. Financial Statements and Supplementary Data The index to Management’s Discussion and Analysis, Consolidated Financial Statements and Supplementary Data is presented on page FS-1.

### cvx_2023_10k Item 6

- Ticker: `CVX`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `262`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 6. [Reserved]`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 6. [Reserved] Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations The index to Management’s Discussion and Analysis of Financial Condition and Results of Operations is pr...

End snippet:

> ...cussion and Analysis of Financial Condition and Results of Operations The index to Management’s Discussion and Analysis of Financial Condition and Results of Operations is presented in the Financial Table of Contents.

### cvx_2023_10k Item 7

- Ticker: `CVX`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `medium` `0.75`
- Text length: `242`
- Warnings: `Start heading has TOC-like signals.`, `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations The index to Management’s Discussion and Analysis of Financial Condition and Results of Operations is presented in the Fina...

End snippet:

> ...cussion and Analysis of Financial Condition and Results of Operations The index to Management’s Discussion and Analysis of Financial Condition and Results of Operations is presented in the Financial Table of Contents.

### cvx_2023_10k Item 7A

- Ticker: `CVX`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `354`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 8. Financial Statements and Supplementary Data`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 7A. Quantitative and Qualitative Disclosures About Market Risk The company’s discussion of interest rate, foreign currency and commodity price market risk is contained in Management’s Discussion and Analysis of F...

End snippet:

> ...odity price market risk is contained in Management’s Discussion and Analysis of Financial Condition and Results of Operations — Financial and Derivative Instruments and in Note 10 Financial and Derivative Instruments.

### cvx_2023_10k Item 8

- Ticker: `CVX`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `158`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 8. Financial Statements and Supplementary Data`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 9. Changes in and Disagreements With Accountants on Accounting and Financial Disclosure`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 8. Financial Statements and Supplementary Data The index to Financial Statements and Supplementary Data is presented in the Financial Table of Contents.

End snippet:

> Item 8. Financial Statements and Supplementary Data The index to Financial Statements and Supplementary Data is presented in the Financial Table of Contents.

### cvx_2023_10k Item 14

- Ticker: `CVX`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `313143`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 14. Principal Accountant Fees and Services`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `PART IV Item 15. Exhibit and Financial Statement Schedules`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 14. Principal Accountant Fees and Services The information required by Item 9(e) of Schedule 14A and contained under the heading “Board Proposal to Ratify PricewaterhouseCoopers LLP as the Independent Registered...

End snippet:

> ...cretion of discount 23,306 5,722 29,028 Net change in income tax 30,070 7,142 37,212 Net Change for 2023 (51,715) (15,215) (66,930) Present Value at December 31, 2023 $ 118,757 $ 26,251 $ 145,008 114 Table of Contents

### wmt_2014_10k Item 7

- Ticker: `WMT`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `413`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS The information required by this item is incorporated by reference to all information under the caption "Management's Discu...

End snippet:

> ...ion "Management's Discussion and Analysis of Financial Condition and Results of Operations" included in our Annual Report to Shareholders. Such information is included in Exhibit 13 to this Annual Report on Form 10-K.

### wmt_2014_10k Item 7A

- Ticker: `WMT`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `423`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK The information required by this item is incorporated by reference to all information under the sub-caption "Market Risk" under the caption "Manageme...

End snippet:

> ...ion "Management's Discussion and Analysis of Financial Condition and Results of Operations" included in our Annual Report to Shareholders. Such information is included in Exhibit 13 to this Annual Report on Form 10-K.

### wmt_2014_10k Item 8

- Ticker: `WMT`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `606`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `ITEM 9. CHANGES IN AND DISAGREEMENTS WITH ACCOUNTANTS ON ACCOUNTING AND FINANCIAL DISCLOSURE`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `needs_external_source` / `external_or_other_document_reference`: Short section likely requires a referenced annual report, exhibit, proxy, or other source document.
  Options: `fetch_referenced_document, upload_reference_document, accept_short_text`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA The information required by this item is incorporated by reference to all information under the captions "Consolidated Statements of Income," "Consolidated Statement...

End snippet:

> ...ated Financial Statements" and "Report of Independent Registered Public Accounting Firm" included in our Annual Report to Shareholders. Such information is included in Exhibit 13 to this Annual Report on Form 10-K. 28

### wmt_2023_10k Item 6

- Ticker: `WMT`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `21`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `ITEM 6. RESERVED`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
- End evidence: `ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> ITEM 6. RESERVED 34

End snippet:

> ITEM 6. RESERVED 34

### amzn_2014_10k Item 2

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `1253`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 2. Properties`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 4. Mine Safety Disclosures`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 2. Properties As of December 31, 2014, we operated the following facilities (in thousands): Description of Use Square Footage (1) Location Lease Expirations Owned office space 1,802 North America Leased office sp...

End snippet:

> ...other facilities, principally in North America, Europe, and Asia. Item 3. Legal Proceedings See Item 8 of Part II, “Financial Statements and Supplementary Data—Note 8—Commitments and Contingencies—Legal Proceedings.”

### amzn_2014_10k Item 3

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `152`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 3. Legal Proceedings`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 4. Mine Safety Disclosures`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 3. Legal Proceedings See Item 8 of Part II, “Financial Statements and Supplementary Data—Note 8—Commitments and Contingencies—Legal Proceedings.”

End snippet:

> Item 3. Legal Proceedings See Item 8 of Part II, “Financial Statements and Supplementary Data—Note 8—Commitments and Contingencies—Legal Proceedings.”

### amzn_2014_10k Item 6

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `2423`
- Warnings: `Start heading does not contain the expected canonical title.`
- Start evidence: `Item 6. Selected Consolidated Financial Data`
- Start evidence reasons: `REGEX_ITEM_HEADING, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.00 | 0.10 | False |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MISSING, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading does not contain the expected canonical title.`

Start snippet:

> Item 6. Selected Consolidated Financial Data The following selected consolidated financial data should be read in conjunction with the consolidated financial statements and the notes thereto in Item 8 of Part II, “Fin...

End snippet:

> ...scussion and Analysis of Financial Condition and Results of Operations—Results of Operations—Non-GAAP Financial Measures” for additional information as well as alternative free cash flow measures. 17 Table of Contents

### amzn_2014_10k Item 9A

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `7010`
- Warnings: `End heading has TOC-like signals.`
- Start evidence: `Item 9A. Controls and Procedures`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 9B. Other Information`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.00 | 0.10 | False |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_TOC_LIKE_USED_AS_FALLBACK`
- Attempt warnings: `End heading has TOC-like signals.`

Start snippet:

> Item 9A. Controls and Procedures Evaluation of Disclosure Controls and Procedures We carried out an evaluation required by the Securities Exchange Act of 1934 (the “1934 Act”), under the supervision and with the parti...

End snippet:

> ...in the period ended December 31, 2014 of Amazon.com, Inc. and our report dated January 29, 2015 expressed an unqualified opinion thereon. /s/ Ernst & Young LLP Seattle, Washington January 29, 2015 73 Table of Contents

### amzn_2014_10k Item 9B

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `medium` `0.75`
- Text length: `34`
- Warnings: `Start heading has TOC-like signals.`, `End heading has TOC-like signals.`
- Start evidence: `Item 9B. Other Information`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `PART III Item 10. Directors, Executive Officers, and Corporate Governance`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.00 | 0.10 | False |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_TOC_LIKE_USED_AS_FALLBACK`
- Attempt warnings: `Start heading has TOC-like signals., End heading has TOC-like signals.`

Start snippet:

> Item 9B. Other Information None.

End snippet:

> Item 9B. Other Information None.

### amzn_2014_10k Item 10

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `1545`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `PART III Item 10. Directors, Executive Officers, and Corporate Governance`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 13. Certain Relationships and Related Transactions, and Director Independence`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> PART III Item 10. Directors, Executive Officers, and Corporate Governance Information regarding our Executive Officers required by Item 10 of Part III is set forth in Item 1 of Part I “Business—Executive Officers of t...

End snippet:

> ...nd Management and Related Shareholder Matters Information required by Item 12 of Part III is included in our Proxy Statement relating to our 2015 Annual Meeting of Shareholders and is incorporated herein by reference.

### amzn_2014_10k Item 11

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `484`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 11. Executive Compensation`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 13. Certain Relationships and Related Transactions, and Director Independence`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 11. Executive Compensation Information required by Item 11 of Part III is included in our Proxy Statement relating to our 2015 Annual Meeting of Shareholders and is incorporated herein by reference. Item 12. Secu...

End snippet:

> ...nd Management and Related Shareholder Matters Information required by Item 12 of Part III is included in our Proxy Statement relating to our 2015 Annual Meeting of Shareholders and is incorporated herein by reference.

### amzn_2014_10k Item 12

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `277`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder Matters`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 13. Certain Relationships and Related Transactions, and Director Independence`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder Matters Information required by Item 12 of Part III is included in our Proxy Statement relating to our 2015 Annual Meetin...

End snippet:

> ...nd Management and Related Shareholder Matters Information required by Item 12 of Part III is included in our Proxy Statement relating to our 2015 Annual Meeting of Shareholders and is incorporated herein by reference.

### amzn_2023_10k Item 2

- Ticker: `AMZN`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `79315`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 2. Properties`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 4. Mine Safety Disclosures`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 2. Properties 18 Item 3. Legal Proceedings 18 Item 4. Mine Safety Disclosures 18 PART II Item 5. Market for the Registrant’s Common Stock, Related Shareholder Matters, and Issuer Purchases of Equity Securities 19...

End snippet:

> ...in Washington’s Puget Sound region and Arlington, Virginia. Item 3. Legal Proceedings See Item 8 of Part II, “Financial Statements and Supplementary Data — Note 7 — Commitments and Contingencies — Legal Proceedings.”

### amzn_2023_10k Item 3

- Ticker: `AMZN`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `79290`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 3. Legal Proceedings`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 4. Mine Safety Disclosures`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 3. Legal Proceedings 18 Item 4. Mine Safety Disclosures 18 PART II Item 5. Market for the Registrant’s Common Stock, Related Shareholder Matters, and Issuer Purchases of Equity Securities 19 Item 6. Reserved 19 I...

End snippet:

> ...in Washington’s Puget Sound region and Arlington, Virginia. Item 3. Legal Proceedings See Item 8 of Part II, “Financial Statements and Supplementary Data — Note 7 — Commitments and Contingencies — Legal Proceedings.”

### amzn_2023_10k Item 6

- Ticker: `AMZN`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `40`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 6. Reserved`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.15 | 0.15 | True |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `none`

Start snippet:

> Item 6. Reserved 19 Table of Contents

End snippet:

> Item 6. Reserved 19 Table of Contents

### amzn_2023_10k Item 9C

- Ticker: `AMZN`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `medium` `0.75`
- Text length: `268364`
- Warnings: `Start heading has TOC-like signals.`, `Section length is outside the expected first-pass range.`
- Start evidence: `Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `PART III Item 10. Directors, Executive Officers, and Corporate Governance`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.00 | 0.10 | False |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections 73 PART III Item 10. Directors, Executive Officers, and Corporate Governance 73 Item 11. Executive Compensation 73 Item 12. Security Ownersh...

End snippet:

> ...ll up to 5,760 shares of Amazon.com, Inc. common stock over a period ending on March 8, 2024, subject to certain conditions. Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections Not applicable.

### amzn_2023_10k Item 13

- Ticker: `AMZN`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `256`
- Warnings: `Start heading has TOC-like signals.`
- Start evidence: `Item 13. Certain Relationships and Related Transactions, and Director Independence`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 14. Principal Accountant Fees and Services`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.

Confidence components:

| Component | Earned | Weight | Passed |
| --- | ---: | ---: | --- |
| `legal_boundary_pair` | 0.55 | 0.55 | True |
| `start_not_toc_like` | 0.00 | 0.15 | False |
| `end_not_toc_like` | 0.10 | 0.10 | True |
| `start_expected_title` | 0.10 | 0.10 | True |
| `section_length_reasonable` | 0.10 | 0.10 | True |

Selected candidate attempt:

- Validation reasons: `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE`
- Attempt warnings: `Start heading has TOC-like signals.`

Start snippet:

> Item 13. Certain Relationships and Related Transactions, and Director Independence Information required by Item 13 of Part III is included in our Proxy Statement relating to our 2024 Annual Meeting of Shareholders and...

End snippet:

> ...lated Transactions, and Director Independence Information required by Item 13 of Part III is included in our Proxy Statement relating to our 2024 Annual Meeting of Shareholders and is incorporated herein by reference.

## Rejected Candidate Pairs

### aapl_2023_10k Item 9C

- Ticker: `AAPL`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `medium` `0.75`
- Final start evidence: `Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections` | `PART III Item 10. Directors, Executive Officers and Corporate Governance` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### msft_2023_10k Item 3

- Ticker: `MSFT`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `ITEM 3. LEGAL PROCEEDINGS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 3. Legal Proceedings` | `Item 4. Mine Safety Disclosures` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### msft_2023_10k Item 11

- Ticker: `MSFT`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `ITEM 11. EXECUTIVE COMPENSATION`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 11. Executive Compensation` | `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Stockholder M...` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### msft_2023_10k Item 12

- Ticker: `MSFT`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `ITEM 12. SECURITY OWNERSHIP OF CERTAIN BENEFICIAL OWNERS AND MANAGEMENT AND RELATED STOCKHOLDER MATTERS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Stockholder M...` | `Item 13. Certain Relationships and Related Transactions, and Director Independence` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### msft_2023_10k Item 13

- Ticker: `MSFT`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `ITEM 13. CERTAIN RELATIONSHIPS AND RELATED TRANSACTIONS, AND DIRECTOR INDEPENDENCE`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 13. Certain Relationships and Related Transactions, and Director Independence` | `Item 14. Principal Accountant Fees and Services` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2014_10k Item 6

- Ticker: `JPM`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `ITEM 6: SELECTED FINANCIAL DATA`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 6 Selected financial data` | `Item 7 Management’s discussion and analysis of financial condition and results of operations` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2014_10k Item 7

- Ticker: `JPM`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.90`
- Final start evidence: `ITEM 7: MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 7 Management’s discussion and analysis of financial condition and results of operations` | `Item 7A Quantitative and qualitative disclosures about market risk` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2014_10k Item 11

- Ticker: `JPM`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `ITEM 11: EXECUTIVE COMPENSATION`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 11 Executive compensation` | `Item 12 Security ownership of certain beneficial owners and management and related stockholder ma...` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2023_10k Item 7

- Ticker: `JPM`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `0.90`
- Final start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations.`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations.` | `Item 7A. Quantitative and Qualitative Disclosures About Market Risk.` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2023_10k Item 11

- Ticker: `JPM`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Item 11. Executive Compensation.`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 11. Executive Compensation.` | `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Stockholder M...` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### unh_2014_10k Item 2

- Ticker: `UNH`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.85`
- Final start evidence: `Item 2. Properties`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `ITEM 2. PROPERTIES` | `ITEM 3. LEGAL PROCEEDINGS` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 1B

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Item 1B. Unresolved Staff Comments`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 1B. Unresolved Staff Comments` | `Item 2. Properties` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 2

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.85`
- Final start evidence: `Item 2. Properties`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 2. Properties` | `Item 3. Legal Proceedings` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 3

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.85`
- Final start evidence: `Item 3. Legal Proceedings`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 3. Legal Proceedings` | `Item 4. Mine Safety Disclosures` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 9B

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `medium` `0.75`
- Final start evidence: `Item 9B. Other Information`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 9B. Other Information` | `PART III Item 10. Directors, Executive Officers, and Corporate Governance` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 10

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.85`
- Final start evidence: `PART III Item 10. Directors, Executive Officers, and Corporate Governance`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `PART III Item 10. Directors, Executive Officers, and Corporate Governance` | `Item 11. Executive Compensation` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 11

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.85`
- Final start evidence: `Item 11. Executive Compensation`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 11. Executive Compensation` | `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder M...` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 12

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.85`
- Final start evidence: `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder Matters`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder M...` | `Item 13. Certain Relationships and Related Transactions, and Director Independence` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2023_10k Item 9C

- Ticker: `AMZN`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `medium` `0.75`
- Final start evidence: `Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections` | `PART III Item 10. Directors, Executive Officers, and Corporate Governance` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2023_10k Item 13

- Ticker: `AMZN`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `0.85`
- Final start evidence: `Item 13. Certain Relationships and Related Transactions, and Director Independence`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 13. Certain Relationships and Related Transactions, and Director Independence` | `Item 16. Form 10-K Summary` | `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Start heading has TOC-like signals., Candidate pair is too short and follows an ordered TOC-like transition.` |
