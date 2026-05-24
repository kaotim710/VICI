# Warning Audit Report

Generated: 2026-05-24

Scope: seed 10-K filings with non-empty item warnings.

Warning items: 13
Items with rejected candidate pairs: 12
Missing filings: 0

## Warning Counts

| Warning | Count |
| --- | ---: |
| `Section appears to be a cross-reference rather than full narrative text.` | 2 |
| `Section length is outside the expected first-pass range.` | 11 |
| `Start heading does not contain the expected canonical title.` | 2 |
| `Start heading has TOC-like signals.` | 2 |

## Audit Items

### jpm_2014_10k Item 7

- Ticker: `JPM`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `395`
- Warnings: `Section length is outside the expected first-pass range.`, `Section appears to be a cross-reference rather than full narrative text.`
- Start evidence: `ITEM 7: MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
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

### jpm_2023_10k Item 7

- Ticker: `JPM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `396`
- Warnings: `Section length is outside the expected first-pass range.`, `Section appears to be a cross-reference rather than full narrative text.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations.`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
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
- Confidence: `high` `0.90`
- Text length: `386`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
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

> Item 7. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS The information called for by this item is incorporated herein by reference to the narrative and tabular material under the...

End snippet:

> ...ce to the narrative and tabular material under the caption “Management’s Discussion and Analysis of Results of Operations and Financial Condition” of the Annual Report, filed as Exhibit 13 to this Report on Form 10-K.

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

> Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations Reference is made to the section entitled “Management’s Discussion and Analysis of Financial Condition and Results of Opera...

End snippet:

> ...Financial Condition and Results of Operations Reference is made to the section entitled “Management’s Discussion and Analysis of Financial Condition and Results of Operations” in the Financial Section of this report.

### xom_2023_10k Item 7

- Ticker: `XOM`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `265`
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

> ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS Reference is made to the section entitled “Management’s Discussion and Analysis of Financial Condition and Results of Opera...

End snippet:

> ...FINANCIAL CONDITION AND RESULTS OF OPERATIONS Reference is made to the section entitled “Management’s Discussion and Analysis of Financial Condition and Results of Operations” in the Financial Section of this report.

### cvx_2014_10k Item 7

- Ticker: `CVX`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `278`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`
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

### cvx_2023_10k Item 7

- Ticker: `CVX`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `242`
- Warnings: `Section length is outside the expected first-pass range.`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 7A. Quantitative and Qualitative Disclosures About Market Risk`
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

> Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations The index to Management’s Discussion and Analysis of Financial Condition and Results of Operations is presented in the Fina...

End snippet:

> ...cussion and Analysis of Financial Condition and Results of Operations The index to Management’s Discussion and Analysis of Financial Condition and Results of Operations is presented in the Financial Table of Contents.

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

## Rejected Candidate Pairs

### msft_2023_10k Item 1

- Ticker: `MSFT`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `ITEM 1. BUSINESS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `PART I Item 1. Business` | `Item 1A. Risk Factors` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### msft_2023_10k Item 1A

- Ticker: `MSFT`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `PART I Item 1A ITEM 1A. RISK FACTORS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 1A. Risk Factors` | `Item 1B. Unresolved Staff Comments` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### msft_2023_10k Item 7

- Ticker: `MSFT`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `PART II Item 7 ITEM 7. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations` | `Item 7A. Quantitative and Qualitative Disclosures about Market Risk` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2014_10k Item 1

- Ticker: `JPM`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Part I ITEM 1: BUSINESS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 1 Business` | `Item 1A Risk factors` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2014_10k Item 1A

- Ticker: `JPM`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Part I Item 1A: RISK FACTORS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 1A Risk factors` | `Item 1B Unresolved SEC Staff comments` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2014_10k Item 7

- Ticker: `JPM`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.90`
- Final start evidence: `ITEM 7: MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 7 Management’s discussion and analysis of financial condition and results of operations` | `Item 7A Quantitative and qualitative disclosures about market risk` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2023_10k Item 1

- Ticker: `JPM`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Part I Item 1. Business.`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 1. Business.` | `Item 1A. Risk Factors.` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2023_10k Item 1A

- Ticker: `JPM`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Item 1A. Risk Factors.`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 1A. Risk Factors.` | `Item 1B. Unresolved Staff Comments.` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### jpm_2023_10k Item 7

- Ticker: `JPM`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `0.90`
- Final start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations.`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations.` | `Item 7A. Quantitative and Qualitative Disclosures About Market Risk.` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 1

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `PART I Item 1. Business`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `PART I Item 1. Business` | `Item 1A. Risk Factors` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 1A

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Item 1A. Risk Factors`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 1A. Risk Factors` | `Item 1B. Unresolved Staff Comments` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 7

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operation` | `Item 7A. Quantitative and Qualitative Disclosure About Market Risk` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |
