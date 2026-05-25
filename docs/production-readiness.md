# Production Readiness Review

This document answers the production review questions for the SEC 10-K item extraction pipeline.
It is intentionally implementation-oriented: each section states the reliability risk, the current
control, and the next validation signal we should add.

## Operating Principles

The pipeline should be judged by whether a reviewer can understand and reproduce a boundary
decision, not only by whether the extracted text looks plausible.

Core rules:

- `Deterministic first`: normal extraction must not depend on LLMs, embeddings, or hidden state.
- `Evidence over intuition`: every selected start/end boundary should have evidence kind, offset,
  text context, and strategy trace.
- `Uncertainty is output`: low confidence, warnings, and recovery actions are first-class result
  fields, not logs that disappear after execution.
- `No silent replacement`: recovery can add reviewable alternatives, but should not overwrite the
  primary extracted item without user acceptance.
- `Small deployable steps`: new strategy should land with focused tests and a reportable evaluation
  signal before broad abstraction.

## 1. Robustness Under Format Variation

SEC filings do not share one stable HTML shape. The extractor must assume variation across issuers,
years, filing vendors, iXBRL wrappers, front-matter TOCs, cross-reference indexes, exhibit indexes,
tables, images, and annual-report-style financial sections.

Current control:

- Use deterministic retrieval from multiple independent signals: regex headings, aliases, DOM/raw
  heading evidence, TOC order, and Form 10-K cross-reference index rows.
- Treat TOC rows as evidence, not as body starts, unless validated by page/offset context.
- Prefer item-to-next-item boundary reconstruction over fixed text-length rules.
- Preserve raw scoped HTML for table/image-heavy sections so reviewers can inspect fidelity.
- Emit per-item `strategy_trace`, evidence offsets, warnings, and confidence instead of silently
  discarding weak sections.

Next validation signal:

- Eval reports should group failures by structural cause: front TOC confusion, internal TOC,
  cross-reference composite item, exhibit/index content, table/image fidelity, missing body heading,
  and over/under boundary.
- The 48-filing eval set should include at least one filing per bucket where an item is known to be
  annual-report style rather than classic `Item N. Title` format.

Detailed strategy:

1. Normalize the filing into both clean narrative text and raw-offset-aware blocks.
2. Retrieve candidate starts from independent deterministic channels:
   - canonical item heading regex
   - expected SEC item title aliases
   - DOM/raw block heading signals
   - front TOC and internal TOC rows
   - Form 10-K cross-reference index rows
3. Reject likely front-matter TOC starts when they are early, dense, page-number-like, or followed by
   stronger body evidence.
4. Reconstruct boundaries by legal item order first, then TOC order, then cross-reference page spans,
   then terminal fallback.
5. Return valid short or long sections when the surrounding boundary context is coherent; attach
   warnings instead of dropping content.
6. Keep raw scoped HTML available for visual fidelity review when text extraction cannot faithfully
   represent tables, images, signatures, or exhibits.

## 2. Validation Without Public Ground Truth

There is no authoritative public boundary dataset for exact 10-K item extraction. That means the
project should not claim absolute accuracy from a single benchmark. It should use layered validation.

Current control:

- Seed filings cover known reviewed cases and regression issues.
- Held-out validation filings catch overfitting to the first seed corpus.
- Reviewed issue cases encode human discoveries as regression tests.
- The new eval manifest expands coverage by sector, market-cap bucket, and time window.
- Confidence and warnings are part of the output contract, so uncertainty can be measured instead of
  hidden.

Validation model:

- `Exact checks`: for manually reviewed boundary issues, assert the specific start/end behavior.
- `Structural checks`: verify canonical item labels, legal item order, non-overlapping spans, and
  scoped raw previews.
- `Metamorphic checks`: changing source route, such as upload sample to SEC direct fetch, should
  identify the same ticker/year and produce the same filing-level item set.
- `Differential checks`: compare current extraction against previous committed reports and flag new
  warning categories, failed items, or large confidence drops.
- `Human review loop`: store accepted/rejected/corrected boundary decisions as append-only feedback,
  then convert high-value corrections into deterministic tests.

Next validation signal:

- The deployed eval runner should write a report with warning category counts, failed request counts,
  failed item counts, SEC format statuses, and top recurring issuer-specific failure modes.

Validation layers:

