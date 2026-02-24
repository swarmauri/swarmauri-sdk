from __future__ import annotations

from tigrbl.specs import ColumnSpec, F, IO, vcol


def test_virtual_column_read_producer() -> None:
    def display_value(obj, ctx):
        return f"{obj['name']}!"

    spec = ColumnSpec(storage=None, field=F(py_type=str), io=IO(out_verbs=("read",)))
    col = vcol(spec=spec, read_producer=display_value)
    assert col.read_producer is display_value
