import pytest
import pytest_asyncio
from tigrbl.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped

from tigrbl import TigrblApp as Tigrblv3
from tigrbl.engine.shortcuts import mem
from tigrbl.specs import F, IO, S, acol
from tigrbl.orm.tables import Base as Base3
from tigrbl.core import crud


@pytest_asyncio.fixture()
async def client_and_model():
    Base3.metadata.clear()

    class Widget(Base3):
        __tablename__ = "widgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read", "list")),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(required_in=("create",)),
            io=IO(in_verbs=("create", "update")),
        )

        __tigrbl_cols__ = {"id": id, "name": name}

    app = App()
    api = Tigrblv3(engine=mem())
    api.include_model(Widget, prefix="")
    await api.initialize()
    # Remove output schemas to trigger fallback serialization
    Widget.schemas.read.out = None
    Widget.schemas.list.out = None

    app.include_router(api.router)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, Widget
    finally:
        await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_read_and_list_with_row_results(client_and_model, monkeypatch):
    client, Widget = client_and_model

    async def read_row(model, ident, db):
        stmt = select(model).where(getattr(model, "id") == ident)
        res = await db.execute(stmt)
        return res.first()  # returns Row

    async def list_rows(model, filters=None, db=None, **kwargs):
        stmt = select(model)
        res = await db.execute(stmt)
        return res.all()  # list[Row]

    monkeypatch.setattr(crud, "read", read_row)
    monkeypatch.setattr(crud, "list", list_rows)

    created = await client.post("/widget", json={"name": "A"})
    item_id = created.json()["id"]

    resp = await client.get(f"/widget/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id

    resp_list = await client.get("/widget")
    assert resp_list.status_code == 200
    data = resp_list.json()
    assert isinstance(data, list)
    assert data[0]["id"] == item_id
