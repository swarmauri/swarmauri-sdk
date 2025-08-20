import asyncio

import pytest
from fastapi import FastAPI
from sqlalchemy import String, create_engine
from sqlalchemy.orm import sessionmaker

from autoapi.v3 import core as _core
from autoapi.v3.bindings.model import bind
from autoapi.v3.decorators import hook_ctx
from autoapi.v3.opspec.types import PHASES
from autoapi.v3.runtime import system as runtime_system
from autoapi.v3.runtime.kernel import build_phase_chains
from autoapi.v3.specs import IO, S, acol
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk


# --- models --------------------------------------------------------------------


class Gadget(Base, GUIDPk):
    __tablename__ = "gadgets_opspec"
    __allow_unmapped__ = True

    name = acol(
        storage=S(type_=String, nullable=False, default="anon"),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )


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


# --- helpers -------------------------------------------------------------------


def _fresh_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


# --- tests ---------------------------------------------------------------------


@pytest.mark.i9n
def test_request_and_response_schemas():
    bind(Gadget)
    assert hasattr(Gadget.schemas, "create")
    assert hasattr(Gadget.schemas.create, "in_")
    assert hasattr(Gadget.schemas, "read")
    assert hasattr(Gadget.schemas.read, "out")


@pytest.mark.i9n
def test_columns_bound():
    bind(Gadget)
    assert "name" in Gadget.__table__.c
    assert "name" in Gadget.__autoapi_cols__


@pytest.mark.i9n
def test_defaults_value_resolution():
    bind(Gadget)
    db = _fresh_session()
    obj = asyncio.run(_core.create(Gadget, db=db, data={}))
    assert obj.name == "anon"


@pytest.mark.i9n
def test_internal_model_opspec_binding():
    bind(Gadget)
    sp = Gadget.opspecs.by_alias["create"][0]
    assert sp.table is Gadget


@pytest.mark.i9n
def test_openapi_includes_path():
    bind(Gadget)
    app = FastAPI()
    app.include_router(Gadget.rest.router)
    schema = app.openapi()
    assert "/gadget" in schema["paths"]


@pytest.mark.i9n
def test_storage_and_sqlalchemy_persist():
    bind(Gadget)
    db = _fresh_session()
    asyncio.run(_core.create(Gadget, db=db, data={"name": "stored"}))
    fetched = db.query(Gadget).one()
    assert fetched.name == "stored"


@pytest.mark.i9n
def test_rest_routes_bound():
    session = _fresh_session()

    def get_db():
        return session

    Gadget.__autoapi_get_db__ = staticmethod(get_db)  # type: ignore[attr-defined]
    bind(Gadget)
    app = FastAPI()
    app.include_router(Gadget.rest.router)
    paths = {route.path for route in app.router.routes}
    assert "/gadget" in paths


@pytest.mark.i9n
def test_rpc_method_bound():
    bind(Gadget)
    assert hasattr(Gadget.rpc, "create")


@pytest.mark.i9n
def test_core_crud_handler_used():
    bind(Gadget)
    step = Gadget.hooks.create.HANDLER[0]
    assert step.__qualname__ == _core.create.__qualname__


@pytest.mark.i9n
def test_hook_execution():
    bind(Hooked)
    assert Hooked.hooks.create.PRE_HANDLER


@pytest.mark.i9n
def test_atom_injection():
    bind(Gadget)
    chains = build_phase_chains(Gadget, "create")
    non_handler = [ph for ph in PHASES if ph != "HANDLER" and chains.get(ph)]
    assert non_handler  # atoms or hooks provide extra steps


@pytest.mark.i9n
def test_system_step_registry():
    subjects = runtime_system.subjects()
    assert ("txn", "begin") in subjects
    assert ("handler", "crud") in subjects
    assert ("txn", "commit") in subjects
