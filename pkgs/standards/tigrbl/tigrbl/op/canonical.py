from __future__ import annotations

from typing import Type

from .._concrete._table import Table

DEFAULT_CANON_VERBS = Table.DEFAULT_CANON_VERBS


def should_wire_canonical(table: Type, op: str) -> bool:
    helper = getattr(table, "should_wire_canonical", None)
    if callable(helper):
        return bool(helper(op))
    return Table.should_wire_canonical.__func__(table, op)
