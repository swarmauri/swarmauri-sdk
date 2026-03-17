from __future__ import annotations

from tigrbl import TableBase
from tests.conftest import mro_collect_table_spec
from tigrbl.shortcuts.table import defineTableSpec


def test_table_mro_sequence_merge() -> None:
    class BaseSpec(defineTableSpec(ops=("create",))):
        pass

    class ExtraSpec(defineTableSpec(ops=("list",))):
        pass

    class Widget(ExtraSpec, BaseSpec, TableBase):
        __tablename__ = "mro_ops_widgets"

    spec = mro_collect_table_spec(Widget)
    assert spec.ops == ("list", "create")
