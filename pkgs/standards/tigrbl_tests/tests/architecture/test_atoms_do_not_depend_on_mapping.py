from __future__ import annotations

import ast
from pathlib import Path


RUNTIME_ROOT = (
    Path(__file__).resolve().parents[2] / "../tigrbl_atoms/tigrbl_atoms/atoms"
)
PAYLOAD_SELECT = RUNTIME_ROOT / "route" / "payload_select.py"


def _normalized_import(node: ast.ImportFrom | ast.Import) -> str:
    if isinstance(node, ast.ImportFrom):
        return node.module or ""
    return ",".join(alias.name for alias in node.names)


def test_payload_select_does_not_import_mapping_modules() -> None:
    tree = ast.parse(
        PAYLOAD_SELECT.read_text(encoding="utf-8"), filename=str(PAYLOAD_SELECT)
    )

    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "mapping" in module.split("."):
                offenders.append(_normalized_import(node))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if "mapping" in alias.name.split("."):
                    offenders.append(alias.name)

    assert offenders == [], (
        "runtime atoms must not import mapping modules; payload_select should stay "
        f"kernel-only. Offenders: {offenders}"
    )


def test_payload_select_does_not_call_mro_collect_columns() -> None:
    tree = ast.parse(
        PAYLOAD_SELECT.read_text(encoding="utf-8"), filename=str(PAYLOAD_SELECT)
    )

    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == "mro_collect_columns":
                offenders.append(fn.id)
            elif isinstance(fn, ast.Attribute) and fn.attr == "mro_collect_columns":
                offenders.append(ast.unparse(fn))

    assert offenders == [], (
        "runtime atoms must not collect mappings inside the kernel. "
        f"Found mro_collect_columns calls: {offenders}"
    )
