from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .database import dry_run
from .metrics import MetricCompiler
from .registry import SemanticRegistry


app = FastAPI(title="Governed NL-to-SQL Semantic Layer", version="0.1.0")
registry = SemanticRegistry()
compiler = MetricCompiler(registry)


class CompileRequest(BaseModel):
    metric: str
    dimension: str | None = None
    explain: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def list_metrics() -> list[dict]:
    return registry.list_metrics()


@app.post("/metrics/compile")
def compile_metric(request: CompileRequest) -> dict:
    try:
        result = compiler.compile(request.metric, request.dimension)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if request.explain and result["sql"]:
        result["dry_run"] = dry_run(result["sql"]).__dict__
    return result

