from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResolvedIntent:
    metric: str
    dimension: str | None
    confidence: float
    explanation: str


METRIC_PHRASES = {
    "gross_revenue": ("gross revenue", "sales before refunds", "order revenue"),
    "net_revenue": ("net revenue", "revenue after refunds", "recognized revenue"),
    "payment_success_rate": ("payment success rate", "successful payments", "payment conversion"),
}

DIMENSION_PHRASES = {
    "region": "orders.region",
    "payment method": "payments.method",
    "method": "payments.method",
    "month": "date_trunc('month', orders.ordered_at)",
}


class IntentResolutionError(ValueError):
    def __init__(self, message: str, suggestions: list[str]):
        super().__init__(message)
        self.suggestions = suggestions


def resolve_question(question: str) -> ResolvedIntent:
    normalized = " ".join(question.lower().strip().split())
    if not normalized:
        raise IntentResolutionError("Enter a business question", list(METRIC_PHRASES))

    matches = [
        metric
        for metric, phrases in METRIC_PHRASES.items()
        if any(phrase in normalized for phrase in phrases)
    ]
    if len(matches) != 1:
        raise IntentResolutionError(
            "The question does not resolve to exactly one governed metric",
            ["gross revenue by region", "net revenue", "payment success rate by payment method"],
        )

    metric = matches[0]
    dimension = next((value for phrase, value in DIMENSION_PHRASES.items() if phrase in normalized), None)
    if metric == "net_revenue" and dimension == "orders.region":
        raise IntentResolutionError(
            "Net revenue has no governed region dimension in version 1.0.0",
            ["net revenue by payment method", "gross revenue by region"],
        )
    if metric == "payment_success_rate" and dimension not in (None, "payments.method"):
        raise IntentResolutionError(
            "Payment success rate currently supports payment method only",
            ["payment success rate by payment method"],
        )
    if metric == "net_revenue" and dimension == "payments.method":
        confidence = 0.98
    else:
        confidence = 0.96 if dimension else 0.92
    return ResolvedIntent(
        metric=metric,
        dimension=dimension,
        confidence=confidence,
        explanation="Matched governed glossary terms and an approved dimension",
    )

