"""TDD harness: AppSpec -> App surface contract.

These tests define the *desired* public surface for spec-driven compilation.
They should stay stable while internals evolve.

Scope:
  - AppSpec -> TigrblApp.from_spec
  - Spec-provided system/rpc prefixes
  - Table inclusion from spec

NOTE: These tests are intentionally strict. If they fail, update the runtime
implementation, not the assertions, unless the contract changes deliberately.
"""

from __future__ import annotations

import pytest


@pytest.mark.acceptance
def test_appspec_can_materialize_app_instance() -> None:
    """AppSpec should build a runnable TigrblApp via a single entrypoint."""
    from tigrbl import Base
    from tigrbl.app import AppSpec
    from tigrbl.concrete.tigrbl_app import TigrblApp
    from tigrbl.orm.mixins import GUIDPk

    # minimal table
    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_appspec_contract"
        __resource__ = "widget"

    spec = AppSpec(
        title="Harness",
        version="0.0.0",
        tables=(Widget,),
        jsonrpc_prefix="/rpc",
        system_prefix="/system",
    )

    # Contract: one-shot app materialization.
    app = TigrblApp.from_spec(spec)

    assert isinstance(app, TigrblApp)
    assert getattr(app, "title", None) == "Harness"
    assert getattr(app, "version", None) == "0.0.0"
    assert getattr(app, "jsonrpc_prefix", None) == "/rpc"
    assert getattr(app, "system_prefix", None) == "/system"

    # Contract: tables in the spec are included.
    assert "Widget" in getattr(app, "tables", {})
    assert app.tables["Widget"] is Widget


@pytest.mark.acceptance
def test_appspec_can_override_rpc_prefix_only_when_rpc_is_present() -> None:
    """RPC prefix should be honored iff jsonrpc bindings exist.

    Rationale:
      - Avoid mounting /rpc when the app has no RPC surface.
      - If any OpSpec includes a HttpJsonRpcBindingSpec, mount /rpc automatically
        using the prefix from AppSpec.jsonrpc_prefix.
    """
    from sqlalchemy import Column, String

    from tigrbl import Base
    from tigrbl.app import AppSpec
    from tigrbl.concrete.tigrbl_app import TigrblApp
    from tigrbl.orm.mixins import GUIDPk
    from tigrbl.op import OpSpec
    from tigrbl.specs.binding_spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_appspec_rpc_prefix"
        __resource__ = "widget"
        name = Column(String, nullable=False)

    # Declare an OpSpec with BOTH REST and JSON-RPC bindings.
    Widget.__tigrbl_ops__ = (
        OpSpec(
            alias="create",
            target="create",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest", path="/widget", methods=("POST",)
                ),
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="Widget.create",
                ),
            ),
        ),
    )

    spec = AppSpec(
        title="Harness",
        version="0.0.0",
        tables=(Widget,),
        jsonrpc_prefix="/rpcx",
    )

    app = TigrblApp.from_spec(spec)

    # Contract: rpc router is mounted because jsonrpc binding exists.
    paths = {getattr(r, "path", None) for r in getattr(app, "routes", ())}
    assert "/rpcx" in paths or "/rpcx/" in paths


@pytest.mark.acceptance
def test_appspec_does_not_mount_rpc_when_no_rpc_bindings_exist() -> None:
    """No jsonrpc bindings => no /rpc mount (even if AppSpec has jsonrpc_prefix)."""
    from sqlalchemy import Column, String

    from tigrbl import Base
    from tigrbl.app import AppSpec
    from tigrbl.concrete.tigrbl_app import TigrblApp
    from tigrbl.orm.mixins import GUIDPk
    from tigrbl.op import OpSpec
    from tigrbl.specs.binding_spec import HttpRestBindingSpec

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_appspec_no_rpc"
        __resource__ = "widget"
        name = Column(String, nullable=False)

    Widget.__tigrbl_ops__ = (
        OpSpec(
            alias="create",
            target="create",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest", path="/widget", methods=("POST",)
                ),
            ),
        ),
    )

    spec = AppSpec(
        title="Harness",
        version="0.0.0",
        tables=(Widget,),
        jsonrpc_prefix="/rpcx",
    )

    app = TigrblApp.from_spec(spec)
    paths = {getattr(r, "path", None) for r in getattr(app, "routes", ())}

    assert "/rpcx" not in paths
    assert "/rpcx/" not in paths
