import pytest
import pytest_asyncio
from tigrbl.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped

from tigrbl import TigrblApp as Tigrblv3
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.specs import S, acol
from tigrbl.orm.tables import Base as Base3


@pytest_asyncio.fixture()
async def client():
    Base3.metadata.clear()
    from tigrbl.schema.builder import _SchemaCache as _SchemaCache_v3

    _SchemaCache_v3.clear()

    class Widget(Base3):
        __tablename__ = "widgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(storage=S(type_=String))

        __tigrbl_cols__ = {"id": id, "name": name}

    api = Tigrblv3(engine=mem())
    api.include_model(Widget, prefix="")
    await api.initialize()
    prov = _resolver.resolve_provider()
    engine, session_maker = prov.ensure()
    async with session_maker() as session:
        session.add(Widget(name="A"))
        await session.commit()

    # Monkeypatch crud functions to return raw Row objects
    from tigrbl.core import crud

    original_read = crud.read
    original_list = crud.list

    async def row_read(model, ident, db):
        stmt = select(model).where(getattr(model, "id") == ident)
        result = await db.execute(stmt)
        return result.first()  # Row object

    async def row_list(model, filters, *, db, skip=None, limit=None, sort=None):  # noqa: ARG001
        result = await db.execute(select(model))
        return result.all()  # list[Row]

    crud.read = row_read  # type: ignore
    crud.list = row_list  # type: ignore

    app = App()
    app.include_router(api.router)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client
    finally:
        await client.aclose()
        await engine.dispose()
        crud.read = original_read  # type: ignore
        crud.list = original_list  # type: ignore
        Base3.metadata.clear()
        _SchemaCache_v3.clear()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_read_and_list_with_row_result(client):
    resp = await client.get("/widget/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "A"

    resp = await client.get("/widget")
    assert resp.status_code == 200
    assert resp.json()[0]["name"] == "A"
