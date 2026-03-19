from __future__ import annotations

import ast
from pathlib import Path

_STANDARDS = Path(__file__).resolve().parents[3]
ROOT = _STANDARDS / "tigrbl" / "tigrbl"
RUNTIME_ROOT = _STANDARDS / "tigrbl_runtime" / "tigrbl_runtime"
CANON_ROOT = _STANDARDS / "tigrbl_canon" / "tigrbl_canon"


def _source(pkg_root: Path, rel: str) -> str:
    return (pkg_root / rel).read_text()


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


def test_gateway_runtime_module_removed():
    assert not (RUNTIME_ROOT / "runtime" / "gw").exists()


def test_mapping_does_not_import_dispatch_modules():
    rest_collection = CANON_ROOT / "mapping" / "rest" / "collection.py"
    rest_member = CANON_ROOT / "mapping" / "rest" / "member.py"
    rpc_mapping = CANON_ROOT / "mapping" / "rpc.py"
    router_proxy = CANON_ROOT / "mapping" / "router" / "resource_proxy.py"

    for path in (rest_collection, rest_member, rpc_mapping, router_proxy):
        assert not _imports_module(path, "tigrbl", "dispatch_operation")
        assert not _imports_module(path, "..dispatch")
        assert not _imports_module(path, "...dispatch")


def test_mapping_layers_return_operation_envelopes_without_invoke_calls():
    rpc_source = _source(CANON_ROOT, "mapping/rpc.py")
    assert "_invoke(" not in rpc_source


def test_removed_transport_dispatcher_files_are_absent():
    removed = (
        ROOT / "transport" / "dispatch.py",
        ROOT / "transport" / "dispatcher.py",
        ROOT / "transport" / "jsonrpc" / "dispatcher.py",
    )
    assert all(not path.exists() for path in removed)
