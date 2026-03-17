from __future__ import annotations

from tigrbl import TableBase
from tigrbl.shortcuts.engine import mem
from tests.conftest import mro_collect_table_spec
from tigrbl.shortcuts.table import defineTableSpec


def test_table_config_engine_binding() -> None:
    class EngineSpec(defineTableSpec(engine=mem(async_=False))):
        pass

    class Widget(EngineSpec, TableBase):
        __tablename__ = "engine_widgets"

    spec = mro_collect_table_spec(Widget)
    assert spec.engine == mem(async_=False)
