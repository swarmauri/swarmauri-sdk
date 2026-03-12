from __future__ import annotations

import ast
from pathlib import Path

from tigrbl_atoms._request import Request


def _class_members(path: Path, class_name: str) -> tuple[set[str], set[str]]:
    module = ast.parse(path.read_text())
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            methods: set[str] = set()
            properties: set[str] = set()
            for member in node.body:
                if not isinstance(member, ast.FunctionDef):
                    continue
                is_property = any(
                    isinstance(dec, ast.Name) and dec.id == "property"
                    for dec in member.decorator_list
                )
                if is_property:
                    properties.add(member.name)
                else:
                    methods.add(member.name)
            return methods, properties
    raise AssertionError(f"class {class_name} not found in {path}")


def test_atoms_request_contract_matches_request_spec_shape() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    request_spec_path = (
        repo_root
        / "standards"
        / "tigrbl_core"
        / "tigrbl_core"
        / "_spec"
        / "request_spec.py"
    )
    assert request_spec_path.exists(), (
        "tigrbl_core request spec source must exist in workspace"
    )

    spec_methods, spec_properties = _class_members(request_spec_path, "RequestSpec")
    atoms_methods, atoms_properties = _class_members(
        Path(__file__).resolve().parents[1] / "tigrbl_atoms" / "_request.py",
        "Request",
    )

    required_methods = {
        "__init__",
        "_init_from_scope",
        "from_scope",
        "json",
        "json_sync",
    }
    required_properties = {
        "url",
        "query_params",
        "cookies",
        "bearer_token",
        "admin_key",
        "session_token",
        "client",
    }

    assert {"__init__"} <= spec_methods
    assert required_methods <= atoms_methods
    assert not spec_properties
    assert required_properties <= atoms_properties


def test_atoms_request_exposes_query_params_for_dependency_resolver() -> None:
    req = Request(
        {
            "method": "GET",
            "path": "/v1/items",
            "query_string": b"a=1&a=2&b=3",
            "headers": [(b"authorization", b"Bearer tok")],
            "path_params": {"id": "7"},
        }
    )

    assert req.query_params == {"a": "1", "b": "3"}
    assert req.path_params == {"id": "7"}
    assert req.bearer_token == "tok"
