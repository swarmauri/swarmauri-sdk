from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def test_non_transport_modules_do_not_import_legacy_gateway_or_response_primitives():
    blocked = {
        "tigrbl.app.transport",
        "tigrbl.requests",
        "tigrbl.requests.adapters",
        "tigrbl.responses",
        "tigrbl.responses._transport",
    }
    violations: list[str] = []
    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT)
        if rel.parts[0] == "transport":
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module in blocked:
                    violations.append(f"{rel}:{node.lineno}:{node.module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in blocked:
                        violations.append(f"{rel}:{node.lineno}:{alias.name}")
    assert violations == [], "\n".join(violations)


def test_router_module_init_is_transport_agnostic():
    api_file = ROOT / "router" / "_api.py"
    tree = ast.parse(api_file.read_text(), filename=str(api_file))
    modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not any(
        mod.startswith("..transport") or mod.startswith("tigrbl.transport")
        for mod in modules
    )


def test_tigrbl_router_class_has_no_transport_facade_imports():
    api_file = ROOT / "router" / "tigrbl_router.py"
    tree = ast.parse(api_file.read_text(), filename=str(api_file))
    modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not any(
        mod.startswith("..transport")
        or mod.startswith("tigrbl.transport")
        or mod.endswith("transport.gateway")
        for mod in modules
    )


def test_router_domain_does_not_import_gateway_implementations():
    router_root = ROOT / "router"
    violations: list[str] = []
    for path in router_root.rglob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            mod = node.module
            if mod.endswith("transport.gateway") or mod.endswith("transport.gw"):
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}:{mod}")
    assert violations == [], "\n".join(violations)
