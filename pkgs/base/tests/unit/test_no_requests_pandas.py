"""Regression tests for dependencies that do not belong in swarmauri_base."""

import ast
import tomllib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "swarmauri_base"
DISALLOWED = {"pandas", "requests"}


def test_base_does_not_require_requests_or_pandas():
    pyproject = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text())
    dependencies = {
        dependency.split(";", 1)[0].split("[", 1)[0].split("=", 1)[0].strip()
        for dependency in pyproject["project"].get("dependencies", [])
    }

    assert dependencies.isdisjoint(DISALLOWED)


def test_base_does_not_import_requests_or_pandas():
    imports: dict[str, set[str]] = {}

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

            disallowed = roots & DISALLOWED
            if disallowed:
                imports[str(path.relative_to(PACKAGE_ROOT))] = disallowed

    assert imports == {}
