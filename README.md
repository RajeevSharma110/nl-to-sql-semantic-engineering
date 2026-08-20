# NL-to-SQL Semantic Engineering Practice

Interview-practice workspace for a governed NL-to-SQL pipeline, schema registry,
domain glossary, semantic metric layer, MCP tools, query validation, trust scoring,
warehouse integration, BI integration, and data contracts.

## Environment

- Python 3.12 virtual environment: `.venv`
- PostgreSQL 16 on port 5432
- Docker Engine and Docker Compose
- Python MCP implementation; Node.js is not required

## Activate the environment

```bash
cd /root/nl-to-sql
source .venv/bin/activate
```

Do not commit API keys or database passwords. Store local secrets in `.env`, which
is excluded by `.gitignore`.

## Run the checks and services

```bash
pytest -q
uvicorn nl_sql.api:app --host 127.0.0.1 --port 8000
semantic-mcp
```

Try the API in a second terminal:

```bash
curl http://127.0.0.1:8000/metrics
curl -X POST http://127.0.0.1:8000/metrics/compile \
  -H 'content-type: application/json' \
  -d '{"metric":"gross_revenue","dimension":"orders.region","explain":true}'
```

The local database user is intentionally read-only. Replace the demonstration
credential before using this project outside this disposable practice environment.
