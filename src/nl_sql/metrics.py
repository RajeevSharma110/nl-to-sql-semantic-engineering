from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import TrustEvidence
from .registry import SemanticRegistry
from .validator import SQLValidator


class MetricCompiler:
    """Compile governed metric definitions rather than asking an LLM to invent formulas."""

    def __init__(self, registry: SemanticRegistry):
        self.registry = registry
        self.validator = SQLValidator(registry.allowed_tables)

    def compile(self, metric_name: str, dimension: str | None = None) -> dict[str, Any]:
        metric = self.registry.metric(metric_name)
        allowed_dimensions = metric.get("dimensions", [])
        if dimension and dimension not in allowed_dimensions:
            raise ValueError(f"Dimension '{dimension}' is not allowed for {metric_name}")

        select = metric["sql"]
        group = ""
        if dimension:
            select = f"{dimension}, {select}"
            group = f" GROUP BY {dimension} ORDER BY {metric_name} DESC"
        sql = f"SELECT {select} AS {metric_name} FROM {metric['source']}{group}"
        validation = self.validator.validate(sql)
        evidence = TrustEvidence(
            schema_grounding=1.0 if validation.tables else 0.0,
            metric_resolution=1.0,
            sql_validation=1.0 if validation.valid else 0.0,
            dry_run=0.5,
            ambiguity=0.0,
            benchmark_history=0.8,
            reasons=("governed metric definition", "dry run not yet performed"),
        )
        return {
            "metric": metric_name,
            "version": metric["version"],
            "sql": validation.normalized_sql,
            "lineage": metric["lineage"],
            "warnings": validation.warnings,
            "trust": {"score": evidence.score, "decision": evidence.decision, **asdict(evidence)},
        }

