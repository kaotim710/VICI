# Upload Regression Review

Date: 2026-05-25

Files reviewed:

- `/Users/ltkao/Downloads/intc.htm`
- `/Users/ltkao/Downloads/citi.htm`

## Issue Observed

- INTC: item extraction silently selected Form 10-K cross-reference index rows as if they were body item sections.
- Citi: upload extraction completed with zero item candidates because the filing splits item number, title, and page range into separate table cells and uses non-`Item N` body headings.

## Strategy Change

- Detect `FORM 10-K CROSS-REFERENCE INDEX`.
- Treat cross-reference rows as retrieval evidence, not body section starts.
- Build virtual item starts from the row's first page reference and printed page markers.
- Support split cells such as `1.` / `Business` / `4-36`.
- Keep selected starts inspectable through `CROSS_REFERENCE_PAGE_FALLBACK`.

## Post-Fix Smoke Results

### INTC

- Status: `success`
- Candidate count: `38`
- Warning count: `11`
- Key fix: Item 1 now starts at body `Overview`, not the cross-reference index row.
- Notable remaining limitation: some sections are long because the filing maps legal items to non-contiguous narrative ranges.

Selected items:

| Item | Status | Length | Start | End |
| --- | ---: | ---: | --- | --- |
| 1 | success | 44,460 | Item 1. Business: General development of business | Item 2. Properties |
| 1A | success | 104,465 | Item 1A. Risk Factors | Item 1C. Cybersecurity |
| 7 | success | 16,134 | Item 7. Management's Discussion and Analysis... | Item 7A. Quantitative and Qualitative... |
| 8 | success | 208,238 | Item 8. Financial Statements and Supplementary Data | Item 9A. Controls and Procedures |
| 15 | success | 229,110 | Item 15. Exhibits and Financial Statement Schedules | Item 16. Form 10-K Summary |

### Citi

- Status: `partial`
- Candidate count: `11`
- Warning count: `6`
- Key fix: candidate count changed from `0` to `11`; Item 1, 1A, 7, 7A, 8, and 15 now extract.
- Notable remaining limitation: items that are `Not Applicable`, proxy-incorporated, or cross-reference-only may still be `not_present` or `failed` until a dedicated non-contiguous/page-range result model is added.

Selected items:

| Item | Status | Length | Start | End |
| --- | ---: | ---: | --- | --- |
| 1 | success | 150,249 | Item 1. Business | Item 1A. Risk Factors |
| 1A | success | 37,818 | Item 1A. Risk Factors | Item 1C. Cybersecurity |
| 7 | success | 225,913 | Item 7. Management's Discussion and Analysis... | Item 7A. Quantitative and Qualitative... |
| 8 | success | 608,103 | Item 8. Financial Statements and Supplementary Data | Item 9B. Other Information |
| 15 | success | 16,984 | Item 15. EXHIBIT INDEX | SIGNATURES |
