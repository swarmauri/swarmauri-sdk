import pytest
from collections.abc import Iterator

from tigrbl import TigrblApp
from tigrbl.orm.mixins import BulkCapable, GUIDPk
from tigrbl.specs import IO, S, F, acol as spec_acol
from tigrbl.orm.tables import Base
from tigrbl.types import Session, String
from tigrbl.engine.shortcuts import mem
from tigrbl.engine import resolver as _resolver


@pytest.fixture()
def api_and_session() -> Iterator[tuple[TigrblApp, Session, type[Base]]]:
    class Widget(Base, GUIDPk, BulkCapable):
        __tablename__ = "widgets_rpc_ops"
        __allow_unmapped__ = True

        name = spec_acol(
            storage=S(type_=String(50), nullable=False),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                mutable_verbs=("create", "update", "replace"),
            ),
        )

    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget, mount_router=False)
    api.initialize()
    prov = _resolver.resolve_provider()
    _, SessionLocal = prov.ensure()

    session: Session = SessionLocal()
    try:
        yield api, session, Widget
    finally:
        session.close()


@pytest.mark.asyncio
async def test_rpc_create(api_and_session):
    api, db, Widget = api_and_session
    result = await api.rpc_call(Widget, "create", {"name": "a"}, db=db)
    assert result["name"] == "a"


@pytest.mark.asyncio
async def test_rpc_read(api_and_session):
    api, db, Widget = api_and_session
    created = await api.rpc_call(Widget, "create", {"name": "b"}, db=db)
    fetched = await api.rpc_call(Widget, "read", {"id": created["id"]}, db=db)
    assert fetched["id"] == created["id"]


@pytest.mark.asyncio
async def test_rpc_update(api_and_session):
    api, db, Widget = api_and_session
    created = await api.rpc_call(Widget, "create", {"name": "c"}, db=db)
    updated = await api.rpc_call(
        Widget,
        "update",
        {"id": created["id"], "name": "c2"},
        db=db,
    )
    assert updated["name"] == "c2"


@pytest.mark.asyncio
async def test_rpc_replace(api_and_session):
    api, db, Widget = api_and_session
    created = await api.rpc_call(Widget, "create", {"name": "d"}, db=db)
    replaced = await api.rpc_call(
        Widget,
        "replace",
        {"id": created["id"], "name": "d2"},
        db=db,
    )
    assert replaced["name"] == "d2"


@pytest.mark.asyncio
async def test_rpc_delete(api_and_session):
    api, db, Widget = api_and_session
    created = await api.rpc_call(Widget, "create", {"name": "e"}, db=db)
    deleted = await api.rpc_call(
        Widget,
        "delete",
        {"id": created["id"]},
        db=db,
    )
    assert deleted["deleted"] == 1


@pytest.mark.asyncio
async def test_rpc_list(api_and_session):
    api, db, Widget = api_and_session
    await api.rpc_call(Widget, "create", {"name": "f1"}, db=db)
    await api.rpc_call(Widget, "create", {"name": "f2"}, db=db)
    rows = await api.rpc_call(Widget, "list", {}, db=db)
    assert {r["name"] for r in rows} == {"f1", "f2"}


@pytest.mark.asyncio
async def test_rpc_clear(api_and_session):
    api, db, Widget = api_and_session
    await api.rpc_call(Widget, "create", {"name": "g1"}, db=db)
    await api.rpc_call(Widget, "create", {"name": "g2"}, db=db)
    result = await api.rpc_call(Widget, "clear", {"filters": {}}, db=db)
    assert result["deleted"] == 2
