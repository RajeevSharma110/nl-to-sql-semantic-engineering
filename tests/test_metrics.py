import pytest

from nl_sql.metrics import MetricCompiler
from nl_sql.registry import SemanticRegistry


compiler = MetricCompiler(SemanticRegistry())


def test_compiles_governed_metric():
    result = compiler.compile("gross_revenue", "orders.region")
    assert result["metric"] == "gross_revenue"
    assert set(result["lineage"]) == {
        "order_items.quantity",
        "order_items.unit_price",
        "orders.status",
    }
    assert result["trust"]["decision"] == "execute"


def test_rejects_unknown_dimension():
    with pytest.raises(ValueError):
        compiler.compile("gross_revenue", "customers.email")

