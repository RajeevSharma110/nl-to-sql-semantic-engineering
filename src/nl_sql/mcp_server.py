from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from .database import dry_run
from .metrics import MetricCompiler
from .registry import SemanticRegistry


registry = SemanticRegistry()
compiler = MetricCompiler(registry)
mcp = MCPServer(
    "semantic-metric-layer",
    description="Governed cross-agent metric resolution and PostgreSQL dry runs",
    version="0.1.0",
)


@mcp.tool()
def list_metrics() -> list[dict]:
    """List governed metrics, definitions, dimensions, owners, and versions."""
    return registry.list_metrics()


@mcp.tool()
def get_metric_definition(metric_name: str) -> dict:
    """Return the authoritative definition and lineage for a metric."""
    return registry.metric(metric_name)


@mcp.tool()
def compile_metric_query(metric_name: str, dimension: str | None = None) -> dict:
    """Compile a governed metric into validated PostgreSQL."""
    return compiler.compile(metric_name, dimension)


@mcp.tool()
def explain_query(metric_name: str, dimension: str | None = None) -> dict:
    """Dry-run a compiled query using PostgreSQL EXPLAIN without executing it."""
    compiled = compiler.compile(metric_name, dimension)
    result = dry_run(compiled["sql"])
    return {**compiled, "dry_run": result.__dict__}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
