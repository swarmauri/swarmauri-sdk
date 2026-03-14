from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest

PACKAGE_IMPORT = "tigrbl_kernel"
PACKAGE_DIR = Path(__file__).resolve().parents[1] / "tigrbl_concrete"
PYPROJECT_PATH = Path(__file__).resolve().parents[1] / "pyproject.toml"


@pytest.mark.order(1)
def test_01_tigrbl_concrete_does_not_import_tigrbl_kernel() -> None:
    imported_modules: set[str] = set()

    for module_file in PACKAGE_DIR.rglob("*.py"):
        tree = ast.parse(
            module_file.read_text(encoding="utf-8"), filename=str(module_file)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".", maxsplit=1)[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    imported_modules.add(node.module.split(".", maxsplit=1)[0])

    assert PACKAGE_IMPORT not in imported_modules


@pytest.mark.order(1)
def test_01_tigrbl_concrete_does_not_depend_on_tigrbl_kernel() -> None:
    pyproject_data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    declared_dependencies = pyproject_data["project"]["dependencies"]

    assert "tigrbl-kernel" not in declared_dependencies
