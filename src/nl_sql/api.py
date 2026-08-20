from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .database import dry_run, execute_readonly
from .metrics import MetricCompiler
from .registry import SemanticRegistry
from .resolver import IntentResolutionError, resolve_question


app = FastAPI(title="Governed NL-to-SQL Semantic Layer", version="0.1.0")
registry = SemanticRegistry()
compiler = MetricCompiler(registry)
frontend = Path(__file__).resolve().parents[2] / "frontend"


class CompileRequest(BaseModel):
    metric: str
    dimension: str | None = None
    explain: bool = False


class QueryRequest(BaseModel):
    question: str
    explain: bool = True
    execute: bool = True


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(frontend / "index.html")


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


@app.post("/query")
def query(request: QueryRequest) -> dict:
    try:
        intent = resolve_question(request.question)
        result = compiler.compile(intent.metric, intent.dimension)
    except IntentResolutionError as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": str(exc), "suggestions": exc.suggestions},
        ) from exc
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result["question"] = request.question
    result["resolution"] = {
        "metric": intent.metric,
        "dimension": intent.dimension,
        "confidence": intent.confidence,
        "explanation": intent.explanation,
    }
    if request.explain and result["sql"]:
        result["dry_run"] = dry_run(result["sql"]).__dict__
    if request.execute and result["sql"]:
        result["data"] = execute_readonly(result["sql"])
    return result


app.mount("/static", StaticFiles(directory=frontend), name="static")
