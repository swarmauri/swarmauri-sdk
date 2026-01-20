import pytest

from tigrbl.column import (
    Column,
    ColumnSpec,
    F,
    S,
    acol,
    vcol,
    makeColumn,
    makeVirtualColumn,
)
from tigrbl.types import Integer


def test_make_column_components() -> None:
    col = makeColumn(storage=S(type_=Integer))
    assert isinstance(col, Column)
    assert col.storage.type_ is Integer


def test_make_column_from_spec() -> None:
    spec = ColumnSpec(storage=S(type_=Integer))
    col = makeColumn(spec=spec)
    assert col.storage is spec.storage


def test_make_column_conflict_spec_components() -> None:
    spec = ColumnSpec(storage=S(type_=Integer))
    with pytest.raises(ValueError):
        makeColumn(storage=S(type_=Integer), spec=spec)


def test_make_column_read_producer_with_storage_errors() -> None:
    with pytest.raises(ValueError):
        makeColumn(storage=S(type_=Integer), read_producer=lambda o, c: None)


def test_make_virtual_column_components() -> None:
    def producer(obj, ctx):
        return 1

    col = makeVirtualColumn(field=F(py_type=int), producer=producer)
    assert isinstance(col, Column)
    assert col.storage is None
    assert col.read_producer is producer


def test_make_virtual_column_from_spec() -> None:
    spec = ColumnSpec(storage=None, field=F(py_type=int))
    col = makeVirtualColumn(spec=spec)
    assert col.field is spec.field
    assert col.storage is None


def test_make_virtual_column_conflict_spec_components() -> None:
    spec = ColumnSpec(storage=None, field=F(py_type=int))
    with pytest.raises(ValueError):
        makeVirtualColumn(field=F(py_type=int), spec=spec)


def test_make_virtual_column_conflict_producers() -> None:
    with pytest.raises(ValueError):
        makeVirtualColumn(producer=lambda o, c: None, read_producer=lambda o, c: None)


def test_aliases_are_convenience() -> None:
    assert acol is makeColumn
    assert vcol is makeVirtualColumn


def test_alias_functions_behave_equally() -> None:
    c1 = makeColumn(storage=S(type_=Integer))
    c2 = acol(storage=S(type_=Integer))
    assert type(c1) is type(c2)
    assert c1.storage.type_ is c2.storage.type_

    v1 = makeVirtualColumn(field=F(py_type=int))
    v2 = vcol(field=F(py_type=int))
    assert v1.storage is None and v2.storage is None
