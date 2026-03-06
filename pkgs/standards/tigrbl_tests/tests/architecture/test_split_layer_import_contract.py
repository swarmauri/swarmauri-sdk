from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
LAYER_PATHS = {
    "core": ROOT / "tigrbl_core" / "tigrbl_core",
    "base": ROOT / "tigrbl_base" / "tigrbl_base",
}
DISALLOWED_PREFIXES = {
    "core": (
        "tigrbl_base",
        "tigrbl_concrete",
        "tigrbl_core._base",
        "tigrbl_core._concrete",
    ),
    "base": ("tigrbl_concrete", "tigrbl_base._concrete"),
}


def _module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    return ".".join((root.name, *rel.parts))


def _resolved_import_targets(path: Path, pkg_root: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    module_name = _module_name(pkg_root, path)
    targets: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                targets.add(alias.name)
            continue

        if not isinstance(node, ast.ImportFrom):
            continue

        if node.level == 0:
            if node.module:
                targets.add(node.module)
            continue

        parts = module_name.split(".")
        anchor = parts[: -node.level]
        module_parts = node.module.split(".") if node.module else []
        resolved = ".".join(anchor + module_parts)
        if resolved:
            targets.add(resolved)
            for alias in node.names:
                targets.add(f"{resolved}.{alias.name}")

    return targets


@pytest.mark.parametrize("layer", ["core", "base"])
def test_split_layer_imports_follow_contract(layer: str) -> None:
    pkg_root = LAYER_PATHS[layer]
    disallowed = DISALLOWED_PREFIXES[layer]
    violations: list[str] = []

    for path in pkg_root.rglob("*.py"):
        imported = _resolved_import_targets(path, pkg_root)
        blocked = sorted(
            target
            for target in imported
            if any(target.startswith(prefix) for prefix in disallowed)
        )
        if blocked:
            rel = path.relative_to(pkg_root)
            violations.append(f"{rel}: {blocked}")

    assert not violations, "\n".join(violations)
