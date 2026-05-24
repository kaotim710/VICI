# Warning Audit Report

Generated: 2026-05-24

Scope: seed 10-K filings with non-empty item warnings.

Warning items: 12
Items with rejected candidate pairs: 18
Missing filings: 0

## Warning Counts

| Warning | Count |
| --- | ---: |
| `End heading has TOC-like signals.` | 2 |
| `Start heading has TOC-like signals.` | 10 |

## Warning Category Counts

| Category | Count |
| --- | ---: |
| `toc_signal_review` | 12 |

## Audit Items

### unh_2014_10k Item 2

- Ticker: `UNH`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `133299`
- Warnings: `Start heading has TOC-like signals.`
- Warning categories: `toc_signal_review`
- Start evidence: `Item 2. Properties`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 3. LEGAL PROCEEDINGS`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`
- `inspect_only` / `exhibit_index_detected`: Review the exhibit-related text or table captured inside this section.
  Options: `inspect_exhibit_index, accept_current_section`

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
- Warning categories: `toc_signal_review`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`
- `inspect_only` / `exhibit_index_detected`: Review the exhibit-related text or table captured inside this section.
  Options: `inspect_exhibit_index, accept_current_section`

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
- Warning categories: `toc_signal_review`
- Start evidence: `Item 2. Properties`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 4.MINE SAFETY DISCLOSURES`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`
- `inspect_only` / `exhibit_index_detected`: Review the exhibit-related text or table captured inside this section.
  Options: `inspect_exhibit_index, accept_current_section`

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
- Warning categories: `toc_signal_review`
- Start evidence: `Item 3. Legal Proceedings`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 4.MINE SAFETY DISCLOSURES`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`
- `inspect_only` / `exhibit_index_detected`: Review the exhibit-related text or table captured inside this section.
  Options: `inspect_exhibit_index, accept_current_section`

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
- Warning categories: `toc_signal_review`
- Start evidence: `Item 6. Reserved`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`
- `inspect_only` / `exhibit_index_detected`: Review the exhibit-related text or table captured inside this section.
  Options: `inspect_exhibit_index, accept_current_section`

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
- Warning categories: `toc_signal_review`
- Start evidence: `Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`
- `inspect_only` / `exhibit_index_detected`: Review the exhibit-related text or table captured inside this section.
  Options: `inspect_exhibit_index, accept_current_section`

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

### amzn_2014_10k Item 2

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `1253`
- Warnings: `Start heading has TOC-like signals.`
- Warning categories: `toc_signal_review`
- Start evidence: `Item 2. Properties`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 4. Mine Safety Disclosures`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`

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

### amzn_2014_10k Item 9A

- Ticker: `AMZN`
- Fiscal year: `2014`
- Overall status: `success`
- Confidence: `high` `0.90`
- Text length: `7010`
- Warnings: `End heading has TOC-like signals.`
- Warning categories: `toc_signal_review`
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
- Confidence: `high` `0.90`
- Text length: `34`
- Warnings: `End heading has TOC-like signals.`
- Warning categories: `toc_signal_review`
- Start evidence: `Item 9B. Other Information`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `PART III Item 10. Directors, Executive Officers, and Corporate Governance`
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
- Warning categories: `toc_signal_review`
- Start evidence: `PART III Item 10. Directors, Executive Officers, and Corporate Governance`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 13. Certain Relationships and Related Transactions, and Director Independence`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`

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

### amzn_2023_10k Item 2

- Ticker: `AMZN`
- Fiscal year: `2023`
- Overall status: `success`
- Confidence: `high` `0.85`
- Text length: `79315`
- Warnings: `Start heading has TOC-like signals.`
- Warning categories: `toc_signal_review`
- Start evidence: `Item 2. Properties`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 4. Mine Safety Disclosures`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`
- `inspect_only` / `exhibit_index_detected`: Review the exhibit-related text or table captured inside this section.
  Options: `inspect_exhibit_index, accept_current_section`

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
- Warning categories: `toc_signal_review`
- Start evidence: `Item 3. Legal Proceedings`
- Start evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, TOC_DENSE_ITEM_CLUSTER, NEAR_TABLE_OF_CONTENTS_LABEL`
- End evidence: `Item 4. Mine Safety Disclosures`
- End evidence reasons: `REGEX_ITEM_HEADING, EXPECTED_TITLE_MATCH, NEAR_TABLE_OF_CONTENTS_LABEL`

Recommended actions:

- `inspect_only` / `start_toc_like_signal`: Inspect start evidence; extraction is retained because the selected span is not a rejected TOC pair.
- `inspect_only` / `section_reference_detected`: Review detected reference language before deciding whether to follow another section, exhibit, proxy, or annual report.
  Options: `inspect_references, accept_current_section`
- `inspect_only` / `exhibit_index_detected`: Review the exhibit-related text or table captured inside this section.
  Options: `inspect_exhibit_index, accept_current_section`

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

## Rejected Candidate Pairs

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
- Final confidence: `high` `1.00`
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
- Final confidence: `high` `1.00`
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
- Final confidence: `high` `1.00`
- Final start evidence: `Item 3. Legal Proceedings`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 3. Legal Proceedings` | `Item 4. Mine Safety Disclosures` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 9B

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `0.90`
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
- Final confidence: `high` `1.00`
- Final start evidence: `Item 11. Executive Compensation`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 11. Executive Compensation` | `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder M...` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2014_10k Item 12

- Ticker: `AMZN`
- Fiscal year: `2014`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder Matters`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder M...` | `Item 13. Certain Relationships and Related Transactions, and Director Independence` | `START_HEADING_FOUND, START_NOT_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Candidate pair is too short and follows an ordered TOC-like transition.` |

### amzn_2023_10k Item 13

- Ticker: `AMZN`
- Fiscal year: `2023`
- Final status: `success`
- Final confidence: `high` `1.00`
- Final start evidence: `Item 13. Certain Relationships and Related Transactions, and Director Independence`

| Decision | Start Evidence | End Evidence | Reasons | Warnings |
| --- | --- | --- | --- | --- |
| rejected | `Item 13. Certain Relationships and Related Transactions, and Director Independence` | `Item 16. Form 10-K Summary` | `START_HEADING_FOUND, START_TOC_LIKE, START_EXPECTED_TITLE_MATCH, LEGAL_END_HEADING_FOUND, END_NOT_TOC_LIKE, REJECTED_SHORT_ORDERED_TOC_SPAN` | `Start heading has TOC-like signals., Candidate pair is too short and follows an ordered TOC-like transition.` |
