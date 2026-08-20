# Architecture and governance

```text
Question -> intent/metric resolution -> schema + glossary grounding
         -> SQL generation -> AST validation -> PostgreSQL EXPLAIN
         -> trust decision -> read-only execution -> BI/MCP response
```

## Guardrails

- Only one `SELECT` statement is accepted.
- Tables must appear in the versioned schema registry.
- DDL, DML, system catalogs, and unbounded result sets are rejected.
- PostgreSQL dry-runs use `EXPLAIN`, a read-only transaction, and a timeout.
- The production execution identity should have `SELECT` only on approved views.
- Trust below 0.60 asks for clarification; 0.60–0.79 requires review.
- Every response includes metric version, SQL, lineage, warnings, and trust evidence.

## Schema-change process

1. Producer proposes a versioned contract change with owner and migration date.
2. CI checks registry consistency, contract validity, SQL compilation, and benchmarks.
3. Impact analysis identifies metrics, agents, dashboards, and residency policies.
4. Breaking changes require a parallel version and consumer migration window.
5. Observe both versions, notify consumers, then deprecate and remove the old version.
6. Roll back the producer change if freshness, quality, or benchmark SLOs regress.

## Warehouse and residency

Route requests by tenant residency before opening a warehouse connection. Use separate
credentials and audit streams per region. Enforce statement timeouts, row limits,
partition pruning, cost thresholds, result caching, and workload-specific pools.

## BI integration

BI agents call the same semantic MCP tools as NL-to-SQL agents. A BI adapter should
return dataset and dashboard identifiers alongside metric versions, filter context,
lineage, freshness, query identifiers, and streamed progress events.

