from sqlalchemy import String

from tigrbl_base._base._column_base import ColumnBase
from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.io_spec import IOSpec
from tigrbl_core._spec.storage_spec import StorageSpec


def test_column_base_constructs_from_components() -> None:
    storage = StorageSpec(type_=String, nullable=False, unique=True)
    field = FieldSpec(description="name")
    io = IOSpec(alias_in="name")
    column = ColumnBase(storage=storage, field=field, io=io)

    assert isinstance(column, ColumnSpec)
    assert column.storage is storage
    assert column.field is field
    assert column.io is io


def test_column_base_constructs_from_spec() -> None:
    spec = ColumnSpec(storage=StorageSpec(type_=String), field=FieldSpec(), io=IOSpec())
    column = ColumnBase(spec=spec)

    assert column.storage == spec.storage
    assert column.field == spec.field
    assert column.io == spec.io


def test_column_base_rejects_spec_plus_components() -> None:
    spec = ColumnSpec(storage=StorageSpec(type_=String))

    try:
        ColumnBase(spec=spec, storage=StorageSpec(type_=String))
    except ValueError as exc:
        assert "Provide either spec or individual components" in str(exc)
    else:
        raise AssertionError("Expected ValueError when mixing spec and components")


def test_column_base_registers_name_on_owner() -> None:
    column = ColumnBase(storage=StorageSpec(type_=String))

    class Owner:
        __tigrbl_colspecs__ = {}

    column.__set_name__(Owner, "name")
    assert Owner.__tigrbl_colspecs__["name"] is column
