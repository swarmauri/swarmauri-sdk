import httpx
import pytest
import pytest_asyncio
from sqlalchemy.exc import StatementError

from tigrbl import Base, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Boolean, Integer, Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


PII_EMAIL = "jane.doe@example.com"
PII_SSN = "123-45-6789"
SECRET_TOKEN = "super-secret-token"


class Account(Base, GUIDPk):
    __tablename__ = "accounts_redaction"
    __resource__ = "account"

    email: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )
    ssn: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )
    age: Mapped[int] = acol(
        storage=S(Integer, nullable=False),
        field=F(py_type=int),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )

    __tigrbl_cols__ = {
        "id": GUIDPk.id,
        "email": email,
        "ssn": ssn,
        "age": age,
    }

    @op_ctx(alias="leak", target="custom", arity="collection")
    def leak(cls, ctx):
        params = {
            "email": PII_EMAIL,
            "ssn": PII_SSN,
            "token": SECRET_TOKEN,
            "age": 42,
        }
        raise StatementError(
            "failed to persist account",
            "INSERT INTO accounts_redaction (email, ssn, token, age) "
            "VALUES (:email, :ssn, :token, :age)",
            params,
            RuntimeError("db down"),
            hide_parameters=True,
        )


class Credential(Base, GUIDPk):
    __tablename__ = "credentials_redaction"
    __resource__ = "credential"

    provider: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )
    active: Mapped[bool] = acol(
        storage=S(Boolean, nullable=False, default=True),
        field=F(py_type=bool),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )

    __tigrbl_cols__ = {
        "id": GUIDPk.id,
        "provider": provider,
        "active": active,
    }

    @op_ctx(alias="leak", target="custom", arity="collection")
    def leak(cls, ctx):
        params = [SECRET_TOKEN, 7, False]
        raise StatementError(
            "failed to persist credential",
            "UPDATE credentials_redaction SET active=? WHERE provider=?",
            params,
            RuntimeError("db down"),
            hide_parameters=True,
        )


class AuditEvent(Base, GUIDPk):
    __tablename__ = "audit_events_redaction"
    __resource__ = "audit"

    event: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )
    count: Mapped[int] = acol(
        storage=S(Integer, nullable=False, default=0),
        field=F(py_type=int),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )

    __tigrbl_cols__ = {
        "id": GUIDPk.id,
        "event": event,
        "count": count,
    }

    @op_ctx(alias="probe", target="custom", arity="collection")
    def probe(cls, ctx):
        params = {"event": "safe", "count": 3}
        raise StatementError(
            "failed to persist audit event",
            "INSERT INTO audit_events_redaction (event, count) VALUES (:event, :count)",
            params,
            RuntimeError("db down"),
            hide_parameters=False,
        )


@pytest_asyncio.fixture()
async def running_error_app():
    app = TigrblApp(engine=mem(async_=False))
    app.include_models([Account, Credential, AuditEvent])
    app.mount_jsonrpc()
    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hide_parameters_redacts_pii_in_rest(running_error_app):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{running_error_app}/account/leak", json={})

    assert response.status_code == 500
    detail = response.json().get("detail", "")
    assert PII_EMAIL not in detail
    assert PII_SSN not in detail
    assert SECRET_TOKEN not in detail


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hide_parameters_redacts_pii_in_rpc(running_error_app):
    payload = {"jsonrpc": "2.0", "method": "Account.leak", "params": {}, "id": 1}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{running_error_app}/rpc/", json=payload)

    assert response.status_code == 200
    error = response.json()["error"]
    data = error["data"]
    assert data["params_redacted"] is True
    assert set(data["param_keys"]) == {"email", "ssn", "token", "age"}
    assert data["param_types"]["email"] == "str"
    assert data["param_types"]["age"] == "int"
    assert "statement" not in data
    assert "params" not in data
    response_text = response.text
    assert PII_EMAIL not in response_text
    assert PII_SSN not in response_text
    assert SECRET_TOKEN not in response_text


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hide_parameters_redacts_list_params_in_rpc(running_error_app):
    payload = {"jsonrpc": "2.0", "method": "Credential.leak", "params": {}, "id": 2}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{running_error_app}/rpc/", json=payload)

    assert response.status_code == 200
    data = response.json()["error"]["data"]
    assert data["params_redacted"] is True
    assert data["param_keys"] == [0, 1, 2]
    assert data["param_types"] == ["str", "int", "bool"]
    assert "statement" not in data
    assert "params" not in data
    assert SECRET_TOKEN not in response.text


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_show_params_when_not_hidden_in_rpc(running_error_app):
    payload = {"jsonrpc": "2.0", "method": "AuditEvent.probe", "params": {}, "id": 3}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{running_error_app}/rpc/", json=payload)

    assert response.status_code == 200
    data = response.json()["error"]["data"]
    assert data["statement"].startswith("INSERT INTO audit_events_redaction")
    assert "params" in data
    assert data["params"] == "{'event': 'safe', 'count': 3}"
    assert data.get("params_redacted") is not True
