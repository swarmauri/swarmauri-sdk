from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def _source(rel: str) -> str:
    return (ROOT / rel).read_text()


def _imports_module(path: Path, module: str, symbol: str | None = None) -> bool:
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module_name = f"{'.' * node.level}{node.module or ''}"
            if module_name == module:
                if symbol is None:
                    return True
                if any(alias.name == symbol for alias in node.names):
                    return True
    return False


def test_gateway_invoke_invokes_runtime_kernel_plan_and_executor():
    source = _source("runtime/gw/invoke.py")
    assert "kernel.kernel_plan(app)" in source
    assert "await _invoke(" in source


def test_gateway_invoke_uses_runtime_atoms_for_fallback_and_errors():
    source = _source("runtime/gw/invoke.py")
    assert "_runtime_route_handler" in source
    assert "_error_to_transport" in source
    assert "except Exception" not in source


def test_mapping_does_not_import_dispatch_modules():
    rest_collection = ROOT / "mapping" / "rest" / "collection.py"
    rest_member = ROOT / "mapping" / "rest" / "member.py"
    rpc_mapping = ROOT / "mapping" / "rpc.py"
    router_proxy = ROOT / "mapping" / "router" / "resource_proxy.py"

    for path in (rest_collection, rest_member, rpc_mapping, router_proxy):
        assert not _imports_module(path, "tigrbl", "dispatch_operation")
        assert not _imports_module(path, "..dispatch")
        assert not _imports_module(path, "...dispatch")


def test_mapping_layers_return_operation_envelopes_without_invoke_calls():
    rpc_source = _source("mapping/rpc.py")
    assert "_invoke(" not in rpc_source


def test_removed_transport_dispatcher_files_are_absent():
    removed = (
        ROOT / "transport" / "dispatch.py",
        ROOT / "transport" / "dispatcher.py",
        ROOT / "transport" / "jsonrpc" / "dispatcher.py",
    )
    assert all(not path.exists() for path in removed)
