from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.binding_spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    WsBindingSpec,
)
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.op_spec import OpSpec

from tigrbl_kernel._compile import _compile_plan
from tigrbl_kernel.models import KernelPlan, OpKey


@dataclass
class AppFixture:
    tables: tuple[type, ...]


class CompilerFixture:
    def __init__(self) -> None:
        self.packed_marker: object = object()

    def _build_ingress(self, app: Any) -> dict[str, list[Any]]:
        return {"INGRESS": [lambda *_: app]}

    def _build_egress(self, app: Any) -> dict[str, list[Any]]:
        return {"EGRESS": [lambda *_: app]}

    def _build_op(self, model: type, alias: str) -> dict[str, list[Any]]:
        def _step(*_: Any) -> tuple[type, str]:
            return model, alias

        return {"HANDLER": [_step]}

    def _pack_kernel_plan(self, semantic: KernelPlan) -> object:
        return self.packed_marker


class WidgetTable:
    ops = (
        OpSpec(
            alias="list_widgets",
            target="list",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("GET",),
                    path="/widgets",
                ),
            ),
        ),
        OpSpec(
            alias="get_widget",
            target="read",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("GET",),
                    path="/widgets/{widget_id}",
                ),
                WsBindingSpec(proto="ws", path="/ws/widgets/{widget_id}"),
            ),
        ),
        OpSpec(
            alias="rpc_lookup",
            target="custom",
            bindings=(
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="widgets.lookup",
                ),
            ),
        ),
    )


def test_compile_plan_builds_indices_for_rest_ws_and_jsonrpc_bindings() -> None:
    compiler = CompilerFixture()
    app = AppFixture(tables=(WidgetTable,))

    plan = _compile_plan(compiler, app)

    assert plan.packed is compiler.packed_marker
    assert len(plan.opmeta) == 3
    assert plan.opkey_to_meta[OpKey("http.rest", "GET /widgets")] == 0
    assert plan.opkey_to_meta[OpKey("http.rest", "GET /widgets/{widget_id}")] == 1
    assert plan.opkey_to_meta[OpKey("ws", "/ws/widgets/{widget_id}")] == 1
    assert plan.opkey_to_meta[OpKey("http.jsonrpc", "widgets.lookup")] == 2

    http_rest_index = plan.proto_indices["http.rest"]
    assert http_rest_index["exact"]["GET /widgets"] == 0
    templated_rest = http_rest_index["templated"][0]
    assert templated_rest["path"] == "/widgets/{widget_id}"
    assert templated_rest["names"] == ("widget_id",)

    ws_index = plan.proto_indices["ws"]
    templated_ws = ws_index["templated"][0]
    assert templated_ws["path"] == "/ws/widgets/{widget_id}"
    assert templated_ws["names"] == ("widget_id",)

    assert plan.proto_indices["http.jsonrpc"]["widgets.lookup"] == 2


def test_compile_plan_accepts_appspec_and_declared_tigrbl_ops() -> None:
    class GadgetTable:
        __tigrbl_ops__ = (
            OpSpec(
                alias="list_gadgets",
                target="list",
                bindings=(
                    HttpRestBindingSpec(
                        proto="https.rest",
                        methods=("GET",),
                        path="/gadgets",
                    ),
                ),
            ),
        )

    compiler = CompilerFixture()
    app = AppSpec(tables=(GadgetTable,))

    plan = _compile_plan(compiler, app)

    assert len(plan.opmeta) == 1
    assert plan.opmeta[0].alias == "list_gadgets"
    assert plan.opmeta[0].target == "list"
    assert plan.opkey_to_meta[OpKey("https.rest", "GET /gadgets")] == 0
    assert plan.proto_indices["https.rest"]["exact"]["GET /gadgets"] == 0
