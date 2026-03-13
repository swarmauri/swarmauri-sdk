from __future__ import annotations

import ast
import sys
from pathlib import Path

PACKAGE_NAME = "tigrbl_core"
PACKAGE_DIR = Path(__file__).resolve().parents[1] / PACKAGE_NAME

# Static snapshot from pyproject.toml [project.dependencies].
ALLOWED_TOP_LEVEL_IMPORTS = {"tigrbl_typing", "tomli_w", "yaml", "tigrbl_atoms"}


def _collect_top_level_imports(package_dir: Path) -> set[str]:
    imports: set[str] = set()
    for module_file in package_dir.rglob("*.py"):
        tree = ast.parse(
            module_file.read_text(encoding="utf-8"), filename=str(module_file)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".", maxsplit=1)[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    imports.add(node.module.split(".", maxsplit=1)[0])
    return imports


def test_only_declared_dependencies_are_imported() -> None:
    stdlib = set(sys.stdlib_module_names)
    imported = _collect_top_level_imports(PACKAGE_DIR)

    disallowed = {
        module
        for module in imported
        if module not in stdlib
        and module != PACKAGE_NAME
        and module not in ALLOWED_TOP_LEVEL_IMPORTS
    }

    assert not disallowed, (
        "Found imports that are not in the static dependency allowlist: "
        f"{sorted(disallowed)}"
    )
