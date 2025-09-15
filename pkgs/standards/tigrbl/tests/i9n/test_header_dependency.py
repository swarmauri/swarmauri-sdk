import asyncio

import httpx
import pytest
import uvicorn

from tigrbl import TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import App, Mapped, String


async def _run_server(
    model: type, sync_db_session
) -> tuple[uvicorn.Server, asyncio.Task, str]:
    """Start a uvicorn server for the given model and return server, task, base_url."""
    engine, get_sync_db = sync_db_session
    app = App()
    api = TigrblApp(get_db=get_sync_db)
    api.include_models([model])
    await api.initialize()
    app.include_router(api.router)
    cfg = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.1)
    return server, task, "http://127.0.0.1:8000"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_header_in_persists_on_create(sync_db_session):
    class Item(Base, GUIDPk):
        __tablename__ = "items_header_create"
        __resource__ = "item"
        secret: Mapped[str | None] = acol(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create",), out_verbs=("create", "read"), header_in="X-Secret"
            ),
        )

    server, task, base_url = await _run_server(Item, sync_db_session)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/item", headers={"X-Secret": "abc"}, json={}
            )
            assert resp.status_code == 201
            created = resp.json()
            resp_read = await client.get(f"{base_url}/item/{created['id']}")
            assert resp_read.status_code == 200
            assert resp_read.json()["secret"] == "abc"
    finally:
        server.should_exit = True
        await task


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_header_missing_sets_none(sync_db_session):
    class Item(Base, GUIDPk):
        __tablename__ = "items_header_missing"
        __resource__ = "item"
        secret: Mapped[str | None] = acol(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",), header_in="X-Secret"),
        )

    server, task, base_url = await _run_server(Item, sync_db_session)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{base_url}/item", json={})
            assert resp.status_code == 201
            created = resp.json()
            resp_read = await client.get(f"{base_url}/item/{created['id']}")
            assert resp_read.status_code == 200
            assert resp_read.json()["secret"] is None
    finally:
        server.should_exit = True
        await task


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_header_ignored_for_unlisted_verbs(sync_db_session):
    class Item(Base, GUIDPk):
        __tablename__ = "items_header_unlisted"
        __resource__ = "item"
        secret: Mapped[str | None] = acol(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str),
            io=IO(in_verbs=("update",), out_verbs=("read",), header_in="X-Secret"),
        )

    server, task, base_url = await _run_server(Item, sync_db_session)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/item", headers={"X-Secret": "abc"}, json={}
            )
            assert resp.status_code == 201
            created = resp.json()
            resp_read = await client.get(f"{base_url}/item/{created['id']}")
            assert resp_read.status_code == 200
            assert resp_read.json()["secret"] is None
    finally:
        server.should_exit = True
        await task
