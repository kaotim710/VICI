# Extraction Strategy

This file is the living record for extraction strategy rules. Before changing extraction behavior,
read this file first. After changing strategy, update this file in the same change set.

## Strategy Contract

- Deterministic parsing comes first.
- LLM and embedding support are reserved for ambiguity recovery, not primary extraction.
- Every selected boundary must remain inspectable through evidence, candidate attempts, warnings,
  and confidence components.
- Recovery is explicit and bounded. The pipeline must not launch autonomous agent orchestration.
- UI previews should preserve original filing structure when raw tables, images, exhibits, or
  supplemental sections matter for user review.

## Candidate Retrieval

Start candidates are retrieved through deterministic signals:

- regex item heading retrieval
- alias/title matching
- DOM/raw heading evidence where offsets are available
- TOC-assisted candidates and next-item ordering

TOC-like candidates are rejected when they look like index entries rather than real section starts.
Examples include short ordered spans, page-number-like headings, and headings followed by page
ranges inside early table-of-contents regions.

## Boundary Reconstruction

Boundary selection uses the nearest valid next item according to legal 10-K item ordering.

- Prefer validated next-item evidence from the same filing structure.
- Use TOC next-item order when the document's TOC is reliable.
- Fall back to the legal transition graph when TOC evidence is missing or weak.
- Accept short sections when surrounding item order confirms the boundary, even when the extracted
  body is only a title, one word, or a short sentence.
- For terminal sections, allow end-of-document or final-item boundaries only after rejecting stronger
  next-item evidence.

## Length Policy

Length warnings are review signals, not automatic failures.

- Very short sections can be valid when the item is reserved, not applicable, omitted, or explicitly
  answered in one sentence.
- Long sections can be valid when they contain financial statements, exhibit indexes, signatures,
  tables, or internal subsection TOCs.
- Boundary context is more important than raw character count. If previous and next item boundaries
  are coherent, return the content and attach warnings/actions instead of silently dropping it.

## Raw Structure Preview

Raw previews are scoped to the selected item boundary.

- `Show original filing structure` must render only the item's raw HTML fragment, not the whole
  filing.
- Tables and images are preserved inside a sandboxed `srcdoc` iframe with the SEC archive directory
  as the base URL when available.
- Items with tables/images receive UI tags so reviewers can inspect fidelity quickly.
- Normal 10-K items should not show section snippets or section-structure toggles by default. Keep
  the default item surface focused on evidence, warnings/actions, and extracted text.
- `Show original filing structure` is a reversible view toggle. It switches between the extracted
  item view and the scoped original filing HTML view, and can switch back without rerunning
  extraction.
- Exhibit section titles should include SEC archive hyperlinks when the original exhibit index row
  has links.

## Internal TOC Sections

Internal TOCs inside normal items stay inside the item.

- Examples: long Item 7, Item 8, or Item 14 sections with their own financial or management TOC.
- These stay inside the item and can be inspected through `Show original filing structure`.
- If a normal item has a large raw span plus an internal TOC, expose the TOC-derived subsections as
  the primary review surface, with per-title original filing structure toggles.
- Front-matter TOC entries must not drive item extraction when a later body heading exists. Dense
  item clusters are TOC-like only when they are in the early document region or have explicit
  page-number signals.
- They should not be moved into a virtual supplemental item unless they are terminal filing content
  after Item 15 or Item 16.

## Supplemental Section Partition

Supplemental sections are virtual same-page sections appended after the ordinary extracted items.

Current allowed source items:

- Item 15
- Item 16

Current detection rules:

- Search only inside Item 15/16 raw fragments.
- Require a terminal financial-style TOC signal such as `Financial:`, `Audited financial statements`,
  `Financial Table of Contents`, or nearby `Financial Section`.
- Reject signature-only and exhibit-index-only `Table of Contents` blocks unless they are connected
  to financial-section evidence.
- Build subsection toggles from anchor TOC links when possible.
- Treat row-based TOCs as first-class evidence. If a TOC row has a left-side label and a right-side
  linked page number, use the row label as the subsection title and the page link as the boundary.
- If a terminal financial TOC has no usable links, infer subsection starts from TOC row labels and
  later matching heading text in the raw chunk.
- If anchor TOC links are unavailable, fall back to raw bold/headline outline extraction.
- Suppress small unstructured chunks when no sections are found and raw media count is low.
- In the UI, supplemental items with reconstructed subsections should render the child sections as
  the primary review surface and avoid duplicating the full supplemental text chunk below them.
- Each reconstructed supplemental subsection must carry raw fragment offsets so `Show original
  filing structure` can be toggled per subsection, not only for the whole supplemental item.

Current seed coverage:

- `jpm_2014_10k` -> `supplemental-15`
- `jpm_2023_10k` -> `supplemental-15`
- `xom_2014_10k` -> `supplemental-15`
- `xom_2023_10k` -> `supplemental-16`
- `cvx_2014_10k` -> `supplemental-15`

The supplemental raw preview must be scoped to the supplemental chunk itself. It must not include
Item 1 or the whole filing.

## Warning And Recovery Actions

Warnings should be categorized into reviewable causes:

- `length_policy_review`: short/long section requires context review.
- `title_policy_review`: title-only or near-title-only sections may still be valid.
- `reference_recovery`: section points to another page, table, exhibit, or incorporated reference.
- `internal_item_toc_detected`: item contains its own TOC and may need user subsection selection.

Recovery remains explicit:

- same-filing page references can be parsed deterministically and returned for user review.
- short sections that cite same-filing page ranges should remain extracted as the section text and
  emit `same_filing_page_reference`; following the range is a user-confirmed recovery action.
- internal TOC actions should ask the user which subsection to inspect.
- external exhibits or incorporated documents are deferred unless a dedicated exhibit retrieval
  strategy is implemented.

## Testing Expectations

Any strategy change should include focused tests for the behavior being changed.

- Unit tests should cover synthetic edge cases when possible.
- Seed tests should cover known production filings when strategy depends on real filing structure.
- Reviewed issue cases should be recorded in `fixtures/gold/reviewed_issue_cases.json`; add new
  validation filings there when a reviewer identifies a concrete boundary, TOC, or recovery failure.
- Supplemental partition tests must scan the 20 seed filings for expected virtual sections and must
  verify raw preview scope.
- Regression reports should combine seed and validation filings into one review surface with status,
  confidence, warning categories, raw media counts, supplemental section counts, raw preview
  availability, and recovery action counts.
- Full test suite should pass with `python3 -m unittest discover -s tests`.

## Change Log

- 2026-05-24: Created strategy record. Documented deterministic extraction, raw structure previews,
  internal TOC handling, and seed-wide supplemental partition rules.
- 2026-05-24: Expanded supplemental subsection reconstruction to support row-based TOCs where page
  numbers are links and labels are plain text, plus unlinked financial TOC rows with inferred
  heading offsets.
- 2026-05-24: Simplified normal item UI by removing section snippets and section-structure toggles;
  made original filing structure a reversible view toggle instead of an appended one-way preview.
- 2026-05-25: Added regression evaluation as the reliability review surface before live SEC intake;
  recovery readiness is tracked separately from autonomous external fetching.
- 2026-05-25: Added per-subsection raw structure preview for supplemental partitions by preserving
  raw offsets on each reconstructed subsection.
- 2026-05-25: Added internal TOC partitioning for large normal items and tightened front-matter TOC
  candidate ranking so body headings win over table-of-contents entries.
