from __future__ import annotations

import asyncio

import pytest
from tigrbl.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import String, create_engine
from sqlalchemy.orm import sessionmaker

from tigrbl.bindings.model import bind
from tigrbl.hook import hook_ctx
from tigrbl.op.types import PHASES
from tigrbl.runtime import system as runtime_system
from tigrbl.runtime.executor import _Ctx
from tigrbl.runtime.kernel import build_phase_chains
from tigrbl.specs import IO, S, acol
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl import core as _core


def _fresh_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


@pytest.mark.i9n
def test_request_and_response_schemas():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_schema"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    in_model = Gadget.schemas.create.in_(name="gizmo")
    db = _fresh_session()
    obj = asyncio.run(_core.create(Gadget, db=db, data=in_model.model_dump()))
    out_model = Gadget.schemas.read.out.model_validate(obj)
    assert out_model.name == "gizmo"


@pytest.mark.i9n
def test_columns_bound():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_columns"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    assert "name" in Gadget.__table__.c
    assert "name" in Gadget.__tigrbl_cols__


@pytest.mark.i9n
def test_defaults_value_resolution():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_defaults"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False, default="anon"),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    db = _fresh_session()
    obj = asyncio.run(_core.create(Gadget, db=db, data={}))
    assert obj.name == "anon"


@pytest.mark.i9n
def test_internal_model_opspec_binding():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_internal"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    sp = Gadget.opspecs.by_alias["create"][0]
    assert sp.table is Gadget


@pytest.mark.i9n
def test_openapi_includes_path():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_openapi"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    app = App()
    app.include_router(Gadget.rest.router)
    schema = app.openapi()
    assert "/gadget" in schema["paths"]


@pytest.mark.i9n
def test_storage_and_sqlalchemy_persist():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_storage"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    db = _fresh_session()
    asyncio.run(_core.create(Gadget, db=db, data={"name": "stored"}))
    fetched = db.query(Gadget).one()
    assert fetched.name == "stored"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_routes_bound():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_rest"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    session = _fresh_session()

    def get_db():
        return session

    Gadget.__tigrbl_get_db__ = staticmethod(get_db)  # type: ignore[attr-defined]
    bind(Gadget)
    app = App()
    app.include_router(Gadget.rest.router)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/gadget")
        assert res.status_code in {200, 404}


@pytest.mark.i9n
def test_rpc_method_bound():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_rpc"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    db = _fresh_session()
    res = asyncio.run(Gadget.rpc.create({"name": "rpc"}, db=db))
    assert res["name"] == "rpc"
    assert db.query(Gadget).filter_by(name="rpc").count() == 1


@pytest.mark.i9n
def test_core_crud_handler_used():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_crud"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    step = Gadget.hooks.create.HANDLER[0]
    assert step.__qualname__ == _core.create.__qualname__


@pytest.mark.i9n
def test_hook_execution():
    Base.metadata.clear()

    class Hooked(Base, GUIDPk):
        __tablename__ = "hooked_model"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def inject_name(cls, ctx):
            ctx["payload"] = {"name": "hooked"}

    bind(Hooked)
    orig = _Ctx.ensure

    @classmethod
    def patched(cls, *args, **kwargs):
        if args and not kwargs:
            return orig.__func__(cls, request=None, db=None, seed=args[0])
        return orig.__func__(cls, *args, **kwargs)

    _Ctx.ensure = patched
    try:
        payload = asyncio.run(Hooked.hooks.create.PRE_HANDLER[0](ctx={}))
    finally:
        _Ctx.ensure = orig

    assert payload["name"] == "hooked"


@pytest.mark.i9n
def test_atom_injection():
    Base.metadata.clear()

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_atoms"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Gadget)
    chains = build_phase_chains(Gadget, "create")
    non_handler = [ph for ph in PHASES if ph != "HANDLER" and chains.get(ph)]
    assert non_handler


@pytest.mark.i9n
def test_system_step_registry():
    subjects = runtime_system.subjects()
    assert ("txn", "begin") in subjects
    assert ("handler", "crud") in subjects
    assert ("txn", "commit") in subjects
