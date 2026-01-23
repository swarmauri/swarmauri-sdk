import asyncio

import pytest
from tigrbl.types import App
from sqlalchemy import String, create_engine
from sqlalchemy.orm import sessionmaker

from tigrbl import core as _core
from tigrbl.bindings.model import bind
from tigrbl.hook import hook_ctx
from tigrbl.op.types import PHASES
from tigrbl.runtime import system as runtime_system
from tigrbl.runtime.kernel import build_phase_chains
from tigrbl.specs import IO, S, acol
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk


# --- models --------------------------------------------------------------------


# NOTE:
# Historically this test called ``Base.metadata.clear()`` at import time to
# ensure a pristine declarative registry.  When the test module is imported as
# part of the full suite, clearing the global metadata wipes out tables defined
# by earlier tests which still rely on the shared ``Base``.  Subsequent tests
# would then fail with missing table/column errors (manifesting as HTTP 503
# responses) because their models lost their metadata.  The table names used in
# this module are unique, so we can simply avoid clearing the global metadata to
# preserve isolation without impacting other tests.


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

GADGET_TABLE = Gadget.__table__
HOOKED_TABLE = Hooked.__table__


def _ensure_tables():
    for model, table in ((Gadget, GADGET_TABLE), (Hooked, HOOKED_TABLE)):
        if not hasattr(model, "__table__"):
            model.__table__ = table  # type: ignore[attr-defined]
        if table.key not in Base.metadata.tables:
            Base.metadata._add_table(table.name, table.schema, table)
        if not hasattr(model, "__mapper__"):
            Base.registry.map_imperatively(model, table)


def _fresh_session():
    engine = create_engine("sqlite:///:memory:")
    _ensure_tables()
    Base.metadata.create_all(bind=engine, tables=[Gadget.__table__, Hooked.__table__])
    return sessionmaker(bind=engine)()


# --- tests ---------------------------------------------------------------------


@pytest.mark.i9n
def test_request_and_response_schemas():
    _ensure_tables()
    bind(Gadget)
    assert hasattr(Gadget.schemas, "create")
    assert hasattr(Gadget.schemas.create, "in_")
    assert hasattr(Gadget.schemas, "read")
    assert hasattr(Gadget.schemas.read, "out")


@pytest.mark.i9n
def test_columns_bound():
    _ensure_tables()
    bind(Gadget)
    assert "name" in Gadget.__table__.c
    assert "name" in Gadget.__tigrbl_cols__


@pytest.mark.i9n
def test_defaults_value_resolution():
    _ensure_tables()
    bind(Gadget)
    db = _fresh_session()
    obj = asyncio.run(_core.create(Gadget, db=db, data={}))
    assert obj.name == "anon"


@pytest.mark.i9n
def test_internal_model_opspec_binding():
    _ensure_tables()
    bind(Gadget)
    sp = Gadget.opspecs.by_alias["create"][0]
    assert sp.table is Gadget


@pytest.mark.i9n
def test_openapi_includes_path():
    _ensure_tables()
    bind(Gadget)
    app = App()
    app.include_router(Gadget.rest.router)
    schema = app.openapi()
    assert "/gadget" in schema["paths"]


@pytest.mark.i9n
def test_storage_and_sqlalchemy_persist():
    _ensure_tables()
    bind(Gadget)
    db = _fresh_session()
    asyncio.run(_core.create(Gadget, db=db, data={"name": "stored"}))
    fetched = db.query(Gadget).one()
    assert fetched.name == "stored"


@pytest.mark.i9n
def test_rest_routes_bound():
    _ensure_tables()
    session = _fresh_session()

    def get_db():
        return session

    Gadget.__tigrbl_get_db__ = staticmethod(get_db)  # type: ignore[attr-defined]
    bind(Gadget)
    app = App()
    app.include_router(Gadget.rest.router)
    paths = {route.path for route in app.router.routes}
    assert "/gadget" in paths


@pytest.mark.i9n
def test_rpc_method_bound():
    _ensure_tables()
    bind(Gadget)
    assert hasattr(Gadget.rpc, "create")


@pytest.mark.i9n
def test_core_crud_handler_used():
    _ensure_tables()
    bind(Gadget)
    step = Gadget.hooks.create.HANDLER[0]
    assert step.__qualname__ == _core.create.__qualname__


@pytest.mark.i9n
def test_hook_execution():
    _ensure_tables()
    bind(Hooked)
    assert Hooked.hooks.create.PRE_HANDLER


@pytest.mark.i9n
def test_atom_injection():
    _ensure_tables()
    bind(Gadget)
    chains = build_phase_chains(Gadget, "create")
    non_handler = [ph for ph in PHASES if ph != "HANDLER" and chains.get(ph)]
    # atom discovery injects steps into additional phases beyond the handler
    assert non_handler


@pytest.mark.i9n
def test_system_step_registry():
    subjects = runtime_system.subjects()
    assert ("txn", "begin") in subjects
    assert ("handler", "crud") in subjects
    assert ("txn", "commit") in subjects
