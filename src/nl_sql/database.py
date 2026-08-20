from __future__ import annotations

import json
import os
from typing import Any

import psycopg
from dotenv import load_dotenv

from .models import DryRunResult
from .registry import ROOT


load_dotenv(ROOT / ".env")


def database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql:///nl_sql")


def dry_run(sql: str) -> DryRunResult:
    try:
        with psycopg.connect(database_url(), autocommit=False) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SET LOCAL statement_timeout = '3s'")
                cursor.execute("EXPLAIN (FORMAT JSON) " + sql)
                raw: Any = cursor.fetchone()[0]
                plan = raw if isinstance(raw, list) else json.loads(raw)
                root = plan[0]["Plan"]
                return DryRunResult(valid=True, estimated_cost=float(root["Total Cost"]), plan=plan[0])
    except Exception as exc:
        return DryRunResult(valid=False, error=str(exc))