| Layer | Purpose | Failure signal |
| --- | --- | --- |
| Unit tests | Protect parser contracts and synthetic edge cases. | Broken deterministic rule. |
| Seed corpus | Track known production-like filings and previous user-reviewed issues. | Regression in accepted cases. |
| Held-out validation | Detect overfitting to seed filings. | New warnings, failures, or confidence drops. |
| 48-filing eval set | Measure broader robustness across sector, market cap, and year buckets. | Repeated structural failure mode. |
| Human review feedback | Convert user corrections into durable tests. | Same mistake recurring without a test. |
| Deployed smoke/eval | Verify the hosted API path, not only local extraction. | Request failure, timeout, or hosted-only behavior. |

Ground-truth substitute:

- For exact boundaries, use reviewer-approved cases.
- For unknown filings, use invariants: legal order, non-overlap, canonical item format, scoped raw
  preview, confidence consistency, and warning classification.
- For public deployment, compare the deployed report with local reports to catch environment drift.

## 3. Edge Case Handling

Edge cases should become explicit states, not accidental successes.

Known edge cases and intended handling:

- `Front-matter TOC`: reject as start if page-number-like, early dense item list, or followed by body
  duplicate.
- `Internal TOC inside Item 7/8/14/15`: keep the parent item, expose subsections as review UI.
- `Cross-reference index`: use as deterministic retrieval evidence; reconstruct virtual starts from
  referenced pages when body headings are absent.
- `Short item`: return valid short text when surrounding item order confirms it.
- `Long item`: return content with warnings when the span contains financial statements, exhibits,
  signatures, tables, or internal TOCs.
- `Exhibit/reference-only item`: return the reference text and surface recovery actions; do not
  silently fetch or replace external documents.
- `Images and tables`: preserve scoped raw HTML; extracted plaintext is not the sole source of truth.
- `Oversized upload`: identify from a bounded leading sample, then switch to SEC direct fetch by
  ticker or CIK.
- `CIK-only intake`: route by CIK when ticker is missing or unreliable.
- `Empty or thin filing`: return filing status `failed` when no headings are found or when a full
  item-set extraction succeeds on fewer than half of supported items.

Next validation signal:

- Each edge case should have at least one reviewed issue case or eval filing row tagged with the
  expected structural behavior.

Decision table:

| Edge case | Default behavior | Do not do |
| --- | --- | --- |
| Front TOC selected as item | Reject and continue to later body candidate. | Return TOC row as item body. |
| Item exists only as `Not applicable` | Return short section with high/medium confidence when neighbors align. | Fail because text is too short. |
| Internal item TOC | Keep parent item and expose subsections. | Move ordinary Item 7/8/14 content into supplemental. |
| Cross-reference-only item | Return the reference text and same-filing/external recovery action. | Pretend referenced pages are ordinary contiguous body text without trace. |
| Multi-page cross-reference | Build composite spans with page evidence. | Collapse pages into one untraceable blob. |
| Exhibit index/signatures | Preserve section and raw structure; expose links if present. | Cut off because the item is long. |
| Table/image-heavy item | Show extracted text plus scoped raw filing structure. | Treat plaintext as complete fidelity. |
| Oversized upload | Identify ticker/CIK/year from leading sample, then route to SEC fetch. | Attempt full upload in serverless path. |
| Missing ticker but CIK exists | Resolve or route by CIK. | Guess ticker from filename. |
| Empty/thin filing | Mark filing-level extraction as failed with `INSUFFICIENT_ITEM_COVERAGE`. | Present a few extracted snippets as a successful filing. |

## 4. Cost Discipline

The production contract is deterministic-first. LLMs and embeddings are recovery tools, not default
parsers.

Current control:

- Normal extraction uses local deterministic parsing only.
- Live SEC requests fetch one filing on demand and do not persist raw filings by default.
- Upload identification uses a bounded sample for oversized filings.
- Recovery actions are explicit and user-triggered.
- LLM retry is disabled in the retry policy.

LLM budget rule:

- Only call an LLM when deterministic confidence is low and the ambiguity is semantic, not merely
  structural.
- Never send the full 10-K. Send a bounded evidence packet: item label, candidate headings, nearby
  snippets, cross-reference rows, page markers, and current strategy trace.
- Require the LLM to return a constrained decision, such as `related_heading`, `unrelated_heading`,
  `requires_external_reference`, or `insufficient_evidence`.
- LLM output can recommend a recovery action or reviewer prompt; it should not directly overwrite
  deterministic boundaries without an auditable trace.

Next validation signal:

- Reports should include counts for LLM-eligible items, LLM-called items, accepted LLM decisions, and
  cost per filing once LLM recovery is enabled.

LLM/embedding policy:

