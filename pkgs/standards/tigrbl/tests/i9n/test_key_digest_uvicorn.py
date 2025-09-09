from uuid import uuid4

import asyncio
import httpx
import pytest
import uvicorn
import pytest_asyncio

from tigrbl.v3 import AutoApp
from tigrbl.v3.orm.mixins import (
    GUIDPk,
    Created,
    LastUsed,
    ValidityWindow,
    KeyDigest,
    tzutcnow,
    tzutcnow_plus_day,
)
from tigrbl.v3.orm.mixins.utils import CRUD_IO
from tigrbl.v3.orm.tables._base import Base
from tigrbl.v3.specs import F, S, acol
from tigrbl.v3.types import App, Mapped, String
from sqlalchemy import inspect


class ApiKey(Base, GUIDPk, Created, LastUsed, ValidityWindow, KeyDigest):
    __abstract__ = False
    __tablename__ = "apikeys_uvicorn"
    __resource__ = "apikey"

    label: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(constraints={"max_length": 120}),
        io=CRUD_IO,
    )
    service_id: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(constraints={"max_length": 120}),
        io=CRUD_IO,
    )


@pytest_asyncio.fixture()
async def running_app(sync_db_session):
    engine, get_sync_db = sync_db_session

    app = App()
    api = AutoApp(get_db=get_sync_db)
    api.include_models([ApiKey])
    await api.initialize()
    app.include_router(api.router)

    cfg = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.1)
    try:
        yield ("http://127.0.0.1:8000", engine)
    finally:
        server.should_exit = True
        await task


def _payload() -> dict:
    now = tzutcnow()
    return {
        "label": "test",
        "service_id": str(uuid4()),
        "valid_from": now.isoformat(),
        "valid_to": tzutcnow_plus_day().isoformat(),
    }


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_create_apikey_success(running_app):
    base_url, _ = running_app
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{base_url}/apikey", json=_payload())
    assert resp.status_code == 201


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_create_response_fields(running_app):
    base_url, _ = running_app
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{base_url}/apikey", json=_payload())
    body = resp.json()
    expected = {
        "api_key",
        "label",
        "service_id",
        "valid_from",
        "valid_to",
        "digest",
        "last_used_at",
        "created_at",
        "id",
    }
    assert set(body) == expected


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_persisted_columns(running_app):
    base_url, engine = running_app
    async with httpx.AsyncClient() as client:
        await client.post(f"{base_url}/apikey", json=_payload())
    inspector = inspect(engine)
    cols = {col["name"] for col in inspector.get_columns("apikeys_uvicorn")}
    expected = {
        "label",
        "service_id",
        "valid_from",
        "valid_to",
        "digest",
        "last_used_at",
        "created_at",
        "id",
    }
    assert cols == expected


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_read_excludes_api_key(running_app):
    base_url, _ = running_app
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{base_url}/apikey", json=_payload())
        created = resp.json()
        fetched = await client.get(f"{base_url}/apikey/{created['id']}")
    body = fetched.json()
    assert "api_key" not in body
    assert body["digest"] == created["digest"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rejects_digest_in_request(running_app):
    base_url, _ = running_app
    bad = _payload() | {"digest": "x"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{base_url}/apikey", json=bad)
    assert resp.status_code == 422


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rejects_api_key_in_request(running_app):
    base_url, _ = running_app
    bad = _payload() | {"api_key": "raw"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{base_url}/apikey", json=bad)
    assert resp.status_code == 422
