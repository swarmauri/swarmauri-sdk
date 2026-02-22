from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

PKG = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def test_dependency_invoke_is_runtime_event_anchor():
    events = (PKG / "runtime" / "events.py").read_text()
    assert "PRE_TX_DEP" in events
    assert '"PRE_TX_BEGIN"' in events


def test_rest_and_rpc_flow_through_dispatcher():
    rest_member = (PKG / "bindings" / "rest" / "member.py").read_text()
    rest_collection = (PKG / "bindings" / "rest" / "collection.py").read_text()
    rpc_dispatcher = (PKG / "transport" / "jsonrpc" / "dispatcher.py").read_text()
    assert "dispatch_operation" in rest_member
    assert "dispatch_operation" in rest_collection
    assert "dispatch_operation" in rpc_dispatcher
    assert "resolve_operation" in rpc_dispatcher


def test_docs_generation_reads_secdeps_metadata():
    openapi = (PKG / "system" / "docs" / "openapi" / "schema.py").read_text()
    openrpc = (PKG / "system" / "docs" / "openrpc.py").read_text()
    assert "secdeps" in openapi
    assert 'item["name"]' in openrpc


def test_api_instantiation_is_transport_agnostic_and_kernel_plan_builds():
    from tigrbl.router.tigrbl_router import TigrblRouter
    from tigrbl.op.types import OpSpec
    from tigrbl.runtime.kernel import Kernel

    class DemoModel:
        pass

    spec = OpSpec(alias="read", target="read")
    DemoModel.opspecs = SimpleNamespace(all=(spec,))
    DemoModel.ops = SimpleNamespace(by_alias={"read": (spec,)})
    DemoModel.hooks = SimpleNamespace(read=SimpleNamespace())

    router = TigrblRouter()
    router.models = {"DemoModel": DemoModel}

    kernel = Kernel()
    payload = kernel.kernelz_payload(router)

    assert "DemoModel" in payload
    assert "read" in payload["DemoModel"]
