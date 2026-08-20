import pytest

from nl_sql.resolver import IntentResolutionError, resolve_question


def test_resolves_metric_and_dimension():
    intent = resolve_question("Show gross revenue by region")
    assert intent.metric == "gross_revenue"
    assert intent.dimension == "orders.region"
    assert intent.confidence > 0.9


def test_resolves_payment_question():
    intent = resolve_question("What is the payment success rate by payment method?")
    assert intent.metric == "payment_success_rate"
    assert intent.dimension == "payments.method"


def test_rejects_ungoverned_question():
    with pytest.raises(IntentResolutionError):
        resolve_question("Who is our best customer?")
