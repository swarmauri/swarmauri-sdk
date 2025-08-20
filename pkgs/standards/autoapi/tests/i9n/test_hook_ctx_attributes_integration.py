from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI
from sqlalchemy import String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3 import core as _core
from autoapi.v3.bindings.model import bind
from autoapi.v3.decorators import hook_ctx
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.runtime.executor import _Ctx
from autoapi.v3.runtime.kernel import build_phase_chains
from autoapi.v3.runtime import system as runtime_system
from autoapi.v3.specs import IO, S, acol
from autoapi.v3.tables import Base


class Hooked(Base, GUIDPk):
    """Model used to exercise hook_ctx integration."""

    __tablename__ = "hooked_ctx"
    __allow_unmapped__ = True

    name = acol(
        storage=S(type_=String, nullable=False, default="anon"),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    def ensure_name(cls, ctx):
        payload = dict(ctx.get("payload") or {})
        payload.setdefault("name", "hooked")
        ctx["payload"] = payload


def fresh_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


@pytest.mark.i9n
def test_hook_ctx_bindings():
    bind(Hooked)
    hooks = Hooked.__autoapi_hooks__
    assert "create" in hooks
    assert hooks["create"].get("PRE_HANDLER")


@pytest.mark.i9n
def test_request_and_response_schemas():
    bind(Hooked)
    assert hasattr(Hooked.schemas, "create")
    assert hasattr(Hooked.schemas.create, "in_")
    assert hasattr(Hooked.schemas, "read")
    assert hasattr(Hooked.schemas.read, "out")


@pytest.mark.i9n
def test_columns_bound():
    bind(Hooked)
    assert "name" in Hooked.__table__.c
    assert "name" in getattr(Hooked, "__autoapi_cols__", ())


@pytest.mark.i9n
def test_defaults_value_resolution():
    bind(Hooked)
    db = fresh_session()
    obj = asyncio.run(_core.create(Hooked, db=db, data={}))
    assert obj.name == "anon"


@pytest.mark.i9n
def test_internal_model_opspec_binding():
    bind(Hooked)
    sp = Hooked.opspecs.by_alias["create"][0]
    assert sp.table is Hooked


@pytest.mark.i9n
def test_openapi_includes_path():
    bind(Hooked)
    app = FastAPI()
    app.include_router(Hooked.rest.router)
    schema = app.openapi()
    assert "/Hooked" in schema["paths"]


@pytest.mark.i9n
def test_storage_and_sqlalchemy_persist():
    bind(Hooked)
    db = fresh_session()
    asyncio.run(_core.create(Hooked, db=db, data={"name": "stored"}))
    fetched = db.query(Hooked).one()
    assert fetched.name == "stored"


@pytest.mark.i9n
def test_rest_routes_bound():
    bind(Hooked)
    session = fresh_session()

    def get_db():
        return session

    Hooked.__autoapi_get_db__ = staticmethod(get_db)  # type: ignore[attr-defined]
    app = FastAPI()
    app.include_router(Hooked.rest.router)
    paths = {route.path for route in app.router.routes}
    assert "/Hooked" in paths


@pytest.mark.i9n
def test_rpc_method_bound():
    bind(Hooked)
    assert hasattr(Hooked.rpc, "create")


@pytest.mark.i9n
def test_core_crud_create():
    bind(Hooked)
    db = fresh_session()
    obj = asyncio.run(_core.create(Hooked, db=db, data={"name": "core"}))
    assert obj.name == "core"


@pytest.mark.i9n
def test_hookz_phase_chain_contains_hook():
    bind(Hooked)
    chains = build_phase_chains(Hooked, "create")
    assert any(step for step in chains.get("PRE_HANDLER", []) if callable(step))


@pytest.mark.i9n
def test_atomz_temp_ctx():
    ctx = _Ctx.ensure(request=None, db=None)
    assert isinstance(ctx.temp, dict)


@pytest.mark.i9n
def test_system_steps_tx_begin_and_commit():
    ctx = _Ctx.ensure(request=None, db=None)
    runtime_system._sys_tx_begin(None, ctx)
    assert ctx.temp.get("__sys_tx_open__") is False
    runtime_system._sys_tx_commit(None, ctx)
    assert ctx.temp.get("__sys_tx_open__") is False
