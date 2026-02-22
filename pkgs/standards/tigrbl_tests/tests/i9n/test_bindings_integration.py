import asyncio
from types import SimpleNamespace

from sqlalchemy import String

from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import engine as engine_factory, mem

from tigrbl.types import uuid4
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import IO, S, acol
from tigrbl.bindings import (
    bind,
    include_model,
    include_models,
    rpc_call,
    rebind,
)
from tigrbl.runtime import build_phase_chains
from tigrbl.config.constants import TIGRBL_GET_DB_ATTR


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_bindings"
    __allow_unmapped__ = True

    name = acol(
        storage=S(type_=String, nullable=False),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )


class Gizmo(Base, GUIDPk):
    __tablename__ = "gizmos_bindings"
    __allow_unmapped__ = True

    label = acol(
        storage=S(type_=String, nullable=False),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )


def _make_db():
    engine = engine_factory(mem(async_=False))
    raw_engine, _ = engine.raw()
    # The shared Declarative ``Base`` is cleared in various tests to maintain
    # isolation. If another test clears the metadata before this helper runs,
    # ``Base.metadata.create_all`` would create no tables, leading to runtime
    # failures. Creating the tables directly from the model definitions keeps
    # this helper resilient regardless of prior test side effects.
    Widget.__table__.create(bind=raw_engine)
    Gizmo.__table__.create(bind=raw_engine)
    db = engine.provider.session()
    return engine, db


def test_include_model_and_rpc_call():
    engine, db = _make_db()
    router = SimpleNamespace(engine=engine)
    _resolver.register_api(router, engine)

    include_model(router, Widget, mount_router=False)

    # router facade populated
    assert router.models["Widget"] is Widget
    assert hasattr(router.schemas, "Widget")
    assert hasattr(router.handlers, "Widget")
    assert hasattr(router.hooks, "Widget")
    assert hasattr(router.rpc, "Widget")
    assert hasattr(router.rest, "Widget")
    assert "Widget" in router.routers
    assert "Widget" in router.columns
    assert "Widget" in router.table_config
    assert hasattr(router.core, "Widget")

    # model namespaces
    assert hasattr(Widget, TIGRBL_GET_DB_ATTR)
    assert "create" in Widget.opspecs.by_alias
    assert Widget.hooks.create.HANDLER

    phases = build_phase_chains(Widget, "create")
    assert phases["HANDLER"], "phase lifecycle must contain handler step"

    asyncio.run(rpc_call(router, Widget, "create", {"id": uuid4(), "name": "w"}, db=db))
    rows = asyncio.run(rpc_call(router, Widget, "list", {}, db=db))
    assert rows and rows[0]["name"] == "w"


def test_include_models():
    engine, db = _make_db()
    router = SimpleNamespace(engine=engine)
    _resolver.register_api(router, engine)

    include_models(router, [Widget, Gizmo], mount_router=False)

    assert set(router.models) == {"Widget", "Gizmo"}
    assert hasattr(router.schemas, "Widget")
    assert hasattr(router.schemas, "Gizmo")


def test_bind_and_rebind():
    bind(Widget)
    orig_router = Widget.rest.router
    assert orig_router is not None

    rebind(Widget)
    assert Widget.rest.router is not None
