from __future__ import annotations

import re

from sqlglot import exp, parse

from .models import ValidationResult


WRITE_NODES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.Command,
    exp.Merge,
)


class SQLValidator:
    def __init__(self, allowed_tables: set[str], max_limit: int = 500):
        self.allowed_tables = {name.lower() for name in allowed_tables}
        self.max_limit = max_limit

    def validate(self, sql: str) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        try:
            statements = parse(sql, read="postgres")
        except Exception as exc:
            return ValidationResult(valid=False, errors=(f"SQL parse error: {exc}",))

        if len(statements) != 1:
            return ValidationResult(valid=False, errors=("Exactly one SQL statement is allowed",))

        statement = statements[0]
        if not isinstance(statement, (exp.Select, exp.Union, exp.Subquery)):
            errors.append("Only read-only SELECT queries are allowed")
        if any(statement.find(node) is not None for node in WRITE_NODES):
            errors.append("DDL and DML operations are forbidden")

        tables = {table.name.lower() for table in statement.find_all(exp.Table)}
        unknown = sorted(tables - self.allowed_tables)
        if unknown:
            errors.append(f"Tables outside the schema registry: {', '.join(unknown)}")

        if re.search(r"\b(pg_catalog|information_schema)\b", sql, re.IGNORECASE):
            errors.append("System catalog access is forbidden")

        limit = statement.args.get("limit")
        if limit is None:
            statement.set("limit", exp.Limit(expression=exp.Literal.number(self.max_limit)))
            warnings.append(f"LIMIT {self.max_limit} added")
        else:
            try:
                requested = int(limit.expression.name)
                if requested > self.max_limit:
                    limit.set("expression", exp.Literal.number(self.max_limit))
                    warnings.append(f"LIMIT reduced to {self.max_limit}")
            except (TypeError, ValueError):
                errors.append("LIMIT must be a numeric literal")

        return ValidationResult(
            valid=not errors,
            normalized_sql=statement.sql(dialect="postgres") if not errors else None,
            tables=tuple(sorted(tables)),
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

