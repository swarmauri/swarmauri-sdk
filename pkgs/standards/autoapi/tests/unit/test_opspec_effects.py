from __future__ import annotations

import asyncio
import pytest

from autoapi.v3.types import App
from sqlalchemy import String, create_engine
from sqlalchemy.orm import sessionmaker

from autoapi.v3.bindings.model import bind
from autoapi.v3.opspec.types import PHASES
from autoapi.v3.runtime.kernel import build_phase_chains
from autoapi.v3.runtime import system as runtime_system
from autoapi.v3.specs import IO, S, acol
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3 import core as _core
from autoapi.v3.decorators import hook_ctx

# --- models --------------------------------------------------------------------


@pytest.fixture
def gadget_model():
    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_opspec"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False, default="anon"),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    return Gadget


@pytest.fixture
def hooked_model():
    class Hooked(Base, GUIDPk):
        __tablename__ = "hooked_opspec"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def inject_name(cls, ctx):
            payload = dict(ctx.get("payload") or {})
            payload.setdefault("name", "hooked")
            ctx["payload"] = payload

    return Hooked


# --- helpers -------------------------------------------------------------------


def _fresh_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    return session, engine


# --- tests ---------------------------------------------------------------------


def test_request_and_response_schemas(gadget_model):
    bind(gadget_model)
    assert hasattr(gadget_model.schemas, "create")
    assert hasattr(gadget_model.schemas.create, "in_")
    assert hasattr(gadget_model.schemas, "read")
    assert hasattr(gadget_model.schemas.read, "out")


def test_columns_bound(gadget_model):
    bind(gadget_model)
    assert "name" in gadget_model.__table__.c
    assert "name" in gadget_model.__autoapi_cols__


def test_defaults_value_resolution(gadget_model):
    bind(gadget_model)
    db, engine = _fresh_session()
    obj = asyncio.run(_core.create(gadget_model, db=db, data={}))
    assert obj.name == "anon"
    engine.dispose()


def test_internal_model_opspec_binding(gadget_model):
    bind(gadget_model)
    sp = gadget_model.opspecs.by_alias["create"][0]
    assert sp.table is gadget_model


def test_openapi_includes_path(gadget_model):
    bind(gadget_model)
    app = App()
    app.include_router(gadget_model.rest.router)
    schema = app.openapi()
    assert "/gadget" in schema["paths"]


def test_storage_and_sqlalchemy_persist(gadget_model):
    bind(gadget_model)
    db, engine = _fresh_session()
    asyncio.run(_core.create(gadget_model, db=db, data={"name": "stored"}))
    fetched = db.query(gadget_model).one()
    assert fetched.name == "stored"
    engine.dispose()


def test_rest_routes_bound(gadget_model):
    session, engine = _fresh_session()

    def get_db():
        return session

    gadget_model.__autoapi_get_db__ = staticmethod(get_db)  # type: ignore[attr-defined]
    bind(gadget_model)
    app = App()
    app.include_router(gadget_model.rest.router)
    paths = {route.path for route in app.router.routes}
    assert "/gadget" in paths
    engine.dispose()


def test_rpc_method_bound(gadget_model):
    bind(gadget_model)
    assert hasattr(gadget_model.rpc, "create")


def test_core_crud_handler_used(gadget_model):
    bind(gadget_model)
    step = gadget_model.hooks.create.HANDLER[0]
    assert step.__qualname__ == _core.create.__qualname__


def test_hook_execution(hooked_model):
    bind(hooked_model)
    assert hooked_model.hooks.create.PRE_HANDLER


def test_atom_injection(gadget_model):
    bind(gadget_model)
    chains = build_phase_chains(gadget_model, "create")
    non_handler = [ph for ph in PHASES if ph != "HANDLER" and chains.get(ph)]
    assert non_handler  # atoms or hooks provide extra steps


def test_system_step_registry():
    subjects = runtime_system.subjects()
    assert ("txn", "begin") in subjects
    assert ("handler", "crud") in subjects
    assert ("txn", "commit") in subjects
