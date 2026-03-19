from __future__ import annotations

from tigrbl_base._base import AppBase
from tigrbl_base._base._table_base import TableBase
from tigrbl_core._spec.app_spec import AppSpec


class _BoundTable(TableBase):
    __abstract__ = True
    app = None


class _PlainChild:
    app = None


def test_bind_spec_binds_mapped_child_classes_to_parent() -> None:
    parent = object()
    spec = AppSpec(tables=(_BoundTable,))

    bound = AppBase.bind_spec(spec, parent=parent)

    assert len(bound.tables) == 1
    assert isinstance(bound.tables[0], _BoundTable)
    assert bound.tables[0].app is parent


def test_bind_spec_leaves_non_bindable_classes_uninstantiated() -> None:
    parent = object()
    spec = AppSpec(ops=(_PlainChild,))

    bound = AppBase.bind_spec(spec, parent=parent)

    assert bound.ops == (_PlainChild,)
