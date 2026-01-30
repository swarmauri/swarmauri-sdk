from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_app_binding_attaches_model_router():
    Widget = build_widget_model("LessonAppRouter")
    app = TigrblApp(engine=mem(async_=False))

    _, router = app.include_model(Widget)

    assert router is not None
    assert app.routers[Widget.__name__] is router
