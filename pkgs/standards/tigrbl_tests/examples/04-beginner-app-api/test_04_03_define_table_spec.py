from __future__ import annotations

from tigrbl import Base
from tigrbl.table.mro_collect import mro_collect_table_spec
from tigrbl.table.shortcuts import defineTableSpec


def test_define_table_spec_ops_and_columns() -> None:
    class BaseSpec(defineTableSpec(ops=("create",), columns=("id", "name"))):
        pass

    class Widget(BaseSpec, Base):
        __tablename__ = "spec_widgets"

    spec = mro_collect_table_spec(Widget)
    assert spec.ops == ("create",)
    assert spec.columns == ("id", "name")
