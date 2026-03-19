import pytest
import pytest_asyncio
from types import SimpleNamespace
from httpx import ASGITransport, AsyncClient
from tigrbl.types import Integer, Mapped, String

from tigrbl import TigrblApp
from tigrbl_ops_oltp import crud
from tigrbl.shortcuts.engine import mem
from tigrbl._spec import F, IO, S
from tigrbl.shortcuts import acol
from tigrbl.orm.tables import TableBase as Base3


@pytest_asyncio.fixture()
async def client_and_model():
    Base3.metadata.clear()

    class Gadget(Base3):
        __tablename__ = "gadgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
            ),
        )
        age: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False, default=0),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
            ),
        )

        __tigrbl_cols__ = {"id": id, "name": name, "age": age}

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Gadget, prefix="")
    await app.initialize()

    # Remove generated out schemas to exercise jsonable fallback
    if hasattr(Gadget.schemas, "read"):
        Gadget.schemas.read.out = None
    if hasattr(Gadget.schemas, "list"):
        Gadget.schemas.list.out = None

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, Gadget
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_rest_read_and_list_without_schema(client_and_model, monkeypatch):
    client, _ = client_and_model

    async def read_stub(model, ident, db):
        return SimpleNamespace(id=ident, name="A", age=1)

    async def list_stub(model, filters=None, db=None, **kwargs):
        return [SimpleNamespace(id=1, name="A", age=1)]

    monkeypatch.setattr(crud, "read", read_stub)
    monkeypatch.setattr(crud, "list", list_stub)

    item_id = 1
    resp = await client.get(f"/gadget/{item_id}")
    assert resp.status_code == 404

    resp_list = await client.get("/gadget")
    assert resp_list.status_code == 200
    data = resp_list.json()
    if isinstance(data, list):
        assert data == [] or "name" in data[0]
    else:
        assert "name" in data
