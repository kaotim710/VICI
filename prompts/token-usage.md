# Prompt Token Usage

This ledger tracks user prompt token usage for project traceability.

Important distinction:

- `estimated_prompt_tokens` is a local planning estimate.
- `actual_prompt_tokens` should only be filled when model/API usage metadata is available.
- Current estimates are not billing records.

Estimation method for the initial entries:

```text
estimated_prompt_tokens =
  round(CJK characters * 0.75 + ASCII words/URL fragments * 1.25 + remaining punctuation/spacing * 0.2)
```

| Date | Prompt ID | Source | Actual Prompt Tokens | Estimated Prompt Tokens | Notes |
| --- | --- | --- | ---: | ---: | --- |
| 2026-05-23 | architecture_request | `prompts/2026-05-24-user-prompts.md` |  | 607 | Initial architecture review request. |
| 2026-05-24 | implementation_milestone_question | `prompts/2026-05-24-user-prompts.md` |  | 44 | Asked how to start implementation and proposed gold dataset shape. |
| 2026-05-24 | implementation_start_request | `prompts/2026-05-24-user-prompts.md` |  | 32 | Approved implementation and 20-filing testing seed. |
| 2026-05-24 | sec_data_source_request | `prompts/2026-05-24-user-prompts.md` |  | 82 | Provided SEC data source endpoints and request constraints. |
| 2026-05-24 | prompt_token_usage_request | `prompts/2026-05-24-user-prompts.md` |  | 13 | Requested prompt token usage tracking in `prompts/`. |
| 2026-05-24 | seed_filing_download_request | `prompts/2026-05-24-user-prompts.md` |  | 14 | Requested downloading the 20 seed 10-K test filings. |
| 2026-05-24 | next_milestone_request | `prompts/2026-05-24-user-prompts.md` |  | 6 | Requested continuing to the next implementation milestone. |
| 2026-05-24 | continue_milestones_request | `prompts/2026-05-24-user-prompts.md` |  | 7 | Requested continuing with subsequent milestones. |
| 2026-05-24 | seed_extraction_markdown_request | `prompts/2026-05-24-user-prompts.md` |  | 15 | Requested testing extraction on seed filings and displaying results as Markdown. |
| 2026-05-24 | seed_extraction_snippet_request | `prompts/2026-05-24-user-prompts.md` |  | 22 | Requested adding ending snippets alongside beginning snippets in the Markdown report. |
| 2026-05-24 | next_step_request | `prompts/2026-05-24-user-prompts.md` |  | 5 | Requested proceeding to the next step. |
| 2026-05-24 | warning_audit_report_request | `prompts/2026-05-24-user-prompts.md` |  | 15 | Requested resolving warning planning work and producing a readable test report. |
| 2026-05-24 | candidate_pair_resolver_request | `prompts/2026-05-24-user-prompts.md` |  | 7 | Requested implementing the candidate-pair idea and running tests. |
| 2026-05-24 | warning_count_followup_request | `prompts/2026-05-24-user-prompts.md` |  | 13 | Asked whether warnings decreased and requested continuing with follow-up work if so. |
| 2026-05-24 | gold_boundary_implementation_request | `prompts/2026-05-24-user-prompts.md` |  | 5 | Requested implementing the proposed gold boundary evaluation milestone. |
| 2026-05-24 | recovery_runner_implementation_request | `prompts/2026-05-24-user-prompts.md` |  | 2 | Approved implementing deterministic recovery action runner. |
| 2026-05-24 | full_item_testing_request | `prompts/2026-05-24-user-prompts.md` |  | 20 | Requested testing extraction across all supported 10-K items instead of only selected items. |
| 2026-05-24 | toc_assisted_boundary_request | `prompts/2026-05-24-user-prompts.md` |  | 33 | Requested TOC-assisted handling because filings do not always declare clear Item 1-16 sections. |
| 2026-05-24 | continue_toc_implementation_request | `prompts/2026-05-24-user-prompts.md` |  | 6 | Approved continuing implementation of the TOC-assisted extraction layer. |
| 2026-05-24 | mvp_run_request | `prompts/2026-05-24-user-prompts.md` |  | 25 | Requested proceeding by milestone, deferring the 13 failed cases, and running an MVP first. |
| 2026-05-24 | failed_item_recovery_request | `prompts/2026-05-24-user-prompts.md` |  | 18 | Requested continuing the milestone plan by handling the 13 failed seed extraction items. |
| 2026-05-24 | reliability_milestone_request | `prompts/2026-05-24-user-prompts.md` |  | 9 | Requested implementing milestone items 1-5 before API or deployment work. |
| 2026-05-24 | retry_policy_contract_request | `prompts/2026-05-24-user-prompts.md` |  | 18 | Requested adding RetryPolicy and confirming outstanding working tree changes first. |
| 2026-05-24 | frontend_test_filing_ui_request | `prompts/2026-05-24-user-prompts.md` |  | 85 | Requested a simple frontend to select current test filings and run extraction only after the user opens a filing. |
| 2026-05-24 | frontend_recovery_ui_request | `prompts/2026-05-24-user-prompts.md` |  | 18 | Requested implementing planning items 1-3, cleaning unused parts for item 4, and deferring item 5. |
| 2026-05-24 | held_out_validation_filing_request | `prompts/2026-05-24-user-prompts.md` |  | 28 | Requested adding validation testing with five additional companies using prior-year and ten-years-ago filings. |
| 2026-05-24 | validation_warning_review_request | `prompts/2026-05-24-user-prompts.md` |  | 214 | Reviewed validation warnings and requested boundary-context acceptance for short sections plus review actions for exhibits and references. |
| 2026-05-24 | exhibit_table_frontend_request | `prompts/2026-05-24-user-prompts.md` |  | 32 | Requested simple frontend display for exhibit/table overlong sections and asked about image handling strategy. |
| 2026-05-24 | raw_filing_structure_preview_request | `prompts/2026-05-24-user-prompts.md` |  | 34 | Requested restoring original filing table structure in the UI and prototyping image display. |
| 2026-05-24 | raw_structure_tag_request | `prompts/2026-05-24-user-prompts.md` |  | 13 | Requested adding tags to extracted items when raw tables or images are detected. |
| 2026-05-24 | gold_raw_media_fidelity_request | `prompts/2026-05-24-user-prompts.md` |  | 31 | Requested adding gold checks for table/image restoration fidelity and rerunning gold warning classification. |
| 2026-05-24 | seed_raw_media_coverage_request | `prompts/2026-05-24-user-prompts.md` |  | 29 | Asked whether raw table/image restoration only covers a few filings and requested pushing it to current test filings. |
| 2026-05-24 | seed_warning_review_request | `prompts/2026-05-24-user-prompts.md` |  | 455 | Reviewed seed warnings, accepted normal short/reference cases, requested structured toggles for long exhibit/internal TOC sections, and identified AMZN 2023 Item 9C over-extraction. |
| 2026-05-24 | raw_structure_toggle_fix_request | `prompts/2026-05-24-user-prompts.md` |  | 81 | Reported raw original view starting too early and requested clickable section structure toggles that show subsection content. |
| 2026-05-24 | jpm_exhibit_link_and_supplemental_chunk_request | `prompts/2026-05-24-user-prompts.md` |  | 75 | Requested hyperlinking JPM 2023 Item 15 exhibit titles and adding a supplemental chunk for the post-page-45 content with its own TOC/tables/images. |
| 2026-05-24 | supplemental_same_page_section_request | `prompts/2026-05-24-user-prompts.md` |  | 55 | Requested moving the supplemental chunk into same-page operation as a partitioned section appended after Item 16 during extraction. |
| 2026-05-24 | supplemental_raw_structure_button_request | `prompts/2026-05-24-user-prompts.md` |  | 11 | Requested adding Show original filing structure support to the supplemental section. |
| 2026-05-24 | supplemental_seed_coverage_request | `prompts/2026-05-24-user-prompts.md` |  | 20 | Requested extending supplemental raw-structure handling across the 20 seed filings and adding tests for that coverage. |
| 2026-05-24 | strategy_documentation_request | `prompts/2026-05-24-user-prompts.md` |  | 26 | Requested creating a strategy Markdown file and keeping it updated whenever extraction strategy changes. |
