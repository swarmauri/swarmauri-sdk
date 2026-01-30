from __future__ import annotations

from tigrbl import Base
from tigrbl.engine.shortcuts import mem
from tigrbl.table.mro_collect import mro_collect_table_spec
from tigrbl.table.shortcuts import defineTableSpec


def test_table_mro_engine_precedence() -> None:
    class BaseSpec(defineTableSpec(engine=mem(async_=False))):
        pass

    class OverrideSpec(defineTableSpec(engine=mem(async_=True))):
        pass

    class Widget(OverrideSpec, BaseSpec, Base):
        __tablename__ = "mro_widgets"

    spec = mro_collect_table_spec(Widget)
    assert spec.engine == mem(async_=True)
