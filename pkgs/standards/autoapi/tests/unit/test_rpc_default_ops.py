import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.mixins import BulkCapable, GUIDPk
from autoapi.v3.specs import IO, S, F, acol as spec_acol
from autoapi.v3.tables import Base
from autoapi.v3.types import String


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


@pytest.fixture()
def api_and_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    api = AutoAPI(get_db=get_db)
    api.include_model(Widget, mount_router=False)
    api.initialize_sync()

    session = SessionLocal()
    try:
        yield api, session
    finally:
        session.close()
        engine.dispose()


@pytest.mark.asyncio
async def test_rpc_create(api_and_session):
    api, db = api_and_session
    result = await api.rpc_call(Widget, "create", {"name": "a"}, db=db)
    assert result["name"] == "a"


@pytest.mark.asyncio
async def test_rpc_read(api_and_session):
    api, db = api_and_session
    created = await api.rpc_call(Widget, "create", {"name": "b"}, db=db)
    fetched = await api.rpc_call(Widget, "read", {"id": created["id"]}, db=db)
    assert fetched["id"] == created["id"]


@pytest.mark.asyncio
async def test_rpc_update(api_and_session):
    api, db = api_and_session
    created = await api.rpc_call(Widget, "create", {"name": "c"}, db=db)
    updated = await api.rpc_call(
        Widget,
        "update",
        {"name": "c2"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert updated["name"] == "c2"


@pytest.mark.asyncio
async def test_rpc_replace(api_and_session):
    api, db = api_and_session
    created = await api.rpc_call(Widget, "create", {"name": "d"}, db=db)
    replaced = await api.rpc_call(
        Widget,
        "replace",
        {"name": "d2"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert replaced["name"] == "d2"


@pytest.mark.asyncio
async def test_rpc_delete(api_and_session):
    api, db = api_and_session
    created = await api.rpc_call(Widget, "create", {"name": "e"}, db=db)
    deleted = await api.rpc_call(
        Widget,
        "delete",
        {},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert deleted["deleted"] == 1


@pytest.mark.asyncio
async def test_rpc_list(api_and_session):
    api, db = api_and_session
    await api.rpc_call(Widget, "create", {"name": "f1"}, db=db)
    await api.rpc_call(Widget, "create", {"name": "f2"}, db=db)
    rows = await api.rpc_call(Widget, "list", {}, db=db)
    assert {r["name"] for r in rows} == {"f1", "f2"}


@pytest.mark.asyncio
async def test_rpc_clear(api_and_session):
    api, db = api_and_session
    await api.rpc_call(Widget, "create", {"name": "g1"}, db=db)
    await api.rpc_call(Widget, "create", {"name": "g2"}, db=db)
    result = await api.rpc_call(Widget, "clear", {"filters": {}}, db=db)
    assert result["deleted"] == 2
