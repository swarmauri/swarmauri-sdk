import pytest
from collections.abc import Iterator

from tigrbl import TigrblApp
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.op import OpSpec
from tigrbl.orm.mixins import BulkCapable, GUIDPk, Replaceable
from tigrbl.orm.tables import Base
from tigrbl.specs import IO, S, F, acol as spec_acol
from tigrbl.types import Session, String, uuid4


@pytest.fixture()
def app_and_session() -> Iterator[tuple[TigrblApp, Session]]:
    class Widget(Base, GUIDPk, BulkCapable, Replaceable):
        __tablename__ = "widgets_rpc_all_ops"
        __allow_unmapped__ = True
        __tigrbl_ops__ = (
            OpSpec(alias="bulk_create", target="bulk_create"),
            OpSpec(alias="bulk_update", target="bulk_update"),
            OpSpec(alias="bulk_replace", target="bulk_replace"),
            OpSpec(alias="bulk_delete", target="bulk_delete"),
            OpSpec(alias="merge", target="merge"),
            OpSpec(alias="bulk_merge", target="bulk_merge"),
        )

        name = spec_acol(
            storage=S(type_=String(50), nullable=False),
            field=F(py_type=str),
            io=IO(
                in_verbs=(
                    "create",
                    "update",
                    "replace",
                    "merge",
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_merge",
                ),
                out_verbs=(
                    "read",
                    "list",
                    "merge",
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_merge",
                ),
                mutable_verbs=(
                    "create",
                    "update",
                    "replace",
                    "merge",
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_merge",
                ),
            ),
        )

    cfg = mem(async_=False)
<<<<<<< HEAD
    app = TigrblApp(engine=cfg)
    app.include_table(Widget, mount_router=False)
    app.initialize()
=======
    router = TigrblApp(engine=cfg)
    router.include_model(Widget, mount_router=False)
    router.initialize()
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c

    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    session: Session = maker()
    try:
<<<<<<< HEAD
        yield app, session
=======
        yield router, session
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    finally:
        session.close()
        engine.dispose()
        _resolver.set_default(None)


<<<<<<< HEAD
async def _op_create(app, db):
    result = await app.rpc.Widget.create({"name": "a"}, db=db)
    assert result["name"] == "a"


async def _op_read(app, db):
    created = await app.rpc.Widget.create({"name": "b"}, db=db)
    result = await app.rpc.Widget.read({"id": created["id"]}, db=db)
    assert result["id"] == created["id"]


