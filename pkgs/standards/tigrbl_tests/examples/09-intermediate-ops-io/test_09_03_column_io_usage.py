from __future__ import annotations

from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Integer


def test_column_io_metadata() -> None:
    col = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )
    assert col.io.in_verbs == ("create",)
    assert col.io.out_verbs == ("read", "list")
