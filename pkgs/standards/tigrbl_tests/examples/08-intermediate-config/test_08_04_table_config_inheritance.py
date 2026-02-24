from __future__ import annotations

from tigrbl import Base
from tigrbl.table.mro_collect import mro_collect_table_spec
from tigrbl.table.shortcuts import defineTableSpec


def test_table_config_inheritance() -> None:
    class BaseSpec(defineTableSpec(columns=("name",))):
        pass

    class Widget(BaseSpec, Base):
        __tablename__ = "inherit_widgets"

    spec = mro_collect_table_spec(Widget)
    assert spec.columns == ("name",)
