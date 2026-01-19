import asyncio
import httpx
import pytest
import pytest_asyncio
import uvicorn

from tigrbl import TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables._base import Base
from tigrbl.specs import F, S, IO, acol
from tigrbl.types import App, Mapped, String


class Item(Base, GUIDPk):
    __tablename__ = "items_hdr"
    __resource__ = "item"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )
    worker_key: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create",),
            out_verbs=("create", "read"),
            header_in="X-Worker-Key",
            header_required_in=True,
        ),
    )
    __tigrbl_cols__ = {
        "id": GUIDPk.id,
        "name": name,
        "worker_key": worker_key,
    }


@pytest_asyncio.fixture()
async def running_app(sync_db_session):
    engine, get_sync_db = sync_db_session

    app = App()
    api = TigrblApp(get_db=get_sync_db)
    api.include_models([Item])
    await api.initialize()
    app.include_router(api.router)

    cfg = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.1)
    try:
        yield "http://127.0.0.1:8000"
    finally:
        server.should_exit = True
        await task


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, status",
    [({}, 422), ({"X-Worker-Key": "alpha"}, 201)],
)
async def test_header_in_out(running_app, headers, status):
    base_url = running_app
    payload = {"name": "foo", "worker_key": "body"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{base_url}/item", json=payload, headers=headers)
    assert resp.status_code == status
    if status == 201:
        body = resp.json()
        assert body["worker_key"] == "alpha"
