import pytest

from tigrbl.table import Table
from tigrbl.specs import ColumnSpec


class Example(Table):
    __abstract__ = True
    one: int = ColumnSpec(storage=None)
    two: int = ColumnSpec(storage=None)


@pytest.mark.parametrize("attr", ["one", "two"])
def test_columns_namespace_exposes_specs(attr: str) -> None:
    assert getattr(Example.columns, attr) is getattr(Example, attr)


@pytest.mark.parametrize("attr", ["missing", "other"])
def test_columns_namespace_missing(attr: str) -> None:
    with pytest.raises(AttributeError):
        getattr(Example.columns, attr)
