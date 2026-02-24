from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _imports_bindings(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.startswith("tigrbl.bindings") for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("tigrbl.bindings"):
                return True
    return False


def test_no_tests_import_from_bindings() -> None:
    offenders: list[str] = []
    for py in ROOT.rglob("*.py"):
        if ".venv" in py.parts:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        if _imports_bindings(tree):
            offenders.append(str(py.relative_to(ROOT)))

    assert offenders == [], (
        "Found legacy bindings imports; tests should use tigrbl.mapping or top-level "
        f"exports instead: {offenders}"
    )
