from __future__ import annotations

import pytest

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.io_spec import IOSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.router_spec import RouterSpec
from tigrbl_core._spec.storage_spec import StorageSpec
from tigrbl_core._spec.table_spec import TableSpec


class _Handler:
    def __call__(self) -> None: ...


def test_router_spec_from_dict_rejects_string_table_entries() -> None:
    with pytest.raises(TypeError):
        RouterSpec.from_dict({"name": "api", "tables": ("users",)})


def test_router_spec_from_dict_accepts_nested_table_specs() -> None:
    user_table = TableSpec(model_ref="pkg.models:User")

    spec = RouterSpec.from_dict({"name": "api", "tables": (user_table,)})

    assert isinstance(spec.tables[0], TableSpec)


def test_app_spec_from_dict_accepts_string_router_entries() -> None:
    spec = AppSpec.from_dict({"title": "app", "routers": ("api",)})
    assert spec.routers == ("api",)


def test_table_spec_from_dict_rejects_string_column_entries() -> None:
    with pytest.raises(TypeError):
        TableSpec.from_dict({"model_ref": "pkg.models:User", "columns": ("id",)})


def test_table_spec_from_dict_accepts_nested_column_specs() -> None:
    id_column = ColumnSpec(
        storage=StorageSpec(type_=int, nullable=False),
        field=FieldSpec(py_type=int),
        io=IOSpec(in_verbs=("create",), out_verbs=("read",)),
    )

    spec = TableSpec.from_dict(
        {
            "model_ref": "pkg.models:User",
            "ops": (OpSpec(alias="list_users", target=_Handler()),),
            "columns": (id_column,),
        }
    )

    assert isinstance(spec.columns, tuple)
    assert isinstance(spec.columns[0], ColumnSpec)
