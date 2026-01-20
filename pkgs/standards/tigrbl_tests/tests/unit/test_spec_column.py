from sqlalchemy import Integer

from tigrbl.column import ColumnSpec, F, IO, acol, is_virtual, makeVirtualColumn
from tigrbl.column.storage_spec import StorageSpec


def test_column_spec_defaults_and_virtual_detection():
    spec = ColumnSpec(storage=None)
    assert isinstance(spec.field, F)
    assert isinstance(spec.io, IO)
    assert is_virtual(spec) is True


def test_column_shortcuts_and_storage_binding():
    storage = StorageSpec(type_=Integer, primary_key=True)
    column = acol(storage=storage, field=F(py_type=int), io=IO(out_verbs=("read",)))
    assert column.storage is storage
    assert column.field.py_type is int
    assert column.io.out_verbs == ("read",)
    assert is_virtual(column) is False

    vcol = makeVirtualColumn(field=F(py_type=str), io=IO(out_verbs=("read",)))
    assert vcol.storage is None
    assert is_virtual(vcol) is True
