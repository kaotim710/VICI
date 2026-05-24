from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class NarrativeBlock:
    text: str
    clean_start: int
    clean_end: int
    raw_start: int | None
    raw_end: int | None
    tag: str | None = None
    source: str = "html"
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CleanDocument:
    text: str
    blocks: list[NarrativeBlock]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class HeadingCandidate:
    item: str
    start: int
    end: int
    text: str
    normalized_text: str
    is_toc_like: bool = False
    reasons: list[str] = field(default_factory=list)
    raw_start: int | None = None
    raw_end: int | None = None
    block_index: int | None = None
    block_tag: str | None = None


@dataclass(frozen=True)
class TocProfile:
    items: list[str]
    confidence: str
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Evidence:
    kind: str
    item: str
    offset: int
    text: str
    reasons: list[str] = field(default_factory=list)
    raw_offset: int | None = None
    block_index: int | None = None
    block_tag: str | None = None


@dataclass(frozen=True)
class CandidateAttempt:
    item: str
    decision: str
    start_evidence: Evidence
    end_evidence: Evidence | None = None
    validation_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ConfidenceComponent:
    name: str
    weight: float
    earned: float
    passed: bool
    reason: str


@dataclass(frozen=True)
class RecommendedAction:
    action_type: str
    reason: str
    description: str
    options: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ItemResult:
    item: str
    status: str
    text: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    confidence_level: str = "low"
    confidence_score: float = 0.0
    confidence_components: list[ConfidenceComponent] = field(default_factory=list)
    start_evidence: Evidence | None = None
    end_evidence: Evidence | None = None
    candidate_attempts: list[CandidateAttempt] = field(default_factory=list)
    validation_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommended_actions: list[RecommendedAction] = field(default_factory=list)
    strategy_used: str = "deterministic_text_v1"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ExtractionResult:
    filing_id: str | None
    status: str
    parser_version: str
    item_results: list[ItemResult]
    warnings: list[str] = field(default_factory=list)
    candidate_count: int = 0
    document_warnings: list[str] = field(default_factory=list)
    toc_items: list[str] = field(default_factory=list)
    toc_confidence: str = "none"

    def to_dict(self) -> dict:
        return asdict(self)
