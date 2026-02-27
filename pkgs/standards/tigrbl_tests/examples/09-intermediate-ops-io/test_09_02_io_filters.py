from __future__ import annotations

from tigrbl._spec import IOSpec as IO


def test_io_spec_filters() -> None:
    spec = IO(filter_ops=("eq", "ilike"), sortable=True)
    assert "eq" in spec.filter_ops
    assert spec.sortable is True
