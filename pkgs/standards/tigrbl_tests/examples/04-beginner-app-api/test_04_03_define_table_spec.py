from __future__ import annotations

from tigrbl import TableBase
from tests.conftest import mro_collect_table_spec
from tigrbl.shortcuts.table import defineTableSpec


def test_define_table_spec_ops_and_columns() -> None:
    class BaseSpec(defineTableSpec(ops=("create",), columns=("id", "name"))):
        pass

    class Widget(BaseSpec, TableBase):
        __tablename__ = "spec_widgets"

    spec = mro_collect_table_spec(Widget)
    assert spec.ops == ("create",)
    assert spec.columns == ("id", "name")
