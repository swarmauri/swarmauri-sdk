import pytest
from collections.abc import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.mixins import BulkCapable, GUIDPk, Replaceable
from autoapi.v3.specs import IO, S, F, acol as spec_acol
from autoapi.v3.tables import Base
from autoapi.v3.types import Session, String
from autoapi.v3.opspec import OpSpec


@pytest.fixture()
def api_and_session() -> Iterator[tuple[AutoAPI, Session]]:
    class Widget(Base, GUIDPk, BulkCapable, Replaceable):
        __tablename__ = "widgets_rpc_all_ops"
        __allow_unmapped__ = True
        __autoapi_ops__ = (
            OpSpec(alias="bulk_create", target="bulk_create"),
            OpSpec(alias="bulk_update", target="bulk_update"),
            OpSpec(alias="bulk_replace", target="bulk_replace"),
            OpSpec(alias="bulk_delete", target="bulk_delete"),
            OpSpec(alias="upsert", target="upsert"),
            OpSpec(alias="bulk_upsert", target="bulk_upsert"),
        )

        name = spec_acol(
            storage=S(type_=String(50), nullable=False),
            field=F(py_type=str),
            io=IO(
                in_verbs=(
                    "create",
                    "update",
                    "replace",
                    "upsert",
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_upsert",
                ),
                out_verbs=(
                    "read",
                    "list",
                    "upsert",
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_upsert",
                ),
                mutable_verbs=(
                    "create",
                    "update",
                    "replace",
                    "upsert",
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_upsert",
                ),
            ),
        )

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    api = AutoAPI(get_db=get_db)
    api.include_model(Widget, mount_router=False)
    api.initialize_sync()

    session: Session = SessionLocal()
    try:
        yield api, session
    finally:
        session.close()
        engine.dispose()


async def _op_create(api, db):
    result = await api.rpc.Widget.create({"name": "a"}, db=db)
    assert result["name"] == "a"


async def _op_read(api, db):
    created = await api.rpc.Widget.create({"name": "b"}, db=db)
    result = await api.rpc.Widget.read({"id": created["id"]}, db=db)
    assert result["id"] == created["id"]


async def _op_update(api, db):
    created = await api.rpc.Widget.create({"name": "c"}, db=db)
    result = await api.rpc.Widget.update(
        {"name": "c2"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert result["name"] == "c2"


async def _op_replace(api, db):
    created = await api.rpc.Widget.create({"name": "d"}, db=db)
    result = await api.rpc.Widget.replace(
        {"name": "d2"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert result["name"] == "d2"


async def _op_delete(api, db):
    created = await api.rpc.Widget.create({"name": "e"}, db=db)
    result = await api.rpc.Widget.delete(
        {},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert result["deleted"] == 1


async def _op_list(api, db):
    await api.rpc.Widget.create({"name": "f1"}, db=db)
    await api.rpc.Widget.create({"name": "f2"}, db=db)
    result = await api.rpc.Widget.list({}, db=db)
    assert {r["name"] for r in result} == {"f1", "f2"}


async def _op_clear(api, db):
    await api.rpc.Widget.create({"name": "g1"}, db=db)
    await api.rpc.Widget.create({"name": "g2"}, db=db)
    result = await api.rpc.Widget.clear({"filters": {}}, db=db)
    assert result["deleted"] == 2


async def _op_bulk_create(api, db):
    result = await api.rpc.Widget.bulk_create(
        [{"name": "h1"}, {"name": "h2"}],
        db=db,
    )
    assert {r["name"] for r in result} == {"h1", "h2"}


async def _op_bulk_update(api, db):
    rows = await api.rpc.Widget.bulk_create(
        [{"name": "i1"}, {"name": "i2"}],
        db=db,
    )
    payload = [
        {"id": rows[0]["id"], "name": "i1u"},
        {"id": rows[1]["id"], "name": "i2u"},
    ]
    result = await api.rpc.Widget.bulk_update(None, db=db, ctx={"payload": payload})
    assert {r["name"] for r in result} == {"i1u", "i2u"}


async def _op_bulk_replace(api, db):
    rows = await api.rpc.Widget.bulk_create(
        [{"name": "j1"}, {"name": "j2"}],
        db=db,
    )
    payload = [
        {"id": rows[0]["id"], "name": "j1r"},
        {"id": rows[1]["id"], "name": "j2r"},
    ]
    result = await api.rpc.Widget.bulk_replace(None, db=db, ctx={"payload": payload})
    assert {r["name"] for r in result} == {"j1r", "j2r"}


async def _op_bulk_delete(api, db):
    rows = await api.rpc.Widget.bulk_create(
        [{"name": "k1"}, {"name": "k2"}],
        db=db,
    )
    ids = [r["id"] for r in rows]
    result = await api.rpc.Widget.bulk_delete({"ids": ids}, db=db)
    assert result["deleted"] == 2


async def _op_upsert(api, db):
    created = await api.rpc.Widget.upsert({"name": "u1"}, db=db)
    assert created["name"] == "u1"
    updated = await api.rpc.Widget.upsert({"id": created["id"], "name": "u1u"}, db=db)
    assert updated["name"] == "u1u"


async def _op_bulk_upsert(api, db):
    rows = await api.rpc.Widget.bulk_upsert([{"name": "b1"}, {"name": "b2"}], db=db)
    ids = [r["id"] for r in rows]
    payload = [
        {"id": ids[0], "name": "b1u"},
        {"name": "b3"},
    ]
    result = await api.rpc.Widget.bulk_upsert(None, db=db, ctx={"payload": payload})
    assert {r["name"] for r in result} == {"b1u", "b3"}


OPS = [
    _op_create,
    _op_read,
    _op_update,
    _op_replace,
    _op_delete,
    _op_list,
    _op_clear,
    _op_bulk_create,
    _op_bulk_update,
    _op_bulk_replace,
    _op_bulk_delete,
    _op_upsert,
    _op_bulk_upsert,
]


@pytest.mark.asyncio
@pytest.mark.parametrize("op", OPS, ids=[fn.__name__ for fn in OPS])
async def test_rpc_all_default_op_verbs(op, api_and_session):
    api, db = api_and_session
    await op(api, db)