async def _op_update(app, db):
    created = await app.rpc.Widget.create({"name": "c"}, db=db)
    result = await app.rpc.Widget.update(
=======
async def _op_create(router, db):
    result = await router.rpc.Widget.create({"name": "a"}, db=db)
    assert result["name"] == "a"


async def _op_read(router, db):
    created = await router.rpc.Widget.create({"name": "b"}, db=db)
    result = await router.rpc.Widget.read({"id": created["id"]}, db=db)
    assert result["id"] == created["id"]


async def _op_update(router, db):
    created = await router.rpc.Widget.create({"name": "c"}, db=db)
    result = await router.rpc.Widget.update(
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
        {"name": "c2"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert result["name"] == "c2"


<<<<<<< HEAD
async def _op_replace(app, db):
    created = await app.rpc.Widget.create({"name": "d"}, db=db)
    result = await app.rpc.Widget.replace(
=======
async def _op_replace(router, db):
    created = await router.rpc.Widget.create({"name": "d"}, db=db)
    result = await router.rpc.Widget.replace(
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
        {"name": "d2"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert result["name"] == "d2"


<<<<<<< HEAD
async def _op_delete(app, db):
    created = await app.rpc.Widget.create({"name": "e"}, db=db)
    result = await app.rpc.Widget.delete(
=======
async def _op_delete(router, db):
    created = await router.rpc.Widget.create({"name": "e"}, db=db)
    result = await router.rpc.Widget.delete(
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
        {},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    assert result["deleted"] == 1


<<<<<<< HEAD
async def _op_list(app, db):
    await app.rpc.Widget.create({"name": "f1"}, db=db)
    await app.rpc.Widget.create({"name": "f2"}, db=db)
    result = await app.rpc.Widget.list({}, db=db)
    assert {r["name"] for r in result} == {"f1", "f2"}


async def _op_clear(app, db):
    await app.rpc.Widget.create({"name": "g1"}, db=db)
    await app.rpc.Widget.create({"name": "g2"}, db=db)
    result = await app.rpc.Widget.clear({"filters": {}}, db=db)
    assert result["deleted"] == 2


async def _op_bulk_create(app, db):
    result = await app.rpc.Widget.bulk_create(
=======
async def _op_list(router, db):
    await router.rpc.Widget.create({"name": "f1"}, db=db)
    await router.rpc.Widget.create({"name": "f2"}, db=db)
    result = await router.rpc.Widget.list({}, db=db)
    assert {r["name"] for r in result} == {"f1", "f2"}


async def _op_clear(router, db):
    await router.rpc.Widget.create({"name": "g1"}, db=db)
    await router.rpc.Widget.create({"name": "g2"}, db=db)
    result = await router.rpc.Widget.clear({"filters": {}}, db=db)
    assert result["deleted"] == 2


async def _op_bulk_create(router, db):
    result = await router.rpc.Widget.bulk_create(
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
        [{"name": "h1"}, {"name": "h2"}],
        db=db,
    )
    assert {r["name"] for r in result} == {"h1", "h2"}


<<<<<<< HEAD
async def _op_bulk_update(app, db):
    rows = await app.rpc.Widget.bulk_create(
=======
async def _op_bulk_update(router, db):
    rows = await router.rpc.Widget.bulk_create(
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
        [{"name": "i1"}, {"name": "i2"}],
        db=db,
    )
    payload = [
        {"id": rows[0]["id"], "name": "i1u"},
        {"id": rows[1]["id"], "name": "i2u"},
    ]
<<<<<<< HEAD
    result = await app.rpc.Widget.bulk_update(payload, db=db)
    assert {r["name"] for r in result} == {"i1u", "i2u"}


async def _op_bulk_replace(app, db):
    rows = await app.rpc.Widget.bulk_create(
=======
    result = await router.rpc.Widget.bulk_update(payload, db=db)
    assert {r["name"] for r in result} == {"i1u", "i2u"}


async def _op_bulk_replace(router, db):
    rows = await router.rpc.Widget.bulk_create(
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
        [{"name": "j1"}, {"name": "j2"}],
        db=db,
    )
    payload = [
        {"id": rows[0]["id"], "name": "j1r"},
        {"id": rows[1]["id"], "name": "j2r"},
    ]
<<<<<<< HEAD
    result = await app.rpc.Widget.bulk_replace(payload, db=db)
    assert {r["name"] for r in result} == {"j1r", "j2r"}


async def _op_bulk_delete(app, db):
    rows = await app.rpc.Widget.bulk_create(
=======
    result = await router.rpc.Widget.bulk_replace(payload, db=db)
    assert {r["name"] for r in result} == {"j1r", "j2r"}


async def _op_bulk_delete(router, db):
    rows = await router.rpc.Widget.bulk_create(
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
        [{"name": "k1"}, {"name": "k2"}],
        db=db,
    )
    ids = [r["id"] for r in rows]
<<<<<<< HEAD
    result = await app.rpc.Widget.bulk_delete(ids[:1], db=db)
    assert result["deleted"] == 1
    remaining = await app.rpc.Widget.list({}, db=db)
    assert len(remaining) == 1 and remaining[0]["id"] == ids[1]


async def _op_merge(app, db):
    ident = str(uuid4())
    created = await app.rpc.Widget.merge({"id": ident, "name": "u1"}, db=db)
    assert created["name"] == "u1"
    updated = await app.rpc.Widget.merge({"id": ident, "name": "u1u"}, db=db)
    assert updated["name"] == "u1u"


async def _op_bulk_merge(app, db):
    rows = await app.rpc.Widget.bulk_merge(
=======
    result = await router.rpc.Widget.bulk_delete(ids[:1], db=db)
    assert result["deleted"] == 1
    remaining = await router.rpc.Widget.list({}, db=db)
    assert len(remaining) == 1 and remaining[0]["id"] == ids[1]


async def _op_merge(router, db):
    ident = str(uuid4())
    created = await router.rpc.Widget.merge({"id": ident, "name": "u1"}, db=db)
    assert created["name"] == "u1"
    updated = await router.rpc.Widget.merge({"id": ident, "name": "u1u"}, db=db)
    assert updated["name"] == "u1u"


async def _op_bulk_merge(router, db):
    rows = await router.rpc.Widget.bulk_merge(
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
        [{"id": str(uuid4()), "name": "b1"}, {"id": str(uuid4()), "name": "b2"}],
        db=db,
    )
    ids = [r["id"] for r in rows]
    payload = [
        {"id": ids[0], "name": "b1u"},
        {"id": str(uuid4()), "name": "b3"},
    ]
<<<<<<< HEAD
    result = await app.rpc.Widget.bulk_merge(None, db=db, ctx={"payload": payload})
=======
    result = await router.rpc.Widget.bulk_merge(None, db=db, ctx={"payload": payload})
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
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
    _op_merge,
    _op_bulk_merge,
]


@pytest.mark.asyncio
@pytest.mark.parametrize("op", OPS, ids=[fn.__name__ for fn in OPS])
<<<<<<< HEAD
async def test_rpc_all_default_op_verbs(op, app_and_session):
    app, db = app_and_session
    await op(app, db)
=======
async def test_rpc_all_default_op_verbs(op, api_and_session):
    router, db = api_and_session
    await op(router, db)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
