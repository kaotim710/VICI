# Recovery Readiness

This document defines the next recovery layer to implement after deterministic extraction and
regression reporting.

## Current Boundary

Recovery is explicit. It runs only when the user calls recovery actions from the UI or scripts.
The extractor must not autonomously fetch external documents or replace item content without review.

## Action Classes

### Internal TOC Selection

- Trigger: `internal_item_toc_detected`
- Current behavior: return subsection options and require user selection.
- Next implementation target: show selected subsection content in the UI while preserving the original
  extracted item.
- Do not move internal Item 7/8/14 TOCs into supplemental sections.

### Same-Filing References

- Trigger: `same_filing_page_reference`
- Current behavior: deterministic page-range extraction returns reviewable text.
- Next implementation target: expose same-filing reference snippets as review panels with accept/reject
  controls.
- Do not silently replace the original item content.

### Exhibit And External References

- Trigger: `exhibit_index_detected` or `external_or_other_document_reference`
- Current behavior: show inspect-only or deferred action.
- Next implementation target: display referenced exhibit/index metadata and links when already present
  in the filing.
- External exhibit/API fetching remains deferred until the intake layer is implemented.

## Regression Signals

Recovery readiness is tracked in `reports/regression_report.md`.

- warning category counts
- recommended action counts
- raw media counts for warning/action rows
- supplemental section counts
- raw preview availability

## Change Log

- 2026-05-25: Created recovery readiness plan for the regression evaluation milestone.
