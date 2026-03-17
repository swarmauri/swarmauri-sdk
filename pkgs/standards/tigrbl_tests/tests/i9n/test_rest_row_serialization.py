import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from tigrbl.types import Integer, Mapped, String
from tigrbl import TigrblApp, TigrblRouter
import tigrbl_ops_oltp as _oltp_pkg
from tigrbl.core import crud
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.tables import TableBase as Base3
from tigrbl._spec import IO, F, S
from tigrbl.shortcuts.column import acol


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

    app = TigrblApp(engine=mem())
    router = TigrblRouter(engine=mem())
    app.include_table(Widget, prefix="")
    await app.initialize()
    # Remove output schemas to trigger fallback serialization
    if hasattr(Widget.schemas, "read"):
        Widget.schemas.read.out = None
    if hasattr(Widget.schemas, "list"):
        Widget.schemas.list.out = None

    app.include_router(router)
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

    # Insert a row so DB-backed stubs return data
    create_res = await client.post("/widget", json={"name": "A"})
    assert create_res.status_code == 201
    item_id = create_res.json()["id"]

    monkeypatch.setattr(crud, "read", read_row)
    monkeypatch.setattr(crud, "list", list_rows)
    monkeypatch.setattr(_oltp_pkg, "read", read_row)
    monkeypatch.setattr(_oltp_pkg, "list", list_rows)

    resp = await client.get(f"/widget/{item_id}")
    assert resp.status_code == 200
    assert "id" in resp.json()

    resp_list = await client.get("/widget")
    assert resp_list.status_code == 200
    data = resp_list.json()
    if isinstance(data, list):
        assert "id" in data[0]
    else:
        assert "id" in data
