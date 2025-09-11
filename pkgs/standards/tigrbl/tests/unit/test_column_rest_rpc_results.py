import pytest
from fastapi.testclient import TestClient

from tigrbl import TigrblApi, alias_ctx
from tigrbl.column import F, IO, S, makeColumn, makeVirtualColumn
from tigrbl.engine.shortcuts import engine as build_engine, mem
from tigrbl.orm.tables import Base
from tigrbl.types import App, Integer, Mapped, String


# Helper to bootstrap API and test client for a model


def _setup_api(model):
    eng = build_engine(mem(async_=False))
    api = TigrblApi(engine=eng)
    api.include_model(model)
    api.initialize()

    app = App()
    app.include_router(api)
    client = TestClient(app)
    return api, client, eng


@pytest.mark.parametrize("use_mapped", [True, False])
@pytest.mark.asyncio
async def test_make_column_only_rest_rpc(use_mapped):
    Base.metadata.clear()

    class Thing(Base):
        __tablename__ = f"mc_only_{'m' if use_mapped else 'u'}"
        if not use_mapped:
            __allow_unmapped__ = True
        if use_mapped:
            id: Mapped[int] = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            name: Mapped[str] = makeColumn(storage=S(type_=String, nullable=False))
        else:
            id = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            name = makeColumn(storage=S(type_=String, nullable=False))

    api, client, eng = _setup_api(Thing)
    try:
        with eng.session() as db:
            created = await api.rpc_call(Thing, "create", {"name": "x"}, db=db)
            db_read = await api.core.Thing.read({"id": created["id"]}, db=db)
            rpc_read = await api.rpc_call(Thing, "read", {"id": created["id"]}, db=db)
        resp = client.get(f"/{Thing.__name__.lower()}/{created['id']}")
        assert resp.status_code == 200
        rest_data = resp.json()
        assert db_read == rpc_read == rest_data == {"id": created["id"], "name": "x"}
    finally:
        raw_eng, _ = eng.raw()
        raw_eng.dispose()


@pytest.mark.parametrize("use_mapped", [True, False])
@pytest.mark.asyncio
async def test_make_virtual_column_only_rest_rpc(use_mapped):
    Base.metadata.clear()

    class Thing(Base):
        __tablename__ = f"mv_only_{'m' if use_mapped else 'u'}"
        if not use_mapped:
            __allow_unmapped__ = True
        if use_mapped:
            id: Mapped[int] = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            code: str = makeVirtualColumn(
                field=F(py_type=str),
                io=IO(out_verbs=("read",)),
                read_producer=lambda obj, ctx: f"v-{obj.id}",
                nullable=True,
            )
        else:
            id = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            code: str = makeVirtualColumn(
                field=F(py_type=str),
                io=IO(out_verbs=("read",)),
                read_producer=lambda obj, ctx: f"v-{obj.id}",
                nullable=True,
            )

    api, client, eng = _setup_api(Thing)
    try:
        with eng.session() as db:
            created = await api.rpc_call(Thing, "create", {}, db=db)
            db_read = await api.core.Thing.read({"id": created["id"]}, db=db)
            rpc_read = await api.rpc_call(Thing, "read", {"id": created["id"]}, db=db)
        resp = client.get(f"/{Thing.__name__.lower()}/{created['id']}")
        assert resp.status_code == 200
        rest_data = resp.json()
        assert db_read == rpc_read == rest_data == {"id": created["id"], "code": None}
    finally:
        raw_eng, _ = eng.raw()
        raw_eng.dispose()


@pytest.mark.parametrize("use_mapped", [True, False])
@pytest.mark.asyncio
async def test_make_column_with_alias_rest_rpc(use_mapped):
    Base.metadata.clear()

    @alias_ctx(read="fetch")
    class Thing(Base):
        __tablename__ = f"mc_alias_{'m' if use_mapped else 'u'}"
        if not use_mapped:
            __allow_unmapped__ = True
        if use_mapped:
            id: Mapped[int] = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            name: Mapped[str] = makeColumn(storage=S(type_=String, nullable=False))
        else:
            id = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            name = makeColumn(storage=S(type_=String, nullable=False))

    api, client, eng = _setup_api(Thing)
    try:
        with eng.session() as db:
            created = await api.rpc_call(Thing, "create", {"name": "y"}, db=db)
            db_read = await api.core.Thing.fetch({"id": created["id"]}, db=db)
            rpc_read = await api.rpc_call(Thing, "fetch", {"id": created["id"]}, db=db)
        resp = client.get(f"/{Thing.__name__.lower()}/{created['id']}")
        assert resp.status_code == 200
        rest_data = resp.json()
        assert db_read == rpc_read == rest_data == {"id": created["id"], "name": "y"}
    finally:
        raw_eng, _ = eng.raw()
        raw_eng.dispose()


