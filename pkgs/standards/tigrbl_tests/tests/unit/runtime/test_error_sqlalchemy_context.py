from __future__ import annotations

from sqlalchemy.exc import DBAPIError, OperationalError, StatementError

from tigrbl.runtime.errors.converters import create_standardized_error


def test_statement_error_includes_sql_context() -> None:
    original = AttributeError("missing hex")
    exc = StatementError(
        "statement failed",
        "INSERT INTO audit_logs (id) VALUES (?)",
        {"id": "not-a-uuid"},
        original,
    )

    http_exc = create_standardized_error(exc)
    data = getattr(http_exc, "rpc_data", None)

    assert isinstance(data, dict)
    assert data.get("statement") == "INSERT INTO audit_logs (id) VALUES (?)"
    assert "not-a-uuid" in data.get("params", "")
    assert data.get("orig") == "AttributeError: missing hex"


def test_operational_error_includes_sql_context() -> None:
    original = RuntimeError("db down")
    exc = OperationalError(
        "SELECT 1",
        {"ping": True},
        original,
    )

    http_exc = create_standardized_error(exc)
    data = getattr(http_exc, "rpc_data", None)

    assert isinstance(data, dict)
    assert data.get("statement") == "SELECT 1"
    assert "ping" in data.get("params", "")
    assert data.get("orig") == "RuntimeError: db down"


def test_dbapi_error_includes_sql_context() -> None:
    original = ValueError("bad bind")
    exc = DBAPIError(
        "UPDATE audit_logs SET user_id=?",
        ["not-a-uuid"],
        original,
        connection_invalidated=False,
    )

    http_exc = create_standardized_error(exc)
    data = getattr(http_exc, "rpc_data", None)

    assert isinstance(data, dict)
    assert data.get("statement") == "UPDATE audit_logs SET user_id=?"
    assert "not-a-uuid" in data.get("params", "")
    assert data.get("orig") == "ValueError: bad bind"
