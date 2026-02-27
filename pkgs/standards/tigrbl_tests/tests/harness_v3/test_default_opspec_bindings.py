"""Harness: default Ops + BindingSpecs.

Contract (TDD):
1) Including a model/table automatically generates the canonical CRUD operation
   specs (collection + member arities).
2) Those op specs automatically get REST + JSON-RPC BindingSpecs.

This suite deliberately avoids assertions about Starlette/FastAPI routes.
Instead it asserts on *specs* and *bindings* that power runtime-owned routing.
"""

from __future__ import annotations

import inspect

from tigrbl import Base, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec
from tigrbl.types import Column, String


def _rest_bindings(op) -> list[HttpRestBindingSpec]:
    return [
        b for b in getattr(op, "bindings", ()) if isinstance(b, HttpRestBindingSpec)
    ]


def _rpc_bindings(op) -> list[HttpJsonRpcBindingSpec]:
    return [
        b for b in getattr(op, "bindings", ()) if isinstance(b, HttpJsonRpcBindingSpec)
    ]


def test_include_table_builds_default_opspecs_and_bindings() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "harness_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    # --- Ops exist and are indexed by alias ---
    assert hasattr(Widget, "opspecs"), "Model must be decorated with opspecs after bind"
    assert "create" in Widget.opspecs.by_alias
    assert "read" in Widget.opspecs.by_alias
    assert "update" in Widget.opspecs.by_alias
    assert "delete" in Widget.opspecs.by_alias
    assert "list" in Widget.opspecs.by_alias

    create = Widget.opspecs.by_alias["create"]
    read = Widget.opspecs.by_alias["read"]
    update = Widget.opspecs.by_alias["update"]
    delete = Widget.opspecs.by_alias["delete"]
    list_ = Widget.opspecs.by_alias["list"]

    # --- Arity contract (collection vs member) ---
    assert create.arity == "collection"
    assert list_.arity == "collection"
    assert read.arity == "member"
    assert update.arity == "member"
    assert delete.arity == "member"

    # --- REST BindingSpecs (canonical CRUD routes) ---
    # Collection routes.
    assert any(
        b.path == "/widget" and "POST" in b.methods for b in _rest_bindings(create)
    )
    assert any(
        b.path == "/widget" and "GET" in b.methods for b in _rest_bindings(list_)
    )

    # Member routes (note: the runtime must match concrete IDs like /widget/<uuid>).
    assert any(
        b.path == "/widget/{item_id}" and "GET" in b.methods
        for b in _rest_bindings(read)
    )
    assert any(
        b.path == "/widget/{item_id}" and "PATCH" in b.methods
        for b in _rest_bindings(update)
    )
    assert any(
        b.path == "/widget/{item_id}" and "DELETE" in b.methods
        for b in _rest_bindings(delete)
    )

    # --- JSON-RPC BindingSpecs ---
    assert any(b.rpc_method == "Widget.create" for b in _rpc_bindings(create))
    assert any(b.rpc_method == "Widget.read" for b in _rpc_bindings(read))
    assert any(b.rpc_method == "Widget.update" for b in _rpc_bindings(update))
    assert any(b.rpc_method == "Widget.delete" for b in _rpc_bindings(delete))
    assert any(b.rpc_method == "Widget.list" for b in _rpc_bindings(list_))


def test_model_initialize_is_awaitable_or_sync() -> None:
    """Smoke test: initialize() may be sync or async depending on engine kind."""

    class Widget(Base, GUIDPk):
        __tablename__ = "harness_widget_init"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    result = app.initialize()
    assert result is None or inspect.isawaitable(result)