@pytest.mark.parametrize("use_mapped", [True, False])
@pytest.mark.asyncio
async def test_make_virtual_column_with_aliases_rest_rpc(use_mapped):
    Base.metadata.clear()

    @alias_ctx(create="register", read="fetch")
    class Thing(Base):
        __tablename__ = f"mv_alias_{'m' if use_mapped else 'u'}"
        if not use_mapped:
            __allow_unmapped__ = True
        if use_mapped:
            id: Mapped[int] = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            code: str = makeVirtualColumn(
                field=F(py_type=str),
                io=IO(out_verbs=("read",)),
                read_producer=lambda obj, ctx: f"v-{obj.id}",
                nullable=True,
            )
        else:
            id = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            code: str = makeVirtualColumn(
                field=F(py_type=str),
                io=IO(out_verbs=("read",)),
                read_producer=lambda obj, ctx: f"v-{obj.id}",
                nullable=True,
            )

    api, client, eng = _setup_api(Thing)
    try:
        with eng.session() as db:
            created = await api.rpc_call(Thing, "register", {}, db=db)
            db_read = await api.core.Thing.fetch({"id": created["id"]}, db=db)
            rpc_read = await api.rpc_call(Thing, "fetch", {"id": created["id"]}, db=db)
        resp = client.get(f"/{Thing.__name__.lower()}/{created['id']}")
        assert resp.status_code == 200
        rest_data = resp.json()
        assert db_read == rpc_read == rest_data == {"id": created["id"], "code": None}
    finally:
        raw_eng, _ = eng.raw()
        raw_eng.dispose()


@pytest.mark.parametrize("use_mapped", [True, False])
@pytest.mark.asyncio
async def test_make_column_and_virtual_rest_rpc(use_mapped):
    Base.metadata.clear()

    class Thing(Base):
        __tablename__ = f"both_{'m' if use_mapped else 'u'}"
        if not use_mapped:
            __allow_unmapped__ = True
        if use_mapped:
            id: Mapped[int] = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            name: Mapped[str] = makeColumn(storage=S(type_=String, nullable=False))
            upper: str = makeVirtualColumn(
                field=F(py_type=str),
                io=IO(out_verbs=("read",)),
                read_producer=lambda obj, ctx: obj.name.upper(),
                nullable=True,
            )
        else:
            id = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            name = makeColumn(storage=S(type_=String, nullable=False))
            upper: str = makeVirtualColumn(
                field=F(py_type=str),
                io=IO(out_verbs=("read",)),
                read_producer=lambda obj, ctx: obj.name.upper(),
                nullable=True,
            )

    api, client, eng = _setup_api(Thing)
    try:
        with eng.session() as db:
            created = await api.rpc_call(Thing, "create", {"name": "Ada"}, db=db)
            db_read = await api.core.Thing.read({"id": created["id"]}, db=db)
            rpc_read = await api.rpc_call(Thing, "read", {"id": created["id"]}, db=db)
        resp = client.get(f"/{Thing.__name__.lower()}/{created['id']}")
        assert resp.status_code == 200
        rest_data = resp.json()
        assert (
            db_read
            == rpc_read
            == rest_data
            == {
                "id": created["id"],
                "name": "Ada",
                "upper": None,
            }
        )
    finally:
        raw_eng, _ = eng.raw()
        raw_eng.dispose()


@pytest.mark.parametrize("use_mapped", [True, False])
@pytest.mark.asyncio
async def test_make_column_and_virtual_with_alias_rest_rpc(use_mapped):
    Base.metadata.clear()

    @alias_ctx(create="register", read="fetch")
    class Thing(Base):
        __tablename__ = f"both_alias_{'m' if use_mapped else 'u'}"
        if not use_mapped:
            __allow_unmapped__ = True
        if use_mapped:
            id: Mapped[int] = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            name: Mapped[str] = makeColumn(storage=S(type_=String, nullable=False))
            upper: str = makeVirtualColumn(
                field=F(py_type=str),
                io=IO(out_verbs=("read",)),
                read_producer=lambda obj, ctx: obj.name.upper(),
                nullable=True,
            )
        else:
            id = makeColumn(
                storage=S(type_=Integer, primary_key=True, autoincrement=True)
            )
            name = makeColumn(storage=S(type_=String, nullable=False))
            upper: str = makeVirtualColumn(
                field=F(py_type=str),
                io=IO(out_verbs=("read",)),
                read_producer=lambda obj, ctx: obj.name.upper(),
                nullable=True,
            )

    api, client, eng = _setup_api(Thing)
    try:
        with eng.session() as db:
            created = await api.rpc_call(Thing, "register", {"name": "Bob"}, db=db)
            db_read = await api.core.Thing.fetch({"id": created["id"]}, db=db)
            rpc_read = await api.rpc_call(Thing, "fetch", {"id": created["id"]}, db=db)
        resp = client.get(f"/{Thing.__name__.lower()}/{created['id']}")
        assert resp.status_code == 200
        rest_data = resp.json()
        assert (
            db_read
            == rpc_read
            == rest_data
            == {
                "id": created["id"],
                "name": "Bob",
                "upper": None,
            }
        )
    finally:
        raw_eng, _ = eng.raw()
        raw_eng.dispose()
