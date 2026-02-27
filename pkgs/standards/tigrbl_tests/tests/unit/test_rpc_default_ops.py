import pytest
from collections.abc import Iterator

from tigrbl import TigrblApp
from tigrbl.orm.mixins import BulkCapable, GUIDPk
from tigrbl._spec import IOSpec as IO, StorageSpec as S, FieldSpec as F
from tigrbl.shortcuts.column import acol as spec_acol
from tigrbl.orm.tables import Base
from tigrbl.types import Session, String
from tigrbl.shortcuts.engine import mem
from tigrbl import resolver as _resolver


@pytest.fixture()
def app_and_session() -> Iterator[tuple[TigrblApp, Session, type[Base]]]:
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

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget, mount_router=False)
    app.initialize()
    prov = _resolver.resolve_provider()
    _, SessionLocal = prov.ensure()

    session: Session = SessionLocal()
    try:
        yield app, session, Widget
    finally:
        session.close()


@pytest.mark.asyncio
async def test_rpc_create(app_and_session):
    app, db, Widget = app_and_session
    result = await app.rpc_call(Widget, "create", {"name": "a"}, db=db)
    assert result["name"] == "a"


@pytest.mark.asyncio
async def test_rpc_read(app_and_session):
    app, db, Widget = app_and_session
    created = await app.rpc_call(Widget, "create", {"name": "b"}, db=db)
    fetched = await app.rpc_call(Widget, "read", {"id": created["id"]}, db=db)
    assert fetched["id"] == created["id"]


@pytest.mark.asyncio
async def test_rpc_update(app_and_session):
    app, db, Widget = app_and_session
    created = await app.rpc_call(Widget, "create", {"name": "c"}, db=db)
    updated = await app.rpc_call(
        Widget,
        "update",
        {"id": created["id"], "name": "c2"},
        db=db,
    )
    assert updated["name"] == "c2"


@pytest.mark.asyncio
async def test_rpc_replace(app_and_session):
    app, db, Widget = app_and_session
    created = await app.rpc_call(Widget, "create", {"name": "d"}, db=db)
    replaced = await app.rpc_call(
        Widget,
        "replace",
        {"id": created["id"], "name": "d2"},
        db=db,
    )
    assert replaced["name"] == "d2"


@pytest.mark.asyncio
async def test_rpc_delete(app_and_session):
    app, db, Widget = app_and_session
    created = await app.rpc_call(Widget, "create", {"name": "e"}, db=db)
    deleted = await app.rpc_call(
        Widget,
        "delete",
        {"id": created["id"]},
        db=db,
    )
    assert deleted["deleted"] == 1


@pytest.mark.asyncio
async def test_rpc_list(app_and_session):
    app, db, Widget = app_and_session
    await app.rpc_call(Widget, "create", {"name": "f1"}, db=db)
    await app.rpc_call(Widget, "create", {"name": "f2"}, db=db)
    rows = await app.rpc_call(Widget, "list", {}, db=db)
    assert {r["name"] for r in rows} == {"f1", "f2"}


@pytest.mark.asyncio
async def test_rpc_clear(app_and_session):
    app, db, Widget = app_and_session
    await app.rpc_call(Widget, "create", {"name": "g1"}, db=db)
    await app.rpc_call(Widget, "create", {"name": "g2"}, db=db)
    result = await app.rpc_call(Widget, "clear", {"filters": {}}, db=db)
    assert result["deleted"] == 2
