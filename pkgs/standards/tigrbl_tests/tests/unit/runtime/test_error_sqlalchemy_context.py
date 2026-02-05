from __future__ import annotations

from sqlalchemy.exc import DBAPIError, OperationalError, StatementError

from tigrbl.runtime.errors.converters import (
    create_standardized_error,
    to_rpc_error_payload,
)


def test_statement_error_includes_sql_context() -> None:
    original = AttributeError("missing hex")
    exc = StatementError(
        "statement failed",
        "INSERT INTO audit_logs (id) VALUES (?)",
        {"id": "not-a-uuid"},
        original,
    )

    http_exc = create_standardized_error(exc)
    rest_payload = {"detail": http_exc.detail}
    rpc_payload = to_rpc_error_payload(http_exc)
    data = rpc_payload.get("data")

    assert rest_payload["detail"]
    assert rpc_payload.get("message")
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
    rest_payload = {"detail": http_exc.detail}
    rpc_payload = to_rpc_error_payload(http_exc)
    data = rpc_payload.get("data")

    assert rest_payload["detail"]
    assert rpc_payload.get("message")
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
    rest_payload = {"detail": http_exc.detail}
    rpc_payload = to_rpc_error_payload(http_exc)
    data = rpc_payload.get("data")

    assert rest_payload["detail"]
    assert rpc_payload.get("message")
    assert isinstance(data, dict)
    assert data.get("statement") == "UPDATE audit_logs SET user_id=?"
    assert "not-a-uuid" in data.get("params", "")
    assert data.get("orig") == "ValueError: bad bind"


def test_dbapi_error_redacts_params_when_hidden() -> None:
    original = AttributeError("missing hex")
    exc = DBAPIError(
        "INSERT INTO audit_logs (id) VALUES (?)",
        ["ffffffff-0000-0000-0000-000000000000"],
        original,
        connection_invalidated=False,
        hide_parameters=True,
    )

    http_exc = create_standardized_error(exc)
    rest_payload = {"detail": http_exc.detail}
    rpc_payload = to_rpc_error_payload(http_exc)
    data = rpc_payload.get("data")

    assert rest_payload["detail"]
    assert rpc_payload.get("message")
    assert isinstance(data, dict)
    assert data.get("params_redacted") is True
    assert data.get("param_keys") == [0]
    assert data.get("param_types") == ["str"]
    assert data.get("statement") is None
    assert "ffffffff-0000-0000-0000-000000000000" not in str(data)