- Embeddings are appropriate only for retrieval ranking or alias discovery after deterministic
  evidence is exhausted; they should not define final boundaries alone.
- LLMs are appropriate for semantic ambiguity, such as deciding whether a bold heading belongs to
  the current item or starts unrelated narrative.
- LLMs are not appropriate for parsing all filings, reading full filings, or doing autonomous
  exhibit/API fetching.
- The bounded evidence packet should include at most the candidate heading list, nearby snippets,
  cross-reference rows, page labels, selected start/end evidence, warnings, and strategy trace.
- Every LLM call must produce an auditable decision object and be counted in evaluation reports.

Cost guardrails:

- Default path: zero model calls.
- User-triggered recovery path: deterministic recovery first.
- Model path: only low-confidence or semantically ambiguous items.
- Batch eval path: model calls disabled by default unless explicitly enabled for a controlled run.

## 5. Performance, Scalability, And Correctness

Performance risk comes from large filings, raw HTML preservation, repeated SEC calls, and future
eval runs across many issuers.

Current control:

- Extraction runs per filing on demand.
- Raw filings are not stored by default for live SEC or upload flows.
- SEC client is rate-limited and requires a User-Agent.
- Reports aggregate warning and confidence signals instead of requiring manual inspection of every
  successful item.

Performance targets:

- One filing should extract within an interactive latency budget on hosted infrastructure.
- The parser should avoid full DOM-heavy transformations when plaintext/offset evidence is enough.
- Raw iframe fragments should be scoped to selected item boundaries, not whole filings.
- Eval jobs should run as batch scripts with sleep/rate controls, not through frontend clicks.

Scaling model:

- `Interactive path`: one ticker/year or upload sample, run extraction on demand, return inspectable
  item payload.
- `Batch eval path`: manifest-driven runner, one request per filing, report aggregate failures.
- `Future persistence path`: store only selected metadata, reports, and reviewed feedback unless raw
  storage is explicitly enabled.

Correctness checks:

- Item spans should be ordered and non-overlapping unless explicitly marked as composite.
- A selected start should be tied to evidence kind and offset.
- A selected end should be tied to next-item evidence, page-range evidence, or terminal boundary
  logic.
- Confidence should decrease when boundaries come from weaker evidence, when SEC format metadata is
  noncanonical, or when recovery actions are required.
- The UI must show uncertainty instead of converting warnings into hidden success.

Next validation signal:

- Add deployed eval report thresholds for `failed_requests`, `failed_items`, warning category deltas,
  SEC format review count, and median/p95 elapsed time.

Latency risks and controls:

- Large HTML files: prefer streaming/download-once behavior and avoid repeated full DOM passes.
- Raw previews: slice scoped raw fragments by item boundary instead of rendering the full filing.
- SEC calls: keep rate limiting and avoid fetching raw filings until a user selects a filing.
- Serverless deployment: avoid large uploads and long-running batch eval inside frontend requests.
- Batch validation: use scripts with sleep/rate controls and write reports to disk.

Correctness instrumentation:

- `candidate_attempts`: every tried start/end pair and rejection reason.
- `strategy_trace`: chosen retrieval and boundary path.
- `confidence_components`: score breakdown instead of a black-box score.
- `sec_format`: canonical label/title match status.
- `warnings` and `recommended_actions`: reviewable uncertainty and recovery path.
- `raw_structure`: scoped original HTML for fidelity inspection.

Acceptance gates:

- No missing filings in a required manifest run.
- No failed request in deployed smoke/eval runs unless explicitly marked environment-blocked.
- No new failed item without a reviewed issue case or documented strategy gap.
- Warning count/category increases must be classified before optimization.
- Performance regressions should be tracked with elapsed time and source size.

## 6. Practical Next Steps

1. Run the 48-filing deployed eval set and capture the first report.
2. Classify every warning/failure by structural cause.
3. Convert repeated causes into reviewed issue cases before changing extractor behavior.
4. Add performance fields to the deployed eval report: elapsed time, source bytes, item count, and
   warning count per filing.
5. Only after deterministic fixes plateau, add a bounded LLM verifier for low-confidence semantic
   ambiguity.

## 7. Documentation Maintenance

When strategy changes:

1. Read `docs/extraction-strategy.md` and this file before editing parser behavior.
2. Update the strategy document in the same change set.
3. Add or update a focused test.
4. Run the smallest relevant test first, then the broader suite when behavior risk is meaningful.
5. If the change came from a reviewed filing issue, record the case in
   `fixtures/gold/reviewed_issue_cases.json` or the eval manifest metadata.
