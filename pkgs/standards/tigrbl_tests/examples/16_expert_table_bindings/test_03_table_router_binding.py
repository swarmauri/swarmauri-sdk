from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_table_binding_attaches_rest_router():
    Widget = build_widget_model("LessonTableRouter")
    api = TigrblApi(engine=mem(async_=False))

    _, router = api.include_model(Widget)

    assert router is not None
    assert api.routers[Widget.__name__] is router
