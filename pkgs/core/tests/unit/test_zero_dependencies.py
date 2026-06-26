"""Regression tests for the zero-dependency core contract."""

import ast
import sys
import tomllib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "swarmauri_core"

ALLOWED_IMPORT_ROOTS = set(sys.stdlib_module_names) | {"swarmauri_core"}


def test_core_declares_no_runtime_dependencies():
    pyproject = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"].get("dependencies", []) == []


def test_core_imports_only_stdlib_and_itself():
    external_imports: dict[str, set[str]] = {}

    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.partition(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                if node.module is None or node.level:
                    continue
                roots = {node.module.partition(".")[0]}
            else:
                continue

            disallowed = roots - ALLOWED_IMPORT_ROOTS
            if disallowed:
                external_imports[str(path.relative_to(PACKAGE_ROOT))] = disallowed

    assert external_imports == {}
