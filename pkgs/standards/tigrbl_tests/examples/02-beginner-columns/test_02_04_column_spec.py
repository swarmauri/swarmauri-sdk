from __future__ import annotations

from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.types import Integer, String


def test_column_spec_composition() -> None:
    spec = ColumnSpec(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )
    col = acol(spec=spec)
    assert col.storage.type_ is Integer
    assert col.field.py_type is int
    assert col.io.in_verbs == ("create",)
    assert col.io.out_verbs == ("read",)

    name = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )
    assert name.storage.type_ is String
