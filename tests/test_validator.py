from nl_sql.validator import SQLValidator


validator = SQLValidator({"orders", "payments"}, max_limit=100)


def test_adds_limit_to_valid_select():
    result = validator.validate("SELECT status, count(*) FROM orders GROUP BY status")
    assert result.valid
    assert "LIMIT 100" in result.normalized_sql
    assert result.tables == ("orders",)


def test_rejects_write():
    result = validator.validate("DELETE FROM orders")
    assert not result.valid


def test_rejects_multiple_statements():
    result = validator.validate("SELECT * FROM orders; SELECT * FROM payments")
    assert not result.valid


def test_rejects_unknown_table():
    result = validator.validate("SELECT * FROM secrets")
    assert not result.valid
    assert "schema registry" in result.errors[0]


def test_caps_limit():
    result = validator.validate("SELECT * FROM orders LIMIT 1000")
    assert result.valid
    assert "LIMIT 100" in result.normalized_sql

