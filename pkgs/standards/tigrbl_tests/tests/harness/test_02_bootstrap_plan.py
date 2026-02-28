"""TDD harness: Bootstrap plan contract.

Bootstrap plan = the *transport-agnostic ingress pipeline* executed before op is known.

Requirements:
  - Deterministic phase order: INGRESS_BEGIN -> INGRESS_PARSE -> INGRESS_ROUTE
  - Provides minimum atoms needed to:
      * build RawGatewayEvent from ASGI scope/event
      * detect protocol (http.rest vs http.jsonrpc vs ws/wss)
      * match binding (path/method or rpc method)
      * select op (OpKey -> OpMeta)
      * finalize ctx for op-specific chain execution

The API below is the intended stable entrypoint for tests and diagnostics.
"""

from __future__ import annotations

import pytest


@pytest.mark.acceptance
def test_kernel_compiles_bootstrap_plan_with_required_anchors() -> None:
    from sqlalchemy import Column, String

    from tigrbl import TableBase
    from tigrbl._spec import AppSpec
    from tigrbl import TigrblApp
    from tigrbl.orm.mixins import GUIDPk
    from tigrbl._spec import OpSpec
    from tigrbl.runtime import events as ev
    from tigrbl.runtime.kernel import Kernel
    from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec

    class Widget(TableBase, GUIDPk):
        __tablename__ = "widgets_bootstrap_plan"
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

    # Contract: kernel exposes an explicit bootstrap plan compiler.
    bootstrap = Kernel().compile_bootstrap_plan(app)

    # Contract: bootstrap is a phase->steps mapping.
    assert isinstance(bootstrap, dict)

    # Contract: bootstrap includes ingress phases.
    assert ev.INGRESS_BEGIN in bootstrap
    assert ev.INGRESS_PARSE in bootstrap
    assert ev.INGRESS_ROUTE in bootstrap

    # Contract: required anchors appear in step labels.
    labels = []
    for phase in ("INGRESS_BEGIN", "INGRESS_PARSE", "INGRESS_ROUTE"):
        for step in bootstrap.get(phase, ()) or ():
            lbl = getattr(step, "__tigrbl_label", None)
            if isinstance(lbl, str):
                labels.append(lbl)

    # Minimal anchor coverage.
    required = {
        ev.INGRESS_CTX_INIT,
        ev.INGRESS_RAW_FROM_SCOPE,
        ev.ROUTE_PROTOCOL_DETECT,
        ev.ROUTE_BINDING_MATCH,
        ev.ROUTE_OP_RESOLVE,
        ev.ROUTE_PLAN_SELECT,
        ev.ROUTE_CTX_FINALIZE,
    }

    missing = [a for a in sorted(required) if not any(a in lab for lab in labels)]
    assert not missing, f"bootstrap missing anchors: {missing}"
