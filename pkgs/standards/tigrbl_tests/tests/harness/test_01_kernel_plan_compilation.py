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
    from tigrbl import TableBase
    from tigrbl._spec import AppSpec
    from tigrbl import TigrblApp
    from tigrbl._spec import OpSpec
    from tigrbl.orm.mixins import GUIDPk
    from tigrbl_kernel import Kernel
    from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec

    class Widget(TableBase, GUIDPk):
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
    from tigrbl import TableBase
    from tigrbl._spec import AppSpec
    from tigrbl import TigrblApp
    from tigrbl._spec import OpSpec
    from tigrbl.orm.mixins import GUIDPk
    from tigrbl_kernel import Kernel
    from tigrbl_kernel.models import OpKey
    from tigrbl._spec import HttpRestBindingSpec

    class Widget(TableBase, GUIDPk):
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


@pytest.mark.acceptance
def test_compile_kernel_plan_from_app_spec_includes_all_operation_bindings() -> None:
    from tigrbl._spec import AppSpec
    from tigrbl._spec import ColumnSpec, FieldSpec as F, IOSpec as IO
    from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec
    from tigrbl._spec import OpSpec, TableSpec
    from tigrbl_kernel import Kernel

    table_spec = TableSpec(
        model_ref="tests.models:Gadget",
        columns={
            "name": ColumnSpec(
                storage=None,
                field=F(py_type=str, required_in=("create",)),
                io=IO(in_verbs=("create",), out_verbs=("list", "read")),
            )
        },
        ops=(
            OpSpec(
                alias="list",
                target="list",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest", path="/gadget", methods=("GET",)
                    ),
                ),
            ),
            OpSpec(
                alias="create",
                target="create",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest", path="/gadget", methods=("POST",)
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="Gadget.create",
                    ),
                ),
            ),
        ),
    )

    app_spec = AppSpec(tables=[table_spec])

    plan = Kernel().compile_plan(app_spec)

    assert "http.rest" in plan.proto_indices
    assert "http.jsonrpc" in plan.proto_indices
    assert "GET /gadget" in plan.proto_indices["http.rest"]["exact"]
    assert "POST /gadget" in plan.proto_indices["http.rest"]["exact"]
    assert "Gadget.create" in plan.proto_indices["http.jsonrpc"]

    aliases = {meta.alias for meta in plan.opmeta}
    assert aliases == {"list", "create"}
