from __future__ import annotations

from tigrbl_core._spec.app_spec import AppSpec


def test_collect_reads_scalar_and_sequence_attributes() -> None:
    class DemoApp:
        TITLE = "Demo"
        DESCRIPTION = "desc"
        VERSION = "1.0.0"
        JSONRPC_PREFIX = "/r"
        SYSTEM_PREFIX = "/s"
        ROUTERS = ("router",)
        OPS = ("op",)

    spec = AppSpec.collect(DemoApp)

    assert spec.title == "Demo"
    assert spec.description == "desc"
    assert spec.version == "1.0.0"
    assert spec.jsonrpc_prefix == "/r"
    assert spec.system_prefix == "/s"
    assert spec.routers == ("router",)
    assert spec.ops == ("op",)


def test_collect_falls_back_to_defaults() -> None:
    class EmptyApp:
        pass

    spec = AppSpec.collect(EmptyApp)

    assert spec.title == "Tigrbl"
    assert spec.version == "0.1.0"
    assert spec.jsonrpc_prefix == "/rpc"
    assert spec.system_prefix == "/system"
