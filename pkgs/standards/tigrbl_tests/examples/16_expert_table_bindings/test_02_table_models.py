from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_table_binding_registers_model():
    Widget = build_widget_model("LessonTableModel")
    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)

    assert api.models[Widget.__name__] is Widget
