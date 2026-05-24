from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class HeadingCandidate:
    item: str
    start: int
    end: int
    text: str
    normalized_text: str
    is_toc_like: bool = False
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Evidence:
    kind: str
    item: str
    offset: int
    text: str
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ItemResult:
    item: str
    status: str
    text: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    confidence_level: str = "low"
    confidence_score: float = 0.0
    start_evidence: Evidence | None = None
    end_evidence: Evidence | None = None
    validation_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
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

    def to_dict(self) -> dict:
        return asdict(self)

