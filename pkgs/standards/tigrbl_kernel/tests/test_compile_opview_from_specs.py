from __future__ import annotations

from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.io_spec import IOSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.storage_spec import StorageSpec

from tigrbl_kernel._compile import _compile_opview_from_specs


def test_compile_opview_from_specs_builds_in_and_out_schema_metadata() -> None:
    columns = {
        "id": ColumnSpec(
            storage=StorageSpec(type_=int, nullable=False),
            field=FieldSpec(py_type=int, required_in=("create",)),
            io=IOSpec(in_verbs=("create",), out_verbs=("create",)),
        ),
        "display_name": ColumnSpec(
            storage=StorageSpec(type_=str, nullable=True),
            field=FieldSpec(py_type=str),
            io=IOSpec(
                in_verbs=("create",),
                out_verbs=("create",),
                alias_in="displayName",
                alias_out="displayName",
            ),
        ),
        "computed": ColumnSpec(
            storage=None,
            field=FieldSpec(py_type=str),
            io=IOSpec(in_verbs=("create",), out_verbs=("create",)),
        ),
    }
    op_spec = OpSpec(alias="create", target="create")

    opview = _compile_opview_from_specs(self=None, specs=columns, sp=op_spec)

    assert opview.schema_in.fields == ("computed", "display_name", "id")
    assert opview.schema_out.fields == ("computed", "display_name", "id")
    assert opview.schema_in.by_field["id"]["required"] is True
    assert opview.schema_in.by_field["display_name"]["alias_in"] == "displayName"
    assert opview.schema_out.by_field["display_name"]["alias_out"] == "displayName"
    assert opview.schema_in.by_field["computed"]["virtual"] is True
    assert opview.schema_out.by_field["computed"]["virtual"] is True
