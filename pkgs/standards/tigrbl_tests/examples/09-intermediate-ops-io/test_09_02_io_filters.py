from __future__ import annotations

from tigrbl.specs import IO


def test_io_spec_filters() -> None:
    spec = IO(filter_ops=("eq", "ilike"), sortable=True)
    assert "eq" in spec.filter_ops
    assert spec.sortable is True
