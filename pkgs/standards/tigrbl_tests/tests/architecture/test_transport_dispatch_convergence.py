from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def _source(rel: str) -> str:
    return (ROOT / rel).read_text()


def _imports_module(path: Path, module: str, symbol: str | None = None) -> bool:
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            if symbol is None:
                return True
            if any(alias.name == symbol for alias in node.names):
                return True
    return False


def _calls_named(path: Path, name: str) -> bool:
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == name:
                return True
            if isinstance(fn, ast.Attribute) and fn.attr == name:
                return True
    return False


def test_jsonrpc_dispatcher_uses_unified_dispatch_only():
    source = _source("transport/jsonrpc/dispatcher.py")
    assert "dispatch_operation" in source
    assert "_select_auth_dep" not in source
    assert "_user_from_request" not in source
    assert "_authorize(" not in source


def test_rest_and_rpc_call_transport_dispatcher_operation():
    rest_collection = ROOT / "bindings" / "rest" / "collection.py"
    rest_member = ROOT / "bindings" / "rest" / "member.py"
    rpc_dispatcher = ROOT / "transport" / "jsonrpc" / "dispatcher.py"

    for path in (rest_collection, rest_member, rpc_dispatcher):
        assert _imports_module(path, "...transport.dispatcher", "dispatch_operation")
        assert _calls_named(path, "dispatch_operation")


def test_only_transport_dispatcher_invokes_runtime_executor_directly():
    violations: list[str] = []
    targets = [ROOT / "transport", ROOT / "bindings" / "rest"]
    for target in targets:
        for path in target.rglob("*.py"):
            rel = path.relative_to(ROOT)
            if rel.as_posix() == "transport/dispatcher.py":
                continue
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr == "_invoke":
                    violations.append(f"{rel}:{node.lineno}")
    assert violations == [], "\n".join(violations)


def test_dep_name_strategy_prefers_explicit_then_module_qualname():
    from tigrbl.runtime.atoms.deps_inject._common import dep_name

    def local_dep():
        return None

    assert dep_name(local_dep).endswith(".local_dep")

    class NamedDep:
        __tigrbl_dep_name__ = "custom.dep"

        def __call__(self):
            return None

    assert dep_name(NamedDep()) == "custom.dep"
