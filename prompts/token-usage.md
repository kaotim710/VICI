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
