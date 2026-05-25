# Recovery Readiness

This document defines the next recovery layer to implement after deterministic extraction and
regression reporting.

## Current Boundary

Recovery is explicit. It runs only when the user calls recovery actions from the UI or scripts.
The extractor must not autonomously fetch external documents or replace item content without review.
In the UI, recovery actions belong after the extracted item list so users can review primary item
content before choosing recovery paths.

## Action Classes

### Internal TOC Selection

- Trigger: `internal_item_toc_detected`
- Current behavior: return subsection options, require user selection, and show the selected
  subsection as a review candidate in the UI.
- The UI preserves the original extracted item and labels the recovered content as review-only.
- Do not move internal Item 7/8/14 TOCs into supplemental sections.

### Same-Filing References

- Trigger: `same_filing_page_reference`
- Current behavior: deterministic page-range extraction returns reviewable text and exposes page
  range, before/after lengths, and start/end snippets in the UI.
- Accept/reject persistence is intentionally deferred; the UI labels decision buttons as disabled
  review controls so replacement cannot happen silently.
- Do not silently replace the original item content.

### Exhibit And External References

- Trigger: `exhibit_index_detected` or `external_or_other_document_reference`
- Current behavior: show inspect-only or deferred action plus filing-local review snippets.
- Exhibit links detected in the raw item structure are surfaced in the recovery action card.
- External exhibit/API fetching remains deferred until the intake layer is implemented.

## Regression Signals

Recovery readiness is tracked in `reports/regression_report.md`.

- warning category counts
- recommended action counts
- raw media counts for warning/action rows
- supplemental section counts
- raw preview availability
- validation gate status

## Change Log

- 2026-05-25: Created recovery readiness plan for the regression evaluation milestone.
- 2026-05-25: Productized recovery action review panels for same-filing references, internal TOC
  selections, and exhibit links while keeping replacement decisions explicit and deferred.
