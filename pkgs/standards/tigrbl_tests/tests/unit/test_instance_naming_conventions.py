from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISALLOWED_NAMES = {
    "Fast" + "API",
    "Fast" + "Api",
    "fast" + "api",
    "Star" + "lette",
    "star" + "lette",
}


def _iter_test_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("test_*.py") if path != Path(__file__).resolve()
    )


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def test_tigrbl_instances_use_app_and_router_variable_names() -> None:
    violations: list[str] = []

    for path in _iter_test_files():
        module = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(module):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue

            value = node.value
            if not isinstance(value, ast.Call):
                continue

            ctor_name = _call_name(value)
            if ctor_name not in {"TigrblApp", "TigrblRouter"}:
                continue

            targets = [node.target] if isinstance(node, ast.AnnAssign) else node.targets
            expected = "app" if ctor_name == "TigrblApp" else "router"

            for target in targets:
                if isinstance(target, ast.Name) and target.id != expected:
                    relpath = path.relative_to(ROOT.parent)
                    violations.append(
                        f"{relpath}:{node.lineno} uses '{target.id}' for {ctor_name}; "
                        f"expected '{expected}'"
                    )

    assert not violations, "\n".join(violations)


def test_tigrbl_tests_do_not_use_disallowed_framework_names() -> None:
    violations: list[str] = []

    for path in _iter_test_files():
        content = path.read_text(encoding="utf-8")
        for disallowed_name in DISALLOWED_NAMES:
            if disallowed_name in content:
                relpath = path.relative_to(ROOT.parent)
                violations.append(
                    f"{relpath} references disallowed '{disallowed_name}'"
                )

    assert not violations, "\n".join(violations)
