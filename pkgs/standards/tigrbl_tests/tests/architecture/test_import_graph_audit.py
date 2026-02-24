from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)
            elif node.level:
                modules.add("." * node.level)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
    return modules


def test_runtime_and_core_are_transport_agnostic() -> None:
    violations: list[str] = []
    for scope in ("runtime", "core"):
        for path in (ROOT / scope).rglob("*.py"):
            modules = _imported_modules(path)
            bad = [
                mod
                for mod in modules
                if mod.startswith("tigrbl.transport")
                or mod.startswith("..transport")
                or mod.startswith(".transport")
            ]
            if bad:
                rel = path.relative_to(ROOT)
                violations.append(f"{rel}: {sorted(set(bad))}")
    assert violations == [], "\n".join(violations)


def test_transport_public_surface_centralizes_core_exports() -> None:
    init_file = ROOT / "transport" / "__init__.py"
    text = init_file.read_text()
    expected = [
        "from .gw import asgi_app, wsgi_app, wrap_middleware_stack",
        "from .headers import HeaderCookies, Headers, SetCookieHeader",
        "from .request import AwaitableValue, Request, URL, request_from_asgi, request_from_wsgi",
        "from .response import (",
    ]
    for entry in expected:
        assert entry in text
