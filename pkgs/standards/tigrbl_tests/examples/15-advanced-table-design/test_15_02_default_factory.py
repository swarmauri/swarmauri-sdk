from __future__ import annotations

from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.types import String


def test_default_factory_for_column_spec() -> None:
    def make_default(ctx):
        return "generated"

    spec = ColumnSpec(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",)),
        default_factory=make_default,
    )
    col = acol(spec=spec)
    assert col.default_factory is make_default
