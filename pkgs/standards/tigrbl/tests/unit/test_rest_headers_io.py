from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.specs import IO, F, S, acol
from tigrbl.types import App


@pytest_asyncio.fixture()
async def app_client() -> AsyncIterator[tuple[AsyncClient, TigrblApp, type]]:
    Base.metadata.clear()

    class Doc(Base):
        __tablename__ = "docs"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, required_in=("create",)),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )
        # inbound header used on create/update, also echoed on read
        worker_key: Mapped[str] = acol(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create", "update"),
                out_verbs=("read",),
                header_in="X-Worker-Key",
                header_out="X-Worker-Key",
            ),
        )
        __tigrbl_cols__ = {
            "id": id,
            "name": name,
            "worker_key": worker_key,
        }

    cfg = mem()
    app = TigrblApp(engine=cfg)
    app.include_model(Doc, prefix="")
    app.attach_diagnostics()
    await app.initialize()

    host = App()
    host.include_router(app.router)
    transport = ASGITransport(app=host)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, app, Doc
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_header_in_merged_on_create_and_update(app_client):
    client, app, Doc = app_client

    # create with inbound header
    r = await client.post(
        "/doc",
        headers={"X-Worker-Key": "abc123"},
        json={"name": "first"},
    )
    assert r.status_code in (200, 201), r.text
    created = r.json()
    assert created.get("name") == "first"
    # worker_key should persist and be visible on read
    doc_id = created.get("id")
    r2 = await client.get(f"/doc/{doc_id}")
    assert r2.status_code == 200, r2.text
    assert r2.json().get("worker_key") == "abc123"

    # update with different header; expect change to persist
    r3 = await client.patch(
        f"/doc/{doc_id}",
        headers={"X-Worker-Key": "xyz"},
        json={"name": "second"},
    )
    assert r3.status_code == 200, r3.text
    r4 = await client.get(f"/doc/{doc_id}")
    assert r4.status_code == 200, r4.text
    body = r4.json()
    assert body.get("name") == "second"
    assert body.get("worker_key") == "xyz"


@pytest.mark.asyncio
async def test_header_out_emitted_on_read(app_client):
    client, app, Doc = app_client

    # create document (no need to pass worker header here)
    r = await client.post("/doc", json={"name": "n"})
    assert r.status_code in (200, 201), r.text
    doc_id = r.json().get("id")

    # read and verify worker header is emitted from payload via header_out
    r2 = await client.get(f"/doc/{doc_id}")
    assert r2.status_code == 200, r2.text
    assert r2.headers.get("x-worker-key") is not None
