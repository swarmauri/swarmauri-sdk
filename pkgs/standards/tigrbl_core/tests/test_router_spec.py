from __future__ import annotations

import pytest

from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.router_spec import RouterSpec
from tigrbl_core._spec.schema_spec import SchemaSpec
from tigrbl_core._spec.table_spec import TableSpec


def test_router_spec_defaults() -> None:
    spec = RouterSpec()

    assert spec.name == "router"
    assert spec.prefix == ""
    assert spec.tags == ()
    assert spec.ops == ()


def test_router_spec_custom_values() -> None:
    table_spec = TableSpec(model_ref="pkg.models:User")
    op_spec = OpSpec(alias="create_user", target="create")
    schema_spec = SchemaSpec(alias="user.out", kind="out")
    spec = RouterSpec(
        name="api",
        prefix="/v1",
        tags=("core",),
        tables=(table_spec,),
        ops=(op_spec,),
        schemas=(schema_spec,),
    )

    assert spec.name == "api"
    assert spec.prefix == "/v1"
    assert spec.tags == ("core",)
    assert spec.tables == (table_spec,)
    assert spec.ops == (op_spec,)
    assert spec.schemas == (schema_spec,)


def test_router_spec_rejects_legacy_models_key() -> None:
    with pytest.raises(ValueError, match="does not accept 'models'"):
        RouterSpec.from_dict(
            {"name": "api", "models": ({"model_ref": "pkg.models:User"},)}
        )


def test_router_spec_rejects_string_entries_for_nested_specs() -> None:
    with pytest.raises(TypeError, match="tables entries must be nested specs"):
        RouterSpec(tables=("users",))
