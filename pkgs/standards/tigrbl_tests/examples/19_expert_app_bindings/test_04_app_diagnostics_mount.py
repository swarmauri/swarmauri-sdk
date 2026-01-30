from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App

from examples._support import build_widget_model


def test_app_binding_mounts_diagnostics_router():
    Widget = build_widget_model("LessonAppDiagnostics")
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)

    host = App()
    router = app.attach_diagnostics(app=host)

    assert router is not None
