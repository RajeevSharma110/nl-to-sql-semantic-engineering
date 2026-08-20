from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


class SemanticRegistry:
    def __init__(self, registry_path: Path | None = None, glossary_path: Path | None = None):
        self.registry_path = registry_path or ROOT / "semantic" / "schema_registry.json"
        self.glossary_path = glossary_path or ROOT / "semantic" / "glossary.json"
        self.schema: dict[str, Any] = json.loads(self.registry_path.read_text())
        self.glossary: dict[str, Any] = json.loads(self.glossary_path.read_text())

    @property
    def allowed_tables(self) -> set[str]:
        return set(self.schema["tables"])

    def table(self, name: str) -> dict[str, Any]:
        return self.schema["tables"][name]

    def metric(self, name: str) -> dict[str, Any]:
        return self.glossary["metrics"][name]

    def list_metrics(self) -> list[dict[str, Any]]:
        return [dict(name=name, **definition) for name, definition in self.glossary["metrics"].items()]

