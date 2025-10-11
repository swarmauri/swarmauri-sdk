from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
TABLES_DIR = PACKAGE_ROOT / "src" / "tigrbl_billing" / "tables"


def _extract_strings(node: ast.AST) -> List[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        values: List[str] = []
        for element in node.elts:
            values.extend(_extract_strings(element))
        return values
    return []


def load_table_metadata(table_name: str) -> Dict[str, Any]:
    """Return column and IO metadata for ``table_name`` using static analysis."""

    path = TABLES_DIR / f"{table_name}.py"
    if not path.exists():
        raise FileNotFoundError(f"Unknown table module: {table_name}")

    module = ast.parse(path.read_text())

    def is_table_class(node: ast.AST) -> bool:
        if not isinstance(node, ast.ClassDef):
            return False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Enum":
                return False
        for stmt in node.body:
            if (
                isinstance(stmt, ast.AnnAssign)
                and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Name)
                and stmt.value.func.id == "acol"
            ):
                return True
        return False

    table_class = next((node for node in module.body if is_table_class(node)), None)
    if not isinstance(table_class, ast.ClassDef):
        raise ValueError(f"No table class with acol columns found in {table_name}.py")

    columns: List[str] = []
    foreign_keys: List[List[str]] = []
    requests: Dict[str, List[str]] = {}
    responses: Dict[str, List[str]] = {}

    for stmt in table_class.body:
        if not (isinstance(stmt, ast.AnnAssign) and isinstance(stmt.value, ast.Call)):
            continue
        call = stmt.value
        if not (isinstance(call.func, ast.Name) and call.func.id == "acol"):
            continue

        if isinstance(stmt.target, ast.Name):
            column_name = stmt.target.id
        elif isinstance(stmt.target, ast.Attribute):
            column_name = stmt.target.attr
        else:
            continue

        columns.append(column_name)

        for kw in call.keywords:
            if kw.arg == "storage" and isinstance(kw.value, ast.Call):
                for storage_kw in kw.value.keywords:
                    if storage_kw.arg == "fk" and isinstance(
                        storage_kw.value, ast.Call
                    ):
                        for fk_kw in storage_kw.value.keywords:
                            if fk_kw.arg == "target":
                                foreign_keys.append(
                                    [column_name, ast.unparse(fk_kw.value)]
                                )
            if kw.arg == "io" and isinstance(kw.value, ast.Call):
                for io_kw in kw.value.keywords:
                    if io_kw.arg == "in_verbs":
                        for verb in _extract_strings(io_kw.value):
                            requests.setdefault(verb, []).append(column_name)
                    if io_kw.arg == "out_verbs":
                        for verb in _extract_strings(io_kw.value):
                            responses.setdefault(verb, []).append(column_name)

    return {
        "columns": columns,
        "foreign_keys": foreign_keys,
        "requests": {k: sorted(v) for k, v in sorted(requests.items())},
        "responses": {k: sorted(v) for k, v in sorted(responses.items())},
    }


__all__ = ["load_table_metadata"]
