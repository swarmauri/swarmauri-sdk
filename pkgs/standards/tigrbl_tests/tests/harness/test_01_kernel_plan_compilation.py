"""TDD harness: KernelPlan compilation contract.

This category locks down:
  - AppSpec -> Kernel.compile_plan(app) (or equivalent)
  - REST selectors are materialized as OpKeys: "METHOD /path"
  - JSON-RPC selectors are rpc_method strings
  - plan.proto_indices and plan.opmeta are internally consistent

These tests are meant to be run during kernel/compiler refactors.
"""

from __future__ import annotations

import pytest


@pytest.mark.acceptance
def test_compile_kernel_plan_indexes_rest_and_jsonrpc_bindings() -> None:
    from sqlalchemy import Column, String
    from tigrbl import Base
    from tigrbl.app import AppSpec
    from tigrbl.concrete.tigrbl_app import TigrblApp
    from tigrbl.op import OpSpec
    from tigrbl.orm.mixins import GUIDPk
    from tigrbl.runtime.kernel import Kernel
    from tigrbl.specs.binding_spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_kernel_plan"
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
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="Widget.create",
                ),
            ),
        ),
    )

    app = TigrblApp.from_spec(AppSpec(tables=(Widget,)))
    plan = Kernel().compile_plan(app)

    # --- REST index ---
    rest = plan.proto_indices.get("http.rest")
    assert rest is not None
    assert "POST /widget" in rest

    # --- JSON-RPC index ---
    rpc = plan.proto_indices.get("http.jsonrpc")
    assert rpc is not None
    assert "Widget.create" in rpc

    # --- Consistency ---
    rest_meta_idx = rest["POST /widget"]
    rpc_meta_idx = rpc["Widget.create"]
    assert rest_meta_idx == rpc_meta_idx

    meta = plan.opmeta[rest_meta_idx]
    assert meta.alias == "create"
    assert meta.target == "create"
    assert meta.model is Widget


@pytest.mark.acceptance
def test_kernel_plan_roundtrips_opkey_to_meta() -> None:
    from sqlalchemy import Column, String
    from tigrbl import Base
    from tigrbl.app import AppSpec
    from tigrbl.concrete.tigrbl_app import TigrblApp
    from tigrbl.op import OpSpec
    from tigrbl.orm.mixins import GUIDPk
    from tigrbl.runtime.kernel import Kernel
    from tigrbl.runtime.kernel.models import OpKey
    from tigrbl.specs.binding_spec import HttpRestBindingSpec

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_kernel_opkey"
        __resource__ = "widget"
        name = Column(String, nullable=False)

    Widget.__tigrbl_ops__ = (
        OpSpec(
            alias="list",
            target="list",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest", path="/widget", methods=("GET",)
                ),
            ),
        ),
    )

    app = TigrblApp.from_spec(AppSpec(tables=(Widget,)))
    plan = Kernel().compile_plan(app)

    key = OpKey(proto="http.rest", selector="GET /widget")
    assert key in plan.opkey_to_meta
    meta_idx = plan.opkey_to_meta[key]
    assert plan.opmeta[meta_idx].alias == "list"
