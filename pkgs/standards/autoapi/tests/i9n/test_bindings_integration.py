import asyncio
from types import SimpleNamespace

from sqlalchemy import String, create_engine
from sqlalchemy.orm import sessionmaker

from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.specs.shortcuts import IO, S, acol
from autoapi.v3.bindings import (
    bind,
    include_model,
    include_models,
    rpc_call,
    rebind,
)
from autoapi.v3.bindings import col_info
from autoapi.v3.runtime import build_phase_chains
from autoapi.v3.config.constants import AUTOAPI_GET_DB_ATTR


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
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session()


def test_include_model_and_rpc_call():
    _, db = _make_db()
    api = SimpleNamespace(get_db=lambda: db)

    include_model(api, Widget, mount_router=False)

    # api facade populated
    assert api.models["Widget"] is Widget
    assert hasattr(api.schemas, "Widget")
    assert hasattr(api.handlers, "Widget")
    assert hasattr(api.hooks, "Widget")
    assert hasattr(api.rpc, "Widget")
    assert hasattr(api.rest, "Widget")
    assert "Widget" in api.routers
    assert "Widget" in api.columns
    assert "Widget" in api.table_config
    assert hasattr(api.core, "Widget")

    # model namespaces
    assert hasattr(Widget, AUTOAPI_GET_DB_ATTR)
    assert "create" in Widget.opspecs.by_alias
    assert Widget.hooks.create.HANDLER

    phases = build_phase_chains(Widget, "create")
    assert phases["HANDLER"], "phase lifecycle must contain handler step"

    asyncio.run(rpc_call(api, Widget, "create", {"name": "w"}, db=db))
    rows = asyncio.run(rpc_call(api, Widget, "list", {}, db=db))
    assert rows and rows[0]["name"] == "w"


def test_include_models():
    _, db = _make_db()
    api = SimpleNamespace(get_db=lambda: db)

    include_models(api, [Widget, Gizmo], mount_router=False)

    assert set(api.models) == {"Widget", "Gizmo"}
    assert hasattr(api.schemas, "Widget")
    assert hasattr(api.schemas, "Gizmo")


def test_bind_and_rebind():
    bind(Widget)
    orig_router = Widget.rest.router
    assert orig_router is not None

    rebind(Widget)
    assert Widget.rest.router is not None


def test_col_info_reexport():
    from autoapi.v3.schema import col_info as schema_col_info

    assert col_info.normalize is schema_col_info.normalize
    assert col_info.VALID_KEYS == schema_col_info.VALID_KEYS
