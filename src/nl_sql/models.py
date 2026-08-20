from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    normalized_sql: str | None = None
    tables: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunResult:
    valid: bool
    estimated_cost: float | None = None
    plan: dict[str, Any] | None = None
    error: str | None = None


@dataclass(frozen=True)
class TrustEvidence:
    schema_grounding: float
    metric_resolution: float
    sql_validation: float
    dry_run: float
    ambiguity: float
    benchmark_history: float
    reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def score(self) -> float:
        weighted = (
            0.25 * self.schema_grounding
            + 0.25 * self.metric_resolution
            + 0.20 * self.sql_validation
            + 0.15 * self.dry_run
            + 0.10 * (1 - self.ambiguity)
            + 0.05 * self.benchmark_history
        )
        return round(max(0.0, min(1.0, weighted)), 3)

    @property
    def decision(self) -> str:
        if self.score >= 0.80:
            return "execute"
        if self.score >= 0.60:
            return "review"
        return "clarify"

