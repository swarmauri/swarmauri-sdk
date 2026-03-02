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
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
    return modules


def test_runtime_and_core_are_transport_agnostic() -> None:
    violations: list[str] = []
    for scope in ("runtime", "core"):
        for path in (ROOT / scope).rglob("*.py"):
            modules = _imported_modules(path)
            bad = [mod for mod in modules if mod.startswith("tigrbl.transport")]
            if bad:
                rel = path.relative_to(ROOT)
                violations.append(f"{rel}: {sorted(set(bad))}")
    assert violations == [], "\n".join(violations)


def test_transport_surface_files_are_fast_broken_removed() -> None:
    transport = ROOT / "transport"
    removed = [
        "contracts.py",
        "dispatch.py",
        "dispatcher.py",
        "gateway.py",
        "gw.py",
        "headers.py",
        "httpx.py",
        "request.py",
        "request_adapters.py",
        "response.py",
        "_header.py",
        "_response.py",
        "background.py",
    ]
    assert all(not (transport / rel).exists() for rel in removed)
