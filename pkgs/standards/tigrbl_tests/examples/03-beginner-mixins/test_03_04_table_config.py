from __future__ import annotations

from tigrbl import Base
from tigrbl.engine.shortcuts import mem
from tigrbl.table.mro_collect import mro_collect_table_spec
from tigrbl.table.shortcuts import defineTableSpec


def test_table_config_engine_binding() -> None:
    class EngineSpec(defineTableSpec(engine=mem(async_=False))):
        pass

    class Widget(EngineSpec, Base):
        __tablename__ = "engine_widgets"

    spec = mro_collect_table_spec(Widget)
    assert spec.engine == mem(async_=False)
